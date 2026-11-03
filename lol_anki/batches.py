"""Bounded roster-driven draft production. No approval, apply or APKG operations."""
from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import tomllib
from .io import atomic,canonical,digest,inside,read_json,write_json
from .project import Project
from .operations import project_operation,serialized,OperationBusy
from .editorial import Editorial
from .generation.evidence import Retriever,DD,resolve,token
from .generation.workflow import generate,processing_identity
from .generation.archive import archive_run
from .batch_qa import validate_run


def stamp(): return dt.datetime.now(dt.timezone.utc).isoformat()


class BatchRunner:
    def __init__(self,root):
        self.root=Path(root).resolve(); self.folder=self.root/'data/batches'; self.editor=Editorial(self.root)

    def path(self,key):
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,70}',key): raise ValueError('Use a lowercase batch name')
        return self.folder/key

    def protected(self):
        result={}
        for profile in ('pilot','batch01','editorial'):
            project=Project(self.root,profile)
            for field in ('content','sources','lock'):
                path=project.path(field)
                if path.exists(): result[path.relative_to(self.root).as_posix()]=digest(path.read_bytes())
        return result

    def inventory(self,index):
        approved=[]
        for profile in ('pilot','batch01','editorial'):
            project=Project(self.root,profile)
            if project.path('content').exists(): approved+=project.content()['cards']
        working=list(self.editor.registry()['cards'].values())
        generated=set(p.parent.name for p in (self.root/'data/drafts').glob('*/index.json'))
        generated.update(p.parent.parent.name for p in (self.root/'build/generated').glob('*/*/cards.json'))
        for file in self.folder.glob('*/staging.json'):
            generated.update(slug for slug,e in read_json(file)['champions'].items() if e['status']=='generated')
        reservations={}
        for p in self.folder.glob('*/batch.json'):
            batch=read_json(p)
            for slug,entry in batch['champions'].items():
                if entry['status']!='skipped': reservations[slug]=batch['id']
        rows=[]
        for item in sorted(index['data'].values(),key=lambda c:c['id'].lower()):
            slug=item['id'].lower(); cid=int(item['key']); entity='champ:'+str(cid)
            owned=[c for c in approved if c.get('entity_id')==entity or token(c['row']['champion'])==token(item['name'])]
            pending=[r for r in working if r['working']['entity_id']==entity or token(r['champion'])==token(item['name'])]
            state='approved' if owned else 'editorial_pending' if pending else 'generated' if slug in generated else 'reserved' if slug in reservations else 'eligible'
            rows.append({'slug':slug,'ddragon_id':item['id'],'riot_id':cid,'name':item['name'],
                         'status':state,'approved_cards':len({c['id'] for c in owned}),
                         'editorial_cards':len(pending),'reserved_by':reservations.get(slug)})
        return rows

    def roster(self,offline=False):
        config=tomllib.loads((self.root/'generation.toml').read_text('utf-8')); retriever=Retriever(self.root,config,offline)
        versions,version_meta=retriever.get(DD+'/api/versions.json',refresh=not offline)
        version=json.loads(versions)[0]
        if not re.fullmatch(r'\d+\.\d+\.\d+',version): raise ValueError('Invalid Riot release')
        blob,meta=retriever.get(f'{DD}/cdn/{version}/data/en_US/champion.json')
        return json.loads(blob),{'version':version,'index':meta,'versions':version_meta}

    @serialized
    def plan(self,key,size=10,selections=None,offline=False,authorization=None):
        path=self.path(key)
        if (path/'batch.json').exists(): raise ValueError('Batch already exists; resume with batch-run '+key)
        if not 1<=size<=25: raise ValueError('Batch size must be between 1 and 25')
        pending_review=[]
        for file in self.folder.glob('*/batch.json'):
            if not read_json(file).get('batch_review'):
                pending_review.append(file.parent.name)
            if not read_json(file).get('batch_review') and not (isinstance(authorization,str) and authorization.strip()):
                raise ValueError('Review the previous batch before creating another: '+file.parent.name)
        index,receipt=self.roster(offline); inventory=self.inventory(index)
        by_slug={r['slug']:r for r in inventory}
        if selections:
            selected=[by_slug[resolve(index,name)['id'].lower()] for name in selections]
            if len({r['slug'] for r in selected})!=len(selected): raise ValueError('Champion selection contains duplicate aliases')
            if len(selected)>size: raise ValueError('Selection exceeds batch size')
        else: selected=[r for r in inventory if r['status']=='eligible'][:size]
        if not selected: raise ValueError('No new champions selected')
        config=(self.root/'generation.toml').read_text('utf-8')
        if 'ddragon_version' in tomllib.loads(config)['retrieval']: raise ValueError('Configure the roster release through the batch plan, not an existing retrieval override')
        config=config.replace('[retrieval]','[retrieval]\nddragon_version = "'+receipt['version']+'"',1)
        atomic(path/'generation.toml',config.encode()); write_json(path/'roster.json',index)
        state={'schema_version':1,'id':key,'status':'planned','created_at':stamp(),'updated_at':stamp(),
               'batch_size':size,'roster':receipt,'roster_sha256':digest(canonical(index)),
               'config_sha256':digest(config.encode()),'approved_before':self.protected(),
               'existing_editorial_sha256':{k:digest(canonical(v)) for k,v in self.editor.registry()['cards'].items()},
               'inventory_before':inventory,'champions':{},'batch_review':None}
        if authorization:
            state['continuation_authorization']={'request':authorization.strip(),'at':stamp(),
                'previous_unreviewed_batches':pending_review,
                'scope':'Explicit additional draft-batch request only; does not assert earlier batch review or approve any cards/media'}
        for row in selected:
            state['champions'][row['slug']]={**row,'status':'queued' if row['status']=='eligible' else 'skipped',
                'skip_reason':None if row['status']=='eligible' else row['status'],'attempts':[],'result':None}
        self.save(state); return state

    def save(self,state):
        # Checkpoints travel with the workspace rather than a particular drive.
        for entry in state['champions'].values():
            if entry.get('archive') and Path(entry['archive']).is_absolute():
                entry['archive']=inside(self.root,entry['archive']).relative_to(self.root).as_posix()
            for field in ('output','previews'):
                value=(entry.get('result') or {}).get(field)
                if value and Path(value).is_absolute():
                    entry['result'][field]=inside(self.root,value).relative_to(self.root).as_posix()
        state['updated_at']=stamp(); write_json(self.path(state['id'])/'batch.json',state)
        self.report(state)

    def assert_preserved(self,state):
        if self.protected()!=state['approved_before']: raise ValueError('Approved content/source/lock changed since the batch plan; batch stopped')
        data=self.editor.registry()['cards']
        for key,sha in state['existing_editorial_sha256'].items():
            current=digest(canonical(data[key])) if key in data else None
            if current!=sha:
                state.setdefault('concurrent_editorial_changes',{})[key]={
                    'initial_sha256':sha,'observed_sha256':current,
                    'disposition':'Preserved external review/edit; the batch does not modify this record'}

    def model_attempts(self):
        return {p.relative_to(self.root).as_posix() for p in (self.root/'.cache/generator/ai').glob('*/attempt-*') if p.is_dir()}

    def verified_archive(self,entry):
        archive=inside(self.root,entry['archive']); manifest=read_json(archive/'archive.json')
        if digest(canonical(manifest['files']))!=manifest['file_manifest_sha256']:
            raise ValueError('Completed draft archive manifest changed: '+entry['slug'])
        for rel,sha in manifest['files'].items():
            if digest(inside(archive,rel).read_bytes())!=sha:
                raise ValueError('Completed draft archive changed: '+entry['slug']+'/'+rel)
        return archive

    def run(self,key,offline=False,retry_qa=False):
        # Separate long-running batch lock; editorial actions remain responsive.
        self.path(key) # Validate before creating any lock directory.
        claim=self.root/'build/batch-locks'/key
        with project_operation(claim):
            try: return self._run(key,offline,retry_qa)
            except (OSError,ValueError,RuntimeError,KeyboardInterrupt) as ex:
                path=self.path(key)/'batch.json'
                if path.exists():
                    state=read_json(path); state['status']='interrupted' if isinstance(ex,KeyboardInterrupt) else 'blocked'
                    state['last_error']={'type':type(ex).__name__,'message':str(ex)[:2000],'at':stamp()}
                    self.save(state)
                raise

    def _run(self,key,offline,retry_qa=False):
        path=self.path(key); state=read_json(path/'batch.json')
        self.assert_preserved(state)
        if digest((path/'generation.toml').read_bytes())!=state['config_sha256'] or digest(canonical(read_json(path/'roster.json')))!=state['roster_sha256']:
            raise ValueError('Frozen batch configuration/roster changed')
        config=tomllib.loads((path/'generation.toml').read_text('utf-8'))
        if retry_qa:
            if offline: raise ValueError('QA regeneration requires online mode; ordinary offline resume does not regenerate')
            with project_operation(self.root):
                for entry in state['champions'].values():
                    if entry['status']!='failed' or not entry.get('result') or not entry.get('qa',{}).get('errors'):
                        continue
                    if entry.get('archive'): raise ValueError('Cannot regenerate already imported/archived editorial work')
                    previous=inside(self.root,entry['result']['output'])
                    archived=archive_run(self.root,previous)['path']
                    entry.setdefault('superseded_results',[]).append({'result':entry['result'],'qa':entry['qa'],
                        'archive':Path(archived).relative_to(self.root).as_posix(),'at':stamp(),
                        'reason':'Explicit QA retry after processor/prompt correction; prior failure retained, not waived'})
                    entry['result']=None
                self.save(state)
        state['status']='running'; self.save(state)
        for slug,entry in state['champions'].items():
            if entry['status']=='skipped': continue
            if entry['status']=='completed':
                archive=self.verified_archive(entry)
                # Restores a missing import after an interrupted sync, without replacing edits.
                cards=read_json(archive/'cards.json')['cards']; known=self.editor.registry()['cards']
                if any(c['id'] not in known for c in cards):
                    with project_operation(self.root): self.editor.sync(archive)
                continue
            with project_operation(self.root):
                self.assert_preserved(state)
                now={r['slug']:r for r in self.inventory(read_json(path/'roster.json'))}[slug]
                if now['status'] in ('approved','editorial_pending') and not entry.get('archive'):
                    entry.update(status='skipped',skip_reason='existing_'+now['status']); self.save(state); continue
                if now['status']=='generated' and not entry.get('source_input'):
                    entry.update(status='skipped',skip_reason='existing_generated'); self.save(state); continue
            attempt={'started_at':stamp(),'processor':processing_identity(),'status':'running'}
            entry['attempts'].append(attempt); started=self.model_attempts(); self.save(state)
            try:
                if not entry.get('source_input'):
                    entry['status']='retrieving'; self.save(state)
                    retriever=Retriever(self.root,config,offline); packet,folder=retriever.collect(entry['ddragon_id'])
                    entry['source_input']=folder.relative_to(self.root).as_posix()
                    entry['source_sha256']=digest((folder/'packet.json').read_bytes()); self.save(state)
                source=inside(self.root,entry['source_input'])
                if digest((source/'packet.json').read_bytes())!=entry['source_sha256']: raise ValueError('Batch source checkpoint changed')
                entry['status']='generating'; self.save(state)
                result=entry.get('result')
                if not result:
                    result=generate(self.root,entry['ddragon_id'],offline=offline,source_input=source,
                                    config_path=path/'generation.toml',readable_ids=True)
                    entry['result']=result; self.save(state)
                run=inside(self.root,result['output']); entry['status']='validating'; self.save(state)
                report=validate_run(self.root,run,entry); entry['qa']=report
                write_json(path/'qa'/f'{slug}.json',report)
                if report['errors']: raise ValueError('Blocking structural/factual QA errors: '+str(report['errors']))
                archived=entry.get('archive')
                if not archived:
                    archived=archive_run(self.root,run)['path']; entry['archive']=archived; self.save(state)
                archive_path=inside(self.root,archived)
                with project_operation(self.root):
                    self.assert_preserved(state)
                    known=self.editor.registry()['cards']; cards=read_json(archive_path/'cards.json')['cards']
                    origin=archive_path.relative_to(self.root).as_posix()
                    if any(r['working']['entity_id']=='champ:'+str(entry['riot_id']) and r['source']['run']!=origin for r in known.values()):
                        raise ValueError('Other editorial work now exists for this champion; preserving it without importing duplicates')
                    for card in cards:
                        if card['id'] in known and known[card['id']]['source']['run']!=origin:
                            raise ValueError('Existing editorial identity collision: '+card['id'])
                    entry['editorial_import']=self.editor.sync(archive_path)
                    self.editor.render()
                    entry['status']='completed'; attempt['status']='completed'; self.save(state)
            except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as ex:
                stage=entry['status']; entry['status']='failed'; attempt.update(status='failed',stage=stage,error_type=type(ex).__name__,error=str(ex)[:4000])
                # Other champions continue. Successful model calls/sources remain cached.
            except KeyboardInterrupt:
                entry['status']='interrupted'; attempt['status']='interrupted'; state['status']='interrupted'
                self.save(state); raise
            finally:
                attempt['finished_at']=stamp(); attempt['new_model_attempts']=sorted(self.model_attempts()-started)
                self.save(state)
        self.assert_preserved(state); self.editor.render()
        state['status']='awaiting_batch_review'; self.save(state)
        return state

    @serialized
    def acknowledge_review(self,key,reviewer):
        if not reviewer.strip(): raise ValueError('A named human batch reviewer is required')
        state=read_json(self.path(key)/'batch.json')
        if state['status']!='awaiting_batch_review': raise ValueError('Finish the batch before acknowledging its review')
        state['batch_review']={'reviewer':reviewer.strip(),'at':stamp(),'scope':'Batch report inspected; this does not approve individual content/media or apply proposals'}
        self.save(state); return state['batch_review']

    def audit(self,key):
        """Revalidate retained drafts with current deterministic QA, without AI/import."""
        self.path(key)
        with project_operation(self.root/'build/batch-locks'/key),project_operation(self.root):
            state=read_json(self.path(key)/'batch.json'); self.assert_preserved(state)
            for slug,entry in state['champions'].items():
                if entry['status']!='completed': continue
                archive=self.verified_archive(entry)
                report=validate_run(self.root,archive,entry)
                entry['qa']=report; write_json(self.path(key)/'qa'/f'{slug}.json',report)
            self.save(state); return read_json(self.path(key)/'report.json')

    def report(self,state):
        path=self.path(state['id']); rows=list(state['champions'].values()); counts=Counter(r['status'] for r in rows)
        cards=[]; findings=[]
        for entry in rows:
            qa=entry.get('qa',{}); findings+=qa.get('findings',[])
            for key in qa.get('card_ids',[]): cards.append({'id':key,'champion':entry['name'],'slug':entry['slug'],
                'status':'pending_editorial_review' if entry['status']=='completed' else 'withheld_pending_QA','archive':entry.get('archive')})
        usage=Counter(); unavailable=0
        duplicates=sorted(key for key,count in Counter(c['id'] for c in cards).items() if count>1)
        for row in rows:
            for attempt in row['attempts']:
                for rel in attempt.get('new_model_attempts',[]):
                    meta=inside(self.root,rel)/'metadata.json'
                    if not meta.exists(): unavailable+=1; continue
                    values=read_json(meta).get('usage',[])
                    for value in values if isinstance(values,list) else [values]:
                        if isinstance(value,dict): usage.update({k:v for k,v in value.items() if isinstance(v,int)})
        write_json(path/'cards.json',{'cards':cards})
        report={'id':state['id'],'status':state['status'],'champions':dict(counts),'draft_cards':len(cards),
                'errors':sum(f['severity']=='error' for f in findings)+sum(r['status']=='failed' and not r.get('qa',{}).get('errors') for r in rows)+len(duplicates),
                'warnings':sum(f['severity']=='warning' for f in findings),
                'duplicate_ids':duplicates,
                'failed_champions':[r['slug'] for r in rows if r['status']=='failed'],
                'model_attempts_started':sum(len(a.get('new_model_attempts',[])) for r in rows for a in r['attempts']),
                'available_model_usage':dict(usage),'attempts_without_usage_receipt':unavailable,
                'all_drafts_unapproved':True,'second_batch_requires_human_review':not bool(state['batch_review'])}
        write_json(path/'report.json',report)
        lines=[f'# Champion batch {state["id"]}', '',f'Status: {state["status"]}. Pinned asset release: {state["roster"]["version"]}; gameplay patch remains independently verified or unknown.',
               '',f'{len(rows)} selected champions; {len(cards)} draft cards; {report["errors"]} QA errors; {report["warnings"]} warnings.',
               'No approvals, proposal applications or APKG exports. Human review is required before another batch.',
               'Initial roster status: '+json.dumps(dict(Counter(r['status'] for r in state['inventory_before'])))+'.','',
               '| Champion | Status | Cards | Errors | Warnings | GIF / static / portrait | Citations |',
               '| --- | --- | ---: | ---: | ---: | --- | ---: |']
        for row in rows:
            qa=row.get('qa',{}); media=qa.get('media',{})
            lines.append(f'| {row["name"]} | {row["status"]} | {qa.get("cards",0)} | {qa.get("errors",0) or int(row["status"]=="failed")} | {qa.get("warnings",0)} | {media.get("gif",0)} / {media.get("icon",0)} / {media.get("portrait",0)} | {qa.get("citations",0)} |')
        for row in rows:
            lines+=['',f'## {row["name"]}','']
            if row.get('archive'): lines+=['Review archive: `'+row['archive']+'`.']
            for section in row.get('qa',{}).get('section_dispositions',[]):
                if section['disposition'] in ('merged','advanced_only','out_of_scope'):
                    lines+=['- **Kit coverage / '+section['disposition']+'** `'+section['source_id']+'`: '+section['reason']]
            for attempt in row['attempts']:
                if attempt.get('error'): lines+=['- **'+('Historical failed attempt (resumed)' if row['status']=='completed' else 'BLOCKING execution failure')+'**: '+attempt['error']]
            for finding in row.get('qa',{}).get('findings',[]):
                lines.append(f'- **{finding["severity"]} / {finding["category"]} / {finding["code"]}** `{finding["id"]}`: {finding["message"]}')
        lines+=['','## All new draft IDs','']+['- `'+c['id']+'` — '+c['champion'] for c in cards]
        if state.get('concurrent_editorial_changes'):
            lines+=['','## Concurrent editorial work preserved','']+[
                '- `'+key+'`: '+value['disposition'] for key,value in state['concurrent_editorial_changes'].items()]
        lines+=['','## Usage and limits','',f'{report["model_attempts_started"]} new model attempts recorded (including failed/repair calls). Receipts and available token usage remain in each archive and attempt cache.',
                'Available new-attempt token usage: '+json.dumps(dict(usage))+f'. {unavailable} attempts lack usage receipts.',
                'All media still needs human matching/current-client review. Model support checks are fallible. Decode/citation checks do not constitute editorial approval.']
        atomic(path/'REPORT.md',('\n'.join(lines)+'\n').encode())

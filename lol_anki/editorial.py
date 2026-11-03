"""Local editorial state, protected learning text, and explicit promotion proposals."""
import copy
import datetime as dt
from pathlib import Path
from .io import atomic,canonical,digest,inside,read_json,write_json
from .project import Project
from .editorial_media import MediaOverrides,inspect_media,variant_identity,matches,immutable
from .generation.presentation import check_learning_row
from .generation.contracts import check_citations,numeric_tokens
from .editorial_contract import text_fingerprint
from .operations import serialized

EDITABLE={'question','answer','counterplay','build_focus','priority','visual_cue_description'}
MEDIA_FIELDS=('media_path','icon_path','visual_cue_media_path')


def stamp(): return dt.datetime.now(dt.timezone.utc).isoformat()


class Editorial:
    def __init__(self,root):
        self.root=Path(root).resolve(); self.folder=self.root/'data/editorial'
        self.path=self.folder/'registry.json'; self.overrides=MediaOverrides(self.root)

    def registry(self):
        return read_json(self.path) if self.path.exists() else {'schema_version':1,'cards':{},'events':[]}

    @serialized
    def initialize(self):
        base=Project(self.root,profile='batch01'); project=Project(self.root,profile='editorial')
        for key in ('content','sources','lock'):
            target=project.path(key)
            if not target.exists(): atomic(target,base.path(key).read_bytes())
        if not self.path.exists(): write_json(self.path,self.registry())
        if not self.overrides.path.exists(): write_json(self.overrides.path,self.overrides.records())
        return project

    @serialized
    def sync(self,run):
        run=Path(run).resolve()
        if not run.is_relative_to(self.root): raise ValueError('Import a generated run/archive inside the workspace')
        if (run/'archive.json').exists():
            manifest=read_json(run/'archive.json')
            for rel,sha in manifest['files'].items():
                if digest(inside(run,rel).read_bytes())!=sha: raise ValueError('Draft archive integrity failure: '+rel)
        cards=read_json(run/'cards.json')['cards']; packet=read_json(run/'source-packet.json')
        baseline={c['id'] for c in Project(self.root,profile='batch01').content()['cards']}
        data=self.registry(); imported=[]; incoming=[]
        for card in cards:
            if card['id'] in baseline or card['content_status']!='draft': raise ValueError('Import unapproved additions only; baseline cards are protected')
            key=card['id']; source={'run':run.relative_to(self.root).as_posix(),
                'card_sha256':digest(canonical(card)),'packet_sha256':digest((run/'source-packet.json').read_bytes())}
            if key in data['cards']:
                record=data['cards'][key]
                if record['source']['card_sha256']!=source['card_sha256']:
                    record['incoming_generated_revision']=source; incoming.append(key)
                continue  # Never replace pinned working text, reviews or selected overrides.
            data['cards'][key]={'id':key,'champion':packet['champion']['name'],'source':source,
                'working':copy.deepcopy(card),'revision':1,'content_review':{'status':'pending'},
                'media_review':{'status':'pending'}}
            imported.append(key)
        if imported or incoming:
            data['events'].append({'action':'import','at':stamp(),'ids':imported,'incoming_ids':incoming})
            write_json(self.path,data)
        return {'imported':imported,'incoming_preserved':incoming,'cards':len(data['cards'])}

    def packet(self,record):
        path=inside(self.root,record['source']['run'])/'source-packet.json'
        if digest(path.read_bytes())!=record['source']['packet_sha256']: raise ValueError('Pinned source packet changed')
        return read_json(path)

    def override_card(self,key):
        record=self.registry()['cards'][key]; card=copy.deepcopy(record['working'])
        if card.get('learning_unit',{}).get('kind')=='ability_variant':
            assets=read_json(inside(self.root,record['source']['run'])/'assets.json')
            generic=assets['abilities'].get(card['row']['slot'],{})
            card['ambiguous_media_sha256']=[r['sha256'] for r in generic.values() if r]
        return card

    def text_hash(self,record):
        return text_fingerprint(record['working'])

    def effective(self,record):
        card=copy.deepcopy(record['working']); row=card['row']; run=inside(self.root,record['source']['run'])
        manifest=read_json(run/'assets.json'); assets={r['path']:r for r in manifest['files']}
        versions=self.packet(record)['versions']
        files={}; provenance=[]
        for column in MEDIA_FIELDS:
            if row.get(column):
                path=inside(run,row[column]); files[column]=path
                upstream=copy.deepcopy(assets[row[column]])
                if digest(path.read_bytes())!=upstream['sha256']: raise ValueError('Pinned source media changed')
                original=next((r for r in assets.values() if r['sha256']==upstream.get('source_sha256') and r['kind'] in ('webm','mp4')),None)
                if original:
                    original_path=self.folder/'originals'/(original['sha256']+Path(original['path']).suffix)
                    immutable(original_path,inside(run,original['path']).read_bytes())
                    upstream['original_path']=original_path.relative_to(self.root).as_posix()
                provenance.append({'role':column,'sha256':digest(path.read_bytes()),'source':'archived_source_matched',
                    'path':path.relative_to(self.root).as_posix(),
                    'upstream_asset':upstream,'asset_version':versions['ddragon'],'game_patch':versions.get('game_patch'),
                    'rights_holder':'Upstream asset rights holder; inspect original provenance',
                    'license_reference':'https://www.riotgames.com/en/legal','distribution_status':'pending'})
        override=self.overrides.select(card)
        if override:
            path=inside(self.root,override['path']); role=override['provenance'].get('display_role','animation' if path.suffix=='.gif' else 'icon')
            if row['slot']=='P' and (path.suffix=='.gif' or role=='supplemental'):
                column='visual_cue_media_path'; row['visual_cue_status']='approved'
            else:
                column='media_path'; row['media_type']='gif' if path.suffix=='.gif' else 'icon'
                if role=='screenshot': card['editorial_presentation']={'large_front':True}
            files[column]=path
            provenance=[p for p in provenance if p['role']!=column]
            provenance.append({'role':column,**copy.deepcopy(override)})
        selected_by_role={'front':override['id']} if override else {}
        for role,column in (('icon','icon_path'),('cue','visual_cue_media_path')):
            replacement=self.overrides.select(card,role)
            if replacement:
                if role=='cue' and row['slot']!='P': raise ValueError('Only passive cards accept supplementary cue media')
                files[column]=inside(self.root,replacement['path'])
                if role=='cue': row['visual_cue_status']='approved'
                provenance=[p for p in provenance if p['role']!=column]
                provenance.append({'role':column,**copy.deepcopy(replacement)})
                selected_by_role[role]=replacement['id']
        for column,path in files.items():
            blob=path.read_bytes(); name='ed-'+digest(blob)+path.suffix.lower()
            immutable(self.folder/'media'/name,blob); row[column]='media/'+name
        row['source_video_path']=''  # Originals/recipes remain in provenance, never embedded as video.
        payload={'card_id':card['id'],'variant':variant_identity(card),'media_type':row['media_type'],
                 'files':{c:digest(p.read_bytes()) for c,p in files.items()},'provenance':provenance}
        signature=digest(canonical(payload))
        kind=card.get('learning_unit',{}).get('kind','ability' if row['level']=='L2' and row['slot']!='P' else 'other')
        fallback=row['level']=='L2' and kind in ('ability','ability_variant','conditional_effect','transformation') and row['media_type']!='gif'
        selection='manually_approved_override' if selected_by_role else ('icon_fallback' if fallback else ('verified_source_matched' if record['media_review'].get('status')=='approved' and record['media_review'].get('media_sha256')==signature else 'source_candidate_pending_review'))
        return card,signature,{'signature':signature,'files':payload['files'],'provenance':provenance,'selection':selection,
                               'priority':1 if selected_by_role else 3 if fallback else 2,
                               'fallback':fallback,'selected_override':override['id'] if override else None,'overrides_by_role':selected_by_role}

    def blockers(self,record):
        issues=[]; card,media_hash,media=self.effective(record)
        packet=self.packet(record)
        if not packet['versions'].get('wiki_revision') or not any('wiki.leagueoflegends.com' in r['url'] for r in packet['resources']): issues.append('Retrieved Wiki revision/snapshot required')
        if not card['row']['media_path'] or not card['row']['icon_path']: issues.append('Real front media and icon required')
        content=record['content_review']; visual=record['media_review']
        if content['status']!='approved' or content.get('text_sha256')!=self.text_hash(record): issues.append('Content rejected' if content['status']=='rejected' else 'Content review required')
        if visual['status']!='approved' or visual.get('media_sha256')!=media_hash: issues.append('Media rejected' if visual['status']=='rejected' else 'Media review required')
        if media['fallback'] and not visual.get('accept_static_fallback'): issues.append('Animation missing; explicitly review the matched static fallback')
        return issues

    def _content_decision(self,record,payload,reviewer,notes,reviewed_revision,at):
        decision=payload.get('status')
        if decision not in ('approved','rejected','pending'): raise ValueError('Invalid review decision')
        source_ids=payload.get('source_ids',[])
        review={'status':decision,'reviewer':reviewer,'notes':notes,'at':at,
                'reviewed_revision':reviewed_revision,'text_sha256':self.text_hash(record),
                'selected_source_ids':sorted(set(source_ids))}
        if decision=='rejected': review['reason']=notes
        if decision=='approved':
            packet=self.packet(record); known={e['id']:e for e in packet['excerpts']}
            if not source_ids or set(source_ids)-set(known): raise ValueError('Select the retrieved evidence used to check all claims')
            if not all(payload.get(k) is True for k in ('claims_checked','cores_checked','inferences_acknowledged','warnings_acknowledged')):
                raise ValueError('Explicit claim/core/inference/warning review attestations required')
            citations=[{'source_id':i,'quote':known[i]['text']} for i in sorted(set(source_ids))]
            check_citations(citations,packet)
            if not numeric_tokens(record['working']['row']['answer'])<=numeric_tokens(' '.join(c['quote'] for c in citations)):
                raise ValueError('Numbers in the edited explanation lack matching cited evidence')
            if numeric_tokens(record['working']['row']['counterplay']): raise ValueError('Numeric Counterplay timings require separate exact-stat review')
            review.update(citations=citations,claims_checked=True,cores_checked=True,inferences_acknowledged=True,warnings_acknowledged=True)
        return review

    def _media_decision(self,record,payload,reviewer,notes,reviewed_revision,at):
        decision=payload.get('status')
        if decision not in ('approved','rejected','pending'): raise ValueError('Invalid review decision')
        card,signature,media=self.effective(record)
        if decision=='approved':
            if not card['row']['media_path'] or not card['row']['icon_path']: raise ValueError('Real front media and icon are required')
            if payload.get('matching_checked') is not True or payload.get('rights_acknowledged') is not True: raise ValueError('Explicit identity/visual matching and rights review required')
            if media['fallback'] and payload.get('accept_static_fallback') is not True:
                raise ValueError('Missing animation needs an explicit static-fallback exception')
            for column in MEDIA_FIELDS:
                if card['row'].get(column): inspect_media(inside(self.folder,card['row'][column]))
        review={'status':decision,'reviewer':reviewer,'notes':notes,'at':at,
                'reviewed_revision':reviewed_revision,'media_sha256':signature,'media_file_hashes':copy.deepcopy(media['files']),
                'matching_checked':payload.get('matching_checked',False),
                'rights_acknowledged':payload.get('rights_acknowledged',False),
                'accept_static_fallback':payload.get('accept_static_fallback',False),
                'fallback_reason':payload.get('fallback_reason',''),'distribution_status':payload.get('distribution_status','pending')}
        if decision=='rejected': review['reason']=notes
        return review,media

    @serialized
    def approve_content_and_media(self,key,payload,expected=None):
        data=self.registry(); current=data['cards'][key]; before=copy.deepcopy(current)
        if expected and expected!=digest(canonical(current)): raise ValueError('Stale review page; reload before changing or approving this card')
        reviewer=payload.get('reviewer','').strip(); notes=payload.get('notes','').strip()
        if not reviewer: raise ValueError('Reviewer name is required')
        if payload.get('confirmation') is not True: raise ValueError('Confirm that you reviewed the card content and selected media')
        reviewed_revision=current['revision']; at=stamp()
        content_payload={'status':'approved','source_ids':payload.get('source_ids',[]),
                         'claims_checked':payload.get('claims_checked'),'cores_checked':payload.get('cores_checked'),
                         'inferences_acknowledged':payload.get('inferences_acknowledged'),
                         'warnings_acknowledged':payload.get('warnings_acknowledged')}
        media_payload={'status':'approved','matching_checked':payload.get('matching_checked'),
                       'rights_acknowledged':payload.get('rights_acknowledged'),
                       'accept_static_fallback':payload.get('accept_static_fallback',False),
                       'fallback_reason':payload.get('fallback_reason','')}
        content=self._content_decision(current,content_payload,reviewer,notes,reviewed_revision,at)
        media,_=self._media_decision(current,media_payload,reviewer,notes,reviewed_revision,at)
        previous_content=current['content_review']; previous_media=current['media_review']
        if (previous_content.get('status')=='approved' and previous_media.get('status')=='approved'
                and previous_content.get('reviewer')==reviewer and previous_media.get('reviewer')==reviewer
                and previous_content.get('notes')==notes and previous_media.get('notes')==notes
                and previous_content.get('selected_source_ids')==content['selected_source_ids']
                and previous_content.get('text_sha256')==content['text_sha256']
                and previous_media.get('media_sha256')==media['media_sha256']
                and previous_media.get('media_file_hashes')==media['media_file_hashes']
                and all(previous_content.get(field)==content[field] for field in
                        ('claims_checked','cores_checked','inferences_acknowledged','warnings_acknowledged'))
                and all(previous_media.get(field)==media[field] for field in
                        ('matching_checked','rights_acknowledged','accept_static_fallback','fallback_reason'))):
            return current
        updated=copy.deepcopy(current); updated['content_review']=content; updated['media_review']=media
        updated['revision']+=1
        event={'id':key,'action':'combined_approval','at':at,'reviewer':reviewer,
               'reviewed_revision':reviewed_revision,'revision':updated['revision'],
               'before_record_sha256':digest(canonical(before)),'after_record_sha256':digest(canonical(updated)),
               'record_sha256':digest(canonical(updated)),'selected_source_ids':content['selected_source_ids'],
               'media_sha256':media['media_sha256'],'media_file_hashes':copy.deepcopy(media['media_file_hashes']),
               'attestations':{'combined_confirmation':True,'claims_checked':True,'cores_checked':True,
                   'inferences_acknowledged':True,'warnings_acknowledged':True,'matching_checked':True,
                   'rights_acknowledged':True,'accept_static_fallback':media['accept_static_fallback']}}
        data['cards'][key]=updated; data['events'].append(event); write_json(self.path,data)
        return updated

    @serialized
    def mutate(self,key,action,payload,expected=None):
        data=self.registry(); record=data['cards'][key]; before=copy.deepcopy(record)
        if expected and expected!=digest(canonical(record)): raise ValueError('Stale review page; reload before changing or approving this card')
        reviewer=payload.get('reviewer','').strip(); notes=payload.get('notes','').strip()
        reviewed_revision=record['revision']
        if action=='edit':
            fields=payload['fields']
            if set(fields)-EDITABLE or not all(isinstance(v,str) for v in fields.values()): raise ValueError('Only learning text, priority and cue description may be edited')
            row={**record['working']['row'],**fields}; check_learning_row(row)
            if '<' in ' '.join(fields.values()) or row['priority'] not in ('A','B','C') or not row['question'] or not row['answer'] or not row['counterplay']: raise ValueError('Plain English question, answer, Counterplay and priority required')
            if (row['level']=='L1')!=bool(row['build_focus']): raise ValueError('Build focus is required on L1 and must be empty on L2')
            import re
            if re.search(r'[\u0400-\u04ff\u0600-\u06ff\u4e00-\u9fff]|\ufffd',' '.join(fields.values())): raise ValueError('Learning content must remain in English')
            record['working']['row']=row; record['content_review']={'status':'pending','reason':'Learning text changed'}
        elif action in ('content','media'):
            if not reviewer: raise ValueError('Reviewer name is required')
            at=stamp()
            if action=='content':
                record['content_review']=self._content_decision(record,payload,reviewer,notes,reviewed_revision,at)
            else:
                record['media_review'],media=self._media_decision(record,payload,reviewer,notes,reviewed_revision,at)
        else: raise ValueError('Unknown editorial action')
        record['revision']+=1
        changes={field:{'before':before.get('working',{}).get('row',{}).get(field),
                        'after':record.get('working',{}).get('row',{}).get(field)}
                 for field in EDITABLE
                 if before.get('working',{}).get('row',{}).get(field)!=record.get('working',{}).get('row',{}).get(field)}
        event={'id':key,'action':action,'at':stamp(),'reviewer':reviewer or None,
               'reviewed_revision':reviewed_revision if action in ('content','media') else None,
               'revision':record['revision'],'before_record_sha256':digest(canonical(before)),
               'after_record_sha256':digest(canonical(record)),'record_sha256':digest(canonical(record))}
        if changes: event['changes']=changes
        if action=='content':
            event['selected_source_ids']=record['content_review'].get('selected_source_ids',[])
            event['attestations']={k:record['content_review'].get(k,False) for k in
                                   ('claims_checked','cores_checked','inferences_acknowledged','warnings_acknowledged')}
        elif action=='media':
            event['media_sha256']=record['media_review'].get('media_sha256')
            event['media_file_hashes']=copy.deepcopy(record['media_review'].get('media_file_hashes',{}))
            event['attestations']={k:record['media_review'].get(k,False) for k in
                                   ('matching_checked','rights_acknowledged','accept_static_fallback')}
        data['events'].append(event)
        write_json(self.path,data)
        return record

    @serialized
    def audit_media_event(self,key,action,reviewer,details):
        data=self.registry(); record=data['cards'][key]
        data['events'].append({'id':key,'action':action,'at':stamp(),'reviewer':reviewer or None,
                               'revision':record['revision'],'record_sha256':digest(canonical(record)),
                               'details':copy.deepcopy(details)})
        write_json(self.path,data)

    def render(self):
        from .generation.preview import create_previews
        data=self.registry(); groups={}
        for record in data['cards'].values():
            card,_,_=self.effective(record); groups.setdefault(record['champion'].lower(),[]).append(card)
        paths={}
        for champion,cards in groups.items():
            folder=self.root/'build/editorial/workspaces'/champion; folder.mkdir(parents=True,exist_ok=True)
            for card in cards:
                for column in MEDIA_FIELDS:
                    if card['row'].get(column):
                        src=inside(self.folder,card['row'][column]); atomic(folder/card['row'][column],src.read_bytes())
                card.setdefault('versioning',{'verified_game_patch':None})
            create_previews(cards,folder)
            from .generation.preview import page_name
            for card in cards:
                if card.get('editorial_presentation',{}).get('large_front'):
                    page=folder/'previews'/page_name(card)
                    atomic(page,page.read_text(encoding='utf-8').replace('class="icon"','class="ability-gif"').encode())
            write_json(folder/'cards.json',{'schema_version':2,'cards':cards})
            paths[champion]=str(folder/'previews/index.html')
        return paths

    def state(self):
        data=self.registry(); cards=[]; champions={}
        for record in data['cards'].values():
            card,_,media=self.effective(record); packet=self.packet(record)
            blockers=self.blockers(record); champion=record['champion']
            qa_path=inside(self.root,record['source']['run'])/'qa.json'; qa=read_json(qa_path)
            inventory_path=inside(self.root,record['source']['run'])/'mechanics-inventory.json'
            inventory=read_json(inventory_path) if inventory_path.exists() else {}
            slot=card['row'].get('slot')
            core_mechanics=[copy.deepcopy(core) for ability in inventory.get('abilities',[])
                            if ability.get('slot')==slot
                            for core in ability.get('core_mechanics',[])] if slot not in (None,'-') else []
            source_labels={'riot:'+str(a.get('slot')):'Riot: '+str(a.get('name')) for a in packet.get('abilities',[])}
            source_labels['riot:role']='Riot: Champion role'
            cards.append({**copy.deepcopy(record),'expected':digest(canonical(record)),'effective_card':card,'media':media,
                'blockers':blockers,'evidence':packet['excerpts'],
                'core_mechanics':core_mechanics,
                'source_labels':source_labels,
                'source_conflicts':qa.get('source_conflicts',[]),'factual_risks':qa.get('factual_risks',[]),
                'warnings':next((c for c in qa['cards'] if c['id']==record['id']),{}),
                'overrides':[r for r in self.overrides.records()['records'] if matches(r['target'],card)]})
            summary=champions.setdefault(champion,{'cards':0,'ready':0,'blocked':[]})
            summary['cards']+=1; summary['ready']+=not blockers
            if blockers: summary['blocked'].append({'id':record['id'],'blockers':blockers})
        return {'cards':cards,'champions':champions,'model_calls':0,'baseline_cards':100}

    @serialized
    def propose(self,ids,folder):
        from .review import propose
        project=self.initialize(); data=self.registry(); base=project.content(); candidate=copy.deepcopy(base); sources=copy.deepcopy(project.sources())
        positions={c['id']:i for i,c in enumerate(candidate['cards'])}; selected=[]
        for key in ids:
            record=data['cards'][key]
            if self.blockers(record): raise ValueError(key+': '+', '.join(self.blockers(record)))
            card,signature,media=self.effective(record); packet=self.packet(record)
            card['content_status']='curated'; card['qa_status']='approved'; card['revision']=base['build_epoch']
            card['media_review']={'status':'approved_source_match','current_client_review':'pending','reviewer':record['media_review']['reviewer']}
            card['editorial_review']={'content':record['content_review'],'media':record['media_review'],
                'text_sha256':self.text_hash(record),'media_sha256':signature,'source_packet_sha256':record['source']['packet_sha256'],
                'distribution_status':'pending','media_lineage':media}
            card['evidence']['claims']=[{'field':'answer','claim':card['row']['answer'],'locator':'Manual editorial review of selected exact source excerpts',
                                        'citations':record['content_review']['citations']}]
            source_dir=self.folder/'sources'; source_dir.mkdir(exist_ok=True)
            run=inside(self.root,record['source']['run'])
            packet_sha=record['source']['packet_sha256']; packet_path=source_dir/(packet_sha+'.json')
            immutable(packet_path,(run/'source-packet.json').read_bytes())
            card['editorial_review']['source_packet_path']=packet_path.relative_to(self.root).as_posix()
            wiki=next((r for r in packet['resources'] if 'wiki.leagueoflegends.com' in r['url']),None)
            if not wiki: raise ValueError('A retrieved Wiki snapshot is required for promotion')
            wiki_path=source_dir/wiki['sha256']; immutable(wiki_path,(run/'sources'/wiki['sha256']).read_bytes())
            card['evidence']['wiki_snapshot']={'path':wiki_path.relative_to(self.root).as_posix(),'sha256':wiki['sha256']}
            for path,sha in ((packet_path,packet_sha),(wiki_path,wiki['sha256'])):
                rel=path.relative_to(self.root).as_posix()
                if not any(s['path']==rel for s in sources['snapshots']): sources['snapshots'].append({'path':rel,'sha256':sha,'upstream_version':packet['versions']['ddragon'],'legacy_path':'editorial source promotion'})
            if not any(e['id']==card['entity_id'] for e in sources['entities']): sources['entities'].append({'id':card['entity_id'],'name':card['row']['champion'],'riot_id':packet['champion']['riot_id']})
            catalog=sources.setdefault('editorial_catalog',{})
            catalog[card['row']['champion']]={'entity_id':card['entity_id'],'card_ids':sorted(k for k,r in data['cards'].items() if r['champion']==record['champion'])}
            for column in MEDIA_FIELDS:
                path=card['row'].get(column)
                if path: sources['media_sha256'][path]=digest(inside(self.folder,path).read_bytes())
            if key in positions: candidate['cards'][positions[key]]=card
            else: positions[key]=len(candidate['cards']); candidate['cards'].append(card)
            selected.append(key)
        frozen=Project(self.root,profile='batch01').content()['cards']
        if candidate['cards'][:len(frozen)]!=frozen: raise ValueError('The approved 100-card baseline is immutable')
        folder=Path(folder); write_json(folder/'candidate.json',candidate); write_json(folder/'candidate-sources.json',sources)
        return propose(project,folder/'candidate.json',folder,source_candidate_path=folder/'candidate-sources.json',
                       editorial_inputs={key:digest(canonical(data['cards'][key])) for key in selected})

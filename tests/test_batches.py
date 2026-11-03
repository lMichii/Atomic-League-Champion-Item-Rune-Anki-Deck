"""Small isolated runner fixtures; live model/media checks belong to the pilot run."""
import copy
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from lol_anki.batches import BatchRunner
from lol_anki.io import canonical,digest,read_json,write_json
from lol_anki.project import ROOT
from lol_anki.generation.workflow import compile_cards
from lol_anki.generation.kit_contracts import freeze_plan


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests',prefix='batch-'); self.root=Path(self.temp.name)
        for file in ('pipeline.toml','pipeline.batch01.toml','pipeline.editorial.toml','generation.toml'):
            shutil.copy2(ROOT/file,self.root/file)
        for profile in ('pilot','production','editorial'):
            write_json(self.root/f'data/content/{profile}.json',{'cards':[]})
            write_json(self.root/f'data/content/{profile}.lock.json',{})
            write_json(self.root/f'data/sources/{profile}.json',{})
        self.runner=BatchRunner(self.root)
        self.index={'data':{s:{'id':s,'name':s,'key':str(i)} for i,s in enumerate(('Annie','Garen','Karma','Braum','Aphelios'),1)}}
        self.roster_patch=patch.object(BatchRunner,'roster',return_value=(self.index,{'version':'16.21.1'})); self.roster_patch.start()
        self.addCleanup(self.roster_patch.stop); self.addCleanup(self.temp.cleanup)

    def seed(self):
        self.state=self.runner.plan('test',3,['Annie','Garen','Karma'])
        self.generated=[]; self.retrieved=[]
        def collect(owner,name):
            item=self.index['data'][name]; self.retrieved.append(name)
            folder=self.root/'build/generated/inputs'/name
            write_json(folder/'packet.json',{'champion':{'name':name,'ddragon_id':name,'riot_id':int(item['key'])},'resources':[]})
            return read_json(folder/'packet.json'),folder
        def generate(root,name,**kwargs):
            self.assertTrue(kwargs['readable_ids']); self.generated.append(name)
            folder=self.root/'build/generated'/name.lower()/'run'
            packet=read_json(Path(kwargs['source_input'])/'packet.json')
            key=f'champ:{name.lower()}:overview:L1'
            card={'id':key,'entity_id':'champ:'+str(packet['champion']['riot_id']),'entity_kind':'champion',
                  'content_status':'draft','qa_status':'needs_review','row':{'id':key,'champion':name}}
            write_json(folder/'cards.json',{'cards':[card]}); write_json(folder/'source-packet.json',packet)
            return {'output':str(folder),'cards':1,'published':False,'approved':False}
        def archive(root,run):
            dest=self.root/'data/drafts'/run.parent.name/run.name
            shutil.copytree(run,dest,dirs_exist_ok=True)
            files={p.relative_to(dest).as_posix():digest(p.read_bytes()) for p in dest.rglob('*') if p.is_file() and p.name!='archive.json'}
            write_json(dest/'archive.json',{'files':files,'file_manifest_sha256':digest(canonical(files))})
            return {'path':str(dest)}
        def qa(root,run,entry):
            return {'cards':1,'card_ids':[f'champ:{entry["slug"]}:overview:L1'],'errors':0,'warnings':1,
                    'findings':[{'severity':'warning','category':'media','code':'manual','id':entry['slug'],'message':'Review required'}]}
        self.patches=[patch('lol_anki.batches.Retriever.collect',collect),patch('lol_anki.batches.generate',generate),
                      patch('lol_anki.batches.archive_run',archive),patch('lol_anki.batches.validate_run',qa),
                      patch('lol_anki.batches.processing_identity',return_value={'source_sha256':'test'}),
                      patch('lol_anki.batches.Editorial.render',return_value={})]
        for p in self.patches: p.start(); self.addCleanup(p.stop)

    def test_selection_excludes_approved_pending_generated_and_duplicate_aliases(self):
        write_json(self.root/'data/content/editorial.json',{'cards':[{'id':'champ:braum:q:recognize:L2','entity_id':'champ:4','row':{'champion':'Braum'}}]})
        write_json(self.root/'data/editorial/registry.json',{'cards':{'existing':{'champion':'Aphelios','working':{'entity_id':'champ:5'}}},'events':[]})
        write_json(self.root/'data/drafts/karma/index.json',{'status':'unapproved'})
        rows={r['slug']:r for r in self.runner.inventory(self.index)}
        self.assertEqual(rows['braum']['status'],'approved'); self.assertEqual(rows['aphelios']['status'],'editorial_pending')
        self.assertEqual(rows['karma']['status'],'generated')
        state=self.runner.plan('eligible',2)
        self.assertEqual(set(state['champions']),{'annie','garen'})
        self.assertEqual(state['status'],'planned')
        with self.assertRaisesRegex(ValueError,'previous batch'): self.runner.plan('second')

    def test_duplicate_aliases_and_invalid_batch_bounds_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate aliases'): self.runner.plan('bad',2,['Annie','1'])
        with self.assertRaises(ValueError): self.runner.plan('bad',26)
        with self.assertRaises(ValueError): self.runner.plan('../escape')

    def test_explicit_continuation_is_not_fabricated_batch_or_card_approval(self):
        first=self.runner.plan('first',1,['Annie'])
        with self.assertRaisesRegex(ValueError,'previous batch'): self.runner.plan('next',1,['Garen'])
        second=self.runner.plan('next',1,['Garen'],authorization='Build the next ten champion drafts.')
        self.assertIsNone(read_json(self.runner.path('first')/'batch.json')['batch_review'])
        self.assertIsNone(second['batch_review'])
        self.assertEqual(second['continuation_authorization']['previous_unreviewed_batches'],['first'])
        self.assertEqual(second['champions']['garen']['status'],'queued')

    def test_failed_champion_does_not_stop_others_and_resume_is_idempotent(self):
        self.seed()
        import lol_anki.batches as module
        original=module.generate
        def fail(root,name,**kwargs):
            if name=='Garen': raise RuntimeError('Isolated transport failure')
            return original(root,name,**kwargs)
        with patch('lol_anki.batches.generate',side_effect=fail): state=self.runner.run('test')
        self.assertEqual(state['champions']['garen']['status'],'failed')
        self.assertEqual(state['champions']['karma']['status'],'completed')
        self.assertEqual(len(self.runner.editor.registry()['cards']),2)
        first=copy.deepcopy(self.runner.editor.registry()['cards'])
        state=self.runner.run('test'); self.assertTrue(all(r['status']=='completed' for r in state['champions'].values()))
        self.assertEqual(self.retrieved.count('Garen'),1) # Frozen sources reused.
        self.assertEqual(self.generated.count('Annie'),1); self.assertEqual(self.generated.count('Karma'),1)
        for key,value in first.items(): self.assertEqual(self.runner.editor.registry()['cards'][key],value)
        registry=self.runner.editor.registry(); self.runner.run('test'); self.assertEqual(registry,self.runner.editor.registry())
        calls=len(self.generated); audit=self.runner.audit('test')
        self.assertEqual(audit['errors'],0); self.assertEqual(len(self.generated),calls)
        self.assertEqual(registry,self.runner.editor.registry())
        self.assertEqual(len(registry['cards']),3)
        self.assertTrue(all(r['content_review']['status']==r['media_review']['status']=='pending' for r in registry['cards'].values()))
        self.assertEqual(read_json(self.root/'data/content/editorial.json')['cards'],[])
        self.assertFalse(list(self.root.rglob('*.apkg')))

    def test_interrupted_checkpoint_resumes_cached_result_without_another_model_call(self):
        self.seed()
        import lol_anki.batches as module
        original=module.validate_run; calls=[]
        def interrupt(root,run,entry):
            calls.append(entry['slug'])
            if len(calls)==1: raise KeyboardInterrupt()
            return original(root,run,entry)
        with patch('lol_anki.batches.validate_run',side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt): self.runner.run('test')
        self.assertEqual(read_json(self.runner.path('test')/'batch.json')['status'],'interrupted')
        self.runner.run('test'); self.assertEqual(self.generated.count('Annie'),1)

    def test_explicit_qa_retry_retains_failed_result_and_does_not_regenerate_completed_work(self):
        self.seed()
        import lol_anki.batches as module
        original=module.validate_run
        def blocked(root,run,entry):
            qa=original(root,run,entry)
            if entry['slug']=='annie':
                qa['errors']=1; qa['findings'].append({'severity':'error','category':'factual','code':'core','id':'annie','message':'Unsupported inventory core'})
            return qa
        with patch('lol_anki.batches.validate_run',side_effect=blocked): self.runner.run('test')
        self.assertEqual(self.generated.count('Annie'),1)
        # Ordinary resume revalidates retained result; does not spend more model calls.
        with patch('lol_anki.batches.validate_run',side_effect=blocked): self.runner.run('test')
        self.assertEqual(self.generated.count('Annie'),1)
        state=self.runner.run('test',retry_qa=True)
        self.assertEqual(self.generated.count('Annie'),2)
        self.assertEqual(self.generated.count('Garen'),1); self.assertEqual(self.generated.count('Karma'),1)
        entry=state['champions']['annie']; self.assertEqual(entry['status'],'completed')
        previous=entry['superseded_results'][0]
        self.assertEqual(previous['qa']['errors'],1)
        self.assertTrue((self.root/previous['archive']/'archive.json').exists())
        self.assertTrue(all(r['content_review']['status']==r['media_review']['status']=='pending' for r in self.runner.editor.registry()['cards'].values()))

    def test_frozen_config_sources_and_approved_content_are_integrity_guarded(self):
        self.seed(); config=self.runner.path('test')/'generation.toml'; blob=config.read_bytes(); config.write_bytes(blob+b'\n')
        with self.assertRaisesRegex(ValueError,'configuration/roster'): self.runner.run('test')
        config.write_bytes(blob); write_json(self.root/'data/content/editorial.json',{'cards':[{'new':'human edit'}]})
        with self.assertRaisesRegex(ValueError,'Approved content'): self.runner.run('test')

    def test_new_pending_work_after_planning_is_skipped_without_changes(self):
        self.seed()
        existing={'champion':'Karma','source':{'run':'manual'},'working':{'entity_id':'champ:3'},'content_review':{'status':'pending'}}
        write_json(self.runner.editor.path,{'cards':{'human-pending':existing},'events':[]})
        state=self.runner.run('test')
        self.assertEqual(state['champions']['karma']['status'],'skipped')
        self.assertNotIn('Karma',self.generated)
        self.assertEqual(self.runner.editor.registry()['cards']['human-pending'],existing)

    def test_completed_archive_integrity_is_checked_on_offline_rerun(self):
        self.seed(); state=self.runner.run('test')
        archive=self.root/state['champions']['annie']['archive']; (archive/'cards.json').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Completed draft archive changed'): self.runner.run('test',offline=True)

    def test_concurrent_unrelated_human_review_is_retained_not_overwritten(self):
        existing={'champion':'Aphelios','source':{'run':'manual'},'working':{'entity_id':'champ:5'},'revision':1}
        write_json(self.runner.editor.path,{'cards':{'human':existing},'events':[]})
        self.seed()
        reviewed={**existing,'revision':2,'reviewer':'Human reviewer'}
        write_json(self.runner.editor.path,{'cards':{'human':reviewed},'events':[]})
        state=self.runner.run('test')
        self.assertEqual(self.runner.editor.registry()['cards']['human'],reviewed)
        self.assertIn('human',state['concurrent_editorial_changes'])
        self.assertTrue(all(r['status']=='completed' for r in state['champions'].values()))

    def test_batch_review_gate_requires_named_explicit_acknowledgment(self):
        self.seed(); self.runner.run('test')
        with self.assertRaises(ValueError): self.runner.plan('next',1)
        with self.assertRaises(ValueError): self.runner.acknowledge_review('test','')
        self.runner.acknowledge_review('test','Isolated human reviewer')
        self.assertTrue(read_json(self.runner.path('test')/'batch.json')['batch_review'])
        self.assertTrue(all(r['content_review']['status']=='pending' for r in self.runner.editor.registry()['cards'].values()))

    def test_standard_and_variant_draft_identifiers_are_readable_and_source_ids_numeric(self):
        run=ROOT/'data/drafts/braum/8696ff171e68869fcc76'
        cards=compile_cards(read_json(run/'ai-draft.json'),read_json(run/'source-packet.json'),read_json(run/'assets.json'),readable_ids=True)
        self.assertEqual({c['id'] for c in cards},{'champ:braum:overview:L1',*(f'champ:braum:{s}:recognize:L2' for s in 'pqwer')})
        self.assertEqual({c['entity_id'] for c in cards},{'champ:201'})
        plan=read_json(ROOT/'data/drafts/aphelios/c6569ae4b284ca4203c1/kit-analysis.json')
        units=freeze_plan(plan,'aphelios')
        self.assertEqual(len(units),14)
        self.assertTrue(all(c['card_id'].startswith('champ:aphelios:') for c in units))
        self.assertTrue(any(':ability_variant:q:moonshot:calibrum:' in c['card_id'] for c in units))

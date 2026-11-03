"""Author-only resume/export uses real fixtures; no live content or model calls."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from lol_anki.io import read_json,write_json,digest,canonical
from lol_anki.project import ROOT,Project
from lol_anki.staging import run_staging,verify_saved,split_joint,standard_text,export_saved,author,reviewed_response
from lol_anki.generation.contracts import check_draft
from lol_anki.package import read_collection
from lol_anki.generation.ai import AIClient,ModelError


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'build/tests',prefix='staging-')
        self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name)
        for name in ('pipeline.toml','pipeline.batch01.toml','pipeline.editorial.toml','generation.toml'):
            shutil.copy2(ROOT/name,self.root/name)
        legacy=Project(self.root).legacy; legacy.mkdir(parents=True)
        shutil.copy2(Project(ROOT).legacy/'anki_template.anki2',legacy/'anki_template.anki2')
        for name in ('pilot','production','editorial'):
            write_json(self.root/f'data/content/{name}.json',{'cards':[],'build_epoch':Project(ROOT,'batch01').content()['build_epoch']})
        run=read_json(ROOT/'data/drafts/annie/index.json')['current_run']
        archive=Path('data/drafts/annie')/run
        shutil.copytree(ROOT/archive,self.root/archive)
        self.folder=self.root/'data/batches/fixture'
        self.folder.mkdir(parents=True); shutil.copy2(ROOT/'generation.toml',self.folder/'generation.toml')
        write_json(self.folder/'roster.json',{'data':{'Annie':{'id':'Annie','key':'1','name':'Annie'}}})
        write_json(self.folder/'batch.json',{'id':'fixture','champions':{'annie':{'slug':'annie','name':'Annie','status':'completed','archive':archive.as_posix(),'qa':{'errors':0}}}})

    def run_batch(self):
        with patch('lol_anki.staging.author',side_effect=AssertionError('No authoring on reused/completed champions')):
            return run_staging(self.root,'fixture',offline=True)

    def test_explicit_repair_is_single_champion_and_cannot_repeat(self):
        plan=read_json(self.folder/'batch.json')
        plan['champions']['annie'].pop('archive')
        plan['champions']['annie']['source_input']='data/saved-source'
        plan['champions']['other']={'slug':'other','name':'Other'}
        write_json(self.folder/'batch.json',plan)
        original={'status':'failed','error':'Original validation failure'}
        write_json(self.folder/'staging.json',{'champions':{'annie':original},'approved_before':{}})
        with patch('lol_anki.staging.BatchRunner.inventory',return_value=[{'slug':'annie','status':'reserved'}]), \
             patch('lol_anki.staging.author',side_effect=ValueError('Still invalid')) as model:
            result=run_staging(self.root,'fixture',repair_champion='annie')
            self.assertEqual(model.call_count,1)
            self.assertEqual(result['champions'],{'failed':1})
            state=read_json(self.folder/'staging.json')
            self.assertNotIn('other',state['champions'])
            self.assertEqual(state['champions']['annie']['error'],'Still invalid')
            saved=read_json(self.folder/'repairs/annie/authorization.json')
            self.assertEqual(saved['previous'],original)
            with self.assertRaisesRegex(ValueError,'already attempted'):
                run_staging(self.root,'fixture',repair_champion='annie')
            self.assertEqual(model.call_count,1)

    def test_repair_rejects_saved_success_and_offline_mode(self):
        self.run_batch()
        with self.assertRaisesRegex(ValueError,'failed champion'):
            run_staging(self.root,'fixture',repair_champion='annie')
        with self.assertRaisesRegex(ValueError,'online author'):
            run_staging(self.root,'fixture',offline=True,repair_champion='annie')

    def test_human_correction_requires_confirmation_and_pinned_hashes(self):
        folder=self.folder/'staging/annie'; review=self.folder/'repairs/annie'
        packet={'schema_version':1}; value={'cards':[]}
        self.assertIsNone(reviewed_response(folder,packet))
        response=review/'correction.json'; write_json(response,value)
        record={'response_path':response.name,'response_sha256':digest(response.read_bytes()),
            'source_packet_sha256':digest(canonical(packet)),
            'receipt':{'output_sha256':digest(canonical(value)),'metadata':{}}}
        write_json(review/'reviewed-response.json',record)
        with self.assertRaisesRegex(ValueError,'confirmation'):
            reviewed_response(folder,packet)
        record['receipt']['metadata']['explicit_user_confirmation']='User confirmed citation-only correction'
        write_json(review/'reviewed-response.json',record)
        with patch('lol_anki.staging.standard_text',return_value=value), patch('lol_anki.staging.check_draft') as validate:
            self.assertEqual(reviewed_response(folder,packet)[0],value)
            validate.assert_called_once_with(value,packet)
        with self.assertRaisesRegex(ValueError,'source packet changed'):
            reviewed_response(folder,{'schema_version':1,'changed':True})
        write_json(response,{'cards':['tampered']})
        with self.assertRaisesRegex(ValueError,'correction or source'):
            reviewed_response(folder,packet)

    def test_confirmed_source_resolution_resumes_only_unused_author_allowance(self):
        plan=read_json(self.folder/'batch.json'); plan['champions']['annie'].pop('archive')
        plan['champions']['annie']['ddragon_id']='Annie'
        write_json(self.folder/'batch.json',plan)
        write_json(self.folder/'staging.json',{'champions':{'annie':{'status':'failed','error':'original'}},'approved_before':{}})
        with patch('lol_anki.staging.BatchRunner.inventory',return_value=[{'slug':'annie','status':'reserved'}]), \
             patch('lol_anki.staging.Retriever.collect',side_effect=ValueError('ambiguous source identities')), \
             patch('lol_anki.staging.author') as model:
            run_staging(self.root,'fixture',repair_champion='annie')
            model.assert_not_called()
        previous=read_json(self.folder/'staging.json')['champions']['annie']
        write_json(self.folder/'repairs/annie/source-resolution.json',{
            'explicit_user_confirmation':'Merge identical source sections',
            'failed_state_sha256':digest(canonical(previous))})
        source=self.root/'source'; write_json(source/'packet.json',{})
        with patch('lol_anki.staging.BatchRunner.inventory',return_value=[{'slug':'annie','status':'reserved'}]), \
             patch('lol_anki.staging.Retriever.collect',return_value=({},source)), \
             patch('lol_anki.staging.author',side_effect=ValueError('Human response required')) as model:
            run_staging(self.root,'fixture',repair_champion='annie')
            self.assertEqual(model.call_count,1)
            with self.assertRaisesRegex(ValueError,'already attempted'):
                run_staging(self.root,'fixture',repair_champion='annie')
            self.assertEqual(model.call_count,1)

    def test_reviewed_qa_notes_require_real_sources(self):
        folder=self.folder/'staging/annie'; review=self.folder/'repairs/annie'
        packet={'schema_version':1,'excerpts':[{'id':'wiki:R'}]}; value={'cards':[]}
        response=review/'correction.json'; write_json(response,value)
        record={'response_path':response.name,'response_sha256':digest(response.read_bytes()),
            'source_packet_sha256':digest(canonical(packet)),
            'receipt':{'output_sha256':digest(canonical(value)),
                'metadata':{'explicit_user_confirmation':'Keep source-quality note',
                    'qa_findings':[{'code':'source_quality_note','source_ids':['topic_placeholder']}]}}}
        write_json(review/'reviewed-response.json',record)
        with self.assertRaisesRegex(ValueError,'Unknown reviewed QA source'):
            reviewed_response(folder,packet)
        record['receipt']['metadata']['qa_findings'][0]['source_ids']=['wiki:R']
        write_json(review/'reviewed-response.json',record)
        with patch('lol_anki.staging.standard_text',return_value=value), patch('lol_anki.staging.check_draft'):
            result=reviewed_response(folder,packet)
        self.assertEqual(result[1]['metadata']['qa_findings'][0]['source_ids'],['wiki:R'])

    def test_saved_resume_stable_package_and_approved_preservation(self):
        protected=self.root/'data/content/editorial.json'; before=protected.read_bytes()
        report=self.run_batch(); first=(self.root/report['output']).read_bytes()
        self.assertEqual(report['cards'],6); self.assertEqual(report['new_ai_verifier_calls'],0)
        self.assertEqual(report['new_ai_media_calls'],0); self.assertFalse(report['editorial_approval'])
        state=read_json(self.folder/'staging.json'); entry=state['champions']['annie']
        self.assertEqual(entry['status'],'generated'); self.assertTrue(entry['reused_existing'])
        self.assertEqual(read_json(self.root/'data/batches/progress.json')['champions']['annie']['import_status'],'not_recorded')
        progress=read_json(self.root/'data/batches/progress.json')
        progress['champions']['annie']['import_status']='manually_recorded_import'
        write_json(self.root/'data/batches/progress.json',progress)
        self.run_batch(); self.assertEqual((self.root/report['output']).read_bytes(),first)
        self.assertEqual(read_json(self.root/'data/batches/progress.json')['champions']['annie']['import_status'],'manually_recorded_import')
        self.assertEqual(protected.read_bytes(),before)
        human={'cards':[{'id':'human-owned','row':{'champion':'Other'},'entity_id':'champ:999'}],'build_epoch':1790000000}
        write_json(protected,human); human_bytes=protected.read_bytes()
        self.run_batch(); self.assertEqual(protected.read_bytes(),human_bytes)
        self.assertIn('external_approved_changes',read_json(self.folder/'staging.json'))
        con=read_collection(self.root/report['output'])
        try:
            self.assertEqual(con.execute('select count(*) from notes').fetchone()[0],6)
            fields=con.execute('select flds from notes').fetchall()
            self.assertTrue(all(r[0].split('\x1f')[0].startswith('champ:annie:') for r in fields))
            self.assertTrue(all(r[0].split('\x1f')[14]=='26.21' for r in fields))
            model_id=con.execute('select mid from notes limit 1').fetchone()[0]
            model=json.loads(con.execute('select models from col').fetchone()[0])[str(model_id)]
            self.assertNotIn('bottom',model['tmpls'][0]['qfmt'])
            self.assertIn('Patch {{Patch}}',model['tmpls'][0]['afmt'])
        finally: con.close()
        (self.root/entry['path']/'cards.json').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Saved champion changed'): verify_saved(self.root,entry)

    def test_saved_collection_export_does_not_generate_or_approve(self):
        self.run_batch()
        before=(self.root/'data/content/editorial.json').read_bytes()
        with patch('lol_anki.staging.validate',return_value={'errors':0}) as validation,patch('lol_anki.generation.ai.AIClient._codex',side_effect=AssertionError('Export must not call a model')):
            report=export_saved(self.root,self.root/'build/all-saved.apkg')
        validation.assert_called_once()
        self.assertEqual(report['package']['cards'],6)
        self.assertEqual(report['generation_calls'],0); self.assertEqual(report['approval_changes'],0)
        self.assertEqual((self.root/'data/content/editorial.json').read_bytes(),before)

    def test_joint_authoring_assigns_existing_variant_identity_in_python(self):
        archive=ROOT/'data/drafts/aphelios/c6569ae4b284ca4203c1'
        packet=read_json(archive/'source-packet.json'); plan=read_json(archive/'kit-analysis.json')
        draft=read_json(archive/'ai-draft.json'); inventory=read_json(archive/'card-inventory.json')
        by_id={c['card_id']:c for c in draft['cards']}
        combined={**plan,'cards':[{'unit':u,'text':{k:v for k,v in by_id[i['card_id']].items() if k!='card_id'}} for u,i in zip(plan['cards'],inventory)]}
        _,units,output=split_joint(combined,packet)
        self.assertEqual(len(units),14)
        self.assertTrue(all(c['card_id'].startswith('champ:aphelios:') for c in units))
        self.assertEqual({u['card_id'] for u in units},{c['card_id'] for c in output['cards']})
        self.assertTrue(any(':ability_variant:q:moonshot:calibrum:' in c['card_id'] for c in units))
        for card in combined['cards']:
            for core in card['unit']['core_mechanics']: core['id']='model-reused-label'
        combined['cards'][0]['unit']['subject_id']='Aphelios'
        _,normalized,_=split_joint(combined,packet)
        core_ids=[c['id'] for u in normalized for c in u['core_mechanics']]
        self.assertEqual(len(core_ids),len(set(core_ids)))

    def test_staging_author_never_repairs_after_a_failed_first_call(self):
        archive=next((self.root/'data/drafts/annie').iterdir())
        with patch('lol_anki.generation.ai.AIClient._codex',side_effect=ModelError('Single failed author call')) as calls:
            with self.assertRaises(ModelError):
                author(self.root,{}, {'ai':{'provider':'codex','attempts':3}},False,archive)
            self.assertEqual(calls.call_count,1)
            with self.assertRaisesRegex(ModelError,'Persistent model-attempt budget'):
                author(self.root,{}, {'ai':{'provider':'codex','attempts':3}},False,archive)
            self.assertEqual(calls.call_count,1)

    def test_author_repair_budget_survives_process_resume(self):
        client=AIClient({'provider':'codex','attempts':2,'max_total_attempts':2},self.root/'cache')
        with patch.object(client,'_codex',side_effect=ModelError('Transport failure')) as calls,patch('lol_anki.generation.ai.time.sleep'):
            with self.assertRaises(ModelError): client.generate('test','test',{}, {'type':'object','properties':{},'required':[],'additionalProperties':False})
            self.assertEqual(calls.call_count,2)
            with self.assertRaisesRegex(ModelError,'Persistent model-attempt budget'): client.generate('test','test',{}, {'type':'object','properties':{},'required':[],'additionalProperties':False})
            self.assertEqual(calls.call_count,2)

    def test_unused_visual_metadata_is_not_learning_text_or_new_verification(self):
        archive=ROOT/'data/drafts/braum/8696ff171e68869fcc76'
        packet=read_json(archive/'source-packet.json'); raw=read_json(archive/'ai-draft.json')
        for card in raw['cards']:
            card['passive_visual']={'meaningful':True,'description':'UNVERIFIED cue metadata','source_ids':[]}
        normalized=standard_text(raw); check_draft(normalized,packet)
        self.assertEqual(normalized['cards'][0]['answer'],raw['cards'][0]['answer'])
        self.assertEqual(raw['cards'][0]['passive_visual']['description'],'UNVERIFIED cue metadata')
        normalized['cards'][0]['answer']='UNVERIFIED '+normalized['cards'][0]['answer']
        with self.assertRaisesRegex(ValueError,'QA marker'): check_draft(normalized,packet)

    def test_usage_limit_stops_without_spending_a_repair(self):
        client=AIClient({'provider':'codex','attempts':2,'max_total_attempts':2,'stop_on_usage_limit':True},self.root/'cache')
        with patch.object(client,'_codex',side_effect=ModelError('You have hit your usage limit')) as calls:
            with self.assertRaisesRegex(ModelError,'Provider usage limit'):
                client.generate('test','test',{}, {'type':'object','properties':{},'required':[],'additionalProperties':False})
            self.assertEqual(calls.call_count,1)
        with patch.object(client,'_codex',return_value=({}, {'usage':[]})) as resumed:
            client.generate('test','test',{}, {'type':'object','properties':{},'required':[],'additionalProperties':False})
            self.assertEqual(resumed.call_count,1)

    @unittest.skipUnless(importlib.util.find_spec('anki'),'Optional isolated Anki runtime unavailable')
    def test_staging_real_reimport_preserves_existing_and_new_scheduling(self):
        from anki.collection import Collection,ImportAnkiPackageRequest,ImportAnkiPackageOptions
        report=self.run_batch(); col=Collection(str(self.root/'collection.anki2'))
        try:
            def load(path):
                col.import_anki_package(ImportAnkiPackageRequest(package_path=str(path),options=ImportAnkiPackageOptions(with_scheduling=False,with_deck_configs=False,update_notes=0,update_notetypes=0)))
            load(Project(ROOT).legacy/'LoL_Anki_Pilot_6_Champions_v4_English.apkg')
            original=col.db.scalar('select min(id) from cards')
            col.db.execute('update cards set type=2,queue=2,due=123,ivl=17,reps=9,lapses=2 where id=?',original)
            columns='id,nid,type,queue,due,ivl,reps,lapses,factor'
            before=col.db.first('select '+columns+' from cards where id=?',original)
            load(self.root/report['output']); self.assertEqual(col.note_count(),70)
            added=col.db.scalar("select c.id from cards c join notes n on n.id=c.nid where n.sfld='champ:annie:q:recognize:L2'")
            col.db.execute('update cards set type=2,queue=2,due=234,ivl=21,reps=5 where id=?',added)
            new_before=col.db.first('select '+columns+' from cards where id=?',added)
            load(self.root/report['output']); self.assertEqual(col.note_count(),70)
            self.assertEqual(before,col.db.first('select '+columns+' from cards where id=?',original))
            self.assertEqual(new_before,col.db.first('select '+columns+' from cards where id=?',added))
        finally: col.close()

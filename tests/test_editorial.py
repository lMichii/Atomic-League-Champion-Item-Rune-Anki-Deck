"""Isolated explicit-review fixtures. Never approve or build additions in the real store."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
from lol_anki.editorial import Editorial
from lol_anki.editorial_media import MediaOverrides,variant_identity,inspect_media
from lol_anki.editorial_server import make_server
from lol_anki.io import canonical,digest,read_json,write_json
from lol_anki.media import V4_FILTER,gif_info
from lol_anki.package import build,read_collection,export_key
from lol_anki.identity import guid,stable_id
from lol_anki.v4 import FIELD_NAMES
from lol_anki.project import ROOT,Project
from lol_anki.review import apply_review
from lol_anki.validation import validate
from lol_anki.operations import project_operation,OperationBusy,run_pipeline
from lol_anki.editorial_export import EditorialExport

BRAUM='champ:201:q:recognize:L2'
MOONSHOT='champ:523:ability_variant:q:moonshot:calibrum:recognize:L2'
BINDING='champ:523:ability_variant:q:bindingeclipse:gravitum:recognize:L2'


class EditorialTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='ed-',dir=ROOT/'build/tests'); self.root=Path(self.temp.name)
        for name in ('pipeline.toml','pipeline.batch01.toml','pipeline.editorial.toml'):
            shutil.copy2(ROOT/name,self.root/name)
        for folder in ('LoL_Anki_Pilot_Project_v4_English','data/sources','data/batch01','data/drafts/braum','data/drafts/aphelios'):
            shutil.copytree(ROOT/folder,self.root/folder,copy_function=shutil.copy2,
                            ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        # Seed the isolated editorial profile from production, not the user's
        # promoted live manifest (whose editorial objects are outside this fixture).
        (self.root/'data/sources/editorial.json').unlink(missing_ok=True)
        for name in ('pilot.json','pilot.lock.json','production.json','production.lock.json'):
            dest=self.root/'data/content'/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/'data/content'/name,dest)
        self.editor=Editorial(self.root); self.project=self.editor.initialize()
        for champion in ('braum','aphelios'):
            index=read_json(self.root/'data/drafts'/champion/'index.json')
            self.editor.sync(self.root/'data/drafts'/champion/index['current_run'])
    def tearDown(self): self.temp.cleanup()

    def original(self,key,column='media_path'):
        record=self.editor.registry()['cards'][key]
        return self.root/record['source']['run']/record['working']['row'][column]

    def provenance(self,role='icon'):
        return {'origin':'isolated_test_fixture','source':'Real archived Riot/Wiki media used only in a temporary test project',
            'rights_holder':'Riot Games / upstream holder','license_reference':'https://www.riotgames.com/en/legal',
            'asset_version':'16.21.1','distribution_status':'pending','display_role':role}

    def content(self,key):
        record=self.editor.registry()['cards'][key]
        return self.editor.mutate(key,'content',{'status':'approved','reviewer':'Isolated test reviewer',
            'notes':'',
            'claims_checked':True,'cores_checked':True,'inferences_acknowledged':True,'warnings_acknowledged':True,
            'source_ids':[e['id'] for e in self.editor.packet(record)['excerpts']]})

    def media(self,key,fallback=False):
        return self.editor.mutate(key,'media',{'status':'approved','reviewer':'Isolated test reviewer',
            'notes':'',
            'matching_checked':True,'rights_acknowledged':True,'accept_static_fallback':fallback,
            'fallback_reason':'Matched real source icon accepted until the correct animation is supplied.' if fallback else ''})

    def promote(self,ids):
        result=self.editor.propose(ids,self.root/'build/review')
        apply_review(self.project,Path(result['proposal']),result['accept_token'],'Isolated final test reviewer')
        return result

    def test_import_and_regeneration_preserve_manual_text_and_approval_state(self):
        old=self.editor.registry()['cards'][BRAUM]
        self.editor.mutate(BRAUM,'edit',{'fields':{'counterplay':'Move out of the projectile path.'}})
        self.content(BRAUM); before=copy.deepcopy(self.editor.registry()['cards'][BRAUM])
        incoming=self.root/'build/regenerated'; incoming.mkdir(parents=True)
        source=self.root/old['source']['run']
        shutil.copy2(source/'source-packet.json',incoming/'source-packet.json')
        card=copy.deepcopy(old['working']); card['row']['answer']='A different generated suggestion that must not replace editorial work.'
        write_json(incoming/'cards.json',{'cards':[card]})
        result=self.editor.sync(incoming); after=self.editor.registry()['cards'][BRAUM]
        self.assertEqual(after['working'],before['working']); self.assertEqual(after['content_review'],before['content_review'])
        self.assertEqual(result['incoming_preserved'],[BRAUM]); self.assertIn('incoming_generated_revision',after)
        self.editor.mutate(BRAUM,'edit',{'fields':{'counterplay':'Avoid the incoming projectile.'}})
        self.assertEqual(self.editor.registry()['cards'][BRAUM]['content_review']['status'],'pending')
        self.assertEqual(len(self.project.content()['cards']),100)

    def test_state_exposes_only_pinned_claim_and_core_citations(self):
        cards=self.editor.state()['cards']
        overview=next(c for c in cards if c['champion']=='Braum' and c['working']['row']['slot']=='-')
        braum_e=next(c for c in cards if c['champion']=='Braum' and c['working']['row']['slot']=='E')
        self.assertEqual(overview['content_review']['status'],'pending')
        self.assertEqual(overview['source_labels']['riot:P'],'Riot: Concussive Blows')
        self.assertFalse(overview['core_mechanics'])
        self.assertEqual([core['id'] for core in braum_e['core_mechanics']],[
            'E.projectile_interception','E.first_hit_negation','E.directional_damage_reduction'])
        excerpt_ids={excerpt['id'] for excerpt in braum_e['evidence']}
        for core in braum_e['core_mechanics']:
            self.assertTrue(core['citations'])
            self.assertTrue({citation['source_id'] for citation in core['citations']}<=excerpt_ids)
        self.assertEqual(braum_e['content_review']['status'],'pending')

    def test_ordinary_approvals_allow_blank_notes_and_keep_review_audit_details(self):
        record=self.editor.registry()['cards'][BRAUM]
        before_text=record['working']['row']['counterplay']
        edited=self.editor.mutate(BRAUM,'edit',{'fields':{'counterplay':'Avoid the incoming projectile.'}})
        text_event=self.editor.registry()['events'][-1]
        self.assertEqual(text_event['changes']['counterplay'],{
            'before':before_text,'after':'Avoid the incoming projectile.'})
        self.assertNotEqual(text_event['before_record_sha256'],text_event['after_record_sha256'])
        packet=self.editor.packet(edited); selected=[e['id'] for e in packet['excerpts']]
        content=self.editor.mutate(BRAUM,'content',{'status':'approved','reviewer':'Local reviewer','notes':'',
            'source_ids':selected,'claims_checked':True,'cores_checked':True,
            'inferences_acknowledged':True,'warnings_acknowledged':True})
        self.assertEqual(content['content_review']['notes'],'')
        self.assertEqual(content['content_review']['reviewed_revision'],edited['revision'])
        self.assertEqual(content['content_review']['selected_source_ids'],sorted(selected))
        self.assertTrue(content['content_review']['at'])
        content_event=self.editor.registry()['events'][-1]
        self.assertEqual(content_event['selected_source_ids'],sorted(selected))
        self.assertTrue(all(content_event['attestations'].values()))
        _,signature,details=self.editor.effective(content)
        reviewed=self.editor.mutate(BRAUM,'media',{'status':'approved','reviewer':'Local reviewer','notes':'',
            'matching_checked':True,'rights_acknowledged':True,'accept_static_fallback':False})
        self.assertEqual(reviewed['media_review']['notes'],'')
        self.assertEqual(reviewed['media_review']['reviewed_revision'],content['revision'])
        self.assertEqual(reviewed['media_review']['media_sha256'],signature)
        self.assertEqual(reviewed['media_review']['media_file_hashes'],details['files'])
        media_event=self.editor.registry()['events'][-1]
        self.assertEqual(media_event['media_sha256'],signature)
        self.assertTrue(media_event['attestations']['matching_checked'])
        self.assertTrue(media_event['attestations']['rights_acknowledged'])
        self.assertFalse(media_event['attestations']['accept_static_fallback'])

    def test_notes_are_optional_but_names_and_static_fallback_consent_are_required(self):
        for action in ('content','media'):
            with self.subTest(action=action):
                result=self.editor.mutate(BRAUM,action,{'status':'rejected','reviewer':'Local reviewer'})
                self.assertEqual(result[action+'_review']['notes'],'')
                with self.assertRaisesRegex(ValueError,'Reviewer name'):
                    self.editor.mutate(BRAUM,action,{'status':'rejected','reviewer':''})
        with self.assertRaisesRegex(ValueError,'explicit static-fallback exception'):
            self.editor.mutate(MOONSHOT,'media',{'status':'approved','reviewer':'Local reviewer','notes':'',
                'matching_checked':True,'rights_acknowledged':True,'accept_static_fallback':False})
        result=self.editor.mutate(MOONSHOT,'media',{'status':'approved','reviewer':'Local reviewer',
            'matching_checked':True,'rights_acknowledged':True,'accept_static_fallback':True})
        self.assertEqual(result['media_review']['notes'],'')

    def test_combined_approval_is_atomic_and_records_both_decisions(self):
        record=self.editor.registry()['cards'][BRAUM]; packet=self.editor.packet(record)
        payload={'reviewer':'Local reviewer','notes':'','confirmation':True,
            'source_ids':[e['id'] for e in packet['excerpts']],
            'claims_checked':True,'cores_checked':True,'inferences_acknowledged':True,'warnings_acknowledged':True,
            'matching_checked':True,'rights_acknowledged':True,'accept_static_fallback':False}
        approved=self.editor.approve_content_and_media(BRAUM,payload,digest(canonical(record)))
        self.assertEqual(approved['revision'],record['revision']+1)
        self.assertEqual(approved['content_review']['status'],'approved')
        self.assertEqual(approved['media_review']['status'],'approved')
        self.assertEqual(approved['content_review']['reviewed_revision'],record['revision'])
        self.assertEqual(approved['media_review']['reviewed_revision'],record['revision'])
        self.assertEqual(approved['content_review']['notes'],'')
        self.assertEqual(approved['media_review']['media_sha256'],self.editor.effective(approved)[1])
        self.assertTrue(approved['media_review']['media_file_hashes'])
        event=self.editor.registry()['events'][-1]
        self.assertEqual(event['action'],'combined_approval')
        self.assertEqual(event['selected_source_ids'],sorted(payload['source_ids']))
        self.assertEqual(event['media_file_hashes'],approved['media_review']['media_file_hashes'])
        self.assertTrue(all(value for key,value in event['attestations'].items() if key!='accept_static_fallback'))
        self.assertFalse(event['attestations']['accept_static_fallback'])

        blocked=self.editor.registry()['cards'][MOONSHOT]; packet=self.editor.packet(blocked)
        self.editor.mutate(MOONSHOT,'content',{'status':'approved','reviewer':'Local reviewer','notes':'',
            'source_ids':[e['id'] for e in packet['excerpts']], 'claims_checked':True,'cores_checked':True,
            'inferences_acknowledged':True,'warnings_acknowledged':True})
        blocked=self.editor.registry()['cards'][MOONSHOT]; before=copy.deepcopy(blocked)
        event_count=len(self.editor.registry()['events']); packet=self.editor.packet(blocked)
        invalid={**payload,'source_ids':[e['id'] for e in packet['excerpts']],
                 'accept_static_fallback':False,'fallback_reason':''}
        with self.assertRaisesRegex(ValueError,'static-fallback exception'):
            self.editor.approve_content_and_media(MOONSHOT,invalid,digest(canonical(blocked)))
        after=self.editor.registry()
        self.assertEqual(after['cards'][MOONSHOT],before)
        self.assertEqual(len(after['events']),event_count)

    def test_override_precedence_and_exact_variant_matching_are_not_filename_based(self):
        card=self.editor.override_card(MOONSHOT); store=self.editor.overrides
        target={'kind':'variant','identity':variant_identity(card)}
        renamed=self.root/'recorded-other-name.png'; shutil.copy2(self.original(MOONSHOT),renamed)
        record=store.ingest(card,renamed,target,self.provenance())
        self.assertIsNone(store.select(card))
        with self.assertRaisesRegex(ValueError,'Named reviewer required'):
            store.approve(record['id'],card,'','')
        store.approve(record['id'],card,'Isolated media reviewer','')
        self.assertEqual(store.select(card)['id'],record['id'])
        self.assertIsNone(store.select(self.editor.override_card(BINDING)))
        with self.assertRaises(ValueError): store.ingest(self.editor.override_card(BRAUM),renamed,{'kind':'variant','identity':None},self.provenance())
        with self.assertRaisesRegex(ValueError,'target'): store.ingest(self.editor.override_card(BINDING),renamed,target,self.provenance())
        specific=store.ingest(card,renamed,{'kind':'card','card_id':MOONSHOT},self.provenance())
        store.approve(specific['id'],card,'Isolated media reviewer','Explicit card-specific matching overrides the variant-wide asset.')
        self.assertEqual(store.select(card)['id'],specific['id'])
        store.ingest(card,renamed,target,self.provenance())
        self.assertEqual(store.select(card)['id'],specific['id'])
        working=self.editor.registry()['cards'][MOONSHOT]
        self.assertEqual(self.editor.effective(working)[2]['selection'],'manually_approved_override')

    def test_generic_slot_video_and_corrupt_or_modified_media_are_rejected(self):
        card=self.editor.override_card(MOONSHOT)
        record=self.editor.registry()['cards'][MOONSHOT]
        assets=read_json(self.root/record['source']['run']/'assets.json')
        generic=self.root/record['source']['run']/assets['abilities']['Q']['video']['path']
        with self.assertRaisesRegex(ValueError,'Generic slot'): self.editor.overrides.ingest(card,generic,{'kind':'card','card_id':MOONSHOT},self.provenance('animation'))
        corrupt=self.root/'bad.png'; corrupt.write_bytes(b'\x89PNG\r\n\x1a\ninvalid')
        with self.assertRaises((ValueError,subprocess.SubprocessError)): inspect_media(corrupt)
        media=self.editor.overrides.ingest(card,self.original(MOONSHOT),{'kind':'card','card_id':MOONSHOT},self.provenance())
        self.editor.overrides.approve(media['id'],card,'Test reviewer','Checked this exact variant image in the isolated fixture.')
        (self.root/media['path']).write_bytes(b'changed media')
        with self.assertRaisesRegex(ValueError,'integrity'): self.editor.overrides.select(card)

    def test_answer_icons_and_passive_cues_have_independent_identity_bound_roles(self):
        card=self.editor.override_card(BRAUM); source=self.original(BRAUM,'icon_path')
        override=self.editor.overrides.ingest(card,source,{'kind':'card','card_id':BRAUM,'role':'icon'},self.provenance())
        self.editor.overrides.approve(override['id'],card,'Role test reviewer','Checked the exact answer icon without changing the front animation.')
        self.assertIsNone(self.editor.overrides.select(card))
        self.assertEqual(self.editor.overrides.select(card,'icon')['id'],override['id'])
        effective,_,media=self.editor.effective(self.editor.registry()['cards'][BRAUM])
        self.assertEqual(effective['row']['media_type'],'gif')
        self.assertEqual(media['overrides_by_role'],{'icon':override['id']})
        p='champ:201:p:recognize:L2'; record=self.editor.registry()['cards'][p]
        assets=read_json(self.root/record['source']['run']/'assets.json')
        video=self.root/record['source']['run']/assets['abilities']['P']['video']['path']
        passive=self.editor.override_card(p)
        cue=self.editor.overrides.ingest(passive,video,{'kind':'card','card_id':p},self.provenance('supplemental'))
        self.assertEqual(cue['target']['role'],'cue')
        self.editor.overrides.approve(cue['id'],passive,'Role test reviewer','Reviewed the passive demonstration as a supplemental visual cue.')
        effective,_,_=self.editor.effective(record)
        self.assertEqual(effective['row']['media_type'],'icon')
        self.assertTrue(effective['row']['visual_cue_media_path'])

    def test_local_mp4_is_preserved_and_converted_with_locked_gif_recipe(self):
        record=self.editor.registry()['cards'][BRAUM]; run=self.root/record['source']['run']
        assets=read_json(run/'assets.json'); source=run/assets['abilities']['Q']['video']['path']
        mp4=self.root/'local-clip.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-c:v','libx264','-an',str(mp4)],check=True,capture_output=True)
        card=self.editor.override_card(BRAUM)
        r=self.editor.overrides.ingest(card,mp4,{'kind':'card','card_id':BRAUM},self.provenance('animation'))
        self.assertEqual((self.root/r['original_path']).read_bytes(),mp4.read_bytes())
        self.assertEqual(r['recipe']['filter'],V4_FILTER)
        self.assertEqual(gif_info((self.root/r['path']).read_bytes())['loop'],0)
        self.assertEqual(r['output_info']['full_decode'],'passed')
        self.assertEqual(r['review']['status'],'pending')

    def test_partial_approval_proposal_and_stale_decisions_fail_closed(self):
        self.content(MOONSHOT)
        with self.assertRaises(ValueError): self.editor.propose([MOONSHOT],self.root/'build/blocked')
        with self.assertRaisesRegex(ValueError,'fallback'): self.media(MOONSHOT)
        self.media(MOONSHOT,True)
        result=self.editor.propose([MOONSHOT],self.root/'build/review')
        self.assertEqual(len(self.project.content()['cards']),100)
        self.editor.mutate(MOONSHOT,'edit',{'fields':{'counterplay':'Dodge the incoming shot.'}})
        with self.assertRaisesRegex(ValueError,'decisions changed'): apply_review(self.project,Path(result['proposal']),result['accept_token'],'Test reviewer')
        self.assertEqual(len(self.project.content()['cards']),100)

    def test_two_q_variants_can_be_approved_without_publishing_the_rest_of_a_champion(self):
        before=copy.deepcopy(self.project.content()['cards'])
        for key in (MOONSHOT,BINDING): self.content(key); self.media(key,True)
        self.promote([MOONSHOT,BINDING])
        self.assertEqual(self.project.content()['cards'][:100],before)
        self.assertEqual(len(self.project.content()['cards']),102)
        report=validate(self.project)
        self.assertEqual(report['errors'],0,[f for f in report['findings'] if f['severity']=='error'])
        self.assertTrue(any(f['code']=='partial_champion_approval' for f in report['findings']))
        self.assertTrue(any(f['code']=='unknown_gameplay_patch' for f in report['findings']))
        self.assertTrue(any(f['code']=='reviewed_static_fallback' for f in report['findings']))
        self.assertEqual(sum(r['content_review']['status']=='approved' for r in self.editor.registry()['cards'].values()),2)

    def test_new_champion_exports_use_readable_slugs_without_rewriting_reviews(self):
        baseline=self.root/'build/baseline.apkg'
        build(Project(self.root,profile='batch01'),baseline)
        ids=[key for key,r in self.editor.registry()['cards'].items() if r['champion']=='Braum']
        for key in ids: self.content(key); self.media(key)
        self.promote(ids)
        before={str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'data').rglob('*') if p.is_file()}
        output=self.root/'build/readable.apkg'; build(self.project,output)
        self.assertEqual(before,{str(p.relative_to(self.root)):p.read_bytes() for p in (self.root/'data').rglob('*') if p.is_file()})
        original,published=read_collection(baseline),read_collection(output)
        try:
            expected={'champ:braum:overview:L1',*(f'champ:braum:{s}:recognize:L2' for s in 'pqwer')}
            rows=published.execute('select id,guid,flds,sfld from notes').fetchall()
            actual={r[3] for r in rows if r[3].startswith('champ:braum:')}
            self.assertEqual(actual,expected)
            self.assertFalse(any(r[3].startswith('champ:201:') for r in rows))
            for nid,g,fields,key in rows:
                self.assertEqual(fields.split('\x1f')[FIELD_NAMES.index('Key')],key)
                self.assertEqual(nid,stable_id(key,1800000000000)); self.assertEqual(g,guid(key))
                self.assertEqual(published.execute('select id from cards where nid=?',(nid,)).fetchone()[0],stable_id(key,2300000000000))
            # Every baseline note/card stays identical, including Morgana's readable IDs.
            for table in ('notes','cards'):
                for row in original.execute('select * from '+table):
                    self.assertEqual(row,published.execute('select * from '+table+' where id=?',(row[0],)).fetchone())
            self.assertIn('champ:morgana:q:recognize:L2',{r[3] for r in rows})
            # Numeric source/review handles and all authored learning fields survive.
            for card in self.project.content()['cards'][100:]:
                self.assertTrue(card['id'].startswith('champ:201:'))
                self.assertEqual(card['entity_id'],'champ:201')
                key=export_key(card,self.root)
                values=published.execute('select flds from notes where sfld=?',(key,)).fetchone()[0].split('\x1f')
                self.assertEqual(values[FIELD_NAMES.index('Ability')],card['row']['ability'])
            # Generic projection retains nonstandard context; it is not Braum-specific.
            record=self.editor.registry()['cards'][MOONSHOT]
            variant=copy.deepcopy(record['working'])
            variant['editorial_review']={'source_packet_path':record['source']['run']+'/source-packet.json'}
            self.assertEqual(export_key(variant,self.root),'champ:aphelios:ability_variant:q:moonshot:calibrum:recognize:L2')
        finally: original.close(); published.close()

    def test_local_review_api_rejects_cross_origin_stale_and_unattested_approval(self):
        server=make_server(self.root,0); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            self.assertIn(b'League card review',urllib.request.urlopen(url).read())
            record=self.editor.registry()['cards'][BRAUM]
            payload={'action':'content','id':BRAUM,'expected':digest(canonical(record)),'status':'approved','reviewer':'Test','notes':'Reviewed fixture content.'}
            def request(headers): return urllib.request.urlopen(urllib.request.Request(url+'/api/action',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json',**headers}))
            with self.assertRaises(urllib.error.HTTPError) as caught: request({})
            self.assertEqual(caught.exception.code,403)
            with self.assertRaises(urllib.error.HTTPError): request({'X-Review-Token':server.review_nonce,'Origin':'http://malicious.example'})
            with self.assertRaises(urllib.error.HTTPError): request({'X-Review-Token':server.review_nonce})
            edit={**payload,'action':'edit','fields':{'counterplay':'Avoid the incoming projectile.'}}
            req=urllib.request.Request(url+'/api/action',data=json.dumps(edit).encode(),headers={'Content-Type':'application/json','X-Review-Token':server.review_nonce})
            self.assertEqual(urllib.request.urlopen(req).status,200)
            with self.assertRaises(urllib.error.HTTPError) as stale: request({'X-Review-Token':server.review_nonce})
            self.assertIn(b'Stale review page',stale.exception.read())
            self.assertEqual(self.editor.registry()['cards'][BRAUM]['content_review']['status'],'pending')
        finally: server.shutdown(); server.server_close(); thread.join()

    def test_combined_review_http_action_is_atomic_and_idempotent(self):
        page=(ROOT/'lol_anki/editorial_ui.html').read_text(encoding='utf-8')
        self.assertIn("await act('approve-content-and-media'",page)
        server=make_server(self.root,0); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            record=self.editor.registry()['cards'][BRAUM]
            payload={'action':'approve-content-and-media','id':BRAUM,'expected':digest(canonical(record)),
                     'reviewer':'Isolated reviewer','notes':'','confirmation':True,
                     'source_ids':[e['id'] for e in self.editor.packet(record)['excerpts']],
                     'claims_checked':True,'cores_checked':True,'inferences_acknowledged':True,
                     'warnings_acknowledged':True,'matching_checked':True,'rights_acknowledged':True}
            def post(body):
                request=urllib.request.Request(url+'/api/action',data=json.dumps(body).encode(),
                    headers={'Content-Type':'application/json','X-Review-Token':server.review_nonce})
                try:
                    with urllib.request.urlopen(request) as response: return response.status,json.load(response)
                except urllib.error.HTTPError as error: return error.code,json.load(error)
            before=self.editor.registry(); count=len(before['events'])
            status,result=post({**payload,'confirmation':False})
            self.assertEqual(status,400); self.assertIn('Confirm',result['error'])
            self.assertEqual(self.editor.registry(),before)
            status,result=post({**payload,'expected':'stale'})
            self.assertEqual(status,400); self.assertIn('Stale review page',result['error'])
            self.assertEqual(self.editor.registry(),before)
            status,result=post(payload)
            self.assertEqual(status,200,result)
            approved=result['result']
            self.assertEqual(approved['content_review']['status'],'approved')
            self.assertEqual(approved['media_review']['status'],'approved')
            self.assertEqual(approved['content_review']['notes'],'')
            self.assertEqual(approved['media_review']['reviewed_revision'],record['revision'])
            self.assertEqual(len(self.editor.registry()['events']),count+1)
            status,result=post({**payload,'expected':digest(canonical(approved))})
            self.assertEqual(status,200,result)
            self.assertEqual(result['result'],approved)
            self.assertEqual(len(self.editor.registry()['events']),count+1)
            state=json.load(urllib.request.urlopen(url+'/api/state'))
            shown=next(card for card in state['cards'] if card['id']==BRAUM)
            self.assertEqual(shown['content_review']['status'],'approved')
            self.assertEqual(shown['media_review']['status'],'approved')

            invalid_key=next(key for key,card in self.editor.registry()['cards'].items()
                             if card['working']['row']['champion']=='Braum' and card['working']['row']['slot']=='E')
            data=self.editor.registry(); data['cards'][invalid_key]['working']['row']['media_path']=''
            write_json(self.editor.path,data)
            invalid=data['cards'][invalid_key]
            status,result=post({**payload,'id':invalid_key,'expected':digest(canonical(invalid)),
                                'source_ids':[e['id'] for e in self.editor.packet(invalid)['excerpts']]})
            self.assertEqual(status,400); self.assertIn('Real front media',result['error'])
            self.assertEqual(self.editor.registry()['cards'][invalid_key],invalid)
            self.assertEqual(len(self.editor.registry()['events']),count+1)
        finally: server.shutdown(); server.server_close(); thread.join()

    def start_review_server(self):
        server=make_server(self.root,0)
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        def close(): server.shutdown(); server.server_close(); thread.join()
        self.addCleanup(close)
        url=f'http://127.0.0.1:{server.server_port}'
        def post(body):
            request=urllib.request.Request(url+'/api/action',data=json.dumps(body).encode(),
                headers={'Content-Type':'application/json','X-Review-Token':server.review_nonce})
            try:
                with urllib.request.urlopen(request) as response: return response.status,json.load(response)
            except urllib.error.HTTPError as ex: return ex.code,json.load(ex)
        return server,url,post

    def test_http_full_proposal_inspect_apply_build_download_with_blank_notes(self):
        frozen=copy.deepcopy(self.project.content()['cards'])
        ids=[k for k,r in self.editor.registry()['cards'].items() if r['champion']=='Braum']
        for key in ids: self.content(key); self.media(key)
        approvals=copy.deepcopy(self.editor.registry())
        server,url,post=self.start_review_server()
        create={'action':'propose','ids':ids,'request_id':'fixture-create-request'}
        status,result=post(create)
        self.assertEqual(status,200,result); p=result['result']; key=p['id']
        self.assertEqual(post(create),(200,result))
        self.assertEqual(post({**create,'ids':[BRAUM]})[0],400)
        before={n:self.project.path(n).read_bytes() for n in ('content','sources','lock')}
        review_count=len(read_json(self.project.path('lock'))['reviews'])
        status,error=post({'action':'build-editorial','proposal_id':key,'reviewer':'Fixture'})
        self.assertEqual(status,400)
        apply={'action':'apply-proposal','proposal_id':key,'accept_token':p['accept_token'],
               'reviewer':'Fixture final reviewer','confirmed':True}
        self.assertEqual(post(apply)[0],400) # Session inspection is mandatory.
        inspected=json.load(urllib.request.urlopen(url+'/api/proposal?id='+key))
        self.assertEqual(inspected['before_count'],100); self.assertEqual(inspected['after_count'],106)
        self.assertEqual(inspected['groups'],{'added':sorted(ids),'modified':[],'removed':[]})
        self.assertEqual(inspected['validation']['errors'],0)
        self.assertTrue(inspected['validation']['warnings'])
        self.assertTrue(any(d['field']=='answer' for c in inspected['cards'] for d in c['diffs']))
        self.assertIn(b'proposed',urllib.request.urlopen(url+inspected['diff_url']).read())
        apply['inspection_token']=inspected['inspection_token']
        for change in ({'reviewer':''},{'confirmed':False},{'accept_token':'wrong'}):
            self.assertEqual(post({**apply,**change})[0],400)
            self.assertEqual(before,{n:self.project.path(n).read_bytes() for n in before})
        status,result=post(apply); self.assertEqual(status,200,result)
        self.assertEqual(result['result']['status'],'applied')
        self.assertEqual(result['result']['apply_result']['review']['notes'],'')
        self.assertEqual(len(self.project.content()['cards']),106)
        self.assertEqual(self.project.content()['cards'][:100],frozen)
        self.assertEqual(self.editor.registry(),approvals)
        self.assertEqual(post(apply)[0],400) # No second receipt or revision.
        self.assertEqual(len(read_json(self.project.path('lock'))['reviews']),review_count+1)
        status,result=post({'action':'build-editorial','proposal_id':key,'reviewer':'Fixture export reviewer'})
        self.assertEqual(status,200,result); exported=result['result']; package=exported['build_result']
        self.assertEqual(package['package']['cards'],106); self.assertEqual(package['validation']['errors'],0)
        self.assertTrue(Path(package['output']).is_relative_to(self.root/'build/editorial/exports'))
        self.assertFalse((self.root/'build/LoL_Reviewed.apkg').exists())
        with urllib.request.urlopen(url+exported['download_url']) as download:
            self.assertIn('attachment',download.headers['Content-Disposition'])
            self.assertEqual(digest(download.read()),package['package']['sha256'])
        self.assertEqual(post({'action':'build-editorial','proposal_id':key,'reviewer':'Fixture'})[0],400)
        self.assertEqual(self.project.content()['cards'][:100],frozen)
        self.assertEqual(self.editor.registry(),approvals)
        history=json.load(urllib.request.urlopen(url+'/api/workflow'))
        self.assertEqual(history['proposals'][0]['status'],'built')
        self.assertNotIn('proposal_path',history['proposals'][0])
        # Modified additions have real before/after text, preserving the baseline.
        self.editor.mutate(BRAUM,'edit',{'fields':{'counterplay':'Move out of the projectile path.'}})
        self.content(BRAUM)
        changed=server.workflow.create([BRAUM]); summary=server.workflow.inspect(changed['id'])
        self.assertEqual(summary['groups']['modified'],[BRAUM])
        diff=next(d for d in summary['cards'][0]['diffs'] if d['field']=='counterplay')
        self.assertTrue(diff['before']); self.assertEqual(diff['after'],'Move out of the projectile path.')

    def test_export_stale_inputs_hashes_and_concurrent_operations_fail_closed(self):
        self.content(BRAUM); self.media(BRAUM)
        server,url,post=self.start_review_server()
        status,result=post({'action':'propose','ids':[BRAUM]}); self.assertEqual(status,200)
        p=result['result']; seen=server.workflow.inspect(p['id'])
        apply={'action':'apply-proposal','proposal_id':p['id'],'accept_token':p['accept_token'],
               'inspection_token':seen['inspection_token'],'reviewer':'Fixture','confirmed':True}
        # Changing the exact proposal bytes cannot be accepted with the old hash.
        record=server.workflow.record(p['id']); path=self.root/record['proposal_path']; original=path.read_bytes()
        tampered=read_json(path); tampered['changed_ids']=[]; write_json(path,tampered)
        self.assertEqual(post(apply)[0],400); path.write_bytes(original)
        # Decisions made after inspection invalidate the existing proposal.
        self.editor.mutate(BRAUM,'edit',{'fields':{'counterplay':'Move out of the projectile path.'}})
        self.assertEqual(post(apply)[0],400); self.assertEqual(len(self.project.content()['cards']),100)
        self.content(BRAUM)
        result=server.workflow.create([BRAUM]); seen=server.workflow.inspect(result['id'])
        server.workflow.apply(result['id'],result['accept_token'],seen['inspection_token'],'Fixture',True)
        # A failed build stays applied and is retryable; never offers a broken download.
        with patch('lol_anki.editorial_export.run_pipeline',side_effect=ValueError('Fixture build failure')):
            status,error=post({'action':'build-editorial','proposal_id':result['id'],'reviewer':'Fixture'})
        self.assertEqual(status,400); self.assertEqual(server.workflow.record(result['id'])['status'],'applied')
        self.assertIn('Fixture build failure',error['error'])
        # A later store change blocks an export tied to an earlier approved state.
        lock=read_json(self.project.path('lock')); lock['reviews'].append({'test':'changed lock'})
        write_json(self.project.path('lock'),lock)
        status,error=post({'action':'build-editorial','proposal_id':result['id'],'reviewer':'Fixture'})
        self.assertEqual(status,400); self.assertIn('store changed',error['error'])
        # A second operation is rejected, not queued to apply unexpected content.
        entered=threading.Event(); release=threading.Event()
        def hold():
            with project_operation(self.root): entered.set(); release.wait(10)
        thread=threading.Thread(target=hold); thread.start(); self.assertTrue(entered.wait(5))
        try:
            status,error=post({'action':'propose','ids':[BRAUM]})
            self.assertEqual(status,409); self.assertIn('operation is running',error['error'])
            with self.assertRaises(OperationBusy): run_pipeline(self.project)
            script="import sys\nsys.path.insert(0,sys.argv[1])\nfrom lol_anki.operations import project_operation,OperationBusy\ntry:\n with project_operation(sys.argv[2]): pass\nexcept OperationBusy:\n sys.exit(23)\n"
            child=subprocess.run([sys.executable,'-c',script,str(ROOT),str(self.root)],capture_output=True)
            self.assertEqual(child.returncode,23,child.stderr)
        finally: release.set(); thread.join()

    @unittest.skipUnless(os.environ.get('LEAGUE_EXPORT_BROWSER_CHECK')=='1','Optional Playwright/browser workflow check')
    def test_isolated_real_browser_proposal_to_download(self):
        before=copy.deepcopy(self.project.content()['cards'])
        for key,record in self.editor.registry()['cards'].items():
            if record['champion']=='Braum': self.content(key); self.media(key)
        reviews=copy.deepcopy(self.editor.registry())
        server,url,post=self.start_review_server()
        result=subprocess.run(['node',str(ROOT/'tools/check_editorial_export_ui.cjs'),url,str(self.root)],
                              capture_output=True,text=True,encoding='utf-8',timeout=180)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(self.project.content()['cards'][:100],before)
        self.assertEqual(len(self.project.content()['cards']),106)
        self.assertEqual(self.editor.registry(),reviews)

    @unittest.skipUnless(importlib.util.find_spec('anki'),'Optional Anki importer runtime required')
    def test_real_import_additions_and_reviewed_edits_preserve_all_schedules(self):
        from anki.collection import Collection,ImportAnkiPackageRequest,ImportAnkiPackageOptions
        baseline=self.root/'build/baseline.apkg'; build(Project(self.root,profile='batch01'),baseline)
        for key in (BRAUM,MOONSHOT,BINDING): self.content(key); self.media(key,key!=BRAUM)
        self.promote([BRAUM,MOONSHOT,BINDING]); package=self.root/'build/reviewed.apkg'; build(self.project,package)
        old=read_collection(baseline); new=read_collection(package)
        try:
            for row in old.execute('select id,guid,mid,mod,tags,flds from notes'):
                self.assertEqual(row,new.execute('select id,guid,mid,mod,tags,flds from notes where id=?',(row[0],)).fetchone())
            old_model=json.loads(old.execute('select models from col').fetchone()[0])['2042610311001']
            new_model=json.loads(new.execute('select models from col').fetchone()[0])['2042610311001']
            for key in ('css','tmpls','flds','req'): self.assertEqual(old_model[key],new_model[key])
        finally: old.close(); new.close()
        previous=Path.cwd(); col=None
        try:
            col=Collection(str(self.root/'build/isolated.anki2'))
            def load(path): col.import_anki_package(ImportAnkiPackageRequest(package_path=str(path),options=ImportAnkiPackageOptions(with_scheduling=False,with_deck_configs=False,update_notes=0,update_notetypes=0)))
            load(baseline)
            for i,cid in enumerate(col.db.list('select id from cards order by id')):
                col.db.execute('update cards set type=2,queue=2,due=?,ivl=37,reps=11,lapses=3 where id=?',i+10,cid)
                col.db.execute('insert into revlog (id,cid,usn,ease,ivl,lastIvl,factor,time,type) values (?,?,?,?,?,?,?,?,?)',1790000000000+i,cid,-1,3,37,21,2400,1200,1)
            columns='id,nid,type,queue,due,ivl,reps,lapses,factor,left,odue,odid,flags,data'
            schedules={r[0]:r for r in col.db.all('select '+columns+' from cards')}
            logs=col.db.all('select * from revlog order by id')
            load(package); load(package); self.assertEqual(col.note_count(),103)
            for cid,row in schedules.items(): self.assertEqual(row,col.db.first('select '+columns+' from cards where id=?',cid))
            self.assertEqual(logs,col.db.all('select * from revlog order by id'))
            for i,cid in enumerate(col.db.list('select id from cards order by id')):
                if cid not in schedules:
                    col.db.execute('update cards set type=2,queue=2,due=73,ivl=91,reps=23,lapses=4 where id=?',cid)
                    col.db.execute('insert into revlog (id,cid,usn,ease,ivl,lastIvl,factor,time,type) values (?,?,?,?,?,?,?,?,?)',1790000000500+i,cid,-1,3,91,37,2400,1200,1)
            all_schedules={r[0]:r for r in col.db.all('select '+columns+' from cards')}
            all_logs=col.db.all('select * from revlog order by id')
            self.editor.mutate(BRAUM,'edit',{'fields':{'counterplay':'Move out of the incoming projectile path.'}})
            self.content(BRAUM); self.promote([BRAUM]); build(self.project,package); load(package)
            self.assertEqual(col.note_count(),103)
            for cid,row in all_schedules.items(): self.assertEqual(row,col.db.first('select '+columns+' from cards where id=?',cid))
            self.assertEqual(all_logs,col.db.all('select * from revlog order by id'))
            self.assertTrue(any('Move out of the incoming projectile path.' in f for f in col.db.list('select flds from notes')))
        finally:
            if col: col.close()
            os.chdir(previous)

"""Real nonstandard-kit fixture: source/context coverage, media safety and replay."""
import copy
from collections import Counter
from pathlib import Path
import re
import unittest
from unittest.mock import patch
from lol_anki.generation.archive import restore_inputs
from lol_anki.generation.contracts import normalized,numeric_tokens
from lol_anki.generation.evidence import readable
from lol_anki.generation.kit_contracts import (validate_plan,validate_text,validate_support,card_key)
from lol_anki.generation.presentation import check_learning_row,QA_MARKER
from lol_anki.generation.workflow import generate,approved_fingerprints
from lol_anki.identity import guid,stable_id
from lol_anki.io import read_json,digest,canonical
from lol_anki.media import gif_info
from lol_anki.project import ROOT,Project
from lol_anki.review import apply_review
from lol_anki.v4 import CSS,FIELD_NAMES

ARCHIVE=ROOT/'data/drafts/aphelios'/read_json(ROOT/'data/drafts/aphelios/index.json')['current_run']


class ApheliosGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(ARCHIVE/'source-packet.json')
        cls.plan=read_json(ARCHIVE/'kit-analysis.json')
        cls.inventory=read_json(ARCHIVE/'card-inventory.json')
        cls.cards=read_json(ARCHIVE/'cards.json')['cards']
        cls.draft=read_json(ARCHIVE/'ai-draft.json')
        cls.verifier=read_json(ARCHIVE/'ai-verification.json')
        cls.assets=read_json(ARCHIVE/'assets.json')
        cls.qa=read_json(ARCHIVE/'qa.json')

    def test_actual_kit_coverage_without_five_conventional_spells(self):
        validate_plan(self.plan,self.packet)
        self.assertEqual(len(self.packet['kit_sections']),15)
        self.assertEqual(len({s['id'] for s in self.packet['kit_sections']}),15)
        self.assertEqual(len(self.inventory),14)
        self.assertEqual(sum(len(c['core_mechanics']) for c in self.inventory),28)
        self.assertEqual(Counter(c['kind'] for c in self.inventory),
            Counter(overview=1,system=1,weapon=5,ability_variant=5,ability=2))
        self.assertEqual(next(s for s in self.plan['slots'] if s['slot']=='E')['role'],'indicator')
        self.assertFalse(any(c['row']['slot']=='E' for c in self.cards))
        self.assertTrue(all(c['purpose'] for c in self.inventory))
        self.assertEqual({c['subject_id']:c['context_id'] for c in self.inventory if c['kind']=='ability_variant'},
            {'wiki:moonshot':'wiki:calibrum','wiki:onslaught':'wiki:severum','wiki:bindingeclipse':'wiki:gravitum',
             'wiki:duskwave':'wiki:infernum','wiki:sentry':'wiki:crescendum'})
        self.assertIn('unconventional_leveling',self.plan['features'])
        self.assertTrue(self.plan['relationships'])

    def test_sources_claims_core_completeness_and_clean_learning_language(self):
        validate_text(self.draft,self.packet,self.inventory)
        validate_support(self.verifier,self.packet,self.inventory,self.draft)
        self.assertTrue(self.verifier['kit_complete']); self.assertEqual(self.verifier['omitted_topics'],[])
        self.assertTrue(all(c['source_supported_draft'] and not c['missing_supported_core_ids'] for c in self.qa['cards']))
        for resource in self.packet['resources']:
            self.assertEqual(digest((ARCHIVE/'sources'/resource['sha256']).read_bytes()),resource['sha256'])
        overview=next(c for c in self.cards if c['row']['level']=='L1')
        self.assertEqual(overview['row']['question'],'What can this champion do?')
        self.assertEqual(overview['row']['build_focus'],'AD')
        self.assertRegex(overview['row']['answer'].lower(),r'dash|blink')
        self.assertTrue(any(f['basis']=='exhaustive_kit_inference' for f in overview['evidence']['claims']))
        system=next(c['row']['answer'].lower() for c in self.cards if c['learning_unit']['kind']=='system')
        self.assertRegex(system,r'ammo|ammunition'); self.assertIn('skill points',system)
        for stat in ('attack damage','attack speed','lethality'): self.assertIn(stat,system)
        ultimate=next(c['row']['answer'].lower() for c in self.cards if c['row']['slot']=='R')
        for name in ('calibrum','severum','gravitum','infernum','crescendum'): self.assertIn(name,ultimate)
        for c in self.cards:
            check_learning_row(c['row'])
            self.assertEqual(c['row']['patch'],''); self.assertEqual(c['row']['review_status'],'')
            self.assertIsNone(c['versioning']['verified_game_patch'])
            self.assertEqual(c['versioning']['asset_version'],self.packet['versions']['ddragon'])
            self.assertEqual(c['pedagogy']['counterplay_basis'],'source_grounded_inference')
            self.assertEqual(c['content_status'],'draft'); self.assertEqual(c['qa_status'],'needs_review')

    def test_real_media_and_variant_to_weapon_matching(self):
        for record in self.assets['files']:
            blob=(ARCHIVE/record['path']).read_bytes()
            self.assertEqual(digest(blob),record['sha256'])
            self.assertTrue(record['source_url'].startswith(('https://ddragon.leagueoflegends.com/',
                'https://raw.communitydragon.org/','https://wiki.leagueoflegends.com/',
                'https://d28xe8vt774jo5.cloudfront.net/')))
            if record['kind']=='gif':
                info=gif_info(blob); self.assertGreater(info['frames'],1); self.assertEqual(info['loop'],0)
        units={c['card_id']:c for c in self.inventory}; sections={s['id']:s for s in self.packet['kit_sections']}
        for binding in self.assets['bindings']:
            unit=units[binding['card_id']]
            self.assertTrue(binding['icon']); self.assertFalse(binding['human_verified'])
            self.assertTrue(binding['manual_weapon_ability_matching_required'])
            if unit['kind']=='ability_variant':
                self.assertIsNone(binding['gif'])
                self.assertEqual(binding['icon']['source_url'],sections[unit['subject_id']]['icon_url'])
                self.assertTrue(binding['unresolved'])
                self.assertTrue(binding['slot_clip_candidate'])
        for slot in ('W','R'):
            card=next(c for c in self.cards if c['row']['slot']==slot)
            self.assertEqual(card['row']['media_type'],'gif')
        self.assertNotIn(self.assets['abilities']['Q']['gif']['path'].removeprefix('media/'),self.qa['media_references'])
        self.assertEqual(len(self.qa['passive_frame_evidence']),4)
        self.assertEqual(read_json(ARCHIVE/'media-report.json')['bindings'],self.assets['bindings'])
        self.assertTrue(all(f['severity']=='info' for f in self.assets['findings'] if f['code']=='noncombat_slot_without_animation'))

    def test_unique_v4_previews_and_hidden_qa_metadata(self):
        self.assertEqual(len(list((ARCHIVE/'previews').glob('*.html'))),15)
        self.assertEqual(len({c['preview'] for c in self.qa['cards']}),14)
        for c in self.qa['cards']:
            page=(ARCHIVE/c['preview']).read_text(encoding='utf-8')
            legacy_css=CSS.replace('.bottom a{color:inherit;text-decoration:none;border-bottom:1px solid #43484e}\n.bottom a:hover{color:#bfb5a5}\n','')
            self.assertIn(legacy_css,page)
            visible=readable(page.encode())
            self.assertIsNone(QA_MARKER.search(visible),visible)
            self.assertNotIn('Patch',visible); self.assertIn('Counterplay:',visible) # Archived previews are historical snapshots.
            self.assertNotRegex(page,r'{{\w+}}')
            for reference in re.findall(r'src="([^"]+)"',page): self.assertTrue((ARCHIVE/'media'/reference).is_file())
        overview=next(c for c in self.qa['cards'] if c['kind']=='overview')
        self.assertIn('stat-ad',(ARCHIVE/overview['preview']).read_text(encoding='utf-8'))
        self.assertEqual(len(FIELD_NAMES),17)

    def test_stable_identity_approved_preservation_and_no_approval_or_export(self):
        project=Project(profile='batch01'); before=approved_fingerprints(project)
        self.assertEqual(before,self.qa['base_approved_hashes'])
        candidate=read_json(ARCHIVE/'candidate.json')
        self.assertEqual(len(candidate['cards']),114)
        self.assertEqual(candidate['cards'][:100],project.content()['cards'])
        self.assertEqual({c['id'] for c in self.cards},set(self.qa['identity_map']))
        for unit in self.inventory:
            self.assertEqual(unit['card_id'],card_key(523,unit))
            changed={**unit,'title':'Different English display text','purpose':'A different editorial explanation.'}
            self.assertEqual(card_key(523,changed),unit['card_id'])
            key=unit['card_id']; self.assertEqual(self.qa['identity_map'][key],
                {'guid':guid(key),'nid':stable_id(key,1800000000000),'cid':stable_id(key,2300000000000)})
        self.assertIn('champ:523:w:recognize:L2',self.qa['identity_map'])
        self.assertIn('champ:523:r:recognize:L2',self.qa['identity_map'])
        proposal=read_json(ARCHIVE/'proposal.json')
        self.assertEqual(proposal['candidate_sha256'],digest(canonical(candidate)))
        self.assertEqual(set(proposal['changed_ids']),{c['id'] for c in self.cards})
        with self.assertRaisesRegex(ValueError,'cannot be auto-approved'):
            apply_review(project,ARCHIVE/'proposal.json',digest(canonical(proposal)),'test-not-a-reviewer')
        self.assertFalse(self.qa['human_approved']); self.assertFalse(self.qa['publishable'])
        self.assertTrue(self.qa['source_conflicts']); self.assertTrue(self.qa['factual_risks'])
        self.assertTrue(self.qa['missing_media']); self.assertEqual(self.qa['extra_cards_created'],0)
        for p in (ARCHIVE/'ai').glob('verifier-pass-*/request.json'):
            contract=read_json(p)['data']['pedagogical_metadata']
            self.assertEqual(contract['counterplay_basis'],'source_grounded_inference')
            self.assertFalse(contract['card_facing_labels'])
        self.assertTrue(all(not c['row']['cooldown'] for c in self.cards))
        self.assertFalse(list(ARCHIVE.rglob('*.apkg')))
        self.assertEqual(before,approved_fingerprints(project))

    def test_saved_inventory_and_content_replay_offline_without_new_model_calls(self):
        identifier=restore_inputs(ROOT,ARCHIVE)
        before=approved_fingerprints(Project(profile='batch01'))
        with patch('urllib.request.urlopen',side_effect=AssertionError('Network during replay')), \
             patch('lol_anki.generation.ai.AIClient._codex',side_effect=AssertionError('Model during replay')), \
             patch('lol_anki.generation.ai.AIClient._openai',side_effect=AssertionError('Model during replay')):
            result=generate(ROOT,identifier,offline=True,resume_draft=ARCHIVE/'draft-seed.json')
        output=Path(result['output'])
        for name in ('source-packet.json','kit-analysis.json','card-inventory.json','cards.json','candidate.json',
                     'proposal.json','assets.json','media-report.json','changes.diff','QA.md','REVIEW.md'):
            self.assertEqual((ARCHIVE/name).read_bytes(),(output/name).read_bytes(),name)
        expected=read_json(ARCHIVE/'qa.json'); actual=read_json(output/'qa.json')
        # Processor updates get a fresh history identity, never a changed archive.
        # Content, source/media bindings, support results and receipts stay exact.
        for key in ('processing','run_id'):
            expected['generation'].pop(key); actual['generation'].pop(key)
        self.assertEqual(expected,actual)
        for path in (ARCHIVE/'previews').glob('*.html'):
            old=path.read_text('utf-8'); new=(output/'previews'/path.name).read_text('utf-8')
            new=new.replace('.bottom a{color:inherit;text-decoration:none;border-bottom:1px solid #43484e}\n.bottom a:hover{color:#bfb5a5}\n','')
            new=re.sub(r'<div class="bottom">.*?</div>','',new)
            old=re.sub(r'<div class="sub">.*?</div>','',old)
            new=re.sub(r'<div class="sub">.*?</div>','',new)
            self.assertEqual(old,new,path.name)
        self.assertEqual(before,approved_fingerprints(Project(profile='batch01')))
        self.assertEqual(result['cards'],14); self.assertFalse(result['approved']); self.assertFalse(result['published'])

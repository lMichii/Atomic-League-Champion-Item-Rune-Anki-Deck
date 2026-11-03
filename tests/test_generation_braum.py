"""Live-generated Braum evidence fixture; tests replay it without network/model calls."""
import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from lol_anki.generation.archive import restore_inputs
from lol_anki.generation.contracts import check_draft,check_inventory,check_verification
from lol_anki.generation.presentation import check_learning_row,QA_MARKER
from lol_anki.generation.evidence import readable
from lol_anki.generation.workflow import generate,approved_fingerprints,draft_qa,compile_cards
from lol_anki.io import canonical,digest,read_json
from lol_anki.media import gif_info
from lol_anki.project import ROOT,Project
from lol_anki.validation import validate
from lol_anki.v4 import CSS,QFMT,AFMT,FIELD_NAMES

ARCHIVE=ROOT/'data/drafts/braum'/read_json(ROOT/'data/drafts/braum/index.json')['current_run']


class BraumGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=read_json(ARCHIVE/'source-packet.json')
        cls.draft=read_json(ARCHIVE/'ai-draft.json')
        cls.cards=read_json(ARCHIVE/'cards.json')['cards']
        cls.assets=read_json(ARCHIVE/'assets.json')
        cls.qa=read_json(ARCHIVE/'qa.json')
        cls.inventory=read_json(ARCHIVE/'mechanics-inventory.json')

    def test_exact_six_drafts_with_english_conventions_and_stable_identity(self):
        check_draft(self.draft,self.packet)
        self.assertEqual(len(self.cards),6)
        self.assertEqual([c['row']['slot'] for c in self.cards],list('-PQWER'))
        self.assertEqual(self.cards[0]['row']['question'],'What can this champion do?')
        self.assertTrue(self.cards[0]['row']['build_focus'])
        self.assertTrue(all(c['content_status']=='draft' and c['qa_status']=='needs_review' for c in self.cards))
        self.assertTrue(all(c['row']['cooldown']=='' for c in self.cards))
        self.assertEqual(self.cards[1]['id'],'champ:201:p:recognize:L2')
        self.assertTrue(all(c['importance']['reason'] and c['row']['counterplay'] for c in self.cards))
        self.assertFalse(self.qa['human_approved']); self.assertFalse(self.qa['publishable'])

    def test_all_100_approved_records_and_locks_unchanged_and_proposal_only_adds_six(self):
        project=Project(profile='batch01')
        self.assertEqual(approved_fingerprints(project),self.qa['base_approved_hashes'])
        candidate=read_json(ARCHIVE/'candidate.json')
        self.assertEqual(len(candidate['cards']),106)
        self.assertEqual(candidate['cards'][:100],project.content()['cards'])
        proposal=read_json(ARCHIVE/'proposal.json')
        self.assertEqual(set(proposal['changed_ids']),{c['id'] for c in self.cards})
        self.assertEqual(proposal['candidate_sha256'],digest(canonical(candidate)))
        self.assertFalse(proposal['apply_supported']); self.assertTrue(proposal['approval_required'])
        errors={f['code'] for f in validate(project,candidate,False)['findings'] if f['severity']=='error'}
        self.assertIn('draft',errors)
        self.assertFalse(list(ARCHIVE.rglob('*.apkg')))

    def test_real_icons_gifs_portrait_quotes_and_visual_inputs(self):
        self.assertEqual(self.packet['versions']['wiki_revision'],'4022592')
        self.assertEqual(len(self.packet['excerpts']),11)
        for resource in self.packet['resources']:
            blob=(ARCHIVE/'sources'/resource['sha256']).read_bytes()
            self.assertEqual(digest(blob),resource['sha256'])
        for file in self.assets['files']:
            blob=(ARCHIVE/file['path']).read_bytes()
            self.assertEqual(digest(blob),file['sha256'])
            self.assertTrue(file['source_url'].startswith(('https://ddragon.leagueoflegends.com/','https://d28xe8vt774jo5.cloudfront.net/')))
            if file['kind']=='gif':
                info=gif_info(blob)
                self.assertGreater(info['frames'],1); self.assertEqual(info['loop'],0)
        self.assertTrue(self.assets['portrait'])
        for slot in 'PQWER': self.assertTrue(self.assets['abilities'][slot]['icon'])
        for slot in 'QWER': self.assertTrue(self.assets['abilities'][slot]['gif'])
        self.assertEqual(len(self.qa['passive_frame_evidence']),4)
        if next(c for c in self.draft['cards'] if c['slot']=='P')['passive_visual']['meaningful']:
            self.assertTrue(self.cards[1]['row']['visual_cue_media_path'])
        self.assertEqual(self.cards[1]['row']['visual_cue_status'],'needs_visual_cue_review')
        self.assertTrue(self.qa['source_conflicts'])
        self.assertTrue(self.qa['factual_risks'])

    def test_citation_and_numeric_hallucinations_rejected(self):
        bad=copy.deepcopy(self.draft)
        bad['cards'][0]['facts'][0]['citations'][0]['quote']='This string was not present in any retrieved evidence.'
        with self.assertRaisesRegex(ValueError,'Citation quote'): check_draft(bad,self.packet)
        bad=copy.deepcopy(self.draft)
        passive=next(c for c in bad['cards'] if c['slot']=='P')
        original=passive['facts'][0]
        old=original['claim']; original['claim']=old+' It deals 9999 damage.'
        passive['answer']=passive['answer'].replace(old,original['claim'])
        with self.assertRaisesRegex(ValueError,'Numeric claim'): check_draft(bad,self.packet)

    def test_v4_previews_reference_real_local_media_and_single_template_contract(self):
        self.assertEqual(len(list((ARCHIVE/'previews').glob('*.html'))),7)
        for card in self.cards:
            name=card['row']['slot'].lower().replace('-','overview')+'.html'
            page=(ARCHIVE/'previews'/name).read_text('utf-8')
            legacy_css=CSS.replace('.bottom a{color:inherit;text-decoration:none;border-bottom:1px solid #43484e}\n.bottom a:hover{color:#bfb5a5}\n','')
            self.assertIn(legacy_css,page)
            self.assertNotIn('UNAPPROVED DRAFT',page)
            self.assertIn('<base href="../media/">',page)
            for reference in re.findall(r'src="([^"]+)"',page):
                self.assertTrue((ARCHIVE/'media'/reference).is_file(),reference)
            self.assertNotRegex(page,r'{{\w+}}')
        self.assertEqual(len(FIELD_NAMES),17)

    def test_clean_learning_content_versions_and_supported_unbreakable_core(self):
        check_inventory(self.inventory,self.packet)
        check_verification(read_json(ARCHIVE/'ai-verification.json'),self.packet,self.inventory,self.draft)
        for card in self.cards:
            row=card['row']; check_learning_row(row)
            self.assertEqual(row['review_status'],'')
            self.assertEqual(row['patch'],'')
            self.assertEqual(card['versioning']['asset_version'],self.packet['versions']['ddragon'])
            self.assertIsNone(card['versioning']['verified_game_patch'])
            self.assertEqual(card['pedagogy']['counterplay_basis'],'source_grounded_inference')
            name=row['slot'].lower().replace('-','overview')+'.html'
            visible=readable((ARCHIVE/'previews'/name).read_bytes())
            self.assertIsNone(QA_MARKER.search(visible),visible)
            self.assertNotIn('Patch',visible) # Historical archive preview remains immutable.
            self.assertNotIn(self.packet['versions']['ddragon'],visible)
            self.assertIn('Counterplay:',visible)
            self.assertNotIn('INFERRED',visible)
        e=next(c for c in self.cards if c['row']['slot']=='E')
        self.assertRegex(e['row']['answer'].lower(),r'reduc\w* (?:subsequent )?(?:eligible )?damage')
        self.assertRegex(e['row']['answer'].lower(),r'negat\w* (?:the )?first')
        old=read_json(ROOT/'data/drafts/braum/dca12fd8e32ff8f42b90/qa.json')
        self.assertEqual(self.qa['identity_map'],old['identity_map'])

    def test_support_failure_stays_visible_and_bounded_repairs_are_recorded(self):
        passes=self.qa['generation']['passes']
        self.assertTrue(1<=len(passes)<=3)
        self.assertEqual(passes[-1]['support_issues'],0)
        self.assertTrue(all(c['source_supported_draft'] for c in self.qa['cards']))
        verifier=read_json(ARCHIVE/'ai-verification.json')
        verifier['checks'][0]['facts_supported']=False
        report=draft_qa(self.cards,self.packet,self.assets,verifier,self.inventory)
        self.assertTrue(any(f['code']=='ai_support_check_failed' for f in report['findings']))
        self.assertFalse(report['cards'][0]['source_supported_draft'])
        self.assertFalse(report['publishable'])
        verifier=read_json(ARCHIVE/'ai-verification.json')
        e_check=next(c for c in verifier['checks'] if c['slot']=='E')
        e_check['core_coverage'][0].update(covered=False,answer_quote='',reason='Omitted due to disputed advanced exceptions.')
        report=draft_qa(self.cards,self.packet,self.assets,verifier,self.inventory)
        self.assertTrue(any(f['code']=='missing_supported_core_mechanic' for f in report['findings']))
        self.assertFalse(next(c for c in report['cards'] if c['slot']=='E')['source_supported_draft'])
        e=next(c for c in self.qa['cards'] if c['slot']=='E')
        self.assertEqual(e['missing_supported_core_ids'],[])
        self.assertTrue(e['mechanics']['advanced_exceptions'])
        self.assertTrue(e['mechanics']['unsupported_claims'])
        self.assertEqual(len(self.qa['cooldown_candidates']),4)
        self.assertEqual(self.qa['extra_cards_created'],0)

    def test_archived_run_replays_offline_with_identical_content_and_previews(self):
        before=approved_fingerprints(Project(profile='batch01'))
        identifier=restore_inputs(ROOT,ARCHIVE)
        with patch('urllib.request.urlopen',side_effect=AssertionError('Unexpected network during replay')),patch('lol_anki.generation.ai.AIClient._codex',side_effect=AssertionError('Unexpected model during replay')):
            result=generate(ROOT,identifier,offline=True)
        output=Path(result['output'])
        for name in ('cards.json','candidate.json','proposal.json','assets.json','changes.diff','mechanics-inventory.json'):
            self.assertEqual((ARCHIVE/name).read_bytes(),(output/name).read_bytes(),name)
        # A changed processor receives a new run identity while archived learning
        # content, evidence, reviews and model receipts remain unchanged.
        expected=read_json(ARCHIVE/'qa.json'); actual=read_json(output/'qa.json')
        for key in ('processing','run_id'):
            expected['generation'].pop(key); actual['generation'].pop(key)
        self.assertEqual(expected,actual)
        for page in (ARCHIVE/'previews').glob('*.html'):
            if page.name=='index.html': continue
            replayed=(output/'previews'/page.name).read_text('utf-8')
            self.assertIn('Patch 26.21 · <a href=',replayed)
            self.assertIn('League</a> · <a href=',replayed)
        self.assertEqual(before,approved_fingerprints(Project(profile='batch01')))

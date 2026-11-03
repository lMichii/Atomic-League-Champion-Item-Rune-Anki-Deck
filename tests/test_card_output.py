"""Card-facing projection and core/exception/unsupported separation regressions."""
import copy
import unittest
from lol_anki.generation.presentation import (check_learning_row,check_learning_text,
    version_fields,learning_fields,draft_templates)
from lol_anki.generation.preview import template
from lol_anki.generation.contracts import (check_inventory,check_verification,
    core_coverage_failures,support_check_passed)
from lol_anki.validation import ROW_FIELDS
from lol_anki.v4 import CSS,QFMT,AFMT
from lol_anki.project import ROOT


class CardOutputTests(unittest.TestCase):
    def card(self):
        row={k:'' for k in ROW_FIELDS}
        row.update(id='term:test:L0',level='L0',champion='Test',slot='-',ability='Test',
                   media_type='none',question='What does this do?',answer='It reduces incoming damage.',
                   counterplay='Attack from another direction.',patch='16.21.1',priority='A',
                   review_status='UNVERIFIED: internal review warning',source_riot='https://www.leagueoflegends.com/',
                   source_wiki='https://wiki.leagueoflegends.com/')
        return {'row':row,'qa_status':'needs_review','pedagogy':{'counterplay_basis':'source_grounded_inference'},
                'versioning':{'asset_version':'16.21.1','verified_game_patch':None,'game_patch_evidence':[]}}

    def test_qa_markers_are_rejected_in_all_card_facing_fields(self):
        for marker in ('INFERRED:','SUPPORTED:','UNVERIFIED','UNAPPROVED','TENTATIVE proposal:','confidence score','source packet','attached frames'):
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError,'QA marker'):
                check_learning_text(marker+' move away.')
        for field in ('question','answer','counterplay','build_focus','visual_cue_description','front_hint'):
            row=copy.deepcopy(self.card()['row']); row[field]='UNVERIFIED: check this'
            with self.subTest(field=field),self.assertRaises(ValueError): check_learning_row(row)
        check_learning_text('Braum protects his allies. Attack from another direction.')

    def test_unified_footer_is_back_only_below_counterplay_with_clickable_links(self):
        card=self.card(); before=copy.deepcopy(card)
        fields,_=learning_fields(card,ROOT,set())
        front_template,back_template=draft_templates()
        front=template(front_template,fields)
        back=template(back_template,{**fields,'FrontSide':front})
        self.assertNotIn('Patch',front); self.assertNotIn('href=',front)
        self.assertIn('Patch 26.21',back); self.assertNotIn('16.21.1',back)
        self.assertNotIn('UNVERIFIED',back); self.assertNotIn('review warning',back)
        self.assertIn('href="https://www.leagueoflegends.com/"',back)
        self.assertIn('href="https://wiki.leagueoflegends.com/"',back)
        self.assertNotIn('Priority',back)
        self.assertEqual(back.count('Patch 26.21'),1)
        self.assertLess(back.index('Counterplay:'),back.index('Patch 26.21'))
        self.assertIn('<b>Counterplay:</b> Attack from another direction.',back)
        self.assertEqual(card,before)  # Projection never upgrades or destroys QA metadata.
        self.assertEqual(card['qa_status'],'needs_review')
        self.assertEqual(card['pedagogy']['counterplay_basis'],'source_grounded_inference')

    def test_single_display_patch_is_independent_of_asset_release_and_game_patch_metadata(self):
        packet={'versions':{'ddragon':'16.21.1','game_patch':'26.21'}}
        self.assertIsNone(version_fields(packet)['verified_game_patch'])
        self.assertEqual(version_fields(packet)['asset_version'],'16.21.1')
        card=self.card()
        card['versioning']['verified_game_patch']='26.21'
        fields,_=learning_fields(card,ROOT,set())
        self.assertEqual(fields['Patch'],'26.21')
        card['versioning']['game_patch_evidence']=[{'reference':'explicit independent verification record'}]
        fields,_=learning_fields(card,ROOT,set())
        front,back=draft_templates()
        rendered_front=template(front,fields)
        rendered_back=template(back,{**fields,'FrontSide':rendered_front})
        self.assertNotIn('Patch',rendered_front)
        self.assertIn('Patch 26.21',rendered_back)
        self.assertNotIn('16.21.1',rendered_back)
        legacy_fields={**fields,'Patch':''}
        legacy_front=template(front,legacy_fields)
        legacy_back=template(back,{**legacy_fields,'FrontSide':legacy_front})
        self.assertIn('Patch 26.21',legacy_back)  # Existing notes with empty legacy Patch fields retain the footer.
        # The shared template retains the v4 field schema and hides internal QA.
        self.assertNotIn('bottom',QFMT)
        self.assertIn('Patch {{Patch}}',AFMT)
        self.assertNotIn('{{Review}}',AFMT)
        self.assertIn('color:#77c3ff',CSS)

    def mechanics(self):
        text='The shield reduces incoming damage. Special hit eligibility remains disputed.'
        packet={'excerpts':[{'id':'riot:E','text':text},{'id':'wiki:E','text':text}]}
        abilities=[]
        for slot in 'PQWER':
            abilities.append({'slot':slot,'core_mechanics':[{'id':slot+'.core','summary':'The shield reduces incoming damage.',
                'citations':[{'source_id':'riot:E','quote':'The shield reduces incoming damage.'}]}],
                'advanced_exceptions':[{'summary':'Special hit eligibility remains disputed.','status':'disputed',
                'citations':[{'source_id':'wiki:E','quote':'Special hit eligibility remains disputed.'}]}],
                'unsupported_claims':['The shield blocks every possible effect.']})
        return packet,{'abilities':abilities}

    def checks(self):
        return {'checks':[{'slot':slot,'facts_supported':True,'all_answer_claims_covered':True,
            'counterplay_grounded':True,'english':True,'beginner_friendly':True,'priority_reasonable':True,
            'core_coverage':[] if slot=='-' else [{'mechanic_id':slot+'.core','covered':True,
                'answer_quote':'It reduces incoming damage.','reason':'The general mechanic is explained.'}],
            'issues':[]} for slot in '-PQWER'],'conflicts':[],'factual_risks':[]}

    def test_disputed_exception_does_not_cancel_supported_core(self):
        packet,inventory=self.mechanics(); check_inventory(inventory,packet)
        result=self.checks(); draft={'cards':[{'slot':s,'answer':'It reduces incoming damage.'} for s in '-PQWER']}
        check_verification(result,packet,inventory,draft)
        e=next(c for c in result['checks'] if c['slot']=='E')
        self.assertTrue(support_check_passed(e,inventory))
        self.assertEqual(core_coverage_failures(e,inventory),[])
        self.assertEqual(inventory['abilities'][3]['advanced_exceptions'][0]['status'],'disputed')
        self.assertTrue(inventory['abilities'][3]['unsupported_claims'])

    def test_missing_core_is_a_failure_even_when_other_checks_pass(self):
        packet,inventory=self.mechanics(); result=self.checks()
        e=next(c for c in result['checks'] if c['slot']=='E')
        e['core_coverage'][0].update(covered=False,answer_quote='',reason='Omitted because an advanced exception is disputed.')
        check_verification(result,packet,inventory)
        self.assertFalse(support_check_passed(e,inventory))
        self.assertEqual(core_coverage_failures(e,inventory),['E.core'])
        e['core_coverage']=[]
        with self.assertRaisesRegex(ValueError,'every frozen supported core'):
            check_verification(result,packet,inventory)

    def test_verifier_cannot_claim_core_coverage_using_text_not_in_the_answer(self):
        packet,inventory=self.mechanics(); result=self.checks()
        draft={'cards':[{'slot':s,'answer':'It intercepts a projectile.'} for s in '-PQWER']}
        with self.assertRaisesRegex(ValueError,'quote actual answer'):
            check_verification(result,packet,inventory,draft)
        # A fabricated evidence quote is also rejected before authoring.
        inventory['abilities'][0]['core_mechanics'][0]['citations'][0]['quote']='A completely fabricated damage mechanic.'
        with self.assertRaisesRegex(ValueError,'Citation quote'):
            check_inventory(inventory,packet)

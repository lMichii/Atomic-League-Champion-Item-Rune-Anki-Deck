"""Nonstandard structures use source/context identities, not a five-slot grid."""
import copy
import unittest
from lol_anki.generation.kit_contracts import (card_key,freeze_plan,validate_plan,
    validate_text,validate_support,supported)
from lol_anki.generation.kit_media import choose_primary
from lol_anki.generation.kit_sources import live_sections,extend_packet
from lol_anki.generation.preview import page_name
from lol_anki.generation.kit_workflow import usage_report,check_seed,TEACHING_CONTRACT
from lol_anki.io import canonical,digest


class KitContractTests(unittest.TestCase):
    def fixture(self):
        quote='The weapon fires a slowing projectile. Its form changes the attack.'
        sections=[{'id':'wiki:'+s,'name':s.title(),'anchor':s,'icon_url':None} for s in ('system','alpha','beta','strike','ultimate')]
        packet={'champion':{'riot_id':999,'name':'Test'},'kit_sections':sections,
            'abilities':[{'slot':'Q','name':'Strike'}],
            'excerpts':[{'id':s['id'],'text':quote} for s in sections]}
        cards=[]
        for index,(kind,subject,context,slot) in enumerate([
            ('overview','system','',''),('system','system','','P'),
            ('weapon','alpha','',''),('form','beta','',''),
            ('ability_variant','strike','alpha','Q'),('ability_variant','strike','beta','Q'),
            ('stance','alpha','beta',''),('transformation','beta','alpha','R'),
            ('conditional_effect','ultimate','alpha','R')]):
            sid='wiki:'+subject
            cards.append({'kind':kind,'subject_id':sid,'context_id':'wiki:'+context if context else '',
                'slot':slot,'title':subject.title(),'purpose':'A distinct source-grounded enemy recognition goal.',
                'source_ids':[sid],'core_mechanics':[{'id':f'core.{index}','summary':'The weapon fires a slowing projectile.',
                'citations':[{'source_id':sid,'quote':'The weapon fires a slowing projectile.'}]}],
                'advanced_exceptions':[],'unsupported_claims':[]})
        plan={'features':['weapon_system','multiple_forms','ability_variants','conditional_effects'],
            'summary':'An unconventional kit with weapons, forms and context-specific abilities.',
            'slots':[{'slot':'E','role':'indicator','source_ids':['wiki:system']}],
            'relationships':[{'from_id':'wiki:strike','to_id':'wiki:alpha','kind':'variant_of',
                'condition':'The form determines which attack is available.',
                'citations':[{'source_id':'wiki:alpha','quote':'Its form changes the attack.'}]}],
            'cards':cards,'section_disposition':[{'source_id':s['id'],'disposition':'taught',
                'target_subject_ids':[s['id']],'reason':'Covered by the distinct source-grounded learning goal.'} for s in sections],
            'conflicts':[],'factual_risks':[]}
        return packet,plan

    def content(self,inventory):
        return {'language':'en','champion_id':999,'cards':[{'card_id':u['card_id'],
            'answer':'The weapon fires a slowing projectile.','counterplay':'Dodge the projectile to avoid its slow.',
            'build_focus':'AD' if u['kind']=='overview' else '', 'priority':'A',
            'priority_reason':'Recognizing the projectile helps avoid its slow.',
            'facts':[{'claim':'The weapon fires a slowing projectile.','basis':'source_assertion',
                'citations':[{'source_id':u['subject_id'],'quote':'The weapon fires a slowing projectile.'}]}],
            'uncertainties':[]} for u in inventory],'cooldown_candidates':[],'conflicts':[],'factual_risks':[]}

    def test_weapons_forms_stances_transformations_and_conditional_effects_are_supported(self):
        packet,plan=self.fixture(); validate_plan(plan,packet)
        units=freeze_plan(plan,999); draft=self.content(units); validate_text(draft,packet,units)
        self.assertEqual(len(units),9)
        self.assertEqual(len({u['card_id'] for u in units}),9)
        self.assertEqual(plan['slots'][0]['role'],'indicator')
        self.assertFalse(any(u['slot']=='E' for u in units))
        pages=[page_name({'id':u['card_id'],'learning_unit':u,'row':{'slot':u['slot']}}) for u in units]
        self.assertEqual(len(pages),len(set(pages)))

    def test_identity_is_independent_of_wording_order_and_preserves_standard_ids(self):
        packet,plan=self.fixture(); before={card_key(999,c) for c in plan['cards']}
        plan['cards'].reverse()
        for c in plan['cards']: c['title']='A different display title'; c['purpose']='Different editorial wording.'
        self.assertEqual(before,{card_key(999,c) for c in plan['cards']})
        conventional={'kind':'ability','slot':'Q','subject_id':'wiki:strike','context_id':''}
        self.assertEqual(card_key(201,conventional),'champ:201:q:recognize:L2')
        conventional['kind']='overview'
        self.assertEqual(card_key(201,conventional),'champ:201:overview:L1')

    def test_plan_rejects_unknown_context_missing_sections_duplicate_identity_and_fake_core(self):
        packet,plan=self.fixture()
        for mutation in ('context','disposition','duplicate','quote','number'):
            bad=copy.deepcopy(plan)
            if mutation=='context': bad['cards'][4]['context_id']='wiki:invented'
            if mutation=='disposition': bad['section_disposition'].pop()
            if mutation=='duplicate': bad['cards'].append(copy.deepcopy(bad['cards'][0]))
            if mutation=='quote': bad['cards'][0]['core_mechanics'][0]['citations'][0]['quote']='An invented mechanic not present in any source.'
            if mutation=='number': bad['cards'][0]['core_mechanics'][0]['summary']='The weapon fires 999 projectiles.'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError): validate_plan(bad,packet)

    def test_generic_slot_clip_never_establishes_variant_matching(self):
        packet,plan=self.fixture()
        variant=next(c for c in plan['cards'] if c['kind']=='ability_variant')
        self.assertIsNone(choose_primary(variant,packet))
        standard={**variant,'kind':'ability','context_id':''}
        self.assertEqual(choose_primary(standard,packet)['slot'],'Q')
        for kind in ('weapon','form','stance','transformation','conditional_effect'):
            self.assertIsNone(choose_primary({**standard,'kind':kind},packet))

    def test_variable_card_and_core_coverage_is_exact_and_omission_fails(self):
        packet,plan=self.fixture(); inventory=freeze_plan(plan,999); draft=self.content(inventory)
        result={'checks':[{'card_id':u['card_id'],'facts_supported':True,'all_answer_claims_covered':True,
            'counterplay_grounded':True,'english':True,'beginner_friendly':True,'priority_reasonable':True,
            'core_coverage':[{'mechanic_id':u['core_mechanics'][0]['id'],'covered':True,
            'answer_quote':'The weapon fires a slowing projectile.','reason':'The answer explains the core.'}],
            'issues':[]} for u in inventory],'kit_complete':True,'omitted_topics':[],'conflicts':[],'factual_risks':[]}
        validate_support(result,packet,inventory,draft)
        result['checks'][4]['core_coverage'][0].update(covered=False,answer_quote='',reason='An advanced exception was disputed.')
        validate_support(result,packet,inventory,draft)
        self.assertFalse(supported(result['checks'][4]))
        result['checks'][4]['core_coverage']=[]
        with self.assertRaises(ValueError): validate_support(result,packet,inventory,draft)
        draft['cards'].pop()
        with self.assertRaisesRegex(ValueError,'every frozen card'): validate_text(draft,packet,inventory)

    def test_uncited_numbers_and_internal_labels_are_rejected_before_semantic_review(self):
        packet,plan=self.fixture(); units=freeze_plan(plan,999); draft=self.content(units)
        draft['cards'][0]['answer']+=' It also deals 999 damage.'
        with self.assertRaisesRegex(ValueError,'Uncited numeric'): validate_text(draft,packet,units)
        draft=self.content(units); draft['cards'][0]['counterplay']='INFERRED: Dodge the projectile.'
        with self.assertRaisesRegex(ValueError,'QA marker'): validate_text(draft,packet,units)

    def test_overview_requires_build_focus_and_l2_cannot_carry_it(self):
        packet,plan=self.fixture(); units=freeze_plan(plan,999); draft=self.content(units)
        draft['cards'][0]['build_focus']=''
        with self.assertRaisesRegex(ValueError,'requires a nonempty build_focus'): validate_text(draft,packet,units)
        draft=self.content(units); draft['cards'][1]['build_focus']='AD'
        with self.assertRaisesRegex(ValueError,'must have empty build_focus'): validate_text(draft,packet,units)

    def test_usage_reports_requests_attempts_and_available_tokens_without_double_counting(self):
        report=usage_report([{'attempts':2,'metadata':{'usage':[{'input_tokens':100,'cached_input_tokens':20,'output_tokens':30}]}},
                            {'attempts':1,'metadata':{'usage':{'input_tokens':50,'output_tokens':10}}}])
        self.assertEqual(report['logical_requests'],2)
        self.assertEqual(report['recorded_model_attempts'],3)
        self.assertEqual(report['available_receipt_usage'],{'input_tokens':150,'cached_input_tokens':20,'output_tokens':40})

    def test_resume_seed_is_source_and_identity_bound_and_keeps_guidance_inferred(self):
        packet,plan=self.fixture(); inventory=freeze_plan(plan,999); draft=self.content(inventory)
        evidence={'source_packet':'test evidence'}
        seed={'draft':draft,'author_receipt':{'output_sha256':digest(canonical(draft))},
              'model_input_sha256':digest(canonical(evidence)),'inventory_sha256':digest(canonical(inventory))}
        check_seed(seed,evidence,inventory,packet)
        bad=copy.deepcopy(seed); bad['draft']['cards'][0]['counterplay']='Move away from the projectile.'
        with self.assertRaisesRegex(ValueError,'recorded model receipt'): check_seed(bad,evidence,inventory,packet)
        with self.assertRaisesRegex(ValueError,'does not match'): check_seed(seed,{'different':'sources'},inventory,packet)
        self.assertEqual(TEACHING_CONTRACT['counterplay_basis'],'source_grounded_inference')
        self.assertEqual(TEACHING_CONTRACT['build_focus_basis'],'broad_learning_orientation')
        self.assertFalse(TEACHING_CONTRACT['card_facing_labels'])

    def test_live_parser_discovers_extra_sections_without_borrowing_prior_anchor_or_pets(self):
        blob=b'''<h2 id="Abilities">Abilities</h2><span id="Alpha"></span>
        <div class="ability-info-stats&#95;&#95;ability">Alpha</div>
        <p>Active: The weapon fires a slowing projectile.</p>'''+b'x'*1100+b'''
        <div class="ability-info-stats__ability">Phase</div><p>Active: Swap weapons.</p>
        <h2 id="Pets">Pets</h2><div class="ability-info-stats__ability">Unrelated</div>'''
        sections=live_sections(blob)
        self.assertEqual([s['id'] for s in sections],['wiki:alpha','wiki:phase'])
        self.assertNotIn('Unrelated',sections[-1]['text'])

    def test_zero_cdragon_maxlevels_do_not_misclassify_a_standard_kit(self):
        names=['Passive','First','Second','Third','Ultimate']
        wiki=('<h2 id="Abilities">Abilities</h2>'+''.join(
            '<div class="ability-info-stats__ability">'+n+'</div><p>Active: A projectile slows enemies.</p>' for n in names)+'<h2 id="Pets">Pets</h2>').encode()
        packet={'schema_version':1,'abilities':[{'name':n,'description':'A projectile slows enemies.'} for n in names],
                'versions':{'wiki_revision':'1'}}
        class NoRetrieval:
            def get(self,*a,**kw): raise AssertionError('Unnecessary source/media discovery')
        result=extend_packet(NoRetrieval(),packet,{'spells':[{}]*4},wiki,{},
                             {'spells':[{'maxLevel':0}]*4})
        self.assertIs(result,packet)
        self.assertEqual(result['schema_version'],1)

    def test_duplicate_headings_use_distinct_explicit_template_identities_only(self):
        blob=b'''<h2 id="Abilities">Abilities</h2>
        <span id="Passive"></span><a href="/en-us/Template:Data_Test/Passive?action=edit">Edit</a>
        <div class="ability-info-stats__ability">Passive</div><p>Innate: First form.</p>
        <span id="Passive"></span><a href="/en-us/Template:Data_Test/Passive_2?action=edit">Edit</a>
        <div class="ability-info-stats__ability">Passive</div><p>Innate: Second form.</p>'''
        sections=live_sections(blob)
        self.assertEqual([s['id'] for s in sections],['wiki:passive','wiki:passive2'])
        self.assertIn('Template:Data_Test/Passive_2',sections[1]['anchor'])
        ambiguous=blob.replace(b'Passive_2?action',b'Passive?action')
        self.assertEqual([s['id'] for s in live_sections(ambiguous)],['wiki:passive','wiki:passive'])

    def test_shared_template_merges_only_identical_full_text_and_icon(self):
        section='''<span id="Shared"></span><a href="/en-us/Template:Data_Test/Shared?action=edit"></a>
        <div class="ability-info-stats__ability">Shared</div><p>Innate: Same ability.</p>'''
        sections=live_sections(('<h2 id="Abilities">Abilities</h2>'+section*2).encode())
        self.assertEqual(len(sections),1)
        changed=section.replace('Same ability.','Different ability.')
        self.assertEqual(len(live_sections(('<h2 id="Abilities">Abilities</h2>'+section+changed).encode())),2)

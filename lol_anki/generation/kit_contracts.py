"""Variable-size, source-addressed learning inventory and content contracts (v2)."""
import re
from .contracts import (obj,array,string,enum,BOOL,CITATION,CORE,EXCEPTION,CONFLICT,
    CARD,CORE_COVERAGE,schema_check,check_citations,normalized,numeric_tokens)
from .presentation import check_learning_text

KINDS=['overview','system','weapon','ability','ability_variant','form','stance','transformation','conditional_effect']
PLAN_CARD=obj({'kind':enum(KINDS),'subject_id':string(1,100),'context_id':string(0,100),
    'slot':string(0,12),'title':string(1,120),'purpose':string(15,500),
    'source_ids':array(string(1,100),1,12),'core_mechanics':array(CORE,1,9),
    'advanced_exceptions':array(EXCEPTION,0,8),'unsupported_claims':array(string(5,700),0,8)})
KIT_SCHEMA=obj({'features':array(enum(['standard','weapon_system','resource_cycle','multiple_forms',
    'stances','transformations','ability_variants','conditional_effects','unconventional_leveling','noncombat_slot']),1,10),
    'summary':string(25,2200),
    'slots':array(obj({'slot':string(1,12),'role':enum(['passive','active','toggle','indicator','unused','contextual']),
                     'source_ids':array(string(1,100),1,8)}),0,12),
    'relationships':array(obj({'from_id':string(1,100),'to_id':string(1,100),
        'kind':enum(['variant_of','off_hand_effect','equips','cycles','swaps','changes_form','changes_stance','unlocks','conditional_effect']),
        'condition':string(5,700),'citations':array(CITATION,1,5)}),0,45),
    'cards':array(PLAN_CARD,2,35),
    'section_disposition':array(obj({'source_id':string(1,100),
        'disposition':enum(['taught','merged','advanced_only','out_of_scope']),
        'target_subject_ids':array(string(1,100),0,12),'reason':string(10,500)}),1,55),
    'conflicts':array(CONFLICT,0,15),'factual_risks':array(string(5,700),0,25)})
KIT_FACT=obj({'claim':string(5,800),'citations':array(CITATION,1,10),
              'basis':enum(['source_assertion','exhaustive_kit_inference'])})
TEXT_CARD=obj({'card_id':string(5,220),'answer':string(25,1100),'counterplay':string(15,450),
    'build_focus':CARD['properties']['build_focus'],'priority':enum(['A','B','C']),
    'priority_reason':string(15,400),'facts':array(KIT_FACT,1,15),
    'uncertainties':array(string(5,700),0,12)})
KIT_DRAFT_SCHEMA=obj({'language':enum(['en']),'champion_id':{'type':'integer'},
    'cards':array(TEXT_CARD,2,35),
    'cooldown_candidates':array(obj({'card_id':string(5,220),'priority':enum(['A','B','C']),
        'reason':string(15,500),'source_ids':array(string(1,100),1,8)}),0,12),
    'conflicts':array(CONFLICT,0,15),'factual_risks':array(string(5,700),0,25)})
KIT_CHECK=obj({'card_id':string(5,220),'facts_supported':BOOL,'all_answer_claims_covered':BOOL,
    'counterplay_grounded':BOOL,'english':BOOL,'beginner_friendly':BOOL,'priority_reasonable':BOOL,
    'core_coverage':array(CORE_COVERAGE,1,9),'issues':array(string(5,700),0,15)})
KIT_VERIFY_SCHEMA=obj({'checks':array(KIT_CHECK,2,35),'kit_complete':BOOL,
    'omitted_topics':array(string(5,700),0,20),'conflicts':array(CONFLICT,0,15),
    'factual_risks':array(string(5,700),0,25)})


def component(value):
    return re.sub('[^a-z0-9]+','-',value.casefold()).strip('-')


def card_key(cid,card):
    """Identity uses source anchors/context, never authored prose or ordinal position."""
    if card['kind']=='overview': return f'champ:{cid}:overview:L1'
    slot=card['slot'].lower()
    if card['kind']=='ability' and slot in ('p','q','w','e','r'):
        return f'champ:{cid}:{slot}:recognize:L2'
    subject=component(card['subject_id'].split(':',1)[-1])
    context=':'+component(card['context_id'].split(':',1)[-1]) if card['context_id'] else ''
    return f'champ:{cid}:{card["kind"]}:{slot or "none"}:{subject}{context}:recognize:L2'


def validate_plan(plan,packet):
    schema_check(plan,KIT_SCHEMA); known={e['id'] for e in packet['excerpts']}
    sections={s['id'] for s in packet['kit_sections']}; ids=set(); subjects=set(); cores=set()
    if sum(c['kind']=='overview' for c in plan['cards'])!=1: raise ValueError('Exactly one overview is required')
    for card in plan['cards']:
        if card['subject_id'] not in known or (card['context_id'] and card['context_id'] not in known):
            raise ValueError('Unknown subject/context reference')
        if set(card['source_ids'])-known: raise ValueError('Unknown card source')
        if card['kind']=='ability_variant' and not card['context_id']: raise ValueError('Ability variants require an explicit context')
        key=card_key(packet['champion']['riot_id'],card)
        if key in ids: raise ValueError('Duplicate learning identity')
        ids.add(key); subjects.add(card['subject_id'])
        check_learning_text(card['title'])
        for core in card['core_mechanics']:
            if core['id'] in cores: raise ValueError('Duplicate core mechanic ID')
            cores.add(core['id']); check_citations(core['citations'],packet)
            missing=numeric_tokens(core['summary'])-numeric_tokens(' '.join(c['quote'] for c in core['citations']))
            if missing:
                raise ValueError(f'Unsupported numeric core claim {core["id"]}: {sorted(missing)} absent from its exact quotes; add the actual source quote containing the number or use qualitative wording')
        for exception in card['advanced_exceptions']: check_citations(exception['citations'],packet)
    disposition=plan['section_disposition']
    if {d['source_id'] for d in disposition}!=sections or len(disposition)!=len(sections):
        raise ValueError('Every live kit section needs an explicit coverage disposition exactly once')
    for d in disposition:
        if set(d['target_subject_ids'])-subjects: raise ValueError('Disposition refers to an unplanned card')
        if d['disposition'] in ('taught','merged') and not d['target_subject_ids']: raise ValueError('Taught/merged sections need a target')
    for slot in plan['slots']:
        if set(slot['source_ids'])-known: raise ValueError('Unknown slot evidence')
    for relation in plan['relationships']:
        if relation['from_id'] not in known or relation['to_id'] not in known: raise ValueError('Unknown relationship endpoint')
        check_citations(relation['citations'],packet)
    for conflict in plan['conflicts']:
        if set(conflict['source_ids'])-known: raise ValueError('Unknown conflict evidence')


def freeze_plan(plan,cid):
    return [{**c,'card_id':card_key(cid,c)} for c in plan['cards']]


def validate_text(draft,packet,inventory):
    schema_check(draft,KIT_DRAFT_SCHEMA)
    if draft['champion_id']!=packet['champion']['riot_id']: raise ValueError('Champion identity changed')
    expected={c['card_id']:c for c in inventory}
    if {c['card_id'] for c in draft['cards']}!=set(expected) or len(draft['cards'])!=len(expected):
        raise ValueError('Author must cover every frozen card identity exactly once')
    for c in draft['cards']:
        for field in ('answer','counterplay','build_focus'):
            check_learning_text(c[field])
            if '<' in c[field] or '\ufffd' in c[field] or re.search(r'[\u0400-\u04ff\u0600-\u06ff\u4e00-\u9fff]',c[field]): raise ValueError('Card text must be plain English')
        overview=expected[c['card_id']]['kind']=='overview'
        if overview and not c['build_focus']: raise ValueError('Overview '+c['card_id']+' requires a nonempty build_focus enum (e.g. AD); do not leave it blank')
        if not overview and c['build_focus']: raise ValueError('L2 '+c['card_id']+' must have empty build_focus; it belongs only on the overview')
        for fact in c['facts']:
            if normalized(fact['claim']) not in normalized(c['answer']): raise ValueError('Fact must quote actual answer')
            quotes=check_citations(fact['citations'],packet)
            if not numeric_tokens(fact['claim'])<=numeric_tokens(' '.join(quotes)): raise ValueError('Unsupported numeric claim')
        all_quotes=' '.join(q['quote'] for f in c['facts'] for q in f['citations'])
        if not numeric_tokens(c['answer'])<=numeric_tokens(all_quotes): raise ValueError('Uncited numeric claim in answer')
        if numeric_tokens(c['counterplay']): raise ValueError('No numerical counterplay timing')
    for candidate in draft['cooldown_candidates']:
        if candidate['card_id'] not in expected or set(candidate['source_ids'])-{e['id'] for e in packet['excerpts']}: raise ValueError('Unknown cooldown topic')
        if numeric_tokens(candidate['reason']): raise ValueError('Cooldown topics must not introduce numbers')
    if len({c['card_id'] for c in draft['cooldown_candidates']})!=len(draft['cooldown_candidates']): raise ValueError('Duplicate cooldown topic')
    known={e['id'] for e in packet['excerpts']}
    unknown={s for c in draft['conflicts'] for s in c['source_ids'] if s not in known}
    if unknown: raise ValueError('Unknown conflict source IDs '+repr(sorted(unknown))+': use only exact source IDs supplied in excerpts, never commentary text')


def validate_support(result,packet,inventory,draft):
    schema_check(result,KIT_VERIFY_SCHEMA)
    expected={c['card_id']:c for c in inventory}; texts={c['card_id']:c['answer'] for c in draft['cards']}
    if len(result['checks'])!=len(expected) or {c['card_id'] for c in result['checks']}!=set(expected): raise ValueError('Verifier must cover all frozen cards exactly once')
    for check in result['checks']:
        cores={c['id'] for c in expected[check['card_id']]['core_mechanics']}
        coverage=check['core_coverage']
        if len(coverage)!=len(cores) or {c['mechanic_id'] for c in coverage}!=cores: raise ValueError('Verifier must account for every frozen supported core')
        for core in coverage:
            if core['covered'] and (not core['answer_quote'] or normalized(core['answer_quote']) not in normalized(texts[check['card_id']])):
                raise ValueError('Core coverage must quote actual answer text')
    known={e['id'] for e in packet['excerpts']}
    unknown={s for c in result['conflicts'] for s in c['source_ids'] if s not in known}
    if unknown: raise ValueError('Unknown verifier conflict source IDs '+repr(sorted(unknown))+': use only exact IDs supplied in excerpts')


def supported(check):
    return all(check[k] for k in ('facts_supported','all_answer_claims_covered','counterplay_grounded','english','beginner_friendly','priority_reasonable')) and all(c['covered'] for c in check['core_coverage'])

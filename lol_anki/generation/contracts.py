"""Strict provider schemas and deterministic evidence checks (standard library)."""
import html
import re
from .presentation import check_learning_text


def obj(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
def array(item,minimum=0,maximum=30):
    return {'type':'array','items':item,'minItems':minimum,'maxItems':maximum}
def string(minimum=0,maximum=1200):
    return {'type':'string','minLength':minimum,'maxLength':maximum}
def enum(values): return {'type':'string','enum':values}
BOOL={'type':'boolean'}
CITATION=obj({'source_id':string(1,80),'quote':string(15,1000)})
FACT=obj({'claim':string(5,600),'citations':array(CITATION,1,6)})
CARD=obj({'level':enum(['L1','L2']),'slot':enum(['-','P','Q','W','E','R']),
          'answer':string(25,850),'counterplay':string(15,450),
          'build_focus':enum(['','AD','AP','AD / AP','Health, Armor, MR','AP, Health','AD, Health']),
          'priority':enum(['A','B','C']),'priority_reason':string(15,400),
          'facts':array(FACT,1,10),'uncertainties':array(string(5,500),0,12),
          'passive_visual':obj({'meaningful':BOOL,'description':string(0,300),'source_ids':array(string(1,80),0,8)})})
CONFLICT=obj({'topic':string(5,400),'source_ids':array(string(1,80),2,8),'resolution':string(5,600)})
CORE=obj({'id':string(3,100),'summary':string(10,600),'citations':array(CITATION,1,6)})
EXCEPTION=obj({'summary':string(10,700),'status':enum(['supported','disputed','uncertain']),
               'citations':array(CITATION,1,6)})
INVENTORY_SCHEMA=obj({'abilities':array(obj({'slot':enum(['P','Q','W','E','R']),
    'core_mechanics':array(CORE,1,12),'advanced_exceptions':array(EXCEPTION,0,15),
    'unsupported_claims':array(string(10,700),0,10)}),5,5)})
CORE_COVERAGE=obj({'mechanic_id':string(3,100),'covered':BOOL,'answer_quote':string(0,850),'reason':string(0,600)})
DRAFT_SCHEMA=obj({'language':enum(['en']),'champion_id':{'type':'integer'},'champion_name':string(1,100),
                  'cards':array(CARD,6,6),'cooldown_candidates':array(obj({'slot':enum(['Q','W','E','R']),
                     'priority':enum(['A','B','C']),'reason':string(15,500),'source_ids':array(string(1,80),1,8)}),0,4),
                  'conflicts':array(CONFLICT,0,12),'factual_risks':array(string(5,600),0,20)})
CHECK=obj({'slot':enum(['-','P','Q','W','E','R']),'facts_supported':BOOL,'all_answer_claims_covered':BOOL,
           'counterplay_grounded':BOOL,'english':BOOL,'beginner_friendly':BOOL,'priority_reasonable':BOOL,
           'core_coverage':array(CORE_COVERAGE,0,12),
           'issues':array(string(5,600),0,20)})
VERIFY_SCHEMA=obj({'checks':array(CHECK,6,6),'conflicts':array(CONFLICT,0,12),
                   'factual_risks':array(string(5,600),0,20)})


def schema_check(value,schema,path='$'):
    """Validate the complete small JSON-Schema subset used by our provider contract."""
    typ=schema['type']
    good={'object':isinstance(value,dict),'array':isinstance(value,list),'string':isinstance(value,str),
          'integer':isinstance(value,int) and not isinstance(value,bool),'boolean':isinstance(value,bool)}
    if not good.get(typ): raise ValueError(f'{path}: expected {typ}')
    if 'enum' in schema and value not in schema['enum']: raise ValueError(f'{path}: invalid enum')
    if typ=='object':
        if set(value)!=set(schema['properties']): raise ValueError(f'{path}: missing or extra properties')
        for key,sub in schema['properties'].items(): schema_check(value[key],sub,path+'.'+key)
    elif typ=='array':
        if not schema.get('minItems',0)<=len(value)<=schema.get('maxItems',10**6): raise ValueError(f'{path}: invalid array length')
        for i,item in enumerate(value): schema_check(item,schema['items'],f'{path}[{i}]')
    elif typ=='string':
        if not schema.get('minLength',0)<=len(value)<=schema.get('maxLength',10**6): raise ValueError(f'{path}: invalid string length')


def normalized(text):
    return ' '.join(html.unescape(text).replace('’',"'").replace('–','-').replace('—','-').split()).casefold()


def numeric_tokens(text):
    text=normalized(text)
    for i,word in enumerate(('zero','one','two','three','four','five','six','seven','eight','nine','ten')):
        text=re.sub(r'\b'+word+r'\b',str(i),text)
    return set(re.findall(r'(?<![a-z])\d+(?:\.\d+)?%?',text))


def check_citations(citations,packet):
    excerpts={e['id']:e for e in packet['excerpts']}
    quotes=[]
    for citation in citations:
        source=excerpts.get(citation['source_id'])
        if not source or normalized(citation['quote']) not in normalized(source['text']):
            raise ValueError('Citation quote does not match retrieved evidence: '+citation['source_id'])
        quotes.append(citation['quote'])
    return quotes


def check_inventory(value,packet):
    schema_check(value,INVENTORY_SCHEMA)
    if {a['slot'] for a in value['abilities']}!=set('PQWER'):
        raise ValueError('Mechanics inventory must cover P/Q/W/E/R exactly once')
    ids=set()
    for ability in value['abilities']:
        for core in ability['core_mechanics']:
            if core['id'] in ids or not core['id'].startswith(ability['slot']+'.'):
                raise ValueError('Core mechanic ID must be unique and prefixed by its slot')
            ids.add(core['id'])
            check_citations(core['citations'],packet)
        for exception in ability['advanced_exceptions']:
            check_citations(exception['citations'],packet)


def core_coverage_failures(check,inventory):
    """A supported core is required regardless of disputes in advanced exceptions."""
    if check['slot']=='-': return []
    ability=next(a for a in inventory['abilities'] if a['slot']==check['slot'])
    coverage={c['mechanic_id']:c for c in check.get('core_coverage',[])}
    return [core['id'] for core in ability['core_mechanics']
            if not coverage.get(core['id'],{}).get('covered',False)]


def support_check_passed(check,inventory=None):
    good=all(check[k] for k in ('facts_supported','all_answer_claims_covered','counterplay_grounded','english','beginner_friendly','priority_reasonable'))
    return good and not (inventory and core_coverage_failures(check,inventory))


def check_draft(draft,packet):
    schema_check(draft,DRAFT_SCHEMA)
    if draft['champion_id']!=packet['champion']['riot_id'] or draft['champion_name']!=packet['champion']['name']:
        raise ValueError('AI changed the champion identity')
    slots={c['slot'] for c in draft['cards']}
    if slots!=set('-PQWER') or sum(c['level']=='L1' for c in draft['cards'])!=1:
        raise ValueError('Exactly one L1 and P/Q/W/E/R L2 are required')
    excerpts={e['id']:e for e in packet['excerpts']}
    for card in draft['cards']:
        if (card['slot']=='-') != (card['level']=='L1'): raise ValueError('Level/slot mismatch')
        if card['level']=='L1' and not card['build_focus']: raise ValueError('Overview build focus missing')
        if card['level']=='L2' and card['build_focus']: raise ValueError('Build focus belongs only on overview')
        for text in (card['answer'],card['counterplay'],card['build_focus']):
            check_learning_text(text)
            if '<' in text or '\ufffd' in text or re.search(r'[\u0400-\u04ff\u0600-\u06ff\u4e00-\u9fff]',text):
                raise ValueError('Unescaped markup, corrupt text or non-English-script content')
        for fact in card['facts']:
            if normalized(fact['claim']) not in normalized(card['answer']):
                raise ValueError('Each fact must be an exact contiguous part of its answer')
            quotes=[]
            for citation in fact['citations']:
                source=excerpts.get(citation['source_id'])
                if not source or normalized(citation['quote']) not in normalized(source['text']):
                    raise ValueError('Citation quote does not match retrieved evidence: '+citation['source_id'])
                quotes.append(citation['quote'])
            if not numeric_tokens(fact['claim']) <= numeric_tokens(' '.join(quotes)):
                raise ValueError('Numeric claim lacks a matching number in cited quotes')
        for source_id in card['passive_visual']['source_ids']:
            if source_id not in excerpts: raise ValueError('Unknown passive-cue source')
        check_learning_text(card['passive_visual']['description'])
        if card['slot']!='P' and card['passive_visual']['meaningful']:
            raise ValueError('Supplementary passive cue only belongs to P')
        if numeric_tokens(card['counterplay']):
            raise ValueError(f'Counterplay for {card["slot"]} must contain NO numbers, including written number words or stack thresholds: {sorted(numeric_tokens(card["counterplay"]))}. Keep source-supported quantities in the answer and make Counterplay qualitative.')
    for candidate in draft['cooldown_candidates']:
        if any(s not in excerpts for s in candidate['source_ids']): raise ValueError('Unknown cooldown source')
        if numeric_tokens(candidate['reason']): raise ValueError('Cooldown proposals must not introduce numeric values')
    if len({c['slot'] for c in draft['cooldown_candidates']})!=len(draft['cooldown_candidates']):
        raise ValueError('Duplicate supplementary cooldown topics')
    for conflict in draft['conflicts']:
        if any(s not in excerpts for s in conflict['source_ids']): raise ValueError('Unknown conflict source')


def check_verification(value,packet,inventory=None,draft=None):
    schema_check(value,VERIFY_SCHEMA)
    if {c['slot'] for c in value['checks']}!=set('-PQWER'): raise ValueError('Verifier must review every card exactly once')
    known={e['id'] for e in packet['excerpts']}
    if any(s not in known for c in value['conflicts'] for s in c['source_ids']): raise ValueError('Unknown verifier source')
    if inventory is not None:
        for check in value['checks']:
            expected=set() if check['slot']=='-' else {c['id'] for a in inventory['abilities'] if a['slot']==check['slot'] for c in a['core_mechanics']}
            reported=[c['mechanic_id'] for c in check['core_coverage']]
            if set(reported)!=expected or len(reported)!=len(expected):
                raise ValueError('Verifier must account for every frozen supported core mechanic exactly once')
            if draft:
                answer=next(c['answer'] for c in draft['cards'] if c['slot']==check['slot'])
                for coverage in check['core_coverage']:
                    if coverage['covered'] and (not coverage['answer_quote'] or normalized(coverage['answer_quote']) not in normalized(answer)):
                        raise ValueError('Claimed core coverage must quote actual answer text')

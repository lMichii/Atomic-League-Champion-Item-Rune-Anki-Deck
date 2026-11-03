"""Deterministic draft QA, independent of model authoring and human approval."""
from collections import Counter
from pathlib import Path
from .io import canonical,digest,inside,read_json
from .editorial_media import inspect_media
from .generation.presentation import check_learning_row
from .generation.contracts import check_citations,check_draft,check_inventory,check_verification
from .generation.kit_contracts import validate_plan,validate_text,validate_support,freeze_plan


def validate_run(root,run,champion):
    findings=[]
    def issue(severity,code,message,key=None,category='structural'):
        findings.append({'severity':severity,'category':category,'code':code,'id':key or champion['slug'],'message':message})
    packet=read_json(run/'source-packet.json'); cards=read_json(run/'cards.json')['cards']
    qa=read_json(run/'qa.json'); assets=read_json(run/'assets.json')
    if packet['champion']['riot_id']!=champion['riot_id'] or packet['champion']['ddragon_id'].lower()!=champion['slug']:
        issue('error','champion_identity','Source packet belongs to a different champion')
    if qa.get('human_approved') or qa.get('publishable'): issue('error','automatic_approval','Generated run must be unapproved')
    if len({c['id'] for c in cards})!=len(cards): issue('error','duplicate_id','Duplicate card IDs')
    if len({(c['row']['question'],c['row']['answer']) for c in cards})!=len(cards): issue('error','duplicate_content','Duplicate learning cards')
    if sum(c['row']['level']=='L1' for c in cards)!=1: issue('error','overview_coverage','Exactly one L1 overview required')
    if packet['schema_version']==1:
        if Counter(c['row']['slot'] for c in cards if c['row']['level']=='L2')!=Counter('PQWER'):
            issue('error','slot_coverage','Conventional kit must cover P/Q/W/E/R exactly once')
        inventory=read_json(run/'mechanics-inventory.json')
        check_inventory(inventory,packet); check_draft(read_json(run/'ai-draft.json'),packet)
        check_verification(read_json(run/'ai-verification.json'),packet,inventory,read_json(run/'ai-draft.json'))
    else:
        plan=read_json(run/'kit-analysis.json'); inventory=read_json(run/'card-inventory.json')
        validate_plan(plan,packet)
        if {a['slot'] for a in packet['abilities']}-{s['slot'] for s in plan['slots']}:
            issue('error','slot_roles','Every primary Riot slot needs an explicit active/passive/indicator/contextual disposition')
        if inventory!=freeze_plan(plan,champion['slug']): issue('error','variant_inventory','Inventory differs from source-addressed slug identities')
        validate_text(read_json(run/'ai-draft.json'),packet,inventory)
        validate_support(read_json(run/'ai-verification.json'),packet,inventory,read_json(run/'ai-draft.json'))
        if not qa.get('kit_complete_draft') or qa.get('omitted_topics'):
            issue('error','kit_completeness','Unresolved required kit coverage: '+str(qa.get('omitted_topics',[])),category='factual')
    for resource in packet['resources']:
        path=inside(run/'sources',resource['sha256'])
        if not path.is_file() or digest(path.read_bytes())!=resource['sha256']:
            issue('error','source_integrity','Archived source missing/changed: '+resource['url'])
    media_files={r['path']:r for r in assets['files']}; checked=set(); citations=0; media_counts=Counter()
    for card in cards:
        key=card['id']; row=card['row']; check_learning_row(row)
        if key!=row['id'] or not key.startswith('champ:'+champion['slug']+':') or card['entity_id']!='champ:'+str(champion['riot_id']):
            issue('error','card_identity','Readable key and numeric source identity must match the champion',key)
        if card['content_status']!='draft' or card['qa_status']!='needs_review': issue('error','card_status','Draft/pending status required',key)
        if not row['answer'] or not row['counterplay'] or (row['level']=='L1' and not row['build_focus']):
            issue('error','learning_content','Explanation, Counterplay and overview build focus are required',key)
        for claim in card['evidence']['claims']:
            check_citations(claim['citations'],packet); citations+=len(claim['citations'])
        media_counts[row['media_type']]+=1
        for field in ('media_path','icon_path','visual_cue_media_path'):
            path=row.get(field)
            if not path:
                if field!='visual_cue_media_path': issue('error','required_media','Real front/icon media missing',key,'media')
                continue
            record=media_files.get(path); file=inside(run,path)
            if not record or not file.is_file() or digest(file.read_bytes())!=record['sha256']:
                issue('error','media_integrity','Missing/changed media '+path,key,'media'); continue
            if path not in checked: inspect_media(file); checked.add(path)
        kind=card.get('learning_unit',{}).get('kind','ability')
        if row['level']=='L2' and row['slot']!='P' and kind in ('ability','ability_variant','transformation','conditional_effect') and row['media_type']!='gif':
            issue('warning','static_fallback','No source-matched animation; inspect the actual ability/context before accepting the real icon',key,'media')
        issue('warning','manual_visual_review','Human ability/variant/cue matching and current-client appearance review required',key,'media')
        if row['slot']=='P' or kind=='system': issue('warning','passive_visual_cue','Determine whether an important passive/system cue needs supplementary media',key,'media')
    for check in qa['cards']:
        if check.get('missing_supported_core_ids'): issue('error','missing_supported_core',str(check['missing_supported_core_ids']),check['id'],'factual')
        if not check.get('source_supported_draft',False): issue('warning','semantic_review','AI support checker reported unresolved claims; human factual review required',check['id'],'factual')
    if not packet['versions'].get('wiki_revision'): issue('warning','missing_wiki_revision','Detailed Wiki evidence/revision missing; do not infer unquoted mechanics',category='factual')
    if not any(e['provider']=='league_wiki' for e in packet['excerpts']): issue('warning','missing_wiki_excerpts','No usable detailed Wiki excerpts',category='factual')
    if not cards[0].get('versioning',{}).get('verified_game_patch'): issue('warning','unknown_gameplay_patch','Asset release is separate; unknown gameplay patch stays hidden',category='metadata')
    for missing in qa.get('missing_media',[]):
        issue('warning','media_mapping',str(missing['issues']),missing['card_id'],'media')
    for category,field in (('factual','source_conflicts'),('factual','factual_risks'),('source','findings')):
        for finding in qa.get(field,[]): issue('warning',field,str(finding),category=category)
    return {'schema_version':1,'cards':len(cards),'card_ids':[c['id'] for c in cards],
            'errors':sum(f['severity']=='error' for f in findings),'warnings':sum(f['severity']=='warning' for f in findings),
            'findings':findings,'media':dict(media_counts),'decoded_media_files':len(checked),'citations':citations,
            'source_excerpts':len(packet['excerpts']),'wiki_revision':packet['versions'].get('wiki_revision'),
            'asset_version':packet['versions']['ddragon'],'kit_schema':packet['schema_version'],
            'slot_roles':plan['slots'] if packet['schema_version']>1 else [{'slot':s,'role':'passive' if s=='P' else 'active'} for s in 'PQWER'],
            'section_dispositions':plan['section_disposition'] if packet['schema_version']>1 else [],
            'qa_processor_sha256':digest(Path(__file__).read_bytes()),
            'source_packet_sha256':digest(canonical(packet)),'core_coverage_checked':True,
            'all_pending_editorial_review':True,'model_usage':qa['generation'].get('usage',{})}

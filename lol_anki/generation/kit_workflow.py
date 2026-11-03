"""Generic adaptive-kit draft production; approved stores/exporter remain untouched."""
import copy
import difflib
import json
from pathlib import Path
from ..identity import guid,stable_id
from ..io import atomic,canonical,digest,write_json,read_json
from ..validation import ROW_FIELDS
from .ai import AIClient
from .kit_contracts import (KIT_SCHEMA,KIT_DRAFT_SCHEMA,KIT_VERIFY_SCHEMA,
    validate_plan,freeze_plan,validate_text,validate_support,supported)
from .kit_prompts import PLAN,AUTHOR,VERIFY
from .kit_media import collect_kit_media
from .presentation import version_fields,check_learning_row
from .preview import create_previews,page_name

TEACHING_CONTRACT={'counterplay_basis':'source_grounded_inference',
    'build_focus_basis':'broad_learning_orientation',
    'scope':'Applies to every draft; inferred guidance must still follow from cited kit effects. It is not a confirmed mechanical fact or an optimal build.',
    'card_facing_labels':False}


def compact_packet(packet):
    """One copy of relevant source text, without raw data/URLs/media/numeric tables."""
    excerpts=[]
    for e in packet['excerpts']:
        lines=e['text'].splitlines(); selected=[]
        for line in lines:
            if len(line)<45: continue
            if 'NOTICE TO API USERS' in line: continue
            selected.append(line)
        excerpts.append({'id':e['id'],'provider':e['provider'],'text':'\n'.join(selected)[:7500]})
    return {'champion':packet['champion'],'primary_slots':[{'slot':a['slot'],'name':a['name']} for a in packet['abilities']],
            'live_sections':[{k:s[k] for k in ('id','name')} for s in packet['kit_sections']],
            'excerpts':excerpts,'limitations':packet['limitations']}


def usage_report(receipts,cache_folder=None):
    usage=[]
    for r in receipts:
        saved=list((Path(cache_folder)/r['request_sha256']).glob('attempt-*/metadata.json')) if cache_folder else []
        metadata=[read_json(p) for p in saved] or [r['metadata']]
        for meta in metadata:
            u=meta.get('usage')
            usage.extend(u if isinstance(u,list) else [u] if u else [])
    totals={}
    for u in usage:
        if not isinstance(u,dict): continue
        for k,v in u.items():
            if isinstance(v,int): totals[k]=totals.get(k,0)+v
    return {'logical_requests':len(receipts),'recorded_model_attempts':sum(r['attempts'] for r in receipts),
            'available_receipt_usage':totals,'usage_receipts_available':len(usage),
            'scope':'Recorded generation usage; cached replay does not repeat these model calls. Failed-attempt usage may be unavailable.'}


def compile_kit(draft,inventory,packet,assets):
    texts={c['card_id']:c for c in draft['cards']}; media={m['card_id']:m for m in assets['bindings']}
    result=[]; versions=version_fields(packet); champion=packet['champion']
    sections={s['id']:s['name'] for s in packet['kit_sections']}
    for unit in inventory:
        text=texts[unit['card_id']]; binding=media[unit['card_id']]; overview=unit['kind']=='overview'
        image=binding['gif'] or binding['icon']; row={k:'' for k in ROW_FIELDS}
        context=sections.get(unit['context_id'],'').split(',')[0]
        hint='CHAMPION OVERVIEW' if overview else ('IDENTIFY THIS ABILITY' if binding['gif'] else
            ' · '.join(x for x in (champion['name'].upper(),context.upper(),unit['slot']) if x))
        question='What can this champion do?' if overview else ('What does this weapon do?' if unit['kind']=='weapon' else
            'What does this system do?' if unit['kind']=='system' else 'What does this ability do?')
        row.update(id=unit['card_id'],level='L1' if overview else 'L2',category='Champion',
            champion=champion['name'],slot='-' if overview else unit['slot'],
            ability=' / '.join(champion['roles']) if overview else sections.get(unit['subject_id'],unit['title']),front_hint=hint,
            question=question,answer=text['answer'],counterplay=text['counterplay'],build_focus=text['build_focus'],
            priority=text['priority'],patch=versions['verified_game_patch'] or '',review_status='',
            media_type=('portrait' if overview else 'gif' if binding['gif'] else 'icon') if image else 'none',
            media_path=image['path'] if image else '',icon_path=binding['icon']['path'] if binding['icon'] else '',
            source_video_path=binding['video']['path'] if binding['video'] else '',
            source_riot=packet['attribution']['riot'],source_wiki=packet['attribution']['wiki'],
            visual_cue_status='needs_visual_cue_review' if unit['kind']=='system' else '')
        check_learning_row(row)
        result.append({'id':unit['card_id'],'entity_id':f'champ:{champion["riot_id"]}','entity_kind':'champion',
            'content_status':'draft','qa_status':'needs_review','revision':1,'versioning':copy.deepcopy(versions),
            'learning_unit':copy.deepcopy(unit),'evidence':{'riot_url':row['source_riot'],'wiki_url':row['source_wiki'],
                'wiki_revision':packet['versions']['wiki_revision'],'verified_patch':versions['verified_game_patch'],
                'claims':text['facts'],'verification_scope':'Exact citations and fallible AI semantic/completeness check; no human approval'},
            'importance':{'priority':text['priority'],'reason':text['priority_reason']},
            'pedagogy':{'counterplay_basis':'source_grounded_inference','build_focus_basis':'broad_learning_orientation'},
            'uncertainties':text['uncertainties'],'media_review':{'status':'unreviewed','current_client_review':'pending'},'row':row})
    if len({c['id'] for c in result})!=len(result): raise ValueError('Duplicate generated identity')
    if len({(c['row']['question'],c['row']['answer']) for c in result})!=len(result): raise ValueError('Duplicate generated learning text')
    return result


def check_seed(seed,evidence,inventory,packet):
    if seed.get('model_input_sha256')!=digest(canonical(evidence)) or seed.get('inventory_sha256')!=digest(canonical(inventory)):
        raise ValueError('Draft checkpoint does not match these source inputs and learning identities')
    validate_text(seed['draft'],packet,inventory)
    if seed['author_receipt']['output_sha256']!=digest(canonical(seed['draft'])):
        raise ValueError('Draft checkpoint output differs from its recorded model receipt')


def generate_kit(root,config,retriever,packet,source_folder,approved,before,offline,resume_draft=None,readable_ids=False):
    from .workflow import processing_identity,approved_fingerprints
    root=Path(root); processing=processing_identity()
    seed=read_json(resume_draft) if resume_draft else None
    run_id=digest(canonical({'packet':packet,'config':config,'processing':processing,'prompts':[PLAN,AUTHOR,VERIFY],'draft_seed':seed,
                            'schemas':[KIT_SCHEMA,KIT_DRAFT_SCHEMA,KIT_VERIFY_SCHEMA],'base':before}))
    if readable_ids: run_id=digest(canonical({'source_run_id':run_id,'id_style':'ddragon_slug_v1'}))
    folder=root/'build/generated'/packet['champion']['ddragon_id'].lower()/run_id[:20]; folder.mkdir(parents=True,exist_ok=True)
    write_json(folder/'source-packet.json',packet)
    for source in (source_folder/'raw').iterdir(): atomic(folder/'sources'/source.name,source.read_bytes())
    client=AIClient(config['ai'],root/'.cache/generator/ai',offline); evidence=compact_packet(packet)
    plan,plan_receipt=client.generate('kit-inventory',PLAN,evidence,KIT_SCHEMA,lambda v:validate_plan(v,packet))
    inventory=freeze_plan(plan,packet['champion']['ddragon_id'].lower() if readable_ids else packet['champion']['riot_id'])
    if seed:
        check_seed(seed,evidence,inventory,packet)
        atomic(folder/'draft-seed.json',canonical(seed))
    write_json(folder/'kit-analysis.json',plan); write_json(folder/'card-inventory.json',inventory)
    media_packet={**packet,'slot_roles':plan['slots'],'relationships':plan['relationships']}
    assets,frames,frame_info=collect_kit_media(retriever,media_packet,inventory,folder)
    passes=[]; request={'sources':evidence,'inventory':inventory}
    for number in range(1,config['generation'].get('max_content_passes',3)+1):
        if number==1 and seed:
            draft,author=seed['draft'],seed['author_receipt']
        else:
            draft,author=client.generate('kit-author',AUTHOR,request,KIT_DRAFT_SCHEMA,lambda v:validate_text(v,packet,inventory))
        write_json(folder/'draft-checkpoint.json',{'schema_version':1,'draft':draft,'author_receipt':author,
            'model_input_sha256':digest(canonical(evidence)),'inventory_sha256':digest(canonical(inventory))})
        verification,verifier=client.generate('kit-verify',VERIFY,{'sources':evidence,'inventory':inventory,
            'section_disposition':plan['section_disposition'],'draft':draft,
            'pedagogical_metadata':TEACHING_CONTRACT},KIT_VERIFY_SCHEMA,
            lambda v:validate_support(v,packet,inventory,draft))
        failures=sum(not supported(c) for c in verification['checks'])+int(not verification['kit_complete'])+len(verification['omitted_topics'])
        passes.append({'pass':number,'author':author,'verifier':verifier,'support_issues':failures})
        if not failures: break
        request={'sources':evidence,'inventory':inventory,'previous_draft':draft,'support_review':verification}
    cards=compile_kit(draft,inventory,packet,assets); base=approved.content(); candidate=copy.deepcopy(base)
    for card in cards: card['revision']=base['build_epoch']
    candidate['cards'].extend(cards)
    if candidate['cards'][:len(base['cards'])]!=base['cards']: raise ValueError('Approved content changed')
    used=create_previews(cards,folder)
    checks={c['card_id']:c for c in verification['checks']}; bindings={m['card_id']:m for m in assets['bindings']}
    findings=packet['findings']+assets['findings']
    card_qa=[]
    for card in cards:
        key=card['id']; check=checks[key]; unit=card['learning_unit']; binding=bindings[key]
        missing=[c['mechanic_id'] for c in check['core_coverage'] if not c['covered']]
        if not supported(check): findings.append({'code':'ai_support_check_failed','id':key,'issues':check['issues'],'missing_core_ids':missing})
        inferred=[c for c in card['evidence']['claims'] if c['basis']!='source_assertion']
        card_qa.append({'id':key,'kind':unit['kind'],'purpose':unit['purpose'],'status':'draft_not_approved',
            'source_supported_draft':supported(check),'ai_support_check':check,'missing_supported_core_ids':missing,
            'confirmed_vs_inferred':{'answer_assertions':'Cited draft claims, not human verified',
                'answer_inferences':inferred,'counterplay':'source_grounded_inference','build_focus':'broad_learning_orientation'},
            'core_mechanics':unit['core_mechanics'],'advanced_exceptions':unit['advanced_exceptions'],
            'unsupported_claims':unit['unsupported_claims'],'issues':card['uncertainties']+check['issues'],
            'media':binding,'preview':'previews/'+page_name(card),'manual_visual_review_required':True})
    receipts=[plan_receipt]+[p[t] for p in passes for t in ('author','verifier')]
    qa={'schema_version':2,'human_approved':False,'publishable':False,'new_cards':len(cards),'extra_cards_created':0,
        'cards':card_qa,'features':plan['features'],'kit_complete_draft':verification['kit_complete'],
        'omitted_topics':verification['omitted_topics'],'findings':findings,'missing_media':assets['missing_media'],
        'source_conflicts':plan['conflicts']+draft['conflicts']+verification['conflicts'],
        'factual_risks':plan['factual_risks']+draft['factual_risks']+verification['factual_risks'],
        'source_versions':packet['versions'],'versioning':version_fields(packet),'media_references':used,
        'passive_frame_evidence':frame_info,'cooldown_candidates':draft['cooldown_candidates'],
        'base_approved_hashes':before,'identity_map':{c['id']:{'guid':guid(c['id']),'nid':stable_id(c['id'],1800000000000),
            'cid':stable_id(c['id'],2300000000000)} for c in cards},
        'generation':{'run_id':run_id,'processing':processing,'inventory':plan_receipt,'passes':passes,
            'usage':usage_report(receipts,client.folder),'model_source_characters':len(canonical(evidence).decode('utf-8'))},
        'approval_blockers':['All cards require editorial approval and source-scope review.',
            'Weapon/ability image matching and all animations/cues require manual visual review.',
            'Missing variant animations use matched icons; generic slot clips are not variant verification.',
            'Unknown gameplay patch is hidden; source-supported draft status is not human QA.'],
        'limitations':packet['limitations']+['AI planning/verification is fallible and cannot prove every source topic was inventoried.']}
    if not verification['kit_complete'] or verification['omitted_topics']:
        qa['findings'].append({'code':'kit_completeness_review','omitted_topics':verification['omitted_topics']})
    for stage,receipt in [('inventory',plan_receipt)]+[(f'{task}-pass-{p["pass"]}',p[task]) for p in passes for task in ('author','verifier')]:
        source=client.folder/receipt['request_sha256']
        for path in source.rglob('*'):
            if path.is_file(): atomic(folder/'ai'/stage/path.relative_to(source),path.read_bytes())
    proposal={'schema_version':2,'kind':'champion_draft','approval_required':True,'apply_supported':False,
        'base_sha256':digest(canonical(base)),'candidate_sha256':digest(canonical(candidate)),
        'sources_sha256':before['sources'],'changed_ids':[c['id'] for c in cards],
        'source_packet_sha256':digest(canonical(packet)),'asset_manifest_sha256':digest(canonical(assets)),
        'inventory_sha256':digest(canonical(inventory)),'candidate':candidate,'status':'unapproved_generated_proposal'}
    for name,value in [('cards.json',{'schema_version':2,'cards':cards}),('candidate.json',candidate),
        ('proposal.json',proposal),('qa.json',qa),('ai-draft.json',draft),('ai-verification.json',verification),
        ('media-report.json',{'schema_version':1,'bindings':assets['bindings'],'missing_or_ambiguous':assets['missing_media'],
            'human_verified':False,'passive_frames':frame_info})]: write_json(folder/name,value)
    diff=''.join(difflib.unified_diff(canonical(base).decode().splitlines(True),canonical(candidate).decode().splitlines(True),
        fromfile='approved-100',tofile=f'proposed-{len(candidate["cards"])}-drafts'))
    atomic(folder/'changes.diff',diff.encode())
    lines=[f'# {packet["champion"]["name"]} — unapproved adaptive-kit QA','',
        f'{len(cards)} drafts; {len(base["cards"])} approved cards unchanged. No approval, publication or APKG export.','',
        'Gameplay patch: unknown unless independently established; asset version: '+qa['versioning']['asset_version']+'.','',
        '## Learning inventory','', '| ID | Type | Why this card exists | AI support |','| --- | --- | --- | --- |']
    for c in card_qa: lines.append(f'| `{c["id"]}` | {c["kind"]} | {c["purpose"]} | {"supported draft" if c["source_supported_draft"] else "REVIEW REQUIRED"} |')
    for title,values in [('Source conflicts',qa['source_conflicts']),('Factual risks',qa['factual_risks']),
        ('Missing / ambiguous media',qa['missing_media']),('Findings',qa['findings']),('Approval blockers',qa['approval_blockers'])]:
        lines+=['','## '+title,'']+(['- '+(json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v) for v in values] or ['None detected; this is not proof of completeness.'])
    lines+=['','## Model usage','',json.dumps(qa['generation']['usage'],ensure_ascii=False),
        '', 'Detailed core coverage, conditions, exact citations, inference types and visual mapping are in qa.json, card-inventory.json and kit-analysis.json.']
    atomic(folder/'QA.md',('\n'.join(lines)+'\n').encode())
    atomic(folder/'REVIEW.md',(f'# Unapproved adaptive-kit proposal\n\n{len(cards)} drafts. Proposal SHA-256: `{digest(canonical(proposal))}`.\n\nReview previews/index.html, QA.md, qa.json, kit-analysis.json, card-inventory.json, media-review data in assets.json, source-packet.json and changes.diff.\n\nAll approved records are preserved. The champion_draft proposal is rejected by apply-review. No approval, source/media promotion, APKG export or publication is performed.\n').encode())
    if approved_fingerprints(approved)!=before: raise ValueError('Approved store changed')
    return {'status':'drafts_ready_for_review','champion':packet['champion'],'cards':len(cards),
        'approved_cards_unchanged':len(base['cards']),'output':str(folder),'previews':str(folder/'previews/index.html'),
        'ai_support_issues':passes[-1]['support_issues'],'model_usage':qa['generation']['usage'],
        'published':False,'approved':False}

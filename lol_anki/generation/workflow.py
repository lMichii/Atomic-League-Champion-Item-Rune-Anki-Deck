"""One-identifier workflow. Drafts/proposals only; never approval or APKG export."""
import copy
import difflib
import json
from pathlib import Path
import shutil
import tomllib
import subprocess
from ..identity import guid,stable_id
from ..io import atomic,canonical,digest,read_json,write_json,inside
from ..project import Project
from ..validation import ROW_FIELDS
from .ai import AIClient
from .assets import collect_assets,passive_frames
from .contracts import (DRAFT_SCHEMA,VERIFY_SCHEMA,INVENTORY_SCHEMA,check_draft,check_verification,
                        check_inventory,support_check_passed,core_coverage_failures)
from .evidence import Retriever
from .preview import create_previews
from .prompts import AUTHOR,VERIFIER,MECHANICS
from .presentation import version_fields,check_learning_row
from ..v4 import CSS,QFMT,AFMT,FIELD_NAMES


def approved_fingerprints(project):
    return {k:digest(project.path(k).read_bytes()) for k in ('content','sources','lock')}


def processing_identity():
    """A changed processor/runtime receives a new history directory, never overwrites one."""
    directory=Path(__file__).resolve().parent
    sources={p.name:p.read_text(encoding='utf-8') for p in sorted(directory.glob('*.py'))}
    for name in ('io.py','cache.py','identity.py','media.py','v4.py'):
        sources['../'+name]=(directory.parent/name).read_text(encoding='utf-8')
    ffmpeg=subprocess.run(['ffmpeg','-version'],check=True,capture_output=True,text=True,timeout=10).stdout.splitlines()[0]
    return {'source_sha256':digest(canonical(sources)),'ffmpeg':ffmpeg,
            'v4_sha256':digest(canonical({'css':CSS,'front':QFMT,'back':AFMT,'fields':FIELD_NAMES}))}


def stable_key(cid,level,slot):
    return f'champ:{cid}:overview:L1' if level=='L1' else f'champ:{cid}:{slot.lower()}:recognize:L2'


def compile_cards(draft,packet,assets,include_proposed_passive_cue=True,readable_ids=False):
    cards=[]; cid=packet['champion']['riot_id']; name=packet['champion']['name']
    abilities={a['slot']:a for a in packet['abilities']}
    versioning=version_fields(packet)
    for slot in '-PQWER':
        authored=next(c for c in draft['cards'] if c['slot']==slot)
        level=authored['level']; key=stable_key(packet['champion']['ddragon_id'].lower() if readable_ids else cid,level,slot)
        row={k:'' for k in ROW_FIELDS}
        row.update(id=key,level=level,category='Champion',champion=name,slot=slot,
                   ability=' / '.join(packet['champion']['roles']) if level=='L1' else abilities[slot]['name'],
                   question='What can this champion do?' if level=='L1' else 'What does this ability do?',
                   answer=authored['answer'],counterplay=authored['counterplay'],priority=authored['priority'],
                   source_riot=packet['attribution']['riot'],source_wiki=packet['attribution']['wiki'],
                   patch=versioning['verified_game_patch'] or '',build_focus=authored['build_focus'],
                   review_status='')
        if level=='L1':
            portrait=assets['portrait']
            row.update(media_type='portrait' if portrait else 'none',media_path=portrait['path'] if portrait else '',
                       icon_path=portrait['path'] if portrait else '',front_hint='CHAMPION OVERVIEW')
        else:
            media=assets['abilities'][slot]
            chosen=media['icon'] if slot=='P' else (media['gif'] or media['icon'])
            row.update(media_type='icon' if slot=='P' or not media['gif'] else 'gif',
                       media_path=chosen['path'] if chosen else '',icon_path=media['icon']['path'] if media['icon'] else '',
                       source_video_path=media['video']['path'] if media['video'] else '',
                       front_hint=name.upper()+' · PASSIVE' if slot=='P' else ('IDENTIFY THIS ABILITY' if media['gif'] else name.upper()+' · '+slot))
            if slot=='P':
                cue=authored['passive_visual']
                proposed=bool(include_proposed_passive_cue and cue['meaningful'] and media['gif'])
                row.update(visual_cue_status='needs_visual_cue_review',visual_cue_media_path=media['gif']['path'] if proposed else '',
                           visual_cue_description=cue['description'] if proposed else '')
        check_learning_row(row)
        cards.append({'id':key,'entity_id':f'champ:{cid}','entity_kind':'champion','content_status':'draft','qa_status':'needs_review',
                      'versioning':copy.deepcopy(versioning),
                      'revision':1,'evidence':{'riot_url':row['source_riot'],'wiki_url':row['source_wiki'],
                          'wiki_revision':packet['versions']['wiki_revision'],'verified_patch':versioning['verified_game_patch'],
                          'claims':authored['facts'],'verification_scope':'Citation matching + AI support check; not editorial approval'},
                      'importance':{'priority':authored['priority'],'reason':authored['priority_reason']},
                      'pedagogy':{'counterplay_basis':'source_grounded_inference','build_focus_basis':'broad_learning_orientation'},
                      'uncertainties':authored['uncertainties'],'media_review':{'status':'unreviewed','current_client_review':'pending'},
                      'row':row})
    return cards


def draft_qa(cards,packet,assets,verification,inventory=None):
    findings=list(packet['findings'])+list(assets['findings'])
    checks={c['slot']:c for c in verification['checks']}
    per_card=[]
    for card in cards:
        slot=card['row']['slot']; check=checks[slot]
        supported=support_check_passed(check,inventory)
        issues=list(card['uncertainties'])+check['issues']
        missing=core_coverage_failures(check,inventory) if inventory else []
        if missing: findings.append({'code':'missing_supported_core_mechanic','id':card['id'],'mechanic_ids':missing})
        if not supported: findings.append({'code':'ai_support_check_failed','id':card['id'],'issues':issues})
        per_card.append({'id':card['id'],'slot':slot,'priority':card['importance'],'status':'draft_not_approved',
                         'citation_matching':'passed','ai_support_check':check,'source_supported_draft':supported,
                         'confirmed_vs_inferred':{'answer':'Cited source-supported draft assertions; human review required',
                                                 'counterplay':'inferred guidance','build_focus':'inferred broad learning orientation'},
                         'issues':issues,'media_type':card['row']['media_type'],
                         'versioning':card['versioning'],
                         'mechanics':next((copy.deepcopy(a) for a in inventory['abilities'] if a['slot']==slot),None) if inventory else None,
                         'missing_supported_core_ids':missing,
                         'visual_cue_status':'proposed_unverified' if card['row']['visual_cue_media_path'] else 'unverified',
                         'manual_visual_review_required':True})
    return {'schema_version':1,'cards':per_card,'findings':findings,'source_versions':packet['versions'],
            'versioning':version_fields(packet),
            'source_conflicts':verification['conflicts'],'factual_risks':verification['factual_risks'],
            'human_approved':False,'publishable':False,'new_cards':6,'extra_cards_created':0,
            'approval_blockers':['All six cards are drafts requiring explicit editorial approval.',
                                 'All clips/cues need manual visual verification.']+
                                ([] if version_fields(packet)['verified_game_patch'] else ['Game patch label has not been independently established.']),
            'limitations':packet['limitations']+['Exact-quote matching does not prove semantic truth.',
                                               'AI verification is fallible and is not a human content or visual review.']}


def generate(root,identifier,offline=False,sources_only=False,cached_sources=False,resume_draft=None,
             source_input=None,config_path=None,readable_ids=False):
    root=Path(root)
    config=tomllib.loads((inside(root,config_path) if config_path else root/'generation.toml').read_text('utf-8'))
    if config['ai']['provider'] not in ('codex','openai') or not 1<=config['ai']['attempts']<=5:
        raise ValueError('Configure codex/openai and 1-5 AI transport/schema attempts')
    if not 1<=config['generation'].get('max_content_passes',3)<=5:
        raise ValueError('Configure 1-5 bounded content-review passes')
    if config['generation'].get('semantic_verification',True) is not True:
        raise ValueError('Semantic support verification cannot be disabled')
    approved=Project(root,profile='batch01')
    before=approved_fingerprints(approved)
    retriever=Retriever(root,config,offline or cached_sources)
    if source_input:
        source_folder=inside(root,source_input); packet=read_json(source_folder/'packet.json')
        for resource in packet['resources']:
            if digest(inside(source_folder/'raw',resource['sha256']).read_bytes())!=resource['sha256']:
                raise ValueError('Pinned batch source changed: '+resource['url'])
        if config['retrieval'].get('ddragon_version')!=packet['versions']['ddragon']:
            raise ValueError('Pinned batch source release does not match configuration')
    else:
        packet,source_folder=retriever.collect(identifier)
    # Resume authoring against the same snapshots while still allowing missing
    # real media/model calls; --offline remains strictly network/model free.
    retriever.offline=offline; retriever.cache.offline=offline
    cid=packet['champion']['riot_id']; key=packet['champion']['ddragon_id'].lower()
    if any(c['entity_id']==f'champ:{cid}' for c in approved.content()['cards']):
        raise ValueError('Champion already has approved content; this command cannot overwrite it')
    if sources_only:
        return {'status':'sources_collected','champion':packet['champion'],'packet':str(source_folder/'packet.json')}
    if packet['schema_version']>=2:
        from .kit_workflow import generate_kit
        return generate_kit(root,config,retriever,packet,source_folder,approved,before,offline,resume_draft,readable_ids)
    processing=processing_identity()
    run_id=digest(canonical({'packet':packet,'config':config,'processing':processing,'author':AUTHOR,'verifier':VERIFIER,
                            'mechanics_prompt':MECHANICS,'inventory_schema':INVENTORY_SCHEMA,
                            'draft_schema':DRAFT_SCHEMA,'verify_schema':VERIFY_SCHEMA,'base':before}))
    if readable_ids: run_id=digest(canonical({'source_run_id':run_id,'id_style':'ddragon_slug_v1'}))
    folder=root/'build/generated'/key/run_id[:20]; folder.mkdir(parents=True,exist_ok=True)
    write_json(folder/'source-packet.json',packet)
    for source in (source_folder/'raw').iterdir(): atomic(folder/'sources'/source.name,source.read_bytes())
    assets=collect_assets(retriever,packet,folder)
    images,frame_metadata=passive_frames(folder,assets) if config['generation'].get('passive_frame_review',True) else ([],[])
    client=AIClient(config['ai'],root/'.cache/generator/ai',offline)
    # Retrieval provenance stays outside the model request; prose depends only on evidence.
    model_packet={k:v for k,v in packet.items() if k not in ('resources','portrait_url')}
    model_packet=copy.deepcopy(model_packet)
    for excerpt in model_packet['excerpts']: excerpt.pop('sha256',None)
    model_packet['visual_frames']=frame_metadata
    inventory,inventory_receipt=client.generate('mechanics',MECHANICS,model_packet,INVENTORY_SCHEMA,lambda v:check_inventory(v,packet))
    write_json(folder/'mechanics-inventory.json',inventory)
    passes=[]; request_data={'packet':model_packet,'mechanics_inventory':inventory}
    for content_pass in range(1,config['generation'].get('max_content_passes',3)+1):
        draft,author_receipt=client.generate('author',AUTHOR,request_data,DRAFT_SCHEMA,lambda v:check_draft(v,packet),images)
        verification,verify_receipt=client.generate('verify',VERIFIER,{'packet':model_packet,'draft':draft,'mechanics_inventory':inventory},VERIFY_SCHEMA,lambda v:check_verification(v,packet,inventory,draft),images)
        failures=sum(not support_check_passed(c,inventory) for c in verification['checks'])
        passes.append({'pass':content_pass,'author':author_receipt,'verifier':verify_receipt,'support_issues':failures})
        if not failures: break
        request_data={'packet':model_packet,'mechanics_inventory':inventory,'previous_draft':draft,'support_review':verification}
    cards=compile_cards(draft,packet,assets,config['generation'].get('include_proposed_passive_cue',True),readable_ids)
    qa=draft_qa(cards,packet,assets,verification,inventory)
    qa['source_conflicts']=draft['conflicts']+qa['source_conflicts']
    qa['factual_risks']=draft['factual_risks']+qa['factual_risks']
    qa['cooldown_candidates']=draft['cooldown_candidates']
    qa['base_approved_hashes']=before
    qa['generation']={'author':author_receipt,'verifier':verify_receipt,'mechanics':inventory_receipt,'run_id':run_id,'passes':passes,'processing':processing}
    qa['passive_frame_evidence']=frame_metadata
    source=client.folder/inventory_receipt['request_sha256']
    for p in source.rglob('*'):
        if p.is_file(): atomic(folder/'ai/mechanics'/p.relative_to(source),p.read_bytes())
    for step in passes:
        for task in ('author','verifier'):
            receipt=step[task]; source=client.folder/receipt['request_sha256']
            target=folder/'ai'/f"{task}-pass-{step['pass']}"
            for p in source.rglob('*'):
                if p.is_file(): atomic(target/p.relative_to(source),p.read_bytes())
    write_json(folder/'ai-draft.json',draft); write_json(folder/'ai-verification.json',verification)
    base=approved.content(); candidate=copy.deepcopy(base)
    for card in cards: card['revision']=base['build_epoch']
    candidate['cards'].extend(cards)
    if candidate['cards'][:-6]!=base['cards']: raise ValueError('Approved card preservation failure')
    write_json(folder/'cards.json',{'schema_version':1,'cards':cards})
    write_json(folder/'candidate.json',candidate)
    used=create_previews(cards,folder)
    qa['media_references']=used
    qa['identity_map']={c['id']:{'guid':guid(c['id']),'nid':stable_id(c['id'],1800000000000),'cid':stable_id(c['id'],2300000000000)} for c in cards}
    proposal={'schema_version':1,'kind':'champion_draft','approval_required':True,'apply_supported':False,
              'base_sha256':digest(canonical(base)),'candidate_sha256':digest(canonical(candidate)),
              'sources_sha256':before['sources'],'changed_ids':[c['id'] for c in cards],
              'source_packet_sha256':digest(canonical(packet)),'asset_manifest_sha256':digest(canonical(assets)),
              'new_source_paths':sorted(s.name for s in (folder/'sources').iterdir()),
              'status':'unapproved_generated_proposal','candidate':candidate}
    write_json(folder/'proposal.json',proposal)
    diff=''.join(difflib.unified_diff(canonical(base).decode().splitlines(True),canonical(candidate).decode().splitlines(True),fromfile='approved-100',tofile='proposed-106-drafts'))
    atomic(folder/'changes.diff',diff.encode())
    write_json(folder/'qa.json',qa)
    lines=[f"# {packet['champion']['name']} — unapproved generation QA",'',
           'Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.','',
           f"Sources: Data Dragon {packet['versions']['ddragon']}; CommunityDragon {packet['versions']['communitydragon_requested']}; Wiki revision {packet['versions']['wiki_revision'] or 'unavailable'}.",
           'Game patch label: '+(qa['versioning']['verified_game_patch'] or 'unknown (not inferred from asset release).'),'',
           '## Card review','', '| ID | Priority | AI source-support check | Visual QA |','| --- | --- | --- |']
    for c in qa['cards']:
        lines.append(f"| `{c['id']}` | {c['priority']['priority']} | {'supported draft' if c['source_supported_draft'] else 'REVIEW REQUIRED'} | {c['visual_cue_status']} |")
    lines+=['','## Supported core coverage','',
            'Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.','',
            '| Slot | Supported core ID | Included in explanation |','| --- | --- | --- |']
    for check in verification['checks']:
        for core in check['core_coverage']:
            lines.append(f"| {check['slot']} | `{core['mechanic_id']}` | {'yes' if core['covered'] else 'NO — repair/review required'} |")
    for heading,values in (('Findings',qa['findings']),('Source conflicts',qa['source_conflicts']),('Factual risks',qa['factual_risks']),('Cooldown topics (no cards created)',qa['cooldown_candidates'])):
        lines+=['', '## '+heading,'']
        lines += ['- '+(json.dumps(v,ensure_ascii=False) if isinstance(v,dict) else v) for v in values] or ['None detected; this is not a guarantee of completeness.']
    lines+=['','## Approval blockers','']+['- '+v for v in qa['approval_blockers']]
    lines+=['','## Limits','']+['- '+v for v in qa['limitations']]
    atomic(folder/'QA.md',('\n'.join(lines)+'\n').encode())
    atomic(folder/'REVIEW.md',(f"# Unapproved champion proposal\n\nProposal SHA-256: `{digest(canonical(proposal))}`\n\nInspect previews/index.html, QA.md, cards.json, mechanics-inventory.json, source-packet.json and changes.diff.\n\nOnly six draft IDs are added; all {len(base['cards'])} approved records are preserved.\n\nAsset release and verified game patch are separate metadata fields. Unknown game patches, source references, inference labels and review statuses are not learning text.\n\nThis proposal cannot be passed directly to apply-review. An editor must review claims, sources, visual cues and statuses, promote sources/media explicitly, and then create the ordinary editorial proposal. No automatic approval or APKG export occurs.\n").encode())
    if approved_fingerprints(approved)!=before: raise ValueError('Approved store changed during generation')
    return {'status':'drafts_ready_for_review','champion':packet['champion'],'cards':6,
            'approved_cards_unchanged':len(base['cards']),'output':str(folder),'previews':str(folder/'previews/index.html'),
            'proposal_sha256':digest(canonical(proposal)),'ai_support_issues':sum(not c['source_supported_draft'] for c in qa['cards']),
            'published':False,'approved':False}

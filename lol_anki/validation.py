"""Structural errors block packaging. Unverified facts remain explicit warnings."""
from collections import Counter
import re
from .cache import Cache
from .identity import guid, stable_id
from .io import canonical, digest, inside, read_json, write_json
from .v4 import FIELD_NAMES, render_fields

ROW_FIELDS = {'id','level','category','champion','slot','ability','question','answer',
              'counterplay','cooldown','priority','source_riot','source_wiki','patch',
              'media_type','media_path','poster_path','icon_path','front_hint','review_status',
              'source_video_path','build_focus','visual_cue_description','visual_cue_media_path','visual_cue_status'}


def validate(project, content=None, check_lock=True, sources=None, check_source_lock=True):
    content = project.content() if content is None else content
    sources = project.sources() if sources is None else sources
    findings = []
    def issue(severity, code, key, message):
        findings.append({'severity': severity, 'code': code, 'id': key, 'message': message})
    if content.get('schema_version') != 1 or not isinstance(content.get('cards'), list):
        raise ValueError('Unsupported authored-content schema')
    if check_lock and digest(canonical(content)) != read_json(project.path('lock'))['content_sha256']:
        issue('error', 'unreviewed_content', 'content', 'Content differs from reviewed lock; use propose and apply-review')
    source_lock = read_json(project.path('lock')).get('sources_sha256')
    if check_source_lock and source_lock and digest(project.path('sources').read_bytes()) != source_lock:
        issue('error', 'unreviewed_sources', 'sources', 'Source/media provenance differs from migration lock')
    if sources.get('schema_version') != 1:
        issue('error', 'source_schema', 'sources', 'Unsupported source schema')
    for snap in sources['snapshots']:
        p = inside(project.root, snap['path'])
        if not p.is_file() or digest(p.read_bytes()) != snap['sha256']:
            issue('error', 'source_hash', snap['path'], 'Archived source missing or modified')
        if snap['upstream_version'] == 'unknown_legacy_latest':
            issue('warning', 'mutable_legacy_source', snap['legacy_path'], 'CDragon release unknown; archived bytes pinned by SHA-256')
    ids, nids, cids, guids, semantics, prose = (Counter() for _ in range(6))
    used = set()
    champions = {}
    lock = read_json(project.path('lock'))
    for card in content['cards']:
        key = card.get('id', '<missing>')
        r = card.get('row', {})
        editorial=bool(card.get('editorial_review'))
        if set(r) != ROW_FIELDS or not all(isinstance(v, str) for v in r.values()):
            issue('error', 'row_schema', key, 'Expected exact v4 row fields containing strings')
            continue
        if key != r['id'] or not re.fullmatch(r'[a-z0-9_:\-]+:L[0-3]', key) or not key.endswith(':'+r['level']):
            issue('error', 'identity', key, 'Card/row key mismatch or invalid stable key')
        ids[key] += 1
        nid, cid, g = stable_id(key,1800000000000), stable_id(key,2300000000000), guid(key)
        nids[nid] += 1; cids[cid] += 1; guids[g] += 1
        expected = lock['identities'].get(key)
        if expected and expected != {'nid': nid, 'cid': cid, 'guid': g}:
            issue('error', 'identity_drift', key, 'Published Anki identity differs from identity lock')
        if not isinstance(card.get('revision'), int) or not 0 < card['revision'] <= content.get('build_epoch', 0):
            issue('error', 'revision', key, 'Revision must be positive and no later than build epoch')
        if card.get('content_status') not in ('curated_legacy', 'draft', 'curated') or card.get('qa_status') not in ('needs_review','approved','blocked'):
            issue('error', 'status', key, 'Invalid content or QA status')
        if card.get('qa_status') == 'blocked':
            issue('error', 'qa_blocked', key, 'Card explicitly blocked by QA')
        if card.get('content_status') == 'draft':
            issue('error', 'draft', key, 'Draft content cannot be exported')
        if r['level'] not in ('L0','L1','L2'):
            issue('error', 'unsupported_level', key, 'L3 exact stats reserved; requires an implemented evidence gate before export')
        if not r['question'] or not r['answer'] or r['priority'] not in ('A','B','C'):
            issue('error', 'content_required', key, 'Question, answer and priority A/B/C required')
        if not editorial and r['patch'] != project.config['game_patch']:
            issue('error', 'patch_mismatch', key, 'Authored patch differs from selected project patch')
        if r['level'] != 'L0':
            entity = next((e for e in sources['entities'] if e['id'] == card.get('entity_id')), None)
            if not entity or entity['name'] != r['champion'] or card.get('entity_kind') != 'champion':
                issue('error', 'entity', key, 'Champion must resolve to a stable Riot numeric entity')
            champions.setdefault(r['champion'], []).append(r)
        elif card.get('entity_kind') != 'term':
            issue('error', 'entity', key, 'L0 must use a terminology entity')
        concept = 'timer' if ':timer:' in key else ('recognize' if r['level']=='L2' else r['level'])
        unit=card.get('learning_unit')
        semantic=(unit['kind'],unit['subject_id'],unit['context_id']) if editorial and unit else (r['slot'],concept)
        semantics[(card.get('entity_id'), r['level'], semantic)] += 1
        prose[(r['level'], re.sub(r'\s+',' ',r['question']).strip().lower(), re.sub(r'\s+',' ',r['answer']).strip().lower())] += 1
        evidence = card.get('evidence', {})
        if evidence.get('riot_url') != r['source_riot'] or evidence.get('wiki_url') != r['source_wiki']:
            issue('error', 'evidence_mismatch', key, 'Evidence URLs must match authored attributions')
        if not r['source_riot'] or not r['source_wiki']:
            issue('warning', 'missing_source', key, 'Riot/Wiki attribution missing; do not infer facts')
        evidence_complete = bool(evidence.get('wiki_revision') and evidence.get('wiki_snapshot')
                                 and evidence.get('verified_patch') == r['patch'] and evidence.get('claims'))
        if not evidence_complete:
            issue('warning', 'unverified_mechanics', key, 'Missing patch/revision/snapshot/claim evidence; retained legacy wording requires review')
        if card.get('qa_status')=='approved':
            if editorial:
                try:
                    if not project.config.get('editorial_profile'): raise ValueError('Reviewed additions require the editorial profile')
                    from .editorial_contract import validate_reviewed
                    validate_reviewed(card,project.root)
                    if not r['patch']: issue('warning','unknown_gameplay_patch',key,'Gameplay patch unknown; hidden in the card presentation')
                    if card['editorial_review']['media_lineage']['fallback']: issue('warning','reviewed_static_fallback',key,card['editorial_review']['media'].get('fallback_reason') or 'Explicitly accepted matched static fallback; animation remains unresolved')
                    if card['editorial_review'].get('distribution_status')!='cleared': issue('warning','distribution_review_pending',key,'Media/source distribution rights remain a separate review')
                except (OSError,ValueError,KeyError,TypeError) as ex: issue('error','editorial_review_invalid',key,str(ex))
            elif not evidence_complete or not r['source_riot'] or not r['source_wiki']:
                issue('error', 'unsupported_qa_approval', key, 'QA approval requires patch/revision/snapshot and claim evidence')
            else:
                try:
                    snap = evidence['wiki_snapshot']
                    p = inside(project.root, snap['path'])
                    if digest(p.read_bytes()) != snap['sha256']:
                        raise ValueError('Wiki evidence hash mismatch')
                    claims = evidence['claims']
                    if not str(evidence['wiki_revision']).isdigit() or not isinstance(claims,list) or any(not all(claim.get(k) for k in ('field','claim','locator')) for claim in claims):
                        raise ValueError('Expected numeric Wiki revision and precise field/claim/locator citations')
                except (OSError,ValueError,KeyError,TypeError,AttributeError) as ex:
                    issue('error', 'invalid_evidence', key, str(ex))
        if card.get('qa_status') != 'approved':
            issue('warning', 'qa_pending', key, r['review_status'])
        media_review = card.get('media_review',{})
        if media_review.get('current_client_review')=='pending':
            issue('warning','current_client_visual_review',key,'Official clip/contact sheet reviewed; current-client and skin-specific appearance still requires manual review')
        if card.get('pedagogy',{}).get('counterplay_basis')=='source_grounded_inference':
            issue('warning','editorial_counterplay',key,'Counterplay is a qualitative teaching inference from cited mechanics, not a measured matchup guarantee')
        if r['level']=='L2' and r['slot']=='P':
            if r['media_type'] != 'icon' or r['champion'].upper() not in r['front_hint']:
                issue('error', 'passive_front', key, 'Passive must use icon and champion-identifying hint')
            if r.get('visual_cue_status') == 'needs_visual_cue_review':
                issue('warning', 'passive_cue_pending', key, 'Optional passive cue not verified')
            if r['visual_cue_media_path'] and r['visual_cue_status'] != 'approved':
                issue('error', 'passive_cue_unreviewed', key, 'Added passive cue must be approved')
        if not editorial and r['level']=='L2' and r['slot'] in 'QWER' and concept=='recognize' and r['media_type']!='gif':
            severity = 'warning' if card.get('content_status')=='curated_legacy' else 'error'
            issue(severity, 'active_gif_missing', key, 'Active recognition has no GIF; inherited icon fallback requires review')
        try:
            media_root = project.media_root_for(r)
            render_fields(r, media_root, used)
            for column in ('media_path','icon_path','poster_path','source_video_path','visual_cue_media_path'):
                if not r[column]:
                    continue
                p = inside(media_root/'media', str(r[column]).removeprefix('media/'))
                if not r[column].startswith('media/') or not p.is_file():
                    raise ValueError(f'Missing/unsafe {column}: {r[column]}')
                expected_hash = sources['media_sha256'].get(r[column])
                if not expected_hash or digest(p.read_bytes()) != expected_hash:
                    raise ValueError(f'Unreviewed or changed media bytes: {r[column]}')
                ext = p.suffix.lower()
                if ext in ('.png','.jpg','.gif'):
                    Cache.validate(p.read_bytes(), ext[1:])
                if column=='media_path' and r['media_type']=='gif':
                    from .media import gif_info
                    info = gif_info(p.read_bytes())
                    if ext!='.gif' or info['frames']<2 or info['loop']!=0:
                        raise ValueError('Active GIF must animate and loop infinitely')
        except (ValueError, KeyError, FileNotFoundError) as ex:
            issue('error', 'media', key, str(ex))
    for counter, code in ((ids,'duplicate_id'),(nids,'note_id_collision'),(cids,'card_id_collision'),(guids,'guid_collision'),(semantics,'duplicate_concept'),(prose,'duplicate_content')):
        for key, count in counter.items():
            if count > 1:
                issue('error', code, str(key), f'{count} duplicates')
    for name in sorted(set(project.config['champions']) | set(champions)):
        rows = champions.get(name, [])
        if name in sources.get('editorial_catalog',{}) and project.config.get('editorial_profile'):
            expected=set(sources['editorial_catalog'][name]['card_ids'])
            if not {r['id'] for r in rows}<=expected: issue('error','unreviewed_editorial_identity',name,'Card is not in the reviewed champion inventory')
            if len(rows)<len(expected): issue('warning','partial_champion_approval',name,f'{len(rows)} of {len(expected)} inventory cards approved; remaining drafts excluded')
            continue
        slots = Counter(r['slot'] for r in rows if r['level']=='L2' and ':recognize:' in r['id'])
        if sum(r['level']=='L1' for r in rows)!=1 or slots != Counter('PQWER'):
            issue('error', 'champion_coverage', name, 'Expected one L1 overview and one P/Q/W/E/R recognition card')
    paths = project.media_paths(used)
    if len(paths) != len(used):
        issue('error', 'ambiguous_media', 'media', 'Referenced media basenames are missing or duplicated')
    report = {'schema_version': 1, 'cards': len(content['cards']), 'champions': sorted(champions),
              'media_files': len(used), 'errors': sum(f['severity']=='error' for f in findings),
              'warnings': sum(f['severity']=='warning' for f in findings), 'findings': findings}
    return report


def save_report(report, folder):
    from .io import atomic
    folder.mkdir(parents=True, exist_ok=True)
    write_json(folder/'validation.json', report)
    lines = [f"# Pilot validation: {report['cards']} cards, {report['media_files']} media", '',
             f"Errors: {report['errors']}. Warnings: {report['warnings']}.", '']
    for f in report['findings']:
        lines.append(f"- **{f['severity']} / {f['code']}** `{f['id']}`: {f['message']}")
    atomic(folder/'validation.md', ('\n'.join(lines)+'\n').encode())

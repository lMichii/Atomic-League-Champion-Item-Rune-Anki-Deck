"""Review/export checks for additions; the frozen v4 model and baseline stay intact."""
from .io import canonical,digest,inside,read_json
from .generation.contracts import check_citations,numeric_tokens
from .generation.presentation import check_learning_row
from .editorial_media import variant_identity
import re


def text_fingerprint(card):
    row=card['row']
    keys=('id','level','champion','slot','ability','front_hint','question','answer','counterplay',
          'build_focus','priority','visual_cue_description','patch')
    return digest(canonical({k:row[k] for k in keys}))


def validate_reviewed(card,root):
    review=card['editorial_review']; content=review['content']; media=review['media']; row=card['row']
    check_learning_row(row)
    if card['content_status']!='curated' or card['qa_status']!='approved': raise ValueError('Reviewed additions must be explicitly curated/approved')
    if (row['level']=='L1')!=bool(row['build_focus']): raise ValueError('Overview build focus required; L2 build focus must be empty')
    if content.get('status')!='approved' or media.get('status')!='approved': raise ValueError('Independent content and media approvals required')
    if not all(content.get(k) is True for k in ('claims_checked','cores_checked','inferences_acknowledged','warnings_acknowledged')): raise ValueError('Missing editorial attestations')
    if not all(r.get('reviewer', '').strip() for r in (content, media)):
        raise ValueError('Named reviewer required')
    if content['text_sha256']!=text_fingerprint(card): raise ValueError('Content changed after editorial approval')
    path=inside(root,review['source_packet_path'])
    if digest(path.read_bytes())!=review['source_packet_sha256']: raise ValueError('Reviewed source packet changed')
    packet=read_json(path)
    if card['entity_id']!=f'champ:{packet["champion"]["riot_id"]}' or row['champion']!=packet['champion']['name']: raise ValueError('Editorial source/identity mismatch')
    check_citations(content['citations'],packet)
    if not numeric_tokens(row['answer'])<=numeric_tokens(' '.join(c['quote'] for c in content['citations'])): raise ValueError('Uncited quantity in edited answer')
    if row['review_status'] or row['cooldown']: raise ValueError('Internal review text/exact cooldowns cannot enter new learning fields')
    patch=card.get('versioning',{}).get('verified_game_patch') or ''
    if row['patch']!=patch or (patch and not card['versioning'].get('game_patch_evidence')): raise ValueError('Gameplay patch is not independently established')
    if patch and patch!=packet['versions'].get('verified_game_patch'): raise ValueError('Patch label is not established by the reviewed source packet')
    if not row['media_path'] or not row['icon_path']: raise ValueError('Real reviewed front media/icon required')
    lineage=review['media_lineage']
    for column,sha in lineage['files'].items():
        if digest(inside(root/'data/editorial',row[column]).read_bytes())!=sha: raise ValueError('Media changed after approval')
    for asset in lineage['provenance']:
        original=asset if asset.get('original_path') else asset.get('upstream_asset',{})
        if original.get('original_path') and digest(inside(root,original['original_path']).read_bytes())!=original['source_sha256']:
            raise ValueError('Original media provenance object changed')
    payload={'card_id':card['id'],'variant':variant_identity(card),'media_type':row['media_type'],
             'files':lineage['files'],'provenance':lineage['provenance']}
    signature=digest(canonical(payload))
    if signature!=media['media_sha256'] or signature!=review['media_sha256']: raise ValueError('Media review fingerprint mismatch')
    if not media.get('matching_checked') or not media.get('rights_acknowledged'): raise ValueError('Media matching/rights review incomplete')
    if lineage['fallback'] and not media.get('accept_static_fallback'): raise ValueError('Unreviewed static fallback')


def note_fields(card,fields):
    """Keep card-specific editorial adjustments out of the shared v4 template."""
    if not (card.get('editorial_review') or card.get('staging_status')): return fields
    fields=dict(fields); fields['Review']=''
    # Older staging notes hid both footer selectors inside MediaHTML. The unified
    # footer now belongs to the shared template, so drop only those legacy snippets.
    fields['MediaHTML']=re.sub(r'<style>\.source(?:,\.bottom)?\{display:none\}</style>','',fields['MediaHTML'])
    if card.get('editorial_presentation',{}).get('large_front'):
        fields['MediaHTML']=fields['MediaHTML'].replace('class="icon"','class="ability-gif"')
    return fields

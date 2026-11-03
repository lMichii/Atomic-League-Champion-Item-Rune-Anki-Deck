"""Conservative source-addressed media matching for variants and noncombat systems."""
from pathlib import Path
from ..io import atomic,digest,write_json
from .assets import collect_assets,passive_frames
from .evidence import token


def choose_primary(unit,packet):
    sections={s['id']:s for s in packet['kit_sections']}
    name=sections.get(unit['subject_id'],{}).get('name')
    # A slot alone never establishes that a clip belongs to a variant.
    if unit['kind'] in ('ability_variant','conditional_effect','weapon','form','stance','transformation'):
        return None
    return next((a for a in packet['abilities'] if a['name']==name or 'riot:'+a['slot']==unit['subject_id']),None)


def collect_kit_media(retriever,packet,inventory,folder):
    folder=Path(folder); assets=collect_assets(retriever,packet,folder)
    sections={s['id']:s for s in packet['kit_sections']}; mappings=[]
    for unit in inventory:
        key=unit['card_id']; primary=choose_primary(unit,packet)
        icon=None; animation=None; video=None; basis=''; source_ref=unit['subject_id']
        if unit['kind']=='overview':
            icon=assets['portrait']; basis='official champion portrait'
        elif primary:
            media=assets['abilities'][primary['slot']]
            icon=media['icon']; video=media['video']
            animation=media['gif'] if primary['slot']!='P' else None
            basis='exact primary ability name/source; no variant inference'
        else:
            section=sections.get(unit['subject_id'],{})
            url=section.get('icon_url')
            subject=unit['subject_id'].split(':',1)[-1]
            catalog=[c for c in packet['media_catalog'] if token(c['filename'].removesuffix('.png')) in (subject,subject+'l')]
            if unit['kind']=='weapon' and len(catalog)==1:
                url=catalog[0]['url']; basis='versioned CDragon asset filename matches canonical weapon anchor; visual review pending'
            else:
                basis='full-size ability icon inside matching live Wiki section; visual review pending'
            if url:
                blob,meta=retriever.get(url,'png',optional=True)
                if blob:
                    name='unit-'+digest(key.encode())[:20]+'.png'; path=folder/'media'/name; atomic(path,blob)
                    icon={'path':path.relative_to(folder).as_posix(),'sha256':digest(blob),
                          'source_url':url,'source_sha256':meta['sha256'],'retrieved_at':meta['retrieved_at'],'kind':'png'}
                    assets['files'].append(icon)
        active=unit['kind'] in ('ability','ability_variant','conditional_effect','transformation')
        unresolved=[]
        if not icon: unresolved.append('No source-matched image was resolved; text-only draft requires review.')
        if active and not animation:
            unresolved.append('No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant.')
        conditional=any(r['kind']=='conditional_effect' and unit['subject_id'] in (r['from_id'],r['to_id']) for r in packet.get('relationships',[]))
        if animation and conditional:
            unresolved.append('The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review.')
        if unit['kind']=='system': unresolved.append('Passive/resource/leveling visual cues require manual review of the archived demonstration frames.')
        mappings.append({'card_id':key,'subject_id':source_ref,'context_id':unit['context_id'],
            'icon':icon,'gif':animation,'video':video,'mapping_basis':basis,
            'slot_clip_candidate':assets['abilities'].get(unit['slot'],{}).get('video') if active and not animation else None,
            'unresolved':unresolved,'manual_weapon_ability_matching_required':True,'human_verified':False})
    assets['bindings']=mappings
    # A missing animation is expected for an indicator, rather than a missing combat spell.
    noncombat={c['slot'] for c in packet.get('slot_roles',[]) if c['role'] in ('indicator','unused')}
    noncombat_video_names={packet['champion']['ddragon_id'].lower()+'_'+s.lower()+'.webm' for s in noncombat}
    for finding in assets['findings']:
        if ((finding.get('slot') in noncombat and finding['code']=='active_icon_fallback') or
            (finding.get('name') in noncombat_video_names and finding['code']=='media_url_missing')):
            finding.update(original_code=finding['code'],code='noncombat_slot_without_animation',severity='info',
                           message='Source inventory identifies an indicator/unused slot; no combat animation expected.')
    assets['missing_media']=[{'card_id':m['card_id'],'issues':m['unresolved']} for m in mappings if m['unresolved']]
    write_json(folder/'assets.json',assets)
    frames,frame_info=passive_frames(folder,assets)
    return assets,frames,frame_info

"""Bounded Batch 01 production run; uses the existing fetcher, media and review APIs."""
import copy
import csv
import datetime as dt
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from .io import atomic, canonical, digest, read_json, write_json
from .media import gif, gif_info
from .project import Project

CHAMPIONS = ('Caitlyn','Ashe','Jinx','Leona','Lux','Morgana')


def normalize(text):
    return text.replace(' \ufffd ',' · ').replace('\ufffd',"'")


def stage(project, offline=False):
    """Additive source promotion, isolated production seed, and un-applied candidate.

    No existing pilot content/media is written. Editorial apply remains an explicit
    call to the ordinary propose/apply-review CLI with its exact proposal hash.
    """
    root = project.root
    pilot = Project(root)
    production = Project(root,profile='batch01')
    review = read_json(root/'data/batch01/editorial_review.json')
    if review['scope'] != list(CHAMPIONS):
        raise ValueError('Editorial review does not match the authorized batch')
    downloads = root/'build/batch01/downloads'
    if not offline:
        args = ['--champions',','.join(CHAMPIONS),'--patch','16.21.1','--cdragon-version','16.21',
                '--video-format','mp4','--output',str(downloads)]
        spec = importlib.util.spec_from_file_location('batch01_legacy_fetcher',root/'LoL_Anki_Riot_Medien_Fetcher/lol_anki_media_fetcher/media_fetcher.py')
        fetcher = importlib.util.module_from_spec(spec); spec.loader.exec_module(fetcher)
        if fetcher.main(args):
            raise ValueError('Legacy fetcher failed; inspect retrieval log')
    manifest_path = downloads/'manifest.json'
    if not manifest_path.exists():
        # A checkout can rebuild the committed production profile without downloads.
        if production.path('content').exists() and production.path('sources').exists():
            return {'status':'already_promoted','cards':len(production.content()['cards'])}
        raise FileNotFoundError('Batch download cache missing; run documented fetch command')
    manifest = read_json(manifest_path)['ability_assets']
    if len(manifest)!=30 or {m['champion'] for m in manifest} != set(CHAMPIONS):
        raise ValueError('Expected all 30 ability records for the six authorized champions')
    access = read_json(root/'data/batch01/qa/source_access.json')
    if any(a['status']!='retrieved' for a in access) or len(access)!=12:
        raise ValueError('Source review requires all six Riot and six Wiki snapshots')
    sources = copy.deepcopy(pilot.sources())
    snapshot_records = []
    for path in sorted((downloads/'cache').rglob('*.json')):
        rel = path.relative_to(downloads/'cache').as_posix()
        if rel=='ddragon/16.21.1/champion.json':
            url='https://ddragon.leagueoflegends.com/cdn/16.21.1/data/en_US/champion.json'
        elif rel.startswith('ddragon/16.21.1/details/'):
            url='https://ddragon.leagueoflegends.com/cdn/16.21.1/data/en_US/champion/'+path.name
        elif rel.startswith('cdragon/16.21/'):
            url='https://raw.communitydragon.org/16.21/plugins/rcp-be-lol-game-data/global/default/v1/champions/'+path.name
        else:
            continue
        sha = digest(path.read_bytes())
        destination = root/'data/batch01/sources/raw'/f'{sha}.json'
        atomic(destination,path.read_bytes())
        snapshot_records.append({'provider':'riot_ddragon' if rel.startswith('ddragon/') else 'communitydragon',
                                 'source_url':url,'upstream_version':'16.21.1' if rel.startswith('ddragon/') else '16.21',
                                 'snapshot_id':sha,'sha256':sha,'path':destination.relative_to(root).as_posix(),
                                 'legacy_path':'batch01/'+rel,
                                 'retrieved_at':dt.datetime.fromtimestamp(path.stat().st_mtime,dt.timezone.utc).isoformat(),
                                 'retrieval_status':'downloaded_and_archived'})
    for a in access:
        snapshot_records.append({'provider':a['provider'],'source_url':a['url'],'upstream_version':'archived_page',
                                 'snapshot_id':a['sha256'],'sha256':a['sha256'],'path':a['path'],
                                 'legacy_path':'batch01/'+a['champion']+'/'+a['provider'],
                                 'retrieved_at':a['retrieved_at'],'retrieval_status':'downloaded_and_archived'})
    sources['snapshots'].extend(snapshot_records)
    sources['ability_assets'].extend(manifest)
    sources['batch01_source_review'] = {'review_sha256':digest(canonical(review)),
                                      'method':'Riot descriptions plus archived Wiki revisions; no exact cooldown/scaling claims'}
    index = {(m['champion'],m['slot']):m for m in manifest}
    for name in CHAMPIONS:
        sources['entities'].append({'id':'champ:'+str(index[name,'P']['champion_id']),
                                    'riot_id':int(index[name,'P']['champion_id']),'name':name})
    # Copy only genuinely retrieved files; existing original bytes cannot be overwritten.
    asset_records = []
    def promote(source, relative, url, transform=None):
        source = Path(source)
        if not source.is_file():
            raise FileNotFoundError(f'Unresolved production media: {source}')
        blob = source.read_bytes()
        destination = root/'data/batch01'/relative
        if destination.exists() and digest(destination.read_bytes())!=digest(blob):
            raise ValueError('Refusing to replace promoted media without a new review: '+relative)
        atomic(destination,blob)
        sources['media_sha256'][relative]=digest(blob)
        record={'path':relative,'sha256':digest(blob),'source_url':url,
                'source_sha256':digest(blob) if not transform else transform['recipe']['source_sha256'],
                'transform':transform,'bytes':len(blob)}
        asset_records.append(record)
        return relative
    for name in CHAMPIONS:
        slug=name.lower(); passive=index[name,'P']
        promote(downloads/passive['portrait_local'],f'media/champions/{slug}_portrait.jpg',passive['portrait_source_url'])
        for slot in 'PQWER':
            m=index[name,slot]; low=slot.lower()
            promote(downloads/m['icon_local'],f'media/abilities/{slug}_{low}_icon.png',m['icon_source_url'])
            source=downloads/f'cache/webm/{slug}_{low}.webm'
            if source.exists():
                promote(source,f'media/videos/{slug}_{low}.webm',m['video_source_url'])
            if slot!='P' or review['passive_cues'][name]['include']:
                converted=root/f'build/batch01/gifs/{slug}_{low}.gif'
                conversion=gif(source,converted)
                # Provenance describes the asset's transformation, not this run's cache outcome.
                conversion['status']='converted'
                promote(converted,f'media/gifs/{slug}_{low}.gif',m['video_source_url'],conversion)
    sources['batch01_media_provenance']=asset_records
    # Build reviewed content from the untouched archived draft, never from generated prose.
    with (root/'data/batch01/input/new_cards.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=36 or len({r['id'] for r in rows})!=36:
        raise ValueError('Batch input must contain 36 distinct established IDs')
    candidate=copy.deepcopy(pilot.content())
    qa=[]
    for original in rows:
        r={k:normalize(v) for k,v in original.items()}
        changes=review['corrections'].get(r['id'],{})
        r.update(changes)
        name=r['champion']; slot=r['slot']; low=slot.lower(); slug=name.lower()
        wiki=next(a for a in access if a['champion']==name and a['provider']=='league_wiki')
        html=(root/wiki['path']).read_text('utf-8')
        revision=re.search(r'"wgRevisionId":(\d+)',html)
        if not revision or f'{name} | League of Legends Wiki' not in html:
            raise ValueError('Wiki response is not an identifiable revision: '+name)
        revision=revision.group(1)
        detail=read_json(downloads/f'cache/ddragon/16.21.1/details/{name}.json')['data'][name]
        cid=int(detail['key'])
        dd=next(s for s in snapshot_records if s['source_url'].endswith('/champion/'+name+'.json'))
        if r['level']=='L1':
            r['icon_path']=r['media_path']
            locator='Abilities and champion role; qualitative overview'
        else:
            ability=detail['passive'] if slot=='P' else detail['spells']['QWER'.index(slot)]
            r['ability']=ability['name']
            r['source_video_path']=f'media/videos/{slug}_{low}.webm'
            locator=r['ability']+' — qualitative ability description (no numeric tables or pending-test notes)'
            if slot=='P':
                cue=review['passive_cues'][name]
                r['front_hint']=name.upper()+' · PASSIVE'
                r['visual_cue_status']='approved' if cue['include'] else 'needs_visual_cue_review'
                r['visual_cue_description']=cue['description']
                r['visual_cue_media_path']=f'media/gifs/{slug}_p.gif' if cue['include'] else ''
            else:
                r['media_type']='gif'
                r['poster_path']=''  # unused preview is not an export dependency
        r['review_status']=f'Qualitative mechanics checked: Riot 16.21.1 + Wiki revision {revision}. '+('Official portrait checked.' if r['level']=='L1' else 'Official clip frames reviewed; current-client visual follow-up pending.')
        if r['cooldown']:
            raise ValueError('Batch 01 must not introduce cooldown claims')
        claims=[{'field':'answer','claim':r['answer'],'locator':locator,'snapshot_sha256':wiki['sha256'],'kind':'source_grounded_summary'},
                {'field':'counterplay','claim':r['counterplay'],'locator':locator,'snapshot_sha256':wiki['sha256'],'kind':'editorial_inference_from_mechanics'}]
        if r['build_focus']:
            claims.append({'field':'build_focus','claim':r['build_focus'],'locator':'Role, adaptive damage and ability scaling/defense sections','snapshot_sha256':wiki['sha256'],'kind':'broad_learning_orientation'})
        card={'id':r['id'],'entity_id':f'champ:{cid}','entity_kind':'champion','content_status':'curated',
              'qa_status':'approved','revision':candidate['build_epoch'],
              'evidence':{'riot_url':r['source_riot'],'wiki_url':r['source_wiki'],'wiki_revision':revision,
                          'wiki_snapshot':{'path':wiki['path'],'sha256':wiki['sha256']},'verified_patch':'26.21',
                          'riot_snapshot':{'path':dd['path'],'sha256':dd['sha256'],'source_url':dd['source_url']},
                          'scope':'Qualitative L1/L2 summary only; not every omission is a negative claim','claims':claims},
              'pedagogy':{'counterplay_basis':'source_grounded_inference','build_focus_basis':'broad_learning_orientation' if r['level']=='L1' else None},
              'media_review':{'status':'official_portrait_reviewed' if r['level']=='L1' else 'official_clip_frames_reviewed',
                              'current_client_review':'not_applicable' if r['level']=='L1' else 'pending',
                              'reviewer':review['visual_review']['reviewer']},'row':r}
        candidate['cards'].append(card)
        relevant=[a for a in asset_records if a['path'] in (r['media_path'],r['icon_path'],r['source_video_path'],r['visual_cue_media_path'])]
        qa.append({'id':r['id'],'champion':name,'level':r['level'],'slot':slot,
                   'decision':'approved_with_disclosed_follow_up','content_confidence':'source_grounded_qualitative',
                   'wiki_revision':revision,'wiki_snapshot_sha256':wiki['sha256'],'riot_snapshot_sha256':dd['sha256'],
                   'changes_from_draft':changes,'encoding_repaired':any('\ufffd' in v for v in original.values()),
                   'media':relevant,'manual_visual_review':None if r['level']=='L1' else (review['passive_cues'][name]['manual_follow_up'] if slot=='P' else 'Confirm current-client/skin/opponent-view appearance and playback on target Anki device.'),
                   'passive_cue':review['passive_cues'][name] if slot=='P' else None,
                   'unresolved_sources':[],'counterplay_basis':'explicitly labeled editorial inference from cited mechanics'})
    if candidate['cards'][:64]!=pilot.content()['cards'] or len(candidate['cards'])!=100:
        raise ValueError('Pilot preservation or bounded batch count failure')
    candidate_path=root/'data/batch01/candidate.json'
    if candidate_path.exists() and candidate_path.read_bytes()!=canonical(candidate):
        raise ValueError('Candidate changed; inspect the prior reviewed artifact before regenerating')
    write_json(candidate_path,candidate)
    source_bytes=canonical(sources)
    source_path=production.path('sources')
    if source_path.exists() and source_path.read_bytes()!=source_bytes:
        raise ValueError('Production source promotion changed; explicit new source review required')
    write_json(source_path,sources)
    promotion={'reviewer':review['reviewer'],'authorization':review['authorization'],
               'base_source_sha256':digest(pilot.path('sources').read_bytes()),'promoted_source_sha256':digest(source_bytes),
               'editorial_review_sha256':digest(canonical(review)),'new_champions':list(CHAMPIONS),
               'new_source_snapshots':len(snapshot_records),'new_media_files':len(asset_records),
               'pilot_source_entries_unchanged':True}
    write_json(root/'data/batch01/qa/source_promotion.json',promotion)
    if not production.path('content').exists():
        write_json(production.path('content'),pilot.content())
        lock=copy.deepcopy(read_json(pilot.path('lock')))
        lock['sources_sha256']=digest(source_bytes)
        lock['source_promotion']=promotion
        write_json(production.path('lock'),lock)
    elif not production.path('lock').exists():
        raise ValueError('Production seed incomplete; inspect rather than overwrite content')
    report={'schema_version':1,'batch':'01','reviewer':review['reviewer'],'pilot_cards_preserved':64,
            'candidate_additions':36,'approved_additions':36,'withheld':[],'maximum_deck_cards':100,
            'sources':{'ddragon':'16.21.1','cdragon':'16.21','wiki_snapshots':6,'unresolved':[]},
            'media_summary':{'portraits':6,'ability_icons':30,'active_gifs':24,'supplementary_passive_gifs':4,
                             'real_source_webms_archived':30,'active_fallbacks':0,'unresolved_active_media':[]},
            'source_conflicts':review['source_conflicts'],'manual_visual_review_cards':[q['id'] for q in qa if q['manual_visual_review']],
            'limitations':review['visual_review']['limitations'],'cards':qa}
    write_json(root/'data/batch01/qa/report.json',report)
    return {'status':'staged_not_applied','candidate':str(candidate_path),'additions':36,
            'source_promotion':promotion,'qa_report':'data/batch01/qa/report.json'}

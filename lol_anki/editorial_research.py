"""Media investigation reports. Evidence/reference discovery never approves an asset."""
import re
from .io import canonical,digest,read_json,write_json,atomic
from .editorial_media import immutable


def report_tasks(root):
    from pathlib import Path
    root=Path(root); folder=root/'data/editorial/research'; folder.mkdir(parents=True,exist_ok=True)
    archive=root/'data/drafts/aphelios'/read_json(root/'data/drafts/aphelios/index.json')['current_run']
    current=folder/'aphelios-media-tasks.json'; previous=read_json(current) if current.exists() else {}
    packet=read_json(archive/'source-packet.json'); inventory=read_json(archive/'card-inventory.json')
    wiki=next(r for r in packet['resources'] if 'wiki.leagueoflegends.com' in r['url'])
    raw=(archive/'sources'/wiki['sha256']).read_bytes()
    animations=sorted(set(re.findall(rb'(?:src|href)="([^\"]+\.(?:gif|webm|mp4)[^\"]*)"',raw)))
    primer=root/'build/phase3_3/riot-primer.html'; sources=[]
    if not primer.exists():
        saved=next((s.get('snapshot') for s in previous.get('investigated_sources',[]) if 'aphelios-kit-primer' in s['url']),None)
        if saved: primer=root/saved
    if primer.exists():
        blob=primer.read_bytes(); path=folder/'raw'/digest(blob); immutable(path,blob)
        sources.append({'url':'https://www.leagueoflegends.com/en-us/news/game-updates/aphelios-kit-primer/',
            'sha256':digest(blob),'snapshot':path.relative_to(root).as_posix(),
            'result':'Official current page exposes weapon diagrams; no directly embedded MP4/WebM animation URLs found.',
            'publication':'2019-11-25','gameplay_patch':'unverified'})
    cd=next(r for r in packet['resources'] if 'raw.communitydragon.org' in r['url'] and r['url'].endswith('/523.json'))
    sources.append({'url':cd['url'],'sha256':cd['sha256'],'result':'Versioned metadata exposes one generic Q demonstration, not source-addressed clips for the five weapon variants.'})
    sources.append({'url':packet['attribution']['wiki']+'?oldid='+packet['versions']['wiki_revision'],
        'sha256':wiki['sha256'],'result':f'{len(animations)} GIF/MP4/WebM links in the archived Wiki page; audio sources are not animations.'})
    sources.append({'url':'https://www.youtube.com/watch?v=lDoeuuBRUFg','publisher':'League of Legends',
        'publication':'2019-12-11','result':'Official Champion Spotlight is a longer reference candidate, not a per-weapon clip or a distribution license.',
        'downloaded':False,'matching':'Manual timestamps and variant/frame verification required','distribution_status':'pending'})
    tasks=[]
    for unit in inventory:
        if unit['kind']=='ability_variant':
            tasks.append({'id':'animation:'+unit['card_id'],'card_id':unit['card_id'],'subject_id':unit['subject_id'],
                'context_id':unit['context_id'],'title':unit['title'],'kind':'required_variant_animation','status':'open',
                'current_fallback':'Real icon matched to the specific Wiki ability container',
                'acceptance':'Supply a short exact-variant clip or local gameplay recording, identify weapon and action, retain source/version/license details, decode and visually review.',
                'forbidden':'Do not assign the generic Q demo to a single weapon variant.'})
    ultimate=next(c for c in inventory if c['slot']=='R')
    for weapon in (c for c in inventory if c['kind']=='weapon'):
        tasks.append({'id':'supplement:'+ultimate['card_id']+':'+weapon['subject_id'],'card_id':ultimate['card_id'],
            'context_id':weapon['subject_id'],'title':weapon['title'].split(':')[0]+' · Moonlight Vigil',
            'kind':'supplementary_ultimate_visual','status':'open',
            'acceptance':'Show this weapon-dependent ultimate effect; the generic base-cast demonstration does not establish all five effects.'})
    old_tasks={t['id']:t for t in previous.get('tasks',[])}
    for task in tasks:
        if task['id'] in old_tasks:
            for field in ('status','notes','recording_reference'):
                if field in old_tasks[task['id']]: task[field]=old_tasks[task['id']][field]
    report={'schema_version':1,'champion':'Aphelios','source_packet_sha256':digest((archive/'source-packet.json').read_bytes()),
        'investigated_sources':sources,'tasks':tasks,'overrides_approved':0,'model_calls':0,
        'licensing':{'reference':'https://www.riotgames.com/en/legal','status':'pending_distribution_review',
                     'note':'Source attribution does not establish redistribution permission, including third-party recordings.'}}
    if previous and previous!=report: write_json(folder/'history'/(digest(canonical(previous))+'.json'),previous)
    write_json(current,report)
    lines=['# Aphelios manual media tasks','', 'No new animation was confidently matched and approved. Five Q icon fallbacks remain.','',
           '| Task | Status |','| --- | --- |']+['| '+t['title']+' | '+t['status']+' |' for t in tasks]
    lines+=['','## Investigated sources','']+['- '+s['url']+' — '+s['result'] for s in sources]
    lines+=['','Retain provenance, capture/asset version and source/license notes. Every imported replacement starts pending. Model calls: 0.']
    atomic(folder/'aphelios-media-tasks.md',('\n'.join(lines)+'\n').encode())
    return report

"""Retain a completed unapproved run for review/history; never promote content."""
from pathlib import Path
from ..io import atomic,canonical,digest,inside,read_json,write_json


def archive_run(root,run):
    root=Path(root).resolve(); run=Path(run).resolve()
    if not run.is_relative_to(root/'build/generated') or not (run/'qa.json').is_file():
        raise ValueError('Archive only a completed generated run beneath build/generated')
    qa=read_json(run/'qa.json')
    if qa.get('human_approved') or qa.get('publishable'):
        raise ValueError('This archive function only handles unapproved drafts')
    packet=read_json(run/'source-packet.json')
    slug=packet['champion']['ddragon_id'].lower()
    destination=inside(root,'data/drafts/'+slug+'/'+run.name)
    files={}
    for p in sorted(run.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(run).as_posix()
        if p.suffix=='.apkg': raise ValueError('An unapproved draft archive must not contain an APKG')
        blob=p.read_bytes()
        # Persist events/results but exclude model reasoning text from the review archive.
        if p.name=='events.jsonl':
            import json
            safe=[]
            for line in blob.decode('utf-8').splitlines():
                event=json.loads(line)
                if event.get('item',{}).get('type') in ('reasoning','plan'):
                    event={**event,'item':{k:v for k,v in event['item'].items() if k in ('type','id')}}
                safe.append(json.dumps(event,ensure_ascii=False))
            blob=('\n'.join(safe)+'\n').encode()
        existing=destination/rel
        if existing.exists() and existing.read_bytes()!=blob:
            raise ValueError('Archived run is immutable: '+rel)
        atomic(existing,blob); files[rel]=digest(blob)
    write_json(destination/'archive.json',{'schema_version':1,'status':'unapproved_draft_history',
                'run_id':qa['generation']['run_id'],'files':files,'file_manifest_sha256':digest(canonical(files))})
    write_json(destination.parent/'index.json',{'schema_version':1,'status':'unapproved_drafts_only',
               'current_run':destination.name,'run_id':qa['generation']['run_id']})
    return {'status':'unapproved_run_archived','path':str(destination),'files':len(files)}


def restore_inputs(root,archive):
    """Restore verified public snapshots/model results for offline deterministic replay."""
    root=Path(root).resolve(); archive=Path(archive).resolve()
    manifest=read_json(archive/'archive.json')
    if manifest.get('status')!='unapproved_draft_history': raise ValueError('Not a draft archive')
    if digest(canonical(manifest['files']))!=manifest['file_manifest_sha256']: raise ValueError('Archive manifest mismatch')
    for rel,sha in manifest['files'].items():
        path=inside(archive,rel)
        if not path.is_file() or digest(path.read_bytes())!=sha: raise ValueError('Archive file modified: '+rel)
    packet=read_json(archive/'source-packet.json')
    http=root/'.cache/generator/http'
    for meta in packet['resources']:
        blob=(archive/'sources'/meta['sha256']).read_bytes()
        atomic(http/'blobs'/meta['sha256'],blob)
        write_json(http/'urls'/(digest(meta['url'].encode())+'.json'),meta)
    assets=read_json(archive/'assets.json')
    for record in assets['files']:
        if record['kind']=='gif': continue
        blob=inside(archive,record['path']).read_bytes()
        if digest(blob)!=record['source_sha256']: raise ValueError('Asset source hash mismatch')
        meta={'url':record['source_url'],'sha256':record['source_sha256'],'kind':record['kind'],
              'bytes':len(blob),'retrieved_at':record['retrieved_at']}
        atomic(http/'blobs'/meta['sha256'],blob)
        write_json(http/'urls'/(digest(meta['url'].encode())+'.json'),meta)
    for step in (archive/'ai').iterdir():
        if not step.is_dir(): continue
        receipt=read_json(step/'receipt.json')
        target=root/'.cache/generator/ai'/receipt['request_sha256']
        for source in step.rglob('*'):
            if source.is_file(): atomic(target/source.relative_to(step),source.read_bytes())
    return packet['champion']['ddragon_id']

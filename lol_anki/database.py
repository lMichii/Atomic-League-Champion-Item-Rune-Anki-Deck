"""Small searchable card/source index; raw source packets remain in place."""
import html
import json
import re
from pathlib import Path
from .io import atomic
from .package import read_collection, inspect_apkg
from .v4 import FIELD_NAMES, CURRENT_PATCH
from .lanes import read_assignments, SOURCE_MANIFEST

DEFAULT_APKG='build/staging/League_Anki_Gesamtstand_Reparaturen_2026-11-03.apkg'
INDEX='data/database/cards.jsonl'

def _source_packets(root):
    found={}
    for path in list((root/'data/batches').glob('*/staging/*/source-packet.json'))+list((root/'data/drafts').glob('**/source-packet.json')):
        try:
            packet=json.loads(path.read_text('utf-8'))
            name=packet.get('champion',{}).get('name','')
            slug=packet.get('champion',{}).get('ddragon_id','').lower()
            if name:
                item={'path':path.relative_to(root).as_posix(),'slug':slug,'name':name}
                for key in {name.casefold(),slug}-{''}:
                    values=found.setdefault(key,[])
                    if not any(existing['path']==item['path'] for existing in values): values.append(item)
        except (OSError,ValueError):
            continue
    return found

def _source_catalogs(root, champion):
    result=[]
    for name in ('pilot.json','production.json','editorial.json'):
        path=root/'data/sources'/name
        if not path.is_file(): continue
        try:
            data=json.loads(path.read_text('utf-8'))
            if any(a.get('champion','').casefold()==champion.casefold() for a in data.get('ability_assets',[])):
                result.append(path.relative_to(root).as_posix())
        except (OSError,ValueError): pass
    return result

def build_index(root, apkg=DEFAULT_APKG, output=INDEX):
    root=Path(root).resolve(); package=root/apkg; report=inspect_apkg(package)
    con=read_collection(package)
    packets=_source_packets(root)
    lane_assignments=read_assignments(root) if (root/SOURCE_MANIFEST).is_file() else {}
    result=[]
    try:
        rows=con.execute('select n.id,c.id,n.guid,n.mid,n.tags,n.flds from notes n join cards c on c.nid=n.id order by n.id').fetchall()
        for nid,cid,guid,mid,tags,flds in rows:
            values=flds.split('\x1f')
            if len(values)!=len(FIELD_NAMES): raise ValueError(f'Invalid fields for note {nid}')
            f=dict(zip(FIELD_NAMES,values)); key=f['Key']; champion=f['Champion']
            media=sorted(set(html.unescape(x) for x in re.findall(r'src="([^"]+)"',f['MediaHTML']+' '+f['IconHTML'])))
            champion_packets=packets.get(champion.casefold(),[])
            entry={'key':key,'note_id':nid,'card_id':cid,'guid':guid,'note_type_id':mid,
                'champion':champion,'ability':f['Ability'],'slot':f['Slot'],'level':f['Level'],
                'question':html.unescape(re.sub('<[^>]+>','',f['Question'])),
                'answer':html.unescape(re.sub('<[^>]+>','',f['Answer'])),
                'counterplay':html.unescape(re.sub('<[^>]+>','',f['Counterplay'])),
                'media':media,'sources':{'league':f['Riot'],'wiki':f['Wiki']},'patch':CURRENT_PATCH,
                'tags':tags.strip().split(),'source_packets':champion_packets,
                'source_catalogs':_source_catalogs(root,champion)}
            if key.startswith('champ:') and f['Level']=='L1':
                entry['lanes']=lane_assignments.get(key.split(':')[1],[])
                entry['lane_source']='senseos-champion-positions-26.21'
            result.append(entry)
    finally: con.close()
    if len(result)!=report['notes']: raise ValueError('Inventory count differs from APKG')
    target=root/output; target.parent.mkdir(parents=True,exist_ok=True)
    atomic(target,b''.join((json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8') for row in result))
    return {'path':target.relative_to(root).as_posix(),'cards':len(result),'champions':len({r['champion'] for r in result if r['level']!='L0'}),
            'source_packets':len({p['path'] for r in result for p in r['source_packets']}),'apkg_sha256':report['sha256']}

def lookup(root, champion, ability=None, include_raw=False):
    root=Path(root).resolve(); path=root/INDEX; query=champion.casefold(); ability_query=ability.casefold() if ability else None
    hits=[]
    lines=path.read_text('utf-8').splitlines()
    for extra in sorted((root/'data/database').glob('items-*.jsonl')):
        lines.extend(extra.read_text('utf-8').splitlines())
    for line in lines:
        row=json.loads(line)
        if query not in (row['champion'].casefold(),row['key'].split(':')[1].casefold()): continue
        if ability_query and ability_query not in (row['ability'].casefold(),row['slot'].casefold()): continue
        sources=[]
        seen=set()
        slot=row['slot']
        for pointer in row['source_packets']:
            rel=pointer['path']
            if rel in seen: continue
            seen.add(rel); packet_path=root/rel
            item={'path':rel}
            if include_raw:
                data=json.loads(packet_path.read_text('utf-8'))
            else: data=json.loads(packet_path.read_text('utf-8'))
            wanted={f'riot:{slot}',f'wiki:{slot}'} if slot else set()
            if row['key'] in data.get('card_evidence',{}): wanted=set(data['card_evidence'][row['key']])
            item['resources']=[]
            for resource in data.get('resources',[]):
                if row['key'] in data.get('card_evidence',{}) and resource.get('id') not in wanted|{'icon:'+row['key'].split(':')[1]}:
                    continue
                raw_path=root/resource['path'] if resource.get('path') else packet_path.parent/'sources'/resource.get('sha256','')
                if not raw_path.is_file(): continue
                entry={'kind':resource.get('kind'),'url':resource.get('url'),'sha256':resource.get('sha256'),
                       'raw_path':raw_path.relative_to(root).as_posix()}
                if include_raw and resource.get('kind') in ('html','json'): entry['content']=raw_path.read_text('utf-8',errors='replace')
                item['resources'].append(entry)
            item['excerpts']=[{'id':x.get('id'),'url':x.get('url'),'text':x.get('text','') if include_raw else x.get('text','')[:1600]}
                for x in data.get('excerpts',[]) if (not ability_query and row['key'] not in data.get('card_evidence',{})) or x.get('id') in wanted]
            item['abilities']=[a for a in data.get('abilities',[]) if not ability_query or a.get('slot','').casefold()==slot.casefold()]
            related=[]
            for filename in ('kit-analysis.json','card-inventory.json','mechanics-inventory.json','author-output.json','qa.json','media-report.json','assets.json'):
                related_path=packet_path.parent/filename
                if not related_path.is_file(): continue
                related_item={'path':related_path.relative_to(root).as_posix()}
                if include_raw:
                    try: related_item['data']=json.loads(related_path.read_text('utf-8'))
                    except (OSError,ValueError): related_item['text']=related_path.read_text('utf-8',errors='replace')
                related.append(related_item)
            item['related_analyses']=related
            sources.append(item)
        for rel in row.get('source_catalogs',[]):
            data=json.loads((root/rel).read_text('utf-8'))
            assets=[a for a in data.get('ability_assets',[]) if a.get('champion','').casefold()==query and
                    (not ability_query or ability_query in (a.get('slot','').casefold(),a.get('ability_name','').casefold()))]
            ids={a.get('champion_id') for a in data.get('ability_assets',[]) if a.get('champion','').casefold()==query}
            snapshots=[s for s in data.get('snapshots',[]) if any(re.search(r'(?<!\d)'+re.escape(str(i))+r'(?!\d)',s.get('legacy_path','')+' '+s.get('source_url','')) for i in ids if i)]
            if include_raw:
                for snapshot in snapshots:
                    source_path=snapshot.get('path')
                    if source_path and (root/source_path).is_file():
                        snapshot['stored_content']=(root/source_path).read_text('utf-8',errors='replace')
            sources.append({'path':rel,'ability_assets':assets,'snapshots':snapshots,
                'raw_snapshot_paths':[s.get('path') for s in snapshots if s.get('path')]})
        row['stored_sources']=sources; hits.append(row)
    return {'champion':champion,'ability':ability,'cards':hits,'count':len(hits)}

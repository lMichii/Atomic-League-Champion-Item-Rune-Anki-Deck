"""Bounded item/visual-glossary prototype adapter around the existing cache and APKG writer."""
import json
import re
from pathlib import Path
from .cache import Cache
from .database import build_index
from .editorial_media import inspect_media
from .generation.evidence import readable
from .generation.preview import create_previews
from .identity import DECKS, new_key, stable_id
from .io import atomic, digest, inside, read_json, write_json
from .item_visuals import visual_glossary, VISUALS
from .operations import project_operation
from .package import assemble
from .project import Project

CONTENT='data/content/items-prototype.json'
SOURCES='data/sources/items-prototype.json'
INDEX='data/database/items-prototype.jsonl'
OUTPUT='build/items-prototype/League_Anki_Items_Prototype_26.21.apkg'
ITEMS={'3157','3140','3916','3077','3153'}
TERMS={'term:grievous_wounds:L0','term:on_hit:L0','term:stasis:L0'}


class ItemContext:
    def __init__(self,root):
        self.root=Path(root); self.legacy=Project(root).legacy
        self.folder=self.root/'build/items-prototype'
    def media_root_for(self,row): return self.folder
    def media_paths(self,used):
        return [self.folder/'media'/name for name in sorted(used)]


def validate_items(root,content,packet):
    """Structural/source checks, never an AI verifier or editorial approval."""
    cards=content['cards']; keys=[c['id'] for c in cards]
    expected={new_key('item',i,'overview','L1') for i in ITEMS}
    expected.add(new_key('item','3140','cleanse_limits','L2')); expected|=TERMS
    if set(keys)!=expected or len(keys)!=len(expected): raise ValueError('Prototype scope or duplicate IDs changed')
    if content['patch']!='26.21' or packet['patch']!='26.21': raise ValueError('Prototype patch mismatch')
    existing=[json.loads(line) for line in (root/'data/database/cards.jsonl').read_text('utf-8').splitlines()]
    if set(keys)&{r['key'] for r in existing}: raise ValueError('Prototype would duplicate an existing card')
    old_terms={re.sub(r'[^a-z]','',r['ability'].casefold()) for r in existing if r['level']=='L0'}
    for c in cards:
        r=c['row']
        if c['entity_kind']=='term' and re.sub(r'[^a-z]','',r['ability'].casefold()) in old_terms:
            raise ValueError('Fundamental is already in the glossary')
        if r['id']!=c['id'] or r['patch']!=content['patch'] or not r['question'] or not r['answer']:
            raise ValueError('Missing learning text or identity/patch mismatch')
        if r.get('sections'):
            from .learning_style import render_sections
            render_sections(r['sections'])
            if r['answer']!='\\n\\n'.join(s['label']+': '+s['text'] for s in r['sections']):
                raise ValueError('Section text differs from learning answer')
        if c['entity_kind']=='item' and r['level']=='L1' and (r['front_hint'] or r['question']!='What does this item do?' or not r.get('use')):
            raise ValueError('L1 item front must hide name; practical Use required')
    resources={r['id']:r for r in packet['resources']}
    texts={}
    for resource in resources.values():
        blob=inside(root,resource['path']).read_bytes()
        if digest(blob)!=resource['sha256']: raise ValueError('Stored source/media hash changed: '+resource['id'])
        Cache.validate(blob,resource['kind'])
        texts[resource['id']]=readable(blob) if resource['kind']=='html' else blob.decode('utf-8',errors='replace')
    for excerpt in packet['excerpts']:
        if any(line not in texts[excerpt['id']] for line in excerpt['text'].splitlines()):
            raise ValueError('Evidence excerpt does not match its archived source')
    riot=json.loads(texts['riot-items'])['data']
    for c in cards:
        if not set(c['source_ids'])<=set(resources): raise ValueError('Unknown card source')
        if packet['card_evidence'].get(c['id'])!=c['source_ids']: raise ValueError('Card evidence mapping changed')
        if c['entity_kind']=='item':
            item_id=c['entity_id'].split(':')[1]; item=riot[item_id]
            if not item['maps'].get('11') or not item['gold'].get('purchasable'): raise ValueError('Item is not a purchasable SR item')
            if item['name'].casefold()!=c['row']['champion'].casefold(): raise ValueError('Item ID/name mismatch')
        evidence='\n'.join(texts[i] for i in c['source_ids'])
        for number in re.findall(r'\d+(?:\.\d+)?',c['row']['answer']):
            if not re.search(r'(?<!\d)'+re.escape(number)+r'(?!\d)',evidence): raise ValueError('Number missing from stored evidence')
    return {'errors':0,'cards':len(cards),'items':len(ITEMS),'l1':5,'l2':1,'l0':3,
            'checks':['unique stable keys','existing glossary','Summoner\'s Rift availability','source hashes',
                      'exact evidence excerpts','numeric evidence presence','PNG integrity/full decoding','APKG media references'],
            'scope':'Deterministic checks and source-grounded authoring; no separate AI verification or editorial approval.'}


def build_prototype(root,offline=False):
    root=Path(root).resolve()
    with project_operation(root):
        content=read_json(root/CONTENT); packet=read_json(root/SOURCES)
        folder=root/'data/items-prototype'; folder.mkdir(exist_ok=True)
        resources={r['id']:r for r in packet['resources']}
        riot=json.loads(inside(root,resources['riot-items']['path']).read_text('utf-8'))['data']
        cache=Cache(root/'.cache/generator/http',offline=offline,retries=1)
        media=[]
        for item_id in sorted(ITEMS):
            image=riot[item_id]['image']['full']
            if image!=item_id+'.png': raise ValueError('Unexpected Riot icon mapping')
            url=f'https://ddragon.leagueoflegends.com/cdn/{packet["asset_version"]}/img/item/{image}'
            path=folder/'media'/f'item-{item_id}.png'; prior=resources.get('icon:'+item_id)
            if prior and path.is_file():
                if prior['url']!=url or digest(path.read_bytes())!=prior['sha256']: raise ValueError('Saved prototype icon changed')
            else:
                if path.exists(): raise ValueError('Do not overwrite manually supplied media without provenance')
                blob,meta=cache.get(url,'png'); atomic(path,blob)
                resources['icon:'+item_id]={'id':'icon:'+item_id,**meta,'path':path.relative_to(root).as_posix(),
                    'rights':'Riot Games item icon; educational prototype; distribution rights not granted by this record.'}
                packet['resources']=list(resources.values()); write_json(root/SOURCES,packet)
            media.append({'item_id':item_id,'path':path.relative_to(root).as_posix(),'sha256':digest(path.read_bytes()),**inspect_media(path)})
        report=validate_items(root,content,packet)
        output_folder=root/'build/items-prototype'
        for item_id in sorted(ITEMS):
            path=folder/'media'/f'item-{item_id}.png'
            atomic(output_folder/'media'/path.name,path.read_bytes())
        projected,visual_report=visual_glossary(root,content,output_folder)
        report.update(visual_report)
        report.update(cards=len(projected['cards']),l0=8)
        report.update(media=media,missing_media=[],unresolved_mechanics=[],source_notes=packet.get('findings',[]),
                      author_provider_calls=0,verifier_calls=0,approval_changes=0)
        # Reuse the standalone browser preview generator and unchanged cached media.
        create_previews(projected['cards'],output_folder)
        write_json(output_folder/'cards.json',projected)
        write_json(output_folder/'qa.json',report)
        atomic(output_folder/'QA.md',('# Item prototype QA\n\n14 cards: five L1, one L2 and eight L0 fundamentals (five existing identities reused).\n'
            'Source hashes, excerpts, SR availability, icon decoding and export structure checked.\n'
            'Use sections are practical recommendations. No separate AI verifier or approval.\n'
            'Six cached GIFs reused byte-for-byte, fully decoded and sampled visually; no current-client VFX verification.\n'
            'Grievous Wounds and On-Hit remain text-only. Suppression/Nearsight have no existing glossary cards; none added.\n'
            'The Stasis alias redirects; its card cites the explicit Hourglass definition.\n').encode())
        decks={level:stable_id('item-prototype:'+level,2042610313000) for level in DECKS}
        package=assemble(ItemContext(root),root/OUTPUT,projected,decks,'LoL · Item Prototype',
                         {'L1':'L1 · Item Overview','L2':'L2 · Item Mechanics'})
        build_index(root,OUTPUT,INDEX)
        rows=[json.loads(line) for line in (root/INDEX).read_text('utf-8').splitlines()]
        # Existing glossary identities already live in the frozen main sidecar.
        rows=[row for row in rows if row['key'] in packet['card_evidence']]
        for row in rows:
            row['source_packets']=[{'path':SOURCES,'name':row['champion']}] if row['key'] in packet['card_evidence'] else []
            if row['level']=='L0': row['visual_manifest']=VISUALS
        atomic(root/INDEX,b''.join((json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode() for row in rows))
        report.update(package=package,output=OUTPUT,ids=[c['id'] for c in projected['cards']])
        write_json(root/'build/items-prototype/report.json',report)
        return report

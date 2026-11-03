"""Deterministic source resolution and evidence extraction; no authored card prose."""
import datetime as dt
from html.parser import HTMLParser
import html
import json
from pathlib import Path
import re
import urllib.parse
from ..cache import Cache
from ..io import atomic, canonical, digest, write_json

DD='https://ddragon.leagueoflegends.com'
CD='https://raw.communitydragon.org'
VIDEO='https://d28xe8vt774jo5.cloudfront.net/'


def token(text):
    return re.sub(r'[^a-z0-9]','',str(text).casefold())


class PageText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','li','tr','h1','h2','h3','h4'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.skip: self.skip-=1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def readable(blob):
    parser=PageText(); parser.feed(blob.decode('utf-8'))
    return '\n'.join(' '.join(line.split()) for line in ''.join(parser.parts).splitlines() if line.strip())


def wiki_sections(blob, names):
    """Keep the first live ability sections; exclude historical and transcluded kits."""
    text=readable(blob)
    start=text.find('Abilities[edit')
    if start<0: start=text.find('Abilities')
    if start<0: raise ValueError('Wiki ability section not found; do not infer missing mechanics')
    text=text[start:]
    positions=[]
    lines=text.splitlines()
    cursor=0
    for name in names:
        found=next((i for i in range(cursor,len(lines)) if lines[i].strip()==name),None)
        if found is None: raise ValueError('Wiki ability heading missing: '+name)
        positions.append(found); cursor=found+1
    result=[]
    for i,begin in enumerate(positions):
        end=positions[i+1] if i+1<len(positions) else min(len(lines),begin+180)
        section=lines[begin:end]
        for stop in ('Champion skins','Champion Skins','Patch history','Patch History','References','Trivia','Relations'):
            if stop in section: section=section[:section.index(stop)]
        # Retain qualitative descriptions, not unrelated numeric history tables.
        descriptions=[line for line in section if re.match(r'^(Innate|Passive|Active|Recast|Toggle|[A-Z][A-Za-z ]{1,28}):',line)]
        notes=[]
        for j,line in enumerate(section):
            if line in ('Notes/General Details','Notes','Tips & Tricks'):
                notes=section[j+1:j+36]; break
        result.append({'name':names[i],'descriptions':descriptions[:12],
                       'notes':notes,'excerpt':'\n'.join(section[:145])[:15000]})
    return result


def resolve(index, identifier):
    wanted=token(identifier)
    if not wanted or len(identifier)>80 or identifier.casefold()=='all' or ',' in identifier or '/' in identifier or '\\' in identifier:
        raise ValueError('Supply exactly one champion name, Data Dragon ID or Riot numeric key')
    matches=[c for c in index['data'].values() if wanted in {token(c['id']),token(c['name']),str(c['key'])}]
    if len(matches)!=1: raise ValueError('Champion identifier is not unique in the current Riot index: '+identifier)
    return matches[0]


class Retriever:
    def __init__(self, root, config, offline=False):
        self.root=Path(root)
        cfg=config['retrieval']
        self.cache=Cache(self.root/'.cache/generator/http',offline=offline,
                         retries=cfg['attempts'],timeout=cfg['timeout_seconds'],max_bytes=cfg['max_bytes'])
        self.offline=offline; self.resources=[]; self.findings=[]
        self.release=cfg.get('ddragon_version')

    def get(self,url,kind='json',refresh=False,optional=False):
        try:
            blob,meta=self.cache.get(url,kind,refresh=refresh)
            self.resources.append(meta)
            return blob,meta
        except (OSError,ValueError) as ex:
            if not optional: raise
            self.findings.append({'code':'source_unavailable','url':url,'message':str(ex)})
            return None,None

    def collect(self, identifier):
        if self.release:
            version=self.release
        else:
            versions,_=self.get(DD+'/api/versions.json',refresh=not self.offline)
            version=json.loads(versions)[0]
        if not re.fullmatch(r'\d+\.\d+\.\d+',version): raise ValueError('Unexpected Riot release identifier')
        raw,_=self.get(f'{DD}/cdn/{version}/data/en_US/champion.json')
        champion=resolve(json.loads(raw),identifier)
        key=champion['id']; cid=int(champion['key'])
        data_url=f'{DD}/cdn/{version}/data/en_US/champion/{key}.json'
        raw,dd_meta=self.get(data_url)
        detail=json.loads(raw)['data'][key]
        release='.'.join(version.split('.')[:2])
        cd_url=f'{CD}/{release}/plugins/rcp-be-lol-game-data/global/default/v1/champions/{cid}.json'
        cd_blob,cd_meta=self.get(cd_url,optional=True)
        cd=json.loads(cd_blob) if cd_blob else {'passive':{},'spells':[]}
        skill={'P':cd.get('passive',{})}
        skill.update({s.get('spellKey','').upper():s for s in cd.get('spells',[])})
        vanity=token(detail['name'])
        # Discover Riot's canonical vanity slug from versioned CDN champion ID where possible.
        overrides={'MonkeyKing':'wukong','Renata':'renata-glasc','KSante':'k-sante','Nunu':'nunu'}
        slug=overrides.get(key,re.sub(r'[^a-z0-9]+','-',detail['name'].casefold()).strip('-'))
        riot_url=f'https://www.leagueoflegends.com/en-us/champions/{slug}/'
        riot_blob,riot_meta=self.get(riot_url,'html',refresh=not self.offline,optional=True)
        wiki_url='https://wiki.leagueoflegends.com/en-us/'+urllib.parse.quote(detail['name'].replace(' ','_'))
        wiki_blob,wiki_meta=self.get(wiki_url,'html',refresh=not self.offline,optional=True)
        wiki_revision=None; sections=[]
        names=[a['name'] for a in [detail['passive'],*detail['spells']]]
        if wiki_blob:
            revision=re.search(rb'"wgRevisionId":(\d+)',wiki_blob)
            if not revision or detail['name'].casefold() not in readable(wiki_blob)[:1500].casefold():
                self.findings.append({'code':'wiki_unidentified','url':wiki_url,'message':'Page/revision identity not established'})
            else:
                wiki_revision=revision.group(1).decode()
                try: sections=wiki_sections(wiki_blob,names)
                except ValueError as ex: self.findings.append({'code':'wiki_extraction','url':wiki_url,'message':str(ex)})
        excerpts=[]
        abilities=[]
        for i,(slot,ability) in enumerate(zip('PQWER',[detail['passive'],*detail['spells']])):
            riot_text=readable(ability.get('description','').encode())
            excerpts.append({'id':'riot:'+slot,'provider':'riot_ddragon','url':data_url,'sha256':dd_meta['sha256'],
                             'locator':f'/data/{key}/'+('passive/description' if slot=='P' else f'spells/{i-1}/description'),
                             'text':riot_text})
            if len(sections)==5:
                excerpts.append({'id':'wiki:'+slot,'provider':'league_wiki','url':wiki_url+'?oldid='+wiki_revision,
                                 'sha256':wiki_meta['sha256'],'locator':ability['name'],'text':sections[i]['excerpt']})
            filename=ability.get('image',{}).get('full')
            icon_url=f'{DD}/cdn/{version}/img/'+('passive/' if slot=='P' else 'spell/')+urllib.parse.quote(filename or '')
            video_rel=skill.get(slot,{}).get('abilityVideoPath','').lstrip('/')
            valid=bool(re.fullmatch(r'champion-abilities/[A-Za-z0-9_/-]+\.webm',video_rel)) and '..' not in video_rel
            abilities.append({'slot':slot,'name':ability['name'],'description':riot_text,
                              'icon_url':icon_url if filename else None,'video_url':VIDEO+video_rel if valid else None,
                              'cooldown_source_only':ability.get('cooldown'),'primary_source_ids':['riot:'+slot]+(['wiki:'+slot] if len(sections)==5 else [])})
        role_text=f"Name: {detail['name']}. Official role tags: {', '.join(detail.get('tags',[]))}."
        excerpts.append({'id':'riot:role','provider':'riot_ddragon','url':data_url,'sha256':dd_meta['sha256'],
                         'locator':f'/data/{key}/tags','text':role_text})
        if len(sections)!=5: self.findings.append({'code':'wiki_evidence_incomplete','message':'Not all five Wiki ability sections were retrieved; unsupported details must remain uncertain'})
        packet={'schema_version':1,'champion':{'name':detail['name'],'ddragon_id':key,'riot_id':cid,'roles':detail.get('tags',[])},
                'versions':{'ddragon':version,'communitydragon_requested':release,'communitydragon_available':bool(cd_blob),
                            'game_patch':None,'wiki_revision':wiki_revision},
                'attribution':{'riot':riot_url,'wiki':wiki_url},'abilities':abilities,'excerpts':excerpts,
                'portrait_url':f'{DD}/cdn/img/champion/splash/{key}_0.jpg',
                'findings':self.findings,'resources':self.resources.copy(),
                'limitations':['Data Dragon release is pinned; game patch label is not inferred from its numbering.',
                               'Riot CDN clips are demonstrations, not current-client or skin-specific verification.']}
        from .kit_sources import extend_packet
        packet=extend_packet(self,packet,detail,wiki_blob,wiki_meta,cd)
        # Save immutable raw bytes and metadata independently of AI output.
        fingerprint=digest(canonical(packet))
        folder=self.root/'build/generated/inputs'/fingerprint
        for resource in self.resources:
            blob=(self.cache.root/'blobs'/resource['sha256']).read_bytes()
            atomic(folder/'raw'/resource['sha256'],blob)
        write_json(folder/'packet.json',packet)
        return packet,folder

"""Discover live kit sections and their media without a champion-specific table."""
import html
import re
import urllib.parse
from .evidence import readable,token,CD


def live_sections(blob):
    raw=blob.decode('utf-8')
    start=re.search(r'<h2\b[^>]*id="Abilities"[^>]*>',raw)
    if not start: return []
    end=re.search(r'<h2\b',raw[start.end():])
    raw=raw[start.end():start.end()+end.start()] if end else raw[start.end():]
    headings=list(re.finditer(r'<div\b[^>]*class="ability-info-stats(?:_|&#95;){2}ability"[^>]*>(.*?)</div>',raw,re.S))
    result=[]; identities=set(); templates={}
    for i,heading in enumerate(headings):
        section=raw[heading.start():headings[i+1].start() if i+1<len(headings) else len(raw)]
        anchors=re.findall(r'<span id="([^"]+)"></span>',raw[max(0,heading.start()-1000):heading.start()])
        name=html.unescape(re.sub('<[^>]+>','',heading[1])).strip()
        anchor=html.unescape(anchors[-1]) if anchors else name.replace(' ','_')
        links=re.findall(r'href="([^"]*Template:Data_[^"]+)"',raw[max(0,heading.start()-1000):heading.start()])
        template=urllib.parse.unquote(html.unescape(links[-1])).split('?',1)[0] if links else None
        identity='wiki:'+token(anchor)
        locator=anchor
        if identity in identities:
            # Some forms repeat a heading/anchor but transclude distinct Wiki
            # templates. Use that explicit upstream identity, never an ordinal
            # or a guessed form name. Truly ambiguous duplicates still fail.
            if template:
                candidate='wiki:'+token(template.rsplit('/',1)[-1])
                if candidate not in identities:
                    identity=candidate; locator=template
        identities.add(identity)
        # Only full-size icons within this live section, not keyword/linked-ability thumbnails.
        icons=[]
        for tag in re.findall(r'<img\b[^>]*>',section):
            src=re.search(r'\bsrc="([^"]+)"',tag)
            if src and re.search(r'(?<![\w-])width="64"',tag) and '/thumb/' not in src[1]:
                icons.append(urllib.parse.urljoin('https://wiki.leagueoflegends.com',html.unescape(src[1])))
        text=readable(section.encode())
        # Retain qualitative descriptions and relevant notes; avoid numeric tables and other modes.
        lines=text.splitlines(); keep=[]
        for line in lines:
            if line in ('Map-Specific Differences','One for All differences edit','Arena differences edit'): break
            keep.append(line)
        full_text='\n'.join(keep)
        item={'id':identity,'anchor':locator,'name':name,
              'text':full_text[:8500],'icon_url':icons[0] if icons else None}
        # A shared ability can be transcluded unchanged under several forms.
        # Collapse only an identical explicit template, full text and icon.
        if template and any(item==old and full_text==text for old,text in templates.get(template,[])): continue
        result.append(item)
        if template: templates.setdefault(template,[]).append((item,full_text))
    return result


def extend_packet(retriever,packet,detail,wiki_blob,wiki_meta,cd):
    sections=live_sections(wiki_blob) if wiki_blob and packet['versions']['wiki_revision'] else []
    primary_names=[a['name'] for a in packet['abilities']]
    structural_text=' '.join(a['description'] for a in packet['abilities'])
    variant_signal=bool(re.search(r'\b(?:main.hand|off.hand|no (?:third|fourth) ability|different activated abilities|transforms?|stance)\b',structural_text,re.I))
    unusual=(len(detail.get('spells',[]))!=4 or variant_signal or len(sections)>5 or
             bool(sections and [s['name'] for s in sections]!=primary_names))
    if not unusual: return packet
    packet['schema_version']=2
    if len({s['id'] for s in sections})!=len(sections):
        raise ValueError('Live kit sections have ambiguous source identities; editorial source mapping required')
    packet['kit_sections']=[]
    for section in sections:
        source={k:section[k] for k in ('id','name','anchor','icon_url')}
        packet['kit_sections'].append(source)
        packet['excerpts'].append({'id':section['id'],'provider':'league_wiki',
            'url':packet['attribution']['wiki']+'?oldid='+packet['versions']['wiki_revision'],
            'sha256':wiki_meta['sha256'],'locator':section['anchor'],'text':section['text']})
    if not sections:
        retriever.findings.append({'code':'kit_sections_missing','message':'Nonstandard source requires editorial kit mapping; do not fabricate slot coverage'})
    # Discover available official asset names from the versioned CDragon directory.
    catalog=[]; directories=set()
    for ability in [cd.get('passive',{}),*cd.get('spells',[])]:
        icon=ability.get('abilityIconPath','')
        if icon.startswith('/lol-game-data/assets/ASSETS/'):
            path='/assets/'+icon.split('/ASSETS/',1)[1].lower()
            directories.add(f"{CD}/{packet['versions']['communitydragon_requested']}/plugins/rcp-be-lol-game-data/global/default"+path.rsplit('/',1)[0]+'/')
    for url in sorted(directories):
        blob,_=retriever.get(url,'html',optional=True)
        if not blob: continue
        for filename in sorted(set(re.findall(r'href="([^"/]+\.png)"',blob.decode('utf-8')))):
            catalog.append({'id':'cd:'+token(filename),'filename':filename,'url':urllib.parse.urljoin(url,filename)})
    packet['media_catalog']=catalog
    packet['findings']=[f for f in retriever.findings if f['code'] not in ('wiki_extraction','wiki_evidence_incomplete')]
    packet['findings'].append({'code':'adaptive_kit_structure','message':f'{len(sections)} live sections discovered; conventional slot headings are not a completeness contract.'})
    packet['resources']=retriever.resources.copy()
    return packet

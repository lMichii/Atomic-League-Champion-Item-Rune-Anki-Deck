#!/usr/bin/env python3
"""v4 visual/wording renderer, mechanically ported from the legacy builder.
See tools/port_v4_renderer.py. Keep the established layout, field order and card count.
"""
from __future__ import annotations
import csv, hashlib, html, json, re, shutil, sqlite3, tempfile, time, zipfile
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]/'LoL_Anki_Pilot_Project_v4_English'
CSV=ROOT/'cards.csv'
MEDIA=ROOT/'media'
TEMPLATE=ROOT/'anki_template.anki2'
OUTPUT=ROOT/'LoL_Anki_Pilot_6_Champions_v4_English.apkg'
MODEL_ID=2042610311001
CURRENT_PATCH='26.21'
# Independent of content build dates: Anki's default importer compares this
# timestamp before replacing an existing shared template. Bump for template edits.
TEMPLATE_REVISION=1793732400  # 2026-11-03 19:00 UTC; optional item subtitle.
DECKS={'root':2042610312000,'L0':2042610312003,'L1':2042610312001,'L2':2042610312002}
FIELD_NAMES=['Key','Level','Champion','Slot','Ability','FrontHint','Question','Answer','Counterplay','Cooldown','MediaHTML','IconHTML','Riot','Wiki','Patch','Priority','Review']

def stable_id(text,prefix):
    # deterministic IDs make generation reproducible; GUID below controls Anki updates
    return prefix + int.from_bytes(hashlib.sha256(text.encode('utf-8')).digest()[:7], 'big') % 300_000_000_000

def guid(text):
    return hashlib.sha1(('lol-anki-pilot-v1:'+text).encode('utf-8')).hexdigest()[:14]

def esc(x): return html.escape(str(x or ''),quote=True)

def champion_urls(champion):
    if str(champion).casefold() in ('basics','term','league of legends'):
        return 'https://www.leagueoflegends.com/en-us/champions/','https://wiki.leagueoflegends.com/en-us/Champion'
    slug=re.sub(r'[^a-z0-9]+','-',str(champion).lower()).strip('-')
    wiki=quote(str(champion).replace(' ','_'),safe='_')
    return f'https://www.leagueoflegends.com/en-us/champions/{slug}/',f'https://wiki.leagueoflegends.com/en-us/{wiki}'

# Order matters: match complete phrases before AP/AD/MR abbreviations.
STAT_TERMS = [
    (r'true[\s-]+damage', 'stat-true'),
    (r'magic[\s-]+damage', 'stat-magic'),
    (r'physical[\s-]+damage', 'stat-physical'),
    (r'magic[\s-]+resist(?:ance)?', 'stat-mr'),
    (r'ability[\s-]+power', 'stat-ap'),
    (r'attack[\s-]+damage', 'stat-ad'),
    (r'armor', 'stat-armor'),
    (r'health', 'stat-health'),
    (r'mana', 'stat-mana'),
    (r'AP|AD|MR|HP', None),
]
STAT_INLINE_STYLES = {
    'stat-ap':'color:#77c3ff;font-weight:600',
    'stat-magic':'color:#77c3ff;font-weight:600',
    'stat-ad':'color:#f3a46f;font-weight:600',
    'stat-physical':'color:#f3a46f;font-weight:600',
    'stat-true':'color:#ffffff;font-weight:700;text-decoration:underline',
    'stat-mr':'color:#c5a0fc;font-weight:600',
    'stat-armor':'color:#e3c776;font-weight:600',
    'stat-health':'color:#81d8a1;font-weight:600',
    'stat-mana':'color:#83d4d8;font-weight:600',
}
STAT_REGEX = re.compile(r'(?<![a-zA-Z])(?:' + '|'.join('(?:' + p + ')' for p,_ in STAT_TERMS) + r')(?![a-zA-Z])', re.I)

def format_stats(value):
    """Escape CSV text then semantically highlight complete stats, not HTML tags."""
    value = str(value or '')
    def mark(match):
        raw = match.group(0)
        cls = None
        for pattern, candidate in STAT_TERMS:
            if re.fullmatch(pattern,raw,re.I):
                cls = candidate
                break
        if cls is None:
            cls = {'ap':'stat-ap','ad':'stat-ad','mr':'stat-mr','hp':'stat-health'}.get(raw.lower())
        return '<span class="' + cls + '" style="' + STAT_INLINE_STYLES[cls] + '">' + html.escape(raw) + '</span>' if cls else html.escape(raw)
    chunks=[]; last=0
    for m in STAT_REGEX.finditer(value):
        chunks.append(html.escape(value[last:m.start()]))
        chunks.append(mark(m))
        last=m.end()
    chunks.append(html.escape(value[last:]))
    return ''.join(chunks).replace('\\n','<br>')

def media_file(p, root=ROOT):
    path=root/str(p)
    if not path.is_file():raise FileNotFoundError(f'Medium fehlt: {path}')
    if (root/'media').resolve() not in path.resolve().parents: raise ValueError(f'Medienpfad außerhalb media/: {p}')
    return path.name

CSS=r'''
.card{background:#101317;color:#e8e8e8;font-family:Arial,"Segoe UI",sans-serif;text-align:left;font-size:17px;line-height:1.5;margin:0;padding:0}
.lol{max-width:710px;margin:0 auto;padding:22px 16px 32px;box-sizing:border-box}
.top{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:15px;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#a7a8a8}
.level{color:#c9ad74;font-weight:bold}
.hint{color:#898f96;font-size:11px;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px}
.visual{margin:10px 0 18px;text-align:center}
.visual img{display:block;margin:auto;max-width:100%;height:auto}
.visual .portrait{width:100%;max-height:345px;object-fit:cover;object-position:center 27%}
.visual .ability-gif{width:100%;max-width:590px;object-fit:contain}
.visual .icon{width:116px;height:116px;object-fit:contain}
.question{font-size:clamp(20px,4.2vw,25px);line-height:1.35;font-weight:650;margin:10px 0 12px}
.bottom{font-size:11px;color:#788089;margin-top:21px}
.bottom a{color:inherit;text-decoration:none;border-bottom:1px solid #43484e}
.bottom a:hover{color:#bfb5a5}
#answer{height:1px;background:#363c43;border:0;margin:10px 0 0}
.back .name{display:flex;align-items:center;gap:13px;margin-bottom:13px}
.back .name img{width:42px;height:42px;object-fit:contain}
.back h2{font-size:22px;margin:0;line-height:1.25;font-weight:650;color:#f1f0ed}
.back .sub{font-size:12px;color:#939ca4;margin-top:4px}
.back .answer{font-size:17px;line-height:1.6;margin:12px 0 17px;white-space:normal}
.box{border-left:2px solid #8b8f91;margin:15px 0;padding:2px 0 2px 13px;color:#c9cbd0;font-size:15px}
.box.cd{border-left-color:#b59c66}
.build-focus{font-size:15px;margin:15px 0 0;color:#d7c08e}
.cue-description{font-size:15px;color:#c9cbd0;margin:13px 0}
.passive-cue{margin-top:18px}
.cue-label{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#939ca4;margin-bottom:6px}
.source{font-size:11px;color:#858c93;margin-top:25px;line-height:1.8}
.source a{color:#bfb5a5}
@media(max-width:540px){.lol{padding:16px 9px 26px}.question{font-size:21px}.back .answer{font-size:16px}}
/* Semantic League stats. Changes here affect every card at once. */
.stat-ap,.stat-magic{color:#77c3ff;font-weight:600}
.stat-ad,.stat-physical{color:#f3a46f;font-weight:600}
.stat-true{color:#ffffff;font-weight:700;text-decoration:underline;text-decoration-color:#929aa1;text-underline-offset:3px}
.stat-mr{color:#c5a0fc;font-weight:600}
.stat-armor{color:#e3c776;font-weight:600}
.stat-health{color:#81d8a1;font-weight:600}
.stat-mana{color:#83d4d8;font-weight:600}

'''
QFMT=r'''<div class="lol lvl{{Level}}"><div class="top"><span>LEAGUE OF LEGENDS</span><span class="level">{{Level}}</span></div><div class="hint">{{FrontHint}}</div>{{#MediaHTML}}<div class="visual">{{MediaHTML}}</div>{{/MediaHTML}}<div class="question">{{Question}}</div></div>'''
AFMT=r'''{{FrontSide}}<hr id="answer"><div class="lol back lvl{{Level}}"><div class="name">{{IconHTML}}<div><h2>{{Champion}} {{Slot}}{{#Ability}} · {{Ability}}{{/Ability}}</h2><div class="sub">{{Level}}</div></div></div><div class="answer">{{Answer}}</div>{{#Counterplay}}<div class="box"><b>Counterplay:</b> {{Counterplay}}</div>{{/Counterplay}}{{#Cooldown}}<div class="box cd"><b>Cooldown:</b> {{Cooldown}}</div>{{/Cooldown}}<div class="bottom">{{#Patch}}Patch {{Patch}}{{/Patch}}{{^Patch}}Patch 26.21{{/Patch}} · <a href="{{Riot}}">League</a> · <a href="{{Wiki}}">Wiki</a></div></div>'''

QFMT=QFMT.replace('\\"','"')
AFMT=AFMT.replace('\\"','"')

def make_model(now):
    return {'id':MODEL_ID,'name':'LoL Pilot · Media Cards V1','type':0,'mod':max(now,TEMPLATE_REVISION),'usn':-1,'sortf':0,'did':DECKS['L1'],
      'flds':[{'name':f,'ord':i,'sticky':False,'rtl':False,'font':'Arial','size':20,'description':''} for i,f in enumerate(FIELD_NAMES)],
      'tmpls':[{'name':'Medienkarte','ord':0,'qfmt':QFMT,'afmt':AFMT,'did':None,'bqfmt':'','bafmt':''}],
      'css':CSS,'latexPre':'\\documentclass{article}\\begin{document}','latexPost':'\\end{document}',
      'req':[[0,'all',[6]]],'vers':[]}

def make_deck(id,name,now):
    return {'id':id,'name':name,'conf':1,'mod':now,'usn':-1,'desc':'League learning cards with local Riot media; sourced from Riot and LoL Wiki, patch 26.21.',
      'dyn':0,'collapsed':False,'browserCollapsed':False,'newToday':[0,0],'revToday':[0,0],'lrnToday':[0,0],'timeToday':[0,0]}

def render_media(r, used, root=ROOT):
    typ=r['media_type']
    if typ=='none':
        return ''
    fname=media_file(r['media_path'], root);used.add(fname)
    if typ=='portrait':
        return f'<img class="portrait" src="{esc(fname)}">'
    if typ=='gif':
        # Native animated GIF works in Anki WebView without a video decoder.
        return f'<img class="ability-gif" src="{esc(fname)}">'
    if typ=='icon':
        return f'<img class="icon" src="{esc(fname)}">'
    if typ=='video':
        raise ValueError('MP4 is intentionally not embedded. Convert it to a GIF via prepare_gifs.py first.')
    raise ValueError('Unknown media_type: '+typ)


def render_fields(r, root, used):
    fmt = format_stats
    if r.get("learning_style"):
        from .learning_style import format_learning, render_sections
        fmt = format_learning
    media_file = lambda p: globals()["media_file"](p, root)
    used.add(media_file(r['icon_path'])) if r['icon_path'] else None
    icon=('<img src="'+esc(media_file(r['icon_path']))+'">' if r['icon_path'] else ('<img src="'+esc(media_file('media/champions/'+r['champion'].lower()+'_portrait.jpg'))+'">' if r['level'] != 'L0' else ''))
    if not r['icon_path'] and r['level']!='L0':used.add(media_file('media/champions/'+r['champion'].lower()+'_portrait.jpg'))
    front=render_media(r,used,root)
    # A passive can have both its icon AND a verified in-game visual cue.
    cue_path=(r.get('visual_cue_media_path') or '').strip()
    if r['slot']=='P' and cue_path:
        cue_name=media_file(cue_path); used.add(cue_name)
        front += '<div class="passive-cue"><div class="cue-label">In-game cue</div><img class="ability-gif" src="'+esc(cue_name)+'"></div>'
    flds={
      'Key':r['id'],'Level':r['level'],'Champion':r['champion'],'Slot':r['slot'] if r['slot']!='-' else '',
      'Ability':r['ability'] if r['ability'] else 'Overview',
      'FrontHint':esc(r['front_hint']),'Question':fmt(r['question']),'Answer':fmt(r['answer']) + (('<p class="build-focus"><b>Build focus:</b> '+fmt(r.get('build_focus',''))+'</p>') if r['level']=='L1' and r.get('build_focus') else '') + (('<p class="lanes" style="font-size:12px;color:#89939c;margin:5px 0 0"><b>Lanes:</b> '+ ' · '.join(esc(x) for x in r.get('lanes',[]) if x in ('Top','Jungle','Mid','Bot','Support'))+'</p>') if r['level']=='L1' and r.get('lanes') else '') + (('<p class="cue-description"><b>Visual cue:</b> '+fmt(r.get('visual_cue_description',''))+'</p>') if r['level']=='L2' and r['slot']=='P' and r.get('visual_cue_description') else ''),'Counterplay':fmt(r['counterplay']),
      'Cooldown':fmt(r['cooldown']),'MediaHTML':front,'IconHTML':icon,'Riot':r.get('source_riot') or champion_urls(r['champion'])[0],
      'Wiki':r.get('source_wiki') or champion_urls(r['champion'])[1],'Patch':CURRENT_PATCH,'Priority':r['priority'],'Review':r.get('review_status','')}
    if r.get('learning_style') and r.get('sections'):
        flds['Answer']=render_sections(r['sections'])
    if r.get('learning_style') and r.get('mechanic_example'):
        flds['MediaHTML']+='<div class="mechanic-example" style="font-size:13px;color:#a7a8a8;margin-top:8px">'+fmt(r['mechanic_example'])+'</div>'
        flds['Answer']+='<p style="font-size:12px;color:#939ca4">Example: <a style="color:inherit" href="'+esc(r['example_source_riot'])+'">League ability</a> · <a style="color:inherit" href="'+esc(r['example_source_wiki'])+'">Wiki ability</a></p>'
    is_item=r['id'].startswith('item:')
    if is_item:
        flds['Ability']=r['ability']  # An item overview needs no redundant subtitle.
        flds['MediaHTML']=flds['MediaHTML'].replace('class="icon"','class="icon" style="width:160px;height:160px"')
        if r.get('use'):
            flds['Answer']+='<div class="box"><b>Use:</b> '+fmt(r['use'])+'</div>'
    tags=f" lol {('item' if is_item else 'basics' if r['level']=='L0' else 'champion')} level::{r['level'][1:]} prio::{r['priority']} "
    tags+=(('item::'+r['id'].split(':')[1]) if is_item else r['champion'].lower())+' '
    if r['slot'] in ('P','Q','W','E','R'):tags+=f"slot::{r['slot'].lower()} "
    if r.get('visual_cue_status')=='needs_visual_cue_review': tags+=' cue_review_needed '
    if 'timer:' in r['id']:tags+=' timer hook '
    return flds, tags

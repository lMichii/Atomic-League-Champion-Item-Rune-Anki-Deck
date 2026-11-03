#!/usr/bin/env python3
"""LoL Anki Pilot Builder (stdlib only). Run: python build_deck.py
Edit cards.csv and keep stable IDs to update notes on re-import.
"""
from __future__ import annotations
import csv, hashlib, html, json, re, shutil, sqlite3, tempfile, time, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CSV=ROOT/'cards.csv'
MEDIA=ROOT/'media'
TEMPLATE=ROOT/'anki_template.anki2'
OUTPUT=ROOT/'LoL_Anki_Pilot_6_Champions_v4_English.apkg'
MODEL_ID=2042610311001
DECKS={'root':2042610312000,'L0':2042610312003,'L1':2042610312001,'L2':2042610312002}
FIELD_NAMES=['Key','Level','Champion','Slot','Ability','FrontHint','Question','Answer','Counterplay','Cooldown','MediaHTML','IconHTML','Riot','Wiki','Patch','Priority','Review']

def stable_id(text,prefix):
    # deterministic IDs make generation reproducible; GUID below controls Anki updates
    return prefix + int.from_bytes(hashlib.sha256(text.encode('utf-8')).digest()[:7], 'big') % 300_000_000_000

def guid(text):
    return hashlib.sha1(('lol-anki-pilot-v1:'+text).encode('utf-8')).hexdigest()[:14]

def esc(x): return html.escape(str(x or ''),quote=True)

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

def media_file(p):
    path=ROOT/str(p)
    if not path.is_file():raise FileNotFoundError(f'Medium fehlt: {path}')
    if MEDIA.resolve() not in path.resolve().parents: raise ValueError(f'Medienpfad außerhalb media/: {p}')
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
QFMT=r'''<div class="lol lvl{{Level}}"><div class="top"><span>LEAGUE OF LEGENDS</span><span class="level">{{Level}}</span></div><div class="hint">{{FrontHint}}</div>{{#MediaHTML}}<div class="visual">{{MediaHTML}}</div>{{/MediaHTML}}<div class="question">{{Question}}</div><div class="bottom">Patch {{Patch}}</div></div>'''
AFMT=r'''{{FrontSide}}<hr id="answer"><div class="lol back lvl{{Level}}"><div class="name">{{IconHTML}}<div><h2>{{Champion}} {{Slot}} · {{Ability}}</h2><div class="sub">{{Level}} · Priority {{Priority}}</div></div></div><div class="answer">{{Answer}}</div>{{#Counterplay}}<div class="box"><b>Counterplay:</b> {{Counterplay}}</div>{{/Counterplay}}{{#Cooldown}}<div class="box cd"><b>Cooldown:</b> {{Cooldown}}</div>{{/Cooldown}}<div class="source"><a href="{{Riot}}">Riot</a> · <a href="{{Wiki}}">Wiki</a> · Patch {{Patch}}<br><small>{{Review}}</small></div></div>'''

QFMT=QFMT.replace('\\"','"')
AFMT=AFMT.replace('\\"','"')

def make_model(now):
    return {'id':MODEL_ID,'name':'LoL Pilot · Media Cards V1','type':0,'mod':now,'usn':-1,'sortf':0,'did':DECKS['L1'],
      'flds':[{'name':f,'ord':i,'sticky':False,'rtl':False,'font':'Arial','size':20,'description':''} for i,f in enumerate(FIELD_NAMES)],
      'tmpls':[{'name':'Medienkarte','ord':0,'qfmt':QFMT,'afmt':AFMT,'did':None,'bqfmt':'','bafmt':''}],
      'css':CSS,'latexPre':'\\documentclass{article}\\begin{document}','latexPost':'\\end{document}',
      'req':[[0,'all',[6]]],'vers':[]}

def make_deck(id,name,now):
    return {'id':id,'name':name,'conf':1,'mod':now,'usn':-1,'desc':'League learning cards with local Riot media; sourced from Riot and LoL Wiki, patch 26.21.',
      'dyn':0,'collapsed':False,'browserCollapsed':False,'newToday':[0,0],'revToday':[0,0],'lrnToday':[0,0],'timeToday':[0,0]}

def render_media(r, used):
    typ=r['media_type']
    if typ=='none':
        return ''
    fname=media_file(r['media_path']);used.add(fname)
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

def build():
    rows=list(csv.DictReader(CSV.open('r',encoding='utf-8-sig',newline='')))
    assert len({r['id'] for r in rows})==len(rows), 'Doppelte Karten-ID gefunden'
    assert all(r['level'] in ('L0','L1','L2') for r in rows),'Dieses Pilotdeck unterstützt L0/L1/L2'
    now=int(time.time()); used=set(); names=set(); notes=[]
    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/'collection.anki2';shutil.copy2(TEMPLATE,db)
        con=sqlite3.connect(db)
        # Repair templates created by the first pilot builder. Anki expects
        # `lapses`, not `laps`. Keep this migration for older project copies.
        columns = {r[1] for r in con.execute('PRAGMA table_info(cards)')}
        if 'lapses' not in columns and 'laps' in columns:
            con.execute('ALTER TABLE cards RENAME COLUMN laps TO lapses')
            columns = {r[1] for r in con.execute('PRAGMA table_info(cards)')}
        if 'lapses' not in columns:
            raise RuntimeError('Ungueltiges Anki-Datenbankschema: lapses fehlt')
        col=con.execute('select * from col').fetchone()
        fields=[d[0] for d in con.execute('select * from col').description]
        models=json.loads(col[fields.index('models')]);models[str(MODEL_ID)]=make_model(now)
        decks=json.loads(col[fields.index('decks')]);deckroot='LoL · Pilot (6 Champions)'
        decks.update({str(DECKS['root']):make_deck(DECKS['root'],deckroot,now),
                      str(DECKS['L0']):make_deck(DECKS['L0'],deckroot+'::L0 · Basics',now),
                      str(DECKS['L1']):make_deck(DECKS['L1'],deckroot+'::L1 · Champion Overview',now),
                      str(DECKS['L2']):make_deck(DECKS['L2'],deckroot+'::L2 · Abilities & Timers',now)})
        conf=json.loads(col[fields.index('conf')])
        conf['curDeck']=DECKS['L1'];conf['activeDecks']=[DECKS['L1']];conf['curModel']=MODEL_ID
        con.execute('update col set mod=?,scm=?,models=?,decks=?,conf=?',(now,now,json.dumps(models,ensure_ascii=False),json.dumps(decks,ensure_ascii=False),json.dumps(conf,ensure_ascii=False)))
        for i,r in enumerate(rows):
            mid=stable_id(r['id'],1_800_000_000_000);cid=stable_id(r['id'],2_300_000_000_000)
            used.add(media_file(r['icon_path'])) if r['icon_path'] else None
            icon=('<img src="'+esc(media_file(r['icon_path']))+'">' if r['icon_path'] else ('<img src="'+esc(media_file('media/champions/'+r['champion'].lower()+'_portrait.jpg'))+'">' if r['level'] != 'L0' else ''))
            if not r['icon_path'] and r['level']!='L0':used.add(media_file('media/champions/'+r['champion'].lower()+'_portrait.jpg'))
            front=render_media(r,used)
            # A passive can have both its icon AND a verified in-game visual cue.
            cue_path=(r.get('visual_cue_media_path') or '').strip()
            if r['slot']=='P' and cue_path:
                cue_name=media_file(cue_path); used.add(cue_name)
                front += '<div class="passive-cue"><div class="cue-label">In-game cue</div><img class="ability-gif" src="'+esc(cue_name)+'"></div>'
            flds={
              'Key':r['id'],'Level':r['level'],'Champion':r['champion'],'Slot':r['slot'] if r['slot']!='-' else '',
              'Ability':r['ability'] if r['ability'] else 'Overview',
              'FrontHint':esc(r['front_hint']),'Question':format_stats(r['question']),'Answer':format_stats(r['answer']) + (('<p class="build-focus"><b>Build focus:</b> '+format_stats(r.get('build_focus',''))+'</p>') if r['level']=='L1' and r.get('build_focus') else '') + (('<p class="cue-description"><b>Visual cue:</b> '+format_stats(r.get('visual_cue_description',''))+'</p>') if r['level']=='L2' and r['slot']=='P' and r.get('visual_cue_description') else ''),'Counterplay':format_stats(r['counterplay']),
              'Cooldown':format_stats(r['cooldown']),'MediaHTML':front,'IconHTML':icon,'Riot':r['source_riot'],
              'Wiki':r['source_wiki'],'Patch':r['patch'],'Priority':r['priority'],'Review':r['review_status']}
            serial='\x1f'.join(flds[k] for k in FIELD_NAMES)
            tags=f" lol {('basics' if r['level']=='L0' else 'champion')} level::{r['level'][1:]} prio::{r['priority']} {r['champion'].lower()} "
            if r['slot'] in ('P','Q','W','E','R'):tags+=f"slot::{r['slot'].lower()} "
            if r.get('visual_cue_status')=='needs_visual_cue_review': tags+=' cue_review_needed '
            if 'timer:' in r['id']:tags+=' timer hook '
            # Anki csum uses SHA1 of sort field's initial 8 hex digits (unsigned)
            csum=int(hashlib.sha1(flds['Key'].encode('utf-8')).hexdigest()[:8],16)
            con.execute('insert into notes values (?,?,?,?,?,?,?,?,?,?,?)',(
                mid,guid(r['id']),MODEL_ID,now,-1,tags,serial,flds['Key'],csum,0,''))
            con.execute('insert into cards values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
                cid,mid,DECKS[r['level']],0,now,-1,0,0,i+1,0,2500,0,0,0,0,0,0,''))
        con.commit()
        integrity=con.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity!='ok': raise RuntimeError(integrity)
        importer_cards=con.execute('SELECT id, nid, did, ord, cast(mod AS integer), usn, type, queue, due, cast(ivl AS integer), factor, reps, lapses, left, odue, odid, flags, data FROM cards').fetchall()
        if len(importer_cards)!=len(rows):
            raise RuntimeError('Kartenanzahl stimmt im Anki-Schema nicht')
        con.close()
        # copy only referenced media with filenames indexed (Anki package convention)
        with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            z.write(db,'collection.anki2')
            media_map={}
            for i,fname in enumerate(sorted(used)):
                matches=list(MEDIA.rglob(fname))
                if len(matches)!=1:raise RuntimeError(f'Medien-Dateiname mehrdeutig: {fname}')
                z.write(matches[0],str(i));media_map[str(i)]=fname
            z.writestr('media',json.dumps(media_map,ensure_ascii=False))
    print(f'Erstellt: {OUTPUT.name}; {len(rows)} Karten (inkl. Begriffe); {len(used)} Mediendateien; {OUTPUT.stat().st_size/1024/1024:.2f} MB')

if __name__=='__main__':build()

"""Deterministic legacy APKG packaging, using the frozen v4 Anki contract."""
import hashlib
import html
import io
import json
import re
import sqlite3
import zipfile
from .identity import DECKS, MODEL_ID, guid, stable_id
from .io import atomic, digest, inside, read_json
from .validation import validate
from .v4 import FIELD_NAMES, make_deck, make_model, render_fields


def export_key(card, root):
    """Publish readable champion keys without rewriting source/review identities."""
    key = card['id']
    if not card.get('editorial_review') or card.get('entity_kind') != 'champion':
        return key
    prefix = card['entity_id'] + ':'
    if not re.fullmatch(r'champ:\d+:', prefix) or not key.startswith(prefix):
        return key  # Established readable IDs remain unchanged.
    packet = read_json(inside(root, card['editorial_review']['source_packet_path']))
    slug = packet['champion']['ddragon_id'].lower()
    if not re.fullmatch(r'[a-z][a-z0-9_-]*', slug):
        raise ValueError('A stable readable Riot champion identifier is required for export')
    return f'champ:{slug}:' + key[len(prefix):]


def read_collection(package):
    with zipfile.ZipFile(package) as z:
        con = sqlite3.connect(':memory:')
        con.deserialize(z.read('collection.anki2'))
    return con


def inspect_apkg(path):
    with zipfile.ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())) or z.testzip():
            raise ValueError('Corrupt/duplicate ZIP entries')
        media = json.loads(z.read('media'))
        if len(set(media.values())) != len(media):
            raise ValueError('Duplicate media filenames')
        if set(z.namelist()) != {'collection.anki2','media'} | set(media):
            raise ValueError('Unexpected or missing package entries')
        if any('/' in n or '\\' in n for n in media.values()):
            raise ValueError('Media filenames must be flat')
        con = sqlite3.connect(':memory:')
        con.deserialize(z.read('collection.anki2'))
        try:
            if con.execute('pragma integrity_check').fetchone()[0] != 'ok':
                raise ValueError('SQLite integrity failure')
            notes = con.execute('select id,guid,mid,flds from notes').fetchall()
            cards = con.execute('select id,nid,ord from cards').fetchall()
            if len(notes)!=len(cards) or {n[0] for n in notes}!={c[1] for c in cards} or any(c[2]!=0 for c in cards):
                raise ValueError('Expected exactly one forward card per note')
            if len({n[1] for n in notes})!=len(notes):
                raise ValueError('Duplicate note GUIDs')
            models = json.loads(con.execute('select models from col').fetchone()[0])
            model = models[str(MODEL_ID)]
            if len(model['tmpls']) != 1 or [f['name'] for f in model['flds']] != FIELD_NAMES:
                raise ValueError('Anki note-type compatibility broken')
            refs = set()
            for nid, g, mid, fields in notes:
                values = fields.split('\x1f')
                if len(values)!=len(FIELD_NAMES) or mid!=MODEL_ID or g!=guid(values[0]) or nid!=stable_id(values[0],1800000000000):
                    raise ValueError('Published identity or field schema mismatch')
                refs.update(html.unescape(n) for n in re.findall(r'src="([^"]+)"', fields))
            if refs != set(media.values()):
                raise ValueError('Missing or unreferenced package media')
            return {'notes': len(notes), 'cards': len(cards), 'media': len(media), 'sqlite_integrity': 'ok', 'sha256': digest(path.read_bytes())}
        finally:
            con.close()


def build(project, output):
    report = validate(project)
    if report['errors']:
        raise ValueError(f"Export blocked by {report['errors']} validation errors; run validate for details")
    content = project.content()
    return assemble(project,output,content)


def assemble(project,output,content,deck_ids=None,deck_name=None,level_names=None):
    """Shared deterministic serializer; callers validate their own production/staging scope."""
    deck_ids=deck_ids or DECKS
    keys = [export_key(card, project.root) for card in content['cards']]
    from .lanes import read_assignments
    lane_assignments = read_assignments(project.root) if (project.root / 'data/sources/champion-lanes-26.21.json').is_file() else {}
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate published card IDs after champion slug normalization')
    epoch = content['build_epoch']
    con = sqlite3.connect(':memory:')
    con.deserialize((project.legacy/'anki_template.anki2').read_bytes())
    try:
        columns = {r[1] for r in con.execute('pragma table_info(cards)')}
        if 'lapses' not in columns and 'laps' in columns:
            con.execute('alter table cards rename column laps to lapses')
        for table in ('notes','cards','revlog','graves'):
            con.execute('delete from '+table)
        cur = con.execute('select * from col')
        col = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        # make_model versions templates independently of historical content dates.
        models = json.loads(col['models']); models[str(MODEL_ID)] = make_model(epoch)
        decks = json.loads(col['decks'])
        root = deck_name or 'LoL · Pilot (6 Champions)'
        names = {'root':root,'L0':root+'::L0 · Basics','L1':root+'::L1 · Champion Overview','L2':root+'::L2 · Abilities & Timers'}
        names.update({key:root+'::'+name for key,name in (level_names or {}).items()})
        for key, name in names.items():
            decks[str(deck_ids[key])] = make_deck(deck_ids[key],name,epoch)
        conf = json.loads(col['conf'])
        conf.update(curDeck=deck_ids['L1'], activeDecks=[deck_ids['L1']], curModel=MODEL_ID)
        serial = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',',':'))
        con.execute('update col set mod=?,scm=?,models=?,decks=?,conf=?',
                    (epoch, epoch, serial(models), serial(decks), serial(conf)))
        used = set()
        for i, (card, key) in enumerate(zip(content['cards'], keys)):
            row = {**card['row'], 'id': key}
            if key.startswith('champ:') and row['level'] == 'L1':
                row['lanes'] = lane_assignments.get(key.split(':')[1], [])
            fields, tags = render_fields(row, project.media_root_for(row), used)
            if card.get('editorial_review') or card.get('staging_status'):
                from .editorial_contract import note_fields
                fields=note_fields(card,fields)
            flds = '\x1f'.join(fields[k] for k in FIELD_NAMES)
            nid = stable_id(key,1800000000000); cid = stable_id(key,2300000000000)
            csum = int(hashlib.sha1(key.encode()).hexdigest()[:8],16)
            con.execute('insert into notes values (?,?,?,?,?,?,?,?,?,?,?)',
                        (nid,guid(key),MODEL_ID,card['revision'],-1,tags,flds,key,csum,0,''))
            con.execute('insert into cards values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (cid,nid,deck_ids[row['level']],0,card['revision'],-1,0,0,i+1,0,2500,0,0,0,0,0,0,''))
        con.commit()
        con.execute('vacuum')
        db = con.serialize()
    finally:
        con.close()
    stream = io.BytesIO()
    def entry(z, name, data):
        info = zipfile.ZipInfo(name, (1980,1,1,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        z.writestr(info, data, compresslevel=6)
    paths = {p.name:p for p in project.media_paths(used)}
    with zipfile.ZipFile(stream, 'w') as z:
        entry(z,'collection.anki2',db)
        mapping = {}
        for n, name in enumerate(sorted(used)):
            entry(z,str(n),paths[name].read_bytes())
            mapping[str(n)] = name
        entry(z,'media',serial(mapping).encode())
    atomic(output,stream.getvalue())
    return inspect_apkg(output)

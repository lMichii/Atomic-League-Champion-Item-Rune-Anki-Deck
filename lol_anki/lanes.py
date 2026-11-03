"""Conservative champion lane assignments from an archived ranked-position table."""
from __future__ import annotations

from html.parser import HTMLParser
import hashlib
import json
import re
from pathlib import Path

from .io import atomic, read_json

SOURCE_MANIFEST = 'data/sources/champion-lanes-26.21.json'
LANES = {'Top', 'Jungle', 'Mid', 'Bot', 'Support'}
SOURCE_ALIASES = {'monkeyking': 'MonkeyKing', 'nunu': 'Nunu', 'renata': 'Renata'}


def _key(value):
    return re.sub(r'[^a-z0-9]', '', value.casefold())


class _Table(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.in_row = False
        self.in_positions = False
        self.current_name = None
        self.current_lanes = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get('class') or '').split())
        if tag == 'tr' and 'lolm-row' in classes:
            self.in_row, self.current_name, self.current_lanes = True, None, []
        elif self.in_row and tag == 'a' and a.get('data-pick'):
            self.current_name = a['data-pick']
        elif self.in_row and tag == 'td' and 'lolm-c-pos' in classes:
            self.in_positions = True
        elif self.in_row and self.in_positions and tag == 'img':
            lane = a.get('alt') or a.get('title')
            lane = {'Middle': 'Mid', 'Bottom': 'Bot'}.get(lane, lane)
            if lane in LANES and lane not in self.current_lanes:
                self.current_lanes.append(lane)

    def handle_endtag(self, tag):
        if tag == 'td':
            self.in_positions = False
        elif tag == 'tr' and self.in_row:
            if self.current_name:
                self.rows.append((self.current_name, self.current_lanes))
            self.in_row = self.in_positions = False


def read_assignments(root):
    """Return slug-to-lanes mapping from the saved source manifest, never champion classes."""
    manifest = read_json(Path(root) / SOURCE_MANIFEST)
    return {slug: list(record['lanes']) for slug, record in manifest['champions'].items()}


def map_source_html(html_text, champion_names):
    """Match source position rows to card champion names; unmatched records stay blank."""
    parser = _Table()
    parser.feed(html_text)
    by_key = {}
    for name, lanes in parser.rows:
        key = _key(name)
        if key in by_key:
            raise ValueError(f'Duplicate champion in lane source: {name}')
        by_key[key] = (name, lanes)
    result = {}
    used = set()
    for slug, name in champion_names.items():
        found = by_key.get(_key(SOURCE_ALIASES.get(slug, name))) or by_key.get(_key(name))
        if not found:
            result[slug] = {'name': name, 'lanes': [], 'source_name': None}
            continue
        source_name, lanes = found
        used.add(_key(source_name))
        result[slug] = {'name': name, 'lanes': lanes[:2], 'source_name': source_name}
    return result, sorted(name for name, _ in parser.rows if _key(name) not in used)


def create_manifest(root, source_html, champion_names, retrieved_utc):
    """Archive the already retrieved evidence and write a compact assignment manifest."""
    root = Path(root)
    raw_path = root / 'data/sources/raw/champion-lanes/roles-26.21.html'
    raw_bytes = Path(source_html).read_bytes()
    atomic(raw_path, raw_bytes)
    mapped, unmatched = map_source_html(raw_bytes.decode('utf-8'), champion_names)
    manifest = {
        'source': {
            'title': 'League of Legends Champions | SenseOS',
            'url': 'https://senseos.gg/wiki/league-of-legends/champions/',
            'retrieved_utc': retrieved_utc,
            'patch': '26.21',
            'data_window': 'Patches 26.20–26.21; ranked Solo/Duo across 15 regions, all ranks',
            'method': 'Use only the first two positions listed in the source Position column, in displayed order. The first is primary and the next is common secondary. Do not infer positions from champion classes. Source ranking requires at least 100 games in a position when listed.',
            'source_rows': 173,
            'html_sha256': hashlib.sha256(raw_bytes).hexdigest(),
            'archived_html': raw_path.relative_to(root).as_posix(),
            'normalization': {'Middle': 'Mid', 'Bottom': 'Bot'},
        },
        'champions': mapped,
        'unmatched_source_names': unmatched,
    }
    atomic(root / SOURCE_MANIFEST, (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'))
    return manifest


def apply_to_apkg(source, output, manifest, template_revision):
    """Copy an existing APKG and update only its champion L1 back answer and model CSS."""
    import io
    import sqlite3
    import zipfile

    source, output = Path(source), Path(output)
    lanes_by_slug = {slug: row['lanes'] for slug, row in manifest['champions'].items()}
    with zipfile.ZipFile(source, 'r') as zin:
        original_entries = [(info, zin.read(info.filename)) for info in zin.infolist()]
    db_index = next(i for i, (info, _) in enumerate(original_entries) if info.filename == 'collection.anki2')
    con = sqlite3.connect(':memory:')
    con.deserialize(original_entries[db_index][1])
    try:
        changed = []
        for nid, flds in con.execute('select id,flds from notes').fetchall():
            values = flds.split('\x1f')
            row = dict(zip(('Key','Level','Champion','Slot','Ability','FrontHint','Question','Answer','Counterplay','Cooldown','MediaHTML','IconHTML','Riot','Wiki','Patch','Priority','Review'), values))
            match = re.fullmatch(r'champ:([^:]+):overview:L1', row['Key'])
            if not match:
                continue
            slug = match.group(1)
            lanes = lanes_by_slug.get(slug, [])
            if lanes:
                addition = '<p class="lanes" style="font-size:12px;color:#89939c;margin:5px 0 0"><b>Lanes:</b> ' + ' · '.join(lanes) + '</p>'
                values[7] += addition
                con.execute('update notes set flds=?,mod=? where id=?', ('\x1f'.join(values), template_revision, nid))
                changed.append((slug, lanes))
        con.commit()
        con.execute('vacuum')
        db = con.serialize()
    finally:
        con.close()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zout:
        for i, (info, data) in enumerate(original_entries):
            info_out = zipfile.ZipInfo(info.filename, info.date_time)
            info_out.compress_type = info.compress_type
            info_out.external_attr = info.external_attr
            info_out.create_system = info.create_system
            zout.writestr(info_out, db if i == db_index else data)
    atomic(output, buffer.getvalue())
    return changed

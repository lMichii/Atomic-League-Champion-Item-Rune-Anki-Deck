"""Read every original file, hash binaries, inspect archives/SQLite/XLSX without edits."""
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def workbook(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        sheets = ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets', NS)
        result = []
        for n, sheet in enumerate(sheets, 1):
            path = f'xl/worksheets/sheet{n}.xml'
            rows = []
            if path not in z.namelist():
                continue
            for row in ET.fromstring(z.read(path)).findall('.//s:row', NS):
                values = []
                for c in row:
                    v = c.find('s:v', NS)
                    text = v.text if v is not None else ''.join(c.itertext())
                    if c.get('t') == 's' and text:
                        text = strings[int(text)]
                    values.append(text or '')
                if any(values):
                    rows.append(values)
            result.append({'sheet': sheet.get('name'), 'rows': len(rows), 'values': rows})
        return result


def inspect():
    result = {'files': [], 'archives': {}, 'workbooks': {}}
    paths = sorted(p for p in ROOT.rglob('*') if p.is_file() and
                   (p.relative_to(ROOT).parts[0].startswith('LoL_')) and '__pycache__' not in p.parts)
    for p in paths:
        blob = p.read_bytes()
        name = p.relative_to(ROOT).as_posix()
        result['files'].append({'path': name, 'bytes': len(blob), 'sha256': hashlib.sha256(blob).hexdigest()})
        if p.suffix == '.xlsx':
            result['workbooks'][name] = workbook(blob)
        elif p.suffix in ('.zip', '.apkg'):
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                entries = {}
                for f in z.namelist():
                    data = z.read(f)
                    entry = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                    if f.endswith(('.md', '.csv', '.py', '.bat', '.json', '.txt')):
                        entry['text'] = data.decode('utf-8-sig')
                    entries[f] = entry
                result['archives'][name] = entries
    cards = list(csv.DictReader((ROOT/'LoL_Anki_Pilot_Project_v4_English/cards.csv').open(encoding='utf-8-sig')))
    result['cards_summary'] = {'count': len(cards), 'levels': dict(collections.Counter(r['level'] for r in cards)),
                               'media': dict(collections.Counter(r['media_type'] for r in cards))}
    for p in [ROOT/'LoL_Anki_Pilot_Project_v4_English/anki_template.anki2']:
        with sqlite3.connect(p.as_uri()+'?mode=ro', uri=True) as con:
            result['template_schema'] = con.execute('select name,sql from sqlite_master').fetchall()
            result['template_counts'] = {t: con.execute('select count(*) from '+t).fetchone()[0] for t in ('notes','cards','col')}
    return result


if __name__ == '__main__':
    result = inspect()
    out = ROOT/'docs/legacy_inventory.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Original files:', len(result['files']), 'bytes:', sum(f['bytes'] for f in result['files']))
    print('Cards:', result['cards_summary'])
    for name, sheets in result['workbooks'].items():
        print(name, [(s['sheet'], s['rows']) for s in sheets])
    for name, entries in result['archives'].items():
        print(name, list(entries)[:20], 'entries:', len(entries))
        if name.endswith('.zip'):
            for f, e in entries.items():
                if f.endswith('.md'):
                    print(f, e['text'])

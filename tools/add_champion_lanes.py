"""Apply archived champion position data to L1 backs without rebuilding card content."""
import argparse
import json
import sqlite3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lol_anki.lanes import apply_to_apkg, create_manifest
from lol_anki.package import inspect_apkg, read_collection
from lol_anki.v4 import TEMPLATE_REVISION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-apkg', type=Path, default=ROOT/'build/staging/League_Anki_Gesamtstand_BackOnly_2026-11-03.apkg')
    parser.add_argument('--source-html', type=Path, default=ROOT/'data/sources/raw/champion-lanes/roles-26.21.html')
    parser.add_argument('--output-apkg', type=Path, default=ROOT/'build/staging/League_Anki_Gesamtstand_Lanes_26.21.apkg')
    parser.add_argument('--retrieved-utc', default='2026-11-03T19:20:00Z')
    args = parser.parse_args()
    con = read_collection(args.source_apkg)
    try:
        names = {}
        for fields, in con.execute('select flds from notes'):
            row = dict(zip(('Key','Level','Champion'), fields.split('\x1f')))
            if row.get('Key','').startswith('champ:') and row.get('Level') == 'L1':
                slug = row['Key'].split(':')[1]
                names[slug] = row['Champion']
    finally:
        con.close()
    manifest = create_manifest(ROOT, args.source_html, names, args.retrieved_utc)
    if len(manifest['champions']) != 173:
        raise SystemExit(f"Expected 173 champions, found {len(manifest['champions'])}")
    changed = apply_to_apkg(args.source_apkg, args.output_apkg, manifest, TEMPLATE_REVISION)
    expected = sum(bool(row['lanes']) for row in manifest['champions'].values())
    if len(changed) != expected:
        raise SystemExit(f'Expected {expected} lane-bearing L1 cards to update, found {len(changed)}')
    print(json.dumps({'output':str(args.output_apkg),'cards':inspect_apkg(args.output_apkg),
                      'lane_cards':len(changed),'blank_lanes':[slug for slug,row in manifest['champions'].items() if not row['lanes']],
                      'unmatched_source_names':manifest['unmatched_source_names']},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()

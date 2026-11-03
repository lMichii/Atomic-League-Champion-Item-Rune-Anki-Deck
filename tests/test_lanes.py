import json
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch
import zipfile

from lol_anki.lanes import LANES, SOURCE_MANIFEST, map_source_html
from lol_anki.project import ROOT
from lol_anki.v4 import TEMPLATE_REVISION, render_fields


class LaneDataTests(unittest.TestCase):
    def test_reads_only_explicit_positions_and_normalizes_names(self):
        page = '''<table><tr class="lolm-row"><td><a data-pick="MonkeyKing">Wukong</a></td>
        <td class="lolm-c-pos"><img alt="Jungle"><img alt="Top"><img alt="Support"></td></tr></table>'''
        result, unmatched = map_source_html(page, {'monkeyking':'Wukong', 'unknown':'Unknown'})
        self.assertEqual(result['monkeyking']['lanes'], ['Jungle', 'Top'])
        self.assertEqual(result['unknown']['lanes'], [])
        self.assertEqual(unmatched, [])
        self.assertTrue(set(result['monkeyking']['lanes']) <= LANES)

    def test_lanes_render_only_on_l1_answer(self):
        row = {'id':'champ:test:overview:L1','level':'L1','champion':'Test','slot':'-',
               'ability':'','icon_path':'','media_type':'none','media_path':'','front_hint':'',
               'question':'What can this champion do?','answer':'A short overview.',
               'counterplay':'Watch the approach.','cooldown':'','priority':2,
               'build_focus':'Tank','lanes':['Jungle','Top']}
        with patch('lol_anki.v4.media_file',return_value='portrait.webp'):
            fields, _ = render_fields(row, Path('.'), set())
        self.assertIn('<p class="lanes" style="font-size:12px;color:#89939c;margin:5px 0 0"><b>Lanes:</b> Jungle · Top</p>', fields['Answer'])
        self.assertNotIn('Lanes', fields['Question'] + fields['MediaHTML'])
        self.assertIn('Build focus:', fields['Answer'])

        row.update(id='champ:test:q:recognize:L2',level='L2',slot='Q',lanes=['Jungle'])
        with patch('lol_anki.v4.media_file',return_value='icon.webp'):
            fields, _ = render_fields(row, Path('.'), set())
        self.assertNotIn('Lanes', fields['Answer'])


class CompleteLaneExportTests(unittest.TestCase):
    def test_export_changes_only_173_l1_answers_and_css(self):
        original = ROOT/'build/staging/League_Anki_Gesamtstand_BackOnly_2026-11-03.apkg'
        updated = ROOT/'build/staging/League_Anki_Gesamtstand_Lanes_26.21.apkg'
        index = ROOT/'data/database/cards.jsonl'
        if not all(p.is_file() for p in (original, updated, index, ROOT/SOURCE_MANIFEST)):
            self.skipTest('Full lane APKG has not been built in this checkout')
        manifest=json.loads((ROOT/SOURCE_MANIFEST).read_text('utf-8'))
        lane_map={slug:entry['lanes'] for slug,entry in manifest['champions'].items()}
        with zipfile.ZipFile(original) as oldz, zipfile.ZipFile(updated) as newz:
            oldmedia=json.loads(oldz.read('media')); newmedia=json.loads(newz.read('media'))
            self.assertEqual(oldmedia,newmedia)
            for name in oldmedia:
                self.assertEqual(oldz.read(name),newz.read(name))
            old=sqlite3.connect(':memory:'); old.deserialize(oldz.read('collection.anki2'))
            new=sqlite3.connect(':memory:'); new.deserialize(newz.read('collection.anki2'))
            try:
                oldnotes=old.execute('select * from notes order by id').fetchall()
                newnotes=new.execute('select * from notes order by id').fetchall()
                self.assertEqual(len(oldnotes),1089); self.assertEqual(len(newnotes),1089)
                changed=0
                for a,b in zip(oldnotes,newnotes):
                    self.assertEqual((a[0],a[1],a[2]),(b[0],b[1],b[2]))
                    self.assertEqual(a[4:6],b[4:6])
                    self.assertEqual(a[7:],b[7:])
                    av,bv=a[6].split('\x1f'),b[6].split('\x1f')
                    self.assertEqual(len(av),17); self.assertEqual(len(bv),17)
                    self.assertEqual([x for i,x in enumerate(av) if i!=7],[x for i,x in enumerate(bv) if i!=7])
                    key=av[0]
                    if key.startswith('champ:') and av[1]=='L1':
                        lanes=lane_map[key.split(':')[1]]
                        expected='<p class="lanes" style="font-size:12px;color:#89939c;margin:5px 0 0"><b>Lanes:</b> '+' · '.join(lanes)+'</p>' if lanes else ''
                        self.assertEqual(bv[7],av[7]+expected)
                        self.assertEqual(b[3],TEMPLATE_REVISION if expected else a[3])
                        changed+=bool(expected)
                    else:
                        self.assertEqual(av[7],bv[7])
                        self.assertEqual(a[3],b[3])
                self.assertEqual(changed,173)
                oldcards=old.execute('select * from cards order by id').fetchall()
                newcards=new.execute('select * from cards order by id').fetchall()
                self.assertEqual(oldcards,newcards)
                oldmodel=json.loads(old.execute('select models from col').fetchone()[0])['2042610311001']
                newmodel=json.loads(new.execute('select models from col').fetchone()[0])['2042610311001']
                self.assertEqual(oldmodel,newmodel)
            finally:
                old.close(); new.close()
        rows=[json.loads(line) for line in index.read_text('utf-8').splitlines()]
        self.assertEqual(len(rows),1089)
        l1=[r for r in rows if r['key'].startswith('champ:') and r['level']=='L1']
        self.assertEqual(len(l1),173)
        self.assertTrue(all(r['lanes'] and r['lane_source']=='senseos-champion-positions-26.21' for r in l1))


if __name__ == '__main__':
    unittest.main()

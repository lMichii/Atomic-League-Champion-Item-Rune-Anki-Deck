"""Prototype scope, v4 rendering and real isolated importer regression."""
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import copy
from lol_anki.database import lookup
from lol_anki.generation.preview import template
from lol_anki.identity import guid,stable_id,MODEL_ID
from lol_anki.io import read_json
from lol_anki.items import CONTENT,SOURCES,INDEX,OUTPUT,build_prototype,validate_items
from lol_anki.package import inspect_apkg,read_collection
from lol_anki.project import ROOT
from lol_anki.v4 import FIELD_NAMES,QFMT,AFMT,CSS
from lol_anki.learning_style import format_learning, render_sections, KEYWORDS
from lol_anki.item_visuals import visual_glossary
from lol_anki.v4 import format_stats, render_fields
from lol_anki.io import digest, canonical


def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


class ItemPrototypeTests(unittest.TestCase):
    def test_visual_overlay_rejects_duplicate_identity_and_changed_provenance(self):
        content=read_json(ROOT/CONTENT)
        original=read_json(ROOT/'data/sources/items-glossary-visuals.json')
        for corruption in ('duplicate','provenance','baseline'):
            manifest=copy.deepcopy(original)
            if corruption=='duplicate': manifest['examples'].append(manifest['examples'][0])
            elif corruption=='provenance': manifest['examples'][0]['source_records'][0]['sha256']='0'*64
            else: manifest['examples'][0]['baseline_sha256']='0'*64
            def read(path):
                return manifest if Path(path).name=='items-glossary-visuals.json' else read_json(path)
            with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temp:
                with patch('lol_anki.item_visuals.read_json',side_effect=read):
                    with self.assertRaises(ValueError): visual_glossary(ROOT,content,Path(temp))

    def test_compact_qss_keywords_and_visual_identity(self):
        content=read_json(ROOT/CONTENT)
        qss=next(c for c in content['cards'] if c['row']['level']=='L2')
        self.assertEqual([s['label'] for s in qss['row']['sections']],
                         ['Cooldown','Can remove','Limitations','Key difference'])
        self.assertLess(len(qss['row']['answer'].split()),65)
        for word in ('Ignite','Exhaust','Mordekaiser'): self.assertNotIn(word,qss['row']['answer'])
        for word in ('suppression','airborne','90 seconds','Cleanse'): self.assertIn(word,qss['row']['answer'])
        for word in ('AD','AP','physical damage','magic damage','armor','magic resistance'):
            self.assertEqual(format_learning(word),format_stats(word))
        for key,(pattern,color) in KEYWORDS.items():
            word={'root':'root','stun':'stun','airborne':'airborne'}.get(key,key.replace('-',' '))
            self.assertIn('keyword-'+key,format_learning(word))
        self.assertNotIn('keyword-',format_learning('charming rooted stunning'))
        self.assertIn('&lt;script&gt;',format_learning('<script>Stun</script>'))
        with self.assertRaises(ValueError): render_sections([{'label':'Unknown','text':'x'}])
        con=read_collection(ROOT/OUTPUT)
        try:
            exported={f.split('\x1f')[0]:dict(zip(FIELD_NAMES,f.split('\x1f'))) for f, in con.execute('select flds from notes')}
            pilot=read_json(ROOT/'data/content/pilot.json')
            for card in pilot['cards']:
                if card['id'] not in exported: continue
                original,_=render_fields(card['row'],ROOT/'LoL_Anki_Pilot_Project_v4_English',set())
                self.assertEqual(exported[card['id']]['Key'],original['Key'])
                # Definitions stay unchanged; highlighting removes to the same text.
                from html import unescape
                text=unescape(re.sub('<[^>]+>','',exported[card['id']]['Answer'].split('<p style=')[0]))
                self.assertEqual(text,card['row']['answer'])
        finally: con.close()

    def test_scope_sources_catalogue_and_offline_replay_protect_champions(self):
        content=read_json(ROOT/CONTENT); packet=read_json(ROOT/SOURCES)
        report=validate_items(ROOT,content,packet)
        self.assertEqual((report['cards'],report['l1'],report['l2'],report['l0']),(9,5,1,3))
        protected=[ROOT/'data/database/cards.jsonl',ROOT/'data/content/pilot.json',
                   ROOT/'data/content/production.json',ROOT/'data/content/editorial.json',
                   ROOT/'data/editorial/registry.json',ROOT/'build/staging/League_Anki_Gesamtstand_Lanes_26.21.apkg',
                   ROOT/CONTENT,ROOT/SOURCES,ROOT/OUTPUT]
        before={p:sha(p) for p in protected}
        result=build_prototype(ROOT,offline=True)
        self.assertEqual((result['package']['notes'],result['package']['cards'],result['package']['media']),(14,14,11))
        self.assertEqual(before,{p:sha(p) for p in protected})
        self.assertEqual(len((ROOT/'data/database/cards.jsonl').read_text('utf-8').splitlines()),1089)
        index=[json.loads(x) for x in (ROOT/INDEX).read_text('utf-8').splitlines()]
        self.assertEqual(len(index),9)
        self.assertEqual(lookup(ROOT,'3140')['count'],2)
        for card in lookup(ROOT,'3140',include_raw=True)['cards']:
            source=card['stored_sources'][0]
            self.assertTrue(all((ROOT/r['raw_path']).is_file() for r in source['resources']))
            self.assertEqual([e['id'] for e in source['excerpts']],['Quicksilver_Sash'])
            self.assertTrue(all('content' not in r for r in source['resources'] if r['kind']=='png'))

    def test_item_fronts_back_only_footer_and_unchanged_champion_rendering(self):
        self.assertEqual(inspect_apkg(ROOT/OUTPUT)['notes'],14)
        new=read_collection(ROOT/OUTPUT)
        old=read_collection(ROOT/'build/staging/League_Anki_Gesamtstand_Lanes_26.21.apkg')
        try:
            for nid,g,fields in new.execute('select id,guid,flds from notes'):
                f=dict(zip(FIELD_NAMES,fields.split('\x1f'))); key=f['Key']
                self.assertEqual((nid,g),(stable_id(key,1800000000000),guid(key)))
                front=template(QFMT,f); back=template(AFMT,{**f,'FrontSide':front})
                self.assertNotIn('class="bottom"',front); self.assertNotIn('Patch 26.21',front)
                self.assertNotIn('League</a>',front); self.assertEqual(back.count('class="bottom"'),1)
                self.assertIn('Patch 26.21',back)
                if key.startswith('item:'):
                    self.assertIn('item-'+key.split(':')[1]+'.png',front)
                    self.assertIn('width:160px',front)
                    if f['Level']=='L1':
                        self.assertNotIn(f['Champion'],front)
                        self.assertIn('What does this item do?',front); self.assertIn('<b>Use:</b>',back)
                        self.assertLess(back.index('<b>Use:</b>'),back.index('class="bottom"'))
                        stats=re.sub('<[^>]+>','',f['Answer'].split('<br>')[0])
                        self.assertFalse(any(ch.isdigit() for ch in stats))
                    else: self.assertIn('Quicksilver Sash',front)
            self.assertEqual(old.execute('select count(*) from notes').fetchone()[0],1089)
            model=json.loads(new.execute('select models from col').fetchone()[0])[str(MODEL_ID)]
            self.assertEqual(model['css'],CSS)
            self.assertEqual(model['tmpls'][0]['qfmt'],QFMT)
            self.assertEqual(model['tmpls'][0]['afmt'],AFMT)
        finally: new.close(); old.close()

    @unittest.skipUnless(importlib.util.find_spec('anki'),'Optional isolated Anki runtime unavailable')
    def test_real_import_reimport_rendering_and_schedule_preservation(self):
        from anki.collection import Collection,ImportAnkiPackageRequest,ImportAnkiPackageOptions
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temp:
            previous=tempfile.tempdir; previous_cwd=Path.cwd(); tempfile.tempdir=temp; col=None
            try:
                col=Collection(str(Path(temp)/'items.anki2'))
                def load(package=ROOT/OUTPUT):
                    col.import_anki_package(ImportAnkiPackageRequest(package_path=str(package),
                        options=ImportAnkiPackageOptions(with_scheduling=False,with_deck_configs=False,
                                                        update_notes=0,update_notetypes=0)))
                    col.models._clear_cache()
                from lol_anki.package import build
                from lol_anki.project import Project
                baseline=Path(temp)/'baseline.apkg'; build(Project(),baseline)
                load(baseline)
                self.assertEqual(col.note_count(),64)
                champion_fields={nid:fields for nid,fields in col.db.all('select id,flds from notes') if fields.startswith('champ:')}
                col.db.execute('update cards set type=2,queue=2,due=99,ivl=12,reps=7,lapses=1,factor=2400')
                columns='id,nid,type,queue,due,ivl,reps,lapses,factor'
                original_schedules=col.db.all('select '+columns+' from cards order by id')
                load(); self.assertEqual((col.note_count(),col.card_count()),(73,73))
                for schedule in original_schedules:
                    self.assertEqual(schedule,col.db.first('select '+columns+' from cards where id=?',schedule[0]))
                for nid,fields in champion_fields.items():
                    self.assertEqual(fields,col.db.scalar('select flds from notes where id=?',nid))
                ids=col.db.all('select id,guid,mid from notes order by id')
                col.db.execute('update cards set type=2,queue=2,due=123,ivl=17,reps=9,lapses=2,factor=2500')
                columns='id,nid,type,queue,due,ivl,reps,lapses,factor'
                schedules=col.db.all('select '+columns+' from cards order by id')
                load(); load()
                self.assertEqual((col.note_count(),col.card_count()),(73,73))
                self.assertEqual(ids,col.db.all('select id,guid,mid from notes order by id'))
                self.assertEqual(schedules,col.db.all('select '+columns+' from cards order by id'))
                for cid, in col.db.all('select id from cards'):
                    card=col.get_card(cid); note=card.note()
                    self.assertNotIn('class="bottom"',card.question())
                    self.assertNotIn('League</a>',card.question())
                    self.assertEqual(card.answer().count('class="bottom"'),1)
                    if note['Key'].startswith('item:') and note['Level']=='L1':
                        self.assertNotIn(note['Champion'],card.question())
                media=Path(temp)/'items.media'
                for item in ('3077','3140','3153','3157','3916'): self.assertTrue((media/('item-'+item+'.png')).is_file())
                self.assertGreaterEqual(len(list(media.glob('*.gif'))),6)
            finally:
                if col: col.close()
                os.chdir(previous_cwd); tempfile.tempdir=previous

"""Production regression tests: real batch assets and isolated Anki reimport."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from lol_anki.io import digest,read_json
from lol_anki.media import gif_info
from lol_anki.package import build,read_collection,inspect_apkg
from lol_anki.project import Project,ROOT
from lol_anki.validation import validate


class Batch01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project=Project(profile='batch01')
        cls.output=ROOT/'build/batch01/test-production.apkg'
        cls.result=build(cls.project,cls.output)

    def test_only_the_established_36_ids_added_and_all_pilot_records_unchanged(self):
        pilot=Project().content()['cards']; production=self.project.content()['cards']
        with (ROOT/'data/batch01/input/new_cards.csv').open(encoding='utf-8-sig',newline='') as f:
            original_ids={r['id'] for r in csv.DictReader(f)}
        self.assertEqual(len(production),100)
        self.assertEqual(production[:64],pilot)
        self.assertEqual({c['id'] for c in production[64:]},original_ids)
        lock=read_json(self.project.path('lock'))
        self.assertEqual(set(lock['reviews'][-1]['changed_ids']),original_ids)
        self.assertEqual(validate(self.project)['errors'],0)

    def test_production_pilot_fields_ids_media_and_design_match_original(self):
        old=read_collection(Project().legacy/'LoL_Anki_Pilot_6_Champions_v4_English.apkg')
        new=read_collection(self.output)
        from lol_anki.lanes import read_assignments
        lane_map=read_assignments(ROOT)
        try:
            for row in old.execute('select id,guid,mid,mod,tags,flds,sfld,csum from notes'):
                updated=new.execute('select id,guid,mid,mod,tags,flds,sfld,csum from notes where id=?',(row[0],)).fetchone()
                self.assertEqual(row[:5]+row[6:],updated[:5]+updated[6:])
                before,after=row[5].split('\x1f'),updated[5].split('\x1f')
                key=before[0]
                if key.startswith('champ:') and before[1]=='L1' and lane_map.get(key.split(':')[1]):
                    from html import escape
                    lane_html='<p class="lanes" style="font-size:12px;color:#89939c;margin:5px 0 0"><b>Lanes:</b> '+' · '.join(escape(x,quote=True) for x in lane_map[key.split(':')[1]])+'</p>'
                    before[7]+=lane_html
                self.assertEqual(before,after)
            model_id='2042610311001'
            om=json.loads(old.execute('select models from col').fetchone()[0])[model_id]
            nm=json.loads(new.execute('select models from col').fetchone()[0])[model_id]
            for key in ('flds','req','type','sortf'):
                self.assertEqual(om[key],nm[key])
            self.assertNotIn('bottom',nm['tmpls'][0]['qfmt'])
            self.assertIn('Patch {{Patch}}',nm['tmpls'][0]['afmt'])
            self.assertNotIn('Patch',nm['tmpls'][0]['qfmt'])
            self.assertNotIn('{{Review}}',nm['tmpls'][0]['afmt'])
            self.assertEqual(len(nm['tmpls']),1)
        finally:
            old.close(); new.close()
        with zipfile.ZipFile(Project().legacy/'LoL_Anki_Pilot_6_Champions_v4_English.apkg') as a,zipfile.ZipFile(self.output) as b:
            ma=json.loads(a.read('media')); mb={v:k for k,v in json.loads(b.read('media')).items()}
            for k,name in ma.items():
                self.assertEqual(a.read(k),b.read(mb[name]),name)

    def test_real_media_and_fact_review_evidence(self):
        sources=self.project.sources()
        for card in self.project.content()['cards'][64:]:
            r=card['row']; self.assertEqual(card['qa_status'],'approved')
            self.assertNotIn('\ufffd',' '.join(r.values()))
            self.assertEqual(r['cooldown'],'')
            if r['level']=='L1':
                self.assertEqual(r['question'],'What can this champion do?')
                self.assertTrue(r['build_focus']); self.assertTrue(r['counterplay'])
            elif r['slot']!='P':
                self.assertEqual(r['media_type'],'gif')
                info=gif_info((self.project.media_root_for(r)/r['media_path']).read_bytes())
                self.assertGreater(info['frames'],1); self.assertEqual(info['loop'],0)
            snap=card['evidence']['wiki_snapshot']
            html=(ROOT/snap['path']).read_bytes()
            self.assertEqual(digest(html),snap['sha256'])
            self.assertIn(('"wgRevisionId":'+card['evidence']['wiki_revision']).encode(),html)
            self.assertIn(card['row']['ability'].encode(),html) if r['level']=='L2' else None
        provenance=sources['batch01_media_provenance']
        self.assertEqual(len(provenance),94)
        self.assertTrue(all(p['source_url'].startswith(('https://ddragon.leagueoflegends.com/','https://d28xe8vt774jo5.cloudfront.net/')) for p in provenance))
        caitlyn=next(c for c in self.project.content()['cards'] if c['id']=='champ:caitlyn:p:recognize:L2')
        self.assertTrue(caitlyn['row']['visual_cue_media_path'])
        self.assertIn('pending',caitlyn['media_review']['current_client_review'])

    def test_production_structure_and_reproducibility(self):
        self.assertEqual(self.result['notes'],100)
        self.assertEqual(self.result['media'],120)
        stamp=self.output.stat().st_mtime_ns
        self.assertEqual(build(self.project,self.output)['sha256'],self.result['sha256'])
        self.assertEqual(stamp,self.output.stat().st_mtime_ns)
        self.assertEqual(inspect_apkg(self.output)['cards'],100)

    @unittest.skipUnless(importlib.util.find_spec('anki'),'Optional Anki importer runtime required')
    def test_real_reimport_preserves_all_pilot_scheduling_and_review_history(self):
        from anki.collection import Collection,ImportAnkiPackageRequest,ImportAnkiPackageOptions
        import os
        previous=Path.cwd()
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
            col=None
            try:
                col=Collection(str(Path(folder)/'collection.anki2'))
                def load(path):
                    return col.import_anki_package(ImportAnkiPackageRequest(package_path=str(path),
                        options=ImportAnkiPackageOptions(with_scheduling=False,with_deck_configs=False,update_notes=0,update_notetypes=0)))
                load(Project().legacy/'LoL_Anki_Pilot_6_Champions_v4_English.apkg')
                self.assertEqual(col.note_count(),64)
                pilot_ids=col.db.list('select id from cards order by id')
                for i,cid in enumerate(pilot_ids):
                    col.db.execute('update cards set type=2,queue=2,due=?,ivl=37,reps=11,lapses=3,factor=2400 where id=?',i+17,cid)
                    col.db.execute('insert into revlog (id,cid,usn,ease,ivl,lastIvl,factor,time,type) values (?,?,?,?,?,?,?,?,?)',1790000000000+i,cid,-1,3,37,21,2400,1200,1)
                fields='id,nid,type,queue,due,ivl,reps,lapses,factor,left,odue,odid,flags,data'
                before={row[0]:row for row in col.db.all('select '+fields+' from cards')}
                logs=col.db.all('select * from revlog order by id')
                notes={n[0]:n for n in col.db.all('select guid,flds from notes')}
                for _ in range(2):
                    load(self.output)
                    self.assertEqual(col.note_count(),100); self.assertEqual(col.card_count(),100)
                    for cid in pilot_ids:
                        self.assertEqual(before[cid],col.db.first('select '+fields+' from cards where id=?',cid))
                    self.assertEqual(logs,col.db.all('select * from revlog order by id'))
                    current={n[0]:n for n in col.db.all('select guid,flds from notes')}
                    self.assertTrue(all(current[g]==n for g,n in notes.items()))
                media=list((Path(folder)/'collection.media').glob('*'))
                self.assertEqual(len(media),120)
                write=__import__('lol_anki.io',fromlist=['write_json']).write_json
                write(ROOT/'build/batch01/reimport_verification.json',{'anki_version':'25.9.2','notes':100,'cards':100,'media_files':120,
                     'pilot_schedules_preserved':64,'pilot_review_log_rows_preserved':64,'repeat_imports':2,'user_collection_opened':False})
            finally:
                if col: col.close()
                os.chdir(previous)

import copy
import csv
import importlib.util
import json
from pathlib import Path
import sqlite3
import unittest
import zipfile
from helpers import sandbox_project
from lol_anki.identity import guid, new_key, stable_id, MODEL_ID
from lol_anki.io import canonical, digest, inside, read_json, write_json
from lol_anki.package import build, inspect_apkg, read_collection
from lol_anki.project import Project, ROOT
from lol_anki.validation import validate
from lol_anki import v4


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = Project()
        cls.output = ROOT/'build/tests/pilot.apkg'
        cls.result = build(cls.project,cls.output)
        cls.original = cls.project.legacy/'LoL_Anki_Pilot_6_Champions_v4_English.apkg'

    def test_lossless_authored_migration(self):
        with (self.project.legacy/'cards.csv').open(encoding='utf-8-sig',newline='') as f:
            original = list(csv.DictReader(f))
        self.assertEqual(original,[c['row'] for c in self.project.content()['cards']])

    def test_all_64_published_note_fields_and_ids_unchanged(self):
        old,new = read_collection(self.original),read_collection(self.output)
        from lol_anki.lanes import read_assignments
        lane_map=read_assignments(ROOT)
        try:
            sql = 'select id,guid,mid,tags,flds,sfld,csum,flags,data from notes order by id'
            before,after=old.execute(sql).fetchall(),new.execute(sql).fetchall()
            self.assertEqual(len(before),len(after))
            for a,b in zip(before,after):
                self.assertEqual(a[:4],b[:4]); self.assertEqual(a[5:],b[5:])
                af,bf=a[4].split('\x1f'),b[4].split('\x1f')
                self.assertEqual(len(af),len(bf))
                key=af[0]
                if key.startswith('champ:') and af[1]=='L1' and lane_map.get(key.split(':')[1]):
                    from html import escape
                    af[7]+='<p class="lanes" style="font-size:12px;color:#89939c;margin:5px 0 0"><b>Lanes:</b> '+' · '.join(escape(x,quote=True) for x in lane_map[key.split(':')[1]])+'</p>'
                self.assertEqual(af[:14]+af[15:],bf[:14]+bf[15:])
                self.assertEqual(bf[14],'26.21')
            self.assertEqual(old.execute('select id,nid,did,ord from cards order by id').fetchall(),new.execute('select id,nid,did,ord from cards order by id').fetchall())
        finally:
            old.close(); new.close()

    def test_v4_css_field_order_and_stat_colors_preserved_with_unified_footer(self):
        old,new = read_collection(self.original),read_collection(self.output)
        try:
            a = json.loads(old.execute('select models from col').fetchone()[0])[str(MODEL_ID)]
            b = json.loads(new.execute('select models from col').fetchone()[0])[str(MODEL_ID)]
            for key in ('flds','req','type','sortf'):
                self.assertEqual(a[key],b[key],key)
            old_css=a['css']
            self.assertEqual(old_css,b['css'].replace('.bottom a{color:inherit;text-decoration:none;border-bottom:1px solid #43484e}\n.bottom a:hover{color:#bfb5a5}\n',''))
            self.assertEqual(len(b['tmpls']),1)
            self.assertNotIn('bottom',b['tmpls'][0]['qfmt'])
            self.assertIn('Patch {{Patch}}',b['tmpls'][0]['afmt'])
            self.assertNotIn('Patch',b['tmpls'][0]['qfmt'])
            self.assertIn('League</a> · <a href="{{Wiki}}">Wiki</a>',b['tmpls'][0]['afmt'])
            self.assertNotIn('{{Review}}',b['tmpls'][0]['qfmt']+b['tmpls'][0]['afmt'])
            self.assertNotIn('Priority {{Priority}}',b['tmpls'][0]['afmt'])
        finally:
            old.close(); new.close()
        spec = importlib.util.spec_from_file_location('legacy_builder',self.project.legacy/'build_deck.py')
        legacy = importlib.util.module_from_spec(spec); spec.loader.exec_module(legacy)
        for text in ('AP AD MR HP armor health mana true damage magic damage physical damage','<script>health</script>','Attack Damage\\nAbility Power'):
            self.assertEqual(legacy.format_stats(text),v4.format_stats(text))

    def test_media_package_bytes_match_original(self):
        with zipfile.ZipFile(self.original) as a,zipfile.ZipFile(self.output) as b:
            ma,mb = json.loads(a.read('media')),json.loads(b.read('media'))
            self.assertEqual(set(ma.values()),set(mb.values()))
            da = {name:a.read(k) for k,name in ma.items()}
            self.assertEqual(da,{name:b.read(k) for k,name in mb.items()})

    def test_byte_identical_rebuild_and_idempotent_output(self):
        before = self.output.stat().st_mtime_ns
        result = build(self.project,self.output)
        self.assertEqual(self.result['sha256'],result['sha256'])
        self.assertEqual(before,self.output.stat().st_mtime_ns)
        second = ROOT/'build/tests/pilot-again.apkg'
        build(self.project,second)
        self.assertEqual(self.output.read_bytes(),second.read_bytes())

    def test_integrity_structure_and_coverage(self):
        self.assertEqual(inspect_apkg(self.output)['notes'],64)
        report = validate(self.project)
        self.assertEqual(report['errors'],0)
        self.assertEqual(len(report['champions']),6)
        self.assertEqual(report['media_files'],56)
        missing = [f['id'] for f in report['findings'] if f['code']=='active_gif_missing']
        self.assertEqual(len(missing),4)
        self.assertTrue(all('locke' in key for key in missing))
        self.assertEqual(sum(f['code']=='passive_cue_pending' for f in report['findings']),6)
        self.assertEqual(sum(f['code']=='unverified_mechanics' for f in report['findings']),64)

    def test_identity_vectors_and_future_namespaces(self):
        key = 'champ:ahri:e:recognize:L2'
        self.assertEqual(stable_id(key,2300000000000),2538403411050)
        self.assertEqual(new_key('item',3157,'overview','L1'),'item:3157:overview:L1')
        self.assertNotEqual(guid(key),guid(key+'x'))
        with self.assertRaises(ValueError):
            new_key('item','3157:evil','overview','L1')

    def test_curated_direct_edit_duplicate_content_and_concept_rejected(self):
        data = copy.deepcopy(self.project.content())
        data['cards'][1]['row']['answer'] = 'Changed without review'
        self.assertIn('unreviewed_content',{f['code'] for f in validate(self.project,data)['findings']})
        data['cards'].append(copy.deepcopy(data['cards'][0]))
        codes = {f['code'] for f in validate(self.project,data,False)['findings']}
        self.assertTrue({'duplicate_id','duplicate_content','duplicate_concept'}<=codes)

    def test_missing_media_and_l3_block_export(self):
        data = copy.deepcopy(self.project.content())
        data['cards'][1]['row']['media_path']='media/missing.png'
        codes = {f['code'] for f in validate(self.project,data,False)['findings']}
        self.assertIn('media',codes)
        data['cards'][1]['row']['level']='L3'
        codes = {f['code'] for f in validate(self.project,data,False)['findings']}
        self.assertIn('unsupported_level',codes)

    def test_download_or_status_alone_cannot_approve_mechanics(self):
        data = copy.deepcopy(self.project.content())
        data['cards'][0]['qa_status']='approved'
        codes = {f['code'] for f in validate(self.project,data,False)['findings']}
        self.assertIn('unsupported_qa_approval',codes)

    def test_source_tamper_is_not_a_refresh(self):
        with sandbox_project() as project:
            sources = project.sources(); sources['ability_assets'][0]['description_en']='invented'
            write_json(project.path('sources'),sources)
            self.assertIn('unreviewed_sources',{f['code'] for f in validate(project)['findings']})

    def test_all_original_files_still_match_audit(self):
        for f in read_json(ROOT/'docs/legacy_inventory.json')['files']:
            path = ROOT/f['path']
            # Duplicate fetcher media/cache ZIPs are intentionally omitted in fresh clones.
            if path.exists() or f['path'].startswith('LoL_Anki_Pilot_Project_v4_English/'):
                self.assertEqual(digest(path.read_bytes()),f['sha256'],f['path'])

    def test_path_traversal(self):
        for relative in ('../cards.csv','../../private','media/../../private'):
            with self.assertRaises(ValueError):
                inside(self.project.legacy,relative)


if __name__=='__main__':
    unittest.main()

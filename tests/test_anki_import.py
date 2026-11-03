"""Real Rust-backed Anki importer integration, isolated from user collections."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from helpers import sandbox_project
from lol_anki.io import write_json
from lol_anki.package import build
from lol_anki.project import ROOT, Project
from lol_anki.review import propose, apply_review

HAS_ANKI = importlib.util.find_spec('anki') is not None


@unittest.skipUnless(HAS_ANKI,'Optional Anki runtime missing: install requirements-anki-test.txt into .cache/anki-runtime')
class RealAnkiImportTests(unittest.TestCase):
    def test_lanes_export_reimports_without_duplicates_or_progress_loss(self):
        from anki.collection import Collection, ImportAnkiPackageRequest, ImportAnkiPackageOptions
        import os
        baseline=ROOT/'build/staging/League_Anki_Gesamtstand_BackOnly_2026-11-03.apkg'
        updated=ROOT/'build/staging/League_Anki_Gesamtstand_Lanes_26.21.apkg'
        self.assertTrue(updated.is_file(),'Build the complete lanes APKG before the importer regression')
        with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as temp:
            previous_temp=tempfile.tempdir; old_cwd=Path.cwd(); tempfile.tempdir=temp
            col=None
            try:
                col=Collection(str(Path(temp)/'lanes-collection.anki2'))
                def load(path):
                    result=col.import_anki_package(ImportAnkiPackageRequest(package_path=str(path),options=ImportAnkiPackageOptions(
                        with_scheduling=False,with_deck_configs=False,update_notes=0,update_notetypes=0)))
                    # The headless backend call bypasses the desktop app's cache
                    # invalidation after an import operation.
                    col.models._clear_cache()
                    return result
                load(baseline)
                self.assertEqual((col.note_count(),col.card_count()),(1089,1089))
                note=col.db.first('select id,guid,flds from notes order by id limit 1')
                col.db.execute('update cards set type=2,queue=2,due=(id % 100000)+1,ivl=17,reps=9,lapses=2,factor=2500')
                fields='id,nid,type,queue,due,ivl,reps,lapses,factor'
                before=col.db.all('select '+fields+' from cards order by id')
                identities=col.db.all('select id,guid,mid from notes order by id')
                self.assertNotIn('class="bottom"',col.get_card(before[0][0]).question())
                load(updated); load(updated)
                self.assertEqual((col.note_count(),col.card_count()),(1089,1089))
                self.assertEqual(before,col.db.all('select '+fields+' from cards order by id'))
                self.assertEqual(identities,col.db.all('select id,guid,mid from notes order by id'))
                identity=col.db.first('select id,guid,mid from notes where guid=?',note[1])
                self.assertEqual(identity[:2],note[:2])
                model=col.models.get(identity[2])
                self.assertNotIn('bottom',model['tmpls'][0]['qfmt'])
                self.assertIn('Patch {{Patch}}',model['tmpls'][0]['afmt'])
                self.assertNotIn('League</a>',model['tmpls'][0]['qfmt'])
                self.assertIn('League</a>',model['tmpls'][0]['afmt'])
                self.assertLess(model['tmpls'][0]['afmt'].index('{{#Counterplay}}'),model['tmpls'][0]['afmt'].index('<div class="bottom">'))
                # Check actual Anki rendering, including FrontSide expansion.
                for level in ('L0','L1','L2'):
                    cid=col.db.scalar("select c.id from cards c join notes n on c.nid=n.id where n.flds like ? limit 1",'%\x1f'+level+'\x1f%')
                    card=col.get_card(cid)
                    self.assertNotIn('class="bottom"',card.question())
                    self.assertNotIn('League</a>',card.question())
                    self.assertEqual(card.answer().count('class="bottom"'),1)
                    self.assertIn('Patch 26.21',card.answer())
                l1_ids=col.db.list("select c.id from cards c join notes n on c.nid=n.id where n.flds like ?",'%\x1fL1\x1f%')
                self.assertEqual(len(l1_ids),173)
                for cid in l1_ids:
                    card=col.get_card(cid)
                    self.assertNotIn('Lanes:',card.question())
                    self.assertIn('Lanes:',card.answer())
            finally:
                if col: col.close()
                os.chdir(old_cwd); tempfile.tempdir=previous_temp

    def test_original_new_repeat_and_reviewed_update_preserve_scheduling(self):
        from anki.collection import Collection, ImportAnkiPackageRequest, ImportAnkiPackageOptions
        original = Project()
        output = ROOT/'build/tests/import-pilot.apkg'; build(original,output)
        with sandbox_project() as project:
            # Anki may use its own temp files. Keep them inside this isolated workspace.
            import os
            old_cwd = Path.cwd()
            previous_temp = tempfile.tempdir
            tempfile.tempdir = str(project.root)
            col = None
            try:
                col = Collection(str(project.root/'collection.anki2'))
                def load(package):
                    return col.import_anki_package(ImportAnkiPackageRequest(
                        package_path=str(package),options=ImportAnkiPackageOptions(
                            with_scheduling=False,with_deck_configs=False,
                            update_notes=0,update_notetypes=0)))
                load(original.legacy/'LoL_Anki_Pilot_6_Champions_v4_English.apkg')
                self.assertEqual(col.note_count(),64)
                self.assertEqual(col.card_count(),64)
                card_id = col.db.scalar('select min(id) from cards')
                col.db.execute('update cards set type=2,queue=2,due=123,ivl=17,reps=9,lapses=2,factor=2500 where id=?',card_id)
                fields = 'id,nid,type,queue,due,ivl,reps,lapses,factor'
                before = col.db.first('select '+fields+' from cards where id=?',card_id)
                load(output); load(output)
                self.assertEqual(col.note_count(),64)
                self.assertEqual(col.card_count(),64)
                self.assertEqual(before,col.db.first('select '+fields+' from cards where id=?',card_id))
                candidate = copy.deepcopy(project.content())
                key = candidate['cards'][0]['id']
                candidate['cards'][0]['row']['answer'] += ' Reviewed import test.'
                write_json(project.root/'candidate.json',candidate)
                review = propose(project,project.root/'candidate.json',project.root/'review')
                apply_review(project,project.root/'review/proposal.json',review['accept_token'],'Integration test')
                changed = project.root/'changed.apkg'; build(project,changed)
                result = load(changed)
                self.assertEqual(col.note_count(),64)
                self.assertEqual(col.card_count(),64)
                self.assertIn('Reviewed import test.',col.db.scalar('select flds from notes where sfld=?',key))
                self.assertEqual(before,col.db.first('select '+fields+' from cards where id=?',card_id))
                load(changed)
                self.assertEqual(col.note_count(),64)
                self.assertEqual(len(list((project.root/'collection.media').glob('*'))),56)
            finally:
                if col:
                    col.close()
                os.chdir(old_cwd)
                tempfile.tempdir = previous_temp

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse
from lol_anki.database import INDEX
from lol_anki.project import ROOT
from lol_anki.v4 import CURRENT_PATCH, QFMT, AFMT, TEMPLATE_REVISION, champion_urls, make_model
from lol_anki.package import read_collection
from lol_anki.database import DEFAULT_APKG, lookup
import zipfile


class CardDatabaseAndFooterTests(unittest.TestCase):
    def test_shared_footer_structure_and_fallback_urls(self):
        self.assertEqual(make_model(1)['mod'],TEMPLATE_REVISION)
        previous=read_collection(ROOT/'build/staging/League_Anki_Gesamtstand_Footer_2026-11-03.apkg')
        try:
            old_models=json.loads(previous.execute('select models from col').fetchone()[0])
            self.assertTrue(all(TEMPLATE_REVISION>m['mod'] for m in old_models.values()))
        finally: previous.close()
        self.assertNotIn('bottom',QFMT)
        self.assertIn('Patch {{Patch}}',AFMT)
        self.assertIn('<a href="{{Riot}}">League</a> · <a href="{{Wiki}}">Wiki</a></div>',AFMT)
        self.assertLess(AFMT.index('{{#Counterplay}}'),AFMT.index('<div class="bottom">'))
        self.assertNotIn('{{Review}}',QFMT+AFMT)
        self.assertNotIn('Priority {{Priority}}',AFMT)
        riot,wiki=champion_urls('Aurelion Sol')
        self.assertEqual(riot,'https://www.leagueoflegends.com/en-us/champions/aurelion-sol/')
        self.assertEqual(wiki,'https://wiki.leagueoflegends.com/en-us/Aurelion_Sol')

    def test_complete_export_inventory_is_searchable_and_linked(self):
        path=ROOT/INDEX
        self.assertTrue(path.is_file(),'Build the card inventory after the complete export')
        rows=[json.loads(line) for line in path.read_text('utf-8').splitlines() if line]
        self.assertEqual(len(rows),1089)
        self.assertEqual(len({r['key'] for r in rows}),1089)
        self.assertEqual(len({r['note_id'] for r in rows}),1089)
        self.assertEqual(len({r['guid'] for r in rows}),1089)
        for row in rows:
            self.assertEqual(row['patch'],CURRENT_PATCH)
            self.assertFalse({'content_status','generation_status','review_status','qa_status','media_review_status'} & row.keys())
            for url in row['sources'].values():
                parsed=urlparse(url)
                self.assertEqual(parsed.scheme,'https')
                self.assertTrue(parsed.netloc)
            self.assertIsInstance(row['media'],list)

    def test_source_lookup_resolves_ability_citations_and_archived_blob_paths(self):
        result=lookup(ROOT,'bard','q')
        self.assertEqual(result['count'],1)
        sources=result['cards'][0]['stored_sources']
        self.assertTrue(sources)
        packet=next(s for s in sources if s['path'].endswith('source-packet.json'))
        self.assertTrue(any(x['id']=='wiki:Q' and x['text'] for x in packet['excerpts']))
        self.assertTrue(all((ROOT/x['raw_path']).is_file() for x in packet['resources']))

    def test_current_export_preserves_all_notes_content_and_media_bytes(self):
        baseline=read_collection(ROOT/DEFAULT_APKG)
        updated=read_collection(ROOT/'build/staging/League_Anki_Gesamtstand_BackOnly_2026-11-03.apkg')
        try:
            old=baseline.execute('select id,guid,mid,flds from notes order by id').fetchall()
            new=updated.execute('select id,guid,mid,flds from notes order by id').fetchall()
            previous=read_collection(ROOT/'build/staging/League_Anki_Gesamtstand_Footer_2026-11-03.apkg')
            try:
                self.assertEqual(previous.execute('select id,guid,mid,flds from notes order by id').fetchall(),new)
            finally: previous.close()
            self.assertEqual(len(old),1089); self.assertEqual(len(new),1089)
            for a,b in zip(old,new):
                self.assertEqual(a[:3],b[:3])
                before,after=a[3].split('\x1f'),b[3].split('\x1f')
                self.assertEqual(before[:10]+before[11:12]+before[15:],after[:10]+after[11:12]+after[15:])
                self.assertEqual(after[14],'26.21')
                self.assertTrue(after[12].startswith('https://'))
                self.assertTrue(after[13].startswith('https://'))
                self.assertEqual(set(re.findall(r'src="([^"]+)"',before[10])),set(re.findall(r'src="([^"]+)"',after[10])))
        finally:
            baseline.close(); updated.close()
        old_path=ROOT/DEFAULT_APKG; new_path=ROOT/'build/staging/League_Anki_Gesamtstand_BackOnly_2026-11-03.apkg'
        with zipfile.ZipFile(old_path) as a,zipfile.ZipFile(new_path) as b:
            ma,mb=json.loads(a.read('media')),json.loads(b.read('media'))
            self.assertEqual(set(ma.values()),set(mb.values()))
            self.assertEqual({name:a.read(k) for k,name in ma.items()},
                             {name:b.read(k) for k,name in mb.items()})


if __name__=='__main__': unittest.main()

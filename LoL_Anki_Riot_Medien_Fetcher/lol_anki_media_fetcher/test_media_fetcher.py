"""Offline smoke tests, no Riot requests or actual media required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import media_fetcher as m


class MediaTests(unittest.TestCase):
    def test_safe_relpath(self):
        self.assertEqual(m.valid_rel('champion-abilities/0103/ability_0103_E1.webm',
                                     'champion-abilities/', '.webm'), 'champion-abilities/0103/ability_0103_E1.webm')
        self.assertEqual(m.valid_rel('../../private.webm','champion-abilities/','.webm'), '')
        self.assertEqual(m.valid_rel('https://evil.example/a.webm','champion-abilities/','.webm'), '')

    def test_identification(self):
        idx = [{'id': 'MonkeyKing', 'key':'62', 'name':'Wukong'},
               {'id': 'Ahri', 'key':'103', 'name':'Ahri'}]
        self.assertEqual(m.choose_champion(idx, 'Wukong')['id'], 'MonkeyKing')
        self.assertEqual(m.choose_champion(idx, 'ahri')['key'], '103')

    def test_ahri_manifest_offline(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cache = root / 'cache'
            for path, obj in {
                'ddragon/16.21.1/champion.json': {'data': {'Ahri': {'id':'Ahri','key':'103','name':'Ahri'}}},
                'ddragon/16.21.1/details/Ahri.json': {'data': {'Ahri': {
                    'passive': {'name':'Essence Theft','image':{'full':'Ahri_P.png'}},
                    'spells': [{'name':s,'image':{'full':f'Ahri{s}.png'}} for s in 'QWER'],
                }}},
                'cdragon/latest/103.json': {'passive': {'name':'Essence Theft'},
                    'spells': [{'spellKey':s.lower(), 'name':s,
                                'abilityVideoPath':f'champion-abilities/0103/ability_0103_{s}1.webm',
                                'abilityVideoImagePath':f'champion-abilities/0103/ability_0103_{s}1.jpg'}
                               for s in 'QWER']},
            }.items():
                p=cache/path; p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(json.dumps(obj),encoding='utf-8')
            # Mock actual downloads for test; XML data structure is real.
            from PIL import Image
            import io
            jpg=io.BytesIO(); Image.new('RGB',(64,64),'#285576').save(jpg,format='JPEG')
            png=io.BytesIO(); Image.new('RGB',(64,64),'#285576').save(png,format='PNG')
            def fake_request(url):
                if url.endswith('.jpg'): return jpg.getvalue()
                if url.endswith('.png'): return png.getvalue()
                raise ValueError('Fake video unavailable')
            with patch.object(m.Client,'_request',fake_request):
                # Bind self when mocking the Client method
                pass
            with patch.object(m.Client, '_request', lambda _self, url: fake_request(url)):
                client=m.Client(cache, offline=False)
                p, index=m.build_index(client,'16.21.1')
                cards=m.handle_champion(client,index,'Ahri',p,'latest',root,'mp4',False)
            self.assertEqual(len(cards),5)
            self.assertEqual(cards[0]['preferred_front'],'icon')
            self.assertEqual(cards[3]['preferred_front'],'poster')
            self.assertIn('Ahri', cards[0]['champion'])
            self.assertTrue(cards[3]['front_local'].endswith('_poster.jpg'))
            self.assertEqual(cards[3]['video_source_url'],
                             'https://d28xe8vt774jo5.cloudfront.net/champion-abilities/0103/ability_0103_E1.webm')
            m.save_manifest(root,cards,p)
            self.assertTrue((root/'manifest.csv').is_file())
            self.assertTrue((root/'manifest.json').is_file())


if __name__=='__main__':
    unittest.main()

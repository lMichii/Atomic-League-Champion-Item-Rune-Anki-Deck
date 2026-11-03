import io
import json
import unittest
from unittest.mock import patch
import urllib.error
from helpers import sandbox_project
from lol_anki.cache import Cache
from lol_anki.io import read_json
from lol_anki.sources import fetch

URL = 'https://ddragon.leagueoflegends.com/cdn/16.21.1/data/en_US/champion.json'


class Response(io.BytesIO):
    def geturl(self):
        return URL


class CacheTests(unittest.TestCase):
    def test_cache_resume_corruption_and_offline_miss(self):
        with sandbox_project() as project:
            cache = Cache(project.root/'cache')
            with patch('urllib.request.urlopen',return_value=Response(b'{"data":{}}')) as request:
                data,meta = cache.get(URL)
                self.assertEqual(request.call_count,1)
            with patch('urllib.request.urlopen',side_effect=AssertionError('Unexpected network')):
                self.assertEqual(Cache(cache.root,offline=True).get(URL)[0],data)
                self.assertEqual(cache.get(URL)[1],meta)
            (cache.root/'blobs'/meta['sha256']).write_bytes(b'corrupt')
            with self.assertRaises(FileNotFoundError):
                Cache(cache.root,offline=True).get(URL)
            with patch('urllib.request.urlopen',return_value=Response(b'{"data":{}}')):
                self.assertEqual(cache.get(URL)[0],data)

    def test_bounded_retry_and_permanent_http_error(self):
        with sandbox_project() as project:
            cache = Cache(project.root/'cache')
            with patch('urllib.request.urlopen',side_effect=[urllib.error.URLError('temporary'),Response(b'{}')]) as request,patch('time.sleep'):
                cache.get(URL)
                self.assertEqual(request.call_count,2)
            error = urllib.error.HTTPError(URL,403,'Forbidden',{},None)
            with patch('urllib.request.urlopen',side_effect=error) as request,patch('time.sleep'):
                with self.assertRaises(urllib.error.HTTPError):
                    cache.get(URL,refresh=True)
                self.assertEqual(request.call_count,1)

    def test_html_invalid_asset_size_and_unapproved_host_never_cached(self):
        with sandbox_project() as project:
            cache = Cache(project.root/'cache',max_bytes=30)
            for blob,kind in ((b'<html>error</html>','json'),(b'<html>error</html>','gif'),(b'x'*31,'json')):
                with patch('urllib.request.urlopen',return_value=Response(blob)):
                    with self.assertRaises(ValueError):
                        cache.get(URL,kind)
            self.assertFalse((cache.root/'urls').exists())
            with self.assertRaises(ValueError):
                cache.get('https://example.com/private.json')

    def test_partial_fetch_returns_error_and_preserves_authored_content(self):
        with sandbox_project() as project:
            before = project.path('content').read_bytes()
            with patch.object(Cache,'get',side_effect=FileNotFoundError('Offline miss')):
                report = fetch(project,['Ahri'],'16.21.1',offline=True)
            self.assertEqual(len(report['errors']),1)
            self.assertEqual(before,project.path('content').read_bytes())
            self.assertTrue((project.root/'build/retrieval.json').exists())

    def test_mutable_version_and_mass_runs_rejected(self):
        with sandbox_project() as project:
            for champs,patch_version,cd in ((['all'],'16.21.1',None),(['Ahri'],'latest',None),(['Ahri'],'16.21.1','latest')):
                with self.assertRaises(ValueError):
                    fetch(project,champs,patch_version,cd)

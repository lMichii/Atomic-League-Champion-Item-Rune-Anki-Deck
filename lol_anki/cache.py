"""Atomic content-addressed HTTP cache; interrupted/partial resources can resume."""
import datetime as dt
import json
import logging
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
from .io import atomic, digest, read_json, write_json

LOG = logging.getLogger(__name__)
HOSTS = {'ddragon.leagueoflegends.com', 'raw.communitydragon.org',
         'd28xe8vt774jo5.cloudfront.net', 'wiki.leagueoflegends.com', 'www.leagueoflegends.com'}


def allowed_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in HOSTS or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Expected HTTPS URL on a configured Riot/CommunityDragon/League Wiki host')
    return url


class Cache:
    def __init__(self, root, offline=False, retries=3, timeout=25, max_bytes=40*1024*1024):
        self.root = Path(root)
        self.offline, self.retries, self.timeout, self.max_bytes = offline, retries, timeout, max_bytes

    def get(self, url, kind='json', refresh=False):
        allowed_url(url)
        key = digest(url.encode())
        meta_path = self.root/'urls'/f'{key}.json'
        if meta_path.exists() and (not refresh or self.offline):
            meta = read_json(meta_path)
            blob = self.root/'blobs'/meta['sha256']
            if blob.is_file() and digest(blob.read_bytes()) == meta['sha256']:
                data = blob.read_bytes()
                self.validate(data, kind)
                LOG.info('cache hit %s %s', meta['sha256'], url)
                return data, meta
            LOG.warning('cache corruption/missing blob %s', url)
        if self.offline:
            raise FileNotFoundError(f'Offline cache unavailable or corrupt: {url}')
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'League-Anki-Pipeline/0.1 (local educational project)'})
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    allowed_url(response.geturl())
                    blob = response.read(self.max_bytes+1)
                if len(blob) > self.max_bytes:
                    raise ValueError('Response exceeds configured size limit')
                self.validate(blob, kind)
                sha = digest(blob)
                meta = {'url': url, 'sha256': sha, 'kind': kind, 'bytes': len(blob),
                        'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat()}
                atomic(self.root/'blobs'/sha, blob)
                write_json(meta_path, meta)
                LOG.info('download %s %s', sha, url)
                return blob, meta
            except (urllib.error.URLError, TimeoutError, OSError) as ex:
                LOG.warning('attempt %s/%s %s: %s', attempt+1, self.retries, url, ex)
                if isinstance(ex, urllib.error.HTTPError) and ex.code in (400, 401, 403, 404):
                    raise
                if attempt+1 == self.retries:
                    raise
                time.sleep(0.5 * 2**attempt)
        raise RuntimeError('No request attempts configured')

    @staticmethod
    def validate(blob, kind):
        good = {'png': blob.startswith(b'\x89PNG\r\n\x1a\n'), 'jpg': blob.startswith(b'\xff\xd8\xff'),
                'gif': blob.startswith((b'GIF87a', b'GIF89a')), 'webm': blob.startswith(b'\x1aE\xdf\xa3'),
                'html': b'<html' in blob[:4096].lower() or b'<!doctype html' in blob[:4096].lower()}
        if kind == 'json':
            json.loads(blob)
        elif not good.get(kind, False):
            raise ValueError(f'Invalid {kind} content; resource was not cached')

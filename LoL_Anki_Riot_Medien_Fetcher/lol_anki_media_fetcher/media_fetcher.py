#!/usr/bin/env python3
"""LoL Anki Medien-Fetcher: Riot / CommunityDragon -> local media + manifest.

Usage: python media_fetcher.py --champions Ahri,Ezreal,Blitzcrank,Nautilus,Thresh,Locke
Online access is needed only when fetching assets; cached runs work offline with --offline.

No Riot API key needed. Riot Data Dragon + CommunityDragon are third-party
asset endpoints; all cards still require manual editorial and visual review.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DD = 'https://ddragon.leagueoflegends.com'
CD = 'https://raw.communitydragon.org'
VIDEO_CDN = 'https://d28xe8vt774jo5.cloudfront.net'
DEFAULT_CHAMPS = ['Ahri', 'Ezreal', 'Blitzcrank', 'Nautilus', 'Thresh', 'Locke']
FIELDS = [
    'champion', 'champion_id', 'slot', 'ability_name', 'description_en',
    'preferred_front', 'video_source_url', 'poster_source_url', 'icon_source_url',
    'portrait_source_url', 'video_local', 'poster_local', 'icon_local',
    'portrait_local', 'front_local', 'media_status', 'needs_manual_review',
    'source_version', 'ddragon_patch', 'riot_page', 'notes',
]


def slugify(value: str) -> str:
    ascii_name = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '', ascii_name)


def readable(text: str) -> str:
    cleaned = re.sub(r'<[^>]*>', ' ', html.unescape(text or ''))
    return ' '.join(cleaned.split())


def valid_rel(path: str, prefix: str, suffix: str) -> str:
    """Restrict remote paths to known CDN-relative asset locations."""
    p = (path or '').lstrip('/')
    if not p.startswith(prefix) or not p.lower().endswith(suffix) or '..' in p or '?' in p:
        return ''
    return p


def local_name(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix() if path.is_file() else ''
    except ValueError:
        return ''


class Client:
    def __init__(self, cache: Path, offline=False, refresh=False, timeout=25, max_mb=40):
        self.cache = cache
        self.offline = offline
        self.refresh = refresh
        self.timeout = timeout
        self.max_bytes = max_mb * 1024 * 1024
        self.cache.mkdir(parents=True, exist_ok=True)

    def _request(self, url: str) -> bytes:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'League-Anki-Personal-Study-Deck/0.2 (+local-education)',
            'Accept': '*/*',
        })
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    length = resp.headers.get('Content-Length')
                    if length and int(length) > self.max_bytes:
                        raise ValueError(f'Datei über Größenlimit: {url}')
                    blob = resp.read(self.max_bytes + 1)
                    if len(blob) > self.max_bytes:
                        raise ValueError(f'Datei über Größenlimit: {url}')
                    return blob
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as ex:
                if attempt == 2 or (isinstance(ex, urllib.error.HTTPError) and ex.code in (400, 401, 403, 404)):
                    raise
                time.sleep(0.6 * (attempt + 1))
        raise RuntimeError('download failed')

    def get_json(self, url: str, file_name: str):
        path = self.cache / file_name
        if path.is_file() and (not self.refresh or self.offline):
            return json.loads(path.read_text('utf-8'))
        if self.offline:
            raise FileNotFoundError(f'Offline-Cache fehlt: {path}')
        blob = self._request(url)
        value = json.loads(blob)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        return value

    def get_asset(self, url: str, path: Path, allowed: tuple[str, ...]):
        if not url:
            return False, 'Kein URL'
        if path.is_file() and path.stat().st_size > 150 and not self.refresh:
            return True, 'Cache'
        if self.offline:
            return False, 'Offline: Datei fehlt'
        try:
            blob = self._request(url)
            # CDN may return a HTML error page with HTTP 200.
            lower_head = blob[:400].lower().lstrip()
            if lower_head.startswith(b'<!doctype html') or lower_head.startswith(b'<html'):
                return False, 'HTML statt Medium'
            kind_ok = ('png' in allowed and blob[:8] == b'\x89PNG\r\n\x1a\n') \
                or ('jpg' in allowed and blob[:3] == b'\xff\xd8\xff') \
                or ('webm' in allowed and blob[:4] == b'\x1a\x45\xdf\xa3')
            if not kind_ok:
                return False, 'Unbekanntes Dateiformat'
            if len(blob) < 150:
                return False, 'Medium zu klein'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
            return True, 'Download'
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            return False, f'{type(e).__name__}: {str(e)[:90]}'


def convert_video(source: Path, target: Path, output_type: str):
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        return False, 'ffmpeg fehlt: Icon/Standbild-Fallback'
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_size > 150:
        return True, 'Cache'
    if output_type == 'gif':
        # GIF can get quite big. Prefer MP4 for AnkiMobile / AnkiDroid.
        args = [ffmpeg, '-v', 'error', '-y', '-i', str(source), '-vf',
                'fps=10,scale=480:-1:flags=lanczos', '-an', '-t', '8', str(target)]
    else:
        args = [ffmpeg, '-v', 'error', '-y', '-i', str(source), '-t', '12',
                '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-an',
                '-c:v', 'libx264', '-crf', '28', '-preset', 'veryfast',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(target)]
    try:
        done = subprocess.run(args, capture_output=True, text=True, timeout=120)
        if done.returncode != 0 or not target.is_file() or target.stat().st_size < 150:
            target.unlink(missing_ok=True)
            return False, 'Konvertierung fehlgeschlagen: ' + (done.stderr or '')[-120:]
        return True, 'Konvertiert'
    except (OSError, subprocess.TimeoutExpired) as e:
        target.unlink(missing_ok=True)
        return False, f'{type(e).__name__}: {str(e)[:100]}'


def build_index(client: Client, patch: str):
    if patch == 'latest':
        versions = client.get_json(f'{DD}/api/versions.json', 'meta/versions.json')
        patch = versions[0]
    index = client.get_json(f'{DD}/cdn/{patch}/data/en_US/champion.json', f'ddragon/{patch}/champion.json')
    return patch, list(index['data'].values())


def cdragon_url(version: str, numeric_id: int):
    return f'{CD}/{version}/plugins/rcp-be-lol-game-data/global/default/v1/champions/{numeric_id}.json'


def choose_champion(champs, wanted):
    clean = slugify(wanted)
    for c in champs:
        if clean in (slugify(c['id']), slugify(c['name'])):
            return c
    return None


def safe_riot_page(name):
    # The official champion site uses vanity slugs (not necessarily DDragon IDs).
    overrides = {'monkeyking': 'wukong', 'nunu': 'nunu', 'renataglasc': 'renata-glasc',
                 'missfortune': 'miss-fortune', 'aurelionsol': 'aurelion-sol',
                 'tahmkench': 'tahm-kench', 'drmundo': 'dr-mundo',
                 'xinzhao': 'xin-zhao', 'twistedfate': 'twisted-fate',
                 'masteryi': 'master-yi', 'leesin': 'lee-sin',
                 'jarvaniv': 'jarvan-iv', 'ksante': 'k-sante'}
    key = slugify(name)
    slug = overrides.get(key, re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', name).encode('ascii','ignore').decode().lower()).strip('-'))
    return f'https://www.leagueoflegends.com/de-de/champions/{slug}/'


def handle_champion(client, index, name, patch, cd_version, root, video_format, skip_videos):
    c = choose_champion(index, name)
    if not c:
        print(f'! {name}: nicht im Data-Dragon-Index, bitte Patch prüfen', file=sys.stderr)
        return []
    key = c['id']
    slug = slugify(key)
    cid = int(c['key'])
    try:
        raw = client.get_json(cdragon_url(cd_version, cid), f'cdragon/{cd_version}/{cid}.json')
    except Exception as e:
        print(f'! {name}: CDragon-Details nicht verfügbar: {e}', file=sys.stderr)
        raw = {'passive': {}, 'spells': []}
    try:
        detail = client.get_json(f'{DD}/cdn/{patch}/data/en_US/champion/{key}.json',
                                 f'ddragon/{patch}/details/{key}.json')['data'][key]
    except Exception as e:
        print(f'! {name}: DDragon-Details nicht verfügbar: {e}', file=sys.stderr)
        detail = {'passive': {}, 'spells': []}
    riot_page = safe_riot_page(c.get('name') or key)
    splash_url = f'{DD}/cdn/img/champion/splash/{key}_0.jpg'
    portrait_path = root / 'media' / 'champions' / f'{slug}_portrait.jpg'
    portrait_ok, _ = client.get_asset(splash_url, portrait_path, ('jpg',))
    if not portrait_ok:
        portrait_url2 = f'{DD}/cdn/{patch}/img/champion/{key}.png'
        portrait_path = root / 'media' / 'champions' / f'{slug}_portrait.png'
        portrait_ok, _ = client.get_asset(portrait_url2, portrait_path, ('png',))
        if portrait_ok: splash_url = portrait_url2
    skill_map = {'P': raw.get('passive') or {}}
    for item in raw.get('spells', []):
        slot = (item.get('spellKey') or '').upper()
        if slot and slot in 'QWER': skill_map[slot] = item
    data = []
    for slot in 'PQWER':
        spell = skill_map.get(slot, {})
        dd = (detail.get('passive') or {}) if slot == 'P' else next(iter(detail.get('spells', [])[ 'QWER'.index(slot): 'QWER'.index(slot)+1]), {})
        filename = ((dd.get('image') or {}).get('full') or '')
        icon_cat = 'passive' if slot == 'P' else 'spell'
        icon_url = f'{DD}/cdn/{patch}/img/{icon_cat}/{urllib.parse.quote(filename)}' if filename else ''
        icon_path = root / 'media' / 'abilities' / f'{slug}_{slot.lower()}_icon.png'
        icon_ok, icon_state = client.get_asset(icon_url, icon_path, ('png',))
        vpath = valid_rel(spell.get('abilityVideoPath', ''), 'champion-abilities/', '.webm')
        ppath = valid_rel(spell.get('abilityVideoImagePath', ''), 'champion-abilities/', '.jpg')
        video_url = f'{VIDEO_CDN}/{vpath}' if vpath else ''
        poster_url = f'{VIDEO_CDN}/{ppath}' if ppath else ''
        poster_path = root / 'media' / 'posters' / f'{slug}_{slot.lower()}_poster.jpg'
        poster_ok, _ = client.get_asset(poster_url, poster_path, ('jpg',))
        video_path = root / 'media' / 'videos' / f'{slug}_{slot.lower()}.{video_format}'
        video_ok, note = False, ''
        if slot == 'P':
            note = 'Passive: Icon bevorzugt, Animation optional'
        elif skip_videos:
            note = 'Videos übersprungen'
        elif video_url:
            source_path = root / 'cache' / 'webm' / f'{slug}_{slot.lower()}.webm'
            source_ok, detail_text = client.get_asset(video_url, source_path, ('webm',))
            if source_ok:
                if client.refresh and video_path.is_file() and video_format != 'webm':
                    video_path.unlink()
                if video_format == 'webm':
                    # If available, keep original to avoid recompression (support varies per device).
                    video_path = source_path
                    video_ok = True
                    note = 'Original-WebM: Wiedergabe in Ziel-Anki prüfen'
                else:
                    video_ok, note = convert_video(source_path, video_path, video_format)
            else:
                note = 'Video nicht verfügbar: ' + detail_text
        else:
            note = 'Keine Riot-Videoreferenz'
        if slot == 'P':
            chosen = icon_path if icon_ok else (poster_path if poster_ok else None)
            preferred = 'icon'
        else:
            chosen = video_path if video_ok else poster_path if poster_ok else icon_path if icon_ok else None
            preferred = 'video' if video_ok else 'poster' if poster_ok else 'icon' if icon_ok else 'missing'
        if not chosen: state = 'Nicht verfügbar'
        elif video_ok: state = 'Video heruntergeladen · manuell prüfen'
        elif poster_ok: state = 'Standbild-Fallback · manuell prüfen'
        else: state = 'Icon-Fallback · manuell prüfen'
        data.append({
            'champion': c.get('name') or key, 'champion_id': cid, 'slot': slot,
            'ability_name': spell.get('name') or dd.get('name') or slot,
            'description_en': readable(spell.get('description') or ''),
            'preferred_front': preferred,
            'video_source_url': video_url,
            'poster_source_url': poster_url,
            'icon_source_url': icon_url,
            'portrait_source_url': splash_url,
            'video_local': local_name(video_path, root) if video_ok else '',
            'poster_local': local_name(poster_path, root) if poster_ok else '',
            'icon_local': local_name(icon_path, root) if icon_ok else '',
            'portrait_local': local_name(portrait_path, root) if portrait_ok else '',
            'front_local': local_name(chosen, root) if chosen else '',
            'media_status': state, 'needs_manual_review': 'JA',
            'source_version': cd_version, 'ddragon_patch': patch,
            'riot_page': riot_page, 'notes': note,
        })
    print(f'  {c["name"]}: ' + ', '.join(f'{r["slot"]}={r["preferred_front"]}' for r in data))
    return data


def save_manifest(root: Path, records, patch):
    root.mkdir(parents=True, exist_ok=True)
    (root / 'manifest.json').write_text(json.dumps({
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'ddragon_patch': patch, 'media_review_required': True,
        'ability_assets': records,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    with (root / 'manifest.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter=';')
        writer.writeheader()
        writer.writerows(records)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Download Riot ability media for LoL Anki (icons + videos + portrait).')
    ap.add_argument('--champions', default=','.join(DEFAULT_CHAMPS), help='Kommagetrennte Champions, oder "all"')
    ap.add_argument('--patch', default='16.21.1', help='Data Dragon version, default 16.21.1; latest possible')
    ap.add_argument('--cdragon-version', default='latest', help='CommunityDragon version (latest or e.g. 16.21)')
    ap.add_argument('--output', default='output', help='Zielverzeichnis')
    ap.add_argument('--video-format', choices=('mp4','gif','webm'), default='mp4')
    ap.add_argument('--skip-videos', action='store_true', help='Nur Icons und Standbilder')
    ap.add_argument('--offline', action='store_true', help='Nur vorhandenen Cache verwenden')
    ap.add_argument('--refresh', action='store_true', help='Existierende Dateien erneut laden')
    ap.add_argument('--max-mb', type=int, default=40, help='Limit pro Asset in MB')
    args = ap.parse_args(argv)
    root = Path(args.output).resolve()
    client = Client(root/'cache', offline=args.offline, refresh=args.refresh, max_mb=args.max_mb)
    print(f'Datenquelle: Data Dragon {args.patch}; CommunityDragon {args.cdragon_version}')
    try:
        patch, champs = build_index(client, args.patch)
    except Exception as e:
        print('FEHLER: Champion-Index nicht abrufbar:', e, file=sys.stderr)
        print('Internetverbindung prüfen oder --offline mit gefülltem Cache verwenden.', file=sys.stderr)
        return 2
    names = [c['name'] for c in champs] if args.champions.strip().lower() == 'all' else [x.strip() for x in args.champions.split(',') if x.strip()]
    records = []
    for name in names:
        try:
            records.extend(handle_champion(client, champs, name, patch, args.cdragon_version,
                                           root, args.video_format, args.skip_videos))
        except Exception as e:
            print(f'! Fehler bei {name}: {e}', file=sys.stderr)
    save_manifest(root, records, patch)
    print(f'\nFertig: {len(records)} Fähigkeits-Medienzuordnungen für {len(set(r["champion"] for r in records))} Champions.')
    print(f'Katalog: {root / "manifest.csv"}')
    print('WICHTIG: Die Videos sind technisch vorhanden, aber Gameplay-Stand und richtige Animation sind NICHT automatisch geprüft.')
    return 0 if records else 1


if __name__ == '__main__':
    sys.exit(main())

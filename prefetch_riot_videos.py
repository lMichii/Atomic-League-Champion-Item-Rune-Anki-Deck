"""Prefetch official Riot champion ability previews, without AI or card generation.

Usage:
  python prefetch_riot_videos.py --limit 2
  python prefetch_riot_videos.py
  python prefetch_riot_videos.py --convert-only
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PATCH = "16.21.1"
CDRAGON = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/"
VIDEO = "https://d28xe8vt774jo5.cloudfront.net/"
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "prefetch" / "riot-videos"
MANIFEST = OUT / "manifest.csv"
FIELDS = ("champion", "riot_id", "spell_key", "video_url", "webm_path", "status", "detail")


def request(url, retries=3):
    last = None
    for attempt in range(retries):
        try:
            return urlopen(Request(url, headers={"User-Agent": "LeagueAnkiAssetPrefetch/1.0"}), timeout=30)
        except (HTTPError, URLError, TimeoutError) as exc:
            last = exc
            if isinstance(exc, HTTPError) and exc.code in (400, 403, 404):
                break
            time.sleep(1 + attempt * 2)
    raise last


def json_get(url):
    with request(url) as response:
        return json.load(response)


def valid_rel(path):
    return bool(re.fullmatch(r"champion-abilities/[A-Za-z0-9_/-]+\.webm", path)) and ".." not in path


def write_rows(rows):
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(MANIFEST)


def download(url, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".webm.part")
    try:
        with request(url) as response, tmp.open("wb") as fp:
            while chunk := response.read(256 * 1024):
                fp.write(chunk)
        with tmp.open("rb") as fp:
            if fp.read(4) != b"\x1aE\xdf\xa3":
                raise ValueError("Downloaded content is not a WebM/Matroska file")
        tmp.replace(target)
    finally:
        tmp.unlink(missing_ok=True)


def convert_only():
    import sys
    sys.path.insert(0, str(ROOT))
    from lol_anki.media import gif
    if not MANIFEST.is_file():
        raise SystemExit("No manifest.csv yet. Run a download first.")
    from lol_anki.media import gif  # Existing project conversion implementation
    with MANIFEST.open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    ok = failed = 0
    for row in rows:
        if row["status"] not in ("downloaded", "cached"):
            continue
        source = ROOT / row["webm_path"]
        dest = source.with_suffix(".gif")
        if dest.exists() and dest.stat().st_size:
            continue
        try:
            gif(source, dest)
            ok += 1
            print("GIF:", dest.relative_to(ROOT))
        except Exception as exc:
            failed += 1
            print("GIF FAILED:", source.name, exc)
    print(f"GIF conversion finished: {ok} converted, {failed} failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patch", default=PATCH)
    parser.add_argument("--limit", type=int, default=None, help="Test only first N champions")
    parser.add_argument("--convert-only", action="store_true", help="Convert downloaded WebM clips to GIF using existing lol_anki.media.gif")
    args = parser.parse_args()
    if args.convert_only:
        convert_only()
        return

    roster_url = f"https://ddragon.leagueoflegends.com/cdn/{args.patch}/data/en_US/champion.json"
    roster = json_get(roster_url)["data"]
    champions = sorted(roster.values(), key=lambda x: x["id"].casefold())
    if args.limit is not None:
        champions = champions[:args.limit]
    prior = {}
    if MANIFEST.is_file():
        with MANIFEST.open(newline="", encoding="utf-8") as fp:
            prior = {(r["riot_id"], r["spell_key"], r["video_url"]): r for r in csv.DictReader(fp)}
    rows = dict(prior)
    for i, champ in enumerate(champions, 1):
        name, riot_id = champ["id"], str(champ["key"])
        print(f"[{i}/{len(champions)}] {name}", flush=True)
        try:
            cd = json_get(CDRAGON + riot_id + ".json")
            spells = cd.get("spells", [])
            if isinstance(spells, dict):
                spells = list(spells.values())
            passive = cd.get("passive")
            if isinstance(passive, dict) and passive.get("abilityVideoPath"):
                spells = [dict(passive, spellKey="p"), *spells]
            found = 0
            for spell in spells:
                raw = (spell.get("abilityVideoPath") or "").lstrip("/")
                if not raw:
                    continue
                if not valid_rel(raw):
                    print("  skipped unexpected path:", raw)
                    continue
                key = re.sub(r"[^a-z0-9_-]", "", str(spell.get("spellKey", "unknown")).lower()) or "unknown"
                url = VIDEO + raw
                # Include a short URL hash so distinct variants never overwrite one another.
                suffix = hashlib.sha1(url.encode()).hexdigest()[:8]
                path = OUT / name.lower() / f"{name.lower()}_{key}_{suffix}.webm"
                relative = path.relative_to(ROOT).as_posix()
                record_key = (riot_id, key, url)
                if path.exists() and path.stat().st_size > 4:
                    status, detail = "cached", ""
                else:
                    try:
                        download(url, path)
                        status, detail = "downloaded", ""
                    except (OSError, ValueError) as exc:
                        status, detail = "error", str(exc)
                rows[record_key] = dict(champion=name, riot_id=riot_id, spell_key=key, video_url=url,
                                        webm_path=relative, status=status, detail=detail)
                found += 1
                print(" ", key, status)
            if not found:
                print("  No official ability videos listed")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print("  CHAMPION ERROR:", exc)
            rows[(riot_id, "", "")] = dict(champion=name, riot_id=riot_id, spell_key="", video_url="",
                                             webm_path="", status="error", detail=str(exc))
        write_rows(list(rows.values()))
        time.sleep(0.15)
    print("Finished. Manifest:", MANIFEST)


if __name__ == "__main__":
    main()

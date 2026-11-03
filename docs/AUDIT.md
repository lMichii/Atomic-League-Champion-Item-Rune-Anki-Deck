# Codebase audit — 2026-10-31

Completed before pipeline implementation. `legacy_inventory.json` records all 233
original files (106,637,032 bytes), SHA-256 hashes, archive entries, full Batch 01
scripts/content, workbook cell values, and the SQLite template schema. Original
files are retained. Frozen v4 media and its original APKG are checked into Git for
offline reproduction; duplicate fetcher media/cache archives are inventoried.

## Existing components

| Component | Findings |
| --- | --- |
| v4 `build_deck.py` | Standard-library SQLite/APKG writer, 17 fixed fields, one forward template, explicit model/deck IDs. SHA-1 GUID namespace `lol-anki-pilot-v1:` and SHA-256 numeric note/card IDs must remain unchanged. Exact CSS, inline stat colors, templates and authored strings are the migration contract. |
| `cards.csv` | 64 unique cards: 25 L0 terms, six L1 overviews, 30 L2 recognition cards, three separate L2 hook timers. Pilots: Ahri, Ezreal, Blitzcrank, Nautilus, Thresh, Locke. Six portraits, 20 looping active GIFs, 13 icon fronts, 25 text fronts. Locke Q/W/E/R deliberately use icons; preserve and flag this exception. |
| `prepare_gifs.py` | v4 filter: 8 fps, width 420, Lanczos, 96-color palette, Bayer dither 4, infinite loop; no arbitrary clip truncation. Uses mtime freshness and writes directly to destinations. Supplied GIF bytes should be reused. |
| Media fetcher | Riot Data Dragon metadata/icons/splash; CommunityDragon discovers Riot CDN video paths. Three retries, size/magic checks, offline cache. Default CDragon `latest` is mutable; cache lacks provenance hashes/atomic writes. Partial champion failures can still yield success and replace a manifest. Fallback preference can mislabel passive status. |
| `manifest.csv` / JSON | 30 ability records, semicolon CSV, Data Dragon 16.21.1 versus game label 26.21. Every asset is still manually reviewable; download presence is not QA. Four Locke video URLs reported HTTP 403. Unversioned splash and CDN clips cannot establish patch correctness. |
| Template + supplied APKG | SQLite v11 schema, `lapses` compatibility fix in builder; APKG consists of legacy `collection.anki2`, numbered assets and JSON `media`. Must test SQLite integrity, exact identity mapping, one card per note, media coverage and actual Anki reimport when its optional runtime is available. |
| `sync_excel.py` | Separate spreadsheet mutation tool, fixed sheet/range assumptions, obsolete environment-specific Python artifact dependency; not a portable source of truth. Keep tracker as reference, replace operational dependency with CSV/JSON. |
| Fetcher tests | Three offline tests: path checks, alias selection, mocked Ahri assets/fallbacks. Pillow required only by tests. No package/reimport, duplicate-content, curated-change, or deterministic-build tests. |
| Launchers/READMEs | Independent workflows and duplicate fetcher; no root CLI, configuration, Git, audit log, schema, or protected editorial update flow. |

## Batch 01 and workbooks

Batch ZIP has nine entries, including an identical copy of the fetcher, a 36-row
draft CSV, a 36-row review queue, a source snapshot, two launchers, merger, README,
and production workbook. Proposed additions are Caitlyn, Ashe, Jinx, Leona, Lux,
Morgana. They have **not** been merged or generated.

`prepare_batch.py` replaces existing rows on matching IDs and copies media using
file size comparisons. A one-time CSV backup does not constitute an explicit
change review; reruns can overwrite curated content. Its GIF mode also uses the
fetcher's 10 fps / 480px / eight-second conversion, unlike v4. New pipeline must
require a hash-bound review before editorial changes and retain v4 conversion.

Production workbook: Overview (12 nonempty rows), Cards (37), QA/Media (37),
Card Rules (11). Tracker: ten sheets covering champions, abilities, items, runes,
learning levels/sources, 2,944 nonempty Anki-Karten rows and media/planning sheets.
These include planned work, not 2,944 verified authored cards. Full cell values
are in the inventory. Workbooks are unchanged; CSV remains authored input.

## Data confidence and source verification

Riot documents versioned champion data/assets in
https://developer.riotgames.com/docs/lol#data-dragon . Data Dragon versions and
game patch labels are separate identifiers: preserve both, do not derive one by
string replacement. Existing raw data includes Locke/805; retain this supplied
record rather than guessing from model memory. The audit browser could not
independently retrieve that JSON. League Wiki access was denied by browser robots
rules. Existing links therefore establish intended attribution, **not** verified
patch-specific mechanics. No mechanics or numbers have been corrected automatically.

Missing review evidence: Wiki revision/snapshot and fact-level citations for
authored answers/timers, patch verification for all clips, six optional passive
cues and the four unavailable active GIFs. Preserve original review text and
produce machine-readable warnings. L3 numeric cards must stay blocked until
patch/revision/units/rank/context evidence and human QA exist.

## Main risks

1. GUID/model/field/template changes can duplicate learned notes or break imports.
2. Mutable downloads or automatic prose replacement can silently invalidate cards.
3. Media existence and generic page links do not prove mechanics or visual accuracy.
4. Non-atomic CSV/media/APKG writes and mtime/size caching make interrupted runs unsafe.
5. Timestamp-bearing DB and ZIP output is not byte-reproducible.
6. Legacy batch launchers bypass review; retained only as historical reference.

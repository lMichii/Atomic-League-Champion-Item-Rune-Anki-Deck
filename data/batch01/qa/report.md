# Batch 01 production QA

**100 cards: 64 unchanged pilots + 36 approved Batch 01 additions. Withheld: 0.**

Approval covers source-grounded qualitative learning content and official media suitability after frame review. Current-client, skin, opponent-view and target-device playback checks remain explicit follow-up items. Reviewer: Codex; no human or live-client review is implied.

## Baseline warning classification

| Category | Warning records | Treatment |
| --- | ---: | --- |
| Blocking structural errors | 0 | None found; any new identity/media/schema failure blocks export. |
| Factual review requirements | 73 | 64 missing evidence + 9 editorial/timer QA labels. Retained pilots unchanged; no automatic approval. |
| Media review requirements | 40 | 30 pending media QA + 6 passive cues + 4 Locke active GIF gaps. Still visible. |
| Non-blocking metadata warnings | 31 | 25 general-term labels + 6 hash-pinned CDragon snapshots with unknown upstream release. No claimed verification. |

The 144 records overlap at card level. Full classification: [pilot_warning_classification.json](pilot_warning_classification.json).

## New sources and content decisions

All six official Riot pages, six versioned Data Dragon details, six pinned CommunityDragon records and six Wiki pages were retrieved. Wiki HTML includes revision IDs and is retained byte-for-byte. No unresolved Batch 01 source access failures. Snapshots, source URLs, claims and hashes are in production source/content JSON.

- Lux overview: replaced “across the map” with “long-range”; Final Spark is not presented as global.
- Ashe passive: removed the bonus-damage condition disputed between Riot and Wiki. The card states their shared slow/critical-slow behavior.
- Leona passive: sources disagree on duration; no duration is taught.
- Clarified damage types, Caitlyn Q trap exception, Morgana shield condition and Jinx passive qualifying targets using the archived sources.
- Repaired replacement characters in the supplied draft, retained its 36 IDs, and kept every card in English.
- Counterplay is explicitly marked as a teaching inference from cited mechanics, not an empirical matchup guarantee. Build focus is broad AD/AP/tank-stat orientation, not an optimal-build claim.
- No new cooldown, damage formula, exact scaling or L3 cards.

## Media and passive cues

Real media: **6 splash portraits, 30 ability icons, 24 looping active GIFs, 4 supplementary passive GIFs**. All 30 original WebMs are archived. No new active fallbacks or unresolved active media. The production APKG references **120** real files. Every new image and every GIF frame decoded successfully.

| Passive | Release cue | Required follow-up |
| --- | --- | --- |
| Caitlyn | Icon + official P GIF | Check Headshot readiness indicator and trap/net targeting cues in the current client, at normal card size and with relevant skins. |
| Ashe | Icon + official P GIF | Check slow readability from the opponent's perspective and on different skins. |
| Jinx | Icon + official P GIF | Check the current-client Get Excited! effect and visibility during crowded fights. |
| Leona | Champion-labeled icon; cue unresolved | Review Sunlight target mark before/after an ally consumes it; retain champion-labeled passive icon for this release. |
| Lux | Icon + official P GIF | Check current-client mark appearance, expiry and skin-specific effects. |
| Morgana | Champion-labeled icon; cue unresolved | Review healing feedback with health bars visible in the current client; retain champion-labeled passive icon for this release. |

Caitlyn’s demonstration is included to support Headshot recognition; a precise ready-state glow/color is not asserted. Leona’s mark and Morgana’s healing feedback were not isolated confidently enough to approve supplementary cues. The contact sheets are available in [contact_sheets](contact_sheets/).

Some source WebMs emit Opus audio-header diagnostics. Audio is absent from GIF output; all emitted GIF frames were fully decoded. No diagnostic was silently turned into a media verification claim.

## Card-by-card release register

| Stable card ID | Front | Content decision / unresolved follow-up |
| --- | --- | --- |
| `champ:caitlyn:overview:L1` | portrait | Approved; portrait identity checked; broad build focus and counterplay remain editorial teaching guidance. |
| `champ:caitlyn:p:recognize:L2` | passive icon + GIF | Approved; Check Headshot readiness indicator and trap/net targeting cues in the current client, at normal card size and with relevant skins. |
| `champ:caitlyn:q:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:caitlyn:w:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:caitlyn:e:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:caitlyn:r:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:ashe:overview:L1` | portrait | Approved; portrait identity checked; broad build focus and counterplay remain editorial teaching guidance. |
| `champ:ashe:p:recognize:L2` | passive icon + GIF | Approved; Check slow readability from the opponent's perspective and on different skins. |
| `champ:ashe:q:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:ashe:w:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:ashe:e:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:ashe:r:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:jinx:overview:L1` | portrait | Approved; portrait identity checked; broad build focus and counterplay remain editorial teaching guidance. |
| `champ:jinx:p:recognize:L2` | passive icon + GIF | Approved; Check the current-client Get Excited! effect and visibility during crowded fights. |
| `champ:jinx:q:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:jinx:w:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:jinx:e:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:jinx:r:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:leona:overview:L1` | portrait | Approved; portrait identity checked; broad build focus and counterplay remain editorial teaching guidance. |
| `champ:leona:p:recognize:L2` | icon | Approved; Review Sunlight target mark before/after an ally consumes it; retain champion-labeled passive icon for this release. |
| `champ:leona:q:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:leona:w:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:leona:e:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:leona:r:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:lux:overview:L1` | portrait | Approved; portrait identity checked; broad build focus and counterplay remain editorial teaching guidance. |
| `champ:lux:p:recognize:L2` | passive icon + GIF | Approved; Check current-client mark appearance, expiry and skin-specific effects. |
| `champ:lux:q:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:lux:w:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:lux:e:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:lux:r:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:morgana:overview:L1` | portrait | Approved; portrait identity checked; broad build focus and counterplay remain editorial teaching guidance. |
| `champ:morgana:p:recognize:L2` | icon | Approved; Review healing feedback with health bars visible in the current client; retain champion-labeled passive icon for this release. |
| `champ:morgana:q:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:morgana:w:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:morgana:e:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |
| `champ:morgana:r:recognize:L2` | gif | Approved; Confirm current-client/skin/opponent-view appearance and playback on target Anki device. |

Full changes, per-card media/source hashes, Wiki revision links, conflicts and decisions: [report.json](report.json).

## Validation and reimport

- Structural errors: **0**. Warning records: **212**.
- All 144 inherited records remain. New follow-ups: 36 editorial counterplay labels + 30 current-client visual checks + 2 unresolved passive cues = 68.
- **32 tests passed**, with 0 failures, 0 errors and 0 skips.
- Exact v4 CSS, stat colors, field order, note type and single forward template preserved. Pilot IDs, note fields/revisions and media bytes unchanged.
- Actual Anki 25.9.2 importer: original 64 → 100 → repeated 100. All 64 pilot schedules and 64 test review-history rows preserved; all 120 media files imported. User collection never opened.
- Repeated production builds are byte-identical; no mass expansion beyond Batch 01.
- Headless import and frame/asset checks do not substitute for desktop/mobile GUI playback or current-client gameplay review.

Package: `build/LoL_Anki_Batch_01_100_Cards.apkg`.
SHA-256: `0f5525d460d1b3edfcaa560949884a54fa9fbae4626de2afe93ded5d2fea89d9`.

Applied proposal: `e2f8cac66c6126db7563c688d846df0fc0e61169974ff1df8c0d3d32cbdd61b7`. Only the 36 new IDs were changed; [the receipt](../../content/production.lock.json) records the reviewer and source promotion.

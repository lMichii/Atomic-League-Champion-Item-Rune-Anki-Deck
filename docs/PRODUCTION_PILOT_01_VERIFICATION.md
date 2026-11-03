# Production pilot 01 — 2026-11-01

Completed the first bounded ten-champion batch. **62 new drafts** were retained
and imported with content/media decisions pending. No generated proposal was
applied, no new draft APKG was exported, and no second batch was started.

## Results

| Champion | Drafts |
| --- | ---: |
| Annie | 6 |
| Darius | 6 |
| Garen | 6 |
| Karma | 8 |
| Malphite | 6 |
| Miss Fortune | 6 |
| Orianna | 6 |
| Renekton | 6 |
| Soraka | 6 |
| Warwick | 6 |

Karma's source-addressed Mantra system incorporates its related passive; base and
empowered Q/W/E units have separate recognition purposes. No forced extra passive
or bonus cooldown cards were added. Renekton's empowerment information is taught
within the relevant ability cards; Dominus is represented as a transformation.

- **0 blocking QA errors; 0 duplicate IDs; 262 exact source citations.** Every
  champion has pinned Riot/CDragon data and an identified League Wiki revision.
- **39 GIF fronts, 13 icon fronts and 10 portraits.** Media integrity/dimensions
  and full image/GIF decoding passed. Real media were used throughout.
- **290 nonblocking warnings** remain: 85 media, 190 factual/editorial, ten
  unknown-gameplay-patch metadata findings and five source/coverage findings.
  These include retained conflicts/advanced exceptions and do not constitute
  290 confirmed mechanical errors. They are listed individually, not suppressed.
- Four active/transformation units retain source-matched static fallbacks:
  Karma's Soulflare, Renewal and Defiance, plus Renekton's Dominus. The official
  Dominus slot-clip candidate is retained for manual transformation matching;
  no generic animation is silently assigned to a variant. All clips and passive/
  system cues still require human current-client/skin-specific review.
- Garen W retains a semantic/editorial warning about explaining tenacity for
  beginners. Its required supported cores are present; absent terminology
  evidence was not replaced by an invented definition.

The complete [batch report](../data/batches/production-pilot-01/REPORT.md),
[explicit 62-card list](../data/batches/production-pilot-01/cards.json),
[structured verification](../data/batches/production-pilot-01/verification.json)
and per-champion `qa/` files are retained with the source/media/model archives.

## Recovery and model usage

The run exercised actual recovery: Darius needed bounded content repairs; an
unrelated human Aphelios review was retained; Soraka/Warwick hit provider usage
limits and then resumed from the same frozen inputs. Completed champions were
not regenerated. Counterplay-number feedback was made explicit and validation
feedback now survives a resumed model request. Full failure/repair history remains.

There were **61 new model attempts**, including six attempts without usage
receipts during provider limits. Available receipts report **1,475,547 input
tokens**, 158,549 output tokens and 76,672 cached input tokens. These are provider
reported categories, not a cost estimate; missing usage is not guessed.

An actual `batch-run production-pilot-01 --offline` made **zero new model attempts**,
kept the editorial registry byte-identical and verified completed archive hashes.
`batch-audit` separately rechecked retained sources, contracts, media and coverage.

## Regression and preservation

- **99 automated tests passed**, zero failures/errors/skips, including real Anki
  repeat-import scheduling/review-log preservation in temporary collections.
  Ten focused batch tests also passed after checkpoint portability changes.
- Read-only browser verification passed for **all 62 drafts across all ten
  champions**, with zero POST requests. Front/back media, editable learning text,
  Counterplay, hidden unknown patches and QA-text separation were checked.
- All **106 approved records**, their sources/locks, existing APKGs and frozen
  inputs remained byte-identical. Among 592 pre-existing data/package files, only
  the editorial registry changed: new pending imports and concurrent human reviews
  of three pre-existing Aphelios records. Those human decisions were preserved.
- A separate pilot-only CLI build reproduced the original 64-card SHA-256
  `23a9f0813db46aacae014ed84d7e95ee4d24cd73ee0fff6f318ab84c396ea123`.
  No user's Anki collection or Anki GUI/mobile playback was exercised.

The implementation commit tracks the new batch archives/report and code. Existing
human approved-store/review changes and the combined live registry are preserved
locally rather than folded into the implementation commit. On a separate checkout,
archives can be imported through `editorial-import` and rendered through
`editorial-status`; resuming the saved batch requires its matching protected stores.

## Scaling recommendation

The runner is structurally ready for bounded batches up to 25, but **do not move
directly to 25**. Review these 62 drafts first, resolve the four media bindings and
terminology/source-conflict findings, and assess model quotas and repair cost.
Then trial **15 mostly conventional champions** before considering 20–25. Keep ten
for complex kits until editorial throughput and source/media matching are proven.
The batch review acknowledgment is still unset, so a second plan is blocked.

See [batch commands and workflow](BATCH_PRODUCTION.md).

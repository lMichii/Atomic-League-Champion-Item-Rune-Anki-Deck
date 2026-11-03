# Pilot verification — 2026-10-31

Completed after the foundational pipeline implementation. No Batch 01 merge,
mass card generation, or original-content corrections were performed.

## Results

- **27 tests passed, zero failures/errors/skips** in this environment, including
  the three original fetcher tests, real FFmpeg conversion and real Anki 25.9.2
  import/reimport tests. Machine-readable result: `build/reports/tests.json`.
- All 64 original note IDs, GUIDs, model IDs, rendered fields, tags, field order,
  card IDs/decks and single forward-template behavior match the original APKG.
- CSS, templates, stat colors and all 56 packaged media files match the original
  output. All 20 GIFs contain multiple frames and an infinite loop instruction.
- Repeated builds yield identical bytes and leave identical outputs untouched.
- Original-file hashes match the pre-implementation inventory (all 233 files
  remain present and unchanged in the working project).
- Original → new → repeated new → reviewed answer update → repeat reviewed
  update leaves a real isolated Anki collection at 64 notes/cards and 56 media.
  The reviewed answer changes; existing due/interval/repetition/lapse/ease state
  stays unchanged. No user's Anki profile was opened.
- Online Riot Data Dragon 16.21.1 retrieval succeeded for all six champions
  (including Locke/805), and the same seven resources were retrieved from cache
  offline. Metadata/hashes/URLs are saved in `riot_source_verification.json`.

Final package: `build/LoL_Pilot.apkg`.

SHA-256:
`23a9f0813db46aacae014ed84d7e95ee4d24cd73ee0fff6f318ab84c396ea123`

## Remaining QA

Validation: **0 structural errors, 144 review warnings**. Of these, 64 concern
missing fact-level Wiki revision/patch/snapshot evidence, 64 retain pending
editorial/media QA, six concern unknown legacy CDragon release, six optional
passive cues, and four the inherited Locke active icon fallbacks. See
`build/reports/validation.md` / `.json` for every card-specific finding.

Wiki browser retrieval was robots-blocked; no facts/numbers were inferred to
replace unavailable evidence. Headless importer and GIF structure/conversion
were tested. Visual gameplay correctness and playback in desktop/mobile Anki
interfaces still need human review. Reproducible APKG bytes refer to the same
Python/SQLite/zlib runtime; GIF conversion receipts record the FFmpeg version.

## Deliberate boundaries

The implemented promotion gate handles authored content corrections. New source
releases, media replacements and additional champion source manifests require a
separate reviewed data/code promotion; retrieval and conversion only stage them.
Items/runes have reserved stable identity namespaces; their source adapters,
learning schemas and content are future work. L3 export remains blocked.

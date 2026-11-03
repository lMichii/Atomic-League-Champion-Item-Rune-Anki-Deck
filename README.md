# League Anki pipeline

For GitHub upload size findings, retained dependencies and local-only backup
requirements, see [GitHub preparation](docs/GITHUB_PREPARATION.md).

One Python CLI for source retrieval, media processing, editorial review,
validation and APKG generation. The pilot profile preserves **64 existing English
cards for Ahri, Ezreal, Blitzcrank, Nautilus, Thresh and Locke**. The separate
Batch 01 production profile adds **36 reviewed cards** for Caitlyn, Ashe, Jinx,
Leona, Lux and Morgana, retaining the pilot records unchanged. The original
audit and plan were completed before foundational implementation:
[audit](docs/AUDIT.md), [implementation plan](docs/IMPLEMENTATION_PLAN.md).

## Local editorial review and media replacements (Phase 3.3)

An explicitly authorized repair can target one failed staging champion:
`python pipeline.py staging-batch efficient-03 --repair-champion corki`.
This preserves the preceding failure under the batch's `repairs/` directory and
permits at most one additional author call. Other champions are untouched; a
second repair is blocked. After a failed repair, stop for the user's response
before selecting the next champion. Normal staging runs still skip failures.

```powershell
python pipeline.py editorial-serve
```

Open **http://127.0.0.1:8765**. The workspace contains the six Braum and fourteen
Aphelios drafts, with front/back previews, editable explanations/Counterplay,
evidence, source risks and separate content/media decisions. The dashboard shows
the saved decisions; a card review does not itself promote or export a card.
Replacements accept GIF/PNG or short local MP4/WebM recordings;
imports start pending and bind a stable card or variant identity. Source clips are
converted with the locked v4 GIF recipe. No new AI calls are needed.

Reviewed additions use `--profile editorial`; the original `pilot` and `batch01`
profiles remain frozen. After individual reviews, click **Create proposal for ready
cards**, inspect the cards, IDs, content/source diffs and validation warnings, enter
your reviewer name and explicitly confirm the proposal. **Apply Reviewed Proposal**
uses the exact inspected acceptance hash. Then choose **Build Editorial APKG** and
download the validated package. Review notes are optional; reviewer names and
evidence/media confirmations remain required. Saved proposals can be reopened;
stale proposals must be recreated. No proposal is applied or exported automatically.

[Setup, review and approval commands](docs/PHASE3_3_WORKFLOW.md) ·
[Media tasks](data/editorial/research/aphelios-media-tasks.md) ·
[Phase 3.3 verification](docs/PHASE3_3_VERIFICATION.md)

The [proposal/export UI verification](docs/EDITORIAL_EXPORT_VERIFICATION.md)
documents isolated browser/API tests, optional-notes coverage and baseline checks.

Champion overview backs include lane labels from the archived patch 26.21 ranked
position table in `data/sources/champion-lanes-26.21.json` and its saved HTML.
Only its listed positions are used; Riot champion classes are not treated as lanes.
Future exports read the same mapping, while non-L1 cards remain unchanged.

## Autonomous single-champion drafts (Phase 3)

For explicitly requested author-only staging batches, run
`python pipeline.py staging-batch BATCH_ID` against a saved batch plan. It resumes
saved champions, uses one author call with no repair attempts, skips AI
verification/media inspection, and writes a separate `build/staging/BATCH_ID.apkg`.
Progress, cards, media and failures are under `data/batches/BATCH_ID/`; import status
is separate from generation. `--offline` verifies/rebuilds saved work without model
calls. Failed champions remain logged rather than being retried indefinitely.
This staging export does not approve cards or change the approved stores.
`python pipeline.py export-saved --output build/staging/Gesamtstand.apkg` exports
approved cards and all saved drafts together, with approved content taking precedence
and current editorial edits retained for unapproved notes. It never generates or
approves content. The current pause/inventory is recorded in `data/batches/PAUSED_REPORT.md`.
`--recover-cached` retries saved failed responses using current Python checks and
cached media; it never calls a model. Original responses and unused visual metadata
remain in the receipts. Actual learning text and citations must still validate.

Bounded production batches now have a roster inventory, pinned inputs, resumable
per-champion checkpoints, structural/media QA, immutable archives and pending-only
editorial import. See [batch production](docs/BATCH_PRODUCTION.md). The first
authorized ten-champion pilot is `production-pilot-01`. An explicit subsequent
request authorizes the next ten as `production-pilot-02`, without claiming that
earlier cards were reviewed. Further batches require human review or a new explicit
request. Isolated author-model experiments are documented in
[the model comparison](data/model-evaluations/MODEL_COMPARISON.md); they do not
import cards or change the production model.

```powershell
python pipeline.py generate-champion braum
```

One name, Data Dragon ID or numeric Riot key is the only required per-run input.
The command resolves the current official release, downloads Riot/CDragon media
and Wiki evidence, calls the configured AI author and independent support checker,
and creates a source-backed learning inventory with v4 HTML previews and an additive
proposal. It never approves cards, changes the approved 100-card store, exports
an APKG, or publishes anything. Exactly one champion is accepted per invocation.

Conventional kits retain one L1 + P/Q/W/E/R L2 cards and their existing IDs.
Nonstandard kits use a variable-size inventory of systems, weapons, forms,
stances, transformations, ability variants and conditional effects. Source anchors
and explicit contexts determine identity; neither display wording nor card order
does. A queue indicator is not treated as a combat ability. Aphelios is the only
new Phase 3.2 stress test; no other champions are generated.

```powershell
python pipeline.py generate-champion aphelios
# Resume against the same cached sources, allowing missing media/model calls
python pipeline.py generate-champion aphelios --cached-sources
# Continue a validated author checkpoint after an interruption
python pipeline.py generate-champion aphelios --cached-sources --resume-draft build/generated/aphelios/RUN_ID/draft-checkpoint.json
```

The completed Braum example is retained as **unapproved** draft history:
[current-run index](data/drafts/braum/index.json),
[card previews](data/drafts/braum/8696ff171e68869fcc76/previews/index.html),
[QA report](data/drafts/braum/8696ff171e68869fcc76/QA.md),
[proposed change set](data/drafts/braum/8696ff171e68869fcc76/REVIEW.md).
See [Phase 3.1 verification](docs/PHASE3_1_VERIFICATION.md) for the test results and
remaining content-quality risks.

The completed Aphelios stress test has **14 unapproved drafts** covering 15 source
sections and 28 required cores:
[previews](data/drafts/aphelios/c6569ae4b284ca4203c1/previews/index.html),
[inventory](data/drafts/aphelios/c6569ae4b284ca4203c1/card-inventory.json),
[QA](data/drafts/aphelios/c6569ae4b284ca4203c1/QA.md),
[media review](data/drafts/aphelios/c6569ae4b284ca4203c1/media-report.json).
See [Phase 3.2 verification](docs/PHASE3_2_VERIFICATION.md) and the
[interruption/recovery record](docs/PHASE3_2_RECOVERY.json).

```powershell
python pipeline.py replay-generated-run data/drafts/aphelios/c6569ae4b284ca4203c1
```

### One-time setup

Python 3.11+, FFmpeg/FFprobe on PATH, and either a logged-in Codex CLI or an API
configuration are required. `generation.toml` selects the AI provider, model,
attempt/timeout limits and passive-frame review. It contains no secrets.

- Default `provider = "codex"`: uses `codex exec` with structured output, ephemeral
  sessions, read-only execution and no project instructions. It reuses your CLI
  login; no new persistent chat or champion-specific prompt is required. Model
  tool use is rejected. The runtime default model is recorded as unknown when
  the runtime does not expose its resolved model name; set `ai.model` for an
  explicit model selection.
- `provider = "openai"`: configure `ai.model` and set `OPENAI_API_KEY` in your
  environment. The standard-library adapter uses the official Responses endpoint
  with strict JSON Schema and image inputs. Keys are never written to artifacts.
  This adapter is covered by interface logic; the live Braum run used Codex.

The provider implementation follows the official
[Codex non-interactive documentation](https://learn.chatgpt.com/docs/non-interactive-mode)
and [Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs).

### Deterministic processing and AI authoring

`lol_anki/generation/evidence.py` resolves identifiers and extracts bounded,
versioned evidence. `assets.py` downloads real images/videos, applies the locked
v4 GIF recipe and samples the passive clip. `ai.py` is the only model boundary;
`prompts.py` and `contracts.py` define shared instructions and strict schemas.
No Python branch contains Braum-specific authored prose or per-champion prompts.

Python checks frozen-inventory coverage, fixed questions, identity, stat-focus
vocabulary, exact source quotations, numeric support and schema constraints.
Source packets and saved draft/review records retain numeric Riot handles. At APKG
export, reviewed champion additions use the pinned Data Dragon identifier as a
lowercase slug: `champ:braum:overview:L1`, `champ:braum:p:recognize:L2`, etc.
The exported Key, GUID, note/card IDs and sort/checksum fields all use that readable
key. Existing readable cards (including Morgana), authored content, source mappings
and review receipts remain unchanged. Rebuild the editorial APKG for corrected
exports; the disposable numeric-ID Braum test deck can be deleted before reimport.
The AI supplies concise learning text, priorities, reasons, tentative cue ideas,
conflict analysis and **cooldown topics only**. Counterplay inference is recorded
in structured metadata; cards show only `Counterplay:` and the recommendation.
Internal status/confidence labels are rejected from card-facing prose, including
passive-cue captions. Review statuses and source references stay on the review
dashboard and in QA, outside the v4 card faces.

A separate pre-authoring inventory classifies cited core mechanics, advanced
exceptions (supported/disputed/uncertain), and unsupported claims. Each L2 must
cover every inventory core with answer quotations. Disputed advanced exceptions
cannot justify omitting a supported core; missing coverage triggers repair and
remains a QA failure if unresolved. Braum E therefore includes directional
damage mitigation while detailed damage-source exceptions stay in editorial QA.
An independent model call checks support/coverage; bounded repair passes use that
feedback. Structural/transport failures are retried with logged validation errors.
Failed generation never falls back to canned champion text.

`kit_sources.py` discovers live Wiki ability containers, including extra weapon,
form and variant sections, stopping before pets/history. `kit_contracts.py`
defines the adaptive v2 inventory, typed dependencies, slot roles and explicit
section dispositions. `kit_workflow.py` plans, authors and checks the frozen
inventory. Standard-kit v1 contracts remain available for compatibility.

Variant media is keyed to its actual source unit and context. A generic slot clip
cannot establish a variant animation. `kit_media.py` uses exact primary matches,
versioned CDragon assets or the icon in the matching Wiki ability container.
Unresolved animations use real matched icons and remain media-review findings.
No unrelated image or generic Q clip is substituted. Existing media are unchanged.

Model support checks are fallible. Matching a quotation is not a proof of its
entailment, nor does passing the checker imply complete ability coverage. All
new cards stay `content_status=draft`, `qa_status=needs_review`. Source conflicts,
missing media/evidence, visual uncertainty and omissions remain in QA. The draft
proposal is intentionally rejected by `apply-review`, even with its exact hash.
An editor must review and promote sources/media and create a new ordinary
editorial proposal after any corrections; the generator cannot grant approval.

### Output, history and reproducibility

Each run is under `build/generated/<champion>/<run-id>/` and includes:

- `source-packet.json` and raw snapshots, hashes, URLs, Wiki revision and release IDs;
- real `media/`, GIF recipes, four passive visual evidence frames and asset records;
- `mechanics-inventory.json`, AI requests, structured responses, attempts, receipts
  and independent support results;
- `cards.json` drafts, a `candidate.json` preserving the approved first 100,
  `proposal.json`, `changes.diff`, `QA.md`/`.json`, and v4 `previews/index.html`.

Adaptive runs also include `kit-analysis.json` (actual slot roles, dependencies,
section coverage and source risks) and `card-inventory.json` (each card's purpose,
source identity/context, required cores and advanced exceptions). `qa.json`
records per-card media matching, missing animations, inference types, model call
counts and available token usage. Compact model packets contain source text once,
without raw HTML, download records, media catalogs or duplicated source metadata.
`media-report.json` separates file availability from weapon/ability visual matching.
Source- and identity-bound `draft-checkpoint.json` files are written immediately
after authoring; resumed runs retain a `draft-seed.json` and original model receipt.
Retries append new attempt directories, including available failed-attempt usage.

Adaptive v2 is a draft/review path. Production approval/export gates for the
existing cards remain unchanged; adaptive drafts cannot be promoted automatically.

The run identity includes source/config/prompt/schema hashes, processing source,
v4 contract and FFmpeg version. A changed processor gets a new directory. Fresh
online runs check the current official version and current Wiki snapshot. Riot
CDN demos remain visually unverified; a Data Dragon release is not silently
converted into a live-game patch label. Drafts store `asset_version` separately
from `verified_game_patch` and its verification evidence. Both card faces omit
the patch label when independent verification is absent. The approved v4 model,
templates, CSS, 17 fields and existing 100 cards remain unchanged; draft rendering
only omits optional QA/source/unknown-patch footer fragments.

```powershell
# Replay current cached snapshots/model responses without network or AI calls
python pipeline.py generate-champion braum --offline
# Optional source-only diagnostics
python pipeline.py generate-champion braum --sources-only
# Retain a completed run for review/versioned draft history
python pipeline.py archive-generated-run build/generated/braum/RUN_ID
# Verify the archived inputs and restore their cache for offline replay
python pipeline.py replay-generated-run data/drafts/braum/8696ff171e68869fcc76
```

The archive includes real inputs and recorded model outputs, not a mock response.
It omits model reasoning text. Replay is deterministic for matching processor,
config and FFmpeg versions; fresh AI calls are not promised identical wording.
Across processor versions, a replay gets a new history identity; the preserved
Braum archive still reproduces its learning content, media, IDs and previews.
The explicit archive command only writes unapproved draft history and a latest
draft pointer. It cannot modify approved content or create an APKG.

`python tools/run_tests.py` includes the live-generated Braum archive checks and
offline replay, schema/citation/numeric rejection, repair limits and approval
guards, plus every earlier regression. Optional local-browser verification:
`node tools/check_generation_preview.cjs <run-directory>` uses local Playwright
and a browser; it is not a production dependency.

## Batch 01 production

```powershell
python pipeline.py --profile batch01 run
python pipeline.py --profile batch01 validate
python pipeline.py inspect-apkg build/LoL_Anki_Batch_01_100_Cards.apkg
python tools/run_tests.py
```

The committed sources, real media, content and review receipts reproduce the
**100-card APKG offline**. Output: `build/LoL_Anki_Batch_01_100_Cards.apkg`.
Pilot commands below continue to build the original 64 cards.

[Production QA report](data/batch01/qa/report.md),
[structured per-card QA](data/batch01/qa/report.json),
[baseline warning classification](data/batch01/qa/pilot_warning_classification.json).
No Batch 01 cards were withheld; current-client visual checks and editorial
counterplay inferences remain disclosed follow-ups, not claims of human approval.

The production stores are `data/content/production.json`,
`data/content/production.lock.json` and `data/sources/production.json`.
`pipeline.batch01.toml` adds `data/batch01/media/` as a separate media root; the
frozen v4 folder and pilot content/source stores are unchanged. Existing deck
names/IDs and note type remain the same for import compatibility.

The actual production sequence used the existing fetcher and pinned cache:

```powershell
python LoL_Anki_Riot_Medien_Fetcher/lol_anki_media_fetcher/media_fetcher.py --champions Caitlyn,Ashe,Jinx,Leona,Lux,Morgana --patch 16.21.1 --cdragon-version 16.21 --video-format mp4 --output build/batch01/downloads
python tools/fetch_batch01_passives.py
python tools/archive_batch01_pages.py
python tools/read_batch01_wiki.py
python tools/review_batch01_media.py
# Inspect sources/contact sheets and the explicit editorial_review.json decisions.
python pipeline.py batch01-stage --offline
python pipeline.py --profile batch01 propose data/batch01/candidate.json --output build/batch01/review
# Use the exact reviewed hash printed by propose; never approve a changed proposal.
python pipeline.py --profile batch01 apply-review build/batch01/review/proposal.json --accept PROPOSAL_SHA256 --reviewer "Reviewer name"
python pipeline.py --profile batch01 run
```

That proposal has already been applied and its receipt committed under
`data/reviews/`; do not replay it against the advanced production store. The
candidate preserves all 64 pilot records and only appends the 36 established IDs.
Future content corrections use a copy of **production.json**, not the old candidate.
`batch01-stage` is bounded to the authorized six additions and uses the existing
v4 GIF converter on original WebMs without the legacy MP4's duration cap.

Optional source/contact-sheet review tools use Pillow, already available during
this run. They are not production rebuild dependencies. Full asset decode and
report refresh commands are:

```powershell
python tools/verify_batch01_assets.py
python tools/report_batch01.py
```

These require the relevant run artifacts under `build/`; the committed QA report
and all production inputs are available without re-downloading. The archive step
recorded actual Wiki revision IDs. Source conflicts in Ashe P and Leona P were
resolved by omitting disputed details, not guessing. All 24 active GIFs and four
supplementary passive GIFs are real Riot footage; no placeholder media are used.
Contact sheets and source-stream diagnostics are QA artifacts, not deck media.

## Setup and offline build

Use Python **3.11+**, Git, and this complete checkout. No Python packages, Riot API
key, Anki installation or FFmpeg are needed for rebuilding the supplied pilots.
Frozen v4 media and original APKG are retained in Git; duplicate fetcher downloads
and generated output are ignored. All paths below are relative to the project root.

```powershell
python pipeline.py run
python pipeline.py validate
python pipeline.py inspect-apkg build/LoL_Pilot.apkg
```

Output: `build/LoL_Pilot.apkg`, `build/reports/validation.md`,
`build/reports/validation.json`, `build/pipeline.log`. `run` and `build` validate
first and export only existing authored content. Rerunning identical inputs leaves
an identical APKG and does not replace an unchanged output. Original CSVs,
workbooks, scripts, media and APKGs are never written by this pipeline.

The original 64 IDs, GUIDs, numeric note/card IDs, note type/deck IDs, 17 fields,
single forward template, English prose, stat colors, and native looping GIF
behavior are preserved. No reverse cards are generated. Import with existing-note
updates enabled and scheduling import disabled. The real Anki integration test
checks this flow against an isolated collection; it never opens your collection.

## Data ownership and layout

| Path | Purpose |
| --- | --- |
| `data/content/pilot.json` | Authored learning rows, unchanged v4 strings, stable entity IDs, content/QA statuses, evidence, per-note revision |
| `data/content/pilot.lock.json` | Reviewed content/source hashes, published Anki identity map, review receipts |
| `data/sources/pilot.json` | Separate source versions, numeric Riot entities, 30 ability/media records, original media hashes |
| `data/sources/raw/` | Immutable original Riot/CDragon JSON snapshots, named by SHA-256 |
| `data/reviews/` | Applied proposals, previous content and reviewer receipts (created on explicit review) |
| `.cache/http/` | Resumable downloaded blobs and per-URL metadata, including URL/hash/retrieval time |
| `build/` | Reports, staged new sources/media, proposals, logs and APKGs |
| `docs/legacy_inventory.json` | Every original file hash, archive inspection and read-only workbook cell inventory |
| `LoL_Anki_Pilot_Project_v4_English/` | Frozen visual/identity/media reference, not the new editing workflow |

`python pipeline.py migrate` is the one-time lossless migration command, already
run for this checkout. Complete migrations are no-ops on rerun; a partial store
fails closed rather than overwrite existing content. Original cache timestamps
are unknown and recorded as `null`. CDragon's inherited `latest` has **unknown
release**, pinned by archived byte hash, not falsely labeled as patch 16.21.

Game patch **26.21** and Data Dragon release **16.21.1** are recorded separately.
No code derives one version from the other.

## Retrieve sources without changing cards

```powershell
python pipeline.py fetch --champions Ahri,Ezreal,Blitzcrank,Nautilus,Thresh,Locke --patch 16.21.1
python pipeline.py fetch --champions Ahri,Ezreal,Blitzcrank,Nautilus,Thresh,Locke --patch 16.21.1 --offline
# Optional: explicitly pinned discovery metadata and official media downloads
python pipeline.py fetch --champions Ahri --patch 16.21.1 --cdragon-version 16.21 --assets
```

Retrieval stages structured champion/ability/stats records in
`build/retrieval.json`, with raw bytes in the content-addressed cache. Official
[Riot Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon) is primary.
[CommunityDragon](https://raw.communitydragon.org/) supplies discovery paths for
official Riot CDN ability clips. `latest` is rejected. Source runs accept 1–6
explicit champions; use bounded batches for later source work. This is not a card
authoring command. Per-resource atomic caching makes interrupted runs resumable;
bounded retries handle temporary failures, while permanent errors and missing
data are reported and return a nonzero exit code. `--refresh` stages new snapshots;
it never replaces curated text or frozen assets.

Detailed mechanics/numbers require archived
[League Wiki](https://wiki.leagueoflegends.com/en-us/) evidence. Given a known
revision, archive it with:

```powershell
python pipeline.py archive-wiki --url https://wiki.leagueoflegends.com/en-us/Ahri --revision REVISION_NUMBER --patch 26.21
```

Replace `REVISION_NUMBER` with a real numeric revision. Fetch failures are visible;
no invented fallback facts, revision IDs or verification claims are produced.
Archiving a page is not fact QA. The editor must record the verified patch,
revision, snapshot and precise claim citations. Live Wiki browser access was
blocked during this audit, so inherited attribution links remain unverified.

## Review authored changes explicitly

The examples below edit the pilot profile. For Batch 01 production corrections,
copy `data/content/production.json` and add `--profile batch01` before `propose`,
`apply-review` and `run`; never replace the production store with the older pilot.

1. Copy `data/content/pilot.json` to `build/candidate.json` and edit the copy.
   Keep IDs/entity IDs/row schema unchanged for ordinary corrections. Preserve
   English conventions, short prompts, stat terms and authored counterplay.
2. Generate a proposal and inspect its readable review, full diff and exact JSON:

   ```powershell
   python pipeline.py propose build/candidate.json --output build/review
   ```

3. After reviewing the changes, apply using the exact printed proposal hash:

   ```powershell
   python pipeline.py apply-review build/review/proposal.json --accept PROPOSAL_SHA256 --reviewer "Your name"
   python pipeline.py run
   ```

The apply command is the explicit change-review acknowledgment. It rejects
unaccepted hashes, tampered candidates, stale bases or changed sources, and stores
the reviewed proposal, previous content and receipt. Only changed notes receive
a newer revision, so Anki can update them on reimport without creating new notes.
It never auto-approves gameplay QA. Direct edits to the authored store block builds.
On interruption between atomic content and lock writes, export fails closed; use
the saved `before.json` and Git history to inspect/recover the transaction.

Source/media promotion is deliberately separate from editorial correction in
this foundation. Fetch and conversion only stage proposals. Adding a new source
release/champion/media requires an explicit reviewed code/data change to extend
the pinned source manifest and source lock, with regression tests. There is no
unchecked source-promotion or overwrite command. Do not run the legacy Batch 01
merge launcher as part of the new workflow.

## Media conversion

```powershell
python pipeline.py prepare-media
```

Optional FFmpeg on `PATH` is required only here. Output goes to
`build/proposed-media/`, not the original media folder. Conversion uses the exact
v4 recipe: 8 fps, width 420, Lanczos, 96 colors, Bayer dither scale 4 and infinite
loop, without truncating the original clip. Source hash, filter, FFmpeg version
and output hash form the resumable receipt. Supplied GIF bytes are reused by
normal builds; changing FFmpeg versions cannot silently change those cards.

## Validation and known pilot gaps

Structural failures block export: unreviewed edits, invalid rows/statuses, missing
media, changed hashes, identity collisions, duplicate IDs/concepts/content,
incomplete champion coverage, invalid/passive media or broken APKG references.
Each champion needs exactly one L1 overview and P/Q/W/E/R recognition cards. L0
terminology and three legacy hook timer cards are retained separately.

The baseline has **0 structural errors and 144 review warnings**, grouped as:

| Finding | Count |
| --- | ---: |
| Missing revision/patch/snapshot/claim-level Wiki evidence | 64 |
| Legacy text/media QA pending | 64 |
| Inherited CDragon release unknown | 6 |
| Optional passive visual cue pending | 6 |
| Locke Q/W/E/R missing GIF, inherited icon fallback | 4 |

All warnings retain the card ID and original review text in the report. They are
not claims that the cards are wrong. New active recognition content must use GIFs;
only inherited fallback cards may export with a warning. Passive fronts stay
icon-first with champion names; added passive cues must be explicitly approved.
L3 export is blocked until exact stats have a dedicated patch/rank/units/context
and evidence gate. No new numbers were authored.

## Tests

```powershell
python tools/run_tests.py
# Optional isolated real Anki importer test runtime:
python -m pip install --target .cache/anki-runtime -r requirements-anki-test.txt
python tools/run_tests.py
```

The standard-library suite covers identity/wording/style equivalence, APKG
structure and byte determinism, media references/GIF blocks, duplicates, review
locking, corrupt/offline cache recovery, retries and partial retrieval. FFmpeg
conversion runs when FFmpeg is available. The optional pinned Anki 25.9.2 runtime
tests original import → repeat new imports → reviewed answer update, card counts,
all 56 imported media and preserved scheduling. Optional original fetcher tests
also run when Pillow is installed. Test collections live under `build/tests`.
Missing optional runtimes are reported as skips, not represented as passed tests.

APKG byte reproducibility is guaranteed for identical frozen inputs and the same
Python/SQLite/zlib runtime. Cross-version compression/SQLite changes can affect
bytes; semantic identity tests remain the compatibility contract. New GIF
conversion records FFmpeg version explicitly.

## Complete deck and source inventory

The **item prototype only** is rebuilt with `python pipeline.py item-prototype --offline`.
Its separate export is `build/items-prototype/League_Anki_Items_Prototype_26.21.apkg`:
five L1 items, one QSS L2 and three missing L0 fundamentals. Authored text lives in
`data/content/items-prototype.json`, sources in `data/sources/items-prototype.json`
and its referenced raw snapshots; icons/previews are in `data/items-prototype/`.
The searchable sidecar is `data/database/items-prototype.jsonl`; for example,
`python pipeline.py source-lookup 3140 --raw` returns stored QSS evidence.
League footer links use Riot's pinned item dataset. Existing champion exports and
the champion inventory are preserved. No additional item production is authorized.

The visual-learning revision also includes five **existing** L0 identities (Charm,
Stun, Root/Snare, Knockup and Silence), for **14 test cards total**. Those five and
Stasis reuse six cached Riot gameplay GIFs without conversion. Captions identify
the mechanic; Soraka E distinguishes its silence from its later root. Grievous
Wounds and On-Hit stay text-only because no inspected clip clearly demonstrates
them. No Suppression/Nearsight glossary cards were added. The frozen pilot glossary
store remains untouched; import updates the same glossary GUIDs rather than adding
duplicates. The separate searchable sidecar retains nine prototype entries, since
the other five terms already exist in the main index.

QSS uses four short sections (Cooldown, Can remove, Limitations, Key difference),
grounded in the existing archived QSS excerpt. Optional plain-text `sections` and
`learning_style` rows use `lol_anki/learning_style.py` for shared keyword colors and
section rendering. Existing damage/stat colors, CSS, templates, field order and
Anki identity rules remain unchanged. This presentation is opt-in for future card
families, without changing existing champion fields.

Open `build/items-prototype/previews/index.html` after rebuilding. Generated media,
previews and QA now live beside the separate test APKG under `build/items-prototype/`.
The hash-bound overlay manifest is `data/sources/items-glossary-visuals.json`.
`node tools/check_item_preview.cjs` checks desktop/narrow layouts, visible GIF
animation and source click targets in headless Chromium. See
[prototype verification](docs/ITEM_VISUAL_VERIFICATION.md) for checks and limitations.

The complete 1,089-card APKG is `build/staging/League_Anki_Gesamtstand_BackOnly_2026-11-03.apkg`.
Its back-only footer has an independent template revision so Anki can update old
front-footer templates with “update note types if newer”. If the local template
was edited more recently, select “always” for note-type updates when importing.
The compact searchable index is `data/database/cards.jsonl`; it stores card/note IDs,
text, media references, source links and Patch 26.21 while pointing to existing source
packets and raw snapshots without copying them. Historical review/status records stay
in their original files.
Rebuild the index with `python pipeline.py build-card-index --apkg <package.apkg>`.
Use `python pipeline.py source-lookup bard --ability q` for a card and stored source
summary, or add `--raw` for the retained source files and analyses. Original HTML/JSON
source files remain in `data/sources/raw`, `data/batch01/sources/raw`, `data/drafts/`,
and each batch's `staging/sources` folder.

## Extension workflow

Keep retrieval, authored prose, QA and packaging separate. `lol_anki/` has modules
for cache, sources, media, identity, migration, review, validation, v4 rendering and
packaging. The pilot CLI works directly from checkout; installation is optional.
Its rendering module was mechanically ported by `tools/port_v4_renderer.py`.

Existing published champion IDs never migrate to numeric keys. New entity
references use Riot numeric IDs; `identity.new_key()` reserves stable namespaces
for `champ`, `item`, `rune` and `term`. Extend source adapters/schemas and level
validators before authoring items, runes or L3. Retain one forward template and
the existing note type for compatible cards. Additional champion content must
enter through reviewed candidates. Batch 01 has now been processed under the
separate production profile; no further expansion is automatic. No
mass-generation command is enabled.

Use Git diffs for source/template/schema changes and explicit proposal receipts
for authored changes. Keep the content/source lock and regression tests together.
See [AGENTS.md](AGENTS.md) for implementation guardrails.

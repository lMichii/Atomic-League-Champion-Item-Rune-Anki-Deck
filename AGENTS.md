# Project instructions

- The item prototype request authorizes only five L1 item cards (3157, 3140, 3916,
  3077, 3153), one QSS L2 and the missing Grievous Wounds, On-Hit and Stasis L0s.
  Reuse `python pipeline.py item-prototype --offline`. Keep its APKG and searchable
  sidecar separate from champions. Do not generate more items before user review.

- The user explicitly resumed on 2026-11-02: continue saved batches and remaining
  champions until provider usage limits or every champion has had an attempt.
  Use one author call per champion, NO repairs/retries after content or transport
  errors. Log failures for manual inspection and continue. A provider quota stop
  remains resumable; preserve completed champions and all existing/manual content.
- The preceding run stopped at Senna in `efficient-11`. The user has explicitly
  requested continuation again: resume there with the same single-attempt policy,
  until another provider limit or all champions have had an attempt. Preserve the
  preceding checkpoint/report in `data/batches/SINGLE_ATTEMPT_REPORT.md`.

- The 2026-11-03 continuation finished the pinned 173-champion inventory: 162
  champions have saved cards and 11 failed attempts remain for manual review.
  Do not retry failed champions or start another production pass without a new
  explicit request. See `data/batches/CONTINUATION_REPORT_2026-11-03.md`.

- The explicitly authorized repair pass on 2026-11-03 saved all eleven formerly
  failed champions. All 173 champions in the pinned inventory now have saved
  cards. Human-confirmed metadata/source corrections are retained separately
  from immutable AI receipts. See `data/batches/REPAIR_PASS.md`. No automatic
  approvals or further production passes are authorized by this completion.

## Scope and source of truth

- The subsequent explicit request authorizes one repair attempt for each of the
  eleven failed champions, sequentially. If a repair still fails, stop BEFORE
  attempting another champion and ask the user; wait for their answer. Preserve
  failed inputs and record each repair. This supersedes the preceding no-repair
  rule only for this explicitly authorized pass; it grants no content approvals.

- Read `docs/AUDIT.md`, `docs/IMPLEMENTATION_PLAN.md` and `README.md` first.
- Use `python pipeline.py` as the single operational entry point. Python 3.11+;
  production logic is standard library only. Tests run with `python tools/run_tests.py`.
- Authorized production scope is the 64 frozen pilots plus Batch 01's 36 cards
  (Caitlyn, Ashe, Jinx, Leona, Lux, Morgana). Do not expand beyond these champions
  or mass-generate champion/item/rune content without a new request.
- Phase 3 authorizes a reusable `generate-champion` workflow and Braum as the
  sole new demonstration. Its six cards remain UNAPPROVED drafts. Do not add
  them to production, export them to APKG, or generate other champions during
  this task. Read `docs/PHASE3_PLAN.md` and `docs/PHASE3_VERIFICATION.md`.
- Phase 3.1 presentation/core-coverage verification is in
  `docs/PHASE3_1_VERIFICATION.md`; it supersedes the initial Braum presentation
  and mitigation omission. Earlier draft archives are historical and immutable.
- Phase 3.2 authorizes Aphelios as the sole additional nonstandard-kit draft test.
  Braum and Aphelios remain unapproved. Do not generate Jayce, Nidalee, Elise,
  Hwei or other champions merely because the adaptive schema supports them.
  Read `docs/APHELIOS_ANALYSIS.md`, `docs/PHASE3_2_VERIFICATION.md` and the recovery
  record. Reuse validated checkpoints; do not repeat completed model/source work.
- Phase 3.3 adds a local editorial/media workflow for the existing Braum and
  Aphelios drafts. Read `docs/PHASE3_3_WORKFLOW.md`. Live additions remain unapproved
  until a human explicitly reviews content and media and accepts the exact change
  proposal. Approval simulations and new-note APKG tests belong in temporary
  projects only. Do not publish a new approved-additions APKG during implementation.
- Frozen original scripts, CSVs, workbooks, APKG and media are reference inputs.
  Preserve their bytes. Generated output belongs under `build/`.
- The scalable-production request authorizes `production-pilot-01` only: ten new
  champions selected from the official inventory. Read `docs/BATCH_PRODUCTION.md`.
  Use the batch runner, pinned source/config checkpoints and pending-only editorial
  import. Never overwrite existing work or apply/approve/export generated drafts.
  New batch draft IDs use readable Data Dragon slugs; numeric Riot entity mapping
  remains separate. No second batch until explicit human batch review.
- The subsequent explicit request authorizes `production-pilot-02`, ten further
  eligible champions, and bounded isolated model comparisons. Record continuation
  authorization without inventing prior batch review or approving cards. Keep model
  evaluation outputs separate from the editorial registry and production AI cache;
  do not weaken checks or change the production model based on list prices alone.
- The 2026-11-02 user request supersedes the required AI verifier/editorial-export
  gate for explicitly requested staging batches. Resume pilot-02 first, reuse saved
  text/media, then use author-only generation with at most one repair, deterministic
  citation/schema/media checks and separate staging APKGs. Preserve prior QA/history,
  all approved stores and manual edits. No automatic editorial approval is granted.
  The user's final instruction authorizes further bounded new-champion batches;
  generation progress and Anki import status must remain separate.

## Editorial and identity contract

- `data/content/pilot.json` owns authored English text. Retrieved JSON/raw descriptions
  are separate in `data/sources` and `.cache`; never turn refreshes into automatic prose.
- The separate `--profile batch01` uses `data/content/production.json`, its lock,
  `data/sources/production.json`, and additive `data/batch01/media`. Preserve all
  64 pilot records byte-for-byte in meaning and rendered fields; do not edit the
  pilot store to correct production content. Read `data/batch01/qa/report.md`.
- `--profile editorial` is the reviewed-additions store seeded with the identical
  approved 100-card baseline. Never modify that frozen prefix or its source/media
  records. Use `editorial-propose`, then the existing hash-bound `apply-review`.
- `data/editorial/registry.json` owns protected working text and independent content/
  media decisions. Generated runs stay immutable; regeneration queues suggestions
  and retains editorial edits, reviews and approved media. Never silently rebase.
- The local UI can inspect/apply a proposal and build/download a separate editorial
  export. Require a named reviewer and explicit hash-bound confirmation; notes are
  optional throughout. Keep source/core/media attestations and static-fallback
  consent mandatory. Exercise apply/export only in isolated fixtures while coding;
  preserve the user's live decisions and proposal files. CLI and UI share the same
  validation/apply/build operations and project transaction guard.
- Overrides bind exact card/variant identities and roles (front/icon/passive cue),
  not guessed filenames. Import is pending; only an explicit named matching review
  selects an override. Keep original/converted hashes, recipes, versions and rights
  notes. Reject known generic slot media for a variant; unresolved cases stay tasks.
- Never overwrite curated cards without an inspectable explicit review. Use a copy,
  `propose`, inspect `changes.diff`/`proposal.json`, then explicit `apply-review` with
  exact proposal hash and reviewer. Do not invent user approval or reviewer identity.
- Preserve published keys, GUID namespace, SHA-based note/card IDs, model/deck IDs,
  17 fields/order, stat colors, CSS, single forward template and v4 English conventions.
  New reviewed notes hide optional QA/unknown-patch footers in their own field HTML;
  never modify the shared frozen templates or the original 100 note fields.
- Reviewed champion additions publish readable lowercase Data Dragon slugs at the
  APKG boundary (`champ:braum:q:recognize:L2`). Keep numeric Riot handles in source/
  review stores. Do not rewrite those stores or frozen readable IDs to change export
  naming. The disposable numeric-ID Braum package needs no migration/compatibility.
- No reverse cards. L1: one overview. L2: P icon with champion hint; Q/W/E/R GIF.
  Existing Locke icon exceptions remain flagged. Passive cues need explicit visual QA.
- For nonstandard kits, use source-addressed system/weapon/form/stance/variant/
  conditional learning units, not a forced P/Q/W/E/R grid. Keep explicit context,
  slot roles, source-section dispositions and a pedagogical purpose for every card.
  Preserve ordinary ability/overview IDs. Never infer a variant's clip from its
  generic slot; unresolved animations use source-matched icons with explicit QA.
- Missing sources/revisions, uncertain mechanics, unverified numbers and stale media
  are review findings, never opportunities to guess. Do not upgrade QA because a
  download succeeded. L3 stays blocked pending dedicated fact-evidence validation.
- Keep AI authoring behind `lol_anki/generation/ai.py`; use shared prompts/schemas,
  not champion-specific prose in Python or manually prepared per-champion prompts.
  Preserve exact source/model-output receipts and bounded retries/repair history.
  Never bypass the generated-proposal rejection in `apply-review`.
  Pass structured Counterplay/build-focus inference types to the verifier as
  metadata; they never belong on card faces. Resumed draft checkpoints must match
  the source/inventory hashes and original model receipt. Preserve failed attempts.
- `data/drafts/` stores explicit unapproved run archives, not curated content.
  Model source-support/vision results are fallible and grant no approval. Keep
  Counterplay inference, missing core details, source conflicts and cue uncertainty
  visible in structured QA, never in learning prose. Cards show plain Counterplay,
  with no provenance/confidence/review prefixes. Reject QA labels in card-facing
  text instead of silently stripping them or upgrading factual confidence.
- Keep asset version separate from independently verified gameplay patch and its
  evidence. Hide an unknown gameplay patch label in new draft previews. Do not
  alter the frozen approved v4 model or its card fields to fix draft presentation.
- Freeze a cited core-mechanics inventory before authoring. Require each L2 to
  explain those cores even when advanced exceptions are disputed. Keep disputed
  exceptions and unsupported claims in metadata for editorial review; do not
  invent special cases/numbers. Unbreakable includes supported directional
  mitigation, but no complete exceptions/current-client-VFX verification is claimed.

## Sources, media and reproducibility

- Riot Data Dragon first; League Wiki for detailed mechanics/numbers. CDragon is
  a discovery source, not an official authority on mechanics. Store exact URL,
  source release, game patch, retrieval time (or explicit unknown) and SHA-256.
- Pin releases. Never label legacy `latest` as an immutable upstream version.
- Source/media promotion requires a separate explicit reviewed data/code change
  to manifest/locks and tests; staging alone never grants promotion authority.
- Keep supplied GIF bytes. Proposed conversions use the exact v4 filter in
  `lol_anki/media.py`; cache on content + recipe + FFmpeg version, not mtime/size.
- Atomic writes; content-addressed cache; bounded retries; explicit offline errors.
  Partial retrieval must remain resumable and report failure accurately.
- Do not regenerate frozen inputs to make a regression test pass.

## Required verification

- Run `python tools/run_tests.py` and `python pipeline.py run` for functional changes.
- Real importer test uses a temporary collection only; never open the user's Anki
  collection. Optional runtime setup is in `requirements-anki-test.txt`.
- Existing IDs, full rendered fields, CSS/templates and packaged media must match
  the supplied original APKG. Test duplicate detection, missing/changed media,
  deterministic bytes, review rejection, and repeat import scheduling preservation.
- Record missing optional integration dependencies as skips. Do not claim GUI or
  mobile playback was tested when only the headless importer was exercised.
- Batch 01 approval means source-grounded content and frame-reviewed official media,
  not completed live-client visual QA. Retain current-client follow-ups and the
  two unresolved passive cues. Never claim a Headshot readiness glow was verified.
- Keep audit/validation reports and README workflow accurate. Use Git for code,
  frozen inputs, authored data, source manifests, locks and applied review receipts.

# Bounded champion draft production

Batch production wraps the existing source retriever, standard/adaptive authoring
contracts, media conversion, immutable draft archive and editorial import. It never
calls approval, proposal application or APKG export. All imported content/media
decisions start pending. The v4 templates, stat formatting and approved stores are
unchanged.

## Inventory and first pilot

```powershell
python pipeline.py champion-inventory
python pipeline.py batch-plan production-pilot-01 --size 10 --champions Garen Darius Annie MissFortune Malphite Soraka Warwick Orianna Karma Renekton
python pipeline.py batch-run production-pilot-01
python pipeline.py batch-status production-pilot-01
# After the runner finishes: recheck all retained media/sources without AI
python pipeline.py batch-audit production-pilot-01
```

The inventory is the current official Riot index, reconciled with all approved
profiles, the editorial registry, retained draft indexes, completed generated
outputs and batch reservations. Approved or pending champions are excluded as a
whole, even if their existing cards use a numeric handle or only cover part of a
kit. Explicit selections that are already owned are recorded as skipped; aliases
of the same champion cannot be selected twice. Omit `--champions` to choose the
next eligible entries deterministically. `--size` accepts 1–25, with 10 as default.

The authorized first pilot has ten champions covering ranged damage, melee
fighters, burst magic, tank initiation, healing, ball-position mechanics and
empowered abilities. It excludes the thirteen approved champions (106 cards) and
Aphelios, whose fourteen cards remain under editorial review. The frozen Riot
index has 173 entries at asset release 16.21.1. Release numbers are not treated as
verified gameplay patches.

## Checkpoints and resuming

Run `batch-run` with the **same batch ID** to resume. Completed champions are not
reauthored; archive hashes are checked and missing imports can be restored without
replacing manual edits. Failed/interrupted champions reuse frozen source packets,
media caches and accepted model requests. A saved generation result resumes at QA/
archive/import without another author call. In-flight model work may need a retry;
exact attempts and available usage are retained.

```powershell
python pipeline.py batch-run production-pilot-01
# Offline resume/recheck: no source downloads or model calls
python pipeline.py batch-run production-pilot-01 --offline
```

Each champion has queued/retrieving/generating/validating/completed, failed or
skipped status. The process continues past ordinary per-champion failures, returns
nonzero if any remain, and records bounded diagnostic history. Keyboard interruption
retains the current checkpoint. A dedicated OS lock prevents concurrent runs of
the same batch; short project locks serialize import/review writes. Approved-store
changes stop the batch. Concurrent editorial edits/decisions are recorded and
retained; the runner never rewrites pre-existing working records.

The plan freezes the roster hash, generation configuration, asset release and
approved-store hashes. Each champion also pins its source packet and raw-source
hashes before model work. Changed configuration/sources fail closed. Source-model
receipts and processor identity stay in the run/archive; replay never invents
missing cache entries. Keep these folders when moving the workspace.

## QA and outputs

`data/batches/BATCH_ID/` contains:

- `batch.json`: per-champion checkpoints, attempts, pinned inputs and preservation
  guards; `generation.toml` and `roster.json`: frozen run inputs.
- `REPORT.md` and `report.json`: readable/machine batch summaries, failures,
  source/media coverage, conflicts, missing evidence, manual tasks and usage.
- `cards.json`: explicit list of new draft IDs and whether withheld by QA.
- `qa/CHAMPION.json`: structural, source/citation, core-coverage and real-media
  integrity/decoding findings, separated into errors and review warnings.

Completed runs are archived under `data/drafts/CHAMPION/RUN_ID/` using the existing
archive manifest. Previews, raw sources, exact model receipts, inventories and media
are retained. Blocking QA failures are withheld from editorial import; missing
animations can use genuine source-matched icons with explicit warnings. Unsupported
cores cannot be removed just to hide advanced disputes. All media still needs
human ability/variant/current-client review; a successful decode is not approval.

New batch card keys are readable from creation, for example
`champ:garen:q:recognize:L2`. Nonstandard units preserve their source/context suffix.
Numeric Riot IDs remain in `entity_id` and source/model identity fields. Historical
Braum/Aphelios archives and review handles are not renamed. The existing exporter
also handles readable keys without changing them.

Open `python pipeline.py editorial-serve` and select the new champions. Review the
front/back previews, evidence, factual risks and media in the existing interface.
Learning edits and media overrides remain protected. Individual approvals and
proposal → apply → export stay explicit human actions; see
[the editorial workflow](PHASE3_3_WORKFLOW.md).

## Review gate and future batches

Do not start a second pilot automatically. A new plan is blocked until a human has
inspected the previous batch's report and made an explicit acknowledgment:

```powershell
# Human operator only, after reviewing the batch:
python pipeline.py batch-review-complete production-pilot-01 --reviewer "Your name"
```

That acknowledgment permits planning a later batch; it does not approve any card,
media or source claim. No acknowledgment is fabricated by the generator. Review
the first pilot's actual failures, repair calls, media gaps and editorial effort
before considering 15–25 champions. Larger runs are technically bounded and
checkpointed, but passing structural tests cannot establish editorial capacity.

An explicit subsequent user request can authorize an additional **draft-only**
batch without claiming that the preceding review occurred. Record the exact request
with `batch-plan NEW_ID --authorization "User's explicit continuation request"`.
The previous `batch_review` stays unset and no content/media approvals are granted.
Never use this option to invent continuation authorization.

If a generated result fails blocking QA, ordinary resume revalidates that retained
result without silently spending more authoring calls. After inspecting the failure
and making a source-backed processor/prompt correction, use:

```powershell
python pipeline.py batch-run BATCH_ID --retry-qa
```

This explicitly regenerates only failed results that have not entered editorial
review. It archives the previous result and its failed QA in `superseded_results`,
reuses pinned source checkpoints, and leaves completed/imported work alone. It
cannot run offline or waive a QA blocker. Historical failures remain in the report.

## Comparing author models without changing production

`evaluate-author ARCHIVE --model MODEL --verifier-model MODEL --output FOLDER`
reuses the archive's exact first-pass source/inventory prompt, schema and actual
image inputs. It applies the same citation/content contracts and independently
checks a valid candidate with the chosen verifier. It never imports the candidate
or changes the production model/configuration. Public requests, responses, repair
errors and available token receipts are retained under the output folder; private
reasoning events are excluded. Use `data/model-evaluations/` or `build/` for output.
Reusing a completed experiment folder returns its retained report without new calls.

Compare schema failures, unsupported/omitted cores and repair work alongside tokens.
A lower list price is not evidence that a model is suitable for this deck. Production
batch usage and experiment usage use separate caches and reports; Codex plan usage
must not be presented as a known API invoice.

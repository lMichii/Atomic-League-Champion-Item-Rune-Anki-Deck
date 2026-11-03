# Editorial proposal/export UI verification — 2026-11-01

The local UI now supports a complete, explicit proposal → inspection → apply →
build → download workflow. Business rules remain in the shared `review.py`
inspection/apply checks, `validation.py` and `package.py`; CLI and UI use the same
`run_pipeline` validation/report/build operation. No model calls were required.

## Acceptance and export safeguards

- Proposals use separate immutable working folders. Inspection shows added,
  modified and removed IDs, per-card learning/media diffs, source/full record
  differences, before/after counts and all validation findings.
- Apply requires a reviewer name, explicit confirmation, the exact acceptance hash
  and a current-session inspection token. The underlying source/content/lock,
  editorial-decision, media-integrity and frozen-prefix checks run again at apply.
- Notes are optional everywhere, including replacements, rejections, static
  fallback explanations and final receipts. Names, evidence/core checks, explicit
  media matching/rights acknowledgment and fallback acceptance remain required.
- Per-request identities prevent duplicate successful writes; concurrent project
  operations fail promptly with a conflict. An OS advisory lock covers UI/CLI
  processes and is released automatically if a process exits.
- Build is a separate user action after successful apply. It binds the applied
  store hashes and exports to a proposal-addressed directory under
  `build/editorial/exports`, preserving normal production output files.
- Failed builds remain retryable. Downloads expose only completed recorded exports
  and verify the packaged bytes against their recorded hash.

## Verification

Run the complete suite, including the optional installed browser runtime:

```powershell
$env:LEAGUE_EXPORT_BROWSER_CHECK='1'
python tools/run_tests.py
python pipeline.py run --output build/ui-export/pilot-verification.apkg
```

**87 tests passed, zero failures/errors/skips**, including the installed Anki and
browser integrations. The existing review-page browser fixture check also passed
with intercepted writes, preserving combined approvals, per-card form state,
required reviewer names and explicit fallback messaging. An older card-order
assumption in that browser check was corrected to compare the actual reviewed card.

The isolated HTTP integration approves six archived Braum fixture cards with blank
notes, proposes them, checks readable diffs/warnings, rejects missing names,
confirmation and incorrect hashes, then applies/builds/downloads a 106-card APKG.
It verifies the first 100 records and fixture review registry remain identical.
Additional checks exercise changed decisions, tampered proposal hashes, changed
approved stores, failed builds, duplicate requests and cross-thread/process locks.

The real-browser integration runs against a temporary `build/tests/ed-*` project
only. It checks disabled Apply until confirmation/name, all three explicit actions,
the 106-card build summary and a real APKG download with blank notes. The existing
real Anki importer regression checks repeated import and reviewed edits without
changing existing scheduling or review logs. No user Anki collection is opened;
no Anki GUI or mobile playback verification is claimed.

The pilot CLI verification produced 64 cards, zero errors and the unchanged SHA-256
`23a9f0813db46aacae014ed84d7e95ee4d24cd73ee0fff6f318ab84c396ea123`.

A before/after hash inventory covers **588 pre-existing data, package and live
proposal files**. All remain byte-identical. The live editorial approved store
still contains 100 cards; all six human Braum content/media approvals are intact.
No current live proposal was applied and no live editorial APKG was built. Existing
uncommitted human review/media changes are preserved separately from this code
change. Detailed test/browser artifacts are under `build/ui-export`.

Restart `python pipeline.py editorial-serve` and reload the browser to load the new
page/dispatcher together. The previous live proposal files are retained; create a
fresh proposal through the updated UI to inspect and explicitly accept it.

See [the workflow](PHASE3_3_WORKFLOW.md) for UI steps and the optional CLI equivalent.

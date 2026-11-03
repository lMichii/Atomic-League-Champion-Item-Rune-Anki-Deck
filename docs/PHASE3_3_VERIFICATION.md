# Phase 3.3 verification — 2026-11-01

Implemented a reusable local media/editorial workflow using the existing six
Braum and fourteen Aphelios drafts. No new AI authoring or verification calls,
live draft approvals, mass generation or approved-additions APKG publication were
performed. The live editorial store retains the exact approved 100-card baseline.

## Delivered workflow

- `editorial-init/import/status/serve` initialize the baseline, pin working drafts,
  render v4 previews and show champion-level content/media/fallback blockers.
- The loopback-only UI displays front/back previews, evidence and original QA,
  supports learning text/Counterplay edits, independent approve/reject decisions,
  local media uploads and explicit replacement matching review. Session nonces,
  host/origin checks, record hashes and serialized writes protect review actions.
- Text edits invalidate content approval. Regeneration keeps working edits and
  reviews and queues changed generated suggestions. An actual cached Braum
  generation returned the protected editorial preview with zero imported/replaced
  records and no new model calls.
- Overrides bind an exact stable card or variant identity and an independent
  front/icon/passive-cue role. Pending files cannot replace approved selections.
  Exact card overrides precede variant overrides, reviewed source media and static
  fallbacks. Known generic Q hashes and null variant identities are rejected.
- GIF/PNG and short local MP4/WebM inputs retain immutable originals, hashes,
  source/version/licensing notes, decode/dimension checks and review/selection
  history. Videos use the locked v4 GIF recipe. Passive animation remains a
  supplementary cue rather than replacing the passive icon.
- Content review attests claims/required cores/inference types against retrieved
  evidence; media review binds every front/icon/cue byte. Static exceptions need
  explicit reasons and remain validation warnings. Unknown gameplay patches stay
  hidden; rights clearance remains a separate distribution review.
- `editorial-propose` stages selected ready cards and coupled source/media
  provenance. The existing `apply-review` requires the exact proposal hash and
  reviewer, rejects stale decisions/selections and preserves the frozen prefix.
  Raw generated `champion_draft` proposals remain ineligible for approval.
- `--profile editorial run` is the normal build path after explicit acceptance.
  It includes only approved additions. Partial champion sets and multiple Q
  variants are supported without adding unapproved siblings.

The shared v4 CSS, templates, 17 fields, forward-template count, model/deck IDs,
identity algorithms and stat formatter are unchanged. New reviewed notes control
optional footer visibility in their own field HTML; all original note fields and
media remain unchanged. No user Anki collection was opened.

## Media investigation and open tasks

The [research report](../data/editorial/research/aphelios-media-tasks.md) retains
source hashes and references from Riot's primer, pinned CommunityDragon metadata,
the archived Wiki and Riot's official Champion Spotlight. The primer exposes
diagrams, CDragon exposes a generic Q demo, and the retained Wiki has no ability
GIF/MP4/WebM links. The longer Spotlight is a reference candidate requiring exact
timestamps, visual matching and rights review; it was not downloaded or assigned.

Five Q tasks remain open with real matched icons:

- Moonshot / Calibrum
- Onslaught / Severum
- Binding Eclipse / Gravitum
- Duskwave / Infernum
- Sentry / Crescendum

Supplementary Moonlight Vigil demonstrations remain open for **all five weapons**:
Calibrum, Severum, Gravitum, Infernum and Crescendum. The generic base-cast clip does
not independently establish their visual effects. Passive cues, current-client/
skin-specific appearance, unknown gameplay patches and distribution rights remain
explicit manual-review concerns. No invented animation or generic Q substitution
was used.

## Tests and results

- **79 regression tests passed**, zero failures/errors/skips. A subsequent focused
  partial-approval check also passed after adding explicit static-fallback warnings.
- New tests exercise pending/approved override precedence, exact variants and
  roles, generic-Q rejection, corrupt/changed media, local MP4 conversion, protected
  manual edits/regeneration, partial approvals, stale proposals, loopback API
  authorization and real Anki reimports.
- Isolated temporary projects approved three real-media fixture cards, built a
  103-card APKG, reimported twice, then edited/reviewed/reimported an added card.
  All original 100 note fields and model properties stayed identical. Scheduling
  and review logs were preserved for the original 100 and then all 103 studied
  fixture cards. These simulated reviewers/approvals were confined to temporary
  projects; none entered the live registry/store.
- Two Q variants could be approved independently while the rest of the champion
  stayed excluded. Missing animation exceptions remained explicit warnings.
- Real-browser checks passed for all **20** editorial previews, without any POST,
  edit or approval request. The production-field probe confirmed unknown patch/QA
  footers stay hidden with the frozen shared templates. The review dashboard was
  visually inspected; browser rendering is not mobile/live-client visual QA.
- The required pilot and Batch 01 CLI builds completed with unchanged hashes:

| Approved package | Cards | SHA-256 |
| --- | --- | --- |
| LoL_Pilot.apkg | 64 | `23a9f0813db46aacae014ed84d7e95ee4d24cd73ee0fff6f318ab84c396ea123` |
| LoL_Anki_Batch_01_100_Cards.apkg | 100 | `0f5525d460d1b3edfcaa560949884a54fa9fbae4626de2afe93ded5d2fea89d9` |

The editorial baseline validates with zero errors; its inherited **212 warnings**
remain visible. Live readiness is **0/6 Braum and 0/14 Aphelios**, with zero approved
overrides. The normal approved-additions output has not been built in the live
workspace. Model author/verification calls for this phase: **0**.

## Operator entry points

- [Workflow and explicit approval commands](PHASE3_3_WORKFLOW.md)
- [Local editorial registry](../data/editorial/registry.json)
- [Media override registry](../data/editorial/overrides.json)
- [Structured manual media tasks](../data/editorial/research/aphelios-media-tasks.json)
- Local review UI: http://127.0.0.1:8765 (`python pipeline.py editorial-serve`)

Editorial source versions remain pinned. Adopting a new source/game revision is a
separate explicit migration, not an automatic rewrite of manual content.

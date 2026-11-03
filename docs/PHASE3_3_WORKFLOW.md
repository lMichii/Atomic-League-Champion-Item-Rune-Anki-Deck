# Local editorial and media workflow

The approved 100-card baseline remains unchanged. `editorial` is a separate approved
store that starts with those exact 100 records and can accept explicitly reviewed
additions. The imported six Braum and fourteen Aphelios cards are working drafts;
importing, editing, generating previews or proposing changes grants no approval.

## Start and review

```powershell
python pipeline.py editorial-init
python pipeline.py editorial-import data/drafts/braum/8696ff171e68869fcc76
python pipeline.py editorial-import data/drafts/aphelios/c6569ae4b284ca4203c1
python pipeline.py editorial-serve
```

Open http://127.0.0.1:8765. The service binds only to loopback. Requests require the
current review session and displayed record revision; cross-origin/stale writes
are rejected. Do not expose the local review service through a public tunnel.

Choose a card, use its front/back button, and inspect the evidence and original
generation QA. Save explanation/Counterplay changes without changing the card ID.
Source assertions, inferred guidance, source conflicts and visual uncertainties
remain separate from learning prose. Unknown game patches are hidden.

Content approval requires a named reviewer, selected retrieved
evidence and explicit checks of claims, required cores, inference types and source
warnings. Edited quantities must occur in the cited excerpts. Every semantic claim
still needs human judgment; these checks do not prove entailment. Review notes are
optional for content/media approvals, rejections, replacements and final acceptance/
export. Missing or short notes are never structural validation failures. Editing learning
text invalidates content approval. Rejection retains the working text/history.

Media approval is independent: inspect the actual files and exact ability/weapon/
form, acknowledge source/rights notes, and explicitly accept a static fallback
when an animation is unresolved (explanatory notes are optional). A media change makes the previous
media fingerprint stale. Approval of an individual replacement does not approve
the rest of the card's media or its content.

The champion summary shows remaining blockers. Current selections and decisions
are separate from the immutable original-generation warnings; new replacements
do not erase the historical QA record.

## Media overrides

Priority, within each media role:

1. Explicitly approved card override, then an exact variant override.
2. Source-matched Riot/CommunityDragon/Wiki media with a valid media review.
3. Matched static fallback, with an explicit exception/warning.

Unreviewed source files can be previewed as candidates, but cannot be promoted
without media approval. Pending overrides never replace approved selections.
Targets use a stable card ID or `{entity_id, subject_id, context_id, slot}`. A
variant cannot match a conventional card with no variant identity. Known generic
Q media hashes are rejected for weapon variants even if the file is renamed.

Roles are `front`, `icon` (PNG answer icon), and `cue` (supplementary passive
visual). Passive GIF/video front imports become supplementary cues, preserving
the passive icon. PNG screenshots can use the existing large ability visual style.
Role-specific replacements can coexist. Approving a different replacement changes
the selection explicitly and preserves earlier objects/review history.

Uploads/CLI imports accept GIF, PNG, MP4 and WebM. Use an ability-length recording
at most 120 seconds and 100 MiB. Video converts to the existing 8 fps/420px,
96-color, infinitely looping v4 GIF recipe; GIFs are preserved rather than silently
re-encoded. Inspection checks signatures, dimensions (16..4096), full decoding
and GIF animation/looping. Invalid, changed or ambiguous media fails closed.

Original files, output hashes, conversion recipe/runtime, source/capture details,
asset/recording version, reviewer, selection history and licensing notes are kept
under `data/editorial`. Source recordings are not embedded as MP4 in Anki. Source
attribution is not distribution clearance; rights review remains explicit metadata.

Example metadata for a local file (replace the descriptive values):

```json
{
  "origin": "local_recording",
  "source": "Your recording date, champion, weapon and demonstrated action",
  "rights_holder": "Recorder attribution and relevant upstream game rights holder",
  "license_reference": "Permission/policy reference and any limitations",
  "asset_version": "unknown",
  "distribution_status": "pending",
  "display_role": "animation"
}
```

```powershell
python pipeline.py editorial-media-import "champ:523:ability_variant:q:moonshot:calibrum:recognize:L2" "my-moonshot.mp4" --metadata media-source.json --variant --role front
# Only after inspecting that exact replacement:
python pipeline.py editorial-media-approve "champ:523:ability_variant:q:moonshot:calibrum:recognize:L2" --override OVERRIDE_ID --reviewer "YOUR_NAME" --notes "Describe how the recording demonstrates this exact variant."
```

The browser upload offers the same import/replacement review flow. Content/media
decisions can also be submitted through `editorial-review CARD_ID decision.json`;
the JSON uses the same explicit action/status/reviewer/notes and attestation fields
as the local API. Never fabricate a reviewer or an approval decision.

## Promotion and APKG after human approval

Create a proposal for selected ready cards from the browser, or use the CLI. Partial
champion approval is supported; pending/rejected cards stay out of the store/APKG.
The frozen first 100 records and their source/media records cannot change.

```powershell
python pipeline.py editorial-propose --ids "champ:201:q:recognize:L2" --output build/editorial/review
```

Inspect `proposal.json`, `changes.diff` and `sources.diff`. They bind the content,
source snapshots, media hashes and current editorial decisions. The generated
`champion_draft` proposal remains rejected. Only the newly reviewed additive
proposal can proceed through the established final change-review mechanism.

### Complete browser workflow

1. Click **Create proposal for ready cards** for the selected champion. The proposal
   panel lists added/modified/removed IDs, before/after learning text and media paths,
   card counts, validation findings and links to full record/source differences.
   Creating or inspecting a proposal does not alter the approved store.
2. Inspect those changes and warnings. Enter a reviewer name, optionally add notes,
   then check the explicit confirmation. **Apply Reviewed Proposal** is enabled only
   after confirmation and successful validation. It calls the same hash-bound
   `apply-review` implementation as the CLI; it cannot bypass current locks, source/
   media hashes, editorial decisions or frozen-baseline checks.
3. After successful apply, click **Build Editorial APKG**. This calls the same
   validation/report/build operation as `--profile editorial run`, with a dedicated
   output under `build/editorial/exports/<proposal-sha>/LoL_Reviewed_<count>.apkg`.
   It never overwrites the pilot/Batch 01 packages or the default CLI export.
4. Inspect output counts, validation/integrity status, full path and file hash;
   use **Download Editorial APKG**. Only recorded completed exports can be downloaded;
   changed file bytes fail the download integrity check.

Saved UI proposals/exports are listed in the panel and retained under
`build/editorial/workflow/`. Restarting the server requires fresh inspection before
accepting an unapplied proposal. A failed build leaves the applied proposal retryable.
If the approved store changes after apply, export is blocked until a fresh proposal
is inspected/applied; do not restore old content to defeat that check. Conflicting
operations fail promptly rather than queue. A shared OS lock serializes local UI
and CLI review/build writes; a server session also rejects duplicate/stale requests.
Review data is preserved when the server is restarted after an update.

The CLI remains available for the human operator **after** explicit inspection:

```powershell
python pipeline.py --profile editorial apply-review build/editorial/review/proposal.json --accept EXACT_PROPOSAL_SHA256 --reviewer "YOUR_NAME"
python pipeline.py --profile editorial run
python pipeline.py inspect-apkg build/LoL_Reviewed.apkg
```

Applying advances only changed note revisions and updates the content/source lock
with a receipt and before-snapshots. Stale proposals, changed selections, modified
files or changed decisions fail. A crash between atomic files fails closed through
the lock; before-snapshots support recovery. Package building does not contact AI.

The approved additions keep the existing model/deck identities, 17 fields, single
forward template, CSS, stat colors and GIF behavior. Optional metadata visibility
is controlled in new notes' field HTML; shared templates and original fields are
unchanged. APKG builds contain only approved cards and referenced media.

## Regeneration and preserved edits

The registry pins the working text and source run. Regenerating an imported
champion queues a different generated revision rather than replacing edits,
reviews or approved overrides. The CLI points to the protected editorial preview
and retains a separate link to raw generation history. Adopting new source/game
versions requires explicit editorial migration, not an automatic rebase.

```powershell
python pipeline.py generate-champion braum --offline
python pipeline.py editorial-status
python pipeline.py editorial-media-tasks
```

Historical archive replay remains faithful to the original generated record. It
does not rewrite the editorial workspace or approvals. The actual regeneration
path and isolated tests exercise manual-edit preservation without new model calls.

## Current manual tasks

The [media task report](../data/editorial/research/aphelios-media-tasks.md) identifies
five unresolved weapon-specific Q animations and supplementary Moonlight Vigil
demonstrations for Calibrum, Severum, Gravitum, Infernum and Crescendum. The current
official primer exposes diagrams; pinned CommunityDragon metadata exposes a generic
Q; the archived Wiki page exposes no ability animation files. Riot's official
Champion Spotlight is a longer reference candidate requiring exact timestamps,
visual matching and rights review. It has not been downloaded or assigned.

All five Q cards retain real matched icons. No generic Q clip or invented animation
is substituted. Passive cues and current-client/skin-specific visuals also remain
manual review requirements. No live Braum/Aphelios approval or new approved-additions
APKG was created against the live store during implementation. New author/verification model calls: **0**.

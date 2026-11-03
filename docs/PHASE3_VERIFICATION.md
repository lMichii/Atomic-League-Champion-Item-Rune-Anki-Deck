# Phase 3 verification — 2026-10-31

Historical Phase 3 results. The card presentation and Unbreakable completeness
gap below are superseded by [Phase 3.1 verification](PHASE3_1_VERIFICATION.md).
The linked earlier archives remain intact as unapproved history.

Implemented `python pipeline.py generate-champion braum` and ran live source
retrieval, genuine Riot media conversion, AI authoring, independent source-support
checking and automatic feedback repair. No manually authored Braum prompt or
card text was supplied. Both shared provider prompts work from the evidence packet.

## Results

- Exactly **six UNAPPROVED drafts**: one L1 overview and P/Q/W/E/R L2 recognition.
- Latest observed Riot Data Dragon release **16.21.1**, pinned CommunityDragon
  **16.21**, Wiki revision **4022592**; all five ability evidence sections found.
  The live-game patch label is intentionally unknown, not inferred from CDN numbering.
- Real media: one splash portrait, five icons, four active GIFs and a tentative
  passive-demo GIF. Four real passive frames were supplied to both model stages.
- Priorities: L1/P/Q/E/R A, W B, each with a gameplay reason. E/R cooldown topics
  are high priority; W/Q are secondary topics. **No timer/extra cards created.**
- Every factual answer clause has source quotations checked against retrieved
  excerpts; numeric claims are checked for a matching supported number. Counterplay
  and build focus are marked as inferred teaching guidance.
- The final configured run recorded **two author/support-check passes**: one
  flagged card after the first pass, zero flagged cards after automatic repair.
  This is fallible AI source-consistency assessment, not complete editorial QA.
- Exactly 100 existing approved records remain at the start of the proposed
  106-card candidate. Approved content/source/lock hashes are unchanged.
- Numeric entity-based IDs (`champ:201:...`) are assigned in Python and remain
  independent of patch, prose and input spelling/case.
- Six v4 HTML previews rendered successfully in an isolated real browser: all
  local media loaded, the frozen background/style was present, and front/back
  controls worked. The passive cue is prominently labeled unapproved.
- **45 tests passed**, zero failures/errors/skips, including the prior actual
  Anki import/reimport and study-progress tests, strict AI contracts, retries,
  citation/numeric rejection, exact draft coverage, real media references, approval
  rejection, and byte-identical offline content/proposal/preview replay.
- The 64-card APKG remains SHA-256
  `23a9f0813db46aacae014ed84d7e95ee4d24cd73ee0fff6f318ab84c396ea123`.
- The 100-card APKG remains SHA-256
  `0f5525d460d1b3edfcaa560949884a54fa9fbae4626de2afe93ded5d2fea89d9`.

No new APKG was created for Braum, no review was applied, no existing card was
edited and no content was published. The generated-proposal kind is rejected by
`apply-review` even when supplied with its exact proposal hash.

## Review artifacts

- [Current unapproved-run index](../data/drafts/braum/index.json)
- [Six card previews](../data/drafts/braum/dca12fd8e32ff8f42b90/previews/index.html)
- [Structured QA](../data/drafts/braum/dca12fd8e32ff8f42b90/qa.json)
- [Readable QA](../data/drafts/braum/dca12fd8e32ff8f42b90/QA.md)
- [Proposal / review instructions](../data/drafts/braum/dca12fd8e32ff8f42b90/REVIEW.md)
- [Additive content diff](../data/drafts/braum/dca12fd8e32ff8f42b90/changes.diff)

The preceding retained draft archive documents the same content before the
processing/runtime fingerprint was added. The index selects the current archive.
Existing archives are not rewritten when the processor changes.

## Remaining factual and visual risks

The source descriptions of Unbreakable contain broad statements alongside more
specific projectile/damage-source exceptions. The final E draft conservatively
omits its damage-mitigation details instead of inventing an overbroad rule. That
is a **content-completeness gap requiring editorial review**. Passing the AI
support checker does not make the E card complete or approve its omission.

The passive marker/stack association is only a tentative visual proposal. No
current-client, skin-specific, opponent-view or mobile Anki playback check was
performed. Wiki excerpts include mode-specific and unrelated material that the
prompts instruct the model to exclude; extraction/AI mistakes remain possible.
General Counterplay is inference, not measured matchup advice or a guarantee.

The default live run used the authenticated Codex CLI in ephemeral/read-only mode,
with structured JSON and no model tool use. The runtime does not expose the exact
resolved default-model name, so the receipt records that uncertainty. An explicit
model can be configured. The alternative OpenAI Responses adapter is implemented
but was not used for the live demonstration; it requires a separately configured
API model/key. No credentials are retained in the archive.

Pinned source/model-output replay is reproducible with matching processor/config
and FFmpeg; a fresh model call or changed upstream evidence can change wording.
Approval still requires an editor to resolve the risks, verify cues and promote
the reviewed sources/media through the ordinary change-review workflow.

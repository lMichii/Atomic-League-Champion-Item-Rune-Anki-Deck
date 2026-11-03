# Phase 3.1 verification — 2026-11-01

Regenerated the six Braum drafts with the shared autonomous workflow. All remain
unapproved; the approved 100-card collection, model, card IDs and media are unchanged.
The initial Phase 3 archives remain intact as historical review records.

## Card output and validation

- Card-facing prose rejects internal provenance, confidence and review labels.
  Counterplay displays the natural recommendation; its inference type, evidence,
  uncertainties and review status remain in structured metadata.
- The review dashboard links to QA separately. Individual front/back faces omit
  review banners and source/status footer text. The frozen v4 CSS, layout fragments,
  stat formatter, icon/GIF handling and 17-field approved model remain unchanged.
- Each draft and QA record stores asset release separately from independently
  verified gameplay patch and its evidence. Braum uses Data Dragon **16.21.1**
  assets, CommunityDragon **16.21**, Wiki revision **4022592**, and an unknown
  verified gameplay patch. Both faces hide the gameplay-patch label.
- A pre-authoring cited mechanics inventory separates supported cores, advanced
  exceptions and unsupported claims. The verifier must account for every frozen
  core ID and quote the answer text that includes it. Missing cores trigger repair
  and remain explicit QA failures if unresolved, regardless of exception disputes.
- All **13** inventoried cores are included. Unbreakable explains projectile
  interception, the first eligible champion-damage negation, and subsequent
  directional damage reduction. Advanced eligibility, collision-effect and damage
  origin qualifications remain available for editorial review, without invented
  numbers or universal-protection claims in the lesson.
- The live run used one inventory call and two author/verifier passes: one support
  issue after the first pass, zero after repair. AI source assessment remains
  fallible; this result grants no editorial or visual approval.
- Four active GIFs retain real Riot media and the locked conversion recipe.
  Passive recognition keeps its icon. The passive clip and four sampled frames
  remain archived for visual review; the model withdrew an inadequately evidenced
  supplementary caption. Current-client/skin-specific visuals remain unverified.
- QA preserves two source-scope records and eleven factual-risk entries. Four
  cooldown topics remain proposals only; no supplementary cards were created.

## Verification

- **52 tests passed**, zero failures, errors or skips. Tests cover QA-label rejection,
  unknown-patch hiding, explicit patch-evidence requirements, core retention despite
  disputed exceptions, omitted-core failures, citation/numeric rejection, six-card
  coverage, stable Braum identities, preservation of all approved records and IDs,
  and deterministic offline replay of content, proposals, inventories and previews.
- Existing real Anki importer/reimport scheduling and review-history tests passed.
- All six previews passed real-browser checks: real local images loaded, v4
  background/style remained, both faces contained clean learning text with no
  unknown-patch label, Counterplay appeared and front/back controls worked.
  Browser screenshots of E and P were inspected. This is browser rendering QA,
  not live-client or mobile Anki visual verification.
- Rebuilt both approved decks through the CLI. Their SHA-256 hashes match the
  pre-change artifacts:

| Approved APKG | Cards | SHA-256 |
| --- | --- | --- |
| LoL_Pilot.apkg | 64 | `23a9f0813db46aacae014ed84d7e95ee4d24cd73ee0fff6f318ab84c396ea123` |
| LoL_Anki_Batch_01_100_Cards.apkg | 100 | `0f5525d460d1b3edfcaa560949884a54fa9fbae4626de2afe93ded5d2fea89d9` |

The additive proposal contains the exact approved first 100 records plus six
drafts. Its generated-proposal type remains ineligible for `apply-review`. No
Braum APKG was generated, no approval applied and no content published.

## Review artifacts

- [Six clean v4 previews](../data/drafts/braum/8696ff171e68869fcc76/previews/index.html)
- [Structured QA](../data/drafts/braum/8696ff171e68869fcc76/qa.json)
- [Readable QA](../data/drafts/braum/8696ff171e68869fcc76/QA.md)
- [Mechanics classification and evidence](../data/drafts/braum/8696ff171e68869fcc76/mechanics-inventory.json)
- [Unapproved change-review instructions](../data/drafts/braum/8696ff171e68869fcc76/REVIEW.md)
- [Additive diff](../data/drafts/braum/8696ff171e68869fcc76/changes.diff)

Reproduce using `python pipeline.py generate-champion braum --offline` with the
matching processor, configuration and FFmpeg version, or restore the committed
inputs with `python pipeline.py replay-generated-run data/drafts/braum/8696ff171e68869fcc76`.
The archive contains genuine retrieved inputs and model receipts, not mock media
or a canned champion response.

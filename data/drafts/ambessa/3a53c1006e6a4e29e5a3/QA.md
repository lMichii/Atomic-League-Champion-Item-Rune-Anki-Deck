# Ambessa — unapproved adaptive-kit QA

7 drafts; 100 approved cards unchanged. No approval, publication or APKG export.

Gameplay patch: unknown unless independently established; asset version: 16.21.1.

## Learning inventory

| ID | Type | Why this card exists | AI support |
| --- | --- | --- | --- |
| `champ:ambessa:overview:L1` | overview | Recognize her physical pressure, attack weaving, and mobility limits before judging an engagement. | supported draft |
| `champ:ambessa:system:p:drakehoundsstep:recognize:L2` | system | Anticipate repositioning after casts and recognize why attack access sustains her energy cycle. | REVIEW REQUIRED |
| `champ:ambessa:q:recognize:L2` | ability | Recognize the outer-edge threat and track whether a hit enabled the follow-up. | supported draft |
| `champ:ambessa:ability_variant:q:sunderingslam:cunningsweep:recognize:L2` | ability_variant | Recognize the line-shaped follow-up and its increased threat to the first target. | supported draft |
| `champ:ambessa:w:recognize:L2` | ability | Recognize the shielded retaliation window and anticipate the smash moving with her dash. | supported draft |
| `champ:ambessa:e:recognize:L2` | ability | Anticipate the repeated area threat at her dash endpoint. | supported draft |
| `champ:ambessa:r:recognize:L2` | ability | Recognize farthest-target selection, the suppression sequence, and the passive source of penetration and sustain. | supported draft |

## Source conflicts

- {"resolution": "Use the wiki's explicit champion, large-monster, and turret trigger list for the learning core; Riot's 'non-minion damage' wording is broader and does not establish every possible damage source.", "source_ids": ["riot:W", "wiki:repudiation"], "topic": "Repudiation empowerment trigger scope"}
- {"resolution": "Teach that the dash can reposition the smash. Preserve the detailed bracing-versus-dash timing as an advanced qualification to the abbreviated destination description.", "source_ids": ["wiki:repudiation", "riot:W"], "topic": "Repudiation smash location and timing"}
- {"resolution": "Retain dash-indicator visibility and player-only empowered-attack pips. The frozen privacy core cannot be fully asserted: the supplied dash-indicator quote establishes visibility to Ambessa but does not establish exclusivity. Preserve this unresolved limitation in metadata.", "source_ids": ["wiki:drakehoundsstep", "riot:P"], "topic": "Frozen private-indicator core exceeds explicit evidence for dash-indicator exclusivity"}
- {"resolution": "Use the specific shield-absorption condition involving champion, large-monster, or turret damage during bracing.", "source_ids": ["riot:W", "wiki:repudiation"], "topic": "Repudiation's broad non-minion wording versus enumerated qualifying damage sources"}
- {"resolution": "Retain possible relocation of the smash to the dash destination, with precise brace-versus-dash timing in metadata.", "source_ids": ["wiki:repudiation", "riot:W"], "topic": "Repudiation destination summary versus detailed timing"}
- {"resolution": "Only empowered-attack pips are explicitly player-only. Keep dash-indicator visibility without asserting exclusivity; the frozen privacy core cannot receive full coverage.", "source_ids": ["wiki:drakehoundsstep", "riot:P"], "topic": "Frozen dash-indicator privacy exceeds supplied evidence"}
- {"resolution": "Use the detailed shield-absorption condition: champion, large-monster, or turret damage during bracing.", "source_ids": ["riot:W", "wiki:repudiation"], "topic": "Broad non-minion wording versus enumerated empowerment sources"}
- {"resolution": "Retain possible smash relocation. Keep the brace-versus-dash timing qualification in metadata.", "source_ids": ["wiki:repudiation", "riot:W"], "topic": "Repudiation relocation summary versus detailed timing"}

## Factual risks

- The supplied Data Dragon release is pinned; its numbering does not establish a current game patch.
- Bug and unexpected-behavior annotations are excluded from established cores, including passive on-hit consumption, shield display delay, ultimate immunity lingering, direction-change bugs, and Flash queuing.
- Raw interaction tables and duplicated wiki passages are not independently verified mechanics.
- No supplied evidence establishes unusual skill leveling, a separate weapon system, or main-hand/off-hand interactions.
- Dash-indicator exclusivity is not established by the supplied evidence; all other supported parts of the indicator core remain in the designated explanation.
- Dash buffering can be replaced or cancelled by later inputs or affected by immobilization and grounding during the lockout.
- The ultimate explanation describes its normal successful sequence; suppression prevention and early removal can prevent the subsequent damage and stun.
- Repudiation's dash relocation is possible rather than an unconditional statement about every dash and brace timing.
- Counterplay is qualitative inference from supplied effects, not a guarantee of avoidance.
- AD is a broad learning orientation, not a proven or optimal item build.
- The supplied interface-indicator descriptions do not establish animations, colors, skins, or current-client media behavior.
- No patch label is inferred from the pinned release.
- The frozen private-indicator core contains unsupported dash-indicator exclusivity; this is an inventory limitation, not a false draft assertion.
- Dash buffering remains subject to later inputs and immobilization or grounding during lockout.
- The ultimate answer describes its normal successful sequence; prevention or early removal of suppression can prevent damage and stun.
- Ultimate passive healing is reduced against minions and monsters; this qualification is retained in metadata.
- Counterplay is explicitly typed source-grounded inference and makes no avoidance guarantees. AD is a reasonable broad orientation supported by physical damage and bonus-AD scaling, not an optimal-build claim.
- Bug and unexpected-behavior notes are not promoted to card facts. Interface descriptions do not verify current-client visuals or skins.

## Missing / ambiguous media

- {"card_id": "champ:ambessa:system:p:drakehoundsstep:recognize:L2", "issues": ["Passive/resource/leveling visual cues require manual review of the archived demonstration frames."]}
- {"card_id": "champ:ambessa:q:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:ambessa:ability_variant:q:sunderingslam:cunningsweep:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:ambessa:w:recognize:L2", "issues": ["The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review."]}
- {"card_id": "champ:ambessa:e:recognize:L2", "issues": ["The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review."]}

## Findings

- {"code": "adaptive_kit_structure", "message": "6 live sections discovered; conventional slot headings are not a completeness contract."}
- {"code": "ai_support_check_failed", "id": "champ:ambessa:system:p:drakehoundsstep:recognize:L2", "issues": ["The frozen private-indicator core is only partially supported and covered. Resolve its unsupported dash-indicator exclusivity in inventory metadata; do not add exclusivity to the answer."], "missing_core_ids": ["step_private_indicators"]}

## Approval blockers

- All cards require editorial approval and source-scope review.
- Weapon/ability image matching and all animations/cues require manual visual review.
- Missing variant animations use matched icons; generic slot clips are not variant verification.
- Unknown gameplay patch is hidden; source-supported draft status is not human QA.

## Model usage

{"logical_requests": 7, "recorded_model_attempts": 8, "available_receipt_usage": {"cache_write_input_tokens": 0, "cached_input_tokens": 0, "input_tokens": 177251, "output_tokens": 23438, "reasoning_output_tokens": 432}, "usage_receipts_available": 7, "scope": "Recorded generation usage; cached replay does not repeat these model calls. Failed-attempt usage may be unavailable."}

Detailed core coverage, conditions, exact citations, inference types and visual mapping are in qa.json, card-inventory.json and kit-analysis.json.

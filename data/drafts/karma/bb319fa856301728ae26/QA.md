# Karma — unapproved adaptive-kit QA

8 drafts; 100 approved cards unchanged. No approval, publication or APKG export.

Gameplay patch: unknown unless independently established; asset version: 16.21.1.

## Learning inventory

| ID | Type | Why this card exists | AI support |
| --- | --- | --- | --- |
| `champ:karma:overview:L1` | overview | Recognize a poke and protection mage whose empowerment choice changes the threat. Her supplied kit describes movement-speed boosts but no dash or blink; account for speed-assisted repositioning. | supported draft |
| `champ:karma:system:r:mantra:recognize:L2` | system | Expect empowerment from the opening levels and recognize that successful champion damage accelerates its return. | supported draft |
| `champ:karma:q:recognize:L2` | ability | Recognize the poke projectile and avoid its splash even when another unit intercepts it. | supported draft |
| `champ:karma:ability_variant:q:soulflare:mantra:recognize:L2` | ability_variant | Recognize empowered Q and leave the lingering field before its delayed damage. | supported draft |
| `champ:karma:w:recognize:L2` | ability | Recognize the tether as a delayed root threat and prioritize breaking it before completion. | supported draft |
| `champ:karma:ability_variant:w:renewal:mantra:recognize:L2` | ability_variant | Anticipate a low-health Karma's healing reversal and the longer root; breaking the tether can prevent its completion-triggered heal. | supported draft |
| `champ:karma:e:recognize:L2` | ability | Recognize protection and speed that can help a target escape, approach or maintain a tether. | supported draft |
| `champ:karma:ability_variant:e:defiance:mantra:recognize:L2` | ability_variant | Recognize group protection and acceleration that can enable a coordinated approach or retreat. | supported draft |

## Source conflicts

- {"resolution": "Use qualitative damage effects. The appended change note is not treated as a current damage table.", "source_ids": ["wiki:Q", "wiki:soulflare"], "topic": "Soulflare damage arrays coexist with a different appended primary-damage change note."}
- {"resolution": "Teach champion-hit cooldown reduction qualitatively from the dedicated live section and Riot description; omit exact reduction values.", "source_ids": ["wiki:P", "wiki:gatheringfire", "riot:P"], "topic": "Gathering Fire's live description is mixed with an uncontextualized historical cooldown-reduction change line in wiki:P."}
- {"resolution": "Retain the shared qualitative cooldown-reduction mechanic; omit exact reduction amounts.", "source_ids": ["riot:P", "wiki:P", "wiki:gatheringfire"], "topic": "Passive excerpts contain differing numeric cooldown-reduction text."}
- {"resolution": "Retain increased impact damage and delayed field damage; omit disputed damage values.", "source_ids": ["wiki:Q", "wiki:soulflare"], "topic": "Soulflare excerpts include damage tables and a differing change-note value."}
- {"resolution": "Keep qualitative champion-hit cooldown recovery. The change-note fragment does not establish a competing current value; omit numerical claims rather than treating historical text as current mechanics.", "source_ids": ["riot:P", "wiki:P", "wiki:gatheringfire"], "topic": "Passive numerical descriptions mixed with a change-note fragment."}
- {"resolution": "Keep increased impact damage and delayed field damage. The differing change-note value is not established as current and need not override the qualitative mechanics.", "source_ids": ["wiki:Q", "wiki:soulflare"], "topic": "Soulflare damage tables mixed with a historical change-note value."}

## Factual risks

- The packet does not establish a current patch label; pinned Data Dragon numbering must not be converted into one.
- The absence of a dash or blink is an inference from the complete supplied active kit, not an explicit quoted mobility restriction.
- Renewal bug and unexpected-interaction notes are not established current mechanics; visual tether bugs, cast-cancellation bugs and rune interactions are excluded from core requirements.
- Lore, skins and collection text embedded in wiki:R do not describe combat mechanics.
- Exact damage, shielding, healing, cooldown and duration arrays are unnecessary for these recognition goals and may contain stale notes.
- This inventory is unapproved editorial material.
- Build focus is a broad AP learning orientation, not an optimal item-build claim.
- Counterplay is qualitative guidance derived from the described effects, rather than an explicit source assertion or a guaranteed outcome.
- The supplied excerpts mix repeated descriptions, numeric tables, change notes and bug reports; learning answers retain the frozen qualitative cores.
- No ability-absence inference is used; the answers make no claim that Karma lacks a dash or blink.
- No current patch, animation, color or skin claim is established from the supplied material.
- Counterplay is appropriately typed in external metadata as source-grounded inference; it introduces no unsupported timings or guaranteed escape outcomes.
- Renewal counterplay specifically prevents the completion-triggered heal; it does not claim that breaking the tether reverses the initial heal or removes the separate death-trigger condition.
- AP is a broad learning orientation supported by supplied scaling evidence, not an optimal-build claim.
- Bug reports, historical fragments and demonstration limitations remain outside card-facing mechanics. No exhaustive ability-absence inference or human approval is asserted.

## Missing / ambiguous media

- {"card_id": "champ:karma:system:r:mantra:recognize:L2", "issues": ["The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review.", "Passive/resource/leveling visual cues require manual review of the archived demonstration frames."]}
- {"card_id": "champ:karma:ability_variant:q:soulflare:mantra:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:karma:ability_variant:w:renewal:mantra:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:karma:ability_variant:e:defiance:mantra:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}

## Findings

- {"code": "adaptive_kit_structure", "message": "8 live sections discovered; conventional slot headings are not a completeness contract."}
- {"code": "media_url_missing", "name": "karma_p.webm"}

## Approval blockers

- All cards require editorial approval and source-scope review.
- Weapon/ability image matching and all animations/cues require manual visual review.
- Missing variant animations use matched icons; generic slot clips are not variant verification.
- Unknown gameplay patch is hidden; source-supported draft status is not human QA.

## Model usage

{"logical_requests": 3, "recorded_model_attempts": 3, "available_receipt_usage": {"cache_write_input_tokens": 0, "cached_input_tokens": 0, "input_tokens": 67993, "output_tokens": 10070, "reasoning_output_tokens": 193}, "usage_receipts_available": 3, "scope": "Recorded generation usage; cached replay does not repeat these model calls. Failed-attempt usage may be unavailable."}

Detailed core coverage, conditions, exact citations, inference types and visual mapping are in qa.json, card-inventory.json and kit-analysis.json.

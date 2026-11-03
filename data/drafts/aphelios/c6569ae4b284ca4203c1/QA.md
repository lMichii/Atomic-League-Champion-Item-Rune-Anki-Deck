# Aphelios — unapproved adaptive-kit QA

14 drafts; 100 approved cards unchanged. No approval, publication or APKG export.

Gameplay patch: unknown unless independently established; asset version: 16.21.1.

## Learning inventory

| ID | Type | Why this card exists | AI support |
| --- | --- | --- | --- |
| `champ:523:overview:L1` | overview | Recognize an attack-focused marksman; assess his equipped weapons before choosing spacing or committing to an engage. | supported draft |
| `champ:523:system:p:thehitmanandtheseer:recognize:L2` | system | Track the equipped pair and ammunition cycle; anticipate changing threats and recognize the unusual early ability unlocks. | supported draft |
| `champ:523:weapon:none:calibrum:recognize:L2` | weapon | Recognize ranged harassment and respect marked follow-ups even after leaving ordinary attack range. | supported draft |
| `champ:523:ability_variant:q:moonshot:calibrum:recognize:L2` | ability_variant | Recognize and dodge the rifle shot; use intervening units to prevent it from reaching a desired target. | supported draft |
| `champ:523:weapon:none:severum:recognize:L2` | weapon | Recognize sustain and shielding during trades; account for Severum's non-projectile attacks when relying on projectile defenses. | supported draft |
| `champ:523:ability_variant:q:onslaught:severum:recognize:L2` | ability_variant | Recognize mobile sustained fire and judge its additional threat from the off-hand weapon. | supported draft |
| `champ:523:weapon:none:gravitum:recognize:L2` | weapon | Recognize the control weapon: being hit creates a slow and exposes the target to Binding Eclipse. | supported draft |
| `champ:523:ability_variant:q:bindingeclipse:gravitum:recognize:L2` | ability_variant | Recognize the root setup after a Gravitum hit; do not mistake this for a freely aimed root. | supported draft |
| `champ:523:weapon:none:infernum:recognize:L2` | weapon | Recognize the area-damage weapon and avoid lining up behind his attack target. | supported draft |
| `champ:523:ability_variant:q:duskwave:infernum:recognize:L2` | ability_variant | Avoid the cone and recognize that its follow-up carries the off-hand weapon's threat. | supported draft |
| `champ:523:weapon:none:crescendum:recognize:L2` | weapon | Recognize dangerous close-range damage, especially with accumulated mirror chakrams; disengage to let temporary strength expire. | supported draft |
| `champ:523:ability_variant:q:sentry:crescendum:recognize:L2` | ability_variant | Recognize off-hand-dependent zone control; avoid activating the sentry carelessly or destroy it once targetable. | supported draft |
| `champ:523:w:recognize:L2` | ability | Reassess his threat immediately after a swap; the previously off-hand weapon can now supply the active. | supported draft |
| `champ:523:r:recognize:L2` | ability | Identify the firing weapon to anticipate marks, healing, control, splash or strengthened follow-up attacks; spread against Infernum and respect Crescendum afterward. | supported draft |

## Source conflicts

- {"resolution": "Treat E as a noncombat queue indicator with an informational text action. The wiki's 'Active' label does not establish a combat spell.", "source_ids": ["riot:E", "wiki:weaponqueuesystem"], "topic": "E described as no ability versus an informational active"}
- {"resolution": "Teach qualitative ultimate effects. Exclude stale numerical values and the explicitly uncertain critical-damage anomaly.", "source_ids": ["wiki:moonlightvigil", "riot:R"], "topic": "Ultimate numerical notes include outdated values and an unverified bug"}
- {"resolution": "Use the explicit Calibrum attribution in the Calibrum section. Treat the Crescendum projectile note embedded in Moonshot as cross-topic detail, not a Moonshot mechanic.", "source_ids": ["wiki:moonshot", "wiki:calibrum", "wiki:crescendum"], "topic": "Cross-topic notes embedded in ability sections"}
- {"resolution": "Teach E as a next-weapon indicator with an optional text prompt, consistent with having no third combat ability.", "source_ids": ["riot:E", "wiki:weaponqueuesystem"], "topic": "E indicator versus active text prompt"}
- {"resolution": "Specify ammunition costs for basic attacks and primary casts, and explicitly exempt automatic attacks caused by abilities from additional costs.", "source_ids": ["riot:P", "wiki:thehitmanandtheseer"], "topic": "General ammunition description versus detailed cost rules"}
- {"resolution": "Retain qualitative ultimate effects while excluding alternative numerical formulas, anomalous critical damage and pending-test claims.", "source_ids": ["riot:R", "wiki:moonlightvigil"], "topic": "Ultimate numerical uncertainty"}
- {"resolution": "The supplied P/Q/W/E/R descriptions enumerate the active kit, permitting the requested absence inference. The review's kit_complete=false is retained as a completeness risk rather than treated as evidence of an omitted ability.", "source_ids": ["riot:P", "riot:Q", "riot:W", "riot:E", "riot:R"], "topic": "Complete active enumeration versus review completeness flag"}
- {"resolution": "E displays the next reserve weapon and can produce a text prompt; this does not establish a third combat spell.", "source_ids": ["riot:E", "wiki:weaponqueuesystem"], "topic": "E description"}
- {"resolution": "The detailed ammunition rule qualifies the short general description: primary casts and ordinary attacks consume ammunition, while ability-generated automatic attacks consume no additional ammunition.", "source_ids": ["riot:P", "wiki:thehitmanandtheseer"], "topic": "Ammunition consumption"}
- {"resolution": "Retain qualitative ultimate effects. Exclude conflicting formulas, bug reports, pending tests and outdated numerical examples from learned facts.", "source_ids": ["wiki:moonlightvigil", "riot:R"], "topic": "Ultimate numerical uncertainty"}
- {"resolution": "The explicit in-flight swap rule qualifies the general current-main-weapon wording; teaching the firing weapon's effect is supported.", "source_ids": ["wiki:moonlightvigil", "riot:R"], "topic": "Ultimate weapon selection"}

## Factual risks

- This is unapproved editorial material derived only from the supplied packet; no current-client verification was performed.
- The pinned Data Dragon release does not establish a current game patch label.
- The mobility conclusion is an inference from the complete supplied active kit, which lists movement speed but no displacement.
- The shorter-return-distance benefit for Crescendum is inferred from its return-gated attack timing.
- Moonlight Vigil includes explicitly outdated values and bug or pending-test notes; qualitative effects are retained without treating those numerical notes as current facts.
- Crescendum attack-speed-limit behavior is pending testing and is not established.
- Demonstration clips do not verify current-client or skin-specific recognition cues; no weapon colors or skin-specific visuals are asserted.
- No dash or blink is an exhaustive-kit inference, not an explicit source assertion, and depends on the supplied enumeration being complete.
- AD build_focus describes broad physical attack orientation; the sources do not prescribe an item build.
- Counterplay inference type for every card is qualitative_effect_derivation, recorded in each card's metadata because the output schema has no dedicated counterplay inference field.
- The close-range Crescendum consequence is derived from return travel and the attack-timer reset. The schema permits no general mechanical-inference basis; its source_assertion fact cites the underlying mechanics and discloses this limitation.
- Stationary sentry behavior follows the supplied placement and autonomous in-range targeting description.
- Binding Eclipse's general slow-to-root behavior retains the targetability condition; immunity and in-flight projectile exceptions remain metadata.
- Numerical anomalies and pending-test claims are excluded without dropping qualitative frozen cores.
- The supplied release is pinned; no patch label, appearance, animation or skin-specific behavior is inferred.
- Dash/blink absence remains an explicitly typed exhaustive-kit inference with a recorded completeness dependency, rather than a confirmed source quotation.
- The draft conflict entry mentioning a prior kit_complete=false review has no independently supplied supporting review. Treat that reference as unverified metadata; the supplied live sections support completeness at the requested teaching scope.
- Crescendum's close-range advantage and Sentry's stationary characterization are qualitative derivations from supplied mechanics, not verbatim assertions; their metadata discloses this.
- Ultimate numerical uncertainty and Binding Eclipse immunity/projectile exceptions remain metadata issues; they do not invalidate the supported qualitative cores.

## Missing / ambiguous media

- {"card_id": "champ:523:system:p:thehitmanandtheseer:recognize:L2", "issues": ["Passive/resource/leveling visual cues require manual review of the archived demonstration frames."]}
- {"card_id": "champ:523:ability_variant:q:moonshot:calibrum:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:523:ability_variant:q:onslaught:severum:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:523:ability_variant:q:bindingeclipse:gravitum:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:523:ability_variant:q:duskwave:infernum:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:523:ability_variant:q:sentry:crescendum:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}
- {"card_id": "champ:523:r:recognize:L2", "issues": ["The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review."]}

## Findings

- {"code": "adaptive_kit_structure", "message": "15 live sections discovered; conventional slot headings are not a completeness contract."}
- {"code": "noncombat_slot_without_animation", "name": "aphelios_e.webm", "original_code": "media_url_missing", "severity": "info", "message": "Source inventory identifies an indicator/unused slot; no combat animation expected."}
- {"code": "noncombat_slot_without_animation", "slot": "E", "message": "Source inventory identifies an indicator/unused slot; no combat animation expected.", "original_code": "active_icon_fallback", "severity": "info"}

## Approval blockers

- All cards require editorial approval and source-scope review.
- Weapon/ability image matching and all animations/cues require manual visual review.
- Missing variant animations use matched icons; generic slot clips are not variant verification.
- Unknown gameplay patch is hidden; source-supported draft status is not human QA.

## Model usage

{"logical_requests": 3, "recorded_model_attempts": 3, "available_receipt_usage": {"cache_write_input_tokens": 0, "cached_input_tokens": 0, "input_tokens": 93855, "output_tokens": 22187, "reasoning_output_tokens": 261}, "usage_receipts_available": 3, "scope": "Recorded generation usage; cached replay does not repeat these model calls. Failed-attempt usage may be unavailable."}

Detailed core coverage, conditions, exact citations, inference types and visual mapping are in qa.json, card-inventory.json and kit-analysis.json.

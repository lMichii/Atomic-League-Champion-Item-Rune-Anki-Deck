# Renekton — unapproved adaptive-kit QA

6 drafts; 100 approved cards unchanged. No approval, publication or APKG export.

Gameplay patch: unknown unless independently established; asset version: 16.21.1.

## Learning inventory

| ID | Type | Why this card exists | AI support |
| --- | --- | --- | --- |
| `champ:renekton:overview:L1` | overview | Recognize his close-range damage, sustain, stun and conditional pursuit before choosing trade distance. | supported draft |
| `champ:renekton:system:p:reignofanger:recognize:L2` | system | Read Fury before committing, including when low health increases his ability to rebuild it. | supported draft |
| `champ:renekton:q:recognize:L2` | ability | Recognize his surrounding sustain threat and avoid giving him easy healing during trades. | supported draft |
| `champ:renekton:w:recognize:L2` | ability | Recognize the targeted stun threat and the added danger of relying on damage shields against empowered W. | supported draft |
| `champ:renekton:e:recognize:L2` | ability | Track whether Slice hit an enemy before judging his remaining pursuit or escape, and recognize empowered Dice's armor reduction. | supported draft |
| `champ:renekton:transformation:r:dominus:recognize:L2` | transformation | Recognize his enlarged sustained-fight state, account for renewed Fury, and reassess close-range trades when he activates it. | supported draft |

## Source conflicts

- {"resolution": "Use the detailed passive's inclusive threshold of at least 50 Fury. Riot ability descriptions say more than 50; the wiki's introductory percentage wording is less precise than its detailed rule.", "source_ids": ["riot:Q", "riot:W", "wiki:reignofanger"], "topic": "Fury empowerment threshold"}
- {"resolution": "Teach Slice's exclusion from Fury consumption and Dice's empowerment using the detailed passive and E descriptions.", "source_ids": ["wiki:reignofanger", "wiki:sliceanddice", "riot:E"], "topic": "Generic basic-ability empowerment wording versus Slice exception"}
- {"resolution": "Use the detailed passive rule of at least 50 Fury, with Slice excluded, rather than the simplified descriptions saying more than 50.", "source_ids": ["riot:Q", "riot:W", "wiki:reignofanger"], "topic": "Fury empowerment threshold"}
- {"resolution": "Describe healing per enemy hit, increased against champions, following the detailed Q description; omit the simplified damage-proportional wording.", "source_ids": ["riot:Q", "wiki:cullthemeek"], "topic": "Cull the Meek healing model"}
- {"resolution": "Apply the passive's explicit exception that empowered abilities do not generate Fury. Q's Fury generation is described only for its normal version.", "source_ids": ["wiki:reignofanger", "wiki:cullthemeek", "wiki:ruthlesspredator", "wiki:sliceanddice"], "topic": "Ability-hit Fury generation versus empowerment exception"}
- {"resolution": "Use the detailed passive's at-least-50 threshold and explicit Slice exception rather than the simplified Riot descriptions saying more than 50.", "source_ids": ["riot:Q", "riot:W", "wiki:reignofanger"], "topic": "Fury empowerment threshold"}
- {"resolution": "Use the detailed per-enemy healing model, increased against champions, rather than describing healing as proportional to damage dealt.", "source_ids": ["riot:Q", "wiki:cullthemeek"], "topic": "Cull the Meek healing model"}
- {"resolution": "Apply the explicit passive exception: empowered abilities do not generate Fury. Read general ability-hit generation statements subject to that exception.", "source_ids": ["wiki:reignofanger", "wiki:cullthemeek", "wiki:ruthlesspredator", "wiki:sliceanddice"], "topic": "Normal versus empowered Fury generation"}

## Factual risks

- The Data Dragon release is pinned; the packet does not establish a current game patch label.
- The pending parrying-effects test is uncertain and supplies no established Fury interaction.
- The cooldown-change note in wiki:W is excluded as an isolated numerical change note.
- Lore, skins, collection text and credits embedded in wiki:R are excluded from gameplay teaching.
- Health Relics and peripheral pickup interactions are omitted from the central Fury goal because their mode context is not established.
- Detailed wiki-only interaction exceptions remain advanced material; no current-client verification is supplied.
- Counterplay is qualitative inference from the supplied effects, not a guaranteed outcome.
- The overview's AD orientation summarizes basic-ability damage and scaling; it does not establish an optimal build or follow causally from Fury empowerment.
- No exhaustive-kit ability-absence inference is used; the Slice and empowered-Fury exceptions are explicit source assertions.
- W's general shield-destruction core describes champion combat; monster and structure exceptions and attack-trigger distinctions remain in metadata.
- Fury generation against blind, dodge and block remains unresolved in the supplied material.
- No patch label or visual appearance is inferred from the supplied material.
- General attack-generated Fury wording is a beginner summary: the detailed passive excludes structures, and empowered abilities do not generate Fury.
- W's shield-destruction wording must retain its declared champion-combat scope; the detailed source excludes monsters and says the empowered attack does not trigger against structures.
- AD is inferred broad learning guidance from the supplied scaling, not an explicit source statement establishing an optimal build. The external pedagogical metadata supplies the required interpretation.
- Counterplay is qualitative source-grounded inference and makes no timing or outcome guarantees.
- Fury generation against blind, dodge and block remains pending testing and is correctly confined to metadata.
- No exhaustive-kit absence inference, patch identification or visual verification is asserted.

## Missing / ambiguous media

- {"card_id": "champ:renekton:system:p:reignofanger:recognize:L2", "issues": ["Passive/resource/leveling visual cues require manual review of the archived demonstration frames."]}
- {"card_id": "champ:renekton:q:recognize:L2", "issues": ["The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review."]}
- {"card_id": "champ:renekton:w:recognize:L2", "issues": ["The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review."]}
- {"card_id": "champ:renekton:e:recognize:L2", "issues": ["The primary clip does not individually verify every weapon/form-dependent effect; conditional visual matching requires review."]}
- {"card_id": "champ:renekton:transformation:r:dominus:recognize:L2", "issues": ["No verified variant-specific animation; matched icon fallback only. A generic slot clip is not attributed to this variant."]}

## Findings

- {"code": "adaptive_kit_structure", "message": "5 live sections discovered; conventional slot headings are not a completeness contract."}

## Approval blockers

- All cards require editorial approval and source-scope review.
- Weapon/ability image matching and all animations/cues require manual visual review.
- Missing variant animations use matched icons; generic slot clips are not variant verification.
- Unknown gameplay patch is hidden; source-supported draft status is not human QA.

## Model usage

{"logical_requests": 5, "recorded_model_attempts": 5, "available_receipt_usage": {"cache_write_input_tokens": 0, "cached_input_tokens": 25472, "input_tokens": 122684, "output_tokens": 16287, "reasoning_output_tokens": 389}, "usage_receipts_available": 5, "scope": "Recorded generation usage; cached replay does not repeat these model calls. Failed-attempt usage may be unavailable."}

Detailed core coverage, conditions, exact citations, inference types and visual mapping are in qa.json, card-inventory.json and kit-analysis.json.

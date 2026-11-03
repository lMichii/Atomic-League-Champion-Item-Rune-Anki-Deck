# Garen — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 3892614.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:garen:overview:L1` | B | supported draft | unverified |
| `champ:garen:p:recognize:L2` | B | supported draft | unverified |
| `champ:garen:q:recognize:L2` | A | supported draft | unverified |
| `champ:garen:w:recognize:L2` | A | REVIEW REQUIRED | unverified |
| `champ:garen:e:recognize:L2` | A | supported draft | unverified |
| `champ:garen:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.regeneration` | yes |
| Q | `Q.speed_and_slow_cleanse` | yes |
| Q | `Q.empowered_attack` | yes |
| W | `W.passive_resistances` | yes |
| W | `W.shield_and_tenacity` | yes |
| W | `W.damage_reduction` | yes |
| E | `E.area_damage` | yes |
| E | `E.spin_count` | yes |
| E | `E.nearest_target_bonus` | yes |
| E | `E.armor_reduction` | yes |
| R | `R.missing_health_true_damage` | yes |

## Findings

- {"code": "ai_support_check_failed", "id": "champ:garen:w:recognize:L2", "issues": ["UNAPPROVED draft.", "The support review requests a plain-language definition of tenacity, but the supplied packet contains none. The supported core term is retained; this beginner-learning gap cannot be repaired without additional evidence.", "Eligible kills exclude assists, wards, structures and several special units.", "The Wiki summary mentions an additional boost at the resistance cap without specifying it in the detailed mechanics.", "Map-specific differences and advanced tenacity interactions are omitted.", "Tenacity is unexplained jargon for beginners. Obtain supporting evidence for a plain-language definition and add it while retaining the supported mechanic."]}

## Source conflicts

- {"resolution": "Use the Wiki's specific eligible interruption sources and retain damage-prevention exceptions in metadata. Do not describe every damage source as interrupting regeneration.", "source_ids": ["riot:P", "wiki:P"], "topic": "Passive interruption scope"}
- {"resolution": "Follow the Wiki's explicit timing: damage reduction begins at activation and lasts beyond the brief shield and tenacity window.", "source_ids": ["riot:W", "wiki:W"], "topic": "Courage damage-reduction timing"}
- {"resolution": "Preserve capped resistance gains. Leave the additional cap boost unresolved because the detailed excerpt does not specify it.", "source_ids": ["wiki:W", "riot:W"], "topic": "Additional defensive boost at Courage's resistance cap"}
- {"resolution": "Use the Wiki's specific interruption sources and damage-prevention exceptions to qualify Riot's broad summary. The draft's conditional wording is supported.", "source_ids": ["riot:P", "wiki:P"], "topic": "Passive interruption scope"}
- {"resolution": "The Wiki explicitly places damage reduction at activation and beyond the opening shield window. The draft accommodates that timing; Riot's sequential wording should not establish a delayed start.", "source_ids": ["riot:W", "wiki:W"], "topic": "Courage damage-reduction timing"}
- {"resolution": "The Wiki summary asserts an additional permanent boost at the cap, but its detailed mechanics do not specify that boost. Retain the supported capped gains and flag the additional boost for QA.", "source_ids": ["wiki:W", "riot:W"], "topic": "Unresolved additional resistance boost at Courage's cap"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- The requested beginner explanation of tenacity remains unresolved because the packet does not define it and additional evidence cannot be obtained within this task.
- The demonstration frames do not establish a healing cue, current-client behavior or skin-specific appearance.
- The pinned Data Dragon release does not establish a game patch label.
- Counterplay is inferred teaching guidance grounded in the supplied effects.
- AD and health are broad learning focuses, not an optimal item build.
- Wiki-only mechanics lack independent Riot confirmation where Riot's excerpts are silent.
- Historical skin prose, bugs and map-specific variants are excluded from the core explanations.
- The supplied evidence does not define tenacity, leaving a beginner-learning gap.
- The AD and Health build focus has scaling support in Q/E and W respectively, but the evidence does not establish an optimal build.
- The supplied frames do not establish a recognizable healing cue or current-client behavior; no visual verification is provided.
- The pinned Data Dragon version does not establish a game patch label.
- Counterplay is supported as conditional inference, without guaranteed outcomes or invented timings. Its visible wording contains no inference or confidence labels.
- UNAPPROVED and support-review labels occur in metadata, not in the answer or counterplay text; keep them out of card-facing presentation.
- This support check does not constitute human approval.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Availability of the speed boost and silencing attack matters when judging approach threats.", "slot": "Q", "source_ids": ["riot:Q", "wiki:Q"]}
- {"priority": "A", "reason": "Availability of his defensive activation matters before committing damage.", "slot": "W", "source_ids": ["riot:W", "wiki:W"]}
- {"priority": "A", "reason": "Availability of his finishing blow matters before staying nearby at low health.", "slot": "R", "source_ids": ["riot:R", "wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

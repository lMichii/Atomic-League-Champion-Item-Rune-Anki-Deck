# Darius — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4022598.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:darius:overview:L1` | B | supported draft | unverified |
| `champ:darius:p:recognize:L2` | A | supported draft | unverified |
| `champ:darius:q:recognize:L2` | A | supported draft | unverified |
| `champ:darius:w:recognize:L2` | B | supported draft | unverified |
| `champ:darius:e:recognize:L2` | A | supported draft | unverified |
| `champ:darius:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.bleed` | yes |
| P | `P.noxian_might` | yes |
| Q | `Q.circular_damage` | yes |
| Q | `Q.blade_handle` | yes |
| Q | `Q.heal` | yes |
| W | `W.empowered_attack` | yes |
| W | `W.attack_reset` | yes |
| E | `E.armor_penetration` | yes |
| E | `E.pull_slow` | yes |
| R | `R.true_damage` | yes |
| R | `R.hemorrhage_scaling` | yes |
| R | `R.kill_reuse` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Use Wiki's enemy-champion restriction for maximum-stack empowerment rather than extending Riot's broad wording to every enemy type.", "source_ids": ["riot:P", "wiki:P"], "topic": "Maximum-stack empowerment target scope"}
- {"resolution": "Preserve general eligible bleed application and explicitly explain that Q handle hits neither apply nor refresh it.", "source_ids": ["riot:P", "wiki:P", "wiki:Q"], "topic": "General passive application versus Q handle exception"}
- {"resolution": "Preserve qualifying kill-based reuse and distinguish the temporary recast window from the permanent maximum-rank cooldown reset. Retain special target exceptions in metadata.", "source_ids": ["riot:R", "wiki:R"], "topic": "R kill qualification and rank-dependent reuse"}
- {"resolution": "Use the Wiki's enemy-champion restriction for maximum-stack empowerment; the passive draft does so.", "source_ids": ["riot:P", "wiki:P"], "topic": "Maximum-stack empowerment target scope"}
- {"resolution": "Read broad passive application descriptions with the explicit Q handle exception. The drafts preserve eligible application and explain the exception.", "source_ids": ["riot:P", "wiki:P", "wiki:Q"], "topic": "General bleed application versus Q handle hits"}
- {"resolution": "The detailed healing text and Riot both include large monsters, despite the Wiki's shorter champion-only description. Exact healing values and cap need not appear in this summary.", "source_ids": ["riot:Q", "wiki:Q"], "topic": "Q healing target scope within the excerpts"}
- {"resolution": "Use the detailed Wiki qualification and rank distinction to refine Riot's abbreviated reset description. Keep special target exceptions in metadata.", "source_ids": ["riot:R", "wiki:R"], "topic": "R kill qualification and rank-dependent reuse"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Counterplay and broad build focus are inferred teaching guidance.
- Pinned Data Dragon and Wiki versions do not establish the current game patch.
- No passive visual cue is proposed; demonstration frames do not establish current-client or skin-specific appearance.
- Pending-test E notes and unrelated skin material are excluded from factual explanations.
- Advanced bleed application, W spell-shield behavior and R reset qualification and cancellation exceptions remain relevant beyond these beginner summaries.
- W's attack reset is explained as an earlier follow-up attack to address the beginner-language support review.
- This support check does not provide human approval or visual verification.
- Pinned source versions do not establish the current game patch.
- AD and Health are inferred broad build guidance, not a sourced optimal build or evidence of direct health scaling.
- E rebound-location and simultaneous-stun or brittle claims remain explicitly pending testing.
- W's entire empowered attack being blocked by spell shields is explicitly reported by the Wiki but lacks independent corroboration in the supplied evidence.
- Special R target exceptions distinguish cooldown resets from Noxian Might activation; the general beginner wording does not enumerate them.
- No internal provenance or confidence labels appear in the visible answer, counterplay or build-focus text.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Pull availability determines when Darius can force close combat.", "slot": "E", "source_ids": ["riot:E", "wiki:E"]}
- {"priority": "A", "reason": "Kill-based reuse and maximum-rank resets affect repeated finishing threats.", "slot": "R", "source_ids": ["riot:R", "wiki:R"]}
- {"priority": "A", "reason": "Availability affects access to blade damage and healing.", "slot": "Q", "source_ids": ["riot:Q", "wiki:Q"]}
- {"priority": "B", "reason": "Kill refunds reduce the cooldown without fully resetting it.", "slot": "W", "source_ids": ["wiki:W"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

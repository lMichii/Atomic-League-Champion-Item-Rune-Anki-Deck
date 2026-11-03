# Alistar — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 3892578.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:alistar:overview:L1` | A | supported draft | unverified |
| `champ:alistar:p:recognize:L2` | B | REVIEW REQUIRED | proposed_unverified |
| `champ:alistar:q:recognize:L2` | A | supported draft | unverified |
| `champ:alistar:w:recognize:L2` | A | supported draft | unverified |
| `champ:alistar:e:recognize:L2` | A | supported draft | unverified |
| `champ:alistar:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.charge` | yes |
| P | `P.heal` | yes |
| Q | `Q.area_damage` | yes |
| Q | `Q.knockup` | yes |
| W | `W.targeted_dash` | yes |
| W | `W.damage` | yes |
| W | `W.knockback` | yes |
| E | `E.periodic_damage` | yes |
| E | `E.ignore_unit_collision` | yes |
| E | `E.champion_stacks` | yes |
| E | `E.empowered_attack` | yes |
| R | `R.cleanse` | yes |
| R | `R.damage_reduction` | yes |

## Findings

- {"code": "ai_support_check_failed", "id": "champ:alistar:p:recognize:L2", "issues": ["UNAPPROVED draft.", "The visual cue is a tentative proposal from the supplied official demonstration frames, not current-client verification. Mechanics source IDs do not independently verify its appearance.", "Nearby enemy champion or epic monster deaths supply full charge.", "Failed crowd control attempts do not generate stacks, and death clears stored stacks.", "Healing is simultaneous; the visual projectile does not deliver the actual heal.", "The passive_visual description asserts an appearance and trigger association that the cited mechanics excerpts do not verify. Its tentative status is disclosed only in metadata. Repair or independently verify this card-facing visual claim; this check does not provide visual verification."]}

## Source conflicts

- {"resolution": "Preserve normal W knockback. Leave exact buffered-Q displacement unresolved because the supplied Wiki describes both reduced knockback and overriding knockback.", "source_ids": ["wiki:W", "wiki:Q"], "topic": "W knockback when Q is buffered"}
- {"resolution": "Preserve supported physical and magic damage reduction. Exclude the interaction marked unexpected from learning text and retain it as provisional metadata.", "source_ids": ["wiki:R", "riot:R"], "topic": "Provisional R interaction with Hemoplague"}
- {"resolution": "Retain normal W knockback and the supported general fact that buffering Q modifies it. Keep the exact resulting displacement unresolved pending QA: the supplied Wiki describes both reduction to 200 units and overriding knockback.", "source_ids": ["wiki:W", "wiki:Q"], "topic": "W displacement when Q is buffered"}
- {"resolution": "The Hemoplague interaction is explicitly marked unexpected, rather than established by conflicting independent sources. Keep it provisional in metadata; it does not undermine the supported general damage reduction.", "source_ids": ["wiki:R", "riot:R"], "topic": "Provisional R interaction with Hemoplague"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- The overview uses AP as a supported scaling-learning focus, not an optimal build recommendation; supplied evidence does not establish a tank-stat recommendation.
- Counterplay and fighting-role implications are inferred teaching guidance grounded in the supplied effects.
- The passive visual cue is a tentative official-demo proposal, not current-client or skin-specific verification.
- The passive's full-charge heal can wait for its internal cooldown.
- The pinned Data Dragon release does not establish the current game patch.
- Alternate-mode values and transcluded skin material are excluded from ability explanations.
- Advanced immunity, buffered-combo and failed-attack interactions qualify the general ability behavior.
- This is an AI support check, not human approval or visual verification.
- The passive visual description remains unverified; mechanics citations alone cannot establish its appearance or trigger association.
- The overview's AP statement supports increased ability damage overall, not AP scaling on every damage component or an optimal build recommendation.
- Counterplay and gameplay implications are reasonable inferences from the supplied mechanics, without guaranteed outcomes or invented timing.
- Advanced immunity, failed-attack and combo exceptions remain relevant metadata; their omission does not make these general beginner explanations misleading.
- The pinned release and demonstration frames do not establish current-client, current-patch or skin-specific behavior.
- No internal provenance, confidence or development labels appear in the supplied card-facing wording.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Availability changes his ability to engage or interrupt nearby enemies.", "slot": "Q", "source_ids": ["wiki:Q"]}
- {"priority": "A", "reason": "Availability changes his targeted approach and displacement threat.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "B", "reason": "Availability determines whether he can build toward an empowered attack stun.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Availability strongly affects attempts to disable him or deal heavy damage.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

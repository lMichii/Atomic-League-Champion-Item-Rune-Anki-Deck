# Annie — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4033194.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:annie:overview:L1` | A | supported draft | unverified |
| `champ:annie:p:recognize:L2` | A | supported draft | proposed_unverified |
| `champ:annie:q:recognize:L2` | A | supported draft | unverified |
| `champ:annie:w:recognize:L2` | A | supported draft | unverified |
| `champ:annie:e:recognize:L2` | A | supported draft | unverified |
| `champ:annie:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.stun` | yes |
| P | `P.starts_ready` | yes |
| Q | `Q.targeted_damage` | yes |
| Q | `Q.kill_refund` | yes |
| W | `W.cone_damage` | yes |
| E | `E.shield` | yes |
| E | `E.move_speed` | yes |
| E | `E.retaliation` | yes |
| R | `R.summon_damage` | yes |
| R | `R.pet_damage` | yes |
| R | `R.pet_control` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Use the detailed stack rule: Q generates a stack on hitting an enemy, while her other abilities generate stacks on casting.", "source_ids": ["riot:P", "wiki:P"], "topic": "Riot's four-spell summary does not specify Q's hit requirement."}
- {"resolution": "Include attacks and damaging spells, supported by Riot and the Wiki's detailed description. Retain specific retaliation exceptions in QA metadata.", "source_ids": ["riot:E", "wiki:E"], "topic": "The Wiki's short E summary mentions basic attacks, while its detailed description and Riot include broader retaliation."}
- {"resolution": "The detailed Wiki rule supports Q generating stacks on hitting an enemy and other abilities on casting. The draft appropriately uses that qualification.", "source_ids": ["riot:P", "wiki:P"], "topic": "Riot's casting summary omits Q's hit requirement."}
- {"resolution": "The Wiki explicitly supplies first-landing guidance, supporting the draft's landing-order explanation despite its separate next-cast wording.", "source_ids": ["wiki:P", "riot:P"], "topic": "Passive descriptions alternate between next cast and first ability to land."}
- {"resolution": "Riot and the detailed Wiki description support retaliation from damaging attacks and spells. The narrower Wiki summary does not justify removing spell retaliation; reported exceptions remain QA metadata.", "source_ids": ["riot:E", "wiki:E"], "topic": "The Wiki's short E summary mentions only basic attacks."}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Evidence is pinned to the supplied Data Dragon release and Wiki revision; no current patch equivalence is established.
- Official demonstration frames do not establish current-client or skin-specific visual behavior.
- Wiki map-specific changes, pending-test notes and historical or skin material are not used as general mechanics.
- Tibbers has complex pet behavior beyond the beginner card; reported bugs and untested recast interactions remain unresolved.
- The supplied evidence is version-pinned and establishes no equivalence to the current game patch.
- The passive counter description is text-supported; this check does not verify the supplied demonstration frames or current-client visuals.
- E retaliation exceptions involving Noxious Trap and Jack in the Box are reported bugs without independent verification.
- R recast activation interactions remain advanced QA concerns: Experimental Hexplate is described as a bug, and Force Pulse is explicitly pending testing.
- All six drafts remain unapproved; this assessment provides neither human approval nor visual verification.

## Cooldown topics (no cards created)

- {"priority": "B", "reason": "Kill-based cooldown reduction affects how often Annie can use her targeted fireball.", "slot": "Q", "source_ids": ["wiki:Q"]}
- {"priority": "A", "reason": "Availability affects access to her cone and its potential area stun.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "A", "reason": "Availability affects shielding, movement speed and retaliation.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Initial summon availability matters for her area threat; recasting commands the existing pet.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

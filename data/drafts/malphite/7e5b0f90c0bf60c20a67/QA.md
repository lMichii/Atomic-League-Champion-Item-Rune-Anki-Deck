# Malphite — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4007956.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:malphite:overview:L1` | A | supported draft | unverified |
| `champ:malphite:p:recognize:L2` | A | supported draft | unverified |
| `champ:malphite:q:recognize:L2` | B | supported draft | unverified |
| `champ:malphite:w:recognize:L2` | B | supported draft | unverified |
| `champ:malphite:e:recognize:L2` | A | supported draft | unverified |
| `champ:malphite:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.shield` | yes |
| P | `P.recharge` | yes |
| Q | `Q.damage` | yes |
| Q | `Q.speed_steal` | yes |
| W | `W.armor` | yes |
| W | `W.empowered_attack` | yes |
| W | `W.cone` | yes |
| E | `E.area_damage` | yes |
| E | `E.attack_speed_reduction` | yes |
| R | `R.dash` | yes |
| R | `R.displacement_immunity` | yes |
| R | `R.impact` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Use the Wiki's specific qualification: damage absorbed by shields does not restart recharge. Do not interpret Riot's shorter wording as an every-hit rule.", "source_ids": ["riot:P", "wiki:P"], "topic": "Passive recharge wording"}
- {"resolution": "The Wiki supplies a specific exception to Riot's abbreviated recharge wording: shield-absorbed damage does not restart recharge. The draft includes this qualification.", "source_ids": ["riot:P", "wiki:P"], "topic": "Passive recharge trigger"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- The frozen Data Dragon release does not establish a game patch label.
- Official demonstration frames do not verify current-client or skin-specific appearance. The previously asserted passive visual transition was removed.
- Counterplay and fight-starting role guidance are teaching inferences grounded in the supplied effects.
- MR build guidance was removed because the packet does not support it; AP focus is supported by supplied spell scaling.
- Several core mechanics are supplied only by the Wiki because Riot's summaries omit them.
- Skin lore and specialized mode details were not used as standard ability mechanics.
- This review checks supplied textual evidence only; it does not provide human approval or visual verification.
- The pinned Data Dragon release does not establish a game patch label.
- Several required mechanics rely on the supplied Wiki excerpt because Riot's summaries omit them.
- R's crowd-control resistance must remain distinct from invulnerability, casting while grounded, and cancellation through death or documented nonfatal interruption. The draft preserves that distinction.
- The L1 AP statement is supported across the supplied ability formulas, although its attached citations show only E and R.
- No passive visual cue is asserted; the demonstration frames do not establish current-client or skin-specific appearance.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Availability of his rapid area knockup strongly affects engage threat.", "slot": "R", "source_ids": ["wiki:R"]}
- {"priority": "A", "reason": "Availability of the nearby attack-speed reduction matters when committing to basic-attack trades.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "B", "reason": "Availability of the targeted slow and speed gain affects chasing and spacing.", "slot": "Q", "source_ids": ["wiki:Q"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

# Anivia — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 3891994.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:anivia:overview:L1` | B | supported draft | unverified |
| `champ:anivia:p:recognize:L2` | A | supported draft | proposed_unverified |
| `champ:anivia:q:recognize:L2` | A | supported draft | unverified |
| `champ:anivia:w:recognize:L2` | A | supported draft | unverified |
| `champ:anivia:e:recognize:L2` | A | supported draft | unverified |
| `champ:anivia:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.egg` | yes |
| P | `P.revive` | yes |
| Q | `Q.projectile` | yes |
| Q | `Q.explosion` | yes |
| Q | `Q.recast` | yes |
| W | `W.terrain` | yes |
| W | `W.temporary` | yes |
| E | `E.targeted_damage` | yes |
| E | `E.double_damage` | yes |
| R | `R.toggle` | yes |
| R | `R.damage_slow` | yes |
| R | `R.growth` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Describe survival-dependent revival without guaranteeing full health on completion; distinguish initial health restoration from remaining health at revival.", "source_ids": ["riot:P", "wiki:P"], "topic": "Rebirth health restoration timing"}
- {"resolution": "Retain the fully formed storm requirement shared by Riot and the detailed Wiki mechanics.", "source_ids": ["riot:E", "wiki:E"], "topic": "Frostbite storm qualification"}
- {"resolution": "Use the detailed distance and cast-inhibiting crowd-control rules; do not claim she must stand inside the storm or that every disable interrupts it.", "source_ids": ["wiki:R", "wiki:R"], "topic": "Glacial Storm maintenance and interruption"}
- {"resolution": "Completed revival at full health remains unresolved: Riot's summary says full health, while the detailed Wiki distinguishes initial restoration from current health at revival. The draft correctly avoids guaranteeing completion health.", "source_ids": ["riot:P", "wiki:P"], "topic": "Rebirth health restoration timing"}
- {"resolution": "Use Riot and the detailed Wiki requirement of a fully formed storm. The abbreviated Wiki statement omits this condition; the draft retains it.", "source_ids": ["riot:E", "wiki:E"], "topic": "Frostbite storm qualification"}
- {"resolution": "Prefer the detailed distance, mana and cast-inhibiting crowd-control rules over the abbreviated interruption summary. The draft makes no universal interruption claim.", "source_ids": ["wiki:R", "wiki:R"], "topic": "Glacial Storm maintenance and interruption"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- The overview names the three damaging spells with supplied magic-damage and AP-scaling evidence; it does not generalize these properties to Crystallize.
- Sources are frozen to the supplied releases; no current game patch or current-client verification is established.
- Passive visuals support only a tentative cue proposal, without skin-specific, color-specific or VFX verification.
- Counterplay and priority explanations are inferred teaching guidance grounded in the supplied effects.
- Wiki lore, skin descriptions and pending-test notes are not additional mechanics evidence.
- This is a text evidence support check, not human approval or visual verification; all six drafts remain unapproved.
- The passive visual description is mechanically supported, but its appearance and current-client accuracy are not verified.
- Frostbite's qualifying mark must still exist at impact. The draft's general recent-hit explanation is supported and does not guarantee bonus damage from cast-time qualification.
- Storm persistence is conditional on distance, mana and interruption rules. Their omission is acceptable introductory simplification, not evidence of unconditional persistence.
- Crystallize knockback speed remains explicitly unverified; no draft claim depends on it.
- Evidence is frozen to the supplied versions and does not establish current-patch accuracy.
- Counterplay and priorities are reasonable mechanic-grounded inferences. No visible inference, confidence or development labels appear in the learning text.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Stun availability affects her ability to stop enemies and set up damage.", "slot": "Q", "source_ids": ["wiki:Q"]}
- {"priority": "A", "reason": "Wall availability affects whether she can block an approach or escape route.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "B", "reason": "Repeated targeted damage matters after qualifying hits enable its bonus.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Turning the storm off or interrupting it affects when she can establish the area again.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

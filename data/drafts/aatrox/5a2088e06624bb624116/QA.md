# Aatrox — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4013021.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:aatrox:overview:L1` | B | supported draft | unverified |
| `champ:aatrox:p:recognize:L2` | B | supported draft | unverified |
| `champ:aatrox:q:recognize:L2` | A | supported draft | unverified |
| `champ:aatrox:w:recognize:L2` | A | supported draft | unverified |
| `champ:aatrox:e:recognize:L2` | A | supported draft | unverified |
| `champ:aatrox:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.empowered_attack` | yes |
| Q | `Q.three_strikes` | yes |
| Q | `Q.sweetspot` | yes |
| W | `W.first_hit` | yes |
| W | `W.delayed_pull` | yes |
| E | `E.damage_healing` | yes |
| E | `E.dash` | yes |
| R | `R.empowered_form` | yes |
| R | `R.fear` | yes |
| R | `R.takedown_extension` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Use the detailed minion qualification: the passive heals Aatrox, but its healing is reduced against minions. Do not imply healing always equals all bonus damage dealt.", "source_ids": ["riot:P", "wiki:P"], "topic": "The abbreviated passive healing summaries omit the detailed minion reduction."}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Evidence is pinned to supplied Data Dragon and Wiki versions; live patch equivalence is not established.
- The supplied passive frames are demonstration evidence, not current-client or skin-specific visual verification.
- Counterplay, priority reasons and the broad learning focus are teaching interpretations grounded in the supplied mechanics.
- Detailed timing, hitbox, terrain and resurrection interactions remain outside the beginner explanations.
- No unresolved contradiction was identified in the frozen core mechanics.
- Evidence is version-pinned; equivalence to the live game is not established.
- Passive healing summaries omit the detailed minion reduction, but the draft includes it; this is an abbreviation rather than an unresolved contradiction.
- The overview's attack-damage and sustained-fighting focus is a supported teaching synthesis, not evidence of an optimal item build.
- Advanced hitbox, timing, terrain and resurrection details are omitted without contradicting the required general mechanics.
- No passive readiness cue is claimed. The supplied demonstration frames do not establish current-client or skin-specific visual verification.
- These checks provide AI support only; they do not constitute human approval or visual verification.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Track availability of the repeated strikes and knockups, including the recast window.", "slot": "Q", "source_ids": ["wiki:Q"]}
- {"priority": "A", "reason": "Track availability of the chain's slow and delayed pull.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "A", "reason": "Track dash availability because it changes positioning during other abilities.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Track availability of the empowered form because it increases fighting threat.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

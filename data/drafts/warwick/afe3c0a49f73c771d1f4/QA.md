# Warwick — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 3960181.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:warwick:overview:L1` | A | supported draft | unverified |
| `champ:warwick:p:recognize:L2` | B | supported draft | unverified |
| `champ:warwick:q:recognize:L2` | A | supported draft | unverified |
| `champ:warwick:w:recognize:L2` | B | supported draft | unverified |
| `champ:warwick:e:recognize:L2` | A | supported draft | unverified |
| `champ:warwick:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.bonus_magic_damage` | yes |
| P | `P.low_health_healing` | yes |
| Q | `Q.bite_and_heal` | yes |
| Q | `Q.hold_and_follow` | yes |
| Q | `Q.displacement_immunity` | yes |
| W | `W.hunt_low_health` | yes |
| W | `W.attack_speed` | yes |
| W | `W.stronger_low_health_bonuses` | yes |
| W | `W.active_hunt` | yes |
| E | `E.damage_reduction` | yes |
| E | `E.fear` | yes |
| R | `R.directional_leap` | yes |
| R | `R.suppression` | yes |
| R | `R.damage_and_healing` | yes |
| R | `R.leap_cc_immunity` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Retain stronger healing below one-quarter health without choosing the disputed triple or 250% multiplier.", "source_ids": ["riot:P", "wiki:P"], "topic": "Passive healing multiplier"}
- {"resolution": "Retain stronger bonuses against very wounded enemies without choosing an exact threshold or multiplier; Riot and Wiki disagree, and Wiki is internally inconsistent.", "source_ids": ["riot:W", "wiki:W"], "topic": "Blood Hunt enhanced bonuses"}
- {"resolution": "Retain temporary damage reduction without choosing between the stated maximum durations of 2.5 and 2.75 seconds.", "source_ids": ["riot:E", "wiki:E"], "topic": "Primal Howl protection duration"}
- {"resolution": "Unresolved exact multiplier: Riot says triple healing below 25% health; Wiki says 250%. The draft correctly retains only stronger healing.", "source_ids": ["riot:P", "wiki:P"], "topic": "Passive healing multiplier"}
- {"resolution": "Unresolved threshold and multiplier: Riot specifies triple below 25%; Wiki variously specifies enhancement below 20% and doubling below 25%. The draft correctly retains the supported general increase.", "source_ids": ["riot:W", "wiki:W"], "topic": "Blood Hunt enhanced bonuses"}
- {"resolution": "Unresolved maximum protection duration: Riot states 2.5 seconds and Wiki states up to 2.75 seconds. The draft correctly avoids an exact duration.", "source_ids": ["riot:E", "wiki:E"], "topic": "Primal Howl protection duration"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Evidence is frozen to the supplied Data Dragon release and Wiki revision; it does not establish current-patch behavior.
- Official demonstration frames do not establish current-client or skin-specific visual behavior.
- Wiki pending-test notes and documented bugs are not promoted to universal rules.
- Q tracking and interruption, W detection, E/R interaction and R channel protection have advanced exceptions retained in card metadata.
- Counterplay and the broad AD learning focus are teaching recommendations grounded in the supplied effects and ratios; no optimal build is established.
- This support check establishes neither human approval nor visual verification; supplied frames remain unverified.
- Frozen excerpts do not establish current-patch behavior.
- Q tracking exceptions and cooldown-refund reliability remain QA caveats; the qualified tracking wording does not promise universal following.
- W's Nexus Obelisk exception, decoy detection and attack-speed timing are advanced qualifications; the draft does not claim unrestricted vision or exhaustive eligibility.
- E's R-triggered howl can preserve protection. The draft does not claim that every howl ends damage reduction.
- R target protection is evaluated at collision; later spell shields do not block an existing channel. Suppression removal can leave a nondamaging channel, and a specific Singed interaction qualifies channel interruption.
- AD scaling supports the broad learning focus, but does not establish an optimal build. Expanding AD to attack damage would optionally improve beginner clarity.
- No provenance, confidence or development labels appear in the answer or counterplay text; UNAPPROVED labels remain in metadata.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Availability determines access to bite healing, movement tracking and displacement immunity.", "slot": "Q", "source_ids": ["wiki:Q"]}
- {"priority": "B", "reason": "Active availability determines whether he can hunt a nearby healthy champion.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "A", "reason": "Availability determines access to damage reduction and nearby fear.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Availability determines his major leap and suppression threat.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

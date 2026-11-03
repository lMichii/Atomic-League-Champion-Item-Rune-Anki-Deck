# Amumu — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4007948.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:amumu:overview:L1` | A | supported draft | unverified |
| `champ:amumu:p:recognize:L2` | B | supported draft | unverified |
| `champ:amumu:q:recognize:L2` | A | supported draft | unverified |
| `champ:amumu:w:recognize:L2` | B | supported draft | unverified |
| `champ:amumu:e:recognize:L2` | B | supported draft | unverified |
| `champ:amumu:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.curse` | yes |
| P | `P.magic_amplification` | yes |
| Q | `Q.projectile_hit` | yes |
| Q | `Q.dash` | yes |
| Q | `Q.charges` | yes |
| W | `W.toggle_damage` | yes |
| W | `W.curse_refresh` | yes |
| E | `E.physical_reduction` | yes |
| E | `E.area_damage` | yes |
| E | `E.cooldown_reduction` | yes |
| R | `R.area_damage_stun` | yes |
| R | `R.curse` | yes |

## Findings

- {"code": "media_url_missing", "name": "amumu_p.webm"}

## Source conflicts

- {"resolution": "Use Wiki's basic-attack trigger to qualify Riot's broad wording. Retain blocked attacks, blindness misses and repeated on-hit interactions in metadata without removing the general effect.", "source_ids": ["riot:E", "wiki:E"], "topic": "Riot describes E cooldown reduction whenever Amumu is hit; Wiki specifies basic attacks and detailed hit interactions."}
- {"resolution": "The draft appropriately uses Wiki's more specific basic-attack trigger. Riot's broader wording does not establish that spells or every damage tick reduce the cooldown. Detailed hit interactions remain in metadata.", "source_ids": ["riot:E", "wiki:E"], "topic": "E cooldown reduction: Riot says each time Amumu is hit; Wiki specifies basic attacks and on-hit interactions."}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Evidence is frozen to the supplied Data Dragon release and Wiki revision; current-client behavior was not verified.
- The game patch label is unknown and must not be inferred from the Data Dragon version.
- No visible passive cue is established by the supplied evidence.
- Counterplay and the broad tank-stat learning focus are inferred teaching guidance.
- Q blocker advice specifies the reader's own team's minions, which are enemies of Amumu, to resolve the previous allegiance ambiguity.
- Supported advanced interactions are retained in metadata; the answers do not assert universal shield bypass, complete damage negation or immediate amplification of R's own damage.
- Wiki skin and lore material was excluded from mechanics.
- Assessment uses only supplied frozen excerpts; current-client behavior and visuals are unverified.
- The L1 tank-stat build focus is inferred teaching guidance, not an evidence-established optimal build.
- Counterplay follows the supplied mechanics as conditional advice, without guaranteed outcomes or invented timings.
- Supported advanced exceptions are retained in draft metadata; their omission from concise answers does not make these general descriptions misleading.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Charge replenishment and the interval between casts govern repeated engage threats.", "slot": "Q", "source_ids": ["wiki:Q"]}
- {"priority": "B", "reason": "Incoming basic attacks change when his area damage becomes available again.", "slot": "E", "source_ids": ["riot:E", "wiki:E"]}
- {"priority": "A", "reason": "Availability of the area stun strongly affects teamfight engagement.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

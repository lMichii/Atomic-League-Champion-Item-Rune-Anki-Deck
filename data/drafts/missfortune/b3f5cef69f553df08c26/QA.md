# Miss Fortune — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4036014.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:missfortune:overview:L1` | B | supported draft | unverified |
| `champ:missfortune:p:recognize:L2` | B | supported draft | unverified |
| `champ:missfortune:q:recognize:L2` | B | supported draft | unverified |
| `champ:missfortune:w:recognize:L2` | B | supported draft | unverified |
| `champ:missfortune:e:recognize:L2` | A | supported draft | unverified |
| `champ:missfortune:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.new_target_damage` | yes |
| Q | `Q.bouncing_damage` | yes |
| Q | `Q.love_tap` | yes |
| W | `W.passive_movement_speed` | yes |
| W | `W.active_attack_speed` | yes |
| W | `W.instant_movement_bonus` | yes |
| W | `W.love_tap_cooldown` | yes |
| E | `E.area_damage` | yes |
| E | `E.slow` | yes |
| E | `E.area_vision` | yes |
| R | `R.channeled_cone_damage` | yes |
| R | `R.wave_critical_strikes` | yes |

## Findings

- {"code": "source_unavailable", "message": "HTTP Error 404: Not Found", "url": "https://www.leagueoflegends.com/en-us/champions/miss-fortune/"}

## Source conflicts

- {"resolution": "Use Wiki's more specific damage condition, explained as excluding repeated damage over time. Retain its zero-damage exception in metadata.", "source_ids": ["riot:W", "wiki:W"], "topic": "Strut's passive movement-speed condition"}
- {"resolution": "Use Wiki's detailed non-periodic-damage condition to qualify Riot's broad 'not attacked' summary. Retain the zero-damage exception in metadata; its omission does not make this beginner explanation misleading.", "source_ids": ["riot:W", "wiki:W"], "topic": "Strut movement-speed damage condition"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- The Riot champion page returned HTTP 404; supplied Riot evidence comes from pinned Data Dragon excerpts.
- Data Dragon version numbering does not establish a game patch label.
- The tentative passive visual proposal remains in metadata only; supplied clip frames do not establish current-client or skin-specific appearance.
- Wiki excerpts include Arena differences, skin material and pending-test notes; these are excluded from the learning answers.
- The overview's AD focus and counterplay recommendations are teaching inferences grounded in the supplied mechanics.
- All frozen core mechanics are retained. Advanced exceptions are scoped in metadata without turning general behavior into universal rules.
- The validation error 'Unknown verifier source' remains unresolved; this content check does not establish verifier provenance.
- Pinned Data Dragon excerpts and the supplied Wiki revision do not establish current-client accuracy or a game patch label; the Riot champion page was unavailable.
- Bullet Time's precise unseen-location reveal conditions remain pending testing in the supplied source and require QA before use.
- The passive visual cue remains unverified and appropriately excluded from card-facing text.
- The overview's AD focus is a supported teaching inference from physical damage and AD scaling, not evidence of an optimal build.
- This review provides AI support checking only; it does not constitute human approval or visual verification.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Track availability of her major channeled area-damage threat.", "slot": "R", "source_ids": ["riot:R", "wiki:R"]}
- {"priority": "A", "reason": "Track availability of the area slow that restricts enemy movement.", "slot": "E", "source_ids": ["riot:E", "wiki:E"]}
- {"priority": "B", "reason": "Her attack-speed boost affects trades, and Love Tap reduces its remaining cooldown.", "slot": "W", "source_ids": ["riot:W", "wiki:W"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

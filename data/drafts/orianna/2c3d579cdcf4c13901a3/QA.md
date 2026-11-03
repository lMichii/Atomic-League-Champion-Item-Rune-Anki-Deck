# Orianna — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 3892665.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:orianna:overview:L1` | A | supported draft | unverified |
| `champ:orianna:p:recognize:L2` | B | supported draft | proposed_unverified |
| `champ:orianna:q:recognize:L2` | B | supported draft | unverified |
| `champ:orianna:w:recognize:L2` | B | supported draft | unverified |
| `champ:orianna:e:recognize:L2` | A | supported draft | unverified |
| `champ:orianna:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.bonus_magic_damage` | yes |
| P | `P.repeated_target` | yes |
| Q | `Q.position_ball` | yes |
| Q | `Q.magic_damage` | yes |
| W | `W.pulse_damage` | yes |
| W | `W.ally_speed` | yes |
| W | `W.enemy_slow` | yes |
| E | `E.attach_shield` | yes |
| E | `E.path_damage` | yes |
| E | `E.carrier_resistances` | yes |
| R | `R.area_damage` | yes |
| R | `R.delayed_displacement` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Retain the supported delayed displacement toward the Ball. Leave terrain traversal unresolved without asserting either wall interaction.", "source_ids": ["wiki:R", "riot:R"], "topic": "The Wiki active description excludes displacement through terrain, while its notes allow passage through walls; Riot does not resolve the conflict."}
- {"resolution": "Describe the Ball as the shockwave source without asserting a precise end-of-cast positioning rule.", "source_ids": ["wiki:R", "riot:R"], "topic": "R's end-of-cast positioning notes ambiguously refer to the caster and the Ball's attached carrier."}
- {"resolution": "Keep terrain traversal unresolved for QA. The supported general displacement remains covered; the draft asserts neither wall outcome.", "source_ids": ["wiki:R", "riot:R"], "topic": "Wiki R's active description excludes displacement through terrain, but its notes allow passage through walls. Riot does not resolve this."}
- {"resolution": "Keep the precise end-of-cast origin rule unresolved for QA. The general Ball-centered description is supported.", "source_ids": ["wiki:R", "riot:R"], "topic": "Wiki R's positioning notes refer ambiguously to both the caster and the attached carrier."}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Only the supplied frozen evidence was used; no current-client verification or patch inference was performed.
- Counterplay, priorities and the AP learning focus are inferred teaching guidance grounded in the supplied mechanics.
- The passive buff-bar cue is a tentative proposal supported by Wiki text, not visually verified by the supplied demonstration frames.
- Q projectile-blocker interactions remain unresolved and are not treated as established mechanics.
- R terrain traversal and precise end-of-cast origin remain unresolved.
- Ball retrieval, leash limits, carrier state, interception and travel-time casting restrictions create advanced positioning exceptions.
- Q persistence wording allows further commands to reposition the Ball rather than treating retrieval and leash limits as exhaustive.
- Arena-specific values, historical material, skin descriptions and transcluded pet ability labels were not used to establish standard ability effects.
- The passive buff-bar cue is supported by wiki:P text but is not visually verified; the supplied frames do not establish its appearance.
- Q projectile-blocker outcomes remain explicitly pending or questioned in the evidence.
- The AP focus is teaching guidance supported by damage and shield scaling, not evidence of an optimal build.
- Omitted stack expiry, lingering slow decay, temporary shield duration and advanced travel or carrier exceptions do not make these qualified beginner descriptions misleading.
- Counterplay and priority judgments follow from supplied mechanics without guaranteed outcomes or invented timings.
- UNAPPROVED and other provenance labels occur in metadata, not card-facing wording. This check does not confer human approval or current-client verification.

## Cooldown topics (no cards created)

- {"priority": "B", "reason": "Ball repositioning availability affects where subsequent area abilities can threaten.", "slot": "Q", "source_ids": ["wiki:Q"]}
- {"priority": "B", "reason": "Pulse availability affects access to movement control.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "A", "reason": "Shield availability affects defensive protection and moving the Ball onto an ally.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Shockwave availability determines access to her major area displacement threat.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

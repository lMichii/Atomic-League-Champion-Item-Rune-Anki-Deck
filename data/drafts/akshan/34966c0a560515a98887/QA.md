# Akshan — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4091133.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:akshan:overview:L1` | B | supported draft | unverified |
| `champ:akshan:p:recognize:L2` | A | supported draft | proposed_unverified |
| `champ:akshan:q:recognize:L2` | B | supported draft | unverified |
| `champ:akshan:w:recognize:L2` | A | supported draft | unverified |
| `champ:akshan:e:recognize:L2` | A | supported draft | unverified |
| `champ:akshan:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.three_hit` | yes |
| P | `P.second_shot` | yes |
| P | `P.cancel_speed` | yes |
| Q | `Q.boomerang` | yes |
| Q | `Q.range_extension` | yes |
| Q | `Q.champion_speed` | yes |
| Q | `Q.reveal` | yes |
| W | `W.scoundrel_marks` | yes |
| W | `W.revenge_revive` | yes |
| W | `W.camouflage` | yes |
| W | `W.pursuit` | yes |
| E | `E.terrain_swing` | yes |
| E | `E.automatic_shots` | yes |
| E | `E.dismount` | yes |
| E | `E.takedown_reset` | yes |
| R | `R.charge` | yes |
| R | `R.missing_health_damage` | yes |
| R | `R.interception` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Use qualifying takedown language, retaining recent-damage and state restrictions in metadata.", "source_ids": ["riot:W", "wiki:W"], "topic": "W kill summary versus detailed takedown trigger"}
- {"resolution": "Preserve the general revival mechanic; leave the alive requirement and zombie-state allowance for advanced-state QA.", "source_ids": ["wiki:W", "riot:W"], "topic": "W alive requirement versus zombie-state allowance"}
- {"resolution": "Describe automatic shots at eligible enemies without claiming nearest-enemy selection is universal.", "source_ids": ["riot:E", "wiki:E"], "topic": "E proximity summary versus targeting priority overrides"}
- {"resolution": "Use a refresh with a brief remaining cooldown rather than promising immediate availability.", "source_ids": ["wiki:E", "riot:E"], "topic": "E reset shorthand versus detailed remaining cooldown"}
- {"resolution": "Scope missing-health scaling to champions and structures and explicitly distinguish minion execution.", "source_ids": ["riot:R", "wiki:R"], "topic": "R general damage summary versus minion execution"}
- {"resolution": "The qualified takedown wording preserves the supported general mechanic. Recent damage remains a restriction; the alive requirement versus zombie-state allowance needs advanced-state QA.", "source_ids": ["riot:W", "wiki:W"], "topic": "W kill summary, qualifying takedowns and state restrictions"}
- {"resolution": "The detailed terrain-or-brush wording agrees with Riot and supports the draft; the Wiki's introductory terrain-and-brush wording is inconsistent with its detailed description.", "source_ids": ["riot:W", "wiki:W"], "topic": "W camouflage terrain-or-brush versus terrain-and-brush wording"}
- {"resolution": "Eligible-enemy wording avoids treating the nearest-enemy summary as universal; detailed targeting priorities remain separate.", "source_ids": ["riot:E", "wiki:E"], "topic": "E proximity summary versus targeting overrides"}
- {"resolution": "The draft correctly retains a brief remaining cooldown instead of interpreting reset shorthand as immediate availability.", "source_ids": ["wiki:E", "riot:E"], "topic": "E reset shorthand versus detailed cooldown"}
- {"resolution": "The draft correctly scopes missing-health scaling to champions and structures and distinguishes the Wiki's explicit minion execution.", "source_ids": ["riot:R", "wiki:R"], "topic": "R general damage summary versus minion execution"}

## Factual risks

- All six cards are UNAPPROVED drafts.
- AD focus is an inferred learning recommendation grounded in supplied physical attacks and AD scaling.
- The pinned Data Dragon release does not establish a game patch label.
- Official demonstration frames do not establish current-client or skin-specific visual verification.
- W revival and pursuit have recent-damage, state, facing, distance and mode-specific conditions beyond the beginner explanation.
- E has stage-specific crowd-control interactions and targeting priorities; pending-test measurements were excluded.
- R missing-health scaling is scoped to champions and structures because Wiki separately specifies minion execution.
- Wiki mode variants, bug notes, pending-test notes and unrelated skin material were not promoted into general mechanics.
- Conflict source references use only excerpt IDs present in the supplied packet.
- AD focus is a supported teaching inference, not evidence of an optimal build.
- W's qualifying takedown and pursuit wording is accurate but leaves recent-damage, state, facing and distance restrictions implicit; these qualifications must not be removed.
- E hook wall-edge behavior and final-jump measurements remain explicitly pending testing.
- The passive visual description is a text-supported proposal, not verified current-client or skin-specific visual evidence.
- The pinned Data Dragon version does not establish a game patch label.
- This review provides AI support checking only; it does not confer human approval or visual verification.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Availability determines access to a major movement tool, and champion takedowns can refresh it.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Availability matters when assessing the threat of a finishing volley.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

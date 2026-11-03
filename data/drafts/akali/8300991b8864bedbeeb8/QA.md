# Akali — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4008175.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:akali:overview:L1` | B | supported draft | unverified |
| `champ:akali:p:recognize:L2` | B | supported draft | unverified |
| `champ:akali:q:recognize:L2` | B | supported draft | unverified |
| `champ:akali:w:recognize:L2` | A | supported draft | unverified |
| `champ:akali:e:recognize:L2` | A | supported draft | unverified |
| `champ:akali:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.ring` | yes |
| P | `P.empowered_attack` | yes |
| P | `P.movement_speed` | yes |
| Q | `Q.cone_damage` | yes |
| Q | `Q.outer_slow` | yes |
| W | `W.shroud_protection` | yes |
| W | `W.action_reveal` | yes |
| W | `W.movement_speed` | yes |
| W | `W.energy` | yes |
| E | `E.flip_projectile` | yes |
| E | `E.mark` | yes |
| E | `E.return_dash` | yes |
| R | `R.initial_dash` | yes |
| R | `R.recast_execute_damage` | yes |

## Findings

- {"code": "media_url_missing", "name": "akali_p.webm"}

## Source conflicts

- {"resolution": "Leave the first dash's damage type unspecified while retaining champion targeting and path damage.", "source_ids": ["wiki:R", "riot:R"], "topic": "The Wiki's introductory R description says physical damage, while its detailed description says magic damage."}
- {"resolution": "Use the Wiki's more specific outer-range restriction for the slow.", "source_ids": ["riot:Q", "wiki:Q"], "topic": "Riot describes Q slowing without specifying which part of the cone applies it."}
- {"resolution": "Describe increasing missing-health damage rather than a guaranteed kill.", "source_ids": ["riot:R", "wiki:R"], "topic": "Riot's execution shorthand is clarified by the Wiki's missing-health damage description."}
- {"resolution": "Unresolved first-cast damage type: retain the supported damaging-dash core without specifying its type and preserve the QA flag.", "source_ids": ["wiki:R", "riot:R"], "topic": "The Wiki's introductory R description specifies physical damage, while its detailed description and damage records specify magic damage. Riot does not resolve the type."}
- {"resolution": "Use the Wiki's explicit outer-range restriction, as the draft does.", "source_ids": ["riot:Q", "wiki:Q"], "topic": "Riot's abbreviated Q description omits the slow's range restriction; the Wiki supplies it."}
- {"resolution": "Describe missing-health damage rather than an automatic kill, as the draft does.", "source_ids": ["riot:R", "wiki:R"], "topic": "Riot's execution shorthand is clarified by the Wiki's explicit missing-health damage mechanic."}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Evidence is frozen to the supplied Data Dragon release and Wiki revision; no game patch label is inferred.
- No visual frames were supplied, and the passive cue has not been verified in the current client.
- Wiki excerpts include mode-specific changes and unrelated skin material; these are excluded from the explanations.
- R has an unresolved first-dash damage-type conflict.
- Shroud invisibility and E tracking have advanced exceptions; neither should be read as unconditional protection or pursuit.
- Counterplay is inferred teaching guidance grounded in the described effects.
- The first R dash's damage type remains unresolved in the supplied evidence.
- The passive visual description is supported by text only; no visual verification was supplied. Opponents cannot see the ring, so its exit should not be taught as a directly visible enemy cue.
- Passive ring creation and empowerment have advanced restrictions retained in metadata; the answer presents their supported general mechanics.
- Shroud invisibility has dashing and recalling exceptions and does not establish damage immunity or protection from every detection effect.
- E recast initiation has targetability and realm restrictions; its dash can also be interrupted. The draft does not promise an unavoidable return.
- Evidence is frozen to the supplied releases and revision; this check provides neither current-client verification nor human approval.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Shroud availability determines access to invisibility and target-selection denial.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "A", "reason": "Shuriken Flip availability affects her ability to reposition and threaten a return engage.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Ultimate availability and its recast restrictions affect her engage and finishing threat.", "slot": "R", "source_ids": ["wiki:R"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

# Braum — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 4022592.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:201:overview:L1` | B | supported draft | unverified |
| `champ:201:p:recognize:L2` | A | supported draft | unverified |
| `champ:201:q:recognize:L2` | A | supported draft | unverified |
| `champ:201:w:recognize:L2` | B | supported draft | unverified |
| `champ:201:e:recognize:L2` | A | supported draft | unverified |
| `champ:201:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.stacking` | yes |
| P | `P.stun` | yes |
| P | `P.immunity_followup` | yes |
| Q | `Q.damage_slow` | yes |
| Q | `Q.passive_stack` | yes |
| W | `W.ally_dash` | yes |
| W | `W.resistances` | yes |
| E | `E.projectile_interception` | yes |
| E | `E.first_hit_negation` | yes |
| E | `E.directional_damage_reduction` | yes |
| R | `R.knockup` | yes |
| R | `R.damage` | yes |
| R | `R.slow_field` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Preserve interception, first-hit negation and subsequent reduction with directional and eligibility qualifications. Retain collision effects and detailed exceptions in metadata rather than implying universal protection.", "source_ids": ["riot:E", "wiki:E"], "topic": "Riot's broad projectile and first-attack wording is qualified by Wiki's detailed eligibility and champion-damage rules."}
- {"resolution": "The Wiki qualifies Riot's broad wording with projectile eligibility, champion-source first-instance negation and directional damage rules. The draft preserves all required general mechanics with appropriate qualifications. Detailed collision effects and exceptions can remain in metadata.", "source_ids": ["riot:E", "wiki:E"], "topic": "Scope of Unbreakable's projectile interception and damage negation."}

## Factual risks

- All six cards are UNAPPROVED drafts.
- The Data Dragon release is pinned; no game patch label is inferred.
- The prior passive visual description was removed because its exact sequence is not established by text. Demonstration frames are not current-client or skin-specific verification.
- Build focus is an inferred broad learning recommendation, not an optimal build.
- Wiki Arena differences and unrelated skin material are excluded.
- Unbreakable has complex projectile eligibility and damage-origin rules. Interception does not imply cancellation of collision effects, immunity to crowd control or damage reduction shared with allies.
- Pure true damage not consuming E's first-instance reduction does not establish that the damage is negated.
- E's pure-true-damage non-consumption rule does not establish true-damage negation. The draft's eligibility qualification avoids that claim; the interaction remains a QA consideration.
- E interception does not cancel collision effects or resulting areas of effect and does not grant allies Braum's damage reduction. The draft does not assert those broader protections.
- The L1 build focus is a broad inference supported by the tank role, defensive resistances and Q health scaling, rather than evidence of an optimal build.
- The supplied demonstration frames do not establish current-client passive visuals; no visual verification or human approval is provided by this check.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Shield availability determines whether Braum can intercept projectiles and deny incoming damage.", "slot": "E", "source_ids": ["riot:E", "wiki:E"]}
- {"priority": "A", "reason": "Ultimate availability changes the threat of a line knockup and lingering slow field.", "slot": "R", "source_ids": ["riot:R", "wiki:R"]}
- {"priority": "B", "reason": "Leap availability affects his ability to reach an ally and grant resistances.", "slot": "W", "source_ids": ["riot:W", "wiki:W"]}
- {"priority": "B", "reason": "Projectile availability affects his ranged slow and passive-stack setup.", "slot": "Q", "source_ids": ["riot:Q", "wiki:Q"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

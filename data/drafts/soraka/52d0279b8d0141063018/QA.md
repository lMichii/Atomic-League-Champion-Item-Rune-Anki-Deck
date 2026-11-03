# Soraka — unapproved generation QA

Six drafts only. Approved cards unchanged. No APKG generated, approval applied or publication performed.

Sources: Data Dragon 16.21.1; CommunityDragon 16.21; Wiki revision 3892689.
Game patch label: unknown (not inferred from asset release).

## Card review

| ID | Priority | AI source-support check | Visual QA |
| --- | --- | --- |
| `champ:soraka:overview:L1` | B | supported draft | unverified |
| `champ:soraka:p:recognize:L2` | B | supported draft | proposed_unverified |
| `champ:soraka:q:recognize:L2` | B | supported draft | unverified |
| `champ:soraka:w:recognize:L2` | A | supported draft | unverified |
| `champ:soraka:e:recognize:L2` | A | supported draft | unverified |
| `champ:soraka:r:recognize:L2` | A | supported draft | unverified |

## Supported core coverage

Core mechanics are required independently of advanced exceptions. The source taxonomy is in mechanics-inventory.json; detailed evidence and inference types stay out of learning text.

| Slot | Supported core ID | Included in explanation |
| --- | --- | --- |
| P | `P.ally_approach_speed` | yes |
| Q | `Q.area_damage_slow` | yes |
| Q | `Q.rejuvenation` | yes |
| Q | `Q.share_rejuvenation` | yes |
| W | `W.ally_heal` | yes |
| W | `W.rejuvenation_synergy` | yes |
| E | `E.silence_zone` | yes |
| E | `E.delayed_root` | yes |
| E | `E.two_damage_events` | yes |
| R | `R.global_heal` | yes |
| R | `R.low_health_bonus` | yes |

## Findings

None detected; this is not a guarantee of completeness.

## Source conflicts

- {"resolution": "Describe the delayed root for enemy champions, preserving the supported core without asserting its behavior for every enemy unit.", "source_ids": ["riot:E", "wiki:E"], "topic": "Equinox root target scope"}
- {"resolution": "The draft preserves the delayed-root core using enemy champions, the shared supported scope. Root behavior for other enemy units remains unresolved and requires QA only if broader wording is desired.", "source_ids": ["riot:E", "wiki:E"], "topic": "Equinox root target scope: Riot says all enemies; the Wiki explicitly describes enemy champions."}

## Factual risks

- All six cards are UNAPPROVED drafts.
- Evidence is pinned to Data Dragon 16.21.1 and Wiki revision 3892689; a live game patch is not established.
- Official passive clip frames are demonstrations, not current-client or skin-specific verification.
- Map-specific differences are present in the Wiki excerpts; the cards describe the supplied general mechanics.
- Counterplay and gameplay priorities are inferred teaching guidance grounded in the supplied effects.
- Advanced projectile, health-cost, cleanse and realm interactions are summarized in metadata rather than expanded into beginner answers.
- This check assesses supplied textual evidence only; it is neither human approval nor visual verification.
- Evidence is pinned to Data Dragon 16.21.1 and Wiki revision 3892689; current-client behavior and a live patch label are not established.
- The passive arrow description is textually supported by wiki:P, but the supplied demonstration frames do not establish current-client or skin-specific visuals.
- Q's general Rejuvenation description omits supported delivery and interception details. It must not be interpreted as guaranteeing immediate receipt; sharing can begin before Soraka receives the returning projectile.
- W's supported low-health casting restriction and health-cost exceptions are omitted beginner details, not contradicted by its qualified normal-cost description.
- The excerpts include map-specific differences and a reported immediate-respawn Wish bug; the draft makes no precise cost, scaling or cooldown promises affected by those details.
- AP as a learning focus is supported by supplied healing and damage ratios, but those ratios do not establish an optimal build.
- No internal provenance, confidence or development labels appear in the card-facing answers, counterplay or passive description; such labels remain in metadata.

## Cooldown topics (no cards created)

- {"priority": "A", "reason": "Track availability of her global heal before committing to a fight.", "slot": "R", "source_ids": ["wiki:R"]}
- {"priority": "A", "reason": "Track availability of her silence zone and delayed root when planning an engage.", "slot": "E", "source_ids": ["wiki:E"]}
- {"priority": "A", "reason": "Repeated targeted healing can affect attempts to finish an ally.", "slot": "W", "source_ids": ["wiki:W"]}
- {"priority": "B", "reason": "Starcall availability affects her access to Rejuvenation and cheaper allied healing.", "slot": "Q", "source_ids": ["wiki:Q", "wiki:W"]}

## Approval blockers

- All six cards are drafts requiring explicit editorial approval.
- All clips/cues need manual visual verification.
- Game patch label has not been independently established.

## Limits

- Data Dragon release is pinned; game patch label is not inferred from its numbering.
- Riot CDN clips are demonstrations, not current-client or skin-specific verification.
- Exact-quote matching does not prove semantic truth.
- AI verification is fallible and is not a human content or visual review.

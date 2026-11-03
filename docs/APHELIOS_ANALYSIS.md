# Aphelios source and learning analysis — 2026-11-01

Analysis preceded authoring. Current retrieval resolved Riot Data Dragon 16.21.1,
CommunityDragon 16.21 champion 523, and League Wiki revision 4022591. Asset release
does not establish a gameplay patch. The committed generation archive retains the
raw inputs, hashes, retrieval metadata and exact cited excerpts.

## Actual structure

Aphelios carries a main-hand and an off-hand weapon from an arsenal of five. The
main hand determines basic attacks and Q; ammunition consumption replaces an empty
weapon with the next reserve weapon and sends the depleted weapon to the back of
the queue. W swaps the equipped pair. E displays the next reserve weapon rather
than providing a conventional combat ability. These are explicit Riot descriptions.
[Current Riot champion page](https://www.leagueoflegends.com/en-us/champions/aphelios/),
[versioned Riot champion data](https://ddragon.leagueoflegends.com/cdn/16.21.1/data/en_US/champion/Aphelios.json).

The five attack purposes and distinct Q abilities need separate recognition goals:

| Weapon | Basic-attack purpose | Weapon-specific Q |
| --- | --- | --- |
| Calibrum | Range and ability-applied marks for long-range follow-up attacks | Moonshot: a directional shot that damages and marks |
| Severum | Healing; excess healing can shield | Onslaught: movement speed and alternating attacks with both weapons |
| Gravitum | Slowing attacks | Binding Eclipse: damage and root on targets affected by Gravitum |
| Infernum | Spreading damage behind the main target | Duskwave: cone damage followed by off-hand attacks |
| Crescendum | Returning blade, with accumulated mirror-chakram damage | Sentry: a placed sentry using the off-hand weapon |

Moonlight Vigil's follow-up depends on its weapon: empowered marks, healing,
enhanced slowing/root interaction, spreading area damage, or additional mirror
chakrams. The passive also replaces conventional skill-point upgrades with stat
choices while abilities unlock/improve automatically. Detailed eligibility,
critical-hit interactions, bug notes, pending tests and outdated numerical notes
require separation from beginner cores.
[Wiki evidence at the retrieved revision](https://wiki.leagueoflegends.com/en-us/Aphelios?oldid=4022591).

The complete retrieved kit has movement-speed assistance but no conventional dash
or blink. That absence is an inference from exhaustive kit coverage, not a direct
quoted assertion; draft facts must type it accordingly and keep a factual-risk
entry. Counterplay remains inferred guidance from cited effects.

## Implications for the pipeline

The five-slot Wiki parser fails because Riot's generic Q name differs from the
Wiki's grouping name. Discovering the live ability containers yields 15 sections;
their boundaries stop before pets/history and retain exact source locations.
The adaptive planner assigns every section a taught/merged/advanced-only/out-of-
scope disposition and validates every planned core independently of edge disputes.

The natural compact proposal is an overview, one system card, five weapon-purpose
cards, five Q cards, swapping and an ultimate card. The model selects and justifies
the actual inventory; Python does not hardcode this count or these weapon names.
Queue display and stat leveling can merge into the system card. Conditional R
effects can share one ultimate card, avoiding five repetitive base-cast lessons.

The primary CommunityDragon record exposes generic P/Q/W/R demonstrations, not
separate source-addressed Q clips for all weapons. A generic Q video therefore
cannot be copied to five variant cards. Versioned asset-directory icons and exact
Wiki-section icons are candidates for identification, with weapon-to-ability
matching still requiring explicit visual QA. Real generic clips and passive
frames remain review evidence, not proof of current-client appearance.

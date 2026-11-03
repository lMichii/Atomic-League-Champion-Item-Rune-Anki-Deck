# Phase 3.2 verification — 2026-11-01

Completed the Aphelios stress test from the interrupted repository checkpoint.
The saved 15-section source analysis, validated 14-card inventory, 28 cores and
real media were retained. The initial author had stopped at the usage limit;
there was no successfully authored/verified deck to publish or approve.
[Recovery record](PHASE3_2_RECOVERY.json) separates written work, rejected changes,
earlier failures and available historical token usage.

## Results and learning inventory

**14 unapproved drafts**, preserving the exact first 100 approved records in a
114-record proposed candidate:

| Kind | Count | Learning goal |
| --- | --- | --- |
| L1 overview | 1 | Weapon-dependent marksman, physical damage, broad AD orientation, mobility limits |
| L2 system | 1 | Equipped pair, ammunition, queue/E indicator, separate active cooldowns and unusual leveling |
| L2 weapon | 5 | Calibrum, Severum, Gravitum, Infernum and Crescendum attack purposes |
| L2 ability variant | 5 | Moonshot, Onslaught, Binding Eclipse, Duskwave and Sentry in their weapon contexts |
| L2 ordinary ability | 2 | Phase swapping and Moonlight Vigil with weapon-dependent effects |

Every live source section has an explicit coverage disposition. E is an indicator,
not an invented combat spell. All 28 frozen cores have answer quotations and a
passing final AI support check. This is a fallible source-consistency assessment,
not human fact QA or approval.

The corrected explanations distinguish primary ammunition costs from automatic
attacks, qualify which abilities generate returning chakrams, include Onslaught's
casting restrictions, and identify the ultimate's weapon at firing. Advanced
exceptions remain in metadata. No cooldown durations or supplementary cards were
generated. The system and ultimate lessons remain relatively dense and warrant
editorial judgment about beginner recall burden.

## Generic schema and implementation

- Adaptive source packets use schema v2 with live `kit_sections` and a versioned
  media catalog. Extra weapon/form/variant containers are discovered without a
  champion-name branch or a hardcoded card-count/weapon table.
- Inventory units support `overview`, `system`, `weapon`, `ability`,
  `ability_variant`, `form`, `stance`, `transformation` and `conditional_effect`.
  Units have canonical source subjects, explicit contexts, actual slot roles,
  relationships, pedagogical purposes, required cores and separate exceptions.
- IDs derive from source/context identities, independent of prose/order. Ordinary
  overview and P/Q/W/E/R identity patterns remain unchanged. Preview filenames
  derive from full IDs so variants cannot overwrite one another's Q page.
- Claims distinguish source assertions from exhaustive-kit inferences. The
  no-dash/blink conclusion and Crescendum spacing implications retain inference
  risks; they are not presented as direct source quotations in QA.
- The verifier now receives the same structured inference types that Python stores
  for Counterplay/build focus. Advice must still follow from cited effects. This
  fixes the interface mismatch without suppressing factual checks or adding labels
  to learning prose.
- Numeric checks cover both individual claims and uncited quantities elsewhere in
  an answer. Exact citations, all frozen identities/cores and section dispositions
  are validated. Missing cores cannot be excused by edge-case disputes.
- Checkpoints are bound to source/inventory hashes and the original model output
  receipt. Each accepted author result is saved immediately; resumed attempts append
  to prior history. `replay-generated-run` restores the retained draft seed.

The adaptive production/export approval path remains deliberately closed. No
approved model, CSS, stat formatter, field order, forward-template count, media or
scheduling records were changed. Other unusual champions have schema-level tests,
not generated champion content.

## Sources and media QA

Retained source versions: Data Dragon **16.21.1**, CommunityDragon **16.21**, Wiki
revision **4022591**. Gameplay patch remains independently unverified and its label
is hidden on both card faces. Source bytes, URLs, locations and hashes are archived.

All 14 drafts have real matched images. W and R have real Riot GIFs using the locked
v4 conversion. The generic Q demonstration is archived as review evidence and is
not assigned to any weapon-specific Q card.

Remaining review requirements:

- **Five Q animations unresolved:** Moonshot, Onslaught, Binding Eclipse, Duskwave
  and Sentry use the icon from the corresponding live Wiki ability section.
- Weapon/icon-to-ability matching needs explicit human visual review, including the
  versioned CDragon Calibrum icon and the Wiki-hosted variants.
- Passive/resource cues need review; the genuine passive clip and four sampled
  frames are retained.
- The primary R GIF does not independently verify every weapon-dependent effect.
- Current-client and skin-specific VFX are unverified. Inferred absence/spacing,
  broad AD teaching focus and source-scope qualifications remain editorial risks.

QA retains **11 source-scope records and 19 factual-risk entries**, including
overlapping observations from planning, authoring and verification. These counts
are not counts of distinct unresolved factual contradictions. Informational E
media findings preserve their original codes and explain why a combat animation
is not expected. No uncertain source/media status grants approval.

## Verification and reproducibility

- **70 tests passed**, zero failures/errors/skips, including real Anki
  import/reimport scheduling/review-history tests and every earlier regression.
- Tests cover non-five-slot structures, weapons/forms/stances/transformations,
  context identities, duplicate detection, conservative variant media matching,
  source/quantity rejection, required cores, inference separation, clean text,
  unknown-patch hiding, checkpoint integrity and append-only retry history.
- Aphelios content, inventory, proposal, QA, media manifest and previews replay
  byte-for-byte offline with network/model calls blocked. Braum's archived learning
  text, IDs, media, proposal and previews remain unchanged across the processor
  extension; only a new processor/run fingerprint is expected on replay.
- All **14 previews** passed real-browser checks for actual local media, v4
  styling, clean front/back text, hidden unknown patch, Counterplay and controls.
  R and system screenshots were visually inspected. This does not establish
  live-client or mobile Anki playback/visual matching.
- Both approved decks rebuilt with unchanged SHA-256 hashes:

| APKG | Cards | SHA-256 |
| --- | --- | --- |
| LoL_Pilot.apkg | 64 | `23a9f0813db46aacae014ed84d7e95ee4d24cd73ee0fff6f318ab84c396ea123` |
| LoL_Anki_Batch_01_100_Cards.apkg | 100 | `0f5525d460d1b3edfcaa560949884a54fa9fbae4626de2afe93ded5d2fea89d9` |

The retained successful path has three model receipts (inventory, repaired author,
final verifier): **93,855 input tokens and 22,187 output tokens** as reported by the
runtime. Inventory and repaired author were reused; final completion required one
new verifier call. These recorded totals are not replay charges and do not include
all earlier rejected/non-final experiments; the recovery record preserves their
available usage. The compact source packet avoids raw HTML/download catalogs and
duplicate provenance data in model inputs. No source/media research was repeated
during final recovery.

## Review and replay

- [Previews](../data/drafts/aphelios/c6569ae4b284ca4203c1/previews/index.html)
- [Card inventory and reasons](../data/drafts/aphelios/c6569ae4b284ca4203c1/card-inventory.json)
- [Structured QA](../data/drafts/aphelios/c6569ae4b284ca4203c1/qa.json)
- [Readable QA](../data/drafts/aphelios/c6569ae4b284ca4203c1/QA.md)
- [Media availability/matching](../data/drafts/aphelios/c6569ae4b284ca4203c1/media-report.json)
- [Kit analysis and section dispositions](../data/drafts/aphelios/c6569ae4b284ca4203c1/kit-analysis.json)
- [Unapproved proposal instructions](../data/drafts/aphelios/c6569ae4b284ca4203c1/REVIEW.md)

```powershell
python pipeline.py replay-generated-run data/drafts/aphelios/c6569ae4b284ca4203c1
python tools/run_tests.py
node tools/check_generation_preview.cjs data/drafts/aphelios/c6569ae4b284ca4203c1
```

Braum and Aphelios remain unapproved. No new APKG, publication, approval or mass
generation was performed; the generated proposal is rejected by `apply-review`.

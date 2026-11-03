# Item visual-learning prototype verification â€” 2026-11-03

The separate prototype contains 14 cards: the same five item overviews, one QSS L2,
three item-related L0s, and five existing glossary identities. No new items,
champions, batches or glossary concepts were generated. No AI/provider calls or
approval changes were made.

QSS has four compact sections: 90-second cooldown, removable crowd control including
suppression, airborne restrictions, and the difference from the Cleanse summoner
spell. Ignite, Exhaust and Realm of Death are omitted. Claims were checked against
the retained exact QSS excerpt and hash-validated HTML (Wiki revision 3729899),
not model memory or newly inferred gameplay changes. Grievous Wounds and Stasis
have shorter definitions with their original meaning retained.

| Existing glossary identity | Reused gameplay example | What to observe |
| --- | --- | --- |
| Charm | Ahri E | Target walks toward Ahri |
| Stun | Leona Q | Target stops after shield strike |
| Root / Snare | Morgana Q | Target held inside purple binding |
| Knock-up | Blitzcrank E | Target lifted off ground |
| Silence | Soraka E | Speech-bubble cue within zone; later root explicitly distinguished |
| Stasis | Bard R | Golden targets freeze, then resume |

All six GIFs were reused byte-for-byte. Sampled contact sheets were inspected;
FFmpeg fully decoded each file, and the GIF parser confirmed multiple frames and
infinite looping. These are representative examples, not claims of current-client
or patch-specific visual QA. Grievous Wounds and On-Hit remain text-only because no
inspected cached footage clearly demonstrates those mechanics. Suppression and
Nearsight have no existing glossary identities; no extra concepts were added.

The opt-in `learning_style` renderer highlights mechanic names with one reusable
palette. It delegates damage/stat terms to the unchanged v4 formatter. Optional
plain-text sections render only when supplied. No shared CSS/template/model or
field-schema changes are needed. The 17 fields, note type, stable keys/GUIDs,
numeric IDs and single forward card remain intact. Other card families can opt in
without changing existing champion output.

The original pilot/production/editorial content stores, editorial registry,
1,089-row champion index and existing complete 1,089-note APKG were hash-compared
before/after and are unchanged. Existing glossary definitions remain frozen in the
pilot store; their visual overlays are hash-bound in
`data/sources/items-glossary-visuals.json`. The test APKG updates those same note
identities. The separate item sidecar retains nine entries to avoid duplicating
the five glossary terms already in the main index.

Verification completed:

- `python pipeline.py item-prototype --offline`: 14 notes, 14 forward cards, 11
  media files (five icons, six GIFs); source hashes/excerpts and numeric evidence
  checked; SQLite integrity and all media references passed. Rebuilding the same
  inputs produced identical APKG bytes.
- Five focused item tests passed, including the real Rust-backed Anki importer.
  A temporary collection imported the 64-note pilot, then this prototype: 73 notes,
  with five existing glossary identities updated rather than duplicated. Champion
  fields and existing scheduling stayed unchanged. Two repeat imports preserved
  all note identities, card counts and scheduling. The user's collection was never
  opened.
- `node tools/check_item_preview.cjs`: all 14 previews passed at 850px and 360px,
  without horizontal overflow. Each of the six GIFs visibly changed frames in
  headless Chromium. Back links were clicked with navigation intercepted and
  matched their expected HTTPS destinations. No source links or patch footer
  appeared on fronts. QSS has exactly four sections. QSS and Stasis screenshots
  were visually inspected.
- `python pipeline.py run` passed the original pilot validation/build.
- `git diff --check` passed.

Browser playback was tested in headless desktop Chromium, not the desktop Anki
WebView or a mobile device. The actual Anki backend rendered the cards and verified
import/reimport, but does not test visual playback. Link targets and archived
sources were verified offline; live website availability was not retested.

The full repository suite (`python tools/run_tests.py`) completed: 129 tests,
120 passed, seven errors, two skips and zero assertion failures. Three errors
reference absent historical generated APKGs (`BackOnly`, `Reparaturen`, `Footer`);
four existing editorial HTTP tests encounter Windows socket permission error
10013 in this restricted environment. The optional editorial browser check and
an unavailable complete-lane artifact check were skipped. These unrelated
artifacts/workflows were not rebuilt or changed to satisfy the tests. The full log
is `build/items-visual-inspection/tests.log`; summary is `build/reports/tests.json`.
The five focused item tests were also run separately against the final inputs
and all passed, including rejection of changed source provenance/definitions and
duplicate glossary identities.

Outputs: `build/items-prototype/League_Anki_Items_Prototype_26.21.apkg` (about 3.6 MB),
`build/items-prototype/previews/index.html`, `report.json`, `browser-checks.json`
and `preservation-checks.json`. Build outputs remain separate from champion exports.
Rebuild only with `python pipeline.py item-prototype --offline`.

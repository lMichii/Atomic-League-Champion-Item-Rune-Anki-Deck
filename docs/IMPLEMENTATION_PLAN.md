# Foundational implementation plan

Scope: migrate and test the existing six pilots and 64 authored cards only.
Batch 01 remains an audited draft. No champion-wide generation or L3 authoring.

1. Freeze original hashes, v4 identity mapping and exact rendered fields/CSS/template
   contract; initialize Git. Preserve originals as read-only reference inputs.
2. Add a standard-library Python package and one CLI with separate ingestion,
   retrieval/cache, media, review, validation, rendering, packaging/report modules.
3. Migrate authored rows losslessly to a separate content store. Add stable entity
   IDs, status/QA/evidence metadata alongside (not inside) card prose. Save raw
   source snapshots independently, with source URLs, hashes, versions and unknown
   retrieval times explicitly recorded. Pin pilot source versions in config.
4. Freeze legacy CDragon `latest` by content hash without falsely relabeling it a
   pinned upstream release. Online refresh requires an explicit immutable version.
   Retrieve official Data Dragon first, use CDragon only for discovery, and support
   separately archived Wiki evidence without turning source prose into authored cards.
5. Add atomic hash-checked cache/downloads, bounded retries, offline failures,
   resumable per-resource runs, logs and content-based GIF processing. Reuse
   supplied media; emit proposals for changed assets rather than replace originals.
6. Require an inspectable, hash-bound change proposal and explicit reviewed apply
   for every curated addition/edit/deletion. Validate before writing; stale review
   must fail. Ingestion, fetch and build never change authored content.
7. Preserve renderer and ID algorithms exactly; make SQLite/ZIP serialization
   deterministic with a fixed recorded build epoch. Preserve model/deck IDs,
   17 fields, one forward template and existing GIF embedding. Export only
   referenced media. New namespaced IDs support terms/champions/items/runes.
8. Validate schemas/statuses, identity collisions, semantic duplicates, champion
   L1/PQWER coverage, media paths/hashes/formats, missing source evidence, fallback
   exceptions, APKG schema/media/foreign keys. Write JSON and readable reports;
   structural errors block export, inherited review warnings remain visible.
9. Test all pilots against the supplied APKG, byte-repeatability, cache recovery,
   review rejection, GIFs, and actual Anki import/reimport with preserved scheduling
   using an isolated optional Anki test environment. Document limits honestly if
   a real importer cannot be installed or run.
10. Document setup, offline and online CLI workflow, reviewed updates, test commands,
    schema extension for all champions and future items/runes/L3 in README/AGENTS.
    Recheck original-file hashes and leave Batch 01 unmerged.

Acceptance: all 64 original IDs/GUIDs/rendered fields and v4 style match; same
inputs yield byte-identical APKGs; no original curated/media bytes change; all six
pilots have one L1 and five L2 recognition rows; known gaps appear in reports;
tests prove reviewed updates and repeat imports do not add duplicates.

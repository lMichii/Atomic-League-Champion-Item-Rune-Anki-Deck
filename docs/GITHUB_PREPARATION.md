# GitHub preparation — 2026-11-03

## Findings and decisions

The original checkout contained about 5.65 GB of tracked files. Of that,
`data/prefetch/riot-videos/` accounted for 4.21 GB. Its champion subfolders
contain redundant downloaded videos and converted GIFs; the root `manifest.csv`
retains discovery URLs and download status. No production code or tests reference
that prefetch directory. Keep the downloads locally, but exclude them from new Git
history. `.gitignore` now does this, while retaining the manifest and utility.

The existing Git object packs occupy 3.47 GiB. Ignore rules do not remove committed
files or old objects. A normal commit in this checkout would still send its large
ancestry. GitHub limits a single push to 2 GiB and individual regular Git files to
100 MiB:
https://docs.github.com/en/get-started/using-git/troubleshooting-the-2-gb-push-limit
https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

Rather than rewrite this checkout, a separate upload snapshot is prepared at
`build/github-upload/`. It includes the current working versions of tracked files
and nonignored new files, including changes that predate this audit, except for
the prefetch champion subfolders. It has independent fresh Git history. The old
checkout, its index, branches, history and local data remain intact. No push is
performed. The snapshot manifest and verification results live beside it under
`build/github-preparation/`, outside the upload tree.

## Required for future work

- Keep `pipeline.py`, `lol_anki/`, `tests/`, `tools/`, configuration, README and
  project instructions. `python pipeline.py` remains the content workflow.
- Keep `data/content`, locks, source snapshots, editorial registry, source/media
  review records, immutable AI receipts, batch plans, checkpoints and repair
  history. The completed 173-champion inventory must not be regenerated simply
  to restore a checkout. Drafts remain unapproved unless separately reviewed.
- Keep frozen v4 inputs and `data/batch01/` assets: offline builds and regression
  checks depend on their exact bytes.
- Keep `LoL_Anki_Riot_Medien_Fetcher/`: the Batch 01 adapter and optional tests
  still import its code. Its legacy launchers are reference-only.
- Keep historical draft runs and model comparisons: regression tests explicitly
  read old Braum, Aphelios and Annie archives. They are not abandoned folders.
- Keep original ZIP/workbooks and their inventory. They are small protected
  reference inputs, not the cause of the upload failure.
- Keep the one existing Bard GIF referenced by the item prototype. A narrow
  ignore exception includes it; without that exception a fresh checkout loses
  the Stasis example. No media or content approval is granted by tracking it.
  The prototype's five existing item PNGs also have an explicit keep rule.

No feature folders were moved: observed dependencies make an arbitrary archive
move unsafe. No files were deleted and no original history was rewritten.

## Local data versus the Git backup

`build/`, `.cache/`, generated APKGs, duplicate fetcher media and most staging media
were already ignored. They remain local. The clean Git snapshot is therefore NOT
a complete backup of this working folder or of every champion's export media.
Back up this original checkout separately before changing computers or removing
anything. In particular, retain `data/batches/*/staging/*/media/`, all original
editorial inputs and the current complete APKG under `build/staging/` if you need
to reproduce the full 1,089-card export offline. Do not rely on fresh downloads to
reproduce pinned media. The frozen pilot and Batch 01 rebuild inputs stay in Git.

The new `.env` and `.part` exclusions prevent accidental inclusion of local
credentials and interrupted downloads in future commits. They do not sanitize
the old Git history or constitute a full secrets audit.

## Use the upload copy

Add `build/github-upload/` as an existing local repository in your GitHub client.
Its remote points to the same GitHub URL as this checkout. Inspect the snapshot
commit and push `main` from that copy. Do not push all branches from the original
checkout: those still contain the large ancestry. If GitHub already contains
commits, inspect them before reconciling histories; do not force-push blindly.

Continue work in the upload copy if it becomes the new primary Git checkout,
but remember that its ignored local media/cache are not carried over. Otherwise,
use the original workspace and make an explicit plan to migrate its Git history
later. The upload copy is a point-in-time snapshot and does not synchronize later
edits automatically.

## Verification

The source and copied files were compared with SHA-256 hashes. The upload tree
contains about 1.48 GB before Git compression (including nonignored local inputs);
its initial Git pack is about 649 MiB. Its largest retained file is
11,929,786 bytes. This is below the individual-file and single-push limits without
requiring Git LFS for this snapshot. The remote had no branches at the read-only
check on 2026-11-03; no remote writes were performed.

The fresh upload copy successfully ran these offline builds:

- `python pipeline.py run`: 64 cards, 56 media, zero errors, 144 existing warnings.
- `python pipeline.py --profile batch01 run`: 100 cards, 120 media, zero errors,
  212 existing warnings.
- `python pipeline.py item-prototype --offline`: 14 cards, 11 media, zero errors,
  no author/verifier calls or approvals.

The original checkout ran `python tools/run_tests.py`: 130 tests, 121 passed,
seven errors and two skips. Three errors require absent historical generated
APKGs (`BackOnly`, `Reparaturen`, `Footer`); four local HTTP tests were blocked
by Windows socket permissions (`WinError 10013`). The skips were the optional
browser workflow and a complete lane export comparison. Frozen-file, identity,
rendering, media, review guards and isolated importer tests otherwise passed.
These errors are recorded rather than weakening tests or recreating historical
packages. The machine-readable test summary remains in `build/reports/tests.json`.

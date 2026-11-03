# Autonomous champion drafts

Scope: one identifier per invocation; demonstrate Braum only. Existing 100
approved cards, their source/media locks and the v4 renderer remain unchanged.

1. Resolve an identifier/name/numeric Riot key against the current official Data
   Dragon index. Pin the observed release, retrieve matching champion JSON and
   CommunityDragon discovery metadata, and archive Riot/Wiki evidence.
2. Python extracts a bounded evidence packet, exact quote locators, raw hashes,
   source revisions and real media. No champion-specific prose lives in Python.
3. A configurable provider (authenticated ephemeral Codex CLI or OpenAI Responses)
   consumes one shared prompt and strict output schema. Persist requests,
   responses, errors and bounded repair retries. Independent AI source-support
   review supplements deterministic citation/identity/schema checks; neither
   constitutes editorial approval.
4. Generate exactly one L1 + P/Q/W/E/R L2 draft; derive stable IDs in Python,
   keep inference guidance separate, and propose cooldown topics without cards.
5. Produce v4 HTML previews, structured QA, a hash-bound source/content proposal,
   and an additive diff against the 100-card production store. Mark every new
   card draft/needs-review; do not apply or export an APKG.
6. Test fresh live retrieval and AI generation for Braum, deterministic offline
   replay, real GIF/icon references, citations, draft rejection, retries and
   unchanged approved-store hashes. Run all prior regression tests, then commit
   code and an explicitly unapproved reproducibility/example archive.

Source matching is not a proof of semantic truth. Conflicts, missing evidence,
numeric claim risks, multi-form coverage and visual uncertainty stay in QA.
Pinned input/model-output replay is reproducible; a fresh AI call is not promised
to return identical prose. Never hide model failure behind canned champion text.

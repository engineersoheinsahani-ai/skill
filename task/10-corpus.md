# Task 10 — Corpus (pointer only: study CLOSED for this paper)

The literature study for this manuscript is complete under the ceiling-20 law
(Phase-16 decision): the deposited anchors live in `work/ledger.jsonl`
(corpus rows E2/E4/E6) and `sources/CORPUS.md`; campaign executors consume
them through the anchor pool — no new literature work is authorized.

For a FUTURE paper the tools remain (same as v3.1):
- `run.py corpus fetch --query "..." --limit 10` → OpenAlex keyless
  (set `OPENALEX_MAILTO` to a real address for the polite pool).
- `run.py ledger add/check --ceiling 20` → row_filled requires takeaway +
  >=2 quotes with locators; ceiling is a hard stop.
- Anchor pools are built per axis in `work/corpus/axis.json`; junk anchors
  (browser-upgrade noise etc.) must be skipped by executors, not ingested.
- No downloads of full texts into the workspace (Phase-16 law).

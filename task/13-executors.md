# Task 13 — Executors (writers' stage, after council verdicts)

Run: `python3 engine/run.py campaign run --stage writers --work work`
(6 fixed roles = one real call each; briefs = council verdicts + manuscript
excerpts + anchors + duty card; output `work/writer-output.jsonl`).

Roles and what they may produce:
- **WR-TEXT-1/2/3** — `revisions` rows `{location, before, after, rationale, fid}`.
  Location = exact section + anchor quote. `before` MUST be a verbatim copy of
  the current text (the owner diff-checks it). No whole-section rewrites.
- **FIG-MPL / FIG-GV** — `figure-code` rows: complete runnable code on
  `templates/figures/enb_style.py`, exact ENB widths (1063/1615/2244 px @300),
  colorblind-safe (Okabe-Ito), vector where possible, fonts >=8 pt effective.
  The code is executed BY THE OWNER (or their pipeline), never by agents;
  afterwards `figureqc` must pass on the produced file.
- **STAT-CHECK** — may only verify claims against `input/results/` artifacts
  (law 10) and propose wording that matches the artifacts exactly.

Hard rules:
1. Every revision cites the `fid` it implements (council-confirmed items only).
2. Nothing is applied in place: the owner runs task/05 `apply_revisions.py`
   onto a NEW copy, diffs, decides.
3. No numbers may be invented or "corrected" by writers — if an artifact
   disagrees with the manuscript, the fix is the manuscript text (diffnum
   finding), and the number comes from the artifact, quoted exactly.
4. Style rewrites must respect humanize gates in the owner's private bundle
   (triads <=3/1000w, hedging ratio target) — writers state which gate a
   change serves.

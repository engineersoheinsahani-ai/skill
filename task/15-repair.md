# Task 15 — Repair of quarantined findings (never silent deletion)

`python3 engine/run.py check work/findings.jsonl` quarantines rows that fail
schema or law 2 (an `L:rule-<id>` anchor must exist in checklists/engine files)
or law 9 (`indep` label missing / malformed).

Repair loop (owner-side, minutes):
1. **Locatable rows with a wrong locator** — fix the locator to the exact
   checklist line (`checklists/<file>.md:L<n>`) or the manuscript anchor
   (`L17:`-style) and re-run `check`.
2. **Rows whose rule id was invented** — re-anchor to the nearest real rule in
   the 8 checklist files; if none exists, the finding becomes a `style` note
   with anchor `L:rule-none` and a rationale sentence (kept, downgraded, not
   deleted).
3. **Rows missing quotes** — the executor must have quoted; if the quote is
   lost, the row goes to `work/quarantine.jsonl` and is listed in the next
   campaign wave as a retry target (`--retry-quarantine` re-briefs those slots).
4. **`[single]` P0s** — cannot be repaired into P0 by editing: either a second
   independent slot confirms it (new row, new stamp) or it is reclassified P1
   with note `single-source`.

Invariant: `findings.jsonl` row count only grows or changes severity; deleted
rows must appear in `quarantine.jsonl` with a reason. The validate gate
(`run.py validate`) compares the two files and fails on silent loss.

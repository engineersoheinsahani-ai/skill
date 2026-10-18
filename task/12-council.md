# Task 12 — Council meeting (after the campaign checkpoint)

Inputs: `work/council-input.md` (machine-built) · findings with verdicts
`python3 engine/run.py council work/findings.jsonl work/council-input.md`

Council members: the OWNER (chair) + one representative per active group +
the machine (deterministic facts, no vote). The meeting answers three questions:

1. **Which P0/fatal items are truly confirmed?**
   `machine` (diffnum/figureqc/precheck/validate) or **>=2 independent executors**
   (`indep=harness` stamps from different slots/models) or owner confirmation.
   A `[single]` item is never a P0 alone — it becomes a P1 investigation task.
2. **Which findings merge?** Same body region + same issue type + >=2 executors
   → one P0 with a merged quote set (no double counting).
3. **What goes to the writers' stage?** Each confirmed item gets exactly one
   owner assignment: WR-TEXT-n / FIG-MPL / FIG-GV / STAT-CHECK / owner-only.

Output (appended to `work/council-input.md` as `## COUNCIL VERDICTS`):
one line per item — `FID | confirmed? | indep labels | assignment | note`.
Findings without a council line stay PENDING (they must not reach the kit).

Rules: no new findings in the council; no severity invention — use the rows'
own severity; disagreements get recorded as `note`, resolved by the owner.

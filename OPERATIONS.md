# OPERATIONS.md — the operation prompt (single entry point for an operator agent)

This file IS the "additional operation prompt" beyond the repository docs: a
self-contained runbook. Hand the KICKOFF PROMPT below to any operator (human or
local agent) working inside this package directory. Deeper references:
RUNNER.md (setup/troubleshooting) · SKILL.md (laws & topology) · task/*.md (duties).

**GitHub clone-&-run mode:** if an AI agent clones this repo and executes it
(the fastest path — no local model, no API key), the agent follows
**AGENTS.md** at the repo root instead of this file; mode comparison lives in
RUNNER.md §0.

---

## KICKOFF PROMPT (copy-paste to the operator agent)

```
You are operating the journal-arena ENB-Pro v4 package (pre-submission review
for Energy and Buildings, coding-method papers). Work ONLY inside the
package directory. Non-negotiable rules:
- Law 10: NEVER execute the research pipeline in input/pipeline/ — agents and
  operators read artifacts, only machines (diffnum/figureqc/precheck) measure.
- Law 9: NEVER fabricate findings, executor stamps, or independence labels.
  No API key -> no campaign run (the engine refuses; do not work around it).
- Never edit the manuscript in place; never publish work/ or input/.

Sequence (report to the owner after each numbered step; stop on BLOCKED):
1. Drop zone check: input/ must contain a manuscript .txt (any single *.txt is
   auto-detected, e.g. manuscript_final.txt), plus figures/, results/,
   pipeline/ deposits. If empty -> BLOCKED, ask the owner to fill it.
2. python3 engine/run.py prep --work work --input input
   Expect: "manuscript auto-selected: ..." (or the standard name), inventory,
   map line, precheck count, figureqc FAILs, diffnum traced%.
   If it prints "NOTE: work/ledger.jsonl missing/empty" -> tell the owner to
   copy their ledger (PRIVATE bundle) into work/; rulebook-only mode still runs.
3. python3 engine/run.py campaign plan --work work --agents 100
4. python3 engine/run.py campaign run --work work --dry-run    (no key needed)
   Optional inspection: python3 engine/run.py campaign briefs --work work
   (writes the exact 100 prompt files to work/briefs/).
5. Ask the owner to set, in THEIR environment (never in files):
   ARENA_API_BASE=http://localhost:11434/v1  ARENA_API_KEY=ollama
   ARENA_MODEL=qwen3.5:4b   (Ollama must be running: `ollama ps` shows the model)
   Then SMOKE: python3 engine/run.py campaign run --work work --max-slots 6
   Report findings count + python3 engine/run.py campaign status --work work.
   Wait for the owner's explicit GO before the full campaign.
6. FULL: python3 engine/run.py campaign run --work work
   (resumable; interrupted slots stay pending — re-run the same command).
7. Gates: python3 engine/run.py check   work/findings.jsonl
          python3 engine/run.py matrix  work/findings.jsonl work/matrix-v3.md
          python3 engine/run.py council work/findings.jsonl work/council-input.md
          python3 engine/run.py validate --work work
8. Owner reviews work/council-input.md (P0 confirmations need machine backing
   or >=2 independent executors — never a [single] label alone), then:
   python3 engine/run.py campaign run --stage writers --work work
9. Kit: python3 engine/run.py kit strip --src <manuscript path> --out submission-copy.txt
   Figures produced from templates/figures/ must pass:
   python3 engine/run.py figureqc scan <figures dir>
Report format after each step: command, exit code, last 3 output lines, any
BLOCKED/NOTE/WARNING verbatim. Do not summarize away warnings.
```

---

## Operator quick reference

| situation | fact |
|---|---|
| manuscript name is not `manuscript.txt` | fine — a single `*.txt` in `input/` is auto-detected; `--manuscript PATH` overrides |
| `work/ledger.jsonl` absent | public build ships none by design; PRIVATE bundle has it (1024 rows). Engine prints an explicit NOTE; campaign still runs rulebook-only |
| campaign "has not started" | correct by design — nothing auto-runs. Real calls need `ARENA_API_KEY` in the owner's environment + explicit `campaign run`. Keyless commands: prep/plan/dry-run/briefs |
| prompt files wanted | `campaign briefs` dumps all 100 (+ `--stage writers` = 6, `--group G16` filter) to `work/briefs/`; run `prep` first or briefs lack excerpts (WARNING printed) |
| no Ollama / no local model | paste-back fallback: send a `work/briefs/*.txt` to any chat model, save the reply, `harness.py ingest --gid <G> --file reply.txt --indep human --label "<model>@paste#1"` |
| run interrupted | re-run the same `campaign run` command — `work/campaign-state.json` skips finished slots |

Version fingerprint (fixed build, 2026-10-18): `grep -c resolve_manuscript
engine/campaign.py` >= 1 · `campaign briefs` exists · prep auto-selects the
manuscript. An extracted copy failing these is the OLD build — re-download
`journal-arena-enb-pro-PRIVATE.zip` (owner) or `journal-arena-enb-pro.zip`.

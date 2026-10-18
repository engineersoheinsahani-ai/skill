# journal-arena ENB-Pro v4.0 — exclusive pre-submission edition (Energy and Buildings)

The original 16-group division, executed by **real agents on local models**:
<=100 separate executor calls (campaign.py), every finding stamped with its
execution topology (law 9). All English. The research pipeline is NEVER run by
agents (law 10): the owner deposits its artifacts in `input/`, machines diff,
agents judge.

## What is what (single topology table)
| layer | ENB-Pro v4 (THIS package) | journal-arena v3.1 (sibling skill) | v2 (legacy, inside both) |
|---|---|---|---|
| groups | G1–G16 original division + writers team (WR-TEXT-1/2/3, FIG-MPL, FIG-GV, STAT-CHECK) | E1–E10 scientometrics groups | G1–G16 chat-brief mode |
| executor | `campaign.py` (real calls via Ollama/API) + `harness.py` | `harness.py` | copy-paste prompts |
| machine wave | `prep`: map + precheck + **figureqc** + **diffnum** + inventory | map + precheck + validate | precheck |
| findings | `work/findings.jsonl` (finding-v3 schema + aid/campaign stamps) | same | `work/findings/*.json` |
| severity | fatal/major/minor/style (blocker≡fatal mapped) | same | blocker/... |
| literature | deposited ledger (E2/E4/E6 anchors, ceiling-20 study CLOSED) | live corpus tools | distilled checklists |

## Quickstart (owner machine, keyless machine wave first)
```bash
# 0) fill the drop zone:  input/manuscript.txt (any single *.txt auto-detected)
#                         input/figures/  input/results/  input/pipeline/
#    anchor pools:        work/ledger.jsonl (PRIVATE bundle ships it; PUBLIC warns)
python3 engine/run.py prep --work work --input input      # minutes, no key
python3 engine/run.py campaign plan --work work --agents 100
python3 engine/run.py campaign run --work work --dry-run  # slot table + brief sizes
python3 engine/run.py campaign briefs --work work         # dump all 100 prompt files

# 1) connect the local model (Ollama) and run the real division
set ARENA_API_BASE=http://localhost:11434/v1              # (Windows; export on Linux/mac)
set ARENA_API_KEY=ollama
set ARENA_MODEL=qwen3.5:4b
python3 engine/run.py campaign run --work work --max-slots 6      # smoke: first 6 slots
python3 engine/run.py campaign run --work work                    # full campaign (resumable)
python3 engine/run.py campaign status --work work

# 2) aggregate + writers + kit
python3 engine/run.py council work/findings.jsonl work/council-input.md
python3 engine/run.py campaign run --stage writers --work work
python3 engine/run.py kit strip --src input/manuscript.txt --out submission-copy.txt
python3 engine/run.py figureqc scan input/figures --emit-findings
```

## GitHub / agent mode (clone & run — fastest, no local model)
Publish the PUBLIC build (never the PRIVATE one) as a repo, then tell any
capable agent: *"Clone <repo-url>, read AGENTS.md, follow it exactly. I will
provide the input/ deposits."* The agent runs the machine wave, answers the
100 briefs itself (wave by wave), and stamps every finding `indep=single`
(law 9 — honest: one model, many hats; P0s then need machine backing or your
confirmation). Publish steps:
```bash
unzip journal-arena-enb-pro.zip && cd journal-arena-enb-pro
git init && git add -A && git commit -m "ENB-Pro v4.1 (guard-clean public build)"
git remote add origin https://github.com/<you>/journal-arena-enb-pro.git
git push -u origin main          # or drag-drop upload via the GitHub web UI
```
`.gitignore` blocks input/ deposits, work/ state, demo/ and engine/humanize.py —
never force-add them. No LICENSE file yet by design (pending owner decision;
without one, all rights reserved).

## Environment (local-model mode)
| var | purpose |
|---|---|
| `ARENA_API_BASE` | default `http://localhost:11434/v1` (Ollama); any OpenAI-compatible endpoint |
| `ARENA_API_KEY` | required for real runs (any non-empty string for Ollama); NEVER stored in files |
| `ARENA_MODEL` | default `qwen3.5:4b`; per-group override `ARENA_MODEL_G16=...` |
| `OPENALEX_MAILTO` | real email for keyless corpus fetches (future papers) |

## Layout
`OPERATIONS.md` (the operation prompt / runbook — start here) · `checklists/
engine/ groups/ input/ sources/ task/ templates/ demo/ work/ NOTICE.md RUNNER.md`
`templates/figures/` ships the advanced ENB figure gallery (style + 6 templates).
`engine/humanize.py` is a PRIVATE module — see NOTICE.md before sharing anything.

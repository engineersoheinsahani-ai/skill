# RUNNER — connecting ENB-Pro to a local language model

Target hardware profile (owner's): i7-6700HQ · 16 GB RAM · GTX 960M 4 GB ·
Windows. Current model: **qwen3.5:4b** (Q4 fits fully in 4 GB VRAM → fast).
Everything below also works with any OpenAI-compatible endpoint.

## 0. Pick the execution mode
| mode | how | 100 slots take | law-9 stamp |
|---|---|---|---|
| **Agent clone (GitHub)** | publish the public build; the agent follows `AGENTS.md`: `campaign briefs` -> answers -> `campaign ingest-dir` | one session (wave-batched), no key | `single` (honest: P0 needs machine backing or owner confirmation) |
| **Fast hosted API** | `set ARENA_API_BASE=<any OpenAI-compatible provider>` + `campaign run` | minutes | `harness` (100 real separate calls) |
| **Local Ollama** (rest of this file) | `campaign run` against localhost | ~4-6 h on GTX 960M | `harness` |
| **Paste-back** | `campaign briefs` + `harness ingest --indep human` | manual | `human` |

## 1. Install (once)
1. Ollama for Windows — ollama.com/download
2. `ollama pull qwen3.5:4b`  (optional second mind: `ollama pull llama3.2:3b-instruct`)
3. Verify GPU: `ollama run qwen3.5:4b "hi"` then `ollama ps` in another terminal —
   PROCESSOR column should show GPU (100% or a split). 100% CPU for a 4B model
   means the GPU is not engaged (driver/Ollama version issue).

## 2. Fill the drop zone
```
input/manuscript.txt   <- raw text of the paper (any single *.txt in input/ is
                          auto-detected, e.g. manuscript_final.txt; or pass
                          --manuscript PATH explicitly)
input/figures/         <- designed artwork (+ sources: .py/.dot/.svg)
input/results/         <- the pipeline's OWN outputs (manifests, audit json, tables/, csv, logs)
input/pipeline/        <- the code + run logs (agents READ, never execute)
```
Anchor pools: `work/ledger.jsonl` must contain your literature deposit (the
PRIVATE bundle ships the real one; the PUBLIC build ships none and the engine
warns `NOTE: work/ledger.jsonl missing/empty`). Without it the campaign still
runs — pooled groups fall back to rulebook-only briefs (weaker grounding).

## 3. Machine wave (no key, minutes)
```bash
python3 engine/run.py prep --work work --input input
```
Watch: `diffnum: X/Y traced (Z%)` and `figureqc: N files | M FAIL`.

## 4. The real 100-agent division
```bash
set ARENA_API_BASE=http://localhost:11434/v1
set ARENA_API_KEY=ollama
set ARENA_MODEL=qwen3.5:4b
python3 engine/run.py campaign plan --work work --agents 100     # 100 = G1-G4 x7 + G5-G16 x6
python3 engine/run.py campaign run  --work work --dry-run        # free: slot table + sizes
python3 engine/run.py campaign run  --work work --max-slots 6    # SMOKE TEST first!
python3 engine/run.py campaign run  --work work                  # full (~4-6 h; resumable)
python3 engine/run.py campaign status --work work
```
Interrupted? Just re-run the same command — finished slots are skipped
(`work/campaign-state.json`). After every group the machine checkpoint refreshes
matrix + council automatically.

**Multi-mind tip (real diversity):** run the same campaign with different
`ARENA_MODEL_G16=llama3.2:3b-instruct` etc. — per-group model override; or run
`--group G16 --max-slots 3` twice with two models. Same-model x N = temperature
diversity only (honest label stays `harness`).

## 5. Check quality before scaling
After the smoke test:
```bash
python3 engine/run.py check   work/findings.jsonl     # schema + law-2 quarantine report
python3 engine/run.py matrix  work/findings.jsonl work/matrix-v3.md
python3 engine/run.py council work/findings.jsonl work/council-input.md
```
4B-class yield is honestly lower than frontier models: expect ~2-4 surviving
findings per executor and aggressive quarantine — the gates doing their job.
If JSONL compliance is poor, check `--think off` (default) and keep
`--max-tokens 1200`.

## 6. Writers stage (after council verdicts)
```bash
python3 engine/run.py campaign run --stage writers --work work
```
6 fixed roles (WR-TEXT-1/2/3, FIG-MPL, FIG-GV, STAT-CHECK) → `work/writer-output.jsonl`
(revisions + figure-code). Owner applies via task/05 + `apply_revisions.py`
(never in-place); figure code runs locally, then `figureqc` must pass.

## 7. No-key fallback (paste-back) / prompt files
There are no shipped prompt files — briefs are built at runtime per slot.
To get them as real files (inspect, or run manually through any model):
```bash
python3 engine/run.py campaign briefs --work work                 # all 100 -> work/briefs/
python3 engine/run.py campaign briefs --work work --stage writers # the 6 writer prompts
python3 engine/run.py campaign briefs --work work --group G16     # one group only
```
Or per group: `python3 engine/harness.py brief --gid G8 --work work > brief-G8.txt`.
Paste a brief into any chat model → save the answer → `python3 engine/harness.py
ingest --gid G8 --file answer.txt --indep human --label "chatgpt@paste#1"`.

## Troubleshooting
| symptom | fix |
|---|---|
| `ARENA_API_KEY not set — refusing...` | set the three env vars (law 9: no faking) |
| `ollama ps` shows 100% CPU on 4B | update Ollama; driver must be >= 570 (yours: 581.80 OK) |
| 0 findings from a slot | normal occasionally on 4B; campaign retries once, then leaves the slot pending — re-run to retry |
| diffnum traced% very low | wrong artifacts in input/results (must be the SAME run the manuscript cites) |
| call timeouts | raise harness timeout (edit `call_api(timeout=...)`) or lower `--max-tokens` |

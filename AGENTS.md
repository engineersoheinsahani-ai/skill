# AGENTS.md — instructions for any AI agent that clones this repository

You are operating **journal-arena ENB-Pro v4.1**: a pre-submission review engine
for Energy and Buildings papers (coding method). The machine layer is
deterministic Python (no dependencies; PIL optional). The judgment layer is
**you**: you answer the 100 executor briefs yourself — no API keys, no local
model needed. Work wave by wave and report to the owner after each step.

## Hard rules (laws — violating them invalidates the whole run)
- **Law 10:** NEVER execute anything in `input/pipeline/`. Read artifacts only;
  only the shipped machines (diffnum/figureqc/precheck) measure.
- **Law 9 (execution honesty):** every finding you produce is stamped
  `indep=single` (one model wearing 100 hats). NEVER relabel your own answers as
  `harness`/`machine`/`human`. A P0/fatal is only confirmed with machine backing,
  >=2 genuinely independent sources, or the owner's explicit confirmation.
- No fabrication: quotes must be verbatim from the brief's excerpt/anchor pool;
  numbers must come from `input/results/` artifacts or be written `[number needed]`.
- Never edit the manuscript in place; never `git add` anything under `input/` or
  `work/` (the .gitignore already blocks them — do not force-add).

## Protocol
```bash
# 0) Requirements: python3 (3.9+). Ask the owner for the four deposits and put
#    them in input/ (they upload them to your session; they are NOT in the repo):
#    input/<manuscript>.txt · input/figures/ · input/results/ · input/pipeline/

# 1) Machine wave (deterministic, minutes)
python3 engine/run.py prep --work work --input input
#    Report: manuscript auto-selected line, inventory, map counts, precheck N,
#    figureqc FAILs, diffnum traced%. A ledger NOTE is normal for a fresh clone
#    (rulebook-only anchors) — continue.

# 2) Plan + prompt files
python3 engine/run.py campaign plan   --work work --agents 100
python3 engine/run.py campaign briefs --work work          # -> work/briefs/ (100 files)

# 3) EXECUTOR WAVES — answer briefs yourself, 10 slots per wave (waves are in
#    work/campaign-plan.json). For each slot:
#      - read work/briefs/brief-<slot>.txt
#      - produce JSONL findings EXACTLY per the brief's schema (max 5 lines,
#        each <=120 words; copy the few-shot field names; gid = the slot's group)
#      - save the raw JSONL to work/answers/<slot>.txt  (mkdir work/answers)
#    After each wave:
mkdir -p work/answers
python3 engine/run.py campaign ingest-dir --work work --indep single \
        --label "<your-model-id>@clone"
python3 engine/run.py campaign status --work work
#    Interrupted or out of context? Nothing is lost: campaign-state.json tracks
#    done slots; a new session resumes at the first pending slot.

# 4) Gates (machine)
python3 engine/run.py check    work/findings.jsonl
python3 engine/run.py matrix   work/findings.jsonl work/matrix-v3.md
python3 engine/run.py council  work/findings.jsonl work/council-input.md
python3 engine/run.py validate --work work

# 5) Writers stage (only after the owner reviewed council-input.md)
python3 engine/run.py campaign briefs --work work --stage writers   # 6 prompts
#    answer them into work/answers/<ROLE>.txt (WR-TEXT-1..3, FIG-MPL, FIG-GV,
#    STAT-CHECK), then:
python3 engine/run.py campaign ingest-dir --work work --stage writers \
        --indep single --label "<your-model-id>@clone"

# 6) Submission kit (never touches the master)
python3 engine/run.py kit strip --src input/<manuscript>.txt --out submission-copy.txt
python3 engine/run.py figureqc scan input/figures
```

## Quality guidance for your answers
- Follow each brief's duty card and small-model focus literally; the brief
  already contains the manuscript excerpt, anchors, and machine facts you need —
  do not go read the whole manuscript (context discipline).
- Prefer 1–3 precise findings over 5 vague ones. Every finding needs: exact
  `ms_quote` (from the excerpt), `lit_quote`+`lit_quote_id` (from the anchor
  pool; rulebook anchors `L:rule-*` only if the rule text is quoted in the brief
  or exists in `checklists/`), severity ∈ fatal/major/minor/style, <=3 actions.
- Empty answer files are allowed for clean slots — say so in your wave report
  ("G3-a02: no issues found") instead of inventing findings.
- Writer revisions: `before` must be verbatim current text; figure code must run
  on `templates/figures/enb_style.py` and pass `figureqc` after the owner renders it.

## Report format (after every step)
command · exit code · last 3 output lines · every BLOCKED/NOTE/WARNING verbatim.
Final report to the owner: council P0 list with confirmation labels, per-group
status table, quarantined rows, and the exact files you produced.

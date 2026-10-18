# SKILL.md — journal-arena ENB-Pro v4.0 (exclusive pre-submission edition)

Purpose: full scientometrics review of a manuscript **before submission to
Energy and Buildings** (coding method), executed by **real agents on local
models** — the original 16-group division, <=100 executors, every call separate
and stamped. All English. All v3.1 capabilities retained (dual grounding,
ledger, corpus, matrix, council, kit, guard) plus the machine wave over
`input/` (map, precheck, figureqc, diffnum) and the post-council writers team
with figure specialists.

## 0. The laws (every agent, every model, every phase)
1. **One-duty law** — each agent owns EXACTLY one part (its G-group card in
   `groups/16-group-playbooks.md`); out-of-duty observations go to at most one
   forwarded note (severity `style`).
2. **Dual-grounding law** — every evaluative judgment carries TWO anchors:
   (a) an exact quote from the STUDIED LITERATURE with source id + locator
   (`[L:e4-012 ...]` from `work/ledger.jsonl`), and (b) an exact manuscript
   quote, only where a claim is being mapped. No (a) => quarantined, never
   counted. Exemption: deterministic rule-compliance findings
   (`anchor_type: rulebook|machine`, `lit_quote_id: L:rule-<id>` where the id
   exists in `checklists/` or an engine enforcer) are FACTS — machine-verified
   by `matrix3.py rule_exists`.
3. **Decision-value law** — verdict + at most 3 actionable moves + the quotes.
   No paraphrase-only summaries. The ledger deduplicates; activity without a
   decision is waste.
4. **Evidence-tier law** — body=1.0 > abstract=0.5 > rulebook=1.0 (deterministic)
   > metadata=0 (quarantine). Every quote carries its tier.
5. **Verification license** — read-only toward sources and `input/`; the
   manuscript never leaves the owner's machine except the owner's explicit
   `--attach` decision (POL-AI-5 for online models; local models exempt).
6. **PRIV-1…PRIV-6** — `engine/humanize.py` is a PRIVATE derived module: never
   publish it; `guard_private.py scan` must print clean before ANY package
   leaves this machine (public builds exclude it — see NOTICE.md).
7. **No-fabrication law** — never invent numbers; missing value =
   `[number needed]`, resolved only by the author. No detector score decides.
8. **No-exaggeration law** — no claim bigger than its evidence; claim inflation
   is scored and vetoable (G11 meta-audit + arena rubric weight).
9. **Execution-honesty law** — every artifact records WHO executed it:
   `indep: machine` (deterministic tool — a fact) · `harness` (separate model
   calls via engine/harness.py, key from owner env only) · `human` (owner or
   paste-back) · `single` (one model wearing hats — a labeled simulation).
   "100 agents" is only true with 100 separate calls (campaign.py) — otherwise
   it is `single`. Single-executor findings NEVER confirm a P0 alone: P0 needs
   machine confirmation, >=2 independent executors, or the owner's sign-off.
10. **Artifact-diff law (NEW, owner decision 2026-10-12)** — agents NEVER
    execute the research pipeline (time-consuming; owner's job). The owner
    deposits the pipeline's own outputs in `input/results/` (manifests, audit
    JSONs, tables, CSVs, logs) and the code in `input/pipeline/` (read-only
    static review). `engine/diffnum.py` screens every manuscript number against
    the artifacts (traced / UNTRACED); untraced numbers become machine findings
    for G8 and `[number needed]` candidates. An UNTRACED flag is a screen hit,
    not proof of error — honest by construction.

## 1. Decisions on record
Carried from v3.1 (owner, 2026-10-09/11): `code_scope=research_code` ·
`tier1_journals=[Energy and Buildings (primary), Applied Energy, Building &
Environment, Energy, Journal of Building Engineering, Energy and AI]` ·
`corpus_axis=manuscript-derived` (work/corpus/axis.json) ·
`corpus_counting=body-access-only` · `corpus_ceiling=20` + sufficiency (study
CLOSED at E6 128 / E2 82 / E4 76 countable; anchors deposited in work/ledger.jsonl) ·
`humanizer_mode=distilled-brief`.
New (owner, 2026-10-12): **ENB-Pro exclusive edition** — all English · agent
division EXACTLY the original v2 topology (16 duty groups, waves of 10, <=100
real executors) · execution on LOCAL models (current: `qwen3.5:4b`; code
optimized for 4B-class) · pipeline never executed by agents (law 10) ·
`input/` drop-zone contract · writers team includes FIG-MPL + FIG-GV figure
specialists · figures must meet the most advanced ENB craft (templates shipped).

## 2. Topology — the original 16-group division (single source: groups/16-group-playbooks.md)
G1 title · G2 abstract · G3 keywords-highlights-GA · G4 introduction-gap ·
G5 literature-review · G6 methodology-coding · G7 data · G8 results-consistency ·
G9 statistics-UQ · G10 discussion-claims · G11 recommendations+meta-audit (veto) ·
G12 references-integrity · G13 ethics-policy · G14 formatting-kit ·
G15 language-style · G16 reviewer-simulation.
Division math (campaign.py): N=100 => G1–G4 x7 + G5–G16 x6 = exactly 100 slots
(v2 used ceil => 112; Pro honors the owner's standing <=100 law), waves of 10,
agent ids `G6-a03`. Post-council **writers team** (6 fixed roles): WR-TEXT-1/2/3,
FIG-MPL, FIG-GV, STAT-CHECK.

## 3. Pipeline (waves, resumable)
```
W-machine   run.py prep --work work --input input        (map, precheck, figureqc,
                                                          diffnum, inventory — no key)
W-division  run.py campaign run --work work [--agents 100] (real executors, law 9;
            resumable; checkpoint after every group: check + matrix + council)
  or AGENT MODE (no key; GitHub clone-&-run per AGENTS.md): campaign briefs ->
            the cloning agent answers work/answers/<slot>.txt -> campaign
            ingest-dir --indep single (honest stamp: one model, 100 hats)
W-aggregate run.py check/matrix/council work/findings.jsonl ...
W-writers   run.py campaign run --stage writers --work work (after council verdicts)
W-apply     task/05 + apply_revisions.py (owner approves; traceability: copies only)
W-kit       kit.py strip --src input/manuscript.txt --out <submission-copy> + figureqc clean
W-release   LICENSE / Zenodo DOI / data deposit (Option C) / GenAI declaration
```

## 4. Anchors & pools
Ledger rows keep their v3.1 E-gids; campaign maps duty groups to pools:
G2,G7,G8 -> E6 (integrity 319 anchors) · G4,G5 -> E2+E4 (novelty/methodology
412) · G6,G9 -> E4(+E5 repo rows) · all other groups: rulebook anchors from
`checklists/` (L:rule-*). Briefs embed <=20 anchors (120-char trim) — the ONLY
quotable pool (law 2).

## 5. Small-model contract (4B-class local models)
Prompts: laws digest ~700 chars + duty card + <=20 anchors + duty-relevant
manuscript excerpt ONLY (<=6000 chars, section-mapped) + machine facts +
one few-shot JSONL example. Generation: max_tokens 1200, temperature profile
0.2–0.5, `/no_think` for qwen3-family (default), one parse-retry, robust
extraction (fences/trailing commas/concatenated objects). Expect aggressive
quarantine by the gates — that is the system working, not failing; realistic
yield on 4B: 2–4 surviving findings per executor.

## 6. Layout & commands
`checklists/ engine/ groups/ input/ sources/ task/ templates/ demo/ work/`
Entry: `python3 engine/run.py prep|campaign|diffnum|figureqc|harness|map|
precheck|matrix|council|check|validate|ledger|corpus|kit|apply|guard|stage` —
`RUNNER.md` is the connection guide (Ollama/API/paste-back). `NOTICE.md`:
privacy, license status, environment variables.

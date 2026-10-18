# -*- coding: utf-8 -*-
"""P2/P4: agent topology v2 (duty-separated, learning phase, verification license).
  --mode division : N agents across 16 duty groups (default 32, --agents up to 100),
                    waves of 10; each brief = self-contained (paste into ANY chat model).
                    Phase A (learning): every agent studies its SRC ids LIVE, writes
                    work/playbooks/<gid>-playbook.md. Phase B: review -> findings JSON.
  --mode arena    : single-elimination bracket for contested revisions (work/arena.json).
  next            : prints next wave/round (resume after context compaction).
"""
import json, os, argparse, math

# gid, name, duty (ONE part only), lenses, sources to study live, checklists
GROUPS = [
    ("G1",  "title", "TITLE only: conciseness, scope tokens, SEO, overclaim, consistency",
     "scope-editor / search-engine / overclaim-auditor lenses", "25,26,27,08,05", "08,07,01"),
    ("G2",  "abstract", "ABSTRACT only: <=250w, stand-alone, purpose-procedures-findings-conclusions",
     "structure / numbers-trace / abbreviation lenses", "25,07,23", "01,07"),
    ("G3",  "keywords-highlights-GA", "keywords 1-7, highlights 3-5x85 file, graphical abstract spec",
     "indexing / bullet-craft / pictorial-design lenses", "25,08,09", "01,07"),
    ("G4",  "introduction-gap", "gap logic & positioning vs ENB scope/special issues",
     "gap-map / contribution-clarity lenses", "25,26,27", "01,07"),
    ("G5",  "literature-review", "PRIOR-WORK review: coverage, recency, citation accuracy, fair comparison",
     "coverage / recency / fairness lenses", "25,18,19,20,04,26", "05,07"),
    ("G6",  "methodology-coding", "METHODS & CODING: split roles, transform fitting, audit tests A-H, "
     "stacking math, equation correctness, code reproducibility",
     "leakage-hunter / reproducibility-auditor / equation-checker lenses", "25,10,11,15", "01,07,04"),
    ("G7",  "data", "DATA only: provenance, versions, licences, Option C deposit/cite/link, SAGER data items",
     "provenance / licence / SAGER lenses", "02,03,10,11,15,16", "04,03,07"),
    ("G8",  "results-consistency", "RESULTS numbers: text <-> tables <-> figures traceability, numbering",
     "number-tracer / table-auditor lenses", "25", "01,07"),
    ("G9",  "statistics-UQ", "STATISTICS: conformal coverage math, seed CIs, LOGO design, weighting",
     "coverage-math / seed-design / survey-weights lenses", "25,23", "07"),
    ("G10", "discussion-claims", "DISCUSSION/CONCLUSIONS claims vs evidence ladder (CLM-*)",
     "claim-ranker / hedge-auditor lenses", "25,12", "07,01"),
    ("G11", "recommendations-suggestions", "RECOMMENDATIONS proportionality + META-audit of every other "
     "agent's suggestion for claim inflation (veto power)",
     "proportionality / meta-audit lenses", "25,12", "07"),
    ("G12", "references-integrity", "REFERENCES: bidirectional, et-al consistency, LTWA, [dataset]/"
     "[software], access dates, existence verification via CrossRef",
     "integrity / style / LTWA lenses", "18,19,20,25,04", "05"),
    ("G13", "ethics-policy", "ETHICS/POLICY: AI declaration, CRediT, COI, funding, SAGER, inclusive language",
     "policy-auditor / SAGER-auditor lenses", "04,12,02,03,17,25", "02,03,04"),
    ("G14", "formatting-kit", "FORMATTING/KIT: file formats, line numbers, artwork specs, EM inventory",
     "typesetter / artwork / inventory lenses", "25,06,07,09,21,22,24", "01,06"),
    ("G15", "language-style", "LANGUAGE: clarity, grammar, journal tone, inclusive language, abbreviations",
     "editor / plain-language lenses", "12,23,04,14", "02,07"),
    ("G16", "reviewer-simulation", "SIMULATED PEER REVIEW: 2 single-anonymized reports + editor meta-review",
     "reviewer-1 / reviewer-2 / editor lenses", "25,12,24,28,05", "01,02,07"),
]
CARDS = ["conservative-editor", "reviewer-2-adversarial", "statistician", "policy-auditor",
         "plain-language", "scope-guardian", "data-steward", "typesetter", "claim-auditor"]
RUBRIC = ("score = 3*axis_fit + 2*journal_fit + 2*evidence + (5-risk) + (5-effort)"
          " + 2*(5-claim_inflation); each 0-5; judge = median of 3 judges")

# NOTE (audit 2.1): v2 LEGACY topology (16 G-groups), kept for init/plan archive runs.
# Current engine: orchestrate_v3.py (gates/briefs/next) + harness.py (real executors).


def axis_text(work):
    """Axis law (SKILL §4, task/10 §0): the axis is READ from work/corpus/axis.json —
    never hardcoded (audit 2.4). Fallback is explicitly tagged."""
    p = os.path.join(work, "corpus", "axis.json")
    if os.path.exists(p):
        try:
            d = json.load(open(p, encoding="utf-8"))
            terms = "; ".join(d.get("terms", [])) or d.get("title", "")
            return terms + f"  [source: {d.get('source', 'axis.json')}]"
        except Exception:
            pass
    return ("[FALLBACK-AXIS — work/corpus/axis.json missing; run `corpus axis "
            "--manuscript <txt>` first; fallback tagged per task/10 §0]")


BRIEF = """# Agent brief {aid} — duty group {gid}: {gname}
You are ONE duty-specialist reviewer agent in a model-agnostic editorial board assessing a
manuscript for *Energy & Buildings* (Elsevier). Your duty is EXACTLY ONE part: {duty}.
Do not review anything outside your duty; out-of-duty observations go to at most ONE
forwarded note with `group: "{gid}"` and severity `style`.

## Phase A — LEARNING (mandatory, before any judgement)
Study these sources YOURSELF (fetch/read/search; do not rely only on summaries): SRC {src}
— full list & urls in sources/CORPUS.md (read it first). Then write
`work/playbooks/{gid}-playbook.md`: >=6 actionable role rules YOU extracted, each with the
source url + access date. Lenses to train: {lenses}.
If your runtime has NO web access: use checklists/{cls}.md instead and set
`source_mode: distilled` on every finding.
Checklists to master: checklists/{cls}.md + checklists/07-claims-and-overclaim.md (all groups).

## Phase B — VERIFICATION LICENSE (read-only web permission)
You MAY fetch/search public pages to verify references (CrossRef/DOI), dataset versions
(RECS 2020 / TMY3 / ResStock 2025.1), journal scope & special issues, LTWA abbreviations,
policy wording. You MUST NOT upload/paste any manuscript text into online tools or GenAI
(POL-AI-5), submit anything, or contact anyone. Record every web check in
`verified_via: [{{"url": ..., "accessed": ...}}]`.

## Phase C — REVIEW
Inputs: {ms}, work/manuscript-map.json, work/precheck-report.md, your playbook.
AXIS of this paper: {axis}
Three laws (SKILL.md §0): AXIS (axis_link mandatory), EVIDENCE (exact quote + rule id),
TRACEABILITY (no in-place edits). Fourth law: CLAIM SIZE — no claim or suggestion bigger
than the evidence (checklists/07).
Output: JSON array (2-8 findings) per templates/finding.schema.json -> work/findings/{aid}.json
Severity: blocker/major/minor/style. Effort tag required. No new experiments outside the
paper's public data; no praise-only or hate-only items.
"""


def division(work, ms, agents):
    agents = min(max(agents, 16), 100)
    per = max(1, math.ceil(agents / len(GROUPS)))
    bdir = os.path.join(work, "briefs")
    pdir = os.path.join(work, "playbooks")
    fdir = os.path.join(work, "findings")
    for d in (bdir, pdir, fdir):
        os.makedirs(d, exist_ok=True)
    made, plan = [], {"mode": "division", "agents": agents, "groups": [g[0] for g in GROUPS],
                      "phases": ["A-learning", "B-review"], "waves": [], "next": None}
    for gid, gname, duty, lenses, src, cls in GROUPS:
        for k in range(per):
            aid = f"{gid}-a{k+1:02d}"
            open(os.path.join(bdir, f"{aid}.md"), "w", encoding="utf-8").write(
                BRIEF.format(axis=axis_text(work), aid=aid, gid=gid, gname=gname, duty=duty, lenses=lenses,
                             src=src, cls=cls, ms=ms))
            made.append(aid)
    waves = [made[i:i + 10] for i in range(0, len(made), 10)]
    plan["waves"] = waves
    plan["next"] = (f"wave 1 (Phase A learning first, then B): {', '.join(waves[0])}"
                    if waves else None)
    json.dump(plan, open(os.path.join(work, "plan.json"), "w", encoding="utf-8"), indent=1)
    print(f"division v2: {len(made)} agents / {len(GROUPS)} duty groups / {len(waves)} wave(s)")


def arena(work, contested):
    st = {"mode": "arena", "contested": contested, "round": 1, "cards": CARDS, "rubric": RUBRIC,
          "pairs": [[contested[i], contested[i + 1]] for i in range(0, len(contested) - 1, 2)],
          "next": "round 1: attack -> defend+revise -> 3 judges score with rubric (claim_inflation weighted)"}
    if len(contested) % 2:
        st["bye"] = contested[-1]
    json.dump(st, open(os.path.join(work, "arena.json"), "w", encoding="utf-8"), indent=1)
    print(f"arena: {len(contested)} contested revisions, {len(st['pairs'])} pair(s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["division", "arena", "next"], default="division")
    ap.add_argument("--agents", type=int, default=32)
    ap.add_argument("--work", default="work")
    ap.add_argument("--ms", default="manuscript.txt")
    ap.add_argument("--contested", nargs="*", default=[])
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    if a.mode == "division":
        division(a.work, a.ms, a.agents)
    elif a.mode == "arena":
        arena(a.work, a.contested or ["rev-title-A", "rev-title-B"])
    else:
        for f in ("plan.json", "arena.json"):
            p = os.path.join(a.work, f)
            if os.path.exists(p):
                print(f, "->", json.load(open(p)).get("next"))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diffnum.py — machine enforcer of the ARTIFACT-DIFF law (law 10).

Every numeric claim in the manuscript must trace to an artifact deposited in
input/results/ (run manifests, audit JSONs, tables, CSVs, logs) — or be flagged.
Agents NEVER re-run the research pipeline (owner decision 2026-10-12: too
time-consuming); the owner deposits the pipeline's own outputs and this tool
diffs numbers against them. Deterministic => indep=machine (law 9).

Commands:
  scan  --input DIR [--work W]                    inventory numeric-bearing artifacts
  check --manuscript MS --input DIR [--work W] [--tol 0.001] [--emit-findings]

HONESTY: this is a SCREEN, not a proof. UNTRACED means "no artifact match
found" (could be a derived/rounded number) — flagged items go to G8 agents and
the owner for inspection. Traced % is the headline metric.
"""
import argparse, bisect, json, os, re, sys

NUM = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d{2,}")
SKIP_CTX = re.compile(r"(?i)(section|fig\.?|figure|table|eq\.?|equation|step|phase|"
                      r"pass|chapter|page|rule|law|version|line|round|v\d)\s*\.?\s*$")


def norm(tok):
    return tok.replace(",", "")


def artifact_numbers(results_dir):
    strs, floats = set(), set()
    files = 0

    def add_str(t):
        for m in NUM.finditer(t):
            n = norm(m.group())
            strs.add(n)
            try:
                floats.add(round(float(n), 6))
            except ValueError:
                pass

    def walk_json(x):
        if isinstance(x, bool):
            return
        if isinstance(x, (int, float)):
            floats.add(round(float(x), 6))
            strs.add(str(x))
        elif isinstance(x, dict):
            for v in x.values():
                walk_json(v)
        elif isinstance(x, list):
            for v in x:
                walk_json(v)
        elif isinstance(x, str):
            add_str(x)

    for root, _, fns in os.walk(results_dir):
        for fn in sorted(fns):
            p = os.path.join(root, fn)
            ext = fn.lower().rsplit(".", 1)[-1] if "." in fn else ""
            try:
                if ext == "json":
                    walk_json(json.load(open(p, encoding="utf-8", errors="replace")))
                    files += 1
                elif ext in ("csv", "tsv", "txt", "md", "log"):
                    add_str(open(p, encoding="utf-8", errors="replace").read())
                    files += 1
            except Exception:
                continue
    return strs, sorted(floats), files


def cmd_scan(a):
    strs, floats, files = artifact_numbers(os.path.join(a.input, "results"))
    out = {"artifact_files": files, "distinct_number_strings": len(strs),
           "distinct_floats": len(floats)}
    os.makedirs(a.work, exist_ok=True)
    json.dump(out, open(os.path.join(a.work, "diffnum-scan.json"), "w"), indent=1)
    print("diffnum scan:", json.dumps(out))
    return 0


def cmd_check(a):
    if not os.path.exists(a.manuscript):
        print("diffnum: manuscript not found:", a.manuscript)
        return 2
    ms = open(a.manuscript, encoding="utf-8", errors="replace").read()
    strs, floats, files = artifact_numbers(os.path.join(a.input, "results"))
    if files == 0:
        print("diffnum: no artifacts in input/results — law 10 inactive "
              "(deposit run manifests/tables/CSVs)")
        return 0
    traced, untraced, total = 0, [], 0
    for m in NUM.finditer(ms):
        ctx = ms[max(0, m.start() - 34):m.start()]
        if SKIP_CTX.search(ctx):
            continue                       # section/figure/table labels are not claims
        tok = norm(m.group())
        if len(tok) < 2:
            continue
        total += 1
        hit = tok in strs
        if not hit:
            try:
                v = float(tok)
                i = bisect.bisect_left(floats, v)
                for j in (i - 1, i):
                    if 0 <= j < len(floats) and \
                       abs(v - floats[j]) <= a.tol * max(1.0, abs(v)):
                        hit = True
                        break
            except ValueError:
                pass
        if hit:
            traced += 1
        else:
            untraced.append({"num": m.group(), "context": " ".join(ctx.split())[-42:]})
    pct = round(100 * traced / total) if total else 100
    os.makedirs(a.work, exist_ok=True)
    rep = {"manuscript": a.manuscript, "artifact_files": files, "total": total,
           "traced": traced, "untraced": untraced, "traced_pct": pct, "tol": a.tol}
    json.dump(rep, open(os.path.join(a.work, "diffnum.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    lines = ["# diffnum report — artifact-diff law (law 10)", "",
             f"manuscript numbers screened: {total} | traced to input/results: "
             f"{traced} ({pct}%) | UNTRACED: {len(untraced)}", "",
             "UNTRACED (top 40) — inspect, not proof of error:", ""]
    for u in untraced[:40]:
        lines.append(f"- `{u['num']}`  …{u['context']}")
    open(os.path.join(a.work, "diffnum-report.md"), "w", encoding="utf-8").write(
        "\n".join(lines) + "\n")
    print(f"diffnum: {traced}/{total} traced ({pct}%), {len(untraced)} untraced "
          f"-> {a.work}/diffnum-report.md")
    if a.emit_findings and untraced:
        fp = os.path.join(a.work, "findings.jsonl")
        with open(fp, "a", encoding="utf-8") as f:
            for i, u in enumerate(untraced[:15], 1):
                row = {"claim_id": f"NUM-{i:03d}", "gid": "G8", "verdict": "untraceable",
                       "lit_quote": "diffnum: rule enforced by engine/diffnum.py — every "
                                    "numeric claim must trace to a deposited artifact",
                       "lit_quote_id": "L:rule-diffnum", "lit_tier": "rulebook",
                       "anchor_type": "machine", "severity": "major",
                       "action": f"Trace `{u['num']}` (…{u['context']}) to an input/results "
                                 "artifact or mark [number needed]",
                       "ms_quote": u["num"], "ms_locator": f"context: {u['context']}",
                       "indep": "machine", "executor": "engine/diffnum.py@run",
                       "machine_verified": "diffnum check"}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"emitted {min(15, len(untraced))} machine findings (gid G8) -> {fp}")
    return 0 if pct >= 90 else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["scan", "check"])
    ap.add_argument("--input", default="input")
    ap.add_argument("--manuscript", default=None)
    ap.add_argument("--work", default="work")
    ap.add_argument("--tol", type=float, default=0.001)
    ap.add_argument("--emit-findings", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "scan":
        return cmd_scan(a)
    if not a.manuscript:
        a.manuscript = os.path.join(a.input, "manuscript.txt")
    return cmd_check(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

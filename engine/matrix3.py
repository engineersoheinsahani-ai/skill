#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""matrix3.py — v3 findings: validate, quarantine, dedup, tier-weight, aggregate.

Commands:
  check   <findings.jsonl>        schema-lite validation + quarantine report
  matrix  <findings.jsonl> <out>  write work/matrix-v3.md (grouped, weighted)
  council <findings.jsonl> <out>  weighted aggregation as council input

Tier weights (law 4): body=1.0, abstract=0.5, rulebook=1.0 (deterministic),
metadata=0.0 (quarantined). Severity: v2 "blocker" == v3 "fatal" (SEVMAP).
Law 2: a finding without lit_quote_id/lit_quote is quarantined, never counted.
"""
import json, sys, os
from collections import defaultdict

W = {"body": 1.0, "abstract": 0.5, "metadata": 0.0, "rulebook": 1.0}
SEVMAP = {"blocker": "fatal"}   # v2->v3 vocab (audit 2.3): blocker == fatal
HERE = os.path.dirname(os.path.abspath(__file__))


def rule_exists(rid):
    """Machine check for rulebook anchors (audit 2.2): the rule id must literally
    exist in the distilled checklists or be enforced by engine/precheck.py."""
    rid_u = rid.upper()
    roots = [os.path.join(os.path.dirname(HERE), "checklists"), HERE]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for fn in sorted(os.listdir(root)):
            if fn.endswith((".md", ".py")):
                try:
                    txt = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                if rid_u in txt.upper():
                    return True
    return False


def confirmed(r):
    """Law 9 P0 confirmation label: machine facts, harness/human executors, or an
    explicit machine verification. Single-model alone => owner must confirm."""
    if r.get("indep") == "machine" or r.get("machine_verified") or \
       r.get("anchor_type") in ("rulebook", "machine"):
        return "[confirmed:machine]"
    if r.get("indep") in ("harness", "human"):
        return f"[confirmed:{r['indep']}]"
    return "[!single - owner confirmation required]"
REQ = ["claim_id", "gid", "verdict", "lit_quote", "lit_tier", "severity", "action"]


def load(path):
    rows, bad = [], []
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            bad.append((i, f"json: {e}"))
            continue
        miss = [k for k in REQ if not r.get(k)]
        if miss:
            bad.append((i, f"missing {miss}"))
        if r.get("severity") in SEVMAP:                       # audit 2.3
            r["severity_raw"] = r["severity"]
            r["severity"] = SEVMAP[r["severity"]]
        rulebook = r.get("anchor_type") in ("rulebook", "machine") and \
            str(r.get("lit_quote_id", "")).startswith("rule-")
        if rulebook:
            rid = str(r["lit_quote_id"])[5:]
            if not rule_exists(rid):
                r["quarantined"] = True
                bad.append((i, f"quarantine: rulebook anchor '{rid}' not found in checklists/ or precheck.py"))
        elif not r.get("lit_quote_id") or len(r.get("lit_quote", "")) < 15:
            r["quarantined"] = True
            bad.append((i, f"quarantine (law 2): weak/absent literature anchor: {r.get('claim_id')}"))
        if r.get("lit_tier") == "metadata":
            r["quarantined"] = True
        if r.get("gid") == "E9" and r.get("severity") != "style":
            r["severity"] = "style"
            bad.append((i, f"E9 severity forced to style: {r.get('claim_id')}"))
        r.setdefault("quarantined", False)
        rows.append(r)
    return rows, bad


def dedup(rows):
    seen, out = set(), []
    for r in rows:
        k = (r["claim_id"], r["gid"], r["verdict"])
        if k in seen:
            r["quarantined"] = True
            r.setdefault("action", "")
            continue
        seen.add(k)
        out.append(r)
    return out


def weight(r):
    return W.get(r.get("lit_tier", "metadata"), 0.0)


def matrix(rows, out):
    rows = dedup(rows)
    by_gid = defaultdict(list)
    for r in rows:
        by_gid[r["gid"]].append(r)
    with open(out, "w", encoding="utf-8") as f:
        f.write("# matrix v4-pro — dual-anchored findings (weighted)\n\n")
        for gid in sorted(by_gid):
            rs = by_gid[gid]
            live = [r for r in rs if not r["quarantined"]]
            f.write(f"## {gid} — {len(live)} live / {len(rs)-len(live)} quarantined\n\n")
            f.write("| claim | verdict | tier | w | severity | action | anchor |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for r in sorted(rs, key=lambda x: (x["quarantined"], -weight(x))):
                f.write(f"| {r['claim_id']} | {r['verdict']} | {r.get('lit_tier','-')} "
                        f"| {weight(r):.1f} | {r['severity']} | {r.get('action','')[:80]} "
                        f"| {r.get('lit_quote_id','-')}{' ⛔' if r['quarantined'] else ''} |\n")
            f.write("\n")
    return out


def council(rows, out):
    rows = dedup(rows)
    live = [r for r in rows if not r["quarantined"]]
    agg = defaultdict(float)
    sev = defaultdict(int)
    for r in live:
        agg[r["gid"]] += weight(r)
        sev[r["severity"]] += 1
    n_q = len(rows) - len(live)
    with open(out, "w", encoding="utf-8") as f:
        f.write("# council input — weighted aggregation (task/12-council.md)\n\n")
        f.write(f"total findings: {len(rows)} | live: {len(live)} | quarantined: {n_q}\n\n")
        f.write("## evidence weight by group (body=1.0, abstract=0.5, rulebook=1.0)\n")
        for gid in sorted(agg):
            f.write(f"- {gid}: {agg[gid]:.1f}\n")
        f.write("\n## severities\n")
        for s in ("fatal", "major", "minor", "style"):
            f.write(f"- {s}: {sev.get(s, 0)}\n")
        f.write("\n## P0 candidates (fatal/major, weight >= 1.0) — law-9 confirmation labels\n")
        for r in live:
            if r["severity"] in ("fatal", "major") and weight(r) >= 1.0:
                f.write(f"- [{r['gid']}] {r['claim_id']}: {r.get('action','')[:100]} "
                        f"{confirmed(r)}\n")
        f.write("\nCouncil reminder: three mandatory answers + verdict template in task/12-council.md §2-§3.\n")
    return out


def main(argv):
    if len(argv) < 2 or argv[0] not in ("check", "matrix", "council"):
        print(__doc__)
        return 2
    if argv[0] != "check" and len(argv) < 3:
        print(__doc__)
        return 2
    rows, bad = load(argv[1])
    if argv[0] == "check":
        print(f"loaded {len(rows)} findings; issues:")
        for i, why in bad:
            print(f"  line {i}: {why}")
        print("VERDICT:", "ok" if not bad else f"{len(bad)} issue(s)")
        return 0 if not bad else 1
    out = argv[2]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    fn = matrix if argv[0] == "matrix" else council
    print("written:", fn(rows, out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

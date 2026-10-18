# -*- coding: utf-8 -*-
"""QA gate: schema-check findings / revisions / matrix; enforce the three laws."""
import json, glob, re, sys, os

SEV = {"blocker", "major", "minor", "style"}
FREQ = ("id", "severity", "section", "quote", "issue", "suggestion", "axis_link")
RREQ = ("id", "section", "old", "new", "rationale", "approved")


def main(work, ms_path=None):
    errs = []
    ms = open(ms_path, encoding="utf-8").read() if ms_path and os.path.exists(ms_path) else None
    mf = " ".join(ms.split()) if ms else None
    # --- v3 store: work/findings.jsonl (dual-schema validate, audit 2.2) ---
    V3REQ = ("claim_id", "gid", "verdict", "lit_quote", "lit_tier", "severity", "action")
    V3SEV = {"fatal", "major", "minor", "style", "blocker"}   # blocker == fatal downstream
    V3PAT = re.compile(r"^L:((g|e)\d+-\d+|seed-\d+|shared-\d+|rule-[a-z0-9-]+)$")
    v3p = os.path.join(work, "findings.jsonl")
    if os.path.exists(v3p):
        for ln, line in enumerate(open(v3p, encoding="utf-8"), 1):
            if not line.strip():
                continue
            try:
                f3 = json.loads(line)
            except json.JSONDecodeError as e:
                errs.append(f"findings.jsonl:{ln}: bad json: {e}")
                continue
            for k in V3REQ:
                if not str(f3.get(k, "")).strip():
                    errs.append(f"findings.jsonl:{ln}: {f3.get('claim_id','?')} missing {k}")
            if f3.get("severity") not in V3SEV:
                errs.append(f"findings.jsonl:{ln}: {f3.get('claim_id','?')} bad severity")
            lq = f3.get("lit_quote_id")
            if lq and not V3PAT.match(lq):
                errs.append(f"findings.jsonl:{ln}: {f3.get('claim_id','?')} bad lit_quote_id {lq}")
    # --- v2 stores ---
    for p in glob.glob(os.path.join(work, "findings", "*.json")) + \
             glob.glob(os.path.join(work, "precheck.json")) + \
             glob.glob(os.path.join(work, "review-matrix.json")):
        data = json.load(open(p, encoding="utf-8"))
        items = data.get("findings", data) if isinstance(data, dict) else data
        if not isinstance(items, list):
            continue
        for f in items:
            for k in FREQ:
                if not str(f.get(k, "")).strip():
                    errs.append(f"{p}: {f.get('id','?')} missing {k}")
            if f.get("severity") not in SEV:
                errs.append(f"{p}: {f.get('id','?')} bad severity")
            if mf and f.get("quote") and not any(t in f["quote"] for t in ("(absent)", "(file property)", "(structural)")):
                if " ".join(f["quote"].split()) not in mf:
                    errs.append(f"{p}: {f.get('id','?')} quote not in manuscript")
    rp = os.path.join(work, "revisions.json")
    if os.path.exists(rp):
        for r in json.load(open(rp, encoding="utf-8")):
            for k in RREQ:
                if k not in r:
                    errs.append(f"revisions.json: {r.get('id','?')} missing {k}")
            if ms and r.get("approved") and r["old"] and ms.count(r["old"]) != 1:
                errs.append(f"revisions.json: {r['id']} old-text not unique in manuscript")
    rep = os.path.join(work, "validation-report.md")
    open(rep, "w", encoding="utf-8").write(
        "# Validation report\n\n" + ("PASS — all artefacts schema-clean and evidence-bound.\n"
        if not errs else "\n".join(f"- {e}" for e in errs) + "\n"))
    print("validate:", "PASS" if not errs else f"{len(errs)} ERRORS")
    return 0 if not errs else 1


if __name__ == "__main__":
    argv, pos = sys.argv[1:], []
    work = ms = None
    i = 0
    while i < len(argv):                       # accepts --work/--manuscript OR positionals
        if argv[i] == "--work" and i + 1 < len(argv):
            work, i = argv[i + 1], i + 2
        elif argv[i] == "--manuscript" and i + 1 < len(argv):
            ms, i = argv[i + 1], i + 2
        else:
            pos.append(argv[i]); i += 1
    work = work or (pos[0] if pos else "work")
    ms = ms or (pos[1] if len(pos) > 1 else None)
    sys.exit(main(work, ms))

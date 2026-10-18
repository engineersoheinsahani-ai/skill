# -*- coding: utf-8 -*-
"""P6: apply AUTHOR-APPROVED revisions to a NEW manuscript file (never in place).
revisions.json = [{"id","section","old","new","rationale","rule","approved":true}]
Outputs: ms_revN.txt, CHANGELOG.md, point-by-point.md (reviewer-response ready)."""
import json, os, sys


def main(ms_path, rev_path, out_dir):
    ms = open(ms_path, encoding="utf-8").read()
    revs = [r for r in json.load(open(rev_path, encoding="utf-8")) if r.get("approved")]
    n = 1
    while os.path.exists(os.path.join(out_dir, f"ms_rev{n}.txt")):
        n += 1
    os.makedirs(out_dir, exist_ok=True)
    log, pp = [], ["# Point-by-point change log", ""]
    for r in revs:
        old, new = r["old"], r["new"]
        c = ms.count(old)
        if c != 1:
            raise SystemExit(f"[{r['id']}] old-text occurs {c} times (must be exactly 1); aborting safely, nothing written.")
        ms = ms.replace(old, new)
        log.append(f"- rev{n}.{len(log)+1} [{r['id']}] {r.get('rule','-')} :: {old[:70]!r} -> {new[:70]!r}")
        pp += [f"## {r['id']} ({r.get('rule','-')})", f"- **Change:** {r.get('rationale','')}",
               f"- **Before:** {old[:200]}", f"- **After:** {new[:200]}", ""]
    out = os.path.join(out_dir, f"ms_rev{n}.txt")
    open(out, "w", encoding="utf-8").write(ms)
    open(os.path.join(out_dir, "CHANGELOG.md"), "a", encoding="utf-8").write(
        f"\n## revision {n} ({len(revs)} approved changes)\n" + "\n".join(log) + "\n")
    open(os.path.join(out_dir, "point-by-point.md"), "w", encoding="utf-8").write("\n".join(pp))
    print(f"wrote {out} with {len(revs)} approved revisions; changelog + point-by-point updated")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "work")

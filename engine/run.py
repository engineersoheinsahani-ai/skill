#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run.py — v4-pro dispatcher (single entry point, all English).

python3 engine/run.py <cmd> [args...]
  prep             -> campaign.py prep   (MACHINE wave over input/: map, precheck,
                                           figureqc, diffnum, inventory — no key)
  campaign         -> campaign.py plan|run|status|briefs|ingest-dir (<=100-agent division,
                                           16 groups, resumable, law-9 stamped)
  diffnum          -> diffnum.py scan|check       (law 10 artifact-diff)
  figureqc         -> figureqc.py scan            (ENB artwork QC)
  harness          -> harness.py brief|run|ingest (per-group real executor)
  map / precheck   -> manuscript_map.py / precheck.py
  matrix / council / check -> matrix3.py (dual-anchored aggregation, law-9 labels)
  validate         -> validate.py (dual schema)
  ledger / corpus  -> ledger.py / corpus.py (literature study, keyless)
  kit              -> kit.py check|strip (P7 submission copy; never edits src)
  apply            -> apply_revisions.py (P5)
  humanize         -> humanize.py score (PRIVATE module — see NOTICE.md)
  guard / stage    -> guard_private.py (PRIV export guard)
  init / plan / next -> orchestrate.py (v2 LEGACY planner; campaign.py supersedes)
Unknown args print this help. Every shipped package must pass `guard` first.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {
    "prep": ("campaign.py", ["prep"]), "campaign": ("campaign.py", None),
    "diffnum": ("diffnum.py", None), "figureqc": ("figureqc.py", None),
    "harness": ("harness.py", None),
    "map": ("manuscript_map.py", None), "precheck": ("precheck.py", None),
    "matrix": ("matrix3.py", ["matrix"]), "council": ("matrix3.py", ["council"]),
    "check": ("matrix3.py", ["check"]),
    "validate": ("validate.py", None),
    "ledger": ("ledger.py", None), "corpus": ("corpus.py", None),
    "kit": ("kit.py", None), "apply": ("apply_revisions.py", None),
    "humanize": ("humanize.py", ["score"]),
    "guard": ("guard_private.py", ["scan"]), "stage": ("guard_private.py", ["stage"]),
    "init": ("orchestrate.py", None), "plan": ("orchestrate.py", None),
    "next": ("orchestrate.py", None),
}


def main(argv):
    if not argv or argv[0] not in MAP or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if not argv else 2
    script, prefix = MAP[argv[0]]
    cmd = [sys.executable, os.path.join(HERE, script)] + (prefix or []) + argv[1:]
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

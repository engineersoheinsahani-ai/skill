#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kit.py — P7 submission-kit helper (traceability law: NEVER edits the source).

  check --src MS              list internal artefacts still present (exit 1 if any)
  strip --src MS --out COPY   write a submission COPY with internal blocks removed
                              (REVISION NOTES / "delete before submission" memos)

Owner standing rule (phase 8): review corrections are NOT applied to the master
manuscript in-session. `strip` only ever WRITES A NEW COPY; the master stays
untouched. Machine wave (law 9): deterministic, indep=machine.
"""
import argparse, os, re, sys

SEP = re.compile(r"^={10,}\s*$")
INTERNAL = ("revision notes", "delete before submission", "draft note",
            "internal note", "todo:")


def sections(lines):
    """Parse ====/HEADER/==== delimited sections -> list of dicts(header, start, end).
    `end` is exclusive (start of the next section's opening separator or EOF)."""
    marks = [i for i, l in enumerate(lines) if SEP.match(l.strip())]
    secs, k = [], 0
    while k + 1 < len(marks):
        header = "\n".join(lines[marks[k] + 1:marks[k + 1]]).strip()
        end = marks[k + 2] if k + 2 < len(marks) else len(lines)
        secs.append({"header": header, "start": marks[k], "end": end})
        k += 2
    return secs


def internal_hits(lines):
    hits = []
    for i, l in enumerate(lines, 1):
        low = l.lower()
        for t in INTERNAL:
            if t in low:
                hits.append((i, l.strip()[:90]))
                break
        if "[number needed]" in l:
            hits.append((i, l.strip()[:90]))
    return hits


def cmd_check(a):
    lines = open(a.src, encoding="utf-8", errors="replace").read().splitlines()
    hits = internal_hits(lines)
    if not hits:
        print("kit check: CLEAN — no internal artefacts found")
        return 0
    print(f"kit check: {len(hits)} internal artefact line(s):")
    for ln, txt in hits[:20]:
        print(f"  line {ln}: {txt}")
    return 1


def cmd_strip(a):
    if os.path.abspath(a.src) == os.path.abspath(a.out):
        print("refusing: --out must differ from --src (traceability law)")
        return 2
    text = open(a.src, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()
    drop = set()
    for s in sections(lines):
        h = s["header"].lower()
        if any(t in h for t in INTERNAL):
            drop.update(range(s["start"], s["end"]))
            print(f"strip: removing section '{s['header'][:60]}' "
                  f"(lines {s['start']+1}..{s['end']})")
    kept = [l for i, l in enumerate(lines) if i not in drop]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(kept) + "\n")
    w0, w1 = len(text.split()), len("\n".join(kept).split())
    print(f"kit strip: {a.src} ({w0} w) -> {a.out} ({w1} w); master untouched")
    rest = internal_hits(kept)
    if rest:
        print(f"warning: {len(rest)} internal marker line(s) survive outside "
              f"delimited sections — inspect `kit check --src {a.out}`")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "strip"])
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "strip" and not a.out:
        print("--out required for strip")
        return 2
    return cmd_check(a) if a.cmd == "check" else cmd_strip(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

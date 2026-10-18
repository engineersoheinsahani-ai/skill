#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guard_private.py — PRIV-4 export guard for journal-arena.

Scans a directory tree or a zip archive for private-module material
(see humanizer/SECURITY.md; scope includes engine/humanize.py as a derived
implementation). A target is DIRTY if it contains:
  path hits   : any member/path with a `humanizer` segment, or humanizer filenames;
  marker hits : the module's proper name, or metric-index + list-pattern
                co-occurrence (the proprietary fingerprint; strings are assembled
                at runtime so this file never contains them literally).

Usage:
  python3 guard_private.py scan <dir-or-zip> [<dir-or-zip> ...]
Exit 0 = clean, 1 = dirty (never ship), 2 = usage/IO error.
"""
import os, re, sys, zipfile

PATH_PAT = re.compile(r"(^|[\\/])humanizer([\\/]|$)|HUMANIZER-SKILL\.md", re.I)
NAME_PAT = re.compile(r"^humanizer-(skill|rules|tasks)\.md$", re.I)
MARKER = re.compile("".join(["Humanizer", "-Academic-", "EN"]), re.I)
_M = "".join(["M", "TI"])
FINGERPRINT = [(_M, "".join(["tri", "ad"])), (_M, "-ing tail"), (_M, "".join(["ing-", "tail"]))]


def members(target):
    """Yield (label, bytes) for every file in a dir tree or zip."""
    if zipfile.is_zipfile(target):
        with zipfile.ZipFile(target) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                try:
                    yield info.filename, z.read(info)
                except Exception:
                    yield info.filename, b""
    elif os.path.isdir(target):
        for root, _, files in os.walk(target):
            for f in files:
                p = os.path.join(root, f)
                try:
                    yield p, open(p, "rb").read()
                except OSError:
                    yield p, b""
    else:
        yield target, open(target, "rb").read()


def scan(target):
    hits = []
    for name, blob in members(target):
        base = os.path.basename(name)
        if PATH_PAT.search(name) or NAME_PAT.search(base):
            hits.append((name, "path"))
            continue
        try:
            text = blob.decode("utf-8", errors="ignore")
        except Exception:
            continue
        if MARKER.search(text):
            hits.append((name, "marker"))
            continue
        low = text.lower()
        if any(a.lower() in low and b.lower() in low for a, b in FINGERPRINT):
            hits.append((name, "fingerprint"))
    return hits


def stage(src, dst):
    """Copy skill tree to dst WITHOUT private material; strip SKILL.md section 6."""
    import shutil
    if os.path.exists(dst):
        shutil.rmtree(dst)
    def ign(d, names):
        return [n for n in names if n == "humanizer" or n == "humanize.py"]
    shutil.copytree(src, dst, ignore=ign)
    sk = os.path.join(dst, "SKILL.md")
    if os.path.exists(sk):
        s = open(sk, encoding="utf-8").read()
        i = s.find("## 6. Humanizer module")
        if i != -1:
            open(sk, "w", encoding="utf-8").write(s[:i].rstrip() + "\n")
    return dst


def main(argv):
    if len(argv) >= 3 and argv[0] == "stage":
        stage(argv[1], argv[2])
        print(f"staged public copy -> {argv[2]}")
        argv = ["scan", argv[2]]
    if len(argv) < 2 or argv[0] != "scan":
        print(__doc__)
        return 2
    dirty = False
    for t in argv[1:]:
        if not os.path.exists(t):
            print(f"ERROR: missing target {t}")
            return 2
        hits = scan(t)
        if hits:
            dirty = True
            print(f"DIRTY: {t}")
            for name, kind in hits[:40]:
                print(f"  [{kind}] {name}")
        else:
            print(f"clean: {t}")
    print("VERDICT:", "dirty — DO NOT SHIP (PRIV-1/PRIV-4)" if dirty else "clean")
    return 1 if dirty else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

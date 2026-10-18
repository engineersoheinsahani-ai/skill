#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""humanize.py — machine-tone gates for journal-arena, implementing the user-supplied
Humanizer-Academic-EN skill (see ../humanizer/{RULES.md,TASKS.md}).

Computes the countable gates of TASKS.md "Master exit summary" on a manuscript draft:
  title blacklist hits, abstract/body MTI, -ing tails, triads, not-but,
  conclusion-ritual openers, vague citations, hedge density, [number needed] leftovers.

Usage:
  python3 humanize.py score draft.txt --title "..." --abstract abstract.txt
  python3 humanize.py score draft.txt            # whole text treated as body

Exit code 0 = all computable gates pass; 1 = at least one gate failed.
NEVER edits text: this tool only measures. Editing lives in the writers' playbook.
"""
import argparse, re, sys, json

# ---- R1.1 umbrella-adjective blacklist (primary + secondary) -----------------
BLACKLIST = (r"(?ix)\b(additionally|crucial|comprehensive|delv\w*|emphasiz\w*|enduring|"
             r"enhanc\w*|foster\w*|highlight\w*|intricate|landscape|meticul\w*|notably|pivotal|"
             r"testament|underscor\w*|vital|align\swith)\b")
BLACKLIST2 = (r"(?ix)\b(interplay|bolster\w*|garner\w*|boast\w*|tapestr\w*|"
              r"sheds?\slight|deep\sdive)\b|plays\s+a\s+(vital|crucial|pivotal|key)\s+role|"
              r"a\s+step\s+forward")

# ---- R2 patterns -------------------------------------------------------------
TRIAD = r"(?ix)\b[a-z][a-z' -]{1,30},\s+[a-z][a-z' -]{1,30}\s+(?:and|&)\s+[a-z][a-z' -]{1,30}\b"
INGTAIL = r"""(?ix),\s+(ensuring|highlighting|providing|enabling|reflecting|supporting|
 fostering|demonstrating|indicating|showing|revealing|allowing|reducing|improving|
 offering|yielding|confirming|underscoring|facilitating|promoting|contributing|
 emphasizing)\b"""
NOTBUT = r"(?ix)\bnot\s+(?:merely|just|so\s+much|only)?\s*[a-z][a-z' -]{0,40},\s+but\b"
CONCL = r"(?im)^\s*(In\s+conclusion|Overall\s*,?|To\s+summarize|In\s+summary)\b"
VAGUE = (r"(?ix)\b(studies\s+have\s+shown|previous\s+studies\s+have|it\s+is\s+well\s+known|"
         r"research\s+has\s+shown|several\s+studies\s+have|a\s+number\s+of\s+studies)\b")
HEDGE = (r"(?ix)\b(may|might|suggests?|suggesting\s+that|possibly|likely|in\s+our\s+sample|"
         r"to\s+our\s+knowledge|appears\s+to)\b")
NEEDNUM = r"\[number needed\]"
WE = r"(?ix)\b(we|our)\b"
WORDS = r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*"


def n(pattern, text):
    return len(re.findall(pattern, text))


def mti(text):
    """Machine-Tone Index per 1k words (SKILL.md appendix A)."""
    w = max(1, n(WORDS, text))
    hits = n(BLACKLIST, text) + n(BLACKLIST2, text) + n(TRIAD, text) + n(INGTAIL, text)
    return round(hits / w * 1000, 2), hits, w


def band(v):
    return "human-range" if v <= 4 else ("gray" if v <= 8 else "machine-range")


def score(body, title=None, abstract=None):
    out = {}
    bt = abstract if abstract else body
    m_abs, h_abs, w_abs = mti(bt)
    m_body, h_body, w_body = mti(body)
    out["title_blacklist"] = (n(BLACKLIST, title) + n(BLACKLIST2, title)) if title else None
    out["abstract_mti"] = m_abs
    out["abstract_mti_band"] = band(m_abs)
    out["body_mti"] = m_body
    out["body_mti_band"] = band(m_body)
    out["ing_tails"] = n(INGTAIL, body)
    out["triads"] = n(TRIAD, body)
    out["triad_cap_per_1500w"] = max(1, w_body // 1500)
    out["not_but"] = n(NOTBUT, body)
    out["conclusion_rituals"] = n(CONCL, body)
    out["vague_citations"] = n(VAGUE, body)
    out["hedges_per_1k"] = round(n(HEDGE, body) / max(1, w_body) * 1000, 2)
    out["we_our_per_1k"] = round(n(WE, body) / max(1, w_body) * 1000, 2)
    out["number_needed_left"] = n(NEEDNUM, body)
    gates = []
    if out["title_blacklist"] is not None:
        gates.append(("title blacklist = 0", out["title_blacklist"] == 0))
    gates.append(("abstract MTI <= 4", m_abs <= 4))
    gates.append(("body MTI <= 4", m_body <= 4))
    gates.append(("-ing tails = 0", out["ing_tails"] == 0))
    gates.append(("triads <= cap", out["triads"] <= out["triad_cap_per_1500w"]))
    gates.append(("not-but <= 1", out["not_but"] <= 1))
    gates.append(("conclusion rituals = 0", out["conclusion_rituals"] == 0))
    gates.append(("vague citations = 0", out["vague_citations"] == 0))
    gates.append(("hedges >= 1/1k in analysis", out["hedges_per_1k"] >= 1))
    gates.append(("no [number needed] left", out["number_needed_left"] == 0))
    out["gates"] = gates
    out["pass"] = all(ok for _, ok in gates)
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score"])
    ap.add_argument("body")
    ap.add_argument("--title", default=None)
    ap.add_argument("--abstract", default=None)
    a = ap.parse_args(argv)
    body = open(a.body, encoding="utf-8").read()
    abstract = open(a.abstract, encoding="utf-8").read() if a.abstract else None
    r = score(body, a.title, abstract)
    print(json.dumps({k: v for k, v in r.items() if k != "gates"}, ensure_ascii=False, indent=1))
    for name, ok in r["gates"]:
        print(("  PASS  " if ok else "  FAIL  ") + name)
    print("VERDICT:", "gates clear" if r["pass"] else "gates blocked")
    return 0 if r["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

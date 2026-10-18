#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""corpus.py — کورپوس‌ساز v3 (task/10-corpus.md). بدون کلید API.

Commands:
  seeds   --manuscript <txt> --work <dir>   extract numbered references -> seeds.jsonl
  queries --work <dir> [--axis "a,b,c"]     per-group OpenAlex/Crossref query plan
  fetch   --gid E2 --work <dir> [--max 25]  optional polite fetch (OpenAlex, mailto)
  coverage --work <dir>                     ledger coverage report per gid
"""
import argparse, json, os, re, sys, urllib.parse, urllib.request

TIER1 = ["Energy and Buildings", "Applied Energy", "Building and Environment",
         "Energy", "Journal of Building Engineering", "Energy and AI"]
AXIS_DEFAULT = ["residential energy prediction", "building stock modelling",
                "data leakage audit", "conformal prediction",
                "uncertainty quantification", "energy performance gap",
                "retrofit savings", "RECS microdata"]  # fallback ONLY; real axis = corpus axis
GIDS = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10"]
RECENCY = {"E2": 24, "E7": 24, "E10": 24}   # months; others -> 10-year window
MAILTO = os.environ.get("OPENALEX_MAILTO", "owner@example.org")  # polite pool, no key


def cmd_axis(a):
    """Derive the corpus axis FROM THE MANUSCRIPT (title + keywords). Never hardcode."""
    txt = open(a.manuscript, encoding="utf-8", errors="ignore").read()
    title = ""
    m = re.search(r"(?im)^title:\s*$\n(.+?)(?=\n\s*(?:authors|abstract|keywords)\b)", txt, re.S)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
    else:
        m2 = re.search(r"(?im)^title:\s*(.+)$", txt)
        if m2:
            title = m2.group(1).strip()
    terms, src = [], "manuscript keywords"
    mk = re.search(r"(?im)^keywords:\s*$\n(.+?)(?=\n\s*={5,}|\n\s*(?:abstract|introduction)\b)", txt, re.S)
    if mk:
        kw = re.sub(r"\s+", " ", mk.group(1)).strip()
        terms = [t.strip(" .") for t in re.split(r"[;•]", kw) if len(t.strip()) > 2]
    if not terms:
        terms, src = list(AXIS_DEFAULT), "fallback"
    out = os.path.join(a.work, "corpus", "axis.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"title": title, "terms": terms, "source": src,
               "manuscript": os.path.abspath(a.manuscript)},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"axis [{src}]: {len(terms)} terms -> {out}")
    for t in terms:
        print("  -", t)
    return 0


def cmd_seeds(a):
    """Parse the REFERENCES section (author-year blocks; indented continuation lines)."""
    txt = open(a.manuscript, encoding="utf-8", errors="ignore").read()
    m = re.search(r"(?im)^\s*references\s*$", txt)
    body = txt[m.end():] if m else txt
    body = re.split(r"(?m)^={10,}\s*$", body)
    body = body[1] if len(body) > 1 else body[0]
    entries, cur = [], []
    for line in body.splitlines():
        if not line.strip():
            continue
        if line[0].isspace():
            if cur:
                cur.append(line.strip())
        else:
            if cur:
                entries.append(" ".join(cur))
            cur = [line.strip()]
    if cur:
        entries.append(" ".join(cur))
    os.makedirs(os.path.join(a.work, "corpus"), exist_ok=True)
    out = os.path.join(a.work, "corpus", "seeds.jsonl")
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for e in entries:
            e = re.sub(r"\s+", " ", e).strip()
            if len(e) < 20 or not re.search(r"(19|20)\d{2}", e):
                continue
            n += 1
            f.write(json.dumps({"source_id": f"seed-{n:03d}", "cite": e[:280],
                                "tier": "metadata", "origin": "manuscript-ref"},
                               ensure_ascii=False) + "\n")
    print(f"seeds: {n} references -> {out}")
    return 0


def oa_url(search, journal=None, months=None):
    filt = []
    if months:
        import datetime
        d = (datetime.date.today() - datetime.timedelta(days=30 * months)).isoformat()
        filt.append(f"from_publication_date:{d}")
    if journal:
        filt.append(f"primary_location.source.display_name.search:{journal}")
    q = {"search": search, "per-page": "25", "mailto": MAILTO}
    if filt:
        q["filter"] = ",".join(filt)
    return "https://api.openalex.org/works?" + urllib.parse.urlencode(q)


def cmd_queries(a):
    axisfile = os.path.join(a.work, "corpus", "axis.json")
    if a.axis:
        axis = [t.strip() for t in a.axis.split(",") if t.strip()]
    elif os.path.exists(axisfile):
        axis = json.load(open(axisfile, encoding="utf-8"))["terms"]
    else:
        axis = list(AXIS_DEFAULT)
        print("WARNING: no axis.json and no --axis; built-in fallback used. Run `corpus axis` first.")
    os.makedirs(os.path.join(a.work, "corpus"), exist_ok=True)
    out = os.path.join(a.work, "corpus", "query-plan.jsonl")
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for gid in GIDS:
            months = RECENCY.get(gid, 120)
            terms = {"E4": axis[:3] + ["uncertainty quantification", "statistical validation", "data leakage audit"],
                     "E5": axis[:2] + ["reproducibility", "open source pipeline", "code availability"],
                     "E8": axis[:2] + ["data availability statement", "research ethics"]}.get(gid, axis)
            for t in terms[:4]:
                f.write(json.dumps({"gid": gid, "term": t, "months": months,
                                    "openalex": oa_url(t, months=months)}, ensure_ascii=False) + "\n")
                n += 1
            for j in TIER1[:3]:
                f.write(json.dumps({"gid": gid, "term": j, "months": months,
                                    "openalex": oa_url(terms[0], journal=j, months=months)},
                                   ensure_ascii=False) + "\n")
                n += 1
    print(f"queries: {n} planned ({len(GIDS)} groups) -> {out}")
    print("tier-1 journals:", "; ".join(TIER1))
    return 0


def cmd_fetch(a):
    import time
    plan = os.path.join(a.work, "corpus", "query-plan.jsonl")
    rows = [json.loads(l) for l in open(plan, encoding="utf-8") if l.strip()]
    mine = [r for r in rows if r["gid"] == a.gid][: a.queries]
    got = 0
    dest = os.path.join(a.work, "corpus", a.gid)
    os.makedirs(dest, exist_ok=True)
    for r in mine:
        try:
            req = urllib.request.Request(r["openalex"], headers={"User-Agent": "journal-arena/3 (mailto)"})
            data = json.load(urllib.request.urlopen(req, timeout=20))
            for w in data.get("results", [])[: a.max]:
                rec = {"gid": a.gid, "source_id": f"{a.gid.lower()}-{got:03d}",
                       "cite": w.get("display_name"), "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
                       "year": w.get("publication_year"), "tier": "abstract",
                       "abstract_inv": w.get("abstract_inverted_index") is not None,
                       "oa_url": (w.get("open_access") or {}).get("oa_url"),
                       "url": r["openalex"]}
                with open(os.path.join(dest, "list.jsonl"), "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                got += 1
            time.sleep(1.0)  # polite: <=1 req/s
        except Exception as e:
            print(f"fetch degraded (offline/ratelimit): {type(e).__name__}: {e}")
            break
    print(f"fetched {got} works for {a.gid} -> {dest}/list.jsonl")
    return 0




E6_INTEGRITY_TERMS = ["data integrity audit research", "research integrity paper mill",
                      "citation manipulation detection", "image forensics publication",
                      "FAIR data availability statement", "results verification reproducibility"]


def _load_list(gid, work):
    p = os.path.join(work, "corpus", gid, "list.jsonl")
    if not os.path.exists(p):
        return p, []
    rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return p, rows


def _fetch_oa(url, months=None, per_page=25, page=1, oa_only=True):
    q = {"search": url, "per-page": str(per_page), "page": str(page), "mailto": MAILTO}
    filt = []
    if months:
        import datetime
        d = (datetime.date.today() - datetime.timedelta(days=30 * months)).isoformat()
        filt.append(f"from_publication_date:{d}")
    if oa_only:
        filt.append("open_access.is_oa:true")   # countable-100 needs full text (owner policy)
    if filt:
        q["filter"] = ",".join(filt)
    api = "https://api.openalex.org/works?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(api, headers={"User-Agent": "journal-arena/3 (mailto)"})
    return json.load(urllib.request.urlopen(req, timeout=20)).get("results", [])


def cmd_topup(a):
    """Bring one gid's corpus up to --need unique works (pagination + integrity terms + snowball)."""
    import time
    p, rows = _load_list(a.gid, a.work)
    seen = {r.get("doi") or r.get("cite") for r in rows}
    start = len(rows)
    print(f"{a.gid}: have {start}, need {a.need}")
    if start >= a.need:
        return 0
    terms = E6_INTEGRITY_TERMS if a.gid == "E6" else None
    if terms is None:
        axisfile = os.path.join(a.work, "corpus", "axis.json")
        base = json.load(open(axisfile, encoding="utf-8"))["terms"] if os.path.exists(axisfile) else AXIS_DEFAULT
        terms = [f"{t} data integrity" for t in base[:3]] + base[:3]
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        n = start
        for t in terms:
            if n >= a.need:
                break
            try:
                pages = []
                for pg in range(1, a.pages + 1):
                    pages.extend(_fetch_oa(t, months=RECENCY.get(a.gid, 120), page=pg))
                    time.sleep(1.0)
                for w in pages:
                    doi = (w.get("doi") or "").replace("https://doi.org/", "")
                    key = doi or w.get("display_name")
                    if key in seen:
                        continue
                    seen.add(key)
                    n += 1
                    rec = {"gid": a.gid, "source_id": f"{a.gid.lower()}-{n:03d}",
                           "cite": w.get("display_name"), "doi": doi, "year": w.get("publication_year"),
                           "tier": "abstract",  # honest: body only after `corpus bodies` extracts text
                           "oa_url": (w.get("open_access") or {}).get("oa_url"), "origin": "topup"}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    if n >= a.need:
                        break
            except Exception as e:
                print(f"topup degraded: {type(e).__name__}: {e}")
            time.sleep(1.0)
    print(f"{a.gid}: {start} -> {n} unique works")
    return 0 if n >= a.need else 1


def cmd_bodies(a):
    """Upgrade tier abstract->body by fetching OA full text (best effort, polite)."""
    import time, re as _re
    p, rows = _load_list(a.gid, a.work)
    dest = os.path.join(a.work, "corpus", a.gid, "bodies")
    os.makedirs(dest, exist_ok=True)
    up = fail = done = 0
    log = []
    for r in rows:
        if done >= a.max:
            break
        if r.get("tier") == "body" or not r.get("oa_url"):
            continue
        done += 1
        try:
            req = urllib.request.Request(r["oa_url"], headers={"User-Agent": "journal-arena/3 (mailto)"})
            blob = urllib.request.urlopen(req, timeout=25).read()
            ctype = "pdf" if blob[:4] == b"%PDF" else "html"
            if ctype == "html":
                text = _re.sub(r"<[^>]+>", " ", blob.decode("utf-8", "ignore"))
                text = _re.sub(r"\s+", " ", text)
            else:
                try:
                    from pypdf import PdfReader
                    import io
                    text = "\n".join((pg.extract_text() or "") for pg in PdfReader(io.BytesIO(blob)).pages)
                except Exception:
                    text = ""
            if len(text.strip()) >= 400:
                sid = r["source_id"]
                open(os.path.join(dest, f"{sid}.txt"), "w", encoding="utf-8").write(text)
                r["tier"] = "body"
                up += 1
            else:
                fail += 1
                log.append({"source_id": r["source_id"], "reason": f"{ctype}-text-too-short-or-no-extractor"})
            time.sleep(1.0)
        except Exception as e:
            fail += 1
            log.append({"source_id": r["source_id"], "reason": f"{type(e).__name__}: {e}"})
    with open(p, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if log:
        json.dump(log, open(os.path.join(dest, "fetch-log.json"), "w", encoding="utf-8"), indent=1)
    print(f"bodies {a.gid}: upgraded {up}, failed {fail}, attempted {done}; text -> {dest}; reasons -> bodies/fetch-log.json")
    return 0


def cmd_coverage(a):
    # list.jsonl is the AUTHORITATIVE corpus state (tiers updated by `corpus bodies`);
    # the ledger tracks reading progress, not coverage.
    per = {}
    for gid in GIDS:
        lp = os.path.join(a.work, "corpus", gid, "list.jsonl")
        if os.path.exists(lp):
            d = per.setdefault(gid, {"n": 0, "body": 0, "abstract": 0})
            for l in open(lp, encoding="utf-8"):
                if l.strip():
                    w = json.loads(l)
                    d["n"] += 1
                    d["body" if w.get("tier") == "body" else "abstract"] += 1
    if a.exception:
        os.makedirs(os.path.join(a.work, "corpus", a.gid), exist_ok=True)
        ex = os.path.join(a.work, "corpus", a.gid, "coverage-exception.json")
        json.dump({"gid": a.gid, "reason": a.exception,
                   "policy": "task/15-repair-protocol.md step 3b; council applies half-weight (law 4)",
                   "date": __import__("datetime").date.today().isoformat()},
                  open(ex, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("coverage exception recorded:", ex)
    # Owner policy (2026-10-11): countable-100 = FULL-TEXT-ACCESSIBLE papers from ANY
    # journal (priority: 1 axis-fit, 2 journal level). Abstract-only papers = mandatory
    # key-abstract reading + special BONUS points for the group; they do NOT count to 100.
    # owner decision 2026-10-11: study ceiling lowered 100 -> 20 (sufficiency);
    # groups may also carry a recorded coverage-exception (waiver with reason).
    print("gid  countable(body)  target  bonus(abstract)  status")
    for gid in GIDS:
        d = per.get(gid, {"n": 0, "body": 0, "abstract": 0})
        need = max(0, a.need - d["body"])
        if os.path.exists(os.path.join(a.work, "corpus", gid, "coverage-exception.json")):
            ok = "EXEMPT (exception on file)" if d["body"] < a.need else "OK (exception also on file)"
        else:
            ok = "OK" if d["body"] >= a.need else f"NEED {need} more full-text"
        print(f"{gid:4s} {d['body']:14d} {a.need:6d} {d['abstract']:15d}  {ok}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["axis", "seeds", "queries", "fetch", "topup", "bodies", "coverage"])
    ap.add_argument("--manuscript")
    ap.add_argument("--work", default="work")
    ap.add_argument("--axis", default=None)
    ap.add_argument("--gid", default="E2")
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--queries", type=int, default=3)
    ap.add_argument("--need", type=int, default=20)   # ceiling; owner decision 2026-10-11 (was 100)
    ap.add_argument("--pages", type=int, default=4)
    ap.add_argument("--exception", default=None)
    a = ap.parse_args(argv)
    return {"axis": cmd_axis, "seeds": cmd_seeds, "queries": cmd_queries,
            "fetch": cmd_fetch, "topup": cmd_topup, "bodies": cmd_bodies,
            "coverage": cmd_coverage}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

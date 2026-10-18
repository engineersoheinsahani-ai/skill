# -*- coding: utf-8 -*-
"""P0: map a plain-text manuscript into a machine-readable structure (model-agnostic input)."""
import json, re, sys, os

SEC_RE = re.compile(r"^={10,}\s*$")


def split_blocks(lines):
    blocks, cur, head = [], [], None
    i = 0
    while i < len(lines):
        if SEC_RE.match(lines[i].strip()) and i + 1 < len(lines) and SEC_RE.match(lines[i + 2].strip() if i + 2 < len(lines) else ""):
            if head is not None or cur:
                blocks.append((head, cur))
            head = lines[i + 1].strip()
            cur = []
            i += 3
            continue
        cur.append(lines[i])
        i += 1
    blocks.append((head, cur))
    return blocks


def words(t):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-\.]*", t))


def main(src, out_dir):
    lines = open(src, encoding="utf-8").read().splitlines()
    blocks = split_blocks(lines)
    m = {"source": os.path.abspath(src), "blocks": [], "sections": {}, "meta": {}}
    for head, body in blocks:
        text = "\n".join(body).strip()
        if not head:
            head = "(preamble)"
        m["blocks"].append({"head": head, "words": words(text), "chars": len(text),
                            "first_line": text.splitlines()[0][:80] if text else ""})
        m["sections"][head] = text

    g = lambda k: m["sections"].get(k, "")
    # highlights bullets
    hl = g("Highlights")
    bullets = [l.strip("•- ").strip() for l in hl.splitlines() if l.strip().startswith(("•", "-"))]
    stray = [l.strip() for l in hl.splitlines()
             if l.strip() and not l.strip().startswith(("•", "-"))]
    # title page
    tp = g("TITLE PAGE")
    title = ""
    if "Title:" in tp:
        title = tp.split("Title:", 1)[1].split("Authors:", 1)[0].replace("\n", " ").strip()
        title = re.sub(r"\s+", " ", title)
    kws = []
    if "Keywords:" in tp:
        kws = [k.strip() for k in tp.split("Keywords:", 1)[1].replace("\n", " ").split(";") if k.strip()]
    # abstract
    ab = g("ABSTRACT")
    # tables / figures defined & cited
    full = "\n".join(m["sections"].values())
    tbl_def = sorted({int(n) for n in re.findall(r"^Table (\d+)\.", full, re.M)})
    tbl_cit = sorted({int(n) for n in re.findall(r"Table (\d+)", full)})
    fig_def = sorted({int(n) for n in re.findall(r"^Fig\.? (\d+)[\.:]", full, re.M)})
    fig_cit = sorted({int(n) for n in re.findall(r"Fig\.? (\d+)", full)})
    # references
    refs = g("REFERENCES")
    entries = re.findall(r"\n([A-Z][A-Za-z\.\- ’/]+?(?:\([\w ;\/]+\))?, \d{4}\.|^[A-Z][A-Z\/ \.]+ \([A-Z][^)]+\), \d{4}\.)", refs, re.M)
    # entry = non-indented start line + indented/wrapped continuation lines.
    # Org authors (ABCB / DCCEEW (Australian Building Codes Board; Department of
    # Climate\n    Change, ...), 2019.) were missed by the single-line regex
    # (audit 2.7: 17 found vs 18 true).
    _entries, _cur = [], None
    for _ln in refs.splitlines():
        if not _ln.strip():
            continue
        _is_new = (not _ln.startswith((" ", "\t")) and re.match(r"^[A-Z(\[]", _ln)
                   and _cur and re.search(r", (19|20)\d{2}", _cur))
        if _is_new:
            _entries.append(_cur)
            _cur = _ln.strip()
        elif _cur is None:
            _cur = _ln.strip()
        else:
            _cur += " " + _ln.strip()
    if _cur:
        _entries.append(_cur)
    entry_heads = [e[:90] for e in _entries if re.search(r", (19|20)\d{2}[a-z]?\.", e)]
    # in-text citations (author-year)
    incit = re.findall(r"\(([A-Z][A-Za-z\-’]+(?:, [A-Za-z\-’]+)*(?: and [A-Za-z\-’]+)?(?: et al\.)?, \d{4}[a-z]?)\)", full)
    m["meta"] = {
        "title": title, "title_words": words(title),
        "keywords": kws, "n_keywords": len(kws),
        "abstract_words": words(ab),
        "highlights_bullets": bullets,
        "highlights_bullet_lens": [len(b) for b in bullets],
        "highlights_stray_lines": stray,
        "tables_defined": tbl_def, "tables_cited": tbl_cit,
        "figures_defined": fig_def, "figures_cited": fig_cit,
        "n_reference_entries": len(entry_heads),
        "reference_heads": entry_heads,
        "in_text_citations": sorted(set(incit)),
        "body_words": sum(b["words"] for b in m["blocks"] if b["head"] != "(preamble)"),
        "has_revision_notes": "REVISION NOTES" in full or any(h.startswith("REVISION NOTES") for h in m["sections"]),
        "sections_order": [b["head"] for b in m["blocks"]],
    }
    os.makedirs(out_dir, exist_ok=True)
    json.dump(m, open(os.path.join(out_dir, "manuscript-map.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"mapped {len(m['blocks'])} blocks | body {m['meta']['body_words']} w | "
          f"abstract {m['meta']['abstract_words']} w | kw {m['meta']['n_keywords']} | "
          f"hl bullets {len(bullets)} (stray {len(stray)}) | refs {len(entry_heads)} | "
          f"tables {tbl_def} cited {tbl_cit} | figs cited {fig_cit}")
    return m


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "work")

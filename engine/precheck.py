# -*- coding: utf-8 -*-
"""P1: deterministic pre-submission checks -> rule-id'd findings (no LLM needed)."""
import json, os, re, sys

SEV = {"blocker": 0, "major": 1, "minor": 2, "style": 3}


def F(rid, sev, section, quote, issue, suggestion, axis):
    return {"id": rid, "severity": sev, "section": section, "quote": quote,
            "issue": issue, "suggestion": suggestion, "axis_link": axis,
            "group": "P1-precheck", "rule": rid}


def run(map_path, ms_path, out_dir):
    m = json.load(open(map_path, encoding="utf-8"))
    meta, secs = m["meta"], m["sections"]
    full = "\n".join(secs.values())
    fx = []

    if meta["has_revision_notes"]:
        fx.append(F("LEFTOVER-001", "blocker", "REVISION NOTES",
                    "REVISION NOTES (delete before submission)",
                    "Internal revision memo left in the submission file; it exposes internal "
                    "process details (run stamps, AI 'humanisation' passes) that reviewers must "
                    "not see and that contradict the AI-declaration wording.",
                    "Delete the whole block from the submission manuscript (keep it only in the "
                    "author's private master copy).",
                    "Desk-reject risk: leftover editorial artefacts signal an unpolished submission."))
    if meta["abstract_words"] > 250:
        fx.append(F("ENB-ABS-1", "major", "ABSTRACT", full[:0] or secs.get("ABSTRACT", "")[:60],
                    f"Abstract is {meta['abstract_words']} words; ENB caps at 250.",
                    "Trim to <=250 words keeping purpose/procedures/findings/conclusions.",
                    "Hard journal limit; over-long abstracts are returned by the editorial office."))
    hl = meta["highlights_bullets"]; hll = meta["highlights_bullet_lens"]
    if not (3 <= len(hl) <= 5):
        fx.append(F("ENB-HL-2", "major", "Highlights", "; ".join(hl)[:60],
                    f"{len(hl)} bullets; allowed 3-5.", "Reduce/merge to 3-5 bullets.",
                    "Mandatory submission item with strict count."))
    for b, n in zip(hl, hll):
        if n > 85:
            fx.append(F("ENB-HL-2", "major", "Highlights", b,
                        f"Bullet is {n} chars (>85 incl. spaces).", "Shorten to <=85 chars.",
                        "Hard character limit enforced by the submission system."))
    if meta["highlights_stray_lines"]:
        fx.append(F("ENB-HL-1", "major", "Highlights", meta["highlights_stray_lines"][0],
                    "Non-bullet lines (title/authors) inside the Highlights block; the separate "
                    "highlights file must contain bullets only.",
                    "Keep bullets only in highlights file; title/authors belong to title page.",
                    "File-format compliance; stray lines break highlights ingestion."))
    if meta["n_keywords"] > 7:
        fx.append(F("ENB-KW-1", "major", "TITLE PAGE", "; ".join(meta["keywords"]),
                    f"{meta['n_keywords']} keywords; allowed 1-7.",
                    "Drop the least discoverable keywords to <=7 (e.g. merge 'Energy performance "
                    "gap' into others; 'RECS' is a survey name, not an indexing keyword).",
                    "Indexing rule; excess keywords are returned at submission."))
    for k in meta["keywords"]:
        if re.search(r"\b(and|of)\b", k):
            fx.append(F("ENB-KW-1", "minor", "TITLE PAGE", k,
                        "Multi-word keyword with 'and'/'of' discouraged.",
                        "Rephrase as a compact indexing term.", "Keyword quality/discoverability."))
    if meta["title_words"] > 20:
        fx.append(F("ENB-TP-1", "minor", "TITLE PAGE", meta["title"],
                    f"Title runs {meta['title_words']} words; guide asks concise titles.",
                    "Shorten while keeping 'leakage-audited', 'uncertainty-calibrated', "
                    "'national-scale' (the axis keywords).",
                    "Title is the first scope signal for the desk editor."))
    tg, tc = meta["tables_cited"], meta["tables_defined"]
    gap_t = sorted(set(range(1, max(tc + [0]) + 1)) - set(tc))
    if gap_t:
        fx.append(F("ENB-TBL-1", "major", "RESULTS", f"(structural) table numbering {tc}",
                    f"Table numbering gap: no Table {gap_t} cited/defined.",
                    "Renumber tables consecutively (or restore the missing table).",
                    "Consecutive numbering is a formatting gate; gaps read as missing content."))
    fg = meta["figures_cited"]
    gap_f = sorted(set(range(1, max(fg + [0]) + 1)) - set(fg))
    if gap_f:
        fx.append(F("ENB-FIG-1", "major", "RESULTS", f"(structural) figure citations {fg}",
                    f"Figure numbering gap: Fig. {gap_f} never cited/defined.",
                    "Renumber figures consecutively or add the missing figure.",
                    "Consecutive numbering is a formatting gate."))
    if "will be archived" in secs.get("Data availability", "") or "upon acceptance" in secs.get("Data availability", ""):
        fx.append(F("DAT-2", "major", "DECLARATIONS", "will be archived on Zenodo and GitHub upon acceptance",
                    "ENB enforces data Option C: deposit + cite + link AT submission; a promise "
                    "to archive after acceptance does not satisfy it.",
                    "Deposit code/audit-report/manifests to Zenodo NOW (DOI is instant, no "
                    "publication needed) and cite with [dataset]/[software] + DOI; keep RECS/TMY3/"
                    "ResStock citations as third-party data references.",
                    "Option C is a journal requirement; missing data citation is a return reason."))
    if not re.search(r"Funding|did not receive any specific grant", full, re.I):
        fx.append(F("POL-FUND-1", "minor", "DECLARATIONS", "(absent)",
                    "No funding statement; Elsevier recommends the standard no-funding sentence.",
                    "Add: 'This research did not receive any specific grant from funding agencies "
                    "in the public, commercial, or not-for-profit sectors.'",
                    "Funding disclosure is part of the submission declaration."))
    if not re.search(r"sex|gender", full, re.I):
        fx.append(F("SAGER-5b", "minor", "DATA / LIMITATIONS", "(absent)",
                    "Sex/gender neither used nor discussed although RECS microdata carry "
                    "household-reference-person demographics (SAGER applied-sciences items).",
                    "Add one sentence in Data or Limitations stating sex/gender was not a "
                    "predictor and noting the generalisability limitation.",
                    "SAGER compliance is checked by editors; a one-sentence fix removes the flag."))
    # reference hygiene
    heads = meta["reference_heads"]
    web_no_date = [h for h in heads if "http" in h and "accessed" not in h]
    if web_no_date:
        fx.append(F("REF-2", "minor", "REFERENCES", web_no_date[0][:60],
                    f"{len(web_no_date)} web reference(s) without access date.",
                    "Add '(accessed DD Month YYYY)' to each web reference.",
                    "Journal reference style requires access dates for web sources."))
    etal_full = [c for c in meta["in_text_citations"] if c.count(",") >= 3 and "et al" not in c]
    etal_short = [c for c in meta["in_text_citations"] if "et al" in c]
    if etal_full and etal_short:
        fx.append(F("REF-1", "minor", "INTRODUCTION", etal_full[0],
                    "Mixed et-al convention: some 3+-author works cited with full author lists, "
                    "others as 'et al.' — style must be consistent.",
                    "Pick one convention (recommended: list up to 2 authors, then et al.) and "
                    "apply everywhere.",
                    "Consistency is the only hard referencing rule at submission."))
    ds = [h for h in heads if "ResStock" in h or "RECS" in h or "Public Use Data" in h]
    if ds and not re.search(r"\[dataset\]", full):
        fx.append(F("DAT-4", "minor", "REFERENCES", ds[0][:60],
                    "Third-party datasets cited without the [dataset] tag / version elements.",
                    "Tag dataset references with [dataset] and include version/year/identifier.",
                    "Data citation is part of Option C compliance."))
    if not re.search(r"line number", full, re.I):
        fx.append(F("ENB-LINE-1", "minor", "KIT", "(file property)",
                    "Continuous line numbers are a journal-specific requirement for the "
                    "submitted manuscript file (not visible in this plain-text master).",
                    "Enable continuous line numbering in the Word/LaTeX submission file.",
                    "Reviewers reference lines; missing numbers slow review and flag formatting."))
    fx.append(F("ENB-GA-1", "blocker", "KIT", "(absent)",
                "No graphical abstract artefact exists yet; ENB requires it AT submission "
                "(531x1328 px+, readable at 5x13 cm).",
                "Produce one pictorial summary (pipeline: audit -> conformal intervals -> "
                "honest ceiling -> retrofit bounds); keep text minimal; no GenAI-primary images.",
                "Mandatory submission item; absence = incomplete submission."))

    fx.sort(key=lambda f: SEV[f["severity"]])
    os.makedirs(out_dir, exist_ok=True)
    json.dump(fx, open(os.path.join(out_dir, "precheck.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    lines = ["# Pre-submission precheck (deterministic)", "",
             f"Findings: {len(fx)}  |  blockers: {sum(f['severity']=='blocker' for f in fx)}  |  "
             f"major: {sum(f['severity']=='major' for f in fx)}  |  "
             f"minor: {sum(f['severity']=='minor' for f in fx)}", ""]
    for f in fx:
        lines += [f"## [{f['severity'].upper()}] {f['id']} — {f['section']}",
                  f"- quote: {f['quote'][:110]}", f"- issue: {f['issue']}",
                  f"- fix: {f['suggestion']}", f"- axis: {f['axis_link']}", ""]
    open(os.path.join(out_dir, "precheck-report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"precheck: {len(fx)} findings (blockers "
          f"{sum(f['severity']=='blocker' for f in fx)}, major "
          f"{sum(f['severity']=='major' for f in fx)})")
    return fx


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "work")

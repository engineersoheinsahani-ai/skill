# 05 — References: style, integrity, tooling (distilled, rule-id'd)
Sources: ENB guide references section; citationstyles.org (CSL); Mendeley Reference Manager;
ISSN LTWA (portal.issn.org/ltwa); Elsevier artwork/data reference rules.

## Style rules (REF-*)
- REF-1 Submission: any style acceptable **iff internally consistent** (author-year OR
  numbered — never mixed; et-al behaviour consistent for 3+ author works).
- REF-2 Journal style at proof: numbered [n] citation order; e.g.
  `[1] J. van der Geer, T. Handgraaf, R.A. Lupton, J. Sci. Commun. 163 (2020) 51–59. https://doi.org/…`
  journal titles abbreviated per **LTWA**; books: eds, edition, publisher, city;
  web: full URL + access date; datasets `[dataset]`; software `[software]`.
- REF-3 Bidirectional completeness: every in-text citation ↔ reference list entry.
- REF-4 Reality check: every entry must exist (Elsevier explicit); verify suspicious entries
  via DOI resolution or CrossRef `https://api.crossref.org/works?query.bibliographic=<title>`;
  mark `unverified` if offline — never delete/keep silently.
- REF-5 In-text: author-year style → "(Surname et al., YYYY)" for ≥3 authors EVERY time after
  first? (choose one convention and keep it); numbered style → "[3,6]" brackets, names optional.
- REF-6 Preprints labelled (server + DOI); unpublished results/personal comms NOT in list.
- REF-7 DOIs included where available (discoverability + integrity).

## Tooling (REF-T-*)
- REF-T-1 Use CSL journal template (Mendeley/Zotero) → auto ENB style; remove field codes.
- REF-T-2 LTWA lookup for every journal name when converting to journal style
  (e.g. "Energy and Buildings" → "Energy Build."; "Renewable and Sustainable Energy Reviews"
  → "Renew. Sustain. Energy Rev."; "Applied Energy" → "Appl. Energy").
- REF-T-3 Keep a `references.bib`-like JSON in work/ so conversions are mechanical, not manual.

## Known failure patterns the reviewer groups hunt
1. Mixed et-al conventions (full list once, et-al later) → REF-1 `minor`.
2. Web refs without access date (NREL/NeurIPS pages) → REF-2 `minor`.
3. Dataset used but cited as plain report (no `[dataset]`, no version) → DAT-4 `minor`.
4. Cited-in-text but missing from list (or vice versa) → REF-3 `blocker` if real gap.
5. Fabricated/hallucinated entries (wrong volume/pages) → REF-4 `blocker`.
6. Style drift inside list (some with DOI, some without; mixed italics) → REF-1 `minor`.

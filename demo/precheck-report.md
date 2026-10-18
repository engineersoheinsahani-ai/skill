# Pre-submission precheck (deterministic)

Findings: 14  |  blockers: 2  |  major: 5  |  minor: 7

## [BLOCKER] LEFTOVER-001 — REVISION NOTES
- quote: REVISION NOTES (delete before submission)
- issue: Internal revision memo left in the submission file; it exposes internal process details (run stamps, AI 'humanisation' passes) that reviewers must not see and that contradict the AI-declaration wording.
- fix: Delete the whole block from the submission manuscript (keep it only in the author's private master copy).
- axis: Desk-reject risk: leftover editorial artefacts signal an unpolished submission.

## [BLOCKER] ENB-GA-1 — KIT
- quote: (absent)
- issue: No graphical abstract artefact exists yet; ENB requires it AT submission (531x1328 px+, readable at 5x13 cm).
- fix: Produce one pictorial summary (pipeline: audit -> conformal intervals -> honest ceiling -> retrofit bounds); keep text minimal; no GenAI-primary images.
- axis: Mandatory submission item; absence = incomplete submission.

## [MAJOR] ENB-ABS-1 — ABSTRACT
- quote: Machine learning is now the default tool for predicting resi
- issue: Abstract is 273 words; ENB caps at 250.
- fix: Trim to <=250 words keeping purpose/procedures/findings/conclusions.
- axis: Hard journal limit; over-long abstracts are returned by the editorial office.

## [MAJOR] ENB-HL-1 — Highlights
- quote: A leakage-audited, uncertainty-calibrated pipeline for residential
- issue: Non-bullet lines (title/authors) inside the Highlights block; the separate highlights file must contain bullets only.
- fix: Keep bullets only in highlights file; title/authors belong to title page.
- axis: File-format compliance; stray lines break highlights ingestion.

## [MAJOR] ENB-KW-1 — TITLE PAGE
- quote: Residential energy prediction; Building stock modelling; Data leakage audit; Conformal prediction; Uncertainty
- issue: 9 keywords; allowed 1-7.
- fix: Drop the least discoverable keywords to <=7 (e.g. merge 'Energy performance gap' into others; 'RECS' is a survey name, not an indexing keyword).
- axis: Indexing rule; excess keywords are returned at submission.

## [MAJOR] ENB-TBL-1 — RESULTS
- quote: (structural) table numbering [1, 2, 4, 5]
- issue: Table numbering gap: no Table [3] cited/defined.
- fix: Renumber tables consecutively (or restore the missing table).
- axis: Consecutive numbering is a formatting gate; gaps read as missing content.

## [MAJOR] ENB-FIG-1 — RESULTS
- quote: (structural) figure citations [1, 2, 3, 4, 6]
- issue: Figure numbering gap: Fig. [5] never cited/defined.
- fix: Renumber figures consecutively or add the missing figure.
- axis: Consecutive numbering is a formatting gate.

## [MINOR] ENB-TP-1 — TITLE PAGE
- quote: A leakage-audited, uncertainty-calibrated pipeline for residential energy prediction: national-scale evidence 
- issue: Title runs 22 words; guide asks concise titles.
- fix: Shorten while keeping 'leakage-audited', 'uncertainty-calibrated', 'national-scale' (the axis keywords).
- axis: Title is the first scope signal for the desk editor.

## [MINOR] POL-FUND-1 — DECLARATIONS
- quote: (absent)
- issue: No funding statement; Elsevier recommends the standard no-funding sentence.
- fix: Add: 'This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.'
- axis: Funding disclosure is part of the submission declaration.

## [MINOR] SAGER-5b — DATA / LIMITATIONS
- quote: (absent)
- issue: Sex/gender neither used nor discussed although RECS microdata carry household-reference-person demographics (SAGER applied-sciences items).
- fix: Add one sentence in Data or Limitations stating sex/gender was not a predictor and noting the generalisability limitation.
- axis: SAGER compliance is checked by editors; a one-sentence fix removes the flag.

## [MINOR] REF-2 — REFERENCES
- quote: NeurIPS, 2025. NeurIPS paper checklist guidelines. https://n
- issue: 1 web reference(s) without access date.
- fix: Add '(accessed DD Month YYYY)' to each web reference.
- axis: Journal reference style requires access dates for web sources.

## [MINOR] REF-1 — INTRODUCTION
- quote: Dong, Lam, Huang and Dobbs, 2021
- issue: Mixed et-al convention: some 3+-author works cited with full author lists, others as 'et al.' — style must be consistent.
- fix: Pick one convention (recommended: list up to 2 authors, then et al.) and apply everywhere.
- axis: Consistency is the only hard referencing rule at submission.

## [MINOR] DAT-4 — REFERENCES
- quote: National Renewable Energy Laboratory, 2025. ResStock 2025.1:
- issue: Third-party datasets cited without the [dataset] tag / version elements.
- fix: Tag dataset references with [dataset] and include version/year/identifier.
- axis: Data citation is part of Option C compliance.

## [MINOR] ENB-LINE-1 — KIT
- quote: (file property)
- issue: Continuous line numbers are a journal-specific requirement for the submitted manuscript file (not visible in this plain-text master).
- fix: Enable continuous line numbering in the Word/LaTeX submission file.
- axis: Reviewers reference lines; missing numbers slow review and flag formatting.

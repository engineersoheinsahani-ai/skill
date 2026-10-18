# 04 — Research data, data statements, CRediT (distilled, rule-id'd)
Sources: elsevier.com/about/policies-and-standards/research-data; researcher/…/data-guidelines;
data-statement; data-base-linking; credit.niso.org; ENB guide (Option C).

## Research data policy principles (DAT-*)
- DAT-1 FAIR-aligned: data underlying findings should be findable, accessible, interoperable,
  reusable; deposit in a relevant repository (e.g. Mendeley Data, Zenodo).
- DAT-2 ENB enforces **Option C**: deposit REQUIRED + cite & link dataset in the article;
  if impossible → statement explaining why (e.g. confidential).
- DAT-3 Data availability statement mandatory at submission; published with article.
  Canonical options to phrase: (A) public repository + DOI/link; (B) available on reasonable
  request with reason; (C) restricted/embargoed with reason; (D) no new data generated.
- DAT-4 Dataset reference elements: author(s), title, repository, version, year, persistent
  identifier; tag `[dataset]`; in-text linking format `Database: ID`.
- DAT-5 Code/software/models count as research data: archive with DOI (Zenodo) and tag
  `[software]`; version + licence stated.
- DAT-6 Co-submission (Data in Brief / MethodsX) optional booster for reproducibility credit.
- DAT-7 Third-party data (RECS, TMY3, ResStock): cite the original sources precisely
  (publisher, version, year, URL/DOI) — licence terms respected & acknowledged.

## CRediT (CRED-*)
- CRED-1 14 roles: Conceptualization; Data curation; Formal analysis; Funding acquisition;
  Investigation; Methodology; Project administration; Resources; Software; Supervision;
  Validation; Visualization; Writing – original draft; Writing – review and editing.
- CRED-2 Corresponding author must provide CRediT statement for all co-authors;
  format "Name: Role, Role. Name: Role." ; only real contributions; degrees of contribution
  may be added optionally.
- CRED-3 Statement placed before references (with declarations block); role spellings exact
  (en-dash in "Writing – original draft").

## Checks the engine/agents must run
- Data statement tense: "will be archived upon acceptance" ≠ Option C (deposit BEFORE or at
  submission with citable DOI) → `major` finding (rule DAT-2/DAT-3).
- Every third-party dataset used → matching reference with `[dataset]` tag → else `minor`.
- CRediT roles ∈ the 14; both authors' roles plausible vs acknowledgements → else `minor`.

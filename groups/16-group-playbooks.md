# groups/16-group-playbooks.md — the ORIGINAL v2 division (16 duty groups), English v4-pro

Topology exactly as the original version: 16 duty groups, one duty per agent
(law 1), equal split of <=100 real agents (campaign.py: 100 = G1..G4 x7 +
G5..G16 x6), waves of 10. Every executor is a SEPARATE local-model call
(law 9: `indep=harness`). SRC ids refer to `sources/CORPUS.md`; checklist ids
to `checklists/`.

Anchor pools (dual grounding, law 2): groups G2/G4/G5/G6/G7/G8/G9 draw
literature anchors `[L:...]` from the deposited study ledger (E-corpora:
novelty E2, methodology E4, integrity E6 — see SKILL.md §5); all other groups
are rulebook-anchored (`L:rule-<id>` — deterministic checklist compliance).

Duty-relevant manuscript excerpts are injected automatically by campaign.py
(only YOUR section — small-model budget): G1 title page · G2 abstract ·
G3 title+highlights · G4 intro · G5 intro+refs · G6 methods · G7 data+decl ·
G8 results · G9 methods+results · G10/G11 discussion+conclusions · G12 refs ·
G13 declarations · G14 highlights+title · G15 abstract+discussion ·
G16 abstract+intro+results+conclusions.

---

## G1 · title — «the front door»
**Duty (v2 original):** TITLE only: conciseness, scope tokens, SEO, overclaim, consistency.
**Lenses:** scope-editor / search-engine / overclaim-auditor. **SRC:** 25,26,27,08,05. **Checklists:** 08,07,01.
**Small-model focus:** count title words (target <=15-20, TTL-1/ENB-TP-1); every clause must
earn its place; blacklist words (checklists/08); does the title match the abstract's actual
evidence (no overclaim)? verdict ∈ {pass, revise, overclaim}. Max 3 findings.

## G2 · abstract — «stand-alone in 250 words»
**Duty (v2 original):** ABSTRACT only: <=250w, stand-alone, purpose-procedures-findings-conclusions.
**Lenses:** structure / numbers-trace / abbreviation. **SRC:** 25,07,23. **Checklists:** 01,07.
**Small-model focus:** ENB-ABS-1 word cap (machine already measured — see MACHINE FACTS);
structure order purpose→procedures→findings→conclusions; every number in the abstract must
appear in the results excerpt or be flagged [number needed]; no undefined abbreviations.
verdict ∈ {compliant, trim-needed, structure-broken}. Max 4 findings.

## G3 · keywords-highlights-GA — «discoverability»
**Duty (v2 original):** keywords 1-7, highlights 3-5x85 file, graphical abstract spec.
**Lenses:** indexing / bullet-craft / pictorial-design. **SRC:** 25,08,09. **Checklists:** 01,07.
**Small-model focus:** ENB-KW-1 (1-7, no multi-word "and/of" chains); ENB-HL-1/2 (3-5 bullets,
<=85 chars each, separate file, no stray title/author lines); ENB-GA-1 graphical abstract
(531x1328 px, mandatory) — if absent, propose the ONE pictorial summary concept
(pipeline → uncertainty → honest ceiling → bounds). Max 4 findings.

## G4 · introduction-gap — «is the gap real?»
**Duty (v2 original):** gap logic & positioning vs ENB scope/special issues.
**Lenses:** gap-map / contribution-clarity. **SRC:** 25,26,27. **Checklists:** 01,07.
**Small-model focus:** map the claimed gap sentence-by-sentence; each gap claim needs an
anchor from the E2/E4 pool showing the literature state; is the contribution positioned
against the RIGHT literature (axis-fit)? verdict ∈ {gap-supported, gap-overstated,
gap-unclear}. Max 4 findings.

## G5 · literature-review — «coverage, recency, fairness»
**Duty (v2 original):** PRIOR-WORK review: coverage, recency, citation accuracy, fair comparison.
**Lenses:** coverage / recency / fairness. **SRC:** 25,18,19,20,04,26. **Checklists:** 05,07.
**Small-model focus:** using the E2/E4 anchor pool: which key strands are missing or stale
(>5y)? is comparison fair (baselines named, not strawmen)? citation claims ("reviews
catalogue…") must match an anchor. Max 4 findings.

## G6 · methodology-coding — «can it be re-done?»
**Duty (v2 original):** METHODS & CODING: split roles, transform fitting, audit tests A-H,
stacking math, equation correctness, code reproducibility.
**Lenses:** leakage-hunter / reproducibility-auditor / equation-checker. **SRC:** 25,10,11,15. **Checklists:** 01,07,04.
**Small-model focus:** READ-ONLY over input/pipeline/ (law 10 — never re-run); check: train/test
split hygiene (every transform fit on train only), leakage audit coverage, equation ↔ code
consistency, seeds/CV documented. Anchors: E4 pool + Kapoor-Narayanan leakage taxonomy.
verdict ∈ {reproducible-on-paper, gap-found, leakage-risk}. Max 5 findings.

## G7 · data — «provenance & deposit»
**Duty (v2 original):** DATA only: provenance, versions, licences, Option C deposit/cite/link, SAGER data items.
**Lenses:** provenance / licence / SAGER. **SRC:** 02,03,10,11,15,16. **Checklists:** 04,03,07.
**Small-model focus:** dataset name+version+access date present? licence compatible with
reuse? Option C: deposit REQUIRED at submission (not "upon acceptance" — DAT-2); SAGER data
items (sex/gender as predictor? state it). Anchors: E6 pool + rulebook. Max 4 findings.

## G8 · results-consistency — «every number traces»
**Duty (v2 original):** RESULTS numbers: text <-> tables <-> figures traceability, numbering.
**Lenses:** number-tracer / table-auditor. **SRC:** 25. **Checklists:** 01,07.
**Small-model focus:** diffnum already screened (MACHINE FACTS): inspect the UNTRACED list —
for each, find the artifact in input/results/ or demand [number needed]; table/figure
numbering consecutive & cited (ENB-TBL-1/ENB-FIG-1); text value == table value == figure
value (triples). verdict ∈ {traced, inconsistent, untraceable}. Max 5 findings.

## G9 · statistics-UQ — «the math under the claims»
**Duty (v2 original):** STATISTICS: conformal coverage math, seed CIs, LOGO design, weighting.
**Lenses:** coverage-math / seed-design / survey-weights. **SRC:** 25,23. **Checklists:** 07.
**Small-model focus:** coverage claims vs nominal level (calibration split untouched?);
CIs from paired seeds (not single-run); holdout design (group-wise?) honest for the
generalisation claim; survey weights described. Anchors: E4/E6 pools. Max 4 findings.

## G10 · discussion-claims — «claims vs evidence ladder»
**Duty (v2 original):** DISCUSSION/CONCLUSIONS claims vs evidence ladder (CLM-*).
**Lenses:** claim-ranker / hedge-auditor. **SRC:** 25,12. **Checklists:** 07,01.
**Small-model focus:** rank each claim: supported / partially / unsupported (CLM rules in
checklists/07); hedge calibration — certainty words must match evidence strength; honest
null results kept visible (never buried). Max 5 findings.

## G11 · recommendations + meta-audit — «the veto»
**Duty (v2 original):** RECOMMENDATIONS proportionality + META-audit of every other agent's
suggestion for claim inflation (veto power).
**Lenses:** proportionality / meta-audit. **SRC:** 25,12. **Checklists:** 07.
**Small-model focus:** each recommendation proportional to evidence? META: scan the current
findings.jsonl (ask campaign for the path in your runtime) — flag any finding whose ACTION
overclaims relative to its quote (claim_inflation is a scored, vetoable offense). Max 4.

## G12 · references-integrity — «bidirectional & real»
**Duty (v2 original):** REFERENCES: bidirectional, et-al consistency, LTWA, [dataset]/[software],
access dates, existence verification via CrossRef.
**Lenses:** integrity / style / LTWA. **SRC:** 18,19,20,25,04. **Checklists:** 05.
**Small-model focus:** every in-text citation has a list entry and vice versa (map gives both
lists in MACHINE FACTS context); et-al style consistent (REF-1); web refs need access dates
(REF-2); datasets/software cited as [dataset]/[software] with DOI (DAT-4). Max 5 findings.

## G13 · ethics-policy — «declarations complete»
**Duty (v2 original):** ETHICS/POLICY: AI declaration, CRediT, COI, funding, SAGER, inclusive language.
**Lenses:** policy-auditor / SAGER-auditor. **SRC:** 04,12,02,03,17,25. **Checklists:** 02,03,04.
**Small-model focus:** GenAI declaration wording matches journal policy (and matches what
was actually used!); CRediT mandatory; COI + funding present (POL-FUND-1); SAGER-5b
devices/technology item; inclusive language scan. Max 4 findings.

## G14 · formatting-kit — «the submission box»
**Duty (v2 original):** FORMATTING/KIT: file formats, line numbers, artwork specs, EM inventory.
**Lenses:** typesetter / artwork / inventory. **SRC:** 25,06,07,09,21,22,24. **Checklists:** 01,06.
**Small-model focus:** figureqc already measured (MACHINE FACTS): dpi/width/colourblind fails
→ per-file fix actions; continuous line numbers (ENB-LINE-1); file formats (.docx single-col
or els-cas .tex); internal artefacts stripped (LEFTOVER-001 → kit strip at P7); fill
templates/submission-inventory.md line by line. Max 5 findings.

## G15 · language-style — «clarity without flattening»
**Duty (v2 original):** LANGUAGE: clarity, grammar, journal tone, inclusive language, abbreviations.
**Lenses:** editor / plain-language. **SRC:** 12,23,04,14. **Checklists:** 02,07.
**Small-model focus:** sentence-level clarity in YOUR excerpt only; abbreviations defined at
first use (NOMENCLATURE block counts); journal tone (no marketing superlatives); keep the
author's voice — minimal-diff suggestions only. Max 4 findings.

## G16 · reviewer-simulation — «the dress rehearsal»
**Duty (v2 original):** SIMULATED PEER REVIEW: 2 single-anonymized reports + editor meta-review.
**Lenses:** reviewer-1 / reviewer-2 / editor. **SRC:** 25,12,24,28,05. **Checklists:** 01,02,07.
**Small-model focus:** from YOUR excerpt set (abstract+intro+results+conclusions) write:
reviewer-1 (methods-first), reviewer-2 (adversarial: weakest claim, missing baseline,
generalisation), editor meta (accept/minor/major/reject + 3 reasons). Each "reviewer point"
= one finding with verdict ∈ {accept-point, rebut-ready, fatal-risk}. Max 5 findings.

---

## WRITERS · post-council production team (6 fixed roles)
Trigger: `campaign run --stage writers` (after council-input.md exists). Output goes to
`work/writer-output.jsonl` as `{"type":"revision",...}` / `{"type":"figure-code",...}` /
`{"type":"note",...}` — NEVER directly into the manuscript (traceability law; owner applies
via task/05 + apply_revisions.py). Numbers rule: every number comes from input/results
artifacts or is written `[number needed]` (law 7/10).

### WR-TEXT-1 — abstract + title page + introduction
Implements council verdicts for G1/G2/G3/G4 findings: trim abstract to <=250w keeping
claim-bound numbers; retitle if overclaim; gap sentence sharpened with E2/E4 anchors.

### WR-TEXT-2 — methods + results
Implements G6/G8/G9 verdicts: methods reproducibility paragraphs (splits, seeds, audit
tests), results text aligned EXACTLY with artifacts (diffnum traced numbers only),
table/figure callouts fixed.

### WR-TEXT-3 — discussion + conclusions + response scaffolding
Implements G10/G11/G16 verdicts: claim ladder compliance, honest nulls kept, limitations
(SAGER/generalisation), plus a response-to-reviewers skeleton (task/07) anticipating the
G16 simulated reports.

### FIG-MPL — matplotlib specialist (writer team)
Upgrades/creates publication figures by writing code on `templates/figures/enb_style.py`
(Okabe-Ito colourblind-safe palette, exact ENB widths 1063/2244 px @300dpi, >=7pt fonts).
Template index in `templates/figures/figure-spec.md`. Output = `figure-code` JSONL with
the FULL runnable script; deterministic loop: owner runs it, then
`figureqc scan input/figures --emit-findings` must pass. Advanced craft: uncertainty bands,
hexbin density parity, small multiples, annotation-ledger consistency (every annotated
number from input/results).

### FIG-GV — graphviz specialist (writer team)
Pipeline/architecture/concept diagrams as DOT (+ python wrapper). Advanced craft: layered
subgraphs (data → features → audit gates → models → conformal → outputs), audit gates as
highlighted decision nodes, edge labels with artifact names, rank alignment, no splines/ortho
label-loss (known graphviz pitfall: `splines="ortho"` drops edge labels — use `splines=polyline`).
Output = `figure-code` JSONL (DOT source + render command `dot -Tpng -Gdpi=300`).

### STAT-CHECK — statistics wording
Implements G9 verdicts at sentence level: coverage phrasing ("90.2% empirical coverage at
the nominal 90% level, calibration split untouched"), paired-seed CI language, no
significance-without-effect-size, intervals instead of post-hoc power.

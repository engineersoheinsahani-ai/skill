# Source corpus — the 28 sources every agent may (and some must) study live
Agents are NOT limited to the distilled checklists: each brief lists SRC ids the agent must
open and read itself (web fetch / browser / search), then record what it learned in its
playbook with URL + access date. If a runtime has no web access, the agent falls back to
`checklists/` and marks `source_mode: distilled` in every finding.

> **v3 mapping (audit 2.5):** the "primary learners" column keeps the v2 G-ids for
> provenance. Current v3 groups (SKILL §2 / task/10b): manuscript (SRC 01) → ALL
> E1–E10 · SAGER (02, 03) → E8 · GenAI/AI policy (04) → E7+E8 · publishing
> overview (05) → E7 · LaTeX/formatting (06) → E9 · reference style → E7 ·
> data/repo sources → E5+E6.

| SRC | source | url / path | primary learners |
|-----|--------|-----------|------------------|
| 01 | Manuscript under review | uploads/manuscript_final.txt (local) | all |
| 02 | EASE SAGER Checklist 2022 (PDF) | ease.org.uk/wp-content/uploads/2023/01/EASE-SAGER-Checklist-2022.pdf | G7, G13 |
| 03 | SAGER guidelines Table 1 (Springer) | link.springer.com/article/10.1186/s41073-016-0007-6/tables/1 | G7, G13 |
| 04 | Elsevier Generative AI policies for journals | elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals | G5, G12, G13, G15 |
| 05 | Elsevier: publish in a journal (overview) | elsevier.com/publishing/publish-in-a-journal | G1, G16 |
| 06 | Elsevier LaTeX instructions | elsevier.com/researcher/author/policies-and-guidelines/latex-instructions | G14 |
| 07 | Researcher Academy: beginner's guide to LaTeX manuscripts | researcheracademy.elsevier.com/writing-research/technical-writing-skills/beginners-guide-writing-manuscript-latex | G2, G14 |
| 08 | Elsevier Highlights tool & examples | elsevier.com/researcher/author/tools-and-resources/highlights | G3 |
| 09 | Elsevier Graphical abstract guidelines | elsevier.com/researcher/author/tools-and-resources/graphical-abstract | G3, G14 |
| 10 | Elsevier Research data policy | elsevier.com/about/policies-and-standards/research-data | G6, G7 |
| 11 | Elsevier Research data guidelines | elsevier.com/researcher/author/tools-and-resources/research-data/data-guidelines | G6, G7 |
| 12 | Elsevier Publishing ethics (editors' & authors' duties) | elsevier.com/about/policies-and-standards/publishing-ethics | G10, G11, G13, G16 |
| 13 | Elsevier AI products insights | elsevier.com/insights/ai-products-from-elsevier | G15, G16 |
| 14 | Elsevier: 10 tips when unlocking AI for R&D | elsevier.com/connect/10-tips-when-unlocking-ai-for-r-and-d | G15 |
| 15 | Elsevier: innovations built on organized data | elsevier.com/connect/todays-innovations-are-built-on-organized-data | G6, G7 |
| 16 | Elsevier: database linking (data-base-linking) | elsevier.com/researcher/author/tools-and-resources/research-data/data-base-linking | G7 |
| 17 | NISO CRediT taxonomy | credit.niso.org | G13 |
| 18 | ISSN LTWA (journal title abbreviations) | portal.issn.org/ltwa | G5, G12 |
| 19 | Citation Style Language | citationstyles.org | G5, G12 |
| 20 | Mendeley Reference Manager | mendeley.com/reference-management/reference-manager/ | G5, G12 |
| 21 | Elsevier Share Link | elsevier.com/researcher/author/submit-your-paper/sharing-and-promoting-your-article/share-link | G14 |
| 22 | Elsevier: sharing & promoting your article | elsevier.com/researcher/author/submit-your-paper/sharing-and-promoting-your-article | G14 |
| 23 | Researcher Academy (writing skills hub) | researcheracademy.elsevier.com | G2, G9, G15 |
| 24 | Editorial Manager video: five pre-submission tips | elsevier.support/publishing/answer/video-guide-five-presubmission-tips-for-elsevier-authors-in-editorial-manager | G14, G16 |
| 25 | **ENB Guide for Authors** (most important) | sciencedirect.com/journal/energy-and-buildings/publish/guide-for-authors | all |
| 26 | ENB Insights (aims, recent topics) | sciencedirect.com/journal/energy-and-buildings/about/insights | G1, G4, G16 |
| 27 | ENB Call for papers / special issues | sciencedirect.com/journal/energy-and-buildings/about/call-for-papers | G1, G4, G16 |
| 28 | arena-skill repo (tournament method reference) | github.com/Jakeschincariol/arena-skill | G16, orchestrator |

## Verification license (read-only web permission, granted to every agent)
ALLOWED: fetch/search public pages to (a) verify a reference exists (CrossRef/DOI/publisher),
(b) check dataset versions & licences (EIA RECS 2020, NREL TMY3, ResStock 2025.1), (c) confirm
journal scope/special issues, (d) look up LTWA abbreviations, (e) re-read any policy wording
quoted in a finding, (f) check recent ENB papers for novelty positioning.
FORBIDDEN: uploading/pasting any part of the unpublished manuscript into online tools or GenAI
services (POL-AI-5), submitting or contacting anyone, writing to external services.
Every web-verified claim records `verified_via: [{"url": …, "accessed": "YYYY-MM-DD"}]`.

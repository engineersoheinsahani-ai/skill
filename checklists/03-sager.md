# 03 — SAGER (Sex and Gender Equity in Research) checklist, distille
Sources: EASE SAGER Checklist 2022 (PDF); Heidari et al. 2016, Res Integr Peer Rev 1:2
(springer table 1). Two tables: studies WITH human participants (T1) and OTHER studies
incl. applied sciences/engineering (T2). Rule ids SAGER-<item>.

## Table 1 — human participants (items)
- SAGER-1 Terms sex/gender used appropriately (defined, not conflated).
- SAGER-2 Title specifies sex/gender if only one included.
- SAGER-3a/3b Abstract specifies sex/gender if single; study population described with
  sex/gender breakdown.
- SAGER-4a/4b/4c Introduction cites prior sex/gender difference evidence where relevant;
  states whether sex/gender might be an important variant; outlines demographics.
- SAGER-5a/5b Methods: how sex/gender defined (self-report etc.); how considered in design,
  representation, exclusions justified.
- SAGER-6a..6g Results: full breakdown; disaggregated presentation; sex/gender-based analyses
  reported regardless of outcome; trials adverse events & PROs disaggregated; Table 1 rows
  per sex/gender category.
- SAGER-7a/7b Discussion: implications for generalisability across sexes/genders; if no
  analysis done, rationale + interpretation impact.

## Table 2 — other studies (applied sciences, engineering, technology)
- SAGER-2b/3b Title & abstract indicate if the model/application was based on, or intended
  for, one specific sex/gender.
- SAGER-5b Devices/technology: explain whether the product applies to / was tested with all
  genders in mind.
- SAGER-5c If relevant, how sex/gender was considered in design.
- SAGER-7b (analogue) If not considered, state rationale and generalisability limitation.

## Applicability mapping for THIS manuscript type (secondary household survey + ML model)
- Human-derived secondary microdata (RECS includes household demographics): T1 items apply
  partially via data description; T2 items apply to the model/technology side.
- Expected compliant handling: (a) state that sex/gender of household reference person was
  NOT used as a model feature and WHY (or analyse it); (b) discuss generalisability across
  household compositions in Limitations; (c) use gender-neutral language (POL-LANG-1).
- Finding template: severity `minor`, rule `SAGER-5b`/`SAGER-7b`, suggestion = one sentence
  in Data or Limitations, e.g. "Sex/gender of the household reference person was not used as
  a predictor; RECS-based household-level models therefore carry no gender-disaggregated
  validation, which we note as a generalisability limitation."

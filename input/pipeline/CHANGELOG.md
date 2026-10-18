# CHANGELOG

## v8.2 — Journal-grade figure suite

**Problem.** The v8.x figures (plain scatter, plain bars) were below the visual
standard of recent Energy & Buildings ML papers (SHAP beeswarms, jointplots,
reliability diagrams, dumbbell/lollipop stability plots are now the norm), and
the pipeline flowchart was hand-drawn with matplotlib instead of a graph tool.

**Fix.** New `tools/make_advanced_figures.py` regenerates the entire figure set:

- `fig1_pipeline` — flowchart rendered with **Graphviz `dot`** (python binding
  preferred, CLI fallback; `.gv` source written next to the PNG).
- `graphical_abstract` — four-panel abstract built from matplotlib patches only.
- `fig2_jointplot` — pred-vs-actual jointplot: marginal histograms, climate hue,
  multiplicative ±20% band, binned-median ±IQR residual inset; axes clipped to
  the 0.5–99.5 percentile for robustness.
- `fig3_shap` — two panels: SHAP beeswarm (top 10) + importance bars decomposed
  by feature source (RECS survey / TMY3 physics / teacher meta-feature);
  automatic importance-bars fallback when shap is unavailable.
- `fig4_calibration` — conformal reliability by predicted-magnitude decile with
  95% Wilson binomial CIs + coverage-by-interval-width deciles.
- `fig5_logo` — lollipop plot of LOGO climate regimes with held-out n.
- `fig6_seed_stability` — per-seed dumbbells (TL effect) + mean±SD repetition panel.
- `fig7_counterfactual` — diverging chart: routed model p10–p90 bands vs
  ResStock matched-cell and naive deltas; sign-flip annotation.

Style: Okabe–Ito colour-blind-safe palette, Arial/Helvetica, 300 dpi PNG + PDF.
`--smoke` self-tests fig2/3/4 code paths with synthetic inputs; `--copy-to`
copies results into the LaTeX folder. Requires Graphviz installed on the host
(`winget install graphviz` / `apt` / `brew`) — no substitute plotting library.

## v8.1 — Reviewer-response release

All items below are **code-level** fixes answering the peer review. The review's
writing/PDF-ligature/reference-formatting notes are out of scope for this release
by request; nothing in the code depends on them.

### A. Conformal prediction — the guarantee is now valid (#2, most serious)

**Problem.** The split-CV conformal quantile was calibrated on `X_val`, the same
validation split used for early stopping, Optuna hyper-parameter selection and
task routing. Those steps optimise validation error, so validation residuals are
systematically smaller than population residuals and the resulting interval is
too narrow. The reported 90.1 % coverage was an in-sample number and did not
support a 1−α claim.

**Fix.**
- `preprocessing.stratified_split` now returns **four** disjoint splits:
  `train` 70 % / `val` 10 % / `calib` 5 % / `test` 15 %.
- `EnergyConservingModel.fit` takes `X_calib` / `y_total_calib` and calibrates
  exclusively on that split. The mode is recorded
  (`calib-split` when n ≥ 50, otherwise `cross-conformal` OOF) and written into
  the manifest, the run summary and Table 2.
- Coverage is measured on the untouched test split and logged with its n.
- Pinned by tests: `test_calibration_split_is_never_used_for_selection` (q_hat
  must respond to the calibration sample), and
  `test_conformal_coverage_is_near_nominal_on_held_out_data`.

### B. Transfer-learning claim — honest effect size (#1)

**Problem.** "+0.8 pp average improvement" was not reproducible. On matched
protocols the effect is ≈ +0.3 pp for XGB and ≈ −0.3 pp for LGBM — i.e. no
measurable gain. The published ablation had also retrained the no-TL arm under
Optuna, so the two arms differed in more than the TL features.

**Fix.**
- New `src/seed_repeat.py` runs 10 seeds × 4 arms (`xgb/lgb × TL/noTL`) on the
  identical split and selection, reports paired 95 % CIs and a verdict from a
  fixed vocabulary (`consistent_gain` / `no_measurable_gain` / `within_noise`)
  against `EFFECT_THRESHOLD_PP = 0.10`.
- `EnergyConservingModel.fit(..., fixed_params=...)` bypasses Optuna so the
  ablation's no-TL arm reuses the primary arm's exact hyper-parameters; the
  paired comparison is now apples-to-apples.
- `evaluation.paired_difference` emits mean, 95 % t-CI, sign consistency and the
  verdict; `evaluation.summarise` emits mean ± sd and CI for the seed ensembles.
- Table 3 gains a `ci95` column so every headline number carries uncertainty.

### C. Leakage audit — real teeth (#6)

**Problem.** The audit ran three tests, all passing, which is only evidence that
the guard did not fire. No forbidden-pattern list was published, and the per
column |r| > 0.90 tripwire cannot see a set of individually weak columns whose
**sum** is the target — precisely the shape of RECS BTU components.

**Fix (`src/leakage_audit.py`, rewritten).**
- `LEAKAGE_PATTERNS` (config) is the published list and is echoed verbatim into
  the JSON so a reviewer can read the exact rules, not a prose summary.
- `run_audit` runs tests A–H: forbidden-pattern match (train and test
  separately), raw-vs-engineered name match, end-use columns present in the
  guard ledger, **train-only fit verified against `feature_engineer.medians`**,
  **test G: greedy-OLS R² of the target on candidate features must not exceed
  the reported score by more than 0.02**, and a removed-column ledger.
- Two documented limitations (E: engineered-from-target derivatives; F:
  permutation-importance probe) are declared in the JSON instead of implied
  covered.
- JSON is written next to the tables at submission time
  (`outputs/tables/leakage_audit_<stamp>.json`).
- Pinned by tests: `test_audit_publishes_the_forbidden_pattern_list`,
  `test_audit_linear_combination_test_catches_a_sum_decomposition`,
  `test_audit_detects_a_transformer_fitted_outside_train`,
  `test_audit_flags_a_forbidden_column`.

### D. Table consistency — one number per cell (#1, #4)

**Problem.** Tables 2 and 3 printed two numbers in one cell (e.g. "0.721 0.730")
because different runs were concatenated into the same cell. Table 4 had 0 of 6
rows, and Fig 3 disagreed with the SHAP table because they came from different
runs (0.160 vs 0.161, 0.0104 vs 0.089, different top-10 members). Feature count
was reported as both 250 and 252.

**Fix.**
- `src/results_manifest.py` (`RunManifest`) is the single writer. One run → one
  JSON plus one CSV per table; `add_row` appends rows, never concatenates.
- `shap_analysis.run_shap` computes mean |SHAP| **once** and emits the figure and
  the table from that single computation, returning the payload to the manifest.
- The 250 vs 252 discrepancy is explained in code and in output: 250 selected +
  2 transfer-learning meta-features appended later = 252, stated explicitly at
  both points.
- Coverage is reported consistently from the conformal calibration/reporting
  path only.

### E. ResStock counterfactual deltas — the −8.69 % artefact (#7)

**Problem.** Air-sealing showed −8.69 % (i.e. "air sealing increases energy
use"), and the counterfactual table had only 2 of 5 rows. Cause: the upgrade
files for selective measures cover only eligible households (air sealing: 63 %
of stock — the leaky homes, which consume the most), so a plain mean comparison
measures *which* households are in the file, not the measure's effect. Matching
on observed stock characteristics cannot fix it either: eligibility depends on a
variable the match keys do not carry, so every cell still mixes leaky and tight
homes.

**Fix (`src/decision_support.py`).**
- `matched_cell_delta` reports naive **and** matched estimates plus coverage, and
  warns on sign disagreement.
- New `shared_support_delta` uses the intervention's own driver, which *is*
  published in the upgrade file (infiltration for air sealing, roof insulation
  for attic work): it restricts the baseline to the driver values the upgrade
  file actually contains, then compares inside matched cells.
- `measure_resstock_deltas` reports all three (`reported_pct` prefers the
  diagnosis-corrected value for subset files, else the matched value) and logs a
  `[COMPOSITION BIAS]` warning when naive and corrected disagree in sign.
- `TransferLearner._cell_matched_pairs` resolves the renamed ResStock columns via
  `RS_MATCH_KEY_ALIASES`, bins floor area by 500 ft², and logs the failure reason
  when matching is not possible (v8.0 silently returned None, which is why 4 of
  6 rows were missing).
- `RS_CELL_MIN_CELLS` lowered 200 → 100: the shipped climate × type × fuel space
  has ~193 non-empty cells, so the old threshold was unreachable and every
  matched estimate silently fell back to the naive one.
- Verified against the generator's ground truth: air sealing
  naive −3.27 % → corrected **+1.45 %** (true +1.35 %).
- Pinned by `test_shared_support_estimator_recovers_the_true_effect`,
  `test_matched_cell_estimator_flags_subset_coverage`,
  `test_delta_pairing_resolves_renamed_resstock_columns`,
  `test_match_key_aliases_cover_the_renamed_columns`.

### F. LOGO transparency (#8)

**Problem.** It was unclear whether the per-fold pipeline was refit inside each
fold, and the n_test total (18,496) was not stated.

**Fix.** `climate_validation.leave_one_climate_out` rebuilds feature
engineering, feature selection and the model **inside** each fold, reports
per-fold `n_train` / `n_test` / `n_features_selected`, writes a
`PROTOCOL_NOTE` column on every row ("...REFIT FROM SCRATCH inside each fold...")
and logs `sum(n_test)` with an assertion that it equals the non-missing target
count. Mirrored in the manifest and Table 4.

### G. Figures — vector output (#11)

**Fix.** New `src/figure_style.py` (`apply_style`, `save_figure`,
`annotate_above_bars`, `PALETTE`). `save_figure` always writes **PDF + SVG +
PNG** with `bbox_inches="tight"`; `annotate_above_bars` replaces manual
offsets that overlapped. `eda.py`, `publication_outputs.py` and
`shap_analysis.py` now go through it. `publication_outputs.py` supplies five
figures: prediction, coverage curve (calibration → test), LOGO with the mean
line, counterfactuals (student/teacher/matched, n/a stubs where unavailable) and
an architecture schematic.

### H. ASHRAE G14.1 scope (#5)

**Fix.** Every output that framed the result as "meeting G14.1" now carries an
explicit scope note: G14.1 calibration criteria apply to *calibrated simulation
of a specific building against metered time-series*, not to cross-sectional
survey models, and are therefore not claimed here. The note is written into the
manifest (`ashrae_g14_note`) and the run summary rather than deleted, so the
reviewer sees the scope reasoning rather than a missing sentence.

### I. Bugs found and fixed while implementing the above

- `ensemble_models.HonestStacking`: the meta-learner was an unconstrained
  `RidgeCV` whose coefficients were clipped at 0 **after** fitting. The
  intercept had been solved for the unclipped coefficients, so `predict()`
  applied a biased intercept and the stacked score fell below every base learner
  (observed: base OOF 0.734 / 0.729 / 0.740 → stacked 0.582). Replaced with a
  `StandardScaler → Ridge(positive=True)` pipeline selected over alphas, with a
  `RidgeCV` fallback for older sklearn. Now reports coefficients, their sum and
  the stacked OOF next to the best base OOF.
  Pinned by `test_stacking_meta_learner_is_not_biased_by_coefficient_clipping`.
- `leakage_audit._greedy_ols_r2`: `Xv.loc[boolean_mask]` applied a column mask
  on the row axis, raising `IndexingError` on any real frame. Fixed to
  `Xv[keep]`.
- `decision_support.matched_cell_delta`: `groupby` on an energy series whose
  index did not align with the feature frame raised `IndexingError`; fixed by
  assigning `.to_numpy()`.
- `model_training` cross-conformal fallback: XGBoost rejects
  `early_stopping_rounds` without `eval_set`, so the fallback silently failed
  and `conformal_mode` came back as `none`. The parameter is now dropped for the
  fold models.
- `main.py`: `report.task_val_scores` did not exist on `TrainReport`; the value
  lives on the model.

### J. Test suite

`tests/test_protocol_fixes.py` — 20 tests, each pinning one reviewer finding to
executable behaviour. Together with the pre-existing
`tests/test_aux_data.py` (14 tests) the suite is **35 passing**.

### K. Low-memory production architecture (final full run, exit 0)

The 2 GB sandbox forced a redesign of the heavy steps; all behaviour is
documented in code comments and reproducible with `python src/main.py --n-seeds 10`:

- **LOGO moved to STEP 0** and runs in one fresh worker process per climate
  zone (`src/logo_worker.py`, `--zone`/`--list-zones`). Folds are independent,
  so per-zone processes give identical numbers to a single-process LOGO
  (verified: Cold 0.7047 / Hot 0.6367 / Mixed 0.7294 either way) while each
  process resets the allocator high-water between folds. Running LOGO at
  pipeline start keeps the resident parent (~300 MB at that point) far below
  the worker peak (~1.0–1.2 GB); running it at the end OOM-killed the worker
  against the ~1 GB parent (pymalloc arenas from the RECS object columns are
  not returnable by `malloc_trim`, so the parent never shrinks back).
- **Leakage audit moved to STEP 10a** (before Table 4 reporting) because it is
  the last consumer of the large training frames; they are freed right after.
- **Model + ensemble persist to `outputs/models/` before STEP 10** and the
  primary model is reloaded from disk for the counterfactuals; `df`,
  `resstock`, `ab_model`, `ensemble` and the split frames are freed between
  steps and resstock is reloaded in seconds for STEP 12.
- **`EnergyConservingModel.__init__` fails fast** with a clear `ImportError`
  when neither xgboost nor lightgbm is importable (a missing lightgbm used to
  surface as `NameError: LGBMRegressor` three layers into `fit()`).
- Per-fold feature frames inside LOGO are cast to float32 (LightGBM bins to
  32-bit internally, so accuracy is unchanged).

**Final production run (full RECS 18,496, 10 seeds): exit 0 in 1498 s.**

### L. Accuracy package (no new data, no leakage): Optuna + physics monotonicity

Goal: raise test R² without touching the honest protocol. Two levers, both
opt-in, both verified end-to-end on the full dataset (run `20260912_054522`,
exit 0, audit PASS):

- **`--optimize` (was already implemented, now exercised):** Optuna tunes the
  primary on train+val only (calib/test untouched). 45 trials, best val loss
  0.2299. Allocator trim after the study returns trial memory to the OS.
- **`--monotone` (new):** `PHYSICS_MONOTONE_SIGNS` (config.py) encodes 45
  domain-certain directions (+size/UA/degree-days/occupancy/loads, −efficiency
  /insulation). Applied ONLY to the aggregate log-total model and the stacking
  bases — end-use share/direct models stay unconstrained because per-end-use
  signs differ (e.g. HDD vs cooling share). Constraints are priors, not data-
  fitted, so they cannot leak. XGBoost gets the paren-string form (3.x API),
  LightGBM a list, CatBoost a list. The flag round-trips through save/load,
  the paired ablation inherits it (identical protocol), and 5 new tests pin
  the behaviour (40 total passing). LOGO and the multi-seed arms are
  deliberately left unconstrained/untuned so the published TL/stacking
  verdicts are untouched.
- **Memory hygiene for the tail stages:** ablation model + training targets
  freed right after the ablation; SHAP capped at 800 rows; model/ensemble
  persisted and all heavyweights freed immediately after SHAP (before FINAL
  RESULTS/audit). This removed the post-SHAP OOM kill seen on a 2 GB box.

**Measured (full RECS 18,496, sandbox synthetic TMY3/ResStock):**
| metric | baseline (v10) | + optimize + monotone (v13) |
|---|---|---|
| primary test R² (total) | 0.6397 | **0.6504** (+1.07 pp) |
| primary RMSE (kBtu) | 33,409 | 32,908 |
| derived EUI R² | 0.6541 | **0.6657** (+1.16 pp) |
| weighted R² | 0.6711 | 0.6756 |
| ensemble test R² | 0.6541 | 0.6542 (flat; OOF 0.7642) |
| conformal coverage 80/90/95 | 79.5/90.3/96.2 | 79.5/90.4/96.1 (nominal) |
| leakage audit | PASS | PASS |
A repeat run (v11, different Optuna cut) gave 0.6470 — the gain (+0.7…1.1 pp)
exceeds the seed-noise band (±0.4 pp) in both runs. Recommended on real data:
`python src/main.py --n-seeds 10 --optimize --monotone`.

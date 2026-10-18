# figure-spec.md — ENB artwork specifications + template index (v4-pro)

## Hard specs (machine-checked by engine/figureqc.py)
| property | requirement | rule id |
|---|---|---|
| resolution | photos/combination >= 300 dpi; line art >= 600-1000 dpi | ENB-FIG-2 |
| width | single column 1063 px · 1.5 column 1615 px · full page 2244 px (@300 dpi) | ENB-FIG-2 |
| fonts | >= 7 pt at FINAL print size; sans-serif (Arial/Helvetica); embedded in PDF/EPS | ENB-FIG-2 |
| colour | RGB preferred; colourblind-safe palette mandatory (Okabe-Ito shipped) | figureqc |
| formats | TIFF/EPS/PDF/PNG/JPG; vector PDF twin recommended for plots | ENB-FILE |
| citation | every figure cited in text, numbered consecutively | ENB-FIG-1 |
| graphical abstract | separate file, 531 x 1328 px, mandatory at submission | ENB-GA-1 |

## Template index (templates/figures/) — all runnable standalone with synthetic demo data
| template | technique | width class |
|---|---|---|
| `enb_style.py` | shared style: exact px widths, 7pt floor, Okabe-Ito palette | — |
| `t1_pipeline_flow.py` | graphviz layered clusters, audit-gate diamonds, artifact-labelled edges (polyline splines — ortho drops labels) | full |
| `t2_conformal_calibration.py` | coverage vs nominal + binomial bands + twin-axis widths + inset operating point | single |
| `t3_parity_residual.py` | log-log hexbin parity + regime violins, NMBE/CV(RMSE) annotation box | full |
| `t4_feature_stability.py` | importance lollipops with seed-CIs + unstable-rank flags (answers the SHAP-stability critique) | single |
| `t5_logo_small_multiples.py` | leave-one-regime-out facets, paired-seed CIs, full-refit reference | full |
| `t6_tornado_bounds.py` | assumption tornado + naive-vs-corrected violins (sign-flip story) | full |

## FIG-MPL / FIG-GV agent workflow (writer stage)
1. Read the council verdicts (`work/council-input.md`) + `work/figureqc-report.md`.
2. Pick the closest template; replace synthetic arrays with values READ from
   `input/results/` artifacts (law 10 — `[number needed]` otherwise; law 7 — never invent).
3. Emit `{"type":"figure-code","file":"figures/figX.py","code":"...","rationale":"..."}`
   JSONL lines to `work/writer-output.jsonl`.
4. Owner runs the code locally; then `python3 engine/run.py figureqc scan input/figures
   --emit-findings` must come back clean; fails loop back to the figure agent.

## Known pitfalls (do not rediscover)
- `bbox_inches="tight"` CHANGES the exact pixel width → `save_enb` never uses it.
- graphviz `splines="ortho"` silently drops edge labels → use `polyline`.
- Raster font size is NOT machine-verifiable → keep source (PDF/SVG/DOT) in
  `input/figures/` so the owner can confirm >= 7 pt.
- PNG without pHYs chunk = no embedded dpi → export with dpi metadata (matplotlib
  `savefig(dpi=300)` does this correctly).

# input/ — the owner's drop zone (contract)

Put the paper's ground truth here BEFORE running `engine/run.py prep`. Agents
READ this directory; they NEVER execute the research pipeline (law 10 — owner
decision 2026-10-12: pipeline re-runs are the owner's job, deposited once).

```
input/
├── manuscript.txt      raw manuscript text (plain-text export; the master copy)
├── figures/            designed artwork (PNG/TIFF/PDF/EPS + source: .py/.dot/.svg)
├── results/            FULL pipeline outputs — the artifact pool for law 10:
│   ├── run_manifest*.json      every number the pipeline published
│   ├── leakage_audit*.json     audit verdict (passed: true/false)
│   ├── tables/                 paper tables (csv/txt/md)
│   └── *.csv, *.log            metrics, OOF predictions, run logs
└── pipeline/           the code itself + run logs (READ-ONLY for agents:
                        static review only — splits, seeds, fit-scope, docs)
```

## Machine wave over input/ (no API key, minutes):
```bash
python3 engine/run.py prep --work work --input input
```
Produces: `work/map/manuscript-map.json` · `work/precheck/` ·
`work/figureqc-report.md` (+json) · `work/diffnum-report.md` (+json, traced %) ·
`work/inventory.json`. These deterministic facts are then injected into every
agent brief (MACHINE FACTS block) — agents judge, machines measure.

## Privacy
`input/` is NEVER packaged for distribution (see NOTICE.md). Manuscript text
reaches a model only via duty-relevant excerpts (campaign) or your explicit
`--attach` — your decision, POL-AI-5 applies to ONLINE models; local models
(Ollama) keep everything on your machine.

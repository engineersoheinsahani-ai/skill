# demo/ — real machine-wave outputs (regenerable, keyless)

Generated 2026-10-11 by the deterministic engine on the owner's manuscript (the
manuscript itself is NOT bundled — privacy + leanness). Reproduce with:

```bash
python3 engine/run.py map      <manuscript.txt> work/map
python3 engine/run.py precheck work/map/manuscript-map.json <manuscript.txt> work/precheck
python3 engine/run.py validate work <manuscript.txt>
```

| file | what it shows |
|---|---|
| `manuscript-map-meta.json` | 13 blocks; body 5,417 w; abstract **273 w** (cap 250 → ENB-ABS-1); keywords **9** (cap 7 → ENB-KW-1); highlights 5 bullets + **3 stray lines** (→ ENB-HL-1); refs **18** (org-author entry ABCB/DCCEEW counted after the audit-2.7 continuation-line fix); tables [1,2,4,5] (**Table 3 missing** → ENB-TBL-1); figures cited [1,2,3,4,6] (**Fig. 5 uncited** → ENB-FIG-1); `has_revision_notes: true` (→ LEFTOVER-001) |
| `precheck.json` / `precheck-report.md` | **14** rule-id'd findings (2 blockers, 5 major): LEFTOVER-001, ENB-GA-1, ENB-ABS-1, ENB-HL-1, ENB-KW-1, ENB-TBL-1, ENB-FIG-1, ENB-TP-1, POL-FUND-1, SAGER-5b, REF-1, REF-2, DAT-4, ENB-LINE-1 |
| `validation-report.md` | dual-schema validate **PASS** (v2 stores + v3 `findings.jsonl` incl. `L:rule-*` anchors) |

These findings enter `work/findings.jsonl` as `indep: machine`,
`anchor_type: rulebook`, `lit_quote_id: L:rule-<id>` — machine-verified against
`checklists/` + `engine/precheck.py` by `matrix3.py rule_exists` (audit 2.2
exemption: deterministic compliance is a fact, not an evaluative judgment).

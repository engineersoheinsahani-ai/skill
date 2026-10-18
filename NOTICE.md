# NOTICE — journal-arena ENB-Pro v4.0 (exclusive edition)

## Private material (never publish)
- `engine/humanize.py` is a PRIVATE derived module (PRIV-1…PRIV-6 of the parent
  project). This PRIVATE bundle may contain it for the owner's local use; the
  PUBLIC package must NOT: build it with `python3 engine/guard_private.py stage
  <src> <dst>` and verify `scan` prints `VERDICT: clean`.
- `input/` (manuscript, figures, results, pipeline) and `work/` (run state,
  findings, ledger with quotes) are the owner's research material — never
  include them in a PUBLIC build, never upload them to GitHub or online
  models. The owner's PRIVATE bundle MAY carry them (as of 2026-10-18 it
  ships `input/manuscript_final.txt` + `input/figures/` deposits) for
  local/clone-and-run convenience on the owner's own machines and sessions.
- `work/findings.jsonl` / matrix / council outputs may embed humanizer-derived
  metrics and manuscript quotes: owner-machine only.

## License status
No LICENSE file by design at this time (parent-project council finding E5-LIC,
P0, awaiting the owner's decision). Until then: all rights reserved; the
audited research code in `input/pipeline/` has its OWN license obligations —
check before any deposit (Option C).

## Environment variables (keys never in files)
| var | purpose |
|---|---|
| `ARENA_API_BASE` / `ARENA_API_KEY` / `ARENA_MODEL[_<GID>]` | executor endpoint (default Ollama local; key required for real runs — the engine refuses to fake independence) |
| `OPENALEX_MAILTO` | real email for keyless OpenAlex polite pool (corpus tools) |

## Execution-honesty labels (law 9)
`indep: machine` (deterministic tool — fact) · `harness` (separate model call,
stamped `<model>@<utc>#<slot>`) · `human` (owner/paste-back) · `single` (one
model wearing hats — informative only, never confirms a P0 alone).
Every finding row carries `executor` + `campaign` stamps; `campaign status`
shows exactly which slots were really executed.

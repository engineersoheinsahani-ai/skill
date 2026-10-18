# P0 Intake
Inputs: manuscript txt (any plain-text export). Run `engine/manuscript_map.py MS work/`.
Output: work/manuscript-map.json (blocks, word counts, highlights bullets+lengths, keywords,
abstract words, table/figure numbering & citations, reference heads, in-text citations).
Gate: map parses; if blocks missing (no ==== headers), normalise headings first and re-run.

# P2 Division review
`engine/orchestrate.py --mode division --agents N --work work --ms MS` (N=32 default, 100 max).
16 DUTY groups (title / abstract / kw-hl-GA / intro / literature / methods-coding / data /
results / stats-UQ / discussion-claims / recommendations+meta-audit / references /
ethics / formatting / language / reviewer-sim). Each agent: Phase A learning playbook
(SRC ids live) THEN Phase B findings; verification license per SKILL.md §3.
Run waves of 10 briefs in parallel (paste each work/briefs/*.md into any model; collect JSON to
work/findings/<aid>.json). Enforce: findings per templates/finding.schema.json; axis_link mandatory.
G12 outputs two reviewer reports + editor meta-review as findings with severity mapped.

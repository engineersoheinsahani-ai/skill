# P5–P6 Approve & apply
Author converts chosen matrix rows into work/revisions.json (templates/revisions.schema.json)
and sets approved:true ONLY for rows they accept. Then:
`engine/apply_revisions.py MS work/revisions.json work/` → ms_revN.txt + CHANGELOG.md +
point-by-point.md. `engine/validate.py work MS` must print PASS before anything is shipped.

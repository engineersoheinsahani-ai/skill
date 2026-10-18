# P4 Arena (contested revisions only)
When two agents propose conflicting rewrites of the same span, list their revision ids:
`engine/orchestrate.py --mode arena --contested revA revB --work work`.
Rounds: attack → defend+revise → 3 judges score with rubric in SKILL.md §2; median wins;
loser's best surviving ideas may be merged by the winner (judge may order it).

# 07 — Claims discipline & overclaim guard (CLM-*)
Purpose: no claim, suggestion or revision may be BIGGER than the evidence in the manuscript;
suggestions must never inflate the paper's contribution. Applies to (a) manuscript text,
(b) every agent's findings/suggestions, (c) revision drafts. G10/G11 enforce; all groups obey.

## Evidence ladder (rank every claim before judging it)
L1 measured: a number in a table/figure with run stamp. L2 bounded: CI/coverage/sign-consistency
stated. L3 interpreted: mechanism/plausibility reading. L4 speculative: "could/may/whether".
Rule CLM-1: a sentence may sit at most ONE rung above its strongest evidence; L4 wording must
keep hedge verbs; L1 wording ("shows", "demonstrates") only with L1 evidence.
Rule CLM-2: observational data ⇒ no causal verbs for retrofit effects ("reduces", "causes")
unless the matched-cell/teacher design is named in the same sentence.
Rule CLM-3: generalisation scope = RECS 2020 US households + TMY3 typical climate; any wider
claim ("all buildings", "global", "extreme events") is overclaim unless in Limitations as negation.
Rule CLM-4: sign vs magnitude: where the paper supports SIGN only (air sealing), magnitude
wording ("~2% savings") is overclaim; keep "direction reliable, magnitude uncertain".
Rule CLM-5: novelty superlatives ("first", "only", "record") require a verified literature scan
(verified_via) or removal; the paper's own "We offer no R2 record" stance is the axis.
Rule CLM-6: suggestions must not add claims: a fix may restate/qualify/shrink a claim, request
a clarification, or fix compliance — never promise new experiments/results the data cannot give.
Rule CLM-7: abstract/highlights/cover letter are claim-amplifiers: every bullet must trace to
an L1/L2 item in results; check them against tables before acceptance.

## How G11 audits OTHER agents' suggestions (meta-pass)
For each matrix row: extract implied claim of `suggestion`; rank on ladder; if implied claim >
evidence of the quoted span ⇒ mark `claim_inflation: true` and propose a shrunk wording;
rows with unchecked inflation are quarantined by review_matrix (field checked by validate.py).

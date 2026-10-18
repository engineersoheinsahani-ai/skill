# Task 14 — Mandatory training before judgment (per group)

Law: an executor may NOT judge a body region it has not studied. In ENB-Pro
the training happens INSIDE every campaign call (small-model contract):

1. **Duty card** (groups/16-group-playbooks.md) — the original v2 duty, verbatim,
   + the small-model focus list for that group.
2. **Section excerpt** — the group's mapped manuscript sections (<=6000 chars,
   from `work/map/manuscript-map.json`), so the model reads the actual text.
3. **Anchor pool** — <=20 short quotes with `L:` locators for that region.
4. **Machine digest** — precheck/diffnum/figureqc hits relevant to the group,
   so judgment starts from measured facts, not impressions.
5. **Few-shot JSONL** — one filled example row in the prompt; the model must
   copy the schema exactly (`/no_think`, temp 0.2-0.5, <=1200 tokens).

Group→section map (campaign.py `MAP_G2SEC`): G1 title page · G2 abstract ·
G3 keywords/highlights/GA · G4 introduction · G5 literature review ·
G6 methodology · G7 data · G8 results · G9 statistics/UQ · G10 discussion ·
G11 recommendations/conclusions · G12 references/declarations · G13 ethics/
policy declarations · G14 whole-manuscript formatting (figures dir too) ·
G15 whole body (language) · G16 abstract+introduction+conclusions (reviewer
simulation writes 2 reviewer reports + 1 editor meta).

Owner-side training (human, once per group, before the campaign):
read `task/06-judgment.md` + the group's checklist file + skim the excerpt.
For deposited corpus anchors (E2/E4/E6 in `work/ledger.jsonl`): study is
CLOSED (ceiling-20); executors may cite anchor takeaways via the anchor pool
but must mark corpus-derived claims `indep=machine` only when the anchor row
itself has a locator.

Verification: `campaign status` shows, per slot, the excerpt size and anchor
count actually sent — a slot that went out with an empty excerpt is invalid
(brief build failed) and must be re-run, never counted.

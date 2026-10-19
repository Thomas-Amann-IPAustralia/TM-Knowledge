# HANDOFF

**Last updated:** 2026-10-19 · S041 (end) · branch `claude/vibrant-hawking-9r6ev3`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0): a foundation, an examiner research tool, a customer
explanation aid. **The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`'s order: Package 1, then 3,
then 2, then 4.** S041 started from S040's branch (`claude/adoring-pascal-38ogq7`, fast-forwarded:
it held the response and the handoff) and **did Package 1**. No model was called; spend is still
US$9.63 against the US$9.49 cap, so every paid call is refused.

Package 1, each item shown done by re-running its probe from the response's "How to repeat the
checks" (scratch scripts; the tests named below hold the same properties):

- **R04.** The envelope shapes also target `tmk:Definition` and `tmk:Correction`; a Definition and a
  Correction shape. Deleting GD-0001's (or GK-0001's) author, reasoning and sources now gives 4
  defects each, where it gave 0. RULE-0001 records object `true`; `validate.inference_equality`
  checks every inference against its triple both ways: 0 of 192 disagree (5 did).
  `test_validate_gate.py`, `test_rules.py`.
- **R03.** Every evidence item is a `tmk:EvidenceAnchor`, `<record>/evidence/<n>` (ref, span, hash,
  quote, `checkedAgainst`, `isStale`; `docs/IDENTIFIERS.md` §2); the source graph closes over every
  store's evidence. 996 of 996 items round-trip from `graph/dataset.nq` (0 did); 0 refs dangle (13
  did). `test_ontology_build.py`.
- **R01.** GR-0699, GR-0700, GR-0701 → `qualifies` with their hedge (GR-0699 and GR-0700 on the
  section 43 ground; GR-0700 quotes the "However" and "more recently" sentences); GR-0702 kept as
  the one exception, re-anchored to the conditional sentence, phoneword scope as its condition.
  `hedge` is its own field (schema, harness, `tmk:hedge`, cards, both path-line engines); the five
  hedges moved. The dictionary's example is Part 29.6's "does not arise". ADR-0140. Ledger
  `data/derived/audit/review-response-2.yaml`. The three near misses: `test_predicates.py`.
- **R02.** Triage as harness notes (`definitions.triage`): 18 flags over 15 definitions; 5 remain,
  read and kept (GD-0002, GD-0007, GD-0081 state the test or duty that is their meaning; GD-0003,
  GD-0128 false positives). 17 definitions re-read (GD-0050, GD-0084, GD-0128, GD-0146 and 13
  more, 7 of them among the 45 signed-concept definitions, all read); GC-0179 takes regs 4.8 and
  4.10. `test_definitions.py`.
- **R07.** Condition state by rule (`ontology.conditions`); proceeding and mark type from the Part.
  All 101 open relationships assessed (`data/derived/audit/conditions-r07.yaml`): 64 conditions
  copied, 37 `no_condition` reasons. Now 88 stated, 212 none stated, 37 assessed none, 0 not
  assessed. `test_applies_when.py`.
- **Small.** `graph/README.md` (not empty; the shape claim; direct edges are navigation only),
  `eval/README.md` (agents author, in `authored/`), roles as capacities with the disjointness
  scoped, `ExaminationOutcome` represents a recorded outcome and never generates one.

Graph rebuilt, ontology report rebuilt. SHACL 0 defects, 0 gaps, 259 notes; harness 0 defects.
TESTS. Counts: 52 signed + 112 machine-written concepts; 35 signed relationships (20 serving, 15
corrected) + 337 machine-written; 37 corrections; 149 definitions; RULE-0002 187 conclusions.

## Next actions (agent work, no spend)

**Package 3: the live answer** (ADR-0139, ruling `2026-10-19-chat-approvals.yaml`, `applied: null`).
Package 1 has repaired the definitions it waits on, so it can start. In `bulk/jobs.py` and
`site/js/engine.js` together (`test_explorer.py` holds the prompts identical):
- **A06.** Replace the 1,600 cut (`explorer/build.py` `passage_chars`; `jobs._answer_render`;
  `engine.prompt`): legislation whole up to a budget, the matched units plus any unit a "Subject to
  subsections ..." lead-in names for the largest; Manual chunks cut around the match
  (`passage_block`'s `around`); every cut marked in the prompt and on the page. Fixture: a section
  44 question sees (3) and (4).
- **A08.** A new answer version (`ANSWER_VERSION`; `test_search.py` pins `answer-v3`): claims, each
  with its quotes; `Engine.verify` against the excerpt sent, not `this.text(ref)`; `ask.js` marks an
  unsupported claim, shows "no checked support" for an answer with none, streams as an unchecked
  draft; the page says the check proves a quote exists, not that it supports.
- **Definitions** in the prompt, each with basis and stamp. Label the 129 prepared answers
  (`answer-v2`) as written from cut passages. Fill the ruling's `applied`; mark ADR-0139 acted on.

**Package 2: what examiners use.** R05 dependency index keyed by any ref (reuse the staleness check),
feeding `explorer.build.stability`; RULE-0002 left as is, labelled signed-only. R06 each competency
query tested against its signed record; CQ-0009, CQ-0024 rewritten. R08, R10, A07, A11.

**Package 4: the first customer slice, fictional** (tests for ss 41, 43, 44; regs 4.8–4.10 process;
matter, objection, role assignment, built on roles-as-capacities; evidence for s 41(3), (4)).

**Afterwards:** the blend (S034, F10); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **Nothing new is waiting on you from S041.** Gates ahead, asked when reached: anything published to
  customers; real customer or case data; spend; who writes the next benchmark.
- **Revoke the old OpenAI key** and delete the unread `OPENAI_API_KEY` secret (S038).
- Still waiting from S034: the page's blend; ADR-0131; the four disputed signed readings.

## What to distrust

- **R07's 101 assessments and R02's 17 re-reads are one agent session's reading**, unreviewed. A
  `no_condition` reason is a judgement; so is choosing one contiguous span as a condition where the
  sentence has two (GR-0148, GR-0309 carry their consequent with them).
- **The proceeding lookup is coarse**: Parts 52, 54, 55, 7, 9, 15 cover several proceedings and fix
  none; a statutory source fixes none.
- **Live answers about long provisions still read only their first 1,600 characters** (A06) until
  Package 3; a kept citation proves a quote exists, not that it supports (A08).
- **A clean authority flag is not a verified attribution** (R08).
- **GC-0179 keeps "The report must include the lapsing date."** among its evidence (the old reading's
  quote, still true of the Manual); its definition now takes the deferral from reg 4.10(3).
- **`docs/PITCH-PACK.md` is stale**; **21 legislative bases are unverified**; **GK-0037** is the
  agent's (CHAT-0082); **GR-0672, GK-0003** carry hand-copied hashes; `site/data/ontology.json`
  carries the reviewer's initials (S028).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); about fifteen minutes for the full suite.
- **After changing records, the builder or any `ontology/draft/` module**: `tmk-graph --write
  --rules`, then `tmk-ontology-report --write`. CI checks both. `--check` needs `--rules`.
- **Four structure ledgers now** (`restructure.yaml`, `review-response.yaml`,
  `review-response-2.yaml`, `conditions-r07.yaml`): dry-run all four after touching
  `bulk/restructure.py`; each must report 0 to re-read and 0 refused (Q-93, Q-98). Re-running a
  ledger's `--write` regenerates its report from nothing left to do: apply a ledger in one pass.
- **A condition or hedge must be verbatim in the sentence**; a sentence with a conditional word gets
  a condition or a `no_condition` reason, and the harness counts the states.
- **Read evidence through `tmk:evidence`** (anchors), not `tmk:sourcePassage` (the passage only).
- **Probing SHACL**: `validate.run` on the loaded `Dataset`, never a flat graph (Q-97).
- **Engines change together**: `engine.js`/`search/index.py`, `jobs.passage_block`/the
  `engine.prompt` cut, `jobs.path_line`/`engine.pathLine` (now eight fields, the hedge last),
  `search.authority`/`authorityFlags`, `links.find_mentions`/`Recogniser`,
  `jobs.reading_input`/`live.readingInput`.
- **Definitions and corrections have their own readers**; pass `authored.root` to
  `corrections.load` (Q-77). **`served_gold()` serves; `goldset.load()` measures.**
- **The explorer needs the snapshot**: `tmk-explorer --write`, test the page, restore a stand-in
  `live.json` (Q-90). `PREPARED_LAW` is the law the 129 prepared answers read.
- **Moving the pin**: Q-95. **Measuring**: Q-91, Q-85, Q-83.

## Open items (agent-proposed, provisional)

- **ADR-0140** (exceptions only where the source excludes; the hedge field), S041.
- S041's engineering: evidence-anchor IRIs and `checkedAgainst`; `assertionObject` as `rdf:Property`;
  the span and hash properties losing their domain; the triage's three rules and thresholds; the
  condition-state rule and the Part lookup tables; the applier's three fixes (Q-98).
- ADR-0138's agent parts and S040's verdicts in the response.
- Earlier, unchanged (listed in full in `git show 8d4c6ef:docs/HANDOFF.md`): ADR-0137, ADR-0134,
  ADR-0135 (but for ADR-0140's supersession), Q-96, the agent parts of ADR-0113 to ADR-0133;
  S036 and S038's engineering; "too general" labels (E1).

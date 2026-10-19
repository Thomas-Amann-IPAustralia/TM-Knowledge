# HANDOFF

**Last updated:** 2026-10-19 · S040 (end) · branch `claude/adoring-pascal-38ogq7`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose changed (ADR-0138).** In the owner's words, the ontology is "a foundational layer for
any future machine learning, machine decision making, customer service delivery or policy writing
aid"; immediately, an examiner research and decision-support tool, and a customer explanation aid
(requirements, the application process, objections; likely a chatbot with visuals). `CLAUDE.md` §0
has it verbatim, with D4 now the customer aid. **The pitch pack is stale: spend no tokens on it.**

**The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`**, S040's check of ChatGPT's consolidated review
(`docs/Trade-Mark-Ontology-Consolidated-Review.md`), re-judged against that purpose: all 22 findings
stand; 17 fixes agreed, 5 in part. Its "Recommended order of work" is the backlog below.

**Two owner approvals wait to be built (ADR-0139, ruling `2026-10-19-chat-approvals.yaml`,
`applied: null`):** CHAT-0087, the live chatbot gets complete provisions with marked cuts and
claim-level quote checking against what it was sent; CHAT-0088, it gets the definitions once
Package 1 has re-read the flagged ones. Fill the ruling's `applied` when done.

S040 changed documents only: no record, graph, query, shape, prompt or page. Spend is US$9.63 against
the US$9.49 cap, so every paid call is refused. 783 tests pass; `tmk-graph --rules --check` matches;
SHACL 0 defects, 259 notes; harness 0 defects, 12 gaps, 15 notes. Counts: 52 signed + 112
machine-written concepts (one connected piece); 35 signed relationships (20 serving, 15 corrected) +
337 machine-written; 37 corrections; 149 definitions.

## Start here

1. `pip install -e ".[rdf,test]"`, then `tmk-fetch-upstream` (the snapshot is not committed).
2. Read the response's R01 to R07, A06, A08 and "Recommended order of work". Its "How to repeat
   the checks" lists every probe, so each "done" can be shown by re-running the probe.
3. Work in order: **Package 1, then Package 3, then Package 2, then Package 4.** Package 3 waits on
   Package 1 because the definitions it puts in the prompt are the ones Package 1 repairs.

## Next actions (agent work, no spend)

**Package 1: repair the foundation** (one session; then `tmk-graph --write --rules` and
`tmk-ontology-report --write`).
- **R04.** Add `tmk:Definition` and `tmk:Correction` as further `sh:targetClass` on
  `AuthoredAssertionShape` and `AuthoredEvidenceShape` (`shapes/provenance.ttl` lines 152, 224); a
  Definition shape (`defines`, text, basis). RULE-0001's `tmk:assertionObject ?chunk`
  (`queries/rules/RULE-0001-mixed-authority.rq` line 17) becomes `true`. Add an equality check
  (each reified inference matches its emitted triple, both ways). Test through `validate.run` on a
  `Dataset`, with negative fixtures (Q-97).
- **R03.** In `ontology/build.py`, `_origin` (line 705) writes only `tmk:sourcePassage` per
  evidence item; spans and hashes come only from `_provenance` for a relationship's `source_ref`.
  Add one evidence-anchor node per item (ref, span, hash, quote, version) for every store; record
  the IRI pattern in `docs/IDENTIFIERS.md`; keep `sourcePassage` as the shortcut. Close the source
  graph over every store's evidence refs (`record_provisions`, line 1423, reads relationships only;
  GD-0060, GD-0112, GD-0138 dangle). A round-trip test: all 634 items reconstructable.
- **R01.** Re-read GR-0699 to GR-0702 (`authored/relationships.yaml` from line 12809) in a
  restructure ledger: three to `qualifies` (GR-0700 also quoting the "However" sentence), GR-0702
  re-anchored to the conditional sentence with phoneword scope. Split `applies_when` into condition
  and `hedge` (schema, builder, cards, `path_line`/`pathLine`); move the five hedges (GR-0565,
  GR-0574, GR-0608, GR-0699, GR-0700). Replace `isAnExceptionTo`'s example (`predicates.py` line
  188) with Part 29.6's "a section 43 ground for rejection does not arise". An agent-proposed ADR
  superseding ADR-0135's reading of the three.
- **R02.** Three triage checks as harness notes (a: statutory evidence citing some child units, not
  all; b: Manual evidence followed by a qualifier; c: non-ground definitions stating "must" or
  "rejected"). Re-read what they flag plus GD-0050, GD-0084, GD-0128, GD-0146, GC-0179's notes and
  basis, and the 45 definitions of signed concepts.
- **R07.** Condition state set by rule: no conditional marker gives `none_stated`, a marker and no
  condition `not_assessed`; then assess the ~103 flagged. Proceeding and mark type from the Part.
- **Small.** `graph/README.md` line 69 ("It is empty today") and the shape claim; `eval/README.md`
  line 40; role comments as capacities and the disjointness (`examination.ttl` line 210);
  `ExaminationOutcome`'s comment (line 45): represent a recorded outcome, never generate one.

**Package 3: the live answer** (ADR-0139; one session). In `bulk/jobs.py` and `site/js/engine.js`
together (`test_explorer.py::test_the_live_prompt_is_the_measured_one` holds them identical):
- **A06.** Replace the 1,600 cut (`explorer/build.py` line 729 `passage_chars`; `jobs.py` lines
  1117, 1122; `engine.js` line 260): legislation whole up to a budget, the matched units plus any
  unit a "Subject to subsections ..." lead-in names for the ten largest; Manual chunks cut around
  the match (`passage_block`'s `around`); every cut marked in the prompt and on the page. Fixture:
  a section 44 question sees (3) and (4).
- **A08.** A new answer version (`ANSWER_VERSION`, line 1145; `test_search.py` pins `answer-v3`):
  `_ANSWER_SCHEMA` (line 1166) becomes claims, each with its quotes; `Engine.verify` (line 280)
  checks against the excerpt sent, not `this.text(ref)`; `ask.js` (around line 221) marks an
  unsupported claim, shows "no checked support" for an answer with none, and streams as an
  unchecked draft. Say on the page that the check proves a quote exists, not that it supports.
- **Definitions** in the prompt, each with basis and stamp. Label the 129 prepared answers
  (`answer-v2`) as written from cut passages. Fill the ruling's `applied`.

**Package 2: what examiners use.** R05 dependency index keyed by any ref, feeding
`explorer.build.stability` (line 482), RULE-0002 untouched and labelled signed-only; R06 each
competency query tested against its own signed record in `eval/gold/competency-questions.yaml`,
CQ-0009 and CQ-0024 rewritten; R08 limits, tests of its misses, two tightenings; R10 coverage table
by Part and the Manual's capture date (3 August 2026) beside the compilation; A07 exact-reference
lookup and provision search, a source register, customer pages raised with upstream; A11
`build.json`.

**Package 4: the first customer slice, fictional.** Test records for ss 41, 43, 44 (within
ADR-0009's decision tables); the regs 4.8 to 4.10 process template; matter, objection and
role-assignment schema; s 41(3) and (4) evidence requirements; the explanation object and three
views on a page apart from the explorer, unpublished. Schema design may start during Package 1.

**Afterwards:** the blend (S034, F10: hub concepts in expansion, ties by ref order, both engines,
never tuned on the benchmark); the 15 undefined concepts; heading-only edges (GR-0270 at least).

## For the owner

- **Gates ahead**, asked when reached: anything published to customers or tested with them; real
  customer or case data; spend for a support check or re-measurement; who writes the next benchmark.
- **Revoke the old OpenAI key** and delete the unread `OPENAI_API_KEY` secret (S038).
- Still waiting from S034: the page's blend; ADR-0131; the four disputed signed readings.

## What to distrust

- **"SHACL passed" does not cover definitions or corrections** (Q-97); the RDF holds span and hash
  for relationships only.
- **Live answers about long provisions read only their first 1,600 characters** (A06), so section
  44's exceptions are unseen. A kept citation proves a quote exists, not that it supports (A08).
- **A clean authority flag is not a verified attribution** (R08); two more misses are in the response.
- **All 149 definitions are one agent session's reading**; at least four omit a qualification.
- **Three of the four `isAnExceptionTo` edges** state likelihood, not exclusion (R01).
- **`docs/PITCH-PACK.md` is stale**; the measurements in it are from 9 and 12 October.
- **GK-0037's choice** is the agent's (CHAT-0082); **GR-0672 and GK-0003** carry hand-copied hashes.
- **21 legislative bases are unverified** (the harness; older handoffs said 22).
- **`site/data/ontology.json` still carries the reviewer's initials** (S028).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); about fourteen minutes for the full suite.
- **After changing records, the builder or any `ontology/draft/` module**: `tmk-graph --write
  --rules`, then `tmk-ontology-report --write`. CI checks both. `--check` needs `--rules`.
- **Probing SHACL**: `validate.run` on the loaded `Dataset`, never a flat graph (Q-97).
- **Definitions and corrections have their own readers**; pass `authored.root` to
  `corrections.load` (Q-77). **`served_gold()` serves; `goldset.load()` measures.**
- **Engines change together**: `engine.js`/`search/index.py`, `jobs.passage_block`/the
  `engine.prompt` cut, `jobs.path_line`/`engine.pathLine`, `search.authority`/`authorityFlags`,
  `links.find_mentions`/`Recogniser`, `jobs.reading_input`/`live.readingInput`.
- **Two structure ledgers**: dry-run both after touching `restructure` (Q-93); a condition must be
  verbatim in the sentence; renaming is how a site label changes (Q-94). Edit record files block by
  block (Q-76); off-kind edge, check the kinds first (Q-86).
- **The explorer needs the snapshot**: `tmk-explorer --write`, test the page, restore a stand-in
  `live.json` (Q-90). `PREPARED_LAW` is the law the 129 prepared answers read.
- **Moving the pin**: Q-95. **Measuring**: `measure-<date>.md` when grades move (Q-91); price from
  completed calls (Q-85); Gemini ignores its schema (Q-83).

## Open items (agent-proposed, provisional)

- ADR-0138's agent parts (D4's done-test, the real-data gate, the order of work, tests as data
  within ADR-0009) and S040's verdicts in the response.
- Earlier, unchanged and listed in full in the previous handoff (`git show 8d4c6ef:docs/HANDOFF.md`):
  ADR-0137, ADR-0134, ADR-0135, Q-96, and the agent parts of ADR-0113 to ADR-0133; S036 and S038's
  engineering; the first response's recommendations not yet done; "too general" labels (E1).

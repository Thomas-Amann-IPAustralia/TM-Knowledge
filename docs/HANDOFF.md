# HANDOFF

**Last updated:** 2026-10-19 · S042 (end) · branch `ccr-c4fac9a6-uq5d6d`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`'s
order: Package 1 and 3 done (S041), Package 2 done here (S042) but for two items, Package 4 next.**

**The owner gave up to US$4 more** (*"Please complete the next phase of work. You can spend UP to
$4"*, CHAT-0089, ADR-0141): the cap is **US$13.63** (`config.SPEND_CAP_USD`). **S042 spent none of
it.** The first paid call (rebuilding the passage vectors, about two cents, which the answer job's
dry-run needs) was refused by this session's permission layer, not by the cap, and was not routed
around (Q-99). Recorded spend stays US$9.63.

Package 2, item by item:

- **R05, the dependency index.** `ontology/dependencies.py`: every store and record type (signed,
  authored, definitions, corrections), keyed by any ref (Part, page, chunk, provision, unit), with
  record, type, store, review status, field, hash and staleness (the harness's resolver); a current
  view (`served_gold()`) and an as-signed one, never summed; `via_manual` reaches records through
  the Manual passages citing a provision, upstream's `extraction`/`certainty` kept, ambiguous ones
  listed, never resolved. 2,355 dependencies of 963 records on 556 refs; 0 stale; 19 history-only.
  s 44 reaches 19 records directly and 89 through 34 passages. Feeds `explorer.build.stability`
  (pages now list definitions and corrections; every relationship's evidence, not its one `ref`;
  `provisions` and `held`), the change view's new "start from the Act or the Regulations" panel,
  and the ontology report's §7. RULE-0002 unchanged, labelled the signed-only view
  (`queries/rules/README.md`, which also no longer says neither rule is approved).
  `test_dependencies.py`, two tests in `test_explorer.py`.
- **R06, competency queries.** `ask.contracts`: each query checked against its own signed record
  (required sources, expected concepts, answer-shape columns). The report's §3 says "queries
  implemented: 13; contracts met: 1" with every unmet item named: a gap, not a test failure.
  CQ-0009 rewritten (both graphs, `standing` column, every relationship from 29.9; reaches its
  required passage through GR-0103, still misses "average consumer"); CQ-0024 rewritten (one row
  per relationship, `standing` and `authority`: practice for the Manual, law for the legislation;
  contract met). `test_competency_queries.py`.
- **R08, the authority detector.** Both exemptions (the Manual named, a negation) read only the
  match's own clause; every match in a sentence is read, not the first. Known misses are four strict
  xfail tests, and the docstring says what a clean result means. The Ask page's lede no longer says
  "kept apart"; its stamp says the warning can miss; the report's §6 says the same.
  `test_authority_check.py`, both engines.
- **R10.** The coverage table by Part is the report's §7 (Parts 1, 4, 8, 41, 61 not in the graph;
  7 and 45 with no relationship, as the review found). Every answer's footer now names the Manual's
  capture date beside the compilations, and a live one says the Manual predates compilation 48
  (`explorer.build.manual`, `ask.js` `lawLine`).
- **A07.** Exact-reference lookup (`search/citations.py` = `engine.namedProvisions`): "section
  44(3)", "s 41(4)", "reg 4.10" put the named provision first in the answer's legislation, at the
  provision level. One helper, `jobs.legislation_refs`, now serves `cli._measurement_items`, the
  parity test and (mirrored) `Engine.prepare`. `docs/SOURCE-REGISTER.md`: tasks against sources,
  held or not; the customer pages to raise upstream first. `test_citations.py`.
- **A11.** `graph/manifest.json` (`build.manifest`, written by `tmk-graph --write`, drift-checked):
  pin, compilations, profile, schema ids, per graph its triples, classes and review states. The
  site's `build.json` adds the date, the git revision, the Manual capture, the answer versions and
  the dependency counts.

Graph rebuilt (`--rules`; only `manifest.json` new, the `.ttl` files unchanged), ontology report
rebuilt. Headless check: the change view's provision panel and a prepared answer's footer render,
no console errors. Test count: see the commit that records it.

## Next actions

**First, if the owner allows the paid calls** (US$4 approved, ADR-0141): `tmk-bulk embed --confirm`,
then `tmk-bulk run answer --dry-run`, a smoke run with `--limit 3 --confirm`, read it, then the 129
if the estimate fits. Re-writing the prepared answers moves `PREPARED_ANSWER_VERSION`,
`PREPARED_LAW` (to compilation 48), `PREPARED_MANUAL_CAPTURED` and the footer together, and
`explorer.build.examples` must pass `claims` so the page shows them (it renders prepared answers as
prose today).

**Package 2's two remainders:** keyword search over the 763 provisions beside the Manual (A07; a
second BM25 index in both engines with its own parity test, shown apart, not in the prompt); and
the 21 unverified legislative bases (R10: re-cite each from a quoted passage, or mark it
unresolved; the harness note lists them).

**Package 4: the first customer slice, fictional** (tests for ss 41, 43, 44; regs 4.8–4.10
process; matter, objection, role assignment on roles-as-capacities; evidence for s 41(3), (4)).
CQ-0009 is A04's natural first customer: a structured s 43 geographical test would meet its
contract.

**Afterwards:** the blend (S034, F10); the 15 undefined concepts; heading-only edges (GR-0270);
the dependency index into the graph as a candidate rule (R05, Package 5).

## For the owner

- **The US$4 is unspent.** This session's permission layer refused the first paid call as a
  real-world transaction. To use it, allow `tmk-bulk` paid calls in the session's permissions (or
  run `tmk-bulk embed --confirm` yourself) and say so; nothing else is waiting.
- Gates ahead, asked when reached: anything published to customers; real customer or case data;
  re-measurement and who writes the next benchmark.
- **Revoke the old OpenAI key** and delete the unread `OPENAI_API_KEY` secret (S038).
- Still waiting from S034: the page's blend; ADR-0131; the four disputed signed readings.

## What to distrust

- **The dependency index sees only what a record names** (Q-28): "no recorded dependency" is all
  an empty answer means. Its generic ref walk counts every ref-shaped string in a record, so a
  signed question's `expected_sources` count as dependencies (intended: they would need re-reading).
- **A contract "met" is a property of the rows, not of a correct answer**: required sources
  reached, concept labels present, columns present. CQ-0024 "met" does not mean the modalities are
  right.
- **The clause rule is a heuristic too**: "and" without a comma does not start a clause, so "The
  Manual says X and section 41 requires Y" is exempt.
- **Exact-reference lookup reads the first number after the word**: "sections 41 and 43" finds 41
  only; a bare "44(3)" finds nothing, on purpose.
- From S041, unchanged: R07's 101 assessments and R02's 17 re-reads are one session's reading;
  the proceeding lookup is coarse; **`answer-v4` has never run against the real model**; the live
  answer is not the measured one; the block rule fills spare budget with unmatched blocks; GC-0179
  keeps an old quote; `docs/PITCH-PACK.md` is stale; GK-0037 is the agent's; GR-0672, GK-0003 carry
  hand-copied hashes; `site/data/ontology.json` carries the reviewer's initials (S028).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); about fifteen minutes for the full suite.
- **A paid call may be refused by the session, not the cap** (Q-99); the answer job needs the
  vectors rebuilt first.
- **After changing records, the builder or any `ontology/draft/` module**: `tmk-graph --write
  --rules`, then `tmk-ontology-report --write`. CI checks both, `graph/manifest.json` included.
- **Build the dependency index once** (about five seconds) and pass it.
- **Four structure ledgers** (`restructure.yaml`, `review-response.yaml`, `review-response-2.yaml`,
  `conditions-r07.yaml`): dry-run all four after touching `bulk/restructure.py` (Q-93, Q-98).
- **Engines change together**: `engine.js`/`search/index.py`, `jobs.excerpt`/`engine.excerpt`,
  `jobs.check_claims`/`Engine.verify`, `jobs.definition_lines`, `jobs.path_line`/`engine.pathLine`,
  `search.authority`/`authorityFlags` (now clause-scoped), `search.citations`/`namedProvisions`,
  `jobs.legislation_refs`/`Engine.prepare`, `links.find_mentions`/`Recogniser`,
  `jobs.reading_input`/`live.readingInput`.
- **A condition or hedge must be verbatim in the sentence**; **read evidence through
  `tmk:evidence`**; **probe SHACL on the loaded `Dataset`** (Q-97).
- **Definitions and corrections have their own readers**; pass `authored.root` to
  `corrections.load` (Q-77). **`served_gold()` serves; `goldset.load()` measures.**
- **The explorer needs the snapshot**: `tmk-explorer --write`, test the page, restore a stand-in
  `live.json` (Q-90). A local server must serve `.mjs` as JavaScript or the vendored libraries fail.
- **Moving the pin**: Q-95. **Measuring**: Q-91, Q-85, Q-83.

## Open items (agent-proposed, provisional)

- **ADR-0141's agent part** (what the US$4 is for: the first real `answer-v4` run and the prepared
  answers' re-write).
- S042's engineering: the dependency index's two views and ref walk; the clause-break pattern; the
  citation pattern and provision-level resolution; the contract's three checks and `SHAPE_COLUMNS`;
  CQ-0009 selecting by section 29.9 rather than by label; the manifest's fields;
  `docs/SOURCE-REGISTER.md`'s rows.
- From S041: ADR-0140; Package 3's budgets, block rule, lead-in pattern and claim schema; the
  evidence-anchor IRIs; the triage rules; the condition-state rule and Part lookups; the applier's
  three fixes (Q-98). ADR-0138's agent parts.
- Earlier, unchanged (listed in full in `git show 8d4c6ef:docs/HANDOFF.md`): ADR-0137, ADR-0134,
  ADR-0135 (but for ADR-0140's supersession), Q-96, the agent parts of ADR-0113 to ADR-0133.

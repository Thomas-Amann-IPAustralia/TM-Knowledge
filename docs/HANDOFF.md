# HANDOFF

**Last updated:** 2026-10-19 · S042 (end, second portion) · branch `ccr-c4fac9a6-uq5d6d`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`'s
order: Packages 1 and 3 done (S041); Package 2 done (S042); Package 4, the first customer slice,
started (S042).** The owner asked for "the next phase of work", then "the next portion".

**Spend.** The owner gave up to US$4 (CHAT-0089, ADR-0141); the cap is **US$13.63**. **None spent.**
The first paid call (the vector rebuild the answer job needs) was refused by the session's
permission layer, not the cap, and was not routed around (Q-99). Recorded spend stays US$9.63.

**Package 2, complete.** R05 the dependency index (`ontology/dependencies.py`; change view, report
§7); R06 query contracts (`ask.contracts`; CQ-0009 and CQ-0024 rewritten); R08 clause-scoped
authority check with strict-xfail known misses; R10 coverage by Part, the Manual's capture date on
every answer, and **the 21 unverified legislative bases re-read** (ledger
`data/derived/audit/bases-r10.yaml`: 11 quoted, 4 re-cited, 5 withdrawn; the harness note is down
to 1, GC-0012's s 27(3)(b), signed, which only an owner-ruled correction can change); A07
exact-reference lookup and **keyword search over the 763 provisions** (`search.index.ProvisionIndex`
= `Engine.provisionSearch`, parity on all 129 questions, shown on the Ask page in its own card, not
in the prompt); A11 `graph/manifest.json` and the site's `build.json`; `docs/SOURCE-REGISTER.md`.
The restructure applier now keeps a concept's chain of readings, as it does a relationship's.

**Package 4, the slice so far (ADR-0142, agent-proposed).**
- **`GL-` structured legal tests** (`authored/legal-tests.yaml`): GL-0001 s 44 (an all/any tree;
  (3) a discretion, (4) a bar; deferment and evidence routes), GL-0002 s 43 (two evaluative
  conditions; the Manual's geographical route, scoped), GL-0003 s 41 ((3) OR (4); the Manual's
  Part 23 evidence requirements split into relevance and sufficiency). 48 quotes, each in the
  envelope, each checked by the harness.
- **`GP-0001` process template** (`authored/processes.yaml`): regs 4.8–4.14, ss 33, 37 — 8 steps, 12
  transitions (with what a matter must say, and the grounds a branch exists for), 4 time rules.
- **Reader** `authored/procedure.py`; schemas `legal-test`, `process`, `fictional-matter`;
  harness counts and checks both; `next_number` allocates GL/GP.
- **Fictional matters** `scenarios/matters.yaml` (FM-0001 to FM-0004, one per acceptance example:
  A01 two objections over overlapping goods; A02 report–response–deferment; A04 an unknown date and
  a discretion; A05 + A03 exhibits and an unknown filing date). The schema allows only
  `fictional: true`.
- **`tm_knowledge.explain`**: one explanation object (three-valued; evaluative conditions only as a
  named person recorded them; a "may" stays a "may"; questions only where the answer changes the
  reading; stated dates compared, never calculated; law and practice labelled), `render_text`, and
  `page.py`'s three views with text equivalents. `tmk-explain [--matter] [--html PATH]` writes the
  page to a file; it is **not deployed and not for customers**.
  `tests/unit/test_explain.py` (31 tests) holds every acceptance example and rule.

- **In the graph**: each GL/GP record is a `tmk:StructuredTest` or `tmk:ProcessTemplate` (records,
  apart from the `tmk:LegalTest` concept kind) in the authored graph with its envelope and an anchor
  per quote; a test `tmk:readsProvision` its provision. The envelope shapes target both, and
  `tmk:ProcedureRecordShape`/`tmk:StructuredTestShape` require a title, anchors and one provision.
  The condition tree and the steps are not yet in the graph.

Graph rebuilt, ontology report rebuilt, SHACL 0 defects, harness 0 defects. Full-suite count: the
commit that records it.

## Next actions

1. **Paid run, if the owner allows it** (US$4 approved): `tmk-bulk embed --confirm`, `tmk-bulk run
   answer --dry-run`, a `--limit 3 --confirm` smoke run read by hand, then the 129 if it fits.
   Re-writing the prepared answers moves `PREPARED_ANSWER_VERSION`, `PREPARED_LAW`,
   `PREPARED_MANUAL_CAPTURED` and the footer together, and `explorer.build.examples` must pass
   `claims`.
2. **Package 4, continued.** The condition tree, exceptions, steps and transitions into the graph
   (the records and envelopes are there; their inner structure is not); D4's other two explanations: *requirements*
   (a test explained with no matter) and *the application process* from filing (a second template,
   before examination); A06 step 2 (a question about s 44 retrieves GL-0001's conditions and
   exceptions); more fictional matters from A12's list (evidence covering the wrong period,
   ambiguous everyday wording that should be asked about, not chosen).
3. **Afterwards:** Package 5 (versioning model A03; the dependency index as a candidate rule; scenarios
   A10); the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **The US$4 is unspent.** Allow `tmk-bulk` paid calls in the session's permissions (or run
  `tmk-bulk embed --confirm` yourself) and say so.
- **The customer prototype page** (`tmk-explain --html`) is sent to you as a file; it shows four
  invented matters. Showing anything like it to customers, or testing it with them, is your gate.
- **GC-0012's s 27(3)(b)** stays unverified unless you rule that a correction may anchor it.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark.

## What to distrust

- **The legal tests are one agent session's reading**, unreviewed: which conditions are `fact` and
  which `evaluative`, the leaf texts (plain words within each quote), the s 41 relevance/sufficiency
  split, and the routes chosen. GL-0001 models goods only; s 44(2) is named, not repeated.
- **The process template simplifies**: one consideration step for every report; a hearing (s 33(4))
  as a condition, not a step; extensions of time (s 224, reg 4.12(3)) named only in "needs".
- **The explanation is only as good as the fictional matter's recording**; "recorded as met" means
  the fictional report's examiner assessed it, never that it is so.
- **The outcome guard reads unattributed sentences only** (a sentence with "report", "whether",
  "if" is skipped): a determined phrasing could pass it. It is a test, not a filter on output.
- From earlier in S042: the dependency index sees only what a record names; a contract "met" is a
  property of rows; the clause rule and the citation pattern are heuristics; the provision search
  is unmeasured. The 20 base re-reads are one session's judgement.
- From S041, unchanged: R07 and R02 readings; the coarse proceeding lookup; **`answer-v4` has never
  run against the real model**; the live answer is not the measured one; GC-0179's old quote;
  `docs/PITCH-PACK.md` stale; GK-0037; hand-copied hashes on GR-0672, GK-0003; the reviewer's
  initials in `site/data/ontology.json`.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29).
- **A paid call may be refused by the session, not the cap** (Q-99).
- **After changing records, the builder, a schema or `ontology/draft/`**: `tmk-graph --write --rules`
  (a new schema `$id` moves `graph/manifest.json`), then `tmk-ontology-report --write`.
- **Five structure ledgers now** (`restructure`, `review-response`, `review-response-2`,
  `conditions-r07`, `bases-r10`): dry-run all five after touching `bulk/restructure.py`.
- **Writing a GL/GP record**: every element needs `ref` + `quote`, and every quote must be in the
  envelope's evidence with span and hash (`jobs.evidence` locates them); the reader refuses one
  that is not. Element ids are lowercase and unique within the record.
- **YAML flow mappings in `scenarios/`**: a comma in an unquoted value splits it; the matter
  checker reports it as an unexpected property.
- **Engines change together**: as before, plus `search.citations`/`namedProvisions`,
  `ProvisionIndex`/`provisionSearch` (one shared `bm25Index` in `engine.js`),
  `jobs.legislation_refs`/`Engine.prepare`.
- **Definitions, corrections, legal tests and processes have their own readers**
  (`authored.definitions`, `.corrections`, `.procedure`); `served_gold()` serves, `goldset.load()`
  measures.
- **The explorer needs the snapshot** (Q-90); a local server must serve `.mjs` as JavaScript.

## Open items (agent-proposed, provisional)

- **ADR-0142** (the slice's record types, the engine's rules, fictional-only), and its content: the
  three tests, the template, the four matters.
- **ADR-0141's agent part** (what the US$4 is for).
- S042's engineering: the dependency index's views and ref walk; the clause-break and citation
  patterns; contracts and `SHAPE_COLUMNS`; CQ-0009 by section 29.9; the manifest's fields; the
  source register; provision search shown apart; the bases ledger's 20 judgements; the outcome
  guard's attribution words.
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

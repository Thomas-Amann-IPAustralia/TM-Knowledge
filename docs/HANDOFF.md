# HANDOFF

**Last updated:** 2026-10-20 · S043 (end) · branch `claude/busy-sagan-4k4kom`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`'s
order: Packages 1 and 3 done (S041); Package 2 done (S042); Package 4, the first customer slice,
done (S042 started it, S043 finished it, ADR-0142 and ADR-0144).** The owner asked S043 to "conduct
the remaining stage 4 work", read as the handoff's Package 4. Nothing was spent.

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

**Package 4, as it now stands (all agent-proposed, all unreviewed, all fictional where a case is involved).**
- **Legal tests** `authored/legal-tests.yaml`: GL-0001 s 44, GL-0002 s 43, GL-0003 s 41 (unchanged in S043).
- **Process templates** `authored/processes.yaml`: GP-0001, the regs 4.8–4.14 report loop (S042);
  **GP-0002, filing to registration** (S043): ss 27, 31, 33, 34, 52, 68, 72 and regs 4.8, 5.6, 7.1;
  8 steps, 9 transitions, 3 time rules, 14 quotes; its report step `continues_in` GP-0001 (process
  schema 1.1.0; the reader refuses a `continues_in` naming no template).
- **In the graph** (ADR-0144): every element of a test or template is a `tmk:RecordElement` node
  (`tmka:GL-0001/element/<id>`, minted by `namespaces.element_node`, documented in `IDENTIFIERS.md`):
  condition groups with their join and ordered parts, fact and evaluative leaves, effects with their
  kind, exceptions, evidence requirements, routes, steps, transitions (from, to, needs, the ground a
  branch exists for), time rules. Each is stamped, says law or practice, and is anchored to the
  evidence item holding its exact quote. 85 elements, 12 new shapes, 12 new classes (105 declared).
- **Three explanations** (`tm_knowledge.explain.engine`), D4's three: an objection on a fictional
  matter (S042); **`requirements(test)`** with no matter; **`walkthrough(template)`** with no
  matter. `tmk-explain --test GL-0001`, `--process GP-0002`; `--html PATH` writes all of it on one
  page (matters, then the process drawn as a flow, then each test's requirements), each view with
  its text equivalent. **Not deployed, not for customers.**
- **Fictional matters** `scenarios/matters.yaml`: FM-0001–0004 (S042) plus **FM-0005** (s 41(3),
  evidence all after the filing date or undated) and **FM-0006** (an objection known only from the
  customer's words, `test: null`; matter schema 1.1.0). The engine never maps everyday words to a
  ground: it names every ground held and asks which section the report cites; deferment is offered
  with "whether the objection is under s 44" as its first need. The evidence view now lists a
  requirement it sets aside (after-filing use under s 41(4) when the report reads (3)) and why.
- **A06 step 2**: `search.structured.find` = `engine.js` `structuredTests` — a test is reached when
  the question names its provision or recognises its ground. The Ask page shows a reached test's
  conditions and exceptions in a card of its own ("Machine · unreviewed"), for live and prepared
  questions. **Not given to the answering model.** `search.json` carries the tests; parity is held
  on all 129 benchmark questions.

Graph rebuilt, ontology report rebuilt, SHACL 0 defects, harness 0 defects. Full test suite: see
the commit that closes S043 for the count (the run is recorded in its body).

## Next actions

1. **Package 5** (the response's order): the versioning model defined (A03), with version selection
   once upstream holds a second compilation; the dependency index in the graph as a candidate rule
   (R05, A10); normative scenarios on fictional matters (A10).
2. **Customer slice, widening** (no gate needed while fictional): more tests (s 42 scandalous or
   contrary to law, s 39 prescribed signs, s 41's Part 22–26 sub-routes); an opposition template;
   GP-0002's left-outs (revocation of acceptance s 38, divisionals, priority claims).
3. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **The prototype page** (`tmk-explain --html`) now holds six fictional matters, the process from
  filing as a flow, and the three tests' requirements. Showing it to customers, or testing it with
  them, is your gate.
- **A decision when you want it: should the answering model see a reached structured test?**
  Today the Ask page shows GL-0001's conditions and exceptions beside the answer for a s 44
  question, but the model still writes from passages and provisions alone (ADR-0139's inputs).
  Giving it the test would put the exceptions in front of it by rule; it changes what the chatbot
  is given, so it is yours. Recommended, with the test stamped in the prompt as the definitions are.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

- **GP-0002 is one agent session's reading**: opposition ends only in registration or lapse here;
  the transition from opposition to registration quotes s 68(1)(b)(i) and names (ii) and (iii) in
  words only; the report → acceptance transition stands for all of GP-0001's paths to acceptance.
- **The structured-test lookup is unmeasured** and coarse: a recognised ground pulls its test even
  when the question is about something else under that ground.
- **FM-0006's candidate list is every test held** (three); it does not narrow. That is deliberate
  (ADR-0144 c4), and it means the list grows with the tests.
- **The legal tests are one agent session's reading** (S042), unreviewed: fact/evaluative splits,
  leaf texts, the s 41 relevance/sufficiency split, the routes. GL-0001 models goods only.
- **The explanation is only as good as the fictional matter's recording**; "recorded as met"
  means the fictional examiner assessed it.
- **The outcome guard reads unattributed sentences only**; GP-0002's opposition step had to be
  reworded ("After acceptance", not "Once the application is accepted") to pass it. It is a test,
  not a filter on output.
- From S042: the dependency index sees only what a record names; contract "met" is a property of
  rows; the clause rule and citation pattern are heuristics; provision search is unmeasured; the
  re-written answers are checked, not judged (A08); nobody has read the 810 claims.
- From S041, unchanged: R07 and R02 readings; the coarse proceeding lookup; GC-0179's old quote;
  `docs/PITCH-PACK.md` stale; GK-0037; a hand-copied hash on GR-0672.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29).
- **A paid call may be refused by the session, not the cap** (Q-99).
- **Naming a TBox property** (Q-100): not a `str` method (`TMK.join` is the method), not a
  predicate's name (`runsFrom` is one).
- **After changing records, the builder, a schema or `ontology/draft/`**: `tmk-graph --write --rules`
  (a new schema `$id` moves `graph/manifest.json`), then `tmk-ontology-report --write`.
- **Writing a GL/GP record**: every element needs `ref` + `quote`, and every quote must be in the
  envelope's evidence with span and hash (`bulk.jobs.evidence` locates them; S043's GP-0002 was
  written by a script that locates every quote first). Element ids are lowercase and unique within
  the record, and they become IRIs.
- **The outcome guard in `test_explain.py`** flags "the application is accepted" even inside a
  "once"/"after" clause; word steps and transitions around it.
- **Five structure ledgers** (`restructure`, `review-response`, `review-response-2`,
  `conditions-r07`, `bases-r10`): dry-run all five after touching `bulk/restructure.py`.
- **Engines change together**: as before (`search.citations`/`namedProvisions`,
  `ProvisionIndex`/`provisionSearch`, `jobs.legislation_refs`/`Engine.prepare`), plus
  **`search.structured.find`/`structuredTests`**.
- **YAML flow mappings in `scenarios/`**: a comma in an unquoted value splits it.
- **The explorer needs the snapshot** (Q-90); a local server must serve `.mjs` as JavaScript.

## Open items (agent-proposed, provisional)

- **ADR-0144** (elements as nodes and their shapes; the two no-matter explanations; GP-0002;
  everyday wording asked, never mapped; FM-0005 and FM-0006; the A06 lookup rule and its card).
- **ADR-0142** (the slice's record types, the engine's rules, fictional-only), and its content.
- ADR-0141's and ADR-0143's agent parts.
- S042's engineering: the dependency index's views; the clause-break and citation patterns;
  contracts and `SHAPE_COLUMNS`; CQ-0009; the manifest; the source register; provision search
  shown apart; the bases ledger's 20 judgements; the outcome guard's attribution words.
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

# HANDOFF

**Last updated:** 2026-10-20 · S045 · Package 5 on branch `ccr-a421cc83-m425ob`, with `main` merged
in after PR #45 (S044's site rework). S045 touched the site in one card only.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`'s
order, and every package in it is now built: 1 and 3 (S041), 2 (S042), 4 (S042–S043), 5 (S045,
ADR-0147).** The owner asked S045 to "Complete the construction of package 5". Nothing was spent.

**The site rework is finished and on `main`** (S044, ADR-0145, ADR-0146, PR #45): four layers
(what it does, what it could do, rules as code, the ontology), `#/rules` with s 44 drawn and the
process from filing as a flow, `#/standards`, and the **customer preview** `#/customers` behind its
banner (the owner's "Build it", CHAT-0096). `tmk-explorer` writes `site/data/explain.json` from
`tm_knowledge.explain` itself, so S045's version line reaches the preview's text equivalents by
itself, and `#/rules` counts RULE-0003 from its file.

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

**Package 5, as it now stands (ADR-0147, all agent-proposed).**
- **The versioning model (A03).** `ontology/draft/time.ttl`: an instrument is enduring
  (`tmk:doc/TMA1995`, `tmk:registerTitleId` C2004A04969); a `tmk:Compilation` is one text of it
  (`tmk:doc/TMA1995/compilation/48`), in force over an OWL-Time interval with a beginning and no
  stated end; `tmk:currentAtCapture`; every provision and unit says `tmk:textFrom` its
  compilation; five `tmk:VersionState`s; `tmk:applicableDuring` defined for scoped statements and
  unused. `tm_knowledge.versions.select` answers held / not held / after capture / unconfirmed /
  no date, tested on two invented compilations, because the snapshot holds one of each
  instrument. It never decides which date governs a question. `upstream.records.Instrument` now
  reads `title_id`, `status` and `has_unincorporated_amendments` (optional).
- **Every customer explanation names the text it quotes** and what can be said of the text in
  force on the filing date: four of the six fictional matters were filed before compilation 48
  began ("an earlier text than the one quoted here, which is not held"); two give no date (an
  explicit unknown). Text, page and object alike.
- **One definition per concept per scope** (definition schema 1.1.0, `scope`;
  `Definitions.resolve` → none / single / scoped / unresolved). No concept has two today; a test
  says so and will fail on purpose when one does. Supersedes ADR-0137's "one per concept".
  `tmk:defines` stays functional (one concept per definition, which is all it ever said).
- **RULE-0003, the dependency index in the graph** (`queries/rules/RULE-0003-dependency-index.rq`):
  `tmk:restsOn` from every record of either store to every held source it names, with
  `tmk:dependencyVia` and `tmk:dependantStore`; 1,528 conclusions, **pending, asked as OQ-0030**.
  Held to the Python index's pairs by `test_rule_0003_agrees_with_the_dependency_index`; the
  check found and S045 closed two export gaps (a typing's `basis`, now `tmk:typingBasis`; an
  element's own refs) and one misattribution (a relationship's direct edge credited to its
  concept, now excluded).
- **Normative scenarios (A10).** `scenarios/amendments.yaml`: FS-0001 (s 41(3) counts use after
  filing; on FM-0004, FM-0005), FS-0002 (s 44(3)(a) omitted: a near miss, elements change and no
  reading does), FS-0003 (s 44(1) "may"; on FM-0001, FM-0003). `tm_knowledge.explain.scenarios`
  edits a copy of the test, labels every changed element `draft`, explains each matter both
  ways and compares them element by element; beside it the records resting on the provision
  (split: naming it, naming only the whole, through the Manual) and the behavioural effect stated
  unknown. `tmk-explain --scenario FS-0001|all`. A draft is in no graph, index, site or prompt
  (tested). A scenario naming a compilation not held is refused.
- **The site:** only `future.js`'s policy card changed, to say two layers work.

Graph rebuilt (source 69,460, authored 30,071, inferred 24,048 triples), ontology report rebuilt,
SHACL 0 defects, harness 0 defects. **948 tests pass, 4 xfail** at the end of S045 (the full run: 947 and one
declaration failure, fixed and re-run with its neighbours).

## Next actions

1. **Raise upstream: a second compilation of the Act** (the one before 48, and the transitional
   provisions), so `versions.select` can choose between texts and a scenario can compare a draft
   with an earlier law. Raising it is the owner's or a session's to do; nothing here captures it.
2. **Customer slice, widening** (no gate needed while fictional): more tests (s 42, s 39, s 41's
   Part 22–26 sub-routes); an opposition template; GP-0002's left-outs. Each new test can carry a
   scenario at little cost.
3. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **OQ-0030: approve or reject RULE-0003** (what rests on each source). Nothing is blocked.
- **The scenarios are a command, not a page.** Showing them to anyone, or simulating a real
  draft, is yours; a real draft is policy content (§3a: outward-facing).
- **A decision when you want it: should the answering model see a reached structured test?**
  (unchanged from S043; recommended, with the test stamped in the prompt.)
- **The customer preview is on the site** (your choice); showing it to customers, testing with
  them, or real case data are still yours.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

- **A scenario's edits are one agent session's reading of an invented draft.** FS-0001 assumes
  the Manual's "before the filing date" practice would follow the Act; it says so, and it is an
  assumption, not a reading.
- **The compare step is element-keyed**: an element renamed by a draft would show as removed and
  added, not changed. No scenario renames one today.
- **"Held" for the latest compilation rests on upstream's record at capture** (status InForce,
  nothing unincorporated). Between the capture (17 October 2026) and today the snapshot cannot
  tell; that is `after_capture`, by design.
- **RULE-0003's residue** (pairs the index sees and the graph cannot): a correction's added and
  withdrawn values are literals in the graph, and a few signed fields (a search question's
  relevance grades, some concept fields) are not exported as links. The test caps it at 2%.
- From S044: the site's new prose and the s 44 diagram and flow are one session's work on
  unreviewed records; the flow cuts a step label at 34 characters; `checks.rules[].approved` reads
  the `# approved-by:` header.
- From S043: GP-0002 is one session's reading; the structured-test lookup is unmeasured and
  coarse; FM-0006's candidate list is every test held; the legal tests are unreviewed; the
  outcome guard reads unattributed sentences only.
- From S042 and S041, unchanged: the dependency index sees only what a record names; R07 and R02
  readings; the clause rule and citation pattern are heuristics; `docs/PITCH-PACK.md` stale.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29).
- **`tmk-graph --write --rules` takes about 75 seconds** now, half of it RULE-0003; a new rule
  must be timed against the committed dataset first (Q-103: rdflib does not reorder joins).
- **A paid call may be refused by the session, not the cap** (Q-99).
- **Naming a TBox property** (Q-100): not a `str` method, not a predicate's name.
- **After changing records, the builder, a schema or `ontology/draft/`**: `tmk-graph --write
  --rules`, then `tmk-ontology-report --write` (about 2.5 minutes).
- **Writing a GL/GP record**: every element needs `ref` + `quote`, every quote in the envelope's
  evidence with span and hash; element ids lowercase, unique, and they become IRIs — and a
  scenario targets them by id.
- **Writing a scenario**: it names the compilation it amends; `drop_check` needs a check the
  requirement has; `set_effect_kind` targets `effect` or an exception id.
- **The outcome guard in `test_explain.py`** is shared with `test_scenarios.py`
  (`from test_explain import _outcomes`).
- **Five structure ledgers**: dry-run all five after touching `bulk/restructure.py`.
- **Engines change together**: `search.citations`/`namedProvisions`, `ProvisionIndex`/
  `provisionSearch`, `jobs.legislation_refs`/`Engine.prepare`, `search.structured.find`/
  `structuredTests`; and `jobs.definition_lines` now joins a concept's scoped definitions.
- **The explorer needs the snapshot** (Q-90); a new record type reaches neither the site nor the
  dependency index by itself (Q-101).
- **Checking the site**: `tmk-explorer --write`, `python3 -m http.server` in `site/`, Playwright via
  Node (`NODE_PATH=$(npm root -g)`, Chromium in `/opt/pw-browsers`), a fresh page per route (Q-102).
  Prefix new CSS classes (Q-101; S044 used `dg-`, `rx-`, `sd-`, `cx-`, `ab-`).

## Open items (agent-proposed, provisional)

- **ADR-0147** (the versioning vocabulary and states; the explanations' version line; one
  definition per scope and its disambiguation rule; RULE-0003's scope and exclusions; the
  scenario format, its four edits, and the three scenarios).
- **ADR-0146's agent parts** (`explain.json` from the engine, the preview's tabs and banner,
  `diagrams.js`, `checks` and `samples`, the standards page, About's order) and **ADR-0145's** (the
  four layers and their names, the home page, the glossary).
- **ADR-0144** (elements as nodes; the two no-matter explanations; GP-0002; FM-0005, FM-0006;
  the A06 lookup rule). **ADR-0142** (the slice's record types and engine rules) and its content.
- ADR-0141's and ADR-0143's agent parts; S042's engineering (the dependency index's views, the
  clause-break and citation patterns, contracts, CQ-0009, the manifest, the source register,
  the bases ledger's 20 judgements, the outcome guard's attribution words).
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

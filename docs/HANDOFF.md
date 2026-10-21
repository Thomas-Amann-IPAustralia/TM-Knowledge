# HANDOFF

**Last updated:** 2026-10-21 · S047 · a what-if page for geographical indications (ADR-0149) on
branch `ccr-773c02bf-jryenk`, built on `main` after PR #47 (the redesign, merged). Not merged.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **Every package in
`docs/ONTOLOGY-REVIEW-RESPONSE-2.md` is built**; the redesign (ADR-0148) is merged and live.
Nothing was spent in S047.

**S047 added a what-if on the owner's word** (CHAT-0098, `review/returned/261021-owner-chat-gi-what-if.md`,
ADR-0149): *"a small demonstration to the front end about how the introduction of geographic
indicators as a new IP right might impact/influence examination practice"*, which *"must not alter
the underlying ontology"*.
- **`scenarios/what-if.yaml`, FW-0001**: a new fixture series (`FW-`, `docs/IDENTIFIERS.md`). An
  invented premise (a register of geographical indications for any goods; no draft text) and five
  touch points: the register to search, which question a registered name raises (s 42(b) / s 43 /
  an earlier right like s 44), distinctiveness (s 41), s 61 from opposition towards examination,
  certification marks. Each quotes the Manual verbatim (span, hash), names existing GC/GL/GP
  records and provisions, and asks questions; it answers none.
- **`tm_knowledge.explain.whatif`** validates it against the snapshot and records and counts what
  would be re-read from the dependency index; `tmk-explorer` writes `site/data/whatif.json`.
- **`#/whatif`** (`site/js/whatif.js`, prefix `wi-`, layer 2): the invented drawn above a dashed
  line, the ontology below it unchanged (12 ideas, their 12 recorded connections, six provisions,
  three legal tests), with a text equivalent; linked from Trace a change, What's next, the footer.
  s 61 shows as **no recorded dependency**: a real gap the demo exposes.
- **Unchanged:** `authored/`, the graph, every other data file, the prompt, the explanations; a
  test checks the what-if's words reach none of them. No graph rebuild was needed.

**QA:** `#/whatif`, `#/change`, `#/future` at 1280 and 1920 px in Chromium, no script errors, no
sideways scroll; touch point selection, the drawer from a provision and an idea's click to the map
driven. **70 tests pass** in the four touched files (`test_whatif`, `test_explorer`,
`test_scenarios`, `test_hygiene`); the full suite was not run (about twenty minutes, Q-29).

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

**Package 5, unchanged since S045 (ADR-0147, agent-proposed):** the versioning model; RULE-0003
**pending as OQ-0030**; three normative scenarios (`tmk-explain --scenario`), in no graph or site.

## Next actions

1. **The owner's look at the what-if (`#/whatif`), then a merge.** Merging to `main` publishes it
   (ADR-0112). Another what-if is one more `FW-` record in `scenarios/what-if.yaml`; the page draws
   the first one only today.
2. **Raise upstream: a second compilation of the Act** (the one before 48, and the transitional
   provisions), so `versions.select` can choose between texts.
3. **Customer slice, widening** (no gate needed while fictional): more tests (s 42, s 39, s 41's
   Part 22–26 sub-routes); an opposition template; GP-0002's left-outs. A new test reaches the
   Explain page and rules as code on the next build with no page change.
4. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **The what-if is on the branch, not live.** Merging is yours; so is saying anything about
  geographical indications outside the repository.
- **OQ-0030: approve or reject RULE-0003** (what rests on each source). Nothing is blocked.
- **A decision when you want it: should the answering model see a reached structured test?**
  (unchanged since S043; recommended, with the test stamped in the prompt.)
- **The customer preview is on the site** (your choice); showing it to customers, testing with
  them, or real case data are still yours. The scenarios are a command, not a page.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

- **The what-if is one session's reading.** The premise, the five touch points, their "what if"
  paragraphs and questions are the agent's, unreviewed (ADR-0149). The counts are real but
  dominated by s 43, which most of the Manual cites; they say what rests on a provision, not how
  much a new right would change it.

- **The redesign is one session's design.** The site's new prose, the How it works story, the
  Overview's chosen example and every picture's encoding are the agent's; ADR-0148 marks them
  provisional. The Overview says its example question was chosen because it shows the connections
  at work, and that the picture is mixed across all questions; keep both if it changes.
- **The map's layout is shaped to the window when the page opens** (`squeezeFor`): the same data
  and window give the same picture, a different window a different one; resizing does not re-lay
  it out.
- **Light theme only.** A reader with a dark system setting still gets the light page.
- From S045: a scenario's edits are one session's reading of an invented draft; the compare step is
  element-keyed; "held" for the latest compilation rests on upstream's record at capture;
  RULE-0003's residue (capped at 2% by its test).
- From S043 and S044: GP-0002 and the s 44 diagram are one session's readings; the
  structured-test lookup is unmeasured and coarse; the legal tests are unreviewed; the outcome
  guard reads unattributed sentences only.
- From S042 and S041, unchanged: the dependency index sees only what a record names; R07 and R02
  readings; the clause rule and citation pattern are heuristics; `docs/PITCH-PACK.md` stale.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29); install with
  `pip install -e ".[test]"` first or pytest is missing.
- **Clicking an SVG group in Playwright**: click a shape inside it (Q-106).
- **Checking the site**: `tmk-fetch-upstream`, `tmk-explorer --write`, then
  `python3 -m http.server -d site 8000`; Playwright via Node as CommonJS (Q-105), Chromium in
  `/opt/pw-browsers`, a fresh page per route (Q-102).
- **Site CSS**: every view's classes carry its prefix (`site/README.md` lists them, Q-101); grep
  `site/js/` before adding a utility class (Q-104). The phrases the tests pin are in
  `tests/unit/test_explorer.py`; keep each word for word.
- **The hygiene check reads `confidence` near `<` or `>` as a ranking** (`test_hygiene.py`):
  in a template, keep a confidence test and an HTML tag on different lines.
- **`tmk-graph --write --rules` takes about 75 seconds**, half of it RULE-0003 (Q-103).
- **A paid call may be refused by the session, not the cap** (Q-99).
- **After changing records, the builder, a schema or `ontology/draft/`**: `tmk-graph --write
  --rules`, then `tmk-ontology-report --write` (about 2.5 minutes).
- **Writing a GL/GP record**: every element needs `ref` + `quote`, every quote in the envelope's
  evidence with span and hash; element ids lowercase, unique, and they become IRIs.
- **Engines change together**: `site/js/engine.js` with `search.index` (parity test);
  `search.citations`/`namedProvisions`, `ProvisionIndex`/`provisionSearch`,
  `jobs.legislation_refs`/`Engine.prepare`, `search.structured.find`/`structuredTests`; and
  `jobs.definition_lines` joins a concept's scoped definitions.
- **Naming a TBox property** (Q-100): not a `str` method, not a predicate's name.
- **Writing a scenario**: it names the compilation it amends; `drop_check` needs a check the
  requirement has; `set_effect_kind` targets `effect` or an exception id. The outcome guard in
  `test_explain.py` is shared with `test_scenarios.py`. Dry-run all five structure ledgers after
  touching `bulk/restructure.py`.
- **The explorer needs the snapshot** (Q-90); a new record type reaches neither the site nor the
  dependency index by itself (Q-101).

## Open items (agent-proposed, provisional)

- **ADR-0149's agent parts** (the `FW-` series, the five touch points and their wording, the page's
  picture and its place in layer 2).

- **ADR-0148's agent parts** (the header's order and the layers' new names; the visual system and
  its two palettes; light theme only; the Overview's example; How it works' nine steps; the map's
  layout, labelling and Kinds view; the retired modules and Cytoscape).
- **ADR-0147** (the versioning vocabulary and states; the explanations' version line; one
  definition per scope; RULE-0003's scope and exclusions; the scenario format and the three
  scenarios).
- **ADR-0146's agent parts** (`explain.json` from the engine, `diagrams.js`, `checks` and
  `samples`) and **ADR-0145's** (the four layers, the glossary).
- **ADR-0144**, **ADR-0142** and their content; ADR-0141's and ADR-0143's agent parts; S042's
  engineering (the dependency index's views, the clause-break and citation patterns, contracts,
  CQ-0009, the manifest, the source register, the bases ledger's 20 judgements).
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

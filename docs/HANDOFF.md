# HANDOFF

**Last updated:** 2026-10-20 · S046 · the site redesign (ADR-0148) on branch
`claude/trusting-franklin-c1h7wi`, built on `main` after PR #46 (S045's Package 5). Not merged.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **Every package in
`docs/ONTOLOGY-REVIEW-RESPONSE-2.md` is built** (1 and 3 in S041, 2 in S042, 4 in S042–S043, 5 in
S045, ADR-0147). Nothing was spent in S046.

**S046 redesigned the explorer on the owner's word** (CHAT-0097,
`review/returned/261020-owner-chat-site-redesign.md`, ADR-0148): *"completely re-design the front
end"* to communicate the ontology's value, the outcome first, how it works explained simply,
visual, interactive where it helps (the knowledge graph above all), progressive disclosure, no
clutter, desktop and laptop only, and *"must not impact or change the shape of the underlying
ontology"*. The owner's ChatGPT mock-up is `docs/tm-knowledge-redesign.html` (reference only).
What changed, all in `site/`:
- **A design system** in `explorer.css`: paper, deep green and lime; ideas coloured by family,
  passages by source with their marks; both palettes checked for colour-blind readers; light
  theme only (no dark palette passed). `site/README.md` describes it.
- **Outcome pages first**: the Overview (one question answered with and without the map of
  meaning, what it does for examiners, customers and policy, the measurement in both directions,
  the foundation, where things stand); Research, Explain, Trace a change and What's next rebuilt
  as visual pages with the detail behind disclosures.
- **How it works**: a nine-step scrolling story over one picture (`how.js`).
- **The knowledge map rebuilt in D3** (`map.js`, `netlayout.js`): every idea and connection, a
  seeded layout shaped to the frame, hover for a neighbourhood, focus an idea to label its
  connections and gather the passages and provisions it rests on round it, names placed so none
  overlaps, a Kinds view, search, a full card per idea.
- **Rules as code, the standards, the glossary, the tables, Where it stands** restyled: the three
  forms of rule drawn small; the standards as one clickable stack with the four compartments to
  scale; a searchable glossary every inline term links into; the measurement as intervals said in
  words (better, worse, not established).
- **Retired**: `tour.js`, `circles.js`, `model.js`, `minimap.js`, `kinds.js` and the Cytoscape
  library; `#/tour` and `#/model` open How it works, `#/circles` the map's Kinds view.

Nothing in the ontology, its records, the graph, `tmk-explorer`'s data, the answering prompt or
the explanation objects changed; no Python changed. **QA:** every route at 1280, 1440 and 1920 px
in Chromium, no script errors, no sideways scroll; the map's interactions driven end to end
(hover, search, focus, "Why?", the trail, Escape, kinds, zoom). **951 tests pass, 4 xfail**
(the full suite, no test changed).

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

**Package 5, unchanged since S045 (ADR-0147, agent-proposed):** the versioning model
(`ontology/draft/time.ttl`, `tm_knowledge.versions.select`); every customer explanation names the
text it quotes; one definition per concept per scope; RULE-0003, the dependency index in the graph,
**pending as OQ-0030**; three normative scenarios on fictional matters
(`tmk-explain --scenario`), in no graph, index, site or prompt. 948 tests passed, 4 xfail, at the
end of S045.

## Next actions

1. **The owner's look at the redesign, then a merge.** Merging to `main` publishes it (ADR-0112).
   Anything the owner wants changed is a small edit to one view; `site/README.md` maps them.
2. **Raise upstream: a second compilation of the Act** (the one before 48, and the transitional
   provisions), so `versions.select` can choose between texts.
3. **Customer slice, widening** (no gate needed while fictional): more tests (s 42, s 39, s 41's
   Part 22–26 sub-routes); an opposition template; GP-0002's left-outs. A new test reaches the
   Explain page and rules as code on the next build with no page change.
4. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **The redesign is on the branch, not live.** Merging is yours; so is anything outward-facing.
- **OQ-0030: approve or reject RULE-0003** (what rests on each source). Nothing is blocked.
- **A decision when you want it: should the answering model see a reached structured test?**
  (unchanged since S043; recommended, with the test stamped in the prompt.)
- **The customer preview is on the site** (your choice); showing it to customers, testing with
  them, or real case data are still yours. The scenarios are a command, not a page.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

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

# HANDOFF

**Last updated:** 2026-11-08 · S049 · the site rebuilt around the groups it serves (ADR-0151) on
branch `claude/bold-rubin-gvrvea`, built on `main` after PR #49 (the copy pass, merged). Open as PR #50;
not merged.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). Every package in `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`
is built; the redesign (ADR-0148), the what-if (ADR-0149) and the copy pass (ADR-0150) are merged.
Nothing was spent in S049.

**S049 rebuilt the front end by audience, on the owner's word** (CHAT-0100,
`review/returned/261108-owner-chat-audience-rebuild.md`; ChatGPT's three design reviews, its list of
uses and the owner's four sketches are in `docs/Nov_rebuild-ref-doc/`).
- **Five sections** (`site/js/layers.js`): Overview; For examiners; For the public; For direction
  setting; For nerds (how it works, the map, rules as code, standards, tables, results, glossary).
  Each audience section leads with working demonstrations, then possibilities with a drawing and a
  horizon: working now, within reach, needs more data.
- **New demonstrations:** Explore a legal concept (`#/concepts`, examiners: a bow-tie of one
  concept's connections in each predicate's words, its role in a legal test as fact or assessment,
  the Manual by Part, a research trail); Understand an objection rebuilt (`#/customers`, the public:
  six steps beside a picture of the case that lights the part each step explains, two cases under
  one rule compared). Trace a change asks for a guess first. Ask leads with the answer, the concepts
  and the legal test; the search's mechanics fold behind "Why these sources?".
- **The overview** turns section 44 (GL-0001) from the Act's words into structure, facts and
  assessments marked (the owner's sketch asked for that to be very clear).
- **Retired:** `future.js` (What's next) into the sections; its customer-testing section moved word
  for word to `public.js`, and `#/future` opens the public overview.
- **Unchanged:** `authored/`, the graph, every record, `site/data/` and its builder, the prompts and
  the explanation objects. Nothing changes what the system may say.
- **Tests:** `test_explorer.py` reads the sections and the moved customer-testing pin, and checks
  each audience section says what it is. See the commit body for the run.

**QA:** every route in Chromium at 1366 px, no script errors, no `undefined`/`NaN`, no horizontal
overflow; old routes redirect; the public explainer stepped through; Ask's fold opened and replayed.
Not checked: narrow widths below 1200 px, a screen reader, a live answer (no proxy locally).

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

## Next actions

1. **The owner's look at PR #50, then a merge.** Merging to `main` publishes it (ADR-0112). The owner may want
   to adjust the possibilities, their horizons or their wording; they are the agent's reading.
2. **Make the demonstrations measurable** (the reviews' own advice): give first-time readers a fresh
   case without coaching and score whether they find the first action, predict the change and
   explain it. That is testing with people, so it is the owner's to start (§3a).
3. **Raise upstream: a second compilation of the Act** (the one before 48, and the transitional
   provisions), so `versions.select` can choose between texts.
4. **Customer slice, widening** (no gate needed while fictional): more tests (s 42, s 39, s 41's
   Part 22–26 sub-routes); an opposition template; GP-0002's left-outs.
5. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **The site is on the branch, not live.** Start at the overview; each section stands on its own.
- **The possibilities and their horizons are mine.** "Within reach" means buildable on the
  foundation as it stands; "needs more data" names the data. Overlaps from your sketches and
  ChatGPT's list were combined or worded apart (ADR-0151 item 3). Change any freely.
- **The audience tints** (rose, green, blue, near-black) echo your sketches' sticky notes; they are
  for wayfinding only and never colour a record.
- **OQ-0030: approve or reject RULE-0003.** Nothing is blocked.
- Showing the public demonstrations to customers, testing with them, or real case data are still
  yours; so is which measured results become claims outside the repository.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

- **The rebuild is one session's design**, not tested on a reader. The reviews the owner supplied
  say interaction must earn its place by a test on fresh cases; none has been run.
- **The concept explorer's groups are the predicates' own labels**, verbatim (Q-94), with arrows;
  some read stiffly ("requires element →"). Renaming one is a predicate change, not copy.
- **"Same law, different facts"** compares two invented cases condition by condition; the states
  are the explanation objects', never computed on the page.
- **The guess on Trace a change** has fixed bins (fewer than 10, 10 to 99, 100 or more); it is a
  prompt to think, not a measure of anything.
- **The workbench copy is partly stale** (unchanged since S048), and "map-guided search",
  "knowledge map" and "ontology" still name the same thing in places on the nerds pages.
- From S047 and S046: the what-if is one session's reading; the map's layout is shaped to the window
  on load; light theme only.
- From S045 to S041, unchanged: a scenario's edits are one session's reading of an invented draft;
  RULE-0003's residue; GP-0002 and the s 44 diagram; the structured-test lookup is unmeasured; the
  legal tests are unreviewed; the dependency index sees only what a record names; `PITCH-PACK.md`
  is stale.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29); install with
  `pip install -e ".[test,rdf]"` first. `test_explorer.py` alone builds the site data and takes
  several minutes.
- **Checking the site**: `tmk-fetch-upstream`, `tmk-explorer --write`, then
  `python3 -m http.server -d site 8000`; Playwright via Node as CommonJS (Q-105), Chromium in
  `/opt/pw-browsers`, a fresh page per route (Q-102); click a shape inside an SVG group (Q-106).
- **Site CSS**: every view's classes carry its prefix (`site/README.md` lists them, Q-101), and so do
  their state words: `.stamp`, `.next`, `.small` and `.term` are global (Q-108).
- **Site wording is pinned by tests in four files** (Q-107); the customer-testing pin now reads
  `public.js`. `home.js` must not contain the figures 129, 810, 729, 164 or 357 anywhere, an SVG
  coordinate included.
- **The hygiene check reads `confidence` near `<` or `>` as a ranking** (`test_hygiene.py`).
- **`tmk-graph --write --rules` takes about 75 seconds** (Q-103); only needed after record changes.
- **Engines change together**: `site/js/engine.js` with `search.index` (parity test).
- **A legal test's conditions use `all`/`any` in `ontology.json`** but `children` with `kind` in
  `explain.json`; `concepts.js` and `customers.js` each read their own shape.

## Open items (agent-proposed, provisional)

- **ADR-0151's agent parts** (the five sections and their routes; the tints; the overview's example;
  the possibilities, their horizons and wording; the concept explorer's layout; the six steps of the
  objection explainer; the guess on Trace a change; Ask's fold).
- **ADR-0150's agent parts** (which rewrites were kept, changed and declined; "not formally
  tested").
- **ADR-0149's agent parts** (the `FW-` series, the five touch points and their wording).
- **ADR-0148's agent parts** (the visual system and its two palettes; light theme only; How it
  works' nine steps; the map's layout, labelling and Kinds view; the retired modules).
- **ADR-0147** (the versioning vocabulary and states; RULE-0003's scope; the scenario format).
- **ADR-0146's agent parts** and **ADR-0145's** (the glossary); **ADR-0144**, **ADR-0142** and
  their content; ADR-0141's and ADR-0143's agent parts; S042's engineering.
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

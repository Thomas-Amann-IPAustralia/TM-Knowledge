# HANDOFF

**Last updated:** 2026-11-09 · S051 · the owner's annotated screenshots, a new examiners colour and
ChatGPT's copy brief applied to the site (ADR-0153), on branch `claude/inspiring-carson-s929va`,
built on `main` after PR #51 (S050's UX review, merged). Not merged.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). Every package in `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`
is built; the redesign (ADR-0148), the what-if (ADR-0149), the copy pass (ADR-0150), the audience
rebuild (ADR-0151) and the UX review (ADR-0152) are merged. Nothing was spent in S051.

**S051 refined the site on the owner's word** (CHAT-0102,
`review/returned/261109-owner-chat-annotations.md`). The owner gave seven screenshots marked in red
(remove) and blue (change), asked for the rose to become "a pastel orange/yellow", and attached
ChatGPT's copy brief. Inputs are in `docs/Nov_rebuild-ref-doc/annotations/`; every verdict is in
`docs/feedback-inbox/2026-11-09-copy-brief-after-action-report.md`.
- **Removed, as drawn:** the overview hero's description, buttons and source note (and S050's
  three-audience row that replaced the buttons), so the section 44 rule sits under the headline; the
  hero cards on the three audience pages; the about line's "AI wrote most of its records ..." (the
  owner's answer to F10; the status strip on every page still says it, now pinned); the public
  overview's "What we may test with customers"; For nerds' "The contract, in one line".
- **Changed, as drawn:** the examiners' tint is pastel apricot (`--aud-exam #c8751c`, ink `#8a4a0f`,
  6:1 or better); the examiners' and the public's door pictures are redrawn as centred emblems.
- **Copy brief:** all 13 priority-0 items; most priority-1 items. "Working demonstration" against
  "possible future use"; no unmeasured "faster", "every" over what is recorded, "supercharging" or
  "impact modelling"; the horizon "within reach" is "builds on current work". Where the brief and a
  drawing disagree, the drawing won (the lede, the direction chart, the testing section).
- **Along the way:** demo cards side by side keep their pictures one height (Q-111); the direction
  door's subtitle has its own line.
- **Unchanged:** `authored/`, the graph, every record, `site/data/` and its builder, the prompts and
  the explanation objects, the headline, the section 44 example, the section labels and routes.
  Nothing changes what the system may say.

**Tests:** `test_explorer.py`, `test_whatif.py`, `test_dependencies.py`, `test_hygiene.py` and
`test_dashboard.py` (see the commit body for the run). `test_explorer.py` no longer pins the removed
testing section; it pins the status strip's authorship line and the bounded wording instead.
**QA:** 25 routes and old aliases in Chromium at 1366 px: no script errors, no `undefined`/`NaN`, no
horizontal overflow; screenshots of the five section pages, the concept explorer and the what-if.
Not checked: a screen reader, a live answer, 200% zoom (desktop-only, ADR-0148).

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

## Next actions

1. **The owner's look, then a merge.** Merging to `main` publishes it (ADR-0112). Two readings of
   the drawings to confirm (the report's last section): drawing 01 also took the three-audience
   row; drawing 02 was read as "redraw these two pictures".
2. **The brief's owner questions** (§11): which measured results become claims outside the
   repository; commissioning small task-based tests with examiners, applicants and Manual owners.
3. **Small follow-ups:** real micro-examples for the three thumbnails on Rules as code (F23); a full
   icon-meaning audit (F26); the remaining state pills (F30); glossary entries for "recorded link"
   and "working demonstration" if readers stumble on them.
4. **Make the demonstrations measurable:** first-time readers, fresh cases, no coaching. Testing
   with people is the owner's to start (§3a).
5. **Raise upstream: a second compilation of the Act** (the one before 48, and the transitional
   provisions), so `versions.select` can choose between texts.
6. **Customer slice, widening** (no gate needed while fictional): more tests (s 42, s 39, s 41's
   Part 22–26 sub-routes); an opposition template; GP-0002's left-outs.
7. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **The site is on the branch, not live.** Start at the overview.
- **What the brief asked that I did not do, in one line each:** a new lede on the overview, keeping
  the direction chart and keeping the testing section (your drawings said remove); a Manual
  governance card and a new "why a foundation" block (no new blocks while you are removing them);
  glossary entries (not needed yet).
- **OQ-0030: approve or reject RULE-0003.** Nothing is blocked.
- Showing the public demonstrations to customers, testing with them, or real case data are still
  yours; so is which measured results become claims outside the repository.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

- **The drawings carry no words.** Each reading is the agent's, written down in the returned
  artefact; drawings 01 and 02 are the two that could be read another way.
- **The apricot sits near the Act's amber and the machine stamp's rust.** It is wayfinding only and
  never colours a record, but nobody has checked it with a colour-blind reader.
- **Both rebuilds and this pass are agents' designs**, not tested on a reader.
- From S050: "recorded: met" may come from an invented case's dates rather than its report; the
  bundled connections are grouped by predicate and other end only; the concept explorer's groups are
  the predicates' own labels (Q-94); the guess's bins are a prompt, not a measure.
- From S049 and earlier: the workbench copy is partly stale; "map-guided search", "knowledge map"
  and "ontology" still name the same thing in places on the nerds pages; the what-if is one session's
  reading; the map's layout is shaped to the window on load; light theme only; RULE-0003's residue;
  GP-0002 and the s 44 diagram; the structured-test lookup is unmeasured; the legal tests are
  unreviewed; the dependency index sees only what a record names; `PITCH-PACK.md` is stale.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29); install with
  `pip install -e ".[test,rdf]"` first. `test_explorer.py` alone builds the site data and takes
  several minutes.
- **Checking the site**: `tmk-fetch-upstream`, `tmk-explorer --write`, then
  `python3 -m http.server -d site 8000`; Playwright via Node as CommonJS (Q-105), Chromium in
  `/opt/pw-browsers`, a fresh page per route (Q-102); click a shape inside an SVG group (Q-106).
- **Same-page links** (`href="#id"`) are caught by `app.js` before the router (Q-110).
- **Cards in a grid** that stack a picture over words need `grid-template-rows: auto 1fr` (Q-111).
- **Site CSS**: every view's classes carry its prefix (`site/README.md` lists them, Q-101), and so do
  their state words: `.stamp`, `.next`, `.small` and `.term` are global (Q-108).
- **Site wording is pinned by tests in four files** (Q-107). `home.js` must not contain the figures
  129, 810, 729, 164 or 357 anywhere, an SVG coordinate included.
- **The hygiene check reads `confidence` near `<` or `>` as a ranking** (`test_hygiene.py`).
- **An ADR's metadata line may wrap only after a `·`** (Q-109); run `test_dashboard.py` after one.
- **`tmk-graph --write --rules` takes about 75 seconds** (Q-103); only needed after record changes.
- **Engines change together**: `site/js/engine.js` with `search.index` (parity test).
- **A legal test's conditions use `all`/`any` in `ontology.json`** but `children` with `kind` in
  `explain.json`; `concepts.js` and `customers.js` each read their own shape.

## Open items (agent-proposed, provisional)

- **ADR-0153's agent parts** (the reading of each drawing; the apricot's values; the redrawn doors;
  which brief items were done, adapted or declined; "builds on current work").
- **ADR-0152's agent parts** (which findings were done, in part or declined; the "recorded" wording;
  bundling connections; three possibilities shown; the renamed walkthrough; `--ink-3`'s value).
- **ADR-0151's agent parts** (the five sections and their routes; the tints; the overview's example;
  the possibilities, their horizons and wording; the concept explorer's layout; the six steps of the
  objection explainer; the guess on Trace a change; Ask's fold).
- **ADR-0150's agent parts** (which rewrites were kept, changed and declined; "not formally
  tested").
- **ADR-0149's agent parts** (the `FW-` series, the five touch points and their wording).
- **ADR-0148's agent parts** (the visual system and its two palettes; light theme only; the nine-step
  walkthrough; the map's layout, labelling and Kinds view; the retired modules).
- **ADR-0147** (the versioning vocabulary and states; RULE-0003's scope; the scenario format).
- **ADR-0146's agent parts** and **ADR-0145's** (the glossary); **ADR-0144**, **ADR-0142** and
  their content; ADR-0141's and ADR-0143's agent parts; S042's engineering.
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

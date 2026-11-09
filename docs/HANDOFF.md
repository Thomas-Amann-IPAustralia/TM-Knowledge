# HANDOFF

**Last updated:** 2026-11-09 · S050 · ChatGPT's UX review of the site acted on where it holds
(ADR-0152), on branch `claude/practical-thompson-7l786c`, built on `main` after PR #50 (the audience
rebuild, merged). Not merged.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). Every package in `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`
is built; the redesign (ADR-0148), the what-if (ADR-0149), the copy pass (ADR-0150) and the audience
rebuild (ADR-0151) are merged. Nothing was spent in S050.

**S050 worked through ChatGPT's 30-finding UX review, on the owner's word** (CHAT-0101,
`review/returned/261109-owner-chat-ux-audit.md`; the review is
`docs/Nov_rebuild-ref-doc/TM-Knowledge-UX-Audit-2026-11-09.html`). Sixteen done, nine in part, five
declined; every verdict and reason is in
`docs/feedback-inbox/2026-11-09-ux-audit-after-action-report.md`. The owner asked that the
overview's "One rule, from words to structure" stay; it is unchanged.
- **Claims calibrated:** a matching quotation shows where words come from, not that an answer is
  right (home, examiners, Ask); direction setting finds what a change *might* affect, and a count is
  a review list, not an impact.
- **The public preview's recorded states** are document marks with words ("recorded: met"), never
  ticks, and the board says the site restates the invented report and assesses nothing.
- **The concept explorer** bundles several records of one connection into one entry with its count
  (each listed when selected), shows four per group, and wraps names instead of cutting them.
- **Less in the first screen:** the overview offers the three audiences at once; each audience page
  shows three possibilities and folds the rest; Ask shows three examples; the objection walkthrough
  opens on one case with "Change example"; Trace a change shows the counts first, the guess only if
  asked; the what-if folds its premise; Results and limits leads with a one-paragraph verdict.
- **For nerds** opens with a four-step account of the foundation; "How it works" is now "A search,
  step by step" (`#/how`, unchanged route).
- **Design system:** breadcrumbs on deep pages (`crumb`), `--ink-3` darkened to pass 4.5:1,
  readiness as a dot and label, the map's in-place key (dot size is not importance).
- **Found along the way:** the overview's in-page link went through the router and re-rendered the
  page; `app.js` now catches same-page links (Q-110).
- **Unchanged:** `authored/`, the graph, every record, `site/data/` and its builder, the prompts and
  the explanation objects. Nothing changes what the system may say.

**Tests:** `test_explorer.py`, `test_whatif.py`, `test_dependencies.py`, `test_hygiene.py` and
`test_dashboard.py` (see the commit body for the run); a new test pins the calibrated wording, no
ticks on recorded states and the optional guess. **QA:** every route and old alias in Chromium at
1366 px: no script errors, no `undefined`/`NaN`, no horizontal overflow; keyboard checks of the
concept explorer, the guess, "Change example" and the in-page link. At 200% zoom (683 px) every page
scrolls sideways, before and after: the layouts need about 1,040 px (ADR-0148's desktop-only).
Not checked: a screen reader, a live answer (no proxy locally).

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

## Next actions

1. **The owner's look, then a merge.** Merging to `main` publishes it (ADR-0112). The report's last
   section names the two things that are the owner's: dropping any repeated safeguard (F10) and
   reflowing at 200% zoom, which would reverse desktop-only (F28).
2. **Small follow-ups the review left:** real micro-examples for the three thumbnails on Rules as
   code (F23); a full icon-meaning audit (F26); the remaining state pills (F30).
3. **Make the demonstrations measurable** (the reviews' own advice): first-time readers, fresh cases,
   no coaching. Testing with people is the owner's to start (§3a).
4. **Raise upstream: a second compilation of the Act** (the one before 48, and the transitional
   provisions), so `versions.select` can choose between texts.
5. **Customer slice, widening** (no gate needed while fictional): more tests (s 42, s 39, s 41's
   Part 22–26 sub-routes); an opposition template; GP-0002's left-outs.
6. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **The site is on the branch, not live.** Start at the overview; the section 44 example is as it was.
- **What I declined, in one line each:** the headline and the section labels are yours (subtitles
  added instead); the safeguards are required and pinned, so which to drop is yours; the nine-step
  walkthrough is kept and renamed; the map, rules and standards pages are For nerds, where depth is
  allowed; the bow-tie stays the default view of a concept.
- **OQ-0030: approve or reject RULE-0003.** Nothing is blocked.
- Showing the public demonstrations to customers, testing with them, or real case data are still
  yours; so is which measured results become claims outside the repository.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

- **Both rebuilds are agents' designs**, not tested on a reader; the review is a heuristic review,
  not a usability study.
- **"recorded: met"** restates the explanation object's state; for a fact it may come from the
  invented case's dates rather than its report, which is why the words are "recorded", not "report
  says".
- **The bundled connections** are grouped by predicate and other end only; two records with
  different strengths or conditions sit in one entry and show each strength as its own badge.
- **The concept explorer's groups are the predicates' own labels**, verbatim (Q-94); renaming one is
  a predicate change, not copy.
- **The guess's bins** (fewer than 10, 10 to 99, 100 or more) are a prompt to think, not a measure.
- From S049 and earlier: the workbench copy is partly stale; "map-guided search", "knowledge map" and
  "ontology" still name the same thing in places on the nerds pages; the what-if is one session's
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

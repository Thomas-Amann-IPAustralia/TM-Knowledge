# HANDOFF

**Last updated:** 2026-10-20 · S044 · branch `claude/zealous-mccarthy-2r7uvs` (from `main` after
PR [Thomas-Amann-IPAustralia/TM-Knowledge#44](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/pull/44)
merged). No pull request opened yet: merging this branch to `main` publishes the site changes below.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`'s
order: Packages 1 to 4 done (S041 to S043).** Nothing was spent in S044.

**The site rework is finished (ADR-0145, ADR-0146; the owner asked S044 to "complete the
reconstruction of the GUI").** The explorer leads with outcomes and discloses the ontology last:

- **Layer 1, what it does:** home (four outcomes, a status board), Ask, Change, and the new
  **customer preview** `#/customers` (below).
- **Layer 2, what it could do:** `#/future`, with "What we may test with customers".
- **Layer 3, rules as code:** `#/rules`, now with section 44 drawn as a diagram (provision →
  conditions, facts vs assessments → effect → exceptions with "may"/"may not" → routes) and the
  process from filing drawn as a step flow, each with a text equivalent (`site/js/diagrams.js`);
  two real connections with their modality and condition; the checks counted from `shapes/` and
  `queries/rules/` (42 shapes, RULE-0002 approved, RULE-0001 candidate), and the record's stamp.
- **Layer 4, the ontology:** `#/model` (now with a standards door), the map, glance, tables, tour,
  `#/glossary`, and the new **`#/standards`**: RDF and triples, identifiers, named graphs (a table
  of the four with their counts), SKOS, SHACL, SPARQL and rules, PROV-O, JSON, why no OWL profile
  (the manifest's own words), LegalRuleML deferred; each in three parts with real Turtle blocks.
- **Where it stands** (`#/about`): the measurement first, then "the decisions ahead, and whose they
  are", the release manifest, limits, then what it is built from and how Ask works.
- Brand "Trade Marks Manual · proof of concept"; the tour's last step leads back to Ask and
  `#/future`; Ask's and Change's ledes lead with what they do; prepared-answer count read from data.

**The customer preview (ADR-0146, the owner's "Build it", CHAT-0096).** `tmk-explorer` writes
`site/data/explain.json` from `tm_knowledge.explain` itself (every invented matter's explanation,
each test's requirements, each process walked through, each with its text equivalent and stamp).
The page draws three tabs (what the law requires, the application process, an objection) under a
banner: invented matters only, not tested with customers, not advice, never an outcome, the owner's
decision whether it is shown to customers. It evaluates nothing in the browser.

**Builder additions** (`explorer/build.py`): `explain.json`; `build.json` gains `checks` and
`samples` (machine-written blocks only: a reviewed block names its reviewer, ADR-0130);
`passages.json` now carries every clause a structured record or explanation quotes, so no chip
opens "not in the snapshot" (it did before on the tables' sub-clause chips too).

**QA.** Every route at 1400 and 390 px, light and dark, in Chromium: no script errors, no sideways
scroll (two grids fixed, Q-102). Tests: three new in `test_explorer.py` (the preview is the engine's
own explanation; every quoted clause opens; the standards page reads its examples from the build).
Full-suite count: see the commit that records it.

**Spend.** Cap **US$13.63**, recorded **US$11.61**; the remaining US$2.02 is approved for nothing.

## Next actions

1. **Open a pull request for this branch and merge it** when the owner is happy; that publishes
   the rework and the customer preview (Pages deploys from `main` only).
2. **Package 5** (the response's order): the versioning model defined (A03), with version selection
   once upstream holds a second compilation; the dependency index in the graph as a candidate rule
   (R05, A10); normative scenarios on fictional matters (A10).
3. **Customer slice, widening** (no gate needed while fictional): more tests (s 42, s 39, s 41's
   Part 22–26 sub-routes); an opposition template; GP-0002's left-outs (revocation of acceptance
   s 38, divisionals, priority claims). Each reaches `#/customers` on the next build by itself.
4. **Afterwards:** the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).

## For the owner

- **Merging publishes the customer preview** on the examiner site, as you chose. Showing it to
  customers, testing it with them, or using real case data are still yours to approve.
- **A decision when you want it: should the answering model see a reached structured test?**
  (Unchanged from S043.) Recommended, with the test stamped in the prompt as definitions are.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement.

## What to distrust

- **The site's new prose is one agent session's wording** (S043 and S044): the layer names, the
  standards page's "what it is not" lines, the decisions-ahead list on About, the preview's banner.
  Each states this system's state, not law, but nobody has read them.
- **The section 44 diagram and the flow are drawings of unreviewed records**; they look more
  authoritative than a table. The stamp sits beside each.
- **The preview shows exactly what `tmk-explain` builds**, so everything distrusted there holds here:
  GP-0002 is one session's reading (opposition ends only in registration or lapse; s 68(1)(b)(ii) and
  (iii) in words only); the tests are S042's reading, GL-0001 goods only; FM-0006's candidate list is
  every test held; the outcome guard reads unattributed sentences only.
- **The flow diagram cuts a step label at 34 characters**; the list beside it has every label whole.
- **`checks.rules[].approved`** reads the `# approved-by:` header (anything not starting PENDING is
  approved); a rule file without that header would read as unapproved.
- From S043 and earlier: the structured-test lookup is unmeasured and coarse; the dependency index
  sees only what a record names; R07 and R02 readings; GC-0179's old quote; GK-0037; a hand-copied
  hash on GR-0672; `docs/PITCH-PACK.md` stale.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29).
- **A fresh container needs** `pip install -e ".[test]"` and `tmk-fetch-upstream` before
  `tmk-explorer --write` (about a minute) or most tests (they skip without the snapshot).
- **A paid call may be refused by the session, not the cap** (Q-99).
- **Naming a TBox property** (Q-100): not a `str` method, not a predicate's name.
- **After changing records, the builder, a schema or `ontology/draft/`**: `tmk-graph --write --rules`,
  then `tmk-ontology-report --write`. (S044 changed only the explorer builder, which the graph does
  not read.)
- **Writing a GL/GP record**: every element needs `ref` + `quote`, located in the envelope's evidence.
- **The outcome guard in `test_explain.py`** flags "the application is accepted" even inside "once".
- **Five structure ledgers**: dry-run all five after touching `bulk/restructure.py`.
- **Engines change together**: `search.citations`/`namedProvisions`, `ProvisionIndex`/`provisionSearch`,
  `jobs.legislation_refs`/`Engine.prepare`, `search.structured.find`/`structuredTests`. Adding
  sub-clause refs to `passages.json` is safe: `namedProvisions` builds whole-section refs only.
- **The explorer needs the snapshot** (Q-90); a local server must serve `.mjs` as JavaScript.
- **A new record type reaches neither the site nor the dependency index by itself; prefix new CSS
  classes** (Q-101: S044 used `dg-`, `rx-`, `sd-`, `cx-`, `ab-`).
- **Checking the site**: `tmk-explorer --write`, `python3 -m http.server` in `site/`, Playwright via
  Node (`NODE_PATH=$(npm root -g)`; Chromium in `/opt/pw-browsers`). A fresh page per route (Q-102).

## Open items (agent-proposed, provisional)

- **ADR-0146's agent parts**: `explain.json` from the engine, the preview's tabs and banner wording,
  `diagrams.js`'s drawings, `checks` and `samples` in `build.json`, the standards page's content, the
  About page's order and its decisions-ahead list.
- **ADR-0145's agent parts**: the four layers and their names, the home page's outcomes and status
  board, "What we may test with customers", the glossary entries; the GL/GP views.
- **ADR-0144** (elements as nodes; the two no-matter explanations; GP-0002; everyday wording asked,
  never mapped; FM-0005 and FM-0006; the A06 lookup rule and its card).
- **ADR-0142** (the slice's record types, the engine's rules, fictional-only), and its content.
- ADR-0141's and ADR-0143's agent parts.
- S042's engineering: the dependency index's views; the clause-break and citation patterns;
  contracts and `SHAPE_COLUMNS`; CQ-0009; the manifest; the source register; provision search
  shown apart; the bases ledger's 20 judgements; the outcome guard's attribution words.
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

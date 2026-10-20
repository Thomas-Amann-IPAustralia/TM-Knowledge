# HANDOFF

**Last updated:** 2026-10-20 · S043 (end) · branch `claude/brave-cray-nnkmk5` · PR [Thomas-Amann-IPAustralia/TM-Knowledge#44](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/pull/44) (S044 pushes the rest of the site rework to it)

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). **The plan is `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`'s
order: Packages 1 and 3 done (S041); Package 2 done (S042); Package 4, the first customer slice,
started (S042) and left for a new session by the owner.**

**The site rework is half done (ADR-0144, the owner's direction in S043).** The explorer now leads
with outcomes and discloses the ontology last, in four layers: *What it does* (new home: four
outcomes with their numbers and state, a status board), *What it could do* (`#/future`: the stated
purpose, examiners and customers now, four later uses, and **"What we may test with customers"**),
*Rules as code* (`#/rules`, a first version), *The ontology* (`#/model` hub, the map, glance,
tables, tour, `#/glossary`). A depth strip under the header and a go-deeper card on every page but
the map; `glossary.js` explains every standard inline. **S044 finishes it from the checklist in
`docs/SITE-REWORK.md`**, which says what is done and what is left (the brand, the deeper rules
page with diagrams, `#/standards`, the customer preview `#/customers`, About as "Where it stands",
copy on existing views, visual QA, READMEs). The ruling stays `applied: null` until then.

**Earlier in S043: the explorer brought up to date with the ontology.** The GL/GP records were on
no page and missing from the dependency index ("what rests on section 44" missed GL-0001 and
GP-0001): now in `ontology.json` (`structures`), two table tabs (`#/table/tests`,
`#/table/processes`), every idea card naming them, the change view, and `dependencies.build`
(report §7 regenerated: 2,472 dependencies of 967 records). About no longer says twelve same-idea
pairs are unmerged (11 merged, 1 kept apart; read from `ontology.hygiene`). Q-100 says how to keep
the site in step with a new record type.

**Spend.** Cap **US$13.63**; recorded spend **US$11.61**; the remaining US$2.02 is approved for
nothing. S043 spent nothing.

**The 129 prepared answers are `answer-v4`** against compilation 48 (ADR-0143): 810 claims, 729 with
a checked quote, 84 saying what the passages do not cover.

**Package 2 (S042), complete.** Dependency index (`ontology/dependencies.py`, report §7), query
contracts (`ask.contracts`), clause-scoped authority check with strict-xfail known misses, coverage
by Part, the 21 unverified legislative bases re-read (ledger `data/derived/audit/bases-r10.yaml`;
none left unverified), provision keyword search (`ProvisionIndex` = `Engine.provisionSearch`),
`graph/manifest.json` and the site's `build.json`, `docs/SOURCE-REGISTER.md`.

**Package 4, the slice so far (ADR-0142, agent-proposed).**
- **`GL-` structured legal tests** (`authored/legal-tests.yaml`): GL-0001 s 44, GL-0002 s 43,
  GL-0003 s 41. **`GP-0001` process template** (`authored/processes.yaml`): regs 4.8–4.14, ss 33, 37.
  Reader `authored/procedure.py`; schemas `legal-test`, `process`, `fictional-matter`.
- **Fictional matters** `scenarios/matters.yaml` (FM-0001 to FM-0004); schema allows only
  `fictional: true`.
- **`tm_knowledge.explain`** and `tmk-explain [--matter] [--html PATH]`: the customer explanation,
  written to a file; **not deployed, not for customers, and not part of the explorer**. The explorer
  shows the GL/GP records to examiners as records; it does not show the explanation or the matters.
- **In the graph**: `tmk:StructuredTest` / `tmk:ProcessTemplate` with envelopes and anchors; the
  condition tree and the steps are not yet in the graph.

Graph and ontology report match a rebuild; SHACL 0 defects. **886 tests pass, 4 xfail** (the
authority check's known misses) at the end of S043.

## Next actions

1. **Finish the site rework (S044, by the owner's word, at high effort)** from
   `docs/SITE-REWORK.md`; then close the ruling (`applied:`), delete the plan file, and say so in
   ADR-0144's status.
2. **Package 4, continued (a new session, by the owner's word).** The condition tree, exceptions,
   steps and transitions into the graph; D4's other two explanations (*requirements* with no matter;
   *the application process* from filing, a second template); A06 step 2 (a question about s 44
   retrieves GL-0001's conditions and exceptions, which would also put them in the Ask page); more
   fictional matters from A12's list.
3. **Afterwards:** Package 5 (versioning A03; the dependency index as a candidate rule; scenarios
   A10); the blend (S034); the 15 undefined concepts; heading-only edges (GR-0270).
4. **When a new record type lands**, follow Q-100: dependency index, explorer key and view, report.

## For the owner

- **The explorer now shows the three legal tests and the process template** to examiners, as
  machine-written, unreviewed records in the table view. It is a display of existing records, not a
  change to what an answer may say; say if you would rather they stayed off the public page until
  the customer slice is further on.
- **The customer preview on the site (S044's plan)** would put the prototype's explanation of the
  four invented matters on the public examiner site, loudly labelled, as the transparency you asked
  for; say before S044 if you would rather it stayed a file. Testing with customers stays your gate.
- **The customer prototype page** (`tmk-explain --html`) is still a file only; showing anything
  like it to customers, or testing it with them, is your gate.
- Still: revoke the old OpenAI key (S038); the page's blend, ADR-0131 and the four disputed signed
  readings (S034); who writes the next benchmark; re-measurement (the answers changed, the graded
  search did not).

## What to distrust

- **The legal tests are one agent session's reading**, unreviewed: which conditions are `fact` and
  which `evaluative`, the leaf texts, the s 41 relevance/sufficiency split, the routes chosen.
  GL-0001 models goods only; s 44(2) is named, not repeated. The table view shows each leaf's `ask`
  ("what it would ask of a matter") as the record states it.
- **The process template simplifies**: one consideration step for every report; a hearing (s 33(4))
  as a condition, not a step; extensions of time named only in "needs".
- **The explanation is only as good as the fictional matter's recording**; the outcome guard reads
  unattributed sentences only and is a test, not a filter on output.
- From S042: the dependency index sees only what a record names (the structured records now
  included); a contract "met" is a property of rows; the clause rule and citation pattern are
  heuristics; the provision search is unmeasured; the 20 base re-reads are one session's judgement.
- **The re-written answers are checked, not judged**: a kept quote proves the words exist, not that
  they support the claim (A08); nobody has read the 810 claims.
- From S041, unchanged: R07 and R02 readings; the coarse proceeding lookup; GC-0179's old quote;
  `docs/PITCH-PACK.md` stale; GK-0037; a hand-copied hash on GR-0672; the reviewer's initials in
  `site/data/ontology.json`.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29); install with
  `pip install -e ".[rdf,test]"` (the extra is `test`, not `dev`).
- **A paid call may be refused by the session, not the cap** (Q-99).
- **After changing records, the builder, a schema or `ontology/draft/`**: `tmk-graph --write --rules`,
  then `tmk-ontology-report --write`. **After changing `ontology/dependencies.py`**: the report too.
- **A new record type reaches neither the site nor the dependency index by itself** (Q-100).
- **`explorer.css` has short generic classes the tour uses** (`.fact`, `.bars`): prefix new ones.
- **Checking the site**: `tmk-fetch-upstream`, `tmk-explorer --write`, serve `site/` over HTTP and
  drive it with Playwright (Chromium is at `/opt/pw-browsers`); `site/data/` is not committed.
- **Five structure ledgers** (`restructure`, `review-response`, `review-response-2`,
  `conditions-r07`, `bases-r10`): dry-run all five after touching `bulk/restructure.py`.
- **Writing a GL/GP record**: every element needs `ref` + `quote`, each in the envelope's evidence
  with span and hash; element ids lowercase and unique within the record.
- **Engines change together**: `engine.js` and `search.index` (parity test), `search.citations` /
  `namedProvisions`, `ProvisionIndex` / `provisionSearch`, `jobs.legislation_refs` / `Engine.prepare`.
- **Definitions, corrections, legal tests and processes have their own readers**
  (`authored.definitions`, `.corrections`, `.procedure`); `served_gold()` serves, `goldset.load()`
  measures.
- **The explorer needs the snapshot** (Q-90); a local server must serve `.mjs` as JavaScript.

## Open items (agent-proposed, provisional)

- **ADR-0144's agent parts**: the four layers and their names, the home page's outcomes and status
  board, the wording of "What we may test with customers", the glossary entries.

- **S043's presentation choices**: GL/GP records in the table view rather than drawn on the map; the
  words for enumerations ("a person's assessment", "an obligation (must)"); `ask` shown on each leaf;
  the About page's new section.
- **ADR-0142** (the slice's record types, the engine's rules, fictional-only), and its content: the
  three tests, the template, the four matters.
- **ADR-0141's and ADR-0143's agent parts** (how the run was held and what the prepared answers are).
- S042's engineering: the dependency index's views and ref walk; the clause-break and citation
  patterns; contracts and `SHAPE_COLUMNS`; CQ-0009 by section 29.9; the manifest's fields; the source
  register; provision search shown apart; the bases ledger's 20 judgements; the outcome guard's words.
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

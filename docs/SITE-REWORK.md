# Site rework: outcomes first, the ontology last

The owner's direction of 2026-10-20 (ADR-0145, `review/rulings/2026-10-20-chat-site-emphasis.yaml`):
lead with what the ontology enables, not with the ontology; be transparent about the current state,
including what may one day be tested with customers; disclose progressively, so the deeper a reader
goes the more operational the detail; and never assume a reader knows a standard's name. An
executive and a data engineer should finish with a similar understanding of how the system works.

Two sessions: S043 (the second half of a session that had already done other work) and S044 (a
full session at high effort). This file is the plan and the checklist; tick items as they land and
delete the file when the rework is done (its history stays in git).

## The shape: four layers, one direction

| Depth | Layer (nav label) | Route | Question it answers | Register |
|---|---|---|---|---|
| 1 | **What it does** | `#/` (home); tools `#/ask`, `#/change`, `#/customers` | What does the proof of concept do today, and how well? | Outcomes, numbers, status |
| 2 | **What it could do** | `#/future` | What could it enable, what would that need, what would be tested? | Possibilities, dependencies, gates |
| 3 | **Rules as code** | `#/rules` | What makes those outcomes possible? | Mechanism: tests, conditions, procedures, checks |
| 4 | **The ontology** | `#/model` (hub); `#/map`, `#/circles`, `#/table`, `#/tour`, `#/standards`, `#/glossary` | What conceptual model do the rules build, and on what standards? | Structure, standards, data |

Cross-cutting: **Where it stands** (`#/about`, kept as the route): status, measurement, limits, gates.

Every page carries the same **depth strip** under the header (four steps, the current one marked,
each a link) and ends with a **go deeper** card naming the next layer and what it adds. Most
existing views are kept as they are; what changes is the order a reader meets them in, the nav,
the home page, and the words that frame each view.

**Plain words for every standard.** One glossary (`site/js/glossary.js`): each entry has a plain
sentence, what it means here, and (for the curious) the technical name and a link-free pointer.
`term(key)` renders an inline, keyboard-reachable explanation wherever a term appears; `#/glossary`
lists them all. The rule: no acronym or standard name on any page without `term()` the first time
it appears on that page.

## What S043 does (this session)

- [x] Plan (this file); the owner's words recorded (returned, ruling, ADR-0145).
- [x] `site/js/layers.js`: the four layers as data (label, route, question, which routes belong);
      the depth strip; the go-deeper card. Nav regrouped by layer in `index.html`; `app.js`
      highlights the layer of the current route.
- [x] `site/js/glossary.js`: the dictionary (terms layers 1 and 2 use, plus the standards S044
      needs: RDF, triple, named graph, SKOS, SHACL, SPARQL, PROV-O, OWL, provenance, LLM,
      embedding, nDCG, confidence interval, rules as code, knowledge graph, ontology) and `term()`.
- [x] **Home, rewritten (depth 1):** what the proof of concept does today, as four outcomes with
      their numbers read from the data (examiner research: Ask; finding guidance in everyday words:
      the measurement, both directions; change impact: what rests on a page or provision; the
      customer explanation prototype: built on invented matters, not tested with anyone), then a
      plain status board (working · measured · built, not tested · planned · never).
- [x] **`#/future` (depth 2):** the stated purpose; the two immediate users and four future
      consumers, each with what it builds on today, what is still needed, and its status; a
      section **"What we may test with customers"**: what would be tested (understanding of an
      objection, the requirements and the process, from the three views), how (invented matters
      first, no real customer data, a claim-by-claim support check before any release, the
      owner's approval before anyone outside sees it), what success means (understanding, not
      an outcome), and what it will never do.
- [x] Tests for the scaffolding (every route belongs to a layer; every `term()` key exists; the
      home page reads its numbers from data); README; handoff.

**Also landed in S043, ahead of plan:** first versions of `#/rules` (three ways the rules are
written, section 44 as a worked example in words, how they are kept honest), `#/model` (the old
home's four-level ladder and the doors into the map, glance, tables, tour and glossary) and
`#/glossary`; About retitled "Where it stands"; the notice says nothing has been tested with
customers; the builder counts the invented matters (`counts.fictional_matters`). S044 deepens
`#/rules` and finishes the rest below.

## What S044 does

- [ ] **The brand and the tour.** The header still says "Trade Marks Manual **Map**"; rename it to
      fit an outcomes-first site (for example "Trade Marks Manual · proof of concept"). The tour's
      first step still opens on the ontology; it now sits at layer 4, so its last step should lead
      back up to Ask and to `#/future`, not only to Ask.

- [ ] **`#/rules` (depth 3), deepened:** the S043 version states it in words; add section 44
      drawn as a diagram (the provision → its effect → the condition tree drawn as a
      diagram, facts vs a person's assessment → exceptions → routes), with a text equivalent; the
      process template drawn as a step diagram; connections with their modality and condition (a
      "may" stays a "may"); how the rules are checked (validation shapes, the quote check, the
      approved inference rule RULE-0002); provenance stamps. Links into `#/table/tests` and
      `#/table/processes` for the full records. Every element from the records, never restated.
- [ ] **`#/model` (depth 4 hub):** S043's version is in place; add the standards door when
      `#/standards` exists.
- [ ] **`#/standards` (depth 4):** the standards the graph uses, each in the same three parts
      (plain sentence, what it does here with a real example from `build.json`, what it is not):
      RDF and triples, IRIs, named graphs (source / approved / authored / inferred), SKOS, SHACL,
      SPARQL and CONSTRUCT rules, PROV-O, JSON for the site; **OWL: why no OWL profile is
      claimed** (ADR-0134); LegalRuleML deferred (ADR-0009). Counts from `build.json`.
- [x] **`#/glossary`**, from the same dictionary (S043). Extend entries as S044's pages need.
- [ ] **`#/customers` (depth 1 tool), the customer explanation preview** (since PR #43 merged: the
      invented matters, plus each test's requirements and the process from filing, all from
      `tm_knowledge.explain`): `tmk-explorer` writes `data/explain.json` from `tm_knowledge.explain` (the
      explanation objects and their text equivalents); the page draws the three views with a
      loud banner (invented matters; not tested with customers; machine-written and unreviewed;
      not advice; never an outcome). **Before building it, check the ruling still stands**: it puts
      the prototype on the public examiner site, which the owner asked for as transparency; it is
      not showing it to customers, which stays a gate.
- [ ] **`#/about` → "Where it stands":** status, measurement (kept), limits (kept), the gates
      ahead in plain words, the release manifest's facts (`build.json`).
- [ ] Re-frame copy on the existing views only where it leads with the ontology (Ask's intro,
      Change's lede); do not change their behaviour or the strings tests pin.
- [ ] Visual QA in Chromium at 1400 px and 390 px, light and dark, every route, no script errors.
- [ ] `site/README.md`, `src/tm_knowledge/explorer/README.md`, tests, handoff; delete this file.

## Guardrails (both sessions)

- The page states no legal proposition of its own; the prose explains what to look at. Numbers
  are read from `site/data/`, never typed in.
- Machine-written means "Machine · unreviewed" wherever a record appears (rule 8); reviewed records
  stay quiet (ADR-0130).
- Practice and law keep their marks everywhere, including the new pages (rule 5).
- Future outcomes are described as possibilities with their dependencies, never as commitments;
  nothing says the system decides, or will decide, an application.
- Customer testing, real case data, and publishing to customers remain owner gates (CLAUDE.md
  §3a); the site says so in those words.
- Keep `engine.js` parity and the pinned strings in `tests/unit/test_explorer.py` intact.

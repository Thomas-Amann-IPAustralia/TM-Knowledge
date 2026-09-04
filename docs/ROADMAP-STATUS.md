# ROADMAP-STATUS — where each stage stands

The stage view of the programme. `ARCHITECTURE.md` holds the artefact view.
Update the affected row in the same session that moves a deliverable, and say so
in `HANDOFF.md`.

Legend: **done** · **partial** · **not started** · **n/a here** (owned by
`manual-XtrACTor`)

Stage numbering is the roadmap's own, Stages 0–10. `docs/UPSTREAM.md` §6 summarises
it as "Stages 0–7" — that summary undercounts; see Q-01.

## Board

| Stage | Name | Status | Owner |
|---|---|---|---|
| 0 | Pilot selection and evaluation set | **partial** — pilot area chosen (s 43, ADR-0013); apparatus built (S004–S005); **first approved content landed S008: 190 records over all 8 types, harness 0 defects / 12 gaps**; 178 seed records still await correction, of which **10 decisions hold the other 168** (S009, `tmk-blockers`) | this repo — **the blocker** |
| 1 | Ingest and structure source documents | **done** (4 of 6 named deliverables); consumed here since S004 — pinned, fetched and loaded | `manual-XtrACTor` |
| 2 | Candidate terminology and entities | **not started** — stack fixed (TextRank + YAKE + KeyBERT, spaCy NER as metadata, ADR-0019); blocked by ADR-0010 | this repo |
| 3 | Controlled vocabulary (SKOS) | **not started** | this repo |
| 4 | Relationships, propositions, candidate rules | **not started** | this repo |
| 5 | Formalise the ontology | **partial** — S010. Nine OWL 2 RL modules **drafted** in `ontology/draft/` from the 190 approved records; nothing approved, so `ontology/` is still empty (ADR-0056, ADR-0057) | this repo |
| 6 | Populate and validate the knowledge graph | **partial** — S010. Graph built (16,405 source + 2,942 approved triples) and the SHACL gate runs: **0 defects, 0 gaps, 29 notes**. Built against a *draft* TBox | this repo |
| 7 | Ontology-enhanced search | **not started** | this repo |
| 8 | Graph-aware AI retrieval | **not started** | this repo |
| 9 | Automated reasoning | **partial** — S010. Two CONSTRUCT rules written, **neither approved**; everything they produce is quarantined as `review_status: candidate` | this repo |
| 10 | Automated maintenance | **not started** | this repo |

## Stage 0 — the blocker

The pilot **area** is settled: s 43 (ADR-0013). **Stage 0 content now exists**:
190 approved records landed in S008 from the first review round, every record
type is represented, and the harness runs over them with 0 defects. Two of eight
targets are met (concepts, reasoning expectations). It is still incomplete —
entities at 55 of 100–300, search questions at 1 of 20–50, no scope document and
no measures — so ADR-0010 still holds and no Stage 2+ work starts.

| Deliverable | Status | Where it will live |
|---|---|---|
| Pilot area | **done** — s 43, ADR-0013 | `docs/DECISIONS.md` |
| Pilot scope (the boundary) | not started — awaiting owner; **draft to correct** at `review/seed/pilot-scope.seed.md` | `eval/pilot-scope.md` |
| Competency-question catalogue | **partial** — 20 approved (S008); 4 seed drafts left | `eval/gold/competency-questions.yaml` |
| Gold-standard dataset | **partial** — 159 approved: 52 concepts (target met), 55 entities, 35 relationships, 10 retrieval questions, 6 reasoning expectations (target met), 1 search question | `eval/gold/` |
| Prohibited-use list | **partial** — 11 approved covering 5 of the 6 kinds; `stale_source` missing because all three of its records are held on CQ-0013/0014/0016 | `eval/gold/prohibited-uses.yaml` |
| Evaluation measures | not started — **draft thresholds to correct** at `review/seed/measures.seed.md` | `eval/measures.md` |
| Evaluation harness | **done** — S005, P5. Runs, and exits 3 by design | `tmk-harness` |
| Record templates | **done** — 7 record types, now schema-checked | `eval/templates/` |
| Record schemas | **done** — S004, ADR-0027 | `eval/schemas/` |
| Pass B worksheet | **done** — S004, prints 216 chunks (ADR-0022) | `tmk-worksheet` → `data/derived/` |
| Corpus reconnaissance | **done** — S004, s 43 costed | `tmk-recon` → `data/derived/` |
| Expert input guide | **done** — ADR-0014 | `eval/STAGE-0-INPUT-GUIDE.md` |
| Coverage and gap report | **done** — S005, P10 | `tmk-coverage` → `data/derived/reports/` |
| CI wiring | **done** — S005, P11, ADR-0018's split | `.github/workflows/harness.yml` |
| Intake workbook | **done** — S005, P7 | `tmk-workbook` → `data/derived/` |
| Transcription path | **done** — S005, P8; gated on the verdict S008 (ADR-0047, ADR-0048) | `tmk-transcribe` → `eval/gold/` |
| Parallel-track plan | **done** — ADR-0016 | `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` |
| Seed example set | **in review** — S007, ADR-0043. 178 left of 368; 190 promoted, 8 rejected, 139 never reached | `review/seed/` → `tmk-seed` |
| Seed review pack and workbook | **done** — S007, ADR-0044; regenerated S008 over the 178 that remain | `tmk-seed --pack --workbook` → `data/derived/` |
| Review round 1 | **done** — S008. 229 of 368 rows carried a verdict, plus an addendum settling 84 (ADR-0051, ADR-0052) | `review/returned/`, `review/decisions/` |
| Reconciliation path | **done** — S008, ADR-0049 | `tmk-reconcile` |
| Blocker and dependency report | **done** — S009, ADR-0053/0054 | `tmk-blockers` → `data/derived/reports/` |
| Review round 2 (scoped) | **rendered, not sent** — S009, ADR-0055. 10 decisions holding 168 records. **Superseded as the next action by the owner's S010 instruction**: no further expert round for now | `data/derived/stage0-blockers-review.xlsx` |

Target sizes from the roadmap: 100–300 recognised entities, 50–100 approved
concepts, 50–100 known relationships, 20–50 search questions, 20–50 AI retrieval
questions, expected reasoning results, and examples of conclusions the system must
not draw.

Content is expert-owned (CLAUDE.md rule 1). Agents build the templates, the
schemas and the harness — and, since S007, a **seed set of examples to correct**
rather than compose (ADR-0043). Nothing in `review/seed/` moves a row in this
table: a deliverable becomes *started* when a corrected record lands in
`eval/gold/` with a name against it. The full definition of done — including the checks the
harness will assert mechanically — is in `eval/STAGE-0-INPUT-GUIDE.md` §7.

The queue is not a list. Approval does not distribute over an interlinked set
(ADR-0048), so `tmk-blockers` reports it as the graph it is: **10 decisions on
the critical path, 12 records that need no decision at all, and 149 in the
ordinary queue.** `data/derived/reports/blockers.md` is the live version — this
board records only what has moved into `eval/gold/`.

**Stage 0 being the blocker does not mean the repo is blocked.** Which agent
work proceeds without expert content, and at which of five gates expert input
actually becomes required, is in `docs/roadmap/PARALLEL-TRACK-ROADMAP.md`
(ADR-0016). Only the last gate — full Stage 0 completion — stops the programme.
Track the packages there; record movement here only when a Stage 0 deliverable
row above changes.

## Stages 5, 6 and 9 — the draft, and what "partial" means here

S010, on the owner's instruction to stop waiting for the expert and build
something from what exists (ADR-0056). **Read `data/derived/reports/ontology.md`
rather than this section** — it is generated from the same run that builds the
graph and it will not go stale.

| Deliverable | Status | Where it lives |
|---|---|---|
| Ontology modules | **drafted, none approved** — 9 modules, 49 classes, OWL 2 RL | `ontology/draft/` |
| Relation dictionary | **generated** — 14 predicates, derived from 35 approved relationships, regeneration-checked | `ontology/draft/relations.ttl` |
| Ontology guide | **done** | `ontology/draft/GUIDE.md` |
| Knowledge graph | **built** — `tmk-graph --write --rules` | `graph/approved.ttl`, `graph/inferred.ttl` |
| SHACL shapes | **done** — 5 files, every shape with a violating fixture | `shapes/`, `tests/fixtures/shapes/` |
| Publication gate | **done** — 0 defects, 0 gaps, 29 notes | `tmk-shacl` |
| Competency queries | **partial** — 13 of 20 questions; 6 need Stages 7–8, 1 could be written | `queries/competency/` |
| CONSTRUCT rules | **written, both PENDING approval** | `queries/rules/` |
| Ontology status report | **done** — generated | `tmk-ontology-report` → `data/derived/reports/` |

**Why these are `partial` and not `done`, in one line each.** Stage 5 is a draft
nobody has approved. Stage 6 is built against that draft, and `candidates.nq` and
`superseded.nq` do not exist because there are no candidates and nothing has been
retired. Stage 9 has two rules and neither is an approved reasoning template,
which is what the stage actually requires.

**The largest gap the draft exposed**, and it was not on any list before:
`GroundOfRefusal`, `LegalTest`, `RelevantFactor` and `Exception` are declared and
**empty**. All 52 approved concepts are bare `tmk:LegalConcept`, because the gold
concept record has no type field and typing them is a legal judgement. It is one
pass over a list for someone who knows the domain, and it is what turns a flat
vocabulary into a hierarchy the later stages can generalise over.

**ADR-0010 is untouched.** Stage 2 has not started and nothing here brings it
closer: this work generated no candidate, ran no extractor, and measured no
recall. Modelling approved records is not extraction.

## The dashboard — not a stage, and worth a row anyway

S011, on the owner's instruction (ADR-0062). A static site at
<https://thomas-amann-ipaustralia.github.io/TM-Knowledge/> with two jobs: make
the ontology, vocabulary and graph legible to a trade marks expert, and put the
decisions waiting on the owner in front of them as a form they can answer.

| Deliverable | Status | Where it lives |
|---|---|---|
| The site | **done** — 9 pages, no framework, no CDN, no build step | `site/` |
| Site data generator | **done** — generated, drift-checked in CI | `tmk-dashboard` → `site/data/` |
| Publication | **done** — needs one repo setting (Pages source: GitHub Actions) | `.github/workflows/pages.yml` |
| Owner question queue | **done** — 13 asked, 4 parked, schema-validated | `review/questions/open-questions.yaml` |
| Answer round trip | **done** — form → issue → workflow → file | `tmk-ruling`, `.github/workflows/ruling.yml` |
| Recorded rulings | **none yet** — the queue has not been answered | `review/rulings/` |

**This is not the roadmap's review interface.** Release 1 names one, and that is
for triaging Stage 2 extraction candidates — terms, citations, clusters — none of
which exist. This one reviews nothing: it renders approved content and collects
the owner's decisions. When the Stage 2 review interface is built it is a
different tool with a different audience, and reusing this one for it would put
unapproved candidates on a public page.

**It restates and never derives** (ADR-0063). Every figure on it is a count of
something already committed; where the number needs the snapshot the site renders
the generated report instead of paraphrasing it. That is also why moving a record
without running `tmk-dashboard --write` fails CI.

## Stage 1 — inherited, and what is missing from it

Complete as data. Measured at `ingest/0.11.0` and `legislation/0.2.0`:

- Manual: 500 pages, 54 Parts, 2,460 chunks, 12,521 blocks, 2,717 provision
  edges, 519 case edges (411 distinct decisions), 418 internal refs.
- Legislation: 2 instruments, 763 provisions (TMA1995 316, TMR1995 447), 5,813
  numbered units.
- Join: 2,611 of 2,687 in-scope provision edges resolve (97%).
- 583 tests pass; both corpora validate and re-derive from stored raw.

Two roadmap deliverables exist as data but not as named artefacts: the **version
register** and the **source-quality report** (Q-04). If Stage 1 needs formal
sign-off, that is the gap, and it belongs upstream.

## Release view

The roadmap groups the stages into five releases. Useful when reporting progress
to anyone who does not think in stages.

| Release | Contains | Status |
|---|---|---|
| 1 — Automated discovery | parsing, YAKE, citation detection, entity matching, term clustering, review interface | parsing done upstream; rest not started |
| 2 — Vocabulary and knowledge graph | SKOS, ontology modules, relation extraction, provenance, RDF, SHACL, Fuseki | **partial** — SKOS, modules, provenance, RDF and SHACL all exist in draft over the s 43 pilot; relation *extraction* has not started (that is Stage 2/4) and no triple store is deployed |
| 3 — Search and AI retrieval | OpenSearch index, hybrid search, vocabulary expansion, graph traversal, evidence packages, citations | not started |
| 4 — Bounded reasoning | OWL 2 RL, impact analysis, consistency checks, approved SPARQL rules, explanations | **partial** — the profile is OWL 2 RL, impact analysis answers CQ-0017/0019, and every inference explains itself. The rules are **not approved**, which is the substance of the release |
| 5 — Continuous maintenance | change detection, incremental reprocessing, active learning, regression testing, monitoring | not started |

## Standing constraints on any stage

- Tier 3 outputs need expert approval regardless of measured accuracy (ADR-0008).
- Candidates never merge into approved artefacts without a recorded decision
  (ADR-0007).
- The pilot does not attempt to automate a final examination decision. Evaluative
  conclusions — "the evidence establishes acquired distinctiveness" — stay outside
  automated reasoning scope.

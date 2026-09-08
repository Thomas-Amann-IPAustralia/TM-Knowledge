# ROADMAP-STATUS — where each stage stands

The stage view of the programme. `ARCHITECTURE.md` holds the artefact view.
Update the affected row in the same session that moves a deliverable, and say so
in `HANDOFF.md`.

> **The board was reset on 2026-09-08 by ADR-0079 to ADR-0085.** Three gates that
> shaped every row below are gone: Stage 0 no longer blocks Stages 2-4
> (ADR-0083, supersedes ADR-0010), Tier 3 no longer gates output (ADR-0082,
> supersedes ADR-0008), and an agent may now author legal content stamped
> `unreviewed` rather than waiting for an expert (ADR-0079). Scope is the whole
> Manual, not section 43 (ADR-0081).
>
> **What this does and does not mean for "Stage 0 is the blocker".** It is not the
> blocker any more — nothing waits on it. It is also not *done*: the deliverables
> below are still short, and the honest reading is that they will now be filled
> by machine-authored content that no expert has validated. A row that reads
> "in band" from here on is counting `eval/gold/` and `authored/` **separately**,
> because summing them is the one thing ADR-0080 forbids.

Legend: **done** · **partial** · **not started** · **n/a here** (owned by
`manual-XtrACTor`)

Stage numbering is the roadmap's own, Stages 0–10. `docs/UPSTREAM.md` §6 summarises
it as "Stages 0–7" — that summary undercounts; see Q-01.

## Board

| Stage | Name | Status | Owner |
|---|---|---|---|
| 0 | Pilot selection and evaluation set | **partial — and no longer a blocker** (ADR-0083). 190 expert-signed records over all 8 types, harness 0 defects; `eval/gold/` now **frozen** at those 190 as the measurement yardstick (ADR-0080). The 178 held seed records are resolved by authoring rather than by an expert round, so the 10-decision critical path is gone (ADR-0084). **S016: the harness reads both stores** — `authored/` is checked on the same terms plus four of its own, and the completeness gate still counts the signed set alone, so a band met by unreviewed records cannot report Stage 0 finished (ADR-0090) | this repo |
| 1 | Ingest and structure source documents | **done** (4 of 6 named deliverables); consumed here since S004 — pinned, fetched and loaded | `manual-XtrACTor` |
| 2 | Candidate terminology and entities | **open, not started** — gate lifted 2026-09-08 (ADR-0083). Stack fixed (TextRank + YAKE + KeyBERT, spaCy NER as metadata, ADR-0019). **HANDOFF Q3 answered in full the same day it started blocking**: Gemini 3.8 Flash, credential in `GEMINI_API_KEY` (ADR-0087), and corpus text cleared to send (ADR-0088). Deterministic extraction stays preferred — now for cost as well as review debt (rule 7) | this repo |
| 3 | Controlled vocabulary (SKOS) | **open, not started** (ADR-0083) | this repo |
| 4 | Relationships, propositions, candidate rules | **open, not started** (ADR-0083) | this repo |
| 5 | Formalise the ontology | **partial, and unblocked** — nine OWL 2 RL modules drafted in `ontology/draft/`; nothing approved, so `ontology/` stays empty (ADR-0056, ADR-0057). The four concept classes now also fill from **authored** `concept_type` records, not only signed ones (ADR-0079 amends ADR-0071) — the 0-of-52 taxonomy is an agent's to fill. Whole-Manual scope means the class list stops being 30-of-49 empty for want of material (ADR-0081) | this repo |
| 6 | Populate and validate the knowledge graph | **partial** — S010, S012, S016. Graph built (16,405 source + 3,230 approved + 0 authored triples), SHACL gate **0 defects, 0 gaps, 29 notes**, against a *draft* TBox. S012: **all files committed** (ADR-0070) and `tmk-graph --check` fails on drift. **S016: a fourth named graph, `graph/authored.ttl`** — built from `authored/` by the same mapping, every node stamped `tmk:origin` and `tmk:reviewStatus`, an authored relationship typed `tmk:AuthoredAssertion` and never `tmk:ApprovedAssertion` (ADR-0091). Empty until something is authored, and the approved count rose by 284 because both stores now stamp their origin | this repo |
| 7 | Ontology-enhanced search | **not started** | this repo |
| 8 | Graph-aware AI retrieval | **not started** | this repo |
| 9 | Automated reasoning | **partial** — two CONSTRUCT rules. **RULE-0002 approved by the owner** (ADR-0068). **RULE-0001 stays PENDING and an agent may not approve it**: a rule's `approved-by` line is the same kind of artefact as a record's `approved_by`, and ADR-0079 does not license filling either. What changed is that its output is no longer *quarantined* — under ADR-0082 an unapproved rule's conclusions may be served, stamped `candidate` / `requiresHumanReview`, like any other unreviewed content. OQ-0019 becomes optional rather than blocking | this repo |
| 10 | Automated maintenance | **not started** | this repo |

## Stage 0 — no longer the blocker

**Stage 0 stopped being a gate on 2026-09-08.** ADR-0083 lifted ADR-0010, so
Stages 2-4 proceed whatever this section says. What remains true: 190 records a
named expert signed landed in S008, every record type is represented, the harness
runs over them with 0 defects, and `eval/gold/` is now **frozen** at exactly those
190 as the project's only uncontaminated measurement yardstick (ADR-0080).

The counts below are therefore counts of **signed** content and stay that way. The
shortfalls — entities at 55 of 100-300, search questions at 1 of 20-50, no
measures — are now filled by authored content in `authored/`, tracked separately
and never summed into these rows. **There is no pilot scope document and none is
owed**: the whole Manual is in scope and the boundary was withdrawn (ADR-0081).

| Deliverable | Status | Where it will live |
|---|---|---|
| Pilot area | **superseded** — s 43 is the first area worked, not a limit; whole Manual in scope (ADR-0081 amends ADR-0013) | `docs/DECISIONS.md` |
| Pilot scope (the boundary) | **withdrawn, not owed** — the boundary is gone and `eval/pilot-scope.md` will not be written. `tmk-boundary` and `data/derived/reports/boundary.md` are retired and must not be cited as current (ADR-0081, supersedes ADR-0022 and ADR-0072) | — |
| Competency-question catalogue | **partial** — 20 approved (S008); 4 seed drafts left | `eval/gold/competency-questions.yaml` |
| Gold-standard dataset | **partial** — 159 approved: 52 concepts (target met), 55 entities, 35 relationships, 10 retrieval questions, 6 reasoning expectations (target met), 1 search question | `eval/gold/` |
| Prohibited-use list | **partial** — 11 approved covering 5 of the 6 kinds; `stale_source` missing because all three of its records are held on CQ-0013/0014/0016 | `eval/gold/prohibited-uses.yaml` |
| Evaluation measures | not started — **draft thresholds to correct** at `review/seed/measures.seed.md` | `eval/measures.md` |
| Evaluation harness | **done** — S005, P5. Runs, and exits 3 by design | `tmk-harness` |
| Record templates | **done** — 8 record types, schema-checked; `concept-type.template.yaml` added S012 | `eval/templates/` |
| Record schemas | **done** — S004, ADR-0027; a ninth record type, `concept_type`, added S012 (ADR-0071) | `eval/schemas/` |
| Pass B worksheet | **done** — S004, prints 216 chunks (ADR-0022) | `tmk-worksheet` → `data/derived/` |
| Corpus reconnaissance | **done** — S004, s 43 costed | `tmk-recon` → `data/derived/` |
| Expert input guide | **done** — ADR-0014 | `eval/STAGE-0-INPUT-GUIDE.md` |
| Coverage and gap report | **done** — S005, P10 | `tmk-coverage` → `data/derived/reports/` |
| CI wiring | **done** — S005, P11, ADR-0018's split | `.github/workflows/harness.yml` |
| Intake workbook | **done** — S005, P7 | `tmk-workbook` → `data/derived/` |
| Transcription path | **done** — S005, P8; gated on the verdict S008 (ADR-0047, ADR-0048) | `tmk-transcribe` → `eval/gold/` |
| Parallel-track plan | **done** — ADR-0016 | `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` |
| Seed example set | **retired** — the 178 remaining are resolved by authoring, not by waiting; 190 promoted, 8 rejected and staying rejected (ADR-0084) | `review/seed/` → `authored/` |
| Seed review pack and workbook | **done** — S007, ADR-0044; regenerated S008 over the 178 that remain | `tmk-seed --pack --workbook` → `data/derived/` |
| Review round 1 | **done** — S008. 229 of 368 rows carried a verdict, plus an addendum settling 84 (ADR-0051, ADR-0052) | `review/returned/`, `review/decisions/` |
| Reconciliation path | **done** — S008, ADR-0049 | `tmk-reconcile` |
| Concept typing | **unblocked** — an agent now types the 52 (and everything the wider corpus adds), stamped `unreviewed`, into `authored/concept-types.yaml`. The workbook stays available for an expert who wants to correct in bulk (ADR-0079, ADR-0071) | `authored/concept-types.yaml` |
| Blocker and dependency report | **done** — S009, ADR-0053/0054 | `tmk-blockers` → `data/derived/reports/` |
| Review round 2 (scoped) | **not needed** — the 10 decisions holding 168 records are resolved by authoring instead (ADR-0084). The workbook stays on disk for an expert round if one resumes | `data/derived/stage0-blockers-review.xlsx` |

Target sizes from the roadmap: 100–300 recognised entities, 50–100 approved
concepts, 50–100 known relationships, 20–50 search questions, 20–50 AI retrieval
questions, expected reasoning results, and examples of conclusions the system must
not draw.

**Content is no longer expert-owned** (ADR-0079, amending CLAUDE.md rule 1).
Agents build the templates, the schemas and the harness *and* author the content,
stamped `unreviewed`, into `authored/`. Nothing in `authored/` moves a row in this
table: these rows count **signed** records only, and a deliverable becomes
*started* here when a record lands in `eval/gold/` with a person's name against
it. That is now a measure of expert engagement rather than of project progress,
and it is kept for exactly that reason. The full definition of done — including the checks the
harness will assert mechanically — is in `eval/STAGE-0-INPUT-GUIDE.md` §7.

The queue is not a list. Approval does not distribute over an interlinked set
(ADR-0048), so `tmk-blockers` reports it as the graph it is: **10 decisions on
the critical path, 12 records that need no decision at all, and 149 in the
ordinary queue.** `data/derived/reports/blockers.md` is the live version — this
board records only what has moved into `eval/gold/`.

**The five gates in `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` (ADR-0016) are
largely moot.** They described where expert input became required in a programme
that could not proceed without it. ADR-0079 and ADR-0083 removed that dependency:
expert input now *improves* content rather than *unblocking* it. The package list
in that document stays useful; its gating does not apply.
Track the packages there; record movement here only when a Stage 0 deliverable
row above changes.

## Stages 5, 6 and 9 — the draft, and what "partial" means here

S010, on the owner's instruction to stop waiting for the expert and build
something from what exists (ADR-0056). **Read `data/derived/reports/ontology.md`
rather than this section** — it is generated from the same run that builds the
graph and it will not go stale.

| Deliverable | Status | Where it lives |
|---|---|---|
| Ontology modules | **drafted, none approved** — 9 modules, 50 classes, OWL 2 RL | `ontology/draft/` |
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
| Publication | **done and live** — Pages source is GitHub Actions; deploying, and manually re-runnable from the Actions tab | `.github/workflows/pages.yml` |
| Owner question queue | **done** — 10 asked, 2 parked, 10 answered, schema-validated | `review/questions/open-questions.yaml` |
| Answer round trip | **done** — form → issue → workflow → file | `tmk-ruling`, `.github/workflows/ruling.yml` |
| Recorded rulings | **done** — one ruling (issue #12), applied; three further answers given by hand and recorded on the questions themselves | `review/rulings/`, `review/returned/` |

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

- ~~Tier 3 outputs need expert approval regardless of measured accuracy
  (ADR-0008).~~ **Superseded by ADR-0082.** Tier 3 is now a label and a review
  priority, not a gate. The replacement constraint: any surface that presents
  knowledge to a person must show its review status **at the point of use**, and
  a surface that cannot show it must not serve unreviewed content.
- Candidates never merge into approved artefacts without a recorded decision
  (ADR-0007). **Unchanged** — and `authored/` is not an approved artefact.
- **The programme does not attempt to automate a final examination decision.**
  Evaluative conclusions — "the evidence establishes acquired distinctiveness" —
  stay outside automated reasoning scope, and the eleven expert-approved
  prohibited-use records still stand. **Unchanged by ADR-0082**, which removed a
  review gate on knowledge and did not widen what the product may say. An agent
  may not widen it (ADR-0082 consequence 4).
- **Every authored record carries its envelope** — status, model, date, basis,
  evidence, reasoning. A record that cannot is not written (ADR-0079).

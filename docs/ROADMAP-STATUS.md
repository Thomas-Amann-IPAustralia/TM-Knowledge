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
| 0 | Pilot selection and evaluation set | **partial** — pilot area chosen (s 43, ADR-0013); apparatus built (S004); no expert content yet | this repo — **the blocker** |
| 1 | Ingest and structure source documents | **done** (4 of 6 named deliverables); consumed here since S004 — pinned, fetched and loaded | `manual-XtrACTor` |
| 2 | Candidate terminology and entities | **not started** — stack fixed (TextRank + YAKE + KeyBERT, spaCy NER as metadata, ADR-0019); blocked by ADR-0010 | this repo |
| 3 | Controlled vocabulary (SKOS) | **not started** | this repo |
| 4 | Relationships, propositions, candidate rules | **not started** | this repo |
| 5 | Formalise the ontology | **not started** | this repo |
| 6 | Populate and validate the knowledge graph | **not started** | this repo |
| 7 | Ontology-enhanced search | **not started** | this repo |
| 8 | Graph-aware AI retrieval | **not started** | this repo |
| 9 | Automated reasoning | **not started** | this repo |
| 10 | Automated maintenance | **not started** | this repo |

## Stage 0 — the blocker

The pilot **area** is settled: s 43 (ADR-0013). No Stage 0 content exists yet.
ADR-0010 holds that no Stage 2+ work starts before this is done.

| Deliverable | Status | Where it will live |
|---|---|---|
| Pilot area | **done** — s 43, ADR-0013 | `docs/DECISIONS.md` |
| Pilot scope (the boundary) | not started — awaiting owner | `eval/pilot-scope.md` |
| Competency-question catalogue | not started | `eval/competency-questions.md` |
| Gold-standard dataset | not started | `eval/gold/` |
| Prohibited-use list | not started | `eval/prohibited-uses.md` |
| Evaluation measures | not started | `eval/measures.md` |
| Evaluation harness | not started — P5, unblocked by P4 | `eval/` + `tests/` |
| Record templates | **done** — 7 record types, now schema-checked | `eval/templates/` |
| Record schemas | **done** — S004, ADR-0027 | `eval/schemas/` |
| Pass B worksheet | **done** — S004, prints 216 chunks (ADR-0022) | `tmk-worksheet` → `data/derived/` |
| Corpus reconnaissance | **done** — S004, s 43 costed | `tmk-recon` → `data/derived/` |
| Expert input guide | **done** — ADR-0014 | `eval/STAGE-0-INPUT-GUIDE.md` |
| Parallel-track plan | **done** — ADR-0016 | `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` |

Target sizes from the roadmap: 100–300 recognised entities, 50–100 approved
concepts, 50–100 known relationships, 20–50 search questions, 20–50 AI retrieval
questions, expected reasoning results, and examples of conclusions the system must
not draw.

Content is expert-owned (CLAUDE.md rule 1). Agents build the templates, the
schemas and the harness. The full definition of done — including the checks the
harness will assert mechanically — is in `eval/STAGE-0-INPUT-GUIDE.md` §7.

**Stage 0 being the blocker does not mean the repo is blocked.** Which agent
work proceeds without expert content, and at which of five gates expert input
actually becomes required, is in `docs/roadmap/PARALLEL-TRACK-ROADMAP.md`
(ADR-0016). Only the last gate — full Stage 0 completion — stops the programme.
Track the packages there; record movement here only when a Stage 0 deliverable
row above changes.

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
| 2 — Vocabulary and knowledge graph | SKOS, ontology modules, relation extraction, provenance, RDF, SHACL, Fuseki | not started |
| 3 — Search and AI retrieval | OpenSearch index, hybrid search, vocabulary expansion, graph traversal, evidence packages, citations | not started |
| 4 — Bounded reasoning | OWL 2 RL, impact analysis, consistency checks, approved SPARQL rules, explanations | not started |
| 5 — Continuous maintenance | change detection, incremental reprocessing, active learning, regression testing, monitoring | not started |

## Standing constraints on any stage

- Tier 3 outputs need expert approval regardless of measured accuracy (ADR-0008).
- Candidates never merge into approved artefacts without a recorded decision
  (ADR-0007).
- The pilot does not attempt to automate a final examination decision. Evaluative
  conclusions — "the evidence establishes acquired distinctiveness" — stay outside
  automated reasoning scope.

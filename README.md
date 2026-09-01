# TM-Knowledge

A structured knowledge system over the Australian trade marks examination corpus:
controlled vocabulary, ontology, knowledge graph, search, AI retrieval and bounded
automated reasoning — built on top of a deterministic snapshot of the Trade Marks
Manual of Practice and Procedure, the Trade Marks Act 1995 and the Trade Marks
Regulations 1995.

The programme is **automation-first but human-governed**. Machines extract,
cluster, link and propose. Experts define, approve and resolve exceptions. The
ontology formalises approved meaning; SHACL protects data quality; reasoning
operates only over governed knowledge.

## Status

**The apparatus is built and the content is not.** Everything an agent can build
for Stage 0 exists and runs; every remaining Stage 0 deliverable is expert
content that no amount of engineering substitutes for.

- **Stage 1 (ingest) is complete**, in a separate repo:
  [`manual-XtrACTor`](https://github.com/Thomas-Amann-IPAustralia/manual-XtrACTor)
  — 500 Manual pages / 2,460 chunks, 763 legislative provisions, joined at 97%
  coverage, extracted deterministically with no LLM in the pipeline. This repo
  pins a commit of it and reads it; it never re-extracts.
- **Stage 0 (pilot scope and evaluation set) is the blocker.** The pilot area is
  fixed (s 43). The schemas, the annotation worksheet, the evaluation harness,
  the coverage report and the intake workbook all exist. The gold set is empty.
- Stages 2–10 are this repo's work and have not started, deliberately: the first
  plausible extraction output becomes the standard by arriving first, which is
  what Stage 0 exists to prevent.

`docs/ROADMAP-STATUS.md` has the full board.

## Quickstart

```bash
pip install -e ".[test,intake]"
tmk-fetch-upstream    # the pinned corpus into data/upstream/ (~4s)
tmk-worksheet         # 216 chunks to annotate → data/derived/worksheet.md
tmk-workbook          # the intake workbook, EMPTY → data/derived/stage0-intake.xlsx
tmk-seed --pack --workbook   # the seed examples, for expert correction (ADR-0043)
tmk-harness           # every Stage 0 check. Exits 3: incomplete, by design
tmk-coverage          # the same, as a worklist → data/derived/reports/
pytest -q
```

`tmk-harness` exiting non-zero is the intended state, not a broken checkout: **0**
sound and complete, **1** something that arrived is wrong, **3** sound but Stage 0
has not arrived. See ADR-0018 and ADR-0030.

## Repository layout

```
CLAUDE.md          operating rules — read first, every session
docs/              all documentation (start at docs/HANDOFF.md)
eval/              Stage 0: pilot scope, competency questions, gold set, harness
data/              pinned upstream snapshot (not committed)
src/               tm_knowledge Python package
review/            machine-generated candidates awaiting human decision
  seed/            Stage 0 example records, written to be corrected — not content
vocab/             approved SKOS controlled vocabulary
ontology/          approved RDF/RDFS/OWL 2 RL modules
graph/             generated RDF, by named graph
shapes/            SHACL shapes
queries/           SPARQL queries and CONSTRUCT rules
tests/             pytest, SPARQL regression, retrieval benchmarks
.github/           CI: the harness on every push
```

Every directory has a README saying what belongs in it and what does not.

## Documentation

| File | Read it for |
|---|---|
| `CLAUDE.md` | The rules. Loaded into every agent session |
| `docs/HANDOFF.md` | **Current state and the next action.** Start here |
| `docs/DECISIONS.md` | What has been decided and why (append-only ADRs) |
| `docs/QUIRKS.md` | Traps, and where the roadmap and reality disagree |
| `docs/ARCHITECTURE.md` | Intended shape of the system; what lives where |
| `docs/IDENTIFIERS.md` | Refs, IRI minting, naming. Read before writing any ID |
| `docs/ROADMAP-STATUS.md` | Stage-by-stage status board |
| `docs/GLOSSARY.md` | Domain and project terms |
| `docs/UPSTREAM.md` | The upstream data contract — record shapes and the join |
| `docs/roadmap/AUTOMATION-FIRST-ROADMAP.md` | The full programme, Stages 0–10 |
| `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` | What proceeded while Stage 0 content was pending, and the gates where expert input becomes required |
| `eval/STAGE-0-INPUT-GUIDE.md` | **If you are the domain expert, start here.** What to supply and in what shape |

## Working here

This repo is worked on largely by Claude Code sessions in ephemeral containers.
The documentation set exists so that each session starts informed rather than
guessing: `HANDOFF.md` carries the baton, `DECISIONS.md` prevents relitigating
settled questions, `QUIRKS.md` prevents rediscovering the same traps.

If you are a human: the same three files are the fastest way back into context.

If you are an agent: read `CLAUDE.md` in full first. Two rules matter more than
the rest — **never invent legal content**, and **never re-derive what upstream
already extracted**.

## Licence

MIT. See `LICENSE`.

The source materials are Commonwealth of Australia publications and carry their
own terms; this licence covers the code and structure in this repository, not the
underlying legal texts.

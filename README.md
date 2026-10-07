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
- **There is no pilot area any more.** The repo worked section 43 alone until
  2026-09-08, when the owner withdrew the boundary: *"I would like to completely
  remove the s43 barrier."* All 54 Parts are in scope, there is no exclusion rule
  anywhere, and section 43 is the area worked **first** rather than a fence
  (ADR-0081, ADR-0096).
- **An agent now authors legal content, and never launders it.** Also 2026-09-08:
  definitions, concept types, relationships and readings are written by a machine
  and stamped `unreviewed`, with the model that wrote them, the passages they
  rest on, and `approved_by` left empty. `eval/gold/` is frozen at the 190
  records an expert signed so that it stays usable as an independent yardstick
  (ADR-0079, ADR-0080). **Nothing in `authored/` has been read by a trade marks
  expert.**
- Stages 2–10 are this repo's work. Stages 2–4 opened on 2026-09-08 (ADR-0083);
  the deterministic passes run first and are measured against the frozen 190.

`docs/ROADMAP-STATUS.md` has the full board.

### 🗺️ [The Trade Marks Manual Map](https://thomas-amann-ipaustralia.github.io/TM-Knowledge/)

The site for examiners (ADR-0118): a short tour of why an ontology helps, the map at
three levels of detail (kinds of idea → ideas → the text they rest on), *Ask the
Manual* with each question's ideas, connections and passages drawn hop by hop, and
what a rewrite of any Manual page would touch. Everything machine-written says so.
Built from this repository and the pinned snapshot on every push (`site/README.md`).

The owner's workbench — the former dashboard: decisions, reports and the questions
waiting on the owner — is kept at `/workbench/` (`site/workbench/README.md`).

## Quickstart

```bash
pip install -e ".[test,intake]"
tmk-fetch-upstream    # the pinned corpus into data/upstream/ (~4s)
tmk-worksheet         # 216 chunks to annotate → data/derived/worksheet.md
tmk-workbook          # the intake workbook, EMPTY → data/derived/stage0-intake.xlsx
tmk-seed --pack --workbook   # the seed examples, for expert correction (ADR-0043)
tmk-transcribe FILE --write  # a marked-up workbook back in — approved rows only
tmk-reconcile FILE --write   # record the round, retire the seed copies it settled
#   both take --addendum for a decision that arrived as words, not as cells
tmk-harness           # every Stage 0 check. Exits 3: incomplete, by design
tmk-coverage          # the same, as a worklist → data/derived/reports/
tmk-blockers          # what is holding the gold set, and what each decision frees
tmk-seed --only "$(tmk-blockers --ids)" --pack PACK --workbook BOOK
#   a review round scoped to the records on the critical path (ADR-0055)
python3 -m pytest -q  # `python3 -m`, not bare `pytest`, in a container (QUIRKS Q-29)

# The pipeline (ADR-0110, ADR-0111) — see docs/QUOTE.md before spending
tmk-bulk links --write                # free: which passages name which concept, candidate pairs
tmk-bulk run relate --dry-run         # what a run would cost; spends nothing
tmk-bulk run relate --limit 3 --confirm   # a smoke run: cached, capped at config.SPEND_CAP_USD
tmk-bulk run relate --confirm --write     # write what passed the checks (from the cache: free)
tmk-bulk spend                        # recorded spend against the cap
tmk-bulk quote --write                # price the full runs from what was measured

tmk-explorer --write              # the examiner site's data → site/data/ (needs the snapshot)
tmk-dashboard --write             # the workbench's data → site/workbench/data/
python3 -m http.server -d site 8000   # then open http://localhost:8000
#   neither is committed — Pages rebuilds both on deploy (ADR-0112, ADR-0117)
```

`tmk-harness` exiting non-zero is the intended state, not a broken checkout: **0**
sound and complete, **1** something that arrived is wrong, **3** sound but Stage 0
has not arrived. See ADR-0018 and ADR-0030.

## Repository layout

```
CLAUDE.md          operating rules — read first, every session
docs/              all documentation (start at docs/HANDOFF.md)
eval/              Stage 0: competency questions, the frozen gold set, harness
authored/          legal content a machine wrote — validated by nobody
data/              pinned upstream snapshot (not committed)
src/               tm_knowledge Python package
review/            machine-generated candidates awaiting human decision
  candidates/      extraction output: proposals with a score, never judgements
  seed/            Stage 0 example records, written to be corrected — not content
  returned/        what an expert handed back, unmodified — never edited
  decisions/       what each returned artefact was taken to mean
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

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

**A working demonstrator for a pitch** (ADR-0109, ADR-0110): an ontology over the
whole Manual, "Ask the Manual" beside plain search, a measurement of what the
ontology adds, and a pitch pack. The scope and its finish line are in `CLAUDE.md`
§0; where things stand is in `docs/HANDOFF.md`, and what the graph holds, counted,
is in `data/derived/reports/ontology.md`.

- **Ingest is complete**, in a separate repo:
  [`manual-XtrACTor`](https://github.com/Thomas-Amann-IPAustralia/manual-XtrACTor)
  — 500 Manual pages / 2,460 chunks, 763 legislative provisions, extracted
  deterministically with no LLM in the pipeline. This repo pins a commit of it and
  reads it; it never re-extracts. Each answer names the compilation of the Act it
  read.
- **The whole Manual is in scope.** The repo worked section 43 alone until
  2026-09-08, when the owner withdrew the boundary (ADR-0081). Some identifiers and
  signed records still carry that history (the concept scheme's IRI is
  `scheme-s43`); the scope does not.
- **A machine wrote most of the content, and says so.** Concepts, their kinds,
  relationships, definitions and corrections are written by a model or an agent
  session and stamped `unreviewed`, with who wrote them, when, and the passages
  they rest on, quoted; `approved_by` stays empty (ADR-0079). `eval/gold/` is
  frozen at the 190 records an expert signed, the one independent yardstick
  (ADR-0080). **Nothing in `authored/` has been read by a trade marks expert**;
  examiners review the whole when it ships (ADR-0120).
- **The IRIs are names, not addresses.** Every node is named under
  `https://data.ipaustralia.gov.au/tmk/` because RDF needs a base; nothing is
  published there and nothing dereferences. Which address the project may use is
  an open question for the owner (OQ-0008).

`docs/ROADMAP-STATUS.md` has the stage-by-stage board.

### 🗺️ [The Trade Marks Manual · proof of concept](https://thomas-amann-ipaustralia.github.io/TM-Knowledge/)

The site for examiners (ADR-0118), outcomes first and the ontology last (ADR-0145): what
the proof of concept does today (*Ask the Manual*, what a change would touch, the
customer explanation preview on invented matters), what it could do, the rules as code
behind it, and the ontology and the standards it is stored in. Everything machine-written
says so, and every standard is explained in plain words.
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
ontology/          RDF/RDFS modules, all still draft (no OWL profile, ADR-0134)
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
the rest — **author, but never launder** (what a machine wrote is never mistaken
for what a person signed), and **never re-derive what upstream already
extracted**.

## Licence

MIT. See `LICENSE`.

The source materials are Commonwealth of Australia publications and carry their
own terms; this licence covers the code and structure in this repository, not the
underlying legal texts.

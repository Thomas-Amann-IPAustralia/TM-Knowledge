# src/ — pipeline code

All Python lives here as the `tm_knowledge` package. Built in S004: refs,
provenance, the pin and fetch, the loader, and the Stage 0 apparatus. The rest
is still a sketch (ADR-0029).

```
src/tm_knowledge/
  __init__.py
  config.py       the base IRI and the snapshot paths — the ONLY place the base lives
  refs.py         ref parsing/validation, IRI minting, candidate ids, id allocation
                  — the ONLY place IRIs are constructed (docs/IDENTIFIERS.md §2)
  provenance.py   the block every generated record must carry (ADR-0011)
  upstream/       reading the pinned snapshot
    pin.py        the pin, the receipt, the tree digest — refuses a drifted snapshot
    fetch.py      `tmk-fetch-upstream`: bare clone → working data/upstream/
    records.py    typed page / chunk / provision / unit, round-trip faithful
    loader.py     the one door to the corpus, and the join
  authored/       reading authored/ — and refusing a record that cannot say who wrote it
  stage0/         the evaluation apparatus and the passes that fill it
    schemas.py    validation for the eight Stage 0 record types; where the refs are
    goldset.py    reading eval/gold/ — and refusing to skip a file it cannot name
    intake.py     the workbook column layout, derived from the schemas — one copy
    harness.py    `tmk-harness`: the checks, and the completeness gate (ADR-0018)
    coverage.py   `tmk-coverage`: the gap worklist — reports gaps, never fills them
    blockers.py   `tmk-blockers`: who is waiting on whom, and which decision frees most
    recon.py      `tmk-recon`: derived counts about the corpus, or one provision in it
    worksheet.py  `tmk-worksheet`: the Pass B worksheet, and the two selectors
    concepts.py   `tmk-concepts`: concept candidates across all 54 Parts, deterministic
    typing.py     `tmk-typing`: every concept laid out for sorting into the four groups
    workbook.py   `tmk-workbook`: the intake workbook, with no example rows
    transcribe.py `tmk-transcribe`: workbook in, validated records out
    cli.py        the commands above
  candidates/     Stage 2–4 candidate generation — not yet; ADR-0010 was superseded
                  by ADR-0083 and `stage0/concepts.py` is the first pass of it
  vocabulary/     Stage 3 clustering and SKOS emission — not yet
  graph/          Stage 6 RDF emission and named-graph assembly — not yet
  validate/       SHACL runs and validation reporting — not yet
  retrieval/      Stages 7–8 index build, query expansion, evidence packages — not yet
```

## Commands

```bash
pip install -e .            # then, in this order:
tmk-fetch-upstream          # pinned snapshot into data/upstream/ (needs network)
tmk-fetch-upstream --verify # commit, counts and tree digest — no network
tmk-recon                   # every provision the Manual cites, costed → data/derived/reports/
tmk-recon --provision X     # one area, the way this ran before the boundary went
tmk-concepts --write        # concept candidates, all 54 Parts → review/candidates/
tmk-typing --write          # every concept laid out for sorting → data/derived/
tmk-worksheet --provision X # the Pass B worksheet for one area → data/derived/
tmk-harness                 # the Stage 0 harness. Exits 3 today, by design
tmk-coverage                # the gap worklist → data/derived/reports/
tmk-blockers                # the review queue as a graph → data/derived/reports/
tmk-blockers --ids          # just the record ids on the critical path
tmk-workbook                # the intake workbook → data/derived/ (needs [intake])
tmk-transcribe FILE         # a filled workbook → eval/gold/. Dry run unless --write
python3 -m pytest -q        # snapshot-marked tests skip without a fetch (Q-29)
```

`tmk-harness` is the one whose exit code carries meaning: **0** sound and Stage 0
complete, **1** a defect — something that arrived is wrong — and **3** sound but
Stage 0 incomplete, which is today's expected state. CI passes
`--allow-incomplete` to forgive 3 and never 1 (ADR-0018).

## Rules

- **One IRI minter.** No other module concatenates a base IRI. A round-trip test
  (`ref → IRI → ref`) ships with it.
- **Never mutate upstream records.** Load them, key on them, emit new records
  beside them. `extraction` and `certainty` pass through verbatim and never merge
  into this repo's `confidence` (ADR-0011).
- **Every emitted record carries provenance** — method, model and version,
  confidence, source ref, span, source content hash, review status, created_at.
  A record without a source span is a bug, not a low-confidence result.
- **Candidates are written to `review/`, never to `vocab/`, `ontology/` or
  `graph/`** (ADR-0007).
- **Determinism first.** Regex, structural traversal and lookups before models.
  When a model is used, constrain the output schema and require evidence spans;
  a model that cannot cite the passage returns `uncertain`.
- **Re-runs are idempotent.** Candidate ids are content-addressed
  (`docs/IDENTIFIERS.md` §3), so unchanged input produces no new records. A new
  id means something actually changed.
- **Fail loud.** Ambiguity is recorded and queued, never silently resolved. A
  gold file whose name is not recognised stops the harness rather than being
  skipped — a file silently ignored is a set of expert judgements that did not
  count.
- **Report a gap; never close one.** `coverage.py` names every empty judgement
  field and proposes nothing for any of them (guide §9, CLAUDE.md rule 1).

## Conventions

Python 3.11+, matching upstream. `pytest` in `tests/`. Type hints on public
functions. Match the sibling repo's style where it has an opinion — the same
people read both.

Package directories document themselves in their `__init__.py` docstring rather
than in a `README.md` (ADR-0029). A package whose purpose is not stated there is
the bug.

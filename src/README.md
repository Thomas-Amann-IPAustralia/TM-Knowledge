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
  stage0/         the evaluation apparatus (container only — no legal content)
    schemas.py    validation for the eight Stage 0 record types
    recon.py      `tmk-recon`: derived counts about a candidate pilot area
    worksheet.py  `tmk-worksheet`: the Pass B annotation worksheet (ADR-0022)
    cli.py        the two commands above
  candidates/     Stage 2–4 candidate generation — NOT YET, and blocked by ADR-0010
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
tmk-recon                   # derived counts about s 43 → data/derived/reports/
tmk-worksheet               # the Pass B worksheet → data/derived/
pytest -q                   # snapshot-marked tests skip without a fetch
```

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
- **Fail loud.** Ambiguity is recorded and queued, never silently resolved.

## Conventions

Python 3.11+, matching upstream. `pytest` in `tests/`. Type hints on public
functions. Match the sibling repo's style where it has an opinion — the same
people read both.

Package directories document themselves in their `__init__.py` docstring rather
than in a `README.md` (ADR-0029). A package whose purpose is not stated there is
the bug.

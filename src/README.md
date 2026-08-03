# src/ — pipeline code

Empty. All Python lives here as the `tm_knowledge` package:

```
src/tm_knowledge/
  __init__.py
  refs.py         upstream ref parsing/validation and IRI minting — the ONLY place
                  IRIs are constructed (docs/IDENTIFIERS.md §2)
  loader.py       read data/upstream/ into records, preserving extraction/certainty
  candidates/     Stage 2–4 candidate generation (yake, entity rules, relations)
  vocabulary/     Stage 3 clustering and SKOS emission
  graph/          Stage 6 RDF emission and named-graph assembly
  validate/       SHACL runs and validation reporting
  retrieval/      Stages 7–8 index build, query expansion, evidence packages
```

Nothing is built yet. The three pieces worth writing first, because they carry no
legal content and unblock everything else, are `refs.py`, `loader.py` and the
evaluation harness (`eval/README.md`).

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

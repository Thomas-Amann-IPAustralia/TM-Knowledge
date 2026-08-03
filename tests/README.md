# tests/ — pytest, SPARQL regression, retrieval benchmarks

Empty. Nothing to run yet — there is no code.

```
tests/unit/            refs, IRI round-trip, loader, candidate generation
tests/shapes/          each SHACL shape fires on a fixture that violates it
tests/regression/      SPARQL queries with asserted results
tests/prohibited/      the system does NOT produce the outputs in eval/prohibited-uses.md
tests/benchmark/       retrieval and search metrics over the gold set
tests/fixtures/        small hand-built records — never a copy of the snapshot
```

## The first tests to exist

The evaluation harness, running the gold set, **failing**. That is the intended
first output of this repo (ADR-0010), not a placeholder to be replaced by real
work later — it *is* the work that makes everything after it measurable.

## Non-obvious requirements

- **`tests/prohibited/` is not optional.** The roadmap requires examples of
  conclusions the system must not draw, and they are as important as the positive
  cases. A system that scores well on recall while occasionally producing a
  prohibited conclusion has failed.
- **Ref round-tripping.** `ref → IRI → ref` must be lossless, including
  parentheses in unit refs like `TMA1995/s41(3)(a)`. Some RDF tooling will
  percent-encode them; the test is what catches it (`docs/IDENTIFIERS.md` §2).
- **Join integrity.** A chunk's `provisions[].id` must still equal a provision
  `ref` with no transformation, after every transform this repo applies. It is the
  most valuable property inherited from upstream and the easiest to break by
  accident.
- **Trust metadata survives.** Assert that `extraction` and `certainty` come out
  of the pipeline exactly as they went in, and never merged into `confidence`
  (ADR-0011).
- **Fixtures are hand-built and small.** Do not vendor snapshot files into
  `tests/fixtures/` — that is a second copy of the corpus with no pin (ADR-0004).

## Benchmarks are tests with thresholds

`tests/benchmark/` reports metrics *and* fails below the thresholds in
`eval/measures.md`. A benchmark that only prints numbers gets ignored within two
sessions.

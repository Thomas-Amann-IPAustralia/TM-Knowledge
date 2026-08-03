# queries/ — SPARQL

**Roadmap Stages 6 and 9.** Empty.

```
queries/competency/    one query per competency question in eval/
queries/rules/         approved CONSTRUCT rules — explicit derivations
queries/regression/    queries whose results are asserted in tests/
queries/reports/       coverage, review-queue depth, staleness, quality dashboard
```

## `queries/competency/` is the link to Stage 0

Each competency question that is answerable as a graph query gets a query here,
named for its id (`CQ-007.rq`). This is how the graph is measured rather than
admired: if a question has no query and no query has a question, one of the two is
wrong.

## `queries/rules/` — derivations are approvals

Every `CONSTRUCT` rule is an approved reasoning template (roadmap Stage 9: experts
approve every reasoning template before deployment). Each rule file carries, in a
header comment:

- the rule's id and what it derives;
- who approved it and when;
- the test that proves it fires correctly;
- the test that proves it does **not** fire on the near-miss case.

Rules write into `graph/inferred.nq` and nowhere else. Output must be traceable
back to its source facts and to the rule itself.

## Reasoning stays bounded

Classification, relationship propagation through the concept hierarchy, impact
analysis when a provision changes, consistency checking, and simple procedural
validation. Evaluative conclusions — "the evidence establishes acquired
distinctiveness" — stay outside automated reasoning scope, and the prohibited-use
tests exist to keep them there.

## Conventions

`.rq` files. Prefixes from `docs/IDENTIFIERS.md` §2, declared in full — no
implicit bindings. Query the named graph you mean explicitly; a query that
accidentally spans `candidates` and `approved` produces confident nonsense.

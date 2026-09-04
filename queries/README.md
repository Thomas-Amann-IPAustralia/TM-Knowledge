# queries/ — SPARQL

**Roadmap Stages 6 and 9.** Written and running: `tmk-ask`.

```
queries/competency/    13 queries, one per answerable competency question
queries/rules/         2 CONSTRUCT rules — both PENDING approval
queries/regression/    does not exist yet; the assertions live in tests/unit/
queries/reports/       does not exist yet; tmk-ontology-report does this job
```

13 of the 20 competency questions have a query. One more (CQ-0010) could and does
not. The remaining six are search and retrieval questions, which a graph query
cannot answer at all — a search question needs a ranked index (Stage 7) and a
retrieval question needs a generated answer over retrieved passages (Stage 8).
`tmk-ask` reports those two categories separately, because counting them as
coverage gaps would report a shortfall against work that is deliberately five
stages away.

## `queries/competency/` is the link to Stage 0

Each competency question that is answerable as a graph query gets a query here,
named for its id (`CQ-0017.rq`). This is how the graph is measured rather than
admired: if a question has no query and no query has a question, one of the two is
wrong. Both directions are checked — `tmk-ask` reports the first,
`tests/unit/test_competency_queries.py` refuses the second.

Every query carries a `limits:` header saying what it does **not** answer, and
a file without one is refused rather than run. That is the field that does the
work: a query returning rows always looks like an answer.

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

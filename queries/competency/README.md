# queries/competency/ — one query per competency question

Named for the question: `CQ-0017.rq` answers `CQ-0017`. That naming is the link
to Stage 0 and it is checked — `tmk-ask` reports questions with no query, and
`tests/unit/test_competency_queries.py` refuses a query naming a question the
gold set does not hold.

## The header is required

```
# question: CQ-0017
# answers:  the question, restated
# limits:   what this query does NOT answer
```

`tm_knowledge.ontology.ask` refuses a file missing any of the three.

**`limits` is the one that matters.** A query that returns rows always looks
like an answer. The limits line is the only place the query says what it has not
established — that CQ-0017 measures reviewing *effort* and not reviewing
*outcome*, that CQ-0019 finds recorded dependencies and not subject matter, that
CQ-0023's most important row is a blank one. A thin limits line fails a test on
purpose.

## Conventions

- **Name the graph you mean.** `GRAPH tmkg:source { … }`. A query that
  accidentally spans `candidates` and `approved` produces confident nonsense,
  and a test asserts every file names its graph.
- **Full IRIs for ref-addressed nodes.** `TMM/Part29/1#1` has slashes and a hash
  in it, so it cannot be a prefixed local name. Write
  `<https://data.ipaustralia.gov.au/tmk/ref/TMM/Part29/1%231>`; `ask.py` rebases
  the text when `TMK_BASE_IRI` differs.
- **Prefixes declared in full.** No implicit bindings.
- **`OPTIONAL` where a blank row is the answer.** CQ-0023 exists to show that
  the passage stating a proposition cites no decision at all. An inner join
  would have hidden that by returning only the rows that had cases.

## What must not go here

A query that answers a question no one approved; a query with no limits line; a
query that reaches an evaluative conclusion. CQ-0012 is the model for the last:
the question is whether a connotation is strong enough to warrant a ground, and
the query returns the three prohibited outputs that would answer it.

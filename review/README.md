# review/ — candidates awaiting a human decision

Empty. Everything the machines propose lands here and stays here until a person
decides. This directory is the boundary that ADR-0007 exists to protect: nothing
moves from `review/` into `vocab/`, `ontology/` or `graph/` without a recorded
decision.

```
review/candidates/terms/          Stage 2 — YAKE keyphrases, new entity proposals
review/candidates/citations/      Stage 2 — unresolved and ambiguous citations
review/candidates/clusters/       Stage 3 — proposed synonym groups and hierarchy edges
review/candidates/relations/      Stage 4 — relationships, propositions, candidate rules
review/decisions/                 the record of what was approved, rejected or deferred
```

## What belongs here

Any machine output that is not Tier 1, plus every Tier 3 output regardless of
confidence (ADR-0008). Each candidate carries method, model and version,
confidence, the exact supporting span, the source `content_hash`, and
`review_status`.

Upstream's own review-queue material belongs here too — in particular the
`certainty: "ambiguous"` provision edges, which upstream deliberately declined to
resolve and which must not be auto-resolved here either (Q-07).

## What does not

Approved knowledge. Anything an agent decided was "obviously fine". Records
without a supporting span.

## Decisions are data

`review/decisions/` is the audit trail: what was approved, by whom, when, and why
the rejections were rejected. It is not paperwork — Stage 10 active learning
consumes it. Accepted entity labels become `EntityRuler` patterns, rejected terms
become negative examples, corrected relationships become training data, and
recurring decisions become deterministic rules. A decision recorded only in a
person's memory cannot do any of that.

Rejections are as valuable as approvals; keep them.

## Reading a candidate

Never as fact. A candidate in a prompt, a report or an evidence package must be
labelled as unapproved. If that distinction is inconvenient somewhere, the
inconvenience is the point.

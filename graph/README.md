# graph/ — the generated knowledge graph

**Roadmap Stage 6.** Empty.

**Everything here is generated.** Given the pinned upstream snapshot, the approved
inputs in `vocab/` and `ontology/`, and the code in `src/`, a rebuild produces the
same graph. Hand-editing RDF in this directory breaks that guarantee and is
prohibited — fix the inputs or the generator instead.

## Named graphs

The separation is the governance mechanism (ADR-0007). Machine suggestions must
never become indistinguishable from approved knowledge; if they mix once, no later
audit can unmix them.

```
graph/source.nq        assertions derived deterministically from the snapshot
graph/candidates.nq    machine-extracted, unapproved  (mirrors review/)
graph/approved.nq      expert-approved assertions
graph/inferred.nq      produced by reasoning — never authored directly
graph/superseded.nq    retired assertions, kept for audit and point-in-time queries
```

`.nq` because named graphs must survive serialisation. Use `.ttl` only for
single-graph files a human is expected to read.

## Every assertion carries

Exact source passage · source version and `content_hash` · extraction method ·
confidence · review status · reviewer where applicable · creation date ·
applicable date range (ADR-0011).

Inferred assertions additionally identify the source facts, the axiom or rule that
produced them, the date of inference, and whether human review is required. An
inference that cannot explain itself does not get published.

## Publication gate

`shapes/` runs before anything is published. Validation failures that cannot be
corrected deterministically go to a human — they are not suppressed, and they are
not fixed by loosening the shape.

## Staleness

An assertion whose `source_content_hash` no longer matches the pinned snapshot is
stale: the passage under it moved. Stale assertions return to review rather than
being carried forward. This check is the whole mechanism behind Stage 10
incremental reprocessing.

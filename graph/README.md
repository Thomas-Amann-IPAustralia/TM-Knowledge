# graph/ — the generated knowledge graph

**Roadmap Stage 6.** Built, against a **draft** ontology (`ontology/draft/`).
`tmk-graph --write --rules`.

**Everything here is generated.** Given the pinned upstream snapshot, the approved
inputs in `vocab/` and `ontology/`, and the code in `src/`, a rebuild produces the
same graph. Hand-editing RDF in this directory breaks that guarantee and is
prohibited — fix the inputs or the generator instead.

## Named graphs

The separation is the governance mechanism (ADR-0007). Machine suggestions must
never become indistinguishable from approved knowledge; if they mix once, no later
audit can unmix them.

```
graph/source.ttl       assertions derived deterministically from the snapshot   NOT COMMITTED
graph/approved.ttl     expert-approved assertions                               committed
graph/inferred.ttl     produced by the candidate rules — never authored         committed
graph/dataset.nq       all of the above as quads                                NOT COMMITTED
graph/candidates.nq    machine-extracted, unapproved  (mirrors review/)         does not exist
graph/superseded.nq    retired assertions, kept for audit                       does not exist
```

`candidates` does not exist because no Stage 2 run has happened (ADR-0010) and
there are therefore no candidates. `superseded` does not exist because nothing
has been retired.

**Why `.ttl` and not `.nq` for the three that exist.** Each is a single named
graph, and this README already reserves `.ttl` for single-graph files a human
reads — a reviewer reading `approved.ttl` should not have to parse N-Quads.
`dataset.nq` is the quad form, and it is generated for tools that want it.

**What is committed, and why the split** (ADR-0060). `approved.ttl` and
`inferred.ttl` are this repo's own work: small enough to read, and a diff of
`approved.ttl` is a diff of what a reviewer changed. `source.ttl` and
`dataset.nq` are not committed — they restate the pinned upstream corpus, and
putting 6.5MB of it in this history is `data/upstream/` by another route, which
is what ADR-0004 exists to prevent. Both rebuild in one command.

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

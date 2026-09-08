# graph/ — the generated knowledge graph

**Roadmap Stage 6.** Built, against a **draft** ontology (`ontology/draft/`).
`tmk-graph --write --rules`, and `tmk-graph --rules --check` to prove what is
committed here is what a build produces.

**Everything here is generated.** Given the pinned upstream snapshot, the approved
inputs in `vocab/` and `ontology/`, and the code in `src/`, a rebuild produces the
same graph. Hand-editing RDF in this directory breaks that guarantee and is
prohibited — fix the inputs or the generator instead.

## Named graphs

The separation is the governance mechanism (ADR-0007). Machine suggestions must
never become indistinguishable from approved knowledge; if they mix once, no later
audit can unmix them.

```
graph/source.ttl       assertions derived deterministically from the snapshot   committed
graph/approved.ttl     expert-approved assertions                               committed
graph/inferred.ttl     produced by the CONSTRUCT rules — never authored         committed
graph/dataset.nq       all of the above as quads                                committed
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

**All four are committed** (ADR-0070, supersedes ADR-0060). The owner ruled on
OQ-0005: *"Store everything, so the graph can be read without building it."* It
costs about 6.5MB. `data/upstream/` stays out under ADR-0004 and that is not in
tension: the snapshot is another repository's corpus, and this is a derivation
of it — the same line `data/derived/` already draws.

**A committed generated file can go stale, and a stale one is worse than an
absent one** because it reads as current. So `tmk-graph --rules --check` rebuilds
into a temporary directory and compares bytes, CI runs it, and
`tests/unit/test_ontology_build.py::test_the_committed_graph_matches_a_rebuild`
runs it too. If it fails, run `tmk-graph --write --rules` and commit the result;
do not hand-edit.

**`dataset.nq` is written sorted, and that is load-bearing.** rdflib's Turtle
serialiser sorts, its N-Quads serialiser does not — it emits in set-iteration
order, which moves with `PYTHONHASHSEED`, so two builds of an identical dataset
produced two different 5MB files. Uncommitted, nobody noticed; committed, it
would have put a 5MB diff in the history on every rebuild, signifying nothing.
Line order carries no meaning in N-Quads, so sorting canonicalises without
changing what the file says (Q-42).

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

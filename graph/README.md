# graph/ — the generated knowledge graph

**Roadmap Stage 6.** Built, against a **draft** ontology (`ontology/draft/`).
`tmk-graph --write --rules`, and `tmk-graph --rules --check` to prove what is
committed here is what a build produces.

**Everything here is generated.** Given the pinned upstream snapshot, the approved
inputs in `vocab/` and `ontology/`, and the code in `src/`, a rebuild produces the
same graph. Hand-editing RDF in this directory breaks that guarantee and is
prohibited — fix the inputs or the generator instead.

## What the source graph holds

**Every Manual passage any record cites, plus its page-mates, plus every chunk
carrying an `ambiguous` provision edge** (ADR-0097). Not "chunks citing section
43", which is what it held from S010 until 2026-09-09 — that was the boundary
rule, and the owner withdrew the boundary (ADR-0081).

The rule has no provision in it. It selects on what this repository has said
something about, so it grows as knowledge is authored and never needs
re-deciding: authoring a concept about Part 22 puts Part 22's passages in the
graph with no code change. The ambiguous edges are in regardless, because
upstream refused to choose between instruments on purpose and dropping such a
passage for not being spoken about would hide a refusal (Q-07).

**Nothing is excluded.** A passage not in `source.ttl` is one nothing in either
record store has spoken about yet. The whole corpus is in scope; a source graph
over all 2,460 chunks would be about 7.7× the text and would put `dataset.nq`
near 40MB on every build, which is a cost worth naming rather than paying by
default.

## Named graphs

The separation is the governance mechanism (ADR-0007). Machine suggestions must
never become indistinguishable from approved knowledge; if they mix once, no later
audit can unmix them.

```
graph/source.ttl       assertions derived deterministically from the snapshot   committed
graph/approved.ttl     expert-approved assertions                               committed
graph/authored.ttl     machine-authored assertions, validated by nobody         committed
graph/inferred.ttl     produced by the CONSTRUCT rules — never authored         committed
graph/dataset.nq       all of the above as quads                                committed
graph/candidates.nq    machine-extracted, unapproved  (mirrors review/)         does not exist
graph/superseded.nq    retired assertions, kept for audit                       does not exist
```

`candidates` does not exist because no Stage 2 run has happened (ADR-0010) and
there are therefore no candidates. `superseded` does not exist because nothing
has been retired.

**`authored` is the fourth, added when ADR-0080 gave machine-authored content a
store of its own.** It is built from `authored/` by the same code that builds
`approved` from `eval/gold/` — one mapping, run twice — and differs in what the
graph asserts *about* each node rather than in the mapping itself:

- a relationship is a `tmk:AuthoredAssertion`, never a `tmk:ApprovedAssertion`,
  so the eight competency queries that name the second class cannot reach the
  first by accident;
- every node carries `tmk:origin "authored"` and `tmk:reviewStatus "unreviewed"`,
  so a triple lifted out of this file — into a report, a prompt, an evidence pack
  — still says what it is. The named graph is the boundary; the stamp is what
  survives leaving it;
- every node carries `tmk:authoredBy`, `tmk:authoredDate`, `tmk:authoringBasis`
  and `tmk:authoringReasoning`, and a SHACL shape refuses one that does not;
- `tmk:approvedBy` on a node here is a shape violation. It is the single failure
  the whole scheme exists to prevent (ADR-0079 guard 3).

**It is empty today and committed anyway.** An empty declared graph is the honest
state of a repo that has authored nothing yet, and it stops being empty without
any code changing.

**The two record graphs are never summed.** No figure in any generated report
adds `approved` to `authored`. The question a reader has is how much of what
they are looking at a person has read, and one number answers it in the
flattering direction (ADR-0080 consequences 3 and 4).

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
changing what the file says (Q-45).

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

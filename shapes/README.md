# shapes/ — SHACL constraints

**Roadmap Stage 6.** Written and running: `tmk-shacl`. All five files exist, and
against the current graph the result is **0 defects, 0 gaps, 29 notes**.

```
shapes/provenance.ttl    every assertion has method, span, hash, review status
shapes/authority.ttl     Manual instruction vs legislative provision; disjointness; PU-0004
shapes/vocabulary.ttl    SKOS well-formedness; no cycles; the not-label constraint
shapes/temporal.ttl      superseded material carries a status date
shapes/inference.ttl     every inferred assertion names the rule that produced it
```

The load order is `SHAPE_FILES` in `tm_knowledge.ontology.validate`, a fixed
list rather than a glob: a gate that quietly loses a constraint is worse than no
gate.

Severities match `tmk-harness` so the two read alike (ADR-0030) —
`sh:Violation` is a defect and exits 1, `sh:Warning` is a gap and exits 3,
`sh:Info` is a note. The 29 notes are all one constraint: a concept whose
not-label is another concept's preferred label, which is what a not-label is
*for* and is reported so the pairs are visible.

## The starting rule set

From the roadmap, and they are the right first five:

- every approved proposition has a source passage;
- every source passage identifies a document version;
- every extracted relationship identifies its extraction method;
- every legislative provision has a stable identifier;
- every superseded instruction has a status date;
- every inferred result identifies the rule that produced it.

Add to these from the prohibited-use list in `eval/`: any prohibited output that
is structurally detectable belongs here rather than in a test, because a shape
blocks publication while a test only reports.

**PU-0004 is the first one done.** "Section 43 of the Act requires the
connotation to be obvious, direct and immediate" — every word of it is in the
corpus, it is the Manual's formulation, and the Act requires no such thing. The
model separates where words are (`tmk:statedIn`) from what they are presented as
coming from (`tmk:attributedTo`), and `tmk:AuthorityConflationShape` fails any
proposition stated in a practice passage and attributed to a provision.

PU-0008 is the other `detectable_by: shacl` record and is **not** implemented.
It needs a retrieval output to constrain, and there is no retrieval layer yet.

## Rules

- **A failing shape is a finding, not a nuisance.** Do not loosen a shape to make
  a build pass. Fix the data, or record why the constraint was wrong as an ADR.
- **Validation failures that cannot be corrected deterministically go to a
  human.** Never auto-repair a legally significant record.
- **Shapes are tested too.** Each shape needs a fixture that violates it, proving
  it actually fires. An untested shape that never matches anything is worse than
  no shape, because it reads as coverage. The fixtures are in
  `tests/fixtures/shapes/` and the tests in `tests/unit/test_shapes_fire.py`.
- **A fires-test is half the proof.** A shape that fires on everything passes
  one. Where a conforming near-case exists, the fixture carries it and the test
  asserts the shape leaves it alone — `pu-0004-authority-conflation.ttl` holds
  the same words attributed honestly, and the shape must not fire on them.

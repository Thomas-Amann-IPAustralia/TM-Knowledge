# shapes/ — SHACL constraints

**Roadmap Stage 6.** Empty. Run with pySHACL from the pipeline, as the gate before
anything in `graph/` is published.

```
shapes/provenance.ttl    every assertion has method, span, hash, review status
shapes/authority.ttl     Manual instruction vs legislative provision; disjointness
shapes/vocabulary.ttl    SKOS well-formedness; no cycles in broader/narrower
shapes/temporal.ttl      superseded material carries a status date
shapes/inference.ttl     every inferred assertion names the rule that produced it
```

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

## Rules

- **A failing shape is a finding, not a nuisance.** Do not loosen a shape to make
  a build pass. Fix the data, or record why the constraint was wrong as an ADR.
- **Validation failures that cannot be corrected deterministically go to a
  human.** Never auto-repair a legally significant record.
- **Shapes are tested too.** Each shape needs a fixture that violates it, proving
  it actually fires. An untested shape that never matches anything is worse than
  no shape, because it reads as coverage.

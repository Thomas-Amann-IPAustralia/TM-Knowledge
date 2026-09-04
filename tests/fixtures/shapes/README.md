# tests/fixtures/shapes/ — graphs built to be wrong

Each file violates one constraint on purpose, so the shape that forbids it can
be shown to fire. `shapes/README.md`: *an untested shape that never matches
anything is worse than no shape, because it reads as coverage.*

| fixture | proves |
|---|---|
| `pu-0004-authority-conflation.ttl` | the reviewer's own prohibition blocks a publish |
| `disjoint-authority.ttl` | nothing is typed both practice and law |
| `unsigned-assertion.ttl` | six provenance fields, six named violations |
| `broader-cycle.ttl` | a cycle in `skos:broader`; a not-label that is also a label |
| `unexplained-inference.ttl` | an inference that cannot explain itself; a rule reaching an evaluative conclusion |
| `undated-supersession.ttl` | superseded material with no status date |

## The conforming twin

Two fixtures carry one, and they are the more important half.
`pu-0004-authority-conflation.ttl` holds `:bad-claim` and `:good-claim` — the
same words, from the same passage, one attributed to the Act and one to the
Manual. The shape must fire on the first and leave the second alone. A
constraint that fired on both would pass a fires-test and be useless.

## Rules

- **Not test data for anything else.** These graphs are wrong by construction.
  Nothing may import one to stand in for real content.
- **Say what is expected, in the file.** Every fixture opens with a comment
  naming the shape it should trip and what the conforming case is.
- **The TBox goes in with the fixture.** `sh:targetClass` follows
  `rdfs:subClassOf`, so a node typed `tmk:Chunk` is invisible to a shape
  targeting `tmk:Passage` without the class hierarchy — the fixture would pass,
  for a reason that has nothing to do with the constraint.

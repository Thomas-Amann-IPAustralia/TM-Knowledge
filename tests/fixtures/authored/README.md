# tests/fixtures/authored/ — authored stores the harness is pointed at

The sibling of `../harness/`, and it exists for the same reason: the unit of
work is a directory, so the fixtures are directories.

- `sound/` — a small authored store with **no defects**. Every envelope
  validates, every record validates against its own schema, every evidence ref
  resolves against the pinned snapshot, every quote lands at its span, every
  `approved_by` is null. It proves the authored checks stay quiet on good data.
- `defective/` — one record per thing the harness must catch, each broken in
  exactly one way, with the fault named in a comment above it. A check that
  stops catching something fails here rather than passing quietly.

**None of this is project content.** Every legal judgement in it is a
`«placeholder»` or an obviously synthetic value, and none of it may be copied
into `authored/` or `eval/gold/`. What is real is the mechanical part — refs,
spans, quotes and hashes — because a span check cannot be exercised against a
placeholder.

The real content hashes pin these fixtures to the snapshot in `data/pin.json`.
When the pin moves, the staleness check fires on `sound/` — that is the check
working, and the fix is to re-take the hashes from the new snapshot in the same
commit that moves the pin.

**`GC-0001` in `defective/` is not a typo.** It is the id of a real signed
concept in `eval/gold/`, and it is there to exercise the one-sequence-across-two-
stores rule (ADR-0080 consequence 1): the same id in both stores is two records
under one name, and the graph would hold whichever it read second.

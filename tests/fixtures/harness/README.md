# tests/fixtures/harness/ — gold sets the harness is pointed at

Two whole gold sets, not two records. The harness's unit of work is a directory,
so its fixtures are directories.

- `sound/` — a small gold set with **no defects**. Every ref resolves against
  the pinned snapshot, every span lands, every hash is current. It is far under
  every target band, so the harness reports it as gaps and nothing else. This is
  what proves the defect checks stay quiet on good data — a check that fires on
  everything is not a check.
- `defective/` — one record per defect the harness must catch, each broken in
  exactly one way, with the fault named in the record's `id` comment. A check
  that stops catching something fails here instead of silently passing.

**Refs, spans, surfaces and hashes are real**, and they have to be: a span check
cannot be exercised against a placeholder. They are quotations of the corpus,
which is mechanical. Everything that is a *judgement* — a type, a tier, a
modality, a predicate, an approver's name — is a `«placeholder»` or an obviously
synthetic value, and none of it may be copied into `eval/gold/` (CLAUDE.md
rule 1).

The real content hashes here pin these fixtures to the snapshot in `data/pin.json`.
When the pin moves, the staleness check will fire on `sound/` — that is the check
working, and the fix is to re-take the hashes from the new snapshot, in the same
commit that moves the pin.

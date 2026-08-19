# tests/unit/ — refs, provenance, the pin, the loader, the harness

Fast tests over the code in `src/tm_knowledge/`. Two kinds live here and they
are told apart by a marker, not by a directory:

- **Unmarked** — run on a clean checkout, with no snapshot. Anything that needs
  the corpus to exist does not belong in an unmarked test.
- **`@pytest.mark.snapshot`** — needs the pinned snapshot in `data/upstream/`
  (`tmk-fetch-upstream`). These skip rather than fail when it is absent, so a
  bare clone still runs the suite; CI fetches first, so they run there.

The corpus-wide tests are deliberately not "integration tests kept elsewhere".
A ref grammar transcribed slightly wrong passes every hand-picked example and
fails on the 9,000 refs upstream actually emits — which is exactly how the `#`
in 498 chunk refs was found (Q-17). Assert against the corpus.

**A test that asserts today's state expires.** `test_harness.py` proves the
completeness gate is red on an *empty* gold set and quiet on a *full* one, both
built in `tmp_path`. Asserting instead that `eval/gold/` is empty would have made
the suite fail on the day Stage 0 finally succeeded, which is the wrong day to
have to edit a test.

**Do not vendor snapshot files into fixtures** (ADR-0004). A test that needs
real corpus data reads it from `data/upstream/` behind the marker; a test that
needs a shape builds it by hand.

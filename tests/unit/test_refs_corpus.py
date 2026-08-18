"""The identifier rules, exercised over every ref in the pinned corpus.

A hand-picked round-trip proves the minter works on the refs someone thought of.
This proves it on the 9,000-odd refs upstream actually emits — which is where
the `#` in 498 chunk refs came from (ADR-0023, Q-17), and where a grammar
transcribed slightly wrong would show up.

Needs the pinned snapshot: `tmk-fetch-upstream`.
"""

from __future__ import annotations

import json

import pytest

from tm_knowledge.config import UPSTREAM_DIR
from tm_knowledge.refs import InvalidRef, RefKind, from_iri, parse_ref, to_iri

pytestmark = pytest.mark.snapshot

BASE = "https://example.invalid/tmk/"


def _skip_without_snapshot():
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")


@pytest.fixture(scope="module")
def manual_refs() -> dict[str, list[str]]:
    _skip_without_snapshot()
    pages: list[str] = []
    chunks: list[str] = []
    cited: set[str] = set()
    cases: set[str] = set()
    internal: set[str] = set()
    for path in sorted((UPSTREAM_DIR / "snapshot" / "pages").rglob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        pages.append(document["page"]["page_ref"])
        for chunk in document["chunks"]:
            chunks.append(chunk["chunk_ref"])
            cited.update(edge["id"] for edge in chunk.get("provisions", []))
            cases.update(edge["id"] for edge in chunk.get("cases", []))
            internal.update(edge["ref"] for edge in chunk.get("internal_refs", []))
    return {
        "pages": pages,
        "chunks": chunks,
        "cited": sorted(cited),
        "cases": sorted(cases),
        "internal": sorted(internal),
    }


@pytest.fixture(scope="module")
def legislation_refs() -> dict[str, list[str]]:
    _skip_without_snapshot()
    provisions: list[str] = []
    units: list[str] = []
    for path in sorted((UPSTREAM_DIR / "snapshot" / "legislation").rglob("provisions/*/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        provisions.append(record["ref"])
        units.extend(unit["ref"] for unit in record.get("units", []))
    return {"provisions": provisions, "units": units}


def test_every_manual_ref_parses(manual_refs):
    assert len(manual_refs["pages"]) == 500
    assert len(manual_refs["chunks"]) == 2460
    for ref in manual_refs["pages"]:
        assert parse_ref(ref, kind=RefKind.MANUAL_PAGE).value == ref
    for ref in manual_refs["chunks"]:
        assert parse_ref(ref, kind=RefKind.MANUAL_CHUNK).value == ref
    for ref in manual_refs["internal"]:
        assert parse_ref(ref).value == ref


def test_every_cited_provision_and_case_parses(manual_refs):
    for ref in manual_refs["cited"]:
        assert parse_ref(ref).kind in (RefKind.PROVISION, RefKind.UNIT)
    for ref in manual_refs["cases"]:
        assert parse_ref(ref).kind is RefKind.CASE
    assert len(manual_refs["cases"]) == 411


def test_every_legislation_ref_parses_and_units_carry_their_root(legislation_refs):
    assert len(legislation_refs["provisions"]) == 763
    assert len(legislation_refs["units"]) == 5813
    for ref in legislation_refs["provisions"]:
        assert parse_ref(ref).kind in (RefKind.PROVISION, RefKind.LEGISLATION)
    for ref in legislation_refs["units"]:
        parsed = parse_ref(ref)
        assert parsed.kind in (RefKind.UNIT, RefKind.LEGISLATION)
        if parsed.kind is RefKind.UNIT:
            assert parsed.root is not None and ref.startswith(parsed.root)


def test_the_undecidable_refs_are_reported_as_undecided_not_guessed(legislation_refs):
    """Q-18, measured. A provision ref and a definition unit's ref share a
    grammar; 228 refs in the pinned corpus cannot be told apart without the
    snapshot, and this module says so rather than picking one."""
    undecided_provisions = [
        ref for ref in legislation_refs["provisions"]
        if parse_ref(ref).kind is RefKind.LEGISLATION
    ]
    undecided_units = [
        ref for ref in legislation_refs["units"]
        if parse_ref(ref).kind is RefKind.LEGISLATION
    ]
    assert len(undecided_provisions) == 39
    assert len(undecided_units) == 189

    # The caller that read them out of a record knows which level they are, and
    # saying so is accepted rather than second-guessed.
    for ref in undecided_provisions:
        assert parse_ref(ref, kind=RefKind.PROVISION).kind is RefKind.PROVISION
    for ref in undecided_units:
        assert parse_ref(ref, kind=RefKind.UNIT).kind is RefKind.UNIT


def test_the_instrument_invariants_hold_over_the_whole_corpus(legislation_refs, manual_refs):
    """Upstream enforces these in `validate.py`; if our reading of them differed,
    a real ref would be rejected here."""
    for ref in legislation_refs["provisions"] + legislation_refs["units"]:
        parse_ref(ref)
    for ref in manual_refs["cited"]:
        parse_ref(ref)


def test_iri_round_trip_is_lossless_for_every_ref(manual_refs, legislation_refs):
    everything = (
        manual_refs["pages"]
        + manual_refs["chunks"]
        + manual_refs["cited"]
        + manual_refs["cases"]
        + manual_refs["internal"]
        + legislation_refs["provisions"]
        + legislation_refs["units"]
    )
    assert len(everything) > 9_000
    for ref in everything:
        assert from_iri(to_iri(ref, base=BASE), base=BASE) == ref


def test_the_hash_problem_is_real_and_at_scale(manual_refs):
    """The measurement behind ADR-0023, asserted so it cannot quietly change."""
    hashed = [ref for ref in manual_refs["chunks"] if "#" in ref]
    assert len(hashed) == 498
    assert len([ref for ref in manual_refs["chunks"] if "~" in ref]) == 333
    for ref in hashed:
        iri = to_iri(ref, base=BASE)
        assert "#" not in iri, "a '#' left verbatim makes the tail an IRI fragment"


def test_percent_encoding_is_confined_to_the_hash(manual_refs, legislation_refs):
    for ref in manual_refs["chunks"] + legislation_refs["units"]:
        iri = to_iri(ref, base=BASE)
        assert "%" not in iri.replace("%23", "")


def test_a_ref_that_upstream_would_never_emit_is_rejected():
    for bad in ("TMR1995/s224", "TMA1995/s4.7", "TMM/Part22/1/1/2 "):
        with pytest.raises(InvalidRef):
            parse_ref(bad)

"""Identifier module — parsing, invariants, IRI round-trip, candidate ids.

The `ref -> IRI -> ref` round-trip is required to ship with the minter
(`docs/IDENTIFIERS.md` §2, `src/README.md`). The corpus-wide version of it lives
in `tests/unit/test_refs_corpus.py` and needs the pinned snapshot; everything
here runs on a clean checkout.
"""

from __future__ import annotations

import json

import pytest

from tm_knowledge.refs import (
    InvalidRef,
    Ref,
    RefKind,
    SequentialRegister,
    candidate_id,
    from_iri,
    instrument_holds,
    is_ref,
    normalise_value,
    parse_ref,
    to_iri,
)

BASE = "https://example.invalid/tmk/"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value,kind",
    [
        ("TMM/Part22/1/1/2", RefKind.MANUAL),
        ("TMM/Part9/x-relevant-legislation23", RefKind.MANUAL),
        ("TMM/Part26/6#3~2", RefKind.MANUAL_CHUNK),
        ("TMM/Part9/5#1", RefKind.MANUAL_CHUNK),
        ("TMM/Part32A/2/3", RefKind.MANUAL),
        ("TMA1995/s41", RefKind.PROVISION),
        ("TMA1995/s43", RefKind.PROVISION),
        ("TMR1995/r3A.3", RefKind.PROVISION),
        ("TMR1995/sch2", RefKind.PROVISION),
        # Grammar cannot place these: a Schedule item and an instrument's front
        # matter are provision records, but `TMA1995/s128/prescribed-period` is
        # a unit and shares their shape. Reported as undecided, never guessed.
        ("TMR1995/sch3/item1", RefKind.LEGISLATION),
        ("TMA1995/front", RefKind.LEGISLATION),
        ("TMA1995/s128/prescribed-period", RefKind.LEGISLATION),
        ("TMA1995/front~1", RefKind.UNIT),
        ("TMA1995/s41(3)(a)", RefKind.UNIT),
        ("TMA1995/s44(3)", RefKind.UNIT),
        ("CASE/2018/FCAFC/109", RefKind.CASE),
        ("CASE/1894/RPC/11/518", RefKind.CASE),
    ],
)
def test_parses_the_kinds_upstream_emits(value, kind):
    assert parse_ref(value).kind is kind
    assert parse_ref(value).value == value


def test_unit_ref_carries_its_root():
    ref = parse_ref("TMA1995/s41(3)(a)")
    assert ref.root == "TMA1995/s41"
    assert ref.instrument == "TMA1995"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "  ",
        " TMA1995/s41",
        "TMA1995/s41 ",
        "tma1995/s41",  # case-folded: a different string, so not a ref
        "TMM/Chapter4/3",
        "Part22/1/1/2",
        "TMA1995",
        "TMA1995/",
        "https://data.ipaustralia.gov.au/tmk/ref/TMA1995/s41",
        "CASE/18/FCAFC/109",
    ],
)
def test_rejects_loudly_rather_than_normalising(value):
    with pytest.raises(InvalidRef):
        parse_ref(value)
    assert is_ref(value) is False


def test_parse_ref_rejects_non_strings():
    with pytest.raises(InvalidRef):
        parse_ref(None)  # type: ignore[arg-type]


def test_explicit_kind_settles_the_legislation_level(tmp_path=None):
    """The loader knows which file it read the ref out of; this module does not."""
    assert parse_ref("TMA1995/front", kind=RefKind.PROVISION).kind is RefKind.PROVISION
    assert (
        parse_ref("TMA1995/s128/prescribed-period", kind=RefKind.UNIT).kind is RefKind.UNIT
    )
    # But a stated level still cannot make a broken ref valid.
    with pytest.raises(InvalidRef):
        parse_ref("TMR1995/s224", kind=RefKind.PROVISION)


def test_explicit_kind_narrows_the_manual_ambiguity():
    assert parse_ref("TMM/Part22/1", kind=RefKind.MANUAL_PAGE).kind is RefKind.MANUAL_PAGE
    assert parse_ref("TMM/Part22/1/1/2", kind=RefKind.MANUAL_CHUNK).kind is RefKind.MANUAL_CHUNK
    with pytest.raises(InvalidRef):
        parse_ref("TMA1995/s41", kind=RefKind.MANUAL_PAGE)
    with pytest.raises(InvalidRef):
        parse_ref("TMA1995/s41", kind=RefKind.UNIT)


# ---------------------------------------------------------------------------
# The two upstream invariants
# ---------------------------------------------------------------------------

def test_instrument_must_be_able_to_hold_that_kind_of_provision():
    assert instrument_holds("TMA1995/s41") is True
    assert instrument_holds("TMR1995/r3A.3") is True
    # The Regulations have no sections.
    assert instrument_holds("TMR1995/s224") is False
    with pytest.raises(InvalidRef):
        parse_ref("TMR1995/s224")


def test_instrument_must_be_able_to_express_that_number():
    # The Act numbers its sections without dots; the Regulations always with.
    assert instrument_holds("TMA1995/s4.7") is False
    assert instrument_holds("TMR1995/r2016") is False
    with pytest.raises(InvalidRef):
        parse_ref("TMA1995/s4.7")


def test_unknown_instruments_and_schedules_pass():
    # A check for a contradiction, not a whitelist (upstream's own semantics).
    assert instrument_holds("CCA1995/s6.1") is True
    assert instrument_holds("TMR1995/sch2") is True
    assert instrument_holds("TMA1995/sch1") is True


# ---------------------------------------------------------------------------
# IRIs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "ref",
    [
        "TMM/Part22/1/1/2",
        "TMM/Part26/6#3~2",
        "TMM/Part9/x-relevant-legislation23",
        "TMA1995/s41(3)(a)",
        "TMR1995/r3A.3",
        "TMR1995/sch3/item1",
        "CASE/2018/FCAFC/109",
    ],
)
def test_ref_to_iri_round_trip_is_lossless(ref):
    assert from_iri(to_iri(ref, base=BASE), base=BASE) == ref


def test_parentheses_and_tildes_are_not_percent_encoded():
    iri = to_iri("TMA1995/s41(3)(a)", base=BASE)
    assert iri == BASE + "ref/TMA1995/s41(3)(a)"
    assert "%28" not in iri and "%29" not in iri
    assert "%7E" not in to_iri("TMM/Part26/6#3~2", base=BASE)


def test_a_hash_in_a_chunk_ref_is_escaped_because_it_would_be_a_fragment():
    # ADR-0023 / Q-17. 498 of the corpus's 2,460 chunk refs carry a '#'; left
    # verbatim the IRI names a different resource and a fragment of it.
    iri = to_iri("TMM/Part26/6#3~2", base=BASE)
    assert iri == BASE + "ref/TMM/Part26/6%233~2"
    assert "#" not in iri
    assert from_iri(iri, base=BASE) == "TMM/Part26/6#3~2"


def test_minting_validates_first():
    with pytest.raises(InvalidRef):
        to_iri("TMR1995/s224", base=BASE)


def test_from_iri_rejects_a_foreign_iri():
    with pytest.raises(InvalidRef):
        from_iri("https://elsewhere.invalid/ref/TMA1995/s41", base=BASE)


def test_base_iri_is_configurable_and_read_from_one_place(monkeypatch):
    monkeypatch.setenv("TMK_BASE_IRI", "https://other.invalid/x")
    assert to_iri("TMA1995/s41").startswith("https://other.invalid/x/ref/")


# ---------------------------------------------------------------------------
# Candidate ids (ADR-0020)
# ---------------------------------------------------------------------------

def test_candidate_id_is_stable_across_runs_over_unchanged_input():
    first = candidate_id("TMM/Part22/1/1/2", 10, 34, "acquired distinctiveness")
    second = candidate_id("TMM/Part22/1/1/2", 10, 34, "acquired distinctiveness")
    assert first == second
    assert first.startswith("cand-")
    assert len(first) == len("cand-") + 16


def test_candidate_id_does_not_depend_on_the_extractor():
    """The whole point of ADR-0020: one span, one candidate, N pieces of evidence."""
    signature = ("TMM/Part22/1/1/2", 10, 34, "acquired distinctiveness")
    # There is no method parameter to pass. If one is ever added, this fails.
    with pytest.raises(TypeError):
        candidate_id(*signature, "yake")  # type: ignore[call-arg]


def test_candidate_id_changes_when_the_span_or_the_value_changes():
    base = candidate_id("TMM/Part22/1/1/2", 10, 34, "acquired distinctiveness")
    assert candidate_id("TMM/Part22/1/1/2", 11, 34, "acquired distinctiveness") != base
    assert candidate_id("TMM/Part22/1/1/3", 10, 34, "acquired distinctiveness") != base
    assert candidate_id("TMM/Part22/1/1/2", 10, 34, "inherent adaptation") != base


def test_candidate_id_is_insensitive_to_case_and_whitespace_only():
    base = candidate_id("TMM/Part22/1/1/2", 10, 34, "acquired distinctiveness")
    assert candidate_id("TMM/Part22/1/1/2", 10, 34, " Acquired  Distinctiveness ") == base


def test_normalise_value_is_mechanical_only():
    assert normalise_value("  Acquired  DISTINCTIVENESS ") == "acquired distinctiveness"
    # Not stemming, not lemmatising, not article-stripping — those are judgements.
    assert normalise_value("the marks") != normalise_value("mark")


def test_candidate_id_validates_its_source_ref_and_span():
    with pytest.raises(InvalidRef):
        candidate_id("not-a-ref", 0, 1, "x")
    with pytest.raises(ValueError):
        candidate_id("TMM/Part22/1/1/2", 5, 2, "x")


# ---------------------------------------------------------------------------
# Sequential register
# ---------------------------------------------------------------------------

def test_register_allocates_by_appending_and_never_reuses(tmp_path):
    register = SequentialRegister(tmp_path / "concepts.json", "c")
    assert register.allocate(pref_label="") == "c-0001"
    assert register.allocate(pref_label="") == "c-0002"

    # Withdraw the first: the gap is never filled.
    entries = json.loads((tmp_path / "concepts.json").read_text())
    del entries[0]
    (tmp_path / "concepts.json").write_text(json.dumps(entries))
    assert register.allocate(pref_label="") == "c-0003"


def test_register_refuses_a_foreign_prefix(tmp_path):
    path = tmp_path / "concepts.json"
    path.write_text(json.dumps([{"id": "rule-0001"}]))
    with pytest.raises(ValueError):
        SequentialRegister(path, "c").allocate()


def test_ref_is_frozen():
    ref = Ref("TMA1995/s41", RefKind.PROVISION)
    with pytest.raises(Exception):
        ref.value = "TMA1995/s42"  # type: ignore[misc]

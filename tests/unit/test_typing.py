"""The concept typing pass — what the sorter is shown, and who wrote it.

The `notes` cell is the whole of what a sorter sees without opening the evidence
pack: the concept's name, the Manual's other names for it, and the labels it is
explicitly not. Every part of that is copied from an approved record — a summary
that reworded a label would be a machine making a vocabulary judgement
(CLAUDE.md rule 1).

**Since ADR-0092 the pass also fills the `type` column**, from
`authored/concept-types.yaml` and from nowhere else. That is the interesting
half of these tests now, and what they pin down is the boundary rather than the
filling: a signed typing beats an authored one, an authored id is never minted
twice, a refused authored record never reaches the sheet, and `approved_by`
leaves this module empty whatever the authored record says about itself.

Every test builds both stores explicitly. A test that let `rows()` load the real
`authored/` would pass or fail on what the repository happens to hold that day,
which is how a suite stops testing the code (Q-51).

No snapshot needed: nothing here resolves a ref.
"""

from __future__ import annotations

from pathlib import Path

from tm_knowledge.authored import store as authored_store
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.typing import rows, summarise

CONNOTATION = {
    "id": "GC-0001",
    "pref_label": "«a label»",
    "alt_labels": ["«another name for it»", "«a third name»"],
    "not_labels": ["«a near-miss»", "«a second near-miss»"],
}


def _gold(concepts, types=(), retired=()) -> goldset.GoldSet:
    return goldset.GoldSet(
        root=goldset.GOLD_DIR,
        records={"gold_concept": tuple(concepts), "concept_type": tuple(types)},
        files={},
        retired_ids={identifier: {} for identifier in retired},
    )


def _authored(*records, sound=True) -> authored_store.AuthoredSet:
    """An authored store holding exactly these typings.

    `sound=False` builds entries carrying an envelope error, which is how a
    record that could not say who wrote it reaches the code under test.
    """
    envelope = {
        "review_status": "unreviewed",
        "authored_by": "«a model»",
        "authored_date": "2026-09-08",
        "authoring_basis": "corpus_inferred",
        "reasoning": "«why this group»",
    }
    errors = () if sound else (authored_store.SchemaError(None, "authored", "«broken»"),)
    return authored_store.AuthoredSet(
        root=Path("«not read»"),
        entries=tuple(
            authored_store.AuthoredRecord(
                record_type="concept_type",
                record=dict(record),
                envelope=dict(envelope),
                source_file=Path("«not read»"),
                position=position,
                envelope_errors=errors,
            )
            for position, record in enumerate(records)
        ),
    )


#: Nothing authored. The state of the store before 2026-09-08, and the state
#: every test that is not about pre-filling wants to be in.
NOTHING_AUTHORED = _authored()


def test_the_summary_carries_the_other_names_as_well_as_the_near_misses():
    """`pref_label` is one form of words out of several. A sorter who does not
    recognise it may recognise what the Manual also calls it, and the
    near-misses are what stop them typing by label once they do."""
    summary = summarise(CONNOTATION)
    assert summary.startswith("«a label»")
    assert "also called: «another name for it», «a third name»" in summary
    assert "not: «a near-miss», «a second near-miss»" in summary
    assert summary.index("also called") < summary.index("not:")


def test_the_summary_quotes_the_labels_verbatim():
    """It reshapes; it never supplies. Every label in the cell is a string the
    approved record holds, character for character."""
    summary = summarise(CONNOTATION)
    for label in (
        CONNOTATION["pref_label"],
        *CONNOTATION["alt_labels"],
        *CONNOTATION["not_labels"],
    ):
        assert label in summary


def test_a_concept_with_no_other_names_gets_no_also_called_clause():
    """An empty list is not a heading with nothing under it — a clause that
    reads `also called:` and then stops looks like data that went missing."""
    summary = summarise({"pref_label": "«a label»", "not_labels": ["«a near-miss»"]})
    assert "also called" not in summary
    assert summary == "«a label» — not: «a near-miss»"


def test_the_row_carries_the_summary_and_no_type():
    """With nothing authored the row is what it always was: the id, the concept
    and the evidence, with `type` absent — not blank, which the transcriber
    would read as a value."""
    (row,) = rows(_gold([CONNOTATION]), NOTHING_AUTHORED)
    assert row["id"] == "GT-0001"
    assert row["concept"] == "GC-0001"
    assert row["notes"] == summarise(CONNOTATION)
    assert "type" not in row


def test_a_concept_already_sorted_is_returned_as_signed():
    """A second pass must not re-summarise a row somebody has ruled on: the
    signed record is the artefact, and its notes are whatever the signer left."""
    signed = {
        "id": "GT-0007",
        "concept": "GC-0001",
        "type": "legal_test",
        "notes": "«what the signer wrote»",
        "approved_by": "«name»",
        "approved_date": "2026-09-08",
    }
    (row,) = rows(_gold([CONNOTATION], types=[signed]), NOTHING_AUTHORED)
    assert row == signed


def test_ids_are_appended_and_never_fill_a_retired_gap():
    """`IDENTIFIERS.md` §3. A withdrawn id stays withdrawn."""
    concepts = [CONNOTATION, {"id": "GC-0002", "pref_label": "«a second label»"}]
    built = rows(_gold(concepts, retired=["GT-0001", "GT-0002"]), NOTHING_AUTHORED)
    assert [row["id"] for row in built] == ["GT-0003", "GT-0004"]


# ---------------------------------------------------------------------------
# What ADR-0092 added: the machine's answer, and the four things it may not do
# ---------------------------------------------------------------------------


def test_an_authored_typing_pre_fills_the_type_and_keeps_its_id():
    """The premise of ADR-0079 is that correcting an answer is cheaper than
    composing one, so the reviewer's row arrives filled in. It keeps the
    authored record's id, because a record moves between the two stores rather
    than being minted twice (ADR-0080)."""
    proposed = {"id": "GT-0031", "concept": "GC-0001", "type": "relevant_factor"}
    (row,) = rows(_gold([CONNOTATION]), _authored(proposed))
    assert row["id"] == "GT-0031"
    assert row["type"] == "relevant_factor"


def test_a_pre_filled_row_is_never_pre_signed():
    """The one thing this module may not do. Whatever an authored record says
    about itself, `approved_by` leaves here empty: a name in that cell means a
    person read the record, and no code path may write one (CLAUDE.md rule 1,
    ADR-0079 guard 3)."""
    proposed = {
        "id": "GT-0031",
        "concept": "GC-0001",
        "type": "relevant_factor",
        "approved_by": "«a name the record should never carry»",
        "approved_date": "2026-09-08",
    }
    (row,) = rows(_gold([CONNOTATION]), _authored(proposed))
    assert row["approved_by"] is None
    assert row["approved_date"] is None


def test_a_signed_typing_beats_an_authored_one():
    """Both stores hold a typing for the same concept. The signed record wins
    and the sheet does not re-ask — a person's ruling is not put back in front
    of them next to a machine's (ADR-0080 consequence 2)."""
    signed = {
        "id": "GT-0007",
        "concept": "GC-0001",
        "type": "legal_test",
        "notes": "«what the signer wrote»",
        "approved_by": "«name»",
        "approved_date": "2026-09-08",
    }
    proposed = {"id": "GT-0007", "concept": "GC-0001", "type": "exception"}
    (row,) = rows(_gold([CONNOTATION], types=[signed]), _authored(proposed))
    assert row == signed


def test_a_refused_authored_record_never_reaches_the_sheet():
    """An envelope that will not validate means the record cannot say who wrote
    it. It is reported by the harness and it does not pre-fill anything: a
    proposal with no provenance sitting in a reviewer's spreadsheet is
    indistinguishable from one with provenance, which is the whole failure
    ADR-0079 rewrote rule 1 to prevent."""
    refused = {"id": "GT-0031", "concept": "GC-0001", "type": "relevant_factor"}
    (row,) = rows(_gold([CONNOTATION]), _authored(refused, sound=False))
    assert "type" not in row
    assert row["id"] == "GT-0001"


def test_an_authored_id_is_never_minted_a_second_time():
    """`GC-0002` has no typing and needs a new id. It must not be handed
    `GT-0031`, which the authored store already uses for `GC-0001` — two records
    claiming one id across the two stores is a defect the harness reports and
    nothing could undo afterwards (ADR-0080 consequence 1)."""
    concepts = [CONNOTATION, {"id": "GC-0002", "pref_label": "«a second label»"}]
    proposed = {"id": "GT-0031", "concept": "GC-0001", "type": "relevant_factor"}
    built = rows(_gold(concepts), _authored(proposed))
    assert [row["id"] for row in built] == ["GT-0031", "GT-0032"]

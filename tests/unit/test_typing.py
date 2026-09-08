"""The concept typing pass — what the sorter is shown, and what they are not.

The pass supplies the shape and the evidence and never the type
(`stage0/typing.py`, ADR-0071), so the tests worth having are about the row a
person actually reads. The `notes` cell is the whole of it for anyone who does
not open the evidence pack beside the sheet: the concept's name, the Manual's
other names for it, and the labels it is explicitly not. Every part of that is
copied from an approved record — a summary that reworded a label would be a
machine making a vocabulary judgement (CLAUDE.md rule 1).

No snapshot needed: nothing here resolves a ref.
"""

from __future__ import annotations

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
    """Which group a concept belongs in is a legal judgement. The row supplies
    the id, the concept and the evidence, and leaves `type` absent — not blank,
    which the transcriber would read as a value."""
    (row,) = rows(_gold([CONNOTATION]))
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
    (row,) = rows(_gold([CONNOTATION], types=[signed]))
    assert row == signed


def test_ids_are_appended_and_never_fill_a_retired_gap():
    """`IDENTIFIERS.md` §3. A withdrawn id stays withdrawn."""
    concepts = [CONNOTATION, {"id": "GC-0002", "pref_label": "«a second label»"}]
    built = rows(_gold(concepts, retired=["GT-0001", "GT-0002"]))
    assert [row["id"] for row in built] == ["GT-0003", "GT-0004"]

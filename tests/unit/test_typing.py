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


def _authored(*records, concepts=(), sound=True) -> authored_store.AuthoredSet:
    """An authored store holding exactly these typings and these concepts.

    Positional arguments are typings, which is what the store held when this
    helper was written. `concepts=` holds authored concepts, which the sheet
    started reading at ADR-0095 — they are a separate argument rather than a
    second positional list because a caller that muddled the two would build a
    store whose typings type nothing.

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
    entries = [
        authored_store.AuthoredRecord(
            record_type=record_type,
            record=dict(record),
            envelope=dict(envelope),
            source_file=Path("«not read»"),
            position=position,
            envelope_errors=errors,
        )
        for record_type, group in (("gold_concept", concepts), ("concept_type", records))
        for position, record in enumerate(group)
    ]
    return authored_store.AuthoredSet(root=Path("«not read»"), entries=tuple(entries))


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
    assert row["notes"].startswith(summarise(CONNOTATION))
    # And it says where the concept came from. Since ADR-0095 the sheet carries
    # concepts from both stores, and which store a row's concept came from is the
    # difference between a label an expert chose and one a machine did.
    assert row["notes"].endswith("[concept signed by an expert]")
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

# ---------------------------------------------------------------------------
# Concepts from both stores — ADR-0095
# ---------------------------------------------------------------------------


AUTHORED_CONCEPT = {
    "id": "GC-0100",
    "pref_label": "«a label a machine chose»",
    "alt_labels": ["«a synonym a machine chose»"],
    "not_labels": ["«a near-miss a machine chose»"],
}


def test_a_concept_only_the_authored_store_holds_still_reaches_the_sheet():
    """The whole of what ADR-0095 changed.

    Before it, `rows()` read `eval/gold/concepts.yaml` and nothing else, so the
    workbook could only ever hold the 52 concepts found inside the section 43
    boundary — however many the repository authored from the other 53 Parts.
    """
    prepared = rows(
        _gold([CONNOTATION]),
        _authored(concepts=[AUTHORED_CONCEPT]),
    )
    assert [row["concept"] for row in prepared] == ["GC-0001", "GC-0100"]


def test_the_row_says_which_store_its_concept_came_from():
    """A wrong group is a dropdown away from right and a wrong concept is not, so
    the reviewer is told which kind of row they are on."""
    signed_row, authored_row = rows(
        _gold([CONNOTATION]),
        _authored(concepts=[AUTHORED_CONCEPT]),
    )
    assert signed_row["notes"].endswith("[concept signed by an expert]")
    assert authored_row["notes"].endswith("[concept authored by a machine, unreviewed]")


def test_a_refused_authored_concept_never_reaches_the_sheet():
    """A record whose envelope will not validate has no usable provenance, and
    must not arrive in front of a reviewer looking exactly like one that has
    (ADR-0079)."""
    prepared = rows(
        _gold([CONNOTATION]),
        _authored(concepts=[AUTHORED_CONCEPT], sound=False),
    )
    assert [row["concept"] for row in prepared] == ["GC-0001"]


def test_a_signed_concept_wins_over_an_authored_one_with_the_same_id():
    """One `GC-0123` exists in this project (ADR-0080 c1). If both stores hold it
    the signed record is the one a reviewer sees, and the sheet never shows the
    id twice."""
    duplicate = dict(AUTHORED_CONCEPT, id="GC-0001", pref_label="«a machine's version»")
    prepared = rows(_gold([CONNOTATION]), _authored(concepts=[duplicate]))
    assert [row["concept"] for row in prepared] == ["GC-0001"]
    assert prepared[0]["notes"].startswith(summarise(CONNOTATION))


# ---------------------------------------------------------------------------
# The groups live in three files and must agree
# ---------------------------------------------------------------------------
#
# ADR-0098 took the taxonomy from four groups to nine, and a group name now has
# to be written in three places that nothing joins up at runtime: the schema
# enum (which the workbook's dropdown is generated from), `typing.GROUPS` (the
# legend on the sheet and in the report) and `CONCEPT_CLASSES` (the ontology
# class each group asserts). A tenth group added to two of the three fails in
# three different ways — a value the schema rejects, a dropdown missing an
# option, or a concept silently asserting no class — and none of them fails
# loudly. These two tests are the join.


def _schema_groups() -> list[str]:
    import json

    from tm_knowledge.config import REPO_ROOT

    schema = json.loads(
        (REPO_ROOT / "eval" / "schemas" / "concept-type.schema.json").read_text()
    )
    return schema["properties"]["type"]["enum"]


def test_the_sheets_groups_are_exactly_the_schemas_groups_in_the_same_order():
    """The dropdown is generated from the schema and the legend beside it from
    `GROUPS`. If they disagree, a reviewer reads one list and picks from
    another."""
    from tm_knowledge.stage0.typing import GROUPS

    assert [value for value, _ in GROUPS] == _schema_groups()


def test_every_group_but_none_of_these_asserts_a_class():
    """`none_of_these` asserts no class on purpose — it is a real answer about
    the taxonomy and the concept stays a bare `tmk:LegalConcept` (ADR-0093).
    Every other group must name one, and that class must be declared in the
    ontology: a group missing from `CONCEPT_CLASSES` types nothing and says
    nothing about having failed to."""
    from rdflib import OWL, RDF, Graph

    from tm_knowledge.config import REPO_ROOT
    from tm_knowledge.ontology.build import CONCEPT_CLASSES
    from tm_knowledge.ontology.namespaces import TMK

    groups = set(_schema_groups())
    assert set(CONCEPT_CLASSES) == groups - {"none_of_these"}

    declared = Graph()
    declared.parse(
        REPO_ROOT / "ontology" / "draft" / "legal-concepts.ttl", format="turtle"
    )
    for group, class_name in CONCEPT_CLASSES.items():
        assert (TMK[class_name], RDF.type, OWL.Class) in declared, (
            f"{group} maps to tmk:{class_name}, which legal-concepts.ttl does "
            f"not declare"
        )

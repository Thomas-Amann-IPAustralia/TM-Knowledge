"""The one request — what it asks, what it must never fill in, and what it
promises to the transcriber.

Three things are worth pinning here and the rest is prose.

**`approved_by` leaves this module empty**, on both record sheets, whatever the
source record says about itself. It is the cell the whole scheme is built to
protect, and this pack is the only artefact designed to be handed to the person
whose name goes in it — the one place where a stray copy would be invisible.

**The workbook survives `tmk-transcribe`.** The pack adds four annotation
columns, deletes eleven record sheets and appends five sheets of its own, and
every one of those is a chance to break the layout the transcriber refuses to
guess about. A pack whose answers cannot be read back wastes the one request.

**The findings are found, and disclosure is judged across the store.** A
duplicate label the reviewer is told about somewhere is not the same finding as
one nothing mentions, and a check that could not tell them apart would report
seven false alarms beside three real ones.

Every test builds both stores explicitly (Q-51). No snapshot needed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tm_knowledge.authored import store as authored_store
from tm_knowledge.stage0 import expertpack, goldset

openpyxl = pytest.importorskip("openpyxl")


def _gold(concepts=(), types=(), relationships=()) -> goldset.GoldSet:
    return goldset.GoldSet(
        root=goldset.GOLD_DIR,
        records={
            "gold_concept": tuple(concepts),
            "concept_type": tuple(types),
            "gold_relationship": tuple(relationships),
        },
        files={},
        retired_ids={},
    )


def _authored(concepts=(), types=(), envelopes=None) -> authored_store.AuthoredSet:
    base = {
        "review_status": "unreviewed",
        "authored_by": "«a model»",
        "authored_date": "2026-09-09",
        "authoring_basis": "corpus_inferred",
        "reasoning": "«why»",
        "expert_should_check": "«the thing most likely wrong»",
    }
    envelopes = envelopes or {}
    entries = [
        authored_store.AuthoredRecord(
            record_type=record_type,
            record=dict(record),
            envelope={**base, **envelopes.get(str(record.get("id")), {})},
            source_file=Path("«not read»"),
            position=position,
        )
        for record_type, group in (("gold_concept", concepts), ("concept_type", types))
        for position, record in enumerate(group)
    ]
    return authored_store.AuthoredSet(root=Path("«not read»"), entries=tuple(entries))


SIGNED_CONCEPT = {
    "id": "GC-0001",
    "pref_label": "«a shared word»",
    "notes": "«what the signed one means»",
    "approved_by": "TC",
    "approved_date": "2026-08-25",
}


# ---------------------------------------------------------------------------
# The cell an agent may never write
# ---------------------------------------------------------------------------


def test_no_row_this_pack_writes_carries_a_reviewers_name():
    """The load-bearing one. An authored record claiming to be approved is a
    defect the harness reports, but a *workbook* carrying a name is worse: it is
    handed to the person whose name it is, and a pre-filled signature is the one
    thing they would have no reason to look at twice."""
    lying = {
        "id": "GC-0100",
        "pref_label": "«a word»",
        # A record that should never exist, built here on purpose: the pack must
        # empty these cells rather than trust the store to have.
        "approved_by": "TC",
        "approved_date": "2026-01-01",
    }
    typing = {
        "id": "GT-0100",
        "concept": "GC-0100",
        "type": "legal_test",
        "approved_by": "TC",
        "approved_date": "2026-01-01",
    }
    book, _ = expertpack.build_workbook(
        _gold(), _authored(concepts=[lying], types=[typing]), generated="2026-09-09"
    )
    for name in expertpack.RECORD_SHEETS:
        sheet = book[name]
        headers = {cell.value: index for index, cell in enumerate(sheet[1], start=1)}
        for row in range(2, sheet.max_row + 1):
            assert sheet.cell(row=row, column=headers["approved_by"]).value is None
            assert sheet.cell(row=row, column=headers["approved_date"]).value is None


# ---------------------------------------------------------------------------
# The round trip
# ---------------------------------------------------------------------------


def test_the_transcriber_reads_the_pack_back(tmp_path):
    """The pack rearranges the intake workbook heavily. If `tmk-transcribe`
    cannot read the result, every answer the expert writes is stranded in a
    spreadsheet — and this is a request we only get to make once."""
    from tm_knowledge.stage0 import transcribe

    concept = {"id": "GC-0100", "pref_label": "«a word»"}
    typing = {"id": "GT-0100", "concept": "GC-0100", "type": "legal_test"}
    book, _ = expertpack.build_workbook(
        _gold(), _authored(concepts=[concept], types=[typing]), generated="2026-09-09"
    )
    path = tmp_path / "pack.xlsx"
    book.save(path)

    result = transcribe.read_workbook(path)
    assert result.total == 0, "nothing may cross without a verdict and a name"
    assert len(result.held) == 2


def test_a_signed_row_crosses_and_an_untouched_one_does_not(tmp_path):
    """Silence promotes nothing (ADR-0086). The reviewer's name and verdict are
    what move a row, and a row they read and left alone stays where it is."""
    from tm_knowledge.stage0 import transcribe

    concepts = [
        {"id": "GC-0100", "pref_label": "«signed by them»"},
        {"id": "GC-0101", "pref_label": "«left alone»"},
    ]
    book, _ = expertpack.build_workbook(
        _gold(), _authored(concepts=concepts), generated="2026-09-09"
    )
    sheet = book["concepts"]
    headers = {cell.value: index for index, cell in enumerate(sheet[1], start=1)}
    sheet.cell(row=2, column=headers["approved_by"], value="TC")
    sheet.cell(row=2, column=headers["approved_date"], value="2026-09-15")
    sheet.cell(row=2, column=headers["verdict"], value="correct")
    path = tmp_path / "pack.xlsx"
    book.save(path)

    result = transcribe.read_workbook(path)
    assert [record["id"] for record in result.records["gold_concept"]] == ["GC-0100"]
    assert len(result.held) == 1


def test_the_pack_ships_no_empty_record_sheets():
    """Eleven blank sheets in a request with a fixed budget of somebody's
    attention spend some of it on working out that they are blank."""
    book, _ = expertpack.build_workbook(_gold(), _authored(), generated="2026-09-09")
    assert "entities" not in book.sheetnames
    assert "prohibited-uses" not in book.sheetnames
    for name in expertpack.RECORD_SHEETS:
        assert name in book.sheetnames


def test_the_big_questions_come_first():
    """The pack's promise is that stopping early still answers the most valuable
    questions. That is a claim about sheet order and nothing else enforces it."""
    book, _ = expertpack.build_workbook(_gold(), _authored(), generated="2026-09-09")
    order = book.sheetnames
    assert order[1] == "1 the big ones"
    assert order.index("1 the big ones") < order.index("concept-types")


# ---------------------------------------------------------------------------
# The findings
# ---------------------------------------------------------------------------


def test_a_duplicate_label_is_found_across_the_two_stores():
    twin = {"id": "GC-0100", "pref_label": "«a shared word»", "notes": "«ours»"}
    found = expertpack.duplicate_labels(
        _gold(concepts=[SIGNED_CONCEPT]), _authored(concepts=[twin])
    )
    assert [item.authored_id for item in found] == ["GC-0100"]
    assert found[0].signed_id == "GC-0001"


def test_disclosure_counts_wherever_it_was_said():
    """Seven of the ten real collisions name the signed record on the authored
    concept; one names it on that concept's *typing* instead. Both are disclosed
    — the reviewer meets both records in this pack — and a check that only read
    the concept's own record would report a silent clash where somebody had in
    fact flagged it (ADR-0101)."""
    twin = {"id": "GC-0100", "pref_label": "«a shared word»"}
    typing = {"id": "GT-0100", "concept": "GC-0100", "type": "legal_test"}
    said_on_the_typing = _authored(
        concepts=[twin],
        types=[typing],
        envelopes={"GT-0100": {"expert_should_check": "GC-0001 says this too"}},
    )
    found = expertpack.duplicate_labels(_gold(concepts=[SIGNED_CONCEPT]), said_on_the_typing)
    assert found[0].disclosed is True

    silent = _authored(concepts=[twin], types=[typing])
    found = expertpack.duplicate_labels(_gold(concepts=[SIGNED_CONCEPT]), silent)
    assert found[0].disclosed is False


def test_the_undisclosed_duplicates_sort_to_the_top():
    """The three nothing flagged are the finding; the seven that argued for
    themselves are the design working. A reviewer reads down."""
    signed = [
        SIGNED_CONCEPT,
        {"id": "GC-0002", "pref_label": "«a second shared word»", "approved_by": "TC"},
    ]
    authored = _authored(
        concepts=[
            {"id": "GC-0100", "pref_label": "«a shared word»", "notes": "GC-0001"},
            {"id": "GC-0101", "pref_label": "«a second shared word»"},
        ]
    )
    found = expertpack.duplicate_labels(_gold(concepts=signed), authored)
    assert [item.disclosed for item in found] == [False, True]


def test_only_a_blank_modality_is_asked_about():
    """The field sits inside a record a person signed. An agent may not fill it
    even under the amended rules, and a record that already carries one is not a
    question."""
    relationships = [
        {"id": "GR-0006", "subject": "«a»", "predicate": "«p»", "object": "«b»"},
        {"id": "GR-0007", "subject": "«a»", "predicate": "«p»", "object": "«b»",
         "modality": "must"},
    ]
    found = expertpack.unjudged_modalities(_gold(relationships=relationships))
    assert [item.identifier for item in found] == ["GR-0006"]


# ---------------------------------------------------------------------------
# The covering note
# ---------------------------------------------------------------------------


def test_the_note_and_the_workbook_cannot_disagree():
    """Both are produced in one run from one set of counts. A note quoting a
    figure the spreadsheet does not carry is the fastest way to lose a
    reviewer's trust in both."""
    concepts = [{"id": f"GC-{n:04d}", "pref_label": f"«word {n}»"} for n in range(100, 104)]
    book, counts = expertpack.build_workbook(
        _gold(), _authored(concepts=concepts), generated="2026-09-09"
    )
    assert counts["concepts"] == 4
    assert book["concepts"].max_row == 5
    assert "4" in expertpack.render_letter(counts, generated="2026-09-09")


def test_the_note_stays_in_the_readers_language():
    """The audience is an examiner being asked for a few hours, not a
    contributor to this repository. Every piece of our vocabulary they have to
    decode is attention we spent on ourselves."""
    note = expertpack.render_letter(
        {"concepts": 78, "typings": 130, "duplicates": 10, "modality": 5,
         "authored": 208, "signed": 190},
        generated="2026-09-09",
    )
    for jargon in (
        "ADR-", "eval/gold", "authored/", "record type", "ontology", "SHACL",
        "triple", "envelope", "corpus_", "review_status", "chunk_ref",
    ):
        assert jargon not in note, f"{jargon!r} is our word, not theirs"

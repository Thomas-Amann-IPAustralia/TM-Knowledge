"""The intake path — P7's and P8's done-criteria.

P7: the workbook regenerates from the schemas, enum cells reject out-of-
vocabulary values, and a round trip through P8 preserves every field.
P8: a filled workbook transcribes to schema-valid records, every missing
judgement field appears as a gap rather than being filled, and re-running over
unchanged input rewrites nothing.

The tests that matter most are the ones about *not* doing things. Transcription
may reshape and never supply, so a blank `modality` must come out blank, a row
that is not yet a record must be rejected rather than stubbed, and a value
outside an enum must stop the read rather than be snapped to the nearest
allowed one. Each of those is a legal reading if a machine makes it.

No snapshot needed: nothing here resolves a ref.
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip("openpyxl", reason="the intake path needs `pip install -e '.[intake]'`")

from openpyxl.utils import get_column_letter  # noqa: E402

from tm_knowledge.config import REPO_ROOT  # noqa: E402
from tm_knowledge.stage0 import goldset, transcribe, workbook  # noqa: E402
from tm_knowledge.stage0.intake import SHEET_NAMES, sheets  # noqa: E402
from tm_knowledge.stage0.schemas import (  # noqa: E402
    RECORD_TYPES,
    property_order,
    validate,
)

SOUND = REPO_ROOT / "tests" / "fixtures" / "harness" / "sound"


@pytest.fixture(scope="module")
def source_records() -> dict[str, list[dict]]:
    gold = goldset.load(SOUND)
    return {record_type: list(records) for record_type, records in gold.records.items()}


def _filled(tmp_path, records, name="filled.xlsx"):
    book = workbook.build(generated="2026-08-19")
    workbook.fill(book, records)
    path = tmp_path / name
    book.save(path)
    return path


# ---------------------------------------------------------------------------
# P7 — the workbook
# ---------------------------------------------------------------------------


def test_the_workbook_ships_with_no_example_rows(tmp_path):
    """Not one, not even a marked one. A row in a spreadsheet is a keystroke
    from being twenty rows, and a plausible answer nobody approved is worse than
    a blank (CLAUDE.md rule 1)."""
    from openpyxl import load_workbook

    path = tmp_path / "empty.xlsx"
    workbook.write(path, generated="2026-08-19")
    book = load_workbook(path)
    for spec in sheets():
        assert book[spec.name].max_row == 1, f"{spec.name} ships with data in it"


def test_every_schema_field_reaches_a_column():
    """A field with no column is a field the expert is never asked for."""
    for record_type in RECORD_TYPES:
        covered = set()
        for spec in sheets():
            if spec.record_type != record_type:
                continue
            if spec.is_child:
                covered.add(spec.parent_field)
            else:
                covered.update(column.path[0] for column in spec.columns)
        missing = set(property_order(record_type)) - covered
        assert not missing, f"{record_type} has no column for {sorted(missing)}"


def test_enum_cells_offer_only_the_allowed_values(tmp_path):
    from openpyxl import load_workbook

    path = tmp_path / "empty.xlsx"
    workbook.write(path, generated="2026-08-19")
    book = load_workbook(path)
    for spec in sheets():
        wanted = sum(1 for column in spec.columns if column.enum or column.kind == "boolean")
        found = len(book[spec.name].data_validations.dataValidation)
        assert found >= min(wanted, 1) or wanted == 0, spec.name


def test_the_enum_sheet_is_machinery_and_stays_hidden(tmp_path):
    from openpyxl import load_workbook

    path = tmp_path / "empty.xlsx"
    workbook.write(path, generated="2026-08-19")
    book = load_workbook(path)
    assert book[workbook.ENUM_SHEET].sheet_state == "hidden"


def test_the_sheet_names_are_the_gold_file_names():
    """So an expert reading `eval/gold/` recognises the sheet they filled in."""
    for record_type, sheet_name in SHEET_NAMES.items():
        assert goldset.FILE_FOR[record_type] == f"{sheet_name}.yaml"


# ---------------------------------------------------------------------------
# P8 — the round trip
# ---------------------------------------------------------------------------


def test_the_round_trip_preserves_every_populated_field(tmp_path, source_records):
    result = transcribe.read_workbook(_filled(tmp_path, source_records))
    assert result.problems == [], "\n".join(str(p) for p in result.problems)
    for record_type, records in source_records.items():
        transcribed = result.records[record_type]
        assert len(transcribed) == len(records)
        for before, after in zip(records, transcribed):
            for key, value in before.items():
                if value in (None, [], ""):
                    continue  # an optional empty is dropped on purpose
                assert after.get(key) == value, f"{record_type}.{key} did not survive"


def test_transcribed_records_are_in_schema_order(tmp_path, source_records):
    """So a gold file's diff reads like the template it came from."""
    result = transcribe.read_workbook(_filled(tmp_path, source_records))
    for record_type, records in result.records.items():
        order = property_order(record_type)
        for record in records:
            positions = [order.index(key) for key in record]
            assert positions == sorted(positions), f"{record_type} came out reordered"


def test_the_round_trip_is_a_fixed_point(tmp_path, source_records):
    once = transcribe.read_workbook(_filled(tmp_path, source_records, "a.xlsx"))
    twice = transcribe.read_workbook(_filled(tmp_path, once.records, "b.xlsx"))
    assert twice.records == once.records


def test_everything_transcribed_validates(tmp_path, source_records):
    result = transcribe.read_workbook(_filled(tmp_path, source_records))
    for record_type, records in result.records.items():
        for record in records:
            assert validate(record, record_type) == []


def test_a_list_cell_keeps_a_value_that_contains_a_separator(tmp_path):
    """Refs carry `/`, `(`, `~`, `#` and `.`; a comma-separated cell would be a
    data-loss bug waiting for the first value that uses the separator."""
    records = {
        "gold_concept": [
            {
                "id": "GC-001",
                "pref_label": "«label»",
                "alt_labels": ["one, with a comma", "two; with a semicolon"],
                "not_labels": [],
                "definition_sources": ["TMA1995/s41(3)(a)"],
                "approved_by": None,
                "approved_date": None,
            }
        ]
    }
    result = transcribe.read_workbook(_filled(tmp_path, records))
    assert result.records["gold_concept"][0]["alt_labels"] == [
        "one, with a comma",
        "two; with a semicolon",
    ]
    assert result.records["gold_concept"][0]["definition_sources"] == ["TMA1995/s41(3)(a)"]


# ---------------------------------------------------------------------------
# Reshape, never supply
# ---------------------------------------------------------------------------


def _relationship(**overrides):
    record = {
        "id": "GR-001",
        "subject": "«subject»",
        "predicate": "«predicate»",
        "object": "«object»",
        "source_ref": "TMM/Part20/5/5/1",
        "supporting_text": "«the sentence, verbatim»",
        "span": None,
        "source_content_hash": None,
        "tier": None,
        "modality": None,
        "approved_by": None,
        "approved_date": None,
    }
    record.update(overrides)
    return {"gold_relationship": [record]}


def test_a_blank_judgement_field_comes_out_blank_and_is_reported(tmp_path):
    """`modality` is must / may / should, and whether a "may" is possibility or
    permission is a legal reading (guide §5.4). Nothing here may decide it."""
    result = transcribe.read_workbook(_filled(tmp_path, _relationship()))
    record = result.records["gold_relationship"][0]
    assert record["modality"] is None
    assert record["tier"] is None
    assert record["span"] is None
    reported = {name for _, identifier, name in result.blanks if identifier == "GR-001"}
    assert {"modality", "tier", "span", "approved_by", "approved_date"} <= reported


def test_a_row_missing_a_non_nullable_field_is_rejected_not_stubbed(tmp_path):
    result = transcribe.read_workbook(
        _filled(tmp_path, _relationship(predicate=None))
    )
    assert result.records == {}
    assert any("predicate" in str(problem) for problem in result.problems)


def test_an_enum_value_outside_the_list_stops_the_row(tmp_path):
    """Not snapped to the nearest allowed value. "probably" is not "may"."""
    path = _filled(tmp_path, _relationship())
    from openpyxl import load_workbook

    book = load_workbook(path)
    sheet = book["relationships"]
    column = [c.value for c in sheet[1]].index("modality") + 1
    sheet.cell(row=2, column=column, value="probably")
    book.save(path)

    result = transcribe.read_workbook(path)
    assert result.records == {}
    assert any("probably" in str(problem) for problem in result.problems)


def test_half_a_span_is_rejected(tmp_path):
    path = _filled(tmp_path, _relationship())
    from openpyxl import load_workbook

    book = load_workbook(path)
    sheet = book["relationships"]
    column = [c.value for c in sheet[1]].index("span.start") + 1
    sheet.cell(row=2, column=column, value=0)
    book.save(path)

    result = transcribe.read_workbook(path)
    assert any("span.start and span.end" in str(problem) for problem in result.problems)


def test_a_record_that_does_not_validate_is_never_written(tmp_path):
    path = _filled(tmp_path, _relationship())
    from openpyxl import load_workbook

    book = load_workbook(path)
    sheet = book["relationships"]
    column = [c.value for c in sheet[1]].index("id") + 1
    sheet.cell(row=2, column=column, value="XX-001")
    book.save(path)

    result = transcribe.read_workbook(path)
    assert result.records == {}
    assert any("XX-001" in str(problem) for problem in result.problems)


def test_a_child_row_with_no_parent_is_rejected(tmp_path):
    records = {
        "gold_search_question": [
            {
                "id": "GS-001",
                "query": "«a query»",
                "uses_manual_terminology": False,
                "relevant": [{"ref": "TMM/Part20/5/5/1", "grade": 3}],
                "approved_by": None,
                "approved_date": None,
            }
        ]
    }
    path = _filled(tmp_path, records)
    from openpyxl import load_workbook

    book = load_workbook(path)
    sheet = book["GS--relevant"]
    sheet.cell(row=3, column=1, value="GS-999")
    sheet.cell(row=3, column=2, value="TMM/Part20/5/5/1")
    sheet.cell(row=3, column=3, value=3)
    book.save(path)

    result = transcribe.read_workbook(path)
    assert any("GS-999" in str(problem) for problem in result.problems)
    assert len(result.records["gold_search_question"][0]["relevant"]) == 1


def test_a_column_added_by_hand_stops_the_read(tmp_path, source_records):
    """A column the transcriber does not know is a field nobody collects."""
    path = _filled(tmp_path, source_records)
    from openpyxl import load_workbook

    book = load_workbook(path)
    sheet = book["entities"]
    sheet.cell(row=1, column=sheet.max_column + 1, value="confidence")
    book.save(path)

    with pytest.raises(transcribe.WorkbookMismatch) as error:
        transcribe.read_workbook(path)
    assert "confidence" in str(error.value)


# ---------------------------------------------------------------------------
# Writing into approved space
# ---------------------------------------------------------------------------


def test_a_dry_run_writes_nothing(tmp_path, source_records):
    result = transcribe.read_workbook(_filled(tmp_path, source_records))
    gold = tmp_path / "gold"
    outcomes = transcribe.write_records(result, gold, write=False)
    assert outcomes and all(outcome == "would write" for _, outcome in outcomes)
    assert not gold.exists()


def test_writing_twice_changes_nothing_the_second_time(tmp_path, source_records):
    """Re-running over unchanged input must leave git status clean."""
    result = transcribe.read_workbook(_filled(tmp_path, source_records))
    gold = tmp_path / "gold"
    first = transcribe.write_records(result, gold, write=True)
    assert all(outcome == "written" for _, outcome in first)
    second = transcribe.write_records(result, gold, write=True)
    assert all(outcome == "unchanged" for _, outcome in second)


def test_what_was_written_loads_back_as_a_gold_set(tmp_path, source_records):
    result = transcribe.read_workbook(_filled(tmp_path, source_records))
    gold = tmp_path / "gold"
    transcribe.write_records(result, gold, write=True)
    loaded = goldset.load(gold)
    assert loaded.unreadable == ()
    assert loaded.total == result.total


def test_an_empty_sheet_leaves_its_file_alone(tmp_path):
    """An empty sheet means "I have nothing for this yet", never "delete what is
    there". Filling one sheet must not wipe seven others."""
    gold = tmp_path / "gold"
    gold.mkdir()
    (gold / "concepts.yaml").write_text("- {id: GC-001}\n", encoding="utf-8")

    result = transcribe.read_workbook(_filled(tmp_path, _relationship()))
    assert "gold_concept" in result.empty_sheets
    transcribe.write_records(result, gold, write=True)
    assert (gold / "concepts.yaml").read_text(encoding="utf-8") == "- {id: GC-001}\n"


# ---------------------------------------------------------------------------
# Dates (ADR-0047)
# ---------------------------------------------------------------------------


def _date_column():
    for spec in sheets():
        for column in spec.columns:
            if column.header == "approved_date":
                return column
    raise AssertionError("no approved_date column")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-08-25", "2026-08-25"),
        (datetime.datetime(2026, 8, 25, 0, 0), "2026-08-25"),
        (datetime.date(2026, 8, 25), "2026-08-25"),
        ("25/08/2026", "2026-08-25"),
        ("25-08-2026", "2026-08-25"),
        (None, None),
        ("", None),
    ],
)
def test_a_date_the_sheet_can_only_mean_one_way_is_read(value, expected):
    """An Excel date cell and an unambiguous Australian one both convert.

    `25/08/2026` has no other reading — there is no month 25 — so converting it
    supplies nothing. It is the shape the schema wants, in the words that
    arrived.
    """
    assert transcribe._cell(_date_column(), value, "concepts", 2) == expected


@pytest.mark.parametrize("value", ["05/08/2026", "08/25/2026", "25 August 2026", "45890"])
def test_a_date_that_could_be_read_two_ways_is_refused_by_name(value):
    """Rule 6, on the one field where a silent misreading is invisible.

    A wrong `approved_date` looks exactly like a right one for ever: nothing
    downstream cross-checks it, so a day/month guess would be a provenance
    defect that never surfaces. The refusal names the cell and says what to
    write instead.
    """
    with pytest.raises(ValueError) as error:
        transcribe._cell(_date_column(), value, "concepts", 2)
    assert "approved_date" in str(error.value)
    assert "YYYY-MM-DD" in str(error.value)


def test_the_date_column_is_formatted_as_a_date(tmp_path):
    """So Excel parses what the reviewer types instead of storing the string."""
    from openpyxl import load_workbook

    path = tmp_path / "empty.xlsx"
    workbook.write(path, generated="2026-09-02")
    book = load_workbook(path)
    for spec in sheets():
        headers = [cell.value for cell in book[spec.name][1]]
        if "approved_date" not in headers:
            continue
        letter = get_column_letter(headers.index("approved_date") + 1)
        assert book[spec.name].column_dimensions[letter].number_format == "yyyy-mm-dd"


# ---------------------------------------------------------------------------
# The review gate (ADR-0048)
# ---------------------------------------------------------------------------


def test_an_intake_workbook_has_no_gate(tmp_path, source_records):
    """A workbook with no `verdict` column behaves exactly as it always did.

    The gate is about machine-written seed records crossing into approved space.
    An expert's own composed record is awaiting *approval*, not review, and the
    coverage report is what says so about it — holding it here would report the
    same gap twice and write nothing anybody could act on.
    """
    path = tmp_path / "filled.xlsx"
    book = workbook.build(generated="2026-09-02")
    workbook.fill(book, source_records)
    book.save(path)

    result = transcribe.read_workbook(path)
    assert not result.reviewed
    assert not result.held
    assert result.total == sum(len(records) for records in source_records.values())


def test_an_approved_record_may_not_point_at_an_unapproved_one(tmp_path):
    """Approval does not distribute over an interlinked set (ADR-0048).

    Sign a prohibition and not the question it bounds, and `eval/gold/` acquires
    a pointer to nothing — which `tmk-harness` calls a DEFECT, correctly, since
    a measurement standard with a dangling reference is not one. The gate closes
    transitively rather than letting the harness catch it afterwards.
    """
    result = transcribe.Transcription(reviewed=True)
    result.records = {
        "prohibited_use": [
            {"id": "PU-0001", "related_questions": ["GA-0001"]},
            {"id": "PU-0003", "related_questions": []},
        ],
        "gold_retrieval_question": [
            {"id": "GA-0002", "prohibited_conclusions": ["PU-0001"]},
        ],
    }
    transcribe.close_over_cross_references(result)

    # PU-0001 dangles on the unsigned GA-0001; GA-0002 then dangles on PU-0001.
    # PU-0003 names nothing and stands.
    assert [record["id"] for record in result.records["prohibited_use"]] == ["PU-0003"]
    assert "gold_retrieval_question" not in result.records
    assert {held.identifier for held in result.held} == {"PU-0001", "GA-0002"}
    assert all(held.reason == transcribe.DANGLING for held in result.held)


def test_a_pointer_into_what_is_already_approved_resolves(tmp_path):
    """A second round must not hold everything the first round approved."""
    result = transcribe.Transcription(reviewed=True)
    result.records = {
        "prohibited_use": [{"id": "PU-0009", "related_questions": ["GA-0001"]}],
    }
    transcribe.close_over_cross_references(result, frozenset({"GA-0001"}))
    assert [record["id"] for record in result.records["prohibited_use"]] == ["PU-0009"]
    assert not result.held


# ---------------------------------------------------------------------------
# Addenda (ADR-0051)
# ---------------------------------------------------------------------------


def _addendum(tmp_path, body: str):
    path = tmp_path / "confirmation.yaml"
    path.write_text(body, encoding="utf-8")
    return transcribe.read_addendum(path)


def test_an_instruction_signs_only_a_blank_approved_by_on_a_correct_row(tmp_path):
    """The narrowest thing that does the job (ADR-0051).

    A reviewer saying "everything I marked correct is signed TC" is a recorded
    human decision about a defined set of rows. It is not a decision about the
    rows they amended, rejected or never reached, and it does not overwrite a
    name already there.
    """
    addendum = _addendum(
        tmp_path,
        "reviewer: TC\nrecorded_on: 2026-09-02\nsign_unsigned_correct: true\n",
    )
    spec = next(s for s in sheets() if s.name == "concepts")

    cases = [
        ({"id": "GC-1", "verdict": "correct", "approved_by": None}, "TC"),
        ({"id": "GC-2", "verdict": "correct", "approved_by": "AB"}, "AB"),
        ({"id": "GC-3", "verdict": "amend", "approved_by": None}, None),
        ({"id": "GC-4", "verdict": "reject", "approved_by": None}, None),
        ({"id": "GC-5", "verdict": None, "approved_by": None}, None),
    ]
    for values, expected in cases:
        values.setdefault("approved_date", None)
        addendum.apply(spec, values)
        assert values["approved_by"] == expected, values["id"]


def test_an_instruction_settles_a_verdict_by_name_and_only_by_name(tmp_path):
    """`corrrect` is read as `correct` because a person said so about GE-0031 —
    not because it looks like it. There is no pattern and no typo table."""
    addendum = _addendum(
        tmp_path,
        "reviewer: TC\nrecorded_on: 2026-09-02\nverdicts:\n  GE-0031: correct\n",
    )
    spec = next(s for s in sheets() if s.name == "entities")

    named = {"id": "GE-0031", "verdict": "corrrect", "approved_by": None}
    assert addendum.apply(spec, named)
    assert named["verdict"] == "correct"

    unnamed = {"id": "GE-0032", "verdict": "corrrect", "approved_by": None}
    assert not addendum.apply(spec, unnamed)
    assert unnamed["verdict"] == "corrrect"


def test_an_instruction_does_not_reach_a_child_row(tmp_path):
    """A child row has no id to name and no approved_by of its own. Changing one
    costs a workbook, which is the right price for it."""
    addendum = _addendum(
        tmp_path,
        "reviewer: TC\nrecorded_on: 2026-09-02\nsign_unsigned_correct: true\n"
        "verdicts:\n  GS-0007: correct\n",
    )
    child = next(s for s in sheets() if s.is_child)
    values = {"parent_id": "GS-0007", "verdict": "rejext"}
    assert not addendum.apply(child, values)
    assert values["verdict"] == "rejext"


@pytest.mark.parametrize(
    ("body", "because"),
    [
        ("recorded_on: 2026-09-02\n", "reviewer"),
        ("reviewer: TC\n", "recorded_on"),
        ("reviewer: TC\nrecorded_on: 05/08/2026\n", "recorded_on"),
        ("reviewer: TC\nrecorded_on: 2026-09-02\nverdicts:\n  GE-1: corrrect\n", "GE-1"),
    ],
)
def test_an_instruction_it_cannot_act_on_exactly_is_refused(tmp_path, body, because):
    """Including a verdict *the instruction itself* misspells. Nothing here
    reads through a near-miss, wherever it arrives from."""
    with pytest.raises(transcribe.MalformedAddendum) as error:
        _addendum(tmp_path, body)
    assert because in str(error.value)

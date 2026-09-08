"""The authored store, and the line it exists to hold.

ADR-0079 let an agent write legal content. Everything that stops that content
being mistaken for expert knowledge is mechanical, and this is where the
mechanism is checked. Five properties, and every one of them fails silently if
it breaks — which is why they are tested rather than trusted:

1. **A record that cannot say what it is does not load quietly.** It is refused,
   named, and reported. A silently dropped authored record is indistinguishable
   from one that was never written, and no later evidence can tell them apart.
2. **`approved_by` is a defect here, not a gap.** On a signed record a null
   approver is the thing waiting to happen; on an authored one a *filled* one is
   the single failure the whole scheme exists to prevent.
3. **One id sequence across two stores.** The same id in both is two records
   under one name, and the graph would hold whichever it read second.
4. **`general_knowledge` is counted and never punished.** Forbidding the honest
   label would only buy a dishonest `corpus_inferred`.
5. **Nothing sums the two stores.** Not the harness, not the report, not the
   graph. The question a reader has is how much of this a person has read, and
   one number answers it in the flattering direction.

The fixtures are two whole directories, because the store's unit of work is a
directory. See `tests/fixtures/authored/README.md`.
"""

from __future__ import annotations

import pytest
import yaml

from tm_knowledge.authored import store
from tm_knowledge.config import REPO_ROOT, UPSTREAM_DIR
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.harness import AUTHORED_CHECKS, Severity, run
from tm_knowledge.stage0.schemas import RECORD_TYPES

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "authored"


def _skip_without_snapshot() -> None:
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")


# ---------------------------------------------------------------------------
# Reading the store
# ---------------------------------------------------------------------------


def test_every_record_type_has_exactly_one_authored_file():
    """The same names as `eval/gold/`, because ADR-0080 puts the same record
    types in both stores. A name that drifted would put a record type in one
    store the other could not read."""
    assert set(store.FILE_FOR) == set(RECORD_TYPES)
    assert store.AUTHORED_FILES == goldset.GOLD_FILES


def test_an_unrecognised_authored_file_is_an_error_not_a_skip(tmp_path):
    (tmp_path / "conepts.yaml").write_text("- {id: GC-901}\n", encoding="utf-8")
    loaded = store.load(tmp_path)
    assert loaded.held == 0
    assert [path.name for path, _ in loaded.unreadable] == ["conepts.yaml"]


def test_an_absent_authored_directory_is_not_an_error(tmp_path):
    """A repo that has authored nothing is the ordinary state, not a finding."""
    loaded = store.load(tmp_path / "nothing-here")
    assert loaded.held == 0
    assert loaded.total == 0
    assert loaded.unreadable == ()


def test_definitions_yaml_is_reported_rather_than_read(tmp_path):
    """`authored/README.md` names a definitions record type that has no schema
    and no id series. Until it has both, the store says so instead of guessing
    a shape for it — inventing a record type is authoring, not plumbing."""
    (tmp_path / "definitions.yaml").write_text("- {id: GD-0001}\n", encoding="utf-8")
    loaded = store.load(tmp_path)
    assert loaded.held == 0
    assert [path.name for path, _ in loaded.unreadable] == ["definitions.yaml"]


def test_the_envelope_is_split_off_before_the_record_is_read(tmp_path):
    """Every record-type schema is `additionalProperties: false`, so a record
    still carrying `authored:` fails its own schema — and the defect would say
    "unknown field", a true statement about the wrong problem."""
    loaded = store.load(FIXTURES / "sound")
    entry = loaded.of("gold_concept")[0]
    assert store.ENVELOPE_KEY not in entry.record
    assert entry.envelope["authoring_basis"] == "corpus_explicit"
    assert entry.record["pref_label"]


def test_a_record_with_no_envelope_is_refused_and_named():
    loaded = store.load(FIXTURES / "defective")
    refused = {entry.record_id for entry in loaded.refused}
    assert "GC-903" in refused, "a record with no `authored:` block must be refused"
    assert "GC-903" not in {record["id"] for record in loaded["gold_concept"]}, (
        "a refused record must not reach a caller as if it were usable"
    )
    assert loaded.held > loaded.total, (
        "held counts what is on disk and total counts what is usable; a store "
        "where they cannot differ cannot report a refusal"
    )


def test_a_refused_record_is_reported_not_dropped():
    """The whole difference between refusing and skipping."""
    report = run(authored_dir=FIXTURES / "defective")
    subjects = {
        finding.subject
        for finding in report.defects
        if finding.check == "authored-envelope"
    }
    assert "GC-903" in subjects


def test_review_status_is_never_defaulted(tmp_path):
    """A record with no envelope has not claimed to be unreviewed. It has
    claimed nothing, and that is the difference the harness must report."""
    (tmp_path / "concepts.yaml").write_text("- {id: GC-901}\n", encoding="utf-8")
    entry = store.load(tmp_path).of("gold_concept")[0]
    assert entry.review_status == "unknown"


# ---------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------


def test_the_sound_fixture_produces_no_defects():
    """A check that fires on everything is not a check."""
    _skip_without_snapshot()
    report = run(authored_dir=FIXTURES / "sound")
    authored_defects = [
        finding for finding in report.defects if finding.check in AUTHORED_CHECKS
    ]
    assert authored_defects == [], "\n".join(str(f) for f in authored_defects)


#: (record id, the check that must catch it). One record per fault, and the
#: test asserts *which* check caught it — a check that starts catching the wrong
#: thing fails here rather than passing quietly.
CAUGHT: tuple[tuple[str, str], ...] = (
    ("GC-903", "authored-envelope"),   # no `authored:` block at all
    ("GC-904", "authored-approval"),   # approved_by filled in
    ("GC-905", "authored-approval"),   # review_status: approved, sitting here
    ("GC-906", "authored-envelope"),   # claims the corpus and cites nothing
    ("GC-0001", "authored-ids"),       # the same id as a signed record
    ("GC-907", "authored-evidence"),   # evidence ref resolves to nothing
    ("GC-908", "authored-evidence"),   # the quote does not land at its span
    ("GC-909", "authored-evidence"),   # the passage has moved under the record
    ("GC-910", "authored-schema"),     # the record fails its own schema
    ("GE-911", "authored-ids"),        # a GE- id in the concepts file
)


@pytest.mark.parametrize("record_id,check", CAUGHT)
def test_every_defect_in_the_fixture_is_caught(record_id, check):
    _skip_without_snapshot()
    report = run(authored_dir=FIXTURES / "defective")
    caught = {
        (finding.subject, finding.check)
        for finding in report.defects
        if finding.check in AUTHORED_CHECKS
    }
    assert (record_id, check) in caught, (
        f"{record_id} was not caught by {check}. Caught: {sorted(caught)}"
    )


def test_the_defective_fixture_holds_no_surprises():
    """Every defective record is one the fixture means to hold. A record that
    is broken by accident makes the fixture a moving target."""
    _skip_without_snapshot()
    report = run(authored_dir=FIXTURES / "defective")
    subjects = {
        finding.subject
        for finding in report.defects
        if finding.check in AUTHORED_CHECKS
    }
    assert subjects == {record_id for record_id, _ in CAUGHT}


def test_an_id_in_both_stores_is_a_defect():
    """ADR-0080 consequence 1. The message has to name the other store, or the
    reader is left looking for a duplicate that is not in the file they opened."""
    report = run(authored_dir=FIXTURES / "defective")
    message = next(
        finding.message
        for finding in report.defects
        if finding.subject == "GC-0001" and finding.check == "authored-ids"
    )
    assert "signed" in message
    assert "concepts.yaml" in message
    assert "one sequence across both stores" in message


def test_general_knowledge_is_a_note_and_never_a_defect():
    """It is the honest label for an unevidenced judgement. Forbidding it would
    only buy a dishonest `corpus_inferred`."""
    _skip_without_snapshot()
    report = run(authored_dir=FIXTURES / "sound")
    notes = [
        finding for finding in report.notes if finding.check == "authored-basis"
    ]
    assert any(finding.subject == "GC-902" for finding in notes)
    assert any(finding.subject == "authored/" for finding in notes), (
        "the proportion is the figure worth watching, so it is reported as well "
        "as the individual records"
    )
    assert not [
        finding for finding in report.defects if finding.subject == "GC-902"
    ]


def test_an_unevidenced_record_is_counted_by_basis():
    loaded = store.load(FIXTURES / "sound")
    assert loaded.by_basis() == {"corpus_explicit": 1, "general_knowledge": 1}


def test_authored_defects_break_the_build():
    """A malformed authored record is not a Stage 0 gap that can be waited out.
    It is something that arrived wrong, and it exits 1 like any other defect."""
    _skip_without_snapshot()
    assert run(authored_dir=FIXTURES / "defective").exit_code == 1


# ---------------------------------------------------------------------------
# Nothing sums the two stores
# ---------------------------------------------------------------------------


def test_the_report_states_both_counts_and_adds_neither():
    _skip_without_snapshot()
    report = run(authored_dir=FIXTURES / "sound")
    line = report.stores()
    assert str(report.gold.total) in line
    assert str(report.authored.total) in line
    assert str(report.gold.total + report.authored.total) not in line, (
        "a summed figure is the merged store arriving by the back door "
        "(ADR-0080 consequence 3)"
    )
    assert "validated" in line


def test_the_authored_set_is_not_a_gold_set():
    """Deliberately not a subclass. A type that could be passed where a
    `GoldSet` is expected is how the sum gets written by accident."""
    assert not isinstance(store.load(FIXTURES / "sound"), goldset.GoldSet)


def test_the_completeness_gate_counts_signed_records_only(tmp_path):
    """A band met by authored records would report Stage 0 finished on the
    strength of work nobody has read."""
    _skip_without_snapshot()
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir()
    authored_dir = tmp_path / "authored"
    authored_dir.mkdir()
    records = [
        {
            "id": f"GC-{index:04d}",
            "pref_label": f"«label {index}»",
            "alt_labels": [],
            "not_labels": [],
            "definition_sources": ["TMM/Part20/5/5/1"],
            "approved_by": None,
            "approved_date": None,
            "authored": {
                "review_status": "unreviewed",
                "authored_by": "«model»-0.0",
                "authored_date": "2026-09-08",
                "authoring_basis": "corpus_explicit",
                "evidence": [{"ref": "TMM/Part20/5/5/1"}],
                "reasoning": "«why this reading»",
            },
        }
        for index in range(1, 61)
    ]
    (authored_dir / "concepts.yaml").write_text(
        yaml.safe_dump(records, allow_unicode=True), encoding="utf-8"
    )
    report = run(gold_dir=gold_dir, authored_dir=authored_dir, root=tmp_path)
    assert report.authored.total == 60
    short = [
        finding
        for finding in report.gaps
        if finding.check == "completeness" and finding.subject == "concepts.yaml"
    ]
    assert short, "60 authored concepts must not close the gold concepts deliverable"
    assert "0 of 50–100" in short[0].message


def test_this_repos_own_authored_store_holds_no_defects():
    """The live store, whatever it currently holds. Today it is empty, and the
    day it is not this is the test that says so before anything else does."""
    _skip_without_snapshot()
    report = run()
    authored_defects = [
        finding for finding in report.defects if finding.check in AUTHORED_CHECKS
    ]
    assert authored_defects == [], "\n".join(str(f) for f in authored_defects)

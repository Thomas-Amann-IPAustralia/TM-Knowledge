"""The blocker analysis — the arithmetic behind "which decision releases most".

`tmk-blockers` exists because the review queue is not a list: approval does not
distribute over an interlinked set (ADR-0048), so settling one record can free a
chain of others and settling a different one frees nothing. A report that gets
that arithmetic wrong is worse than no report, because it sends an expert's hour
at the wrong record and looks authoritative doing it.

Four properties are what make it trustworthy, and each is a test here.

1. **It agrees with the door.** The reasons come from `transcribe`'s own gate
   constants, and the report's held count reproduces what the transcriber held.
   If the two drift, the report is describing a gate that does not exist.
2. **It terminates on a cycle.** `GA-0002` names `PU-0013`, which names
   `GA-0002` straight back. The real data contains that triangle, and a naive
   reachability walk over it does not stop.
3. **It never invents an owner.** A record whose blocker is not itself
   actionable reports no owner rather than the nearest plausible one.
4. **A record that is rejected is not "waiting".** It is finished, negatively,
   and counting it as a dependent inverts the direction of the whole report.

The tests that read `review/` and `eval/gold/` are exercising the repo's real
state on purpose: this report's whole value is that it is true about *this*
corpus, and a fixture-only suite would pass over a repo whose ledgers had
drifted from its seed set.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tm_knowledge.stage0 import blockers, goldset, seed
from tm_knowledge.stage0.transcribe import (
    AMENDMENT_PENDING,
    CHILD_UNSETTLED,
    DANGLING,
    NOT_REVIEWED,
    REJECTED,
    UNSIGNED,
)


# ---------------------------------------------------------------------------
# Fixtures — a small interlinked set with every state in it
# ---------------------------------------------------------------------------


def _envelope(seed_id: str, record_type: str, record: dict) -> dict:
    return {
        "seed_id": seed_id,
        "record_type": record_type,
        "why_this_example": "a fixture",
        "record": record,
    }


def _seed_dir(tmp_path: Path) -> Path:
    """Six records: a question, three prohibitions and two retrieval questions."""
    defaults = {
        "provenance": {
            "extraction_method": "llm",
            "model": None,
            "generator": "test",
            "generated_on": "2026-09-02",
            "confidence": None,
            "review_status": "candidate",
        },
        "review": {
            "status": "unreviewed",
            "expert": None,
            "reviewed_on": None,
            "correction": None,
        },
    }
    files = {
        "competency-questions.seed.yaml": [
            _envelope(
                "SEED-CQ-9001",
                "competency_question",
                {"id": "CQ-9001", "question": "?", "approved_by": None},
            ),
            _envelope(
                "SEED-CQ-9002",
                "competency_question",
                {"id": "CQ-9002", "question": "?", "approved_by": None},
            ),
        ],
        "prohibited-uses.seed.yaml": [
            _envelope(
                "SEED-PU-9001",
                "prohibited_use",
                {"id": "PU-9001", "related_questions": ["CQ-9001"]},
            ),
            _envelope(
                "SEED-PU-9002",
                "prohibited_use",
                {"id": "PU-9002", "related_questions": ["CQ-9002"]},
            ),
        ],
        "retrieval-questions.seed.yaml": [
            _envelope(
                "SEED-GA-9001",
                "gold_retrieval_question",
                {"id": "GA-9001", "prohibited_conclusions": ["PU-9001"]},
            ),
            _envelope(
                "SEED-GA-9002",
                "gold_retrieval_question",
                {"id": "GA-9002", "prohibited_conclusions": ["PU-9002"]},
            ),
        ],
    }
    root = tmp_path / "seed"
    root.mkdir()
    for name, seeds in files.items():
        (root / name).write_text(
            yaml.safe_dump({"defaults": defaults, "seeds": seeds}), encoding="utf-8"
        )
    return root


def _ledger(tmp_path: Path, decisions: list[dict], child_marks: list[dict] | None = None):
    root = tmp_path / "decisions"
    root.mkdir(exist_ok=True)
    (root / "round.yaml").write_text(
        yaml.safe_dump(
            {
                "source_workbook": "round.xlsx",
                "decisions": decisions,
                "child_marks": child_marks or [],
            }
        ),
        encoding="utf-8",
    )
    return root


def _ruling(seed_id: str, verdict: str, **extra) -> dict:
    row = {
        "seed_id": seed_id,
        "verdict": verdict,
        "approved_by": "TC" if verdict == "correct" else None,
        "correction": None,
    }
    row.update(extra)
    return row


def _analysis(tmp_path, decisions, child_marks=None, gold=None):
    gold_dir = tmp_path / "gold"
    gold_dir.mkdir(exist_ok=True)
    if gold:
        for name, records in gold.items():
            (gold_dir / name).write_text(yaml.safe_dump(records), encoding="utf-8")
    return blockers.analyse(
        seed=seed.load(_seed_dir(tmp_path)),
        gold=goldset.load(gold_dir),
        decisions_dir=_ledger(tmp_path, decisions, child_marks),
    )


# ---------------------------------------------------------------------------
# The reasons agree with the gate
# ---------------------------------------------------------------------------


def test_every_gate_reason_has_a_statement_of_what_is_needed():
    """A reason the report cannot explain is a reason a reviewer cannot act on."""
    assert set(blockers.REASON_ORDER) == set(blockers.WHAT_IS_NEEDED)
    for reason in blockers.REASON_ORDER:
        assert blockers.WHAT_IS_NEEDED[reason].strip()


def test_an_unreviewed_record_is_not_reviewed(tmp_path):
    analysis = _analysis(tmp_path, [])
    assert analysis.total == 6
    assert {entry.reason for entry in analysis.entries} == {NOT_REVIEWED}


def test_the_reasons_follow_the_gates_own_precedence(tmp_path):
    """A record can satisfy several at once; the report says what the door says."""
    analysis = _analysis(
        tmp_path,
        [
            _ruling("SEED-CQ-9001", "reject", correction="not a question"),
            _ruling("SEED-CQ-9002", "amend", correction="reword it"),
            # Correct and signed, but names CQ-9001, which is not approved.
            _ruling("SEED-PU-9001", "correct"),
            # Correct and unsigned — a judgement made and not signed.
            _ruling("SEED-PU-9002", "correct", approved_by=None),
        ],
    )
    assert analysis["CQ-9001"].reason == REJECTED
    assert analysis["CQ-9002"].reason == AMENDMENT_PENDING
    assert analysis["PU-9001"].reason == DANGLING
    assert analysis["PU-9002"].reason == UNSIGNED


def test_an_amendment_is_quoted_not_paraphrased(tmp_path):
    analysis = _analysis(
        tmp_path, [_ruling("SEED-CQ-9002", "amend", correction="the exact words")]
    )
    assert analysis["CQ-9002"].correction == "the exact words"
    assert "the exact words" in blockers.render(analysis)


def test_a_marked_child_row_holds_a_signed_parent(tmp_path):
    analysis = _analysis(
        tmp_path,
        [_ruling("SEED-CQ-9001", "correct")],
        child_marks=[
            {
                "parent_id": "CQ-9001",
                "sheet": "CQ--child",
                "row": 4,
                "verdict": "amend",
                "correction": "grade is wrong",
            }
        ],
    )
    assert analysis["CQ-9001"].reason == CHILD_UNSETTLED
    assert "grade is wrong" in analysis["CQ-9001"].detail


def test_a_rejected_child_row_holds_nothing(tmp_path):
    """`reject` on a child row drops that row from its parent — it does not hold it."""
    analysis = _analysis(
        tmp_path,
        [_ruling("SEED-CQ-9001", "correct")],
        child_marks=[
            {
                "parent_id": "CQ-9001",
                "sheet": "CQ--child",
                "row": 4,
                "verdict": "reject",
                "correction": None,
            }
        ],
    )
    assert analysis["CQ-9001"].reason != CHILD_UNSETTLED


def test_a_verdict_cell_nothing_can_read_is_reported_not_interpreted(tmp_path):
    analysis = _analysis(
        tmp_path,
        [],
        child_marks=[
            {
                "parent_id": "CQ-9001",
                "sheet": "CQ--child",
                "row": 9,
                "verdict": "rejext",
                "correction": None,
            }
        ],
    )
    assert [mark.verdict for mark in analysis.unparseable_marks] == ["rejext"]
    assert "rejext" in blockers.render(analysis)


# ---------------------------------------------------------------------------
# The dependency arithmetic
# ---------------------------------------------------------------------------


def test_holding_is_transitive(tmp_path):
    """CQ-9001 holds PU-9001, which holds GA-9001. So CQ-9001 holds both."""
    analysis = _analysis(
        tmp_path, [_ruling("SEED-PU-9001", "correct"), _ruling("SEED-GA-9001", "correct")]
    )
    assert set(analysis.holds["CQ-9001"]) == {"PU-9001", "GA-9001"}
    assert analysis.releases("CQ-9001") == {
        "prohibited_use": 1,
        "gold_retrieval_question": 1,
    }


def test_a_record_never_holds_itself(tmp_path):
    analysis = _analysis(
        tmp_path, [_ruling("SEED-PU-9001", "correct"), _ruling("SEED-GA-9001", "correct")]
    )
    for record_id, held in analysis.holds.items():
        assert record_id not in held


def test_a_rejected_record_is_not_waiting_on_what_it_names(tmp_path):
    """A rejection is finished. Counting it as a dependent inverts the report."""
    analysis = _analysis(tmp_path, [_ruling("SEED-PU-9001", "reject")])
    assert "PU-9001" not in analysis.holds.get("CQ-9001", ())


def test_a_pointer_at_a_rejected_record_puts_the_pointer_on_the_worklist(tmp_path):
    """Nothing else can satisfy it, so this record repoints or it withdraws."""
    analysis = _analysis(
        tmp_path,
        [_ruling("SEED-CQ-9001", "reject"), _ruling("SEED-PU-9001", "correct")],
    )
    assert "PU-9001" in {entry.record_id for entry in analysis.actionable}
    assert "CQ-9001" not in {entry.record_id for entry in analysis.actionable}


def test_a_record_dangling_on_something_merely_unreviewed_is_not_a_decision(tmp_path):
    """There is nothing to decide on it: it moves when the record it names moves."""
    analysis = _analysis(tmp_path, [_ruling("SEED-PU-9001", "correct")])
    assert "PU-9001" not in {entry.record_id for entry in analysis.actionable}
    assert "CQ-9001" in {entry.record_id for entry in analysis.actionable}


def _make_cycle(root: Path) -> None:
    """PU-9001 names GA-9001 and GA-9001 names PU-9001 — the GA-0002/PU-0013 shape."""
    path = root / "prohibited-uses.seed.yaml"
    document = yaml.safe_load(path.read_text())
    document["seeds"][0]["record"]["related_questions"] = ["GA-9001"]
    path.write_text(yaml.safe_dump(document), encoding="utf-8")


def test_a_mutual_reference_terminates(tmp_path):
    """The real set contains GA-0002 ↔ PU-0013. A naive walk over it never stops."""
    root = _seed_dir(tmp_path)
    _make_cycle(root)
    analysis = blockers.analyse(
        seed=seed.load(root),
        gold=goldset.load(tmp_path / "empty-gold"),
        decisions_dir=_ledger(
            tmp_path,
            [_ruling("SEED-PU-9001", "correct"), _ruling("SEED-GA-9001", "correct")],
        ),
    )
    assert analysis.total == 6
    assert ("GA-9001", "PU-9001") in analysis.cycles
    assert "PU-9001" in analysis.holds["GA-9001"]
    assert "GA-9001" in analysis.holds["PU-9001"]
    blockers.render(analysis, generated="2026-09-02")


def test_a_cycle_is_settled_by_the_decision_inside_it(tmp_path):
    """Nothing outside GA-0002/PU-0013/PU-0014 releases any of it; the amendment does."""
    root = _seed_dir(tmp_path)
    _make_cycle(root)
    analysis = blockers.analyse(
        seed=seed.load(root),
        gold=goldset.load(tmp_path / "empty-gold"),
        decisions_dir=_ledger(
            tmp_path,
            [
                _ruling("SEED-PU-9001", "correct"),
                _ruling("SEED-GA-9001", "amend", correction="reword the answer"),
            ],
        ),
    )
    # GA-9001 waits on PU-9001 and is waited on by it, so demanding an unblocked
    # root would have hidden the one record with a decision on it.
    assert "GA-9001" in {entry.record_id for entry in analysis.actionable}
    assert "PU-9001" not in {entry.record_id for entry in analysis.actionable}


def test_an_approved_record_is_no_longer_a_blocker(tmp_path):
    """The gold set is what satisfies a pointer — nothing in review/seed/ does."""
    analysis = _analysis(
        tmp_path,
        [_ruling("SEED-PU-9001", "correct")],
        gold={"competency-questions.yaml": [{"id": "CQ-9001", "question": "?"}]},
    )
    assert analysis["PU-9001"].waits_on == ()
    assert "CQ-9001" not in analysis.holds


def test_a_pointer_at_nothing_at_all_is_a_defect_not_a_queue_entry(tmp_path):
    root = _seed_dir(tmp_path)
    document = yaml.safe_load((root / "prohibited-uses.seed.yaml").read_text())
    document["seeds"][0]["record"]["related_questions"] = ["CQ-9999"]
    (root / "prohibited-uses.seed.yaml").write_text(
        yaml.safe_dump(document), encoding="utf-8"
    )
    analysis = blockers.analyse(
        seed=seed.load(root),
        gold=goldset.load(tmp_path / "empty-gold"),
        decisions_dir=_ledger(tmp_path, []),
    )
    assert analysis.unknown_targets
    assert "CQ-9999" in analysis.unknown_targets[0][1]


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------


def test_the_report_names_no_owner_it_cannot_justify(tmp_path):
    """Everything on the carried list points at a record on the worklist."""
    analysis = _analysis(
        tmp_path,
        [_ruling("SEED-PU-9001", "correct"), _ruling("SEED-GA-9001", "correct")],
    )
    on_the_path = {entry.record_id for entry in analysis.actionable}
    for entry in analysis.entries:
        for owner in blockers._roots_for(analysis, entry.record_id):
            assert owner in on_the_path


def test_the_report_proposes_no_answers(tmp_path):
    """It says what the gate needs, never what the record should say."""
    analysis = _analysis(
        tmp_path,
        [_ruling("SEED-CQ-9001", "reject"), _ruling("SEED-PU-9001", "correct")],
    )
    text = blockers.render(analysis, generated="2026-09-02")
    assert "expert call" in text
    assert "repoint it or" in text


def test_the_report_is_deterministic(tmp_path):
    analysis = _analysis(tmp_path, [_ruling("SEED-PU-9001", "correct")])
    first = blockers.render(analysis, generated="2026-09-02")
    second = blockers.render(analysis, generated="2026-09-02")
    assert first == second


def test_an_empty_queue_renders_without_a_worklist(tmp_path):
    root = tmp_path / "nothing"
    root.mkdir()
    analysis = blockers.analyse(
        seed=seed.load(root),
        gold=goldset.load(tmp_path / "empty-gold"),
        decisions_dir=_ledger(tmp_path, []),
    )
    assert analysis.total == 0
    assert "ordinary review queue" in blockers.render(analysis)


# ---------------------------------------------------------------------------
# Against the repo's own state
# ---------------------------------------------------------------------------


def test_the_report_accounts_for_every_surviving_seed_record():
    """Every record in review/seed/ has exactly one reason, and none is blank."""
    analysis = blockers.analyse()
    if not analysis.total:
        pytest.skip("review/seed/ is empty")
    assert len(analysis.entries) == seed.load().total
    assert {entry.record_id for entry in analysis.entries} == {
        envelope.record_id for envelope in seed.load().envelopes
    }
    for entry in analysis.entries:
        assert entry.reason in blockers.REASON_ORDER


def test_nothing_in_the_gold_set_is_still_on_the_queue():
    """A record cannot be both approved and awaiting review (ADR-0043 §6)."""
    analysis = blockers.analyse()
    gold = goldset.load()
    approved = {
        str(record["id"])
        for record_type in ("competency_question", "prohibited_use")
        for record in gold[record_type]
        if record.get("id")
    }
    assert approved.isdisjoint({entry.record_id for entry in analysis.entries})


def test_no_pointer_in_the_repo_names_a_record_that_exists_nowhere():
    analysis = blockers.analyse()
    assert analysis.unknown_targets == ()


def test_the_subset_filter_takes_either_id_form():
    """`tmk-seed --only` is fed from `tmk-blockers --ids`, which prints record ids."""
    whole = seed.load()
    if not whole.envelopes:
        pytest.skip("review/seed/ is empty")
    first = whole.envelopes[0]
    by_record, missing = whole.subset([first.record_id])
    by_seed, _ = whole.subset([first.seed_id])
    assert missing == ()
    assert by_record.envelopes == by_seed.envelopes == (first,)


def test_the_subset_filter_reports_a_name_it_did_not_find():
    """A round scoped to six records and rendered over five is a silent loss."""
    _, missing = seed.load().subset(["CQ-0013", "NOT-A-RECORD"])
    assert "NOT-A-RECORD" in missing

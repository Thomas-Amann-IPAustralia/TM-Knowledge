"""Reconciliation — recording a review round, then retiring what it settled.

Two things are being protected here, and neither is about the ledger's prose.

The first is that a rejection **survives**. A reviewer's "this record should not
exist, because the words *this section* mean something different every time they
appear" is the most expensive judgement in the round and the easiest to lose:
delete the row and it is gone. `review/README.md` says why that matters beyond
tidiness — Stage 10 reads rejections as negative examples.

The second is that pruning `review/seed/` **cannot damage a seed file**. The
files are hand-written, and their comments carry the entity annotation rule and
the candidate predicate list — the two decisions the whole set turns on. So the
prune edits lines rather than re-serialising, and every rewrite is parsed back
and compared before it is written (ADR-0049). The tests below try to break that
in the ways it can actually break: an entry in the middle, the first entry, the
last entry, and a file that empties out.

No snapshot needed: nothing here resolves a ref.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

pytest.importorskip("openpyxl", reason="the intake path needs `pip install -e '.[intake]'`")

from tm_knowledge.stage0 import reconcile, seed  # noqa: E402

FILE = textwrap.dedent(
    """\
    # ═══════════════════════════════════════════════════════════════════════
    # SEED EXAMPLES — gold concepts.  NOT PROJECT CONTENT.  NOT APPROVED.
    #
    # The annotation rule this whole set turns on lives in a comment, which is
    # why the prune must not re-serialise the document.
    # ═══════════════════════════════════════════════════════════════════════

    defaults:
      provenance:
        extraction_method: llm
        model: null
        generator: test
        generated_on: "2026-08-21"
        confidence: null
        review_status: candidate
      review:
        status: unreviewed
        expert: null
        reviewed_on: null
        correction: null

    seeds:

      # ── the core of the section ──────────────────────────────────────────
      - seed_id: SEED-GC-9001
        record_type: gold_concept
        why_this_example: the first
        record:
          id: GC-9001
          pref_label: connotation
          alt_labels: []
          not_labels: []
          definition_sources:
            - TMM/Part29/2/2/1~1
          approved_by: null
          approved_date: null

      - seed_id: SEED-GC-9002
        record_type: gold_concept
        why_this_example: the middle
        record:
          id: GC-9002
          pref_label: deception
          alt_labels: []
          not_labels: []
          definition_sources:
            - TMM/Part29/2/2/2
          approved_by: null
          approved_date: null

      - seed_id: SEED-GC-9003
        record_type: gold_concept
        why_this_example: the last
        record:
          id: GC-9003
          pref_label: confusion
          alt_labels: []
          not_labels: []
          definition_sources:
            - TMM/Part29/2/2/3
          approved_by: null
          approved_date: null
    """
)


@pytest.fixture
def seed_dir(tmp_path: Path) -> Path:
    (tmp_path / "concepts.seed.yaml").write_text(FILE, encoding="utf-8")
    return tmp_path


def _labels(path: Path) -> list[str]:
    loaded = seed.load(path.parent)
    return [e.record["pref_label"] for e in loaded.envelopes]


@pytest.mark.parametrize(
    ("approved", "left"),
    [
        ({"GC-9001"}, ["deception", "confusion"]),
        ({"GC-9002"}, ["connotation", "confusion"]),
        ({"GC-9003"}, ["connotation", "deception"]),
        ({"GC-9001", "GC-9003"}, ["deception"]),
    ],
)
def test_pruning_removes_exactly_the_approved_records(seed_dir, approved, left):
    """Whichever entry moved — first, middle, last, or two of them."""
    (result,) = reconcile.prune(approved, seed_dir, write=True)
    assert result.outcome == "rewritten"
    assert result.remaining == len(left)
    assert _labels(seed_dir / "concepts.seed.yaml") == left


def test_pruning_keeps_the_comments_the_set_turns_on(seed_dir):
    reconcile.prune({"GC-9001"}, seed_dir, write=True)
    text = (seed_dir / "concepts.seed.yaml").read_text(encoding="utf-8")
    assert "NOT PROJECT CONTENT" in text
    assert "why the prune must not re-serialise" in text
    assert "── the core of the section ──" in text


def test_a_file_whose_records_all_moved_is_deleted(seed_dir):
    """Two versions of one record, one approved and one not, is the state
    ADR-0043 consequence 6 forbids. An emptied seed file is not kept as a stub."""
    (result,) = reconcile.prune({"GC-9001", "GC-9002", "GC-9003"}, seed_dir, write=True)
    assert result.outcome == "deleted"
    assert not (seed_dir / "concepts.seed.yaml").exists()


def test_a_dry_run_writes_nothing(seed_dir):
    before = (seed_dir / "concepts.seed.yaml").read_text(encoding="utf-8")
    results = reconcile.prune({"GC-9001"}, seed_dir, write=False)
    assert results[0].retired == ("SEED-GC-9001",)
    assert (seed_dir / "concepts.seed.yaml").read_text(encoding="utf-8") == before


def test_nothing_approved_means_nothing_touched(seed_dir):
    (result,) = reconcile.prune(set(), seed_dir, write=True)
    assert result.outcome == "unchanged"
    assert _labels(seed_dir / "concepts.seed.yaml") == [
        "connotation",
        "deception",
        "confusion",
    ]


def test_a_rewrite_that_would_change_a_record_is_refused(seed_dir, monkeypatch):
    """The proof, not the method, is what makes line surgery acceptable."""

    real = reconcile._remove_entries

    def _corrupt(text: str, retiring: set[str]) -> str:
        return real(text, retiring).replace(
            "pref_label: deception", "pref_label: DECEPTION"
        )

    monkeypatch.setattr(reconcile, "_remove_entries", _corrupt)
    with pytest.raises(reconcile.ReconcileRefused) as error:
        reconcile.prune({"GC-9001"}, seed_dir, write=True)
    assert "changed during the rewrite" in str(error.value)
    assert "deception" in (seed_dir / "concepts.seed.yaml").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The ledger
# ---------------------------------------------------------------------------


def _round() -> reconcile.Round:
    return reconcile.Round(
        workbook=Path("260825_ONTOLOGY-Stage-0-Seed.xlsx"),
        outcomes=[
            reconcile.Outcome(
                "gold_concept", "GC-9001", "SEED-GC-9001", "correct", None,
                "TC", "2026-08-25", "approved",
            ),
            reconcile.Outcome(
                "gold_entity", "GE-9008", "SEED-GE-9008", "reject",
                "Lacks specific context to be useful.", None, None, "rejected",
            ),
            reconcile.Outcome(
                "gold_entity", "GE-9031", "SEED-GE-9031", "corrrect", None,
                None, None, "unparseable", "verdict cell reads 'corrrect'",
            ),
        ],
        child_marks=[("GS-9001", "GS--relevant", 4, "amend", "3, highly relevant")],
        reviewers=("TC",),
    )


def test_the_ledger_keeps_the_reviewers_own_words():
    text = reconcile.render_ledger(_round(), as_of="2026-09-02")
    assert "Lacks specific context to be useful." in text
    assert "3, highly relevant" in text
    assert "GE-9031" in text


def test_the_ledger_data_is_one_entry_per_decision():
    data = reconcile.ledger_data(_round(), as_of="2026-09-02")
    assert data["counts"] == {
        "approved": 1,
        "held": 0,
        "rejected": 1,
        "unparseable": 1,
    }
    assert [entry["id"] for entry in data["decisions"]] == [
        "GC-9001",
        "GE-9008",
        "GE-9031",
    ]
    assert data["reviewers"] == ["TC"]


def test_the_ledger_is_named_after_the_workbook_it_came_from(tmp_path):
    markdown, data = reconcile.ledger_paths(
        Path("data/derived/260825_ONTOLOGY-Stage-0-Seed.xlsx"), tmp_path
    )
    assert markdown.name == "260825-ontology-stage-0-seed.md"
    assert data.name == "260825-ontology-stage-0-seed.yaml"

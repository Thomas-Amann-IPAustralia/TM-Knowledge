"""The seed example set — ADR-0043's guard rails, as tests.

The seed set inverts CLAUDE.md rule 1 on purpose: an agent writes candidate
legal content so that an expert can correct it rather than compose it. That
inversion is only safe while three things stay true, and each of them is a test
here rather than a promise in a README.

1. **A seed record can never look approved.** `approved_by` and `approved_date`
   are null on every record in `review/seed/`, and a set that carries either is
   a defect that stops the tool. This is the load-bearing one: the whole risk of
   a seed set is that it silently becomes a gold set.
2. **A seed file cannot be counted as a gold file.** The `.seed.yaml` names are
   not names `goldset.py` reads, so a misfiled seed file stops the harness
   instead of contaminating a measurement (ADR-0032).
3. **Spans are computed, never asserted.** A surface that does not appear in its
   chunk is a defect; a surface that appears twice without an occurrence hint is
   a defect too, and is never resolved to the first hit (rule 6).

The corpus-wide checks skip cleanly without a snapshot, in the same way the
harness suite does — the tests that need `data/upstream/` say so.
"""

from __future__ import annotations

import pytest
import yaml

from tm_knowledge.config import REPO_ROOT, UPSTREAM_DIR
from tm_knowledge.stage0 import goldset, seed
from tm_knowledge.stage0.harness import Severity
from tm_knowledge.stage0.intake import REVIEW_COLUMNS, sheets
from tm_knowledge.stage0.schemas import ID_PREFIXES, RECORD_TYPES

SEED_DIR = REPO_ROOT / "review" / "seed"


def _skip_without_snapshot() -> None:
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")


def _corpus():
    from tm_knowledge.upstream.loader import load_corpus

    return load_corpus()


def _write(tmp_path, filename: str, seeds: list[dict], defaults: dict | None = None):
    document = {
        "defaults": defaults
        if defaults is not None
        else {
            "provenance": {
                "extraction_method": "llm",
                "model": None,
                "generator": "test",
                "generated_on": "2026-08-21",
                "confidence": None,
                "review_status": "candidate",
            },
            "review": {
                "status": "unreviewed",
                "expert": None,
                "reviewed_on": None,
                "correction": None,
            },
        },
        "seeds": seeds,
    }
    (tmp_path / filename).write_text(yaml.safe_dump(document), encoding="utf-8")


def _entity_seed(**overrides) -> dict:
    record = {
        "id": "GE-9001",
        "surface": "decision maker",
        "type": "LegalConcept",
        "source_ref": "TMM/Part29/1#1",
        "span": None,
        "source_content_hash": None,
        "resolves_to": None,
        "notes": None,
        "approved_by": None,
        "approved_date": None,
    }
    record.update(overrides.pop("record", {}))
    envelope = {
        "seed_id": "SEED-GE-9001",
        "record_type": "gold_entity",
        "why_this_example": "a fixture",
        "record": record,
    }
    envelope.update(overrides)
    return envelope


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------


def test_seed_filenames_are_not_gold_filenames():
    """A seed file dropped into eval/gold/ must stop the harness, not be read."""
    assert set(seed.SEED_FILES).isdisjoint(set(goldset.GOLD_FILES))
    assert set(seed.SEED_FILES.values()) == set(RECORD_TYPES)


def test_an_unrecognised_file_is_reported_not_skipped(tmp_path):
    (tmp_path / "entites.seed.yaml").write_text("seeds: []\n", encoding="utf-8")
    loaded = seed.load(tmp_path)
    assert loaded.total == 0
    assert [path.name for path, _ in loaded.unreadable] == ["entites.seed.yaml"]


def test_an_absent_seed_directory_is_not_an_error(tmp_path):
    loaded = seed.load(tmp_path / "nothing-here")
    assert loaded.total == 0
    assert loaded.unreadable == ()


def test_file_defaults_are_materialised_onto_every_envelope(tmp_path):
    """Provenance stated once at the top must reach every record (rule 8)."""
    _write(tmp_path, "entities.seed.yaml", [_entity_seed()])
    loaded = seed.load(tmp_path)
    (envelope,) = loaded.envelopes
    assert envelope.provenance["extraction_method"] == "llm"
    assert envelope.provenance["generator"] == "test"
    assert envelope.verdict == "unreviewed"


def test_a_record_level_override_beats_the_file_default(tmp_path):
    _write(tmp_path, "entities.seed.yaml", [_entity_seed(provenance={"confidence": 0.4})])
    (envelope,) = seed.load(tmp_path).envelopes
    assert envelope.provenance["confidence"] == 0.4
    assert envelope.provenance["extraction_method"] == "llm"


def test_a_bare_list_is_rejected(tmp_path):
    """The shape is a mapping with defaults and seeds — a list has no provenance."""
    (tmp_path / "entities.seed.yaml").write_text("- {seed_id: x}\n", encoding="utf-8")
    loaded = seed.load(tmp_path)
    assert loaded.total == 0
    assert loaded.unreadable


# ---------------------------------------------------------------------------
# The check that keeps a seed set from becoming a gold set
# ---------------------------------------------------------------------------


def test_an_approved_seed_record_is_a_defect(tmp_path):
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed(record={"approved_by": "someone", "approved_date": "2026-08-21"})],
    )
    findings = seed.check(seed.load(tmp_path))
    approval = [f for f in findings if f.check == "seed-approval"]
    assert len(approval) == 2
    assert all(f.severity is Severity.DEFECT for f in approval)


def test_the_shipped_seed_set_has_no_approved_record():
    """The real directory, not a fixture. This is the one that must never fail."""
    loaded = seed.load()
    if not loaded.envelopes:
        pytest.skip("no seed set present")
    for envelope in loaded.envelopes:
        assert envelope.record.get("approved_by") is None, envelope.seed_id
        assert envelope.record.get("approved_date") is None, envelope.seed_id


def test_a_verdict_without_a_reviewer_is_a_defect(tmp_path):
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed(review={"status": "correct", "expert": None})],
    )
    findings = seed.check(seed.load(tmp_path))
    assert any(
        f.check == "seed-envelope" and "no reviewer named" in f.message for f in findings
    )


def test_a_verdict_outside_the_vocabulary_is_a_defect(tmp_path):
    _write(tmp_path, "entities.seed.yaml", [_entity_seed(review={"status": "maybe"})])
    findings = seed.check(seed.load(tmp_path))
    assert any(f.check == "seed-envelope" and "review.status" in f.message for f in findings)


def test_an_empty_why_this_example_is_a_defect(tmp_path):
    _write(tmp_path, "entities.seed.yaml", [_entity_seed(why_this_example="")])
    findings = seed.check(seed.load(tmp_path))
    assert any(
        f.check == "seed-envelope" and "why_this_example" in f.message for f in findings
    )


def test_missing_provenance_is_a_defect(tmp_path):
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed()],
        defaults={"provenance": {"extraction_method": "llm"}, "review": {}},
    )
    findings = seed.check(seed.load(tmp_path))
    assert any(f.check == "seed-envelope" and "provenance" in f.message for f in findings)


def test_a_duplicate_seed_id_is_a_defect(tmp_path):
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed(), _entity_seed(record={"id": "GE-9002"})],
    )
    findings = seed.check(seed.load(tmp_path))
    assert any(f.check == "seed-envelope" and "already used" in f.message for f in findings)


def test_an_id_in_the_wrong_series_is_a_defect(tmp_path):
    _write(tmp_path, "entities.seed.yaml", [_entity_seed(record={"id": "GC-9001"})])
    findings = seed.check(seed.load(tmp_path))
    assert any(f.check == "seed-identifier" for f in findings)
    assert ID_PREFIXES["gold_entity"] == "GE"


def test_a_dangling_cross_reference_is_a_defect(tmp_path):
    _write(
        tmp_path,
        "reasoning-expected.seed.yaml",
        [
            {
                "seed_id": "SEED-GX-9001",
                "record_type": "reasoning_expectation",
                "why_this_example": "a fixture",
                "record": {
                    "id": "GX-9001",
                    "given": ["TMM/Part29/1#1"],
                    "expected_inferences": [],
                    "must_not_infer": ["PU-9999"],
                    "tier": 1,
                    "explanation_required": True,
                    "approved_by": None,
                    "approved_date": None,
                },
            }
        ],
    )
    findings = seed.check(seed.load(tmp_path))
    assert any(f.check == "seed-cross-reference" for f in findings)


# ---------------------------------------------------------------------------
# Spans — computed, never asserted
# ---------------------------------------------------------------------------


@pytest.mark.snapshot
def test_a_span_is_filled_from_the_snapshot(tmp_path):
    _skip_without_snapshot()
    _write(tmp_path, "entities.seed.yaml", [_entity_seed()])
    resolutions, findings = seed.resolve(seed.load(tmp_path), _corpus())
    assert not findings
    (resolution,) = resolutions
    start, end = resolution.record["span"]
    assert resolution.passage_text[start:end] == "decision maker"
    assert resolution.record["source_content_hash"].startswith("sha256:")


@pytest.mark.snapshot
def test_a_surface_that_is_not_in_the_passage_is_a_defect(tmp_path):
    _skip_without_snapshot()
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed(record={"surface": "Connotation Which Is Not There"})],
    )
    _, findings = seed.resolve(seed.load(tmp_path), _corpus())
    assert any(f.check == "seed-span" and "does not appear" in f.message for f in findings)


@pytest.mark.snapshot
def test_an_ambiguous_surface_is_reported_not_guessed(tmp_path):
    """Two mentions and no hint must stop, never resolve to the first (rule 6)."""
    _skip_without_snapshot()
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed(record={"surface": "likely to deceive or cause confusion"})],
    )
    resolutions, findings = seed.resolve(seed.load(tmp_path), _corpus())
    assert any(f.check == "seed-span" and "appears 2 times" in f.message for f in findings)
    assert resolutions[0].record["span"] is None


@pytest.mark.snapshot
def test_an_occurrence_hint_selects_the_right_mention(tmp_path):
    _skip_without_snapshot()
    surface = "likely to deceive or cause confusion"
    _write(
        tmp_path,
        "entities.seed.yaml",
        [
            _entity_seed(record={"surface": surface}, locate={"occurrence": 1}),
            _entity_seed(
                seed_id="SEED-GE-9002",
                record={"id": "GE-9002", "surface": surface},
                locate={"occurrence": 2},
            ),
        ],
    )
    resolutions, findings = seed.resolve(seed.load(tmp_path), _corpus())
    assert not findings
    first, second = (r.record["span"] for r in resolutions)
    assert first != second
    assert first[0] < second[0]


@pytest.mark.snapshot
def test_an_occurrence_out_of_range_is_a_defect(tmp_path):
    _skip_without_snapshot()
    _write(tmp_path, "entities.seed.yaml", [_entity_seed(locate={"occurrence": 9})])
    _, findings = seed.resolve(seed.load(tmp_path), _corpus())
    assert any(f.check == "seed-span" and "locate.occurrence" in f.message for f in findings)


@pytest.mark.snapshot
def test_an_unresolvable_ref_is_a_defect(tmp_path):
    _skip_without_snapshot()
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed(record={"source_ref": "TMM/Part29/9/9/999"})],
    )
    findings = seed.check(seed.load(tmp_path), _corpus())
    assert any("resolves to nothing" in f.message for f in findings)


@pytest.mark.snapshot
def test_a_case_ref_is_a_note_and_not_a_defect(tmp_path):
    """No decision text exists anywhere in the programme (Q-11)."""
    _skip_without_snapshot()
    _write(
        tmp_path,
        "entities.seed.yaml",
        [_entity_seed(record={"resolves_to": "CASE/2000/FCA/720"})],
    )
    findings = seed.check(seed.load(tmp_path), _corpus())
    case_findings = [f for f in findings if "case citation" in f.message]
    assert case_findings
    assert all(f.severity is Severity.NOTE for f in case_findings)


# ---------------------------------------------------------------------------
# The shipped set
# ---------------------------------------------------------------------------


@pytest.mark.snapshot
def test_the_shipped_seed_set_is_free_of_defects():
    """Every ref resolves, every span lands, every pointer points at something."""
    _skip_without_snapshot()
    loaded = seed.load()
    if not loaded.envelopes:
        pytest.skip("no seed set present")
    defects = [
        f for f in seed.check(loaded, _corpus()) if f.severity is Severity.DEFECT
    ]
    assert not defects, "\n".join(str(f) for f in defects)


def test_the_shipped_seed_ids_do_not_collide_with_the_gold_set():
    loaded = seed.load()
    if not loaded.envelopes:
        pytest.skip("no seed set present")
    identifiers = [f for f in seed.check(loaded) if f.check == "seed-identifier"]
    assert not identifiers, "\n".join(str(f) for f in identifiers)


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------


def test_coverage_reports_an_unreviewed_set_as_a_gap(tmp_path):
    _write(tmp_path, "entities.seed.yaml", [_entity_seed()])
    findings = seed.coverage(seed.load(tmp_path))
    assert any(f.check == "seed-review" for f in findings)


def test_coverage_names_the_entity_types_with_no_example(tmp_path):
    _write(tmp_path, "entities.seed.yaml", [_entity_seed()])
    findings = seed.coverage(seed.load(tmp_path))
    missing = {f.message for f in findings if f.check == "seed-coverage"}
    assert any("type = JudicialDecision" in message for message in missing)
    assert not any("type = LegalConcept" in message for message in missing)


# ---------------------------------------------------------------------------
# The review columns, and the one door out
# ---------------------------------------------------------------------------


def test_review_columns_are_not_record_fields():
    """A verdict is how a record got approved, never something it asserts."""
    every_header = {column.header for spec in sheets() for column in spec.columns}
    assert every_header.isdisjoint(set(REVIEW_COLUMNS))


def test_the_transcriber_tolerates_the_review_columns():
    """Otherwise the corrected workbook cannot come back in (ADR-0044)."""
    from tm_knowledge.stage0 import transcribe

    assert set(REVIEW_COLUMNS) <= set(transcribe.REVIEW_COLUMNS)


def test_a_misspelt_envelope_key_is_a_defect(tmp_path):
    """A typo in `locate` would otherwise surface three checks later, wrongly."""
    _write(tmp_path, "entities.seed.yaml", [_entity_seed(locat={"occurrence": 1})])
    findings = seed.check(seed.load(tmp_path))
    assert any(
        f.check == "seed-envelope" and "unknown envelope key" in f.message
        for f in findings
    )


def test_the_schema_is_checked_without_a_snapshot(tmp_path):
    """A null span is schema-valid, so shape errors are catchable on a bare clone."""
    _write(
        tmp_path, "entities.seed.yaml", [_entity_seed(record={"type": "NotAGoldType"})]
    )
    findings = seed.check(seed.load(tmp_path), corpus=None)
    assert any(f.check == "seed-schema" for f in findings)

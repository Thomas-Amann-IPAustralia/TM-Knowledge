"""The Stage 0 evaluation harness — P5's done-criteria.

Four things are checked here, and the second and third are the ones that matter.

1. **The sound gold set produces no defects.** A check that fires on everything
   is not a check.
2. **Every defect the fixture holds is caught, by name.** One record per fault,
   and the test asserts which check caught it — a check that starts catching the
   *wrong* thing fails here rather than passing quietly.
3. **The completeness gate is not vacuous.** An empty gold set must produce one
   named gap per absent deliverable, and a full one must produce none. This is
   the whole of ADR-0018's design, and getting it wrong looks exactly like
   success: a suite that iterates an empty collection is green.
4. **A run that never opened the snapshot never reports Stage 0 complete.**
   Unverified is not the same as sound.

Point 3's two halves are both exercised against synthetic gold sets in `tmp_path`
rather than against `eval/gold/`, so neither needs deleting on the day Stage 0
actually completes.
"""

from __future__ import annotations

import pytest
import yaml

from tm_knowledge.config import REPO_ROOT, UPSTREAM_DIR
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.cli import coverage as coverage_cli
from tm_knowledge.stage0.cli import harness as harness_cli
from tm_knowledge.stage0.harness import DELIVERABLES, Severity, run
from tm_knowledge.stage0.schemas import RECORD_TYPES, enum_values, read_path, ref_paths

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "harness"


def _skip_without_snapshot() -> None:
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")


# ---------------------------------------------------------------------------
# Reading the gold set
# ---------------------------------------------------------------------------


def test_an_unrecognised_gold_file_is_an_error_not_a_skip(tmp_path):
    """A misspelt filename is expert judgements that silently did not count."""
    (tmp_path / "entites.yaml").write_text("- {id: GE-001}\n", encoding="utf-8")
    loaded = goldset.load(tmp_path)
    assert loaded.total == 0
    assert [path.name for path, _ in loaded.unreadable] == ["entites.yaml"]


def test_every_record_type_has_exactly_one_file(tmp_path):
    assert set(goldset.FILE_FOR) == set(RECORD_TYPES)
    assert len(set(goldset.GOLD_FILES)) == len(RECORD_TYPES)


def test_an_absent_gold_directory_is_not_an_error(tmp_path):
    loaded = goldset.load(tmp_path / "nothing-here")
    assert loaded.total == 0
    assert loaded.unreadable == ()


# ---------------------------------------------------------------------------
# The defect checks
# ---------------------------------------------------------------------------


@pytest.mark.snapshot
def test_the_sound_gold_set_has_no_defects():
    _skip_without_snapshot()
    report = run(gold_dir=FIXTURES / "sound")
    assert report.defects == (), "\n".join(str(f) for f in report.defects)
    assert report.exit_code == 3, "under every band, so gaps but no defects"


#: What each fixture record is broken by, and the check that must catch it.
#: Keyed by subject, so a check that starts firing on the wrong record fails.
EXPECTED_DEFECTS = {
    ("gold-file", "entites.yaml"): "not a gold file name",
    ("gold-file", "search-questions.yaml"): "expected a YAML list",
    ("schema", "GE-001"): "'LAW' is not one of",
    ("schema", "GC-900"): "does not match",
    ("ids", "GE-001"): "used by two records",
    ("ids", "GC-900"): "must carry a GE- id",
    ("ids", "GE-777"): "reuses a retired id",
    ("cross-reference", "GA-001"): "PU-404",
    ("resolution", "GE-002"): "resolves to nothing",
    ("span", "GE-003"): "falls outside",
    ("span", "GE-004"): "does not land",
    ("span", "GE-005"): "holds no text",
    ("staleness", "GE-006"): "returns to the expert",
}


@pytest.mark.snapshot
@pytest.mark.parametrize(("key", "fragment"), sorted(EXPECTED_DEFECTS.items()))
def test_every_defect_in_the_fixture_is_caught(key, fragment):
    _skip_without_snapshot()
    check, subject = key
    report = run(gold_dir=FIXTURES / "defective")
    matching = [
        finding
        for finding in report.defects
        if finding.check == check and finding.subject == subject
    ]
    assert matching, f"nothing caught {subject} under {check}"
    assert any(fragment in finding.message for finding in matching), (
        f"{check} caught {subject}, but for a different reason: "
        + " | ".join(finding.message for finding in matching)
    )


@pytest.mark.snapshot
def test_the_defective_fixture_holds_no_surprises():
    """Every defect found is one the fixture meant to hold.

    Without this the test above passes while the harness also fires on things
    nobody asked it to, which is how a check becomes noise.
    """
    _skip_without_snapshot()
    report = run(gold_dir=FIXTURES / "defective")
    found = {(finding.check, finding.subject) for finding in report.defects}
    assert found == set(EXPECTED_DEFECTS)


def test_defects_break_the_build_and_gaps_do_not(tmp_path):
    """Exit codes carry ADR-0018's distinction, and it is the only thing they do."""
    empty = run(gold_dir=tmp_path, root=tmp_path, with_resolution=False)
    assert empty.exit_code == 3
    assert empty.defects == ()

    (tmp_path / "entities.yaml").write_text("id: GE-001\n", encoding="utf-8")
    broken = run(gold_dir=tmp_path, root=tmp_path, with_resolution=False)
    assert broken.exit_code == 1


# ---------------------------------------------------------------------------
# The completeness gate — the point of the whole package
# ---------------------------------------------------------------------------


def test_an_empty_gold_set_is_red_and_says_why(tmp_path):
    """The vacuity trap: with no records every other check passes.

    So the gate has to fail instead, and its output has to be legible enough to
    answer "what is Stage 0 waiting on" without reading any code.
    """
    report = run(gold_dir=tmp_path, root=tmp_path, with_resolution=False)
    assert report.exit_code == 3
    assert not report.complete

    named = {finding.subject for finding in report.gaps if finding.check == "completeness"}
    for deliverable in DELIVERABLES:
        expected = (
            deliverable.path
            if deliverable.kind == "document"
            else goldset.FILE_FOR[deliverable.record_type]
        )
        assert expected in named, f"the gate said nothing about {deliverable.label}"


def _complete_gold_set(directory, corpus) -> None:
    """Write a gold set that meets every band, from real corpus passages.

    Deliberately synthetic and deliberately repetitive: it exists to prove the
    gate can go quiet, not to be an example of Stage 0 content. Nothing here may
    be copied into `eval/gold/` — every judgement field holds a placeholder.
    """
    chunk = next(
        corpus.chunks[ref]
        for ref in sorted(corpus.chunks)
        if len(corpus.chunks[ref].text) >= 40
    )
    ref, text, digest = chunk.chunk_ref, chunk.text, chunk.content_hash
    approval = {"approved_by": "«name»", "approved_date": "2026-08-19"}

    categories = [v for v in enum_values("competency_question", "category") if v]
    kinds = [v for v in enum_values("prohibited_use", "kind") if v]

    records = {
        "prohibited-uses.yaml": [
            {
                "id": f"PU-{index:03d}",
                "prohibited": "«a conclusion the system must not produce»",
                "kind": kind,
                "why": "«why»",
                "detectable_by": "eval",
                "test_ref": None,
                "related_questions": [],
                **approval,
            }
            for index, kind in enumerate(kinds, start=1)
        ],
        "competency-questions.yaml": [
            {
                "id": f"CQ-{index:03d}",
                "question": "«a question»",
                "asked_by": "examiner",
                "category": category,
                "pilot_in_scope": True,
                "expected_sources": {"required": [ref], "supporting": []},
                "answer_shape": "«shape»",
                "measured_by": ["«metric»"],
                **approval,
            }
            for index, category in enumerate(categories, start=1)
        ],
        "concepts.yaml": [
            {
                "id": f"GC-{index:03d}",
                "pref_label": f"«label {index}»",
                "alt_labels": [],
                "not_labels": ["«a near-miss»"],
                "definition_sources": [ref],
                **approval,
            }
            for index in range(1, 51)
        ],
        "entities.yaml": [
            {
                "id": f"GE-{index:03d}",
                "surface": text[:20],
                "type": "Other",
                "source_ref": ref,
                "span": [0, 20],
                "source_content_hash": digest,
                **approval,
            }
            for index in range(1, 101)
        ],
        "relationships.yaml": [
            {
                "id": f"GR-{index:03d}",
                "subject": "«subject»",
                "predicate": "«predicate»",
                "object": "«object»",
                "source_ref": ref,
                "supporting_text": text[:40],
                "span": [0, 40],
                "source_content_hash": digest,
                "tier": 1,
                "modality": "must",
                **approval,
            }
            for index in range(1, 51)
        ],
        "search-questions.yaml": [
            {
                "id": f"GS-{index:03d}",
                "query": "«a query»",
                "uses_manual_terminology": False,
                "relevant": [{"ref": ref, "grade": 3}],
                **approval,
            }
            for index in range(1, 21)
        ],
        "retrieval-questions.yaml": [
            {
                "id": f"GA-{index:03d}",
                "question": "«a question»",
                "required_evidence": [ref],
                "qualifications_expected": "«qualifications»",
                "authority_distinction_required": True,
                "prohibited_conclusions": ["PU-001"],
                **approval,
            }
            for index in range(1, 21)
        ],
        "reasoning-expected.yaml": [
            {
                "id": "GX-001",
                "given": ["«the starting position»"],
                "expected_inferences": [
                    {"conclusion": "«what follows»", "basis": [ref], "kind": "classification"}
                ],
                "must_not_infer": ["PU-001"],
                "tier": 1,
                "explanation_required": True,
                **approval,
            }
        ],
    }
    directory.mkdir(parents=True, exist_ok=True)
    for filename, block in records.items():
        (directory / filename).write_text(
            yaml.safe_dump(block, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )


@pytest.mark.snapshot
def test_the_gate_goes_quiet_when_stage_0_is_finished(tmp_path):
    """The other half: a gate that can never be satisfied measures nothing."""
    _skip_without_snapshot()
    from tm_knowledge.upstream.loader import load_corpus

    corpus = load_corpus()
    gold = tmp_path / "gold"
    _complete_gold_set(gold, corpus)
    (tmp_path / "eval").mkdir()
    (tmp_path / "eval" / "pilot-scope.md").write_text("«the boundary»\n", encoding="utf-8")
    (tmp_path / "eval" / "measures.md").write_text("«the thresholds»\n", encoding="utf-8")

    report = run(gold_dir=gold, root=tmp_path, corpus=corpus)
    assert report.defects == (), "\n".join(str(f) for f in report.defects)
    assert report.gaps == (), "\n".join(str(f) for f in report.gaps)
    assert report.complete
    assert report.exit_code == 0


@pytest.mark.snapshot
def test_a_run_without_the_snapshot_is_never_complete(tmp_path):
    """Unverified is not sound. A gapless run that never opened the corpus has
    checked no ref, no span and no hash, and must not say Stage 0 is done."""
    _skip_without_snapshot()
    from tm_knowledge.upstream.loader import load_corpus

    gold = tmp_path / "gold"
    _complete_gold_set(gold, load_corpus())
    (tmp_path / "eval").mkdir()
    (tmp_path / "eval" / "pilot-scope.md").write_text("«the boundary»\n", encoding="utf-8")
    (tmp_path / "eval" / "measures.md").write_text("«the thresholds»\n", encoding="utf-8")

    report = run(gold_dir=gold, root=tmp_path, with_resolution=False)
    assert not report.complete
    assert report.exit_code == 3
    assert any(finding.check == "resolution" for finding in report.gaps)


def test_an_empty_document_does_not_count_as_written(tmp_path):
    (tmp_path / "eval").mkdir()
    (tmp_path / "eval" / "pilot-scope.md").write_text("\n\n", encoding="utf-8")
    report = run(gold_dir=tmp_path / "gold", root=tmp_path, with_resolution=False)
    assert any(
        finding.subject == "eval/pilot-scope.md" and "empty" in finding.message
        for finding in report.gaps
    )


# ---------------------------------------------------------------------------
# The bands and the enums live in one place
# ---------------------------------------------------------------------------


def test_the_bands_match_the_guide():
    """§7's numbers, asserted against the guide's own text rather than restated.

    ADR-0018 names this duplication as a known cost. This is the check that
    makes moving a band in the guide and forgetting the harness a test failure.
    """
    guide = (REPO_ROOT / "eval" / "STAGE-0-INPUT-GUIDE.md").read_text(encoding="utf-8")
    section = guide.split("## 7. Definition of done", 1)[1].split("## 8.", 1)[0]
    for deliverable in DELIVERABLES:
        if deliverable.minimum is None or deliverable.maximum is None:
            continue
        assert f"{deliverable.minimum}–{deliverable.maximum}" in section, (
            f"{deliverable.label}'s band is not the one §7 states"
        )


def test_the_gate_covers_every_record_type():
    """A record type with no deliverable row is one the gate never asks for."""
    gated = {d.record_type for d in DELIVERABLES if d.kind == "records"}
    assert gated == set(RECORD_TYPES)


# ---------------------------------------------------------------------------
# Ref paths are read off the schema, not listed by hand
# ---------------------------------------------------------------------------


def test_ref_paths_find_the_nested_ones():
    assert ("relevant", "*", "ref") in ref_paths("gold_search_question")
    assert ("expected_sources", "required", "*") in ref_paths("competency_question")
    assert ("expected_inferences", "*", "basis", "*") in ref_paths("reasoning_expectation")
    assert ("resolves_to",) in ref_paths("gold_entity"), "a oneOf branch is still a ref"


def test_ref_paths_stay_in_step_with_the_schemas():
    """Every ref-valued field named in a valid fixture is reachable by a path.

    The fixtures are the schemas' human-readable face; if one grows a ref field
    the walker does not find, the resolution checks would silently skip it.
    """
    import json

    for stem, record_type in (
        ("gold-entity", "gold_entity"),
        ("gold-concept", "gold_concept"),
        ("gold-search-question", "gold_search_question"),
        ("gold-retrieval-question", "gold_retrieval_question"),
    ):
        record = yaml.safe_load(
            (REPO_ROOT / "tests" / "fixtures" / "stage0" / "valid" / f"{stem}.yaml")
            .read_text(encoding="utf-8")
        )
        reached = {
            value
            for path in ref_paths(record_type)
            for _, value in read_path(record, path)
        }
        assert reached, f"{record_type} reaches no refs at all"


def test_read_path_skips_absent_and_null():
    assert list(read_path({}, ("source_ref",))) == []
    assert list(read_path({"source_ref": None}, ("source_ref",))) == []


# ---------------------------------------------------------------------------
# The commands
# ---------------------------------------------------------------------------


@pytest.mark.snapshot
def test_the_command_exit_codes(capsys):
    _skip_without_snapshot()
    assert harness_cli(["--gold-dir", str(FIXTURES / "sound")]) == 3
    assert harness_cli(["--gold-dir", str(FIXTURES / "sound"), "--allow-incomplete"]) == 0
    assert harness_cli(["--gold-dir", str(FIXTURES / "defective")]) == 1
    assert (
        harness_cli(["--gold-dir", str(FIXTURES / "defective"), "--allow-incomplete"]) == 1
    ), "--allow-incomplete forgives gaps and never forgives a defect"


@pytest.mark.snapshot
def test_the_coverage_report_reads_as_a_worklist(tmp_path, capsys):
    _skip_without_snapshot()
    out = tmp_path / "coverage.md"
    assert coverage_cli(["--gold-dir", str(FIXTURES / "sound"), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "# Stage 0 — coverage and gaps" in text
    assert "never fills them" not in text.split("## 1.")[1], "the caveat belongs up top"
    assert "100–300" in text and "50–100" in text, "the bands are on the board"
    for deliverable in DELIVERABLES:
        assert deliverable.label in text


def test_the_coverage_report_survives_an_empty_gold_set(tmp_path):
    from tm_knowledge.stage0.coverage import render

    report = run(gold_dir=tmp_path / "gold", root=tmp_path, with_resolution=False)
    text = render(report, generated="2026-08-19")
    assert "0 defect(s)" in text
    assert "not written" in text
    assert "did not run" in text


def test_nothing_in_the_report_proposes_content(tmp_path):
    """P10 reports gaps and never fills them (guide §9).

    Asserted the only way a test can: no gap message may contain a value for the
    field it is reporting as empty. The messages name the field and stop.
    """
    from tm_knowledge.stage0.coverage import render

    report = run(gold_dir=FIXTURES / "sound", with_resolution=False)
    text = render(report, generated="2026-08-19")
    for finding in report.of(Severity.GAP):
        assert "«" not in finding.message
    assert "suggest" not in text.lower()


@pytest.mark.snapshot
def test_this_repos_own_gold_set_holds_no_defects():
    """The guard CI leans on: a record committed to `eval/gold/` that does not
    validate, does not resolve or has gone stale fails the build here. It passes
    today because the directory is empty, and it keeps passing only while what
    lands in it is sound."""
    _skip_without_snapshot()
    report = run()
    assert report.defects == (), "\n".join(str(f) for f in report.defects)

"""Normative scenarios (A10, ADR-0147): a fictional amendment, read as edits to a legal
test, run on fictional matters. Three layers never summed; the draft never operative."""

from __future__ import annotations

import copy

import pytest
import yaml

from tm_knowledge.authored import procedure
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.explain import engine, scenarios

from test_explain import _outcomes  # the one outcome guard, shared

pytestmark = pytest.mark.snapshot

TESTS = {k: v.record for k, v in procedure.load_tests().by_id().items()}


@pytest.fixture(scope="module")
def corpus():
    from tm_knowledge.upstream.loader import load_corpus

    return load_corpus()


@pytest.fixture(scope="module")
def found(corpus):
    return {s.id: s for s in scenarios.load(corpus=corpus)}


@pytest.fixture(scope="module")
def index(corpus):
    from tm_knowledge.ontology import dependencies

    return dependencies.build(corpus)


@pytest.fixture(scope="module")
def results(found, index):
    return {sid: scenarios.run(s, index=index) for sid, s in found.items()}


def test_every_scenario_loads_clean_and_is_fictional(found):
    assert sorted(found) == ["FS-0001", "FS-0002", "FS-0003"]
    assert all(not s.errors for s in found.values()), {s.id: s.errors for s in found.values() if s.errors}
    assert all(s.record["fictional"] is True for s in found.values())


def test_the_test_record_is_never_edited():
    before = copy.deepcopy(TESTS["GL-0003"])
    scenario = yaml.safe_load(scenarios.AMENDMENTS_PATH.read_text(encoding="utf-8"))[0]
    variant = scenarios.apply(TESTS["GL-0003"], scenario)
    assert TESTS["GL-0003"] == before
    assert variant["scenario"] == "FS-0001"
    assert "before_filing" not in {r["id"] for r in variant["evidence_requirements"]}


def test_every_element_the_draft_changes_is_labelled_draft_never_law():
    scenario = yaml.safe_load(scenarios.AMENDMENTS_PATH.read_text(encoding="utf-8"))[2]
    variant = scenarios.apply(TESTS["GL-0001"], scenario)
    assert variant["effect"]["kind"] == "discretion" and variant["effect"]["draft"] == "FS-0003"
    assert engine._source(variant["effect"])["authority"] == "draft"
    assert engine._source(TESTS["GL-0001"]["effect"])["authority"] == "law"


def test_a_scenario_against_a_text_not_held_is_refused(tmp_path, corpus):
    document = yaml.safe_load(scenarios.AMENDMENTS_PATH.read_text(encoding="utf-8"))
    document[0]["amends"]["compilation"] = "47"
    document[1]["changes"][0]["target"] = "no_such_element"
    document[2]["runs_on"] = ["FM-0004"]
    path = tmp_path / "amendments.yaml"
    path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
    errors = {s.id: " ".join(s.errors) for s in scenarios.load(path, corpus=corpus)}
    assert "not held" in errors["FS-0001"]
    assert "no element of GL-0001" in errors["FS-0002"]
    assert "no objection under GL-0001" in errors["FS-0003"]


def test_after_filing_use_closes_the_period_gap_and_drops_the_filing_date_question(results):
    """FS-0001 on FM-0005: every exhibit dated after the filing date. Under the draft the
    period gap closes; the other gaps stay; and whether the evidence is enough stays the
    examiner's assessment."""
    runs = {r["matter"]: r for r in results["FS-0001"]["normative"]}
    fm5 = runs["FM-0005"]["issues"][0]
    closed = {(g["what"].split(" ")[1], g["gap"]) for g in fm5["gaps"]["closed"]}
    assert closed == {("e1", "dated on or after the filing date (2025-03-03)"),
                      ("e2", "dated on or after the filing date (2025-03-03)")}
    assert not fm5["gaps"]["opened"]
    assert fm5["overall"] == {"was": engine.OPEN, "now": engine.OPEN, "same": True}
    # FM-0004 has no filing date: the question only mattered while use had to precede it.
    assert runs["FM-0004"]["asks"]["no_longer"] == ["What is your application's filing date?"]


def test_a_near_miss_changes_the_test_and_not_the_reading(results):
    """FS-0002 removes honest concurrent use; none of the matters records it assessed, so
    the elements change and the readings do not, and the result says both."""
    for run in results["FS-0002"]["normative"]:
        assert run["differs"] is False, run["matter"]
        issue = run["issues"][0]
        assert [x["key"] for x in issue["removed"]] == ["exception:honest_concurrent_use:hcu"]
        assert "does not change, although the test's elements do" in issue["reads"]


def test_a_must_becoming_a_may_is_reported_as_a_discretion(results):
    issue = {r["matter"]: r for r in results["FS-0003"]["normative"]}["FM-0001"]["issues"][0]
    (effect,) = [c for c in issue["changed"] if c["key"] == "effect"]
    assert effect["was"].endswith("(obligation)") and effect["now"].endswith("(discretion)") and effect["draft"]


def test_the_three_layers_are_kept_apart(results):
    r = results["FS-0002"]
    assert "GL-0001" in r["editorial"]["names_it"]
    assert "not every effect" in r["editorial"]["reads"]
    assert r["behavioural"] == scenarios.BEHAVIOURAL and "Unknown" in r["behavioural"]


def test_no_scenario_states_an_outcome(results):
    for sid, result in results.items():
        assert _outcomes(scenarios.render_text(result)) == [], sid


def test_the_draft_is_kept_out_of_everything_operative():
    """No scenario id and no draft words in the graph, the site's data or the authored
    records: a draft is never law and never served."""
    drafts = yaml.safe_load(scenarios.AMENDMENTS_PATH.read_text(encoding="utf-8"))
    needles = [d["id"] for d in drafts] + [d["draft_text"] for d in drafts]
    places = [REPO_ROOT / "graph" / "dataset.nq", *sorted((REPO_ROOT / "site").rglob("*.json")),
              *sorted((REPO_ROOT / "authored").glob("*.yaml"))]
    for path in places:
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            assert needle not in text, f"{needle!r} in {path.relative_to(REPO_ROOT)}"

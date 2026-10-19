"""The first customer slice (Package 4, ADR-0142): legal tests, the process template, the
fictional matters and the explanation built from them, against the review's acceptance
examples (A01 to A05, A09) and the rules the engine keeps."""

from __future__ import annotations

import copy
import re

import pytest
import yaml

from tm_knowledge.authored import procedure
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.explain import engine, matters

pytestmark = pytest.mark.snapshot

MATTERS = {m.id: m for m in matters.load()}
TESTS = {k: v.record for k, v in procedure.load_tests().by_id().items()}
PROCESS = procedure.load_processes().sound[0].record

#: Wording that would state an outcome or a success the system may never state.
OUTCOME = re.compile(
    r"\b(the|this|your) (application|trade mark)( for [\w ]+)? (will be|is|has been|was) (accepted|rejected|registered|refused)\b"
    r"|\bwill (succeed|fail|lapse)\b|\bsucceeds?\b|\byou will\b|\bis enough\b|\bare enough\b", re.I)
#: A sentence that attributes or conditions what it says ("the report states", "whether",
#: "how much is enough is the examiner's assessment") states no outcome of its own.
ATTRIBUTED = re.compile(r"\b(report|states|whether|how much|if|unless|only the Registrar)\b", re.I)


def _outcomes(text):
    sentences = re.split(r"(?<=[.!?])\s+|\n", text)
    return [s for s in sentences if OUTCOME.search(s) and not ATTRIBUTED.search(s)]


def _explain(matter):
    return engine.explain(matter, TESTS, PROCESS)


def test_every_record_and_matter_loads_clean():
    tests, processes = procedure.load_tests(), procedure.load_processes()
    assert {e.id for e in tests.sound} == {"GL-0001", "GL-0002", "GL-0003"} and not tests.refused
    assert [e.id for e in processes.sound] == ["GP-0001"] and not processes.refused
    assert all(not m.errors for m in MATTERS.values())
    assert all(m.record["fictional"] is True for m in MATTERS.values())


def test_every_quote_is_in_the_envelope_and_lands():
    """Each element's quote is among its record's evidence, and the evidence is exactly
    the text at its span in the pinned snapshot (the harness checks the same)."""
    from tm_knowledge.stage0.harness import passage_at
    from tm_knowledge.upstream.loader import load_corpus

    corpus = load_corpus()
    for entry in (*procedure.load_tests().sound, *procedure.load_processes().sound):
        evidence = entry.envelope["evidence"]
        assert {(i["ref"], i["quote"]) for i in evidence} == set(procedure.quoted(entry.record)), entry.id
        for item in evidence:
            start, end = item["span"]
            assert passage_at(corpus, item["ref"]).text[start:end] == item["quote"]


def test_a_record_quoting_what_its_evidence_does_not_is_refused(tmp_path):
    text = (REPO_ROOT / "authored" / procedure.TESTS_FILE).read_text(encoding="utf-8")
    broken = yaml.safe_load(text)
    broken[0]["condition"]["all"][0]["quote"] = "a quote nobody located"
    (tmp_path / procedure.TESTS_FILE).write_text(yaml.dump(broken, allow_unicode=True), encoding="utf-8")
    found = procedure.load_tests(tmp_path)
    assert found.refused and any("not among the evidence" in str(e) for e in found.refused[0].errors)


def test_a_matter_that_is_not_fictional_is_refused(tmp_path):
    document = yaml.safe_load(matters.MATTERS_PATH.read_text(encoding="utf-8"))
    document[0]["fictional"] = False
    path = tmp_path / "matters.yaml"
    path.write_text(yaml.dump(document, allow_unicode=True), encoding="utf-8")
    assert matters.load(path)[0].errors


# --- the acceptance examples -------------------------------------------------------


def test_a01_two_objections_explained_apart_and_nothing_accepted():
    """Two objections over overlapping goods: each explained separately, the withdrawn one
    said to be withdrawn, what remains open named, and the application never treated as
    accepted. One person holds two capacities without contradiction."""
    e = _explain(MATTERS["FM-0001"])
    by = {i["objection"]: i for i in e["issues"]}
    assert by["o1"]["items"] == ["candles", "perfumes"] and by["o2"]["items"] == ["perfumes", "soaps"]
    assert "withdrawn" in by["o2"]["standing"] and "maintained" in by["o1"]["standing"]
    assert e["unresolved"]["items"] == ["candles", "perfumes"] and e["unresolved"]["clear"] == ["soaps"]
    assert "does not accept the application" in e["unresolved"]["reads"]
    assert {"party": "Wren Example (fictional)", "capacities": ["applicant", "representative"]} in e["roles"]
    assert e["process"]["current"] == "further_report"


def test_a02_the_branch_and_what_it_needs_and_no_lapse_inferred():
    """A report, a response, a deferment: the position is the deferment; the next step and
    what it depends on are named; the lapse date is the report's, flagged as possibly moved
    by the deferment, and never recalculated."""
    p = _explain(MATTERS["FM-0002"])["process"]
    assert p["current"] == "deferment"
    assert [n["to"] for n in p["next"]] == ["consideration"] and p["next"][0]["needs"]
    assert "2027-04-15" in p["lapse"] and "may have moved" in p["lapse"]
    assert "deferment_not_counted" in {d["id"] for d in p["deadlines"]}


def test_a02_a_branch_for_another_ground_is_not_offered():
    """Deferment exists only for a section 44 ground: a section 41 matter is not offered it."""
    nxt = {n["to"] for n in _explain(MATTERS["FM-0004"])["process"]["next"]}
    assert "deferment" not in nxt and "response" in nxt


def test_a04_a_missing_condition_is_not_established_never_a_negative():
    """Section 44 with the priority dates unknown: not established from the available facts,
    and the question that would settle it asked."""
    issue = _explain(MATTERS["FM-0003"])["issues"][0]
    assert issue["test"]["state"] == "open" and engine.OPEN in issue["test"]["reads"]
    asked = [a["condition"] for a in issue["test"]["asks"]]
    assert "priority_not_earlier" in asked


def test_a04_a_discretion_stays_a_discretion_when_its_prerequisites_are_recorded():
    test = TESTS["GL-0001"]
    objection = copy.deepcopy(MATTERS["FM-0003"].record["objections"][0])
    objection["assessments"].append({"condition": "hcu", "value": True, "by": "the examiner (fictional)",
                                     "recorded": "2026-02-11"})
    hcu = next(x for x in engine.read_test(test, objection)["exceptions"] if x["id"] == "honest_concurrent_use")
    assert hcu["state"] == "met" and hcu["effect"]["kind"] == "discretion"
    assert "may accept" in hcu["effect"]["reads"] and "need not" in hcu["effect"]["reads"]
    assert " must " not in hcu["effect"]["reads"]


def test_a04_an_evaluative_condition_is_never_computed():
    """Every fact true and no assessment recorded: the evaluative conditions stay for the
    Registrar, so the test stays open."""
    test = TESTS["GL-0001"]
    facts = [{"condition": leaf["id"], "value": True, "source": "supposed"}
             for leaf in procedure.leaves(test["condition"]) if leaf["kind"] == "fact"]
    read = engine.read_test(test, {"facts": facts, "items": ["i1"]})
    assert read["state"] == "open"
    evaluative = [c for c in read["condition"]["children"] if c.get("kind") == "evaluative"]
    assert evaluative and all("for the Registrar to assess" in c["why"] for c in evaluative)


def test_a05_and_a03_evidence_says_what_is_missing_and_an_unknown_date_is_asked():
    e = _explain(MATTERS["FM-0004"])
    exhibits = {x["id"]: x for x in e["issues"][0]["evidence"]["exhibits"]}
    assert "shows use overseas, not in Australia" in exhibits["e3"]["missing"]
    assert "shows a different sign" in exhibits["e3"]["missing"]
    assert all("the filing date is not known" in x["unclear"] for x in exhibits.values())
    assert {"condition": "filing_date", "question": "What is your application's filing date?"} in e["asks"]
    assert all("examiner's assessment" in x["reads"] for x in exhibits.values())


def test_a09_changing_a_fact_changes_the_object_and_its_text_together():
    """Give FM-0004 a filing date: the question goes, the exhibit before it reads as before
    the filing date, the one after it as missing, and the text says the same."""
    record = copy.deepcopy(MATTERS["FM-0004"].record)
    record["application"]["filing_date"] = "2025-09-01"
    e = _explain(matters.Matter(record=record))
    exhibits = {x["id"]: x for x in e["issues"][0]["evidence"]["exhibits"]}
    assert not e["asks"]
    assert any(c["check"] == "before_filing_date" and c["result"] == "present" for c in exhibits["e1"]["checks"])
    assert any("on or after the filing date" in m for m in exhibits["e2"]["missing"])
    text = engine.render_text(e)
    assert "dated on or after the filing date (2025-09-01)" in text and "What is your application's filing date?" not in text


# --- the rules, over every matter --------------------------------------------------


@pytest.mark.parametrize("matter_id", sorted(MATTERS))
def test_no_explanation_states_an_outcome(matter_id):
    text = engine.render_text(_explain(MATTERS[matter_id]))
    assert _outcomes(text) == []
    assert engine.STAMP in text


def test_the_outcome_guard_catches_an_outcome():
    assert _outcomes("Your objection is resolved. The application will be accepted.")
    assert _outcomes("This evidence is enough.")
    assert not _outcomes("The report states that the application will lapse on 2027-01-01.")


@pytest.mark.parametrize("matter_id", sorted(MATTERS))
def test_no_date_is_computed(matter_id):
    """Every date in the text is one the matter itself states."""
    stated = set(re.findall(r"\d{4}-\d{2}-\d{2}", yaml.dump(MATTERS[matter_id].record)))
    text = engine.render_text(_explain(MATTERS[matter_id]))
    assert set(re.findall(r"\d{4}-\d{2}-\d{2}", text)) <= stated


@pytest.mark.parametrize("matter_id", sorted(MATTERS))
def test_law_and_practice_are_labelled_by_their_source(matter_id):
    sources = _explain(MATTERS[matter_id])["sources"]
    assert sources
    for s in sources:
        assert s["authority"] == ("practice" if s["ref"].startswith("TMM/") else "law"), s


@pytest.mark.parametrize("matter_id", sorted(MATTERS))
def test_a_question_is_asked_only_where_its_answer_changes_the_reading(matter_id):
    e = _explain(MATTERS[matter_id])
    for issue in e["issues"]:
        test = TESTS[issue["test"]["test"]]
        objection = next(o for o in MATTERS[matter_id].record["objections"] if o["id"] == issue["objection"])
        for ask in issue["test"]["asks"]:
            states = set()
            for value in (True, False):
                o = copy.deepcopy(objection)
                o.setdefault("facts", []).append({"condition": ask["condition"], "value": value, "source": "t"})
                o["cited_mark"] = {}
                app = {**MATTERS[matter_id].record["application"], "priority_date": None, "filing_date": None}
                states.add(engine.read_test(test, o, app)["state"])
            assert len(states) > 1 or issue["test"]["state"] not in states


def test_a_known_fact_is_not_asked_about():
    """FM-0001's cited mark is registered, so whether it is still an application changes
    nothing, and is not asked."""
    asked = [a["condition"] for i in _explain(MATTERS["FM-0001"])["issues"] for a in i["test"]["asks"]]
    assert "sought_by_another" not in asked and "priority_not_earlier" not in asked

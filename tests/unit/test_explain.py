"""The first customer slice (Package 4, ADR-0142, ADR-0144): legal tests, the process
templates, the fictional matters and the explanations built from them, against the review's
acceptance examples (A01 to A06, A09, A12) and the rules the engine keeps."""

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
PROCESSES = {k: v.record for k, v in procedure.load_processes().by_id().items()}
PROCESS = PROCESSES[engine.EXAMINATION_PROCESS]

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
    assert [e.id for e in processes.sound] == ["GP-0001", "GP-0002"] and not processes.refused
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


def test_a_step_continuing_in_no_template_is_refused(tmp_path):
    document = yaml.safe_load((REPO_ROOT / "authored" / procedure.PROCESSES_FILE).read_text(encoding="utf-8"))
    report = next(s for s in document[1]["steps"] if s.get("continues_in"))
    report["continues_in"] = "GP-9999"
    (tmp_path / procedure.PROCESSES_FILE).write_text(yaml.dump(document, allow_unicode=True), encoding="utf-8")
    from tm_knowledge.authored import store as authored_store

    found = procedure.load_processes(tmp_path, authored=authored_store.load())
    assert [e.id for e in found.refused] == ["GP-0002"]
    assert any("no template here" in str(e) for e in found.refused[0].errors)


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


def test_a12_evidence_covering_the_wrong_period_says_what_is_missing_never_that_it_fails():
    """FM-0005: every exhibit dated after the filing date or undated, against a report that
    reads subsection (3). Each says what it lacks; the after-filing rule, which belongs to
    (4), is set aside and said to be; nothing says the evidence fails or is not enough."""
    e = _explain(MATTERS["FM-0005"])
    evidence = e["issues"][0]["evidence"]
    exhibits = {x["id"]: x for x in evidence["exhibits"]}
    for key in ("e1", "e2"):
        assert "dated on or after the filing date (2025-03-03)" in exhibits[key]["missing"]
    assert "is not dated" in exhibits["e3"]["missing"] and "is not dated" not in exhibits["e3"]["unclear"]
    assert [s["id"] for s in evidence["set_aside"]] == ["after_filing_relevant"]
    assert not e["asks"]
    assert "Set aside" in engine.render_text(e)
    said = " ".join(x["reads"] for x in exhibits.values())
    assert not re.search(r"\b(fails?|insufficient|not enough)\b", said, re.I)


def test_a12_everyday_wording_is_asked_about_never_chosen():
    """FM-0006: the customer's words could fit section 41 or section 44. The explanation
    names every ground it holds a test for, reads none of them, and asks which section the
    report cites; deferment, which exists only for section 44, is offered with that ground
    named as what it needs."""
    e = _explain(MATTERS["FM-0006"])
    issue = e["issues"][0]
    assert issue["test"] is None and "does not choose" in issue["reads"]
    assert [c["test"] for c in issue["candidates"]] == sorted(TESTS)
    assert e["asks"] == [{"condition": "cited_provision", "question": engine.ASK_GROUND}]
    deferment = next(n for n in e["process"]["next"] if n["to"] == "deferment")
    assert deferment["needs"][0] == "whether the objection is under TMA1995/s44"


def test_an_objection_with_no_test_cannot_record_what_a_test_defines(tmp_path):
    document = yaml.safe_load(matters.MATTERS_PATH.read_text(encoding="utf-8"))
    unidentified = next(m for m in document if m["id"] == "FM-0006")
    unidentified["objections"][0]["facts"] = [{"condition": "registered_by_another", "value": True, "source": "t"}]
    path = tmp_path / "matters.yaml"
    path.write_text(yaml.dump(document, allow_unicode=True), encoding="utf-8")
    broken = {m.id: m for m in matters.load(path)}["FM-0006"]
    assert any("names no test" in error for error in broken.errors)


def test_an_objection_with_no_test_must_carry_the_customers_words(tmp_path):
    document = yaml.safe_load(matters.MATTERS_PATH.read_text(encoding="utf-8"))
    del next(m for m in document if m["id"] == "FM-0006")["objections"][0]["customer_words"]
    path = tmp_path / "matters.yaml"
    path.write_text(yaml.dump(document, allow_unicode=True), encoding="utf-8")
    assert {m.id: m for m in matters.load(path)}["FM-0006"].errors


# --- explanations with no matter (D4: requirements, the application process) -------


def _general_leaves(node):
    if node["kind"] in ("all", "any"):
        for child in node["children"]:
            yield from _general_leaves(child)
    else:
        yield node


@pytest.mark.parametrize("test_id", sorted(TESTS))
def test_requirements_read_no_state_ask_nothing_and_label_every_source(test_id):
    """A test explained with no matter: no condition is met, not met or open, nothing is
    asked, every evaluative condition is said to be the Registrar's assessment, and every
    source is labelled by where it comes from."""
    r = engine.requirements(TESTS[test_id])
    assert r["asks"] == [] and r["stamp"] == engine.GENERAL_STAMP
    flat = yaml.dump(r)
    assert "state:" not in flat and engine.OPEN not in flat
    leaves = list(_general_leaves(r["condition"]))
    assert leaves and all(("assessment" in leaf["settled_by"]) == (leaf["kind"] == "evaluative") for leaf in leaves)
    for s in r["sources"]:
        assert s["authority"] == ("practice" if s["ref"].startswith("TMM/") else "law"), s
    text = engine.render_requirements(r)
    assert _outcomes(text) == [] and engine.GENERAL_STAMP in text


def test_requirements_keep_each_exceptions_kind():
    """Section 44's two exceptions are a discretion and a bar, and say so; neither becomes a must."""
    exceptions = {x["id"]: x for x in engine.requirements(TESTS["GL-0001"])["exceptions"]}
    assert exceptions["honest_concurrent_use"]["effect"]["kind"] == "discretion"
    assert "may, but need not" in exceptions["honest_concurrent_use"]["effect"]["reads"]
    assert exceptions["prior_continuous_use"]["effect"]["kind"] == "bar"
    assert all(" must " not in x["effect"]["reads"] for x in exceptions.values())


def test_requirements_split_evidence_into_relevance_and_sufficiency():
    evidence = engine.requirements(TESTS["GL-0003"])["evidence"]
    assert {e["kind"] for e in evidence} == {"relevance", "sufficiency"}
    assert all(e["authority"] == "practice" and e["for"] for e in evidence)


def test_the_application_process_from_filing_names_every_step_and_computes_no_date():
    """GP-0002, walked through with no matter: every step in order, the report handing over
    to GP-0001, what each way on depends on, the time rules, and no date or outcome."""
    w = engine.walkthrough(PROCESSES["GP-0002"], PROCESSES)
    assert [s["id"] for s in w["steps"]] == [s["id"] for s in PROCESSES["GP-0002"]["steps"]]
    assert w["steps"][0]["kind"] == "start" and {s["kind"] for s in w["steps"][-2:]} == {"end"}
    report = next(s for s in w["steps"] if s["id"] == "report")
    assert report["continues_in"]["process"] == "GP-0001"
    published = next(s for s in w["steps"] if s["id"] == "acceptance_published")
    assert {n["to"] for n in published["next"]} == {"opposition", "registration"}
    assert all(n["needs"] for n in published["next"])
    assert "opposition_period" in {d["id"] for d in published["time_rules"]}
    text = engine.render_walkthrough(w)
    assert not re.search(r"\d{4}-\d{2}-\d{2}", text)
    assert _outcomes(text) == [] and engine.GENERAL_STAMP in text
    assert all(s["authority"] == "law" for s in w["sources"])


# --- the inner structure in the graph (ADR-0144) ------------------------------------


@pytest.fixture(scope="module")
def authored_graph():
    rdflib = pytest.importorskip("rdflib")
    return rdflib.Graph().parse(REPO_ROOT / "graph" / "authored.ttl", format="turtle")


def test_the_graph_holds_each_tests_tree_exceptions_and_effects(authored_graph):
    """GL-0001 in the committed graph: its root an all-group of four parts, an any-group
    inside it, each leaf typed fact or evaluative as the record says, two exceptions whose
    effects are a discretion and a bar, and every quoted element anchored to an evidence
    item carrying the exact words."""
    from rdflib import Literal
    from rdflib.namespace import RDF

    from tm_knowledge.ontology.namespaces import TMK, assertion_node, element_node

    g, gl = authored_graph, assertion_node("GL-0001")
    root = g.value(gl, TMK.hasCondition)
    assert g.value(root, TMK.conditionJoin) == Literal("all") and len(set(g.objects(root, TMK.conditionPart))) == 4
    record = TESTS["GL-0001"]
    leaves = list(procedure.leaves(record["condition"]))
    for x in record["exceptions"]:
        leaves += list(procedure.leaves(x["condition"]))
    for leaf in leaves:
        node = element_node(gl, "element", leaf["id"])
        expected = TMK.EvaluativeCondition if leaf["kind"] == "evaluative" else TMK.FactCondition
        assert (node, RDF.type, expected) in g, leaf["id"]
        anchor = g.value(node, TMK.anchoredBy)
        assert str(g.value(anchor, TMK.quote)) == leaf["quote"] and str(g.value(anchor, TMK.upstreamRef)) == leaf["ref"]
        assert g.value(node, TMK.reviewStatus) == Literal("unreviewed") and g.value(node, TMK.elementOf) == gl
    kinds = {str(g.value(g.value(x, TMK.hasEffect), TMK.effectKind)) for x in g.objects(gl, TMK.hasException)}
    assert kinds == {"discretion", "bar"}
    assert all(g.value(n, TMK.clarifyingQuestion) is None for n in g.subjects(RDF.type, TMK.EvaluativeCondition))


def test_the_graph_holds_each_templates_steps_transitions_and_time_rules(authored_graph):
    from rdflib.namespace import RDF

    from tm_knowledge.ontology.namespaces import TMK, assertion_node, element_node

    g = authored_graph
    for process_id, record in PROCESSES.items():
        node = assertion_node(process_id)
        assert len(set(g.objects(node, TMK.hasStep))) == len(record["steps"])
        assert len(set(g.objects(node, TMK.hasTransition))) == len(record["transitions"])
        assert len(set(g.objects(node, TMK.hasTimeRule))) == len(record.get("deadlines") or ())
        for transition in g.objects(node, TMK.hasTransition):
            assert (g.value(transition, TMK.fromStep), RDF.type, TMK.ProcessStep) in g
            assert (g.value(transition, TMK.toStep), RDF.type, TMK.ProcessStep) in g
    report = element_node(assertion_node("GP-0002"), "element", "report")
    assert g.value(report, TMK.continuesIn) == assertion_node("GP-0001")
    deferments = [t for t in g.objects(assertion_node("GP-0001"), TMK.hasTransition)
                  if g.value(t, TMK.onlyForGround) is not None]
    assert deferments and all(str(g.value(t, TMK.onlyForGround)).endswith("TMA1995/s44") for t in deferments)


# --- A06 step 2: a question reaches the structured test ---------------------------


def test_a06_a_question_naming_section_44_reaches_its_conditions_and_both_exceptions():
    from tm_knowledge.search import structured

    tests = structured.payload(TESTS)
    reached = structured.find("What does section 44(3) say about honest concurrent use?", [], tests)
    assert reached == [{"id": "GL-0001", "why": ["named"]}]
    gl = next(t for t in tests if t["id"] == "GL-0001")
    assert {x["kind"] for x in gl["exceptions"]} == {"discretion", "bar"}
    assert {leaf["id"] for leaf in _general_leaves(gl["condition"])} == {
        leaf["id"] for leaf in procedure.leaves(TESTS["GL-0001"]["condition"])}
    assert all(t["review_status"] == "unreviewed" for t in tests)


def test_a06_a_recognised_ground_reaches_its_test_and_an_unrelated_question_reaches_none():
    from tm_knowledge.search import structured

    tests = structured.payload(TESTS)
    assert structured.find("Can I overcome the citation?", ["GC-0006"], tests) == [{"id": "GL-0001", "why": ["ground"]}]
    assert structured.find("How do I renew a registration?", ["GC-0106"], tests) == []
    # A number with no word saying which instrument names nothing (citations' rule).
    assert structured.find("What does 44(3) say?", [], tests) == []


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
        if issue["test"] is None:
            continue  # asks for the ground itself (test_a12_everyday_wording_is_asked_about_never_chosen)
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


def test_the_page_draws_every_view_with_its_text_equivalent():
    """A09: an issue card per objection, the timeline and the evidence view, each with a
    text equivalent from the same object; the timeline has an accessible title and
    description; state is a mark and a word, not a colour alone."""
    import html as html_module

    from tm_knowledge.explain import page

    explanations = [_explain(MATTERS[k]) for k in sorted(MATTERS)]
    requirements = [engine.requirements(TESTS[k]) for k in sorted(TESTS)]
    walkthroughs = [engine.walkthrough(PROCESSES["GP-0002"], PROCESSES)]
    out = page.render_page(explanations, requirements, walkthroughs)
    assert out.count("<section>") == len(MATTERS) + 2
    assert out.count("<h3>Objection o") == sum(len(e["issues"]) for e in explanations)
    assert out.count('role="img"') == len(MATTERS) + 1 and out.count("<desc") == len(MATTERS) + 1
    for r in requirements:
        assert html_module.escape(engine.render_requirements(r)) in out
    assert html_module.escape(engine.render_walkthrough(walkthroughs[0])) in out
    assert out.count("Text equivalent") >= len(MATTERS) + 1  # every timeline, and FM-0004's evidence
    assert "Not for customers" in out and "recorded as met" in out
    for e in explanations:
        assert html_module.escape(engine.render_text(e)) in out
    plain = re.sub(r"<[^>]+>", " ", html_module.unescape(out))
    assert _outcomes(plain) == []

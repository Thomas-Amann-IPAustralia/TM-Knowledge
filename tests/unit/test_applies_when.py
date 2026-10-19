"""A relationship can say when it holds, in its sentence's own words (the review response, F14).

A relationship record had subject, predicate, object, evidence, tier and modality, and
nowhere to hold the condition or hedge under which its sentence states it, so a
qualified sentence became an unqualified edge: GR-0432's consent is needed only for an
assignment recorded after the documents go to the Commission, GR-0526's filing date
is the registration date "in most cases". `applies_when` holds that condition, copied
from the supporting sentence, never retyped; the graph states it on the reified
record, and the explorer shows it wherever it shows the edge.

Not yet given to the live answering model: that changes what the chatbot is told,
which is the owner's decision (the response's decision 4).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tm_knowledge.stage0 import harness, schemas

SENTENCE = ("If an application to record assignment is received after the documentation required under "
            "reg 16.2 has been sent to the Commission but before the trade mark has been registered, the "
            "assignment will not be recorded unless the applicant provides evidence that the Commission has "
            "consented to the transfer of ownership (section 180A).")
CONDITION = ("an application to record assignment is received after the documentation required under "
             "reg 16.2 has been sent to the Commission but before the trade mark has been registered")


def _record(**extra):
    return {"id": "GR-9001", "subject": "GC-0086", "predicate": "requiresConsentOf", "object": "GC-0133",
            "source_ref": "TMM/Part35/10#1", "supporting_text": SENTENCE, "span": [0, 10],
            "source_content_hash": "sha256:" + "a" * 64, "tier": 3, "modality": "must",
            "approved_by": None, "approved_date": None, **extra}


def test_the_relationship_schema_takes_a_condition():
    assert not schemas.validate(_record(applies_when=CONDITION), "gold_relationship")
    assert not schemas.validate(_record(), "gold_relationship"), "the field is optional"
    assert schemas.validate(_record(applies_when=""), "gold_relationship"), "an empty condition says nothing"


@pytest.mark.parametrize("condition, defect", [
    (CONDITION, False),
    (" ".join(CONDITION.split()[:12]) + "\n " + " ".join(CONDITION.split()[12:]), False),
    ("after the documents have been sent to the Commission", True),
], ids=["verbatim", "rewrapped", "retyped"])
def test_a_condition_is_the_sentences_own_words(condition, defect):
    entry = SimpleNamespace(record_id="GR-9001", record=_record(applies_when=condition), sound=True)
    authored = SimpleNamespace(of=lambda kind: (entry,) if kind == "gold_relationship" else ())
    found = [f for f in harness._authored_conditions(authored) if f.severity is harness.Severity.DEFECT]
    assert bool(found) is defect, found
    if defect:
        assert found[0].severity is harness.Severity.DEFECT


@pytest.mark.rdf
def test_the_graph_states_the_condition_on_the_reified_record():
    from rdflib import Graph, URIRef

    from tm_knowledge.ontology import build
    from tm_knowledge.ontology.namespaces import TMK

    graph, node = Graph(), URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GR-9001")
    build._qualifiers(graph, node, _record(applies_when=CONDITION))
    stated = graph.value(node, TMK.appliesWhen)
    assert str(stated) == CONDITION and stated.language == "en-AU"
    assert str(graph.value(node, TMK.modality)) == "must"
    bare = Graph()
    build._qualifiers(bare, node, _record(modality=None))
    # Absent stays absent: no condition and no modality is stated. What is stated is the
    # computed condition state (R07), so "none" and "nobody looked" stay apart.
    assert not {TMK.modality, TMK.appliesWhen, TMK.hedge} & set(bare.predicates()), "absent stays absent"
    assert TMK.conditionState in set(bare.predicates())


def test_the_explorer_carries_the_condition_with_the_edge():
    from tm_knowledge.explorer import build as explorer

    entry = SimpleNamespace(record_id="GR-9001", record=_record(applies_when=CONDITION), sound=True,
                            envelope={"authored_by": "x", "authored_date": "2026-10-16",
                                      "review_status": "unreviewed", "evidence": []})
    gold = {"gold_relationship": ()}
    authored = SimpleNamespace(of=lambda kind: (entry,) if kind == "gold_relationship" else ())
    (relation,) = explorer._relations(gold, authored)
    assert relation["when"] == CONDITION


# --- the hedge, split from the condition (S041, the second review response R01) -----


def test_a_hedge_is_the_sentences_own_words_and_is_stated_apart():
    assert not schemas.validate(_record(hedge="unless"), "gold_relationship")
    retyped = SimpleNamespace(record_id="GR-9001", record=_record(hedge="normally"), sound=True)
    authored = SimpleNamespace(of=lambda kind: (retyped,) if kind == "gold_relationship" else ())
    found = [f for f in harness._authored_conditions(authored) if f.severity is harness.Severity.DEFECT]
    assert found and "hedge" in found[0].message


@pytest.mark.rdf
def test_the_graph_states_the_hedge_beside_the_condition():
    from rdflib import Graph, URIRef

    from tm_knowledge.ontology import build
    from tm_knowledge.ontology.namespaces import TMK

    graph, node = Graph(), URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GR-9001")
    build._qualifiers(graph, node, _record(applies_when=CONDITION, hedge="unless"))
    assert str(graph.value(node, TMK.hedge)) == "unless"
    assert str(graph.value(node, TMK.appliesWhen)) == CONDITION


def test_the_path_line_says_how_strongly_and_only_when_it_is_recorded():
    from tm_knowledge.bulk import jobs

    labels = {"GC-0001": "a", "GC-0002": "b"}
    hedged = jobs.path_line(labels, ("GC-0001", "qualifies", "GC-0002", "GR-1", "authored", "", "if x", "rarely"))
    assert hedged.endswith('applies when "if x"; hedged "rarely")')
    plain = jobs.path_line(labels, ("GC-0001", "qualifies", "GC-0002", "GR-1", "authored", "", "if x", ""))
    assert plain.endswith('applies when "if x")'), "a line with no hedge is unchanged"


# --- R07: the condition state, set by rule (S041) ----------------------------------


@pytest.mark.parametrize("extra, text, expected", [
    ({"applies_when": "where it is defended"}, "The Registrar decides where it is defended.", "stated"),
    ({}, "The Registrar decides the opposition.", "none_stated"),
    ({}, "The Registrar decides if it is defended.", "not_assessed"),
    ({"no_condition": "the 'if' conditions another clause"}, "The Registrar decides if it is defended.",
     "assessed_none"),
], ids=["stated", "none-stated", "not-assessed", "assessed-none"])
def test_the_condition_state_is_set_by_rule(extra, text, expected):
    from tm_knowledge.ontology import conditions

    assert conditions.state(_record(supporting_text=text, **extra)) == expected


def test_the_proceeding_and_mark_type_come_from_the_part_and_only_where_it_fixes_them():
    from tm_knowledge.ontology import conditions

    assert conditions.proceeding(_record(source_ref="TMM/Part49/4#1")) == "removal_for_non_use"
    assert conditions.mark_type(_record(source_ref="TMM/Part35/4#1")) == "certification"
    assert conditions.proceeding(_record(source_ref="TMM/Part52/1#1")) is None, "hearings: several proceedings"
    assert conditions.proceeding(_record(source_ref="TMA1995/s41")) is None
    assert conditions.mark_type(_record(source_ref="TMM/Part29/1#1")) is None


def test_a_record_with_a_condition_and_a_reason_it_has_none_is_a_defect():
    entry = SimpleNamespace(record_id="GR-9001", record=_record(applies_when=CONDITION, no_condition="x"), sound=True)
    authored = SimpleNamespace(of=lambda kind: (entry,) if kind == "gold_relationship" else ())
    found = [f for f in harness._authored_conditions(authored) if f.severity is harness.Severity.DEFECT]
    assert found and "reason it has none" in found[0].message


@pytest.mark.rdf
def test_the_graph_states_the_condition_state_and_the_part_context():
    from rdflib import Graph, URIRef

    from tm_knowledge.ontology import build
    from tm_knowledge.ontology.namespaces import TMK

    graph, node = Graph(), URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GR-9001")
    build._qualifiers(graph, node, _record(source_ref="TMM/Part49/4#1", supporting_text="Files a notice if it wishes."))
    assert str(graph.value(node, TMK.conditionState)) == "not_assessed"
    assert str(graph.value(node, TMK.proceeding)) == "removal_for_non_use"
    assert graph.value(node, TMK.markType) is None


def test_no_committed_relationship_is_left_not_assessed():
    """S041 assessed all 101; a relationship written later with a conditional word and
    no condition shows on the harness's note until someone does the same."""
    import yaml

    from tm_knowledge.config import REPO_ROOT
    from tm_knowledge.ontology import conditions

    rows = yaml.safe_load((REPO_ROOT / "authored" / "relationships.yaml").read_text(encoding="utf-8"))
    left = [r["id"] for r in rows if conditions.state(r) == "not_assessed"]
    assert left == []
    gr0319 = next(r for r in rows if r["id"] == "GR-0319")
    assert gr0319["applies_when"] == "it wishes to continue with the non-use application"
    assert conditions.proceeding(gr0319) == "removal_for_non_use"

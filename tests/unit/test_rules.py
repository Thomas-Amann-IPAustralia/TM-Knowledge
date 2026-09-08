"""Each CONSTRUCT rule fires where it should and stays quiet where it should not.

`queries/README.md` requires both halves for every rule: *the test that proves it
fires correctly, and the test that proves it does not fire on the near-miss
case.* A rule with only the first is a rule nobody has shown to be selective,
and a rule that fires on everything passes a fires-test.

The rule files name these tests by path in their headers, and
`test_every_rule_names_tests_that_exist` checks the names resolve — so a renamed
test cannot leave a rule pointing at nothing.
"""

from __future__ import annotations

import dataclasses
import re

import pytest
from rdflib import Dataset, Graph, Literal, URIRef

from tm_knowledge.ontology import rules
from tm_knowledge.ontology.namespaces import (
    APPROVED_GRAPH,
    INFERRED_GRAPH,
    SOURCE_GRAPH,
    TMK,
    bind_all,
)
from tm_knowledge.ontology.tbox import load as load_tbox

FIXTURE = URIRef("https://example.org/fixture/")


def rule(rule_id: str) -> rules.Rule:
    found = [r for r in rules.load_rules() if r.rule_id == rule_id]
    assert found, f"no rule file declares {rule_id}"
    return found[0]


def dataset_with(source: list[tuple], approved: list[tuple]) -> Dataset:
    """A minimal dataset in the shape the rules query: TBox in the default
    graph, facts in the two named graphs."""
    dataset = bind_all(Dataset())
    for triple in load_tbox():
        dataset.add(triple)
    for triple in source:
        dataset.graph(SOURCE_GRAPH).add(triple)
    for triple in approved:
        dataset.graph(APPROVED_GRAPH).add(triple)
    return dataset


def chunk(ref: str) -> tuple[URIRef, list[tuple]]:
    node = URIRef(f"https://data.ipaustralia.gov.au/tmk/ref/{ref.replace('#', '%23')}")
    return node, [
        (node, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), TMK.Chunk),
        (node, TMK.upstreamRef, Literal(ref)),
        (node, TMK.authorityKind, Literal("practice")),
    ]


def mention(name: str, passage: URIRef, mention_class) -> list[tuple]:
    node = URIRef(FIXTURE + name)
    return [
        (node, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), TMK.EntityMention),
        (node, TMK.mentionClass, mention_class),
        (node, TMK.sourcePassage, passage),
    ]


# --- RULE-0001 -------------------------------------------------------------


def test_rule_0001_fires_on_the_mixed_chunk():
    """A chunk holding both a provision mention and a practice mention.

    This is GX-0001's own case: TMM/Part29/1#1 quotes s 43 in full and then
    states the Registrar's practice, and the two must stay distinguishable in
    anything derived from it.
    """
    node, facts = chunk("TMM/Part29/1#1")
    produced = rule("RULE-0001").construct(
        dataset_with(
            facts,
            mention("law", node, TMK.LegislativeProvision)
            + mention("practice", node, TMK.ManualInstruction),
        )
    )
    assert (node, TMK.mixedAuthority, Literal(True)) in produced
    inference = next(produced.subjects(TMK.producedByRule, None))
    # Stamped from `approved-by:`, which for this rule still reads PENDING: the
    # owner asked to see the flagged passages before ruling (OQ-0003).
    assert produced.value(inference, TMK.reviewStatus) == Literal("candidate")
    assert produced.value(inference, TMK.requiresHumanReview) == Literal(True)
    assert set(produced.objects(inference, TMK.derivedFrom)) >= {node}


def test_rule_0001_does_not_fire_on_a_practice_only_chunk():
    """The near miss: a chunk with practice mentions and no quoted provision.

    Most of the corpus looks like this. A rule that fired here would classify
    every Manual passage as carrying quoted law, which would make the flag mean
    nothing.
    """
    node, facts = chunk("TMM/Part29/2/2/2")
    produced = rule("RULE-0001").construct(
        dataset_with(
            facts,
            mention("practice-a", node, TMK.ManualInstruction)
            + mention("practice-b", node, TMK.ManualInstruction),
        )
    )
    assert len(produced) == 0


def test_rule_0001_does_not_fire_across_two_chunks():
    """A provision mention in one chunk and a practice mention in another is not
    a mixed chunk. The join is on the passage, and this proves it."""
    first, first_facts = chunk("TMM/Part29/1#1")
    second, second_facts = chunk("TMM/Part29/2/2/2")
    produced = rule("RULE-0001").construct(
        dataset_with(
            first_facts + second_facts,
            mention("law", first, TMK.LegislativeProvision)
            + mention("practice", second, TMK.ManualInstruction),
        )
    )
    assert len(produced) == 0


# --- RULE-0002 -------------------------------------------------------------


def test_rule_0002_fires_for_a_passage_with_dependants():
    node, facts = chunk("TMM/Part29/2/2/3")
    dependant = URIRef(FIXTURE + "GR-0005")
    produced = rule("RULE-0002").construct(
        dataset_with(
            facts,
            [
                (dependant, TMK.sourcePassage, node),
                (dependant, TMK.goldRecord, Literal("GR-0005")),
            ],
        )
    )
    assert (dependant, TMK.impactedBy, node) in produced
    inference = next(produced.subjects(TMK.producedByRule, None))
    assert produced.value(inference, TMK.inferenceKind) == Literal("impact")
    # The owner approved this one on 2026-09-08 (OQ-0004), so its output is no
    # longer quarantined. The header is what says so, and nothing else.
    assert produced.value(inference, TMK.reviewStatus) == Literal("approved")
    assert produced.value(inference, TMK.requiresHumanReview) == Literal(False)


def test_rule_0002_does_not_fire_for_an_unreferenced_passage():
    """The near miss, and the one worth stating in words: a passage nothing
    points at produces nothing. That is a fact about what is *recorded*, never a
    finding that nothing is affected (Q-28)."""
    node, facts = chunk("TMM/Part29/12#1")
    produced = rule("RULE-0002").construct(dataset_with(facts, []))
    assert len(produced) == 0


# --- the headers ------------------------------------------------------------


@pytest.mark.parametrize("rule_file", rules.load_rules(), ids=lambda r: r.rule_id)
def test_every_rule_names_tests_that_exist(rule_file):
    """A rule's `fires-test` and `near-miss-test` must resolve to real tests.

    Otherwise the header is a promise nobody keeps, which is how a rule ends up
    with the appearance of coverage.
    """
    for reference in (rule_file.fires_test, rule_file.near_miss_test):
        _path, _, name = reference.partition("::")
        assert name in globals(), (
            f"{rule_file.rule_id} names {reference}, and {name} is not defined here"
        )


@pytest.mark.parametrize("rule_file", rules.load_rules(), ids=lambda r: r.rule_id)
def test_an_approval_names_someone_and_a_date(rule_file):
    """A name and a date are the approval artefact (ADR-0039), and a rule is not
    exempt from that. `PENDING — <explanation>` must not read as an approval,
    which is why `is_approved` matches the first word rather than the line."""
    if rule_file.is_approved:
        assert re.search(r"\d{4}-\d{2}-\d{2}", rule_file.approved_by), (
            f"{rule_file.rule_id} claims approval with no date on it"
        )
        assert "PENDING" not in rule_file.approved_by.split("—")[0]
    else:
        assert "PENDING" in rule_file.approved_by


@pytest.mark.parametrize("rule_file", rules.load_rules(), ids=lambda r: r.rule_id)
def test_no_rule_declares_its_own_review_status(rule_file):
    """A CONSTRUCT template that sets `tmk:reviewStatus` is a rule asserting its
    own approval, and it can drift from the header in either direction — the
    dangerous one being a body that still says `candidate` after a person
    approved the rule, so an approval the owner gave changes nothing in the data.
    The status is stamped from the header; the body must not touch it."""
    body = rule_file.text.split("CONSTRUCT", 1)[-1]
    assert "reviewStatus" not in body
    assert "requiresHumanReview" not in body


def test_a_body_that_stamps_its_own_status_is_refused():
    """The guard above is a lint over the files as they stand. This one proves
    the runtime refuses such a rule rather than quietly overwriting it."""
    node, facts = chunk("TMM/Part29/2/2/3")
    dependant = URIRef(FIXTURE + "GR-0005")
    original = rule("RULE-0002")
    tampered = dataclasses.replace(
        original,
        text=original.text.replace(
            'tmk:inferenceKind "impact" ;',
            'tmk:inferenceKind "impact" ;\n             tmk:reviewStatus "approved" ;',
        ),
    )
    with pytest.raises(rules.MalformedRule):
        tampered.construct(
            dataset_with(
                facts,
                [(dependant, TMK.sourcePassage, node), (dependant, TMK.goldRecord, Literal("GR-0005"))],
            )
        )

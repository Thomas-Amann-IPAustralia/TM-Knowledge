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
def test_no_rule_claims_approval_it_does_not_have(rule_file):
    """Stage 9 requires an expert to approve every reasoning template before
    deployment. Nobody has approved these, and the flag must say so — the check
    exists because the phrase is `PENDING — <explanation>`, and a substring test
    against the whole line reads that as an approval."""
    assert not rule_file.is_approved
    assert "PENDING" in rule_file.approved_by

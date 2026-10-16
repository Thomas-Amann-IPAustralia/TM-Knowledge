"""The SHACL gate sees every named graph, and knows which one a node sits in.

These tests call `validate.run` on an `rdflib.Dataset`, the way `tmk-shacl` does,
rather than pySHACL on a flat graph the way the shape fixtures do. The two defects
they hold were invisible to a flat-graph test (the review response, F02):

1. **The inferred graph was never validated.** `validate._flatten` merged source,
   approved, authored and the default graph, and left out the inferred one, so
   `InferredAssertionShape` and `BoundedReasoningShape`, the enforcement point for
   "no rule derives an evaluative conclusion", never saw a real inference.
2. **Placement was invisible.** Flattening drops which named graph a triple sat in,
   so a complete machine-written assertion put in the approved graph passed exactly
   as it would in the authored one. The named graphs are the governance boundary
   (CLAUDE.md rule 4), and the gate now checks it before flattening.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.rdf


def _authored_envelope(node):
    """A machine-written assertion carrying everything the authored shapes require."""
    from rdflib import Literal
    from rdflib.namespace import RDF, XSD

    from tm_knowledge.ontology.namespaces import TMK

    return [
        (node, RDF.type, TMK.AuthoredAssertion),
        (node, TMK.goldRecord, Literal("GR-9999")),
        (node, TMK.origin, Literal("authored")),
        (node, TMK.reviewStatus, Literal("unreviewed")),
        (node, TMK.authoredBy, Literal("claude-code-agent-S036")),
        (node, TMK.authoredDate, Literal("2026-10-16", datatype=XSD.date)),
        (node, TMK.authoringBasis, Literal("general_knowledge")),
        (node, TMK.authoringReasoning, Literal("A fixture.", lang="en-AU")),
        (node, TMK.extractionMethod, Literal("authored")),
    ]


def _dataset(graph, triples):
    from rdflib import Dataset

    dataset = Dataset()
    named = dataset.graph(graph)
    for triple in triples:
        named.add(triple)
    return dataset


def test_an_unexplained_inference_in_the_inferred_graph_is_a_defect():
    from rdflib import URIRef
    from rdflib.namespace import RDF

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import INFERRED_GRAPH, TMK

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/IX-fixture")
    report = validate.run(_dataset(INFERRED_GRAPH, [(node, RDF.type, TMK.InferredAssertion)]))
    assert report.exit_code == 1, "an inference naming no rule and no premises passed the gate"
    shapes = {finding.shape for finding in report.by_severity("defect")}
    assert "An inference names its rule and its premises" in shapes


def test_a_machine_written_assertion_in_the_approved_graph_is_a_defect():
    from rdflib import URIRef

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, AUTHORED_GRAPH

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GR-9999")
    triples = _authored_envelope(node)

    control = validate.run(_dataset(AUTHORED_GRAPH, triples))
    assert control.exit_code == 0, [str(f) for f in control.by_severity("defect")]

    misplaced = validate.run(_dataset(APPROVED_GRAPH, triples))
    assert misplaced.exit_code == 1, "machine-written content in the approved graph passed the gate"
    assert any("graph" in finding.shape.lower() for finding in misplaced.by_severity("defect"))


@pytest.mark.parametrize(
    "graph, kind",
    [("authored", "ApprovedAssertion"), ("approved", "InferredAssertion"), ("source", "AuthoredAssertion")],
)
def test_an_assertion_class_outside_its_graph_is_a_defect(graph, kind):
    from rdflib import URIRef
    from rdflib.namespace import RDF

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import TMK, TMKG

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GR-9998")
    report = validate.run(_dataset(URIRef(TMKG[graph]), [(node, RDF.type, TMK[kind])]))
    placement = [f for f in report.by_severity("defect") if f.shape == validate.PLACEMENT_SHAPE]
    assert placement, f"a tmk:{kind} in the {graph} graph was not reported"

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


# --- SKOS S27: related is disjoint with broader's transitive closure ----------------
#
# GC-0017 (geographical reference) is skos:related to GC-0018 (geographical
# indication), and GC-0018 is recorded as a kind of GC-0017. SKOS's integrity
# condition S27 forbids both, and until S036 nothing checked it (the review response,
# F07). Both statements are signed, so the fix is a correction on the owner's ruling
# (ADR-0122): the gate reports a signed pair as a note for the owner, and fails anything
# a machine wrote. The owner confirmed the D2 ruling covers this pair (CHAT-0082), and
# GK-0037 removes the "related" link; the kind-of link stays.


def _skos(approved, authored):
    from rdflib import Dataset, URIRef
    from rdflib.namespace import SKOS

    from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, AUTHORED_GRAPH

    def term(name):
        return URIRef(f"https://example.org/fixture/{name}")

    dataset = Dataset()
    for graph, triples in ((APPROVED_GRAPH, approved), (AUTHORED_GRAPH, authored)):
        named = dataset.graph(graph)
        for subject, predicate, obj in triples:
            named.add((term(subject), getattr(SKOS, predicate), term(obj)))
    return dataset


def test_related_beside_a_machine_written_hierarchy_is_a_defect():
    from tm_knowledge.ontology import validate

    dataset = _skos(approved=[("x", "related", "y")], authored=[("x", "broader", "m"), ("m", "broader", "y")])
    found = validate.skos_integrity(dataset)
    assert [f.severity for f in found] == ["defect"], found


def test_a_machine_written_related_beside_a_signed_narrower_is_a_defect():
    from tm_knowledge.ontology import validate

    dataset = _skos(approved=[("y", "narrower", "x")], authored=[("y", "related", "x")])
    assert [f.severity for f in validate.skos_integrity(dataset)] == ["defect"]


def test_a_signed_pair_both_related_and_broader_is_reported_for_the_owner():
    from tm_knowledge.ontology import validate

    dataset = _skos(approved=[("x", "related", "y"), ("y", "broader", "x")], authored=[])
    found = validate.skos_integrity(dataset)
    assert [f.severity for f in found] == ["note"], found
    assert "owner" in found[0].message


def test_related_without_a_hierarchy_between_them_passes():
    from tm_knowledge.ontology import validate

    dataset = _skos(approved=[("x", "related", "y"), ("x", "broader", "z")], authored=[("y", "broader", "z")])
    assert validate.skos_integrity(dataset) == []


def test_the_committed_graph_has_no_s27_conflict_once_gk_0037_corrects_it():
    """Until S038 the signed geographical pair was the one note; the correction
    serves, so what the graph states no longer breaks S27, and the signed record
    in `eval/gold/` still says what was signed."""
    from rdflib import Dataset

    from tm_knowledge.config import REPO_ROOT
    from tm_knowledge.ontology import validate
    from tm_knowledge.stage0 import goldset

    dataset = Dataset()
    dataset.parse(REPO_ROOT / "graph" / "dataset.nq", format="nquads")
    assert validate.skos_integrity(dataset) == []
    signed = next(r for r in goldset.load()["gold_concept"] if r["id"] == "GC-0017")
    assert "GC-0018" in signed["related"], "eval/gold/ is never edited (ADR-0122)"

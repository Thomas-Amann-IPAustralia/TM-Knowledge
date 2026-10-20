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


# --- definitions and corrections carry the envelope (the second review response, R04) ---
#
# Until S041 the envelope shapes targeted tmk:AuthoredAssertion only, and a definition
# or a correction is a subclass of tmk:Assertion: either, with its author, date,
# reasoning and sources deleted, validated with 0 defects (Q-97).


def _anchor(record):
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF, XSD

    from tm_knowledge.ontology.namespaces import TMK, evidence_node

    anchor = evidence_node(record, 1)
    passage = URIRef("https://data.ipaustralia.gov.au/tmk/ref/TMM/Part29/1%231")
    return [
        (record, TMK.sourcePassage, passage),
        (record, TMK.evidence, anchor),
        (anchor, RDF.type, TMK.EvidenceAnchor),
        (anchor, TMK.sourcePassage, passage),
        (anchor, TMK.upstreamRef, Literal("TMM/Part29/1#1")),
        (anchor, TMK.spanStart, Literal(0, datatype=XSD.integer)),
        (anchor, TMK.spanEnd, Literal(10, datatype=XSD.integer)),
        (anchor, TMK.sourceContentHash, Literal("sha256:" + "0" * 64)),
        (anchor, TMK.quote, Literal("A fixture.")),
        (anchor, TMK.checkedAgainst, URIRef("https://data.ipaustralia.gov.au/tmk/ns/snapshot-fixture")),
    ]


def _definition(node, drop=()):
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF, SKOS

    from tm_knowledge.ontology.namespaces import TMK

    triples = [t for t in _authored_envelope(node) if t[1] != RDF.type]
    triples += [
        (node, RDF.type, TMK.Definition),
        (node, TMK.defines, URIRef("https://data.ipaustralia.gov.au/tmk/concept/GC-9999")),
        (node, SKOS.definition, Literal("A fixture.", lang="en-AU")),
        (node, TMK.definitionBasis, Literal("manual")),
        *_anchor(node),
    ]
    triples = [t for t in triples if t[1] not in drop]
    return [(s, p, o) if p != TMK.authoringBasis else (s, p, Literal("corpus_explicit")) for s, p, o in triples]


def _correction(node, drop=()):
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF

    from tm_knowledge.ontology.namespaces import TMK

    triples = [t for t in _authored_envelope(node) if t[1] != RDF.type]
    triples += [
        (node, RDF.type, TMK.Correction),
        (node, TMK.corrects, URIRef("https://data.ipaustralia.gov.au/tmk/concept/GC-9999")),
        (node, TMK.ruling, Literal("review/rulings/fixture.yaml#X1")),
        *_anchor(node),
    ]
    triples = [t for t in triples if t[1] not in drop]
    return [(s, p, o) if p != TMK.authoringBasis else (s, p, Literal("corpus_explicit")) for s, p, o in triples]


def test_a_complete_definition_and_correction_pass():
    from rdflib import URIRef

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import AUTHORED_GRAPH

    definition = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GD-9999")
    correction = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GK-9999")
    report = validate.run(_dataset(AUTHORED_GRAPH, _definition(definition) + _correction(correction)))
    assert report.exit_code == 0, [str(f) for f in report.by_severity("defect")]


def test_a_definition_without_its_envelope_is_a_defect():
    """The probe of R04: author, sources, reasoning and the concept deleted."""
    from rdflib import URIRef

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import AUTHORED_GRAPH, TMK

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GD-9999")
    stripped = _definition(
        node, drop=(TMK.authoredBy, TMK.sourcePassage, TMK.authoringReasoning, TMK.defines, TMK.evidence)
    )
    report = validate.run(_dataset(AUTHORED_GRAPH, stripped))
    paths = {f.path for f in report.by_severity("defect") if f.node == str(node)}
    assert {"authoredBy", "authoringReasoning", "defines", "evidence"} <= paths, paths
    assert any("cites the corpus" in f.shape for f in report.by_severity("defect") if f.node == str(node))


def test_a_correction_without_its_envelope_is_a_defect():
    from rdflib import URIRef

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import AUTHORED_GRAPH, TMK

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GK-9999")
    stripped = _correction(
        node, drop=(TMK.authoredBy, TMK.authoredDate, TMK.authoringReasoning, TMK.sourcePassage, TMK.ruling)
    )
    report = validate.run(_dataset(AUTHORED_GRAPH, stripped))
    paths = {f.path for f in report.by_severity("defect") if f.node == str(node)}
    assert {"authoredBy", "authoredDate", "authoringReasoning", "ruling"} <= paths, paths


@pytest.mark.parametrize("kind", ["StructuredTest", "ProcessTemplate"])
def test_a_structured_test_or_process_without_its_envelope_is_a_defect(kind):
    """ADR-0142's record classes are targeted by the envelope shapes as definitions are."""
    from rdflib import URIRef
    from rdflib.namespace import RDF

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import AUTHORED_GRAPH, TMK

    from rdflib import Literal
    from rdflib.namespace import RDFS

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GL-9999")
    whole = [t for t in _authored_envelope(node) if t[1] != RDF.type] + [
        (node, RDF.type, TMK[kind]), (node, RDFS.label, Literal("A fixture", lang="en-AU")), *_anchor(node)]
    if kind == "StructuredTest":
        whole.append((node, TMK.readsProvision, URIRef("https://data.ipaustralia.gov.au/tmk/ref/TMA1995/s44")))
        whole += _element(node, "condition", TMK.FactCondition, TMK.hasCondition)
        whole += _element(node, "effect", TMK.LegalEffect, TMK.hasEffect) + [
            (URIRef(f"{node}/effect"), TMK.effectKind, Literal("obligation"))]
    else:
        whole += _element(node, "element/filed", TMK.ProcessStep, TMK.hasStep) + [
            (URIRef(f"{node}/element/filed"), TMK.stepKind, Literal("start")),
            (URIRef(f"{node}/element/filed"), TMK.actorCapacity, Literal("applicant"))]
    assert not [f for f in validate.run(_dataset(AUTHORED_GRAPH, whole)).by_severity("defect") if f.node == str(node)]
    inner = (TMK.readsProvision, TMK.hasCondition, TMK.hasEffect, TMK.hasStep)
    stripped = [t for t in whole if t[1] not in (TMK.authoredBy, TMK.authoringReasoning, TMK.evidence, *inner)]
    paths = {f.path for f in validate.run(_dataset(AUTHORED_GRAPH, stripped)).by_severity("defect") if f.node == str(node)}
    assert {"authoredBy", "authoringReasoning", "evidence"} <= paths, paths
    assert ("readsProvision" in paths) == ("hasCondition" in paths) == ("hasEffect" in paths) == (kind == "StructuredTest")
    assert ("hasStep" in paths) == (kind == "ProcessTemplate")


def _element(record, path, cls, link):
    """One element of a structured record, with everything the element shapes require,
    and the TBox's subclass triple for its class (sh:class follows rdfs:subClassOf, and
    the gate's dataset carries the TBox)."""
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF, RDFS

    from tm_knowledge.ontology.namespaces import TMK, evidence_node

    node = URIRef(f"{record}/{path}")
    return [
        (record, link, node), (node, RDF.type, cls), (node, TMK.elementOf, record),
        (node, TMK.origin, Literal("authored")), (node, TMK.reviewStatus, Literal("unreviewed")),
        (node, TMK.statement, Literal("A fixture element.", lang="en-AU")),
        (node, TMK.sourceAuthority, Literal("law")), (node, TMK.anchoredBy, evidence_node(record, 1)),
        *((c, RDFS.subClassOf, s) for c, s in (
            (TMK.FactCondition, TMK.Condition), (TMK.EvaluativeCondition, TMK.Condition),
            (TMK.ConditionGroup, TMK.Condition), (TMK.Condition, TMK.RecordElement), (TMK.LegalEffect, TMK.RecordElement),
            (TMK.ProcessStep, TMK.RecordElement))),
    ]


@pytest.mark.parametrize("change, shape_path", [
    ("unanchored", "anchoredBy"), ("no authority", "sourceAuthority"), ("asked", "clarifyingQuestion"),
    ("approved", "approvedBy"), ("no kind", "effectKind"), ("no join", "conditionJoin"),
])
def test_an_element_of_a_structured_record_without_what_it_owes_is_a_defect(change, shape_path):
    """ADR-0144: each element quotes its source through an anchor and says law or practice;
    an evaluative condition is never asked as a fact; no element is approved; an effect
    names its kind; a group names its join. Each break is reported on the element."""
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import AUTHORED_GRAPH, TMK

    record = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GL-9999")
    leaf = _element(record, "element/similar", TMK.EvaluativeCondition, TMK.hasCondition)
    effect = _element(record, "effect", TMK.LegalEffect, TMK.hasEffect) + [
        (URIRef(f"{record}/effect"), TMK.effectKind, Literal("discretion"))]
    group = _element(record, "element/both", TMK.ConditionGroup, TMK.hasCondition) + [
        (URIRef(f"{record}/element/both"), TMK.conditionJoin, Literal("all")),
        (URIRef(f"{record}/element/both"), TMK.conditionPart, URIRef(f"{record}/element/similar"))]
    triples = leaf + effect + group + _anchor(record)
    target = {"no kind": f"{record}/effect", "no join": f"{record}/element/both"}.get(change, f"{record}/element/similar")
    baseline = {f.path for f in validate.run(_dataset(AUTHORED_GRAPH, triples)).by_severity("defect") if f.node == target}
    assert shape_path not in baseline, baseline
    node = URIRef(target)
    if change == "unanchored":
        triples = [t for t in triples if not (t[0] == node and t[1] == TMK.anchoredBy)]
    elif change == "no authority":
        triples = [t for t in triples if not (t[0] == node and t[1] == TMK.sourceAuthority)]
    elif change == "asked":
        triples.append((node, TMK.clarifyingQuestion, Literal("Is the mark similar?", lang="en-AU")))
    elif change == "approved":
        triples.append((node, TMK.approvedBy, Literal("someone")))
    elif change == "no kind":
        triples = [t for t in triples if t[1] != TMK.effectKind]
    elif change == "no join":
        triples = [t for t in triples if t[1] != TMK.conditionJoin]
    paths = {f.path for f in validate.run(_dataset(AUTHORED_GRAPH, triples)).by_severity("defect") if f.node == target}
    assert shape_path in paths, paths


def test_an_evidence_anchor_without_its_passage_or_version_is_a_defect():
    from rdflib import URIRef

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import AUTHORED_GRAPH, TMK, evidence_node

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/GD-9999")
    anchor = evidence_node(node, 1)
    triples = [t for t in _definition(node) if not (t[0] == anchor and t[1] in (TMK.upstreamRef, TMK.checkedAgainst))]
    report = validate.run(_dataset(AUTHORED_GRAPH, triples))
    paths = {f.path for f in report.by_severity("defect") if f.node == str(anchor)}
    assert {"upstreamRef", "checkedAgainst"} <= paths, paths


# --- an inference and its triple agree (R04) -----------------------------------------


def _inference(obj, emitted):
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF

    from tm_knowledge.ontology.namespaces import TMK

    node = URIRef("https://data.ipaustralia.gov.au/tmk/assertion/inf-fixture")
    chunk = URIRef("https://data.ipaustralia.gov.au/tmk/ref/TMM/Part29/1%231")
    triples = [
        (node, RDF.type, TMK.InferredAssertion),
        (node, TMK.assertionSubject, chunk),
        (node, TMK.assertionPredicate, TMK.mixedAuthority),
        (node, TMK.assertionObject, obj if obj is not None else chunk),
        (node, TMK.producedByRule, URIRef("https://data.ipaustralia.gov.au/tmk/prop/RULE-0001")),
        (node, TMK.derivedFrom, chunk),
        (node, TMK.reviewStatus, Literal("candidate")),
    ]
    if emitted:
        triples.append((chunk, TMK.mixedAuthority, Literal(True)))
    return triples


def test_an_inference_recording_a_triple_its_rule_did_not_emit_is_a_defect():
    """RULE-0001 until S041: the assertion's object was the chunk, the triple's `true`."""
    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import INFERRED_GRAPH

    report = validate.run(_dataset(INFERRED_GRAPH, _inference(None, emitted=True)))
    found = [f for f in report.by_severity("defect") if f.shape == validate.EQUALITY_SHAPE]
    assert len(found) == 2, [str(f) for f in found]  # the assertion's triple is absent, and the emitted one unrecorded


def test_an_inference_and_its_triple_in_agreement_pass():
    from rdflib import Literal

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import INFERRED_GRAPH

    report = validate.run(_dataset(INFERRED_GRAPH, _inference(Literal(True), emitted=True)))
    assert not [f for f in report.by_severity("defect") if f.shape == validate.EQUALITY_SHAPE]


def test_an_inferred_assertion_with_no_triple_behind_it_is_a_defect():
    from rdflib import Literal

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import INFERRED_GRAPH

    report = validate.run(_dataset(INFERRED_GRAPH, _inference(Literal(True), emitted=False)))
    assert [f for f in report.by_severity("defect") if f.shape == validate.EQUALITY_SHAPE]

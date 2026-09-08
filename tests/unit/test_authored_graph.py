"""The graph reads both stores, and cannot be made to confuse them.

`test_ontology_build.py` checks that the graph stayed a transformation of signed
content. This checks the property ADR-0080 added: it is now a transformation of
*two* stores, built by one mapping run twice, and the whole value of that design
rests on the two staying distinguishable afterwards.

Four things, and each of them would break quietly:

1. **An authored relationship is not a `tmk:ApprovedAssertion`.** Eight
   competency queries ask for that class by name. If an authored assertion could
   answer one, unreviewed content would be served as signed knowledge by a query
   nobody changed.
2. **Every node carries its own origin.** The named graph is the boundary, but a
   triple lifted out of it — into a report, a prompt, an evidence pack — has left
   the boundary behind. The stamp is what survives.
3. **The shapes refuse an authored assertion that claims an approver.** SHACL
   runs over the union of the named graphs, so this is the constraint that would
   catch machine output typed as signed on its way through.
4. **Nothing in the build sums the stores.**
"""

from __future__ import annotations

import pytest
from rdflib import Graph, Literal
from rdflib.namespace import RDF

from tm_knowledge.authored import store as authored_store
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology import validate as validate_module
from tm_knowledge.ontology.build import SCHEME, build
from tm_knowledge.ontology.namespaces import (
    APPROVED_GRAPH,
    AUTHORED_GRAPH,
    NAMED_GRAPHS,
    TMK,
)
from tm_knowledge.stage0 import goldset

pytestmark = pytest.mark.snapshot

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "authored"


@pytest.fixture(scope="module")
def built_with_authored():
    """The real gold set plus the sound authored fixture.

    The fixture rather than `authored/`, because `authored/` is empty today and
    a test that only passes while a directory is empty is a test that stops
    testing the day the work starts.
    """
    return build(authored=authored_store.load(FIXTURES / "sound"))


def test_the_authored_graph_is_declared_and_separate(built_with_authored):
    dataset, report = built_with_authored
    assert AUTHORED_GRAPH in NAMED_GRAPHS
    assert len(dataset.graph(AUTHORED_GRAPH)) > 0
    assert report.triples["authored"] == len(dataset.graph(AUTHORED_GRAPH))


def test_no_record_is_in_both_graphs(built_with_authored):
    """If the two mix once, no later audit can unmix them (ADR-0007).

    The shared triples are the concept scheme's own declaration and nothing
    else. That is deliberate and is not a leak: the scheme is a container, not a
    claim — each file declares the vocabulary its concepts are in so that
    `approved.ttl` and `authored.ttl` are each readable on their own, which is
    the whole reason `graph/README.md` reserves `.ttl` for single-graph files. A
    *record* in both graphs would be the failure, and that is what is asserted.
    """
    dataset, _ = built_with_authored
    approved = dataset.graph(APPROVED_GRAPH)
    authored = dataset.graph(AUTHORED_GRAPH)

    shared_subjects = {
        subject for subject, _, _ in approved
    } & {subject for subject, _, _ in authored}
    assert shared_subjects == {SCHEME}, sorted(str(s) for s in shared_subjects)[:5]

    signed_records = {str(value) for _, value in approved.subject_objects(TMK.goldRecord)}
    machine_records = {str(value) for _, value in authored.subject_objects(TMK.goldRecord)}
    assert signed_records and machine_records
    assert signed_records & machine_records == set()


def test_an_authored_node_is_never_an_approved_assertion(built_with_authored):
    """The eight competency queries ask for `tmk:ApprovedAssertion` by name."""
    dataset, _ = built_with_authored
    authored = dataset.graph(AUTHORED_GRAPH)
    assert list(authored.subjects(RDF.type, TMK.ApprovedAssertion)) == []


def test_every_authored_node_says_what_it_is(built_with_authored):
    """Origin and review status on the node, not only on the graph around it."""
    dataset, _ = built_with_authored
    authored = dataset.graph(AUTHORED_GRAPH)
    stamped = list(authored.subjects(TMK.origin, Literal("authored")))
    assert stamped, "the authored graph holds nodes and none of them says so"
    for node in stamped:
        statuses = list(authored.objects(node, TMK.reviewStatus))
        assert statuses == [Literal("unreviewed")], (
            f"{node} carries review status {statuses}. It is never defaulted and "
            f"never 'approved' — only a signature moves a record (ADR-0086)"
        )
    assert list(authored.subjects(TMK.origin, Literal("approved"))) == []


def test_every_approved_node_says_what_it_is_too(built_with_authored):
    """The stamp is on both stores. One store carrying it and the other not is
    an origin field that means "authored" by its absence, which is exactly the
    inference an audit must not have to make."""
    dataset, _ = built_with_authored
    approved = dataset.graph(APPROVED_GRAPH)
    assert list(approved.subjects(TMK.origin, Literal("authored"))) == []
    assert list(approved.subjects(TMK.origin, Literal("approved")))


def test_an_authored_concept_carries_its_model_and_basis(built_with_authored):
    dataset, _ = built_with_authored
    authored = dataset.graph(AUTHORED_GRAPH)
    assert list(authored.subject_objects(TMK.authoredBy))
    assert list(authored.subject_objects(TMK.authoringBasis))
    assert list(authored.subject_objects(TMK.authoringReasoning))


def test_the_build_reports_the_stores_apart(built_with_authored):
    _, report = built_with_authored
    assert report.concepts == goldset.load().count("gold_concept")
    assert report.authored.concepts == 2
    assert report.concepts != report.authored.concepts
    printed = "\n".join(report.lines())
    assert "signed by a named expert" in printed
    assert "validated by nobody" in printed


def test_a_refused_record_reaches_no_graph():
    """Refused, and named. Excluded from the graph is the right outcome; being
    excluded without anybody being told is the wrong one."""
    dataset, report = build(authored=authored_store.load(FIXTURES / "defective"))
    assert "GC-903" in report.authored_refused
    authored = dataset.graph(AUTHORED_GRAPH)
    assert not list(authored.subject_objects(TMK.goldRecord)) or all(
        str(value) != "GC-903"
        for _, value in authored.subject_objects(TMK.goldRecord)
    )


def test_the_shapes_refuse_an_authored_assertion_with_an_approver():
    """The one failure the whole scheme exists to prevent, as a shape.

    Built by hand rather than by loading a fixture store, because the store
    refuses such a record before the graph is built — which is correct, and
    means the shape would otherwise never be exercised. A shape nothing can
    reach is a shape nobody knows is broken.
    """
    data = Graph()
    node = TMK.term("test-authored-assertion")
    data.add((node, RDF.type, TMK.AuthoredAssertion))
    data.add((node, TMK.goldRecord, Literal("GC-999")))
    data.add((node, TMK.origin, Literal("authored")))
    data.add((node, TMK.reviewStatus, Literal("unreviewed")))
    data.add((node, TMK.extractionMethod, Literal("agent_authoring")))
    data.add((node, TMK.authoredBy, Literal("«model»-0.0")))
    data.add((node, TMK.authoringBasis, Literal("general_knowledge")))
    data.add((node, TMK.authoringReasoning, Literal("«why»", lang="en-AU")))
    from rdflib.namespace import XSD

    data.add((node, TMK.authoredDate, Literal("2026-09-08", datatype=XSD.date)))

    from pyshacl import validate as pyshacl_validate

    shapes = validate_module.load_shapes()
    conforms, _results, text = pyshacl_validate(data, shacl_graph=shapes, ont_graph=None)
    assert conforms, f"a well-formed authored assertion must pass:\n{text}"

    data.add((node, TMK.approvedBy, Literal("«name»")))
    conforms, _results, text = pyshacl_validate(data, shacl_graph=shapes, ont_graph=None)
    assert not conforms, "an authored assertion carrying an approver's name must fail"
    assert "approvedBy" in text or "approved" in text


def test_the_shapes_refuse_an_evidence_free_corpus_claim():
    """`general_knowledge` with no passage is honest. `corpus_explicit` with no
    passage is a claim about the corpus that names nothing."""
    from pyshacl import validate as pyshacl_validate
    from rdflib.namespace import XSD

    shapes = validate_module.load_shapes()
    data = Graph()
    node = TMK.term("test-authored-assertion")
    data.add((node, RDF.type, TMK.AuthoredAssertion))
    data.add((node, TMK.goldRecord, Literal("GC-999")))
    data.add((node, TMK.origin, Literal("authored")))
    data.add((node, TMK.reviewStatus, Literal("unreviewed")))
    data.add((node, TMK.extractionMethod, Literal("agent_authoring")))
    data.add((node, TMK.authoredBy, Literal("«model»-0.0")))
    data.add((node, TMK.authoredDate, Literal("2026-09-08", datatype=XSD.date)))
    data.add((node, TMK.authoringReasoning, Literal("«why»", lang="en-AU")))
    data.add((node, TMK.authoringBasis, Literal("corpus_explicit")))

    conforms, _results, _text = pyshacl_validate(data, shacl_graph=shapes, ont_graph=None)
    assert not conforms, "a corpus_explicit assertion citing no passage must fail"


def test_the_built_graph_still_validates_with_authored_content(built_with_authored):
    """ADR-0082 removed the review gate on serving unreviewed content, which
    makes the shapes the only thing between an authored record and a reader."""
    dataset, _ = built_with_authored
    report = validate_module.run(dataset)
    assert report.by_severity("defect") == [], "\n".join(
        str(finding) for finding in report.by_severity("defect")
    )


# ---------------------------------------------------------------------------
# `none_of_these` — the answer that asserts no class and is still an answer
# ---------------------------------------------------------------------------


def _typings(*records) -> authored_store.AuthoredSet:
    """An authored store holding exactly these concept typings."""
    from pathlib import Path

    envelope = {
        "review_status": "unreviewed",
        "authored_by": "«model»-0.0",
        "authored_date": "2026-09-08",
        "authoring_basis": "corpus_inferred",
        "reasoning": "«why this group»",
    }
    return authored_store.AuthoredSet(
        root=Path("«not read»"),
        entries=tuple(
            authored_store.AuthoredRecord(
                record_type="concept_type",
                record=dict(record),
                envelope=dict(envelope),
                source_file=Path("«not read»"),
                position=position,
            )
            for position, record in enumerate(records)
        ),
    )


def test_none_of_these_is_recorded_as_an_answer_and_asserts_no_class():
    """`none_of_these` says the four groups do not fit this concept. That is
    evidence about the taxonomy, and the opposite of a concept nobody has
    sorted — so the typing node, its record and its group are written, and only
    the `rdf:type` is withheld (ADR-0093, Q-50).

    Before this the record was skipped outright, which made 'sorted into
    none_of_these' and 'never sorted' the same state in the graph and undercounted
    the pass by every such record.
    """
    dataset, report = build(
        authored=_typings(
            {"id": "GT-9001", "concept": "GC-0020", "type": "exception"},
            {"id": "GT-9002", "concept": "GC-0044", "type": "none_of_these"},
        )
    )
    authored = dataset.graph(AUTHORED_GRAPH)
    groups = {str(value) for _, value in authored.subject_objects(TMK.conceptGroup)}
    assert groups == {"exception", "none_of_these"}

    typed = {str(s) for s, _ in authored.subject_objects(TMK.typedBy)}
    assert len(typed) == 2, "both concepts are linked to the typing that sorted them"
    assert (None, RDF.type, TMK.Exception) in authored
    # There is no tmk:NoneOfThese and there must not be one: the concept stays a
    # bare tmk:LegalConcept and the graph says so by saying nothing.
    assert not list(authored.subjects(RDF.type, TMK.NoneOfThese))

    assert report.authored.concept_types == 2, "both count as sorted, not one"

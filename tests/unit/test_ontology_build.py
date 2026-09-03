"""The graph is a transformation of approved content, and these are the checks
that it stayed one.

The tests worth having here are not "does it produce triples" — it plainly does
— but the three properties that, if they broke, would break quietly:

1. **Trust metadata survives.** `extraction` and `certainty` reach the graph
   intact, on a node rather than flattened into an edge (CLAUDE.md rule 3).
2. **A missing judgement stays missing.** Five approved relationships have no
   modality; the graph asserts none for them (guide §5.4).
3. **Nothing enters the approved graph that a person did not sign** (rule 4).
"""

from __future__ import annotations

import pytest
import yaml
from rdflib import Literal
from rdflib.namespace import RDF, SKOS

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology import relations
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, SOURCE_GRAPH, TMK
from tm_knowledge.ontology.tbox import MODULES, load as load_tbox
from tm_knowledge.stage0 import goldset

pytestmark = pytest.mark.snapshot


@pytest.fixture(scope="module")
def built():
    return build()


def test_every_module_parses_and_declares_itself():
    """A module that fails to parse takes the whole TBox with it, and a module
    with no `owl:Ontology` node cannot be imported by another."""
    graph = load_tbox()
    assert len(graph) > 500
    ontologies = set(graph.subjects(RDF.type, TMK.term("").__class__ and None)) if False else None
    from rdflib.namespace import OWL

    declared = set(graph.subjects(RDF.type, OWL.Ontology))
    assert len(declared) == len(MODULES), (
        f"{len(MODULES)} modules but {len(declared)} owl:Ontology declarations"
    )


def test_relations_file_matches_a_regeneration():
    """The dictionary is derived from the approved records, so the committed
    file must be exactly what regenerating produces. A hand-edit here would be
    an agent choosing the vocabulary (CLAUDE.md rule 1)."""
    assert relations.RELATIONS_PATH.read_text(encoding="utf-8") == relations.render(
        relations.collect()
    ), "ontology/draft/relations.ttl is stale — run `tmk-ontology relations --write`"


def test_every_predicate_used_is_on_the_closed_list(built):
    """`relations.ttl` is a closed list, and this is what makes that true of the
    graph rather than only of the document."""
    dataset, _ = built
    tbox = load_tbox()
    approved = {
        str(node) for node in tbox.subjects(RDF.type, TMK.ApprovedRelation)
    }
    used = {
        str(predicate)
        for predicate in dataset.graph(APPROVED_GRAPH).objects(None, TMK.assertionPredicate)
    }
    assert used <= approved, f"predicates used but not declared: {sorted(used - approved)}"


def test_citation_trust_metadata_survives(built):
    """The single most important property of the source graph.

    A loader or a builder that returns a bare chunk-to-provision edge has
    destroyed the only thing separating an author's assertion from upstream's
    inference, and it cannot be recovered afterwards.
    """
    dataset, _ = built
    source = dataset.graph(SOURCE_GRAPH)
    extractions = set(source.objects(None, TMK.extraction))
    certainties = set(source.objects(None, TMK.certainty))
    assert Literal("href") in extractions and Literal("regex") in extractions
    assert Literal("ambiguous") in certainties, (
        "the two ambiguous s 43 edges must reach the graph as ambiguous — an "
        "ambiguous edge is a reason to surface a passage, never to drop it (Q-07)"
    )
    assert Literal("default") in certainties


def test_ambiguous_edges_are_not_resolved(built):
    """Upstream refused to choose an instrument. So does this.

    Two numbers meet here and they are not the same number. `tmk-recon` reports
    **2** ambiguous edges: edges *to s 43*, which is what the reconnaissance
    report is about. The graph holds every citation on all 216 in-scope chunks,
    so its ambiguous count is much larger and includes edges to s 15, s 42, s 83
    and others. Both are right, and asserting the recon figure against the whole
    graph would be comparing a subset to a superset.
    """
    from tm_knowledge.ontology.namespaces import ref_node

    dataset, _ = built
    source = dataset.graph(SOURCE_GRAPH)
    ambiguous = list(source.subjects(TMK.certainty, Literal("ambiguous")))
    assert ambiguous, "the ambiguous edges must reach the graph as ambiguous (Q-07)"

    to_s43 = [
        citation
        for citation in ambiguous
        if source.value(citation, TMK.citedAuthority) == ref_node("TMA1995/s43")
    ]
    assert len(to_s43) == 2, "tmk-recon §5 reports exactly these two"
    assert {str(source.value(c, TMK.citingPassage)) for c in to_s43} == {
        str(ref_node("TMM/Part32B/2/2#1")),
        str(ref_node("TMM/Part32B/x-relevant-legislation25#1")),
    }
    for citation in ambiguous:
        assert source.value(citation, TMK.extraction) == Literal("regex"), (
            "certainty is present on regex edges only — an href edge carrying one "
            "means the loader invented a value"
        )


def test_missing_modality_stays_missing(built):
    """Five approved relationships carry no modality. The graph must carry none
    for them: whether a 'may' is possibility or permission is a legal reading,
    and a default here would certify a judgement nobody made."""
    dataset, _ = built
    approved = dataset.graph(APPROVED_GRAPH)
    records = yaml.safe_load((REPO_ROOT / "eval" / "gold" / "relationships.yaml").read_text())
    blank = {r["id"] for r in records if not r.get("modality")}
    assert blank, "fixture assumption: some approved relationship has no modality"
    for record_id in blank:
        node = next(
            n for n in approved.subjects(TMK.goldRecord, Literal(record_id))
        )
        assert approved.value(node, TMK.modality) is None, (
            f"{record_id} has no modality in the approved record and must have none here"
        )


def test_no_concept_carries_an_invented_definition(built):
    """The approved records hold definition *sources* and no definition text.

    So does the graph. `skos:definition` is absent everywhere, and its absence
    is the honest report (CLAUDE.md rule 1).
    """
    dataset, _ = built
    approved = dataset.graph(APPROVED_GRAPH)
    assert list(approved.objects(None, SKOS.definition)) == []
    assert len(list(approved.subjects(TMK.definitionSource, None))) > 0


def test_every_approved_assertion_names_a_reviewer(built):
    dataset, report = built
    approved = dataset.graph(APPROVED_GRAPH)
    unsigned = [
        str(node)
        for node in approved.subjects(RDF.type, TMK.ApprovedAssertion)
        if approved.value(node, TMK.approvedBy) is None
    ]
    assert unsigned == [], f"unsigned assertions in approved space: {unsigned}"


def test_the_direct_triple_and_the_assertion_agree(built):
    """Both forms are emitted for every relationship. If either could exist
    alone, the approved graph could carry an edge nobody signed."""
    dataset, _ = built
    approved = dataset.graph(APPROVED_GRAPH)
    for assertion in approved.subjects(RDF.type, TMK.ApprovedAssertion):
        predicate = approved.value(assertion, TMK.assertionPredicate)
        if predicate is None:
            continue  # an entity mention carries no triple of its own
        subject = approved.value(assertion, TMK.assertionSubject)
        obj = approved.value(assertion, TMK.assertionObject)
        assert (subject, predicate, obj) in approved


def test_counts_match_the_gold_set(built):
    dataset, report = built
    gold = goldset.load()
    assert report.concepts == gold.count("gold_concept")
    assert report.relationships == gold.count("gold_relationship")
    assert report.mentions == gold.count("gold_entity")
    assert report.prohibited_uses == gold.count("prohibited_use")


def test_nothing_is_stale_and_nothing_dangles(built):
    """Every gold record's recorded hash still matches the pinned snapshot, and
    every source it names is a passage the graph holds. If this fails, the pin
    moved and the records need re-review — never a silent hash refresh."""
    _dataset, report = built
    assert report.stale == []
    assert report.unresolvable_sources == []
    assert report.out_of_scope_sources == []

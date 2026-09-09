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
from tm_knowledge.ontology import build as build_module
from tm_knowledge.ontology import rules
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, SOURCE_GRAPH, TMK
from tm_knowledge.ontology.tbox import MODULES, load as load_tbox
from tm_knowledge.stage0 import goldset

pytestmark = pytest.mark.snapshot


@pytest.fixture(scope="module")
def built():
    return build()


@pytest.fixture(scope="module")
def corpus():
    from tm_knowledge.config import UPSTREAM_DIR
    from tm_knowledge.upstream.loader import load_corpus

    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")
    return load_corpus()


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


# --- the graph is committed, so it has to stay current ----------------------


def test_the_quads_file_is_sorted():
    """rdflib's Turtle serialiser sorts; its N-Quads serialiser emits in
    set-iteration order, which moves with PYTHONHASHSEED. Two builds of an
    identical dataset therefore produced two different 5MB files — invisible
    until `dataset.nq` was committed, at which point every rebuild would have
    put a 5MB diff in the history signifying nothing (Q-45).

    Line order carries no meaning in N-Quads, so sorting is canonicalisation.
    This checks the file on disk is the canonical one."""
    path = build_module.GRAPH_DIR / "dataset.nq"
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines == sorted(lines), "graph/dataset.nq is unsorted — rerun `tmk-graph --write --rules`"


@pytest.mark.rdf
def test_the_committed_graph_matches_a_rebuild():
    """The committed graph is what someone reads instead of building one
    (ADR-0070). If it has drifted, they are reading something the repository no
    longer holds — which is worse than making them build it."""
    dataset, _ = build()
    dataset, _ = rules.apply_rules(dataset)
    stale = build_module.check(dataset)
    assert not stale, (
        "the committed graph differs from a rebuild: "
        + "; ".join(stale)
        + ". Run `tmk-graph --write --rules` and commit."
    )


# --- a boundary is not a gap ------------------------------------------------


def test_a_deliberately_excluded_label_is_a_boundary_and_not_a_gap():
    """CQ-0007 expects "deceptively similar" and no concept carries it, because
    three approved concepts carry it as a *not*-label. Counted as a missing
    concept, it reported a miss on every measurement that used the question. The
    owner ruled it is the boundary the question tests (OQ-0002, ADR-0075)."""
    _dataset, report = build()
    assert "CQ-0007:deceptively similar" in report.boundary_concept_labels
    assert "CQ-0007:deceptively similar" not in report.unmatched_concept_labels


def test_a_label_nothing_excludes_is_still_a_gap():
    """The other half. Three labels remain genuinely unmatched, and softening
    them into boundaries would turn a worklist into a clean bill of health."""
    _dataset, report = build()
    assert report.unmatched_concept_labels, (
        "every unmatched label became a boundary, which means the not-label test "
        "is matching more than it should"
    )


def test_the_boundary_edge_names_the_record_that_drew_it():
    """A boundary asserted with nothing behind it is an agent's opinion. The
    edge points at the approved concepts whose not-labels explain it."""
    dataset, _report = build()
    approved = dataset.graph(APPROVED_GRAPH)
    question = next(approved.subjects(TMK.goldRecord, Literal("CQ-0007")))
    assert (question, TMK.expectsBoundaryLabel, None) in approved
    assert list(approved.objects(question, TMK.testsBoundaryOf)), (
        "the boundary names no concept, so nothing says who drew it"
    )


# --- a role can be what a statement is about --------------------------------


def test_a_relationship_may_be_about_a_role():
    """The owner asked whether a glossary captures the relationship between an
    examiner and a registrar, and said to adopt a Must/May predicate if not
    (OQ-0015). It does not: a glossary holds one entry per term, and "an
    examiner must consult a team leader before accepting on doubt" is a
    normative relation between two roles.

    The Must/May predicate already existed — `tmk:modality` on any approved
    relationship. What was missing was the subject: only concepts and upstream
    refs were terms, so nothing could be *about* a role. This proves an entity
    mention now resolves as one, and that it lands on the same node the mention
    itself is built at — a second node for the same role would make the
    statement and the role invisible to each other.

    No such relationship exists. The point is that one is now expressible, so an
    expert can sign one (ADR-0073)."""
    from tm_knowledge.ontology.build import _term
    from tm_knowledge.ontology.namespaces import assertion_node

    assert _term("GE-0010") == assertion_node("GE-0010")
    assert _term("GC-0001") != _term("GE-0010")


def test_a_role_mention_resolves_to_a_node_the_graph_actually_holds():
    """A term that resolves to a node nothing else builds would be a dangling
    edge that validates."""
    dataset, _report = build()
    approved = dataset.graph(APPROVED_GRAPH)
    roles = [
        record["id"]
        for record in goldset.load()["gold_entity"]
        if record["type"] == "Role"
    ]
    if not roles:
        pytest.skip("no approved Role mentions to check against")
    from tm_knowledge.ontology.build import _term

    node = _term(roles[0])
    assert (node, None, None) in approved, f"{roles[0]} resolves to a node the graph lacks"

# ---------------------------------------------------------------------------
# What the source graph holds — ADR-0097
# ---------------------------------------------------------------------------


@pytest.mark.snapshot
def test_the_source_graph_holds_what_the_records_speak_about(corpus):
    """The rule that replaced the section 43 fence.

    Not "chunks citing a provision" — that was a boundary, and the owner
    withdrew it. Every Manual passage any record cites, plus page-mates, plus
    every chunk carrying an `ambiguous` edge.
    """
    from tm_knowledge.authored import store as authored_store
    from tm_knowledge.ontology.build import source_chunks
    from tm_knowledge.stage0 import goldset

    gold = goldset.load()
    authored = authored_store.load()
    selected = {chunk.chunk_ref for chunk in source_chunks(corpus, gold, authored)}

    # Every Manual ref a record names is in it. This is the property the fence
    # could not have: under ADR-0022 a record naming a Part 22 passage had
    # nothing in the graph to attach to.
    from tm_knowledge.stage0.worksheet import cited_refs

    refs = cited_refs(
        [
            *((record_type, record, None) for record_type, record in gold.all_records()),
            *(
                (entry.record_type, entry.record, entry.envelope)
                for entry in authored.all_entries()
                if entry.sound
            ),
        ]
    )
    for ref in refs:
        if ref in corpus.chunks:
            assert ref in selected, f"{ref} is cited by a record and not in the graph"

    # It reaches well past the old fence, and past Part 29.
    parts = {corpus.chunks[ref].part_id for ref in selected}
    assert len(parts) > 12
    assert {"Part22", "Part26", "Part28", "Part21"} <= parts


@pytest.mark.snapshot
def test_every_ambiguous_edge_reaches_the_graph_however_the_selection_moves(corpus):
    """Q-07, made structural.

    An ambiguous edge is upstream refusing to choose between instruments. It is
    a reason to put a passage in front of a person and never a reason to drop
    one — and under the evidence-driven rule it would have been dropped for not
    being spoken about, which is a distinction the graph could not show anybody.
    """
    from tm_knowledge.authored import store as authored_store
    from tm_knowledge.ontology.build import source_chunks
    from tm_knowledge.stage0 import goldset

    selected = {
        chunk.chunk_ref
        for chunk in source_chunks(corpus, goldset.load(), authored_store.load())
    }
    ambiguous = {
        chunk.chunk_ref
        for chunk in corpus.chunks.values()
        if any(edge.needs_a_human for edge in chunk.provisions)
    }
    assert ambiguous, "the corpus holds ambiguous edges; the fixture is wrong if not"
    assert ambiguous <= selected

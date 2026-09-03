"""Stages 3, 5 and 6 — the vocabulary, the ontology and the knowledge graph.

This package writes into `vocab/`, `ontology/` and `graph/`, which ADR-0007
reserves for approved content. Four properties are what make that legitimate,
and each is a test here rather than a paragraph in a README.

1. **Nothing unapproved gets in.** Every node the build emits carries the name
   and date of the person who signed the record it came from, and the build
   refuses outright if pointed at a gold set that does not.
2. **Nothing is invented.** The classes that would require a legal judgement to
   populate — `GroundOfRefusal`, `LegalTest`, `RelevantFactor`, `Exception` —
   are declared and provably empty. A test that they stay empty is the only
   thing standing between "the ontology has slots for this" and an agent
   quietly filling them (CLAUDE.md rule 1).
3. **The output is stable.** `graph/` is committed, so two builds over the same
   input must be byte-identical or the diff stops being a paper trail.
4. **It parses.** Emitting Turtle by hand is the trade made in ADR-0058, and the
   thing that can go wrong with it is a file that looks right and will not load.

The rdflib-dependent tests skip cleanly without the `[graph]` extra, in the same
way the snapshot tests skip without a fetch.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from tm_knowledge.graph import build as build_module
from tm_knowledge.graph import ontology, queries, shapes
from tm_knowledge.graph.cli import unapproved, write_all
from tm_knowledge.graph.model import concept_iri, ref_iri, tmk
from tm_knowledge.graph.turtle import Document, IRI, Literal, PN, Triples, escape
from tm_knowledge.refs import from_iri
from tm_knowledge.stage0 import goldset

rdflib = pytest.importorskip("rdflib", reason="needs the [graph] extra")


def _parse(text: str):
    graph = rdflib.Graph()
    graph.parse(data=text, format="turtle")
    return graph


@pytest.fixture(scope="module")
def gold():
    loaded = goldset.load()
    if not loaded.total:
        pytest.skip("eval/gold/ is empty")
    return loaded


@pytest.fixture(scope="module")
def built(gold):
    return build_module.build(gold)


# ---------------------------------------------------------------------------
# The writer
# ---------------------------------------------------------------------------


def test_a_backslash_is_escaped_before_everything_else():
    """Escape the escape first, or every later escape gets escaped again."""
    assert escape('a\\b"c') == 'a\\\\b\\"c'
    assert escape("line\nbreak") == "line\\nbreak"


def test_the_writer_refuses_an_unsafe_prefixed_name():
    """Turtle's PN_LOCAL has no `/`, and every ref in this corpus is full of them."""
    with pytest.raises(ValueError):
        tmk("has/slash")


def test_a_ref_is_written_as_a_full_iri_and_still_parses():
    triples = Triples()
    triples.add(ref_iri("TMM/Part29/1#1"), PN("a"), tmk("ManualPassage"))
    text = Document(("t",), {"tmk": "http://example.org/ns/"}, triples).render()
    assert len(_parse(text)) == 1


def test_the_same_triple_twice_is_one_triple():
    triples = Triples()
    triples.add(IRI("http://x/a"), PN("skos:altLabel"), Literal("one"))
    triples.add(IRI("http://x/a"), PN("skos:altLabel"), Literal("one"))
    assert len(triples) == 1


def test_the_written_count_is_the_parsed_count(built):
    """A count nothing else agrees with is worse than no count."""
    for stem, document in built.documents.items():
        assert len(_parse(document.render())) == built.counts[stem], stem


def test_the_output_is_byte_identical_on_a_rebuild(gold):
    first = build_module.build(gold)
    second = build_module.build(gold)
    for stem in first.documents:
        assert first.documents[stem].render() == second.documents[stem].render()


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------


def test_every_ref_iri_round_trips(built):
    """`to_iri` escaping `#` is only safe if `from_iri` gets the ref back."""
    graph = _parse(built.documents["graph/s43-provenance"].render())
    checked = 0
    for subject, _, obj in graph:
        for term in (subject, obj):
            value = str(term)
            if "/ref/" in value:
                assert from_iri(value)
                checked += 1
    assert checked


def test_a_concept_iri_carries_the_gold_id(built):
    assert str(concept_iri("GC-0001")).endswith("/concept/GC-0001>")


# ---------------------------------------------------------------------------
# Nothing unapproved, nothing invented
# ---------------------------------------------------------------------------


def test_every_emitted_node_carries_an_approver(built):
    """ADR-0039: a record with no name against it is not approved knowledge."""
    for stem in ("graph/s43-provenance", "graph/s43-mentions", "graph/s43-bounds"):
        graph = _parse(built.documents[stem].render())
        approved = {s for s, p, _ in graph if str(p).endswith("/ns/approvedBy")}
        typed = {
            s
            for s, p, o in graph
            if str(p).endswith("22-rdf-syntax-ns#type")
            and str(o).endswith(("/Assertion", "/Mention", "/Bound", "/Question"))
        }
        assert typed and typed <= approved, stem


def test_the_build_refuses_a_gold_set_that_is_not_approved(tmp_path):
    (tmp_path / "concepts.yaml").write_text(
        yaml.safe_dump(
            [
                {
                    "id": "GC-9001",
                    "pref_label": "unsigned",
                    "alt_labels": [],
                    "not_labels": [],
                    "definition_sources": [],
                    "approved_by": None,
                    "approved_date": None,
                }
            ]
        ),
        encoding="utf-8",
    )
    assert unapproved(goldset.load(tmp_path)) == ["GC-9001"]


def test_the_classes_that_need_a_judgement_stay_empty(built):
    """The one test standing between an empty slot and an agent filling it."""
    assert set(built.unpopulated) == {
        "GroundOfRefusal",
        "LegalTest",
        "RelevantFactor",
        "Exception",
    }
    for stem, document in built.documents.items():
        graph = _parse(document.render())
        for _, predicate, obj in graph:
            if str(predicate).endswith("22-rdf-syntax-ns#type"):
                assert not str(obj).endswith(
                    ("/GroundOfRefusal", "/LegalTest", "/RelevantFactor", "/Exception")
                ), stem


def test_a_mention_nobody_resolved_carries_no_resolution(built, gold):
    """Absent means nobody linked it, never that it links to nothing."""
    graph = _parse(built.documents["graph/s43-mentions"].render())
    resolved = {
        str(s) for s, p, _ in graph if str(p).endswith("/ns/resolvesTo")
    }
    expected = {
        build_module.assertion_iri(str(record["id"])).value
        for record in gold["gold_entity"]
        if record.get("resolves_to")
    }
    assert resolved == expected


# ---------------------------------------------------------------------------
# The ontology
# ---------------------------------------------------------------------------


def test_every_ontology_module_parses():
    for module in ontology.MODULES:
        assert len(_parse(ontology.render(module)))


def test_law_and_practice_are_disjoint():
    """CLAUDE.md rule 5, as an axiom. The load-bearing one.

    Asserted in both directions on purpose: `owl:disjointWith` is symmetric in
    meaning but not in serialisation, and a reader — or a tool that does no
    reasoning at all — should find it from whichever class it started at.
    """
    graph = _parse(ontology.render("authority"))
    pairs = {
        (str(s).rsplit("/", 1)[-1], str(o).rsplit("/", 1)[-1])
        for s, p, o in graph
        if str(p).endswith("owl#disjointWith")
    }
    assert ("LegislativeProvision", "ManualInstruction") in pairs
    assert ("ManualInstruction", "LegislativeProvision") in pairs


def test_no_relation_property_declares_a_domain_or_a_range():
    """In RDFS those infer rather than check, which would invent claims (ADR-0060)."""
    graph = _parse(ontology.render("relations"))
    for _, predicate, _ in graph:
        assert not str(predicate).endswith(("rdf-schema#domain", "rdf-schema#range"))


def test_every_approved_predicate_has_an_ontology_term(gold):
    declared = {name for name, _ in ontology.PREDICATES}
    used = {str(record["predicate"]) for record in gold["gold_relationship"]}
    assert used <= declared, sorted(used - declared)


def test_the_shapes_parse_and_target_the_approval_fields():
    graph = _parse(shapes.render())
    paths = {str(o) for s, p, o in graph if str(p).endswith("shacl#path")}
    assert any(path.endswith("/ns/approvedBy") for path in paths)
    assert any(path.endswith("/ns/sourceContentHash") for path in paths)


# ---------------------------------------------------------------------------
# Cross-references
# ---------------------------------------------------------------------------


def test_no_concept_points_at_a_concept_that_is_not_there(built):
    graph = _parse(built.documents["vocab/s43-concepts"].render())
    defined = {
        str(s) for s, p, o in graph if str(o).endswith("skos/core#Concept")
    }
    for subject, predicate, obj in graph:
        if str(predicate).endswith(("core#broader", "core#narrower", "core#related")):
            assert str(obj) in defined, f"{subject} -> {obj}"


def test_every_bound_points_at_a_question_that_exists(built):
    graph = _parse(built.documents["graph/s43-bounds"].render())
    questions = {
        str(s) for s, p, o in graph if str(o).endswith("/ns/Question")
    }
    for _, predicate, obj in graph:
        if str(predicate).endswith("/ns/boundsQuestion"):
            assert str(obj) in questions, obj


# ---------------------------------------------------------------------------
# What the build noticed
# ---------------------------------------------------------------------------


def test_the_opposed_pair_in_the_approved_set_is_reported(built):
    """Two signed records saying opposite things. Reported, never resolved."""
    pairs = {(first, second) for first, second, _ in built.conflicts}
    assert ("GR-0008", "GR-0056") in pairs


def test_a_conflict_is_reported_and_not_repaired(built):
    """Both statements are still in the graph. Dropping one would overrule a reviewer."""
    graph = _parse(built.documents["graph/s43-assertions"].render())
    predicates = {
        str(p)
        for s, p, o in graph
        if str(s).endswith("/concept/GC-0001") and str(o).endswith("/concept/GC-0050")
    }
    assert any(p.endswith("/requiresElement") for p in predicates)
    assert any(p.endswith("/excludesBasis") for p in predicates)


# ---------------------------------------------------------------------------
# The demonstration queries
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def dataset(tmp_path_factory, gold):
    root = tmp_path_factory.mktemp("graph")
    write_all(root)
    graph = rdflib.Graph()
    for path in sorted(root.rglob("*.ttl")):
        graph.parse(path, format="turtle")
    return graph


@pytest.mark.parametrize("query", queries.QUERIES, ids=lambda q: q.name)
def test_every_demonstration_query_runs_and_answers(dataset, query):
    """A demonstration query that returns nothing demonstrates nothing."""
    rows = list(dataset.query(queries.render(query)))
    assert rows, query.name


def test_the_expansion_guard_keeps_connotation_apart_from_section_44(dataset):
    """The query that pays for the vocabulary.

    `connotation` must expand to its own synonyms and must **not** reach
    `deceptively similar`, which is section 44's language. The two lists have to
    be disjoint or the guard is decoration: a term that is both a synonym and a
    non-synonym expands anyway.
    """
    query = next(q for q in queries.QUERIES if q.name == "expansion-guard")
    rows = {
        str(row[1]): (str(row[2]), str(row[3]))
        for row in dataset.query(queries.render(query))
    }
    expand, never = rows["connotation"]
    assert "deceptively similar" in never
    assert "deceptively similar" not in expand
    assert "secondary meaning" in expand
    assert not (set(expand.split(" | ")) & set(never.split(" | ")))


def test_the_misdirected_query_finds_where_the_corpus_sends_it(dataset):
    """GS-0003's correct answer, which term frequency ranks 107th of 216."""
    query = next(q for q in queries.QUERIES if q.name == "sent-elsewhere")
    rows = [tuple(str(value) for value in row) for row in dataset.query(queries.render(query))]
    assert rows
    assert any("TMM/Part29/2/2/3" in row[2] and "TMA1995/s44" in row[3] for row in rows)


def test_the_bounds_reach_the_questions_they_guard(dataset):
    query = next(q for q in queries.QUERIES if q.name == "bounds-on-an-answer")
    rows = list(dataset.query(queries.render(query)))
    assert len({str(row[0]) for row in rows}) > 1


def test_written_files_land_where_the_architecture_says(tmp_path, gold):
    written = write_all(tmp_path)
    assert any(path.startswith("vocab/") for path in written)
    assert any(path.startswith("ontology/") for path in written)
    assert any(path.startswith("graph/") for path in written)
    assert any(path.startswith("shapes/") for path in written)
    assert any(path.startswith("queries/") for path in written)

"""Every competency query parses, runs, names a real question, and says what it
does not answer.

The standard is `queries/README.md`'s: *if a question has no query and no query
has a question, one of the two is wrong.* These tests hold both directions, and
one more that matters as much — the `limits:` line. A query that returns rows
always looks like an answer, and the limits line is the only place a query says
what it has not established.
"""

from __future__ import annotations

import pytest

from tm_knowledge.ontology import ask
from tm_knowledge.ontology.build import build
from tm_knowledge.stage0 import goldset

pytestmark = pytest.mark.snapshot

QUERIES = ask.load_queries()


@pytest.fixture(scope="module")
def dataset():
    built, _ = build()
    return built


def test_there_are_queries():
    assert QUERIES, "queries/competency/ is empty"


@pytest.mark.parametrize("query", QUERIES, ids=lambda q: q.question_id)
def test_query_names_an_approved_question(query):
    """A query measuring a question nobody approved is measuring nothing."""
    known = {record["id"] for record in goldset.load()["competency_question"]}
    assert query.question_id in known


@pytest.mark.parametrize("query", QUERIES, ids=lambda q: q.question_id)
def test_query_declares_its_limits(query):
    """Not a formality. `limits` is where the query says what it has not
    established, and a one-word limits line is a query pretending it has none."""
    assert len(query.limits) > 60, f"{query.question_id}: limits line is too thin to mean anything"
    assert query.answers


@pytest.mark.parametrize("query", QUERIES, ids=lambda q: q.question_id)
def test_query_runs(dataset, query):
    """It must execute. A query that raises is a broken measurement that would
    otherwise be discovered as an empty section of a report."""
    list(query.run(dataset))


@pytest.mark.parametrize("query", QUERIES, ids=lambda q: q.question_id)
def test_query_names_the_graph_it_means(query):
    """`queries/README.md`: a query that accidentally spans candidates and
    approved produces confident nonsense. Every query names its graph."""
    assert "GRAPH tmkg:" in query.text


@pytest.mark.parametrize(
    "question_id",
    ["CQ-0017", "CQ-0020", "CQ-0021", "CQ-0022", "CQ-0024", "CQ-0012"],
    ids=str,
)
def test_the_answering_queries_answer(dataset, question_id):
    """The queries whose emptiness would be a regression rather than a fact.

    CQ-0023 is deliberately excluded: its most important row is a blank one.
    """
    query = next(q for q in QUERIES if q.question_id == question_id)
    assert list(query.run(dataset)), f"{question_id} returned nothing"


def test_cq_0017_counts_the_citing_passages_the_graph_holds(dataset):
    """The graph must not lose or duplicate a citation edge on the way in.

    **The assertion changed at ADR-0097 and the reason is the point of the
    test.** It used to check equality with `tmk-recon`'s 67 — recon counts
    chunks off the loader, this counts citation nodes in the graph — and that
    worked because the source graph was fenced to the chunks citing section 43,
    so the two populations were the same set by construction. The fence is gone.
    The graph now holds what the repository has said something about, which for
    section 43 is a *subset* of the citing chunks: 56 of the 67.

    So equality would now be asserting that the graph is fenced, which is what
    was removed. What is still worth pinning is the property the test was really
    for: every citing chunk the graph holds is counted exactly once, and none is
    counted that the corpus does not have. Both halves are checked against the
    loader rather than against a number written down here.
    """
    from tm_knowledge.stage0.worksheet import ScopeRule
    from tm_knowledge.upstream.loader import load_corpus

    corpus = load_corpus()
    rule = ScopeRule()
    citing = {
        chunk.chunk_ref
        for chunk in corpus.chunks.values()
        if any(rule.matches(edge.id) for edge in chunk.provisions)
    }
    assert len(citing) == 67, "recon §1: 67 chunks in the corpus cite the provision"

    query = next(q for q in QUERIES if q.question_id == "CQ-0017")
    rows = {str(row[0]): int(row[1]) for row in query.run(dataset)}
    held = sum(rows.values())

    # A subset, never a superset: a count above the corpus figure means an edge
    # was duplicated on the way into the graph.
    assert 0 < held <= len(citing)

    # And the per-Part split is the corpus's own, restricted to what is held —
    # computed here rather than transcribed, so it cannot drift.
    from tm_knowledge.ontology.build import source_chunks
    from tm_knowledge.stage0 import goldset
    from tm_knowledge.authored import store as authored_store

    selected = {c.chunk_ref for c in source_chunks(corpus, goldset.load(), authored_store.load())}
    expected: dict[str, int] = {}
    for ref in citing & selected:
        part = corpus.chunks[ref].part_id
        expected[part] = expected.get(part, 0) + 1
    assert rows == expected


def test_cq_0012_returns_prohibitions_and_nothing_else(dataset):
    """The question is an evaluative judgement for the decision maker. The
    system's answer is the list of outputs that would answer it and must not be
    produced — so the rows must all be prohibitions."""
    query = next(q for q in QUERIES if q.question_id == "CQ-0012")
    rows = list(query.run(dataset))
    assert {str(row[0]) for row in rows} == {"PU-0001", "PU-0002", "PU-0003"}
    assert all(str(row[1]) == "evaluative_conclusion" for row in rows)


def test_cq_0024_reports_the_missing_modalities_as_missing(dataset):
    """Five approved relationships have no modality and the answer says so in
    those words. A default here would certify a legal reading nobody made."""
    query = next(q for q in QUERIES if q.question_id == "CQ-0024")
    rows = {str(row[0]): int(row[1]) for row in query.run(dataset)}
    blank = [key for key in rows if "not supplied" in key]
    assert len(blank) == 1 and rows[blank[0]] == 5


def test_coverage_separates_unqueried_from_undeliverable(dataset):
    """A search or retrieval question is not a SPARQL result. Counting them as
    coverage gaps would report a shortfall against work that is deliberately
    five stages away."""
    coverage = ask.coverage(dataset, QUERIES)
    assert coverage["unknown"] == []
    assert coverage["deferred"], "the search and retrieval questions must be named as deferred"
    assert all("Stage" in item for item in coverage["deferred"])

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


def test_cq_0017_reproduces_the_recon_part_distribution(dataset):
    """The graph must agree with `tmk-recon` on a number both compute.

    Two independent paths to the same figure — recon counts chunks off the
    loader, this counts citation nodes in the graph. If they disagree, the graph
    lost or duplicated an edge on the way in.
    """
    query = next(q for q in QUERIES if q.question_id == "CQ-0017")
    rows = {str(row[0]): int(row[1]) for row in query.run(dataset)}
    assert rows["Part29"] == 33
    assert rows["Part32A"] == 10
    assert rows["Part20"] == 5 and rows["Part22"] == 5
    assert sum(rows.values()) == 67, "recon §1: 67 chunks cite the provision"


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

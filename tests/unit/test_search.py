"""The measurement scores what it says it scores, and the systems differ only where they should.

- nDCG and recall are the textbook definitions, pinned on hand-worked cases.
- The bootstrap is paired, deterministic, and says "not established" when the
  differences straddle zero.
- **The ontology system is the hybrid system whenever it recognises nothing** —
  so any difference measured comes from the ontology, not from the plumbing.
- Vectors round-trip through the float16 store without losing their ranking.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

np = pytest.importorskip("numpy")

from tm_knowledge.bulk import links as links_module  # noqa: E402
from tm_knowledge.search import measure  # noqa: E402
from tm_knowledge.search import vectors  # noqa: E402
from tm_knowledge.search.index import Hit, Systems  # noqa: E402


def test_ndcg_is_one_for_the_ideal_order_and_less_otherwise():
    grades = {"a": 3, "b": 2, "c": 0}
    assert measure.ndcg(["a", "b", "c"], grades) == pytest.approx(1.0)
    worse = measure.ndcg(["c", "b", "a"], grades)
    expected = (0 / math.log2(2) + 2 / math.log2(3) + 3 / math.log2(4)) / (3 / math.log2(2) + 2 / math.log2(3))
    assert worse == pytest.approx(expected)
    assert measure.ndcg(["x"], {"x": 0}) == 0.0


def test_recall_counts_grades_two_and_three_and_skips_questions_with_none():
    grades = {"a": 3, "b": 2, "c": 1, "d": 0}
    assert measure.recall(["a", "c"], grades) == pytest.approx(0.5)
    assert measure.recall(["a"], {"a": 1}) is None


def test_the_bootstrap_is_deterministic_and_honest_about_zero():
    mean, low, high = measure.bootstrap([0.1, -0.1, 0.05, -0.05] * 10)
    assert low < 0 < high and mean == pytest.approx(0.0)
    assert measure.bootstrap([0.2] * 30) == (pytest.approx(0.2), pytest.approx(0.2), pytest.approx(0.2))
    assert measure.bootstrap([0.3, 0.1, 0.2]) == measure.bootstrap([0.3, 0.1, 0.2])


class _Index:
    corpus = SimpleNamespace(chunks={})

    def search(self, query, k):
        return [Hit("TMM/Part1/1#1", 2.0), Hit("TMM/Part1/2#1", 1.0)][:k]


def _systems(concepts):
    links = links_module.Links(concepts=concepts, mentions={c: [("TMM/Part9/9#9", 0, 4, "x")] for c in concepts},
                               passages=10)
    return Systems(index=_Index(), links=links)


def test_the_ontology_system_is_the_hybrid_when_it_recognises_nothing():
    systems = _systems({"GC-0001": links_module.Concept("GC-0001", "opposition", ("opposition",), "signed")})
    hits, trace = systems.ontology("What is a trade mark?", 5)
    assert trace.recognised == []
    assert [h.ref for h in hits] == [h.ref for h in systems.hybrid("What is a trade mark?", 5)]


def test_a_recognised_concept_brings_its_linked_passages_in():
    systems = _systems({"GC-0001": links_module.Concept("GC-0001", "opposition", ("opposition",), "signed")})
    hits, trace = systems.ontology("How does an opposition start?", 5)
    assert trace.recognised == ["GC-0001"]
    assert "TMM/Part9/9#9" in [h.ref for h in hits]
    assert "linked" in next(h.why for h in hits if h.ref == "TMM/Part9/9#9")


def test_vectors_round_trip_through_the_float16_store(tmp_path):
    store = vectors.Store("t", root=tmp_path)
    rng = np.random.default_rng(1)
    matrix = rng.normal(size=(5, vectors.DIMENSIONS)).astype(np.float32)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    store.keys, store.hashes, store.matrix = list("abcde"), ["h"] * 5, matrix
    store.save()
    again = vectors.Store("t", root=tmp_path)
    assert again.keys == list("abcde")
    query = matrix[2]
    assert int(np.argmax(again.matrix @ query)) == 2

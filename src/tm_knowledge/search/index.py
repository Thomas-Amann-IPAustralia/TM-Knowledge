"""Three search systems over the Manual's passages, fixed before measurement.

- **keyword** — BM25 over the passage text and its heading path (SQLite FTS5).
- **hybrid** — keyword fused with vector similarity. The fair baseline: good
  search with no ontology in it.
- **ontology** — hybrid, plus what the ontology knows about the question:
  1. *recognise* — concepts whose label or everyday phrase appears in it;
  2. *expand* — those concepts' labels, and their neighbours' preferred labels,
     added to the keyword query;
  3. *link* — passages that name a recognised concept (weight 2) or a neighbour
     (weight 1), or that cite a recognised concept's legislative basis (weight 1),
     ordered within a weight by vector similarity.

Every ranking is fused by reciprocal rank with equal weights. **Nothing here was
tuned on the benchmark**: the design was fixed before a passage was judged, so the
comparison measures the design, not a fit to the test (KB SOP §7.2). When the
ontology recognises nothing, `ontology` returns exactly what `hybrid` does.
"""

from __future__ import annotations

import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable

from tm_knowledge.bulk import links as links_module
from tm_knowledge.upstream.loader import Corpus

#: Words that carry no retrieval signal in a question. Short on purpose: BM25
#: already discounts common words, and a long list starts deleting legal terms.
STOPWORDS = frozenset(
    "a an and are as at be by can could do does for from has have how i if in is it its "
    "my of on or our should so that the their them then there these they this to was we "
    "what when where which who why will with would you your".split()
)

#: Reciprocal-rank-fusion constant (the usual 60). Depth of each fused ranking.
RRF_K = 60
DEPTH = 50


def _terms(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9]+", text.lower()) if len(t) > 1 and t not in STOPWORDS]


def _match_expression(terms: Iterable[str]) -> str:
    return " OR ".join(f'"{t}"' for t in dict.fromkeys(terms))


@dataclass
class Hit:
    ref: str
    score: float
    why: tuple[str, ...] = ()


@dataclass
class Trace:
    """What the ontology did for one question — shown on the "Ask the Manual" page."""

    recognised: list[str] = field(default_factory=list)
    neighbours: list[str] = field(default_factory=list)
    provisions: list[str] = field(default_factory=list)
    #: (subject, predicate, object, record id, origin) for every edge followed
    paths: list[tuple[str, str, str, str, str]] = field(default_factory=list)


class KeywordIndex:
    """BM25 over every Manual passage, its heading path and its text."""

    def __init__(self, corpus: Corpus) -> None:
        self.corpus = corpus
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE VIRTUAL TABLE passages USING fts5(ref UNINDEXED, heading, body)")
        self.db.executemany("INSERT INTO passages VALUES (?, ?, ?)", [
            (c.chunk_ref, " > ".join(c.heading_path), c.text)
            for c in sorted(corpus.chunks.values(), key=lambda c: (c.page_ref, c.ordinal))
        ])

    def search(self, query: str, k: int = 10) -> list[Hit]:
        expression = _match_expression(_terms(query))
        if not expression:
            return []
        rows = self.db.execute(
            "SELECT ref, bm25(passages, 0.5, 1.0) AS s FROM passages WHERE passages MATCH ? ORDER BY s LIMIT ?",
            (expression, k),
        ).fetchall()
        return [Hit(ref=ref, score=-score, why=("keyword",)) for ref, score in rows]


def _fuse(rankings: list[tuple[str, list[str]]], k: int) -> list[Hit]:
    fused: dict[str, float] = defaultdict(float)
    why: dict[str, list[str]] = defaultdict(list)
    for name, refs in rankings:
        for rank, ref in enumerate(refs):
            fused[ref] += 1.0 / (RRF_K + rank + 1)
            why[ref].append(name)
    ordered = sorted(fused.items(), key=lambda x: (-x[1], x[0]))[:k]
    return [Hit(ref, score, tuple(why[ref])) for ref, score in ordered]


@dataclass
class Systems:
    """The three systems, sharing one index, one vector store and one ontology."""

    index: KeywordIndex
    links: links_module.Links
    dense: Any = None  # search.vectors.Dense, optional
    aliases: dict[str, list[str]] = field(default_factory=dict)
    #: (subject, predicate, object, record id, origin), concept to concept, both stores
    relations: list[tuple[str, str, str, str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        extra = {cid: tuple(phrases) for cid, phrases in self.aliases.items()}
        self._patterns = links_module._patterns({
            cid: links_module.Concept(id=c.id, pref_label=c.pref_label,
                                      labels=c.labels + extra.get(cid, ()), origin=c.origin)
            for cid, c in self.links.concepts.items()
        })
        self._edges: dict[str, list[tuple[str, str, str, str, str]]] = defaultdict(list)
        for edge in self.relations:
            self._edges[edge[0]].append(edge)
            self._edges[edge[2]].append(edge)

    # -- the parts -----------------------------------------------------------

    def recognise(self, question: str) -> list[str]:
        found = links_module.find_mentions(question, self._patterns)
        return sorted(found, key=lambda cid: found[cid][0])

    def _dense(self, question: str) -> list[tuple[str, float]]:
        return self.dense.search(question, DEPTH) if self.dense is not None else []

    def trace(self, question: str) -> Trace:
        recognised = self.recognise(question)
        specific = [c for c in recognised if c not in self.links.generic]
        paths = [e for c in specific for e in self._edges.get(c, ())]
        neighbours = sorted({e[2] if e[0] in specific else e[0] for e in paths} - set(specific))
        provisions = sorted({r for c in specific for r in self.links.concepts[c].legislative_basis})
        return Trace(recognised, neighbours, provisions, sorted(set(paths)))

    # -- the systems -----------------------------------------------------------

    def keyword(self, question: str, k: int = 10) -> list[Hit]:
        return self.index.search(question, k)

    def hybrid(self, question: str, k: int = 10) -> list[Hit]:
        rankings = [("keyword", [h.ref for h in self.index.search(question, DEPTH)])]
        dense = self._dense(question)
        if dense:
            rankings.append(("vector", [ref for ref, _ in dense]))
        return _fuse(rankings, k)

    def ontology(self, question: str, k: int = 10) -> tuple[list[Hit], Trace]:
        trace = self.trace(question)
        specific = [c for c in trace.recognised if c not in self.links.generic]
        rankings = [("keyword", [h.ref for h in self.index.search(question, DEPTH)])]
        dense = self._dense(question)
        if dense:
            rankings.append(("vector", [ref for ref, _ in dense]))
        if not specific:
            return _fuse(rankings, k), trace

        expansion = [label for c in specific for label in self.links.concepts[c].labels]
        expansion += [self.links.concepts[n].pref_label for n in trace.neighbours]
        rankings.append(("expanded", [h.ref for h in self.index.search(question + " " + " ".join(expansion), DEPTH)]))

        weight: dict[str, float] = defaultdict(float)
        for c in specific:
            for ref, *_ in self.links.mentions.get(c, ()):
                weight[ref] += 2
        for n in trace.neighbours:
            for ref, *_ in self.links.mentions.get(n, ()):
                weight[ref] += 1
        for ref in trace.provisions:
            for chunk in self.index.corpus.chunks_citing(ref):
                weight[chunk.chunk_ref] += 1
        similarity = dict(self.dense.search(question, len(self.index.corpus.chunks))) if dense else {}
        linked = sorted(weight, key=lambda r: (-weight[r], -similarity.get(r, 0.0), r))[:DEPTH]
        rankings.append(("linked", linked))
        return _fuse(rankings, k), trace


def relations_from(gold: Any, authored: Any) -> list[tuple[str, str, str, str, str]]:
    """Concept-to-concept relationships from both stores, with their origin kept."""
    out = []
    for origin, records in (("approved", gold["gold_relationship"]), ("authored", authored["gold_relationship"])):
        for r in records:
            s, o = str(r["subject"]), str(r["object"])
            if s.startswith("GC-") and o.startswith("GC-"):
                out.append((s, str(r["predicate"]), o, str(r["id"]), origin))
    return out

"""Keyword search and ontology-expanded search over the Manual's passages."""

from __future__ import annotations

import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from tm_knowledge.bulk import links as links_module
from tm_knowledge.upstream.loader import Corpus

#: Words that carry no retrieval signal in a question. Short on purpose: BM25
#: already discounts common words, and a long list starts deleting legal terms.
STOPWORDS = frozenset(
    "a an and are as at be by can could do does for from has have how i if in is it its "
    "my of on or our should so that the their them then there these they this to was we "
    "what when where which who why will with would you your".split()
)

#: Reciprocal-rank-fusion constant (the usual 60).
RRF_K = 60


def _terms(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9]+", text.lower()) if len(t) > 1 and t not in STOPWORDS]


def _match_expression(terms: Iterable[str]) -> str:
    unique = list(dict.fromkeys(terms))
    return " OR ".join(f'"{t}"' for t in unique)


@dataclass
class Hit:
    ref: str
    score: float
    why: tuple[str, ...] = ()


class KeywordIndex:
    """BM25 over every Manual passage, its heading path and its text."""

    def __init__(self, corpus: Corpus) -> None:
        self.corpus = corpus
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE VIRTUAL TABLE passages USING fts5(ref UNINDEXED, heading, body)")
        rows = [
            (c.chunk_ref, " > ".join(c.heading_path), c.text)
            for c in sorted(corpus.chunks.values(), key=lambda c: (c.page_ref, c.ordinal))
        ]
        self.db.executemany("INSERT INTO passages VALUES (?, ?, ?)", rows)

    def search(self, query: str, k: int = 10) -> list[Hit]:
        expression = _match_expression(_terms(query))
        if not expression:
            return []
        rows = self.db.execute(
            "SELECT ref, bm25(passages, 0.5, 1.0) AS s FROM passages WHERE passages MATCH ? "
            "ORDER BY s LIMIT ?",
            (expression, k),
        ).fetchall()
        return [Hit(ref=ref, score=-score, why=("keyword",)) for ref, score in rows]


@dataclass
class OntologySearch:
    """Keyword search, plus what the ontology joins the question's concepts to."""

    index: KeywordIndex
    links: links_module.Links
    #: concept id -> everyday phrases (the aliases job's output); optional
    aliases: dict[str, list[str]] = field(default_factory=dict)
    #: concept id -> neighbour concept ids, from relationships in both stores
    neighbours: dict[str, set[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        extra = {cid: tuple(phrases) for cid, phrases in self.aliases.items()}
        concepts = {
            cid: links_module.Concept(
                id=c.id, pref_label=c.pref_label, labels=c.labels + extra.get(cid, ()),
                origin=c.origin,
            )
            for cid, c in self.links.concepts.items()
        }
        self._patterns = links_module._patterns(concepts)

    def recognise(self, question: str) -> list[str]:
        """Concepts whose label or everyday phrase appears in the question."""
        found = links_module.find_mentions(question, self._patterns)
        return sorted(found, key=lambda cid: found[cid][0])

    def search(self, question: str, k: int = 10) -> tuple[list[Hit], list[str]]:
        recognised = self.recognise(question)
        specific = [cid for cid in recognised if cid not in self.links.generic]
        hop = sorted({n for cid in specific for n in self.neighbours.get(cid, ())} - set(specific))
        expansion = [label for cid in specific + hop for label in self.links.concepts[cid].labels]

        rankings: list[tuple[str, list[str]]] = [
            ("keyword", [h.ref for h in self.index.search(question, 50)]),
        ]
        if expansion:
            rankings.append(("expanded", [h.ref for h in self.index.search(
                question + " " + " ".join(expansion), 50)]))
        linked: dict[str, int] = defaultdict(int)
        for cid in specific:
            for ref, *_ in self.links.mentions.get(cid, ()):
                linked[ref] += 2
        for cid in hop:
            for ref, *_ in self.links.mentions.get(cid, ()):
                linked[ref] += 1
        if linked:
            rankings.append(("linked", [r for r, _ in sorted(linked.items(), key=lambda x: (-x[1], x[0]))][:50]))

        fused: dict[str, float] = defaultdict(float)
        why: dict[str, list[str]] = defaultdict(list)
        for name, refs in rankings:
            for rank, ref in enumerate(refs):
                fused[ref] += 1.0 / (RRF_K + rank + 1)
                why[ref].append(name)
        ordered = sorted(fused.items(), key=lambda x: (-x[1], x[0]))[:k]
        return [Hit(ref, score, tuple(why[ref])) for ref, score in ordered], recognised

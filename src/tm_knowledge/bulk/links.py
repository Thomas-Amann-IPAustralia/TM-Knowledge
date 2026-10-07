"""Which passages name which concept, and which concept pairs to ask about.

The free half of the pipeline (CLAUDE.md rule 7). A concept is linked to a Manual
passage when one of its labels appears in the passage's text as a whole word.
That is a fact about strings, not a reading of the law, so it needs no review —
and it is what ontology-enhanced search expands through.

Two rules from the KB SOP shape it:

- **A label in a fifth of the corpus is a generic word, not a signal** (its
  D-020). "trade mark" names 44% of passages; pairing it with everything would
  send the model hundreds of pairs whose answer is "yes, obviously". Generic
  concepts keep their links and are left out of pairing.
- **Never send what already has a record** (ADR-0088 c2). A pair already joined
  by a signed or authored relationship, or by a concept's own broader/narrower/
  related fields, is not a candidate.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from tm_knowledge.authored import store as authored_store
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import goldset
from tm_knowledge.upstream.loader import Corpus

LINKS_DIR = REPO_ROOT / "data" / "derived" / "links"
MENTIONS_PATH = LINKS_DIR / "mentions.json"
PAIRS_PATH = LINKS_DIR / "pairs.json"

#: A concept named in more than this share of passages is generic (KB SOP D-020).
GENERIC_SHARE = 0.20
#: Labels shorter than this match inside too many unrelated words to be useful.
MIN_LABEL_CHARS = 4
#: Partners kept per concept when pairing, before balancing into batches.
PARTNERS_PER_CONCEPT = 6
#: Neighbours sent with one anchor in one model call.
NEIGHBOURS_PER_ANCHOR = 8


@dataclass(frozen=True)
class Concept:
    """A concept from either store, as far as matching and pairing need it."""

    id: str
    pref_label: str
    labels: tuple[str, ...]
    origin: str  # "signed" | "authored" — never merged (ADR-0080 c3)
    legislative_basis: tuple[str, ...] = ()
    group: str | None = None
    quote: str | None = None


@dataclass(frozen=True)
class Pair:
    """Two concepts worth asking about, and the passages that put them together."""

    a: str
    b: str
    score: float
    shared: tuple[str, ...]  # passage refs, closest co-mention first
    signals: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "a": self.a, "b": self.b, "score": round(self.score, 4),
            "shared": list(self.shared), "signals": list(self.signals),
        }


@dataclass
class Links:
    """Mentions per concept, and the generic concepts left out of pairing."""

    concepts: dict[str, Concept]
    #: concept id -> [(passage ref, start, end, label)], reading order
    mentions: dict[str, list[tuple[str, int, int, str]]]
    passages: int
    generic: frozenset[str] = field(default_factory=frozenset)

    def by_passage(self) -> dict[str, dict[str, tuple[int, int, str]]]:
        index: dict[str, dict[str, tuple[int, int, str]]] = defaultdict(dict)
        for concept, hits in self.mentions.items():
            for ref, start, end, label in hits:
                index[ref][concept] = (start, end, label)
        return index


def concepts(
    gold: goldset.GoldSet | None = None, authored: authored_store.AuthoredSet | None = None
) -> dict[str, Concept]:
    """Every concept in both stores, with its labels, group and first quote.

    `not_labels` are deliberately excluded: a near-miss is a form the concept does
    *not* mean (`stage0/concepts.py` makes the same call).
    """
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load()
    groups: dict[str, str] = {}
    quotes: dict[str, str] = {}
    for entry in authored.of("concept_type"):
        if entry.sound:
            groups.setdefault(str(entry.record["concept"]), str(entry.record["type"]))
            for item in entry.evidence():
                if item.get("quote"):
                    quotes.setdefault(str(entry.record["concept"]), str(item["quote"]))
                    break
    for entry in authored.of("gold_concept"):
        if entry.sound:
            for item in entry.evidence():
                if item.get("quote"):
                    quotes[str(entry.record["id"])] = str(item["quote"])
                    break

    out: dict[str, Concept] = {}
    for origin, records in (("signed", gold["gold_concept"]), ("authored", authored["gold_concept"])):
        for record in records:
            identifier = str(record["id"])
            labels = [record.get("pref_label"), *(record.get("alt_labels") or ())]
            clean = tuple(dict.fromkeys(
                str(label).strip() for label in labels if isinstance(label, str) and label.strip()
            ))
            out[identifier] = Concept(
                id=identifier,
                pref_label=str(record.get("pref_label") or identifier),
                labels=clean,
                origin=origin,
                legislative_basis=tuple(str(r) for r in record.get("legislative_basis") or ()),
                group=groups.get(identifier),
                quote=quotes.get(identifier),
            )
    return dict(sorted(out.items()))


def _patterns(concept_map: dict[str, Concept]) -> list[tuple[str, re.Pattern[str], tuple[str, ...]]]:
    """(label, whole-word pattern, concepts carrying it), longest label first."""
    owners: dict[str, list[str]] = defaultdict(list)
    shown: dict[str, str] = {}
    for concept in concept_map.values():
        for label in concept.labels:
            if len(label) < MIN_LABEL_CHARS:
                continue
            key = label.lower()
            shown.setdefault(key, label)
            if concept.id not in owners[key]:
                owners[key].append(concept.id)
    ordered = sorted(owners, key=lambda key: (-len(key), key))
    return [
        (shown[key], re.compile(r"(?<![A-Za-z0-9])" + re.escape(key) + r"(?![A-Za-z0-9])", re.IGNORECASE),
         tuple(sorted(owners[key])))
        for key in ordered
    ]


def find_mentions(
    text: str, patterns: list[tuple[str, re.Pattern[str], tuple[str, ...]]]
) -> dict[str, tuple[int, int, str]]:
    """concept id -> (start, end, label) of its first whole-word mention in `text`."""
    found: dict[str, tuple[int, int, str]] = {}
    for label, pattern, owners in patterns:
        match = pattern.search(text)
        if match is None:
            continue
        for concept in owners:
            current = found.get(concept)
            if current is None or match.start() < current[0]:
                found[concept] = (match.start(), match.end(), label)
    return found


def link(corpus: Corpus, concept_map: dict[str, Concept] | None = None) -> Links:
    """Match every concept's labels against every Manual passage."""
    concept_map = concept_map if concept_map is not None else concepts()
    patterns = _patterns(concept_map)
    mentions: dict[str, list[tuple[str, int, int, str]]] = {cid: [] for cid in concept_map}
    ordered = sorted(corpus.chunks.values(), key=lambda c: (c.page_ref, c.ordinal))
    for chunk in ordered:
        for concept, (start, end, label) in find_mentions(chunk.text, patterns).items():
            mentions[concept].append((chunk.chunk_ref, start, end, label))
    total = len(ordered)
    generic = frozenset(cid for cid, hits in mentions.items() if len(hits) > GENERIC_SHARE * total)
    return Links(concepts=concept_map, mentions=mentions, passages=total, generic=generic)


def existing_edges(
    gold: goldset.GoldSet | None = None, authored: authored_store.AuthoredSet | None = None
) -> set[frozenset[str]]:
    """Unordered concept pairs some record already joins, in either store."""
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load()
    edges: set[frozenset[str]] = set()
    for records in (gold["gold_relationship"], authored["gold_relationship"]):
        for record in records:
            subject, obj = str(record["subject"]), str(record["object"])
            if subject.startswith("GC-") and obj.startswith("GC-"):
                edges.add(frozenset((subject, obj)))
    for records in (gold["gold_concept"], authored["gold_concept"]):
        for record in records:
            for key in ("broader", "narrower", "related"):
                for other in record.get(key) or ():
                    edges.add(frozenset((str(record["id"]), str(other))))
    return edges


def pairs(
    links: Links, already: set[frozenset[str]] | None = None, judged: set[frozenset[str]] | None = None
) -> list[Pair]:
    """Concept pairs worth one model judgement each, best first.

    Score is co-mentions over the geometric mean of the two concepts' passage
    counts — a cosine over passages — plus one for a shared legislative basis.
    Each concept keeps its best `PARTNERS_PER_CONCEPT`; a pair either side keeps
    is kept.

    A pair in `already` has a record and is no candidate at all. A pair in
    `judged` has been asked: it keeps its place in each concept's best six but is
    not returned — otherwise every answer would promote the next-best pair, and a
    re-run would never run out of pairs to ask about.
    """
    already = already or set()
    judged = judged or set()
    index = links.by_passage()
    df = {cid: len(hits) for cid, hits in links.mentions.items()}
    co: dict[frozenset[str], list[tuple[int, str]]] = defaultdict(list)
    for ref, present in index.items():
        ids = sorted(cid for cid in present if cid not in links.generic)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                distance = abs(present[a][0] - present[b][0])
                co[frozenset((a, b))].append((distance, ref))

    basis: dict[str, set[str]] = defaultdict(set)
    for concept in links.concepts.values():
        if concept.id in links.generic:
            continue
        for ref in concept.legislative_basis:
            basis[ref].add(concept.id)
    shared_basis: set[frozenset[str]] = set()
    for members in basis.values():
        ordered = sorted(members)
        if len(ordered) > 12:  # a provision every concept cites joins nothing
            continue
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                shared_basis.add(frozenset((a, b)))

    scored: dict[frozenset[str], Pair] = {}
    for key in set(co) | shared_basis:
        if key in already:
            continue
        a, b = sorted(key)
        hits = sorted(co.get(key, []))
        cosine = len(hits) / math.sqrt(max(df.get(a, 0), 1) * max(df.get(b, 0), 1)) if hits else 0.0
        signals = (["co_mention"] if hits else []) + (["shared_basis"] if key in shared_basis else [])
        scored[key] = Pair(
            a=a, b=b, score=cosine + (1.0 if key in shared_basis else 0.0),
            shared=tuple(dict.fromkeys(ref for _, ref in hits[:2])), signals=tuple(signals),
        )

    keep: set[frozenset[str]] = set()
    by_concept: dict[str, list[Pair]] = defaultdict(list)
    for pair in scored.values():
        by_concept[pair.a].append(pair)
        by_concept[pair.b].append(pair)
    for concept, candidates in by_concept.items():
        candidates.sort(key=lambda p: (-p.score, p.a, p.b))
        for pair in candidates[:PARTNERS_PER_CONCEPT]:
            keep.add(frozenset((pair.a, pair.b)))
    return sorted((scored[k] for k in keep - judged), key=lambda p: (-p.score, p.a, p.b))


def anchors(pair_list: Iterable[Pair]) -> dict[str, list[Pair]]:
    """Group pairs into model calls: one anchor concept, up to eight neighbours.

    Each pair goes to whichever end has fewer pairs so far, so no call is lopsided
    and every pair is asked about exactly once.
    """
    load: dict[str, list[Pair]] = defaultdict(list)
    for pair in pair_list:
        side = pair.a if len(load[pair.a]) <= len(load[pair.b]) else pair.b
        if len(load[side]) >= NEIGHBOURS_PER_ANCHOR:
            side = pair.b if side == pair.a else pair.a
            if len(load[side]) >= NEIGHBOURS_PER_ANCHOR:
                continue
        load[side].append(pair)
    return {k: v for k, v in sorted(load.items()) if v}


def write(links: Links, pair_list: list[Pair], out_dir: Path | None = None) -> list[Path]:
    """Write both files, sorted, so a rebuild with nothing changed changes nothing."""
    out_dir = out_dir or LINKS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    mentions_doc = {
        "method": "label_match",
        "note": "Whole-word, case-insensitive matches of each concept's pref and alt "
                "labels in Manual passages. Deterministic; no model; not reviewed "
                "because it asserts nothing but where a string occurs.",
        "passages": links.passages,
        "generic": sorted(links.generic),
        "concepts": {
            cid: {"labels": list(links.concepts[cid].labels),
                  "hits": [[ref, s, e] for ref, s, e, _ in hits]}
            for cid, hits in sorted(links.mentions.items())
        },
    }
    pairs_doc = {
        "method": "co_mention_cosine + shared_legislative_basis",
        "note": "Candidate pairs for the relationship job. Candidates, not relationships.",
        "pairs": [pair.as_dict() for pair in pair_list],
    }
    paths = []
    for path, doc in ((out_dir / MENTIONS_PATH.name, mentions_doc), (out_dir / PAIRS_PATH.name, pairs_doc)):
        path.write_text(json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
                        encoding="utf-8")
        paths.append(path)
    return paths

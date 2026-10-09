"""The vocabulary's consistency with itself — three checks the owner approved on 2026-10-09.

The ontology review found the repository's checks blind to the problems it listed
(review F2): "zero failures" meant nothing looked. These are the three the owner
approved once they were put in plain English (ADR-0125):

- **Shared names (A5).** Two concepts answering to the same name. The old check
  compared preferred labels letter for letter, so "Registrar" and "Registrar of
  Trade Marks" never met and "endorsements" never met "endorsement". This compares
  every label — preferred and alternative — after `fold`, and reports each clash.
  A clash is a warning, not a failure: two records sharing a name is sometimes a
  homonym the records already separate, and a person should look.
- **Pairs kept apart (A6).** A pair the relate model judged to be one idea and a
  ruling said is not. `authored/merge-candidates.yaml` records every suggestion and
  its decision; a kept-apart pair merged anyway is a defect.
- **"Kind of" beside "not the same as" (D4).** A machine-written "is a kind of" link
  between two concepts where either one lists the other's name as *not* this concept.
  Approved as a check that refuses the link. Read literally it would refuse links
  that are right — the expert's own signed record says every geographical indication
  is a geographical reference and still lists "geographical indication" as not the
  same concept (GC-0017's note), because a narrower idea is never *the same* idea —
  so the refusal yields to one thing only: a written affirmation, in
  `authored/kind-of-affirmed.yaml`, that the hierarchy holds beside the near-miss
  and why. Everything else is refused (ADR-0125).

Every function here reads records and judges nothing; the judgements are in the two
ledgers, each machine-written and unreviewed.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from tm_knowledge.authored import store as authored_store

__all__ = [
    "MERGE_CANDIDATES_FILE",
    "KIND_OF_AFFIRMED_FILE",
    "fold",
    "LabelClash",
    "label_clashes",
    "merge_candidates",
    "kept_apart",
    "affirmations",
    "KindOfClash",
    "kind_of_clashes",
]

MERGE_CANDIDATES_FILE = "merge-candidates.yaml"
KIND_OF_AFFIRMED_FILE = "kind-of-affirmed.yaml"

_ARTICLES = frozenset({"the", "a", "an"})


def _singular(word: str) -> str:
    """A crude singular, for comparison only — never shown to anybody."""
    word = re.sub(r"'s?$", "", word)  # registrar's, owners'
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def fold(label: str) -> str:
    """A label reduced to what two records sharing a name would share.

    Case, curly against straight apostrophes, hyphens and slashes against spaces,
    other punctuation, a leading article, and plurals and possessives word by word.
    Recognition already folds case and apostrophes (`bulk.links`); the rest is for
    finding names that a reader would call the same and a byte comparison would not.
    """
    text = label.lower().replace("’", "'").replace("‘", "'")
    text = re.sub(r"[-‐‑–—/]", " ", text)
    text = re.sub(r"[^\w' ]+", " ", text)
    words = text.split()
    while words and words[0] in _ARTICLES:
        words = words[1:]
    return " ".join(_singular(word) for word in words)


# ---------------------------------------------------------------------- A5


@dataclass(frozen=True)
class LabelClash:
    """One folded name carried by more than one concept."""

    folded: str
    #: (concept id, the label as that record writes it, "signed" | "authored")
    holders: tuple[tuple[str, str, str], ...]

    @property
    def concepts(self) -> tuple[str, ...]:
        return tuple(sorted({holder[0] for holder in self.holders}))

    def describe(self) -> str:
        return "; ".join(f"{cid} ({origin}) as {label!r}" for cid, label, origin in self.holders)


def label_clashes(concept_map: Mapping[str, Any]) -> tuple[LabelClash, ...]:
    """Every folded name two or more concepts carry, preferred or alternative.

    `concept_map` is `bulk.links.concepts()` — the served view, so a label a
    correction removed from a signed record is not counted, and one it added is.
    """
    holders: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for concept in concept_map.values():
        for label in concept.labels:
            key = fold(label)
            if key:
                holders[key].append((concept.id, label, concept.origin))
    out = []
    for key, found in sorted(holders.items()):
        if len({cid for cid, _, _ in found}) > 1:
            out.append(LabelClash(folded=key, holders=tuple(sorted(found))))
    return tuple(out)


# ---------------------------------------------------------------------- A6


def _read(root: Path | None, name: str) -> dict[str, Any]:
    path = (root or authored_store.AUTHORED_DIR) / name
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise authored_store.MalformedAuthoredFile(f"{path} is not a mapping")
    return data


def merge_candidates(root: Path | None = None) -> tuple[dict[str, Any], ...]:
    """Every `same_concept` suggestion and what was decided about it."""
    return tuple(_read(root, MERGE_CANDIDATES_FILE).get("candidates") or ())


def kept_apart(root: Path | None = None) -> frozenset[frozenset[str]]:
    """The pairs a ruling said are two ideas, never to be merged."""
    return frozenset(
        frozenset(str(x) for x in row["pair"])
        for row in merge_candidates(root)
        if row.get("decision") == "kept_apart"
    )


# ---------------------------------------------------------------------- D4


def affirmations(root: Path | None = None) -> dict[tuple[str, str], dict[str, Any]]:
    """(narrower, broader) -> the written reason the hierarchy stands beside a near-miss."""
    return {
        (str(row["narrower"]), str(row["broader"])): row
        for row in _read(root, KIND_OF_AFFIRMED_FILE).get("affirmed") or ()
    }


@dataclass(frozen=True)
class KindOfClash:
    """A "kind of" link whose two ends list each other's names as not this concept."""

    record_id: str
    narrower: str
    broader: str
    #: (the concept whose record says "not", the not-label, the other end's label)
    said: tuple[tuple[str, str, str], ...]
    affirmed: bool

    def describe(self) -> str:
        return "; ".join(f"{cid} lists {nl!r} as not the same concept" for cid, nl, _ in self.said)


def kind_of_clashes(
    concept_map: Mapping[str, Any],
    relationships: Iterable[dict[str, Any]],
    affirmed: Mapping[tuple[str, str], Any] | None = None,
) -> tuple[KindOfClash, ...]:
    """Every `broader` relationship whose ends say, in a not-label, that they differ.

    `relationships` are relationship records (either store); `broader` reads
    narrower → broader (ADR-0113). An end missing from `concept_map` is skipped —
    the cross-reference check reports that, not this one.
    """
    affirmed = affirmed or {}
    out = []
    for record in relationships:
        if record.get("predicate") != "broader":
            continue
        narrower, broader = str(record.get("subject")), str(record.get("object"))
        x, y = concept_map.get(narrower), concept_map.get(broader)
        if x is None or y is None:
            continue
        said = []
        for this, other in ((x, y), (y, x)):
            names = {fold(label): label for label in other.labels}
            for not_label in this.not_labels:
                if fold(not_label) in names:
                    said.append((this.id, not_label, names[fold(not_label)]))
        if said:
            out.append(KindOfClash(
                record_id=str(record.get("id")), narrower=narrower, broader=broader,
                said=tuple(said), affirmed=(narrower, broader) in affirmed,
            ))
    return tuple(out)

"""A small, deterministic Turtle writer.

Why not `rdflib` here: `graph/` is **committed** (ADR-0042), so the diff between
two builds is the paper trail. A serialiser whose output order is an
implementation detail turns "one concept changed" into a five-hundred-line diff
and destroys that. So the emitter sorts everything and writes it itself, and
`rdflib` is used only to *read back* what was written and prove it parses
(ADR-0058).

The other reason is smaller and still real: this keeps the core install at three
dependencies. Emitting the graph needs nothing; querying it needs `[graph]`.

**Every IRI is written in angle brackets unless the caller says otherwise.**
Turtle's `PN_LOCAL` does not admit `/`, and every ref in this corpus is full of
them — `tmkr:TMM/Part29/1` is not valid Turtle and a writer that abbreviates by
string concatenation produces a file that looks right and will not parse. Fixed
vocabulary terms whose local names are letters go through `PN`, which is the
caller promising the name is safe.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Iterator

__all__ = ["IRI", "PN", "Literal", "Term", "Triples", "Document", "escape"]


@dataclass(frozen=True, slots=True)
class IRI:
    """An absolute IRI. Always written `<...>`, always safe."""

    value: str

    def __str__(self) -> str:
        return f"<{self.value}>"


@dataclass(frozen=True, slots=True)
class PN:
    """A prefixed name the caller guarantees is legal — `skos:prefLabel`.

    Never build one of these from corpus data. It exists for the fixed
    vocabulary, where the local name is letters and the prefix is declared.
    """

    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Literal:
    """A literal, with an optional datatype or language tag."""

    value: str | int | bool | date
    datatype: PN | None = None
    language: str | None = None

    def __str__(self) -> str:
        if isinstance(self.value, bool):
            return "true" if self.value else "false"
        if isinstance(self.value, int):
            return str(self.value)
        if isinstance(self.value, date):
            return f'"{self.value.isoformat()}"^^xsd:date'
        text = f'"{escape(str(self.value))}"'
        if self.language:
            return f"{text}@{self.language}"
        if self.datatype:
            return f"{text}^^{self.datatype}"
        return text


Term = IRI | PN | Literal

_ESCAPES = {
    "\\": "\\\\",
    '"': '\\"',
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}


def escape(text: str) -> str:
    """Escape a string for a Turtle short literal.

    Backslash first, or every subsequent escape gets escaped again — the classic
    way to produce a file that parses and says something different.
    """
    for character, replacement in _ESCAPES.items():
        text = text.replace(character, replacement)
    return text


class Triples:
    """A set of triples that knows how to print itself the same way every time.

    Ordering is total and explicit: subjects by IRI, `a` before every other
    predicate, then predicates alphabetically, then objects. Two builds over the
    same input produce byte-identical files, which is the whole point.
    """

    def __init__(self) -> None:
        self._by_subject: dict[str, dict[str, list[str]]] = {}
        self._subjects: dict[str, Term] = {}

    def add(self, subject: Term, predicate: Term, obj: Term) -> "Triples":
        key = str(subject)
        self._subjects.setdefault(key, subject)
        self._by_subject.setdefault(key, {}).setdefault(str(predicate), []).append(
            str(obj)
        )
        return self

    def add_all(
        self, subject: Term, predicate: Term, objects: Iterable[Term]
    ) -> "Triples":
        for obj in objects:
            self.add(subject, predicate, obj)
        return self

    def __len__(self) -> int:
        """Distinct triples — what a parser will find, not what was offered.

        Counting insertions rather than triples reports a number nothing else
        agrees with: the same object added twice is one triple in every store
        that reads the file, and `blocks()` already writes it once.
        """
        return sum(
            len(set(objects))
            for predicates in self._by_subject.values()
            for objects in predicates.values()
        )

    @property
    def subjects(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_subject))

    def _predicate_order(self, name: str) -> tuple[int, str]:
        return (0, "") if name == "a" else (1, name)

    def blocks(self) -> Iterator[str]:
        for subject in self.subjects:
            predicates = self._by_subject[subject]
            lines = [f"{subject}"]
            names = sorted(predicates, key=self._predicate_order)
            for index, name in enumerate(names):
                objects = sorted(set(predicates[name]))
                terminator = " ." if index == len(names) - 1 else " ;"
                if len(objects) == 1:
                    lines.append(f"    {name} {objects[0]}{terminator}")
                    continue
                lines.append(f"    {name}")
                for position, obj in enumerate(objects):
                    tail = terminator if position == len(objects) - 1 else " ,"
                    lines.append(f"        {obj}{tail}")
            yield "\n".join(lines)


@dataclass
class Document:
    """A Turtle file: a header, prefix declarations and a body of triples."""

    header: tuple[str, ...]
    prefixes: dict[str, str]
    triples: Triples

    def render(self) -> str:
        out = [f"# {line}".rstrip() for line in self.header]
        out.append("")
        for prefix in sorted(self.prefixes):
            out.append(f"@prefix {prefix}: <{self.prefixes[prefix]}> .")
        out.append("")
        for block in self.triples.blocks():
            out.append(block)
            out.append("")
        return "\n".join(out).rstrip() + "\n"

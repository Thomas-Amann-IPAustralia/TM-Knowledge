"""Read the pinned snapshot into typed records.

The one door between `data/upstream/` and everything this repo builds. It
verifies the pin before it reads anything (`--shallow` by default, because the
deep digest reads 60MB and the fetcher already checked it), and it never writes
into the snapshot.

The join is the point. A chunk's `provisions[].id` **is** a provision or unit
`ref` in the legislation half, with no transformation and no lookup table
(`docs/UPSTREAM.md` §5). `Corpus.resolve_provision` is that string equality and
nothing more; if it ever needs to normalise a ref to work, something upstream of
it has already broken the corpus.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from tm_knowledge.config import UPSTREAM_DIR
from tm_knowledge.upstream.pin import Pin, verify
from tm_knowledge.upstream.records import Chunk, Page, Provision, Unit

__all__ = ["Corpus", "JoinReport", "load_corpus"]

#: The instruments this corpus holds. A Manual edge to anything else — the Acts
#: Interpretation Act, the repealed 1955 Act — is legitimately unresolvable and
#: is not counted against coverage. Upstream draws the line the same way.
HELD_INSTRUMENTS = frozenset({"TMA1995", "TMR1995"})


@dataclass(frozen=True, slots=True)
class JoinReport:
    """Coverage of Manual provision edges against the legislation held.

    A report, never a failure (upstream's own words). The number to watch is the
    resolved count against the held instruments: if it falls, a citation regex
    or a numbering assumption has moved.
    """

    total: int
    in_scope: int
    resolved: int

    @property
    def unresolved(self) -> int:
        return self.in_scope - self.resolved

    @property
    def coverage(self) -> float:
        return self.resolved / self.in_scope if self.in_scope else 0.0

    def __str__(self) -> str:
        return (
            f"{self.resolved}/{self.in_scope} in-scope provision edges resolve "
            f"({self.coverage:.1%}); {self.total} edges total"
        )


@dataclass(frozen=True)
class Corpus:
    """The loaded snapshot: pages, chunks, provisions and units, joined."""

    pin: Pin
    pages: dict[str, Page]
    chunks: dict[str, Chunk]
    provisions: dict[str, Provision]
    units: dict[str, Unit]
    _chunks_by_page: dict[str, tuple[str, ...]] = field(default_factory=dict)

    # -- lookups ------------------------------------------------------------

    def resolve_provision(self, ref: str) -> Provision | Unit | None:
        """The provision or unit a Manual edge names, by string equality.

        `None` means the corpus does not hold it — an edge to the Acts
        Interpretation Act, or one of the 76 defects and superseded numberings
        upstream leaves visible (Q-06, Q-08). It never means "not found yet";
        there is no second lookup to try.
        """
        return self.provisions.get(ref) or self.units.get(ref)

    def chunks_on_page(self, page_ref: str) -> tuple[Chunk, ...]:
        """Every chunk cut from a page, in `ordinal` order. The page-mates that
        ADR-0022's worksheet rule turns on."""
        return tuple(self.chunks[ref] for ref in self._chunks_by_page.get(page_ref, ()))

    def chunks_citing(self, ref: str, *, include_units: bool = True) -> tuple[Chunk, ...]:
        """Chunks whose `provisions[]` cite a ref, or a unit beneath it.

        Matched on the ref grammar, never by substring: `TMA1995/s43` must not
        match `TMA1995/s430` (ADR-0022). Edges of every `extraction` and
        `certainty` value are included — an `ambiguous` edge is a reason to
        surface a chunk, never a reason to drop one (Q-07).
        """
        prefixes = (ref + "(", ref + "~", ref + "/")
        matched = []
        for chunk in self.chunks.values():
            for edge in chunk.provisions:
                if edge.id == ref or (include_units and edge.id.startswith(prefixes)):
                    matched.append(chunk)
                    break
        return tuple(sorted(matched, key=lambda c: (c.page_ref, c.ordinal)))

    # -- reports ------------------------------------------------------------

    def join_report(self) -> JoinReport:
        total = in_scope = resolved = 0
        known = self.provisions.keys() | self.units.keys()
        for chunk in self.chunks.values():
            for edge in chunk.provisions:
                total += 1
                if edge.id.split("/", 1)[0] not in HELD_INSTRUMENTS:
                    continue
                in_scope += 1
                if edge.id in known:
                    resolved += 1
        return JoinReport(total=total, in_scope=in_scope, resolved=resolved)

    def unresolved_edges(self) -> tuple[str, ...]:
        """In-scope edges that land on nothing, sorted and deduplicated.

        Worth having before gold records are built on one: this is where the
        s 41 renumbering trap surfaces (Q-06).
        """
        known = self.provisions.keys() | self.units.keys()
        return tuple(
            sorted(
                {
                    edge.id
                    for chunk in self.chunks.values()
                    for edge in chunk.provisions
                    if edge.id.split("/", 1)[0] in HELD_INSTRUMENTS and edge.id not in known
                }
            )
        )

    def ambiguous_edges(self) -> tuple[tuple[str, str], tuple[str, str], ...]:
        """(`chunk_ref`, `provision id`) for every `certainty: ambiguous` edge.

        These are upstream refusing to guess. They are recorded as ambiguous,
        queued for a human, and never "corrected" (Q-07)."""
        return tuple(
            sorted(
                (chunk.chunk_ref, edge.id)
                for chunk in self.chunks.values()
                for edge in chunk.provisions
                if edge.needs_a_human
            )
        )


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _page_files(root: Path) -> Iterator[Path]:
    return iter(sorted((root / "snapshot" / "pages").rglob("*.json")))


def _provision_files(root: Path) -> Iterator[Path]:
    return iter(sorted((root / "snapshot" / "legislation").rglob("provisions/*/*.json")))


def load_corpus(root: Path | None = None, *, deep_verify: bool = False) -> Corpus:
    """Load the whole pinned corpus. Verifies the pin first, and refuses without it."""
    root = root or UPSTREAM_DIR
    pin = Pin.load()
    verify(root, pin, deep=deep_verify)

    pages: dict[str, Page] = {}
    chunks: dict[str, Chunk] = {}
    by_page: dict[str, list[str]] = {}
    for path in _page_files(root):
        document = _read(path)
        page = Page.from_dict(document["page"])
        pages[page.page_ref] = page
        for record in document["chunks"]:
            chunk = Chunk.from_dict(record)
            chunks[chunk.chunk_ref] = chunk
            by_page.setdefault(chunk.page_ref, []).append(chunk.chunk_ref)

    provisions: dict[str, Provision] = {}
    units: dict[str, Unit] = {}
    for path in _provision_files(root):
        provision = Provision.from_dict(_read(path))
        provisions[provision.ref] = provision
        for unit in provision.units:
            units[unit.ref] = unit

    ordered = {
        page_ref: tuple(sorted(refs, key=lambda ref: chunks[ref].ordinal))
        for page_ref, refs in by_page.items()
    }
    return Corpus(
        pin=pin,
        pages=pages,
        chunks=chunks,
        provisions=provisions,
        units=units,
        _chunks_by_page=ordered,
    )

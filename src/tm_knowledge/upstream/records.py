"""Typed records for the pinned upstream snapshot.

One class per upstream record shape — page, chunk, provision, unit — plus the
three citation edges a chunk carries. The contract these keep is narrow and
absolute (P2, CLAUDE.md rules 2 and 3):

1. **`extraction` and `certainty` survive intact.** No default value, no
   collapsing `default` into `explicit`, no dropping `ambiguous`. A loader that
   returns a bare list of provision ids has destroyed the trust metadata and is
   worse than no loader.
2. **Refs pass through byte-for-byte.** Nothing is lowercased, stripped, padded
   or re-split; that breaks the string-equality join.
3. **`content_hash` travels with the record**, because staleness detection in
   every later stage depends on it.

Two design choices worth stating, because both are load-bearing.

**An unknown field is an error, not a shrug.** `from_dict` raises on a key it
does not know. Upstream adding a field is a change this repo must notice — a
loader that silently drops one is exactly the failure the round-trip test exists
to prevent, and "fail loud, never guess" (CLAUDE.md rule 6) applies to schema
drift as much as to ambiguous data.

**Rich nested structures stay as they arrived.** `blocks`, `links`, `emphasis`,
`tables` and `headings` are carried as the mappings upstream wrote, not
re-typed. They are shape upstream has already fixed and validated; a second,
subtly different typing of them here would be a second reading of the same data
that agreed with the first until it quietly did not.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Any, ClassVar, Mapping, Sequence

from tm_knowledge.refs import RefKind, parse_ref

__all__ = [
    "UpstreamSchemaDrift",
    "ProvisionEdge",
    "CaseEdge",
    "InternalRef",
    "Chunk",
    "Page",
    "Unit",
    "Provision",
]


class UpstreamSchemaDrift(RuntimeError):
    """Upstream emitted a field this loader does not know about.

    Raised rather than ignored. The pin exists so that a corpus change is a
    deliberate, reviewed event (ADR-0004); a field appearing unannounced is that
    event, and it is worth stopping for.
    """


def _split(record: Mapping[str, Any], known: frozenset[str], where: str) -> dict[str, Any]:
    unknown = set(record) - known
    if unknown:
        raise UpstreamSchemaDrift(
            f"{where}: upstream field(s) {sorted(unknown)} are not in this "
            f"loader. Bump the pin deliberately and update "
            f"tm_knowledge.upstream.records — do not drop them."
        )
    return dict(record)


def _frozen(value: Any) -> Any:
    """Freeze a nested JSON structure so a loaded record cannot be edited.

    `data/upstream/` is read-only (ADR-0002), and the in-memory copy is held to
    the same rule: an accidental mutation here is an invisible fork of the
    corpus that no digest would catch.
    """
    if isinstance(value, Mapping):
        return MappingProxyType({key: _frozen(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_frozen(item) for item in value)
    return value


def _thawed(value: Any) -> Any:
    """Inverse of `_frozen`, for `to_dict`."""
    if isinstance(value, (MappingProxyType, dict)):
        return {key: _thawed(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_thawed(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class ProvisionEdge:
    """A statutory reference on a chunk or unit, with how it was found.

    `extraction` and `certainty` are upstream's words and are never
    reinterpreted here. `certainty` is present on `regex` edges only; an
    `ambiguous` edge feeds a human queue and nothing else (Q-07).
    """

    id: str
    extraction: str
    certainty: str | None = None
    mention: str | None = None

    _KNOWN: ClassVar[frozenset[str]] = frozenset({"id", "extraction", "certainty", "mention"})

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "ProvisionEdge":
        data = _split(record, cls._KNOWN, "provisions[]")
        # Validated, never rewritten: parse_ref raises on a ref this repo could
        # not have read from upstream, and returns the value unchanged.
        parse_ref(data["id"])
        return cls(
            id=data["id"],
            extraction=data["extraction"],
            certainty=data.get("certainty"),
            mention=data.get("mention"),
        )

    def to_dict(self) -> dict[str, Any]:
        record: dict[str, Any] = {"id": self.id, "extraction": self.extraction}
        if self.certainty is not None:
            record["certainty"] = self.certainty
        if self.mention is not None:
            record["mention"] = self.mention
        return record

    @property
    def is_authors_own_link(self) -> bool:
        """`href` — the Manual's authors linked this themselves. The strongest
        evidence the corpus has, and the reason `extraction` may not be
        collapsed."""
        return self.extraction == "href"

    @property
    def needs_a_human(self) -> bool:
        """`ambiguous` — several instruments of that kind are in scope. Never
        auto-resolved; that is what upstream refused to implement."""
        return self.certainty == "ambiguous"


@dataclass(frozen=True, slots=True)
class CaseEdge:
    """A case citation. Citation level only — no decision text exists (Q-11)."""

    id: str
    citation: str

    _KNOWN: ClassVar[frozenset[str]] = frozenset({"id", "citation"})

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "CaseEdge":
        data = _split(record, cls._KNOWN, "cases[]")
        return cls(id=data["id"], citation=data["citation"])

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "citation": self.citation}


@dataclass(frozen=True, slots=True)
class InternalRef:
    """A Manual-internal cross reference, resolved to a page or chunk ref.

    Unresolvable targets are **dropped by upstream, not recorded**, so absence is
    not evidence that the source made no reference (Q-08). Self-page refs are
    kept on purpose.
    """

    ref: str
    extraction: str
    certainty: str | None = None
    mention: str | None = None

    _KNOWN: ClassVar[frozenset[str]] = frozenset({"ref", "extraction", "certainty", "mention"})

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "InternalRef":
        data = _split(record, cls._KNOWN, "internal_refs[]")
        parse_ref(data["ref"])
        return cls(
            ref=data["ref"],
            extraction=data["extraction"],
            certainty=data.get("certainty"),
            mention=data.get("mention"),
        )

    def to_dict(self) -> dict[str, Any]:
        record: dict[str, Any] = {"ref": self.ref, "extraction": self.extraction}
        if self.certainty is not None:
            record["certainty"] = self.certainty
        if self.mention is not None:
            record["mention"] = self.mention
        return record


@dataclass(frozen=True, slots=True)
class Chunk:
    """One retrievable passage of the Manual — the addressable unit of this repo.

    Not "paragraph 4.3.12": `heading_path` is a retrieval signal and a weak
    structural guarantee, because some Manual subsections are bold text that was
    never marked up as a heading (Q-10). `chunk_ref` is the address.
    """

    chunk_ref: str
    page_ref: str
    text: str
    heading_path: tuple[str, ...]
    ordinal: int
    content_hash: str
    kind: str = "body"
    heading_source: str | None = None
    fragment: Mapping[str, Any] | None = None
    provisions: tuple[ProvisionEdge, ...] = ()
    cases: tuple[CaseEdge, ...] = ()
    internal_refs: tuple[InternalRef, ...] = ()
    headings: tuple[Mapping[str, Any], ...] = ()
    blocks: tuple[Mapping[str, Any], ...] = ()
    links: tuple[Mapping[str, Any], ...] = ()
    emphasis: tuple[Mapping[str, Any], ...] = ()
    tables: tuple[Mapping[str, Any], ...] = ()

    _KNOWN: ClassVar[frozenset[str]] = frozenset(
        {
            "chunk_ref", "page_ref", "text", "heading_path", "ordinal", "content_hash",
            "kind", "heading_source", "fragment", "provisions", "cases", "internal_refs",
            "headings", "blocks", "links", "emphasis", "tables",
        }
    )

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "Chunk":
        data = _split(record, cls._KNOWN, "chunk")
        parse_ref(data["chunk_ref"], kind=RefKind.MANUAL_CHUNK)
        parse_ref(data["page_ref"], kind=RefKind.MANUAL_PAGE)
        return cls(
            chunk_ref=data["chunk_ref"],
            page_ref=data["page_ref"],
            text=data["text"],
            heading_path=tuple(data["heading_path"]),
            ordinal=data["ordinal"],
            content_hash=data["content_hash"],
            kind=data.get("kind", "body"),
            heading_source=data.get("heading_source"),
            fragment=_frozen(data["fragment"]) if data.get("fragment") is not None else None,
            provisions=tuple(ProvisionEdge.from_dict(e) for e in data.get("provisions", [])),
            cases=tuple(CaseEdge.from_dict(e) for e in data.get("cases", [])),
            internal_refs=tuple(
                InternalRef.from_dict(e) for e in data.get("internal_refs", [])
            ),
            headings=_frozen(data.get("headings", [])),
            blocks=_frozen(data.get("blocks", [])),
            links=_frozen(data.get("links", [])),
            emphasis=_frozen(data.get("emphasis", [])),
            tables=_frozen(data.get("tables", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_ref": self.chunk_ref,
            "page_ref": self.page_ref,
            "text": self.text,
            "heading_path": list(self.heading_path),
            "ordinal": self.ordinal,
            "content_hash": self.content_hash,
            "kind": self.kind,
            "heading_source": self.heading_source,
            "fragment": _thawed(self.fragment),
            "provisions": [edge.to_dict() for edge in self.provisions],
            "cases": [edge.to_dict() for edge in self.cases],
            "internal_refs": [edge.to_dict() for edge in self.internal_refs],
            "headings": _thawed(self.headings),
            "blocks": _thawed(self.blocks),
            "links": _thawed(self.links),
            "emphasis": _thawed(self.emphasis),
            "tables": _thawed(self.tables),
        }

    @property
    def part_id(self) -> str:
        """`Part22`, derived from the ref.

        Upstream omits this because it is derivable (Q-09) — but note the Part
        comes from the *nav tree*, never the URL, and the ref carries the nav's
        answer. Deriving it from anything else is how a chunk ends up in the
        wrong Part.
        """
        return self.chunk_ref.split("/")[1]

    def text_at(self, start: int, end: int) -> str:
        return self.text[start:end]


@dataclass(frozen=True, slots=True)
class Page:
    """One Manual page: everything constant across the chunks cut from it."""

    page_ref: str
    part_id: str
    url: str
    nav_title: str
    content_hash: str
    crawled_at: str
    extractor_version: str
    archived: bool
    h1: str | None = None
    printed_page_ref: str | None = None
    images: tuple[Mapping[str, Any], ...] = ()
    date_published: str | None = None
    last_amended: str | None = None
    amendment_note: str | None = None
    amendments: tuple[Mapping[str, Any], ...] = ()

    _KNOWN: ClassVar[frozenset[str]] = frozenset(
        {
            "page_ref", "part_id", "url", "nav_title", "h1", "printed_page_ref",
            "content_hash", "archived", "images", "date_published", "last_amended",
            "amendment_note", "amendments", "crawled_at", "extractor_version",
        }
    )

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "Page":
        data = _split(record, cls._KNOWN, "page")
        parse_ref(data["page_ref"], kind=RefKind.MANUAL_PAGE)
        return cls(
            page_ref=data["page_ref"],
            part_id=data["part_id"],
            url=data["url"],
            nav_title=data["nav_title"],
            content_hash=data["content_hash"],
            crawled_at=data["crawled_at"],
            extractor_version=data["extractor_version"],
            archived=data["archived"],
            h1=data.get("h1"),
            printed_page_ref=data.get("printed_page_ref"),
            images=_frozen(data.get("images", [])),
            date_published=data.get("date_published"),
            last_amended=data.get("last_amended"),
            amendment_note=data.get("amendment_note"),
            amendments=_frozen(data.get("amendments", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_ref": self.page_ref,
            "part_id": self.part_id,
            "url": self.url,
            "nav_title": self.nav_title,
            "h1": self.h1,
            "printed_page_ref": self.printed_page_ref,
            "content_hash": self.content_hash,
            "archived": self.archived,
            "images": _thawed(self.images),
            "date_published": self.date_published,
            "last_amended": self.last_amended,
            "amendment_note": self.amendment_note,
            "amendments": _thawed(self.amendments),
            "crawled_at": self.crawled_at,
            "extractor_version": self.extractor_version,
        }

    @property
    def disagrees_with_its_own_heading(self) -> bool:
        """Two Manual pages print an `h1` naming a different page than the nav
        gives them. Upstream records the disagreement rather than resolving it;
        so does this."""
        return self.printed_page_ref is not None


@dataclass(frozen=True, slots=True)
class Unit:
    """A numbered unit inside a provision — subsection, paragraph, definition."""

    ref: str
    ordinal: int
    depth: int
    kind: str
    text: str
    content_hash: str
    parent_ref: str | None = None
    style: str | None = None
    number: str | None = None
    number_collision: Any = None
    emphasis: tuple[Mapping[str, Any], ...] = ()
    provisions: tuple[ProvisionEdge, ...] = ()
    table: Mapping[str, Any] | None = None

    _KNOWN: ClassVar[frozenset[str]] = frozenset(
        {
            "ref", "parent_ref", "ordinal", "depth", "kind", "style", "number",
            "text", "content_hash", "number_collision", "emphasis", "provisions", "table",
        }
    )

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "Unit":
        data = _split(record, cls._KNOWN, "units[]")
        parse_ref(data["ref"], kind=RefKind.UNIT)
        return cls(
            ref=data["ref"],
            ordinal=data["ordinal"],
            depth=data["depth"],
            kind=data["kind"],
            text=data["text"],
            content_hash=data["content_hash"],
            parent_ref=data.get("parent_ref"),
            style=data.get("style"),
            number=data.get("number"),
            number_collision=_frozen(data.get("number_collision")),
            emphasis=_frozen(data.get("emphasis", [])),
            provisions=tuple(ProvisionEdge.from_dict(e) for e in data.get("provisions", [])),
            table=_frozen(data["table"]) if data.get("table") is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "ref": self.ref,
            "parent_ref": self.parent_ref,
            "ordinal": self.ordinal,
            "depth": self.depth,
            "kind": self.kind,
            "style": self.style,
            "number": self.number,
            "text": self.text,
            "content_hash": self.content_hash,
        }
        if self.number_collision is not None:
            record["number_collision"] = _thawed(self.number_collision)
        if self.emphasis:
            record["emphasis"] = _thawed(self.emphasis)
        if self.provisions:
            record["provisions"] = [edge.to_dict() for edge in self.provisions]
        if self.table is not None:
            record["table"] = _thawed(self.table)
        return record


@dataclass(frozen=True, slots=True)
class Provision:
    """One section, regulation, Schedule clause or container of an instrument."""

    ref: str
    instrument: str
    kind: str
    containers: tuple[Any, ...]
    heading_path: tuple[str, ...]
    text: str
    content_hash: str
    captured_at: str
    extractor_version: str
    number: str | None = None
    title: str | None = None
    units: tuple[Unit, ...] = ()

    _KNOWN: ClassVar[frozenset[str]] = frozenset(
        {
            "ref", "instrument", "kind", "number", "title", "containers",
            "heading_path", "text", "content_hash", "units", "captured_at",
            "extractor_version",
        }
    )

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> "Provision":
        data = _split(record, cls._KNOWN, "provision")
        parse_ref(data["ref"], kind=RefKind.PROVISION)
        return cls(
            ref=data["ref"],
            instrument=data["instrument"],
            kind=data["kind"],
            containers=_frozen(data["containers"]),
            heading_path=tuple(data["heading_path"]),
            text=data["text"],
            content_hash=data["content_hash"],
            captured_at=data["captured_at"],
            extractor_version=data["extractor_version"],
            number=data.get("number"),
            title=data.get("title"),
            units=tuple(Unit.from_dict(u) for u in data.get("units", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "instrument": self.instrument,
            "kind": self.kind,
            "number": self.number,
            "title": self.title,
            "containers": _thawed(self.containers),
            "heading_path": list(self.heading_path),
            "text": self.text,
            "content_hash": self.content_hash,
            "units": [unit.to_dict() for unit in self.units],
            "captured_at": self.captured_at,
            "extractor_version": self.extractor_version,
        }

    def unit_refs(self) -> tuple[str, ...]:
        return tuple(unit.ref for unit in self.units)

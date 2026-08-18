"""Upstream refs, IRIs and the identifiers this repo mints.

The executable form of `docs/IDENTIFIERS.md`. Three jobs:

1. **Read** an upstream ref — parse it, classify it, and reject anything that is
   not one (loudly: `InvalidRef`, never a silent normalisation).
2. **Mint** an IRI from a ref, reversibly. This is the *only* module that
   constructs an IRI; nothing else concatenates a base (`IDENTIFIERS.md` §2).
3. **Mint** this repo's own identifiers — the content-addressed candidate id of
   §3, and the sequential allocator for human-facing ids.

Refs are upstream's, and this module never invents, reformats or normalises one
(ADR-0005, confirmed by ADR-0021). Every grammar below is transcribed from
`manual-XtrACTor`'s `schema/*.json`, and the two instrument invariants mirror
`tmm_snapshot.citations.instrument_holds` — including its "unknown instruments
pass" semantics, which is a check for a contradiction and not a whitelist.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from tm_knowledge.config import base_iri

__all__ = [
    "InvalidRef",
    "Ref",
    "RefKind",
    "parse_ref",
    "is_ref",
    "instrument_holds",
    "to_iri",
    "from_iri",
    "PREFIXES",
    "candidate_id",
    "normalise_value",
    "SequentialRegister",
]


class InvalidRef(ValueError):
    """A string that is not an upstream ref.

    Raised rather than repaired. A ref that needs repairing was constructed, not
    read, and constructing one breaks the string-equality join (CLAUDE.md rule 6,
    `IDENTIFIERS.md` §1).
    """


class RefKind(str, Enum):
    """What an upstream ref addresses.

    `MANUAL` and `LEGISLATION` are not fallbacks for a malformed ref — they are
    the honest answer for a well-formed ref whose *level* the grammar cannot
    decide. A page ref and a chunk ref share a grammar, and so do a provision
    ref and the ref of a definition unit inside it (`TMR1995/sch3/item1` is a
    provision, `TMA1995/s128/prescribed-period` is a unit). 228 refs in the
    pinned corpus sit in that gap. Resolving one needs the snapshot, so it is
    the loader's job, not this module's. QUIRKS Q-18.
    """

    MANUAL_PAGE = "manual_page"
    MANUAL_CHUNK = "manual_chunk"
    MANUAL = "manual"
    PROVISION = "provision"
    UNIT = "unit"
    LEGISLATION = "legislation"
    CASE = "case"


# ---------------------------------------------------------------------------
# Grammar — transcribed from upstream `schema/*.json`, not re-derived
# ---------------------------------------------------------------------------

#: A Manual page ref: `TMM/Part22/1`, `TMM/Part9/x-relevant-legislation23`.
#: From `page.schema.json`. Note it admits `#`, though no page ref in the
#: pinned corpus carries one.
_PAGE = re.compile(r"^TMM/Part[0-9]{1,3}[A-Z]?/[A-Za-z0-9/#.-]+$")

#: A Manual chunk ref: `TMM/Part22/1/1/2`, `TMM/Part26/6#3~2`.
#: From `chunk.schema.json`. The chunk grammar is the page grammar plus `~`.
_CHUNK = re.compile(r"^TMM/Part[0-9]{1,3}[A-Z]?/[A-Za-z0-9/#~.-]+$")

#: A provision or unit ref **as a Manual chunk cites it** — the form that
#: carries the join. From `chunk.schema.json` `provisions[].id`.
_CITED_PROVISION = re.compile(
    r"^[A-Z]{2,8}[0-9]{4}/"
    r"(sch[0-9]+[A-Z]*"
    r"|[sr][0-9]+[A-Z]*(\.[0-9]+[A-Z]*)*(\([0-9a-zA-Z]{1,3}\))*)$"
)

#: A provision ref **as the legislation snapshot records it**. Wider than the
#: cited form: it also addresses Schedule clauses and items and an instrument's
#: front matter — `TMR1995/sch3/item1`, `TMR1995/sch9/c1`, `TMA1995/front`.
#: From `provision.schema.json`.
_PROVISION_RECORD = re.compile(r"^[A-Z]{2,8}[0-9]{4}/[A-Za-z0-9/~.()-]+$")

#: A canonical case id, as upstream's `cases[].id` emits it:
#: `CASE/2018/FCAFC/109`, `CASE/1894/RPC/11/518`. Citation level only — no
#: decision text exists anywhere in the programme (Q-11).
_CASE = re.compile(r"^CASE/[0-9]{4}/[A-Za-z]{2,10}/[0-9]+(/[0-9]+)?$")

#: The subdivision tail that makes a legislation ref a *unit* rather than a
#: whole provision. Two forms, and both are upstream's: the cited form
#: `TMA1995/s41(3)(a)`, and the ordinal form the snapshot mints for units of a
#: provision that has no numbered subdivisions — `TMA1995/front~1`,
#: `TMR1995/sch1/pt2~1`. Measured over the pinned corpus: no provision ref
#: carries either character, and 5,624 of the 5,813 unit refs carry one. The
#: remaining 189 are definition slugs and are not decidable — see `RefKind`.
_UNIT_TAIL = re.compile(r"\(|~")

#: A provision address in the form a Manual chunk cites, with no instrument:
#: `s41`, `r3A.3`, `sch2`. A legislation ref whose address is exactly this is a
#: whole provision; one with extra path segments may be either.
_PROVISION_ADDRESS = re.compile(
    r"^(sch[0-9]+[A-Z]*|[sr][0-9]+[A-Z]*(\.[0-9]+[A-Z]*)*)$"
)

#: The leading word of a legislation address. `s41(3)(a)` -> `s`,
#: `sch1/pt2` -> `sch`, `front` -> `front`.
_ADDRESS_HEAD = re.compile(r"^[A-Za-z]+")

#: A provision number with the subdivision detail stripped: `s44(3)(a)` -> `44`.
_NUMBER_ONLY = re.compile(r"^[^(]*")

#: A Schedule address, matched as a whole segment and never by its first
#: character, which is the `s` of a section.
_SCHEDULE_ADDRESS = re.compile(r"^sch\d")

# ---------------------------------------------------------------------------
# Instrument facts — mirrored from `tmm_snapshot.citations`
# ---------------------------------------------------------------------------

#: The kind of provision an instrument divides its body into. Absence means
#: "not asserted", never "holds sections".
INSTRUMENT_KIND: dict[str, str] = {
    "TMA1995": "s",
    "TMA1955": "s",
    "TMA1905": "s",
    "AIA1901": "s",
    "TMR1995": "r",
}

#: Whether an instrument's provision numbers carry dots. Upstream measured it:
#: 0 of the Act's 315 section numbers contain a dot, and 401 of the
#: Regulations' 401 regulation numbers do. **Only instruments actually read are
#: listed** — the Criminal Code Act 1995 numbers its sections `6.1`, and
#: asserting a rule about an instrument nobody has read is the guess rule 6
#: forbids.
INSTRUMENT_DOTTED: dict[str, bool] = {"TMA1995": False, "TMR1995": True}


@dataclass(frozen=True, slots=True)
class Ref:
    """A parsed upstream ref. `value` is the ref, byte-for-byte as it arrived."""

    value: str
    kind: RefKind
    #: Instrument code for a provision or unit ref (`TMA1995`), else `None`.
    instrument: str | None = None
    #: The provision a unit sits under (`TMA1995/s41(3)(a)` -> `TMA1995/s41`),
    #: else `None`. Derivable, and upstream deliberately does not store it (Q-09).
    root: str | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


def parse_ref(value: str, *, kind: RefKind | None = None) -> Ref:
    """Parse an upstream ref, or raise `InvalidRef`.

    Pass `kind` when the caller already knows what it is holding — a
    `page_ref` field, say — and the grammar's own ambiguity is not wanted.

    **Manual page and chunk refs are not distinguishable by grammar** and this
    function does not pretend otherwise. A page ref is a prefix of the chunk
    refs cut from it, both admit slug segments, and in the pinned corpus page
    refs carry 2 or 3 slashes while chunk refs carry 2 to 7. So a bare
    `TMM/Part14/4/4/5` parses as `RefKind.MANUAL`: well-formed, not yet placed.
    Only two things settle it — the field it came out of, or the snapshot.
    """
    if not isinstance(value, str):
        raise InvalidRef(f"ref must be a string, got {type(value).__name__}")
    if value != value.strip() or not value:
        raise InvalidRef(f"ref has leading/trailing whitespace or is empty: {value!r}")

    if kind is not None:
        return _parse_as(value, kind)

    if value.startswith("TMM/"):
        return _parse_manual(value)
    if value.startswith("CASE/"):
        if not _CASE.match(value):
            raise InvalidRef(f"not a case id: {value!r}")
        return Ref(value, RefKind.CASE)
    if _CITED_PROVISION.match(value) or _PROVISION_RECORD.match(value):
        return _parse_legislation(value)
    raise InvalidRef(f"not an upstream ref: {value!r}")


def _parse_as(value: str, kind: RefKind) -> Ref:
    if kind is RefKind.MANUAL_PAGE:
        if not _PAGE.match(value):
            raise InvalidRef(f"not a Manual page ref: {value!r}")
        return Ref(value, kind)
    if kind is RefKind.MANUAL_CHUNK:
        if not _CHUNK.match(value):
            raise InvalidRef(f"not a Manual chunk ref: {value!r}")
        return Ref(value, kind)
    if kind is RefKind.MANUAL:
        return _parse_manual(value)
    if kind is RefKind.CASE:
        if not _CASE.match(value):
            raise InvalidRef(f"not a case id: {value!r}")
        return Ref(value, kind)
    if kind in (RefKind.PROVISION, RefKind.UNIT, RefKind.LEGISLATION):
        parsed = _parse_legislation(value)
        if kind is RefKind.LEGISLATION or parsed.kind is RefKind.LEGISLATION:
            # The caller read this out of a provision record or a units[] entry,
            # so it knows the level the grammar could not settle. Take its word.
            return Ref(value, kind, instrument=parsed.instrument, root=parsed.root)
        if parsed.kind is not kind:
            raise InvalidRef(f"{value!r} is a {parsed.kind.value}, not a {kind.value}")
        return parsed
    raise InvalidRef(f"unsupported ref kind: {kind!r}")  # pragma: no cover


def _parse_manual(value: str) -> Ref:
    if not _CHUNK.match(value):
        raise InvalidRef(f"not a Manual ref: {value!r}")
    if "#" in value or "~" in value:
        # No page ref in the corpus carries either, and the chunker mints both.
        return Ref(value, RefKind.MANUAL_CHUNK)
    return Ref(value, RefKind.MANUAL)


def _parse_legislation(value: str) -> Ref:
    if not (_CITED_PROVISION.match(value) or _PROVISION_RECORD.match(value)):
        raise InvalidRef(f"not a legislation ref: {value!r}")
    instrument, _, address = value.partition("/")
    if not address:
        raise InvalidRef(f"legislation ref has no address: {value!r}")
    if not instrument_holds(value):
        raise InvalidRef(
            f"{instrument} cannot express the address {address!r}: {value!r}. "
            "This ref was constructed, not read — see IDENTIFIERS.md §1."
        )
    if _UNIT_TAIL.search(address):
        # `root` is the ref with the subdivision tail removed. For the ordinary
        # case that is the provision the unit sits in; for a paragraph of a
        # defined term it is the definition unit above it, which is what
        # upstream's own `parent_ref` says too.
        root = re.split(r"[(~]", value, maxsplit=1)[0]
        return Ref(value, RefKind.UNIT, instrument=instrument, root=root)
    if _PROVISION_ADDRESS.match(address):
        return Ref(value, RefKind.PROVISION, instrument=instrument)
    return Ref(value, RefKind.LEGISLATION, instrument=instrument)


def is_ref(value: str) -> bool:
    """`True` if `value` parses as an upstream ref. For filters, not for control
    flow that should have failed loudly."""
    try:
        parse_ref(value)
    except InvalidRef:
        return False
    return True


def instrument_holds(identifier: str) -> bool:
    """Can the instrument this ref names express the address it names?

    The two invariants of `IDENTIFIERS.md` §1, which are two independent
    readings of one fact:

    - **Kind.** An Act holds sections and Regulations hold regulations, so
      `TMR1995/s224` is impossible.
    - **Number.** The Act numbers its sections without dots and the Regulations
      number theirs with them, so `TMA1995/s4.7` is impossible.

    Unknown instruments pass, and so do Schedule addresses: a Schedule is
    neither a section nor a regulation, and an instrument whose numbering nobody
    has read cannot contradict anything. Mirrors upstream's
    `tmm_snapshot.citations.instrument_holds` deliberately — a second, subtly
    different reading of the same rule would agree with the first until it
    quietly did not.
    """
    instrument, _, address = identifier.partition("/")
    if not address or _SCHEDULE_ADDRESS.match(address):
        return True

    head = _ADDRESS_HEAD.match(address)
    if head is None or head.group(0) not in {"s", "r"}:
        # `front`, `pt17a/div8` and the Schedule forms are neither a section nor
        # a regulation, and both rules below are about the two kinds an
        # instrument divides its *body* into. Nothing here can contradict.
        return True

    expected = INSTRUMENT_KIND.get(instrument)
    if expected is not None and address[0] != expected:
        return False

    dotted = INSTRUMENT_DOTTED.get(instrument)
    if dotted is None or address[0] not in {"s", "r"}:
        return True
    return ("." in _NUMBER_ONLY.match(address[1:]).group(0)) is dotted


# ---------------------------------------------------------------------------
# IRIs — the single minter (IDENTIFIERS.md §2)
# ---------------------------------------------------------------------------

#: The one character of the ref grammar that cannot survive verbatim in an IRI.
#: `#` opens a fragment (RFC 3986 §3.5), so `<BASE>ref/TMM/Part26/6#3~2` names
#: the resource `<BASE>ref/TMM/Part26/6` and the fragment `3~2` — a different
#: subject, silently. 498 of the pinned corpus's 2,460 chunk refs carry one.
#: `~`, `(`, `)`, `.` and `-` are all legal in a path and are left alone, so the
#: no-percent-encoding rule of `IDENTIFIERS.md` §2 holds everywhere else.
#: See ADR-0023 and QUIRKS Q-17.
_HASH_ESCAPE = "%23"

PREFIXES: dict[str, str] = {
    "tmk": "ns/",
    "tmkr": "ref/",
    "tmkc": "concept/",
    "tmkp": "prop/",
    "tmka": "assertion/",
    "tmkg": "graph/",
}


def to_iri(ref: str | Ref, *, base: str | None = None) -> str:
    """Mint the IRI for an upstream ref. The only place this happens.

    Validates first: an IRI is only ever minted from a ref that parsed, so a
    malformed ref fails here rather than reaching a graph.
    """
    value = ref.value if isinstance(ref, Ref) else parse_ref(ref).value
    prefix = (base if base is not None else base_iri()) + PREFIXES["tmkr"]
    return prefix + value.replace("#", _HASH_ESCAPE)


def from_iri(iri: str, *, base: str | None = None) -> str:
    """Recover the upstream ref from an IRI. Inverse of `to_iri`."""
    prefix = (base if base is not None else base_iri()) + PREFIXES["tmkr"]
    if not iri.startswith(prefix):
        raise InvalidRef(f"not an IRI minted by this project: {iri!r}")
    value = iri[len(prefix) :].replace(_HASH_ESCAPE, "#")
    return parse_ref(value).value


def iri_for(prefix: str, local_name: str, *, base: str | None = None) -> str:
    """Mint an IRI for an identifier this repo allocated (not an upstream ref)."""
    if prefix not in PREFIXES:
        raise ValueError(f"unknown prefix {prefix!r}; known: {sorted(PREFIXES)}")
    return (base if base is not None else base_iri()) + PREFIXES[prefix] + local_name


# ---------------------------------------------------------------------------
# Identifiers this repo mints (IDENTIFIERS.md §3)
# ---------------------------------------------------------------------------

def normalise_value(value: str) -> str:
    """Normalise an extracted surface form for hashing.

    Mechanical only — NFKC, casefold, collapse internal whitespace, strip. It
    decides when two spans hash to one candidate, so it is deliberately blunt:
    anything cleverer (stemming, lemmatising, stripping articles) is a judgement
    about whether two surface forms mean the same thing, which is Stage 3's
    question and an expert's answer, not a hash function's. ADR-0024.
    """
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def candidate_id(
    source_ref: str | Ref,
    span_start: int,
    span_end: int,
    value: str,
) -> str:
    """The content-addressed id of a machine-generated candidate.

    `sha256(source_ref | span_start | span_end | normalised_value)`, first 16 hex
    (`IDENTIFIERS.md` §3, ADR-0020 confirmed by ADR-0021).

    **`method` is not in the hash, on purpose.** Three keyphrase extractors run
    over the same text (ADR-0019); hashing the method would mint three ids for
    one span and hide the cross-method agreement the ensemble exists to produce.
    The methods that found the span are a set field on the record — see
    `tm_knowledge.provenance`.
    """
    ref = source_ref.value if isinstance(source_ref, Ref) else parse_ref(source_ref).value
    if not isinstance(span_start, int) or not isinstance(span_end, int):
        raise TypeError("span offsets must be ints")
    if span_start < 0 or span_end < span_start:
        raise ValueError(f"nonsensical span [{span_start}, {span_end}]")
    payload = "|".join([ref, str(span_start), str(span_end), normalise_value(value)])
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"cand-{digest}"


class SequentialRegister:
    """The allocator for human-facing ids (`IDENTIFIERS.md` §3).

    A register file *is* the allocator: ids are allocated by appending, and a gap
    left by a withdrawn entry is never filled. The id is never derived from a
    label, because labels get revised and identifiers must not.
    """

    def __init__(self, path: str | Path, prefix: str, *, width: int = 4) -> None:
        self.path = Path(path)
        self.prefix = prefix
        self.width = width

    def entries(self) -> list[dict]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{self.path} is not a register (expected a JSON list)")
        return data

    def allocate(self, **fields: object) -> str:
        """Allocate the next id, append the entry, and return the id."""
        entries = self.entries()
        highest = 0
        for entry in entries:
            identifier = str(entry.get("id", ""))
            if not identifier.startswith(self.prefix + "-"):
                raise ValueError(
                    f"{self.path} holds {identifier!r}, which is not a {self.prefix} id. "
                    "One register, one prefix."
                )
            highest = max(highest, int(identifier.rsplit("-", 1)[1]))
        allocated = f"{self.prefix}-{highest + 1:0{self.width}d}"
        entries.append({"id": allocated, **fields})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
            encoding="utf-8",
        )
        return allocated

"""Read `authored/` into records, and refuse the ones that cannot say what they are.

The sibling of `stage0/goldset.py`, deliberately: same record types, same file
names, same "an unrecognised `.yaml` here is an error, not a file to skip". One
thing is different, and it is the whole reason this module exists rather than a
`root=` argument on `goldset.load`.

**A gold record is trusted because a person signed it. An authored record is
readable because it declares what it is.** So every record here carries an
`authored:` block — the envelope of `eval/schemas/authored-envelope.schema.json`
— and a record without one is not an authored record at all. It is an
unattributed legal assertion sitting in a directory, which is precisely the
laundering ADR-0079 rewrote rule 1 to prohibit.

**Refused, never skipped.** A record whose envelope does not validate is kept,
marked, and reported: `AuthoredSet.refused` names every one of them and
`tmk-harness` turns each into a defect. Dropping it silently would make a
malformed authored record indistinguishable from one that was never written,
and there is no later evidence that could tell the two apart.

**The record and its envelope are separated on read.** Every record-type schema
is `additionalProperties: false`, so a record carrying `authored:` cannot
validate against its own schema while the envelope is still attached. `record`
is therefore the record as the schema knows it and `envelope` is the block
beside it — which also means everything downstream that consumes gold records
consumes authored ones unchanged, and has to go out of its way to lose the
provenance rather than out of its way to keep it.

Nothing here decides whether a judgement is right. It decides whether a record
is in a state where a reviewer could tell.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.schemas import RECORD_TYPES, SchemaError, validator_for_file

__all__ = [
    "AUTHORED_DIR",
    "AUTHORED_FILES",
    "FILE_FOR",
    "ENVELOPE_KEY",
    "ENVELOPE_SCHEMA",
    "AuthoredRecord",
    "AuthoredSet",
    "MalformedAuthoredFile",
    "load",
    "validate_envelope",
]

AUTHORED_DIR = REPO_ROOT / "authored"

#: The key the envelope sits under, on the record and nowhere else.
ENVELOPE_KEY = "authored"

#: The envelope's schema, by filename. Resolved through `stage0.schemas` so the
#: cross-file `$ref`s into `common.schema.json` — the ones that make an
#: `evidence[].ref` a real upstream ref rather than any string — resolve the
#: same way they do for a gold record.
ENVELOPE_SCHEMA = "authored-envelope.schema.json"

#: Filename -> record type. **Identical to `goldset.GOLD_FILES`**, and derived
#: from it rather than restated, because ADR-0080 puts the same record types in
#: both stores and a name that drifted would put a record type in one store that
#: the other could not read.
AUTHORED_FILES: dict[str, str] = dict(goldset.GOLD_FILES)

#: Record type -> filename. Built from the map above so the two cannot diverge.
FILE_FOR: dict[str, str] = {value: key for key, value in AUTHORED_FILES.items()}

#: Files in `authored/` that are not records and are not mistakes.
#:
#: `definitions.yaml` is named in `authored/README.md` and is deliberately
#: **not** here: it has no schema and no id series, so the store cannot hold it
#: yet and reports it like any other unknown name. Inventing a record type in a
#: plumbing pass would be authoring the shape of a definition by accident.
NOT_RECORDS = frozenset({"README.md"})


class MalformedAuthoredFile(Exception):
    """An authored file that could not be read as a list of records."""


@dataclass(frozen=True, slots=True)
class AuthoredRecord:
    """One authored record, split from the envelope that says who wrote it."""

    record_type: str
    #: The record as its own schema knows it — the envelope removed.
    record: dict[str, Any]
    #: The `authored:` block, or None where the record carried none.
    envelope: dict[str, Any] | None
    source_file: Path
    position: int
    #: Why this record cannot be used, empty when it can. Populated by
    #: `validate_envelope` at load time; a non-empty tuple is what `refused`
    #: selects on and what the harness reports as a defect.
    envelope_errors: tuple[SchemaError, ...] = ()

    @property
    def record_id(self) -> str:
        return str(self.record.get("id") or f"<{self.record_type} with no id>")

    @property
    def sound(self) -> bool:
        return not self.envelope_errors

    @property
    def review_status(self) -> str:
        """What the record says about itself. `unknown` when it says nothing.

        Never defaulted to `unreviewed`: a record with no envelope has not
        claimed to be unreviewed, it has claimed nothing, and the difference is
        the one the harness has to be able to report.
        """
        if not isinstance(self.envelope, dict):
            return "unknown"
        return str(self.envelope.get("review_status") or "unknown")

    @property
    def authoring_basis(self) -> str:
        if not isinstance(self.envelope, dict):
            return "unknown"
        return str(self.envelope.get("authoring_basis") or "unknown")

    @property
    def authored_by(self) -> str | None:
        if not isinstance(self.envelope, dict):
            return None
        value = self.envelope.get("authored_by")
        return str(value) if value else None

    def evidence(self) -> tuple[dict[str, Any], ...]:
        if not isinstance(self.envelope, dict):
            return ()
        entries = self.envelope.get("evidence") or ()
        return tuple(entry for entry in entries if isinstance(entry, dict))


@dataclass(frozen=True)
class AuthoredSet:
    """Whatever `authored/` currently holds, keyed by record type.

    Shaped to answer `goldset.GoldSet`'s questions — `set[record_type]`,
    `count`, `total`, `all_records()` — so a caller that counts one store can
    count the other. It is deliberately *not* a subclass: ADR-0080 consequence 3
    forbids summing the two into one figure, and a type that could be passed
    where a `GoldSet` is expected is how that sum gets written by accident.
    """

    root: Path
    entries: tuple[AuthoredRecord, ...] = ()
    files: dict[str, Path] = field(default_factory=dict)
    #: (path, reason) for every file that could not be read at all.
    unreadable: tuple[tuple[Path, str], ...] = ()

    def of(self, record_type: str) -> tuple[AuthoredRecord, ...]:
        if record_type not in RECORD_TYPES:
            raise KeyError(f"unknown Stage 0 record type {record_type!r}")
        return tuple(e for e in self.entries if e.record_type == record_type)

    def __getitem__(self, record_type: str) -> tuple[dict[str, Any], ...]:
        """The bare records of one type, envelope removed — `GoldSet`'s shape.

        **Only the sound ones.** A record whose envelope does not validate has
        no usable provenance, and handing it to a graph builder would put an
        unattributable assertion in the graph. It is not lost: `refused` holds
        it and every caller that builds from this store reports the count.
        """
        return tuple(e.record for e in self.of(record_type) if e.sound)

    def count(self, record_type: str) -> int:
        return len(self[record_type])

    @property
    def total(self) -> int:
        """Sound records only, for the same reason `__getitem__` filters."""
        return sum(1 for entry in self.entries if entry.sound)

    @property
    def held(self) -> int:
        """Every record read, sound or not. What is on disk."""
        return len(self.entries)

    @property
    def refused(self) -> tuple[AuthoredRecord, ...]:
        return tuple(entry for entry in self.entries if not entry.sound)

    def all_records(self) -> Iterator[tuple[str, dict[str, Any]]]:
        """(record type, record) for every sound record, in a stable order."""
        for record_type in sorted({entry.record_type for entry in self.entries}):
            for record in self[record_type]:
                yield record_type, record

    def all_entries(self) -> Iterator[AuthoredRecord]:
        """Every entry, sound or not, in the order the files gave them."""
        yield from self.entries

    def identifiers(self) -> dict[str, AuthoredRecord]:
        """id -> entry, for every entry carrying a string id. Last wins.

        A duplicate within the store is caught by the harness reading
        `all_entries()`; this is for the cheaper question of whether a given id
        is in this store at all.
        """
        return {
            str(entry.record["id"]): entry
            for entry in self.entries
            if isinstance(entry.record.get("id"), str)
        }

    def by_basis(self) -> dict[str, int]:
        """How many sound records rest on each `authoring_basis`.

        The count `general_knowledge` is reported from, everywhere. A store
        filling with unevidenced records is the quiet failure ADR-0079 names,
        and it is only visible as a proportion.
        """
        counts: dict[str, int] = {}
        for entry in self.entries:
            if entry.sound:
                counts[entry.authoring_basis] = counts.get(entry.authoring_basis, 0) + 1
        return counts


# ---------------------------------------------------------------------------
# Validation of the envelope itself
# ---------------------------------------------------------------------------


def validate_envelope(
    envelope: Any, *, record_id: str | None = None
) -> list[SchemaError]:
    """Check one `authored:` block against the envelope schema.

    An absent envelope is the first error rather than an exception: the caller
    is a loader building a report, and a directory of records with no envelopes
    should produce a list of that many findings, not stop on the first.
    """
    if envelope is None:
        return [
            SchemaError(
                record_id=record_id,
                path=ENVELOPE_KEY,
                message=(
                    "no `authored:` block. Every record in authored/ carries one — "
                    "it is what separates a machine's judgement from an expert's "
                    "(ADR-0079 guard 1)"
                ),
            )
        ]
    if not isinstance(envelope, dict):
        return [
            SchemaError(
                record_id=record_id,
                path=ENVELOPE_KEY,
                message=(
                    f"`authored:` is a {type(envelope).__name__}, not a mapping"
                ),
            )
        ]

    validator = validator_for_file(ENVELOPE_SCHEMA)
    return [
        SchemaError(
            record_id=record_id,
            path="/".join([ENVELOPE_KEY, *(str(part) for part in error.path)]),
            message=error.message,
        )
        for error in sorted(validator.iter_errors(envelope), key=lambda e: list(e.path))
    ]


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------


def _read_records(path: Path) -> tuple[dict[str, Any], ...]:
    """The same reader `goldset` uses, held to the same shape: a list of maps."""
    raw = path.read_text(encoding="utf-8")
    try:
        document = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        raise MalformedAuthoredFile(f"not valid YAML: {error}") from error
    if document is None:
        return ()
    if not isinstance(document, list):
        raise MalformedAuthoredFile(
            f"expected a YAML list of records, got {type(document).__name__}"
        )
    for position, record in enumerate(document):
        if not isinstance(record, dict):
            raise MalformedAuthoredFile(
                f"record {position} is a {type(record).__name__}, not a mapping"
            )
    return tuple(document)


def _split(
    raw: dict[str, Any], record_type: str, path: Path, position: int
) -> AuthoredRecord:
    """One raw record into (record, envelope), validated.

    The envelope is *removed* from the record rather than copied out of it. Every
    record-type schema is `additionalProperties: false`, so a record still
    carrying `authored:` would fail its own schema — and the resulting defect
    would say "unknown field", which is a true statement about the wrong
    problem.
    """
    record = {key: value for key, value in raw.items() if key != ENVELOPE_KEY}
    envelope = raw.get(ENVELOPE_KEY)
    identifier = record.get("id")
    errors = validate_envelope(
        envelope, record_id=str(identifier) if isinstance(identifier, str) else None
    )
    return AuthoredRecord(
        record_type=record_type,
        record=record,
        envelope=envelope if isinstance(envelope, dict) else None,
        source_file=path,
        position=position,
        envelope_errors=tuple(errors),
    )


def load(root: Path | None = None) -> AuthoredSet:
    """Load the authored store. Never raises for an empty or absent directory.

    An absent `authored/` is the ordinary state of a repo that has authored
    nothing yet, and it is not a finding. A *misnamed* file in it is, for
    `goldset`'s reason: a file quietly ignored because its name was misspelt is
    a set of judgements that silently did not count (rule 6).
    """
    root = root or AUTHORED_DIR
    if not root.exists():
        return AuthoredSet(root=root)

    entries: list[AuthoredRecord] = []
    files: dict[str, Path] = {}
    unreadable: list[tuple[Path, str]] = []

    for path in sorted(root.iterdir()):
        if path.is_dir() or path.name in NOT_RECORDS or path.name.startswith("."):
            continue
        record_type = AUTHORED_FILES.get(path.name)
        if record_type is None:
            unreadable.append(
                (
                    path,
                    "not an authored file name. Expected one of: "
                    + ", ".join(sorted(AUTHORED_FILES)),
                )
            )
            continue
        try:
            found = _read_records(path)
        except MalformedAuthoredFile as error:
            unreadable.append((path, str(error)))
            continue
        files[record_type] = path
        for position, raw in enumerate(found):
            entries.append(_split(raw, record_type, path, position))

    order = {name: index for index, name in enumerate(goldset.GOLD_FILES.values())}
    entries.sort(key=lambda e: (order.get(e.record_type, 99), e.position))
    return AuthoredSet(
        root=root,
        entries=tuple(entries),
        files=files,
        unreadable=tuple(unreadable),
    )


def strip(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Records with the envelope removed, for a caller holding raw YAML.

    Only for code that read an authored file some other way — `load` already
    splits. Kept public because the alternative is that code popping the key
    itself, and there is exactly one name for that key.
    """
    return [
        {key: value for key, value in record.items() if key != ENVELOPE_KEY}
        for record in records
    ]

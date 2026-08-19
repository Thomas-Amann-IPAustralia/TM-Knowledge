"""Read `eval/gold/` into records, and say loudly when it cannot.

One file per record type, named by the map below. The names come from
`eval/gold/README.md`; the two the README did not name — competency questions
and prohibited uses — follow the same pattern.

**An unrecognised `.yaml` file here is an error, not a file to skip.** A gold set
is the measurement standard for the whole programme; a file quietly ignored
because its name was misspelt is a set of expert judgements that silently did
not count. Rule 6.

Nothing in this module validates a record. It reads YAML into dictionaries and
reports what it could not read; `harness.py` decides whether what it read is
sound.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0.schemas import RECORD_TYPES

GOLD_DIR = REPO_ROOT / "eval" / "gold"

#: Filename -> record type. One file per type, so a diff of a record is a diff
#: of one block in one file (`eval/gold/README.md`).
GOLD_FILES: dict[str, str] = {
    "competency-questions.yaml": "competency_question",
    "entities.yaml": "gold_entity",
    "concepts.yaml": "gold_concept",
    "relationships.yaml": "gold_relationship",
    "search-questions.yaml": "gold_search_question",
    "retrieval-questions.yaml": "gold_retrieval_question",
    "reasoning-expected.yaml": "reasoning_expectation",
    "prohibited-uses.yaml": "prohibited_use",
}

#: Record type -> filename. Built from the map above so the two cannot diverge.
FILE_FOR: dict[str, str] = {value: key for key, value in GOLD_FILES.items()}

#: Files in `eval/gold/` that are not records and are not mistakes.
NOT_RECORDS = frozenset({"README.md", "retired-ids.yaml"})

#: The ledger of ids withdrawn from service. Optional — its absence means
#: nothing has been withdrawn, which is the normal state. Its purpose is
#: non-reuse: `IDENTIFIERS.md` §3 allocates human-facing ids by appending and
#: never fills a gap left by a withdrawal, and this is where the gaps are
#: recorded so a later allocator cannot walk into one.
RETIRED_IDS_FILE = "retired-ids.yaml"


class MalformedGoldFile(Exception):
    """A gold file that could not be read as a list of records."""


@dataclass(frozen=True)
class GoldSet:
    """Whatever `eval/gold/` currently holds, keyed by record type.

    A record type with no file is an empty tuple, not an error: an absent
    deliverable is the expected state of this repo today, and the completeness
    gate is what has an opinion about it.
    """

    root: Path
    records: dict[str, tuple[dict[str, Any], ...]]
    files: dict[str, Path]
    retired_ids: dict[str, dict[str, Any]] = field(default_factory=dict)
    #: (path, reason) for every file that could not be read at all.
    unreadable: tuple[tuple[Path, str], ...] = ()

    def __getitem__(self, record_type: str) -> tuple[dict[str, Any], ...]:
        if record_type not in RECORD_TYPES:
            raise KeyError(f"unknown Stage 0 record type {record_type!r}")
        return self.records.get(record_type, ())

    def count(self, record_type: str) -> int:
        return len(self[record_type])

    @property
    def total(self) -> int:
        return sum(len(records) for records in self.records.values())

    def all_records(self):
        """(record type, record) for every record held, in a stable order."""
        for record_type in sorted(self.records):
            for record in self.records[record_type]:
                yield record_type, record


def _read_records(path: Path) -> tuple[dict[str, Any], ...]:
    raw = path.read_text(encoding="utf-8")
    try:
        document = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        raise MalformedGoldFile(f"not valid YAML: {error}") from error
    if document is None:
        return ()
    if not isinstance(document, list):
        raise MalformedGoldFile(
            f"expected a YAML list of records, got {type(document).__name__}"
        )
    for position, record in enumerate(document):
        if not isinstance(record, dict):
            raise MalformedGoldFile(
                f"record {position} is a {type(record).__name__}, not a mapping"
            )
    return tuple(document)


def _read_retired(path: Path) -> dict[str, dict[str, Any]]:
    entries = _read_records(path)
    retired: dict[str, dict[str, Any]] = {}
    for entry in entries:
        identifier = entry.get("id")
        if not isinstance(identifier, str):
            raise MalformedGoldFile("every retired-ids entry needs a string `id`")
        retired[identifier] = entry
    return retired


def load(root: Path | None = None) -> GoldSet:
    """Load the gold set. Never raises for an empty or absent directory."""
    root = root or GOLD_DIR
    records: dict[str, tuple[dict[str, Any], ...]] = {}
    files: dict[str, Path] = {}
    retired: dict[str, dict[str, Any]] = {}
    unreadable: list[tuple[Path, str]] = []

    if not root.exists():
        return GoldSet(root=root, records=records, files=files)

    for path in sorted(root.iterdir()):
        if path.is_dir() or path.name in NOT_RECORDS:
            if path.name == RETIRED_IDS_FILE:
                try:
                    retired = _read_retired(path)
                except MalformedGoldFile as error:
                    unreadable.append((path, str(error)))
            continue
        record_type = GOLD_FILES.get(path.name)
        if record_type is None:
            unreadable.append(
                (
                    path,
                    "not a gold file name. Expected one of: "
                    + ", ".join(sorted(GOLD_FILES)),
                )
            )
            continue
        try:
            records[record_type] = _read_records(path)
        except MalformedGoldFile as error:
            unreadable.append((path, str(error)))
            continue
        files[record_type] = path

    return GoldSet(
        root=root,
        records=records,
        files=files,
        retired_ids=retired,
        unreadable=tuple(unreadable),
    )

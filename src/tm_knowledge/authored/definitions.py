"""Definitions of concepts — machine-written, unreviewed (the review response, F06).

The owner lifted the deferral on definitions on 2026-10-17 (CHAT-0078, ADR-0136). Two
reviews had named their absence: the expert asked for them first, and the ontology was
a vocabulary of names with sources and no meanings.

A definition is **its own record**, in `authored/definitions.yaml`, never a field on
the concept, for the reason a concept's kind is its own record (ADR-0071): a signed
concept cannot be edited, and writing a definition into it would put machine content
inside a signature (CLAUDE.md rule 4). It follows that approving a label approves no
definition. One definition per concept; ids are `GD-`, one sequence across the project
(`docs/IDENTIFIERS.md` §3).

Each carries the authoring envelope like any machine-written record, and says where its
words come from (`basis`), because a definition is where practice and law are easiest to
blur (CLAUDE.md rule 5):

- `statutory_definition` — the Act's or Regulations' own definition, quoted verbatim
  (preferred wherever one exists: CHAT-0045);
- `statutory_provision` — written from a provision that says what the thing is or does;
- `manual` — written from the Manual's own explanation, which states practice, not law.

A concept whose sources do not define it gets no record: "If the corpus does not support
it, the record says so or is not written" (ADR-0079 guard 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.authored import store as authored_store
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.schemas import SchemaError, validator_for_file

__all__ = ["DEFINITIONS_FILE", "SCHEMA", "BASES", "Definition", "Definitions", "load"]

DEFINITIONS_FILE = "definitions.yaml"
SCHEMA = "definition.schema.json"

#: Where a definition's words come from, and which refs may carry them.
BASES = {
    "statutory_definition": ("TMA1995/", "TMR1995/"),
    "statutory_provision": ("TMA1995/", "TMR1995/"),
    "manual": ("TMM/",),
}


@dataclass(frozen=True)
class Definition:
    record: dict[str, Any]
    envelope: dict[str, Any] | None
    errors: tuple[SchemaError | str, ...] = ()

    @property
    def id(self) -> str:
        return str(self.record.get("id") or "<definition with no id>")

    @property
    def concept(self) -> str:
        return str(self.record.get("concept") or "")

    @property
    def sound(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class Definitions:
    entries: tuple[Definition, ...] = ()
    path: Path | None = None

    @property
    def sound(self) -> tuple[Definition, ...]:
        return tuple(entry for entry in self.entries if entry.sound)

    @property
    def refused(self) -> tuple[Definition, ...]:
        return tuple(entry for entry in self.entries if not entry.sound)

    def by_concept(self) -> dict[str, Definition]:
        return {entry.concept: entry for entry in self.sound}


def _check(record: dict[str, Any], envelope: Any, concepts: set[str]) -> list[SchemaError | str]:
    """Shape, envelope, and what a schema cannot see."""
    errors: list[SchemaError | str] = []
    record_id = str(record.get("id") or "")
    for error in validator_for_file(SCHEMA).iter_errors(record):
        errors.append(SchemaError(record_id, "/".join(str(p) for p in error.absolute_path), error.message))
    if envelope is None:
        errors.append("no `authored:` envelope — a definition is machine-written and must say so")
    else:
        errors.extend(authored_store.validate_envelope(envelope, record_id=record_id))
    if errors:
        return errors

    if record["concept"] not in concepts:
        errors.append(f"defines {record['concept']}, which is no concept in either store")
    refs = [str(item.get("ref")) for item in envelope.get("evidence") or ()]
    if not refs:
        errors.append("rests on no evidence — a definition the corpus does not support is not written")
    if record["source_ref"] not in refs:
        errors.append(f"source_ref {record['source_ref']} is not among the evidence it quotes")
    allowed = BASES[record["basis"]]
    if not any(ref.startswith(allowed) for ref in refs):
        errors.append(f"basis {record['basis']} but no evidence is from {' or '.join(allowed)}")
    if record["basis"] == "statutory_definition" and not all(ref.startswith(allowed) for ref in refs):
        errors.append("a statutory definition quotes the instrument and nothing else")
    return errors


def load(
    root: Path | None = None,
    gold: goldset.GoldSet | None = None,
    authored: authored_store.AuthoredSet | None = None,
) -> Definitions:
    """Every definition, each checked. Refused, never skipped, like any authored record."""
    root = root or authored_store.AUTHORED_DIR
    path = root / DEFINITIONS_FILE
    if not path.exists():
        return Definitions(path=path)
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load(root)
    concepts = {str(r["id"]) for r in gold["gold_concept"]} | {
        entry.record_id for entry in authored.of("gold_concept") if entry.sound
    }
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(document, list):
        raise authored_store.MalformedAuthoredFile(f"{path.name}: expected a list of definitions")
    entries = []
    seen_ids: set[str] = set()
    defined: set[str] = set()
    for raw in document:
        if not isinstance(raw, dict):
            raise authored_store.MalformedAuthoredFile(f"{path.name}: a definition is not a mapping")
        record = {k: v for k, v in raw.items() if k != authored_store.ENVELOPE_KEY}
        envelope = raw.get(authored_store.ENVELOPE_KEY)
        errors = _check(record, envelope, concepts)
        if str(record.get("id")) in seen_ids:
            errors.append("id used twice in definitions.yaml")
        if str(record.get("concept")) in defined:
            errors.append(f"a second definition of {record.get('concept')}; one concept, one definition")
        seen_ids.add(str(record.get("id")))
        defined.add(str(record.get("concept")))
        entries.append(Definition(record=record, envelope=envelope, errors=tuple(errors)))
    return Definitions(entries=tuple(entries), path=path)

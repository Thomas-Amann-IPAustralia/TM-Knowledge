"""Corrections to signed records — machine-written, on the owner's instruction.

The owner ruled on 2026-10-08 that no expert signs anything until the ontology ships
to a group of trade marks examiners, and that known defects in signed records are
corrected now rather than queued for an expert (ADR-0120, ADR-0121 on D2). Two rules
stand in the way of doing that by editing `eval/gold/`, and both are kept:

- `eval/gold/` is frozen as the 190 records a person signed — the only independent
  yardstick the project has (ADR-0080). An edit there is gone for good as a yardstick.
- A change written inside a signature would be machine content wearing a person's name
  (CLAUDE.md rule 4) — laundering.

So a correction is its own record, in `authored/corrections.yaml`, carrying the
authoring envelope like any machine-written record (ADR-0122). It names the signed
record it corrects and the owner's ruling it acts on, and it changes what *serves*:

- **a concept** — values are removed from, or added to, its list fields. A removed value
  stays in `eval/gold/` and is stated nowhere that serves; an added value is stated in
  the authored graph, never the approved one.
- **an entity mention** — a single field is set (`resolves_to`).
- **a relationship** — replaced by an authored relationship carrying the corrected
  triple. The signed record stays as history, flagged; its direct triple stops serving.

`served_gold()` is the corrected view, for recognition, search and the explorer. The
graph build does not use it for the approved graph — it applies removals and
replacements there and states additions in the authored graph — because the approved
graph must never hold a value no person signed. Nothing in the harness, the expert pack
or the transcription path reads a corrected view: they measure and move signed records,
and those are exactly as signed.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.authored import store as authored_store
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.schemas import SchemaError, validator_for_file

__all__ = [
    "CORRECTIONS_FILE",
    "SCHEMA",
    "Correction",
    "Corrections",
    "load",
    "served_gold",
    "in_force_gold",
    "LIST_FIELDS",
]

CORRECTIONS_FILE = "corrections.yaml"
SCHEMA = "correction.schema.json"

#: The list fields a correction may add to or remove from on a concept.
LIST_FIELDS = ("alt_labels", "not_labels", "legislative_basis", "definition_sources", "related")


@dataclass(frozen=True)
class Correction:
    record: dict[str, Any]
    envelope: dict[str, Any] | None
    errors: tuple[SchemaError | str, ...] = ()

    @property
    def id(self) -> str:
        return str(self.record.get("id") or "<correction with no id>")

    @property
    def target(self) -> str:
        return str(self.record.get("corrects") or "")

    @property
    def sound(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class Corrections:
    entries: tuple[Correction, ...] = ()
    path: Path | None = None

    @property
    def sound(self) -> tuple[Correction, ...]:
        return tuple(entry for entry in self.entries if entry.sound)

    @property
    def refused(self) -> tuple[Correction, ...]:
        return tuple(entry for entry in self.entries if not entry.sound)

    def for_target(self, identifier: str) -> tuple[Correction, ...]:
        return tuple(entry for entry in self.sound if entry.target == identifier)

    def targets(self) -> dict[str, tuple[str, ...]]:
        """signed id -> the ids of the sound corrections to it, in file order."""
        out: dict[str, list[str]] = {}
        for entry in self.sound:
            out.setdefault(entry.target, []).append(entry.id)
        return {key: tuple(value) for key, value in out.items()}

    def replacements(self) -> dict[str, str]:
        """signed relationship id -> the authored relationship serving in its place."""
        return {
            entry.target: str(entry.record["replaced_by"])
            for entry in self.sound
            if entry.record.get("replaced_by")
        }


def _check(
    record: dict[str, Any],
    envelope: Any,
    gold: goldset.GoldSet,
    authored: authored_store.AuthoredSet,
) -> list[SchemaError | str]:
    """Shape, envelope, and the facts a schema cannot see."""
    errors: list[SchemaError | str] = []
    record_id = str(record.get("id") or "")
    for error in validator_for_file(SCHEMA).iter_errors(record):
        errors.append(SchemaError(record_id, "/".join(str(p) for p in error.absolute_path), error.message))
    if envelope is None:
        errors.append("no `authored:` envelope — a correction is machine-written and must say so")
    else:
        errors.extend(authored_store.validate_envelope(envelope, record_id=record_id))
    if errors:
        return errors

    signed = {str(r.get("id")): (t, r) for t, r in gold.all_records()}
    target = str(record["corrects"])
    if target not in signed:
        return [f"corrects {target}, which is not a signed record in eval/gold/"]
    record_type, signed_record = signed[target]
    if record_type != record["record_type"]:
        errors.append(f"record_type {record['record_type']} but {target} is a {record_type}")
    if record_type == "gold_concept":
        for name, values in (record.get("remove") or {}).items():
            present = set(signed_record.get(name) or ())
            for value in values:
                if value not in present:
                    errors.append(f"removes {name} {value!r}, which {target} does not carry")
        if record.get("replaced_by") or record.get("set"):
            errors.append("a concept is patched with add/remove only")
    elif record_type == "gold_entity":
        if record.get("add") or record.get("remove") or record.get("replaced_by"):
            errors.append("an entity mention is corrected with `set` only")
        if not record.get("set"):
            errors.append("an entity correction sets nothing")
    elif record_type == "gold_relationship":
        replacement = record.get("replaced_by")
        if not replacement:
            errors.append("a relationship is corrected by naming its replacement in `replaced_by`")
        else:
            held = {e.record_id: e for e in authored.of("gold_relationship") if e.sound}
            entry = held.get(str(replacement))
            if entry is None:
                errors.append(f"replaced_by {replacement}, which is not a sound authored relationship")
            elif entry.record.get("source_ref") != signed_record.get("source_ref"):
                errors.append(
                    f"replacement {replacement} cites {entry.record.get('source_ref')}, but "
                    f"{target} rests on {signed_record.get('source_ref')} — a correction "
                    "re-reads the same sentence, it does not find a new one"
                )
        if record.get("add") or record.get("remove") or record.get("set"):
            errors.append("a relationship is corrected by replacement only")
    return errors


def load(
    root: Path | None = None,
    gold: goldset.GoldSet | None = None,
    authored: authored_store.AuthoredSet | None = None,
) -> Corrections:
    """Every correction, each checked. Refused, never skipped, like any authored record."""
    root = root or authored_store.AUTHORED_DIR
    path = root / CORRECTIONS_FILE
    if not path.exists():
        return Corrections(path=path)
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load(root)
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(document, list):
        raise authored_store.MalformedAuthoredFile(f"{path.name}: expected a list of corrections")
    entries = []
    seen: set[str] = set()
    for raw in document:
        if not isinstance(raw, dict):
            raise authored_store.MalformedAuthoredFile(f"{path.name}: a correction is not a mapping")
        record = {k: v for k, v in raw.items() if k != authored_store.ENVELOPE_KEY}
        envelope = raw.get(authored_store.ENVELOPE_KEY)
        errors = _check(record, envelope, gold, authored)
        if str(record.get("id")) in seen:
            errors.append("id used twice in corrections.yaml")
        seen.add(str(record.get("id")))
        entries.append(Correction(record=record, envelope=envelope, errors=tuple(errors)))
    return Corrections(entries=tuple(entries), path=path)


def _patched(record: dict[str, Any], corrections: tuple[Correction, ...], *, additions: bool) -> dict[str, Any]:
    out = copy.deepcopy(record)
    for correction in corrections:
        for name, values in (correction.record.get("remove") or {}).items():
            out[name] = [v for v in (out.get(name) or []) if v not in set(values)]
        if additions:
            for name, values in (correction.record.get("add") or {}).items():
                current = list(out.get(name) or [])
                current += [v for v in values if v not in current]
                out[name] = current
        for name, value in (correction.record.get("set") or {}).items():
            if additions:
                out[name] = value
    return out


def _view(gold: goldset.GoldSet, corrections: Corrections, *, additions: bool) -> goldset.GoldSet:
    replaced = set(corrections.replacements())
    records: dict[str, tuple[dict[str, Any], ...]] = {}
    for record_type, rows in gold.records.items():
        out = []
        for record in rows:
            identifier = str(record.get("id"))
            if record_type == "gold_relationship" and identifier in replaced and additions:
                continue  # the authored replacement serves; the signed record is history
            mine = corrections.for_target(identifier)
            out.append(_patched(record, mine, additions=additions) if mine else record)
        records[record_type] = tuple(out)
    return goldset.GoldSet(
        root=gold.root, records=records, files=dict(gold.files),
        retired_ids=dict(gold.retired_ids), unreadable=gold.unreadable,
    )


def served_gold(gold: goldset.GoldSet | None = None, corrections: Corrections | None = None) -> goldset.GoldSet:
    """The signed records as they serve: every correction applied.

    For recognition, search, the explorer and the workbench — the surfaces that show an
    examiner what the ontology says. **Never for the harness, the expert pack or a
    measurement**: those read signed records, and these are not quite that any more.
    """
    gold = gold if gold is not None else goldset.load()
    corrections = corrections if corrections is not None else load(gold=gold)
    return _view(gold, corrections, additions=True)


def in_force_gold(gold: goldset.GoldSet, corrections: Corrections) -> goldset.GoldSet:
    """The signed records with withdrawals applied and nothing added — what the
    approved graph states. A replaced relationship stays (as history); the graph
    build suppresses its direct triple."""
    return _view(gold, corrections, additions=False)


@dataclass
class CorrectionIndex:
    """For a surface that needs to say *which* signed records were corrected."""

    by_target: dict[str, tuple[str, ...]] = field(default_factory=dict)

    @classmethod
    def of(cls, corrections: Corrections) -> "CorrectionIndex":
        return cls(by_target=corrections.targets())

    def corrected(self, identifier: str) -> tuple[str, ...]:
        return self.by_target.get(identifier, ())

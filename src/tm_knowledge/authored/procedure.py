"""Structured legal tests and process templates — machine-written, unreviewed (A04, A02).

The second review response's Package 4 starts the customer slice with two record types
the concept graph cannot hold (ADR-0142):

- **a legal test** (`GL-`, `authored/legal-tests.yaml`): one provision read as who acts,
  the conditions with AND and OR, the effect and what kind it is (an obligation, a
  discretion, a bar), the exceptions with their own effects, the evidence the Manual says
  bears on a condition, and the routes for answering it. A condition marked `evaluative`
  is a person's assessment and is never computed;
- **a process template** (`GP-`, `authored/processes.yaml`): the steps of one bounded
  procedure, the transitions between them with their conditions, and the deadline rules,
  explained and never computed; kept apart from any matter's history.

Both are their own records, as definitions are, with a reader of their own. Every element
quotes its exact unit or passage, and every quote is in the envelope's evidence, so the
harness checks each one lands (ADR-0045). ADR-0009 already allows this structure: it
defers LegalRuleML and executed defeasibility, not decision tables for bounded logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

from tm_knowledge.authored import store as authored_store
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.schemas import SchemaError, validator_for_file

__all__ = ["TESTS_FILE", "PROCESSES_FILE", "Record", "Records", "load_tests", "load_processes", "leaves", "quoted"]

TESTS_FILE = "legal-tests.yaml"
PROCESSES_FILE = "processes.yaml"


@dataclass(frozen=True)
class Record:
    record: dict[str, Any]
    envelope: dict[str, Any] | None
    errors: tuple[SchemaError | str, ...] = ()

    @property
    def id(self) -> str:
        return str(self.record.get("id") or "<record with no id>")

    @property
    def sound(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class Records:
    entries: tuple[Record, ...] = ()
    path: Path | None = None

    @property
    def sound(self) -> tuple[Record, ...]:
        return tuple(entry for entry in self.entries if entry.sound)

    @property
    def refused(self) -> tuple[Record, ...]:
        return tuple(entry for entry in self.entries if not entry.sound)

    def by_id(self) -> dict[str, Record]:
        return {entry.id: entry for entry in self.sound}


def quoted(node: Any) -> Iterator[tuple[str, str]]:
    """Every (ref, quote) an element of a record states, in document order."""
    if isinstance(node, dict):
        if isinstance(node.get("ref"), str) and isinstance(node.get("quote"), str):
            yield node["ref"], node["quote"]
        for key, value in node.items():
            if key != authored_store.ENVELOPE_KEY:
                yield from quoted(value)
    elif isinstance(node, list):
        for value in node:
            yield from quoted(value)


def leaves(node: Any) -> Iterator[dict[str, Any]]:
    """The leaf conditions of a condition tree."""
    if not isinstance(node, dict):
        return
    if "all" in node or "any" in node:
        for child in node.get("all") or node.get("any") or ():
            yield from leaves(child)
    else:
        yield node


def _ids(node: Any) -> Iterator[str]:
    if isinstance(node, dict):
        if isinstance(node.get("id"), str) and not str(node["id"]).startswith(("GL-", "GP-")):
            yield node["id"]
        for key, value in node.items():
            if key != authored_store.ENVELOPE_KEY:
                yield from _ids(value)
    elif isinstance(node, list):
        for value in node:
            yield from _ids(value)


def _concepts(gold: goldset.GoldSet, authored: authored_store.AuthoredSet) -> set[str]:
    return {str(r["id"]) for r in gold["gold_concept"]} | {
        e.record_id for e in authored.of("gold_concept") if e.sound}


def _common(record: dict[str, Any], envelope: Any, schema: str, concepts: set[str]) -> list[SchemaError | str]:
    errors: list[SchemaError | str] = []
    record_id = str(record.get("id") or "")
    for error in validator_for_file(schema).iter_errors(record):
        errors.append(SchemaError(record_id, "/".join(str(p) for p in error.absolute_path), error.message))
    if envelope is None:
        return errors + ["no `authored:` envelope — a machine-written record must say so"]
    errors.extend(authored_store.validate_envelope(envelope, record_id=record_id))
    if errors:
        return errors
    evidence = {(str(i.get("ref")), str(i.get("quote"))) for i in envelope.get("evidence") or ()}
    for ref, quote in quoted(record):
        if (ref, quote) not in evidence:
            errors.append(f"quotes {quote[:60]!r} from {ref}, which is not among the evidence it carries")
    seen: set[str] = set()
    for element in _ids(record):
        if element in seen:
            errors.append(f"element id {element!r} used twice")
        seen.add(element)
    named = [record.get("ground")] if record.get("ground") else []
    named += [c for leaf in _all_leaves(record) for c in leaf.get("concepts") or ()]
    named += [c for step in record.get("steps") or () for c in step.get("concepts") or ()]
    errors.extend(f"names {c}, which is no concept in either store" for c in named if c not in concepts)
    return errors


def _all_leaves(record: dict[str, Any]) -> list[dict[str, Any]]:
    out = list(leaves(record.get("condition")))
    for exception in record.get("exceptions") or ():
        out += list(leaves(exception.get("condition")))
    return out


def _test_errors(record: dict[str, Any]) -> list[str]:
    errors = []
    conditions = {leaf["id"] for leaf in _all_leaves(record) if "id" in leaf}
    for requirement in record.get("evidence_requirements") or ():
        errors += [f"evidence requirement {requirement['id']} is for {c}, which is no condition here"
                   for c in requirement["for"] if c not in conditions]
    exceptions = {e["id"] for e in record.get("exceptions") or ()}
    errors += [f"route {r['id']} names exception {r['exception']}, which is not here"
               for r in record.get("routes") or () if r.get("exception") and r["exception"] not in exceptions]
    if not str(record.get("provision", "")).startswith(("TMA1995/", "TMR1995/")):
        errors.append("a legal test is read from the Act or the Regulations")
    return errors


def _process_errors(record: dict[str, Any]) -> list[str]:
    steps = {s["id"] for s in record.get("steps") or ()}
    errors = [f"transition {t['from']} → {t['to']} names a step that is not here"
              for t in record.get("transitions") or () if t["from"] not in steps or t["to"] not in steps]
    errors += [f"deadline {d['id']} runs from {s}, which is no step here"
               for d in record.get("deadlines") or () for s in d["from"] if s not in steps]
    return errors


def _load(filename: str, schema: str, extra, root: Path | None, gold: goldset.GoldSet | None,
          authored: authored_store.AuthoredSet | None) -> Records:
    root = root or authored_store.AUTHORED_DIR
    path = root / filename
    if not path.exists():
        return Records(path=path)
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load(root)
    concepts = _concepts(gold, authored)
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(document, list):
        raise authored_store.MalformedAuthoredFile(f"{path.name}: expected a list of records")
    entries, seen = [], set()
    for raw in document:
        if not isinstance(raw, dict):
            raise authored_store.MalformedAuthoredFile(f"{path.name}: a record is not a mapping")
        record = {k: v for k, v in raw.items() if k != authored_store.ENVELOPE_KEY}
        envelope = raw.get(authored_store.ENVELOPE_KEY)
        errors = _common(record, envelope, schema, concepts)
        if not errors:
            errors += extra(record)
        if str(record.get("id")) in seen:
            errors.append(f"id used twice in {path.name}")
        seen.add(str(record.get("id")))
        entries.append(Record(record=record, envelope=envelope, errors=tuple(errors)))
    return Records(entries=tuple(entries), path=path)


def load_tests(root: Path | None = None, gold: goldset.GoldSet | None = None,
               authored: authored_store.AuthoredSet | None = None) -> Records:
    """Every legal test, each checked. Refused, never skipped (ADR-0089)."""
    return _load(TESTS_FILE, "legal-test.schema.json", _test_errors, root, gold, authored)


def load_processes(root: Path | None = None, gold: goldset.GoldSet | None = None,
                   authored: authored_store.AuthoredSet | None = None) -> Records:
    """Every process template, each checked. A step that continues in another template
    must name one in the same file (GP-0002's report continues in GP-0001)."""
    found = _load(PROCESSES_FILE, "process.schema.json", _process_errors, root, gold, authored)
    ids = {entry.id for entry in found.entries}
    entries = []
    for entry in found.entries:
        missing = [f"step {s['id']} continues in {s['continues_in']}, which is no template here"
                   for s in entry.record.get("steps") or () if isinstance(s, dict)
                   and s.get("continues_in") and (s["continues_in"] not in ids or s["continues_in"] == entry.id)]
        entries.append(Record(record=entry.record, envelope=entry.envelope, errors=entry.errors + tuple(missing)))
    return Records(entries=tuple(entries), path=found.path)

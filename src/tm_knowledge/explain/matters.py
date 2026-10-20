"""Fictional matters (`scenarios/matters.yaml`), each checked against what it names.

A matter is a fixture, not knowledge: it never enters the graph, a measurement or an
answer to an examiner. Every one says `fictional: true` (the schema allows nothing else)
until the owner allows real case data (CLAUDE.md §3a, ADR-0138).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.authored import procedure
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0.schemas import validator_for_file

__all__ = ["MATTERS_PATH", "Matter", "load"]

MATTERS_PATH = REPO_ROOT / "scenarios" / "matters.yaml"


@dataclass(frozen=True)
class Matter:
    record: dict[str, Any]
    errors: tuple[str, ...] = ()

    @property
    def id(self) -> str:
        return str(self.record.get("id"))


def _check(record: dict[str, Any], tests: dict[str, Any], steps: set[str]) -> list[str]:
    errors = [f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}"
              for e in validator_for_file("fictional-matter.schema.json").iter_errors(record)]
    if errors:
        return errors
    items = {i["id"] for i in record["application"]["items"]}
    parties = {p["id"] for p in record["parties"]}
    errors += [f"role names {r['party']}, who is not a party" for r in record["roles"] if r["party"] not in parties]
    errors += [f"event {e['step']} is no step of the template" for e in record["events"] if e["step"] not in steps]
    for objection in record["objections"]:
        if objection["test"] is None:
            # Only the customer's words are known: the objection names no test, so it can
            # carry nothing a test defines (ADR-0144).
            errors += [f"{objection['id']} names no test, so it cannot record {k}"
                       for k in ("facts", "assessments", "exhibits") if objection.get(k)]
            errors += [f"{objection['id']} covers {i}, which is not an item" for i in objection["items"] if i not in items]
            continue
        test = tests.get(objection["test"])
        if test is None:
            errors.append(f"{objection['id']} names {objection['test']}, which is no sound legal test")
            continue
        conditions = {leaf["id"]: leaf for leaf in procedure.leaves(test.record["condition"])}
        for exception in test.record.get("exceptions") or ():
            conditions.update({leaf["id"]: leaf for leaf in procedure.leaves(exception["condition"])})
        errors += [f"{objection['id']} covers {i}, which is not an item" for i in objection["items"] if i not in items]
        for fact in objection.get("facts") or ():
            leaf = conditions.get(fact["condition"])
            if leaf is None or leaf["kind"] != "fact":
                errors.append(f"{objection['id']}: {fact['condition']} is not a fact condition of {objection['test']}")
        for assessment in objection.get("assessments") or ():
            leaf = conditions.get(assessment["condition"])
            if leaf is None or leaf["kind"] != "evaluative":
                errors.append(f"{objection['id']}: {assessment['condition']} is not an evaluative condition of "
                              f"{objection['test']}")
        for exhibit in objection.get("exhibits") or ():
            errors += [f"{objection['id']} {exhibit['id']} shows {i}, which is not an item"
                       for i in exhibit.get("items") or () if i not in items]
    return errors


def load(path: Path | None = None) -> list[Matter]:
    """Every fictional matter, each checked. A matter with errors is returned with them,
    never silently dropped."""
    path = path or MATTERS_PATH
    tests = procedure.load_tests().by_id()
    steps = {s["id"] for p in procedure.load_processes().sound for s in p.record["steps"]}
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    seen: set[str] = set()
    out = []
    for record in document:
        errors = _check(record, tests, steps)
        if str(record.get("id")) in seen:
            errors.append("id used twice")
        seen.add(str(record.get("id")))
        out.append(Matter(record=record, errors=tuple(errors)))
    return out

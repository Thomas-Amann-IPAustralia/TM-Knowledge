"""The column layout the intake path writes and reads (P7, P8).

One module, because the workbook generator and the transcriber must agree
exactly. A column added to the sheet and not to the reader is a field the expert
filled in and nobody collected; a layout listed twice would eventually be two
layouts. It is derived from `eval/schemas/`, so a schema change moves the
workbook, and `test_intake.py` fails if the workbook on disk is older than the
schema it came from.

**The shapes a spreadsheet cannot hold flat.** Three, and each has an answer:

- A nested object (`expected_sources.required`) becomes dotted columns.
- An array of scalars (`alt_labels`, a ref list) becomes one cell, one value per
  line. Newline rather than a separator character because refs contain `/`, `(`,
  `~`, `#` and `.`, and a separator that can appear in a value is a data-loss
  bug waiting for the first ref that uses it.
- An array of *objects* (`relevant[]`, `expected_inferences[]`) becomes its own
  sheet, keyed back to the parent's id. Flattening it into parallel lists in one
  cell would make row 4's third grade belong to row 4's third ref by convention
  alone, and nothing would notice when it stopped being true.

`span` is the one special case: `[start, end]` is written as two integer columns,
because a person typing offsets wants two boxes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from tm_knowledge.stage0.schemas import ID_PREFIXES, RECORD_TYPES, SCHEMA_DIR, _deref

__all__ = ["Column", "Sheet", "sheets", "SHEET_NAMES", "REVIEW_COLUMNS"]

#: Record type -> the sheet a person sees. Kept short: Excel caps sheet names at
#: 31 characters and truncates silently, and a child sheet's name is built from
#: its record type's id prefix (`GS--relevant`) for the same reason.
SHEET_NAMES: dict[str, str] = {
    "competency_question": "competency-questions",
    "gold_entity": "entities",
    "gold_concept": "concepts",
    "gold_relationship": "relationships",
    "gold_search_question": "search-questions",
    "gold_retrieval_question": "retrieval-questions",
    "reasoning_expectation": "reasoning-expected",
    "prohibited_use": "prohibited-uses",
}


#: Headers the seed review workbook adds at the right-hand end of every sheet,
#: and the transcriber therefore has to tolerate rather than reject (ADR-0044).
#: They are annotations *about* a record, never fields *of* one, so they are
#: read by `tmk-seed` and dropped on the way into `eval/gold/` — a verdict is
#: how a record got approved, not something the record asserts.
REVIEW_COLUMNS: tuple[str, ...] = ("seed_id", "verdict", "correction")


@dataclass(frozen=True, slots=True)
class Column:
    """One column, and everything both ends of the round trip need to know."""

    header: str
    path: tuple[str, ...]
    #: text · number · boolean · enum · list — how a cell is read and written.
    kind: str
    enum: tuple[Any, ...] | None = None
    required: bool = False
    nullable: bool = True
    note: str = ""

    @property
    def is_span_part(self) -> bool:
        return self.path[:1] == ("span",) and len(self.path) == 2


@dataclass(frozen=True, slots=True)
class Sheet:
    """A worksheet: one record type, or one repeating group inside one."""

    name: str
    record_type: str
    columns: tuple[Column, ...]
    #: For a child sheet, the field of the parent record it fills.
    parent_field: str | None = None

    @property
    def is_child(self) -> bool:
        return self.parent_field is not None


def _schema(record_type: str) -> dict[str, Any]:
    return json.loads(
        (SCHEMA_DIR / RECORD_TYPES[record_type]).read_text(encoding="utf-8")
    )


def _types(node: dict[str, Any]) -> set[str]:
    declared = node.get("type")
    if declared is None:
        return set()
    return {declared} if isinstance(declared, str) else set(declared)


def _describe(node: dict[str, Any]) -> tuple[str, tuple[Any, ...] | None, bool]:
    """(kind, enum, nullable) for a leaf. `_deref` has already been applied."""
    enum = node.get("enum")
    if enum is not None:
        values = tuple(value for value in enum if value is not None)
        return "enum", values, None in enum or "null" in _types(node)

    types = _types(node)
    nullable = "null" in types or not types  # no declared type = anything, incl. null
    if "boolean" in types:
        return "boolean", None, nullable
    if types & {"integer", "number"}:
        return "number", None, nullable
    return "text", None, nullable


def _is_span(node: dict[str, Any]) -> bool:
    return (
        node.get("minItems") == 2
        and node.get("maxItems") == 2
        and "integer" in _types(_deref(node.get("items", {})))
    )


def _columns(
    node: dict[str, Any],
    path: tuple[str, ...],
    *,
    required: bool,
    note: str,
) -> tuple[list[Column], list[tuple[tuple[str, ...], dict[str, Any]]]]:
    """Columns for one property, plus any repeating groups it wants a sheet for."""
    note = node.get("description", note)
    resolved = _deref(node)
    note = note or resolved.get("description", "")

    if "oneOf" in resolved or "anyOf" in resolved:
        branches = [
            branch
            for branch in (*resolved.get("oneOf", ()), *resolved.get("anyOf", ()))
            if "null" not in _types(_deref(branch))
        ]
        if len(branches) == 1:
            columns, children = _columns(
                branches[0], path, required=required, note=note
            )
            return (
                [
                    Column(c.header, c.path, c.kind, c.enum, c.required, True, c.note)
                    for c in columns
                ],
                children,
            )

    types = _types(resolved)
    header = ".".join(path)

    if "object" in types and "properties" in resolved:
        columns: list[Column] = []
        children: list[tuple[tuple[str, ...], dict[str, Any]]] = []
        inner_required = set(resolved.get("required", ()))
        for name, child in resolved["properties"].items():
            more, more_children = _columns(
                child, path + (name,), required=name in inner_required, note=""
            )
            columns.extend(more)
            children.extend(more_children)
        return columns, children

    if "array" in types:
        items = resolved.get("items", {})
        if _is_span(resolved):
            return (
                [
                    Column(f"{header}.start", path + ("start",), "number",
                           required=required, nullable=True, note=note),
                    Column(f"{header}.end", path + ("end",), "number",
                           required=required, nullable=True, note=note),
                ],
                [],
            )
        if "object" in _types(_deref(items)):
            return [], [(path, resolved)]
        kind, enum, _ = _describe(_deref(items))
        return (
            [Column(header, path, "list", enum, required, True, note)],
            [],
        )

    kind, enum, nullable = _describe(resolved)
    return [Column(header, path, kind, enum, required, nullable, note)], []


@lru_cache(maxsize=1)
def sheets() -> tuple[Sheet, ...]:
    """Every sheet the workbook carries, parents before their children."""
    built: list[Sheet] = []
    for record_type in RECORD_TYPES:
        schema = _schema(record_type)
        required = set(schema.get("required", ()))
        columns: list[Column] = []
        children: list[tuple[tuple[str, ...], dict[str, Any]]] = []
        for name, node in schema["properties"].items():
            more, more_children = _columns(
                node, (name,), required=name in required, note=""
            )
            columns.extend(more)
            children.extend(more_children)
        built.append(
            Sheet(
                name=SHEET_NAMES[record_type],
                record_type=record_type,
                columns=tuple(columns),
            )
        )
        for path, node in children:
            field = ".".join(path)
            item_columns: list[Column] = []
            items = _deref(node["items"])
            item_required = set(items.get("required", ()))
            for name, child in items["properties"].items():
                more, _ = _columns(
                    child, (name,), required=name in item_required, note=""
                )
                item_columns.extend(more)
            built.append(
                Sheet(
                    name=f"{ID_PREFIXES[record_type]}--{field}"[:31],
                    record_type=record_type,
                    parent_field=field,
                    columns=(
                        Column(
                            "parent_id",
                            ("parent_id",),
                            "text",
                            required=True,
                            nullable=False,
                            note=(
                                "The id of the record on the "
                                f"`{SHEET_NAMES[record_type]}` sheet this row belongs "
                                "to. One row per entry; repeat the id."
                            ),
                        ),
                        *item_columns,
                    ),
                )
            )
    return tuple(built)


def sheet_for(name: str) -> Sheet | None:
    for sheet in sheets():
        if sheet.name == name:
            return sheet
    return None

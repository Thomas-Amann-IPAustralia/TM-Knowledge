"""Validation for the Stage 0 record types.

`eval/schemas/*.schema.json` is the machine-checkable face of
`eval/templates/*.yaml`. This module loads them, resolves the cross-file `$ref`s,
and adds the one thing JSON Schema cannot express on its own: that a field
carrying `format: upstream-ref` holds a ref `tm_knowledge.refs` would accept
(P4, P3).

**Shape only.** These schemas say a `modality` is one of three words; they can
never say which. A schema that could reject a legally-correct record has encoded
a judgement, and writing one is out of this repo's authority (CLAUDE.md rule 1).
Two consequences that look like laxity and are not:

- **Judgement fields are required-but-nullable.** The *key* must be present, so
  a gap is visible; the *value* may be null, so an agent can transcribe an
  expert's words without inventing the parts they did not say (P8). Null values
  are what P10 reports and what the completeness gate fails on — that is a
  different check from this one, deliberately.
- **`predicate` is not an enum.** The relationship dictionary is expert-owned
  and does not exist. Enumerating plausible predicates would author it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.refs import InvalidRef, is_ref

SCHEMA_DIR = REPO_ROOT / "eval" / "schemas"
TEMPLATE_DIR = REPO_ROOT / "eval" / "templates"

#: Record type -> schema file. The eight Stage 0 record types of the guide §5.
RECORD_TYPES: dict[str, str] = {
    "competency_question": "competency-question.schema.json",
    "gold_entity": "gold-entity.schema.json",
    "gold_concept": "gold-concept.schema.json",
    "gold_relationship": "gold-relationship.schema.json",
    "gold_search_question": "gold-search-question.schema.json",
    "gold_retrieval_question": "gold-retrieval-question.schema.json",
    "reasoning_expectation": "reasoning-expectation.schema.json",
    "prohibited_use": "prohibited-use.schema.json",
}

#: Record type -> the id prefix its records carry (`IDENTIFIERS.md` §3).
ID_PREFIXES: dict[str, str] = {
    "competency_question": "CQ",
    "gold_entity": "GE",
    "gold_concept": "GC",
    "gold_relationship": "GR",
    "gold_search_question": "GS",
    "gold_retrieval_question": "GA",
    "reasoning_expectation": "GX",
    "prohibited_use": "PU",
}


@dataclass(frozen=True, slots=True)
class SchemaError:
    """One validation failure, said in terms a person can act on."""

    record_id: str | None
    path: str
    message: str

    def __str__(self) -> str:
        where = f"{self.record_id or '<no id>'}"
        return f"{where} at {self.path or '<root>'}: {self.message}"


def _format_checker() -> FormatChecker:
    checker = FormatChecker()

    @checker.checks("upstream-ref", raises=InvalidRef)
    def _(value: object) -> bool:
        if not isinstance(value, str):
            return True  # the type keyword's job, not this one's
        return is_ref(value)

    return checker


@lru_cache(maxsize=1)
def _registry() -> Registry:
    registry = Registry()
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        resource = Resource.from_contents(contents)
        # Under its `$id`, which is what the schemas `$ref` each other by, and
        # under its filename, so a schema can be opened and read on its own.
        registry = resource @ registry
        registry = registry.with_resource(uri=path.name, resource=resource)
    return registry


@lru_cache(maxsize=None)
def validator_for(record_type: str) -> Draft202012Validator:
    if record_type not in RECORD_TYPES:
        raise KeyError(
            f"unknown Stage 0 record type {record_type!r}; known: {sorted(RECORD_TYPES)}"
        )
    path = SCHEMA_DIR / RECORD_TYPES[record_type]
    schema = json.loads(path.read_text(encoding="utf-8"))
    return Draft202012Validator(
        schema,
        registry=_registry(),
        format_checker=_format_checker(),
    )


def validate(record: dict[str, Any], record_type: str) -> list[SchemaError]:
    """Validate one record. Returns every failure, rather than the first.

    A list, not an exception: the caller is usually a coverage report telling an
    expert what to fix, and stopping at the first problem makes that report a
    conversation rather than a worklist.
    """
    validator = validator_for(record_type)
    errors = []
    for error in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
        errors.append(
            SchemaError(
                record_id=record.get("id") if isinstance(record, dict) else None,
                path="/".join(str(part) for part in error.path),
                message=error.message,
            )
        )
    return errors


def validate_all(records: Iterable[dict[str, Any]], record_type: str) -> list[SchemaError]:
    return [error for record in records for error in validate(record, record_type)]


def schema_properties(record_type: str) -> set[str]:
    """Top-level property names a record type admits."""
    path = SCHEMA_DIR / RECORD_TYPES[record_type]
    schema = json.loads(path.read_text(encoding="utf-8"))
    return set(schema["properties"])


#: The `$id` of the shared definitions, and the only IRI any schema `$ref`s.
COMMON_ID = "https://ipaustralia.gov.au/schemas/tmk/stage0/common/1.0.0"


def enum_values(record_type: str, field: str) -> list[Any]:
    """The enum a field admits, read from the schema rather than restated.

    Follows a `$ref` into the shared definitions, so a field defined once in
    `common.schema.json` reports the same list wherever it is used — which is
    the point of defining it once.
    """
    path = SCHEMA_DIR / RECORD_TYPES[record_type]
    prop = json.loads(path.read_text(encoding="utf-8"))["properties"][field]
    if "$ref" in prop:
        reference = prop["$ref"]
        if not reference.startswith(COMMON_ID + "#/$defs/"):
            raise KeyError(f"{record_type}.{field} points outside the shared defs")
        common = json.loads((SCHEMA_DIR / "common.schema.json").read_text(encoding="utf-8"))
        prop = common["$defs"][reference.rsplit("/", 1)[1]]
    if "enum" not in prop:
        raise KeyError(f"{record_type}.{field} is not an enum")
    return list(prop["enum"])


# ---------------------------------------------------------------------------
# Where the refs are — read off the schema, never restated
# ---------------------------------------------------------------------------

#: Placeholder for an array index in a field path.
EACH = "*"


@lru_cache(maxsize=1)
def _common_defs() -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / "common.schema.json").read_text(encoding="utf-8"))["$defs"]


def _deref(node: dict[str, Any]) -> dict[str, Any]:
    """Follow a `$ref` into the shared definitions.

    Two spellings reach the same place: a record schema names the definitions by
    their `$id`, and `common.schema.json` names its own by fragment alone. Both
    are resolved here so `ref_list` — which is a common def whose items are a
    fragment ref — reaches `upstream_ref` like any other.
    """
    reference = node.get("$ref")
    if not reference:
        return node
    if reference.startswith(COMMON_ID + "#/$defs/"):
        name = reference.rsplit("/", 1)[1]
    elif reference.startswith("#/$defs/"):
        name = reference.rsplit("/", 1)[1]
        if name not in _common_defs():
            raise KeyError(f"{reference} is not a shared definition")
    else:
        raise KeyError(f"{reference} points outside the shared definitions")
    return _common_defs()[name]


def _is_upstream_ref(node: dict[str, Any]) -> bool:
    return _deref(node).get("format") == "upstream-ref"


def _walk(node: dict[str, Any], path: tuple[str, ...]) -> Iterable[tuple[str, ...]]:
    if _is_upstream_ref(node):
        yield path
        return
    for branch in (*node.get("oneOf", ()), *node.get("anyOf", ())):
        yield from _walk(branch, path)
    node = _deref(node)
    if "items" in node:
        yield from _walk(node["items"], path + (EACH,))
    for name, child in node.get("properties", {}).items():
        yield from _walk(child, path + (name,))


@lru_cache(maxsize=None)
def ref_paths(record_type: str) -> tuple[tuple[str, ...], ...]:
    """Every place in a record where an upstream ref sits.

    Derived from the schema rather than listed by hand, so adding a ref-valued
    field to a schema automatically puts it under the harness's resolution
    checks. A path is a tuple of property names with `*` for an array index —
    `("relevant", "*", "ref")`.
    """
    path = SCHEMA_DIR / RECORD_TYPES[record_type]
    schema = json.loads(path.read_text(encoding="utf-8"))
    found: list[tuple[str, ...]] = []
    for name, child in schema["properties"].items():
        found.extend(_walk(child, (name,)))
    return tuple(dict.fromkeys(found))


def read_path(record: Any, path: tuple[str, ...]) -> Iterable[tuple[str, Any]]:
    """(pointer, value) for every value a field path reaches in one record.

    Missing keys yield nothing — absence is the schema's business, not this
    function's — and a null yields nothing, because a null ref is a gap the
    completeness gate reports, not an unresolvable ref.
    """
    if not path:
        if record is not None:
            yield "", record
        return
    head, rest = path[0], path[1:]
    if head == EACH:
        if not isinstance(record, list):
            return
        for index, item in enumerate(record):
            for pointer, value in read_path(item, rest):
                yield f"[{index}]{pointer}", value
        return
    if not isinstance(record, dict) or head not in record:
        return
    for pointer, value in read_path(record[head], rest):
        yield f".{head}{pointer}" if pointer.startswith((".", "[")) else f".{head}", value

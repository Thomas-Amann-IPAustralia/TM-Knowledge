"""The return leg: workbook in, validated records out (parallel track P8).

This is the mechanism by which "an agent will transcribe and validate" stops
being a promise in `STAGE-0-INPUT-GUIDE.md` §6 and becomes a command.

**Transcription may reshape, never supply.** A blank cell becomes a null and is
reported as a gap. If a relationship arrives without a `modality`, the record is
written without one and the gap is queued — it is never inferred from the
sentence's grammar, because whether a "may" is possibility or permission is a
legal reading (guide §5.4). Nothing in this module has a default value for a
judgement field, and adding one would be authoring content.

Three things it refuses to do, all of them for the same reason — writing into
`eval/gold/` is writing into approved space (CLAUDE.md rule 4):

- It will not write a record that does not validate. A malformed record in the
  gold set is a measurement standard that is wrong, and the harness would then
  certify everything against it.
- It will not write a row whose non-nullable required fields are blank. That row
  is not yet a record; saying so is more useful than writing a stub.
- It will not write at all without `--write`. The default is a dry run that
  prints what would change.

Re-running over unchanged input rewrites nothing: the YAML is rendered
deterministically and compared before writing, so an unchanged workbook produces
an unchanged git status.
"""

from __future__ import annotations

import datetime as _datetime
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.intake import REVIEW_COLUMNS, Column, Sheet, sheet_for, sheets
from tm_knowledge.stage0.schemas import property_order, required_fields, validate

__all__ = ["Held", "Transcription", "read_workbook", "write_records"]


class WorkbookMismatch(Exception):
    """The workbook's columns are not the ones the schemas describe."""


@dataclass(frozen=True, slots=True)
class Problem:
    """A row that could not become a record, said where a person can find it."""

    sheet: str
    row: int | None
    message: str

    def __str__(self) -> str:
        where = f"{self.sheet}" + (f" row {self.row}" if self.row else "")
        return f"{where}: {self.message}"


#: The verdicts a review workbook's `verdict` column may carry, plus the empty
#: cell that means the row was never reached. Anything else is a typo, and a
#: typo is reported rather than guessed at — `corrrect` is obvious to a reader
#: and is exactly the kind of thing rule 6 says not to interpret.
VERDICTS: frozenset[str] = frozenset({"correct", "amend", "reject"})

#: Why a row that arrived was not written into `eval/gold/`. Each is a state a
#: person can act on, which is the point of separating them from `Problem`: a
#: held row is not malformed, it is simply not approved yet (ADR-0048).
NOT_REVIEWED = "not reviewed"
REJECTED = "rejected by the reviewer"
AMENDMENT_PENDING = "marked 'amend'; the amendment has not been applied"
UNSIGNED = "marked 'correct' but approved_by is blank, so nobody has signed it"
CHILD_UNSETTLED = "approved, but a row on its child sheet is not settled"
DANGLING = "approved, but it names a record that is not"


@dataclass(frozen=True, slots=True)
class Held:
    """A row that was read, understood, and deliberately not written."""

    record_type: str
    identifier: str
    reason: str
    #: What the reviewer wrote in `correction`, where they wrote anything.
    correction: str | None = None
    seed_id: str | None = None
    #: Which child rows are unsettled, for the one reason that needs naming.
    detail: str | None = None

    def __str__(self) -> str:
        tail = f" — {self.correction}" if self.correction else ""
        where = f" [{self.detail}]" if self.detail else ""
        return f"{self.identifier} ({self.record_type}): {self.reason}{where}{tail}"


@dataclass
class Transcription:
    """What came out of one workbook."""

    records: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    problems: list[Problem] = field(default_factory=list)
    #: (record type, id, field) for every judgement field that arrived blank.
    blanks: list[tuple[str, str, str]] = field(default_factory=list)
    #: Record types whose sheet held no rows at all.
    empty_sheets: list[str] = field(default_factory=list)
    #: Rows the review gate kept out of `eval/gold/`, and why.
    held: list[Held] = field(default_factory=list)
    #: (record type, parent id, where) for every child entry a reviewer rejected
    #: and this run therefore left out of its parent's list.
    dropped: list[tuple[str, str, str]] = field(default_factory=list)
    #: True when the workbook carried a `verdict` column — i.e. it is a seed
    #: review workbook and the gate applied. A plain intake workbook has none,
    #: and behaves exactly as it did before the gate existed.
    reviewed: bool = False

    @property
    def total(self) -> int:
        return sum(len(records) for records in self.records.values())

    def held_by_reason(self) -> dict[str, list[Held]]:
        grouped: dict[str, list[Held]] = {}
        for entry in self.held:
            grouped.setdefault(entry.reason, []).append(entry)
        return grouped

    def summary(self) -> str:
        gate = f"; {len(self.held)} row(s) held" if self.reviewed else ""
        return (
            f"{self.total} record(s) from {len(self.records)} sheet(s); "
            f"{len(self.problems)} rejected row(s){gate}; {len(self.blanks)} blank "
            "judgement field(s)"
        )


# ---------------------------------------------------------------------------
# Reading cells
# ---------------------------------------------------------------------------


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


_ISO_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_SLASHED_DATE = re.compile(r"^([0-9]{1,2})[/.-]([0-9]{1,2})[/.-]([0-9]{4})$")


def _date(header: str, value: Any) -> str | None:
    """An approval date to `YYYY-MM-DD`, or a loud refusal.

    Three things arrive in this cell and only one of them is already right:

    - a real Excel date, which openpyxl hands over as a `datetime`. Excel parsed
      it under the typist's locale, so it is unambiguous by the time it gets
      here and converts exactly;
    - an ISO string, which passes through;
    - a string somebody typed with slashes. `25/08/2026` can only be
      day/month — no month is 25 — so it converts. `05/08/2026` cannot be
      resolved by anything in this repo, and a wrong approval date is a
      provenance defect that nothing downstream would ever catch, so it is
      refused by name rather than read as Australian and hoped for (rule 6).
    """
    if isinstance(value, _datetime.datetime):
        return value.date().isoformat()
    if isinstance(value, _datetime.date):
        return value.isoformat()

    text = _text(value)
    if text is None:
        return None
    if _ISO_DATE.match(text):
        try:
            _datetime.date.fromisoformat(text)
        except ValueError as error:
            raise ValueError(f"{header} is {text!r}, which is not a real date") from error
        return text

    slashed = _SLASHED_DATE.match(text)
    if slashed:
        first, second, year = (int(part) for part in slashed.groups())
        if first > 12 and 1 <= second <= 12:
            try:
                return _datetime.date(year, second, first).isoformat()
            except ValueError as error:
                raise ValueError(
                    f"{header} is {text!r}, which is not a real date"
                ) from error
        raise ValueError(
            f"{header} is {text!r}. Written that way it is day/month to one "
            "reader and month/day to another, and this one could be either. "
            "Nothing here will guess at an approval date — write it as "
            "YYYY-MM-DD, or type it into a cell Excel formats as a date"
        )

    raise ValueError(
        f"{header} is {text!r}, which is not a date. Write it as YYYY-MM-DD"
    )


def _cell(column: Column, value: Any, sheet: str, row: int) -> Any:
    """One cell to one Python value. Raises on a value the schema cannot hold."""
    if column.kind == "date":
        return _date(column.header, value)

    if column.kind == "list":
        raw = _text(value)
        if raw is None:
            return []
        return [line.strip() for line in raw.splitlines() if line.strip()]

    text = _text(value)
    if text is None:
        return None

    if column.kind == "boolean":
        lowered = text.lower()
        if lowered in ("true", "yes", "y", "1"):
            return True
        if lowered in ("false", "no", "n", "0"):
            return False
        raise ValueError(f"{column.header} is {text!r}, which is not true or false")

    if column.kind == "number":
        try:
            return int(float(text))
        except ValueError as error:
            raise ValueError(f"{column.header} is {text!r}, which is not a number") from error

    if column.enum:
        for allowed in column.enum:
            if text == str(allowed):
                return allowed
        raise ValueError(
            f"{column.header} is {text!r}; it takes one of "
            + ", ".join(str(v) for v in column.enum)
            + ". Leave it blank rather than choosing the nearest one"
        )

    return text


def _prune_optional(record: dict[str, Any], record_type: str) -> None:
    """Drop optional keys that arrived empty; keep every required one.

    The asymmetry is ADR-0027's, and it is what keeps a gap visible. A required
    key is written even when it is null, because that null *is* the gap the
    coverage report names. An optional key that nobody filled in is not a gap —
    writing `notes: null` on every record would bury the real ones in noise, and
    it would make the transcriber's output differ from an expert's own file for
    no reason.
    """
    required = required_fields(record_type)
    for key in [k for k in record if k not in required]:
        if record[key] is None or record[key] == [] or record[key] == "":
            del record[key]


def _reorder(record: dict[str, Any], record_type: str) -> None:
    """Put the keys back into schema order, in place.

    A child sheet attaches its field after the parent row was built, so
    `relevant` and `expected_inferences` would otherwise land at the end of the
    record — correct YAML, and a diff that reads nothing like the template.
    """
    ordered = {
        key: record[key] for key in property_order(record_type) if key in record
    }
    record.clear()
    record.update(ordered)


def _nest(record: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    node = record
    for key in path[:-1]:
        node = node.setdefault(key, {})
    node[path[-1]] = value


def _collapse_spans(record: dict[str, Any]) -> None:
    """`span.start` / `span.end` back into the `[start, end]` the schema wants."""
    span = record.get("span")
    if not isinstance(span, dict):
        return
    start, end = span.get("start"), span.get("end")
    if start is None and end is None:
        record["span"] = None
        return
    if start is None or end is None:
        raise ValueError("span.start and span.end must be given together, or neither")
    record["span"] = [start, end]


# ---------------------------------------------------------------------------
# Reading sheets
# ---------------------------------------------------------------------------


def _headers(worksheet, spec: Sheet) -> dict[str, int]:
    """Header name -> column index, checked against the layout in both directions."""
    found: dict[str, int] = {}
    for index, cell in enumerate(worksheet[1], start=1):
        name = _text(cell.value)
        if name is None:
            continue
        if name in found:
            raise WorkbookMismatch(f"{spec.name}: the column {name!r} appears twice")
        found[name] = index

    expected = {column.header for column in spec.columns}
    missing = expected - set(found)
    # The seed review workbook carries five annotation columns the intake
    # workbook does not (ADR-0044, ADR-0046). They are about the record, not part
    # of it, so they never become a field — but two of them decide whether the
    # record is written at all (ADR-0048).
    unknown = set(found) - expected - set(REVIEW_COLUMNS)
    if missing or unknown:
        raise WorkbookMismatch(
            f"{spec.name}: the sheet does not match the schemas. "
            + (f"Missing: {', '.join(sorted(missing))}. " if missing else "")
            + (f"Unknown: {', '.join(sorted(unknown))}. " if unknown else "")
            + "Regenerate the workbook with `tmk-workbook` rather than adding "
            "columns by hand — a column the transcriber does not know is a field "
            "nobody collects."
        )
    return found


@dataclass(frozen=True, slots=True)
class _Annotation:
    """The reviewer's marks on one row. Absent entirely on an intake workbook."""

    present: bool = False
    verdict: str | None = None
    correction: str | None = None
    seed_id: str | None = None
    approved_by: str | None = None


def _annotation(spec: Sheet, values: dict[str, Any]) -> _Annotation:
    if "verdict" not in values:
        return _Annotation()
    verdict = _text(values.get("verdict"))
    approved = None
    for column in spec.columns:
        if column.header == "approved_by":
            approved = _text(values.get("approved_by"))
    return _Annotation(
        present=True,
        verdict=verdict.strip().lower() if verdict else None,
        correction=_text(values.get("correction")),
        seed_id=_text(values.get("seed_id")),
        approved_by=approved,
    )


def _rows(worksheet, spec: Sheet, result: Transcription):
    """(row number, record, annotation) for every row that became a record."""
    positions = _headers(worksheet, spec)
    for number, row in enumerate(worksheet.iter_rows(min_row=2), start=2):
        values = {header: row[index - 1].value for header, index in positions.items()}
        if all(_text(value) is None for value in values.values()):
            continue

        marks = _annotation(spec, values)
        if marks.present:
            result.reviewed = True
            if marks.verdict is not None and marks.verdict not in VERDICTS:
                result.problems.append(
                    Problem(
                        spec.name,
                        number,
                        f"verdict is {marks.verdict!r}; it is one of "
                        + ", ".join(sorted(VERDICTS))
                        + ". A near-miss is not read as the value it resembles — "
                        "fix the cell and hand the workbook back",
                    )
                )
                continue

        record: dict[str, Any] = {}
        failed = False
        for column in spec.columns:
            try:
                _nest(record, column.path, _cell(column, values[column.header], spec.name, number))
            except ValueError as error:
                result.problems.append(Problem(spec.name, number, str(error)))
                failed = True
        if failed:
            continue
        try:
            _collapse_spans(record)
        except ValueError as error:
            result.problems.append(Problem(spec.name, number, str(error)))
            continue
        if not spec.is_child:
            _prune_optional(record, spec.record_type)

        blank_required = [
            column.header
            for column in spec.columns
            if column.required and not column.nullable
            and record.get(column.path[0]) in (None, "", [])
        ]
        if blank_required:
            result.problems.append(
                Problem(
                    spec.name,
                    number,
                    f"{', '.join(blank_required)} is blank, so the row is not yet a "
                    "record. Nothing here will fill it in",
                )
            )
            continue
        yield number, record, marks


def read_workbook(path: Path) -> Transcription:
    """Read a filled workbook into records. Writes nothing."""
    try:
        from openpyxl import load_workbook
    except ModuleNotFoundError as error:  # pragma: no cover - depends on install
        raise ModuleNotFoundError(
            "the intake path needs openpyxl: pip install -e '.[intake]'"
        ) from error

    workbook = load_workbook(path, data_only=True)
    result = Transcription()

    parents: dict[str, dict[str, dict[str, Any]]] = {}
    marks: dict[str, dict[str, _Annotation]] = {}
    for spec in sheets():
        if spec.is_child or spec.name not in workbook.sheetnames:
            continue
        rows = list(_rows(workbook[spec.name], spec, result))
        if not rows:
            result.empty_sheets.append(spec.record_type)
            continue
        by_id: dict[str, dict[str, Any]] = {}
        annotations: dict[str, _Annotation] = {}
        for number, record, annotation in rows:
            identifier = record.get("id")
            if identifier in by_id:
                result.problems.append(
                    Problem(spec.name, number, f"id {identifier} is used twice")
                )
                continue
            by_id[identifier] = record
            annotations[identifier] = annotation
        parents[spec.record_type] = by_id
        marks[spec.record_type] = annotations

    # Child sheets fill a repeating field on a parent that must already exist.
    # A child row carries its own verdict and no `approved_by` — approval lives
    # on the parent — so a rejected entry is dropped from the parent's list and
    # anything else unresolved holds the parent whole (ADR-0048).
    child_holds: dict[str, dict[str, list[str]]] = {}
    for spec in sheets():
        if not spec.is_child or spec.name not in workbook.sheetnames:
            continue
        by_id = parents.get(spec.record_type, {})
        for parent in by_id.values():
            parent.setdefault(spec.parent_field, [])
        for number, entry, annotation in _rows(workbook[spec.name], spec, result):
            parent_id = entry.pop("parent_id")
            parent = by_id.get(parent_id)
            if parent is None:
                result.problems.append(
                    Problem(
                        spec.name,
                        number,
                        f"parent_id {parent_id} names no record on the "
                        f"`{_parent_sheet(spec)}` sheet",
                    )
                )
                continue
            if annotation.present:
                if annotation.verdict == "reject":
                    # The reviewer said this entry should not exist. Dropping it
                    # applies their decision; it does not hold the parent, whose
                    # own verdict is on its own row.
                    result.dropped.append(
                        (spec.record_type, str(parent_id), f"{spec.name} row {number}")
                    )
                    continue
                if annotation.verdict != "correct":
                    where = f"{spec.name} row {number}"
                    reason = (
                        AMENDMENT_PENDING
                        if annotation.verdict == "amend"
                        else NOT_REVIEWED
                    )
                    child_holds.setdefault(spec.record_type, {}).setdefault(
                        parent_id, []
                    ).append(f"{where}: {reason}")
            parent[spec.parent_field].append(entry)

    for record_type, by_id in parents.items():
        kept: list[dict[str, Any]] = []
        annotations = marks.get(record_type, {})
        holds = child_holds.get(record_type, {})
        for identifier, record in by_id.items():
            annotation = annotations.get(identifier, _Annotation())
            unsettled = holds.get(identifier, ())
            reason = _gate(annotation, unsettled)
            if reason is not None:
                result.held.append(
                    Held(
                        record_type=record_type,
                        identifier=str(identifier),
                        reason=reason,
                        correction=annotation.correction,
                        seed_id=annotation.seed_id,
                        detail="; ".join(unsettled) if reason is CHILD_UNSETTLED else None,
                    )
                )
                continue
            _reorder(record, record_type)
            errors = validate(record, record_type)
            if errors:
                for error in errors:
                    result.problems.append(
                        Problem(_sheet_name(record_type), None, f"{identifier}: {error}")
                    )
                continue
            kept.append(record)
            result.blanks.extend(
                (record_type, identifier, name) for name in _blank_fields(record)
            )
        if kept:
            result.records[record_type] = kept
    return result


def _gate(annotation: _Annotation, child_holds) -> str | None:
    """Why this row must not enter `eval/gold/`, or None if it may.

    Only reached for a workbook that carries a `verdict` column. A plain intake
    workbook has none, `annotation.present` is False, and every row goes through
    exactly as it did before this gate existed — an expert's own composed record
    is awaiting approval, not awaiting review, and the coverage report is what
    says so about it (ADR-0027, ADR-0039).

    For a seed review workbook the rule is rule 4 with no softening: machine
    output crosses into approved space only where a person said it was right
    *and* put their name to it. `correct` without a name is the interesting
    state — it is a judgement that was made and not signed — so it is reported
    under its own reason rather than lumped in with the unread rows.
    """
    if not annotation.present:
        return None
    if annotation.verdict is None:
        return NOT_REVIEWED
    if annotation.verdict == "reject":
        return REJECTED
    if annotation.verdict == "amend":
        return AMENDMENT_PENDING
    if not annotation.approved_by:
        return UNSIGNED
    if child_holds:
        return CHILD_UNSETTLED
    return None


def close_over_cross_references(
    transcription: Transcription, approved_ids: frozenset[str] = frozenset()
) -> None:
    """Hold every approved record that names one nothing approved defines.

    Approval of a set does not distribute over its members. A reviewer signs
    `PU-0001` — a prohibition that is true on its own terms — and it carries
    `related_questions: [CQ-0012, GA-0003]`; sign the prohibition and not the
    question and the gold set acquires a pointer to nothing. `tmk-harness` calls
    that a DEFECT and is right to: a measurement standard with a dangling
    reference is not a standard, and the check cannot be relaxed to look in
    `review/seed/` without letting approved knowledge rest on candidates
    (CLAUDE.md rule 4).

    So the gate is closed transitively — held to a fixed point, because holding
    one record can dangle another's pointer to it. The cost is real and it is
    the honest number: partial approval of an interlinked set yields less than
    the row count suggests, and the coverage report now says which unsigned
    record is holding which signed one (ADR-0048).

    `approved_ids` is what is already in `eval/gold/` and not being rewritten by
    this run. Applies only to a review workbook; an intake workbook has no
    verdicts and is untouched.
    """
    if not transcription.reviewed:
        return

    from tm_knowledge.stage0.harness import CROSS_REFERENCES
    from tm_knowledge.stage0.schemas import read_path

    while True:
        known = set(approved_ids)
        for record_type, records in transcription.records.items():
            known.update(
                str(record["id"]) for record in records if record.get("id")
            )

        newly_held: list[Held] = []
        for record_type, fields in CROSS_REFERENCES.items():
            kept = transcription.records.get(record_type)
            if not kept:
                continue
            survivors: list[dict[str, Any]] = []
            for record in kept:
                dangling = [
                    f"{pointer} names {value}"
                    for path, prefixes in fields.items()
                    for pointer, value in read_path(record, path)
                    if isinstance(value, str)
                    and value.split("-")[0] in prefixes
                    and value not in known
                ]
                if dangling:
                    newly_held.append(
                        Held(
                            record_type=record_type,
                            identifier=str(record.get("id")),
                            reason=DANGLING,
                            detail="; ".join(dangling),
                        )
                    )
                else:
                    survivors.append(record)
            if survivors:
                transcription.records[record_type] = survivors
            else:
                del transcription.records[record_type]

        if not newly_held:
            return
        transcription.held.extend(newly_held)
        dropped = {(h.record_type, h.identifier) for h in newly_held}
        transcription.blanks = [
            blank for blank in transcription.blanks if (blank[0], blank[1]) not in dropped
        ]


def _sheet_name(record_type: str) -> str:
    return next(s.name for s in sheets() if s.record_type == record_type and not s.is_child)


def _parent_sheet(spec: Sheet) -> str:
    return _sheet_name(spec.record_type)


def _blank_fields(record: dict[str, Any], prefix: str = "") -> list[str]:
    """Every key that arrived null or empty. What P10 turns into a worklist."""
    blank: list[str] = []
    for key, value in record.items():
        name = f"{prefix}{key}"
        if value is None or value == [] or value == "":
            blank.append(name)
        elif isinstance(value, dict):
            blank.extend(_blank_fields(value, f"{name}."))
    return blank


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------


def render(records: list[dict[str, Any]]) -> str:
    """One gold file's YAML, deterministically.

    Key order is the schema's order, because that is the order the workbook's
    columns are in and the order the guide explains the fields in. `sort_keys`
    would reorder every record into alphabetical soup and make the first diff
    after this change unreadable.
    """
    return yaml.safe_dump(
        records,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )


def write_records(
    transcription: Transcription,
    gold_dir: Path | None = None,
    *,
    write: bool = False,
) -> list[tuple[Path, str]]:
    """Write each record type's file. Returns (path, outcome) per file.

    Outcomes: `written`, `unchanged`, `would write` (a dry run). A record type
    whose sheet held no rows is not touched at all — an empty sheet means "I have
    nothing for this yet", never "delete what is there".
    """
    gold_dir = gold_dir or goldset.GOLD_DIR
    outcomes: list[tuple[Path, str]] = []
    for record_type, records in sorted(transcription.records.items()):
        path = gold_dir / goldset.FILE_FOR[record_type]
        text = render(records)
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == text:
            outcomes.append((path, "unchanged"))
            continue
        if not write:
            outcomes.append((path, "would write"))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        outcomes.append((path, "written"))
    return outcomes

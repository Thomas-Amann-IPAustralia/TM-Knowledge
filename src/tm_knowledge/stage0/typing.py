"""The concept typing pass — the 52, laid out for one person to sort.

The owner ruled on OQ-0001: *"Use those four groups — come back to me with the
list of 52 to sort."* This is the coming back.

**Nothing here types a concept.** Every `type` cell is empty, and it stays empty
until a person picks from the dropdown and signs the row. Which of the four
groups *connotation* belongs in is a legal judgement (ADR-0056 consequence 4,
CLAUDE.md rule 1), and a machine-filled taxonomy reads as authoritative and was
authored by nobody. What this module supplies is the id, the concept it points
at, and the evidence — the shape, never the content.

Two artefacts, because they are for two different moments:

- `data/derived/concept-typing.xlsx` — the pass itself. It is an ordinary intake
  workbook with the `concept-types` sheet pre-filled, so `tmk-transcribe` reads
  it back with no new code: the single door into `eval/gold/` stays single
  (ADR-0048).
- `data/derived/reports/concept-typing.md` — the evidence, for reading on the
  dashboard or beside the spreadsheet. Labels, near-misses, and the passages
  each concept was drawn from.

`workbook.fill()` has existed since P7 and was deliberately not a command:
*"generating an empty workbook and pre-filling one with content are different
decisions, and only the first has been made."* The owner has now made the second
(ADR-0071).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import goldset
from tm_knowledge.upstream.loader import load_corpus

__all__ = [
    "WORKBOOK_PATH",
    "REPORT_PATH",
    "summarise",
    "rows",
    "write_workbook",
    "render",
    "write_report",
]

WORKBOOK_PATH = REPO_ROOT / "data" / "derived" / "concept-typing.xlsx"
REPORT_PATH = REPO_ROOT / "data" / "derived" / "reports" / "concept-typing.md"

#: What the four groups mean, in the owner's own question's words. Repeated on
#: the sheet and in the report so nobody has to hold them in their head across
#: 52 rows.
GROUPS: tuple[tuple[str, str], ...] = (
    ("ground_of_refusal", "a reason an application can be refused"),
    ("legal_test", "a question the decision maker has to answer"),
    ("relevant_factor", "something that feeds into that answer"),
    ("exception", "something that takes a case out of the rule"),
    ("none_of_these", "none of the four fit — which is an answer, not a gap"),
)


def summarise(concept: dict[str, Any]) -> str:
    """The concept in one line: what it is called, what else it is called, and
    what it is explicitly not.

    This is the `notes` cell of a typing row, and it is the whole of what a
    sorter sees without opening the evidence pack. All three parts come
    verbatim from the approved concept record — nothing here paraphrases or
    infers, because a summary that reworded a label would be a machine making a
    vocabulary judgement (CLAUDE.md rule 1).

    The alternative labels earn their place for the same reason the near-misses
    do. `pref_label` is one form of words out of several the Manual uses, so a
    sorter who does not recognise *connotation* may well recognise *secondary
    or implied meaning* — and the near-misses then stop them typing by label
    once they do.
    """
    summary = concept["pref_label"]
    if concept.get("alt_labels"):
        summary += " — also called: " + ", ".join(concept["alt_labels"])
    if concept.get("not_labels"):
        summary += " — not: " + ", ".join(concept["not_labels"])
    return summary


def _existing_types() -> dict[str, dict[str, Any]]:
    """Typings already signed, keyed by concept id. A second pass must not ask
    again about a concept somebody has already ruled on."""
    return {record["concept"]: record for record in goldset.load()["concept_type"]}


def rows(gold: goldset.GoldSet | None = None) -> tuple[dict[str, Any], ...]:
    """One partial `concept_type` record per approved concept, `type` empty.

    Ids are allocated by appending, never filling a gap left by a withdrawal
    (`IDENTIFIERS.md` §3), and a concept already typed keeps the id it has.
    """
    gold = gold or goldset.load()
    concepts = sorted(gold["gold_concept"], key=lambda record: record["id"])
    already = {record["concept"]: record for record in gold["concept_type"]}

    taken = {
        int(record["id"].split("-")[1])
        for record in gold["concept_type"]
        if record.get("id", "").startswith("GT-")
    }
    taken |= {
        int(identifier.split("-")[1])
        for identifier in gold.retired_ids
        if identifier.startswith("GT-")
    }
    next_number = max(taken, default=0) + 1

    built: list[dict[str, Any]] = []
    for concept in concepts:
        signed = already.get(concept["id"])
        if signed is not None:
            built.append(dict(signed))
            continue
        built.append(
            {
                "id": f"GT-{next_number:04d}",
                "concept": concept["id"],
                # `type` is absent, not blank-stringed. A blank cell is a gap the
                # transcriber reports; an empty string would be a value.
                "notes": summarise(concept),
            }
        )
        next_number += 1
    return tuple(built)


def write_workbook(path: Path | None = None, *, generated: str | None = None) -> Path:
    """The pass, as a workbook `tmk-transcribe` already knows how to read."""
    from tm_knowledge.stage0 import workbook as workbook_module

    path = path or WORKBOOK_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    typing_rows = rows()
    book = workbook_module.build(generated=generated)
    _mark_as_scoped(book, len(typing_rows))
    workbook_module.fill(book, {"concept_type": list(typing_rows)})
    _fit_the_notes(book, len(typing_rows))
    book.save(path)
    return path


def _fit_the_notes(book, count: int) -> None:
    """Make the `notes` cell readable at the length it now is.

    The summary carries the concept's other names as well as its near-misses,
    so it is several times longer than a hand-typed note. At the intake
    workbook's default 28 characters it shows as one clipped line, and what
    falls off the end is the *not:* part — the half that stops a sorter typing
    by label. Widen the column and let it wrap; the rows auto-fit from there.

    Only the pre-filled rows are touched. The columns below them stay as the
    generated workbook made them, because this sheet is still an ordinary
    intake sheet that `tmk-transcribe` reads back (ADR-0048).
    """
    from openpyxl.styles import Alignment
    from openpyxl.utils import get_column_letter

    from tm_knowledge.stage0.intake import sheets

    spec = next(sheet for sheet in sheets() if sheet.record_type == "concept_type")
    column = [item.header for item in spec.columns].index("notes") + 1
    sheet = book[spec.name]
    sheet.column_dimensions[get_column_letter(column)].width = 72
    for row in range(2, count + 2):
        sheet.cell(row=row, column=column).alignment = Alignment(
            wrap_text=True, vertical="top"
        )


def _mark_as_scoped(book, count: int) -> None:
    """Say on the workbook's face what it is and is not.

    ADR-0055's third guard: a scoped artefact that looks exactly like an
    unscoped one is how a partial round gets filed as a complete one. This one
    is narrower still — every sheet but `concept-types` is empty and is meant to
    stay empty.
    """
    from openpyxl.styles import Alignment, Font

    sheet = book[book.sheetnames[0]]
    sheet["A1"] = "Concept typing pass — sort the concepts into the four groups"
    sheet["A1"].font = Font(bold=True, size=14)
    sheet["A2"] = (
        f"This is not the general intake workbook. Exactly one sheet is in use — "
        f"**concept-types**, pre-filled with {count} rows, one per approved concept. Pick a "
        "group from the dropdown in the `type` column, put your name in `approved_by` and "
        "the date in `approved_date`, and hand the file back. Leave a row blank if you are "
        "not sure: a blank is reported as still-to-do, and a guess is not. Every other "
        "sheet is empty and should stay empty.\n\n"
        "The `notes` column is filled in for you and is the only column you should not "
        "need to touch: it gives each concept's name, what else the Manual calls it "
        "(*also called*), and what it is explicitly *not*. All three come straight from "
        "the approved concept record. For the passages behind them, read "
        "`data/derived/reports/concept-typing.md` beside this sheet."
    )
    sheet["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    sheet.row_dimensions[2].height = 130
    row = 4
    for value, meaning in GROUPS:
        sheet.cell(row=row, column=1, value=value).font = Font(bold=True)
        sheet.cell(row=row, column=2, value=meaning).alignment = Alignment(
            wrap_text=True, vertical="top"
        )
        row += 1


def render(generated: str | None = None) -> str:
    """The evidence pack: every concept with what it is and what it is not."""
    gold = goldset.load()
    corpus = load_corpus()
    concepts = sorted(gold["gold_concept"], key=lambda record: record["id"])
    signed = _existing_types()
    stamp = generated or date.today().isoformat()

    untyped = [c for c in concepts if c["id"] not in signed]
    parts: list[str] = [
        "<!-- Generated by tm_knowledge.stage0.typing. Do not hand-edit. -->",
        "",
        "# The concept typing pass — the evidence",
        "",
        f"**Generated {stamp}** by `tmk-typing --write`, from `eval/gold/concepts.yaml` and "
        "the pinned snapshot.",
        "",
        "## What this is",
        "",
        "You ruled on OQ-0001: *“Use those four groups — come back to me with the list of "
        f"52 to sort.”* Here is the list. There are **{len(concepts)}** approved concepts, "
        f"of which **{len(untyped)}** are not yet sorted.",
        "",
        "Sort them in `data/derived/concept-typing.xlsx`. The `type` column is a dropdown "
        "with the five values below; this document is the evidence to sort by, so keep it "
        "open beside the spreadsheet.",
        "",
        "| group | what it means |",
        "|---|---|",
        *[f"| `{value}` | {meaning} |" for value, meaning in GROUPS],
        "",
        "**Leaving a row blank is fine and is not the same as `none_of_these`.** A blank "
        "says *not yet sorted* and comes back on the next pass. `none_of_these` says *the "
        "four groups do not fit this one*, which is evidence about the taxonomy — and if a "
        "lot of rows come back that way, the taxonomy is what needs revisiting, not the "
        "rows.",
        "",
        "**No concept below has been typed by a machine, and none will be.** Which group a "
        "concept belongs in is a legal judgement, and a taxonomy filled in by a tool reads "
        "as authoritative while having been written by nobody.",
        "",
        "## The concepts",
        "",
    ]

    for concept in concepts:
        existing = signed.get(concept["id"])
        heading = f"### `{concept['id']}` — {concept['pref_label']}"
        if existing:
            heading += (
                f"  *(already sorted: `{existing['type']}`, "
                f"{existing.get('approved_by') or 'unsigned'})*"
            )
        parts.append(heading)
        parts.append("")
        if concept.get("alt_labels"):
            parts.append("*Also called:* " + ", ".join(concept["alt_labels"]))
        if concept.get("not_labels"):
            parts.append(
                "*Explicitly **not** the same as:* "
                + ", ".join(f"**{label}**" for label in concept["not_labels"])
            )
        if concept.get("broader") or concept.get("narrower"):
            wider = ", ".join(concept.get("broader") or ()) or "—"
            narrower = ", ".join(concept.get("narrower") or ()) or "—"
            parts.append(f"*Broader:* {wider} · *Narrower:* {narrower}")
        if concept.get("legislative_basis"):
            parts.append("*Legislative basis:* " + ", ".join(concept["legislative_basis"]))
        if concept.get("notes"):
            parts.append("")
            parts.append(f"> {concept['notes']}")
        parts.append("")
        for ref in concept.get("definition_sources") or ():
            chunk = corpus.chunks.get(ref.split("~")[0]) or corpus.chunks.get(ref)
            if chunk is None:
                parts.append(f"- `{ref}` — not resolvable in the pinned snapshot")
                continue
            text = chunk.text
            excerpt = text if len(text) <= 700 else text[:700].rsplit(" ", 1)[0] + " …"
            parts.append(f"- **`{ref}`** — {excerpt}")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def write_report(path: Path | None = None, generated: str | None = None) -> Path:
    path = path or REPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(generated), encoding="utf-8")
    return path

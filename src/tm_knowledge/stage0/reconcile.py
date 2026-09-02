"""The return leg's second half: record the round, then retire what it settled.

`tmk-transcribe` moves approved records into `eval/gold/`. That leaves the repo
in the one state ADR-0043 consequence 6 forbids — the same record present twice,
approved in `eval/gold/` and unapproved in `review/seed/` — and `tmk-seed`
correctly calls it a defect, because an id is never used twice
(`IDENTIFIERS.md` §3). This module closes that.

Two outputs, and the order between them is the point:

1. **The ledger**, into `review/decisions/`. Every seed record the round
   touched, with the verdict, the reviewer's own words and what became of it.
   `review/README.md` says why this is data rather than paperwork: a rejection
   with a reason is a negative example Stage 10 consumes, and a rejection that
   exists only as a deleted row is nothing at all.
2. **The pruning**, in `review/seed/`. A seed record whose id now appears in
   `eval/gold/` is removed; everything else — unreviewed, amended, rejected —
   stays exactly where it is. **Rejected records are kept on purpose.** They
   have no approved twin, so they are not the duplication the rule is about, and
   other seed records point at them (`must_not_infer: PU-0017`); removing them
   would turn a recorded rejection into a dangling pointer.

**The pruning is textual and then verified.** A seed file is hand-written YAML
whose comments carry the two decisions the whole set turns on — the entity
annotation rule and the candidate predicate list — so it is edited by removing
the lines of the entries that go, never by re-serialising the document. That is
crude enough to deserve a proof, so every rewrite is parsed back and compared
against what should have survived, field by field, before anything is written.
A mismatch refuses the whole file (ADR-0049).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import goldset, seed as seed_module
from tm_knowledge.stage0.intake import sheets
from tm_knowledge.stage0.transcribe import (
    VERDICTS,
    Addendum,
    _date as _iso_date,
    _text,
)

__all__ = [
    "DECISIONS_DIR",
    "Outcome",
    "Round",
    "read_round",
    "prune",
    "render_ledger",
    "ledger_data",
]

DECISIONS_DIR = REPO_ROOT / "review" / "decisions"

_ENTRY = re.compile(r"^  - seed_id: (SEED-[A-Z]{2}-[0-9]{4})\s*$")


class ReconcileRefused(Exception):
    """A rewrite that did not verify. Nothing was written."""


@dataclass(frozen=True, slots=True)
class Outcome:
    """What one row of the returned workbook came to."""

    record_type: str
    identifier: str
    seed_id: str | None
    verdict: str
    correction: str | None
    approved_by: str | None
    approved_date: str | None
    #: `approved` · `held` · `rejected` · `unparseable`
    state: str
    note: str | None = None
    #: True when an addendum supplied the verdict or the signature rather than
    #: the reviewer's own cell. The ledger says so, because how a record came to
    #: be approved is part of the record of its approval (ADR-0051).
    by_instruction: bool = False

    @property
    def retire(self) -> bool:
        return self.state == "approved"


@dataclass
class Round:
    """One returned workbook, read as a set of decisions."""

    workbook: Path
    #: The instruction file applied to this reading, where one was.
    addendum: Addendum | None = None
    outcomes: list[Outcome] = field(default_factory=list)
    #: (parent id, child sheet, row, verdict, correction) for every child row a
    #: reviewer marked anything other than `correct`.
    child_marks: list[tuple[str, str, int, str, str | None]] = field(
        default_factory=list
    )
    reviewers: tuple[str, ...] = ()

    def of(self, state: str) -> list[Outcome]:
        return [o for o in self.outcomes if o.state == state]

    @property
    def reviewed(self) -> int:
        return sum(1 for o in self.outcomes if o.verdict != "unreviewed")


# ---------------------------------------------------------------------------
# Reading the returned workbook
# ---------------------------------------------------------------------------


def read_round(
    path: Path,
    gold_ids: set[str] | None = None,
    addendum: Addendum | None = None,
) -> Round:
    """Read a returned review workbook into outcomes. Writes nothing.

    `gold_ids` decides `approved` from `held`: a row is approved when the record
    it names actually reached `eval/gold/`. Asking the gold set rather than
    re-deriving the gate keeps one gate — `tmk-transcribe`'s — and makes this
    command a reporter of what happened rather than a second opinion on it.
    """
    from openpyxl import load_workbook

    if gold_ids is None:
        gold_ids = _gold_ids()

    book = load_workbook(path, data_only=True)
    result = Round(workbook=path, addendum=addendum)
    reviewers: set[str] = set()

    for spec in sheets():
        if spec.name not in book.sheetnames:
            continue
        sheet = book[spec.name]
        headers = {
            _text(cell.value): index
            for index, cell in enumerate(sheet[1], start=1)
            if _text(cell.value)
        }
        if "verdict" not in headers:
            continue

        def cell(row, name):
            index = headers.get(name)
            return None if index is None else row[index - 1].value

        for number, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            if all(_text(c.value) is None for c in row):
                continue
            raw = _text(cell(row, "verdict"))
            verdict = raw.strip().lower() if raw else "unreviewed"
            correction = _text(cell(row, "correction"))

            if spec.is_child:
                parent = _text(cell(row, "parent_id"))
                if verdict != "correct" and parent:
                    result.child_marks.append(
                        (parent, spec.name, number, verdict, correction)
                    )
                continue

            identifier = _text(cell(row, "id"))
            if identifier is None:
                continue
            approved_by = _text(cell(row, "approved_by"))
            approved_date = _date_text(cell(row, "approved_date"))

            # The same instruction the transcriber applied, applied here, so the
            # ledger describes the run that produced `eval/gold/` rather than a
            # second reading of the same workbook.
            instructed = False
            if addendum is not None:
                ruled = addendum.verdict_for(identifier)
                if ruled is not None and ruled != verdict:
                    verdict, instructed = ruled, True
                if (
                    addendum.sign_unsigned_correct
                    and verdict == "correct"
                    and not approved_by
                ):
                    approved_by = addendum.reviewer
                    approved_date = addendum.recorded_on
                    instructed = True
            if approved_by:
                reviewers.add(approved_by)

            if verdict != "unreviewed" and verdict not in VERDICTS:
                state, note = "unparseable", f"verdict cell reads {raw!r}"
            elif verdict == "reject":
                state, note = "rejected", None
            elif identifier in gold_ids:
                state, note = "approved", None
            else:
                state, note = "held", None

            result.outcomes.append(
                Outcome(
                    record_type=spec.record_type,
                    identifier=identifier,
                    seed_id=_text(cell(row, "seed_id")),
                    verdict=verdict,
                    correction=correction,
                    approved_by=approved_by,
                    approved_date=approved_date,
                    state=state,
                    note=note,
                    by_instruction=instructed,
                )
            )

    result.reviewers = tuple(sorted(reviewers))
    return result


def _date_text(value: Any) -> str | None:
    """The approval date as ISO where it can be read, and verbatim where not.

    The ledger differs from the transcriber here on purpose. `transcribe`
    refuses a date it cannot resolve, because a wrong date would be written into
    approved space. The ledger is a record of what arrived, so an unreadable
    date is reported as the reviewer typed it rather than dropped.
    """
    if value is None:
        return None
    try:
        return _iso_date("approved_date", value)
    except ValueError:
        return _text(value)


def _gold_ids() -> set[str]:
    gold = goldset.load()
    return {
        str(record.get("id")) for _, record in gold.all_records() if record.get("id")
    }


# ---------------------------------------------------------------------------
# The ledger
# ---------------------------------------------------------------------------


def ledger_data(round_: Round, *, as_of: str | None = None) -> dict[str, Any]:
    """The machine-readable half. What Stage 10 active learning reads."""
    return {
        "source_workbook": round_.workbook.name,
        "addendum": round_.addendum.source.name if round_.addendum and round_.addendum.source else None,
        "recorded_on": as_of or date.today().isoformat(),
        "reviewers": list(round_.reviewers),
        "counts": {
            state: len(round_.of(state))
            for state in ("approved", "held", "rejected", "unparseable")
        },
        "decisions": [
            {
                "seed_id": outcome.seed_id,
                "id": outcome.identifier,
                "record_type": outcome.record_type,
                "verdict": outcome.verdict,
                "outcome": outcome.state,
                "approved_by": outcome.approved_by,
                "approved_date": outcome.approved_date,
                "correction": outcome.correction,
                "note": outcome.note,
                "by_instruction": outcome.by_instruction,
            }
            for outcome in round_.outcomes
        ],
        "child_marks": [
            {
                "parent_id": parent,
                "sheet": sheet,
                "row": row,
                "verdict": verdict,
                "correction": correction,
            }
            for parent, sheet, row, verdict, correction in round_.child_marks
        ],
    }


_STATE_HEADING = {
    "rejected": "Rejected — the record should not exist",
    "held": "Held — read, not yet in the gold set",
    "approved": "Approved — now in eval/gold/",
    "unparseable": "Unreadable verdict — fix the cell and hand it back",
}


def render_ledger(round_: Round, *, as_of: str | None = None) -> str:
    """The readable half. One decision per line, the reviewer's words verbatim."""
    stamp = as_of or date.today().isoformat()
    lines = [
        f"# Seed review — `{round_.workbook.name}`",
        "",
        "The decisions a Trade Mark expert recorded on the seed example set, as",
        "they arrived. This file is the round's audit trail: it is what remains",
        "after the approved records move into `eval/gold/` and their seed copies",
        "are retired, and it is the only place the rejections and the reviewer's",
        "own wording survive. Do not edit it to tidy a correction — the words are",
        "the content (`review/README.md`).",
        "",
        f"**Recorded:** {stamp} · **Reviewer(s):** "
        + (", ".join(round_.reviewers) or "not named in the workbook"),
        "",
        f"{round_.reviewed} of {len(round_.outcomes)} records carry a verdict.",
        "",
    ]
    if round_.addendum is not None:
        instructed = [o for o in round_.outcomes if o.by_instruction]
        lines += [
            f"**Addendum applied:** `{round_.addendum.source.name}`, recorded "
            f"{round_.addendum.recorded_on} by {round_.addendum.reviewer} — "
            f"{len(instructed)} record(s). A row marked *by instruction* below "
            "took its verdict or its signature from that file rather than from "
            "the reviewer's own cell (ADR-0051).",
            "",
        ]
    lines += [
        "| outcome | records |",
        "|---|---|",
    ]
    for state in ("approved", "held", "rejected", "unparseable"):
        lines.append(f"| {state} | {len(round_.of(state))} |")
    lines.append("")

    for state in ("rejected", "unparseable", "held", "approved"):
        entries = round_.of(state)
        if not entries:
            continue
        lines += [f"## {_STATE_HEADING[state]}", ""]
        for outcome in entries:
            head = f"- **{outcome.identifier}** ({outcome.record_type}) — {outcome.verdict}"
            if outcome.approved_by:
                head += f", signed {outcome.approved_by}"
                if outcome.approved_date:
                    head += f" {outcome.approved_date}"
            if outcome.by_instruction:
                head += " · *by instruction*"
            lines.append(head)
            if outcome.note:
                lines.append(f"  - {outcome.note}")
            if outcome.correction:
                lines.append(f"  - > {' '.join(outcome.correction.split())}")
        lines.append("")

    if round_.child_marks:
        lines += [
            "## Marks on child rows",
            "",
            "A relevance grade or an expected inference, marked on its own row. A",
            "rejected entry is dropped from its parent; anything else unsettled",
            "holds the parent whole, because the parent's list is part of it.",
            "",
        ]
        for parent, sheet, row, verdict, correction in round_.child_marks:
            line = f"- **{parent}** · `{sheet}` row {row} — {verdict}"
            if correction:
                line += f" — > {' '.join(correction.split())}"
            lines.append(line)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Pruning review/seed/
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Pruned:
    """What one seed file lost."""

    path: Path
    retired: tuple[str, ...]
    remaining: int
    #: `rewritten` · `deleted` · `unchanged`
    outcome: str


def prune(
    gold_ids: set[str] | None = None,
    root: Path | None = None,
    *,
    write: bool = False,
) -> list[Pruned]:
    """Remove every seed record whose id is now in `eval/gold/`.

    Verified before it is written: the rewritten text is parsed back, and the
    envelopes that survive must be exactly the ones expected, each with a record
    identical to the one it had. Anything else raises rather than writes.
    """
    if gold_ids is None:
        gold_ids = _gold_ids()
    loaded = seed_module.load(root)
    results: list[Pruned] = []

    for record_type, path in sorted(loaded.files.items(), key=lambda item: item[1].name):
        envelopes = [e for e in loaded.envelopes if e.source_file == path]
        retiring = {
            e.seed_id for e in envelopes if str(e.record.get("id")) in gold_ids
        }
        if not retiring:
            results.append(Pruned(path, (), len(envelopes), "unchanged"))
            continue

        survivors = [e for e in envelopes if e.seed_id not in retiring]
        if not survivors:
            if write:
                path.unlink()
            results.append(
                Pruned(path, tuple(sorted(retiring)), 0, "deleted")
            )
            continue

        text = _remove_entries(path.read_text(encoding="utf-8"), retiring)
        _verify(path, text, survivors)
        if write:
            path.write_text(text, encoding="utf-8")
        results.append(
            Pruned(path, tuple(sorted(retiring)), len(survivors), "rewritten")
        )
    return results


def _remove_entries(text: str, retiring: set[str]) -> str:
    """Drop the lines of each named envelope, and nothing else.

    An entry runs from its `- seed_id:` line to the line before the next one at
    the same indent, or to the end of the file. A comment banner sitting above a
    removed entry is left alone: it introduces the group, not that one record,
    and it will sit above whichever entry survives next.
    """
    lines = text.splitlines(keepends=True)
    starts: list[tuple[int, str]] = [
        (index, match.group(1))
        for index, line in enumerate(lines)
        if (match := _ENTRY.match(line.rstrip("\n")))
    ]
    if not starts:
        raise ReconcileRefused("no `- seed_id:` entries found; the file is not a seed file")

    kept: list[str] = []
    boundaries = [index for index, _ in starts] + [len(lines)]
    kept.extend(lines[: boundaries[0]])
    for position, (index, seed_id) in enumerate(starts):
        block = lines[index : boundaries[position + 1]]
        if seed_id in retiring:
            continue
        kept.extend(block)
    return "".join(kept)


def _verify(path: Path, text: str, survivors) -> None:
    """Parse the rewrite back and insist it holds exactly what it should."""
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ReconcileRefused(f"{path.name}: the rewrite is not valid YAML: {error}")
    if not isinstance(document, dict) or not isinstance(document.get("seeds"), list):
        raise ReconcileRefused(
            f"{path.name}: the rewrite is not a mapping with a `seeds` list"
        )
    got = document["seeds"]
    if len(got) != len(survivors):
        raise ReconcileRefused(
            f"{path.name}: the rewrite holds {len(got)} envelope(s), expected "
            f"{len(survivors)}"
        )
    for entry, envelope in zip(got, survivors, strict=True):
        if entry.get("seed_id") != envelope.seed_id:
            raise ReconcileRefused(
                f"{path.name}: expected {envelope.seed_id} where the rewrite has "
                f"{entry.get('seed_id')!r}"
            )
        if entry.get("record") != envelope.record:
            raise ReconcileRefused(
                f"{path.name}: {envelope.seed_id}'s record changed during the "
                "rewrite. Nothing was written"
            )


def ledger_paths(workbook: Path, out_dir: Path | None = None) -> tuple[Path, Path]:
    """Where this round's ledger goes: named after the workbook it came from."""
    out_dir = out_dir or DECISIONS_DIR
    slug = re.sub(r"[^a-z0-9]+", "-", workbook.stem.lower()).strip("-")
    return out_dir / f"{slug}.md", out_dir / f"{slug}.yaml"


def write_ledger(
    round_: Round,
    out_dir: Path | None = None,
    *,
    as_of: str | None = None,
    write: bool = False,
) -> tuple[Path, Path]:
    markdown, data = ledger_paths(round_.workbook, out_dir)
    if write:
        markdown.parent.mkdir(parents=True, exist_ok=True)
        markdown.write_text(render_ledger(round_, as_of=as_of), encoding="utf-8")
        data.write_text(
            yaml.safe_dump(
                ledger_data(round_, as_of=as_of),
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
                width=100,
            ),
            encoding="utf-8",
        )
    return markdown, data

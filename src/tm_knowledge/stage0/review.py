"""The seed-review leg: a reviewed row, and where it is allowed to go.

`transcribe.py` answers "what record is on this row". This module answers the
question that comes back with a *reviewed* workbook and not with a blank one:
**has a person accepted this row, and may it therefore be written into approved
space?**

The distinction is not pedantry. The workbook that came back on 2026-08-25 is
not a form an expert filled in — it is 368 machine-written example records over
s 43, handed out for correction because correcting a wrong answer is cheaper
than composing a right one. Every row in it began as LLM output. Transcribing
the file wholesale would move that output into `eval/gold/`, which is the
measurement standard the entire programme is scored against, and the harness
would then certify every later stage against a gold set that is mostly
unreviewed machine writing. That is exactly the failure CLAUDE.md rule 4 exists
to prevent, and it would be invisible: the records validate, the refs resolve,
the spans land, and nothing about a well-formed record says nobody read it.

So the review columns are not decoration and they are not free-text notes. They
are the gate.

## The gate

A row reaches `eval/gold/` only when both halves hold:

1. the expert's `verdict` is `correct` — they read the machine's example and
   accepted it as written; and
2. `approved_by` **and** `approved_date` are both present — the approval
   artefact of ADR-0039, which is a name and a date and nothing else.

Everything else is a candidate and goes to `review/decisions/` with its verdict
recorded: rejected rows, amended rows, rows nobody reached, and rows that were
marked correct but never signed. Nothing is discarded — `review/README.md` is
explicit that rejections are as valuable as approvals, and Stage 10's active
learning consumes them.

## What this module will not do

**It will not apply a correction.** An `amend` verdict arrives with prose:
*"Must, while the usage of the word should might be confusing here, if an
examiner is clearly satisfied that confusion is likely to occur then they must
raise a section 43 grounds for rejection."* Reading that as `modality: must` is
a legal reading of an expert's sentence, and writing it into a record is
authoring legal content under someone else's name (rule 1). The correction is
carried verbatim to `review/decisions/` and reported as work for the expert. The
same holds for the `GS--relevant` corrections that open with a bare digit: `"3,
the section hinges on the word connotation"` almost certainly means the grade
should be 3, and *almost certainly* is not a standard this repo writes into a
measurement set.

**It will not repair a verdict it cannot read.** `corrrect` and `rejext` are
obviously typos and are still not verdicts. They are reported by name and the
row is treated as unreviewed until the expert confirms, which costs a minute and
is recoverable; guessing costs the guarantee that a verdict in `review/` is a
verdict a person actually gave (rule 6).

What it *will* do is normalise what carries no judgement: case and surrounding
whitespace on a verdict (`Correct`, `amend ` — the same word, typed by a person
into a spreadsheet), and a date written in the Australian order when the day is
past the twelfth and the reading is therefore forced.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.provenance import ReviewStatus

__all__ = [
    "VERDICTS",
    "DECISIONS_DIR",
    "Review",
    "Decision",
    "UnreadableVerdict",
    "AmbiguousDate",
    "read_verdict",
    "read_approved_date",
    "route",
    "write_decisions",
]

#: Where the audit trail lives. Named by `review/README.md`, which calls it
#: "the record of what was approved, rejected or deferred".
DECISIONS_DIR = REPO_ROOT / "review" / "decisions"

#: The verdict vocabulary, as the returned workbook's own instructions state it:
#: "one of: unreviewed, correct, amend, reject".
VERDICTS: tuple[str, ...] = ("unreviewed", "correct", "amend", "reject")

#: The five columns the seed pack adds. They describe the *review*, not the
#: record, so none of them is ever written into a gold record — `seed_id`,
#: `why_this_example` and `passage` are printed for the reader and are
#: regenerated from the snapshot, and the schemas set `additionalProperties:
#: false` besides.
REVIEW_HEADERS: tuple[str, ...] = (
    "seed_id",
    "why_this_example",
    "passage",
    "verdict",
    "correction",
)

#: Verdict -> where a row of that verdict stands, before approval is checked.
_STATUS: dict[str, ReviewStatus] = {
    "correct": ReviewStatus.APPROVED,
    "amend": ReviewStatus.IN_REVIEW,
    "reject": ReviewStatus.REJECTED,
    "unreviewed": ReviewStatus.CANDIDATE,
}


class UnreadableVerdict(ValueError):
    """A verdict cell holding something that is not one of `VERDICTS`."""


class AmbiguousDate(ValueError):
    """A date whose day and month cannot be told apart."""


def read_verdict(value: Any) -> str:
    """A verdict cell to one of `VERDICTS`. Blank reads as `unreviewed`.

    Case and surrounding whitespace are normalised because they carry no
    judgement: `Correct`, `correct` and `amend ` are one word typed by a person
    into a spreadsheet. Anything else raises — see the module docstring on why
    `corrrect` is not quietly read as `correct`.
    """
    if value is None:
        return "unreviewed"
    text = str(value).strip().lower()
    if not text:
        return "unreviewed"
    if text not in VERDICTS:
        raise UnreadableVerdict(
            f"verdict is {str(value).strip()!r}, which is not one of "
            + ", ".join(VERDICTS)
            + ". The row is carried to review/decisions/ as unreviewed; nothing "
            "here will decide what was meant"
        )
    return text


def read_approved_date(value: Any) -> str | None:
    """An `approved_date` cell to the ISO date the schemas require.

    Excel hands back a `datetime` when the cell was typed as a date, and a
    string when it was typed as text. The string case is where the care is
    needed: the workbook came back with `25/08/2026`, which is Australian day
    order, and the schema wants `2026-08-25`.

    A slash date is converted **only when the reading is forced** — the day is
    past the twelfth, so it cannot be a month. `05/08/2026` raises instead.
    Australian order is this repo's convention and would usually be the right
    guess, but an approval date is half of the approval artefact itself
    (ADR-0039), and a guessed date is a falsified audit trail rather than an
    inconvenience.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    text = str(value).strip()
    if not text:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text

    slashed = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if slashed is None:
        raise ValueError(
            f"approved_date is {text!r}, which is not a date this can read. "
            "Write it as YYYY-MM-DD"
        )
    first, second, year = (int(part) for part in slashed.groups())
    if first > 12 and second <= 12:  # forced: the first field cannot be a month
        return f"{year:04d}-{second:02d}-{first:02d}"
    raise AmbiguousDate(
        f"approved_date is {text!r}, and the day and month cannot be told "
        "apart. Write it as YYYY-MM-DD rather than leaving it to be guessed — "
        "an approval date is half of the approval record"
    )


@dataclass(frozen=True, slots=True)
class Review:
    """The five review columns off one row, read."""

    seed_id: str | None
    why_this_example: str | None
    passage: str | None
    verdict: str
    correction: str | None
    #: The verdict exactly as typed, when it differed from the normalised form.
    verdict_as_written: str | None = None

    @property
    def is_amended(self) -> bool:
        return self.verdict == "amend"


@dataclass(frozen=True, slots=True)
class Decision:
    """One reviewed row, and what became of it. The audit trail's unit.

    The seed record is carried whole, including on a rejection. A rejected
    candidate with its passage and the expert's reason is training data for
    Stage 10 and evidence for anyone asking why a term is absent; a rejection
    recorded as an id and nothing else is neither.
    """

    record_id: str
    record_type: str
    sheet: str
    row: int
    verdict: str
    review_status: ReviewStatus
    destination: str
    reason: str
    correction: str | None
    approved_by: str | None
    approved_date: str | None
    seed_id: str | None
    record: dict[str, Any]
    #: Set when the verdict cell could not be read, or contradicted itself.
    flag: str | None = None

    def as_dict(self) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "seed_id": self.seed_id,
            "sheet": self.sheet,
            "row": self.row,
            "verdict": self.verdict,
            "review_status": self.review_status.value,
            "destination": self.destination,
            "reason": self.reason,
            "approved_by": self.approved_by,
            "approved_date": self.approved_date,
            "correction": self.correction,
        }
        if self.flag:
            entry["flag"] = self.flag
        # Rule 8: the seed is machine writing and says so wherever it is stored.
        entry["origin"] = "machine_seed"
        entry["record"] = self.record
        return entry


def route(
    review: Review,
    approved_by: str | None,
    approved_date: str | None,
) -> tuple[str, ReviewStatus, str, str | None]:
    """The gate. Returns (destination, review_status, reason, flag).

    Destination is `gold` or `review`. Nothing else decides this; in particular
    a record's own soundness does not — a perfectly formed record nobody read is
    still unreviewed machine output.
    """
    signed = bool(approved_by) and bool(approved_date)
    half_signed = bool(approved_by) != bool(approved_date)
    status = _STATUS[review.verdict]

    if review.verdict == "reject":
        return "review", ReviewStatus.REJECTED, "verdict is `reject`", None

    if review.verdict == "amend":
        return (
            "review",
            ReviewStatus.IN_REVIEW,
            "verdict is `amend`; the correction is prose and is not applied here",
            None,
        )

    if review.verdict == "unreviewed":
        return (
            "review",
            ReviewStatus.CANDIDATE,
            "no verdict; the row is machine-written and nobody has read it",
            None,
        )

    # verdict == "correct" from here.
    if review.correction:
        return (
            "review",
            ReviewStatus.IN_REVIEW,
            "verdict is `correct` but a correction was written; the two disagree",
            "verdict and correction conflict — ask the reviewer which stands",
        )
    if half_signed:
        missing = "approved_by" if not approved_by else "approved_date"
        return (
            "review",
            ReviewStatus.IN_REVIEW,
            f"verdict is `correct` but {missing} is blank; approval is the pair",
            f"{missing} is blank while the other half is filled",
        )
    if not signed:
        return (
            "review",
            ReviewStatus.IN_REVIEW,
            "verdict is `correct` but the row is unsigned; reviewed is not approved",
            None,
        )
    return "gold", ReviewStatus.APPROVED, "reviewed `correct` and signed", None


def render(decisions: list[Decision]) -> str:
    """One decisions file's YAML, deterministically — same rules as the gold set."""
    return yaml.safe_dump(
        [decision.as_dict() for decision in decisions],
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )


def write_decisions(
    decisions: list[Decision],
    decisions_dir: Path | None = None,
    *,
    source: str,
    write: bool = False,
) -> list[tuple[Path, str]]:
    """Write the audit trail, one file per record type.

    Outcomes match `transcribe.write_records`: `written`, `unchanged`,
    `would write`. Unlike the gold set this is *not* approved space, so writing
    here is safe — but it still honours `--write`, because a dry run that
    silently wrote half its output somewhere would be worse than no dry run.
    """
    decisions_dir = decisions_dir or DECISIONS_DIR
    by_type: dict[str, list[Decision]] = {}
    for decision in decisions:
        by_type.setdefault(decision.record_type, []).append(decision)

    outcomes: list[tuple[Path, str]] = []
    for record_type, group in sorted(by_type.items()):
        path = decisions_dir / f"{record_type.replace('_', '-')}.yaml"
        header = (
            f"# Seed-review decisions for {record_type}.\n"
            f"# Source: {source}\n"
            "# Machine-written seed records with a human's verdict against each.\n"
            "# NOT approved knowledge. Approved records live in eval/gold/.\n"
        )
        text = header + render(sorted(group, key=lambda d: d.record_id))
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

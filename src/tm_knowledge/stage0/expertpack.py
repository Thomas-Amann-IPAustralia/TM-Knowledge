"""The one request — everything worth asking a trade marks expert, in one pack.

Sessions S010 to S019 accumulated questions for a trade marks expert in six
different places: `review/questions/open-questions.yaml`, the `expert_should_check`
field of 208 authored records, an expert's own returned note from 2026-08-26, a
draft thresholds file, five signed relationships with a blank judgement field, and
`docs/EXPERT-REVIEW-SCOPE.md`, which listed them without being answerable. None of
those is a thing a person can fill in and hand back.

This module produces the two artefacts that are:

- `data/derived/expert-request.xlsx` — every question, in one workbook, ordered so
  that a reviewer who stops after twenty minutes has answered the most valuable
  twenty minutes' worth.
- `docs/EXPERT-REQUEST.md` — the covering note. Plain English, no record types, no
  ADR numbers, no field names. It says what we want, why we want it, and what
  happens to their answers.

**Two kinds of sheet, and the difference is load-bearing.**

`concepts` and `concept-types` are ordinary intake sheets. They keep the exact
column layout `tmk-transcribe` reads, so a corrected row becomes a record through
the single existing door and no new code touches `eval/gold/` (ADR-0048). The five
numbered sheets in front of them are **not** record sheets: they hold questions
whose answers are sentences, and a sentence comes back the way every other
reviewer instruction comes back — filed verbatim in `review/returned/` and applied
through an instruction file, never by an agent paraphrasing it into a record
(ADR-0051). `tmk-transcribe` iterates the sheets it knows and ignores the rest, so
the extra sheets cost the round trip nothing.

**Every pre-filled answer in here was written by a machine and read by nobody.**
That is said on the covering note, on the guide sheet, and on every sheet's own
banner, because a spreadsheet arriving with the answers already in it looks
exactly like a spreadsheet somebody else has already worked through — which is
the laundering CLAUDE.md rule 1 prohibits, in Excel (ADR-0092).

`approved_by` is left empty by this code in every row it writes, on both stores'
records, whatever the source record says about itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tm_knowledge.authored import store as authored_store
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0 import workbook as workbook_module
from tm_knowledge.stage0.intake import sheets

__all__ = [
    "WORKBOOK_PATH",
    "LETTER_PATH",
    "ROLE_TERMS",
    "duplicate_labels",
    "unjudged_modalities",
    "build_workbook",
    "write_workbook",
    "render_letter",
    "write_letter",
]

WORKBOOK_PATH = REPO_ROOT / "data" / "derived" / "expert-request.xlsx"
LETTER_PATH = REPO_ROOT / "docs" / "EXPERT-REQUEST.md"

#: The two intake sheets this pack uses. Every other record-type sheet is removed
#: rather than shipped empty: this is a request with a fixed budget of somebody's
#: attention, and eleven blank sheets spend some of it on deciding they are blank.
#: `tmk-transcribe` reads whichever sheets are present, so removal is free.
RECORD_SHEETS: tuple[str, ...] = ("concepts", "concept-types")

#: The nine terms the expert named on 2026-08-26 as needing a high-level
#: definition, in the order they wrote them. Their words, not a paraphrase — the
#: sheet asks them to define these and the list has to be recognisably the one
#: they gave us.
ROLE_TERMS: tuple[str, ...] = (
    "Registrar",
    "Delegate",
    "Examiner",
    "Decision Maker",
    "Office Practise",
    "Subject Matter Expert (SME)",
    "Oppositions",
    "Grounds for Rejection",
    "Adverse Report",
)

_VERDICTS: tuple[str, ...] = ("correct", "amend", "reject")

_HEADER_FILL = "FFEFEFEF"
_ANSWER_FILL = "FFFCE4D6"
_CONTEXT_FILL = "FFEFEFEF"


# ---------------------------------------------------------------------------
# Findings the sheets are built from
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Duplicate:
    """One term that names a signed concept and an authored concept at once."""

    label: str
    signed_id: str
    authored_id: str
    signed_note: str
    authored_note: str
    #: True when the authored record mentions the signed one somewhere in its
    #: envelope. Seven of ten do, and those are the design working: a new record
    #: that knows about the old one and argues for standing beside it.
    disclosed: bool


def duplicate_labels(
    gold: goldset.GoldSet | None = None,
    authored: authored_store.AuthoredSet | None = None,
) -> tuple[Duplicate, ...]:
    """Terms that are a preferred label in both stores.

    Compared on `pref_label` alone and deliberately not on `alt_labels`: an
    authored preferred label colliding with a signed *alternative* label is the
    same problem one step less visible, and this pass does not claim to find it
    (ADR-0101 consequence 3).
    """
    gold = gold or goldset.load()
    authored = authored if authored is not None else authored_store.load()

    signed = {
        str(record["pref_label"]).strip().lower(): record
        for record in gold["gold_concept"]
    }
    # Everything written *about* a concept, not only its own record. A collision
    # disclosed on the concept's typing is disclosed: the reviewer meets both
    # records in the same pack, and a check that missed that would report a
    # silent clash where somebody had in fact flagged it.
    said_about: dict[str, list[str]] = {}
    for entry in authored.entries:
        envelope = entry.envelope if isinstance(entry.envelope, dict) else {}
        about = str(
            entry.record.get("concept") or entry.record.get("id") or ""
        )
        said_about.setdefault(about, []).extend(
            str(part)
            for part in (
                entry.record.get("notes"),
                envelope.get("reasoning"),
                envelope.get("expert_should_check"),
                *(envelope.get("alternatives_considered") or ()),
            )
            if part
        )

    found: list[Duplicate] = []
    for entry in authored.of("gold_concept"):
        record = entry.record
        label = str(record.get("pref_label", "")).strip().lower()
        twin = signed.get(label)
        if twin is None:
            continue
        haystack = " ".join(said_about.get(str(record.get("id")), ()))
        found.append(
            Duplicate(
                label=str(record["pref_label"]),
                signed_id=str(twin["id"]),
                authored_id=str(record["id"]),
                signed_note=" ".join(str(twin.get("notes") or "").split()),
                authored_note=" ".join(str(record.get("notes") or "").split()),
                disclosed=str(twin["id"]) in haystack,
            )
        )
    return tuple(sorted(found, key=lambda item: (item.disclosed, item.authored_id)))


@dataclass(frozen=True, slots=True)
class Unjudged:
    """A signed relationship whose force nobody recorded."""

    identifier: str
    subject: str
    predicate: str
    obj: str
    supporting_text: str


def unjudged_modalities(gold: goldset.GoldSet | None = None) -> tuple[Unjudged, ...]:
    """Signed relationships with no `modality`.

    These are the one part of the pack an agent is barred from answering even
    under the amended rules: the field sits inside a record a person signed, and
    writing into it puts unreviewed content inside a signature. So it is asked
    rather than authored, and the answer arrives as words (ADR-0051).
    """
    gold = gold or goldset.load()
    return tuple(
        Unjudged(
            identifier=str(record["id"]),
            subject=str(record.get("subject") or ""),
            predicate=str(record.get("predicate") or ""),
            obj=str(record.get("object") or ""),
            supporting_text=" ".join(str(record.get("supporting_text") or "").split()),
        )
        for record in gold["gold_relationship"]
        if not record.get("modality")
    )


def _role_coverage(
    gold: goldset.GoldSet, authored: authored_store.AuthoredSet
) -> dict[str, str]:
    """For each named role term, where — if anywhere — the vocabulary holds it.

    Three states and they are not the same ask. A term we hold as a preferred
    label needs checking; one we hold only as an alternative label is half
    there; one we hold nowhere has to be written from scratch, and that is the
    request that costs the expert the most.
    """
    preferred: dict[str, str] = {}
    alternates: dict[str, str] = {}
    for source, records in (
        ("signed", gold["gold_concept"]),
        ("written by us", list(authored["gold_concept"])),
    ):
        for record in records:
            preferred.setdefault(str(record["pref_label"]).strip().lower(), source)
            for label in record.get("alt_labels") or ():
                alternates.setdefault(str(label).strip().lower(), source)

    coverage: dict[str, str] = {}
    for term in ROLE_TERMS:
        key = term.split(" (")[0].strip().lower()
        forms = {key, key.rstrip("s") if key.endswith("s") else key, key + "s"}

        exact = next(iter(forms & preferred.keys()), None)
        if exact is not None:
            coverage[term] = f"we hold this word ({preferred[exact]})"
            continue
        alias = next(iter(forms & alternates.keys()), None)
        if alias is not None:
            coverage[term] = (
                "we hold it only as another name for something else "
                f"({alternates[alias]})"
            )
            continue
        # A label like "the registrar's delegate" holds *delegate* without being
        # it. Reporting that as absent would send the expert to write a
        # definition for a word we half-hold, which is a different and smaller
        # job than the one the sheet would be describing.
        inside = next(
            (
                (label, source)
                for label, source in {**alternates, **preferred}.items()
                for form in forms
                if _word_in(form, label)
            ),
            None,
        )
        if inside is not None:
            label, source = inside
            coverage[term] = (
                f"we hold it only inside a longer phrase — “{label}” ({source})"
            )
            continue
        coverage[term] = "WE DO NOT HOLD THIS WORD AT ALL"
    return coverage


def _word_in(needle: str, haystack: str) -> bool:
    """Whole-word containment. Substring matching alone would report *examiner*
    as held by *examiner research* and *opposition* as held by anything ending
    in it, which overstates coverage in exactly the direction that costs the
    expert nothing to correct and costs us a definition we never collect."""
    import re

    return re.search(rf"\b{re.escape(needle)}\b", haystack) is not None


# ---------------------------------------------------------------------------
# The questions whose answers are sentences
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class BigQuestion:
    number: str
    question: str
    why: str
    what_we_think: str
    what_it_changes: str


def big_questions(counts: dict[str, int]) -> tuple[BigQuestion, ...]:
    """The cross-cutting judgements — the ones where a paragraph from them is
    worth more than any number of corrected rows.

    Each is drawn from something already in the repository and each names what
    it changes if the answer is no, because a question whose consequence is not
    stated reads as a survey.
    """
    return (
        BigQuestion(
            "1",
            "We sort every idea in the vocabulary into one of nine groups. Are "
            "nine groups the right way to cut it up, and are these the right nine?",
            "The first four groups came from the project owner. The other five "
            "were invented by us on 9 September and nobody who knows trade marks "
            "has looked at them. Everything else in the vocabulary is built on "
            "top of this, so if it is wrong it is wrong everywhere.",
            "Four groups sort an idea by the part it plays in reaching a "
            "decision: a reason to refuse, a question to answer, something that "
            "feeds the answer, a way out. Five sort it by its part in the "
            "process around that: a person who acts, the thing being examined, a "
            "step, a document, an outside treaty.",
            f"All {counts['typings']} rows on the 'concept-types' sheet.",
        ),
        BigQuestion(
            "2",
            "Are 'examiner', 'delegate', 'decision maker' and 'the Registrar' "
            "four different things, or four ways of saying one thing?",
            "You told us in August that an examiner is delegated by the "
            "Registrar and that the distinction carries weight. We have kept "
            "them apart as separate ideas, but we do not know whether an "
            "examiner reading our output would find that helpful or pedantic.",
            "We hold them apart. We are not confident.",
            "How the system answers any question about who decides what — and "
            "roughly a dozen rows on the 'concept-types' sheet.",
        ),
        BigQuestion(
            "3",
            "You told us the office's real bar for accepting on doubt. We want "
            "to record it as a rule. Have we understood it, and where does it stop?",
            "You wrote: it is not enough for the individual examiner to doubt a "
            "connotation exists — the Registrar as a whole must, and an examiner "
            "would be expected to consult their team leader and the section 43 "
            "specialists first. That is the single most useful thing anybody has "
            "told this project and it is still sitting in your email rather than "
            "in the system.",
            "Nothing. We have not written it. We did not want to put words in "
            "your mouth about what examiners must do.",
            "Whether the system can say anything at all about how the "
            "presumption of registrability is actually applied.",
        ),
        BigQuestion(
            "4",
            "Is 'connotation' a separate question from 'likely to deceive or "
            "cause confusion', or does practice run the two together?",
            "We have treated them as two questions an examiner answers in turn. "
            "If in practice they are one judgement, we have split something that "
            "should not be split, and several rows follow from it.",
            "Two separate questions.",
            "Three rows on the 'concept-types' sheet, and how the system "
            "explains a section 43 objection.",
        ),
        BigQuestion(
            "5",
            "Is an exception the examiner *may* apply the same kind of thing as "
            "one they *must* apply?",
            "We have put both in one group. A discretionary escape and a "
            "mandatory one behave differently for anybody relying on the answer, "
            "and if they should be two groups we would rather split them before "
            "you spend time sorting rows.",
            "One group covers both.",
            "The 'exception' group, and possibly a tenth group.",
        ),
        BigQuestion(
            "6",
            "When the Manual says just 'section 15(1)' with no Act named, may we "
            "read that as the Trade Marks Act?",
            "You said yes in August — that it is safe given what this tool is "
            "for. The system that supplies our source text deliberately refuses "
            "to guess, so we want your answer written down against that refusal "
            "rather than inferred from it. If there are places the assumption is "
            "unsafe, those are the ones we need named.",
            "We follow your answer, but we have not recorded where it stops.",
            "How every citation in the corpus is resolved.",
        ),
        BigQuestion(
            "7",
            "What would you have to see before you would let an examiner rely on "
            "this system without checking the source themselves?",
            "Every accuracy target in this project was invented by a machine "
            "with no basis for any of them. This one question is worth more than "
            "the whole numbers sheet. 'I would always check the source' is a "
            "completely legitimate answer and would change what we build.",
            "We guessed at numbers. See the 'how accurate' sheet.",
            "What the system is for, and how it is measured.",
        ),
        BigQuestion(
            "8",
            "What is missing? What would an examiner reach for that you have not "
            "seen anywhere in this pack?",
            "Everything here was found by machines reading the Manual. Anything "
            "examiners know that the Manual does not say in words is invisible "
            "to that method, and we have no way of discovering what we did not "
            "find.",
            "We do not know what we are missing.",
            "Where the next round of work goes.",
        ),
    )


# ---------------------------------------------------------------------------
# The workbook
# ---------------------------------------------------------------------------


def _style_header(sheet, row: int, headers: tuple[tuple[str, int, str], ...]) -> None:
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    for index, (title, width, fill) in enumerate(headers, start=1):
        cell = sheet.cell(row=row, column=index, value=title)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = sheet.cell(row=row + 1, column=1)


def _banner(sheet, title: str, body: str, span: int) -> None:
    """Every sheet says what it is and who wrote what is already in it.

    Repeated per sheet rather than stated once on the guide, because a reviewer
    opens a spreadsheet at whichever tab they were told to start on and the
    warning has to be where they are.
    """
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter

    sheet["A1"] = title
    sheet["A1"].font = Font(bold=True, size=13)
    sheet["A2"] = body
    sheet["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    last = get_column_letter(max(span, 2))
    sheet.merge_cells(f"A2:{last}2")
    sheet.row_dimensions[2].height = 90


def _wrap(sheet, row: int, columns: int, height: int | None = None) -> None:
    from openpyxl.styles import Alignment

    for column in range(1, columns + 1):
        sheet.cell(row=row, column=column).alignment = Alignment(
            vertical="top", wrap_text=True
        )
    if height is not None:
        sheet.row_dimensions[row].height = height


def _add_verdict_validation(sheet, letter: str, last_row: int) -> None:
    from openpyxl.worksheet.datavalidation import DataValidation

    validation = DataValidation(
        type="list", formula1='"' + ",".join(_VERDICTS) + '"', allow_blank=True
    )
    sheet.add_data_validation(validation)
    validation.add(f"{letter}4:{letter}{max(last_row, 4) + 50}")


def _sheet_big_questions(book, questions: tuple[BigQuestion, ...]) -> None:
    sheet = book.create_sheet("1 the big ones")
    _banner(
        sheet,
        "The eight questions we would ask if we could only ask eight",
        "If you read nothing else in this file, read this sheet. Each of these "
        "decides how dozens or hundreds of other rows should go, so an answer "
        "here saves you work everywhere else — and a wrong assumption here makes "
        "everything else wrong too. Write as much or as little as you like in the "
        "last column; a sentence is useful, a paragraph is better. "
        "'I don't know' and 'that is the wrong question' are both real answers.",
        6,
    )
    _style_header(
        sheet,
        3,
        (
            ("#", 5, _HEADER_FILL),
            ("The question", 62, _HEADER_FILL),
            ("Why we are asking you and not working it out", 62, _CONTEXT_FILL),
            ("What we have assumed so far", 46, _CONTEXT_FILL),
            ("What your answer changes", 40, _CONTEXT_FILL),
            ("YOUR ANSWER", 70, _ANSWER_FILL),
        ),
    )
    for offset, item in enumerate(questions):
        row = 4 + offset
        sheet.cell(row=row, column=1, value=item.number)
        sheet.cell(row=row, column=2, value=item.question)
        sheet.cell(row=row, column=3, value=item.why)
        sheet.cell(row=row, column=4, value=item.what_we_think)
        sheet.cell(row=row, column=5, value=item.what_it_changes)
        _wrap(sheet, row, 6, height=132)


def _sheet_duplicates(book, duplicates: tuple[Duplicate, ...]) -> None:
    sheet = book.create_sheet("2 same word twice")
    undisclosed = sum(1 for item in duplicates if not item.disclosed)
    _banner(
        sheet,
        "The same word is being used for two different ideas",
        f"We hold {len(duplicates)} words that name one idea you signed off last "
        f"year and a second idea we wrote this month. On {undisclosed} of them "
        "nothing in our system noticed. For each one: are these two names for the "
        "same thing, or two genuinely different things that happen to share a "
        "word? If they are the same, we delete ours and keep yours. If they are "
        "different, we need your help naming them apart. Ten minutes, and it "
        "stops a search returning two different answers to one question.",
        5,
    )
    _style_header(
        sheet,
        3,
        (
            ("The word", 30, _HEADER_FILL),
            ("What you signed off (and its reference)", 62, _CONTEXT_FILL),
            ("What we wrote (and its reference)", 62, _CONTEXT_FILL),
            ("Did we notice the clash?", 20, _CONTEXT_FILL),
            ("SAME THING, OR DIFFERENT? (and if different, what should each be "
             "called?)", 62, _ANSWER_FILL),
        ),
    )
    for offset, item in enumerate(duplicates):
        row = 4 + offset
        sheet.cell(row=row, column=1, value=item.label)
        sheet.cell(
            row=row,
            column=2,
            value=f"[{item.signed_id}] {item.signed_note or '(no note recorded)'}",
        )
        sheet.cell(
            row=row,
            column=3,
            value=f"[{item.authored_id}] {item.authored_note or '(no note recorded)'}",
        )
        sheet.cell(
            row=row,
            column=4,
            value="yes" if item.disclosed else "NO — nothing flagged this",
        )
        _wrap(sheet, row, 5, height=96)


def _sheet_missing_words(book, coverage: dict[str, str]) -> None:
    sheet = book.create_sheet("3 missing words")
    absent = sum(1 for state in coverage.values() if state.startswith("WE DO NOT"))
    _banner(
        sheet,
        "The words for who does what — and what they mean",
        "In August you said our vocabulary was built from one part of the Manual "
        "and gave a narrow view of the roles, and you named nine words needing a "
        f"plain high-level definition. {absent} of the nine are still not in our "
        "system in any form. And a thing we should say plainly: we do not hold a "
        "written definition for *any* word in this project — only pointers to "
        "passages. A sentence from you per row is the whole ask. Add rows at the "
        "bottom for anything else you would put on the list.",
        4,
    )
    _style_header(
        sheet,
        3,
        (
            ("The word", 32, _HEADER_FILL),
            ("Where we stand today", 52, _CONTEXT_FILL),
            ("YOUR PLAIN DEFINITION — one or two sentences", 78, _ANSWER_FILL),
            ("Anything an examiner would get wrong about it", 52, _ANSWER_FILL),
        ),
    )
    for offset, term in enumerate(ROLE_TERMS):
        row = 4 + offset
        sheet.cell(row=row, column=1, value=term)
        sheet.cell(row=row, column=2, value=coverage[term])
        _wrap(sheet, row, 4, height=58)
    row = 4 + len(ROLE_TERMS)
    sheet.cell(row=row, column=1, value="(add any other word here)")
    _wrap(sheet, row, 4, height=58)


def _sheet_modality(book, unjudged: tuple[Unjudged, ...]) -> None:
    sheet = book.create_sheet("4 must or may")
    _banner(
        sheet,
        "Five statements you signed off, where nobody recorded how binding they are",
        f"These {len(unjudged)} came back from you last year as correct, but the "
        "column saying whether the Manual is directing an examiner (*must*), "
        "permitting them (*may*), or advising them (*should*) was left blank. "
        "This is the one place in this whole pack where we are not allowed to "
        "guess even provisionally: the record already carries your name, and "
        "putting our guess inside something you signed is exactly what we have "
        "promised never to do. So it is blank until you say. Five dropdowns.",
        5,
    )
    _style_header(
        sheet,
        3,
        (
            ("Ref", 12, _HEADER_FILL),
            ("The statement", 56, _CONTEXT_FILL),
            ("The Manual's own words", 74, _CONTEXT_FILL),
            ("MUST / MAY / SHOULD", 22, _ANSWER_FILL),
            ("Comment, if it is none of those", 46, _ANSWER_FILL),
        ),
    )
    from openpyxl.worksheet.datavalidation import DataValidation

    validation = DataValidation(
        type="list", formula1='"must,may,should"', allow_blank=True
    )
    sheet.add_data_validation(validation)
    for offset, item in enumerate(unjudged):
        row = 4 + offset
        sheet.cell(row=row, column=1, value=item.identifier)
        sheet.cell(
            row=row,
            column=2,
            value=f"{item.subject} — {item.predicate} — {item.obj}",
        )
        sheet.cell(row=row, column=3, value=item.supporting_text)
        _wrap(sheet, row, 5, height=76)
    validation.add(f"D4:D{max(3 + len(unjudged), 4)}")


#: The accuracy questions, in the shape a person can answer without knowing what
#: any of the metric names mean. Every number in the middle column was invented
#: by a machine with no basis for it, which is said on the sheet.
_THRESHOLDS: tuple[tuple[str, str, str], ...] = (
    ("Getting a citation wrong",
     "we guessed: 1 error in 100 is tolerable",
     "A wrong citation sends an examiner to the wrong passage and does not look wrong."),
    ("Presenting Manual practice as if it were the Act",
     "we guessed: 1 error in 100 is tolerable",
     "The Manual states the Registrar's practice. It is not the law and does not bind the Registrar."),
    ("Saying 'current practice' without flagging that our copy has a date",
     "we guessed: 2 errors in 100 is tolerable",
     "Our copy of the Manual was taken on one day and says nothing about what changed after."),
    ("Stating something with no passage behind it",
     "we guessed: 2 errors in 100 is tolerable",
     "An assertion with nothing behind it cannot be checked by the examiner reading it."),
    ("Inventing a case citation that does not exist",
     "we guessed: never acceptable, not once",
     "Is zero the right bar, or is a bar nobody can hold at zero one everybody learns to ignore?"),
    ("Guessing which Act a bare section number refers to",
     "we guessed: never acceptable, not once",
     "Ties to question 6 on the first sheet."),
    ("The right passage is somewhere in the first ten search results",
     "we guessed: 85 times in 100",
     "How often a search is useful at all."),
    ("How much irrelevant material an examiner will tolerate around a good hit",
     "we guessed: 6 of 10 results should be relevant",
     "Too strict and the tool hides things; too loose and nobody trusts it."),
    ("How much of our output an examiner would accept without changing it",
     "we guessed: 6 in 10",
     "This is the number that decides whether any of this saves time."),
    ("Expert minutes to check 100 passages",
     "we guessed: 45 minutes",
     "If checking costs more than doing it by hand, the project does not pay."),
    ("Working days from the Manual changing to our copy catching up",
     "we guessed: 5 working days",
     "How stale is too stale."),
)


def _sheet_thresholds(book) -> None:
    sheet = book.create_sheet("5 how accurate")
    _banner(
        sheet,
        "How accurate does this have to be before an examiner could rely on it?",
        "Every number in the middle column was made up by a machine that has no "
        "way of knowing. They are here to be argued with, not filled in around. "
        "The one question underneath all of them is on the first sheet: what "
        "would you have to see before you would let an examiner use this without "
        "checking the source? 'I would always check the source' is a real answer "
        "and would change what we build rather than what we aim for.",
        4,
    )
    _style_header(
        sheet,
        3,
        (
            ("What could go wrong", 58, _HEADER_FILL),
            ("Our made-up target", 40, _CONTEXT_FILL),
            ("Why it matters", 62, _CONTEXT_FILL),
            ("YOUR VIEW — better, worse, or 'this is the wrong measure'",
             62, _ANSWER_FILL),
        ),
    )
    for offset, (risk, guess, why) in enumerate(_THRESHOLDS):
        row = 4 + offset
        sheet.cell(row=row, column=1, value=risk)
        sheet.cell(row=row, column=2, value=guess)
        sheet.cell(row=row, column=3, value=why)
        _wrap(sheet, row, 4, height=58)


def _concept_rows(
    authored: authored_store.AuthoredSet,
) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """The authored concepts, and the context columns beside each.

    `approved_by` and `approved_date` are emptied on the way out. The source
    records carry null in both and this does not trust that: the one cell an
    agent may never write is worth clearing twice (ADR-0079 guard 3).
    """
    records: list[dict[str, Any]] = []
    context: list[tuple[str, str]] = []
    for entry in sorted(authored.of("gold_concept"), key=lambda e: e.record_id):
        if not entry.sound:
            continue
        record = dict(entry.record)
        record["approved_by"] = None
        record["approved_date"] = None
        records.append(record)
        envelope = entry.envelope or {}
        evidence = envelope.get("evidence") or ()
        quote = ""
        for item in evidence:
            if item.get("quote"):
                quote = f"“{item['quote']}”  — {item.get('ref', '')}"
                break
        context.append(
            (" ".join(str(envelope.get("expert_should_check") or "").split()), quote)
        )
    return records, context


def _typing_rows(
    gold: goldset.GoldSet, authored: authored_store.AuthoredSet
) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Every concept typing, with the machine's argument beside it.

    Built through `typing.rows()` rather than from `authored/` directly, so this
    pack and the standalone typing pass can never disagree about which concepts
    are on the sheet or what id each typing carries.
    """
    from tm_knowledge.stage0 import typing as typing_module

    envelopes = {
        str(entry.record.get("concept")): (entry.envelope or {})
        for entry in authored.of("concept_type")
    }
    records: list[dict[str, Any]] = []
    context: list[tuple[str, str]] = []
    for record in typing_module.rows(gold, authored):
        row = dict(record)
        row["approved_by"] = None
        row["approved_date"] = None
        records.append(row)
        envelope = envelopes.get(str(row.get("concept")), {})
        alternatives = envelope.get("alternatives_considered") or ()
        reasoning = " ".join(str(envelope.get("reasoning") or "").split())
        argument = f"OUR ARGUMENT: {reasoning}" if reasoning else ""
        if alternatives:
            argument += "\n\nWE ALSO CONSIDERED: " + " ".join(
                str(alternatives[0]).split()
            )
        context.append(
            (" ".join(str(envelope.get("expert_should_check") or "").split()), argument)
        )
    return records, context


#: What the four added columns mean, per sheet, in the reviewer's language.
#:
#: The headers themselves cannot be renamed: `tmk-transcribe` tolerates exactly
#: the five names `intake.REVIEW_COLUMNS` fixes and refuses anything else, which
#: is the check that stops a hand-added column becoming a field nobody collects.
#: So `passage` holds an argument on the typing sheet and a quotation on the
#: concept sheet, and the difference is explained in a comment on the header
#: rather than by breaking the round trip.
_COLUMN_NOTES: dict[str, dict[str, str]] = {
    "concepts": {
        "why_this_example": (
            "The one thing this row most expects to have got wrong, written by "
            "the software that wrote the row. Read it before you decide — it is "
            "usually the fastest way into the question. Read-only."
        ),
        "passage": (
            "The sentence from the Manual this word was drawn from, with its "
            "reference. Read-only, and rebuilt from the Manual every time this "
            "file is generated."
        ),
        "verdict": (
            "correct — the row is right as it stands.\n"
            "amend — nearly right; edit the cells and say what you changed.\n"
            "reject — this is not a real term, or does not belong here.\n\n"
            "Leaving it blank is fine and means 'not looked at'. It never means "
            "agreement."
        ),
        "correction": (
            "Anything you want to say in words. This reaches us as your words, "
            "quoted, not as our summary of them."
        ),
    },
    "concept-types": {
        "why_this_example": (
            "The one thing this row most expects to have got wrong. WHERE THIS "
            "MENTIONS OTHER ROWS, ANSWERING IT ONCE SETTLES ALL OF THEM — one "
            "note here covers fifteen rows. Read-only."
        ),
        "passage": (
            "Our argument for the group in the `type` cell, and the next most "
            "likely alternative we rejected. Written by software, checked by "
            "nobody. Read-only."
        ),
        "verdict": (
            "correct — the group is right.\n"
            "amend — wrong group; change the `type` dropdown as well.\n"
            "reject — this idea should not be in the vocabulary at all.\n\n"
            "Leaving it blank is fine and means 'not looked at'. It never means "
            "agreement."
        ),
        "correction": (
            "Anything you want to say in words — including 'none of these nine "
            "groups fits', which is a genuinely useful answer."
        ),
    },
}

#: Said on the first cell of each pre-filled record sheet. The banner the
#: question sheets carry in row 2 cannot be used here: `tmk-transcribe` reads
#: headers from row 1, and a row inserted above them silently breaks the round
#: trip this pack exists to keep working.
_RECORD_SHEET_WARNINGS: dict[str, str] = {
    "concepts": (
        "EVERY ROW ON THIS SHEET WAS WRITTEN BY SOFTWARE AND CHECKED BY NOBODY.\n\n"
        "These are words we pulled out of the Manual and our best guess at what "
        "each one covers. For each: is this the term examiners actually use, do "
        "the other names in `alt_labels` mean the same thing, and are the ones in "
        "`not_labels` genuinely different things?\n\n"
        "Put your initials in `approved_by` and the date in `approved_date` on "
        "rows you are content with. We are not permitted to write in those two "
        "cells under any circumstances."
    ),
    "concept-types": (
        "EVERY GROUP ON THIS SHEET WAS CHOSEN BY SOFTWARE AND CHECKED BY NOBODY.\n\n"
        "One row per idea. Pick a group from the dropdown in `type`. The nine "
        "groups are listed on the guide sheet.\n\n"
        "Many rows rest on one judgement — the `why_this_example` column says "
        "which. Answering that one question settles all of them at once, and it "
        "is much the fastest way through this sheet.\n\n"
        "Put your initials in `approved_by` and the date in `approved_date` on "
        "rows you are content with. We are not permitted to write in those two "
        "cells under any circumstances."
    ),
}


def _decorate_record_sheet(
    book,
    sheet_name: str,
    context: list[tuple[str, str]],
    *,
    title: str,
    body: str,
) -> None:
    """Add the two context columns and the two answer columns to an intake sheet.

    The headers are `intake.REVIEW_COLUMNS` members and nothing else, so
    `tmk-transcribe` reads the sheet back unchanged — it tolerates exactly this
    set and refuses any other addition (ADR-0044, ADR-0046).
    """
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    spec = next(item for item in sheets() if item.name == sheet_name)
    sheet = book[sheet_name]
    first = len(spec.columns) + 1
    headers = (
        ("why_this_example", 62, _CONTEXT_FILL),
        ("passage", 74, _CONTEXT_FILL),
        ("verdict", 14, _ANSWER_FILL),
        ("correction", 58, _ANSWER_FILL),
    )
    from openpyxl.comments import Comment

    notes = _COLUMN_NOTES[sheet_name]
    for offset, (header, width, fill) in enumerate(headers):
        index = first + offset
        cell = sheet.cell(row=1, column=index, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        cell.comment = Comment(notes[header], "tmk-expert-pack", height=200, width=380)
        sheet.column_dimensions[get_column_letter(index)].width = width

    sheet.cell(row=1, column=1).comment = Comment(
        _RECORD_SHEET_WARNINGS[sheet_name], "tmk-expert-pack", height=260, width=420
    )

    for offset, (why, passage) in enumerate(context):
        row = 2 + offset
        cell = sheet.cell(row=row, column=first, value=why or None)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        cell = sheet.cell(row=row, column=first + 1, value=passage or None)
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        sheet.row_dimensions[row].height = 84

    letter = get_column_letter(first + 2)
    _add_verdict_validation(sheet, letter, len(context) + 2)
    # The validation helper anchors at row 4 for the question sheets; a record
    # sheet's data starts at row 2, so it is re-added over the right range here.
    from openpyxl.worksheet.datavalidation import DataValidation

    validation = DataValidation(
        type="list", formula1='"' + ",".join(_VERDICTS) + '"', allow_blank=True
    )
    sheet.add_data_validation(validation)
    validation.add(f"{letter}2:{letter}{max(len(context), 1) + 200}")
    del title, body


def _rewrite_guide(
    book,
    *,
    counts: dict[str, int],
    generated: str,
) -> None:
    """Replace the intake workbook's guide with this pack's own.

    The generated guide explains an empty form somebody composes into. This one
    is a pre-filled request somebody argues with, the two need opposite advice,
    and leaving the wrong one in place is how a reviewer concludes the pack is
    for a different job than the one described in the covering note.
    """
    from openpyxl.styles import Alignment, Font

    name = workbook_module.GUIDE_SHEET
    if name in book.sheetnames:
        book.remove(book[name])
    sheet = book.create_sheet(name, 0)
    sheet.column_dimensions["A"].width = 34
    sheet.column_dimensions["B"].width = 104

    sheet["A1"] = "What we need from you — everything in one file"
    sheet["A1"].font = Font(bold=True, size=14)
    sheet["A2"] = (
        f"Prepared {generated}. Read EXPERT-REQUEST.md first — it is two pages and "
        "explains why we are asking. Then work down the sheets in order: they are "
        "ordered so that if you stop at any point, the most valuable things are "
        "already done.\n\n"
        f"EVERYTHING ALREADY FILLED IN ON THESE SHEETS WAS WRITTEN BY A MACHINE AND "
        f"CHECKED BY NOBODY. There are {counts['authored']} such answers here. They "
        "are not a draft somebody reviewed — they are a first attempt, published so "
        "you can correct it instead of composing from a blank page. Where we are "
        "confident we say so; where we think we are probably wrong we say that too, "
        "in the 'why_this_example' column."
    )
    sheet["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    sheet.merge_cells("A2:B2")
    sheet.row_dimensions[2].height = 120

    plan: tuple[tuple[str, str], ...] = (
        ("1 the big ones",
         "8 questions. About 30 minutes. Worth more than everything below it "
         "put together — each one decides how dozens of other rows should go."),
        ("2 same word twice",
         f"{counts['duplicates']} rows. About 10 minutes. One word, two "
         "meanings — tell us if they are the same thing."),
        ("3 missing words",
         f"{len(ROLE_TERMS)} rows. About 20 minutes. The nine words you named "
         "in August. We still have no written definition for any word at all."),
        ("4 must or may",
         f"{counts['modality']} rows. About 5 minutes. Statements you already "
         "signed off, where nobody said how binding they are. We are not "
         "allowed to guess these."),
        ("5 how accurate",
         f"{len(_THRESHOLDS)} rows. About 20 minutes. Every target was invented "
         "by a machine. Argue with them."),
        ("concepts",
         f"{counts['concepts']} rows. Two to three hours, and it does not have "
         "to be one sitting. Words we pulled out of the Manual: is this the "
         "term examiners use, do the other names mean the same thing, and are "
         "the 'not' names really different things?"),
        ("concept-types",
         f"{counts['typings']} rows. Two to three hours. Sorting each idea into "
         "one of nine groups. Many rows share one judgement — the "
         "'why_this_example' column says which, so answering one settles "
         "fifteen."),
    )

    row = 4
    sheet.cell(row=row, column=1, value="The sheets, in the order to do them").font = (
        Font(bold=True, size=12)
    )
    row += 1
    for tab, note in plan:
        sheet.cell(row=row, column=1, value=tab).font = Font(bold=True)
        cell = sheet.cell(row=row, column=2, value=note)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        sheet.row_dimensions[row].height = 46
        row += 1

    row += 1
    rules: tuple[tuple[str, str], ...] = (
        ("Orange columns are yours",
         "Grey columns are context we generated — editing one changes nothing, "
         "because we rebuild them from the Manual every time. Type in the "
         "orange ones."),
        ("Leaving a row alone is not agreement",
         "A row you read and did not change stays marked 'nobody has checked "
         "this' forever. Nothing gets promoted by being ignored, and we would "
         "rather have 20 rows you actually decided than 130 you skimmed."),
        ("Put your initials and the date on rows you agree with",
         "On the last two sheets there are 'approved_by' and 'approved_date' "
         "columns. That signature is the only thing that turns our guess into "
         "checked knowledge. We are not permitted to write in those cells, "
         "ever — not even to copy your name down a column."),
        ("'I don't know' is a real answer, and so is 'wrong question'",
         "Write it in the answer column. A recorded 'nobody can settle this "
         "from the Manual' is genuinely useful to us and stops the question "
         "coming back."),
        ("You do not have to be consistent with last time",
         "If something you signed off in August looks wrong now, say so. Tell "
         "us and we will bring it back to you properly."),
    )
    from tm_knowledge.stage0 import typing as typing_module

    sheet.cell(row=row, column=1, value="The nine groups, on the last sheet").font = (
        Font(bold=True, size=12)
    )
    row += 1
    sheet.cell(
        row=row,
        column=2,
        value=(
            "The first four are the project owner's own words. The last five were "
            "invented by us on 9 September and are the ones most likely to be "
            "wrong — question 1 on the first sheet asks about them directly."
        ),
    ).alignment = Alignment(wrap_text=True, vertical="top")
    sheet.row_dimensions[row].height = 40
    row += 1
    for value, meaning in typing_module.GROUPS:
        sheet.cell(row=row, column=1, value=f"    {value}")
        cell = sheet.cell(row=row, column=2, value=meaning)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        row += 1

    row += 1
    sheet.cell(row=row, column=1, value="Five things worth knowing").font = Font(
        bold=True, size=12
    )
    row += 1
    for heading, body in rules:
        sheet.cell(row=row, column=1, value=heading).font = Font(bold=True)
        cell = sheet.cell(row=row, column=2, value=body)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        sheet.row_dimensions[row].height = 52
        row += 1


def build_workbook(
    gold: goldset.GoldSet | None = None,
    authored: authored_store.AuthoredSet | None = None,
    *,
    generated: str | None = None,
):
    """The whole request, as one workbook."""
    gold = gold or goldset.load()
    authored = authored if authored is not None else authored_store.load()
    generated = generated or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    concept_records, concept_context = _concept_rows(authored)
    typing_records, typing_context = _typing_rows(gold, authored)
    duplicates = duplicate_labels(gold, authored)
    unjudged = unjudged_modalities(gold)
    coverage = _role_coverage(gold, authored)

    counts = {
        "concepts": len(concept_records),
        "typings": len(typing_records),
        "duplicates": len(duplicates),
        "modality": len(unjudged),
        "authored": authored.total,
        "signed": gold.total,
    }

    book = workbook_module.build(generated=generated)
    workbook_module.fill(
        book, {"gold_concept": concept_records, "concept_type": typing_records}
    )

    # Drop the record sheets this pack does not use. Eleven blank sheets in a
    # request with a fixed budget of somebody's attention spend some of it on
    # working out that they are blank.
    for spec in sheets():
        if spec.name not in RECORD_SHEETS and spec.name in book.sheetnames:
            book.remove(book[spec.name])

    _decorate_record_sheet(
        book, "concepts", concept_context, title="", body=""
    )
    _decorate_record_sheet(
        book, "concept-types", typing_context, title="", body=""
    )

    _sheet_thresholds(book)
    _sheet_modality(book, unjudged)
    _sheet_missing_words(book, coverage)
    _sheet_duplicates(book, duplicates)
    _sheet_big_questions(book, big_questions(counts))

    order = [
        workbook_module.GUIDE_SHEET,
        "1 the big ones",
        "2 same word twice",
        "3 missing words",
        "4 must or may",
        "5 how accurate",
        "concepts",
        "concept-types",
    ]
    _rewrite_guide(book, counts=counts, generated=generated)
    book._sheets.sort(  # noqa: SLF001 - openpyxl's only ordering hook
        key=lambda item: order.index(item.title) if item.title in order else len(order)
    )

    book.properties.title = "TM-Knowledge — everything we need from a trade marks expert"
    book.properties.description = (
        f"Generated by tmk-expert-pack on {generated}. Carries {counts['authored']} "
        "machine-written answers, none of them checked by any person. Nothing in "
        "this file is approved knowledge."
    )
    return book, counts


def write_workbook(path: Path | None = None, *, generated: str | None = None) -> Path:
    path = path or WORKBOOK_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    book, _ = build_workbook(generated=generated)
    book.save(path)
    return path


# ---------------------------------------------------------------------------
# The covering note
# ---------------------------------------------------------------------------


def render_letter(counts: dict[str, int], *, generated: str | None = None) -> str:
    """The covering note. Plain English, and it has to stay that way.

    No record type names, no ADR numbers, no field names, no talk of stores or
    envelopes or graphs. The reader is a trade marks examiner being asked for a
    few hours of their expertise, not a contributor to this repository, and
    every piece of our vocabulary they have to decode is a piece of their
    attention we spent on ourselves.

    Generated rather than hand-written so the counts in it cannot drift from the
    workbook beside it — the two are produced in the same run from the same
    numbers.
    """
    generated = generated or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = counts["authored"]
    return f"""<!-- Generated by tm_knowledge.stage0.expertpack. Do not hand-edit. -->

# What we need from you

**Prepared {generated}. Please read this before opening the spreadsheet.**

---

## The short version

We have built a machine-readable version of the Trade Marks Office Manual — the
words examiners use, what they mean, how they relate to each other, and what the
system must never claim. A person can ask it questions and it answers with the
passage behind every answer.

**{total} of the answers in it were written by software and have never been
checked by anybody who knows trade marks law.** That is not an accident or a
backlog. It is deliberate: we decided it was better to write a first attempt and
have you correct it than to hand you a blank form and ask you to fill it in.
Correcting is faster than composing, and an argument you can disagree with is
more useful than an empty box.

We are now at the point where that only works if somebody checks it.

**The one thing we need is your judgement on the attached spreadsheet.** It is
one file. Everything we would ask you is in it. There is no second request
coming.

---

## Why it has to be you

Three kinds of thing are in the file, and we are only really confident about
the first.

**Things the Manual states and we have copied.** We are good at these and you
should not have to spend time on them.

**Things the Manual implies and we have inferred.** This is most of the file.
The Manual says what an examiner should do; it rarely says *what kind of thing*
an idea is, or whether two phrases mean the same thing, or which of two readings
practice actually follows. We have made {total} of those calls. Each one says
what it rests on and what it thinks it most likely got wrong.

**Things only the office knows.** The Manual does not contain them at all. When
you told us in August that it is not enough for an individual examiner to doubt
a connotation exists — that the Registrar as a whole must, and that an examiner
would be expected to consult their team leader and the section 43 specialists
first — nothing in the Manual said that. No amount of machine reading finds it.
That paragraph was worth more than weeks of automated work, and we have not been
able to record it properly because we did not want to put words in your mouth
about what examiners must do.

---

## What happens to your answers

**Your name and the date, against a row, is the only thing that turns a guess
into checked knowledge.** There is no other route. Software cannot promote its
own work, no matter how long it sits there unchallenged, and it is not permitted
to write your name anywhere for any reason.

Practically:

- A row you correct gets corrected, and the record says you decided it.
- A row you agree with and sign becomes checked knowledge.
- **A row you read and leave alone stays marked "nobody has checked this",
  permanently.** Silence is not agreement here. This is the thing most worth
  knowing before you start: twenty rows you actually decided are worth more to
  us than a hundred you skimmed.
- A row you reject is thrown out and stays thrown out.

Anything you write in a comment box reaches us as your words, quoted, not as our
summary of them.

---

## How much time, and what to do if you have less

The sheets are ordered by value, not by size. If you stop at any point, the most
important things are already done.

| If you have | Do this | What it settles |
|---|---|---|
| **30 minutes** | The first sheet only — 8 questions | Each one decides how dozens of other rows should go. This is the highest-value half hour anybody could spend on this project |
| **1 hour** | Add sheets 2, 3 and 4 | {counts['duplicates']} words we are using for two different things; the {len(ROLE_TERMS)} role words you named in August; {counts['modality']} statements you signed where nobody recorded how binding they are |
| **90 minutes** | Add sheet 5 | Every accuracy target in this project was invented by software with no basis for any of it |
| **A day, split up** | The last two sheets | {counts['typings']} ideas to sort into groups, and {counts['concepts']} words to check. Many rows share a single judgement, and the sheet says which — answering one can settle fifteen |

Nothing needs to be done in one sitting and nothing is wasted if you stop.

---

## Three things we would rather you knew

**We have almost certainly got things wrong in ways we cannot see.** Everything
in this file was found by software reading the Manual. Anything examiners know
that the Manual does not say in words is invisible to that method. Question 8 on
the first sheet asks what is missing, and we genuinely cannot answer it
ourselves.

**You are allowed to disagree with yourself.** If something you signed off in
August looks wrong now, say so on the sheet. We will bring it back to you
properly rather than quietly changing it.

**"I don't know" and "that is the wrong question" are useful answers.** Write
them down. A recorded "nobody can settle this from the Manual" stops us asking
again and tells us something real about the limits of what we are building.

---

## What this system will not do

Worth saying plainly, because it changes what the questions are for.

It does not decide whether to accept or reject a trade mark, and it is not being
built to. It retrieves and explains: the passage, what it says, whether it comes
from the Act or from office practice, and what it does not cover. The
examination decision stays entirely with the examiner.

That is also why some of the questions in the file are about what the system
must **never** say. Those matter as much as the ones about what it should.

---

## In the file

| Sheet | Rows | Roughly |
|---|---|---|
| The eight big questions | 8 | 30 min |
| Same word used twice | {counts['duplicates']} | 10 min |
| Words for who does what | {len(ROLE_TERMS)} | 20 min |
| Must, may or should | {counts['modality']} | 5 min |
| How accurate is accurate enough | {len(_THRESHOLDS)} | 20 min |
| The words themselves | {counts['concepts']} | 2–3 hrs |
| Sorting ideas into groups | {counts['typings']} | 2–3 hrs |

Orange columns are yours to type in. Grey ones are context we generated and
rebuild automatically — editing them changes nothing.

Thank you. Genuinely: this is the part of the work that cannot be automated, and
it is the part that decides whether any of the rest of it was worth doing.
"""


def write_letter(
    path: Path | None = None,
    counts: dict[str, int] | None = None,
    *,
    generated: str | None = None,
) -> Path:
    path = path or LETTER_PATH
    if counts is None:
        gold = goldset.load()
        authored = authored_store.load()
        _, counts = build_workbook(gold, authored, generated=generated)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_letter(counts, generated=generated), encoding="utf-8")
    return path

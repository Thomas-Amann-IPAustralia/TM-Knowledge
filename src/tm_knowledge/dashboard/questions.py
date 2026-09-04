"""The queue of decisions waiting on a person, and the answers that come back.

`review/questions/open-questions.yaml` is the one file a session edits to put
something in front of the owner. It is hand-written on purpose: the whole value
of the queue is that each item is phrased in language the owner can act on
without reading the repo, and no generator can do that. The schema beside it
enforces the parts that *can* be checked — every open question has a control to
answer it, plain-language framing that is not one line long, and a statement of
what stays stuck until it is answered.

Answers arrive as files in `review/rulings/`, written by `ruling.py` from a
GitHub issue the dashboard's form composed. This module reads both sides so the
site can show the queue with the answered items struck through, and so a session
can tell at a glance which rulings it has not yet acted on.

**Nothing here decides anything.** An option list is the set of answers a person
may pick from; choosing one is theirs, and an unanswered question stays
unanswered rather than acquiring a default (rule 6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from tm_knowledge.config import REPO_ROOT

__all__ = [
    "QUESTIONS_PATH",
    "SCHEMA_PATH",
    "RULINGS_DIR",
    "Question",
    "QuestionSet",
    "Ruling",
    "MalformedQuestions",
    "load",
    "load_rulings",
]

QUESTIONS_DIR = REPO_ROOT / "review" / "questions"
QUESTIONS_PATH = QUESTIONS_DIR / "open-questions.yaml"
SCHEMA_PATH = QUESTIONS_DIR / "schema.json"
RULINGS_DIR = REPO_ROOT / "review" / "rulings"

#: The ruling file's `schema` field. Bumped only with a migration, because a
#: session reading an old ruling must not mistake a renamed field for an absent
#: answer.
RULING_SCHEMA = "tmk-ruling/1"


class MalformedQuestions(ValueError):
    """The question queue did not validate. Refused rather than half-rendered."""


@dataclass(frozen=True)
class Question:
    identifier: str
    theme: str
    status: str
    needs: str
    urgency: str
    title: str
    raw: dict[str, Any]

    @property
    def is_asked(self) -> bool:
        """Whether this one reaches the form.

        Only an open question the owner can settle. An expert question and an
        organisational one are shown for context — putting a radio button under
        something the owner cannot decide invites an answer that then has to be
        unpicked.
        """
        return self.status == "open" and self.needs == "owner"


@dataclass(frozen=True)
class QuestionSet:
    path: Path
    version: int
    updated: str
    themes: tuple[dict[str, str], ...]
    questions: tuple[Question, ...]

    def by_status(self, status: str) -> tuple[Question, ...]:
        return tuple(q for q in self.questions if q.status == status)

    @property
    def asked(self) -> tuple[Question, ...]:
        return tuple(q for q in self.questions if q.is_asked)

    def theme(self, identifier: str) -> dict[str, str]:
        for theme in self.themes:
            if theme["id"] == identifier:
                return theme
        raise MalformedQuestions(f"question theme {identifier!r} is not declared in `themes`")


@dataclass(frozen=True)
class Ruling:
    path: Path
    received: str
    issue: dict[str, Any]
    answers: tuple[dict[str, Any], ...]
    applied: Any = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def answered_ids(self) -> tuple[str, ...]:
        return tuple(str(answer.get("id")) for answer in self.answers if answer.get("id"))

    @property
    def is_applied(self) -> bool:
        return bool(self.applied)


def _schema() -> dict[str, Any]:
    import json

    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load(path: Path | None = None) -> QuestionSet:
    """Read and validate the queue. Raises rather than returning a partial set."""
    path = path or QUESTIONS_PATH
    if not path.exists():
        raise MalformedQuestions(
            f"{path} is missing. The dashboard's decision form is generated from it; "
            f"an absent file would render as 'nothing needs you', which is a claim."
        )
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise MalformedQuestions(f"{path.name}: not valid YAML: {error}") from error

    try:
        jsonschema.validate(document, _schema())
    except jsonschema.ValidationError as error:
        location = "/".join(str(part) for part in error.absolute_path) or "(document root)"
        raise MalformedQuestions(f"{path.name}: at {location}: {error.message}") from error

    questions = tuple(
        Question(
            identifier=entry["id"],
            theme=entry["theme"],
            status=entry["status"],
            needs=entry["needs"],
            urgency=entry["urgency"],
            title=entry["title"],
            raw=entry,
        )
        for entry in document["questions"]
    )

    seen: set[str] = set()
    for question in questions:
        if question.identifier in seen:
            raise MalformedQuestions(f"duplicate question id {question.identifier}")
        seen.add(question.identifier)

    question_set = QuestionSet(
        path=path,
        version=document["version"],
        updated=document["updated"],
        themes=tuple(document["themes"]),
        questions=questions,
    )
    for question in questions:
        question_set.theme(question.theme)  # raises on an undeclared theme
    return question_set


def load_rulings(directory: Path | None = None) -> tuple[Ruling, ...]:
    """Every recorded answer, newest first.

    A file that will not parse is an error. A ruling is the owner's decision;
    skipping one because it is malformed would silently drop a decision, which
    is the one failure this directory exists to prevent.
    """
    directory = directory or RULINGS_DIR
    if not directory.exists():
        return ()
    rulings: list[Ruling] = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            raise MalformedQuestions(f"{path.name}: not valid YAML: {error}") from error
        if not isinstance(document, dict) or document.get("schema") != RULING_SCHEMA:
            raise MalformedQuestions(
                f"{path.name}: expected a mapping with `schema: {RULING_SCHEMA}`. "
                f"A ruling file is written by `tmk-ruling`, never by hand."
            )
        rulings.append(
            Ruling(
                path=path,
                received=str(document.get("received_utc", "")),
                issue=dict(document.get("issue") or {}),
                answers=tuple(document.get("answers") or ()),
                applied=document.get("applied"),
                raw=document,
            )
        )
    return tuple(sorted(rulings, key=lambda ruling: ruling.received, reverse=True))

"""Turn a submitted answer into a file the next session reads.

The dashboard cannot write to the repository — it is a static page, and a page
that could write would need a credential in the browser. So the loop goes the
long way round, and the long way is the auditable one:

    the form  ->  a GitHub issue the owner submits  ->  this module  ->
    review/rulings/<date>-issue-<n>.yaml  ->  the next session

The issue is the unmodified artefact, in the owner's own submission, with
GitHub's timestamp and authorship on it. The YAML file is a **transcription** of
it, and it says on its face which issue it came from — the same split as
`review/returned/` (what a person handed back) and `review/decisions/` (what it
was taken to mean).

Everything here refuses rather than repairs. An answer naming a question that
does not exist, or an option that is not on the list, means the form and the
question file have diverged, or the body was edited by hand. Either way the right
move is to stop and say so on the issue, not to guess which answer was meant
(CLAUDE.md rule 6).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.dashboard import questions as questions_module

__all__ = ["MARKER", "FORM_VERSION", "MalformedSubmission", "parse", "transcribe", "write"]

#: What the form writes at the top of the issue body. The workflow keys off it,
#: so an ordinary issue is never mistaken for a submitted decision.
MARKER = "<!-- tmk-ruling:v1 -->"

FORM_VERSION = "tmk-ruling/1"

_FENCE = re.compile(r"```(?:ya?ml)?\s*\n(.*?)\n```", re.DOTALL)


class MalformedSubmission(ValueError):
    """The issue body did not carry a submission this module can transcribe."""


def parse(body: str) -> dict[str, Any]:
    """The payload out of an issue body. Raises if it is not one."""
    if MARKER not in body:
        raise MalformedSubmission(
            f"no {MARKER} marker. This issue was not submitted by the dashboard form, "
            f"so nothing is transcribed from it."
        )
    fenced = _FENCE.search(body, body.index(MARKER))
    if fenced is None:
        raise MalformedSubmission(
            "the marker is there but no fenced code block follows it. The form writes the "
            "answers inside a ```yaml block; if it was edited out, re-submit from the dashboard."
        )
    try:
        payload = yaml.safe_load(fenced.group(1))
    except yaml.YAMLError as error:
        raise MalformedSubmission(f"the answer block is not valid YAML: {error}") from error
    if not isinstance(payload, dict):
        raise MalformedSubmission("the answer block is not a mapping.")
    if payload.get("form") != FORM_VERSION:
        raise MalformedSubmission(
            f"expected `form: {FORM_VERSION}`, found {payload.get('form')!r}."
        )
    answers = payload.get("answers")
    if not isinstance(answers, list) or not answers:
        raise MalformedSubmission("the submission carries no answers.")
    return payload


def _option_label(question: dict[str, Any], value: str) -> str:
    for option in (question.get("answer") or {}).get("options") or ():
        if option["value"] == value:
            return option["label"]
    raise MalformedSubmission(
        f"{question['id']}: {value!r} is not one of the options on the form. Either the "
        f"question changed after the form was opened, or the body was edited by hand. "
        f"Nothing is transcribed — re-submit from the dashboard."
    )


def transcribe(
    payload: dict[str, Any],
    *,
    issue: dict[str, Any],
    question_set: questions_module.QuestionSet | None = None,
    received: str | None = None,
) -> dict[str, Any]:
    """The ruling document, with each answer echoed in full.

    The question and the chosen wording are copied in beside the machine value so
    the file reads on its own six months later, without anyone having to line it
    up against a version of the question queue that has since moved on.
    """
    question_set = question_set or questions_module.load()
    known = {question.identifier: question.raw for question in question_set.questions}
    stamp = received or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    answers: list[dict[str, Any]] = []
    for entry in payload["answers"]:
        identifier = str(entry.get("id", "")).strip()
        question = known.get(identifier)
        if question is None:
            raise MalformedSubmission(
                f"{identifier or '(no id)'} is not a question in "
                f"`review/questions/open-questions.yaml`. Nothing is transcribed."
            )
        kind = (question.get("answer") or {}).get("kind")
        record: dict[str, Any] = {
            "id": identifier,
            "question": question["title"],
            "kind": kind,
        }
        if kind == "multi":
            values = entry.get("values") or []
            if not isinstance(values, list):
                raise MalformedSubmission(f"{identifier}: expected a list of values.")
            record["values"] = [str(value) for value in values]
            record["labels"] = [_option_label(question, str(value)) for value in values]
            record["label"] = "; ".join(record["labels"]) or "nothing ticked — all confirmed"
        elif kind == "choice":
            value = entry.get("value")
            if not value:
                continue
            record["value"] = str(value)
            record["label"] = _option_label(question, str(value))
        else:
            value = entry.get("value")
            if value in (None, ""):
                continue
            record["value"] = str(value)
            record["label"] = str(value)
        notes = str(entry.get("notes") or "").strip()
        if notes:
            record["notes"] = notes
        answers.append(record)

    if not answers:
        raise MalformedSubmission("every answer in the submission was empty.")

    return {
        "schema": questions_module.RULING_SCHEMA,
        "received_utc": stamp,
        "questions_updated": payload.get("questions_updated"),
        "issue": {key: issue[key] for key in sorted(issue) if issue[key] is not None},
        # A session sets this when it has acted on the ruling. Left null so that
        # "answered" and "acted on" never collapse into one state.
        "applied": None,
        "answers": answers,
    }


def write(
    document: dict[str, Any],
    directory: Path | None = None,
) -> Path:
    """Write the ruling. The filename carries the date and the issue number."""
    directory = directory or questions_module.RULINGS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    number = document.get("issue", {}).get("number", "unknown")
    day = str(document["received_utc"])[:10]
    path = directory / f"{day}-issue-{number}.yaml"
    # An edited submission replaces its earlier transcription rather than
    # sitting beside it. Two files for one issue would be two versions of one
    # decision, and nothing would say which one the owner meant.
    for existing in directory.glob(f"*-issue-{number}.yaml"):
        if existing != path:
            existing.unlink()
    header = (
        "# A decision the repo owner made, transcribed from the GitHub issue named\n"
        "# below by `tmk-ruling`. Do not hand-edit the answers: the issue is the\n"
        "# artefact, this is the transcription (review/rulings/README.md).\n"
        "#\n"
        "# A session that acts on this fills in `applied:` and says what it did.\n"
    )
    path.write_text(
        header + yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=88),
        encoding="utf-8",
    )
    return path

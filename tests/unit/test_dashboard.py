"""The dashboard reads the repo faithfully, and refuses when it cannot.

Two things are being protected here.

**The site must not be able to say something the repository does not hold.**
Every page is generated from committed artefacts, so the failure mode is not a
wrong number typed by hand — it is a *stale* number, left behind when a record
moved and nobody rebuilt. `test_committed_data_is_current` is that guard, and it
is the same check CI runs.

**An answer coming back must be transcribed or refused, never guessed.** A
submission naming a question that does not exist, or an option that is not on
the form, means the form and the question file have diverged. The tests below
fix that as a refusal, because the alternative — picking the nearest match — is
an agent deciding what a person meant (CLAUDE.md rule 6).
"""

from __future__ import annotations

import json
import re
import sys

import pytest

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.dashboard import blocks, questions, ruling, sources

pytestmark = []

SITE = REPO_ROOT / "site"


# ------------------------------------------------------- reading the documents


def test_every_adr_parses_with_an_authority():
    """The decisions page is generated from the log's own headings. A reformat
    that broke the parser would empty the page rather than fail, so it fails."""
    adrs = sources.read_decisions()
    assert len(adrs) > 50
    assert {adr.authority for adr in adrs} <= {"inherited", "derived", "agent-proposed", "human"}
    assert all(adr.title and adr.date for adr in adrs)


def test_a_decision_log_without_headings_is_refused(tmp_path):
    path = tmp_path / "DECISIONS.md"
    path.write_text("# DECISIONS\n\nnothing here yet.\n", encoding="utf-8")
    with pytest.raises(sources.MalformedDocument):
        sources.read_decisions(path)


def test_an_adr_without_its_metadata_line_is_refused(tmp_path):
    path = tmp_path / "DECISIONS.md"
    path.write_text("## ADR-0001 — A decision\n\nNo metadata line.\n", encoding="utf-8")
    with pytest.raises(sources.MalformedDocument):
        sources.read_decisions(path)


def test_the_stage_board_has_all_eleven_stages():
    stages = sources.read_stage_board()
    assert [stage.number for stage in stages] == [str(n) for n in range(11)]


def test_a_short_stage_board_is_refused(tmp_path):
    """A row that stopped parsing would disappear from the site silently."""
    path = tmp_path / "ROADMAP-STATUS.md"
    path.write_text(
        "## Board\n\n| Stage | Name | Status | Owner |\n|---|---|---|---|\n"
        "| 0 | Something | **partial** | this repo |\n\n## Next\n",
        encoding="utf-8",
    )
    with pytest.raises(sources.MalformedDocument):
        sources.read_stage_board(path)


def test_the_glossary_covers_the_terms_a_reader_needs():
    """The tooltips are the project's own glossary, not a second one."""
    glossary = sources.read_glossary()
    for term in ("SHACL", "OWL 2 RL", "SKOS", "Triple", "IRI", "Named graph", "Ontology"):
        assert term in glossary, f"{term} is not in docs/GLOSSARY.md"
        assert len(glossary[term]["text"]) > 30


# ------------------------------------------------------------ the question set


def test_the_question_queue_validates():
    question_set = questions.load()
    assert question_set.questions
    assert question_set.asked, "nothing is being asked, which is itself a claim"


def test_every_asked_question_can_actually_be_answered():
    """A question with no control is a question the owner cannot answer from the
    dashboard, which is the one thing the dashboard is for."""
    for question in questions.load().asked:
        answer = question.raw["answer"]
        assert answer["kind"] in {"choice", "multi", "text", "long_text"}
        if answer["kind"] in {"choice", "multi"}:
            assert len(answer["options"]) >= 2
            values = [option["value"] for option in answer["options"]]
            assert len(values) == len(set(values)), f"{question.identifier}: duplicate option value"


def test_a_parked_question_is_not_put_to_the_owner():
    """Expert content is shown for context. A radio button under something the
    owner cannot decide invites an answer that then has to be unpicked."""
    for question in questions.load().by_status("parked"):
        assert not question.is_asked


def test_an_answered_question_can_show_what_the_answer_was():
    """`status: answered` is a claim about the owner, and the card has to be able
    to back it.

    Three questions were marked answered on the strength of a YAML comment. A
    comment is invisible to the schema, to this test and to the dashboard, so the
    site rendered them as answered with no answer under them — indistinguishable
    from an open question that has lost its control. The evidence is either an
    entry in a ruling file, or an `answered:` block naming the record.
    """
    recorded = {
        identifier
        for ruling_file in questions.load_rulings()
        for identifier in ruling_file.answered_ids
    }
    for question in questions.load().by_status("answered"):
        note = question.raw.get("answered")
        assert question.identifier in recorded or note, (
            f"{question.identifier} is marked answered and nothing in the repository "
            f"says what the answer was — no ruling entry, no `answered:` block"
        )
        if note:
            record = REPO_ROOT / note["record"]
            assert record.exists(), f"{question.identifier}: {note['record']} does not exist"


def test_no_theme_blurb_hardcodes_a_count_of_its_questions():
    """A count written into prose is right on the day it is typed.

    The `unblocks` blurb said "Six things nothing can move past" and went on
    saying it after five of the six were answered, which is the same failure as a
    stale number on a generated page — just typed by a person instead (Q-46). The
    dashboard counts each theme itself.
    """
    numbers = re.compile(
        r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
        r"(things?|questions?|decisions?|items?)\b",
        re.IGNORECASE,
    )
    for theme in questions.load().themes:
        found = numbers.search(theme["blurb"])
        assert not found, (
            f"theme {theme['id']}: blurb counts its own questions "
            f"({found.group(0)!r}); the dashboard does that, and does not go stale"
        )


@pytest.mark.snapshot
@pytest.mark.rdf
def test_no_question_quotes_a_rule_triple_count_as_a_finding_count():
    """Where the number the owner acts on comes from.

    OQ-0003 told him RULE-0001 "produced 71 flags" and asked him to review 71
    passages. 71 is the size of the graph the rule builds; it flags five. The
    triple count was read off a generated table, where it is correctly headed
    *triples*, and written into the question as a count of findings (Q-44).

    A question may legitimately quote a triple count — as rows of data, as
    storage — so this checks the pairing, not the number: no rule's triple count
    may sit next to a word that makes it sound like a count of findings.
    """
    from tm_knowledge.ontology import rules as rules_module
    from tm_knowledge.ontology.build import build

    dataset, _ = build()
    _dataset, counts = rules_module.apply_rules(dataset)
    text = questions.QUESTIONS_PATH.read_text(encoding="utf-8")
    finding_words = r"(?:flags?|flagged|passages|links?|findings?|results?|of them)"
    for rule_id, got in counts.items():
        if got.triples == got.assertions:
            continue
        pattern = re.compile(
            rf"\b{got.triples:,}\b\s*{finding_words}|\b{got.triples}\b\s*{finding_words}"
        )
        found = pattern.search(text)
        assert not found, (
            f"open-questions.yaml calls {rule_id}'s triple count ({got.triples:,}) a count of "
            f"{found.group(0)!r}. It concludes {got.assertions}. Quote the conclusion count."
        )


def test_a_question_missing_its_plain_language_framing_is_refused(tmp_path):
    path = tmp_path / "open-questions.yaml"
    path.write_text(
        "version: 1\nupdated: '2026-09-04'\n"
        "themes: [{id: a, title: A theme, blurb: A blurb long enough}]\n"
        "questions:\n"
        "  - id: OQ-0001\n    theme: a\n    status: open\n    needs: owner\n"
        "    urgency: high\n    title: A title long enough to pass\n"
        "    plain: too short\n    why_you: because it is yours to decide\n"
        "    if_unanswered: nothing moves until it is answered\n    raised: S011\n",
        encoding="utf-8",
    )
    with pytest.raises(questions.MalformedQuestions):
        questions.load(path)


# ------------------------------------------------------------------- the build


@pytest.mark.rdf
def test_build_produces_every_page():
    from tm_knowledge.dashboard import build as build_module

    pages = build_module.build(generated="2026-01-01")
    for page, _, _ in build_module.PAGES:
        assert f"{page}.json" in pages, f"{page} has a nav entry and no data"
    assert set(pages) - {"site.json", "glossary.json"} == {
        f"{page}.json" for page, _, _ in build_module.PAGES
    }, "a data file exists with no nav entry, or the other way round"


@pytest.mark.rdf
def test_a_glossary_marker_naming_an_unknown_term_is_refused():
    """A marker that silently renders as plain text is an explanation quietly
    withdrawn from the reader who needed it."""
    from tm_knowledge.dashboard import build as build_module

    page = {"a.json": {"blocks": [blocks.prose("See {{Nonexistent Term}}.")]}}
    with pytest.raises(build_module.BuildError):
        build_module.check_glossary(page, sources.read_glossary())


@pytest.mark.rdf
def test_committed_data_is_current():
    """The site reads only what is committed, so a stale file is a number on a
    public page that this repository no longer holds. `tmk-dashboard --write`."""
    from tm_knowledge.dashboard import build as build_module

    assert build_module.check() == []


def test_an_unknown_tone_is_refused():
    with pytest.raises(ValueError):
        blocks.callout("urgent", "A title", "Some text")


# ------------------------------------------------------------------- the site


def test_the_site_is_self_contained():
    """No package manager, no build step, and nothing loaded from a CDN — this
    is published by a government agency and every byte should be in the repo."""
    html = (SITE / "index.html").read_text(encoding="utf-8")
    for name in ("app.css", "app.js"):
        assert name in html
        assert (SITE / name).exists()
    assert "http://" not in html.replace("http://www.w3.org", "")
    for module in ("app.js", "blocks.js", "inbox.js", "md.js"):
        source = (SITE / module).read_text(encoding="utf-8")
        assert "cdn" not in source.lower()
        assert "import(" not in source


def test_every_nav_entry_has_a_data_file():
    site = json.loads((SITE / "data" / "site.json").read_text(encoding="utf-8"))
    for entry in site["nav"]:
        assert (SITE / "data" / f"{entry['id']}.json").exists()


# ---------------------------------------------------------- answers coming back


def _body(payload: str) -> str:
    return f"{ruling.MARKER}\nAnswers.\n\n```yaml\n{payload}\n```\n"


def _submission(question_id: str, value: str) -> str:
    return _body(
        "form: tmk-ruling/1\nquestions_updated: '2026-09-04'\n"
        f"answers:\n  - id: {question_id}\n    value: {value}\n"
    )


def _first_choice() -> tuple[str, str]:
    for question in questions.load().asked:
        if question.raw["answer"]["kind"] == "choice":
            return question.identifier, question.raw["answer"]["options"][0]["value"]
    raise AssertionError("the queue has no single-choice question to test with")


def test_an_ordinary_issue_is_not_a_submission():
    with pytest.raises(ruling.MalformedSubmission):
        ruling.parse("Hi, the site looks great.")


def test_a_submission_without_its_answer_block_is_refused():
    with pytest.raises(ruling.MalformedSubmission):
        ruling.parse(f"{ruling.MARKER}\nI deleted the block by accident.")


def test_a_round_trip_keeps_the_question_and_the_wording():
    identifier, value = _first_choice()
    document = ruling.transcribe(
        ruling.parse(_submission(identifier, value)),
        issue={"number": 1, "url": "https://example.invalid/1", "author": "someone"},
        received="2026-09-04T00:00:00Z",
    )
    assert document["schema"] == questions.RULING_SCHEMA
    assert document["applied"] is None
    answer = document["answers"][0]
    assert answer["id"] == identifier and answer["value"] == value
    assert answer["question"] and answer["label"], "the file must read on its own"


def test_an_unknown_question_is_refused():
    with pytest.raises(ruling.MalformedSubmission):
        ruling.transcribe(
            ruling.parse(_submission("OQ-9999", "anything")),
            issue={"number": 1, "url": "u", "author": "a"},
        )


def test_an_option_that_is_not_on_the_form_is_refused():
    """Means the form and the question file diverged, or the body was edited.
    Picking the nearest option would be deciding what a person meant."""
    identifier, _ = _first_choice()
    with pytest.raises(ruling.MalformedSubmission):
        ruling.transcribe(
            ruling.parse(_submission(identifier, "not_an_option")),
            issue={"number": 1, "url": "u", "author": "a"},
        )


def test_an_edited_submission_replaces_its_earlier_transcription(tmp_path):
    """Two files for one issue would be two versions of one decision, with
    nothing saying which one the owner meant."""
    identifier, value = _first_choice()
    payload = ruling.parse(_submission(identifier, value))
    issue = {"number": 12, "url": "u", "author": "a"}
    first = ruling.write(
        ruling.transcribe(payload, issue=issue, received="2026-09-04T00:00:00Z"), tmp_path
    )
    second = ruling.write(
        ruling.transcribe(payload, issue=issue, received="2026-09-06T00:00:00Z"), tmp_path
    )
    assert not first.exists() and second.exists()
    assert len(list(tmp_path.glob("*.yaml"))) == 1


def test_the_transcription_path_does_not_need_the_rdf_extra(monkeypatch):
    """`tmk-ruling` runs in a workflow that installs the core three dependencies
    and nothing else. It imported the graph builder at module scope, and so
    rdflib — the optional `[rdf]` extra — until issue #12 died on
    `No module named 'rdflib'` before a line of the transcription ran (Q-42).

    The coupling is invisible on any developer machine, because every developer
    machine has the extras installed. So the test removes them."""
    import builtins
    import importlib

    blocked = {"rdflib", "pyshacl", "owlrl", "openpyxl"}
    real_import = builtins.__import__

    def guard(name, *args, **kwargs):
        head = name.split(".")[0]
        if head in blocked:
            raise ModuleNotFoundError(f"No module named {head!r}")
        return real_import(name, *args, **kwargs)

    for module in list(sys.modules):
        if module.startswith("tm_knowledge.dashboard") or module.split(".")[0] in blocked:
            monkeypatch.delitem(sys.modules, module, raising=False)
    monkeypatch.setattr(builtins, "__import__", guard)

    cli = importlib.import_module("tm_knowledge.dashboard.cli")
    assert hasattr(cli, "ruling")


def test_a_note_with_no_option_chosen_is_still_an_answer():
    """The form lets the owner type a note without picking an option, and puts
    that note in the machine-readable block. Both the block's prose summary and
    this transcription used to drop it, so the note existed only in the issue
    body — which is exactly what happened to OQ-0009 on issue #12 while the
    issue title still counted it as one of seven answers (Q-43)."""
    identifier, _ = _first_choice()
    body = _body(
        "form: tmk-ruling/1\nquestions_updated: '2026-09-04'\n"
        f"answers:\n  - id: {identifier}\n    notes: \"the answer is here\"\n"
    )
    document = ruling.transcribe(
        ruling.parse(body),
        issue={"number": 1, "url": "u", "author": "a"},
        received="2026-09-08T00:00:00Z",
    )
    answer = document["answers"][0]
    assert answer["notes"] == "the answer is here"
    assert "value" not in answer, "no option was picked; inventing one would be deciding"
    assert answer["label"] == ruling.NOTES_ONLY


def test_an_answer_with_neither_an_option_nor_a_note_is_dropped():
    """An empty answer is the owner scrolling past a question, not a decision."""
    identifier, value = _first_choice()
    body = _body(
        "form: tmk-ruling/1\nquestions_updated: '2026-09-04'\n"
        f"answers:\n  - id: {identifier}\n    value: {value}\n"
        f"  - id: {identifier}\n    notes: ''\n"
    )
    document = ruling.transcribe(
        ruling.parse(body), issue={"number": 1, "url": "u", "author": "a"}
    )
    assert len(document["answers"]) == 1


def test_recorded_rulings_load():
    """A ruling that will not parse is a decision silently dropped, so reading
    the directory raises rather than skipping the file.

    Every ruling names where it was made — an issue URL for one submitted through
    the form, a transcription file for one given in chat (ADR-0079 arrived that
    way). The route does not change a decision's weight; being untraceable would.
    """
    for entry in questions.load_rulings():
        assert entry.answers
        assert entry.origin, f"{entry.path.name} names no source"

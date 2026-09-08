"""The Stage 0 evaluation harness (parallel track P5).

It asserts the mechanical list in `eval/STAGE-0-INPUT-GUIDE.md` §7 over whatever
`eval/gold/` holds, and reports what §7 still wants. Two kinds of finding, and
the distinction is the whole design (ADR-0018):

**Since ADR-0080 it checks two stores.** `eval/gold/` holds what an expert
signed; `authored/` holds what a machine wrote and nobody has read. Every
finding names which store it came from, and no count in this module adds them
together — the completeness gate measures the signed set alone, because a band
met by authored records would report Stage 0 finished on the strength of
records nobody has looked at. The authored checks are gathered under
`AUTHORED_CHECKS` below.

- **DEFECT** — something that arrived is wrong: a record that does not validate,
  a duplicated id, a dangling cross-reference, a `source_ref` that resolves to
  nothing, a `span` that does not land on its recorded text, a stale
  `source_content_hash`. These break the build.
- **GAP** — something expected has not arrived: a deliverable missing, a count
  under its band, a judgement field still null, an unapproved record. This is a
  **reported state**, not a broken build. It is also what makes the harness red
  today rather than vacuously green, which is the outcome §7 requires.
- **NOTE** — an observation a human should eyeball and no machine can judge: a
  concept with no `not_labels`, a case ref that no corpus can resolve. Never
  gates anything.

Why the third severity exists: `not_labels` is populated "wherever a near-miss
exists", and whether one exists is an expert's reading. Gating on it would make
Stage 0 uncompletable; ignoring it would drop the guide's most valuable field.
So it is reported and it is nobody's blocker.

**The vacuity trap.** With zero gold records every check above iterates an empty
collection and passes. The completeness gate — `_gate` below — is what fails
instead, naming each absent deliverable. It fails on *absence*, never on content
quality, and when Stage 0 genuinely completes it goes quiet on its own and every
remaining finding is real.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterator

from tm_knowledge.authored import store as authored_store
from tm_knowledge.authored.store import AuthoredRecord, AuthoredSet
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.refs import InvalidRef, RefKind, parse_ref
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.goldset import GoldSet
from tm_knowledge.stage0.schemas import (
    ID_PREFIXES,
    RECORD_TYPES,
    enum_values,
    read_path,
    ref_paths,
    validate,
)
from tm_knowledge.upstream.loader import Corpus, load_corpus
from tm_knowledge.upstream.pin import SnapshotMismatch, UnpinnedSnapshot

__all__ = [
    "Severity",
    "Finding",
    "Report",
    "run",
    "band",
    "DELIVERABLES",
    "SPAN_SURFACE",
    "passage_at",
    "AUTHORED_CHECKS",
]


class Severity(str, Enum):
    DEFECT = "defect"
    GAP = "gap"
    NOTE = "note"


@dataclass(frozen=True, slots=True)
class Finding:
    """One thing the harness has to say, addressed to whoever can fix it."""

    severity: Severity
    check: str
    subject: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.check}: {self.subject} — {self.message}"


@dataclass(frozen=True, slots=True)
class Deliverable:
    """One line of `STAGE-0-INPUT-GUIDE.md` §7, as something checkable.

    The bands live here and in the guide, and nowhere else. ADR-0018 names that
    duplication as a known cost: when a band moves in the guide it moves here in
    the same commit.
    """

    key: str
    label: str
    #: `document` — a file the expert writes · `records` — a gold record type.
    kind: str
    record_type: str | None = None
    path: str | None = None
    minimum: int | None = None
    maximum: int | None = None


#: §7's content checklist. Order is the guide's suggested order of work (§10),
#: so the report reads as a worklist rather than as an inventory.
DELIVERABLES: tuple[Deliverable, ...] = (
    Deliverable("pilot_scope", "Pilot scope, with exclusions", "document",
                path="eval/pilot-scope.md"),
    Deliverable("competency_questions", "Competency questions, covering all six categories",
                "records", record_type="competency_question", minimum=6),
    Deliverable("prohibited_uses", "Prohibited uses, covering all six kinds",
                "records", record_type="prohibited_use", minimum=6),
    Deliverable("concepts", "Gold concepts", "records",
                record_type="gold_concept", minimum=50, maximum=100),
    Deliverable("entities", "Gold entities, over an exhaustively annotated chunk set",
                "records", record_type="gold_entity", minimum=100, maximum=300),
    Deliverable("relationships", "Gold relationships", "records",
                record_type="gold_relationship", minimum=50, maximum=100),
    Deliverable("search_questions", "Search questions", "records",
                record_type="gold_search_question", minimum=20, maximum=50),
    Deliverable("retrieval_questions", "AI retrieval questions", "records",
                record_type="gold_retrieval_question", minimum=20, maximum=50),
    Deliverable("reasoning", "Reasoning expectations", "records",
                record_type="reasoning_expectation", minimum=1),
    # Not a §7 deliverable — added S012 when the owner confirmed the four groups
    # (OQ-0001, ADR-0071). The band is one per approved concept, because the
    # question is "which group is this in" and every concept has an answer,
    # `none_of_these` included. `tmk-typing` renders the pass.
    Deliverable("concept_types", "Concepts sorted into one of the four groups",
                "records", record_type="concept_type", minimum=50, maximum=100),
    Deliverable("measures", "A threshold against every metric", "document",
                path="eval/measures.md"),
)

#: Fields whose null value is a gap the expert must close, by record type.
#: A key that is *absent* is a schema failure and is caught before this runs;
#: this is about the keys that are present and empty (ADR-0027).
JUDGEMENT_FIELDS: dict[str, tuple[str, ...]] = {
    "competency_question": (),
    "gold_entity": ("span", "source_content_hash"),
    "gold_concept": (),
    "gold_relationship": ("span", "source_content_hash", "tier", "modality"),
    "gold_search_question": (),
    "gold_retrieval_question": (),
    "reasoning_expectation": ("tier",),
    "prohibited_use": (),
    "concept_type": (),
}

#: Cross-reference fields: record type -> field path -> the prefix it must name.
#: `broader`/`narrower`/`related` land on concepts, `prohibited_conclusions` and
#: `must_not_infer` on prohibited uses, `related_questions` on either of two.
CROSS_REFERENCES: dict[str, dict[tuple[str, ...], tuple[str, ...]]] = {
    "gold_concept": {
        ("broader", "*"): ("GC",),
        ("narrower", "*"): ("GC",),
        ("related", "*"): ("GC",),
    },
    "gold_retrieval_question": {("prohibited_conclusions", "*"): ("PU",)},
    "reasoning_expectation": {("must_not_infer", "*"): ("PU",)},
    "prohibited_use": {("related_questions", "*"): ("CQ", "GA")},
}

#: Which recorded surface a span must reproduce, by record type.
SPAN_SURFACE: dict[str, str] = {
    "gold_entity": "surface",
    "gold_relationship": "supporting_text",
}


@dataclass(frozen=True)
class Report:
    """What the harness found, and whether Stage 0 is finished."""

    findings: tuple[Finding, ...]
    gold: GoldSet
    #: Whether the resolution half ran, and why not when it did not.
    resolution_ran: bool
    resolution_skipped: str | None = None
    #: The snapshot commit the resolution checks ran against, when they ran.
    pin_commit: str | None = None
    #: What `authored/` holds. A second store, never added to the first
    #: (ADR-0080 consequence 3) — `Report` deliberately has no property that
    #: sums them, because the moment one exists something will print it.
    authored: AuthoredSet = field(
        default_factory=lambda: AuthoredSet(root=authored_store.AUTHORED_DIR)
    )

    def of(self, severity: Severity) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity is severity)

    @property
    def defects(self) -> tuple[Finding, ...]:
        return self.of(Severity.DEFECT)

    @property
    def gaps(self) -> tuple[Finding, ...]:
        return self.of(Severity.GAP)

    @property
    def notes(self) -> tuple[Finding, ...]:
        return self.of(Severity.NOTE)

    @property
    def complete(self) -> bool:
        """Stage 0 is done: no gaps, and the resolution half actually ran.

        A gapless report from a run that never opened the snapshot is not a
        complete Stage 0 — it is an unverified one, and saying otherwise is the
        vacuous green this harness exists to prevent.
        """
        return not self.gaps and self.resolution_ran

    @property
    def exit_code(self) -> int:
        """0 clean and complete · 1 defects · 3 sound but incomplete.

        Three codes rather than two because two signals mean opposite things:
        "what arrived is wrong" has to break a build, and "the expected work has
        not arrived yet" has to be reportable without breaking one (ADR-0018).
        """
        if self.defects:
            return 1
        return 0 if self.complete else 3

    def summary(self) -> str:
        return (
            f"{len(self.defects)} defect(s), {len(self.gaps)} gap(s), "
            f"{len(self.notes)} note(s); Stage 0 "
            f"{'complete' if self.complete else 'incomplete'}"
        )

    def stores(self) -> str:
        """The two record counts, side by side and never added.

        One line, printed wherever the summary is, because the number a reader
        wants — how much of this has a person read — is not derivable from
        either figure alone (ADR-0080 consequence 4).
        """
        line = (
            f"{self.gold.total} signed record(s) in eval/gold/ · "
            f"{self.authored.total} authored record(s) in authored/, none validated"
        )
        if self.authored.refused:
            line += f" ({len(self.authored.refused)} refused)"
        unevidenced = self.authored.by_basis().get("general_knowledge", 0)
        if unevidenced:
            line += f", {unevidenced} of them unevidenced"
        return line


# ---------------------------------------------------------------------------
# Structural checks — no snapshot required
# ---------------------------------------------------------------------------


def _readable(gold: GoldSet) -> Iterator[Finding]:
    for path, reason in gold.unreadable:
        yield Finding(Severity.DEFECT, "gold-file", path.name, reason)


def _schema(gold: GoldSet) -> Iterator[Finding]:
    for record_type, record in gold.all_records():
        for error in validate(record, record_type):
            yield Finding(
                Severity.DEFECT,
                "schema",
                str(record.get("id") or f"<{record_type} with no id>"),
                f"at {error.path or '<root>'}: {error.message}",
            )


def _identifiers(gold: GoldSet) -> Iterator[Finding]:
    seen: dict[str, str] = {}
    for record_type, record in gold.all_records():
        identifier = record.get("id")
        if not isinstance(identifier, str):
            continue  # the schema has already said so
        prefix = ID_PREFIXES[record_type]
        if not identifier.startswith(prefix + "-"):
            yield Finding(
                Severity.DEFECT, "ids", identifier,
                f"a {record_type} record must carry a {prefix}- id, and this one is "
                f"in {goldset.FILE_FOR[record_type]}",
            )
        if identifier in seen:
            yield Finding(
                Severity.DEFECT, "ids", identifier,
                f"used twice — once as a {seen[identifier]}, once as a {record_type}"
                if seen[identifier] != record_type
                else "used by two records",
            )
        seen[identifier] = record_type
        if identifier in gold.retired_ids:
            entry = gold.retired_ids[identifier]
            yield Finding(
                Severity.DEFECT, "ids", identifier,
                "reuses a retired id"
                + (f" (withdrawn {entry['retired_on']})" if entry.get("retired_on") else "")
                + ". Identifiers are allocated by appending and a gap left by a "
                "withdrawal is never filled (IDENTIFIERS.md §3).",
            )


def _cross_references(gold: GoldSet) -> Iterator[Finding]:
    known: dict[str, set[str]] = {}
    for record_type, record in gold.all_records():
        identifier = record.get("id")
        if isinstance(identifier, str):
            known.setdefault(ID_PREFIXES[record_type], set()).add(identifier)

    for record_type, fields in CROSS_REFERENCES.items():
        for record in gold[record_type]:
            subject = str(record.get("id") or f"<{record_type} with no id>")
            for path, prefixes in fields.items():
                for pointer, value in read_path(record, path):
                    if not isinstance(value, str):
                        continue
                    if any(value in known.get(prefix, ()) for prefix in prefixes):
                        continue
                    yield Finding(
                        Severity.DEFECT, "cross-reference", subject,
                        f"{pointer} names {value}, and no such record exists in "
                        + " or ".join(goldset.FILE_FOR[t] for t in RECORD_TYPES
                                      if ID_PREFIXES[t] in prefixes),
                    )


def _approval(gold: GoldSet) -> Iterator[Finding]:
    for record_type, record in gold.all_records():
        subject = str(record.get("id") or f"<{record_type} with no id>")
        for field in ("approved_by", "approved_date"):
            if record.get(field) is None:
                yield Finding(
                    Severity.GAP, "approval", subject,
                    f"{field} is null — the record is transcribed but not approved "
                    "(CLAUDE.md rule 4)",
                )


def _judgement_gaps(gold: GoldSet) -> Iterator[Finding]:
    """Judgement fields left null in a **signed** record.

    The message this used to carry — *"it needs the expert, and nothing here may
    supply it"* — was true until 2026-09-08 and false afterwards. ADR-0079 lets
    an agent author a judgement of exactly this kind. What it does not let an
    agent do is fill the field *here*: this record was signed by a person on a
    date, and writing an unreviewed value into it would put unsigned content
    inside a signature, which is the whole reason a concept's type is a separate
    record rather than a field on the concept (ADR-0071).

    So the gap is real and the route round it is not the one the old message
    implied. There is no record type holding a modality apart from the
    relationship it belongs to, which is why these five are still gaps and not
    authored work.
    """
    for record_type, fields in JUDGEMENT_FIELDS.items():
        for record in gold[record_type]:
            subject = str(record.get("id") or f"<{record_type} with no id>")
            for field in fields:
                if record.get(field) is None:
                    yield Finding(
                        Severity.GAP, "judgement", subject,
                        f"{field} is null in a signed record. An agent may author "
                        "this judgement (ADR-0079) but may not write it here — "
                        "that would put unreviewed content inside a signature. It "
                        "needs either the expert or a record type of its own, the "
                        "way a concept's type got one (ADR-0071)",
                    )
    for record in gold["gold_concept"]:
        if not record.get("not_labels"):
            yield Finding(
                Severity.NOTE, "not_labels", str(record.get("id")),
                "no not_labels. Correct where no near-miss exists, and the most "
                "valuable field in the record where one does (guide §5.3)",
            )
    for record in gold["prohibited_use"]:
        if record.get("detectable_by") == "test" and not record.get("test_ref"):
            yield Finding(
                Severity.NOTE, "test_ref", str(record.get("id")),
                "detectable_by: test, but no test_ref yet",
            )


def _coverage(gold: GoldSet) -> Iterator[Finding]:
    """The two enum-coverage requirements §7 states explicitly."""
    for record_type, field, label in (
        ("competency_question", "category", "competency-question category"),
        ("prohibited_use", "kind", "prohibited-use kind"),
    ):
        required = [v for v in enum_values(record_type, field) if v is not None]
        present = {record.get(field) for record in gold[record_type]}
        for value in required:
            if value not in present:
                yield Finding(
                    Severity.GAP, "coverage", f"{label} '{value}'",
                    "no record carries it. §7 requires the set to span all "
                    f"{len(required)}",
                )

    questions = gold["gold_search_question"]
    if questions:
        plain = sum(1 for q in questions if q.get("uses_manual_terminology") is False)
        if plain * 2 <= len(questions):
            yield Finding(
                Severity.GAP, "coverage", "search questions",
                f"{plain} of {len(questions)} avoid Manual terminology; §7 asks for "
                "a majority, because that is what tests vocabulary expansion",
            )

    for record in gold["competency_question"]:
        sources = record.get("expected_sources") or {}
        if isinstance(sources, dict) and not sources.get("required"):
            yield Finding(
                Severity.GAP, "coverage", str(record.get("id")),
                "expected_sources.required is empty — without it the answer cannot "
                "be marked wrong for missing a passage",
            )


# ---------------------------------------------------------------------------
# Resolution checks — need the pinned snapshot
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Passage:
    """What a ref landed on, reduced to what the checks need."""

    kind: str
    text: str | None
    content_hash: str | None


def _passage(corpus: Corpus, ref: str) -> _Passage | None:
    """Resolve a ref against the snapshot, by string equality and nothing else.

    A ref whose *level* the grammar cannot decide (Q-18) is tried at both
    levels: `MANUAL` may be a page or a chunk, and `LEGISLATION` a provision or
    a unit. That is the loader's job precisely because the grammar cannot do it.
    """
    try:
        parsed = parse_ref(ref)
    except InvalidRef:
        return None
    if parsed.kind is RefKind.CASE:
        return _Passage("case", None, None)
    if parsed.kind in (RefKind.MANUAL_CHUNK, RefKind.MANUAL_PAGE, RefKind.MANUAL):
        chunk = corpus.chunks.get(ref)
        if chunk is not None:
            return _Passage("chunk", chunk.text, chunk.content_hash)
        page = corpus.pages.get(ref)
        if page is not None:
            return _Passage("page", None, page.content_hash)
        return None
    resolved = corpus.resolve_provision(ref)
    if resolved is None:
        return None
    kind = "provision" if ref in corpus.provisions else "unit"
    return _Passage(kind, resolved.text, resolved.content_hash)


def passage_at(corpus: Corpus, ref: str) -> _Passage | None:
    """The ref-to-passage resolution above, under a name other modules may use.

    `review/seed/` has to resolve a ref and land a span exactly the way the
    harness does, or a seed record could pass one check and fail the other for
    no reason a reader could see. One resolver, two callers.
    """
    return _passage(corpus, ref)


def _resolution(gold: GoldSet, corpus: Corpus) -> Iterator[Finding]:
    for record_type, record in gold.all_records():
        subject = str(record.get("id") or f"<{record_type} with no id>")
        for path in ref_paths(record_type):
            for pointer, value in read_path(record, path):
                if not isinstance(value, str):
                    continue
                passage = _passage(corpus, value)
                if passage is None:
                    yield Finding(
                        Severity.DEFECT, "resolution", subject,
                        f"{pointer} = {value} resolves to nothing in the pinned "
                        f"snapshot ({corpus.pin.commit[:12]})",
                    )
                elif passage.kind == "case":
                    yield Finding(
                        Severity.NOTE, "resolution", subject,
                        f"{pointer} = {value} is a case citation. No decision text "
                        "exists anywhere in the programme, so it is checked for "
                        "grammar only (Q-11)",
                    )


def _spans(gold: GoldSet, corpus: Corpus) -> Iterator[Finding]:
    for record_type, surface_field in SPAN_SURFACE.items():
        for record in gold[record_type]:
            subject = str(record.get("id") or f"<{record_type} with no id>")
            span = record.get("span")
            ref = record.get("source_ref")
            if span is None or not isinstance(ref, str):
                continue  # a null span is a gap, already reported
            passage = _passage(corpus, ref)
            if passage is None:
                continue  # already reported as unresolvable
            if passage.text is None:
                yield Finding(
                    Severity.DEFECT, "span", subject,
                    f"source_ref {ref} is a {passage.kind}, which holds no text for "
                    "a span to land in. Spans address a chunk, a provision or a unit",
                )
                continue
            start, end = span
            if end > len(passage.text) or start > end:
                yield Finding(
                    Severity.DEFECT, "span", subject,
                    f"span [{start}, {end}] falls outside {ref}, which is "
                    f"{len(passage.text)} characters",
                )
                continue
            recorded = record.get(surface_field)
            found = passage.text[start:end]
            if isinstance(recorded, str) and found != recorded:
                yield Finding(
                    Severity.DEFECT, "span", subject,
                    f"{surface_field} is {recorded!r} but {ref}[{start}:{end}] is "
                    f"{found!r}. The surface is recorded exactly as it appears, so a "
                    "tidied-up one does not land",
                )


def _staleness(gold: GoldSet, corpus: Corpus) -> Iterator[Finding]:
    for record_type, record in gold.all_records():
        recorded = record.get("source_content_hash")
        ref = record.get("source_ref")
        if not isinstance(recorded, str) or not isinstance(ref, str):
            continue
        passage = _passage(corpus, ref)
        if passage is None or passage.content_hash is None:
            continue
        if passage.content_hash != recorded:
            yield Finding(
                Severity.DEFECT, "staleness",
                str(record.get("id") or f"<{record_type} with no id>"),
                f"source_content_hash was taken against {recorded[:19]}… and {ref} "
                f"now hashes to {passage.content_hash[:19]}…. The passage has "
                "changed, so the record returns to the expert — it is never "
                "silently refreshed (IDENTIFIERS.md §5)",
            )


# ---------------------------------------------------------------------------
# The authored store — the same checks, plus the ones that keep it honest
# ---------------------------------------------------------------------------
#
# `eval/gold/` is checked as a set of expert judgements that arrived; `authored/`
# is checked as a set of machine judgements that must never be mistaken for them
# (ADR-0079, ADR-0080). Most checks transfer unchanged — an authored concept is
# the same shape as a signed one, and is validated against the same schema. Four
# do not, and they are the reason this section exists rather than a second call
# to the same functions with a different directory:
#
# - **`approved_by` filled in is a defect, not a gap.** On a gold record a null
#   `approved_by` is the thing waiting to happen. On an authored record it is the
#   only correct value, and a name in it is the one failure the whole scheme was
#   built to prevent (ADR-0079 guard 3).
# - **An id in both stores is a defect.** One sequence, one `GC-0123`, wherever
#   it lives (ADR-0080 consequence 1). Two records under one id is two answers to
#   "what did the project decide", and the graph would hold whichever it read
#   second.
# - **`review_status: approved` in `authored/` is a defect.** Approval moves a
#   record to `eval/gold/` through `tmk-transcribe` and by no other route, so an
#   approved record sitting here is either a transcription that did not finish or
#   a status an agent wrote. `rejected` is *not* a defect: a rejected record stays
#   here, because `eval/gold/` holds no rejections. This one is the section's only
#   judgement call — HANDOFF Q27, ADR-0090.
# - **`general_knowledge` is a note, counted and listed, never a defect.** It is
#   the honest label for an unevidenced judgement and forbidding it would only
#   buy a dishonest `corpus_inferred`. What it must never be is invisible: a
#   store quietly filling with unevidenced records is the failure ADR-0079's
#   consequence 2 says to watch for, and a proportion is the only way to see it.

#: The checks in this section, by the `check` name they report under. Named so a
#: caller can group the authored findings without matching on message text, and
#: so a check that stops firing is visible as a name nobody produces.
AUTHORED_CHECKS: tuple[str, ...] = (
    "authored-file",
    "authored-envelope",
    "authored-schema",
    "authored-approval",
    "authored-ids",
    "authored-basis",
    "authored-evidence",
)


def _authored_files(authored: AuthoredSet) -> Iterator[Finding]:
    for path, reason in authored.unreadable:
        yield Finding(Severity.DEFECT, "authored-file", path.name, reason)


def _authored_envelopes(authored: AuthoredSet) -> Iterator[Finding]:
    """Every record that cannot say who wrote it, why, or on what evidence.

    Reported one finding per schema error and never collapsed to "N records are
    malformed": the record is refused, so this message is the only description
    of it that reaches anybody.
    """
    for entry in authored.refused:
        for error in entry.envelope_errors:
            yield Finding(
                Severity.DEFECT,
                "authored-envelope",
                entry.record_id,
                f"at {error.path}: {error.message}. Refused — it is not counted, "
                f"not built into the graph, and not lost "
                f"({entry.source_file.name} record {entry.position})",
            )


def _authored_schema(authored: AuthoredSet) -> Iterator[Finding]:
    """The record itself, against its own record-type schema.

    The envelope is stripped before this runs, so an authored concept is checked
    against exactly the schema a signed concept is checked against. That is the
    point: same shape, different provenance, and nothing in the shape says which
    store a record came from.
    """
    for record_type, record in authored.all_records():
        for error in validate(record, record_type):
            yield Finding(
                Severity.DEFECT,
                "authored-schema",
                str(record.get("id") or f"<{record_type} with no id>"),
                f"at {error.path or '<root>'}: {error.message}",
            )


def _authored_approval(authored: AuthoredSet) -> Iterator[Finding]:
    """Nothing in here is signed, and nothing in here may say that it is."""
    for entry in authored.all_entries():
        for approval_field in ("approved_by", "approved_date"):
            value = entry.record.get(approval_field)
            if value is not None:
                yield Finding(
                    Severity.DEFECT,
                    "authored-approval",
                    entry.record_id,
                    f"{approval_field} is {value!r}. It means a person read this "
                    f"record and signed it, and no agent writes it — not with a "
                    f"name, not with a model id, not with initials (ADR-0079 "
                    f"guard 3). A signed record lives in eval/gold/ and gets "
                    f"there through tmk-transcribe alone",
                )
        if entry.review_status == "approved":
            yield Finding(
                Severity.DEFECT,
                "authored-approval",
                entry.record_id,
                "review_status is 'approved' in authored/. Approval moves a "
                "record to eval/gold/ through tmk-transcribe and by no other "
                "route (ADR-0080), so an approved record sitting here is either "
                "a transcription that did not finish or a status an agent wrote",
            )


def _authored_identifiers(authored: AuthoredSet, gold: GoldSet) -> Iterator[Finding]:
    """One sequence across both stores (ADR-0080 consequence 1)."""
    signed = {
        str(record["id"]): record_type
        for record_type, record in gold.all_records()
        if isinstance(record.get("id"), str)
    }
    seen: dict[str, str] = {}
    for entry in authored.all_entries():
        identifier = entry.record.get("id")
        if not isinstance(identifier, str):
            continue  # the schema check has already said so
        prefix = ID_PREFIXES[entry.record_type]
        if not identifier.startswith(prefix + "-"):
            yield Finding(
                Severity.DEFECT, "authored-ids", identifier,
                f"an authored {entry.record_type} must carry a {prefix}- id, and "
                f"this one is in {authored_store.FILE_FOR[entry.record_type]}",
            )
        if identifier in seen:
            yield Finding(
                Severity.DEFECT, "authored-ids", identifier,
                "used by two records in authored/"
                if seen[identifier] == entry.record_type
                else f"used twice — once as a {seen[identifier]}, once as a "
                f"{entry.record_type}",
            )
        seen[identifier] = entry.record_type
        if identifier in signed:
            yield Finding(
                Severity.DEFECT, "authored-ids", identifier,
                f"also names a signed {signed[identifier]} in "
                f"{goldset.FILE_FOR[signed[identifier]]}. Ids are allocated from "
                "one sequence across both stores, so this is two records under "
                "one name and the graph would hold whichever it read second "
                "(ADR-0080 consequence 1). Where an authored record covers ground "
                "a signed one already holds, the signed one wins and the authored "
                "one is retired — it does not share its id",
            )
        if identifier in gold.retired_ids:
            entry_meta = gold.retired_ids[identifier]
            yield Finding(
                Severity.DEFECT, "authored-ids", identifier,
                "reuses a retired id"
                + (f" (withdrawn {entry_meta['retired_on']})"
                   if entry_meta.get("retired_on") else "")
                + ". A gap left by a withdrawal is never filled "
                "(IDENTIFIERS.md §3)",
            )


def _authored_basis(authored: AuthoredSet) -> Iterator[Finding]:
    """What each record rests on — and the count of the ones resting on nothing."""
    unevidenced = [
        entry for entry in authored.all_entries()
        if entry.sound and entry.authoring_basis == "general_knowledge"
    ]
    for entry in unevidenced:
        yield Finding(
            Severity.NOTE, "authored-basis", entry.record_id,
            "authoring_basis: general_knowledge — the corpus does not say this "
            "and it was written from what the model knows. Not wrong, and not "
            "evidenced. A reviewer reaches this before an evidenced record",
        )
    if unevidenced:
        yield Finding(
            Severity.NOTE, "authored-basis", "authored/",
            f"{len(unevidenced)} of {authored.total} authored record(s) carry no "
            "evidence at all. Watch the proportion rather than the number: a "
            "store filling with general_knowledge is ADR-0079 consequence 2 "
            "happening quietly",
        )
    # `expert_should_check` per record only where the record is tier 3 — the
    # schema says it is required in practice there and cannot enforce it,
    # because tier lives on the record and not in the envelope. Everywhere else
    # it is one aggregate line: at volume, a note per record is a page of
    # identical text that nobody reads, and the thing worth knowing is the
    # proportion.
    blank: list[AuthoredRecord] = []
    for entry in authored.all_entries():
        if not entry.sound or entry.authoring_basis == "general_knowledge":
            continue
        if entry.envelope and entry.envelope.get("expert_should_check"):
            continue
        blank.append(entry)
        if entry.record.get("tier") == 3:
            yield Finding(
                Severity.NOTE, "authored-basis", entry.record_id,
                "expert_should_check is empty on a tier 3 record. Tier 3 is the "
                "judgement the guide says is most likely to be contested, and "
                "this is the field that tells a reviewer where to start",
            )
    if blank:
        yield Finding(
            Severity.NOTE, "authored-basis", "authored/",
            f"{len(blank)} evidenced authored record(s) name nothing under "
            "expert_should_check. It is a pointer at the thing most likely to be "
            "wrong, and an empty one usually means the alternatives were not "
            "looked for",
        )


def _authored_evidence(authored: AuthoredSet, corpus: Corpus) -> Iterator[Finding]:
    """Does the evidence exist, and does it say what the record says it says.

    The check the authored store lives or dies on. `authored/README.md`: *"A
    `corpus_explicit` claim whose span does not support it is the worst thing
    that can be written here, because it is a lie a machine will later
    certify."* This is what stops that being a matter of good intentions.
    """
    for entry in authored.all_entries():
        if not entry.sound:
            continue
        for index, item in enumerate(entry.evidence()):
            where = f"authored.evidence[{index}]"
            ref = item.get("ref")
            if not isinstance(ref, str):
                continue  # the envelope schema has already said so
            passage = _passage(corpus, ref)
            if passage is None:
                yield Finding(
                    Severity.DEFECT, "authored-evidence", entry.record_id,
                    f"{where}.ref = {ref} resolves to nothing in the pinned "
                    f"snapshot ({corpus.pin.commit[:12]}). An authored record "
                    "cites the corpus by the corpus's own keys or it cites "
                    "nothing",
                )
                continue
            if passage.kind == "case":
                yield Finding(
                    Severity.NOTE, "authored-evidence", entry.record_id,
                    f"{where}.ref = {ref} is a case citation, checked for grammar "
                    "only — no decision text exists anywhere in the programme "
                    "(Q-11)",
                )
                continue

            recorded_hash = item.get("content_hash")
            if (
                isinstance(recorded_hash, str)
                and passage.content_hash
                and recorded_hash != passage.content_hash
            ):
                yield Finding(
                    Severity.DEFECT, "authored-evidence", entry.record_id,
                    f"{where}.content_hash was taken against {recorded_hash[:19]}… "
                    f"and {ref} now hashes to {passage.content_hash[:19]}…. The "
                    "passage under this record has moved, so the record is stale "
                    "and is re-authored rather than silently refreshed "
                    "(IDENTIFIERS.md §5)",
                )

            span = item.get("span")
            if span is None:
                continue
            if passage.text is None:
                yield Finding(
                    Severity.DEFECT, "authored-evidence", entry.record_id,
                    f"{where}.ref {ref} is a {passage.kind}, which holds no text "
                    "for a span to land in. Spans address a chunk, a provision or "
                    "a unit",
                )
                continue
            start, end = span
            if end > len(passage.text) or start > end:
                yield Finding(
                    Severity.DEFECT, "authored-evidence", entry.record_id,
                    f"{where}.span [{start}, {end}] falls outside {ref}, which is "
                    f"{len(passage.text)} characters",
                )
                continue
            quote = item.get("quote")
            if isinstance(quote, str) and passage.text[start:end] != quote:
                yield Finding(
                    Severity.DEFECT, "authored-evidence", entry.record_id,
                    f"{where}.quote is {quote!r} but {ref}[{start}:{end}] is "
                    f"{passage.text[start:end]!r}. A quote is copied from the "
                    "snapshot character for character; one that will not land "
                    "means the passage was retyped, and a retyped passage is not "
                    "evidence (ADR-0045)",
                )


def _authored(authored: AuthoredSet, gold: GoldSet) -> Iterator[Finding]:
    """Every authored check that needs no snapshot."""
    yield from _authored_files(authored)
    yield from _authored_envelopes(authored)
    yield from _authored_schema(authored)
    yield from _authored_approval(authored)
    yield from _authored_identifiers(authored, gold)
    yield from _authored_basis(authored)


# ---------------------------------------------------------------------------
# The completeness gate
# ---------------------------------------------------------------------------


def _gate(gold: GoldSet, root: Path) -> Iterator[Finding]:
    """§7's checklist, as the thing that makes this suite red today.

    It fails on **absence**: a document not written, a count under its band. It
    never fails on content, which stays expert-judged. Every message names the
    deliverable and what it is waiting for, so the failure output reads as a
    status report — which is the defence ADR-0018 says a permanently red harness
    will need.
    """
    for deliverable in DELIVERABLES:
        if deliverable.kind == "document":
            path = root / deliverable.path
            if not path.exists():
                yield Finding(
                    Severity.GAP, "completeness", deliverable.path,
                    f"{deliverable.label} — not written",
                )
            elif not path.read_text(encoding="utf-8").strip():
                yield Finding(
                    Severity.GAP, "completeness", deliverable.path,
                    f"{deliverable.label} — the file exists and is empty",
                )
            continue

        count = gold.count(deliverable.record_type)
        target = band(deliverable)
        if deliverable.minimum is not None and count < deliverable.minimum:
            yield Finding(
                Severity.GAP, "completeness",
                goldset.FILE_FOR[deliverable.record_type],
                f"{deliverable.label} — {count} of {target}",
            )
        elif deliverable.maximum is not None and count > deliverable.maximum:
            yield Finding(
                Severity.GAP, "completeness",
                goldset.FILE_FOR[deliverable.record_type],
                f"{deliverable.label} — {count}, above the band of {target}. Report "
                "the number and ask rather than deleting records to fit",
            )


def band(deliverable: Deliverable) -> str:
    if deliverable.minimum is not None and deliverable.maximum is not None:
        return f"{deliverable.minimum}–{deliverable.maximum}"
    if deliverable.minimum is not None:
        return f"at least {deliverable.minimum}"
    return "no target"


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------


def run(
    *,
    gold_dir: Path | None = None,
    authored_dir: Path | None = None,
    root: Path | None = None,
    corpus: Corpus | None = None,
    with_resolution: bool = True,
) -> Report:
    """Run every check that can run, and say which ones could not.

    `corpus` is taken as given when supplied and loaded otherwise. A snapshot
    that will not load does not raise here: it is recorded as a gap, because a
    harness that cannot open the corpus has not verified Stage 0 and must not
    report it complete.

    Both stores are read and both are checked, and no finding merges them. The
    completeness gate below still counts `eval/gold/` alone: §7's bands measure
    what an expert delivered, and an authored record is not that — counting one
    towards them would report Stage 0 finished on the strength of records
    nobody has read (ADR-0080 consequence 3).
    """
    root = root or REPO_ROOT
    gold = goldset.load(gold_dir or (root / "eval" / "gold"))
    authored = authored_store.load(authored_dir or (root / "authored"))

    findings: list[Finding] = []
    findings.extend(_readable(gold))
    findings.extend(_schema(gold))
    findings.extend(_identifiers(gold))
    findings.extend(_cross_references(gold))
    findings.extend(_approval(gold))
    findings.extend(_judgement_gaps(gold))
    findings.extend(_coverage(gold))
    findings.extend(_authored(authored, gold))
    findings.extend(_gate(gold, root))

    skipped: str | None = None
    if not with_resolution:
        skipped = "not requested (--no-resolution)"
    elif corpus is None:
        try:
            corpus = load_corpus()
        except (UnpinnedSnapshot, SnapshotMismatch, FileNotFoundError) as error:
            skipped = str(error)
            corpus = None

    if corpus is not None:
        findings.extend(_resolution(gold, corpus))
        findings.extend(_spans(gold, corpus))
        findings.extend(_staleness(gold, corpus))
        findings.extend(_authored_evidence(authored, corpus))
    else:
        findings.append(
            Finding(
                Severity.GAP, "resolution", "data/upstream/",
                f"the resolution checks did not run: {skipped}. Every ref, span and "
                "hash in the gold set is therefore unverified — run "
                "`tmk-fetch-upstream` first",
            )
        )

    return Report(
        findings=tuple(findings),
        gold=gold,
        resolution_ran=corpus is not None,
        resolution_skipped=skipped,
        pin_commit=corpus.pin.commit if corpus is not None else None,
        authored=authored,
    )

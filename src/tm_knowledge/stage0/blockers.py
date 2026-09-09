"""Why each remaining seed record is not in `eval/gold/`, and what it holds.

`tmk-coverage` answers *what is Stage 0 missing*. This answers the next question
down, and it is the one a reviewer can act on: **which single decision releases
the most records?**

The distinction matters because approval does not distribute over an interlinked
set (ADR-0048). After the first round the arithmetic stopped being obvious: 213
records carried `correct`, 190 reached the gold set, and the 23 that did not
were held by six records elsewhere in the set — some of them signed, some of
them rejected, none of them findable by reading a 178-row workbook in order.
Working the queue front to back spends an hour of specialist time on whichever
record happens to sort first. Working it by what it releases spends the same
hour on the record that unblocks eleven others.

Everything here is **derived from committed artefacts** — the ledgers in
`review/decisions/`, the surviving candidates in `review/seed/`, and the
approved records in `eval/gold/`. Nothing re-reads a returned workbook, so the
report stays true after the round that produced it, and no `.xlsx` reader is
needed to run it.

Three rules this module keeps, and they are the reason it is safe to generate:

1. **It never says what a decision should be.** It says a record names one that
   was rejected, and that the structural options are to repoint it or withdraw
   it — which is the gate's arithmetic, not a legal opinion (CLAUDE.md rule 1).
2. **It reports the reviewer's own words verbatim** where the ledger holds them.
   An amendment that has not been applied is quoted, not paraphrased.
3. **It uses the gate's own reasons**, imported from `transcribe`, so the report
   and the door cannot drift apart. If the gate grows a seventh reason, this
   report grows it too or fails loudly on an unmapped one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.stage0 import goldset, seed as seed_module
from tm_knowledge.stage0.harness import CROSS_REFERENCES
from tm_knowledge.stage0.schemas import ID_PREFIXES, RECORD_TYPES, read_path
from tm_knowledge.stage0.transcribe import (
    AMENDMENT_PENDING,
    CHILD_UNSETTLED,
    DANGLING,
    NOT_REVIEWED,
    REJECTED,
    UNSIGNED,
    VERDICTS,
)

__all__ = [
    "Blocked",
    "ChildMark",
    "Analysis",
    "analyse",
    "render",
    "REASON_ORDER",
]

#: How the reasons are printed, worst-actionable first. A rejected record is
#: first because it is the only state that cannot be resolved by reviewing the
#: record itself — something else has to change.
REASON_ORDER: tuple[str, ...] = (
    REJECTED,
    AMENDMENT_PENDING,
    DANGLING,
    CHILD_UNSETTLED,
    UNSIGNED,
    NOT_REVIEWED,
)

#: What the reviewer is being asked to do about each state. Structural only —
#: every one of these is a statement about the gate, not about trade marks law.
WHAT_IS_NEEDED: dict[str, str] = {
    REJECTED: (
        "Nothing, on this record. It stays where it is so the rejection and its "
        "reason survive; what needs to change is every record that names it."
    ),
    AMENDMENT_PENDING: (
        "The amendment applied to the record, and the amended record signed. "
        "The correction is recorded; the record has not been changed to match."
    ),
    DANGLING: (
        "A decision on the record it names. Where that record was rejected, this "
        "one needs its pointer changed or the record withdrawn — expert call."
    ),
    CHILD_UNSETTLED: (
        "The marked row on its child sheet settled. The parent is signed; a "
        "grade or an expected inference inside it is not."
    ),
    UNSIGNED: "A name in `approved_by`. The verdict is `correct` and unsigned.",
    NOT_REVIEWED: "A verdict — `correct`, `amend` or `reject`.",
}

#: The record type of an id, by its prefix. `IDENTIFIERS.md` §3.
TYPE_FOR_PREFIX: dict[str, str] = {
    prefix: record_type for record_type, prefix in ID_PREFIXES.items()
}


@dataclass(frozen=True, slots=True)
class ChildMark:
    """One row on a child sheet the reviewer marked something other than correct."""

    parent_id: str
    sheet: str
    row: int
    verdict: str
    correction: str | None = None

    @property
    def parseable(self) -> bool:
        return self.verdict in VERDICTS

    def __str__(self) -> str:
        text = f"`{self.sheet}` row {self.row} — {self.verdict}"
        if self.correction:
            return f"{text}: {' '.join(self.correction.split())}"
        return text


@dataclass(frozen=True, slots=True)
class Blocked:
    """One surviving seed record, and the reason it is not approved."""

    record_id: str
    seed_id: str
    record_type: str
    reason: str
    #: The specific pointer, child row or reviewer's sentence behind the reason.
    detail: str = ""
    #: Record ids this one names that are not in `eval/gold/`. Present whether or
    #: not `reason` is DANGLING: a record can be both unreviewed and pointing at
    #: something unapproved, and the second fact does not stop mattering.
    waits_on: tuple[str, ...] = ()
    #: The reviewer's own words, where the ledger holds any.
    correction: str | None = None
    #: Child rows marked on this record's own sheets.
    marks: tuple[ChildMark, ...] = ()

    @property
    def rejected(self) -> bool:
        return self.reason == REJECTED


@dataclass(frozen=True)
class Analysis:
    """The whole review queue, plus who is waiting on whom."""

    entries: tuple[Blocked, ...] = ()
    #: record id -> every remaining record that cannot enter `eval/gold/` until
    #: this one is settled, transitively.
    holds: dict[str, tuple[str, ...]] = field(default_factory=dict)
    #: Ids named by a surviving record that exist neither in `eval/gold/` nor in
    #: `review/seed/`. Should be empty; a non-empty one is a defect, not a queue.
    unknown_targets: tuple[tuple[str, str], ...] = ()
    #: Child rows whose verdict cell is not one the gate reads.
    unparseable_marks: tuple[ChildMark, ...] = ()
    #: Pairs that name each other, so neither can be released by the other.
    cycles: tuple[tuple[str, ...], ...] = ()
    approved: int = 0
    gold_counts: dict[str, int] = field(default_factory=dict)

    def __getitem__(self, record_id: str) -> Blocked | None:
        return next((e for e in self.entries if e.record_id == record_id), None)

    @property
    def total(self) -> int:
        return len(self.entries)

    def by_reason(self, reason: str) -> tuple[Blocked, ...]:
        return tuple(e for e in self.entries if e.reason == reason)

    def counts(self) -> dict[str, int]:
        return {
            reason: len(self.by_reason(reason))
            for reason in REASON_ORDER
            if self.by_reason(reason)
        }

    @property
    def ranked(self) -> tuple[Blocked, ...]:
        """Everything that holds at least one other record, most first."""
        held = [e for e in self.entries if self.holds.get(e.record_id)]
        held.sort(key=lambda e: (-len(self.holds[e.record_id]), e.record_id))
        return tuple(held)

    @property
    def actionable(self) -> tuple[Blocked, ...]:
        """The records where one decision moves something, in the order to take them.

        Three kinds, and they are the whole of the critical path:

        - a record holding others whose own state is one a reviewer resolves
          directly — unreviewed, awaiting an amendment, or unsigned. Reviewing
          it is the root of a chain;
        - a record whose pointer names something **rejected**, which no amount of
          reviewing elsewhere can satisfy — it repoints or it withdraws;
        - a record held only by a marked row on its own child sheet, which is
          the cheapest kind there is: the parent is already signed.

        A record whose reason is DANGLING on something merely *unreviewed* is
        deliberately absent: there is nothing to decide on it. It is already
        correct and signed, and it moves when the record it names moves.

        Note what this does **not** require: that the root be waiting on nothing.
        `GA-0002` awaits an amendment and names `PU-0013` and `PU-0014`, both of
        which name `GA-0002` straight back. Nothing outside that triangle
        releases any of it; the amendment does, and demanding an unblocked root
        would have hidden the largest single decision on the queue.

        A record that is merely unreviewed and holds nothing is not here. It is
        in the ordinary queue, and the ordinary queue is `tmk-seed --pack`.
        """
        rejected_ids = {e.record_id for e in self.entries if e.rejected}
        decidable = (NOT_REVIEWED, AMENDMENT_PENDING, UNSIGNED, CHILD_UNSETTLED)
        chosen: list[Blocked] = []
        for entry in self.entries:
            if entry.rejected:
                continue
            root = entry.reason in decidable and bool(self.holds.get(entry.record_id))
            repoint = any(target in rejected_ids for target in entry.waits_on)
            child = entry.reason == CHILD_UNSETTLED
            if root or repoint or child:
                chosen.append(entry)
        chosen.sort(
            key=lambda e: (-len(self.holds.get(e.record_id, ())), e.record_id)
        )
        return tuple(chosen)

    def releases(self, record_id: str) -> dict[str, int]:
        """Record type -> how many of that type settling `record_id` releases."""
        counts: dict[str, int] = {}
        for other in self.holds.get(record_id, ()):
            entry = self[other]
            if entry is not None:
                counts[entry.record_type] = counts.get(entry.record_type, 0) + 1
        return counts


# ---------------------------------------------------------------------------
# Reading the ledgers
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Ruling:
    """One record's line in the ledger, flattened across every round."""

    verdict: str
    approved_by: str | None
    correction: str | None


def read_ledgers(
    root: Path | None = None,
) -> tuple[dict[str, _Ruling], tuple[ChildMark, ...]]:
    """Every recorded decision, keyed by seed id, plus every child mark.

    Later ledgers win, which is what makes a second round a correction of the
    first rather than a contradiction of it. `seed.recorded_verdicts()` does the
    same for the verdict alone; this needs the signature and the reviewer's own
    sentence as well, and those are only in the ledger.
    """
    root = root or seed_module.DECISIONS_DIR
    rulings: dict[str, _Ruling] = {}
    marks: list[ChildMark] = []
    if not root.exists():
        return rulings, ()

    for path in sorted(root.glob("*.yaml")):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(document, dict):
            continue
        for entry in document.get("decisions") or ():
            if not isinstance(entry, dict):
                continue
            seed_id = entry.get("seed_id")
            verdict = entry.get("verdict")
            if not seed_id or not verdict or verdict == "unreviewed":
                continue
            rulings[str(seed_id)] = _Ruling(
                verdict=str(verdict),
                approved_by=(
                    str(entry["approved_by"]) if entry.get("approved_by") else None
                ),
                correction=(
                    str(entry["correction"]) if entry.get("correction") else None
                ),
            )
        for entry in document.get("child_marks") or ():
            if not isinstance(entry, dict) or not entry.get("parent_id"):
                continue
            marks.append(
                ChildMark(
                    parent_id=str(entry["parent_id"]),
                    sheet=str(entry.get("sheet") or "?"),
                    row=int(entry.get("row") or 0),
                    verdict=str(entry.get("verdict") or "unreviewed"),
                    correction=(
                        str(entry["correction"]) if entry.get("correction") else None
                    ),
                )
            )
    return rulings, tuple(marks)


# ---------------------------------------------------------------------------
# The analysis
# ---------------------------------------------------------------------------


def _unsatisfied(record: dict[str, Any], record_type: str, approved: set[str]):
    """(pointer, id) for every cross-reference this record makes to a non-gold id."""
    for path, prefixes in CROSS_REFERENCES.get(record_type, {}).items():
        for pointer, value in read_path(record, path):
            if not isinstance(value, str):
                continue
            if value.split("-")[0] not in prefixes:
                continue
            if value not in approved:
                yield pointer, value


def _reason(
    ruling: _Ruling | None,
    unsatisfied: list[tuple[str, str]],
    marks: tuple[ChildMark, ...],
) -> tuple[str, str]:
    """(reason, detail), in the gate's own precedence.

    Deliberately the same order as `transcribe._gate` followed by the closure in
    `close_over_cross_references`: verdict first, then the signature, then the
    child rows, and the dangling pointer last because the closure runs after the
    gate. A record can satisfy several of these at once — `GA-0002` is both
    awaiting an amendment and naming two unapproved prohibitions — and reporting
    the one the door would report keeps this file and that one in step.
    """
    if ruling is None or ruling.verdict == "unreviewed":
        return NOT_REVIEWED, ""
    if ruling.verdict == "reject":
        return REJECTED, ruling.correction or ""
    if ruling.verdict == "amend":
        return AMENDMENT_PENDING, ruling.correction or ""
    if ruling.verdict not in VERDICTS:
        # Not a verdict the gate reads. It stops the row by name (ADR-0047),
        # which for this report is the same position as never having been read.
        return NOT_REVIEWED, f"verdict cell reads {ruling.verdict!r}"
    if not ruling.approved_by:
        return UNSIGNED, ""
    if marks:
        return CHILD_UNSETTLED, "; ".join(str(mark) for mark in marks)
    if unsatisfied:
        return DANGLING, "; ".join(f"{p} names {v}" for p, v in unsatisfied)
    # Signed, correct, nothing dangling, no marked child row — and still not in
    # `eval/gold/`. The gate has no seventh reason, so say so rather than
    # inventing one (rule 6).
    return NOT_REVIEWED, "signed and correct, but not promoted — reason unknown"


def _closure(waits: dict[str, tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
    """target -> everything transitively waiting on it.

    Cycle-safe by construction: reachability is accumulated into a visited set,
    and a record never appears in its own hold list. `PU-0016` names `GA-0016`
    and `GA-0016` names `PU-0016`, so a naive walk here does not terminate.
    """
    direct: dict[str, set[str]] = {}
    for source, targets in waits.items():
        for target in targets:
            direct.setdefault(target, set()).add(source)

    holds: dict[str, tuple[str, ...]] = {}
    for target in direct:
        seen: set[str] = set()
        frontier = list(direct[target])
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            frontier.extend(direct.get(current, ()))
        seen.discard(target)
        holds[target] = tuple(sorted(seen))
    return holds


def _cycles(waits: dict[str, tuple[str, ...]]) -> tuple[tuple[str, ...], ...]:
    """Mutually-waiting pairs. Reported because neither one releases the other."""
    found: set[tuple[str, ...]] = set()
    for source, targets in waits.items():
        for target in targets:
            if source in waits.get(target, ()):
                found.add(tuple(sorted((source, target))))
    return tuple(sorted(found))


def analyse(
    seed: seed_module.SeedSet | None = None,
    gold: goldset.GoldSet | None = None,
    decisions_dir: Path | None = None,
) -> Analysis:
    """Read the queue and work out who is waiting on whom."""
    seed = seed if seed is not None else seed_module.load()
    gold = gold if gold is not None else goldset.load()
    rulings, marks = read_ledgers(decisions_dir)

    approved: set[str] = set()
    gold_counts: dict[str, int] = {}
    for record_type in RECORD_TYPES:
        records = gold[record_type]
        gold_counts[record_type] = len(records)
        approved.update(str(r["id"]) for r in records if r.get("id"))

    marks_for: dict[str, list[ChildMark]] = {}
    for mark in marks:
        marks_for.setdefault(mark.parent_id, []).append(mark)

    surviving = {e.record_id for e in seed.envelopes}
    entries: list[Blocked] = []
    waits: dict[str, tuple[str, ...]] = {}
    unknown: list[tuple[str, str]] = []

    for envelope in seed.envelopes:
        ruling = rulings.get(envelope.seed_id)
        unsatisfied = list(_unsatisfied(envelope.record, envelope.record_type, approved))
        # A mark is only unsettled while its own verdict is unsettled. `reject`
        # on a child row drops that row from its parent and holds nothing.
        pending = tuple(
            mark
            for mark in marks_for.get(envelope.record_id, ())
            if mark.verdict != "reject"
        )
        reason, detail = _reason(ruling, unsatisfied, pending)
        targets = tuple(dict.fromkeys(value for _, value in unsatisfied))
        # A rejected record is not *waiting* on the things it names — it is
        # finished, negatively, and it stays in `review/seed/` only so the
        # rejection and its reason survive. Counting it as a dependent would
        # report `GA-0016` as holding `PU-0016`, which is backwards: the
        # rejection is why `GA-0016` has to change, not something `GA-0016`
        # releases.
        if targets and reason != REJECTED:
            waits[envelope.record_id] = targets
        for pointer, value in unsatisfied:
            if value not in surviving:
                unknown.append((envelope.record_id, f"{pointer} names {value}"))
        entries.append(
            Blocked(
                record_id=envelope.record_id,
                seed_id=envelope.seed_id,
                record_type=envelope.record_type,
                reason=reason,
                detail=detail,
                waits_on=targets,
                correction=ruling.correction if ruling else None,
                marks=pending,
            )
        )

    return Analysis(
        entries=tuple(entries),
        holds=_closure(waits),
        unknown_targets=tuple(unknown),
        unparseable_marks=tuple(m for m in marks if not m.parseable),
        cycles=_cycles(waits),
        approved=len(approved),
        gold_counts=gold_counts,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


LABELS: dict[str, str] = {
    "competency_question": "competency question",
    "gold_entity": "entity",
    "gold_concept": "concept",
    "gold_relationship": "relationship",
    "gold_search_question": "search question",
    "gold_retrieval_question": "retrieval question",
    "reasoning_expectation": "reasoning expectation",
    "prohibited_use": "prohibited use",
}


def _plural(count: int, label: str) -> str:
    return f"{count} {label}" if count == 1 else f"{count} {label}s"


def _releases_phrase(analysis: Analysis, record_id: str) -> str:
    counts = analysis.releases(record_id)
    if not counts:
        return "nothing else"
    parts = [
        _plural(count, LABELS.get(record_type, record_type))
        for record_type, count in sorted(counts.items(), key=lambda kv: -kv[1])
    ]
    return ", ".join(parts)


def _quote(text: str | None) -> list[str]:
    if not text:
        return []
    return [f"  > {' '.join(text.split())}"]


def render(analysis: Analysis, *, generated: str | None = None) -> str:
    """The worklist, as a document a reviewer can work top to bottom."""
    stamp = generated or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out: list[str] = [
        "<!-- Generated by tm_knowledge.stage0.blockers. Do not hand-edit. -->",
        "",
        "# What is holding the gold set",
        "",
        "Every seed record that has not reached `eval/gold/`, the reason it has",
        "not, and — the point of the document — **what each one releases if it is",
        "settled**. Approval does not distribute over an interlinked set, so the",
        "queue is not a list: settling one record can release a chain of others,",
        "and settling a different one releases nothing at all (ADR-0048).",
        "",
        "**Read the whole of this next paragraph before you read the queue, because",
        "the queue below is not a list of things waiting on a person.** On",
        "2026-09-08 the owner decided that the held seed records are resolved by an",
        "agent authoring them under ADR-0079, stamped `unreviewed`, rather than by",
        "waiting for an expert review round that had been paused since S010",
        "(ADR-0084). Every decision named below is therefore **agent work that has",
        "not been done yet**, not expert work that is owed. The one exception is",
        "the eight records a named expert rejected: a signed rejection is a human",
        "decision, ADR-0079 does not license reversing one, and they stay rejected",
        "(ADR-0084 consequence 2).",
        "",
        "Nothing here proposes an answer. Where a record names one that was",
        "rejected, the options given are the two the gate allows — repoint it or",
        "withdraw it — and this file does not choose between them (CLAUDE.md",
        "rule 6).",
        "",
        "| | |",
        "|---|---|",
        f"| In `eval/gold/` | {analysis.approved} |",
        f"| Still in `review/seed/` | {analysis.total} |",
        f"| Of those, holding at least one other | {len(analysis.ranked)} |",
        f"| Decisions on the critical path | {len(analysis.actionable)} |",
        f"| Generated | {stamp} |",
        "",
    ]

    counts = analysis.counts()
    if counts:
        out += ["## Why each one is held", "", "| reason | records |", "|---|---|"]
        out += [f"| {reason} | {count} |" for reason, count in counts.items()]
        out.append("")

    out += _start_here(analysis)
    out += _chains(analysis)
    out += _loose_ends(analysis)
    out += _remainder(analysis)
    return "\n".join(out).rstrip() + "\n"


def _start_here(analysis: Analysis) -> list[str]:
    actionable = analysis.actionable
    if not actionable:
        return [
            "## Start here",
            "",
            "Nothing on the queue releases anything else. What is left is the",
            "ordinary review queue — `tmk-seed --pack` prints it.",
            "",
        ]
    out = [
        "## Start here",
        "",
        f"{len(actionable)} decision(s), in the order that clears the most. Each",
        "one is a record where a decision moves something: it is the root",
        "of a chain, or it names a record that was rejected and so can never be",
        "satisfied by reviewing anything else, or it is a signed record held only",
        "by a marked row on its own child sheet.",
        "",
        "Since ADR-0084 the decision on each of these is an agent's to author and",
        "stamp `unreviewed` — not an expert's to sign. What an expert alone can",
        "still do is sign, and nothing below is waiting for that.",
        "",
    ]
    for index, entry in enumerate(actionable, start=1):
        held = analysis.holds.get(entry.record_id, ())
        out.append(
            f"### {index}. `{entry.record_id}` — {LABELS.get(entry.record_type, entry.record_type)}"
        )
        out.append("")
        out.append(f"- **State:** {entry.reason}")
        # The detail is only worth a line where it is not repeated below: an
        # amendment's detail *is* the reviewer's sentence, and a dangling
        # pointer's is expanded record by record under **Names**.
        if entry.detail and entry.reason not in (AMENDMENT_PENDING, DANGLING):
            out.append(f"- **Detail:** {entry.detail}")
        out.append(f"- **Needed:** {WHAT_IS_NEEDED.get(entry.reason, '—')}")
        out += _names_lines(analysis, entry)
        out.append(
            f"- **Releases:** {_releases_phrase(analysis, entry.record_id)}"
            + (f" — {', '.join(held)}" if held else "")
        )
        out.append(f"- **Seed id:** `{entry.seed_id}`")
        if entry.correction:
            out.append("- **The reviewer wrote:**")
            out += _quote(entry.correction)
        out.append("")
    return out


def _names_lines(analysis: Analysis, entry: Blocked) -> list[str]:
    """What this record points at, and the state of each thing it points at.

    The distinction this draws is the one that decides what to do. A pointer at
    a record the reviewer **rejected** can never be satisfied by reviewing
    anything else, so this record has to change. A pointer at a record that is
    merely unreviewed resolves itself the moment that record is read, and asking
    for a decision here would be asking twice.
    """
    if not entry.waits_on:
        return []
    lines = ["- **Names, and what each one is waiting for:**"]
    for target in entry.waits_on:
        other = analysis[target]
        if other is None:
            lines.append(f"  - `{target}` — not in `eval/gold/` and not in `review/seed/`")
            continue
        note = other.reason
        if other.rejected:
            note += " — this pointer cannot be satisfied; it changes or the record goes"
        elif other.waits_on:
            note += f", itself waiting on {', '.join(other.waits_on)}"
        lines.append(f"  - `{target}` — {note}")
    return lines


def _chains(analysis: Analysis) -> list[str]:
    ranked = analysis.ranked
    if not ranked:
        return []
    out = [
        "## Everything that holds something",
        "",
        "Read this as a dependency, not a ranking of importance: a record high up",
        "here is not more valuable than one below it, it is merely in more",
        "records' way.",
        "",
        "| record | state | holds | which |",
        "|---|---|---|---|",
    ]
    for entry in ranked:
        held = analysis.holds[entry.record_id]
        out.append(
            f"| `{entry.record_id}` | {entry.reason} | {len(held)} | "
            + ", ".join(f"`{identifier}`" for identifier in held)
            + " |"
        )
    out.append("")
    return out


def _loose_ends(analysis: Analysis) -> list[str]:
    out: list[str] = []
    if analysis.cycles:
        out += [
            "## Records that name each other",
            "",
            "Neither one can be released by settling the other, so one of the two",
            "pointers has to change or one of the records has to go.",
            "",
        ]
        out += [
            "- " + " ↔ ".join(f"`{identifier}`" for identifier in pair)
            for pair in analysis.cycles
        ]
        out.append("")
    if analysis.unparseable_marks:
        out += [
            "## Verdict cells nothing can read",
            "",
            "A cell that is not exactly `correct`, `amend` or `reject` stops its",
            "row by name rather than being read as the value it resembles",
            "(ADR-0047). Deciding what it meant is a person's job, and the",
            "decision goes in an addendum naming the record — never into the",
            "workbook, and never into a typo table (ADR-0051).",
            "",
        ]
        for mark in analysis.unparseable_marks:
            out.append(f"- **{mark.parent_id}** · {mark}")
        out.append("")
    if analysis.unknown_targets:
        out += [
            "## Pointers to nothing at all",
            "",
            "A surviving record names an id that is neither approved nor waiting.",
            "This is a defect rather than a queue entry — the id was constructed,",
            "not read.",
            "",
        ]
        for subject, detail in analysis.unknown_targets:
            out.append(f"- **{subject}** — {detail}")
        out.append("")
    return out


def _remainder(analysis: Analysis) -> list[str]:
    on_the_path = {entry.record_id for entry in analysis.actionable}
    rest = [
        entry
        for entry in analysis.entries
        if not analysis.holds.get(entry.record_id)
        and entry.record_id not in on_the_path
    ]
    if not rest:
        return []

    # Two very different populations, and lumping them together was the first
    # thing that made this report misleading. A record held *only* by a pointer
    # at something already on the worklist needs no decision of its own — it
    # lands when its blocker lands. Telling a reviewer it is on their queue asks
    # them to read twelve records that are already answered.
    carried = [entry for entry in rest if entry.reason == DANGLING]
    queue = [entry for entry in rest if entry.reason != DANGLING]

    out: list[str] = []
    if carried:
        out += [
            "## Carried by a decision above",
            "",
            f"{len(carried)} record(s) that are correct, signed, and held by",
            "nothing but a pointer at a record on the worklist. **No decision is",
            "needed on any of them.** They enter `eval/gold/` on the next run of",
            "`tmk-transcribe` after the record they name does.",
            "",
            "| record | names | which is settled by |",
            "|---|---|---|",
        ]
        for entry in sorted(carried, key=lambda e: e.record_id):
            roots = sorted(_roots_for(analysis, entry.record_id))
            out.append(
                f"| `{entry.record_id}` | "
                + ", ".join(f"`{t}`" for t in entry.waits_on)
                + " | "
                + (", ".join(f"`{t}`" for t in roots) or "—")
                + " |"
            )
        out.append("")

    if queue:
        by_type: dict[str, list[Blocked]] = {}
        for entry in queue:
            by_type.setdefault(entry.record_type, []).append(entry)
        out += [
            "## The ordinary queue",
            "",
            f"{len(queue)} record(s) that need a verdict and hold nothing else.",
            "They are still Stage 0 content — several record types cannot reach",
            "their target without them — they simply do not have to be done in any",
            "particular order. `tmk-seed --pack` prints them in full with their",
            "passages.",
            "",
            "| record type | records | held because |",
            "|---|---|---|",
        ]
        for record_type, entries in sorted(
            by_type.items(), key=lambda kv: (-len(kv[1]), kv[0])
        ):
            reasons: dict[str, int] = {}
            for entry in entries:
                reasons[entry.reason] = reasons.get(entry.reason, 0) + 1
            detail = "; ".join(
                f"{count} {reason}" for reason, count in sorted(reasons.items())
            )
            out.append(
                f"| {LABELS.get(record_type, record_type)} | {len(entries)} | {detail} |"
            )
        out.append("")
    return out


def _roots_for(analysis: Analysis, record_id: str) -> set[str]:
    """The decisions on the worklist that settle `record_id`, following its pointers.

    Walks the wait graph upward and stops at the first record that is on the
    **Start here** list, because that is the definition of a record somebody has
    to do something about. Anything else would send a reviewer to the wrong page:
    `GA-0006` names `PU-0013`, which is signed and correct and has nothing to
    decide; what releases both is the amendment on `GA-0002`. `GA-0018` names
    `PU-0012`, which names the rejected `CQ-0016`; the decision is `PU-0012`'s
    pointer, not the rejection, which is already made.

    The walk is cycle-safe by the visited set, and terminates on the record
    itself when nothing above it is actionable — an honest "nothing here yet"
    rather than an invented owner.
    """
    on_the_path = {entry.record_id for entry in analysis.actionable}
    seen: set[str] = set()
    roots: set[str] = set()
    frontier = [record_id]
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        if current in on_the_path and current != record_id:
            roots.add(current)
            continue
        node = analysis[current]
        if node is None or not node.waits_on:
            continue
        frontier.extend(target for target in node.waits_on if target not in seen)
    return roots


def identifiers(analysis: Analysis) -> tuple[str, ...]:
    """The actionable record ids, for `tmk-seed --only`."""
    return tuple(entry.record_id for entry in analysis.actionable)

"""The seed example set: candidates written to be corrected, never to be copied.

Everything else in `stage0/` exists to hold content an expert produced. This
module exists for the opposite direction, and the reason is a finding about the
people rather than about the data: the Trade Mark experts advising this project
report that they cannot readily *articulate* the judgements the Stage 0 record
types ask for, because those judgements are the tacit part of their practice.
Recognising a wrong answer is much cheaper for them than composing a right one
from a blank form (ADR-0043).

So this is a **red-pen surface**. It holds a large set of machine-written
example records over the pilot area, grounded in the pinned snapshot, shaped
exactly like the gold records they are modelled on — and marked, at every level
the repo has, as *not* project content:

- they live under `review/`, the quarantine ADR-0007 exists to protect;
- every file is `*.seed.yaml`, a name `goldset.py` does not read and will not
  load, so a seed file dropped into `eval/gold/` stops the harness rather than
  being counted;
- every record sits inside an **envelope** carrying provenance and a review
  verdict, so the record itself can never be lifted out and mistaken for one an
  expert wrote;
- `approved_by` and `approved_date` are null on every one of them, and a seed
  record that carries either is a **defect** this module refuses to pass. That
  check is the load-bearing one: the whole risk of a seed set is that it starts
  looking approved.

**Spans are never hand-written here.** A seed record carries `span: null` and
`source_content_hash: null`; `resolve()` finds the recorded `surface` (or
`supporting_text`) in the chunk and fills both from the snapshot. An expert who
corrects a surface form gets a new span for free, and nobody types an offset —
the promise `STAGE-0-INPUT-GUIDE.md` §3 makes, kept in the direction the guide
did not anticipate. Where a surface appears more than once in its chunk, the
envelope's `locate.occurrence` says which one is meant; an unqualified
ambiguity is reported, never silently resolved to the first hit (rule 6).

Nothing in here promotes anything. Promotion is `tmk-transcribe` reading back a
workbook with an expert's name in `approved_by`, exactly as it already works.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.refs import InvalidRef, RefKind, parse_ref
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.harness import SPAN_SURFACE, Finding, Severity, passage_at
from tm_knowledge.stage0.schemas import (
    ID_PREFIXES,
    RECORD_TYPES,
    read_path,
    ref_paths,
    validate,
)
from tm_knowledge.upstream.loader import Corpus

__all__ = [
    "SEED_DIR",
    "SEED_FILES",
    "VERDICTS",
    "Envelope",
    "SeedSet",
    "load",
    "resolve",
    "check",
    "coverage",
]

SEED_DIR = REPO_ROOT / "review" / "seed"

#: Filename -> record type. Deliberately *not* `goldset.GOLD_FILES`' names: the
#: `.seed.` infix is what makes a misfiled seed file loud instead of silent.
SEED_FILES: dict[str, str] = {
    f"{name.removesuffix('.yaml')}.seed.yaml": record_type
    for name, record_type in goldset.GOLD_FILES.items()
}

#: Record type -> filename, built from the map above so the two cannot diverge.
FILE_FOR: dict[str, str] = {value: key for key, value in SEED_FILES.items()}

#: Files under `review/seed/` that are not seed records and are not mistakes.
NOT_RECORDS = frozenset(
    {"README.md", "HOW-TO-CORRECT.md", "pilot-scope.seed.md", "measures.seed.md"}
)

#: What an expert writes in the verdict column. `unreviewed` is the state every
#: seed record ships in; the other three are the only things that move it.
VERDICTS: tuple[str, ...] = ("unreviewed", "correct", "amend", "reject")

_SEED_ID = re.compile(r"^SEED-(CQ|GE|GC|GR|GS|GA|GX|PU)-[0-9]{4}$")

#: The envelope's own keys. `locate` is optional; everything else is required,
#: because each of them is a thing a reader needs in order to trust the record
#: less than they would trust a gold one.
ENVELOPE_KEYS = frozenset(
    {"seed_id", "record_type", "why_this_example", "provenance", "review", "record"}
)
OPTIONAL_ENVELOPE_KEYS = frozenset({"locate"})

PROVENANCE_KEYS = frozenset(
    {"extraction_method", "model", "generator", "generated_on", "confidence",
     "review_status"}
)


class MalformedSeedFile(Exception):
    """A seed file that could not be read as a list of envelopes."""


@dataclass(frozen=True, slots=True)
class Envelope:
    """One example record, plus everything that says it is only an example."""

    seed_id: str
    record_type: str
    why_this_example: str
    record: dict[str, Any]
    provenance: dict[str, Any]
    review: dict[str, Any]
    locate: dict[str, Any] | None
    source_file: Path
    position: int
    #: The keys actually present in the file, so a misspelt one is reported
    #: rather than silently becoming a default. A typo in `locate` would
    #: otherwise turn an occurrence hint into an ambiguity error three checks
    #: later, pointing at the wrong thing.
    raw_keys: tuple[str, ...] = ()

    @property
    def record_id(self) -> str:
        return str(self.record.get("id") or f"<{self.record_type} with no id>")

    @property
    def verdict(self) -> str:
        return str(self.review.get("status") or "unreviewed")


@dataclass(frozen=True)
class SeedSet:
    """Whatever `review/seed/` holds, in file order, keyed by record type."""

    root: Path
    envelopes: tuple[Envelope, ...] = ()
    files: dict[str, Path] = field(default_factory=dict)
    #: (path, reason) for every file that could not be read at all.
    unreadable: tuple[tuple[Path, str], ...] = ()

    def __getitem__(self, record_type: str) -> tuple[Envelope, ...]:
        if record_type not in RECORD_TYPES:
            raise KeyError(f"unknown Stage 0 record type {record_type!r}")
        return tuple(e for e in self.envelopes if e.record_type == record_type)

    def count(self, record_type: str) -> int:
        return len(self[record_type])

    @property
    def total(self) -> int:
        return len(self.envelopes)

    def records(self, record_type: str) -> list[dict[str, Any]]:
        """The bare records of one type — for the workbook, and nothing else."""
        return [dict(envelope.record) for envelope in self[record_type]]


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------


def _read_envelopes(path: Path, record_type: str) -> tuple[Envelope, ...]:
    """Read one seed file into envelopes, materialising the file's defaults.

    A seed file is a mapping with `defaults` and `seeds`. The defaults exist for
    one reason: the provenance block is identical on every record in a file, and
    repeated forty times it becomes wallpaper that nobody reads. Stated once at
    the top of the file it is the first thing a reader sees. It is *materialised*
    onto every envelope here, so nothing downstream can encounter a record whose
    provenance is implicit — which is the whole of rule 8.
    """
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise MalformedSeedFile(f"not valid YAML: {error}") from error
    if document is None:
        return ()
    if not isinstance(document, dict):
        raise MalformedSeedFile(
            "expected a mapping with `defaults` and `seeds`, got "
            f"{type(document).__name__}"
        )
    defaults = document.get("defaults") or {}
    entries = document.get("seeds")
    if not isinstance(entries, list):
        raise MalformedSeedFile(
            f"`seeds` must be a list of envelopes, got {type(entries).__name__}"
        )

    envelopes: list[Envelope] = []
    for position, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise MalformedSeedFile(
                f"envelope {position} is a {type(entry).__name__}, not a mapping"
            )
        record = entry.get("record")
        envelopes.append(
            Envelope(
                seed_id=str(entry.get("seed_id") or ""),
                record_type=str(entry.get("record_type") or record_type),
                why_this_example=str(entry.get("why_this_example") or ""),
                record=record if isinstance(record, dict) else {},
                provenance={
                    **(defaults.get("provenance") or {}),
                    **(entry.get("provenance") or {}),
                },
                review={
                    **(defaults.get("review") or {}),
                    **(entry.get("review") or {}),
                },
                locate=entry.get("locate"),
                source_file=path,
                position=position,
                raw_keys=tuple(entry),
            )
        )
    return tuple(envelopes)


def load(root: Path | None = None) -> SeedSet:
    """Read `review/seed/`, in the order `goldset.GOLD_FILES` names the types.

    An unrecognised `.yaml` here is reported rather than skipped, for the reason
    `goldset` gives: a file quietly ignored because its name was misspelt is a
    set of judgements that silently did not count (rule 6).
    """
    root = root or SEED_DIR
    if not root.exists():
        return SeedSet(root=root)

    envelopes: list[Envelope] = []
    files: dict[str, Path] = {}
    unreadable: list[tuple[Path, str]] = []

    for path in sorted(root.iterdir()):
        if path.is_dir() or path.name in NOT_RECORDS or path.name.startswith("."):
            continue
        record_type = SEED_FILES.get(path.name)
        if record_type is None:
            unreadable.append(
                (
                    path,
                    "not a name review/seed/ reads. Seed files are "
                    f"{', '.join(sorted(SEED_FILES))}",
                )
            )
            continue
        try:
            found = _read_envelopes(path, record_type)
        except MalformedSeedFile as error:
            unreadable.append((path, str(error)))
            continue
        files[record_type] = path
        envelopes.extend(found)

    order = {name: index for index, name in enumerate(goldset.GOLD_FILES.values())}
    envelopes.sort(key=lambda e: (order.get(e.record_type, 99), e.seed_id))
    return SeedSet(
        root=root,
        envelopes=tuple(envelopes),
        files=files,
        unreadable=tuple(unreadable),
    )


# ---------------------------------------------------------------------------
# Resolving spans and hashes from the snapshot
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Resolution:
    """What `resolve()` worked out for one envelope."""

    envelope: Envelope
    record: dict[str, Any]
    #: The full text of the passage the record rests on, where it has one.
    passage_text: str | None = None
    heading_path: tuple[str, ...] = ()


def _occurrences(text: str, needle: str) -> list[int]:
    found: list[int] = []
    start = text.find(needle)
    while start != -1:
        found.append(start)
        start = text.find(needle, start + 1)
    return found


def resolve(
    seed: SeedSet, corpus: Corpus
) -> tuple[tuple[Resolution, ...], tuple[Finding, ...]]:
    """Fill every null `span` and `source_content_hash` from the snapshot.

    Returns resolved copies — the files on disk are not rewritten, because they
    carry the comments that make them readable and a round trip through a YAML
    dumper would eat them. The resolved records are what the review pack and the
    review workbook are built from.
    """
    resolutions: list[Resolution] = []
    findings: list[Finding] = []

    for envelope in seed.envelopes:
        record = dict(envelope.record)
        ref = record.get("source_ref")
        text: str | None = None
        heading: tuple[str, ...] = ()

        if isinstance(ref, str):
            found = passage_at(corpus, ref)
            if found is None:
                findings.append(
                    Finding(
                        Severity.DEFECT, "seed-resolution", envelope.seed_id,
                        f"source_ref {ref} resolves to nothing in the pinned "
                        f"snapshot ({corpus.pin.commit[:12]})",
                    )
                )
            else:
                text = found.text
                if found.content_hash and record.get("source_content_hash") is None:
                    record["source_content_hash"] = found.content_hash
                chunk = corpus.chunks.get(ref)
                if chunk is not None:
                    heading = tuple(chunk.heading_path)

        surface_field = SPAN_SURFACE.get(envelope.record_type)
        if surface_field and record.get("span") is None:
            findings.extend(_fill_span(envelope, record, surface_field, text))

        resolutions.append(
            Resolution(
                envelope=envelope,
                record=record,
                passage_text=text,
                heading_path=heading,
            )
        )

    return tuple(resolutions), tuple(findings)


def _fill_span(
    envelope: Envelope,
    record: dict[str, Any],
    surface_field: str,
    text: str | None,
) -> Iterator[Finding]:
    """Locate `surface_field`'s value in the passage, or say precisely why not."""
    surface = record.get(surface_field)
    if not isinstance(surface, str) or not surface:
        yield Finding(
            Severity.DEFECT, "seed-span", envelope.seed_id,
            f"{surface_field} is empty, so there is nothing to locate. A "
            f"{envelope.record_type} without it is not a record",
        )
        return
    if text is None:
        return  # unresolvable ref, already reported

    hits = _occurrences(text, surface)
    if not hits:
        yield Finding(
            Severity.DEFECT, "seed-span", envelope.seed_id,
            f"{surface_field} {surface[:60]!r} does not appear in "
            f"{record.get('source_ref')}. A surface is copied out of the passage "
            "verbatim — a tidied-up or retyped one does not land",
        )
        return

    wanted = (envelope.locate or {}).get("occurrence")
    if len(hits) > 1 and wanted is None:
        yield Finding(
            Severity.DEFECT, "seed-span", envelope.seed_id,
            f"{surface_field} {surface[:40]!r} appears {len(hits)} times in "
            f"{record.get('source_ref')}. Say which with locate.occurrence — "
            "picking the first would be a guess (rule 6)",
        )
        return
    index = 1 if wanted is None else int(wanted)
    if index < 1 or index > len(hits):
        yield Finding(
            Severity.DEFECT, "seed-span", envelope.seed_id,
            f"locate.occurrence is {index} but {surface_field} appears "
            f"{len(hits)} time(s) in {record.get('source_ref')}",
        )
        return
    start = hits[index - 1]
    record["span"] = [start, start + len(surface)]


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------


def _envelope_shape(seed: SeedSet) -> Iterator[Finding]:
    seen: dict[str, Envelope] = {}
    for envelope in seed.envelopes:
        subject = envelope.seed_id or f"{envelope.source_file.name}#{envelope.position}"

        if not _SEED_ID.match(envelope.seed_id):
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                "seed_id must read SEED-<series>-nnnn, e.g. SEED-GE-0001. It is "
                "what a correction refers to when the record's own id changes",
            )
        elif envelope.seed_id in seen:
            other = seen[envelope.seed_id]
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                f"seed_id is already used at {other.source_file.name}"
                f"#{other.position}",
            )
        else:
            seen[envelope.seed_id] = envelope

        if envelope.record_type not in RECORD_TYPES:
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                f"record_type {envelope.record_type!r} is not a Stage 0 record type",
            )
        if not envelope.why_this_example.strip():
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                "why_this_example is empty. An example whose point nobody wrote "
                "down cannot be judged, only copied — which is the failure mode "
                "this whole set is built to avoid",
            )
        if not envelope.record:
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject, "the envelope holds no record"
            )

        unknown = set(envelope.raw_keys) - ENVELOPE_KEYS - OPTIONAL_ENVELOPE_KEYS
        if unknown:
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                f"unknown envelope key(s): {', '.join(sorted(unknown))}. A "
                "misspelt key is a field nobody reads",
            )

        missing = PROVENANCE_KEYS - set(envelope.provenance)
        if missing:
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                f"provenance is missing {', '.join(sorted(missing))}. Unlabelled "
                "machine output is exactly what rule 8 forbids",
            )
        if envelope.provenance.get("review_status") not in (None, "candidate"):
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                "provenance.review_status on a seed record is 'candidate' and "
                "nothing else. A verdict belongs in review.status",
            )
        if envelope.verdict not in VERDICTS:
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                f"review.status is {envelope.verdict!r}; it is one of "
                f"{', '.join(VERDICTS)}",
            )
        if envelope.verdict in ("correct", "amend") and not envelope.review.get("expert"):
            yield Finding(
                Severity.DEFECT, "seed-envelope", subject,
                f"review.status is {envelope.verdict!r} with no reviewer named. A "
                "verdict without a name is not a recorded human decision (rule 4)",
            )
        if envelope.verdict == "amend" and not envelope.review.get("correction"):
            yield Finding(
                Severity.GAP, "seed-envelope", subject,
                "marked 'amend' with no correction written. The correction is the "
                "content — the verdict on its own carries nothing forward",
            )


def _never_approved(seed: SeedSet) -> Iterator[Finding]:
    """The check that keeps a seed set from becoming a gold set by accident."""
    for envelope in seed.envelopes:
        for field_name in ("approved_by", "approved_date"):
            if envelope.record.get(field_name) is not None:
                yield Finding(
                    Severity.DEFECT, "seed-approval", envelope.seed_id,
                    f"record.{field_name} is set. Nothing in review/seed/ is "
                    "approved — approval happens when a corrected workbook comes "
                    "back through tmk-transcribe with an expert's name on it "
                    "(rule 4, ADR-0043)",
                )


def _schema(seed: SeedSet, resolutions: tuple[Resolution, ...]) -> Iterator[Finding]:
    """Each record against the gold schema it is modelled on.

    Runs with or without a snapshot: a null `span` and a null
    `source_content_hash` are schema-valid, so shape errors are catchable on a
    bare clone and do not wait for a fetch.
    """
    for resolution in resolutions:
        for error in validate(resolution.record, resolution.envelope.record_type):
            yield Finding(
                Severity.DEFECT, "seed-schema", resolution.envelope.seed_id,
                f"{error.path or '<record>'}: {error.message}",
            )


def _identifiers(seed: SeedSet) -> Iterator[Finding]:
    """Record ids: unique here, in the right series, and not already in eval/gold/."""
    gold = goldset.load()
    taken = {
        str(record.get("id"))
        for _, record in gold.all_records()
        if record.get("id")
    } | set(gold.retired_ids)

    seen: dict[str, Envelope] = {}
    for envelope in seed.envelopes:
        identifier = envelope.record.get("id")
        if not isinstance(identifier, str):
            yield Finding(
                Severity.DEFECT, "seed-identifier", envelope.seed_id,
                "the record has no id",
            )
            continue
        prefix = ID_PREFIXES.get(envelope.record_type)
        if prefix and not identifier.startswith(prefix):
            yield Finding(
                Severity.DEFECT, "seed-identifier", envelope.seed_id,
                f"id {identifier} is not in the {prefix} series that "
                f"{envelope.record_type} uses",
            )
        if identifier in seen:
            yield Finding(
                Severity.DEFECT, "seed-identifier", envelope.seed_id,
                f"id {identifier} is already used by {seen[identifier].seed_id}",
            )
        else:
            seen[identifier] = envelope
        if identifier in taken:
            yield Finding(
                Severity.DEFECT, "seed-identifier", envelope.seed_id,
                f"id {identifier} is already allocated in eval/gold/ or retired. "
                "Seed ids are provisional, and they still may not collide — an id "
                "is never reused (IDENTIFIERS.md §3)",
            )


def _cross_references(seed: SeedSet) -> Iterator[Finding]:
    """`PU-*`, `GC-*`, `CQ-*`/`GA-*` pointers resolve inside the seed set."""
    known: dict[str, set[str]] = {}
    for envelope in seed.envelopes:
        identifier = envelope.record.get("id")
        if isinstance(identifier, str):
            known.setdefault(identifier.split("-")[0], set()).add(identifier)

    pointers = {
        "prohibited_conclusions": "PU",
        "must_not_infer": "PU",
        "broader": "GC",
        "narrower": "GC",
        "related": "GC",
        "related_questions": ("CQ", "GA"),
    }
    for envelope in seed.envelopes:
        for field_name, series in pointers.items():
            values = envelope.record.get(field_name) or []
            if not isinstance(values, list):
                continue
            wanted = (series,) if isinstance(series, str) else series
            for value in values:
                if not isinstance(value, str):
                    continue
                pool: set[str] = set()
                for prefix in wanted:
                    pool |= known.get(prefix, set())
                if value not in pool:
                    yield Finding(
                        Severity.DEFECT, "seed-cross-reference", envelope.seed_id,
                        f"{field_name} points at {value}, which no seed record "
                        "defines. A dangling pointer in an example teaches the "
                        "shape wrong",
                    )


def _refs(seed: SeedSet, corpus: Corpus | None) -> Iterator[Finding]:
    """Every ref-valued field: grammatical, and resolvable where a corpus is open."""
    for envelope in seed.envelopes:
        for path in ref_paths(envelope.record_type):
            for pointer, value in read_path(envelope.record, path):
                if not isinstance(value, str):
                    continue
                try:
                    parsed = parse_ref(value)
                except InvalidRef as error:
                    yield Finding(
                        Severity.DEFECT, "seed-ref", envelope.seed_id,
                        f"{pointer} = {value!r} is not a ref: {error}",
                    )
                    continue
                if parsed.kind is RefKind.CASE:
                    yield Finding(
                        Severity.NOTE, "seed-ref", envelope.seed_id,
                        f"{pointer} = {value} is a case citation, checked for "
                        "grammar only — no decision text exists anywhere in the "
                        "programme (Q-11)",
                    )
                    continue
                if corpus is None:
                    continue
                if passage_at(corpus, value) is None:
                    yield Finding(
                        Severity.DEFECT, "seed-ref", envelope.seed_id,
                        f"{pointer} = {value} resolves to nothing in the pinned "
                        f"snapshot ({corpus.pin.commit[:12]})",
                    )


def check(
    seed: SeedSet, corpus: Corpus | None = None
) -> tuple[Finding, ...]:
    """Everything that can be said about a seed set without reading the law.

    A DEFECT is a seed record that is wrong *as a container* — a span that does
    not land, a dangling pointer, an id collision, an `approved_by` that should
    not be there. None of it is an opinion about the legal content, which is the
    expert's to give and the only reason the set exists.
    """
    findings: list[Finding] = []
    for path, reason in seed.unreadable:
        findings.append(
            Finding(
                Severity.DEFECT, "seed-readable",
                str(path.relative_to(REPO_ROOT)), reason,
            )
        )

    resolutions: tuple[Resolution, ...] = ()
    if corpus is not None:
        resolutions, resolution_findings = resolve(seed, corpus)
        findings.extend(resolution_findings)
    else:
        resolutions = tuple(
            Resolution(envelope=e, record=dict(e.record)) for e in seed.envelopes
        )

    findings.extend(_envelope_shape(seed))
    findings.extend(_never_approved(seed))
    findings.extend(_identifiers(seed))
    findings.extend(_cross_references(seed))
    findings.extend(_refs(seed, corpus))
    findings.extend(_schema(seed, resolutions))
    return tuple(findings)


# ---------------------------------------------------------------------------
# Coverage — what the set demonstrates, and what it does not
# ---------------------------------------------------------------------------


def coverage(seed: SeedSet) -> tuple[Finding, ...]:
    """Report the shape lessons the set does not yet carry an example of.

    Not a quality judgement. It counts the things the input guide names as the
    hard cases — every competency-question category, every prohibited-use kind,
    `not_labels`, non-Manual phrasing, `irrelevant_but_tempting` — because a
    seed set that skips them teaches the easy half of every record type.
    """
    findings: list[Finding] = []

    def _values(record_type: str, field_name: str) -> list[Any]:
        return [e.record.get(field_name) for e in seed[record_type]]

    for record_type, field_name, expected, label in (
        ("competency_question", "category",
         ("retrieval", "search", "reasoning", "currency", "impact", "provenance"),
         "competency-question categories"),
        ("prohibited_use", "kind",
         ("evaluative_conclusion", "authority_conflation", "unsupported_inference",
          "stale_source", "overreach", "ambiguity_collapse"),
         "prohibited-use kinds"),
        ("gold_entity", "type",
         ("LegalConcept", "LegislativeProvision", "JudicialDecision",
          "EvidenceCategory", "ManualInstruction", "Role", "Date", "Other"),
         "gold entity types"),
    ):
        present = {v for v in _values(record_type, field_name) if v is not None}
        for value in expected:
            if value not in present:
                findings.append(
                    Finding(
                        Severity.GAP, "seed-coverage", label,
                        f"no example with {field_name} = {value}",
                    )
                )

    empty = [
        e.seed_id for e in seed["gold_concept"] if not (e.record.get("not_labels") or [])
    ]
    if empty:
        findings.append(
            Finding(
                Severity.NOTE, "seed-coverage", "gold concepts",
                f"{len(empty)} concept(s) carry no not_labels: "
                f"{', '.join(empty[:6])}{'…' if len(empty) > 6 else ''}. The guide "
                "calls this the most valuable field in Stage 0",
            )
        )

    searches = seed["gold_search_question"]
    manual_phrased = [e for e in searches if e.record.get("uses_manual_terminology")]
    if searches and len(manual_phrased) * 2 >= len(searches):
        findings.append(
            Finding(
                Severity.GAP, "seed-coverage", "search questions",
                f"{len(manual_phrased)} of {len(searches)} use the Manual's own "
                "terminology. The guide asks for a majority that do not — a query "
                "in the Manual's words tests string matching, which already works",
            )
        )
    without_tempting = [
        e.seed_id for e in searches if not (e.record.get("irrelevant_but_tempting") or [])
    ]
    if without_tempting:
        findings.append(
            Finding(
                Severity.NOTE, "seed-coverage", "search questions",
                f"{len(without_tempting)} search question(s) name nothing under "
                "irrelevant_but_tempting, so they test recall and not precision",
            )
        )

    unreviewed = [e for e in seed.envelopes if e.verdict == "unreviewed"]
    if unreviewed:
        findings.append(
            Finding(
                Severity.GAP, "seed-review", "verdicts",
                f"{len(unreviewed)} of {seed.total} seed records are still "
                "unreviewed. Until an expert rules on one, it is an illustration "
                "of a shape and nothing more",
            )
        )
    return tuple(findings)

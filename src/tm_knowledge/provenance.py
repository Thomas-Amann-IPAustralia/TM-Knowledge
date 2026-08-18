"""Provenance — the block every record this repo generates must carry.

ADR-0011's field list, made a type. CLAUDE.md rule 8: *no LLM output goes
anywhere unlabelled*, and the cheapest way to keep that true is to make an
unlabelled record impossible to construct. Hence the shape below: a `Candidate`
cannot be built without a complete `Provenance`, and `Provenance` cannot be built
without a source span.

Three things here are load-bearing and easy to get wrong.

**Upstream's signals are carried, never merged.** `extraction` (`href`/`regex`)
and `certainty` (`explicit`/`default`/`ambiguous`) pass through verbatim in
`upstream_signals` and never touch `confidence`. Blending them destroys the only
thing separating an author's assertion from an inference, permanently and
irrecoverably (CLAUDE.md rule 3, Q-07).

**`extraction_methods` is a set, not a scalar.** ADR-0019 runs three keyphrase
extractors over the same text and ADR-0020 gives one span one candidate, so a
term found by all three is *one* record carrying three methods with three
scores — because agreement across methods is the confidence signal the ensemble
exists to produce, and it is only visible if the methods land on one record.

**A model-backed method must name its model and version.** KeyBERT's output
depends on which sentence-transformer is loaded; a silent model upgrade changes
candidate output and invalidates every baseline measured before it (ADR-0019
consequence 2). So a method flagged as model-backed without a model identifier
is a construction error, not a warning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum

from tm_knowledge.refs import RefKind, candidate_id, parse_ref

__all__ = [
    "ExtractionMethod",
    "ReviewStatus",
    "MethodEvidence",
    "SourceSpan",
    "UpstreamSignals",
    "Provenance",
    "Candidate",
]


class ExtractionMethod(str, Enum):
    """How a candidate was found.

    The Stage 2 stack is fixed by ADR-0019: TextRank, YAKE and KeyBERT in
    parallel, plus the rule-based paths of roadmap §2.2. `spacy_ner` is here as a
    *metadata* method — it annotates a candidate and is never the entity
    taxonomy, and it must not be used for provisions, cases or internal refs
    (ADR-0019 consequence 4, Q-16).
    """

    TEXTRANK = "textrank"
    YAKE = "yake"
    KEYBERT = "keybert"
    ENTITY_RULER = "entity_ruler"
    PHRASE_MATCHER = "phrase_matcher"
    REGEX = "regex"
    DEPENDENCY_MATCHER = "dependency_matcher"
    SPACY_NER = "spacy_ner"
    LLM = "llm"
    HUMAN = "human"

    @property
    def is_model_backed(self) -> bool:
        """Does this method's output depend on a loaded model?

        The deterministic methods stay deterministic (CLAUDE.md rule 7); the
        others must pin and record what they ran.
        """
        return self in {
            ExtractionMethod.KEYBERT,
            ExtractionMethod.SPACY_NER,
            ExtractionMethod.LLM,
        }


class ReviewStatus(str, Enum):
    """Where a record sits between machine output and approved knowledge.

    `CANDIDATE` and `APPROVED` never share a file, a directory or a named graph
    (CLAUDE.md rule 4, ADR-0007). `STALE` is what a record becomes when the
    passage it rests on changes underneath it — see `Provenance.is_stale`.
    """

    CANDIDATE = "candidate"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class MethodEvidence:
    """One detector's view of a candidate: what fired, how strongly, on what."""

    method: ExtractionMethod
    score: float | None = None
    model: str | None = None
    model_version: str | None = None

    def __post_init__(self) -> None:
        if self.method.is_model_backed and not self.model:
            raise ValueError(
                f"{self.method.value} is model-backed: name the model and its "
                "version, or a silent upgrade invalidates every baseline "
                "measured before it (ADR-0019 consequence 2)."
            )


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """Exact character offsets into the upstream `text` this record rests on.

    A record without a span is a bug, not a low-confidence result
    (`src/README.md`). The span is what lets the harness assert that the text at
    that offset still equals the recorded surface form — the check that catches
    a corpus that moved under an assertion.
    """

    ref: str
    start: int
    end: int
    content_hash: str

    def __post_init__(self) -> None:
        parsed = parse_ref(self.ref)
        if parsed.kind is RefKind.CASE:
            raise ValueError(
                f"{self.ref} is a case citation, and no decision text exists "
                "anywhere in the programme, so nothing can span into it (Q-11)."
            )
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"nonsensical span [{self.start}, {self.end}] on {self.ref}")
        if not self.content_hash.startswith("sha256:"):
            raise ValueError(
                f"content_hash must be upstream's own value, e.g. "
                f"'sha256:…', got {self.content_hash!r}"
            )

    def text_from(self, text: str) -> str:
        """The passage this span names, out of the chunk or unit `text`."""
        return text[self.start : self.end]


@dataclass(frozen=True, slots=True)
class UpstreamSignals:
    """Upstream's trust metadata, carried verbatim.

    `extraction` is `href` (the Manual's authors linked it themselves) or
    `regex` (upstream read it out of prose). `certainty` is `explicit`,
    `default` or `ambiguous`, and is present on regex edges only. An `ambiguous`
    edge is never auto-resolved — that is the behaviour upstream deliberately
    refused to implement (Q-07).
    """

    extraction: str
    certainty: str | None = None

    def __post_init__(self) -> None:
        if self.extraction not in {"href", "regex"}:
            raise ValueError(f"extraction is upstream's field: {self.extraction!r}")
        if self.certainty is not None and self.certainty not in {
            "explicit",
            "default",
            "ambiguous",
        }:
            raise ValueError(f"certainty is upstream's field: {self.certainty!r}")
        if self.extraction == "href" and self.certainty is not None:
            raise ValueError(
                "upstream records certainty on regex edges only; an href edge "
                "with a certainty was constructed, not read."
            )


@dataclass(frozen=True, slots=True)
class Provenance:
    """The block ADR-0011 requires on every record this repo generates."""

    source_span: SourceSpan
    extraction_methods: tuple[MethodEvidence, ...]
    review_status: ReviewStatus = ReviewStatus.CANDIDATE
    confidence: float | None = None
    #: Upstream's own signals, where this record rests on an upstream edge.
    #: Never merged into `confidence`, ever (CLAUDE.md rule 3).
    upstream_signals: UpstreamSignals | None = None
    reviewer: str | None = None
    review_date: date | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0)
    )

    def __post_init__(self) -> None:
        if not self.extraction_methods:
            raise ValueError(
                "a record with no extraction method is unlabelled machine output "
                "(CLAUDE.md rule 8). Name what produced it."
            )
        seen = [evidence.method for evidence in self.extraction_methods]
        if len(seen) != len(set(seen)):
            raise ValueError(
                f"one method, one entry: {[m.value for m in seen]}. Two runs of "
                "the same extractor over one span are one piece of evidence."
            )
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence outside [0, 1]: {self.confidence}")
        if self.review_status in {ReviewStatus.APPROVED, ReviewStatus.REJECTED} and not (
            self.reviewer and self.review_date
        ):
            raise ValueError(
                f"review_status {self.review_status.value} without a reviewer and "
                "a date is not a recorded human decision (CLAUDE.md rule 4)."
            )

    @property
    def methods(self) -> frozenset[ExtractionMethod]:
        return frozenset(evidence.method for evidence in self.extraction_methods)

    @property
    def agreement(self) -> int:
        """How many methods found this span.

        The cheap confidence signal ADR-0019 exists to produce, available before
        any expert has graded anything — and the reason ADR-0020 keeps one span
        on one record.
        """
        return len(self.methods)

    def is_stale(self, current_content_hash: str) -> bool:
        """Has the passage this record rests on changed underneath it?

        The whole mechanism for Stage 10 incremental reprocessing
        (`IDENTIFIERS.md` §5). A stale record returns to review; it is never
        silently carried forward.
        """
        return current_content_hash != self.source_span.content_hash


@dataclass(frozen=True, slots=True)
class Candidate:
    """A machine-generated candidate: a value at a span, plus why anyone thinks so.

    Constructing one without provenance is impossible by design. The id is
    content-addressed and carries no method (ADR-0020), so a re-run over
    unchanged input is a no-op and adding a fourth extractor mutates this record
    rather than minting a new one.
    """

    value: str
    provenance: Provenance
    #: What kind of thing is being proposed — `term`, `relation`, `concept`.
    #: Deliberately a free string: the *taxonomy* is expert-owned and does not
    #: get fixed by an agent in a type (CLAUDE.md rule 1).
    kind: str = "term"
    #: spaCy NER labels observed over this span, under their own key and their
    #: own vocabulary. Never written into an entity type (Q-16, ADR-0019 c.4).
    ner_labels: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("a candidate with no value is not a candidate")
        if not isinstance(self.provenance, Provenance):
            raise TypeError(
                "every candidate carries a Provenance — method, model, "
                "confidence, span, hash, review status (CLAUDE.md rule 8)."
            )

    @property
    def id(self) -> str:
        span = self.provenance.source_span
        return candidate_id(span.ref, span.start, span.end, self.value)

    def with_method(self, evidence: MethodEvidence) -> "Candidate":
        """Add a detector's evidence, keeping the id.

        This is what "adding an extractor mutates existing records" looks like
        in code (ADR-0020). The id does not move, because the thing identified —
        the term at that span — has not changed.
        """
        if evidence.method in self.provenance.methods:
            raise ValueError(f"{evidence.method.value} is already recorded on {self.id}")
        provenance = Provenance(
            source_span=self.provenance.source_span,
            extraction_methods=self.provenance.extraction_methods + (evidence,),
            review_status=self.provenance.review_status,
            confidence=self.provenance.confidence,
            upstream_signals=self.provenance.upstream_signals,
            reviewer=self.provenance.reviewer,
            review_date=self.provenance.review_date,
            created_at=self.provenance.created_at,
        )
        return Candidate(
            value=self.value,
            provenance=provenance,
            kind=self.kind,
            ner_labels=self.ner_labels,
        )

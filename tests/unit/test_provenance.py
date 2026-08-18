"""Provenance — a record cannot be constructed unlabelled.

P12's done-criterion. Every test here is one of CLAUDE.md's hard rules made
mechanical, so a future session breaking one gets a failure rather than a
silently worse corpus.
"""

from __future__ import annotations

from datetime import date

import pytest

from tm_knowledge.provenance import (
    Candidate,
    ExtractionMethod,
    MethodEvidence,
    Provenance,
    ReviewStatus,
    SourceSpan,
    UpstreamSignals,
)

HASH = "sha256:" + "a" * 64
SPAN = SourceSpan(ref="TMM/Part22/1/1/2", start=10, end=34, content_hash=HASH)
YAKE = MethodEvidence(method=ExtractionMethod.YAKE, score=0.031)
TEXTRANK = MethodEvidence(method=ExtractionMethod.TEXTRANK, score=0.88)
KEYBERT = MethodEvidence(
    method=ExtractionMethod.KEYBERT,
    score=0.62,
    model="sentence-transformers/all-MiniLM-L6-v2",
    model_version="2.2.2",
)


def _provenance(**overrides) -> Provenance:
    fields = {"source_span": SPAN, "extraction_methods": (YAKE,)}
    fields.update(overrides)
    return Provenance(**fields)


# ---------------------------------------------------------------------------
# A candidate cannot be constructed without provenance
# ---------------------------------------------------------------------------

def test_a_candidate_needs_a_complete_provenance_block():
    with pytest.raises(TypeError):
        Candidate(value="acquired distinctiveness")  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        Candidate(value="acquired distinctiveness", provenance=None)  # type: ignore[arg-type]


def test_provenance_needs_a_span_and_a_method():
    with pytest.raises(TypeError):
        Provenance(extraction_methods=(YAKE,))  # type: ignore[call-arg]
    with pytest.raises(ValueError, match="unlabelled machine output"):
        Provenance(source_span=SPAN, extraction_methods=())


def test_a_span_needs_the_upstream_content_hash():
    with pytest.raises(ValueError, match="content_hash"):
        SourceSpan(ref="TMM/Part22/1/1/2", start=0, end=1, content_hash="deadbeef")


def test_a_span_must_land_on_a_ref_that_holds_text():
    with pytest.raises(ValueError, match="no decision text"):
        SourceSpan(ref="CASE/2018/FCAFC/109", start=0, end=1, content_hash=HASH)


def test_a_span_validates_its_ref():
    from tm_knowledge.refs import InvalidRef

    with pytest.raises(InvalidRef):
        SourceSpan(ref="TMR1995/s224", start=0, end=1, content_hash=HASH)


# ---------------------------------------------------------------------------
# The ensemble: one span, one candidate, N pieces of evidence (ADR-0019/0020)
# ---------------------------------------------------------------------------

def test_three_extractors_produce_one_record_with_three_methods():
    provenance = _provenance(extraction_methods=(YAKE, TEXTRANK, KEYBERT))
    candidate = Candidate(value="acquired distinctiveness", provenance=provenance)
    assert provenance.agreement == 3
    assert provenance.methods == {
        ExtractionMethod.YAKE,
        ExtractionMethod.TEXTRANK,
        ExtractionMethod.KEYBERT,
    }
    # ...and each keeps its own score.
    assert {e.method: e.score for e in provenance.extraction_methods}[
        ExtractionMethod.TEXTRANK
    ] == 0.88
    # The id does not depend on any of it.
    single = Candidate(value="acquired distinctiveness", provenance=_provenance())
    assert candidate.id == single.id


def test_adding_an_extractor_mutates_the_record_rather_than_minting_a_new_id():
    candidate = Candidate(value="acquired distinctiveness", provenance=_provenance())
    extended = candidate.with_method(TEXTRANK)
    assert extended.id == candidate.id
    assert extended.provenance.agreement == 2
    with pytest.raises(ValueError, match="already recorded"):
        extended.with_method(TEXTRANK)


def test_one_method_one_entry():
    with pytest.raises(ValueError, match="one method, one entry"):
        _provenance(extraction_methods=(YAKE, MethodEvidence(ExtractionMethod.YAKE, 0.2)))


def test_a_model_backed_method_must_name_its_model():
    with pytest.raises(ValueError, match="model-backed"):
        MethodEvidence(method=ExtractionMethod.KEYBERT, score=0.5)
    with pytest.raises(ValueError, match="model-backed"):
        MethodEvidence(method=ExtractionMethod.LLM)
    # The deterministic methods do not need one, and are not asked for one.
    assert MethodEvidence(ExtractionMethod.YAKE).model is None
    assert ExtractionMethod.TEXTRANK.is_model_backed is False


# ---------------------------------------------------------------------------
# Upstream signals are carried, never merged
# ---------------------------------------------------------------------------

def test_upstream_signals_are_carried_verbatim_and_kept_off_confidence():
    signals = UpstreamSignals(extraction="regex", certainty="ambiguous")
    provenance = _provenance(upstream_signals=signals, confidence=0.9)
    assert provenance.upstream_signals.certainty == "ambiguous"
    assert provenance.confidence == 0.9
    # There is nowhere for the two to be blended: they are separate fields with
    # separate types, and no code path collapses one into the other.
    assert provenance.upstream_signals is signals


def test_upstream_signal_values_are_upstreams_and_not_ours():
    with pytest.raises(ValueError):
        UpstreamSignals(extraction="inferred")
    with pytest.raises(ValueError):
        UpstreamSignals(extraction="regex", certainty="probable")


def test_an_href_edge_carries_no_certainty():
    """Upstream records certainty on regex edges only (Q-07)."""
    assert UpstreamSignals(extraction="href").certainty is None
    with pytest.raises(ValueError, match="regex edges only"):
        UpstreamSignals(extraction="href", certainty="explicit")


# ---------------------------------------------------------------------------
# Review status and staleness
# ---------------------------------------------------------------------------

def test_approval_requires_a_recorded_human_decision():
    with pytest.raises(ValueError, match="recorded human decision"):
        _provenance(review_status=ReviewStatus.APPROVED)
    approved = _provenance(
        review_status=ReviewStatus.APPROVED,
        reviewer="an examiner",
        review_date=date(2026, 8, 18),
    )
    assert approved.review_status is ReviewStatus.APPROVED


def test_a_record_defaults_to_candidate():
    assert _provenance().review_status is ReviewStatus.CANDIDATE


def test_staleness_is_detected_from_the_stored_hash():
    provenance = _provenance()
    assert provenance.is_stale(HASH) is False
    assert provenance.is_stale("sha256:" + "b" * 64) is True


def test_confidence_stays_a_probability():
    with pytest.raises(ValueError, match="confidence"):
        _provenance(confidence=1.4)


# ---------------------------------------------------------------------------
# NER metadata stays metadata (Q-16)
# ---------------------------------------------------------------------------

def test_ner_labels_live_under_their_own_key():
    candidate = Candidate(
        value="Trade Marks Act 1995",
        provenance=_provenance(
            extraction_methods=(
                MethodEvidence(ExtractionMethod.SPACY_NER, model="en_core_web_trf"),
            )
        ),
        ner_labels=("LAW",),
    )
    # OntoNotes `LAW` is not the gold `LegislativeProvision`, and nothing here
    # lets it become one: there is no entity-type field to write it into.
    assert candidate.ner_labels == ("LAW",)
    assert not hasattr(candidate, "type")
    assert candidate.kind == "term"


def test_records_are_frozen():
    candidate = Candidate(value="x", provenance=_provenance())
    with pytest.raises(Exception):
        candidate.value = "y"  # type: ignore[misc]

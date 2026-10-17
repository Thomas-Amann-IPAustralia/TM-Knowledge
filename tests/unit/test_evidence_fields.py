"""Evidence is quoted, not retyped: a ref, a span, the content hash and the quote.

That is the rule (ADR-0045, ADR-0090 c3), and until S036 nothing enforced the last
three. The envelope schema required only `ref`, and the harness skipped a missing
hash, stopped at a missing span and never asked for a quote, so a copy of a real
envelope cut down to a bare ref passed both (the review response, F08). The data was
complete; the gate was not.

A case citation is the one exception: no judgment text is held anywhere in the
programme (Q-11), so a `CASE/...` ref has nothing to quote and is checked for grammar.
"""

from __future__ import annotations

import copy

import pytest

from tm_knowledge.authored import store as authored_store


@pytest.fixture(scope="module")
def envelope():
    """A real authored envelope with evidence, as the store holds it."""
    for entry in authored_store.load().entries:
        items = (entry.envelope or {}).get("evidence") or []
        if items and all(item.get("ref", "").startswith("TMM/") for item in items):
            return entry.record_id, copy.deepcopy(entry.envelope)
    pytest.fail("no authored record cites a Manual chunk")


def _cut(envelope, keep):
    out = copy.deepcopy(envelope)
    out["evidence"] = [{key: item[key] for key in keep if key in item} for item in out["evidence"]]
    return out


@pytest.mark.parametrize(
    "keep",
    [("ref",), ("ref", "span", "content_hash"), ("ref", "span", "quote"), ("ref", "content_hash", "quote")],
    ids=["bare-ref", "no-quote", "no-hash", "no-span"],
)
def test_the_schema_refuses_evidence_missing_a_field(envelope, keep):
    record_id, whole = envelope
    assert not authored_store.validate_envelope(whole, record_id=record_id), "the uncut envelope must pass"
    errors = authored_store.validate_envelope(_cut(whole, keep), record_id=record_id)
    assert errors, f"evidence carrying only {keep} passed the envelope schema"


def test_the_schema_accepts_a_case_citation_by_ref_alone(envelope):
    record_id, whole = envelope
    case = copy.deepcopy(whole)
    case["evidence"] = [*case["evidence"], {"ref": "CASE/2010/FCA/1"}]
    assert not authored_store.validate_envelope(case, record_id=record_id)


@pytest.mark.snapshot
@pytest.mark.parametrize(
    "keep",
    [("ref",), ("ref", "span", "content_hash"), ("ref", "span", "quote"), ("ref", "content_hash", "quote")],
    ids=["bare-ref", "no-quote", "no-hash", "no-span"],
)
def test_the_harness_refuses_evidence_missing_a_field(envelope, keep):
    from tm_knowledge.stage0 import harness
    from tm_knowledge.upstream.loader import load_corpus

    record_id, whole = envelope
    corpus = load_corpus()
    assert not [f for f in harness._evidence_findings(record_id, whole["evidence"], corpus)
                if f.severity is harness.Severity.DEFECT], "the uncut evidence must pass"
    cut = _cut(whole, keep)["evidence"]
    defects = [f for f in harness._evidence_findings(record_id, cut, corpus)
               if f.severity is harness.Severity.DEFECT]
    assert defects, f"evidence carrying only {keep} passed the harness"

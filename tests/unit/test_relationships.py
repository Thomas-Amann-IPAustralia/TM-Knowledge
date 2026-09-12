"""The corpus-wide relationship pass — what it joins, and what it refuses to join.

`tmk-relationships` is the pass that took the ontology's relational layer off
section 43. Unlike `tmk-concepts` it **authors**: a relationship has no useful
candidate form, so the pass commits to a predicate and writes a record with an
envelope. That makes the honesty guards the thing to test, not the recall.

Three groups of tests, and the middle group is the one that matters most.

**That it stays deterministic and evidenced.** Same pin, same bytes; every
quote lands at its span; every record names the passage it rests on.

**That it never launders.** `approved_by` null on every record, `review_status`
`unreviewed` on every record, `authored_by` naming the model that actually
wrote it, and `general_knowledge` — the basis that means *the corpus does not
say this* — appearing nowhere, because a deterministic pass that cannot point
at a span has no business writing a record at all.

**That it keeps refusing.** It reads only `must` as a modality; it takes the
signed concept when a label belongs to two and says so; it emits every
definition of a term rather than choosing one; and it declines the active
`overcome` and the passive `is notified`, both of which invert an edge.
"""

from __future__ import annotations

import pytest

from tm_knowledge.config import UPSTREAM_DIR
from tm_knowledge.stage0 import relationships as relationships_module
from tm_knowledge.upstream.loader import load_corpus


# ---------------------------------------------------------------------------
# Without a corpus
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "clause,expected",
    [
        ("the application must be rejected", "must"),
        ("a ground for rejection may be raised", None),
        ("the examiner should consult a team leader", None),
        ("the Registrar will notify the applicant", None),
        ("this is mandatory", None),
    ],
)
def test_only_must_is_read_as_a_modality(clause, expected):
    """`may` is the word the record schema singles out as ambiguous — possibility
    or permission is a legal reading — and `should` in the Manual is practice
    direction whose force is what CQ-0024 exists to ask about.

    `mandatory` returning None is the interesting row. `GR-0001` is a signed
    record whose reviewer read exactly that word as obligation and whose own
    note says the sentence "contains no modal verb at all, so nothing in the
    grammar supports the reading". A person may make that reading; a regex may
    not.
    """
    assert relationships_module._modality(clause) == expected


@pytest.mark.parametrize(
    "sentence,fires",
    [
        ("the ground may be overcome by a letter of consent", True),
        ("an applicant may attempt to overcome the ground by deleting goods", False),
        ("the objection can be overcome by evidence of use", True),
    ],
)
def test_only_the_passive_overcome_fires(sentence, fires):
    """The active form puts the *actor* where the passive puts the thing that
    overcomes, so a pattern accepting both inverts the edge on every active
    sentence. Measured before this guard: two inversions in a sample of four."""
    assert bool(relationships_module._OVERCOME_BY.search(sentence)) is fires


@pytest.mark.parametrize(
    "following,passive",
    [
        (" will be notified of any deficiencies", True),
        (" must be given a copy of the statement", True),
        (" may revoke acceptance of that application", False),
        (" must ensure that the goods are excluded", False),
    ],
)
def test_the_passive_is_declined_rather_than_read_backwards(following, passive):
    """`the applicant will be notified` names the office the act is done *to*.
    The pattern cannot parse, so it declines rather than guessing — this is the
    alternative each `isPerformedBy` record names in `alternatives_considered`,
    caught rather than shipped."""
    assert bool(relationships_module._PASSIVE.search(following)) is passive


def test_a_flattened_table_is_not_a_sentence():
    """Chunks in this corpus carry flattened lists and tables — an annex of
    deferment grounds arrives as one 900-character run. Reading a subject and an
    object out of one takes them from different list items, which is where every
    bad edge in the first sample came from."""
    run = "x" * (relationships_module.MAX_WINDOW + 50) + ". Short one here."
    windows = [text for text, _, _ in relationships_module._sentences(run)]
    assert "Short one here." in windows
    assert all(len(text) <= relationships_module.MAX_WINDOW for text in windows)


def test_sentence_offsets_locate_in_the_source():
    """Offsets are found by scanning forward, not by summing lengths: the split
    discards the whitespace between sentences and reconstructing it by
    arithmetic is how a span drifts by one character and stops locating."""
    text = "First sentence here. Second one follows; third after a semicolon."
    for sentence, start, end in relationships_module._sentences(text):
        assert text[start:end] == sentence


# ---------------------------------------------------------------------------
# Against the pinned corpus
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def corpus():
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")
    return load_corpus()


@pytest.fixture(scope="module")
def lexicon():
    return relationships_module.build_lexicon()


@pytest.fixture(scope="module")
def findings(corpus, lexicon):
    return relationships_module.extract(corpus, lexicon)


@pytest.mark.snapshot
def test_the_pass_is_deterministic(corpus, lexicon, findings):
    """Same pin, same pattern set, same bytes. Without this the records churn on
    every run and a diff stops meaning anything."""
    again = relationships_module.extract(corpus, lexicon)
    assert [f.key for f in again] == [f.key for f in findings]


@pytest.mark.snapshot
def test_every_quote_lands_at_its_span(corpus, findings):
    """A quote that will not locate means the passage was retyped, and a retyped
    passage is not evidence (ADR-0045). The harness checks this over the written
    store; this checks it at the point the quote is cut, which is where a
    regression would actually be introduced."""
    for finding in findings:
        held = (
            corpus.chunks.get(finding.source_ref)
            or corpus.units.get(finding.source_ref)
            or corpus.provisions.get(finding.source_ref)
        )
        assert held is not None, f"{finding.source_ref} is not in the snapshot"
        start, end = finding.span
        assert held.text[start:end] == finding.supporting_text
        assert held.content_hash == finding.source_content_hash


@pytest.mark.snapshot
def test_nothing_is_authored_without_evidence(findings):
    """`general_knowledge` is the honest label for a judgement the corpus does
    not support, and it is permitted (ADR-0079 guard 2). A *deterministic* pass
    has no use for it: every edge here was found by matching text, so an edge
    that could not point at a span would be a bug rather than an abstention."""
    assert {f.basis for f in findings} <= {"corpus_explicit", "corpus_inferred"}


@pytest.mark.snapshot
def test_records_carry_the_envelope_and_never_a_signature(findings, lexicon):
    """The one failure the whole scheme exists to prevent. `approved_by` means a
    person read this record and signed it; an agent writing into it — with a
    name, a model id or anything else — is laundering (CLAUDE.md rule 1,
    ADR-0079 guard 3)."""
    records = relationships_module.render_records(
        findings, lexicon=lexicon, start_id=9000, authored_date="2026-01-01"
    )
    for record in records:
        assert record["approved_by"] is None
        assert record["approved_date"] is None
        envelope = record["authored"]
        assert envelope["review_status"] == "unreviewed"
        assert envelope["authored_by"] == relationships_module.AUTHORED_BY
        assert envelope["reasoning"]
        assert envelope["expert_should_check"]
        assert envelope["evidence"] and envelope["evidence"][0]["ref"]


@pytest.mark.snapshot
def test_a_label_two_concepts_carry_resolves_to_the_signed_one(lexicon):
    """Ten authored concepts reuse a signed concept's preferred label (ADR-0101)
    and the pass has to pick one to build an edge from. It takes the signed
    record — ADR-0080 consequence 2 runs that way — and discloses the collision
    rather than retiring either side."""
    assert lexicon.collisions, "the duplicate-label pairs ADR-0101 found are gone"
    for label, ids in lexicon.collisions.items():
        chosen = lexicon.by_label[label]
        if any(i in lexicon.signed for i in ids):
            assert chosen in lexicon.signed, f"{label!r} resolved to an authored record"
    note = lexicon.collision_note("GC-0006")
    assert note and "GC-0053" in note


@pytest.mark.snapshot
def test_a_term_defined_six_times_gets_six_records(findings):
    """*notice of opposition* is defined in six places across the Regulations.
    Upstream refused to choose between them and so does this: collapsing them to
    a primary definition would resolve somebody else's ambiguity silently
    (CLAUDE.md rule 6, Q-07), and the multiplicity is itself the finding."""
    defined_in = [f for f in findings if f.predicate == "isDefinedIn"]
    per_concept: dict[str, int] = {}
    for finding in defined_in:
        per_concept[finding.subject] = per_concept.get(finding.subject, 0) + 1
    assert max(per_concept.values()) > 1


@pytest.mark.snapshot
def test_the_pass_reaches_past_part_29(findings):
    """The whole point. All 37 source refs in the signed relationship set point
    at `TMM/Part29`; if this pass came back concentrated there too, the
    relational layer would still be a section 43 layer with more rows in it
    (ADR-0109)."""
    sources = {relationships_module._part_of(f.source_ref) for f in findings}
    assert len(sources) > 20
    assert {"TMA1995", "TMR1995"} <= sources, "the legislation contributed no edges"
    part29 = sum(1 for f in findings if relationships_module._part_of(f.source_ref) == "Part29")
    assert part29 < len(findings) / 4


@pytest.mark.snapshot
def test_an_office_is_never_what_gives_rise_to_a_ground(findings, lexicon):
    """An office raises a ground; it is not what the ground arises from. Letting
    a `process_role` concept through produced `applicant mayGiveRiseTo ground
    for rejection` on the first run, which reads plausibly and says nothing."""
    for finding in findings:
        if finding.predicate in {"mayGiveRiseTo", "doesNotGiveRiseTo", "requiresElement"}:
            assert lexicon.groups.get(finding.subject) != "process_role"

"""The corpus-wide candidate pass — what it finds, and what it refuses to decide.

`tmk-concepts` is the pass the section 43 boundary used to make unnecessary. Its
whole value is that it is a lookup: run it twice on one pin and it produces the
same bytes, and every field in it can be checked against the snapshot. So these
tests pin two things down.

**That it stays deterministic and evidenced.** A quote that does not land is the
failure `authored/README.md` calls the worst thing that can be written — a lie a
machine will later certify — and the pass is where the quotes come from.

**That it keeps refusing.** It never chooses between six statutory definitions
of *party*; it never merges the Act's words with the Manual's; it never types
anything; and it marks a term an existing concept claims rather than dropping
it. Each of those is a rule a later "tidy-up" would quietly break.
"""

from __future__ import annotations

import pytest

from tm_knowledge.config import UPSTREAM_DIR
from tm_knowledge.stage0 import concepts as concepts_module
from tm_knowledge.upstream.loader import load_corpus


# ---------------------------------------------------------------------------
# Without a corpus
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "heading,kept",
    [
        ("3. Inherent adaptation to distinguish", True),
        ("2. Honest concurrent use - paragraph 44(3)(a)", True),
        ("1. Introduction", False),
        ("Relevant Legislation", False),
        ("Part 22.7. Examination", False),
        ("section 41", False),
        ("Trade Marks Act 1995", False),
        ("subsection 44(3)", False),
    ],
)
def test_structural_and_citation_headings_are_not_subjects(heading, kept):
    """A heading that says where you are, or names an instrument, is not a
    concept. `section 43` in particular would be a second and worse name for
    `TMA1995/s43` (IDENTIFIERS.md §4)."""
    cleaned = concepts_module._HEADING_NUMBER.sub("", heading).strip(" .-–—:")
    rejected = bool(
        concepts_module._STRUCTURAL_HEADING.match(cleaned)
        or concepts_module._CITATION_ONLY.match(cleaned)
    )
    assert rejected is (not kept)


def test_stripping_the_numbering_does_not_eat_a_leading_letter():
    """The bug this regex was written against: a looser pattern turns
    *Introduction* into *ntroduction* and *Annex A1* into *nnex A1*, which is a
    silent corruption rather than a visible failure."""
    for heading in ("Introduction", "Annex A1 - Divisional Checklist", "Evidence"):
        assert concepts_module._HEADING_NUMBER.sub("", heading) == heading


def test_an_existing_concept_claims_its_labels_but_never_its_near_misses():
    """`not_labels` are forms the concept explicitly does *not* mean, so a
    candidate matching one is not covered — it may be the concept the near-miss
    was pointing at."""
    claimed = concepts_module._existing_labels(
        [
            {
                "id": "GC-0001",
                "pref_label": "connotation",
                "alt_labels": ["secondary meaning"],
                "not_labels": ["deceptively similar"],
            }
        ]
    )
    assert claimed["connotation"] == "GC-0001"
    assert claimed["secondary meaning"] == "GC-0001"
    assert "deceptively similar" not in claimed


def test_strength_says_how_much_a_lookup_established_and_nothing_else():
    evidence = concepts_module.Evidence("TMA1995/s6/x", (0, 1), "sha256:" + "0" * 64, "x")
    both = concepts_module.Candidate("x", "statutory_definition", statutory=(evidence,), manual=(evidence,))
    one = concepts_module.Candidate("x", "statutory_definition", statutory=(evidence,))
    neither = concepts_module.Candidate("x", "manual_topic", topics=(evidence,))
    assert (both.strength, one.strength, neither.strength) == (3, 2, 1)


# ---------------------------------------------------------------------------
# Against the pinned corpus
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def corpus():
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")
    return load_corpus()


@pytest.fixture(scope="module")
def candidates(corpus):
    return concepts_module.extract(corpus)


@pytest.mark.snapshot
def test_the_pass_is_deterministic(corpus, candidates):
    """Same pin, same bytes. Without this the candidate file churns on every run
    and its diff stops meaning anything."""
    again = concepts_module.extract(corpus)
    assert [c.as_dict() for c in again] == [c.as_dict() for c in candidates]


@pytest.mark.snapshot
def test_every_quote_lands_exactly_where_the_candidate_says_it_does(corpus, candidates):
    """The check the whole pass rests on. A quote is `text[start:end]` and
    nothing else — one that will not land means the surface was retyped, and a
    retyped passage is not evidence (ADR-0045)."""
    for candidate in candidates:
        for item in (*candidate.statutory, *candidate.manual, *candidate.topics):
            passage = corpus.chunks.get(item.ref) or corpus.resolve_provision(item.ref)
            assert passage is not None, f"{candidate.term}: {item.ref} resolves to nothing"
            start, end = item.span
            assert passage.text[start:end] == item.quote
            assert passage.content_hash == item.content_hash


@pytest.mark.snapshot
def test_it_reaches_past_section_43(corpus, candidates):
    """The point of the pass. Every concept this repository held before it came
    from one neighbourhood; ADR-0081 put all 54 Parts in scope."""
    parts = {part for candidate in candidates for part in candidate.parts}
    assert len(parts) > 40
    assert "Part29" in parts  # the old pilot area is in scope, not excluded
    terms = {candidate.term.lower() for candidate in candidates}
    assert "inherent adaptation to distinguish" in terms
    assert "deceptively similar" in terms


@pytest.mark.snapshot
def test_a_term_defined_several_times_keeps_every_definition(corpus, candidates):
    """`party` is defined six times across the Regulations. Upstream refuses to
    choose between instruments on purpose and this pass inherits the refusal —
    resolving it here would be resolving somebody else's ambiguity silently
    (CLAUDE.md rule 6, Q-07)."""
    multiply_defined = [c for c in candidates if len(c.statutory) > 1]
    assert multiply_defined, "expected at least one term the corpus defines twice"
    for candidate in multiply_defined:
        assert len({item.ref for item in candidate.statutory}) == len(candidate.statutory)


@pytest.mark.snapshot
def test_no_candidate_carries_a_judgement(candidates):
    """A candidate has no id, no label decision and no type. Every one of those
    is authorship and takes an envelope (ADR-0083 consequence 3)."""
    for candidate in candidates:
        record = candidate.as_dict()
        assert "id" not in record
        assert "type" not in record
        assert "pref_label" not in record
        assert "authored" not in record
        assert "approved_by" not in record


@pytest.mark.snapshot
def test_the_pack_says_what_it_is_not(corpus, candidates):
    report = concepts_module.render(candidates, corpus, generated="2026-09-09")
    assert "Nothing here is a concept and nothing here is authored" in report
    assert "never** `corpus_explicit`" in report
    assert corpus.pin.commit[:12] in report

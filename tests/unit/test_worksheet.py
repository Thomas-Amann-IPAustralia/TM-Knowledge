"""The worksheet and the reconnaissance report — P9 and P6.

Their done-criteria: regenerate deterministically, every printed ref resolves,
every printed hash matches the pinned snapshot, the header states the rule and
that it is provisional — and the report never reads as a scope proposal.
"""

from __future__ import annotations

import re

import pytest

from tm_knowledge.config import UPSTREAM_DIR
from tm_knowledge.stage0 import recon as recon_module
from tm_knowledge.stage0 import worksheet as worksheet_module
from tm_knowledge.stage0.worksheet import ScopeRule
from tm_knowledge.upstream.loader import load_corpus


# ---------------------------------------------------------------------------
# The scope rule, without a corpus
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "edge_id,expected",
    [
        ("TMA1995/s43", True),
        ("TMA1995/s43(1)", True),
        ("TMA1995/s43(1)(a)", True),
        ("TMA1995/s43~1", True),
        ("TMA1995/s430", False),
        ("TMA1995/s4", False),
        ("TMA1995/s44", False),
        ("TMR1995/r4.3", False),
    ],
)
def test_the_rule_matches_on_the_grammar_not_by_substring(edge_id, expected):
    """ADR-0022 says this explicitly: `TMA1995/s430` must not match if the corpus
    ever grows one."""
    assert ScopeRule().matches(edge_id) is expected


def test_the_rule_validates_its_provision():
    from tm_knowledge.refs import InvalidRef

    with pytest.raises(InvalidRef):
        ScopeRule(provision="TMR1995/s224")


def test_the_rule_describes_itself_including_the_page_mates():
    described = ScopeRule().describe()
    assert "TMA1995/s43" in described
    assert "page_ref" in described
    assert "not by substring" in described
    assert "page_ref" not in ScopeRule(include_page_mates=False).describe()


# ---------------------------------------------------------------------------
# Against the pinned corpus
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def corpus():
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")
    return load_corpus()


@pytest.fixture(scope="module")
def worksheet(corpus):
    return worksheet_module.render(corpus, generated="2026-08-18")


@pytest.mark.snapshot
def test_the_worksheet_regenerates_deterministically(corpus, worksheet):
    """Byte-identical from the same pin and the same rule. Without this the
    delta ADR-0022 promises to report when the boundary lands is not computable."""
    assert worksheet_module.render(corpus, generated="2026-08-18") == worksheet


@pytest.mark.snapshot
def test_every_printed_ref_resolves_and_every_hash_matches(corpus, worksheet):
    printed_chunks = re.findall(r"^### `([^`]+)`", worksheet, re.MULTILINE)
    assert len(printed_chunks) == 216
    for chunk_ref in printed_chunks:
        assert chunk_ref in corpus.chunks

    for chunk_ref, digest in re.findall(
        r"^### `([^`]+)`.*?\| content_hash \| `([^`]+)` \|",
        worksheet,
        re.MULTILINE | re.DOTALL,
    ):
        assert corpus.chunks[chunk_ref].content_hash == digest


@pytest.mark.snapshot
def test_the_header_states_the_rule_the_pin_and_that_it_is_provisional(worksheet, corpus):
    head = worksheet[:3000]
    assert "Provisional" in head
    assert "not the pilot scope" in head
    assert corpus.pin.commit in head
    assert corpus.pin.manual_extractor_version in head
    assert "matched on the ref grammar and not by substring" in head
    assert "parked, not deleted" in head


@pytest.mark.snapshot
def test_the_worksheet_prints_the_whole_text_of_every_selected_chunk(corpus, worksheet):
    for chunk in worksheet_module.select(corpus):
        # Printed as a blockquote, so newlines gain a marker; the words are whole.
        assert chunk.text.split("\n")[0][:120] in worksheet


@pytest.mark.snapshot
def test_ambiguous_edges_are_printed_rather_than_dropped(corpus, worksheet):
    """Q-07: an ambiguous edge is a reason to print a chunk, never to drop one."""
    ambiguous = [
        chunk
        for chunk in worksheet_module.select(corpus)
        for edge in chunk.provisions
        if edge.needs_a_human and ScopeRule().matches(edge.id)
    ]
    assert ambiguous
    for chunk in ambiguous:
        assert chunk.chunk_ref in worksheet
        assert "ambiguous" in worksheet


@pytest.mark.snapshot
def test_page_mates_are_carried_in_and_marked_apart_from_citing_chunks(corpus, worksheet):
    citing = corpus.chunks_citing("TMA1995/s43")
    selected = worksheet_module.select(corpus)
    assert len(citing) == 67
    assert len(selected) == 216
    # Citing chunks are starred so the annotator can see why a row is here.
    assert worksheet.count("★") == 67


@pytest.mark.snapshot
def test_narrowing_the_rule_selects_strictly_less(corpus):
    wide = worksheet_module.select(corpus, ScopeRule())
    narrow = worksheet_module.select(corpus, ScopeRule(include_page_mates=False))
    assert len(narrow) == 67
    assert {chunk.chunk_ref for chunk in narrow} < {chunk.chunk_ref for chunk in wide}


# ---------------------------------------------------------------------------
# The reconnaissance report
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def recon(corpus):
    return recon_module.reconnoitre(corpus)


@pytest.mark.snapshot
def test_the_recon_numbers_are_the_corpuss_own(corpus, recon):
    assert len(recon.citing_chunks) == 67
    assert len(recon.pages) == 36
    assert len(recon.with_page_mates) == 216
    assert sum(recon.by_part.values()) == 67
    assert sum(recon.by_kind.values()) == 67
    assert sum(recon.by_extraction.values()) == sum(recon.by_certainty.values())
    for chunk_ref, _ in recon.ambiguous_in_scope:
        assert chunk_ref in corpus.chunks


@pytest.mark.snapshot
def test_the_report_says_on_its_face_that_it_is_not_a_scope_proposal(corpus, recon):
    report = recon_module.render(recon, corpus, generated="2026-08-18")
    assert "not a scope proposal" in report.lower()
    assert "expert judgements and this file cannot make them" in report
    assert report == recon_module.render(recon, corpus, generated="2026-08-18")


@pytest.mark.snapshot
def test_the_report_costs_each_candidate_rule(corpus, recon):
    """The volume implication — the number that turns 'which Parts are in scope'
    into a costed question rather than an abstract one."""
    report = recon_module.render(recon, corpus, generated="2026-08-18")
    assert "| 67 |" in report and "| 216 |" in report
    assert "8.8%" in report
    # Words are reported; annotation hours are not invented.
    assert "hour" not in report.lower()


@pytest.mark.snapshot
def test_the_report_surfaces_the_traps_before_gold_records_rest_on_them(corpus, recon):
    report = recon_module.render(recon, corpus, generated="2026-08-18")
    assert "Q-06" in report  # superseded numbering
    assert "Q-07" in report  # ambiguous edges
    assert "Q-11" in report  # citation level only
    assert recon.unresolved_in_scope
    assert recon.cases_cited

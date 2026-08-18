"""The loader — round-trip fidelity, the join, and the trust metadata.

P2's done-criteria: the whole pinned corpus loads, a round-trip shows no field
loss, the join reproduces upstream's coverage figure, and `certainty: ambiguous`
edges are still ambiguous at the far end.

Most of this needs the snapshot. The parts that do not — schema drift, the
edge types — run on hand-built records.
"""

from __future__ import annotations

import json

import pytest

from tm_knowledge.config import UPSTREAM_DIR
from tm_knowledge.upstream.loader import load_corpus
from tm_knowledge.upstream.records import (
    Chunk,
    InternalRef,
    ProvisionEdge,
    UpstreamSchemaDrift,
)


# ---------------------------------------------------------------------------
# No snapshot needed
# ---------------------------------------------------------------------------

def test_an_unknown_upstream_field_stops_the_load():
    """Schema drift is an event to notice, not a field to drop."""
    with pytest.raises(UpstreamSchemaDrift, match="difficulty_rating"):
        ProvisionEdge.from_dict(
            {"id": "TMA1995/s43", "extraction": "regex", "difficulty_rating": 3}
        )


def test_edges_keep_upstreams_words():
    edge = ProvisionEdge.from_dict(
        {"id": "TMA1995/s43", "extraction": "regex", "certainty": "ambiguous",
         "mention": "section 43"}
    )
    assert edge.certainty == "ambiguous"
    assert edge.needs_a_human is True
    assert edge.is_authors_own_link is False
    assert edge.to_dict()["certainty"] == "ambiguous"


def test_an_href_edge_keeps_its_absent_certainty():
    edge = ProvisionEdge.from_dict({"id": "TMA1995/s43", "extraction": "href"})
    assert edge.certainty is None
    assert edge.is_authors_own_link is True
    # And a certainty is not invented on the way out.
    assert "certainty" not in edge.to_dict()


def test_a_ref_a_chunk_could_not_have_carried_is_rejected():
    from tm_knowledge.refs import InvalidRef

    with pytest.raises(InvalidRef):
        ProvisionEdge.from_dict({"id": "TMR1995/s224", "extraction": "regex"})
    with pytest.raises(InvalidRef):
        InternalRef.from_dict({"ref": "TMM/Chapter4/3", "extraction": "href"})


def test_a_loaded_record_cannot_be_edited():
    chunk = Chunk.from_dict(
        {
            "chunk_ref": "TMM/Part22/1/1/2",
            "page_ref": "TMM/Part22/1",
            "text": "some text",
            "heading_path": ["Part 22", "22.1"],
            "ordinal": 1,
            "content_hash": "sha256:" + "a" * 64,
            "links": [{"href": "/trademark/x", "text": "x", "start": 0, "end": 1}],
        }
    )
    with pytest.raises(Exception):
        chunk.text = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        chunk.links[0]["href"] = "/elsewhere"  # type: ignore[index]
    assert chunk.part_id == "Part22"


# ---------------------------------------------------------------------------
# The pinned corpus
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def corpus():
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")
    return load_corpus()


@pytest.mark.snapshot
def test_the_whole_corpus_loads(corpus):
    assert len(corpus.pages) == 500
    assert len(corpus.chunks) == 2460
    assert len(corpus.provisions) == 763
    assert len(corpus.units) == 5813


@pytest.mark.snapshot
def test_round_trip_loses_no_field(corpus):
    """Load, re-emit, compare against the file. Any field this loader does not
    carry shows up here as a difference."""
    for path in sorted((UPSTREAM_DIR / "snapshot" / "pages").rglob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        page = corpus.pages[document["page"]["page_ref"]]
        assert page.to_dict() == document["page"], page.page_ref
        for record in document["chunks"]:
            chunk = corpus.chunks[record["chunk_ref"]]
            assert chunk.to_dict() == record, chunk.chunk_ref

    for path in sorted(
        (UPSTREAM_DIR / "snapshot" / "legislation").rglob("provisions/*/*.json")
    ):
        record = json.loads(path.read_text(encoding="utf-8"))
        assert corpus.provisions[record["ref"]].to_dict() == record, record["ref"]


@pytest.mark.snapshot
def test_the_join_is_string_equality_and_reproduces_upstreams_coverage(corpus):
    """`docs/UPSTREAM.md` §2 quotes 2,611/2,687. Measured against the pinned
    commit the figure is 2,615/2,691 — the same 76 unresolved edges, four more
    in scope. UPSTREAM.md is a source document and is annotated rather than
    edited (Q-20), so the pinned measurement is asserted here."""
    report = corpus.join_report()
    assert report.total == 2717
    assert report.in_scope == 2691
    assert report.resolved == 2615
    assert report.unresolved == 76
    assert report.coverage == pytest.approx(0.972, abs=0.001)

    # No transformation, no lookup table: the chunk's string is the provision's.
    assert corpus.resolve_provision("TMA1995/s43").ref == "TMA1995/s43"
    assert corpus.resolve_provision("TMA1995/s41(3)(a)").ref == "TMA1995/s41(3)(a)"
    # s 43 is one unnumbered subsection, so its only unit is `~1` and a Manual
    # citation to "s 43(1)" resolves to nothing at all. Worth knowing before a
    # gold record is built on one — it is the pilot provision (ADR-0013).
    assert corpus.resolve_provision("TMA1995/s43~1").ref == "TMA1995/s43~1"
    assert corpus.resolve_provision("TMA1995/s43(1)") is None
    assert corpus.resolve_provision("AIA1901/s7") is None


@pytest.mark.snapshot
def test_ambiguous_edges_are_still_ambiguous_at_the_far_end(corpus):
    ambiguous = corpus.ambiguous_edges()
    assert len(ambiguous) == 119
    for chunk_ref, provision_id in ambiguous:
        edge = next(
            e for e in corpus.chunks[chunk_ref].provisions if e.id == provision_id
        )
        assert edge.certainty == "ambiguous"
        assert edge.extraction == "regex"


@pytest.mark.snapshot
def test_the_trust_metadata_survives_in_the_proportions_upstream_emitted(corpus):
    counts: dict[tuple[str, str | None], int] = {}
    for chunk in corpus.chunks.values():
        for edge in chunk.provisions:
            counts[(edge.extraction, edge.certainty)] = (
                counts.get((edge.extraction, edge.certainty), 0) + 1
            )
    assert counts[("href", None)] == 930
    assert counts[("regex", "default")] == 1608
    assert counts[("regex", "ambiguous")] == 119
    assert counts[("regex", "explicit")] == 60
    # Nothing was defaulted into existence, and nothing was collapsed.
    assert sum(counts.values()) == 2717
    assert ("href", "explicit") not in counts


@pytest.mark.snapshot
def test_content_hash_travels_with_every_record(corpus):
    for chunk in corpus.chunks.values():
        assert chunk.content_hash.startswith("sha256:")
    for unit in corpus.units.values():
        assert unit.content_hash.startswith("sha256:")


@pytest.mark.snapshot
def test_unresolved_edges_are_visible_rather_than_silently_dropped(corpus):
    unresolved = corpus.unresolved_edges()
    assert len(unresolved) == 51  # 76 occurrences, 51 distinct
    # The s 41 renumbering trap (Q-06) is in there, and this is where a gold
    # record built on one would be caught.
    assert any(ref.startswith("TMA1995/s41") for ref in unresolved)


@pytest.mark.snapshot
def test_citing_chunks_are_matched_on_the_grammar_not_by_substring(corpus):
    """ADR-0022's rule. `TMA1995/s43` must select `s43`, `s43(1)`, `s43(1)(a)`
    and nothing whose number merely starts with 43."""
    citing = corpus.chunks_citing("TMA1995/s43")
    assert len(citing) == 67, "s 43 is the pilot area (ADR-0013)"
    for chunk in citing:
        assert any(
            edge.id == "TMA1995/s43" or edge.id.startswith(("TMA1995/s43(", "TMA1995/s43~"))
            for edge in chunk.provisions
        )
    # A hypothetical neighbour must not be swept in by prefix matching.
    assert not any(
        edge.id.startswith("TMA1995/s430")
        for chunk in citing
        for edge in chunk.provisions
    )


@pytest.mark.snapshot
def test_the_worksheet_scope_rule_selects_a_workable_volume(corpus):
    """ADR-0022's rule, costed. The rule is deliberately over-inclusive and its
    consequence clause says to report the number rather than quietly tighten it,
    so the number is asserted here: 67 citing chunks on 36 pages, 216 chunks
    once page-mates are included — 8.8% of the corpus."""
    citing = corpus.chunks_citing("TMA1995/s43")
    pages = {chunk.page_ref for chunk in citing}
    selected = {
        mate.chunk_ref for page_ref in pages for mate in corpus.chunks_on_page(page_ref)
    }
    assert len(citing) == 67
    assert len(pages) == 36
    assert len(selected) == 216


@pytest.mark.snapshot
def test_page_mates_are_reachable_and_ordered(corpus):
    for chunk in list(corpus.chunks.values())[:50]:
        mates = corpus.chunks_on_page(chunk.page_ref)
        assert chunk in mates
        assert [m.ordinal for m in mates] == sorted(m.ordinal for m in mates)

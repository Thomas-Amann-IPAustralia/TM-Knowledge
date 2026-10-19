"""The dependency index (R05): every store, keyed by any ref, two views never summed."""

from __future__ import annotations

import pytest

from tm_knowledge.config import REPO_ROOT

UPSTREAM_DIR = REPO_ROOT / "data" / "upstream"
needs_snapshot = pytest.mark.skipif(not UPSTREAM_DIR.exists(), reason="needs the pinned snapshot")


@pytest.fixture(scope="module")
def index():
    from tm_knowledge.ontology import dependencies
    from tm_knowledge.upstream.loader import load_corpus

    return dependencies.build(load_corpus())


def test_how_one_ref_stands_to_another():
    from tm_knowledge.ontology.dependencies import _related

    assert _related("TMA1995/s44", "TMA1995/s44") == "names it"
    assert _related("TMA1995/s44", "TMA1995/s44(3)") == "names a part of it"
    assert _related("TMA1995/s44(3)", "TMA1995/s44") == "names the whole it is part of"
    assert _related("TMA1995/s4", "TMA1995/s44") is None
    assert _related("TMM/Part29", "TMM/Part29/1#1~1") == "names a part of it"


@needs_snapshot
def test_every_record_type_and_both_stores_are_in_it(index):
    """RULE-0002 sees signed records only; the index sees definitions, corrections and
    machine-written records too, each with its review status."""
    summary = index.summary()
    for kind in ("definition", "correction", "gold_concept", "gold_relationship", "concept_type"):
        assert summary["by_type"].get(kind), kind
    assert set(summary["by_status"]) == {"approved", "unreviewed"}
    assert summary["stale"] == []  # the harness's staleness check agrees: nothing has moved
    signed = {d.record for d in index.all("current") if d.store == "signed"}
    assert all(d.review_status == "approved" for d in index.all() if d.store == "signed")
    assert all(d.review_status == "unreviewed" for d in index.all() if d.store == "authored")
    assert signed


@needs_snapshot
def test_a_provision_reaches_records_directly_and_through_the_manual(index):
    direct = index.touching("TMA1995/s44")
    assert direct and {r["how"] for r in direct} <= {"names it", "names a part of it",
                                                     "names the whole it is part of"}
    # A subsection reaches every record that names its section whole.
    whole = {r["record"] for r in direct if r["how"] == "names it"}
    assert whole <= {r["record"] for r in index.touching("TMA1995/s44(3)")}
    via = index.via_manual("TMA1995/s44")
    assert via and all(r["extraction"] in ("href", "regex") for r in via)
    # upstream's certainty passes through; an ambiguous citation is listed, not dropped
    assert {r["certainty"] for r in via} >= {None, "ambiguous"}
    assert any(r["type"] == "definition" for r in via)


@needs_snapshot
def test_a_correction_moves_a_dependency_into_history(index):
    """The current view applies corrections; the as-signed view does not. A dependency a
    correction removed (or a replaced relationship's) is history, and the summary keeps
    the two apart rather than summing them."""
    current = {(d.ref, d.record, d.field) for d in index.all("current") if d.store == "signed"}
    signed = {(d.ref, d.record, d.field) for d in index.all("as_signed")}
    assert signed - current
    assert index.summary()["history_only"] == len([d for d in index.all("as_signed")
                                                   if (d.ref, d.record, d.field) not in current])


@needs_snapshot
def test_an_absence_is_worded_as_no_recorded_dependency():
    import inspect
    from tm_knowledge.explorer import build

    assert "no recorded dependency" in inspect.getsource(build.provision_impact)
    change = (REPO_ROOT / "site" / "js" / "change.js").read_text(encoding="utf-8")
    assert "no recorded dependency, which is not the same as no impact" in change

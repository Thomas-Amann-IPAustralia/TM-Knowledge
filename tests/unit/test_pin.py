"""The pin: it refuses an unpinned, mismatched or edited snapshot.

Everything here runs without a snapshot except `test_pinned_corpus_counts…`,
which is P1's acceptance test and carries the `snapshot` marker.
"""

from __future__ import annotations

import json

import pytest

from tm_knowledge.config import PIN_PATH, UPSTREAM_DIR
from tm_knowledge.upstream.pin import (
    Pin,
    SnapshotMismatch,
    UnpinnedSnapshot,
    measure_corpus,
    tree_digest,
    verify,
    write_receipt,
)

#: `docs/UPSTREAM.md` §2, transcribed. The pin is only meaningful if these are
#: the numbers it actually produces — that is the whole of ADR-0004's claim that
#: "corpus counts in this repo's docs are only meaningful next to the pinned
#: version".
UPSTREAM_MD_COUNTS = {
    "pages": 500,
    "parts": 54,
    "chunks": 2460,
    "links": 2218,
    "instruments": 2,
    "provisions": 763,
    "units": 5813,
}


def test_the_tracked_pin_loads_and_names_a_real_commit():
    pin = Pin.load()
    assert pin.repo == "Thomas-Amann-IPAustralia/manual-XtrACTor"
    assert len(pin.commit) == 40
    assert pin.manual_extractor_version == "ingest/0.11.0"
    assert pin.legislation_extractor_version == "legislation/0.2.0"


def test_the_pin_agrees_with_upstream_md():
    """If someone bumps the pin without updating the docs, this is what says so."""
    pin = Pin.load()
    for key, expected in UPSTREAM_MD_COUNTS.items():
        assert pin.corpus[key] == expected, f"{key}: pin says {pin.corpus[key]}"


def test_an_unpinned_snapshot_is_refused(tmp_path):
    path = tmp_path / "pin.json"
    payload = json.loads(PIN_PATH.read_text())
    payload["commit"] = ""
    path.write_text(json.dumps(payload))
    with pytest.raises(UnpinnedSnapshot):
        Pin.load(path)

    payload["commit"] = "main"
    path.write_text(json.dumps(payload))
    with pytest.raises(UnpinnedSnapshot):
        Pin.load(path)


def test_a_missing_pin_is_refused(tmp_path):
    with pytest.raises(UnpinnedSnapshot):
        Pin.load(tmp_path / "nothing.json")


def test_verify_refuses_a_missing_snapshot(tmp_path):
    with pytest.raises(SnapshotMismatch):
        verify(tmp_path / "absent", Pin.load())


def test_verify_refuses_a_snapshot_with_no_receipt(tmp_path):
    (tmp_path / "snapshot").mkdir()
    with pytest.raises(SnapshotMismatch, match="no fetch receipt"):
        verify(tmp_path, Pin.load())


def test_verify_refuses_a_snapshot_fetched_from_another_commit(tmp_path):
    pin = Pin.load()
    write_receipt(tmp_path, pin, digest="x", counts={})
    receipt = json.loads((tmp_path / ".fetch.json").read_text())
    receipt["commit"] = "0" * 40
    (tmp_path / ".fetch.json").write_text(json.dumps(receipt))
    with pytest.raises(SnapshotMismatch, match="the pin names"):
        verify(tmp_path, pin, deep=False)


def test_tree_digest_is_order_independent_and_content_sensitive(tmp_path):
    root = tmp_path / "snap"
    (root / "snapshot" / "b").mkdir(parents=True)
    (root / "snapshot" / "one.json").write_text("1")
    (root / "snapshot" / "b" / "two.json").write_text("2")
    first = tree_digest(root, ("snapshot",))
    assert first == tree_digest(root, ("snapshot",))

    (root / "snapshot" / "b" / "two.json").write_text("2 ")
    assert tree_digest(root, ("snapshot",)) != first


def test_tree_digest_reports_a_missing_pinned_path(tmp_path):
    with pytest.raises(SnapshotMismatch, match="pinned path missing"):
        tree_digest(tmp_path, ("snapshot",))


@pytest.mark.snapshot
def test_pinned_corpus_counts_match_upstream_md():
    """P1's acceptance test. Needs `tmk-fetch-upstream` to have run."""
    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")
    counts = measure_corpus(UPSTREAM_DIR)
    for key, expected in UPSTREAM_MD_COUNTS.items():
        assert counts[key] == expected
    verify(deep=True)

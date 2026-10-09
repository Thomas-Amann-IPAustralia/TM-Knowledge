"""Corrections to signed records, the withdrawal ledger, and what serves (ADR-0122).

The owner ruled on 2026-10-08 that known defects in signed records are corrected
now rather than queued for an expert (review D2, ADR-0121). These tests pin the two
rules that make that safe: `eval/gold/` stays exactly as signed, and a correction is
machine-written, unreviewed and applied only where the system serves.
"""

from __future__ import annotations

import copy

import pytest
import yaml

from tm_knowledge.authored import corrections
from tm_knowledge.authored import store as authored_store
from tm_knowledge.stage0 import goldset

AGENT_ENVELOPE = {
    "review_status": "unreviewed", "authored_by": "test-agent", "authored_date": "2026-10-08",
    "authoring_basis": "general_knowledge", "confidence": 0.5, "reasoning": "A fixture.",
    "alternatives_considered": [], "expert_should_check": None,
}


def _write(tmp_path, rows):
    root = tmp_path / "authored"
    root.mkdir()
    (root / "corrections.yaml").write_text(yaml.safe_dump(rows, sort_keys=False), encoding="utf-8")
    return root


def _row(**fields):
    row = {"id": "GK-0001", "corrects": "GC-0006", "record_type": "gold_concept",
           "ruling": "review/rulings/x.yaml#A2", "approved_by": None, "approved_date": None}
    row.update(fields)
    row["authored"] = copy.deepcopy(AGENT_ENVELOPE)
    return row


def test_the_committed_corrections_are_all_sound():
    loaded = corrections.load()
    assert loaded.entries, "authored/corrections.yaml is expected to hold the 2026-10-08 corrections"
    assert loaded.refused == (), [(e.id, e.errors) for e in loaded.refused]
    for entry in loaded.entries:
        assert entry.record["approved_by"] is None
        assert entry.envelope["review_status"] == "unreviewed"


def test_served_and_in_force_views_differ_only_as_designed():
    gold = goldset.load()
    loaded = corrections.load(gold=gold)
    served = corrections.served_gold(gold, loaded)
    in_force = corrections.in_force_gold(gold, loaded)
    signed = {r["id"]: r for r in gold["gold_concept"]}
    for entry in loaded.sound:
        if entry.record["record_type"] != "gold_concept":
            continue
        target = entry.target
        served_record = next(r for r in served["gold_concept"] if r["id"] == target)
        in_force_record = next(r for r in in_force["gold_concept"] if r["id"] == target)
        for name, values in (entry.record.get("remove") or {}).items():
            assert not set(values) & set(served_record.get(name) or ())
            assert not set(values) & set(in_force_record.get(name) or ())
            assert set(values) <= set(signed[target].get(name) or ()), "the signed record keeps it"
        for name, values in (entry.record.get("add") or {}).items():
            assert set(values) <= set(served_record.get(name) or ())
            # the approved graph never states a value nobody signed
            unsigned = set(values) - set(signed[target].get(name) or ())
            assert not unsigned & set(in_force_record.get(name) or ())
    replaced = set(loaded.replacements())
    assert replaced and not replaced & {r["id"] for r in served["gold_relationship"]}
    assert replaced <= {r["id"] for r in in_force["gold_relationship"]}, "history stays in force view"


def test_eval_gold_is_untouched_by_loading_corrections():
    before = goldset.load()
    corrections.served_gold(before)
    after = goldset.load()
    assert [r for _, r in before.all_records()] == [r for _, r in after.all_records()]


def test_a_removal_of_a_value_the_record_does_not_carry_is_refused(tmp_path):
    root = _write(tmp_path, [_row(remove={"alt_labels": ["a label nobody signed"]})])
    loaded = corrections.load(root)
    assert loaded.refused and "does not carry" in str(loaded.refused[0].errors)


def test_approved_by_can_never_be_filled(tmp_path):
    root = _write(tmp_path, [_row(add={"alt_labels": ["x"]}, approved_by="TC")])
    assert corrections.load(root).refused


def test_a_relationship_is_corrected_by_replacement_only(tmp_path):
    root = _write(tmp_path, [_row(corrects="GR-0032", record_type="gold_relationship",
                                  add={"alt_labels": ["x"]})])
    errors = " ".join(str(e) for e in corrections.load(root).refused[0].errors)
    assert "replacement" in errors


def test_withdrawn_ids_are_never_reused():
    from tm_knowledge.bulk.jobs import next_number

    authored = authored_store.load()
    assert authored.retired_ids, "the ledger holds the 2026-10-08 withdrawals"
    held = {e.record_id for e in authored.entries}
    assert not held & set(authored.retired_ids), "a withdrawn id is back in service"
    for prefix in ("GC", "GT", "GR"):
        highest = max(int(i[3:]) for i in authored.retired_ids if i.startswith(prefix + "-"))
        assert next_number(prefix) > highest


@pytest.mark.parametrize("withdrawn", ["GC-0118", "GC-0146", "GC-0166"])
def test_a_withdrawn_concept_says_why_and_by_whose_ruling(withdrawn):
    meta = authored_store.load().retired_ids[withdrawn]
    assert meta["reason"] and meta["ruling"].startswith("review/rulings/2026-10-08-chat-ontology-review.yaml#")
    assert meta.get("label"), "a withdrawn concept keeps its label, so define does not re-propose it"

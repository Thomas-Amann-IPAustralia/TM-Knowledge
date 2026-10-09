"""The structure review's applier (ADR-0131) and the harness check on kinds."""

from __future__ import annotations

from types import SimpleNamespace

import yaml

from tm_knowledge.authored import store as authored_store
from tm_knowledge.bulk import links as links_module
from tm_knowledge.bulk import restructure
from tm_knowledge.stage0 import harness

ENV = {"review_status": "unreviewed", "authored_by": "gpt-6.1-sol", "authored_date": "2026-10-07",
       "authoring_basis": "corpus_explicit", "confidence": 0.9, "reasoning": "«first»",
       "evidence": [{"ref": "TMM/Part1/1#1", "span": [0, 10], "content_hash": "sha256:" + "a" * 64,
                     "quote": "«a quote»"}],
       "alternatives_considered": [], "expert_should_check": None}

LEDGER = {"authored_by": "claude-code-agent-S000", "date": "2026-10-09",
          "ruling": "review/rulings/2026-10-09-chat-ontology-structure.yaml"}


def _concept(cid, label, group):
    return links_module.Concept(cid, label, (label,), "authored", group=group)


def _ctx(tmp_path, records):
    rows = [{**r, "source_ref": "TMM/Part1/1#1", "span": [0, 10], "source_content_hash": "sha256:" + "a" * 64,
             "tier": 3, "modality": None, "approved_by": None, "approved_date": None, "authored": dict(ENV)}
            for r in records]
    (tmp_path / "relationships.yaml").write_text(
        "# header\n" + yaml.dump(rows, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (tmp_path / authored_store.RETIRED_IDS_FILE).write_text("[]\n", encoding="utf-8")
    concepts = {
        "GC-0046": _concept("GC-0046", "Registrar", "process_role"),
        "GC-0040": _concept("GC-0040", "opposition", "procedural_step"),
        "GC-0127": _concept("GC-0127", "Registrar's decision", "instrument_or_record"),
    }
    return SimpleNamespace(links=links_module.Links(concepts=concepts, mentions={}, passages=1),
                           authored=authored_store.load(tmp_path), gold={"gold_relationship": ()})


TEXT = "The Registrar decides the opposition and issues the Registrar's decision."


def test_a_related_edge_is_re_read_withdrawn_or_refused(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "related", "object": "GC-0040", "supporting_text": TEXT},
        {"id": "GR-0002", "subject": "GC-0040", "predicate": "related", "object": "GC-0127", "supporting_text": TEXT},
        {"id": "GR-0003", "subject": "GC-0046", "predicate": "related", "object": "GC-0127", "supporting_text": TEXT},
        {"id": "GR-0004", "subject": "GC-0127", "predicate": "related", "object": "GC-0046", "supporting_text": TEXT},
    ])
    ledger = dict(LEDGER, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "why": "«decides»"},
        {"edge": "GR-0002", "withdraw": "«a co-mention»"},
        # the wrong way round: a step does not perform a role
        {"edge": "GR-0003", "to": ["GC-0040", "performs", "GC-0046"], "why": "«backwards»"},
    ])
    result = restructure.plan(ctx, ledger)
    assert set(result.rereads) == {"GR-0001"}
    assert [w["id"] for w in result.withdrawn] == ["GR-0002"]
    assert any(line.startswith("GR-0003") and "subject" in line for line in result.refused)
    # a "related" edge the ledger says nothing about is refused, not left behind
    assert any(line.startswith("GR-0004") and "retired" in line for line in result.refused)
    record = result.rereads["GR-0001"]
    assert record["authored"]["authored_by"] == "claude-code-agent-S000"
    assert record["approved_by"] is None and record["authored"]["review_status"] == "unreviewed"
    assert "gpt-6.1-sol" in record["authored"]["alternatives_considered"][0]
    assert not result.ok


def test_a_plan_with_refusals_writes_nothing_and_a_clean_one_applies_once(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "related", "object": "GC-0040", "supporting_text": TEXT},
        {"id": "GR-0002", "subject": "GC-0040", "predicate": "related", "object": "GC-0127", "supporting_text": TEXT},
    ])
    ledger = dict(LEDGER, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "why": "«decides»"},
        {"edge": "GR-0002", "to": ["GC-0040", "resultsIn", "GC-0127"], "why": "«ends in»"},
    ])
    result = restructure.plan(ctx, ledger)
    assert result.ok
    assert restructure.apply(result, root=tmp_path)["reread"] == 2
    again = restructure.plan(_ctx_from_disk(tmp_path, ctx), ledger)
    assert again.ok and again.done == 2 and not again.rereads


def _ctx_from_disk(tmp_path, ctx):
    return SimpleNamespace(links=ctx.links, authored=authored_store.load(tmp_path), gold=ctx.gold)


def test_a_re_read_onto_a_triple_already_stated_is_withdrawn_in_its_favour(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040", "supporting_text": TEXT},
        {"id": "GR-0002", "subject": "GC-0046", "predicate": "related", "object": "GC-0040", "supporting_text": TEXT},
    ])
    result = restructure.plan(ctx, dict(LEDGER, edges=[
        {"edge": "GR-0002", "to": ["GC-0046", "performs", "GC-0040"], "why": "«same»"}]))
    assert result.withdrawn == [{"id": "GR-0002", "reason": result.withdrawn[0]["reason"], "replaced_by": "GR-0001"}]


def test_the_harness_refuses_an_edge_between_kinds_its_predicate_does_not_join():
    def entry(rid, record):
        return SimpleNamespace(record_id=rid, record=record, sound=True)

    authored = SimpleNamespace(of=lambda kind: {
        "concept_type": (entry("GT-1", {"concept": "GC-0046", "type": "process_role"}),
                         entry("GT-2", {"concept": "GC-0040", "type": "procedural_step"})),
        "gold_relationship": (entry("GR-1", {"subject": "GC-0046", "predicate": "performs", "object": "GC-0040"}),
                              entry("GR-2", {"subject": "GC-0040", "predicate": "performs", "object": "GC-0046"})),
    }[kind])
    found = list(harness._authored_kinds(authored))
    assert [(f.subject, f.check) for f in found] == [("GR-2", "authored-kinds")]
    assert found[0].severity == harness.Severity.DEFECT

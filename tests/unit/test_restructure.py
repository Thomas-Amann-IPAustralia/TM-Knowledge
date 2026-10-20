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
    defaults = {"source_ref": "TMM/Part1/1#1", "span": [0, 10], "source_content_hash": "sha256:" + "a" * 64,
                "tier": 3, "modality": None, "approved_by": None, "approved_date": None, "authored": dict(ENV)}
    rows = [{**r, **{k: v for k, v in defaults.items() if k not in r}} for r in records]
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


# --- S036: the review response's worklist goes through the same applier -------------
#
# Thirty of the 130 S029 re-reads kept the modality of their earlier reading, because
# a re-read copied every field but the triple (the review response, F05 and F16). A
# re-read that changes the predicate now drops it unless the ledger gives one, a line
# may set a modality or a condition on a record whose triple stands, a line may record
# that a record was checked and kept, and a second ledger reports to its own file under
# its own ruling.

S036 = {"authored_by": "claude-code-agent-S036", "date": "2026-10-16",
        "ruling": "review/rulings/2026-10-09-chat-ontology-structure.yaml", "ruling_item": "CHAT-0073",
        "review": "the review response's worklist (S036)",
        "report": "data/derived/reports/review-response-edges.md"}


def test_a_re_read_onto_another_predicate_drops_the_modality_it_copied(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "issues", "object": "GC-0040",
         "supporting_text": TEXT, "modality": "must"},
        {"id": "GR-0002", "subject": "GC-0040", "predicate": "operatesOn", "object": "GC-0127",
         "supporting_text": TEXT, "modality": "should"},
    ])
    result = restructure.plan(ctx, dict(S036, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "why": "«decides»"},
        {"edge": "GR-0002", "to": ["GC-0040", "resultsIn", "GC-0127"], "modality": "may", "why": "«ends in»"},
    ]))
    assert result.ok, result.refused
    assert result.rereads["GR-0001"]["modality"] is None, "the old verb's modality came along"
    assert result.rereads["GR-0002"]["modality"] == "may"


def test_a_line_may_set_a_records_modality_and_condition_without_moving_it(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040",
         "supporting_text": TEXT, "modality": "should"},
        {"id": "GR-0002", "subject": "GC-0040", "predicate": "resultsIn", "object": "GC-0127", "supporting_text": TEXT},
    ])
    result = restructure.plan(ctx, dict(S036, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "modality": None,
         "applies_when": "decides the opposition", "why": "«the should was another verb's»"},
        {"edge": "GR-0002", "to": ["GC-0040", "resultsIn", "GC-0127"],
         "applies_when": "after the opposition is heard", "why": "«retyped»"},
    ]))
    record = result.rereads["GR-0001"]
    assert record["modality"] is None and record["applies_when"] == "decides the opposition"
    assert "Checked on 2026-10-16" in record["notes"] and record["authored"]["authored_by"] == "claude-code-agent-S036"
    assert any(line.startswith("GR-0002") and "not in the supporting sentence" in line for line in result.refused)


def test_a_keep_line_writes_nothing_and_is_reported(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040", "supporting_text": TEXT},
    ])
    result = restructure.plan(ctx, dict(S036, edges=[{"edge": "GR-0001", "keep": "«it says so»"}]))
    assert result.ok and not result.rereads and not result.withdrawn
    assert [k[0] for k in result.kept] == ["GR-0001"]
    assert "GR-0001" in restructure.render(result, {})


def test_a_second_ledger_reports_to_its_own_file_and_names_its_own_ruling(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040", "supporting_text": TEXT},
    ])
    result = restructure.plan(ctx, dict(S036, edges=[{"edge": "GR-0001", "withdraw": "«overstates»"}]))
    assert restructure.report_path(result.ledger).name == "review-response-edges.md"
    assert restructure.report_path(LEDGER) == restructure.REPORT_PATH
    (tmp_path / authored_store.RETIRED_IDS_FILE).write_text("# withdrawn ids\n", encoding="utf-8")
    restructure.apply(result, root=tmp_path)
    retired = yaml.safe_load((tmp_path / authored_store.RETIRED_IDS_FILE).read_text(encoding="utf-8"))
    assert retired[0]["ruling"].endswith("#CHAT-0073")
    assert retired[0]["reason"].startswith("The review response's worklist (S036)")


def test_an_earlier_ledger_never_undoes_a_later_ones_reading(tmp_path):
    """S029's ledger counted a line as applied only when the record carried S029's stamp,
    so once S036 re-read a record, running S029's ledger again would have re-read it back,
    undoing the later judgement. A record whose kept alternatives hold the earlier
    ledger's reading has been read since: that line is done."""
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "related", "object": "GC-0040", "supporting_text": TEXT},
    ])
    first = dict(LEDGER, edges=[{"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "why": "«decides»"}])
    restructure.apply(restructure.plan(ctx, first), root=tmp_path)
    later = dict(S036, edges=[{"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "modality": "may",
                                "why": "«its discretion»"}])
    restructure.apply(restructure.plan(_ctx_from_disk(tmp_path, ctx), later), root=tmp_path)
    again = restructure.plan(_ctx_from_disk(tmp_path, ctx), first)
    assert again.ok and not again.rereads and again.done == 1


# --- S041: hedges, withdrawn conditions and re-anchoring (the second review response, R01) ---

S041 = dict(S036, authored_by="claude-code-agent-S041", date="2026-10-19",
            review="the second review response's R01 (S041)")
HEDGED = "The Registrar usually decides the opposition where it is defended."


def test_a_line_may_split_a_hedge_from_its_condition_and_withdraw_a_condition(tmp_path):
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040",
         "supporting_text": HEDGED, "applies_when": "usually"},
        {"id": "GR-0002", "subject": "GC-0040", "predicate": "resultsIn", "object": "GC-0127",
         "supporting_text": HEDGED},
    ])
    result = restructure.plan(ctx, dict(S041, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "applies_when": "where it is defended",
         "hedge": "usually", "why": "«split»"},
        {"edge": "GR-0002", "to": ["GC-0040", "resultsIn", "GC-0127"], "hedge": "rarely", "why": "«retyped»"},
    ]))
    record = result.rereads["GR-0001"]
    assert record["applies_when"] == "where it is defended" and record["hedge"] == "usually"
    assert "its hedge recorded" in record["notes"]
    assert any(line.startswith("GR-0002") and "hedge 'rarely' is not in" in line for line in result.refused)

    ctx = _ctx(tmp_path, [{"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040",
                           "supporting_text": HEDGED, "applies_when": "usually"}])
    cleared = restructure.plan(ctx, dict(S041, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "applies_when": None, "hedge": "usually",
         "why": "«a hedge, not a condition»"}]))
    assert "applies_when" not in cleared.rereads["GR-0001"] and cleared.rereads["GR-0001"]["hedge"] == "usually"


def test_a_line_may_re_anchor_a_record_on_sentences_it_locates(tmp_path, monkeypatch):
    from tm_knowledge.bulk import jobs

    passages = {"TMM/Part1/1#2": "First. The Registrar decides the opposition. Unless it is withdrawn."}

    def evidence(_corpus, ref, quote):
        text = passages.get(ref)
        if text is None or quote not in text:
            return None
        start = text.index(quote)
        return {"ref": ref, "span": [start, start + len(quote)], "content_hash": "sha256:" + "b" * 64,
                "quote": quote}

    monkeypatch.setattr(jobs, "evidence", evidence)
    ctx = _ctx(tmp_path, [{"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040",
                           "supporting_text": TEXT}])
    ctx.corpus = None
    result = restructure.plan(ctx, dict(S041, edges=[{
        "edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "why": "«the right sentence»",
        "evidence": [{"ref": "TMM/Part1/1#2", "quote": "The Registrar decides the opposition."},
                     {"ref": "TMM/Part1/1#2", "quote": "Unless it is withdrawn."}]}]))
    record = result.rereads["GR-0001"]
    assert record["source_ref"] == "TMM/Part1/1#2" and record["supporting_text"] == "The Registrar decides the opposition."
    assert record["span"] == [7, 44] and [e["quote"] for e in record["authored"]["evidence"]][1] == "Unless it is withdrawn."
    assert record["authored"]["authoring_basis"] == "corpus_explicit"
    refused = restructure.plan(ctx, dict(S041, edges=[{
        "edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "why": "«»",
        "evidence": [{"ref": "TMM/Part1/1#2", "quote": "Not there."}]}]))
    assert refused.refused and "does not occur" in refused.refused[0]


def test_a_third_ledger_keeps_the_first_ledgers_reading_so_neither_earlier_one_undoes_it(tmp_path):
    """S041 re-read records S036 had re-read from S029's: unless the chain of readings is
    kept, S029's ledger finds no trace of itself and reads them back (Q-93)."""
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "related", "object": "GC-0040", "supporting_text": TEXT},
    ])
    first = dict(LEDGER, edges=[{"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "why": "«decides»"}])
    restructure.apply(restructure.plan(ctx, first), root=tmp_path)
    second = dict(S036, edges=[{"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "modality": "may",
                                "why": "«its discretion»"}])
    restructure.apply(restructure.plan(_ctx_from_disk(tmp_path, ctx), second), root=tmp_path)
    third = dict(S041, edges=[{"edge": "GR-0001", "to": ["GC-0040", "resultsIn", "GC-0127"], "why": "«ends in»"}])
    restructure.apply(restructure.plan(_ctx_from_disk(tmp_path, ctx), third), root=tmp_path)
    for earlier in (first, second):
        again = restructure.plan(_ctx_from_disk(tmp_path, ctx), earlier)
        assert again.ok and not again.rereads and again.done == 1, earlier["authored_by"]


def test_a_same_triple_line_never_withdraws_a_record_that_shares_its_triple(tmp_path):
    """GR-0065 and GR-0066 state one triple from two sentences, each under its own
    condition: qualifying one must not withdraw it in the other's favour."""
    ctx = _ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040", "supporting_text": HEDGED},
        {"id": "GR-0002", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040", "supporting_text": HEDGED},
    ])
    result = restructure.plan(ctx, dict(S041, edges=[
        {"edge": "GR-0002", "to": ["GC-0046", "performs", "GC-0040"], "applies_when": "where it is defended",
         "why": "«its condition»"}]))
    assert not result.withdrawn and result.rereads["GR-0002"]["applies_when"] == "where it is defended"


def test_a_line_may_record_why_a_conditional_word_conditions_nothing(tmp_path):
    ctx = _ctx(tmp_path, [{"id": "GR-0001", "subject": "GC-0046", "predicate": "performs", "object": "GC-0040",
                           "supporting_text": HEDGED}])
    result = restructure.plan(ctx, dict(S041, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "no_condition": "«the where is another clause's»",
         "why": "«assessed»"}]))
    assert result.rereads["GR-0001"]["no_condition"] == "«the where is another clause's»"
    restructure.apply(result, root=tmp_path)
    again = restructure.plan(_ctx_from_disk(tmp_path, ctx), dict(S041, edges=[
        {"edge": "GR-0001", "to": ["GC-0046", "performs", "GC-0040"], "no_condition": "«the where is another clause's»",
         "why": "«assessed»"}]))
    assert again.done == 1 and not again.rereads


def test_an_earlier_ledger_never_undoes_a_later_ones_concept_reading(tmp_path):
    """S042 (R10): the concept path kept only the reading it replaced and counted a line
    done only under its own stamp, so re-reading a concept S029 had relabelled made S029's
    ledger want to relabel it again. A concept re-read keeps the chain of readings, and a
    line is done once a later ledger has read the record since (Q-93, Q-98)."""
    concept = {"id": "GC-0126", "pref_label": "protected term", "alt_labels": [], "not_labels": [],
               "narrower": [], "related": [], "definition_sources": ["TMM/Part1/1#1"],
               "legislative_basis": ["TMA1995/s61"], "notes": None, "approved_by": None,
               "approved_date": None, "authored": dict(ENV)}
    (tmp_path / "concepts.yaml").write_text(yaml.dump([concept], sort_keys=False), encoding="utf-8")
    ctx = _ctx(tmp_path, [])
    first = dict(LEDGER, concepts=[{"concept": "GC-0126", "set": {"alt_labels": ["term on the Wine Register"]},
                                    "why": "«the Manual's name»"}])
    restructure.apply(restructure.plan(_ctx_from_disk(tmp_path, ctx), first), root=tmp_path)
    later = dict(S041, authored_by="claude-code-agent-S042", concepts=[
        {"concept": "GC-0126", "set": {"legislative_basis": []}, "why": "«s 61 says nothing of it»"}])
    restructure.apply(restructure.plan(_ctx_from_disk(tmp_path, ctx), later), root=tmp_path)
    stored = yaml.safe_load((tmp_path / "concepts.yaml").read_text(encoding="utf-8"))[0]["authored"]
    chain = stored["alternatives_considered"]
    assert chain[0].startswith("As first written by claude-code-agent-S000 ")
    assert chain[1].startswith("As first written by gpt-6.1-sol ")
    again = restructure.plan(_ctx_from_disk(tmp_path, ctx), first)
    assert again.ok and not again.concepts and again.done == 1

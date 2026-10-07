"""The paid pipeline spends only what it is allowed, and writes only what lands.

Three things are protected here, in the order money and provenance would be lost:

1. **The cap is checked before a call, and a cached answer is never paid for
   twice.** A stub transport stands in for the API and counts what it was sent;
   the command line never passes one (KB SOP §10).
2. **A quote that does not occur in the snapshot is refused**, and one that does
   is recorded as the snapshot's text, not the model's — so the harness's
   "quote equals text at span" check can never fail on pipeline output.
3. **Every record is unreviewed, carries the model the API reported, and leaves
   `approved_by` empty** (ADR-0079, ADR-0094).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tm_knowledge.bulk import client, jobs
from tm_knowledge.bulk import links as links_module

SCHEMA = jobs._strict({"answer": jobs.STR})


def _stub(reply_text: str = '{"answer": "yes"}', model: str = "gpt-6.1-sol-2026-09-30"):
    sent: list[dict] = []

    def transport(path, body):
        sent.append(body)
        return {
            "model": model, "status": "completed", "service_tier": "flex",
            "usage": {"input_tokens": 1000, "input_tokens_details": {"cached_tokens": 200},
                      "output_tokens": 500, "output_tokens_details": {"reasoning_tokens": 400}},
            "output": [{"type": "reasoning"},
                       {"type": "message", "content": [{"type": "output_text", "text": reply_text}]}],
        }

    return transport, sent


def _call(cache, transport, **overrides):
    kwargs = dict(job="t", prompt_version="t-v1", item="one", instructions="Be brief.",
                  input_text="Question?", schema=SCHEMA, max_output_tokens=1000,
                  model="gpt-6.1-sol", effort="medium", tier="flex", confirm=True,
                  cache=cache, transport=transport)
    kwargs.update(overrides)
    return client.respond(**kwargs)


def test_cost_bills_reasoning_as_output_and_discounts_cached_input():
    usage = {"input_tokens": 1_000_000, "input_tokens_details": {"cached_tokens": 500_000},
             "output_tokens": 100_000}
    # flex: 500k × $1.00 + 500k × $0.05 + 100k × $5.00, per million
    assert client.cost_usd("gpt-6.1-sol", "flex", usage) == pytest.approx(0.5 + 0.025 + 0.5)
    assert client.cost_usd("gpt-6.1-sol-2026-09-30", "default", usage) == pytest.approx(1.0 + 0.05 + 1.0)


def test_an_unpriced_model_is_never_called(tmp_path):
    transport, sent = _stub()
    with pytest.raises(client.UnpricedModel):
        _call(client.Cache(tmp_path), transport, model="some-unknown-model")
    assert sent == []


def test_no_paid_call_without_confirm(tmp_path):
    transport, sent = _stub()
    with pytest.raises(client.NotConfirmed):
        _call(client.Cache(tmp_path), transport, confirm=False)
    assert sent == []


def test_a_dry_run_spends_nothing_and_estimates(tmp_path):
    transport, sent = _stub()
    entry, estimate = _call(client.Cache(tmp_path), transport, dry_run=True, confirm=False)
    assert entry is None and sent == []
    assert estimate.worst_case_usd > 0


def test_a_cached_answer_is_free_and_not_resent(tmp_path):
    cache = client.Cache(tmp_path)
    transport, sent = _stub()
    first, _ = _call(cache, transport)
    second, _ = _call(cache, transport, tier="default")  # the tier changes the price, not the answer
    assert len(sent) == 1
    assert second["from_cache"] and second["output_text"] == first["output_text"]
    assert cache.spent_usd() == pytest.approx(first["cost_usd"])


def test_the_cap_refuses_before_sending(tmp_path, monkeypatch):
    cache = client.Cache(tmp_path)
    transport, sent = _stub()
    monkeypatch.setenv("TMK_SPEND_CAP_USD", "0.001")
    with pytest.raises(client.BudgetExceeded):
        _call(cache, transport)
    assert sent == []


def test_the_entry_records_the_model_the_api_reported(tmp_path):
    transport, _ = _stub(model="gpt-6.1-sol-2026-09-30")
    entry, _ = _call(client.Cache(tmp_path), transport)
    assert entry["model_requested"] == "gpt-6.1-sol"
    assert entry["model_reported"] == "gpt-6.1-sol-2026-09-30"
    assert entry["usage"]["output_tokens_details"]["reasoning_tokens"] == 400


# ------------------------------------------------------------------ quotes


def test_locate_finds_exact_and_normalised_quotes():
    text = "The Registrar must  reject an application — see ‘Part 29’."
    assert jobs.locate(text, "must  reject an application") == (14, 41)
    start, end = jobs.locate(text, "must reject an application - see 'Part 29'")
    assert text[start:end] == "must  reject an application — see ‘Part 29’"
    assert jobs.locate(text, "must accept the application") is None
    assert jobs.locate(text, "must") is None  # too short to mean anything


# --------------------------------------------------------------- relate


def _ctx(text: str):
    chunk = SimpleNamespace(text=text, content_hash="sha256:" + "a" * 64)
    corpus = SimpleNamespace(chunks={"TMM/Part1/1#1": chunk}, pages={}, resolve_provision=lambda ref: None)
    concepts = {
        "GC-0001": links_module.Concept("GC-0001", "opposition", ("opposition",), "signed"),
        "GC-0002": links_module.Concept("GC-0002", "notice of opposition", ("notice of opposition",), "authored"),
    }
    links = links_module.Links(concepts=concepts, mentions={k: [] for k in concepts}, passages=1)
    return SimpleNamespace(corpus=corpus, links=links)


def _judgement(**overrides):
    j = {"neighbour": "GC-0002", "relation": "requiresElement", "direction": "anchor_to_neighbour",
         "passage_ref": "TMM/Part1/1#1", "quote": "An opposition is started by filing a notice of opposition",
         "modality": "must", "basis": "corpus_explicit", "confidence": 0.9, "reasoning": "Stated.",
         "alternative": "related_to", "expert_should_check": "Whether 'started' implies a requirement."}
    j.update(overrides)
    return j


ITEM = jobs.Item("GC-0001", {"anchor": "GC-0001", "neighbours": [{"id": "GC-0002", "refs": ["TMM/Part1/1#1"]}]})
ENTRY = {"model_reported": "gpt-6.1-sol-2026-09-30"}
TEXT = "An opposition is started by filing a notice of opposition within two months."


def test_a_relationship_is_unreviewed_unsigned_and_quotes_the_snapshot():
    outcome = jobs._relate_accept(_ctx(TEXT), ITEM, {"judgements": [_judgement()]}, ENTRY)
    (record,) = outcome.records["relationships"]
    assert record["approved_by"] is None and record["approved_date"] is None
    assert record["authored"]["review_status"] == "unreviewed"
    assert record["authored"]["authored_by"] == "gpt-6.1-sol-2026-09-30"
    start, end = record["span"]
    assert TEXT[start:end] == record["supporting_text"] == record["authored"]["evidence"][0]["quote"]
    assert (record["subject"], record["object"]) == ("GC-0001", "GC-0002")


def test_a_quote_that_does_not_land_is_refused_not_written():
    parsed = {"judgements": [_judgement(quote="An opposition must be filed by the Registrar")]}
    outcome = jobs._relate_accept(_ctx(TEXT), ITEM, parsed, ENTRY)
    assert not outcome.records and "does not occur" in outcome.refused[0]


def test_a_passage_not_shown_or_a_neighbour_not_sent_is_refused():
    outcome = jobs._relate_accept(_ctx(TEXT), ITEM, {"judgements": [
        _judgement(passage_ref="TMM/Part9/9#9"), _judgement(neighbour="GC-0999")]}, ENTRY)
    assert not outcome.records and len(outcome.refused) == 2


def test_same_concept_is_reported_for_a_person_not_written():
    outcome = jobs._relate_accept(_ctx(TEXT), ITEM, {"judgements": [_judgement(relation="same_concept")]}, ENTRY)
    assert not outcome.records and "same concept" in outcome.notes[0]


def test_is_kind_of_becomes_skos_broader_with_the_narrower_concept_as_subject():
    outcome = jobs._relate_accept(_ctx(TEXT), ITEM, {"judgements": [
        _judgement(relation="is_kind_of", direction="neighbour_to_anchor", modality="none")]}, ENTRY)
    (record,) = outcome.records["relationships"]
    assert (record["subject"], record["predicate"], record["object"]) == ("GC-0002", "broader", "GC-0001")
    assert record["modality"] is None and record["tier"] == 2


# ----------------------------------------------------------------- links


def test_labels_match_whole_words_only():
    concepts = {"GC-0001": links_module.Concept("GC-0001", "mark", ("mark",), "signed"),
                "GC-0002": links_module.Concept("GC-0002", "Registrar", ("Registrar",), "signed")}
    patterns = links_module._patterns(concepts)
    found = links_module.find_mentions("The Registrar considered marketplace evidence.", patterns)
    assert set(found) == {"GC-0002"}


def test_a_generic_concept_is_linked_but_never_paired():
    concepts = {cid: links_module.Concept(cid, cid, (cid,), "signed") for cid in ("GC-0001", "GC-0002", "GC-0003")}
    mentions = {
        "GC-0001": [(f"TMM/Part1/{i}#1", 0, 4, "x") for i in range(10)],  # everywhere: generic
        "GC-0002": [("TMM/Part1/1#1", 10, 14, "y"), ("TMM/Part1/2#1", 10, 14, "y")],
        "GC-0003": [("TMM/Part1/1#1", 20, 24, "z"), ("TMM/Part1/2#1", 30, 34, "z")],
    }
    links = links_module.Links(concepts, mentions, passages=10, generic=frozenset({"GC-0001"}))
    pairs = links_module.pairs(links)
    assert [(p.a, p.b) for p in pairs] == [("GC-0002", "GC-0003")]
    assert links_module.pairs(links, {frozenset(("GC-0002", "GC-0003"))}) == []


def test_a_failed_response_is_kept_but_never_replayed(tmp_path):
    cache = client.Cache(tmp_path)
    sent: list[dict] = []

    def failing(path, body):
        sent.append(body)
        return {"model": "gpt-6.1-sol", "status": "failed", "usage": {}, "output": [],
                "error": {"code": "server_error"}}

    first, _ = _call(cache, failing)
    assert first["status"] == "failed" and first["cost_usd"] == 0
    transport, _ = _stub()
    second, _ = _call(cache, transport)
    assert len(sent) == 1 and second["status"] == "completed" and not second.get("from_cache")
    assert len(list(tmp_path.rglob("*.failed-*.json"))) == 1


def test_an_overloaded_flex_call_is_retried_and_the_answer_kept(tmp_path, monkeypatch):
    monkeypatch.setattr(client, "RETRY_WAITS", (0, 0))
    cache = client.Cache(tmp_path)
    replies = iter([
        {"model": "gpt-6.1-sol", "status": "failed", "usage": {}, "output": [],
         "error": {"code": "server_is_overloaded"}},
    ])
    transport, sent = _stub()

    def flaky(path, body):
        try:
            return next(replies)
        except StopIteration:
            return transport(path, body)

    entry, _ = _call(cache, flaky)
    assert entry["status"] == "completed" and len(sent) == 1
    assert len(list(tmp_path.rglob("*.failed-*.json"))) == 1


def test_a_batch_answers_each_request_and_caches_it_as_one_call(tmp_path):
    cache = client.Cache(tmp_path)
    submitted: list[list[dict]] = []

    def fake_batch(lines, poll, progress):
        submitted.append(lines)
        return {line["custom_id"]: {"custom_id": line["custom_id"], "response": {"status_code": 200, "body": {
            "model": "gpt-6.1-sol", "status": "completed",
            "usage": {"input_tokens": 1000, "output_tokens": 100},
            "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"answer": "ok"}'}]}]}}}
            for line in lines}

    rq = dict(job="t", prompt_version="t-v1", instructions="Be brief.", schema=SCHEMA, max_output_tokens=1000,
              model="gpt-6.1-sol", effort="medium")
    requests = [dict(rq, item="a", input_text="One?"), dict(rq, item="b", input_text="Two?")]
    results = client.batch_respond(requests, confirm=True, cache=cache, transport=fake_batch, progress=lambda s: None)
    assert [e["service_tier"] for e, _ in results] == ["batch", "batch"]
    assert results[0][0]["cost_usd"] == pytest.approx((1000 * 1.00 + 100 * 5.00) / 1_000_000)
    again = client.batch_respond(requests, confirm=True, cache=cache, transport=fake_batch, progress=lambda s: None)
    assert len(submitted) == 1 and all(e["from_cache"] for e, _ in again)

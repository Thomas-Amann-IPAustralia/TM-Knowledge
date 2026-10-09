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
import yaml

from tm_knowledge.authored import store as authored_store
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


def test_a_quote_naming_only_one_end_or_a_template_is_refused():
    """Review D5: the sentence carrying a relationship names both ends, and a form
    template is not a statement."""
    text = TEXT + " The notice is filed <day month year> by the opponent. An opposition may then follow."
    one_end = _judgement(quote="An opposition may then follow.")
    template = _judgement(quote="The notice is filed <day month year> by the opponent.")
    for judgement, reason in ((one_end, "both concepts"), (template, "form template")):
        outcome = jobs._relate_accept(_ctx(text), ITEM, {"judgements": [judgement]}, ENTRY)
        assert not outcome.records and reason in outcome.refused[0]


def test_same_concept_is_reported_for_a_person_not_written():
    outcome = jobs._relate_accept(_ctx(TEXT), ITEM, {"judgements": [_judgement(relation="same_concept")]}, ENTRY)
    assert not outcome.records and "same concept" in outcome.notes[0]


def test_is_kind_of_becomes_skos_broader_with_the_narrower_concept_as_subject():
    outcome = jobs._relate_accept(_ctx(TEXT), ITEM, {"judgements": [
        _judgement(relation="is_kind_of", direction="neighbour_to_anchor", modality="none")]}, ENTRY)
    (record,) = outcome.records["relationships"]
    assert (record["subject"], record["predicate"], record["object"]) == ("GC-0002", "broader", "GC-0001")
    assert record["modality"] is None and record["tier"] == 2


def test_a_pair_already_answered_is_never_asked_again_even_when_the_answer_was_none():
    import json

    def answered(item, status, *neighbours):
        text = json.dumps({"judgements": [{"neighbour": n, "relation": "none"} for n in neighbours]})
        return {"job": "relate", "status": status, "item": item, "output_text": text}

    judged = jobs.judged_pairs([answered("GC-0001", "completed", "GC-0002", "GC-0003"),
                                answered("GC-0004", "failed", "GC-0005"),
                                {**answered("GC-0006", "completed", "GC-0007"), "job": "define"}])
    assert judged == {frozenset({"GC-0001", "GC-0002"}), frozenset({"GC-0001", "GC-0003"})}


# ----------------------------------------------------------------- links


def test_labels_match_whole_words_only():
    concepts = {"GC-0001": links_module.Concept("GC-0001", "mark", ("mark",), "signed"),
                "GC-0002": links_module.Concept("GC-0002", "Registrar", ("Registrar",), "signed")}
    patterns = links_module._patterns(concepts, skip=frozenset())
    found = links_module.find_mentions("The Registrar considered marketplace evidence.", patterns)
    assert set(found) == {"GC-0002"}


def test_the_longest_label_wins_its_span():
    """Review C8: a Deputy Registrar mention is not also a Registrar mention — but a
    later 'Registrar' on its own still is."""
    concepts = {"GC-0046": links_module.Concept("GC-0046", "Registrar", ("Registrar",), "signed"),
                "GC-0159": links_module.Concept("GC-0159", "Deputy Registrar", ("Deputy Registrar",), "authored")}
    patterns = links_module._patterns(concepts, skip=frozenset())
    assert set(links_module.find_mentions("The Deputy Registrar decided.", patterns)) == {"GC-0159"}
    found = links_module.find_mentions("The Deputy Registrar acts for the Registrar.", patterns)
    assert set(found) == {"GC-0159", "GC-0046"}
    assert found["GC-0046"][0] == len("The Deputy Registrar acts for the ")


def test_a_not_label_vetoes_its_own_concept_only():
    """Review E2: 'holder' inside 'copyright holder' is not the holder of an
    international registration, which says so in its not-labels."""
    concepts = {"GC-0132": links_module.Concept("GC-0132", "holder of an international registration",
                                                ("holder of an international registration", "holder"),
                                                "authored", not_labels=("copyright holder",))}
    patterns = links_module._patterns(concepts, skip=frozenset())
    vetoes = links_module._vetoes(concepts)
    assert links_module.find_mentions("Consent of the copyright holder.", patterns, vetoes) == {}
    assert set(links_module.find_mentions("The holder must respond.", patterns, vetoes)) == {"GC-0132"}


def test_apostrophes_match_either_way():
    concepts = {"GC-0127": links_module.Concept("GC-0127", "Registrar's decision", ("Registrar's decision",),
                                                "authored")}
    patterns = links_module._patterns(concepts, skip=frozenset())
    assert set(links_module.find_mentions("Appeal from the Registrar’s decision.", patterns)) == {"GC-0127"}


def test_a_label_on_the_too_general_list_is_skipped_for_its_concept_only():
    """Review E1: the label stays on the record; recognition does not use it."""
    concepts = {"GC-0021": links_module.Concept("GC-0021", "geographical qualifier",
                                                ("geographical qualifier", "made in"), "signed"),
                "GC-0999": links_module.Concept("GC-0999", "made in", ("made in",), "authored")}
    patterns = links_module._patterns(concepts, skip=frozenset({("GC-0021", "made in")}))
    assert set(links_module.find_mentions("Goods made in Australia.", patterns)) == {"GC-0999"}


def test_the_committed_too_general_list_names_real_labels():
    from tm_knowledge.authored import corrections

    gold = corrections.served_gold()
    held = {str(r["id"]): r for r in gold["gold_concept"]}
    held.update({e.record_id: e.record for e in authored_store.load().of("gold_concept")})
    for concept, label in links_module.too_general():
        record = held[concept]
        labels = [record["pref_label"], *(record.get("alt_labels") or ())]
        assert label in {x.lower() for x in labels}, (concept, label)
        assert label != str(record["pref_label"]).lower(), "a concept's own name is never too general"


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


class _FakeBatches:
    """Submit, status and collect, with the batch finishing on the second poll."""

    def __init__(self):
        self.submitted: list[list[dict]] = []
        self.polls = 0

    def submit(self, lines):
        self.submitted.append(lines)
        return f"batch_{len(self.submitted)}"

    def status(self, batch_id):
        self.polls += 1
        return {"id": batch_id, "status": "completed" if self.polls > 1 else "in_progress",
                "request_counts": {"total": 2, "completed": 2}}

    def collect(self, batch):
        lines = self.submitted[int(batch["id"].split("_")[1]) - 1]
        return {line["custom_id"]: {"custom_id": line["custom_id"], "response": {"status_code": 200, "body": {
            "model": "gpt-6.1-sol", "status": "completed",
            "usage": {"input_tokens": 1000, "output_tokens": 100},
            "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"answer": "ok"}'}]}]}}}
            for line in lines}


RQ = dict(job="t", prompt_version="t-v1", instructions="Be brief.", schema=SCHEMA, max_output_tokens=1000,
          model="gpt-6.1-sol", effort="medium")


def test_a_batch_answers_each_request_and_caches_it_as_one_call(tmp_path):
    cache = client.Cache(tmp_path / "cache")
    api = _FakeBatches()
    requests = [dict(RQ, item="a", input_text="One?"), dict(RQ, item="b", input_text="Two?")]
    results = client.batch_respond(requests, confirm=True, cache=cache, api=api, poll=0, progress=lambda s: None)
    assert [e["service_tier"] for e, _ in results] == ["batch", "batch"]
    assert results[0][0]["cost_usd"] == pytest.approx((1000 * 1.00 + 100 * 5.00) / 1_000_000)
    again = client.batch_respond(requests, confirm=True, cache=cache, api=api, poll=0, progress=lambda s: None)
    assert len(api.submitted) == 1 and all(e["from_cache"] for e, _ in again)


def test_a_request_in_an_open_batch_is_waited_for_never_sent_twice(tmp_path):
    cache = client.Cache(tmp_path / "cache")
    api = _FakeBatches()
    requests = [dict(RQ, item="a", input_text="One?")]
    client.batch_respond(requests, confirm=True, cache=cache, api=api, wait=False, progress=lambda s: None)
    assert client._in_flight(cache) > 0  # the open batch counts against the cap
    client.batch_respond(requests, confirm=True, cache=cache, api=api, poll=0, progress=lambda s: None)
    assert len(api.submitted) == 1
    assert client._in_flight(cache) == 0 and client.Cache(tmp_path / "cache").spent_usd() > 0


# ---------------------------------------------------------------------------
# Gemini — the D5 edge audit's second model, through its Batch API only
# ---------------------------------------------------------------------------


class _FakeGemini:
    """A Gemini batch that finishes on the second poll and echoes each key."""

    def __init__(self, text='{"answer": "ok"}'):
        self.submitted: list[tuple[str, list]] = []
        self.polls = 0
        self.text = text

    def submit(self, model, entries):
        self.submitted.append((model, entries))
        return f"batches/{len(self.submitted)}"

    def status(self, name):
        self.polls += 1
        done = self.polls > 1
        status = {"name": name, "metadata": {"state": "JOB_STATE_SUCCEEDED" if done else "JOB_STATE_RUNNING"}}
        if done:
            _, entries = self.submitted[int(name.split("/")[1]) - 1]
            status["response"] = {"inlinedResponses": {"inlinedResponses": [
                {"metadata": {"key": key}, "response": {
                    "modelVersion": "gemini-3.1-pro-preview",
                    "candidates": [{"finishReason": "STOP", "content": {"parts": [
                        {"text": "thinking out loud", "thought": True}, {"text": self.text}]}}],
                    "usageMetadata": {"promptTokenCount": 2000, "candidatesTokenCount": 100,
                                      "thoughtsTokenCount": 900}}}
                for key, _ in entries]}}
        return status

    state = staticmethod(client.GeminiBatchAPI.state)
    collect = client.GeminiBatchAPI.collect


GRQ = dict(RQ, model="gemini-3.1-pro-preview", effort="high")


def test_a_gemini_request_carries_the_schema_and_the_thinking_level():
    body = client._gemini_body(dict(GRQ, item="a", input_text="One?"))
    assert body["generationConfig"]["responseJsonSchema"] == SCHEMA
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    assert body["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "HIGH"}
    assert body["systemInstruction"]["parts"][0]["text"] == "Be brief."


def test_gemini_runs_through_its_batch_and_bills_thinking_as_output(tmp_path):
    cache = client.Cache(tmp_path / "cache")
    gemini = _FakeGemini()
    requests = [dict(GRQ, item="a", input_text="One?"), dict(GRQ, item="b", input_text="Two?")]
    results = client.batch_respond(requests, confirm=True, cache=cache, gemini_api=gemini, poll=0,
                                   progress=lambda s: None)
    entry = results[0][0]
    assert entry["status"] == "completed" and entry["output_text"] == '{"answer": "ok"}'
    assert entry["model_reported"] == "gemini-3.1-pro-preview" and entry["provider"] == "gemini"
    assert entry["cost_usd"] == pytest.approx((2000 * 1.00 + 1000 * 6.00) / 1_000_000)
    assert gemini.submitted[0][0] == "gemini-3.1-pro-preview"
    again = client.batch_respond(requests, confirm=True, cache=cache, gemini_api=gemini, poll=0,
                                 progress=lambda s: None)
    assert len(gemini.submitted) == 1 and all(e["from_cache"] for e, _ in again)


def test_a_gemini_model_is_never_called_outside_its_batch(tmp_path):
    with pytest.raises(RuntimeError, match="Batch API only"):
        client.respond(job="t", prompt_version="t-v1", item="a", instructions="x", input_text="y",
                       schema=SCHEMA, max_output_tokens=10, model="gemini-3.1-pro-preview",
                       confirm=True, cache=client.Cache(tmp_path))


def test_the_inline_responses_are_found_wherever_the_status_puts_them():
    item = {"response": {"candidates": []}}
    for status in ({"response": {"inlinedResponses": [item]}},
                   {"dest": {"inlinedResponses": {"inlinedResponses": [item]}}},
                   {"metadata": {"output": {"inlinedResponses": {"inlinedResponses": [item]}}}}):
        assert client.GeminiBatchAPI().collect(status, ["k"]) == {"k": item}


def test_the_audit_keeps_a_verdict_and_checks_the_corrected_reading():
    from tm_knowledge.bulk import jobs

    concepts = {
        "GC-0013": links_module.Concept("GC-0013", "condition of registration", ("condition of registration",), "signed"),
        "GC-0014": links_module.Concept("GC-0014", "endorsement", ("endorsement",), "signed"),
    }
    record = {"id": "GR-0110", "subject": "GC-0014", "predicate": "broader", "object": "GC-0013"}
    ctx = SimpleNamespace(
        links=links_module.Links(concepts=concepts, mentions={}, passages=1),
        authored=SimpleNamespace(of=lambda kind: (SimpleNamespace(record_id="GR-0110", record=record, sound=True),)),
    )
    item = jobs.Item("GR-0110..GR-0111", {"edges": ["GR-0110", "GR-0111"]})
    parsed = {"verdicts": [
        {"edge": "GR-0110", "verdict": "wrong", "problem": "predicate", "reason": "«r»",
         "corrected_subject": "GC-0014", "corrected_predicate": "related", "corrected_object": "GC-0013",
         "remove": False, "confidence": 0.8},
    ]}
    outcome = jobs._audit_accept(ctx, item, parsed, {"model_reported": "gemini-3.1-pro-preview"})
    (row,) = outcome.records["audit"]
    assert row["corrected"] == {"subject": "GC-0014", "predicate": "related", "object": "GC-0013"}
    assert row["model"] == "gemini-3.1-pro-preview" and row["remove"] is False
    assert outcome.refused == ["GR-0111: no verdict returned"]

    bad = {"verdicts": [dict(parsed["verdicts"][0], corrected_predicate="isSortOf")]}
    outcome = jobs._audit_accept(ctx, item, bad, {"model_reported": "m"})
    assert outcome.records["audit"][0]["corrected"] is None and outcome.notes


def test_the_audit_reads_every_shape_gemini_answered_in():
    """Q-83: a renamed field is read; a shape that leaves the verdict in doubt is not."""
    from tm_knowledge.bulk import jobs

    rows = jobs._audit_rows({"_list": [
        {"id": "[GR-0001]", "verdict": "Sound"},
        {"id": "GR-0002", "status": "wrong"},
        {"id": "GR-0003", "sound": False, "vague": False, "wrong": True},
        {"id": "GR-0004", "sound": True, "vague": False, "wrong": True},  # two flags: no verdict
    ]})
    assert [(r["edge"], r["verdict"]) for r in rows] == [
        ("GR-0001", "sound"), ("GR-0002", "wrong"), ("GR-0003", "wrong"), ("GR-0004", "")]

    keyed = jobs._audit_rows({
        "GR-0005": ["wrong", "wrong predicate", "GC-0001", "related", "GC-0002", False, "«why»"],
        "GR-0006": ["sound", "none"],  # not the instructions' seven fields: not read
    })
    assert keyed == [{"edge": "GR-0005", "verdict": "wrong", "problem": "wrong predicate",
                      "corrected_subject": "GC-0001", "corrected_predicate": "related",
                      "corrected_object": "GC-0002", "remove": False, "reason": "«why»"}]


def test_a_re_pooled_question_sends_only_its_ungraded_passages(tmp_path, monkeypatch):
    from tm_knowledge.bulk import cli, jobs

    monkeypatch.setattr(jobs, "BENCH_DIR", tmp_path)
    monkeypatch.setattr(cli, "POOLS_PATH", tmp_path / "pools.yaml")
    monkeypatch.setattr(cli, "_questions", lambda ctx: [
        {"key": key, "kind": "lookup", "question": key, "narrative": "«n»", "required": []} for key in ("Q1", "Q2")])
    (tmp_path / "pools.yaml").write_text(yaml.safe_dump(
        {"pools": [{"key": "Q1", "pool": ["a", "b", "c"]}, {"key": "Q2", "pool": ["d"]}]}), encoding="utf-8")
    (tmp_path / "judgements.yaml").write_text(yaml.safe_dump({"judgements": [
        {"need": "Q1", "grades": {"a": 2, "b": 0}, "model": "m", "date": "2026-10-07"},
        {"need": "Q2", "grades": {"d": 1}, "model": "m", "date": "2026-10-07"}]}), encoding="utf-8")

    items = cli._measurement_items("judge", SimpleNamespace())
    assert [(i.key, i.payload["pool"]) for i in items] == [("Q1", ["c"])]

    jobs._write_judgements({"judgements": [
        {"need": "Q1", "grades": {"c": 3, "a": 0}, "model": "m2", "date": "2026-10-09"}]})
    row = yaml.safe_load((tmp_path / "judgements.yaml").read_text(encoding="utf-8"))["judgements"][0]
    assert row["grades"] == {"a": 2, "b": 0, "c": 3}  # a grade once given stands
    assert row["later"] == [{"date": "2026-10-09", "model": "m2", "refs": ["c"]}]

"""The vocabulary against itself — shared names (A5), pairs kept apart (A6), and
"kind of" beside "not the same as" (D4). The owner approved all three on 2026-10-09
(ADR-0125)."""

from __future__ import annotations

from types import SimpleNamespace

import yaml

from tm_knowledge.authored import store as authored_store
from tm_knowledge.bulk import jobs
from tm_knowledge.bulk import links as links_module
from tm_knowledge.ontology import hygiene
from tm_knowledge.stage0 import goldset, harness


def _concept(cid, label, *, alt=(), not_labels=(), origin="authored"):
    return links_module.Concept(cid, label, (label, *alt), origin, not_labels=tuple(not_labels))


# ---------------------------------------------------------------------- fold


def test_fold_meets_the_names_a_byte_comparison_missed():
    """The old check compared preferred labels letter for letter (review A5)."""
    assert hygiene.fold("Endorsements") == hygiene.fold("endorsement")
    assert hygiene.fold("the Registrar’s delegate") == hygiene.fold("Registrar's delegate")
    assert hygiene.fold("non-use") == hygiene.fold("non use")
    assert hygiene.fold("Goods and Services") == hygiene.fold("goods and service")
    assert hygiene.fold("process") == "process" and hygiene.fold("analysis") == "analysis"


def test_fold_does_not_merge_different_names():
    assert hygiene.fold("Registrar") != hygiene.fold("Registrar of Trade Marks")
    assert hygiene.fold("sign") != hygiene.fold("trade mark")


# ---------------------------------------------------------------------- A5


def test_a_name_two_concepts_share_is_reported_once_with_both_holders():
    concepts = {
        "GC-0001": _concept("GC-0001", "endorsement", origin="signed"),
        "GC-0002": _concept("GC-0002", "suggested endorsement", alt=("Endorsements",)),
        "GC-0003": _concept("GC-0003", "disclaimer"),
    }
    (clash,) = hygiene.label_clashes(concepts)
    assert clash.concepts == ("GC-0001", "GC-0002")
    assert "GC-0001 (signed)" in clash.describe()


def test_the_served_vocabulary_shares_no_name():
    """After the A1–A4 merges and corrections nothing in the served view shares a
    name. A new record that does is reported by the harness as a note."""
    assert hygiene.label_clashes(links_module.concepts()) == ()


def test_the_expert_pack_check_compares_alternative_labels_too():
    from tm_knowledge.stage0 import expertpack

    signed = [{"id": "GC-0001", "pref_label": "Registrar", "alt_labels": ["the Registrar's delegate"]}]
    authored_records = [{"id": "GC-0100", "pref_label": "delegate", "alt_labels": ["Registrar’s delegates"]}]

    class _Gold(dict):
        pass

    gold = _Gold(gold_concept=signed)
    authored = SimpleNamespace(
        entries=(), of=lambda kind: tuple(
            SimpleNamespace(record=r, envelope={}) for r in (authored_records if kind == "gold_concept" else ())
        ),
    )
    (found,) = expertpack.duplicate_labels(gold, authored)
    assert (found.signed_id, found.authored_id) == ("GC-0001", "GC-0100")


# ---------------------------------------------------------------------- A6


def test_the_rejected_merge_is_kept_apart():
    """Implied endorsement is an inference consumers draw; an endorsement is wording
    on a registration (ruling A6)."""
    assert frozenset({"GC-0028", "GC-0014"}) in hygiene.kept_apart()
    decisions = {row["decision"] for row in hygiene.merge_candidates()}
    assert decisions == {"merged", "kept_apart"}


def test_merging_a_kept_apart_pair_is_a_defect(tmp_path):
    (tmp_path / hygiene.MERGE_CANDIDATES_FILE).write_text(yaml.safe_dump({"candidates": [
        {"pair": ["GC-0028", "GC-0014"], "decision": "kept_apart"}]}), encoding="utf-8")
    (tmp_path / authored_store.RETIRED_IDS_FILE).write_text(yaml.safe_dump([
        {"id": "GC-0028", "record_type": "gold_concept", "retired_on": "2026-10-09",
         "reason": "«merged»", "replaced_by": "GC-0014", "ruling": "«x»"}]), encoding="utf-8")
    findings = list(harness._vocabulary(authored_store.load(tmp_path), goldset.load(tmp_path / "none")))
    assert any(f.check == "kept-apart" and f.severity is harness.Severity.DEFECT for f in findings)


def test_the_relate_job_reports_a_repeated_suggestion_as_already_ruled():
    concepts = {
        "GC-0028": _concept("GC-0028", "implied endorsement", origin="signed"),
        "GC-0014": _concept("GC-0014", "endorsement", origin="signed"),
    }
    ctx = SimpleNamespace(links=links_module.Links(concepts=concepts, mentions={}, passages=1))
    item = jobs.Item("GC-0028", {"anchor": "GC-0028", "neighbours": [{"id": "GC-0014", "refs": ["TMM/x"]}]})
    outcome = jobs._relate_accept(ctx, item, {"judgements": [{"neighbour": "GC-0014", "relation": "same_concept"}]}, {})
    assert "kept apart" in outcome.notes[0] and not outcome.records


# ---------------------------------------------------------------------- D4

SIGN = _concept("GC-0073", "sign", not_labels=("trade mark",))
MARK = _concept("GC-0072", "trade mark", not_labels=("sign",))
CONDITION = _concept("GC-0013", "condition of registration", not_labels=("endorsement",), origin="signed")
ENDORSEMENT = _concept("GC-0014", "endorsement", not_labels=("condition of registration",), origin="signed")


def _broader(narrower, broader, rid="GR-9999"):
    return {"id": rid, "subject": narrower, "predicate": "broader", "object": broader}


def test_a_kind_of_link_beside_a_not_label_is_found_from_either_side():
    concepts = {c.id: c for c in (CONDITION, ENDORSEMENT)}
    (clash,) = hygiene.kind_of_clashes(concepts, [_broader("GC-0014", "GC-0013")])
    assert {cid for cid, _, _ in clash.said} == {"GC-0013", "GC-0014"} and not clash.affirmed


def test_a_written_affirmation_lets_a_hierarchy_stand_beside_a_near_miss():
    """Section 17: a trade mark is a sign, and not every sign is a trade mark — which
    is what the two not-labels say. A narrower idea is never the same idea."""
    concepts = {c.id: c for c in (SIGN, MARK)}
    affirmed = {("GC-0072", "GC-0073"): {"why": "s 17"}}
    (clash,) = hygiene.kind_of_clashes(concepts, [_broader("GC-0072", "GC-0073")], affirmed)
    assert clash.affirmed


def test_the_relate_job_refuses_an_unaffirmed_kind_of_link():
    text = "agree to an appropriate endorsement as a condition of registration"
    chunk = SimpleNamespace(text=text, content_hash="sha256:" + "a" * 64)
    corpus = SimpleNamespace(chunks={"TMM/Part1/1#1": chunk}, pages={}, resolve_provision=lambda ref: None)
    concepts = {c.id: c for c in (CONDITION, ENDORSEMENT)}
    ctx = SimpleNamespace(corpus=corpus, links=links_module.Links(concepts=concepts, mentions={}, passages=1))
    item = jobs.Item("GC-0014", {"anchor": "GC-0014", "neighbours": [{"id": "GC-0013", "refs": ["TMM/Part1/1#1"]}]})
    judgement = {"neighbour": "GC-0013", "relation": "is_kind_of", "direction": "anchor_to_neighbour",
                 "passage_ref": "TMM/Part1/1#1", "quote": text, "modality": None, "basis": "corpus_explicit",
                 "confidence": 0.9, "reasoning": "«r»", "alternative": "«a»", "expert_should_check": "«c»"}
    outcome = jobs._relate_accept(ctx, item, {"judgements": [judgement]}, {"model_reported": "m"})
    assert not outcome.records and "not the same concept" in outcome.refused[0]


def test_every_kind_of_clash_in_the_repository_is_affirmed_or_gone():
    """The harness fails an unaffirmed one; this says the same about the live store."""
    authored = authored_store.load()
    findings = [f for f in harness._vocabulary(authored, goldset.load()) if f.severity is harness.Severity.DEFECT]
    assert findings == []
    rows = hygiene.affirmations()
    assert rows and all(row.get("why") and row.get("link") for row in rows.values())


# ---------------------------------------------------------------------- F6


def test_nothing_ranks_or_filters_by_confidence():
    """Review F6, ADR-0125: every author rates itself on its own scale — the bulk
    model at 0.84–0.99 even where it could not identify a referent, an agent session
    at 0.5–0.9 — so no code sorts, thresholds or filters on `confidence`. A score is
    shown beside its author and nowhere else. The one comparison allowed is the
    bounds check that refuses a score outside [0, 1]."""
    import re

    from tm_knowledge.config import REPO_ROOT

    ranking = re.compile(r"(sort|ORDER BY|threshold|filter\()", re.I)
    comparing = re.compile(r"confidence\W{0,4}\s*[<>]|[<>]=?\s*[\w.\[\]\"'()]*confidence")
    allowed = ("0.0 <= self.confidence <= 1.0",)
    offenders = []
    for path in [*(REPO_ROOT / "src").rglob("*.py"), *(REPO_ROOT / "site" / "js").glob("*.js"),
                 *(REPO_ROOT / "queries").rglob("*.rq")]:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "confidence" not in line or any(ok in line for ok in allowed):
                continue
            if ranking.search(line) or comparing.search(line):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}")
    assert offenders == []


# ---------------------------------------------------------------------- D5 apply


def _audit_ctx(tmp_path, records):
    """An authored store on disk holding `records`, and a context over it."""
    from tm_knowledge.bulk import jobs

    env = {"review_status": "unreviewed", "authored_by": "gpt-6.1-sol", "authored_date": "2026-10-07",
           "authoring_basis": "corpus_explicit", "confidence": 0.9, "reasoning": "«first»",
           "evidence": [{"ref": "TMM/Part1/1#1", "span": [0, 10], "content_hash": "sha256:" + "a" * 64,
                         "quote": "«a quote»"}],
           "alternatives_considered": [], "expert_should_check": None}
    rows = [{**r, "source_ref": "TMM/Part1/1#1", "span": [0, 10], "source_content_hash": "sha256:" + "a" * 64,
             "tier": 3, "modality": None, "approved_by": None, "approved_date": None, "authored": env}
            for r in records]
    (tmp_path / "relationships.yaml").write_text(
        "# header\n" + yaml.dump(rows, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (tmp_path / authored_store.RETIRED_IDS_FILE).write_text("[]\n", encoding="utf-8")
    concepts = {
        "GC-0013": _concept("GC-0013", "condition of registration", origin="signed"),
        "GC-0014": _concept("GC-0014", "endorsement", origin="signed"),
        "GC-0168": _concept("GC-0168", "section 43 ground for rejection"),
        "GC-0006": _concept("GC-0006", "ground for rejection", origin="signed"),
    }
    store = authored_store.load(tmp_path)
    return SimpleNamespace(links=links_module.Links(concepts=concepts, mentions={}, passages=1),
                           authored=store, gold={"gold_relationship": ()}), jobs


def test_a_wrong_edge_is_re_read_when_its_correction_passes_and_withdrawn_when_not(tmp_path):
    from tm_knowledge.bulk import audit

    text = "A section 43 ground for rejection may be overcome by an endorsement."
    ctx, _ = _audit_ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0014", "predicate": "qualifies", "object": "GC-0168",
         "supporting_text": text},
        {"id": "GR-0002", "subject": "GC-0014", "predicate": "related", "object": "GC-0013",
         "supporting_text": "An endorsement is entered."},
    ])
    verdicts = [
        {"edge": "GR-0001", "judged": {"subject": "GC-0014", "predicate": "qualifies", "object": "GC-0168"},
         "verdict": "wrong", "problem": "direction", "reason": "«overcome»", "remove": False, "confidence": 0.9,
         "corrected": {"subject": "GC-0168", "predicate": "isOvercomeBy", "object": "GC-0014"},
         "model": "gemini-3.1-pro-preview"},
        # names a concept the sentence does not: refused, so withdrawn
        {"edge": "GR-0002", "judged": {"subject": "GC-0014", "predicate": "related", "object": "GC-0013"},
         "verdict": "wrong", "problem": "object", "reason": "«no»", "remove": False, "confidence": 0.7,
         "corrected": {"subject": "GC-0014", "predicate": "related", "object": "GC-0168"},
         "model": "gemini-3.1-pro-preview"},
        {"edge": "GR-0003", "verdict": "wrong", "remove": True, "model": "m"},  # no longer held
    ]
    actions = {a.edge: a for a in audit.plan(ctx, verdicts)}
    assert actions["GR-0001"].kind == "reread"
    assert actions["GR-0002"].kind == "withdraw" and "does not name both" in actions["GR-0002"].why
    assert actions["GR-0003"].kind == "skip"

    done = audit.apply(list(actions.values()), root=tmp_path)
    assert done == {"reread": 1, "withdrawn": 1}
    reread = authored_store.load(tmp_path).of("gold_relationship")
    (only,) = [e for e in reread if e.record_id == "GR-0001"]
    assert (only.record["subject"], only.record["predicate"], only.record["object"]) == \
        ("GC-0168", "isOvercomeBy", "GC-0014")
    assert only.envelope["authored_by"] == "gemini-3.1-pro-preview"
    assert "gpt-6.1-sol" in only.envelope["alternatives_considered"][0]
    assert only.record["approved_by"] is None and only.envelope["review_status"] == "unreviewed"
    ledger = yaml.safe_load((tmp_path / authored_store.RETIRED_IDS_FILE).read_text(encoding="utf-8"))
    assert [row["id"] for row in ledger] == ["GR-0002"]


def test_a_verdict_on_a_record_that_has_since_changed_is_not_applied(tmp_path):
    from tm_knowledge.bulk import audit

    ctx, _ = _audit_ctx(tmp_path, [{"id": "GR-0001", "subject": "GC-0014", "predicate": "related",
                                   "object": "GC-0013", "supporting_text": "x"}])
    verdict = {"edge": "GR-0001", "judged": {"subject": "GC-0014", "predicate": "broader", "object": "GC-0013"},
               "verdict": "wrong", "remove": True, "model": "m"}
    (action,) = audit.plan(ctx, [verdict])
    assert action.kind == "skip" and "changed" in action.why


def _wrong(edge, judged, corrected=None, remove=False):
    return {"edge": edge, "judged": dict(zip(("subject", "predicate", "object"), judged)), "verdict": "wrong",
            "problem": "predicate", "reason": "«why»", "remove": remove, "confidence": None,
            "corrected": dict(zip(("subject", "predicate", "object"), corrected)) if corrected else None,
            "model": "gemini-3.1-pro-preview"}


def test_a_correction_may_keep_a_concept_both_models_read_the_sentence_as_about(tmp_path):
    from tm_knowledge.bulk import audit

    text = "It is entered as a note on the Register."  # names neither concept
    ctx, _ = _audit_ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0014", "predicate": "qualifies", "object": "GC-0013", "supporting_text": text},
        {"id": "GR-0002", "subject": "GC-0014", "predicate": "appliesTo", "object": "GC-0013", "supporting_text": text},
    ])
    actions = {a.edge: a for a in audit.plan(ctx, [
        _wrong("GR-0001", ("GC-0014", "qualifies", "GC-0013"), ("GC-0014", "related", "GC-0013")),
        # brings in a concept the sentence does not name: still refused
        _wrong("GR-0002", ("GC-0014", "appliesTo", "GC-0013"), ("GC-0168", "related", "GC-0013")),
    ])}
    assert actions["GR-0001"].kind == "reread"
    assert actions["GR-0002"].kind == "withdraw" and "does not name both" in actions["GR-0002"].why
    record = actions["GR-0001"].record
    assert record["authored"]["confidence"] is None  # the second model rated nothing; no default stands in


def test_a_correction_that_only_widens_an_end_leaves_the_record_standing(tmp_path):
    from tm_knowledge.bulk import audit

    ctx, _ = _audit_ctx(tmp_path, [
        {"id": "GR-0001", "subject": "GC-0014", "predicate": "mayGiveRiseTo", "object": "GC-0168",
         "supporting_text": "An endorsement may give rise to a ground for rejection."},
        {"id": "GR-0004", "subject": "GC-0168", "predicate": "broader", "object": "GC-0006", "supporting_text": "x"},
    ])
    (action,) = audit.plan(ctx, [_wrong("GR-0001", ("GC-0014", "mayGiveRiseTo", "GC-0168"),
                                        ("GC-0014", "mayGiveRiseTo", "GC-0006"))])
    assert action.kind == "keep" and "GC-0168 to GC-0006" in action.why
    assert audit.apply([action], root=tmp_path) == {"reread": 0, "withdrawn": 0}


def test_the_audit_never_changes_a_record_serving_for_a_signed_one(tmp_path, monkeypatch):
    from tm_knowledge.bulk import audit

    ctx, _ = _audit_ctx(tmp_path, [{"id": "GR-0001", "subject": "GC-0014", "predicate": "related",
                                   "object": "GC-0013", "supporting_text": "x"}])
    monkeypatch.setattr(audit.corrections_module, "load",
                        lambda root: SimpleNamespace(replacements=lambda: {"GR-0018": "GR-0001"}))
    (action,) = audit.plan(ctx, [_wrong("GR-0001", ("GC-0014", "related", "GC-0013"), remove=True)])
    assert action.kind == "keep" and "signed GR-0018" in action.why


def test_a_withdrawal_chain_is_history_not_a_dangling_pointer(tmp_path):
    (tmp_path / authored_store.RETIRED_IDS_FILE).write_text(yaml.dump([
        {"id": "GR-0146", "record_type": "gold_relationship", "retired_on": "2026-10-08",
         "reason": "«merged»", "replaced_by": "GR-0145"},
        {"id": "GR-0145", "record_type": "gold_relationship", "retired_on": "2026-10-09",
         "reason": "«judged wrong by a second model»"},
        {"id": "GR-0147", "record_type": "gold_relationship", "retired_on": "2026-10-09",
         "reason": "«merged»", "replaced_by": "GR-9998"},
    ], sort_keys=False), encoding="utf-8")
    authored = authored_store.load(tmp_path)
    gold = SimpleNamespace(retired_ids={}, all_records=lambda: iter(()))
    found = [f.subject for f in harness._authored_corrections(authored, gold) if f.check == "authored-ids"]
    assert found == ["GR-0147"]

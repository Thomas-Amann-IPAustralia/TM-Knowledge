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

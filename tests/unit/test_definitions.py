"""Definitions — machine-written, unreviewed, a record of their own (F06, ADR-0137).

The owner lifted the deferral on definitions (CHAT-0078). These tests pin what makes
writing them safe: a definition never enters a signed record or the approved graph;
it quotes what it rests on; it says whether its words are the Act's, written from a
provision, or the Manual's; and "application" says which sense it means.
"""

from __future__ import annotations

import copy

import pytest
import yaml

from tm_knowledge.authored import definitions
from tm_knowledge.stage0 import goldset

ENVELOPE = {
    "review_status": "unreviewed", "authored_by": "test-agent", "authored_date": "2026-10-17",
    "authoring_basis": "corpus_explicit", "confidence": 0.5, "reasoning": "A fixture.",
    "alternatives_considered": [], "expert_should_check": None,
    "evidence": [{"ref": "TMA1995/s17~1", "span": [0, 10],
                  "content_hash": "sha256:" + "0" * 64, "quote": "A trade ma"}],
}


def _row(**fields):
    row = {"id": "GD-0001", "concept": "GC-0001", "text": "A meaning.", "basis": "statutory_provision",
           "source_ref": "TMA1995/s17~1", "approved_by": None, "approved_date": None}
    row.update(fields)
    row["authored"] = copy.deepcopy(ENVELOPE)
    return row


def _load(tmp_path, rows):
    root = tmp_path / "authored"
    root.mkdir(parents=True)
    (root / "definitions.yaml").write_text(yaml.safe_dump(rows, sort_keys=False), encoding="utf-8")
    return definitions.load(root)


def _refused(found):
    return {entry.id: " ".join(str(e) for e in entry.errors) for entry in found.refused}


def test_the_committed_definitions_are_all_sound_and_unreviewed():
    found = definitions.load()
    assert len(found.sound) >= 100, "authored/definitions.yaml is expected to hold S038's definitions"
    assert found.refused == (), _refused(found)
    for entry in found.sound:
        assert entry.record["approved_by"] is None and entry.record["approved_date"] is None
        assert entry.envelope["review_status"] == "unreviewed"
        assert entry.envelope["evidence"], entry.id


def test_a_statutory_definition_is_the_instruments_words_verbatim():
    """CHAT-0045: the Act's own definitions preferred, and when used, quoted, not
    paraphrased. The text is exactly the quoted units, notes aside."""
    for entry in definitions.load().sound:
        if entry.record["basis"] != "statutory_definition":
            continue
        quotes = [e["quote"] for e in entry.envelope["evidence"] if not e["quote"].startswith("Note:")]
        assert entry.record["text"] == " ".join(" ".join(quotes).split()), entry.id


def test_every_sense_of_application_says_which_it_is():
    """The 8 October review's B2: the senses of "application" were typed
    inconsistently. Scope notes first (F06); each definition of a concept named
    for an application says which sense it means."""
    found = definitions.load().by_concept()
    for concept in ("GC-0043", "GC-0051", "GC-0098", "GC-0111", "GC-0116", "GC-0124", "GC-0131",
                    "GC-0142", "GC-0155"):
        note = found[concept].record.get("scope_note") or ""
        assert "application" in note.lower(), concept


@pytest.mark.parametrize(("fields", "says"), [
    ({"concept": "GC-9999"}, "no concept in either store"),
    ({"basis": "manual"}, "no evidence is from TMM/"),
    ({"source_ref": "TMA1995/s41"}, "not among the evidence"),
])
def test_a_definition_that_does_not_hold_together_is_refused(tmp_path, fields, says):
    found = _load(tmp_path, [_row(**fields)])
    assert says in _refused(found)["GD-0001"]


def test_an_approval_written_into_a_definition_is_refused(tmp_path):
    """`approved_by` means a person signed it; no agent writes it (CLAUDE.md §2)."""
    found = _load(tmp_path, [_row(approved_by="claude", approved_date="2026-10-17")])
    assert "GD-0001" in _refused(found)


def test_one_concept_one_definition_per_scope(tmp_path):
    """ADR-0146 relaxed ADR-0137's "one per concept" to one per concept per scope: a
    second unscoped definition is still refused, and so is a second in the same scope."""
    found = _load(tmp_path, [_row(), _row(id="GD-0002")])
    assert "a second definition of GC-0001" in _refused(found)["GD-0002"]
    assert [entry.id for entry in found.sound] == ["GD-0001"]
    found = _load(tmp_path / "again", [_row(scope="TMR1995/Part17"), _row(id="GD-0002", scope="TMR1995/Part17")])
    assert "same scope" in _refused(found)["GD-0002"]


def test_scoped_definitions_stand_together_and_an_unscoped_one_beside_them_is_refused(tmp_path):
    """An unscoped definition beside scoped ones would read as the general meaning and
    win by default, which is the choice the disambiguation rule leaves to the context."""
    found = _load(tmp_path, [_row(scope="TMR1995/Part17"), _row(id="GD-0002", scope="period:2026-09-19/"),
                             _row(id="GD-0003")])
    assert [entry.id for entry in found.sound] == ["GD-0001", "GD-0002"]
    assert "names no scope" in _refused(found)["GD-0003"]


def test_a_concept_with_several_definitions_is_unresolved_until_its_context_names_one(tmp_path):
    found = _load(tmp_path, [_row(scope="TMR1995/Part17"), _row(id="GD-0002", scope="period:2026-09-19/")])
    assert "GC-0001" not in found.by_concept(), "by_concept holds only what needs no context to pick"
    unresolved = found.resolve("GC-0001")
    assert unresolved.state == "unresolved" and unresolved.chosen is None
    assert [d.id for d in unresolved.candidates] == ["GD-0001", "GD-0002"]
    chosen = found.resolve("GC-0001", scope="period:2026-09-19/")
    assert (chosen.state, chosen.chosen.id) == ("scoped", "GD-0002")
    assert found.resolve("GC-0001", scope="sense:another").state == "unresolved"
    assert found.resolve("GC-0002").state == "none"
    single = _load(tmp_path / "one", [_row()])
    assert (single.resolve("GC-0001").state, single.resolve("GC-0001", scope="x").chosen.id) == ("single", "GD-0001")


def test_the_committed_definitions_need_no_context_to_pick():
    """Today every concept has one definition; a scoped pair would change that and this
    test, on purpose, so the session that writes one also says how it is chosen."""
    found = definitions.load()
    assert len(found.by_concept()) == len(found.sound)


def test_a_definition_never_enters_a_signed_record_or_the_approved_graph():
    from rdflib import Dataset
    from rdflib.namespace import RDF, SKOS

    from tm_knowledge.config import REPO_ROOT
    from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, AUTHORED_GRAPH, TMK

    for record in goldset.load()["gold_concept"]:
        assert "definition" not in record, record["id"]
    dataset = Dataset()
    dataset.parse(REPO_ROOT / "graph" / "dataset.nq", format="nquads")
    approved, authored = dataset.graph(APPROVED_GRAPH), dataset.graph(AUTHORED_GRAPH)
    assert next(iter(approved.triples((None, SKOS.definition, None))), None) is None
    assert next(iter(approved.subjects(RDF.type, TMK.Definition)), None) is None
    defined = set(authored.subjects(RDF.type, TMK.Definition))
    assert len(defined) == len(definitions.load().sound)
    for node in defined:
        assert str(authored.value(node, TMK.reviewStatus)) == "unreviewed"
        assert authored.value(node, TMK.defines) is not None


def test_a_definition_in_the_approved_graph_is_a_placement_defect():
    from rdflib import Dataset, URIRef
    from rdflib.namespace import RDF

    from tm_knowledge.ontology import validate
    from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, TMK

    dataset = Dataset()
    dataset.graph(APPROVED_GRAPH).add((URIRef("https://example.org/GD-1"), RDF.type, TMK.Definition))
    assert [f.severity for f in validate.placement(dataset)] == ["defect"]


def test_the_id_allocator_counts_definitions():
    from tm_knowledge.bulk import jobs

    highest = max(int(entry.id.split("-")[1]) for entry in definitions.load().entries)
    assert jobs.next_number("GD") == highest + 1


# --- R02's triage (S041): a definition that may omit a qualification its source states ---


def _triage(definition, units=(), chunks=None, kinds=None):
    from types import SimpleNamespace

    entry = definitions.Definition(record=definition["record"], envelope=definition["envelope"])
    corpus = SimpleNamespace(units=set(units), chunks=chunks or {})
    return definitions.triage(definitions.Definitions(entries=(entry,)), corpus, kinds or {})


def _item(ref, span, quote="q"):
    return {"ref": ref, "span": list(span), "content_hash": "sha256:" + "0" * 64, "quote": quote}


def test_triage_a_flags_a_subsection_quoted_in_part():
    """GD-0128's case: s 11(1)(a), (b) and (d) quoted, (c) not."""
    units = ["TMA1995/s11(1)", "TMA1995/s11(1)(a)", "TMA1995/s11(1)(b)", "TMA1995/s11(1)(c)",
             "TMA1995/s11(1)(c)(i)", "TMA1995/s11(1)(d)", "TMA1995/s11(1)(d)~1"]
    quoted = ["TMA1995/s11(1)", "TMA1995/s11(1)(a)", "TMA1995/s11(1)(b)", "TMA1995/s11(1)(d)"]
    row = {"record": {"id": "GD-9001", "concept": "GC-0155", "text": "pending"},
           "envelope": {"evidence": [_item(r, (0, 1)) for r in quoted]}}
    flags = _triage(row, units)
    assert [(f.check, "s11(1)(c)" in f.message) for f in flags] == [("a", True)]
    row["envelope"]["evidence"].append(_item("TMA1995/s11(1)(c)", (0, 1)))
    assert not _triage(row, units), "every paragraph quoted: no flag (the ~ continuation is not a paragraph)"


def test_triage_b_flags_a_qualifier_just_after_a_manual_quote_unless_it_is_quoted_too():
    """GD-0050's case: 'Section 41 does not apply to certification trade marks.'"""
    from types import SimpleNamespace

    text = "A mark must be rejected if not capable of distinguishing. Section 41 does not apply to certification marks."
    chunks = {"TMM/Part22/1#1": SimpleNamespace(text=text)}
    first = _item("TMM/Part22/1#1", (0, 57))
    row = {"record": {"id": "GD-9002", "concept": "GC-0058", "text": "Whether a mark can distinguish."},
           "envelope": {"evidence": [first]}}
    assert [f.check for f in _triage(row, chunks=chunks)] == ["b"]
    at = text.index("Section 41")
    row["envelope"]["evidence"].append(_item("TMM/Part22/1#1", (at, len(text))))
    assert not _triage(row, chunks=chunks)


def test_triage_c_flags_an_obligation_in_a_non_ground_definition_only():
    row = {"record": {"id": "GD-9003", "concept": "GC-0058", "text": "A mark that cannot must be rejected."},
           "envelope": {"evidence": []}}
    assert [f.check for f in _triage(row)] == ["c"]
    assert not _triage(row, kinds={"GC-0058": "ground_of_refusal"}), "for a ground, rejection is the meaning"


@pytest.mark.snapshot
def test_the_four_named_omissions_are_repaired():
    """GD-0050, GD-0084, GD-0128 (the triage's real flags) and GD-0146 (which no check over
    its quote could see), re-read in S041."""
    from tm_knowledge.config import UPSTREAM_DIR
    from tm_knowledge.upstream.loader import load_corpus

    if not UPSTREAM_DIR.exists():
        pytest.skip("no snapshot fetched; run tmk-fetch-upstream")
    found = definitions.load()
    by_id = {d.id: d for d in found.sound}
    kinds = {}
    flags = {(f.id, f.check) for f in definitions.triage(found, load_corpus(), kinds)}
    for rid, check in (("GD-0050", "b"), ("GD-0084", "b"), ("GD-0128", "a")):
        assert (rid, check) not in flags, rid
    assert "certification" in by_id["GD-0050"].record["scope_note"]
    assert "reg 21.28" in by_id["GD-0084"].record["scope_note"]
    assert "confirmed on appeal" in by_id["GD-0128"].record["text"]
    adverse = by_id["GD-0146"].record
    assert "reg 4.8" in adverse["text"] and "unless acceptance of the application is deferred" in adverse["scope_note"]

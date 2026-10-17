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
    root.mkdir()
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


def test_one_concept_one_definition(tmp_path):
    found = _load(tmp_path, [_row(), _row(id="GD-0002")])
    assert "a second definition of GC-0001" in _refused(found)["GD-0002"]
    assert [entry.id for entry in found.sound] == ["GD-0001"]


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

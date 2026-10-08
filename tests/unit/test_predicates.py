"""The relation dictionary (review D1, C3; ADR-0123) and the decision kinds (C7)."""

from __future__ import annotations

import pytest

from tm_knowledge.authored import store as authored_store
from tm_knowledge.ontology import decisions, relations
from tm_knowledge.ontology.predicates import AUTHORITY_PREDICATES, PREDICATES, SKOS_PREDICATES
from tm_knowledge.stage0 import goldset


def test_every_predicate_is_defined_and_reads_one_way():
    for name, entry in PREDICATES.items():
        assert entry.name == name
        assert entry.definition and entry.example and entry.counter_example
        assert entry.reading.count("<") == 2, f"{name}: a reading names its subject and its object"
        assert entry.admitted in {"signed", "ADR-0113", "owner-2026-10-08"}
        assert entry.authority in {None, "law", "practice"}


def test_every_predicate_any_record_uses_is_in_the_dictionary():
    used = {str(r["predicate"]) for r in goldset.load()["gold_relationship"]}
    used |= {str(r["predicate"]) for r in authored_store.load()["gold_relationship"]}
    assert used <= set(PREDICATES), sorted(used - set(PREDICATES))


def test_the_signed_predicates_are_all_admitted_as_signed():
    used = {str(r["predicate"]) for r in goldset.load()["gold_relationship"]}
    for name in used:
        assert PREDICATES[name].admitted == "signed", name


def test_authority_predicates_say_whether_they_are_law_or_practice():
    """Rule 5 on an edge: delegation and appeal are law, consulting is practice."""
    for name in AUTHORITY_PREDICATES:
        if name in ("constrainsRole", "actsAs"):
            continue
        assert PREDICATES[name].authority in {"law", "practice"}, name
    assert PREDICATES["holdsDelegationFrom"].authority == "law"
    assert PREDICATES["consults"].authority == "practice"


def test_the_dictionary_never_lists_skos_as_its_own_term():
    rendered = relations.render(relations.collect())
    for name in SKOS_PREDICATES:
        assert f"tmk:{name} a owl:ObjectProperty" not in rendered
    for name in set(PREDICATES) - set(SKOS_PREDICATES):
        assert f"tmk:{name} a owl:ObjectProperty" in rendered


@pytest.mark.parametrize("case_id, kind, jurisdiction", [
    ("CASE/2011/ATMO/63", "administrative", "AU"),
    ("CASE/1980/AOJP/50/4200", "administrative", "AU"),
    ("CASE/2013/APO/57", "administrative", "AU"),
    ("CASE/1960/HCA/47", "judicial", "AU"),
    ("CASE/2010/FCAFC/117", "judicial", "AU"),
    ("CASE/2002/EWHC/2709", "judicial", "UK"),
    ("CASE/1983/IPR/1/416", "unclassified", "AU"),
    ("CASE/1969/RPC/600", "unclassified", "UK"),
    ("CASE/1904/ROC/21/617", "unclassified", None),
])
def test_a_decision_is_classified_by_its_series_and_nothing_else(case_id, kind, jurisdiction):
    found = decisions.classify(case_id)
    assert (found.kind, found.jurisdiction) == (kind, jurisdiction)


def test_the_registrars_delegate_is_never_a_court():
    for series, (kind, _, level) in decisions.SERIES.items():
        if level and "delegate" in level:
            assert kind == "administrative", series

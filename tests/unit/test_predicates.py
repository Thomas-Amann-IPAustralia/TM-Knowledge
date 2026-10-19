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
        assert entry.admitted in {"signed", "ADR-0113", "owner-2026-10-08", "owner-2026-10-09"}
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


# ------------------------------------------------- the top level connects (ADR-0131)


def test_is_related_to_is_retired():
    from tm_knowledge.ontology import predicates

    assert "related" not in PREDICATES and "related" in predicates.RETIRED
    assert "related" not in SKOS_PREDICATES
    with pytest.raises(KeyError, match="retired"):
        predicates.get("related")


def test_every_kind_is_in_a_family_and_every_predicate_names_real_kinds():
    from tm_knowledge.ontology.predicates import END_KINDS, FAMILY
    from tm_knowledge.stage0 import typing as typing_module

    kinds = {key for key, _ in typing_module.GROUPS} - {"none_of_these"}
    assert kinds == set(FAMILY)
    assert set(FAMILY.values()) == {"reasoning", "examined", "process"}
    for name, entry in PREDICATES.items():
        assert entry.subjects and set(entry.subjects) <= set(END_KINDS), name
        assert entry.objects and set(entry.objects) <= set(END_KINDS), name


def test_an_edge_must_join_kinds_its_predicate_joins():
    from tm_knowledge.ontology.predicates import off_schema

    kinds = {"GC-1": "process_role", "GC-2": "procedural_step", "GC-3": "instrument_or_record",
             "GC-4": "sign_content", "GC-5": "ground_of_refusal", "GC-6": "none_of_these"}
    assert off_schema("GC-1", "performs", "GC-2", kinds) is None
    assert "subject" in off_schema("GC-2", "performs", "GC-1", kinds)
    assert off_schema("GC-4", "mayGiveRiseTo", "GC-5", kinds) is None
    assert "object" in off_schema("GC-3", "requiresConsentOf", "GC-2", kinds)
    assert "across families" in off_schema("GC-4", "broader", "GC-3", kinds)
    assert off_schema("GC-6", "performs", "GC-2", kinds) is None  # untyped: the typing gate's to report
    assert off_schema("TMA1995/s43", "requiresElement", "GC-5", kinds) is None


def test_the_schema_joins_all_three_families():
    from tm_knowledge.ontology.predicates import FAMILY, schema

    crossings = {(FAMILY[s], FAMILY[o]) for s, _, o in schema() if FAMILY[s] != FAMILY[o]}
    for a, b in (("examined", "reasoning"), ("reasoning", "process"), ("process", "examined")):
        assert (a, b) in crossings or (b, a) in crossings, (a, b)


def test_every_record_that_serves_fits_the_kinds_of_its_predicate():
    """Signed and machine-written alike. The signed records that do not fit are exactly the
    ones a correction already replaces as recorded the wrong way round (ADR-0122) — the kinds
    find, unaided, the defects a person ruled on."""
    from tm_knowledge.authored import corrections
    from tm_knowledge.ontology.predicates import off_schema

    authored = authored_store.load()
    kinds = {str(e.record["concept"]): str(e.record["type"]) for e in authored.of("concept_type") if e.sound}

    def misfits(records):
        return {r["id"] for r in records if off_schema(str(r["subject"]), str(r["predicate"]), str(r["object"]), kinds)}

    serving = list(corrections.served_gold()["gold_relationship"])
    serving += [e.record for e in authored.of("gold_relationship") if e.sound]
    assert misfits(serving) == set()
    replaced = set(corrections.load(authored=authored).replacements())
    assert misfits(goldset.load()["gold_relationship"]) <= replaced


def test_no_concept_is_left_in_none_of_these_or_unconnected():
    from collections import defaultdict

    from tm_knowledge.authored import corrections

    authored = authored_store.load()
    assert all(e.record["type"] != "none_of_these" for e in authored.of("concept_type") if e.sound)
    served = corrections.served_gold()
    ids = {r["id"] for r in served["gold_concept"]} | {e.record["id"] for e in authored.of("gold_concept") if e.sound}
    adjacent = defaultdict(set)
    for r in list(served["gold_relationship"]) + [e.record for e in authored.of("gold_relationship") if e.sound]:
        if r["subject"] in ids and r["object"] in ids:
            adjacent[r["subject"]].add(r["object"])
            adjacent[r["object"]].add(r["subject"])
    seen, stack = set(), [min(ids)]
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(adjacent[node] - seen)
    assert seen == ids, sorted(ids - seen)


def test_the_families_are_classes_and_every_kind_sits_in_one():
    rdflib = pytest.importorskip("rdflib")
    from tm_knowledge.config import REPO_ROOT
    from tm_knowledge.ontology.predicates import FAMILY, KIND_CLASS

    graph = rdflib.Graph().parse(REPO_ROOT / "ontology" / "draft" / "legal-concepts.ttl")
    tmk = rdflib.Namespace("https://data.ipaustralia.gov.au/tmk/ns/")
    families = {tmk.LegalQuestion, tmk.ExaminedMatter, tmk.ProcessElement}
    for kind in FAMILY:
        cls = tmk[KIND_CLASS[kind].split(":", 1)[1]]
        parents = set(graph.objects(cls, rdflib.RDFS.subClassOf)) & families
        assert len(parents) == 1, kind


def test_relations_ttl_says_which_kinds_each_predicate_joins():
    text = relations.RELATIONS_PATH.read_text(encoding="utf-8")
    block = text.split("tmk:performs a owl:ObjectProperty", 1)[1].split("\n\n", 1)[0]
    assert "tmk:expectedSubjectKind tmk:ProcessRole" in block
    assert "tmk:expectedObjectKind tmk:ProceduralStep" in block
    assert "tmk:related a owl:ObjectProperty" not in text


def test_blocking_a_step_and_stopping_its_clock_are_two_predicates():
    """`prevents` meant both, and its records used both: GR-0394, a ground for rejection
    that blocks acceptance, and GR-0534, a deferment that stops the time that would make
    an application lapse (the review response, F13). A reader cannot tell which a
    `prevents` edge asserts, and the two have opposite consequences for the step."""
    assert "time" not in PREDICATES["prevents"].definition
    clock = PREDICATES["suspendsTimeFor"]
    assert "time" in clock.definition and clock.objects == ("procedural_step",)
    assert "suspendsTimeFor" in PREDICATES["prevents"].counter_example


def test_precedes_says_the_first_step_must_happen_first():
    """An ordering of steps, not a sequence the sentence happens to mention: all its
    sound records mean that the second cannot happen until the first has (F13)."""
    entry = PREDICATES["precedes"]
    assert entry.reading == "<step> must come before <step>"
    assert "GR-0167" in entry.counter_example


def test_an_exception_is_its_own_predicate_and_not_insufficiency():
    """F15: a case a ground does not reach, against a thing not enough on its own."""
    exception = PREDICATES["isAnExceptionTo"]
    assert exception.objects == ("ground_of_refusal", "legal_test")
    assert exception.reading == "<case> is an exception to <ground or test>"
    assert "isAnExceptionTo" in PREDICATES["doesNotGiveRiseTo"].counter_example


def test_evidence_may_show_and_never_establishes():
    """`establishes` read "<evidence> establishes <what it shows>" while its own example
    said "may show", and its three records each overstated their sentence (the review
    response, F18). Whether evidence establishes anything is the decision maker's
    evaluative judgement (PU-0001); the relation says what evidence can go to."""
    entry = PREDICATES["mayShow"]
    assert entry.reading == "<evidence> may show <what it shows>"
    assert "evaluative" in entry.definition
    assert entry.subjects == ("instrument_or_record",)


def test_establishes_is_retired_once_nothing_uses_it():
    from tm_knowledge.ontology.predicates import RETIRED

    assert "establishes" in RETIRED and "establishes" not in PREDICATES
    used = {str(r["predicate"]) for r in authored_store.load()["gold_relationship"]}
    assert "establishes" not in used


# --- R01: an exception edge only where the source excludes the case (S041) ----------
#
# ChatGPT's consolidated review asked for near misses with each replacement: a recently
# deceased person, a business identifier challenged on another ground, and evidence that
# prompts reconsideration without establishing acceptance. They are tested on the
# committed records, because the records are what a customer explanation would compose.


def _relationships():
    import yaml

    from tm_knowledge.config import REPO_ROOT

    rows = yaml.safe_load((REPO_ROOT / "authored" / "relationships.yaml").read_text(encoding="utf-8"))
    return {r["id"]: r for r in rows}


def test_a_deceased_person_is_not_an_exception_to_section_43():
    """Near miss 1: the recently deceased whose estate controls the name. GR-0700 is a
    factor with its hedge, and carries the 'However' sentence that reopens the ground."""
    record = _relationships()["GR-0700"]
    assert (record["subject"], record["predicate"], record["object"]) == ("GC-0027", "qualifies", "GC-0168")
    assert record["hedge"] == "Generally"
    quotes = " ".join(e["quote"] for e in record["authored"]["evidence"])
    assert "However, a relevant connotation may arise" in quotes and "the more recently they died" in quotes


def test_a_business_identifier_bears_on_section_43_and_no_other_ground():
    """Near miss 2: a business identifier challenged on another ground. GR-0699 names the
    section 43 ground, not every ground for rejection, and states a tendency."""
    record = _relationships()["GR-0699"]
    assert (record["subject"], record["predicate"], record["object"]) == ("GC-0020", "qualifies", "GC-0168")
    assert record["hedge"] == "rarely"
    assert record["applies_when"] == "Where business identifiers are included in a trade mark"


def test_reconsideration_is_not_the_evidence_for_an_exception():
    """Near miss 3: information that prompts reconsideration does not establish
    acceptance. GR-0702 rests on the conditional sentence, scoped to phonewords."""
    record = _relationships()["GR-0702"]
    assert record["predicate"] == "isAnExceptionTo"
    assert record["supporting_text"].startswith("A section 43 ground for rejection will apply if")
    assert "phoneword" in record["applies_when"]


def test_no_exception_edge_carries_a_hedge_and_no_condition_holds_one():
    rows = _relationships().values()
    hedges = ("usually", "rarely", "generally", "not likely")
    for record in rows:
        if record["predicate"] == "isAnExceptionTo":
            assert not record.get("hedge"), f"{record['id']}: a hedged sentence states a tendency, not an exclusion"
        when = str(record.get("applies_when") or "").casefold()
        assert when not in hedges, f"{record['id']}: applies_when holds a bare hedge"


def test_the_exception_example_is_a_sentence_that_excludes_a_case():
    from tm_knowledge.ontology.predicates import PREDICATES

    entry = PREDICATES["isAnExceptionTo"]
    assert "does not arise" in entry.example and "Generally" not in entry.example
    assert "qualifies" in entry.counter_example

"""The Stage 0 record schemas — P4's done-criteria.

Three things are checked here:

1. Every valid fixture validates, and every malformed fixture fails **for the
   stated reason** — the filename names the rule, and the test asserts the error
   mentions it. A schema that stops catching something fails here.
2. The templates and the schemas cannot drift: every field the schema requires
   appears in the template a human reads, and no template field is unknown to
   the schema.
3. The enum lists match `eval/STAGE-0-INPUT-GUIDE.md` §5 exactly.

And one thing is checked by its absence: no schema encodes a judgement. See
`test_no_schema_decides_a_legal_question`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0.schemas import (
    ID_PREFIXES,
    RECORD_TYPES,
    SCHEMA_DIR,
    enum_values,
    schema_properties,
    validate,
)

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "stage0"
TEMPLATES = REPO_ROOT / "eval" / "templates"

#: fixture filename stem -> record type.
FIXTURE_TYPES = {
    "competency-question": "competency_question",
    "gold-entity": "gold_entity",
    "gold-concept": "gold_concept",
    "gold-relationship": "gold_relationship",
    "gold-search-question": "gold_search_question",
    "gold-retrieval-question": "gold_retrieval_question",
    "reasoning-expectation": "reasoning_expectation",
    "prohibited-use": "prohibited_use",
}

#: The word each malformed fixture's failure must mention. Named per file, so a
#: fixture that starts failing for a *different* reason is a failure too.
EXPECTED_FAILURE = {
    "gold-entity--type-not-in-taxonomy": "LAW",
    "gold-entity--ref-the-corpus-cannot-hold": "TMR1995/s224",
    "gold-entity--iri-instead-of-ref": "https://",
    "gold-entity--missing-approval-fields": "approved_by",
    "gold-relationship--modality-outside-the-three": "probably",
    "gold-relationship--tier-outside-the-three": "4",
    "gold-concept--broader-is-not-a-concept-id": "broader",
    "gold-search-question--grade-outside-the-scale": "5",
    "prohibited-use--kind-outside-the-six": "bad_vibes",
    "prohibited-use--id-in-the-wrong-series": "CQ-002",
    "competency-question--unknown-field": "difficulty_rating",
    "competency-question--category-outside-the-six": "interpretation",
    "reasoning-expectation--inference-kind-invented": "evaluation",
}


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _record_type(path: Path) -> str:
    return FIXTURE_TYPES[path.stem.split("--")[0]]


# ---------------------------------------------------------------------------
# The schemas do what they say
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "path", sorted((FIXTURES / "valid").glob("*.yaml")), ids=lambda p: p.stem
)
def test_a_well_formed_record_validates(path):
    errors = validate(_load(path), _record_type(path))
    assert errors == [], "\n".join(str(error) for error in errors)


@pytest.mark.parametrize(
    "path", sorted((FIXTURES / "malformed").glob("*.yaml")), ids=lambda p: p.stem
)
def test_a_malformed_record_fails_for_the_stated_reason(path):
    errors = validate(_load(path), _record_type(path))
    assert errors, f"{path.name} was supposed to fail and did not"
    expected = EXPECTED_FAILURE[path.stem]
    joined = "\n".join(str(error) for error in errors)
    assert expected in joined, f"failed, but not about {expected!r}:\n{joined}"


def test_every_malformed_fixture_is_covered_by_a_stated_reason():
    stems = {path.stem for path in (FIXTURES / "malformed").glob("*.yaml")}
    assert stems == set(EXPECTED_FAILURE)


def test_all_eight_record_types_have_a_schema_and_a_fixture():
    assert set(RECORD_TYPES) == set(ID_PREFIXES)
    assert len(RECORD_TYPES) == 8
    fixtures = {_record_type(p) for p in (FIXTURES / "valid").glob("*.yaml")}
    assert fixtures == set(RECORD_TYPES)


# ---------------------------------------------------------------------------
# The templates and the schemas cannot drift
# ---------------------------------------------------------------------------

def _template_records() -> dict[str, dict]:
    gold = _load(TEMPLATES / "gold-record.template.yaml")
    return {
        "competency_question": _load(TEMPLATES / "competency-question.template.yaml"),
        "gold_entity": gold["entity"],
        "gold_concept": gold["concept"],
        "gold_relationship": gold["relationship"],
        "gold_search_question": gold["search_question"],
        "gold_retrieval_question": gold["retrieval_question"],
        "reasoning_expectation": _load(TEMPLATES / "reasoning-expectation.template.yaml"),
        "prohibited_use": _load(TEMPLATES / "prohibited-use.template.yaml"),
    }


@pytest.mark.parametrize("record_type", sorted(RECORD_TYPES))
def test_the_template_and_the_schema_describe_the_same_record(record_type):
    """The template is the human-readable face of the schema. If they drift, the
    expert fills in fields the validator will reject, or leaves out ones it
    requires — and finds out after doing the work."""
    template = _template_records()[record_type]
    properties = schema_properties(record_type)
    required = set(
        json.loads((SCHEMA_DIR / RECORD_TYPES[record_type]).read_text())["required"]
    )
    assert set(template) - properties == set(), "template field the schema rejects"
    assert required - set(template) == set(), "required field the template never shows"
    assert properties - set(template) == set(), "schema field the template never shows"


def test_every_template_id_uses_its_own_series():
    for record_type, template in _template_records().items():
        assert str(template["id"]).startswith(ID_PREFIXES[record_type] + "-")


# ---------------------------------------------------------------------------
# The enums match the guide
# ---------------------------------------------------------------------------

def test_enums_match_the_guide_text_exactly():
    """Transcribed from `eval/STAGE-0-INPUT-GUIDE.md` §5. If the guide changes,
    this fails and both move together — which is the only way the enum lists and
    the prose stay the same set."""
    assert enum_values("competency_question", "asked_by") == [
        "examiner", "applicant", "AI assistant", "maintainer", "other",
    ]
    assert enum_values("competency_question", "category") == [
        "retrieval", "search", "reasoning", "currency", "impact", "provenance",
    ]
    assert enum_values("gold_entity", "type") == [
        "LegalConcept", "LegislativeProvision", "JudicialDecision",
        "EvidenceCategory", "ManualInstruction", "Role", "Date", "Other",
    ]
    assert enum_values("gold_relationship", "modality") == ["must", "may", "should", None]
    assert enum_values("prohibited_use", "kind") == [
        "evaluative_conclusion", "authority_conflation", "unsupported_inference",
        "stale_source", "overreach", "ambiguity_collapse",
    ]
    assert enum_values("prohibited_use", "detectable_by") == ["test", "shacl", "eval", "human"]
    assert enum_values("reasoning_expectation", "tier") == [1, 2, 3, None]


def test_the_gold_entity_taxonomy_is_not_spacys():
    """Q-16: two vocabularies that share two spellings. `DATE` and `LAW` are
    OntoNotes labels and must never reach an entity type."""
    taxonomy = set(enum_values("gold_entity", "type"))
    assert {"DATE", "LAW", "ORG", "GPE", "NORP"} & taxonomy == set()
    assert "Date" in taxonomy and "LegislativeProvision" in taxonomy


# ---------------------------------------------------------------------------
# What the schemas must NOT do
# ---------------------------------------------------------------------------

def test_no_schema_decides_a_legal_question():
    """Shape only (CLAUDE.md rule 1). Two specific guards:

    The relationship `predicate` is not enumerated — the dictionary is
    expert-owned and does not exist, and listing plausible predicates would be
    an agent authoring it. And every judgement field is nullable, so an agent
    transcribing an expert's words can leave unsaid things unsaid (P8).
    """
    relationship = json.loads((SCHEMA_DIR / "gold-relationship.schema.json").read_text())
    assert "enum" not in relationship["properties"]["predicate"]

    with_nulls = {
        "modality": ("gold_relationship", None),
        "tier": ("gold_relationship", None),
    }
    for field, (record_type, allowed) in with_nulls.items():
        assert allowed in enum_values(record_type, field)


def test_a_judgement_field_may_be_null_but_its_key_may_not_be_missing():
    """The gap has to be visible. Null is a reportable gap (P10); an absent key
    is a record nobody can tell is incomplete."""
    record = _load(FIXTURES / "valid" / "gold-relationship.yaml")
    assert record["modality"] is None
    assert validate(record, "gold_relationship") == []

    del record["modality"]
    errors = validate(record, "gold_relationship")
    assert any("modality" in str(error) for error in errors)

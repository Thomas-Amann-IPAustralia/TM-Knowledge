"""Every shape has a fixture that violates it, and the fixture is the proof.

`shapes/README.md`: *an untested shape that never matches anything is worse than
no shape, because it reads as coverage.* These tests are that requirement. Each
one loads a fixture built to break exactly one constraint and asserts the named
shape reports it — and, where the fixture carries a conforming twin, asserts the
shape leaves that alone.

The conforming twin matters as much as the violation. A shape that fires on
everything passes a fires-test and is useless.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology import validate

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "shapes"


def check(name: str) -> validate.ValidationReport:
    """Run the whole shape set over one fixture, as the gate would.

    The TBox goes in with the fixture. `sh:targetClass` follows
    `rdfs:subClassOf`, so without the class hierarchy a fixture node typed
    `tmk:Chunk` is invisible to a shape targeting `tmk:Passage` — the fixture
    would pass, and it would pass for a reason that has nothing to do with the
    constraint. The real gate loads it the same way.
    """
    from pyshacl import validate as pyshacl_validate

    from tm_knowledge.ontology.tbox import load as load_tbox

    data = Graph().parse(FIXTURES / name, format="turtle")
    for triple in load_tbox():
        data.add(triple)
    shapes = validate.load_shapes()
    _conforms, results, _text = pyshacl_validate(
        data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True
    )
    return validate.ValidationReport(
        conforms=False, findings=validate._findings(results, shapes)
    )


def fired(report: validate.ValidationReport, fragment: str) -> list[validate.Finding]:
    return [f for f in report.findings if fragment.lower() in f.shape.lower()]


def nodes(findings: list[validate.Finding]) -> set[str]:
    return {f.node.rsplit("/", 1)[-1] for f in findings}


def test_pu_0004_authority_conflation_fires():
    """The headline prohibition, as a constraint that blocks publication.

    PU-0004 is `detectable_by: shacl` and this is what that means in practice:
    a proposition whose words are in a practice passage and which is attributed
    to the Act is refused, while the same words honestly attributed pass.
    """
    report = check("pu-0004-authority-conflation.ttl")
    findings = fired(report, "attributed to the Act")
    assert nodes(findings) == {"bad-claim"}, (
        "The shape must fire on the claim attributed to the Act and must leave "
        "the identically-worded, honestly-attributed claim alone."
    )
    assert findings[0].severity == "defect"
    assert "PU-0004" in findings[0].message


def test_disjoint_authority_fires():
    report = check("disjoint-authority.ttl")
    assert nodes(fired(report, "Nothing is both practice and law")) == {"confused"}


@pytest.mark.parametrize(
    "path",
    ["goldRecord", "sourcePassage", "extractionMethod", "reviewStatus", "approvedBy", "approvedDate"],
)
def test_unsigned_assertion_fires_on_every_missing_field(path):
    """One violation per missing field, not one for the record as a whole.

    A shape reporting 'this assertion is incomplete' tells a reviewer to go
    looking. Six named violations tell them what to fix.
    """
    report = check("unsigned-assertion.ttl")
    findings = [
        f for f in fired(report, "provenance block") if f.path == path
    ]
    assert findings, f"nothing fired for the missing {path}"
    assert nodes(findings) == {"unsigned"}, "the signed twin must conform"


def test_broader_cycle_fires():
    report = check("broader-cycle.ttl")
    assert nodes(fired(report, "No cycles")) == {"a", "b"}


def test_not_label_that_is_also_a_label_fires():
    report = check("broader-cycle.ttl")
    findings = fired(report, "not-label is not also a label")
    assert nodes(findings) == {"c"}
    assert findings[0].severity == "defect"


def test_unexplained_inference_fires():
    report = check("unexplained-inference.ttl")
    findings = fired(report, "names its rule")
    assert "mute" in nodes(findings)
    assert {f.path for f in findings} >= {"producedByRule", "derivedFrom", "reviewStatus"}


def test_bounded_reasoning_fires_on_a_derived_evidentiary_proposition():
    """A rule may not derive an evaluative conclusion. queries/README.md draws
    this line and this is where it is enforced rather than described."""
    report = check("unexplained-inference.ttl")
    assert nodes(fired(report, "Reasoning stays inside its bounds")) == {"overreaching"}


def test_undated_supersession_fires():
    report = check("undated-supersession.ttl")
    assert nodes(fired(report, "status date")) == {"retired"}


def test_the_real_graph_has_no_defects():
    """The gate over the actual content. Notes are expected and are the
    not-label pairs; a defect or a gap is not."""
    report = validate.run()
    assert report.by_severity("defect") == [], "\n".join(
        str(f) for f in report.by_severity("defect")
    )
    assert report.by_severity("gap") == []
    assert report.exit_code == 0

"""Run the SHACL shapes over the built graph. The gate before anything publishes.

`shapes/README.md` states the rule this module has to hold to: **a failing shape
is a finding, not a nuisance.** Nothing here loosens a shape to make a run pass,
and nothing auto-repairs a legally significant record. A violation is reported
with the node and the shape's own message, and the exit code says so.

Three severities, matching `tmk-harness` so the two read alike (ADR-0030):
Violation is a defect and fails, Warning is a gap, Info is a note.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pyshacl import validate as pyshacl_validate
from rdflib import Dataset, Graph, URIRef
from rdflib.namespace import RDF, SH

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, SOURCE_GRAPH, bind_all

__all__ = ["SHAPES_DIR", "Finding", "ValidationReport", "load_shapes", "run"]

SHAPES_DIR = REPO_ROOT / "shapes"

#: Fixed list, in the order `shapes/README.md` gives them. A shape file appearing
#: on disk and being picked up by a glob is how an unreviewed constraint joins
#: the gate — or, worse, how a deleted one stops being noticed.
SHAPE_FILES: tuple[str, ...] = (
    "provenance.ttl",
    "authority.ttl",
    "vocabulary.ttl",
    "temporal.ttl",
    "inference.ttl",
)

_SEVERITY = {
    SH.Violation: "defect",
    SH.Warning: "gap",
    SH.Info: "note",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    shape: str
    node: str
    message: str
    path: str | None = None
    #: The offending value, where the constraint identified one. Part of the
    #: identity: two not-labels on one concept are two findings, and a report
    #: that collapsed them would understate the work.
    value: str | None = None

    def __str__(self) -> str:
        where = f"{self.node}" + (f" [{self.path}]" if self.path else "")
        if self.value:
            where += f" = {self.value}"
        return f"{self.severity}: {self.shape} — {where}\n    {self.message}"


@dataclass
class ValidationReport:
    conforms: bool
    findings: list[Finding] = field(default_factory=list)

    def by_severity(self, severity: str) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == severity]

    @property
    def exit_code(self) -> int:
        """0 clean · 1 defects · 3 gaps only. The harness's codes (ADR-0030)."""
        if self.by_severity("defect"):
            return 1
        if self.by_severity("gap"):
            return 3
        return 0

    def lines(self) -> list[str]:
        out = []
        for severity, heading in (
            ("defect", "DEFECTS — the graph does not publish"),
            ("gap", "GAPS — publishable, and incomplete"),
            ("note", "NOTES — worth an eye"),
        ):
            found = self.by_severity(severity)
            if found:
                out.append(f"\n{heading} ({len(found)})")
                out.extend(f"  {finding}" for finding in found)
        counts = ", ".join(
            f"{len(self.by_severity(severity))} {severity}(s)"
            for severity in ("defect", "gap", "note")
        )
        out.append(f"\n{counts}")
        return out


def load_shapes(directory: Path | None = None) -> Graph:
    directory = directory or SHAPES_DIR
    graph = Graph()
    for name in SHAPE_FILES:
        path = directory / name
        if not path.exists():
            raise FileNotFoundError(
                f"shape file {name} is missing. SHAPE_FILES is a fixed list on purpose: "
                f"a gate that quietly loses a constraint is worse than no gate."
            )
        graph.parse(path, format="turtle")
    return bind_all(graph)


def _flatten(dataset: Dataset) -> Graph:
    """The graphs the shapes run over, as one graph.

    Source and approved together, because several constraints span them: a
    proposition's authority kind lives in the source graph and the proposition
    in the approved one, and a validator that saw only one would pass PU-0004
    by not being able to see it.
    """
    graph = bind_all(Graph())
    for name in (SOURCE_GRAPH, APPROVED_GRAPH):
        for triple in dataset.graph(name):
            graph.add(triple)
    for triple in dataset.default_graph:
        graph.add(triple)
    return graph


_RDFS_LABEL = URIRef("http://www.w3.org/2000/01/rdf-schema#label")


def _label_for(shapes: Graph, shape) -> str | None:
    """The human name of the shape that fired.

    A property-constraint violation names the *property shape* as its source,
    and a property shape is a blank node with no label — so a report built
    naively is a list of `n4ce10a23...b3`, which tells a reviewer nothing. This
    walks up the `sh:property` link to the node shape that has the name.
    """
    label = shapes.value(shape, _RDFS_LABEL)
    if label is not None:
        return str(label)
    for parent in shapes.subjects(SH.property, shape):
        label = shapes.value(parent, _RDFS_LABEL)
        if label is not None:
            return str(label)
    for parent in shapes.subjects(SH.sparql, shape):
        label = shapes.value(parent, _RDFS_LABEL)
        if label is not None:
            return str(label)
    return None


def _findings(results: Graph, shapes: Graph) -> list[Finding]:
    out = []
    for result in results.subjects(RDF.type, SH.ValidationResult):
        severity = results.value(result, SH.resultSeverity)
        shape = results.value(result, SH.sourceShape)
        node = results.value(result, SH.focusNode)
        message = results.value(result, SH.resultMessage)
        path = results.value(result, SH.resultPath)
        value = results.value(result, SH.value)
        label = _label_for(shapes, shape)
        out.append(
            Finding(
                severity=_SEVERITY.get(severity, "defect"),
                shape=str(label or shape),
                node=str(node),
                message=str(message).strip(),
                path=str(path).rsplit("/", 1)[-1] if path else None,
                value=str(value) if value is not None else None,
            )
        )
    # Deduplicated: pySHACL can report one result twice when a shape is reached
    # by two routes, and a doubled count reads as twice the work.
    unique = list(dict.fromkeys(out))
    return sorted(
        unique,
        key=lambda finding: (finding.severity, finding.shape, finding.node, finding.value or ""),
    )


def run(
    dataset: Dataset | None = None, shapes: Graph | None = None
) -> ValidationReport:
    if dataset is None:
        dataset, _ = build()
    shapes = shapes if shapes is not None else load_shapes()
    data = _flatten(dataset)

    conforms, results, _text = pyshacl_validate(
        data,
        shacl_graph=shapes,
        ont_graph=None,
        # The shapes are the check. Inference here would let a shape pass
        # because a reasoner supplied the triple the data was missing, which is
        # the opposite of a publication gate.
        inference="none",
        advanced=True,
        abort_on_first=False,
        meta_shacl=False,
        allow_warnings=True,
    )
    return ValidationReport(conforms=conforms, findings=_findings(results, shapes))

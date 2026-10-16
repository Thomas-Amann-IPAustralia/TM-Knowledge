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
from rdflib.namespace import RDF, SH, SKOS

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import (
    APPROVED_GRAPH,
    AUTHORED_GRAPH,
    INFERRED_GRAPH,
    SOURCE_GRAPH,
    TMK,
    bind_all,
)

__all__ = [
    "SHAPES_DIR", "PLACEMENT_SHAPE", "S27_SHAPE", "Finding", "ValidationReport",
    "load_shapes", "placement", "skos_integrity", "run",
]

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


#: The name a placement finding reports under, as a shape's label would.
PLACEMENT_SHAPE = "Each kind of record sits in its own named graph"

#: The kinds of record each named graph may hold, and the origin its nodes are
#: stamped with. The named graphs are the governance boundary (CLAUDE.md rule 4):
#: signed records in `approved`, machine-written ones and corrections in
#: `authored`, a rule's output in `inferred`, the corpus in `source`. A signed
#: concept with a machine-written type appears in both stores' graphs, which is
#: why this is about the record classes and the origin stamp, not the subjects.
_RECORD_CLASSES = (
    TMK.ApprovedAssertion, TMK.AuthoredAssertion, TMK.CandidateAssertion,
    TMK.InferredAssertion, TMK.Correction, TMK.ReasoningExpectation, TMK.EntityMention,
)
_PLACEMENT: dict = {
    SOURCE_GRAPH: ((), None),
    APPROVED_GRAPH: ((TMK.ApprovedAssertion, TMK.ReasoningExpectation, TMK.EntityMention), "approved"),
    AUTHORED_GRAPH: ((TMK.AuthoredAssertion, TMK.Correction, TMK.ReasoningExpectation, TMK.EntityMention), "authored"),
    INFERRED_GRAPH: ((TMK.InferredAssertion,), None),
}


def placement(dataset: Dataset) -> list[Finding]:
    """What flattening cannot see: a record in a named graph it may not sit in.

    Read before the union, because after it a machine-written assertion in the
    approved graph is indistinguishable from the same node in the authored one
    (the review response, F02). Every finding is a defect.
    """
    out = []
    for graph_name, (allowed, origin) in _PLACEMENT.items():
        graph = dataset.graph(graph_name)
        where = str(graph_name).rsplit("/", 1)[-1]
        for cls in _RECORD_CLASSES:
            if cls in allowed:
                continue
            for node in graph.subjects(RDF.type, cls):
                out.append(Finding(
                    severity="defect", shape=PLACEMENT_SHAPE, node=str(node), path="type",
                    value=str(cls).rsplit("/", 1)[-1],
                    message=f"A {str(cls).rsplit('/', 1)[-1]} in the {where} graph. Signed, "
                            f"machine-written and inferred records never share a named graph "
                            f"(CLAUDE.md rule 4).",
                ))
        for node, stamp in graph.subject_objects(TMK.origin):
            if str(stamp) != origin:
                out.append(Finding(
                    severity="defect", shape=PLACEMENT_SHAPE, node=str(node), path="origin",
                    value=str(stamp),
                    message=f"A node stamped origin \"{stamp}\" in the {where} graph. The stamp "
                            f"and the named graph must agree, or no later audit can tell the "
                            f"stores apart (ADR-0080).",
                ))
    return out


S27_SHAPE = "Related is not also broader (SKOS S27)"


def _parents(*graphs: Graph) -> dict:
    """child -> parents, from skos:broader and skos:narrower read as its inverse."""
    out: dict = {}
    for graph in graphs:
        for child, parent in graph.subject_objects(SKOS.broader):
            out.setdefault(child, set()).add(parent)
        for parent, child in graph.subject_objects(SKOS.narrower):
            out.setdefault(child, set()).add(parent)
    return out


def _ancestors(parents: dict, node) -> set:
    seen: set = set()
    stack = list(parents.get(node, ()))
    while stack:
        current = stack.pop()
        if current not in seen:
            seen.add(current)
            stack.extend(parents.get(current, ()))
    return seen


def skos_integrity(dataset: Dataset) -> list[Finding]:
    """SKOS S27: two concepts that are `skos:related` are not also joined by `broader`.

    Read per named graph, because the remedy depends on who wrote what. Where a
    machine wrote either statement it is a defect, fixed by re-reading the authored
    record. Where both are signed (GC-0017 and GC-0018 today) it is a note: a signed
    record is corrected outside its signature, on the owner's ruling (ADR-0122), and
    an agent may not make that call (the review response, F07).
    """
    approved, authored = dataset.graph(APPROVED_GRAPH), dataset.graph(AUTHORED_GRAPH)
    signed, both = _parents(approved), _parents(approved, authored)
    out, seen = [], set()
    for graph in (approved, authored):
        for one, other in graph.subject_objects(SKOS.related):
            pair = tuple(sorted((one, other)))
            if pair in seen:
                continue
            if other not in _ancestors(both, one) and one not in _ancestors(both, other):
                continue
            seen.add(pair)
            related_signed = (one, SKOS.related, other) in approved or (other, SKOS.related, one) in approved
            hierarchy_signed = other in _ancestors(signed, one) or one in _ancestors(signed, other)
            if related_signed and hierarchy_signed:
                out.append(Finding(
                    severity="note", shape=S27_SHAPE, node=str(pair[0]), value=str(pair[1]),
                    path="related",
                    message="Signed as related and signed as broader or narrower, which SKOS's "
                            "integrity condition S27 forbids. Both statements are signed, so the "
                            "fix is a correction on the owner's ruling (ADR-0122); reported, not "
                            "failed, until the owner decides.",
                ))
            else:
                out.append(Finding(
                    severity="defect", shape=S27_SHAPE, node=str(pair[0]), value=str(pair[1]),
                    path="related",
                    message="Related and also broader or narrower, which SKOS's integrity "
                            "condition S27 forbids, and a machine wrote at least one of the two "
                            "statements. Re-read the authored record: one idea is either a kind of "
                            "the other or associated with it, not both.",
                ))
    return out


def _flatten(dataset: Dataset) -> Graph:
    """The graphs the shapes run over, as one graph.

    All four named graphs and the default one together, because several
    constraints span them: a proposition's authority kind lives in the source graph and the
    proposition in the approved one, and a validator that saw only one would
    pass PU-0004 by not being able to see it.

    **The authored graph is validated on the same terms as the approved one**
    (ADR-0080, ADR-0082). It has to be: ADR-0082 removed the review gate on
    serving unreviewed content, which means these shapes are now the only thing
    standing between an authored record and a reader. An authored graph that
    published unchecked would be the Tier 3 gate removed and nothing put in its
    place.

    **The inferred graph is validated too.** Until S036 it was left out, so the
    shapes written for a rule's output, `BoundedReasoningShape` among them, never
    saw one (the review response, F02).

    Flattening loses the separation the named graphs carry, which is why every
    node stamps its own `tmk:origin`, why `tmk:OriginConsistencyShape` exists,
    and why `placement()` reads the dataset before it is flattened.
    """
    graph = bind_all(Graph())
    for name in (SOURCE_GRAPH, APPROVED_GRAPH, AUTHORED_GRAPH, INFERRED_GRAPH):
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
    own = [*placement(dataset), *skos_integrity(dataset)]
    return ValidationReport(
        conforms=conforms and not any(finding.severity == "defect" for finding in own),
        findings=sorted(
            [*_findings(results, shapes), *own],
            key=lambda finding: (finding.severity, finding.shape, finding.node, finding.value or ""),
        ),
    )

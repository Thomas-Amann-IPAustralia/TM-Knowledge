"""SHACL shapes — the constraints OWL was the wrong tool for.

`ontology.py` explains why no relation property carries `rdfs:domain` or
`rdfs:range`: in RDFS those are inference rules, so declaring a domain does not
check that the subject is the right kind of thing, it silently asserts that it
is. Over this graph that would manufacture claims nobody approved.

SHACL is the other half of that decision. A shape says the same thing and gets
the direction right: a node that breaks it is **reported**, not reclassified.
Everything here is a statement about the shape of an approved record, not about
trade marks law:

- an assertion without a name and a date against it is not approved knowledge
  (ADR-0039), whatever else it carries;
- an assertion without a supporting passage cannot be checked by a reader, which
  is the only thing that makes the graph auditable;
- a mention without a span is a claim that a phrase appears somewhere, which is
  not a claim anybody can verify;
- and nothing may be both a legislative provision and a Manual instruction. OWL
  disjointness already says so, but an OWL reasoner reports that by declaring
  the graph inconsistent, which tells you the file is broken without telling you
  where. The shape names the node.
"""

from __future__ import annotations

from tm_knowledge.graph.model import STANDARD_PREFIXES, project_prefixes, tmk
from tm_knowledge.graph.turtle import Document, IRI, Literal, PN, Triples
from tm_knowledge.refs import iri_for

__all__ = ["render", "SHAPES_FILE"]

SHAPES_FILE = "s43-shapes.ttl"


def _shape(name: str, base: str | None = None) -> IRI:
    return IRI(iri_for("tmk", f"shape/{name}", base=base))


def _property(
    triples: Triples,
    shape: IRI,
    path: PN,
    *,
    message: str,
    min_count: int | None = None,
    datatype: PN | None = None,
    node_kind: PN | None = None,
    severity: str = "sh:Violation",
) -> None:
    node = IRI(f"{shape.value}/{path.value.split(':')[-1]}")
    triples.add(shape, PN("sh:property"), node)
    triples.add(node, PN("sh:path"), path)
    triples.add(node, PN("sh:message"), Literal(message, language="en"))
    triples.add(node, PN("sh:severity"), PN(severity))
    if min_count is not None:
        triples.add(node, PN("sh:minCount"), Literal(min_count))
    if datatype is not None:
        triples.add(node, PN("sh:datatype"), datatype)
    if node_kind is not None:
        triples.add(node, PN("sh:nodeKind"), node_kind)


def _triples(base: str | None = None) -> Triples:
    triples = Triples()

    assertion = _shape("Assertion", base)
    triples.add(assertion, PN("a"), PN("sh:NodeShape"))
    triples.add(assertion, PN("sh:targetClass"), tmk("Assertion"))
    triples.add(
        assertion,
        PN("rdfs:comment"),
        Literal(
            "What makes a reified relationship approved knowledge rather than a "
            "candidate. Every one of these is a field a person filled in.",
            language="en",
        ),
    )
    _property(
        triples, assertion, tmk("approvedBy"), min_count=1,
        message="An assertion with no name against it is not approved knowledge (ADR-0039).",
    )
    _property(
        triples, assertion, tmk("approvedDate"), min_count=1,
        message="An approval with no date cannot be aged against a snapshot.",
    )
    _property(
        triples, assertion, tmk("goldRecord"), min_count=1,
        message="Every node must name the approved record it was built from.",
    )
    _property(
        triples, assertion, PN("prov:wasDerivedFrom"), min_count=1,
        message="An assertion with no source passage cannot be checked by a reader.",
    )
    _property(
        triples, assertion, tmk("supportingText"), min_count=1,
        message="An assertion with no supporting sentence is an opinion.",
    )
    _property(
        triples, assertion, tmk("hasModality"), min_count=1,
        severity="sh:Warning",
        message=(
            "No modality recorded. A warning and not a violation: five approved "
            "relationships have none because the sentence carries none, and "
            "filling that in would be inventing a strength nobody stated."
        ),
    )

    mention = _shape("Mention", base)
    triples.add(mention, PN("a"), PN("sh:NodeShape"))
    triples.add(mention, PN("sh:targetClass"), tmk("Mention"))
    triples.add(
        mention,
        PN("rdfs:comment"),
        Literal(
            "A mention is only useful if a reader can go and look at it. That "
            "means a passage, a span and the hash of the passage as it stood "
            "when it was approved.",
            language="en",
        ),
    )
    _property(
        triples, mention, tmk("mentionOf"), min_count=1,
        message="A mention with no passage is a claim about nowhere.",
    )
    _property(
        triples, mention, tmk("spanStart"), min_count=1, datatype=PN("xsd:integer"),
        message="A mention with no span cannot be verified against the passage.",
    )
    _property(
        triples, mention, tmk("spanEnd"), min_count=1, datatype=PN("xsd:integer"),
        message="A mention with no span cannot be verified against the passage.",
    )
    _property(
        triples, mention, tmk("sourceContentHash"), min_count=1,
        message=(
            "Without the hash the span cannot be told from a stale span, which "
            "is the failure that looks exactly like success."
        ),
    )

    concept = _shape("Concept", base)
    triples.add(concept, PN("a"), PN("sh:NodeShape"))
    triples.add(concept, PN("sh:targetClass"), PN("skos:Concept"))
    _property(
        triples, concept, PN("skos:prefLabel"), min_count=1,
        message="A concept with no preferred label cannot be searched for.",
    )
    _property(
        triples, concept, PN("skos:definition"), min_count=1,
        message="A concept with no defining passage rests on nothing.",
    )

    authority = _shape("AuthorityKept", base)
    triples.add(authority, PN("a"), PN("sh:NodeShape"))
    triples.add(authority, PN("sh:targetClass"), tmk("LegislativeProvision"))
    triples.add(
        authority,
        PN("rdfs:comment"),
        Literal(
            "CLAUDE.md rule 5, as a check rather than as a sentence in a "
            "document: the Manual states the Registrar's practice and does not "
            "bind the Registrar's discretion, so nothing may be both a "
            "provision of the Act and an instruction of the Manual. The OWL "
            "disjointness says the same, but an OWL reasoner reports it by "
            "calling the whole graph inconsistent. This names the node.",
            language="en",
        ),
    )
    not_shape = IRI(f"{authority.value}/notManual")
    triples.add(authority, PN("sh:property"), not_shape)
    triples.add(not_shape, PN("sh:path"), PN("rdf:type"))
    triples.add(not_shape, PN("sh:not"), IRI(f"{not_shape.value}/in"))
    triples.add(IRI(f"{not_shape.value}/in"), PN("sh:hasValue"), tmk("ManualInstruction"))
    triples.add(
        not_shape,
        PN("sh:message"),
        Literal(
            "This node is typed as both binding law and stated practice. One of "
            "the two is wrong and the distinction must survive into any answer.",
            language="en",
        ),
    )
    triples.add(not_shape, PN("sh:severity"), PN("sh:Violation"))

    return triples


def render(base: str | None = None) -> str:
    return Document(
        header=(
            "TM-Knowledge — SHACL shapes for the section 43 pilot",
            "",
            "Constraints that report rather than infer. See the module docstring",
            "in src/tm_knowledge/graph/shapes.py for why these are not OWL.",
            "",
            "GENERATED by tm_knowledge.graph.shapes. Rebuild with tmk-graph.",
        ),
        prefixes={**STANDARD_PREFIXES, **project_prefixes(base)},
        triples=_triples(base),
    ).render()

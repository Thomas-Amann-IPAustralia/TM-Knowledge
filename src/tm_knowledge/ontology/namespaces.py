"""RDF namespace bindings, derived from `docs/IDENTIFIERS.md` §2.

The prefixes are not re-declared here: they are read from `refs.PREFIXES`, so a
change to the identifier rules cannot leave the RDF layer pointing somewhere
else. `TMKR` is deliberately absent as a callable namespace — an upstream ref
becomes an IRI through `refs.to_iri` and by no other route, because `#` needs
escaping in one chunk ref in five (ADR-0023, Q-17) and a namespace object would
happily concatenate it.
"""

from __future__ import annotations

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, RDF, RDFS, SH, SKOS, XSD

from tm_knowledge.config import base_iri
from tm_knowledge.refs import PREFIXES, iri_for, to_iri

__all__ = [
    "TMK", "TMKC", "TMKP", "TMKA", "TMKG",
    "DCTERMS", "OWL", "PROV", "RDF", "RDFS", "SH", "SKOS", "XSD",
    "bind_all", "ref_node", "concept_node", "assertion_node", "proposition_node",
    "SOURCE_GRAPH", "APPROVED_GRAPH", "AUTHORED_GRAPH", "INFERRED_GRAPH",
    "NAMED_GRAPHS",
]


def _ns(prefix: str) -> Namespace:
    return Namespace(base_iri() + PREFIXES[prefix])


TMK = _ns("tmk")
TMKC = _ns("tmkc")
TMKP = _ns("tmkp")
TMKA = _ns("tmka")
TMKG = _ns("tmkg")

#: The named graphs of `graph/README.md`. `candidates` and `superseded` are
#: named there too and are not built yet — there are no candidates (no Stage 2
#: run has happened, ADR-0010) and nothing has been superseded.
#:
#: `authored` is the fourth, added when ADR-0080 gave machine-authored content a
#: store of its own. It is a *separate named graph* rather than a flag on nodes
#: in `approved` for ADR-0007's reason, which has not changed and is now
#: load-bearing: if machine output and signed knowledge mix once, no later audit
#: can unmix them. A flag can be dropped by a careless query; a named graph has
#: to be asked for.
SOURCE_GRAPH = URIRef(TMKG["source"])
APPROVED_GRAPH = URIRef(TMKG["approved"])
AUTHORED_GRAPH = URIRef(TMKG["authored"])
INFERRED_GRAPH = URIRef(TMKG["inferred"])
NAMED_GRAPHS = (SOURCE_GRAPH, APPROVED_GRAPH, AUTHORED_GRAPH, INFERRED_GRAPH)


def bind_all(graph: Graph) -> Graph:
    """Bind every prefix this project uses, plus the standard ones.

    Called on every graph that gets serialised. `queries/README.md` requires
    prefixes to be declared in full in query files; this is the writing half of
    the same rule, so a serialised file reads the same way a query does.
    """
    graph.bind("tmk", TMK)
    graph.bind("tmkr", base_iri() + PREFIXES["tmkr"])
    graph.bind("tmkc", TMKC)
    graph.bind("tmkp", TMKP)
    graph.bind("tmka", TMKA)
    graph.bind("tmkg", TMKG)
    graph.bind("skos", SKOS)
    graph.bind("prov", PROV)
    graph.bind("dcterms", DCTERMS)
    graph.bind("owl", OWL)
    graph.bind("sh", SH)
    return graph


def ref_node(ref: str) -> URIRef:
    """The IRI for an upstream ref. Delegates, never concatenates (ADR-0023)."""
    return URIRef(to_iri(ref))


def concept_node(concept_id: str) -> URIRef:
    """`GC-0001` -> `tmkc:GC-0001`.

    The local name is the gold-set id, not a re-minted `c-nnnn`. The id was
    already allocated once, in `eval/gold/concepts.yaml`, under the
    allocate-by-appending rule of `IDENTIFIERS.md` §3; minting a second
    identifier for the same concept would put the repo in the position of having
    two answers to "which concept is this" (ADR-0059).
    """
    return URIRef(iri_for("tmkc", concept_id))


def assertion_node(record_id: str) -> URIRef:
    """`GR-0001` -> `tmka:GR-0001`. One assertion resource per gold record."""
    return URIRef(iri_for("tmka", record_id))


def proposition_node(record_id: str) -> URIRef:
    """`PU-0001` / `CQ-0001` -> `tmkp:...`.

    Prohibited uses and competency questions are statements *about* the system
    rather than assertions about the corpus, so they sit under the proposition
    prefix and never under `tmka:`.
    """
    return URIRef(iri_for("tmkp", record_id))

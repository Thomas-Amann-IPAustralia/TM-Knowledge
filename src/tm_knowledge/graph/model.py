"""Namespaces, term helpers and the named graphs.

`docs/IDENTIFIERS.md` §2 fixes the prefixes and forbids any other module from
concatenating a base IRI. This module is the one place that turns a gold record
id into an IRI, and it does it through `refs.iri_for` and `refs.to_iri` rather
than by string arithmetic, so that the base stays a configuration value and
`TMK_BASE_IRI` still works (HANDOFF Q7).
"""

from __future__ import annotations

from tm_knowledge.graph.turtle import IRI, PN
from tm_knowledge.refs import iri_for, to_iri

__all__ = [
    "STANDARD_PREFIXES",
    "project_prefixes",
    "concept_iri",
    "assertion_iri",
    "ref_iri",
    "graph_iri",
    "term_iri",
    "tmk",
    "NAMED_GRAPHS",
]

#: Bindings `IDENTIFIERS.md` §2 says keep their usual meaning.
STANDARD_PREFIXES: dict[str, str] = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "prov": "http://www.w3.org/ns/prov#",
    "dcterms": "http://purl.org/dc/terms/",
    "sh": "http://www.w3.org/ns/shacl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}


def project_prefixes(base: str | None = None) -> dict[str, str]:
    """The project's own prefixes, expanded against the configured base."""
    return {
        "tmk": iri_for("tmk", "", base=base),
        "tmkr": iri_for("tmkr", "", base=base),
        "tmkc": iri_for("tmkc", "", base=base),
        "tmka": iri_for("tmka", "", base=base),
        "tmkg": iri_for("tmkg", "", base=base),
    }


def tmk(local_name: str) -> PN:
    """An ontology term this project defines. Local names are letters only.

    A `PN` is the caller promising the name is legal in Turtle, so this refuses
    anything that is not — the failure mode otherwise is a file that looks right
    and will not parse.
    """
    if not local_name.replace("_", "").isalnum():
        raise ValueError(f"not a safe local name for a prefixed name: {local_name!r}")
    return PN(f"tmk:{local_name}")


def term_iri(local_name: str, base: str | None = None) -> IRI:
    """The absolute IRI of an ontology term — for when a full IRI is wanted."""
    return IRI(iri_for("tmk", local_name, base=base))


def concept_iri(gold_id: str, base: str | None = None) -> IRI:
    """The IRI of a SKOS concept, from its gold record id.

    The local name is the **gold id itself** (`GC-0001`), not a freshly
    allocated `c-nnnn` as `IDENTIFIERS.md` §3 sketches. One register, one
    identifier, nothing to drift — see ADR-0057 for why the second register was
    the worse option here.
    """
    return IRI(iri_for("tmkc", gold_id, base=base))


def assertion_iri(gold_id: str, base: str | None = None) -> IRI:
    """The IRI of a single provenanced assertion, from its gold record id."""
    return IRI(iri_for("tmka", gold_id, base=base))


def ref_iri(ref: str, base: str | None = None) -> IRI:
    """The IRI of anything upstream names — a chunk, a provision, a decision."""
    return IRI(to_iri(ref, base=base))


def graph_iri(name: str, base: str | None = None) -> IRI:
    return IRI(iri_for("tmkg", name, base=base))


#: file stem -> (graph name, what it holds). The manifest is what makes these
#: files *named graphs* rather than four files that happen to sit together.
NAMED_GRAPHS: dict[str, tuple[str, str]] = {
    "vocab/s43-concepts": (
        "vocab",
        "The approved SKOS concept scheme for the pilot area.",
    ),
    "graph/s43-assertions": (
        "assertions",
        "The approved relationships as plain triples — what the graph says.",
    ),
    "graph/s43-provenance": (
        "provenance",
        "One reified assertion per relationship — who said it, where, and how "
        "strongly. Kept apart so that a query for what the graph says does not "
        "have to step over the record of why it says it.",
    ),
    "graph/s43-mentions": (
        "mentions",
        "The approved entity mentions: a surface form, a passage and an exact "
        "character span.",
    ),
    "graph/s43-bounds": (
        "bounds",
        "The approved prohibited uses — conclusions the system must not draw. "
        "In the graph on purpose: a bound nobody can query is a bound nobody "
        "will honour.",
    ),
}

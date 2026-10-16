"""The graph keeps the promises its own ontology makes, checked without a reasoner.

A declaration in `ontology/draft/` is not a comment. Under the OWL semantics the
modules claim, a functional property with two values makes the two values the same
individual, and a domain classifies every subject of the property. Nothing in the
product runs a reasoner, so neither shows up as a failure here; it shows up in the
first standard tool someone loads the graph into (the review response, F01).

So this test reads the committed graph against the declarations directly:

1. **A functional property has at most one value per subject.** Until S036
   `tmk:sourcePassage` was functional and 67 subjects carried two or more, which a
   reasoner reads as Manual chunk `owl:sameAs` section of the Act.
2. **Every subject of a property with a declared domain is already in that class.**
   A domain that would reclassify a subject is a declaration bug: until S036 the
   provenance stamps made every concept a `tmk:Assertion`, `tmk:derivedFrom` made a
   reasoning expectation an inferred assertion, and `evidence.ttl`'s stale
   `tmk:establishes` made evidence of use a `tmk:Evidence`.

The committed graph is the right input: CI fails when it differs from a rebuild
(ADR-0070), so it is what a build produces.
"""

from __future__ import annotations

from collections import defaultdict

import pytest

pytestmark = pytest.mark.rdf


@pytest.fixture(scope="module")
def tbox():
    from tm_knowledge.ontology import tbox as tbox_module

    return tbox_module.load()


@pytest.fixture(scope="module")
def data():
    from rdflib import Dataset, Graph

    from tm_knowledge.config import REPO_ROOT

    dataset = Dataset()
    dataset.parse(REPO_ROOT / "graph" / "dataset.nq", format="nquads")
    union = Graph()
    for subject, predicate, obj, _ in dataset.quads((None, None, None, None)):
        union.add((subject, predicate, obj))
    assert len(union) > 10_000, "graph/dataset.nq is missing or nearly empty"
    return union


def _name(term) -> str:
    return str(term).rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def _types(tbox, data):
    """Each subject's asserted classes and their superclasses: what it is without inference."""
    from rdflib.namespace import RDF, RDFS

    parents = defaultdict(set)
    for child, _, parent in tbox.triples((None, RDFS.subClassOf, None)):
        parents[child].add(parent)

    def closure(cls):
        seen, stack = set(), [cls]
        while stack:
            current = stack.pop()
            if current not in seen:
                seen.add(current)
                stack.extend(parents.get(current, ()))
        return seen

    out = defaultdict(set)
    for subject, _, cls in data.triples((None, RDF.type, None)):
        out[subject] |= closure(cls)
    return out


def test_no_functional_property_has_two_values(tbox, data):
    from rdflib.namespace import OWL, RDF

    found = {}
    for prop in tbox.subjects(RDF.type, OWL.FunctionalProperty):
        counts = defaultdict(int)
        for subject, _, _ in data.triples((None, prop, None)):
            counts[subject] += 1
        many = [subject for subject, n in counts.items() if n > 1]
        if many:
            found[_name(prop)] = len(many)
    assert not found, (
        f"functional properties with two or more values on one subject: {found}. Under OWL "
        f"the values become the same individual; drop the declaration or the second value."
    )


def test_no_domain_reclassifies_a_subject(tbox, data):
    from rdflib.namespace import RDFS

    types = _types(tbox, data)
    found = defaultdict(int)
    for prop, _, domain in tbox.triples((None, RDFS.domain, None)):
        for subject, _, _ in data.triples((None, prop, None)):
            if domain not in types[subject]:
                found[(_name(prop), _name(domain))] += 1
    assert not found, (
        "subjects a domain would reclassify (property, domain): "
        f"{dict(sorted(found.items()))}. A domain is an inference, not a check; "
        "put the constraint in a shape."
    )

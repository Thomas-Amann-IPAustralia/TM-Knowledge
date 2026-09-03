"""Build the vocabulary and the knowledge graph from `eval/gold/`.

Every triple this module emits comes from a record a person signed. There is no
extraction step, no model, and no threshold: the input is 190 approved records
and the output is the same content in a form a query engine can traverse. That
is what makes this legitimate while Stage 2 is not (ADR-0056) — and it is also
the honest limit of the demonstration, because a graph built only from approved
content is exactly as complete as the review got.

Five named graphs, kept apart because they answer different questions and
because mixing them is how a provenance record ends up being read as a claim:

- **vocab** — the concept scheme. Labels, the synonyms, and the non-synonyms.
- **assertions** — the plain triples. What the graph says.
- **provenance** — one reified assertion per relationship. Who said it, on which
  passage, at what strength, at what tier, approved by whom and when.
- **mentions** — where each surface form occurs, at an exact character span.
- **bounds** — the conclusions the system must not draw, and the questions each
  one guards.

Three things this module refuses to do, each of which would have been easier:

1. **It does not classify a concept into a legal class.** `GroundOfRefusal` and
   the rest stay empty (see `ontology.py`).
2. **It does not resolve a mention nobody resolved.** `resolves_to` is emitted
   where the approved record carries it and omitted where it does not. An
   absent link means nobody linked it, never that it links to nothing.
3. **It does not repair the input.** Where two approved relationships contradict
   each other, both are emitted and the conflict is reported. Silently dropping
   one would be an agent overruling a reviewer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable

from tm_knowledge.graph.model import (
    NAMED_GRAPHS,
    STANDARD_PREFIXES,
    assertion_iri,
    concept_iri,
    graph_iri,
    project_prefixes,
    ref_iri,
    tmk,
)
from tm_knowledge.graph.turtle import Document, IRI, Literal, PN, Term, Triples
from tm_knowledge.stage0 import goldset

__all__ = ["Build", "build", "conflicts", "SCHEME"]

#: The concept scheme's own local name.
SCHEME = "s43"

_GOLD_ID = re.compile(r"^(CQ|GE|GC|GR|GS|GA|GX|PU)-[0-9]{4}$")

#: Ref prefix -> the ontology class it belongs to. Nothing else infers a class
#: from a ref: a rule that guesses would be wrong for exactly the refs that
#: matter, and `refs.parse_ref` already refuses to place what it cannot.
_CLASS_FOR_REF: tuple[tuple[str, str], ...] = (
    ("TMM/", "ManualPassage"),
    ("TMA1995/", "LegislativeProvision"),
    ("TMR1995/", "LegislativeProvision"),
    ("CASE/", "JudicialDecision"),
)

#: The approved entity `type` values that have a class in this ontology. The
#: three that do not — `Other`, `Date`, `Role` — keep their approved string on
#: `tmk:entityType` and are not typed, because minting a class for them would be
#: this module deciding what they are.
_CLASS_FOR_ENTITY_TYPE: dict[str, str] = {
    "LegislativeProvision": "LegislativeProvision",
    "LegalConcept": "LegalConcept",
    "ManualInstruction": "ManualInstruction",
}


@dataclass
class Build:
    """The emitted graphs, plus what the build noticed on the way through."""

    documents: dict[str, Document] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    #: Pairs of approved records that assert opposite things about the same two
    #: nodes. Reported, never resolved.
    conflicts: tuple[tuple[str, str, str], ...] = ()
    #: Classes declared and deliberately empty, so the report can count them.
    unpopulated: tuple[str, ...] = ()

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def _class_for_ref(ref: str) -> str | None:
    for prefix, name in _CLASS_FOR_REF:
        if ref.startswith(prefix):
            return name
    return None


def _node(value: str, base: str | None = None) -> IRI:
    """The IRI for whatever a relationship names — a concept or an upstream ref."""
    if _GOLD_ID.match(value) and value.startswith("GC-"):
        return concept_iri(value, base)
    return ref_iri(value, base)


def _text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _approval(triples: Triples, subject: Term, record: dict[str, Any]) -> None:
    """The fields that make a node approved knowledge rather than a candidate."""
    if name := _text(record.get("approved_by")):
        triples.add(subject, tmk("approvedBy"), Literal(name))
    if when := _text(record.get("approved_date")):
        triples.add(subject, tmk("approvedDate"), Literal(date.fromisoformat(when)))
    triples.add(subject, tmk("goldRecord"), Literal(str(record["id"])))


def _passage(triples: Triples, ref: str, base: str | None) -> IRI:
    """Emit a passage node for a ref, typed by its instrument, and return it."""
    node = ref_iri(ref, base)
    if name := _class_for_ref(ref):
        triples.add(node, PN("a"), tmk(name))
    return node


# ---------------------------------------------------------------------------
# The vocabulary
# ---------------------------------------------------------------------------


def vocabulary(gold: goldset.GoldSet, base: str | None = None) -> Triples:
    """The approved concepts as SKOS, plus the non-synonyms SKOS cannot express.

    `not_labels` is the field worth the whole exercise. A synonym list widens a
    query and a reviewer can write one in a minute; a non-synonym list is what
    stops the widening reaching a term that means something else, and only
    somebody who knows the domain can write it. `connotation` carries
    `deceptively similar` in `not_labels`, and any system that expands one into
    the other has changed which section of the Act it is answering about.
    """
    triples = Triples()
    scheme = concept_iri(SCHEME, base)
    triples.add(scheme, PN("a"), PN("skos:ConceptScheme"))
    triples.add(
        scheme,
        PN("skos:prefLabel"),
        Literal("Trade marks examination — section 43 pilot vocabulary", language="en"),
    )
    triples.add(
        scheme,
        PN("dcterms:description"),
        Literal(
            "Concepts a reviewer approved over the section 43 material in the "
            "Examiner's Manual. Every concept is traceable to the passage it "
            "was defined from and to the name and date of its approval.",
            language="en",
        ),
    )

    for record in gold["gold_concept"]:
        node = concept_iri(str(record["id"]), base)
        triples.add(node, PN("a"), PN("skos:Concept"))
        triples.add(node, PN("a"), tmk("LegalConcept"))
        triples.add(node, PN("skos:inScheme"), scheme)
        triples.add(
            node, PN("skos:prefLabel"), Literal(str(record["pref_label"]), language="en")
        )
        for label in record.get("alt_labels") or ():
            triples.add(node, PN("skos:altLabel"), Literal(str(label), language="en"))
        for label in record.get("not_labels") or ():
            triples.add(node, tmk("notLabel"), Literal(str(label), language="en"))
        for other in record.get("broader") or ():
            triples.add(node, PN("skos:broader"), concept_iri(str(other), base))
        for other in record.get("narrower") or ():
            triples.add(node, PN("skos:narrower"), concept_iri(str(other), base))
        for other in record.get("related") or ():
            triples.add(node, PN("skos:related"), concept_iri(str(other), base))
        for ref in record.get("definition_sources") or ():
            triples.add(node, PN("skos:definition"), _passage(triples, str(ref), base))
        for ref in record.get("legislative_basis") or ():
            triples.add(node, tmk("hasLegislativeBasis"), _passage(triples, str(ref), base))
        if note := _text(record.get("notes")):
            triples.add(node, PN("skos:scopeNote"), Literal(note, language="en"))
        _approval(triples, node, record)

    return triples


# ---------------------------------------------------------------------------
# The relationships, twice: as claims and as records of who claimed them
# ---------------------------------------------------------------------------


def assertions(gold: goldset.GoldSet, base: str | None = None) -> Triples:
    """The plain triples — what the graph says, with nothing in the way."""
    triples = Triples()
    for record in gold["gold_relationship"]:
        subject = _node(str(record["subject"]), base)
        obj = _node(str(record["object"]), base)
        triples.add(subject, tmk(str(record["predicate"])), obj)
        for value in (str(record["subject"]), str(record["object"])):
            if not value.startswith("GC-") and (name := _class_for_ref(value)):
                triples.add(_node(value, base), PN("a"), tmk(name))
    return triples


def provenance(gold: goldset.GoldSet, base: str | None = None) -> Triples:
    """One reified assertion per relationship.

    Standard RDF reification — `rdf:subject`/`rdf:predicate`/`rdf:object` — and
    not RDF-star, because the graph has to load in tools that do not have it and
    because a reified statement is an ordinary node that ordinary SPARQL can
    filter. The plain triple is in the other graph; nothing here re-asserts it,
    so a query over provenance cannot be mistaken for a query over claims.
    """
    triples = Triples()
    for record in gold["gold_relationship"]:
        node = assertion_iri(str(record["id"]), base)
        triples.add(node, PN("a"), tmk("Assertion"))
        triples.add(node, PN("rdf:subject"), _node(str(record["subject"]), base))
        triples.add(node, PN("rdf:predicate"), tmk(str(record["predicate"])))
        triples.add(node, PN("rdf:object"), _node(str(record["object"]), base))
        if modality := _text(record.get("modality")):
            triples.add(node, tmk("hasModality"), tmk(modality.capitalize()))
        if (tier := record.get("tier")) is not None:
            triples.add(node, tmk("tier"), Literal(int(tier)))
        if text := _text(record.get("supporting_text")):
            triples.add(node, tmk("supportingText"), Literal(text, language="en"))
        if ref := _text(record.get("source_ref")):
            triples.add(node, PN("prov:wasDerivedFrom"), _passage(triples, ref, base))
        span = record.get("span")
        if isinstance(span, (list, tuple)) and len(span) == 2:
            triples.add(node, tmk("spanStart"), Literal(int(span[0])))
            triples.add(node, tmk("spanEnd"), Literal(int(span[1])))
        if digest := _text(record.get("source_content_hash")):
            triples.add(node, tmk("sourceContentHash"), Literal(digest))
        if note := _text(record.get("notes")):
            triples.add(node, PN("rdfs:comment"), Literal(note, language="en"))
        _approval(triples, node, record)
    return triples


# ---------------------------------------------------------------------------
# Mentions
# ---------------------------------------------------------------------------


def mentions(gold: goldset.GoldSet, base: str | None = None) -> Triples:
    """Where each approved surface form occurs, to the character.

    The span is the reason this graph is worth more than a list of terms: an
    answer built from it can quote the passage and point at the exact offsets
    the quote came from, and a reader can check it without trusting anything.
    """
    triples = Triples()
    for record in gold["gold_entity"]:
        node = assertion_iri(str(record["id"]), base)
        triples.add(node, PN("a"), tmk("Mention"))
        triples.add(node, tmk("surfaceForm"), Literal(str(record["surface"])))
        triples.add(node, tmk("entityType"), Literal(str(record["type"])))
        if name := _CLASS_FOR_ENTITY_TYPE.get(str(record["type"])):
            triples.add(node, PN("a"), tmk(name))
        if ref := _text(record.get("source_ref")):
            triples.add(node, tmk("mentionOf"), _passage(triples, ref, base))
        span = record.get("span")
        if isinstance(span, (list, tuple)) and len(span) == 2:
            triples.add(node, tmk("spanStart"), Literal(int(span[0])))
            triples.add(node, tmk("spanEnd"), Literal(int(span[1])))
        if digest := _text(record.get("source_content_hash")):
            triples.add(node, tmk("sourceContentHash"), Literal(digest))
        if target := _text(record.get("resolves_to")):
            triples.add(node, tmk("resolvesTo"), _passage(triples, target, base))
        if note := _text(record.get("notes")):
            triples.add(node, PN("rdfs:comment"), Literal(note, language="en"))
        _approval(triples, node, record)
    return triples


# ---------------------------------------------------------------------------
# Bounds and the questions they guard
# ---------------------------------------------------------------------------


def bounds(gold: goldset.GoldSet, base: str | None = None) -> Triples:
    """The prohibited uses, and the questions each one constrains.

    A prohibition that lives only in a test fixture is checked once, in CI, over
    the cases somebody thought of. The same prohibition in the graph can be
    fetched alongside the answer it applies to, which is the difference between
    a rule the system was tested against and a rule the system can consult.
    """
    triples = Triples()
    for record in gold["prohibited_use"]:
        node = assertion_iri(str(record["id"]), base)
        triples.add(node, PN("a"), tmk("Bound"))
        triples.add(node, tmk("prohibits"), Literal(str(record["prohibited"]), language="en"))
        triples.add(node, tmk("boundKind"), Literal(str(record["kind"])))
        if why := _text(record.get("why")):
            triples.add(node, tmk("why"), Literal(why, language="en"))
        if how := _text(record.get("detectable_by")):
            triples.add(node, tmk("detectableBy"), Literal(how))
        for question in record.get("related_questions") or ():
            triples.add(node, tmk("boundsQuestion"), assertion_iri(str(question), base))
        _approval(triples, node, record)

    for record in gold["competency_question"]:
        node = assertion_iri(str(record["id"]), base)
        triples.add(node, PN("a"), tmk("Question"))
        triples.add(node, tmk("questionText"), Literal(str(record["question"]), language="en"))
        if who := _text(record.get("asked_by")):
            triples.add(node, tmk("askedBy"), Literal(who))
        if category := _text(record.get("category")):
            triples.add(node, tmk("category"), Literal(category))
        sources = record.get("expected_sources") or {}
        for ref in (sources.get("required") or ()):
            triples.add(node, tmk("requiresEvidence"), _passage(triples, str(ref), base))
        _approval(triples, node, record)

    for record in gold["gold_retrieval_question"]:
        node = assertion_iri(str(record["id"]), base)
        triples.add(node, PN("a"), tmk("Question"))
        triples.add(node, tmk("questionText"), Literal(str(record["question"]), language="en"))
        triples.add(node, tmk("category"), Literal("retrieval"))
        for ref in record.get("required_evidence") or ():
            triples.add(node, tmk("requiresEvidence"), _passage(triples, str(ref), base))
        for ref in record.get("required_provisions") or ():
            triples.add(node, tmk("requiresEvidence"), _passage(triples, str(ref), base))
        if (needed := record.get("authority_distinction_required")) is not None:
            triples.add(
                node, tmk("requiresAuthorityDistinction"), Literal(bool(needed))
            )
        _approval(triples, node, record)

    return triples


# ---------------------------------------------------------------------------
# What the build noticed
# ---------------------------------------------------------------------------

#: Predicate pairs that say opposite things about the same two nodes. Asserting
#: this as an OWL `propertyDisjointWith` axiom would let a reasoner call the
#: graph inconsistent, and that is a step too far: whether `requiresElement` and
#: `excludesBasis` are strictly contradictory or merely in tension is a reading
#: of what the predicates mean, which is a legal judgement (rule 1). So the pair
#: is *reported* here and the axiom is filed as a candidate in `review/`.
OPPOSED: tuple[tuple[str, str], ...] = (
    ("requiresElement", "excludesBasis"),
    ("mayGiveRiseTo", "doesNotGiveRiseTo"),
)


def conflicts(gold: goldset.GoldSet) -> tuple[tuple[str, str, str], ...]:
    """(first record, second record, what they disagree about).

    Two approved records, both signed, saying opposed things about the same
    pair. This is not a defect in the graph — it is the graph doing the one job
    a document cannot do, which is noticing.
    """
    seen: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in gold["gold_relationship"]:
        seen.setdefault((str(record["subject"]), str(record["object"])), []).append(record)

    found: list[tuple[str, str, str]] = []
    for (subject, obj), records in sorted(seen.items()):
        if len(records) < 2:
            continue
        for index, first in enumerate(records):
            for second in records[index + 1 :]:
                pair = (str(first["predicate"]), str(second["predicate"]))
                if pair in OPPOSED or pair[::-1] in OPPOSED:
                    found.append(
                        (
                            str(first["id"]),
                            str(second["id"]),
                            f"{subject} {first['predicate']} {obj} "
                            f"against {subject} {second['predicate']} {obj}",
                        )
                    )
    return tuple(found)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

_BUILDERS = {
    "vocab/s43-concepts": vocabulary,
    "graph/s43-assertions": assertions,
    "graph/s43-provenance": provenance,
    "graph/s43-mentions": mentions,
    "graph/s43-bounds": bounds,
}


def _header(stem: str, gold: goldset.GoldSet) -> tuple[str, ...]:
    import textwrap

    name, purpose = NAMED_GRAPHS[stem]
    return (
        f"TM-Knowledge — named graph tmkg:{name}",
        "",
        *textwrap.wrap(purpose, 72),
        "",
        "GENERATED by tm_knowledge.graph.build from eval/gold/. Every triple",
        "here comes from a record a person signed; nothing was extracted, and",
        "nothing was inferred. Rebuild with tmk-graph rather than editing.",
    )


def build(gold: goldset.GoldSet | None = None, base: str | None = None) -> Build:
    """Every named graph, plus the counts and the conflicts."""
    gold = gold if gold is not None else goldset.load()
    prefixes = {**STANDARD_PREFIXES, **project_prefixes(base)}

    result = Build()
    for stem, builder in _BUILDERS.items():
        triples = builder(gold, base)
        result.documents[stem] = Document(
            header=_header(stem, gold), prefixes=prefixes, triples=triples
        )
        result.counts[stem] = len(triples)

    from tm_knowledge.graph.ontology import CLASSES

    result.conflicts = conflicts(gold)
    result.unpopulated = tuple(
        entry.name for entry in CLASSES if entry.unpopulated_by_design
    )
    return result

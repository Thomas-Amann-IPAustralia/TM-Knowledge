"""The pilot ontology modules (Stage 5), as data rather than as hand-cut Turtle.

**Why the ontology is generated.** `IDENTIFIERS.md` says the base IRI lives in
exactly one constant and that changing it must be a configuration change and a
rebuild, "not a find-and-replace across serialised RDF" (HANDOFF Q7, still
unconfirmed). A hand-authored `.ttl` bakes the base into its `@prefix` lines on
the first line of the file, which is precisely the thing that rule forbids. So
the design lives here, where it can carry its reasons, and `ontology/*.ttl` is
the published artefact. The trade is real and is recorded as ADR-0059: editing
this in Protégé now means editing a generated file, and there is no round trip.

**What is asserted here and what is deliberately not.** The class taxonomy comes
from `ARCHITECTURE.md` §4, which comes from the roadmap — inherited, not
invented. The fourteen relation properties are the predicates that appear on
approved gold relationships. Both are safe.

What is **not** here is any classification of a particular concept into a legal
class. `GroundOfRefusal`, `LegalTest`, `RelevantFactor` and `Exception` are
declared and **nothing is a member of any of them**, because deciding that
"likely to deceive or cause confusion" is a legal test rather than a ground is a
legal judgement and CLAUDE.md rule 1 reserves it for a person. The empty classes
are not an oversight; they are the shape of the question, and the demonstration
report counts them so the gap is visible rather than quietly filled.

**Constraints go in SHACL, not in OWL.** No relation property carries
`rdfs:domain` or `rdfs:range`. Domain and range in RDFS are *inference* rules —
declaring `domain tmk:LegalConcept` does not check that the subject is a legal
concept, it silently asserts that it is one. Over a graph whose subjects include
provisions, cases and passages that would manufacture claims nobody approved.
The endpoints are checked instead, in `shapes/`, where a violation is reported
rather than believed (ADR-0060).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tm_knowledge.graph.model import STANDARD_PREFIXES, project_prefixes, tmk
from tm_knowledge.graph.turtle import Document, IRI, Literal, PN, Triples

__all__ = ["MODULES", "CLASSES", "PROPERTIES", "MODALITIES", "PREDICATES", "render"]


@dataclass(frozen=True, slots=True)
class Class:
    name: str
    label: str
    comment: str
    parent: str | None = None
    disjoint_with: tuple[str, ...] = ()
    module: str = "legal-concepts"
    #: True where the class is declared for the model's sake and nothing in the
    #: pilot is a member, because membership is a judgement (rule 1).
    unpopulated_by_design: bool = False


@dataclass(frozen=True, slots=True)
class Property:
    name: str
    label: str
    comment: str
    module: str = "relations"
    kind: str = "object"
    parent: str | None = None


#: The taxonomy. `ARCHITECTURE.md` §4's six modules, reduced to what the pilot's
#: approved content actually exercises — an ontology with classes nothing uses
#: is a diagram, not a model.
CLASSES: tuple[Class, ...] = (
    Class(
        "LegalMatter",
        "legal matter",
        "Anything an approved relationship can stand between: a provision, a "
        "decision, a passage of the Manual, or a concept. Deliberately broad. "
        "It exists so the SHACL shapes have something to name, not so a "
        "reasoner can conclude anything from it.",
        module="authority",
    ),
    Class(
        "Authority",
        "authority",
        "Something that can be cited in support of an examination position. "
        "Its subclasses are the whole point of this module: they do not carry "
        "the same weight and must never be flattened into one another.",
        parent="LegalMatter",
        module="authority",
    ),
    Class(
        "Legislation",
        "legislation",
        "An instrument — the Trade Marks Act 1995 or the Trade Marks "
        "Regulations 1995. Binding.",
        parent="Authority",
        module="authority",
    ),
    Class(
        "LegislativeProvision",
        "legislative provision",
        "A section, regulation, schedule or item within an instrument. Binding "
        "law. Addressed by an upstream provision ref such as TMA1995/s43.",
        parent="Authority",
        disjoint_with=("ManualInstruction",),
        module="authority",
    ),
    Class(
        "JudicialDecision",
        "judicial decision",
        "A decided case. Cited by the Manual and by this graph, but held "
        "nowhere in the programme as a document — every case node is a "
        "citation whose text nothing has read (HANDOFF Q6, QUIRKS Q-11).",
        parent="Authority",
        module="authority",
    ),
    Class(
        "ManualInstruction",
        "Manual instruction",
        "A statement of the Registrar's practice, taken from the Examiner's "
        "Manual. It states what the Office does; it does not bind the "
        "Registrar's discretion and it is not law (CLAUDE.md rule 5). Disjoint "
        "from LegislativeProvision, and the disjointness is the single most "
        "load-bearing axiom in this ontology.",
        parent="Authority",
        disjoint_with=("LegislativeProvision",),
        module="authority",
    ),
    Class(
        "ManualPassage",
        "Manual passage",
        "An addressable chunk of the Manual, identified by its upstream "
        "chunk_ref. The unit is the chunk, not an idealised paragraph number — "
        "upstream headings are not reliable as structure (QUIRKS Q-10).",
        parent="LegalMatter",
        module="document",
    ),
    Class(
        "LegalConcept",
        "legal concept",
        "A concept in the controlled vocabulary that the examination practice "
        "turns on. Every member is also a skos:Concept in the pilot scheme.",
        parent="LegalMatter",
        module="legal-concepts",
    ),
    Class(
        "GroundOfRefusal",
        "ground of refusal",
        "A basis on which an application may be rejected. **No concept in the "
        "pilot is classified into this class**, because deciding that a "
        "particular concept is a ground rather than a test or a factor is a "
        "legal judgement and no approved record carries it (rule 1).",
        parent="LegalConcept",
        module="legal-concepts",
        unpopulated_by_design=True,
    ),
    Class(
        "LegalTest",
        "legal test",
        "A test a decision maker applies. Unpopulated for the same reason as "
        "GroundOfRefusal.",
        parent="LegalConcept",
        module="legal-concepts",
        unpopulated_by_design=True,
    ),
    Class(
        "RelevantFactor",
        "relevant factor",
        "Something a decision maker weighs without it being decisive. "
        "Unpopulated for the same reason.",
        parent="LegalConcept",
        module="legal-concepts",
        unpopulated_by_design=True,
    ),
    Class(
        "Exception",
        "exception",
        "A circumstance that displaces a ground that would otherwise apply. "
        "Unpopulated for the same reason.",
        parent="LegalConcept",
        module="legal-concepts",
        unpopulated_by_design=True,
    ),
    Class(
        "Mention",
        "mention",
        "One occurrence of a surface form in a passage, at an exact character "
        "span. A mention is evidence that a thing was said somewhere; it is "
        "not the thing.",
        module="document",
    ),
    Class(
        "Assertion",
        "assertion",
        "One approved relationship, reified so that it can carry who approved "
        "it, on what passage, at what strength and at what tier. The plain "
        "triple says what the graph believes; this says why, and the two live "
        "in different named graphs so a query for one need not wade through "
        "the other.",
        module="provenance",
    ),
    Class(
        "Bound",
        "bound",
        "A conclusion the system must not draw, with the reason and the way it "
        "is detected. Held in the graph rather than in a test fixture so that "
        "a retrieval answer can be checked against it at query time.",
        module="evaluation",
    ),
    Class(
        "Question",
        "question",
        "A question the system is expected to answer, from the approved "
        "competency and retrieval sets. Present so that a bound has something "
        "to attach to: a prohibition floating free of the questions it "
        "constrains is a sentence in a document, not a guard.",
        module="evaluation",
    ),
    Class(
        "Modality",
        "modality",
        "How strongly a relationship is stated: must, may or should. Taken "
        "from the approved record, never inferred from the grammar — several "
        "approved relationships carry a modality that no modal verb in the "
        "sentence supports, and the record says so.",
        module="relations",
    ),
)

#: The three approved modality values, as named individuals rather than strings,
#: so a query can ask for obligations without matching on spelling.
MODALITIES: tuple[tuple[str, str, str], ...] = (
    ("Must", "must", "Stated as an obligation or as the absence of a discretion."),
    ("May", "may", "Stated as a possibility — it can happen, not that it must."),
    (
        "Should",
        "should",
        "Stated as expected practice. The weakest of the three, and the one "
        "most often mistaken for an obligation when the Manual is read as law.",
    ),
)

#: The fourteen predicates that appear on approved relationships. Nothing here
#: is invented: each is a value a reviewer signed off on a record.
PREDICATES: tuple[tuple[str, str], ...] = (
    ("appliesTo", "The provision applies to the matter, of its own force."),
    (
        "constrainsExaminerTo",
        "The subject limits what a decision maker may do — including by "
        "removing a discretion that would otherwise exist.",
    ),
    ("requiresElement", "The subject is not made out unless the object is present."),
    (
        "excludesBasis",
        "The object may not be used as a basis for the subject. A negative "
        "statement, and one that can sit in genuine tension with "
        "requiresElement over the same pair — see the demonstration report.",
    ),
    ("allocatesTo", "The passage assigns the matter to another provision."),
    ("mayGiveRiseTo", "The subject can lead to the object. Possibility, not consequence."),
    ("interprets", "The decision or passage construes the object."),
    ("citesAuthorityFor", "The subject is cited as authority for the object."),
    ("doesNotGiveRiseTo", "The subject does not lead to the object."),
    ("qualifies", "The subject narrows or conditions the object."),
    ("statesThresholdFor", "The subject fixes the level at which the object is met."),
    ("isOvercomeBy", "The subject is displaced or answered by the object."),
    (
        "dependsOnExternalSource",
        "Establishing the subject needs something the programme does not hold — "
        "a register, a decision text, a fact about the world.",
    ),
    ("extendsTo", "The subject reaches the object as well."),
)

#: Datatype and object properties that are not relation predicates.
PROPERTIES: tuple[Property, ...] = (
    Property(
        "hasModality",
        "has modality",
        "The strength the approved record recorded, as a Modality individual.",
        module="relations",
    ),
    Property(
        "tier",
        "tier",
        "The consequence tier from the gold record: 3 where a wrong reading "
        "would change an examination position, 2 where it would not.",
        module="provenance",
        kind="datatype",
    ),
    Property(
        "supportingText",
        "supporting text",
        "The sentence the assertion rests on, quoted from the passage.",
        module="provenance",
        kind="datatype",
    ),
    Property(
        "spanStart",
        "span start",
        "Character offset of the supporting span within the passage.",
        module="provenance",
        kind="datatype",
    ),
    Property(
        "spanEnd",
        "span end",
        "Character offset, exclusive, of the end of the supporting span.",
        module="provenance",
        kind="datatype",
    ),
    Property(
        "sourceContentHash",
        "source content hash",
        "The passage's content hash at the time of approval. When the pin "
        "moves and this no longer matches, the approval is stale and the "
        "harness says so — a hash is never silently refreshed.",
        module="provenance",
        kind="datatype",
    ),
    Property(
        "approvedBy",
        "approved by",
        "Who signed the record. A record with no name here is not approved "
        "knowledge, whatever else it carries (ADR-0039).",
        module="provenance",
        kind="datatype",
    ),
    Property(
        "approvedDate", "approved date", "When it was signed.",
        module="provenance", kind="datatype",
    ),
    Property(
        "goldRecord",
        "gold record",
        "The id of the approved record this node was built from, so anything "
        "in the graph can be traced back to the row a person signed.",
        module="provenance",
        kind="datatype",
    ),
    Property(
        "notLabel",
        "not a label for",
        "A term that must **not** be treated as a synonym of this concept, "
        "recorded by a reviewer. SKOS has no way to say this and it is the "
        "most valuable field in the vocabulary: a synonym list makes recall "
        "better, and only a non-synonym list stops the expansion turning "
        "'connotation' into 'deceptively similar'.",
        module="legal-concepts",
        kind="datatype",
    ),
    Property(
        "mentionOf",
        "mention of",
        "The passage a mention occurs in.",
        module="document",
    ),
    Property(
        "surfaceForm", "surface form", "The text as it appears in the passage.",
        module="document", kind="datatype",
    ),
    Property(
        "resolvesTo",
        "resolves to",
        "What a mention refers to, where upstream carries an authored link for "
        "it. Absent means nobody resolved it, never that it resolves to "
        "nothing.",
        module="document",
    ),
    Property(
        "prohibits", "prohibits", "The conclusion this bound forbids.",
        module="evaluation", kind="datatype",
    ),
    Property(
        "boundKind", "bound kind", "What kind of failure the bound guards against.",
        module="evaluation", kind="datatype",
    ),
    Property(
        "why", "why", "Why the conclusion is wrong, in the reviewer's words.",
        module="evaluation", kind="datatype",
    ),
    Property(
        "detectableBy",
        "detectable by",
        "How a breach of this bound would be caught — by an automated test, by "
        "evaluation, or only by a person reading the output.",
        module="evaluation",
        kind="datatype",
    ),
    Property(
        "boundsQuestion",
        "bounds question",
        "A competency or retrieval question this bound applies to.",
        module="evaluation",
    ),
    Property(
        "questionText", "question text", "The question as a person would ask it.",
        module="evaluation", kind="datatype",
    ),
    Property(
        "askedBy", "asked by", "Who asks it — an examiner, an applicant, an attorney.",
        module="evaluation", kind="datatype",
    ),
    Property(
        "category", "category", "The approved question category.",
        module="evaluation", kind="datatype",
    ),
    Property(
        "requiresEvidence",
        "requires evidence",
        "A passage or provision an answer must rest on to be right. The "
        "difference between an answer and a plausible sentence.",
        module="evaluation",
    ),
    Property(
        "requiresAuthorityDistinction",
        "requires authority distinction",
        "True where an answer is wrong unless it keeps the Act and the "
        "Manual's practice visibly apart (CLAUDE.md rule 5).",
        module="evaluation",
        kind="datatype",
    ),
    Property(
        "entityType",
        "entity type",
        "The type a reviewer put on the mention. Recorded as the approved "
        "string as well as being typed, because three of the six values have "
        "no class in this ontology and inventing one would be a judgement.",
        module="document",
        kind="datatype",
    ),
)

#: module name -> (filename, title, what it is for)
MODULES: dict[str, tuple[str, str, str]] = {
    "authority": (
        "tmk-authority.ttl",
        "Authority",
        "What may be cited, and the distinction that must survive into every "
        "answer: the Act binds, the Manual states practice.",
    ),
    "legal-concepts": (
        "tmk-legal-concepts.ttl",
        "Legal concepts",
        "The concept classes, and the non-synonym property SKOS lacks.",
    ),
    "document": (
        "tmk-document.ttl",
        "Document",
        "Passages and mentions, mapped onto upstream's chunk refs rather than "
        "onto an idealised chapter tree.",
    ),
    "relations": (
        "tmk-relations.ttl",
        "Relations",
        "The fourteen approved predicates and the three modalities.",
    ),
    "provenance": (
        "tmk-provenance.ttl",
        "Provenance",
        "Reified assertions and the approval fields from ADR-0011.",
    ),
    "evaluation": (
        "tmk-evaluation.ttl",
        "Evaluation",
        "Questions the system must answer and conclusions it must not draw. "
        "In the ontology rather than only in eval/ so that a bound can be "
        "checked against an answer at query time.",
    ),
}


def _header(module: str) -> tuple[str, ...]:
    _, title, purpose = MODULES[module]
    return (
        f"TM-Knowledge ontology — {title}",
        "",
        *_wrap(purpose),
        "",
        "GENERATED by tm_knowledge.graph.ontology. Do not hand-edit: the base",
        "IRI is a configuration value (IDENTIFIERS.md, HANDOFF Q7) and editing",
        "the prefix line here is the find-and-replace that rule forbids.",
        "Edit src/tm_knowledge/graph/ontology.py and rebuild with tmk-graph.",
    )


def _wrap(text: str, width: int = 72) -> list[str]:
    import textwrap

    return textwrap.wrap(text, width) or [""]


def _comment(triples: Triples, subject, text: str) -> None:
    triples.add(subject, PN("rdfs:comment"), Literal(text, language="en"))


def _module_triples(module: str, base: str | None = None) -> Triples:
    triples = Triples()

    for entry in CLASSES:
        if entry.module != module:
            continue
        name = tmk(entry.name)
        triples.add(name, PN("a"), PN("owl:Class"))
        triples.add(name, PN("rdfs:label"), Literal(entry.label, language="en"))
        _comment(triples, name, entry.comment)
        if entry.parent:
            triples.add(name, PN("rdfs:subClassOf"), tmk(entry.parent))
        for other in entry.disjoint_with:
            triples.add(name, PN("owl:disjointWith"), tmk(other))
        if entry.unpopulated_by_design:
            triples.add(name, tmk("unpopulatedByDesign"), Literal(True))

    if module == "relations":
        for name, comment in PREDICATES:
            term = tmk(name)
            triples.add(term, PN("a"), PN("owl:ObjectProperty"))
            triples.add(term, PN("rdfs:label"), Literal(_spaced(name), language="en"))
            _comment(triples, term, comment)
            triples.add(term, PN("rdfs:subPropertyOf"), tmk("relatesLegalMatter"))
        parent = tmk("relatesLegalMatter")
        triples.add(parent, PN("a"), PN("owl:ObjectProperty"))
        triples.add(parent, PN("rdfs:label"), Literal("relates legal matter", language="en"))
        _comment(
            triples,
            parent,
            "The common parent of the fourteen approved predicates, so a query "
            "can ask what the graph says about a concept without naming all "
            "fourteen. Carries no domain or range: in RDFS those infer rather "
            "than check, and the endpoints here are checked in SHACL instead.",
        )
        for name, label, comment in MODALITIES:
            term = tmk(name)
            triples.add(term, PN("a"), tmk("Modality"))
            triples.add(term, PN("rdfs:label"), Literal(label, language="en"))
            _comment(triples, term, comment)

    for prop in PROPERTIES:
        if prop.module != module:
            continue
        term = tmk(prop.name)
        kind = "owl:DatatypeProperty" if prop.kind == "datatype" else "owl:ObjectProperty"
        triples.add(term, PN("a"), PN(kind))
        triples.add(term, PN("rdfs:label"), Literal(prop.label, language="en"))
        _comment(triples, term, prop.comment)

    if module == "provenance":
        assertion = tmk("Assertion")
        triples.add(assertion, PN("rdfs:subClassOf"), PN("prov:Entity"))
        triples.add(tmk("Mention"), PN("rdfs:subClassOf"), PN("prov:Entity"))
        marker = tmk("unpopulatedByDesign")
        triples.add(marker, PN("a"), PN("owl:DatatypeProperty"))
        triples.add(marker, PN("rdfs:label"), Literal("unpopulated by design", language="en"))
        _comment(
            triples,
            marker,
            "Marks a class that is declared and deliberately empty because "
            "putting anything in it would be a legal judgement no approved "
            "record supports. An empty class so marked is a question; an empty "
            "class without it is a bug.",
        )

    return triples


def _spaced(name: str) -> str:
    out: list[str] = []
    for character in name:
        if character.isupper() and out:
            out.append(" ")
        out.append(character.lower())
    return "".join(out)


def render(module: str, base: str | None = None) -> str:
    """One ontology module as Turtle."""
    if module not in MODULES:
        raise KeyError(f"unknown module {module!r}; known: {sorted(MODULES)}")
    return Document(
        header=_header(module),
        prefixes={**STANDARD_PREFIXES, **project_prefixes(base)},
        triples=_module_triples(module, base),
    ).render()

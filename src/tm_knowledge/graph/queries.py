"""Demonstration queries: what the graph answers that a text search cannot.

Each one is here because it is a question somebody actually has and a keyword
index genuinely cannot serve — not because it shows off SPARQL. The test is
blunt: if grep over the Manual would do as well, the query does not belong here.

The queries are held as data and the prefix block is generated, for the same
reason the ontology is generated: the base IRI is configuration (HANDOFF Q7),
and a `.rq` file with the base typed into its PREFIX line is the find-and-
replace `IDENTIFIERS.md` forbids.

**None of these answers a legal question.** They report what approved records
say, with the passage and the approver attached. The difference matters most in
`obligations`: the graph will tell you a reviewer recorded a statement as an
obligation and show you the sentence, and it will not tell you that you are
obliged.
"""

from __future__ import annotations

from dataclasses import dataclass

from tm_knowledge.graph.model import STANDARD_PREFIXES, project_prefixes

__all__ = ["QUERIES", "Query", "render", "prefix_block"]


@dataclass(frozen=True, slots=True)
class Query:
    name: str
    title: str
    #: Why this cannot be done with a search index. The honest part.
    why: str
    body: str


QUERIES: tuple[Query, ...] = (
    Query(
        "obligations",
        "What is recorded as an obligation, and what only as a possibility",
        "A text index can find the word 'must'. It cannot tell you that a "
        "sentence with no modal verb in it at all was read by a reviewer as "
        "removing a discretion — which is what GR-0002 is. Modality here is a "
        "recorded judgement, not a grammatical feature, so it is only "
        "queryable because somebody wrote it down.",
        """
SELECT ?modality ?subject ?predicate ?object ?tier ?text ?source ?who
WHERE {
  ?assertion a tmk:Assertion ;
             tmk:hasModality ?modality ;
             rdf:subject ?subject ;
             rdf:predicate ?predicate ;
             rdf:object ?object ;
             tmk:tier ?tier ;
             tmk:supportingText ?text ;
             prov:wasDerivedFrom ?source ;
             tmk:approvedBy ?who .
}
ORDER BY ?modality ?subject
""",
    ),
    Query(
        "law-or-practice",
        "For a question that must keep them apart: which evidence is law, which is practice",
        "The single most important distinction in the corpus and the one a "
        "retrieval system loses first: the Act binds, the Manual states what "
        "the Office does. Both are prose, both are returned identically by a "
        "text index, and telling them apart by eye means recognising a "
        "citation format. Here the answer's own required evidence is typed, so "
        "'did this answer keep law and practice apart' becomes a check rather "
        "than a hope.",
        """
SELECT ?questionText ?evidence ?kind
WHERE {
  ?question a tmk:Question ;
            tmk:questionText ?questionText ;
            tmk:requiresAuthorityDistinction true ;
            tmk:requiresEvidence ?evidence .
  ?evidence a ?kind .
  FILTER(?kind IN (tmk:LegislativeProvision, tmk:ManualPassage))
}
ORDER BY ?questionText ?kind
""",
    ),
    Query(
        "both-sides",
        "Nodes that sit on both sides of the same relation",
        "A structural smell, not a verdict. `isOvercomeBy` should bottom out — "
        "a thing that overcomes a ground is not itself something the ground "
        "overcomes. Where one concept appears as both subject and object of "
        "the same predicate, at least one of the two records is pointing the "
        "wrong way. It catches GR-0032, whose own note says its subject and "
        "object are reversed and which was approved regardless. No amount of "
        "reading a workbook row by row finds this; it is only visible once "
        "the rows are edges.",
        """
SELECT ?predicate ?label ?asSubjectOf ?asObjectOf
WHERE {
  ?a1 a tmk:Assertion ; rdf:predicate ?predicate ;
      rdf:subject ?node ; tmk:goldRecord ?asSubjectOf .
  ?a2 a tmk:Assertion ; rdf:predicate ?predicate ;
      rdf:object ?node ; tmk:goldRecord ?asObjectOf .
  OPTIONAL { ?node skos:prefLabel ?label }
}
ORDER BY ?predicate ?label
""",
    ),
    Query(
        "expansion-guard",
        "Expanding a user's phrase — and what the expansion must not reach",
        "This is the query that pays for the vocabulary. Any embedding model "
        "will happily put 'connotation' near 'deceptively similar': they are "
        "adjacent in the corpus, they co-occur, and they are about different "
        "sections of the Act. The non-synonym list is a reviewer's explicit "
        "refusal, and nothing but a reviewer could have produced it.",
        """
SELECT ?concept ?prefLabel
       (GROUP_CONCAT(DISTINCT ?alt; separator=" | ") AS ?expandTo)
       (GROUP_CONCAT(DISTINCT ?not; separator=" | ") AS ?neverExpandTo)
WHERE {
  ?concept a skos:Concept ; skos:prefLabel ?prefLabel .
  OPTIONAL { ?concept skos:altLabel ?alt }
  OPTIONAL { ?concept tmk:notLabel ?not }
}
GROUP BY ?concept ?prefLabel
HAVING(COUNT(DISTINCT ?not) > 0)
ORDER BY ?prefLabel
""",
    ),
    Query(
        "provenance-chase",
        "For one statement: the passage, the exact characters, the approver, the date",
        "Not impossible with a search index, but nobody builds one that can do "
        "it, because the index stores a document and the answer needs an "
        "offset. Here every claim carries the span it was read from and the "
        "hash of the passage at the moment it was approved, so a stale claim "
        "is detectable rather than merely wrong.",
        """
SELECT ?record ?subject ?predicate ?object ?source ?start ?end ?hash ?who ?when
WHERE {
  ?assertion a tmk:Assertion ;
             tmk:goldRecord ?record ;
             rdf:subject ?subject ;
             rdf:predicate ?predicate ;
             rdf:object ?object ;
             prov:wasDerivedFrom ?source ;
             tmk:spanStart ?start ;
             tmk:spanEnd ?end ;
             tmk:sourceContentHash ?hash ;
             tmk:approvedBy ?who ;
             tmk:approvedDate ?when .
}
ORDER BY ?record
""",
    ),
    Query(
        "what-overcomes",
        "What answers a ground once it has been raised",
        "A traversal, and the reason a graph beats a list. 'What overcomes X' "
        "and 'what does X overcome' are the same edge read in two directions; "
        "in a document they are two passages that may be chapters apart and "
        "may not share a single word.",
        """
SELECT ?subjectLabel ?objectLabel ?modality ?text ?source
WHERE {
  ?subject tmk:isOvercomeBy ?object .
  ?assertion a tmk:Assertion ;
             rdf:subject ?subject ;
             rdf:predicate tmk:isOvercomeBy ;
             rdf:object ?object ;
             tmk:supportingText ?text ;
             prov:wasDerivedFrom ?source .
  OPTIONAL { ?assertion tmk:hasModality ?modality }
  OPTIONAL { ?subject skos:prefLabel ?subjectLabel }
  OPTIONAL { ?object skos:prefLabel ?objectLabel }
}
ORDER BY ?subjectLabel
""",
    ),
    Query(
        "bounds-on-an-answer",
        "Before answering this question, what must the system not conclude",
        "The one with no equivalent at all. A prohibition that lives in a test "
        "fixture is checked once, in CI, against the cases somebody thought "
        "of. The same prohibition on the question node can be fetched with the "
        "answer and applied to it — a rule the system consults rather than a "
        "rule it was tested against.",
        """
SELECT ?question ?questionText ?prohibited ?kind ?why ?detectableBy
WHERE {
  ?bound a tmk:Bound ;
         tmk:prohibits ?prohibited ;
         tmk:boundKind ?kind ;
         tmk:why ?why ;
         tmk:detectableBy ?detectableBy ;
         tmk:boundsQuestion ?question .
  ?question tmk:questionText ?questionText .
}
ORDER BY ?question
""",
    ),
    Query(
        "opposed-statements",
        "Approved statements that say opposite things about the same pair",
        "The graph doing the one thing a document cannot: noticing. Two "
        "records, both signed by the same reviewer on the same set, assert "
        "that connotation requires reputation and that it excludes it. Neither "
        "reading of the two passages is this file's to make — but nothing in a "
        "368-row workbook was ever going to put them side by side.",
        """
SELECT ?first ?second ?subject ?p1 ?p2 ?object ?t1 ?t2
WHERE {
  ?a1 a tmk:Assertion ; tmk:goldRecord ?first ;
      rdf:subject ?subject ; rdf:predicate ?p1 ; rdf:object ?object ;
      tmk:supportingText ?t1 .
  ?a2 a tmk:Assertion ; tmk:goldRecord ?second ;
      rdf:subject ?subject ; rdf:predicate ?p2 ; rdf:object ?object ;
      tmk:supportingText ?t2 .
  FILTER(STR(?first) < STR(?second))
  FILTER(?p1 != ?p2)
}
ORDER BY ?first
""",
    ),
    Query(
        "sent-elsewhere",
        "You asked about something this section does not cover — where does it go",
        "The one that would have changed a real answer. Approved search "
        "question GS-0003 asks about 'confusion with an existing registered "
        "trade mark'. Term frequency over the in-scope chunks ranks the two "
        "correct passages 107th and 72nd of 216 and puts all three of the "
        "reviewer's tempting-but-wrong passages above them, because the "
        "correct answers are the passages that say this is *not* section 43's "
        "business and they say it in fewer words. The graph holds both halves "
        "of what is needed and an index holds neither: the vocabulary records "
        "'confusion between trade marks' as an explicit **non**-synonym of the "
        "section 43 sense, and an approved edge sends the matter to section "
        "44. Neither is a ranking problem; both are facts a person wrote down.",
        """
SELECT ?prefLabel ?notLabel ?passage ?sentTo ?text ?record
WHERE {
  ?concept a skos:Concept ;
           skos:prefLabel ?prefLabel ;
           tmk:notLabel ?notLabel .
  ?exclusion a tmk:Assertion ;
             rdf:subject ?concept ;
             rdf:predicate tmk:excludesBasis ;
             rdf:object ?sentTo ;
             prov:wasDerivedFrom ?passage .
  ?sentTo a tmk:LegislativeProvision .
  ?allocation a tmk:Assertion ;
              rdf:subject ?passage ;
              rdf:predicate tmk:allocatesTo ;
              rdf:object ?sentTo ;
              tmk:supportingText ?text ;
              tmk:goldRecord ?record .
}
ORDER BY ?prefLabel ?notLabel
""",
    ),
    Query(
        "unanswerable-without-external-source",
        "Which questions the corpus cannot answer on its own",
        "A search index always returns something. This returns the statements "
        "a reviewer marked as depending on material the programme does not "
        "hold — a register, a decision text, a fact about the world — which is "
        "the difference between an honest 'I cannot tell you' and a confident "
        "paragraph assembled from the nearest passage.",
        """
SELECT ?subjectLabel ?objectLabel ?text ?source
WHERE {
  ?assertion a tmk:Assertion ;
             rdf:predicate tmk:dependsOnExternalSource ;
             rdf:subject ?subject ;
             rdf:object ?object ;
             tmk:supportingText ?text ;
             prov:wasDerivedFrom ?source .
  OPTIONAL { ?subject skos:prefLabel ?subjectLabel }
  OPTIONAL { ?object skos:prefLabel ?objectLabel }
}
""",
    ),
)


def prefix_block(base: str | None = None) -> str:
    prefixes = {**STANDARD_PREFIXES, **project_prefixes(base)}
    return "\n".join(
        f"PREFIX {name}: <{prefixes[name]}>" for name in sorted(prefixes)
    )


def render(query: Query, base: str | None = None) -> str:
    """One query as a runnable `.rq` file, with its reasons in the header."""
    import textwrap

    header = [f"# {query.title}", "#"]
    header += [f"# {line}" for line in textwrap.wrap(query.why, 72)]
    header += [
        "#",
        "# GENERATED by tm_knowledge.graph.queries. The PREFIX block is built",
        "# from the configured base IRI; rebuild with tmk-graph rather than",
        "# editing the prefixes here (IDENTIFIERS.md, HANDOFF Q7).",
        "",
    ]
    return "\n".join(header) + prefix_block(base) + "\n" + query.body.strip() + "\n"

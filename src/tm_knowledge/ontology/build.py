"""Build the knowledge graph: the pinned snapshot and the approved gold set as RDF.

Everything here is a transformation. The source graph restates what upstream
already recorded; the approved graph restates what a named reviewer already
signed. Nothing in this module decides anything, and three rules constrain how
it restates:

**Upstream's trust metadata is not flattened.** A citation is a node
(`tmk:Citation`) carrying `extraction` and `certainty`, not a bare edge. The
shortcut `tmk:citesProvision` is emitted alongside for queries that genuinely do
not care — but the shortcut is derived from the node and never the other way
round, so the two cannot disagree (CLAUDE.md rule 3).

**Practice and law are typed apart.** A Manual chunk carries
`tmk:authorityKind "practice"`; a provision carries `"law"`; a decision carries
`"decision"`. `tmk:ManualInstruction` is asserted only where an expert typed a
mention that way in `eval/gold/entities.yaml` — the class is theirs to apply,
not this module's (CLAUDE.md rule 5).

**A missing judgement stays missing.** A relationship with no modality gets no
`tmk:modality` triple. Five approved relationships are in that state and the
graph says nothing about their modality, because inferring one from the
sentence's grammar is a legal reading (guide §5.4).

Staleness is computed, not asserted: a gold record whose `source_content_hash`
no longer matches the pinned snapshot gets `tmk:isStale true` and is reported.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, RDF, RDFS, SKOS, XSD

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology.namespaces import (
    APPROVED_GRAPH,
    INFERRED_GRAPH,
    SOURCE_GRAPH,
    TMK,
    TMKC,
    TMKP,
    assertion_node,
    bind_all,
    concept_node,
    proposition_node,
    ref_node,
)
from tm_knowledge.ontology.tbox import load as load_tbox
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.worksheet import PILOT_PROVISION, ScopeRule, select
from tm_knowledge.upstream.loader import Corpus, load_corpus

__all__ = ["GRAPH_DIR", "BuildReport", "build", "write", "check"]

GRAPH_DIR = REPO_ROOT / "graph"

#: The scheme every approved concept is `skos:inScheme`. One scheme, named for
#: the pilot provision, because a second scheme would be a claim that the
#: vocabulary divides — and nobody has ruled on that.
SCHEME = URIRef(TMKC["scheme-s43"])

#: The one extraction method in the graph today. No Stage 2 run has happened
#: (ADR-0010), so every assertion here came from a person reading a passage.
ELICITATION = "expert_elicitation"


@dataclass
class BuildReport:
    """What the build saw. Printed by the CLI and asserted by the tests."""

    chunks: int = 0
    pages: int = 0
    provisions: int = 0
    cases: int = 0
    citations: int = 0
    unresolved_citations: int = 0
    concepts: int = 0
    relationships: int = 0
    mentions: int = 0
    questions: int = 0
    prohibited_uses: int = 0
    #: Gold records whose source chunk is outside the worksheet scope rule.
    out_of_scope_sources: list[str] = field(default_factory=list)
    #: Gold records whose recorded hash no longer matches the snapshot.
    stale: list[str] = field(default_factory=list)
    #: Gold records naming a source the corpus does not hold at all.
    unresolvable_sources: list[str] = field(default_factory=list)
    #: `CQ-0001:connotation` for every expected-concept label that matched no
    #: approved concept. Either the vocabulary is short a concept or the
    #: question names one by a variant nobody recorded.
    unmatched_concept_labels: list[str] = field(default_factory=list)
    triples: dict[str, int] = field(default_factory=dict)

    def lines(self) -> list[str]:
        out = [
            f"source graph   {self.triples.get('source', 0):>7} triples  "
            f"({self.chunks} chunks, {self.pages} pages, {self.provisions} provisions, "
            f"{self.cases} cases)",
            f"approved graph {self.triples.get('approved', 0):>7} triples  "
            f"({self.concepts} concepts, {self.relationships} relationships, "
            f"{self.mentions} mentions, {self.questions} questions, "
            f"{self.prohibited_uses} prohibited uses)",
            f"citations      {self.citations:>7}  of which {self.unresolved_citations} "
            f"land on nothing this corpus holds",
        ]
        for label, items in (
            ("gold records outside the worksheet scope", self.out_of_scope_sources),
            ("gold records whose source hash has moved", self.stale),
            ("gold records naming a source not held", self.unresolvable_sources),
            ("expected-concept labels matching no concept", self.unmatched_concept_labels),
        ):
            if items:
                out.append(f"{label}: {len(items)} — {', '.join(sorted(items)[:8])}")
        return out


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _lit(value: Any, datatype=None) -> Literal:
    return Literal(value, datatype=datatype) if datatype else Literal(value)


def _en(value: str) -> Literal:
    """Australian English throughout — the corpus is Australian government text."""
    return Literal(value, lang="en-AU")


def _is_case(ref: str) -> bool:
    return ref.startswith("CASE/")


def _is_manual(ref: str) -> bool:
    return ref.startswith("TMM/")


def _each(record: dict, key: str) -> Iterable[str]:
    """Values of a list field that may be absent or null. Absent is not empty:
    it is simply nothing to emit, and a null judgement stays null."""
    return record.get(key) or ()


# ---------------------------------------------------------------------------
# the source graph — deterministic from the snapshot
# ---------------------------------------------------------------------------


def _version_node(corpus: Corpus, graph: Graph) -> URIRef:
    node = URIRef(TMK[f"snapshot-{corpus.pin.commit[:12]}"])
    graph.add((node, RDF.type, TMK.DocumentVersion))
    graph.add((node, TMK.upstreamCommit, _lit(corpus.pin.commit)))
    for name, version in sorted(getattr(corpus.pin, "extractor_versions", {}).items()):
        graph.add((node, TMK.extractorVersion, _lit(f"{name}/{version}")))
    return node


def _add_citation(
    graph: Graph,
    citing: URIRef,
    citing_ref: str,
    index: int,
    kind: str,
    target_ref: str,
    *,
    extraction: str | None,
    certainty: str | None,
    mention: str | None,
    resolves: bool,
) -> URIRef:
    """One reified citation edge.

    The id is the citing ref plus an ordinal, so a rebuild over an unchanged
    snapshot mints the same node. A content-addressed id would be tidier and
    would collapse the two edges a chunk can carry to the same target with
    different extraction methods — and those two edges are exactly the evidence
    CQ-0022 asks about.
    """
    node = URIRef(TMK[f"cite/{citing_ref.replace('#', '%23')}/{kind}/{index}"])
    graph.add((node, RDF.type, TMK.Citation))
    graph.add((node, TMK.citingPassage, citing))
    graph.add((node, TMK.citedAuthority, ref_node(target_ref)))
    graph.add((node, TMK.citationResolves, _lit(resolves, XSD.boolean)))
    if extraction is not None:
        graph.add((node, TMK.extraction, _lit(extraction)))
    if certainty is not None:
        graph.add((node, TMK.certainty, _lit(certainty)))
    if mention:
        graph.add((node, TMK.mention, _lit(mention)))
    graph.add((citing, TMK.hasCitation, node))
    return node


def _build_source(corpus: Corpus, rule: ScopeRule, report: BuildReport) -> Graph:
    graph = bind_all(Graph())
    version = _version_node(corpus, graph)
    known = corpus.provisions.keys() | corpus.units.keys()

    manual = URIRef(TMK["doc/TMM"])
    graph.add((manual, RDF.type, TMK.Document))
    graph.add((manual, RDFS.label, _en("IP Australia Trade Marks Office Manual of Practice and Procedure")))
    for instrument, label in (
        ("TMA1995", "Trade Marks Act 1995"),
        ("TMR1995", "Trade Marks Regulations 1995"),
    ):
        node = URIRef(TMK[f"doc/{instrument}"])
        graph.add((node, RDF.type, TMK.Legislation))
        graph.add((node, RDFS.label, _en(label)))

    chunks = select(corpus, rule)
    report.chunks = len(chunks)
    pages_seen: set[str] = set()
    provisions_seen: set[str] = set()
    cases_seen: set[str] = set()

    for chunk in chunks:
        node = ref_node(chunk.chunk_ref)
        graph.add((node, RDF.type, TMK.Chunk))
        graph.add((node, TMK.upstreamRef, _lit(chunk.chunk_ref)))
        graph.add((node, TMK.text, _lit(chunk.text)))
        graph.add((node, TMK.contentHash, _lit(chunk.content_hash)))
        graph.add((node, TMK.ordinal, _lit(chunk.ordinal, XSD.integer)))
        graph.add((node, TMK.chunkKind, _lit(chunk.kind)))
        graph.add((node, TMK.partId, _lit(chunk.part_id)))
        graph.add((node, TMK.capturedIn, version))
        graph.add((node, DCTERMS.isPartOf, manual))
        # A fact about the document it came from, not a reading of the passage:
        # the Manual states the Registrar's practice (CLAUDE.md rule 5).
        graph.add((node, TMK.authorityKind, _lit("practice")))
        for level in chunk.heading_path:
            graph.add((node, TMK.headingPath, _lit(level)))
        graph.add((node, TMK.onPage, ref_node(chunk.page_ref)))
        pages_seen.add(chunk.page_ref)

        for index, edge in enumerate(chunk.provisions):
            resolves = edge.id in known
            _add_citation(
                graph, node, chunk.chunk_ref, index, "prov", edge.id,
                extraction=edge.extraction, certainty=edge.certainty,
                mention=edge.mention, resolves=resolves,
            )
            graph.add((node, TMK.citesProvision, ref_node(edge.id)))
            provisions_seen.add(edge.id)
            report.citations += 1
            if not resolves:
                report.unresolved_citations += 1
        for index, case in enumerate(chunk.cases):
            _add_citation(
                graph, node, chunk.chunk_ref, index, "case", case.id,
                extraction=None, certainty=None, mention=None, resolves=False,
            )
            graph.add((node, TMK.citesCase, ref_node(case.id)))
            case_node = ref_node(case.id)
            graph.add((case_node, RDF.type, TMK.JudicialDecision))
            graph.add((case_node, TMK.upstreamRef, _lit(case.id)))
            graph.add((case_node, TMK.caseCitation, _lit(case.citation)))
            graph.add((case_node, TMK.authorityKind, _lit("decision")))
            # Cited, and held nowhere in the programme. 'Which cases interpret
            # this test' is answerable; 'what did the court hold' is not (Q-11).
            graph.add((case_node, TMK.authorityStatus, TMK.NotHeld))
            cases_seen.add(case.id)
            report.citations += 1
        for index, internal in enumerate(chunk.internal_refs):
            _add_citation(
                graph, node, chunk.chunk_ref, index, "internal", internal.ref,
                extraction=internal.extraction, certainty=internal.certainty,
                mention=internal.mention, resolves=internal.ref in corpus.chunks
                or internal.ref in corpus.pages,
            )
            graph.add((node, TMK.citesPassage, ref_node(internal.ref)))
            report.citations += 1

    for page_ref in sorted(pages_seen):
        page = corpus.pages[page_ref]
        node = ref_node(page_ref)
        graph.add((node, RDF.type, TMK.Page))
        graph.add((node, TMK.upstreamRef, _lit(page_ref)))
        graph.add((node, TMK.contentHash, _lit(page.content_hash)))
        graph.add((node, TMK.partId, _lit(page.part_id)))
        graph.add((node, TMK.sourceUrl, _lit(page.url, XSD.anyURI)))
        graph.add((node, RDFS.label, _en(page.nav_title)))
        graph.add((node, TMK.capturedIn, version))
        graph.add((node, TMK.authorityKind, _lit("practice")))
        graph.add((node, DCTERMS.isPartOf, manual))
        if page.last_amended:
            graph.add((node, TMK.lastAmended, _lit(page.last_amended)))
    report.pages = len(pages_seen)

    for ref in sorted(provisions_seen):
        node = ref_node(ref)
        held = corpus.resolve_provision(ref)
        graph.add((node, TMK.upstreamRef, _lit(ref)))
        if held is None:
            # Cited by the corpus and held nowhere. Not a defect, and never
            # repaired by guessing — this is what CQ-0020 asks for (Q-06, Q-24).
            graph.add((node, TMK.authorityStatus, TMK.NotHeld))
            continue
        is_unit = ref in corpus.units
        graph.add((node, RDF.type, TMK.LegislativeUnit if is_unit else TMK.LegislativeProvision))
        graph.add((node, TMK.text, _lit(held.text)))
        graph.add((node, TMK.contentHash, _lit(held.content_hash)))
        graph.add((node, TMK.authorityKind, _lit("law")))
        graph.add((node, TMK.authorityStatus, TMK.Current))
        graph.add((node, TMK.capturedIn, version))
        instrument = ref.split("/", 1)[0]
        graph.add((node, DCTERMS.isPartOf, URIRef(TMK[f"doc/{instrument}"])))
        title = getattr(held, "title", None)
        if title:
            graph.add((node, RDFS.label, _en(title)))
        if not is_unit:
            for unit in held.units:
                unit_node = ref_node(unit.ref)
                graph.add((unit_node, RDF.type, TMK.LegislativeUnit))
                graph.add((unit_node, TMK.upstreamRef, _lit(unit.ref)))
                graph.add((unit_node, TMK.text, _lit(unit.text)))
                graph.add((unit_node, TMK.contentHash, _lit(unit.content_hash)))
                graph.add((unit_node, TMK.authorityKind, _lit("law")))
                graph.add((unit_node, TMK.ordinal, _lit(unit.ordinal, XSD.integer)))
                graph.add((unit_node, DCTERMS.isPartOf, node))
                graph.add((unit_node, TMK.capturedIn, version))
    report.provisions = len(provisions_seen)
    report.cases = len(cases_seen)
    return graph


# ---------------------------------------------------------------------------
# the approved graph — from eval/gold/, and only from there
# ---------------------------------------------------------------------------


def _provenance(
    graph: Graph, node: URIRef, record: dict, corpus: Corpus, report: BuildReport
) -> None:
    """The block every approved assertion carries (ADR-0011, CLAUDE.md rule 8).

    `approved_by` and `approved_date` come off the record and are never
    defaulted: a record without them is not approved knowledge, and the gate that
    keeps such a record out of `eval/gold/` is upstream of this function
    (ADR-0048). What this does add is the staleness check, because it is the one
    provenance fact that is a property of *now* rather than of the record.
    """
    graph.add((node, TMK.goldRecord, _lit(record["id"])))
    graph.add((node, TMK.extractionMethod, _lit(ELICITATION)))
    graph.add((node, TMK.reviewStatus, _lit("approved")))
    if record.get("approved_by"):
        graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))
    if record.get("approved_date"):
        graph.add((node, TMK.approvedDate, _lit(str(record["approved_date"]), XSD.date)))
    if record.get("tier") is not None:
        graph.add((node, TMK.tier, _lit(record["tier"], XSD.integer)))
    if record.get("notes"):
        graph.add((node, RDFS.comment, _en(record["notes"])))

    source_ref = record.get("source_ref")
    if not source_ref:
        return
    graph.add((node, TMK.sourcePassage, ref_node(source_ref)))
    span = record.get("span")
    if span:
        graph.add((node, TMK.spanStart, _lit(span[0], XSD.integer)))
        graph.add((node, TMK.spanEnd, _lit(span[1], XSD.integer)))
    recorded = record.get("source_content_hash")
    if recorded:
        graph.add((node, TMK.sourceContentHash, _lit(recorded)))
    chunk = corpus.chunks.get(source_ref)
    if chunk is None:
        report.unresolvable_sources.append(record["id"])
        return
    stale = bool(recorded) and recorded != chunk.content_hash
    graph.add((node, TMK.isStale, _lit(stale, XSD.boolean)))
    if stale:
        report.stale.append(record["id"])


def _build_concepts(graph: Graph, gold: goldset.GoldSet, report: BuildReport) -> None:
    graph.add((SCHEME, RDF.type, TMK.ConceptScheme))
    graph.add((SCHEME, RDFS.label, _en("Section 43 examination vocabulary — pilot")))
    graph.add((SCHEME, SKOS.prefLabel, _en("Section 43 examination vocabulary — pilot")))

    for record in gold["gold_concept"]:
        node = concept_node(record["id"])
        graph.add((node, RDF.type, SKOS.Concept))
        graph.add((node, RDF.type, TMK.LegalConcept))
        graph.add((node, SKOS.inScheme, SCHEME))
        graph.add((node, SKOS.prefLabel, _en(record["pref_label"])))
        graph.add((node, TMK.goldRecord, _lit(record["id"])))
        for label in _each(record, "alt_labels"):
            graph.add((node, SKOS.altLabel, _en(label)))
        # No SKOS property means "must not be confused with this", and it is the
        # most valuable field on the record. tmk:notLabel exists for it.
        for label in _each(record, "not_labels"):
            graph.add((node, TMK.notLabel, _en(label)))
        for other in _each(record, "broader"):
            graph.add((node, SKOS.broader, concept_node(other)))
        for other in _each(record, "narrower"):
            graph.add((node, SKOS.narrower, concept_node(other)))
        for other in _each(record, "related"):
            graph.add((node, SKOS.related, concept_node(other)))
        for source in _each(record, "definition_sources"):
            graph.add((node, TMK.definitionSource, ref_node(source)))
        for basis in _each(record, "legislative_basis"):
            graph.add((node, TMK.legislativeBasis, ref_node(basis)))
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))
        if record.get("approved_date"):
            graph.add((node, TMK.approvedDate, _lit(str(record["approved_date"]), XSD.date)))
        if record.get("notes"):
            graph.add((node, RDFS.comment, _en(record["notes"])))
        # Deliberately absent: skos:definition. The approved records carry
        # definition sources and no definition text, so neither does the graph.
    report.concepts = gold.count("gold_concept")


def _term(value: str) -> URIRef:
    """A relationship's subject or object, whichever kind it is.

    `GC-0001` is a concept; anything else is an upstream ref. The gold schema
    types neither field, so the id grammar is the only thing that says which —
    which is fine, because the two grammars cannot collide.
    """
    return concept_node(value) if value.startswith("GC-") else ref_node(value)


def _build_relationships(
    graph: Graph, gold: goldset.GoldSet, corpus: Corpus, report: BuildReport
) -> None:
    for record in gold["gold_relationship"]:
        node = assertion_node(record["id"])
        subject = _term(str(record["subject"]))
        predicate = URIRef(TMK[record["predicate"]])
        obj = _term(str(record["object"]))

        # Both forms, always. The direct triple is what SPARQL and OWL RL work
        # on; the assertion is what an audit works on. A shape fails if either
        # appears without the other (ADR-0058).
        graph.add((subject, predicate, obj))
        graph.add((node, RDF.type, TMK.ApprovedAssertion))
        graph.add((node, TMK.assertionSubject, subject))
        graph.add((node, TMK.assertionPredicate, predicate))
        graph.add((node, TMK.assertionObject, obj))
        graph.add((node, TMK.supportingText, _lit(record["supporting_text"])))
        # Absent means not supplied, and stays absent. Never inferred from the
        # sentence's grammar — that is a legal reading (guide §5.4).
        if record.get("modality"):
            graph.add((node, TMK.modality, _lit(record["modality"])))
        _provenance(graph, node, record, corpus, report)
    report.relationships = gold.count("gold_relationship")


def _build_mentions(
    graph: Graph, gold: goldset.GoldSet, corpus: Corpus, report: BuildReport
) -> None:
    for record in gold["gold_entity"]:
        node = assertion_node(record["id"])
        graph.add((node, RDF.type, TMK.EntityMention))
        graph.add((node, TMK.surface, _lit(record["surface"])))
        graph.add((node, TMK.mentionType, _lit(record["type"])))
        # The expert's type, applied as the class they chose. This is the only
        # place tmk:ManualInstruction and tmk:LegislativeProvision are asserted
        # over a mention, and it is asserted because a person typed it.
        if record["type"] in {"ManualInstruction", "LegislativeProvision", "LegalConcept", "Role"}:
            graph.add((node, TMK.mentionClass, URIRef(TMK[record["type"]])))
        if record.get("resolves_to"):
            graph.add((node, TMK.resolvesTo, ref_node(record["resolves_to"])))
        _provenance(graph, node, record, corpus, report)
    report.mentions = gold.count("gold_entity")


def _concept_labels(gold: goldset.GoldSet) -> dict[str, tuple[URIRef, ...]]:
    """Every approved label, folded, to the concepts carrying it.

    A tuple rather than a single node because two concepts may legitimately
    share an alt label, and collapsing that to one would be this module picking
    which concept a question meant.
    """
    index: dict[str, list[URIRef]] = {}
    for record in gold["gold_concept"]:
        node = concept_node(record["id"])
        for label in (record["pref_label"], *_each(record, "alt_labels")):
            index.setdefault(label.casefold(), []).append(node)
    return {label: tuple(nodes) for label, nodes in index.items()}


def _build_questions(graph: Graph, gold: goldset.GoldSet, report: BuildReport) -> None:
    labels = _concept_labels(gold)
    for record in gold["competency_question"]:
        node = proposition_node(record["id"])
        graph.add((node, RDF.type, TMK.CompetencyQuestion))
        graph.add((node, TMK.questionText, _en(record["question"])))
        graph.add((node, TMK.questionCategory, _lit(record["category"])))
        graph.add((node, TMK.askedBy, _lit(record["asked_by"])))
        graph.add((node, TMK.pilotInScope, _lit(bool(record["pilot_in_scope"]), XSD.boolean)))
        graph.add((node, TMK.goldRecord, _lit(record["id"])))
        sources = record.get("expected_sources") or {}
        for ref in sources.get("required") or ():
            graph.add((node, TMK.requiresSource, ref_node(ref)))
        for ref in sources.get("supporting") or ():
            graph.add((node, TMK.supportingSource, ref_node(ref)))
        if record.get("answer_shape"):
            graph.add((node, TMK.answerShape, _en(record["answer_shape"])))
        if record.get("caveats"):
            graph.add((node, TMK.caveat, _en(record["caveats"])))
        for label in _each(record, "expected_concepts"):
            graph.add((node, TMK.expectsConceptLabel, _en(label)))
            # Exact match only, against prefLabel and altLabel. An approximate
            # match would attach the question to the wrong concept, and the pair
            # it would get wrong first is the one GX-0005 is about.
            for concept in labels.get(label.casefold(), ()):
                graph.add((node, TMK.expectsConcept, concept))
            if label.casefold() not in labels:
                report.unmatched_concept_labels.append(f"{record['id']}:{label}")
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))

    for record in gold["gold_retrieval_question"]:
        node = proposition_node(record["id"])
        graph.add((node, RDF.type, TMK.RetrievalQuestion))
        graph.add((node, TMK.questionText, _en(record["question"])))
        graph.add((node, TMK.goldRecord, _lit(record["id"])))
        for ref in _each(record, "required_evidence"):
            graph.add((node, TMK.requiresSource, ref_node(ref)))
        for ref in _each(record, "required_provisions"):
            graph.add((node, TMK.requiresProvision, ref_node(ref)))
        for ref in _each(record, "required_cases"):
            graph.add((node, TMK.requiresCase, ref_node(ref)))
        if record.get("qualifications_expected"):
            graph.add((node, TMK.qualificationsExpected, _en(record["qualifications_expected"])))
        if record.get("authority_distinction_required") is not None:
            graph.add((
                node,
                TMK.authorityDistinctionRequired,
                _lit(bool(record["authority_distinction_required"]), XSD.boolean),
            ))
        for pu in _each(record, "prohibited_conclusions"):
            graph.add((node, TMK.mustNotConclude, proposition_node(pu)))
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))

    for record in gold["gold_search_question"]:
        node = proposition_node(record["id"])
        graph.add((node, RDF.type, TMK.SearchQuestion))
        graph.add((node, TMK.queryText, _en(record["query"])))
        graph.add((node, TMK.goldRecord, _lit(record["id"])))
        graph.add((
            node,
            TMK.usesManualTerminology,
            _lit(bool(record.get("uses_manual_terminology")), XSD.boolean),
        ))
        for index, judgement in enumerate(_each(record, "relevant")):
            judged = URIRef(TMKP[f"{record['id']}-relevant-{index}"])
            graph.add((node, TMK.relevantPassage, judged))
            graph.add((judged, RDF.type, TMK.RelevanceJudgement))
            graph.add((judged, TMK.judgedPassage, ref_node(judgement["ref"])))
            graph.add((judged, TMK.relevanceGrade, _lit(judgement["grade"], XSD.integer)))
        for ref in _each(record, "irrelevant_but_tempting"):
            graph.add((node, TMK.temptingButIrrelevant, ref_node(ref)))
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))

    report.questions = (
        gold.count("competency_question")
        + gold.count("gold_retrieval_question")
        + gold.count("gold_search_question")
    )


def _build_reasoning(
    graph: Graph, gold: goldset.GoldSet, corpus: Corpus, report: BuildReport
) -> None:
    for record in gold["reasoning_expectation"]:
        node = assertion_node(record["id"])
        graph.add((node, RDF.type, TMK.ReasoningExpectation))
        graph.add((node, TMK.goldRecord, _lit(record["id"])))
        for given in _each(record, "given"):
            graph.add((node, TMK.given, _term(given)))
        for inference in _each(record, "expected_inferences"):
            graph.add((node, TMK.expectedConclusion, _en(inference["conclusion"])))
            graph.add((node, TMK.inferenceKind, _lit(inference["kind"])))
            for basis in inference.get("basis") or ():
                graph.add((node, TMK.derivedFrom, _term(basis)))
        for pu in _each(record, "must_not_infer"):
            graph.add((node, TMK.mustNotConclude, proposition_node(pu)))
        if record.get("explanation_required") is not None:
            graph.add((
                node,
                TMK.explanationRequired,
                _lit(bool(record["explanation_required"]), XSD.boolean),
            ))
        if record.get("caveats"):
            graph.add((node, TMK.caveat, _en(record["caveats"])))
        _provenance(graph, node, record, corpus, report)


def _build_prohibitions(graph: Graph, gold: goldset.GoldSet, report: BuildReport) -> None:
    for record in gold["prohibited_use"]:
        node = proposition_node(record["id"])
        graph.add((node, RDF.type, TMK.ProhibitedUse))
        # Verbatim: a paraphrase of a prohibited output is not the thing being
        # prohibited, and the shapes match on this string.
        graph.add((node, TMK.prohibitedOutput, _lit(record["prohibited"])))
        graph.add((node, TMK.prohibitionKind, _lit(record["kind"])))
        graph.add((node, TMK.prohibitionReason, _en(record["why"])))
        graph.add((node, TMK.detectableBy, _lit(record["detectable_by"])))
        graph.add((node, TMK.goldRecord, _lit(record["id"])))
        for related in _each(record, "related_questions"):
            graph.add((proposition_node(related), TMK.mustNotConclude, node))
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))
    report.prohibited_uses = gold.count("prohibited_use")


def _build_approved(corpus: Corpus, gold: goldset.GoldSet, report: BuildReport) -> Graph:
    graph = bind_all(Graph())
    _build_concepts(graph, gold, report)
    _build_relationships(graph, gold, corpus, report)
    _build_mentions(graph, gold, corpus, report)
    _build_questions(graph, gold, report)
    _build_reasoning(graph, gold, corpus, report)
    _build_prohibitions(graph, gold, report)
    return graph


# ---------------------------------------------------------------------------
# the whole thing
# ---------------------------------------------------------------------------


def build(
    corpus: Corpus | None = None,
    gold: goldset.GoldSet | None = None,
    rule: ScopeRule | None = None,
) -> tuple[Dataset, BuildReport]:
    """The dataset and what the build saw.

    The TBox goes into the default graph rather than a named one: it is the
    schema every named graph is read under, and a query that had to name it
    would be a query that could forget to.
    """
    corpus = corpus or load_corpus()
    gold = gold or goldset.load()
    rule = rule or ScopeRule()
    report = BuildReport()

    dataset = Dataset()
    bind_all(dataset)

    for triple in load_tbox():
        dataset.add(triple)

    source = _build_source(corpus, rule, report)
    approved = _build_approved(corpus, gold, report)

    in_scope = {
        str(ref) for ref in source.subjects(RDF.type, TMK.Chunk)
    }
    for record_type, record in gold.all_records():
        ref = record.get("source_ref")
        if ref and _is_manual(ref) and str(ref_node(ref)) not in in_scope:
            report.out_of_scope_sources.append(record["id"])

    for graph, name in ((source, SOURCE_GRAPH), (approved, APPROVED_GRAPH)):
        target = dataset.graph(name)
        for triple in graph:
            target.add(triple)

    dataset.graph(INFERRED_GRAPH)  # declared and empty until a rule runs

    report.triples = {
        "source": len(source),
        "approved": len(approved),
        "tbox": len(load_tbox()),
    }
    return dataset, report


def write(
    dataset: Dataset | None = None, directory: Path | None = None
) -> tuple[Path, ...]:
    """Serialise the named graphs, one file each, plus the whole dataset as quads.

    Per-graph Turtle as well as the quads, because `graph/README.md` reserves
    `.ttl` for single-graph files a human is expected to read — and a reviewer
    reading `approved.ttl` should not have to parse N-Quads to do it.
    """
    directory = directory or GRAPH_DIR
    directory.mkdir(parents=True, exist_ok=True)
    if dataset is None:
        dataset, _ = build()

    written = []
    for name, filename in (
        (SOURCE_GRAPH, "source.ttl"),
        (APPROVED_GRAPH, "approved.ttl"),
        (INFERRED_GRAPH, "inferred.ttl"),
    ):
        path = directory / filename
        bind_all(dataset.graph(name)).serialize(destination=path, format="turtle")
        written.append(path)

    # N-Quads, sorted. rdflib's Turtle serialiser sorts; its N-Quads serialiser
    # emits in set-iteration order, which moves with PYTHONHASHSEED — so two
    # builds of an identical dataset produce two different 5MB files. Committed
    # (ADR-0070), that would put a 5MB diff in the history on every rebuild,
    # signifying nothing. N-Quads is one statement per line and line order
    # carries no meaning, so sorting is a canonicalisation and not a change to
    # what the file says (Q-42).
    quads = directory / "dataset.nq"
    serialised = dataset.serialize(format="nquads")
    lines = sorted(line for line in serialised.splitlines() if line.strip())
    quads.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(quads)
    return tuple(written)


def check(dataset: Dataset | None = None, directory: Path | None = None) -> tuple[str, ...]:
    """Which committed graph files no longer match a rebuild. Empty means current.

    The whole graph is committed (ADR-0070), which is only worth anything if
    what is committed is what a build produces — a stale `approved.ttl` read
    without rebuilding is a confident answer from data the repository has moved
    past. Serialisation is byte-stable across runs, so a byte comparison is a
    fair test and does not need to parse either side.
    """
    directory = directory or GRAPH_DIR
    if dataset is None:
        dataset, _ = build()
    with tempfile.TemporaryDirectory() as tmp:
        stale = []
        for fresh in write(dataset, Path(tmp)):
            committed = directory / fresh.name
            if not committed.exists():
                stale.append(f"{fresh.name}: not committed")
            elif committed.read_bytes() != fresh.read_bytes():
                stale.append(f"{fresh.name}: differs from a rebuild")
    return tuple(stale)

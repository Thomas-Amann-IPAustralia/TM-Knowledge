"""Build the knowledge graph: the snapshot and both record stores as RDF.

Everything here is a transformation. The source graph restates what upstream
already recorded; the approved graph restates what a named reviewer signed; the
authored graph restates what a machine wrote and nobody has read (ADR-0080).
Nothing in this module decides anything, and four rules constrain how it
restates:

**The two stores never mix.** They are built by the same code — one mapping,
run twice, parameterised by a `Store` — into two named graphs, and every node of
both carries `tmk:origin` and `tmk:reviewStatus` so a triple lifted out of its
graph still says what it is. An authored relationship is a `tmk:AuthoredAssertion`
and not a `tmk:ApprovedAssertion`, so no query written against the second can
reach the first by accident (ADR-0007, ADR-0079, ADR-0080).

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

from tm_knowledge.authored import store as authored_module
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology.namespaces import (
    APPROVED_GRAPH,
    AUTHORED_GRAPH,
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

__all__ = [
    "GRAPH_DIR",
    "BuildReport",
    "StoreReport",
    "Store",
    "build",
    "write",
    "check",
]

GRAPH_DIR = REPO_ROOT / "graph"

#: The scheme every approved concept is `skos:inScheme`. One scheme, named for
#: the pilot provision, because a second scheme would be a claim that the
#: vocabulary divides — and nobody has ruled on that.
SCHEME = URIRef(TMKC["scheme-s43"])

#: How a signed assertion got here: a person read a passage and said so.
ELICITATION = "expert_elicitation"

#: How an authored assertion got here. A separate value rather than a blank,
#: because `tmk:extractionMethod` is one of the six starting SHACL rules and an
#: assertion that cannot say how it was produced does not publish. When Stage 2
#: runs, its candidates will carry their own method and this one will still mean
#: what it means: a judgement a model committed to, not a span it matched.
AUTHORING = "agent_authoring"


@dataclass
class StoreReport:
    """What one record store contributed, counted apart from the other.

    Two of these, never summed (ADR-0080 consequence 3). The counts are the same
    shape for both stores on purpose: the interesting figure is always the pair,
    and a reader who sees `52 / 0` learns something a reader who sees `52`
    cannot.
    """

    concepts: int = 0
    #: Concepts sorted into one of the four groups (ADR-0071). The gap between
    #: this and `concepts` is what OQ-0001 exists to close on the signed side.
    concept_types: int = 0
    relationships: int = 0
    mentions: int = 0
    questions: int = 0
    prohibited_uses: int = 0
    #: Records whose recorded hash no longer matches the snapshot.
    stale: list[str] = field(default_factory=list)
    #: Records naming a source the corpus does not hold at all.
    unresolvable_sources: list[str] = field(default_factory=list)
    #: `CQ-0001:connotation` for every expected-concept label that matched no
    #: concept in either store and is not explained. Either the vocabulary is
    #: short a concept or the question names one by a variant nobody recorded.
    unmatched_concept_labels: list[str] = field(default_factory=list)
    #: The subset that *is* explained: the label matches no concept because a
    #: concept records it as a not-label — a term deliberately outside the
    #: vocabulary, which the question names as the boundary it is testing.
    #: Reported apart from a gap because it is the opposite of one (ADR-0075).
    boundary_concept_labels: list[str] = field(default_factory=list)

    # No `total`. Summing *within* one store would be harmless and summing
    # across two would not, and a `total` on this class is one attribute access
    # away from the second. The figures are reported as a pair everywhere
    # (ADR-0080 consequence 3).


@dataclass
class BuildReport:
    """What the build saw. Printed by the CLI and asserted by the tests.

    The flat record counters — `concepts`, `relationships` and the rest — are the
    **signed** store's, and they read that way because that is what they have
    always meant. The authored store's are under `authored`, and there is no
    attribute anywhere on this class that adds the two: the moment one exists,
    something prints it.
    """

    chunks: int = 0
    pages: int = 0
    provisions: int = 0
    cases: int = 0
    citations: int = 0
    unresolved_citations: int = 0
    #: Gold records whose source chunk is outside the worksheet scope rule.
    out_of_scope_sources: list[str] = field(default_factory=list)
    triples: dict[str, int] = field(default_factory=dict)
    #: What `eval/gold/` contributed. The flat properties below read from here.
    approved: StoreReport = field(default_factory=StoreReport)
    #: What `authored/` contributed. Never added to the above.
    authored: StoreReport = field(default_factory=StoreReport)
    #: Authored records the store refused — envelope did not validate. Named
    #: rather than counted, because a refused record is one somebody has to fix
    #: and a number is not something you can act on.
    authored_refused: list[str] = field(default_factory=list)

    # The signed store's counters, under the names they have always had. Read
    # only: a caller that needs to set one is building a store, and building a
    # store goes through `StoreReport`.

    @property
    def concepts(self) -> int:
        return self.approved.concepts

    @property
    def concept_types(self) -> int:
        return self.approved.concept_types

    @property
    def relationships(self) -> int:
        return self.approved.relationships

    @property
    def mentions(self) -> int:
        return self.approved.mentions

    @property
    def questions(self) -> int:
        return self.approved.questions

    @property
    def prohibited_uses(self) -> int:
        return self.approved.prohibited_uses

    @property
    def stale(self) -> list[str]:
        return self.approved.stale

    @property
    def unresolvable_sources(self) -> list[str]:
        return self.approved.unresolvable_sources

    @property
    def unmatched_concept_labels(self) -> list[str]:
        return self.approved.unmatched_concept_labels

    @property
    def boundary_concept_labels(self) -> list[str]:
        return self.approved.boundary_concept_labels

    def lines(self) -> list[str]:
        out = [
            f"source graph   {self.triples.get('source', 0):>7} triples  "
            f"({self.chunks} chunks, {self.pages} pages, {self.provisions} provisions, "
            f"{self.cases} cases)",
            f"approved graph {self.triples.get('approved', 0):>7} triples  "
            f"({self.concepts} concepts, {self.relationships} relationships, "
            f"{self.mentions} mentions, {self.questions} questions, "
            f"{self.prohibited_uses} prohibited uses) — signed by a named expert",
            f"authored graph {self.triples.get('authored', 0):>7} triples  "
            f"({self.authored.concepts} concepts, {self.authored.relationships} "
            f"relationships, {self.authored.mentions} mentions, "
            f"{self.authored.questions} questions, "
            f"{self.authored.prohibited_uses} prohibited uses) — "
            f"**validated by nobody**",
            f"citations      {self.citations:>7}  of which {self.unresolved_citations} "
            f"land on nothing this corpus holds",
            # Both figures count typings of the *signed* concepts, because that
            # is what a typing points at: `concept-types.yaml` names a GC- id,
            # and every GC- id in the project is in eval/gold/. The denominator
            # is therefore `self.concepts` for both halves — an earlier version
            # divided the authored half by `authored.concepts`, which is the
            # number of concepts a machine wrote, is structurally 0, and made
            # the line read "45 of 0" (Q-50).
            f"concept types  {self.concept_types:>7}  of {self.concepts} concepts "
            f"sorted into a group by a person; {self.authored.concept_types} of "
            f"{self.concepts} by a machine, validated by nobody",
        ]
        for label, items in (
            ("gold records outside the worksheet scope", self.out_of_scope_sources),
            ("gold records whose source hash has moved", self.stale),
            ("gold records naming a source not held", self.unresolvable_sources),
            ("expected-concept labels matching no concept", self.unmatched_concept_labels),
            (
                "expected-concept labels that name a boundary, not a gap",
                self.boundary_concept_labels,
            ),
            ("authored records whose source hash has moved", self.authored.stale),
            (
                "authored records naming a source not held",
                self.authored.unresolvable_sources,
            ),
            (
                "authored expected-concept labels matching no concept",
                self.authored.unmatched_concept_labels,
            ),
            (
                "authored records refused — the envelope does not validate",
                self.authored_refused,
            ),
        ):
            if items:
                out.append(f"{label}: {len(items)} — {', '.join(sorted(items)[:8])}")
        return out


# ---------------------------------------------------------------------------
# the two stores
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Store:
    """One record store, and everything the graph must say about its records.

    The builders below are written once and run twice. What changes between the
    two runs is not the mapping — an authored concept is the same shape as a
    signed one — but what the graph asserts *about* each node: which class an
    assertion gets, which named graph it lands in, what its review status is,
    and who wrote it. Putting that in one object is what stops the second run
    being a second copy of the mapping, which would drift (CLAUDE.md §5: there
    is exactly one of each reader).
    """

    #: `approved` or `authored`. Stamped on every node as `tmk:origin`.
    name: str
    #: A `goldset.GoldSet` or an `authored.store.AuthoredSet`. Both answer
    #: `store[record_type]` with bare record dicts.
    records: Any
    #: The named graph these nodes are written into.
    graph_name: URIRef
    #: The class a relationship assertion gets. The line between the two stores
    #: in RDF: a query asking for `tmk:ApprovedAssertion` cannot reach an
    #: authored one by accident.
    assertion_class: URIRef
    #: record id -> the `authored:` envelope, for the authored store. Empty for
    #: the signed one, which carries its provenance on the record itself.
    envelopes: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def signed(self) -> bool:
        return self.name == "approved"

    def envelope(self, record_id: str) -> dict[str, Any]:
        return self.envelopes.get(record_id, {})

    def review_status(self, record_id: str) -> str:
        """What the graph says about this record's review state.

        `approved` for the signed store — every record in it carries a name and
        a date, and `eval/gold/` holds nothing else. Otherwise whatever the
        envelope says, which is `unreviewed` unless a transcription has moved
        it, and never defaulted: a record that claims nothing is refused by the
        store long before it reaches here.
        """
        if self.signed:
            return "approved"
        return str(self.envelope(record_id).get("review_status") or "unreviewed")


def approved_store(gold: goldset.GoldSet) -> Store:
    return Store(
        name="approved",
        records=gold,
        graph_name=APPROVED_GRAPH,
        assertion_class=TMK.ApprovedAssertion,
    )


def authored_store(authored: authored_module.AuthoredSet) -> Store:
    return Store(
        name="authored",
        records=authored,
        graph_name=AUTHORED_GRAPH,
        assertion_class=TMK.AuthoredAssertion,
        envelopes={
            entry.record_id: entry.envelope
            for entry in authored.all_entries()
            if entry.sound and entry.envelope
        },
    )


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


def _origin(graph: Graph, node: URIRef, record: dict, store: Store) -> None:
    """Where this node came from, on the node itself.

    Every node of both stores, not only the assertions. The named graph is the
    governance boundary and this is the belt to its braces: a triple lifted out
    of `authored.ttl` into a report, a prompt or an evidence pack still says
    what it is. That is what replaced the Tier 3 gate when ADR-0082 removed it —
    the honesty burden moved onto every surface that serves the content, and a
    surface can only carry a label the data gives it.
    """
    identifier = str(record.get("id") or "")
    graph.add((node, TMK.origin, _lit(store.name)))
    graph.add((node, TMK.reviewStatus, _lit(store.review_status(identifier))))
    if store.signed:
        return
    envelope = store.envelope(identifier)
    if envelope.get("authored_by"):
        graph.add((node, TMK.authoredBy, _lit(envelope["authored_by"])))
    if envelope.get("authored_date"):
        graph.add((node, TMK.authoredDate, _lit(str(envelope["authored_date"]), XSD.date)))
    if envelope.get("authoring_basis"):
        graph.add((node, TMK.authoringBasis, _lit(envelope["authoring_basis"])))
    if envelope.get("reasoning"):
        graph.add((node, TMK.authoringReasoning, _en(envelope["reasoning"])))
    if envelope.get("expert_should_check"):
        graph.add((node, TMK.expertShouldCheck, _en(envelope["expert_should_check"])))
    if envelope.get("supersedes_rejected"):
        graph.add((node, TMK.supersedesRejected, _lit(envelope["supersedes_rejected"])))
    if envelope.get("confidence") is not None:
        graph.add((node, TMK.confidence, _lit(float(envelope["confidence"]))))
    for item in envelope.get("evidence") or ():
        if isinstance(item, dict) and isinstance(item.get("ref"), str):
            graph.add((node, TMK.sourcePassage, ref_node(item["ref"])))


def _provenance(
    graph: Graph,
    node: URIRef,
    record: dict,
    store: Store,
    corpus: Corpus,
    counts: StoreReport,
) -> None:
    """The block every assertion carries (ADR-0011, CLAUDE.md rule 8).

    `approved_by` and `approved_date` come off the record and are never
    defaulted: a record without them is not approved knowledge, and the gate that
    keeps such a record out of `eval/gold/` is upstream of this function
    (ADR-0048). An authored record has neither, by construction and by check, so
    the two lines below simply do not fire for it — which is the correct
    difference and not a special case.

    What this adds is the staleness check, because it is the one provenance fact
    that is a property of *now* rather than of the record.
    """
    graph.add((node, TMK.goldRecord, _lit(record["id"])))
    graph.add((node, TMK.extractionMethod, _lit(ELICITATION if store.signed else AUTHORING)))
    _origin(graph, node, record, store)
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
        counts.unresolvable_sources.append(record["id"])
        return
    stale = bool(recorded) and recorded != chunk.content_hash
    graph.add((node, TMK.isStale, _lit(stale, XSD.boolean)))
    if stale:
        counts.stale.append(record["id"])


def _build_concepts(graph: Graph, store: Store, counts: StoreReport) -> None:
    # Declared by whichever store contributes a concept, and by neither when
    # neither does. A store with no concepts writes an empty graph rather than a
    # graph holding only a scheme nobody is in — `authored graph 0 triples` is a
    # true statement about a repo that has authored nothing, and `3 triples` is
    # a puzzle.
    if store.records.count("gold_concept"):
        graph.add((SCHEME, RDF.type, TMK.ConceptScheme))
        graph.add((SCHEME, RDFS.label, _en("Section 43 examination vocabulary — pilot")))
        graph.add(
            (SCHEME, SKOS.prefLabel, _en("Section 43 examination vocabulary — pilot"))
        )

    for record in store.records["gold_concept"]:
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
        # Deliberately absent: skos:definition. The records carry definition
        # sources and no definition text, so neither does the graph.
        _origin(graph, node, record, store)
    counts.concepts = store.records.count("gold_concept")
    _apply_concept_types(graph, store, counts)


#: `concept_type.type` -> the class it asserts. `none_of_these` is deliberately
#: absent: it is a real answer about the taxonomy and it asserts no class, so a
#: concept typed that way stays a bare `tmk:LegalConcept` and is counted as
#: sorted rather than as waiting.
CONCEPT_CLASSES: dict[str, str] = {
    "ground_of_refusal": "GroundOfRefusal",
    "legal_test": "LegalTest",
    "relevant_factor": "RelevantFactor",
    "exception": "Exception",
}


def _apply_concept_types(graph: Graph, store: Store, counts: StoreReport) -> None:
    """Put each typed concept into the class its type record names.

    The four classes were declared and empty from S010 until somebody ruled.
    They fill from a `concept-types.yaml` record and from nothing else — never
    from a label, a heuristic or a passage this module read. A concept with no
    type record stays a bare `tmk:LegalConcept`, and that absence is reported
    rather than defaulted (ADR-0071).

    The typing assertion carries the origin of the record that made it, so a
    concept a person signed and a machine typed says both things about itself.
    That combination is now the ordinary case (ADR-0079) and the graph has to be
    able to state it without either half swallowing the other.
    """
    typed = 0
    for record in store.records["concept_type"]:
        group = record.get("type", "")
        if not group:
            continue
        class_name = CONCEPT_CLASSES.get(group)
        node = concept_node(record["concept"])
        typing = assertion_node(record["id"])
        # `none_of_these` reaches here with no class and asserts none. What it
        # does assert is that somebody looked and said the four groups do not
        # fit — so the typing node, its record and its origin are all written,
        # and the concept stays a bare `tmk:LegalConcept`. Skipping the record
        # outright would make "sorted into none_of_these" and "never sorted"
        # the same state in the graph, and they are the opposite of each other
        # (ADR-0093, Q-50).
        if class_name is not None:
            graph.add((node, RDF.type, URIRef(TMK[class_name])))
        graph.add((node, TMK.typedBy, typing))
        graph.add((typing, TMK.goldRecord, _lit(record["id"])))
        graph.add((typing, TMK.conceptGroup, _lit(group)))
        _origin(graph, typing, record, store)
        typed += 1
    counts.concept_types = typed


def _term(value: str) -> URIRef:
    """A relationship's subject or object, whichever kind it is.

    `GC-0001` is a concept, `GE-0010` is an entity mention, and anything else is
    an upstream ref. The gold schema types none of the three, so the id grammar
    is the only thing that says which — which is fine, because the grammars
    cannot collide.

    **Why a mention may be a term** (ADR-0073). The owner asked, on OQ-0015,
    whether a glossary captures the relationship between an examiner and a
    registrar, and said to adopt a Must/May predicate if it does not. It does
    not: a glossary holds one entry per term, and "an examiner must consult a
    team leader before accepting on doubt" is a normative relation between two
    roles. The Must/May predicate already exists — `tmk:modality`, carrying
    `must` | `may` | `should` on any approved relationship — so what was missing
    was not the modality but the *subject*: there was no way to make a
    relationship be about a role at all, because a role is an entity mention and
    only concepts and refs were terms.

    Nothing here writes such a relationship. It makes one expressible, so an
    expert can sign one.
    """
    if value.startswith("GC-"):
        return concept_node(value)
    if value.startswith("GE-"):
        return assertion_node(value)
    return ref_node(value)


def _build_relationships(
    graph: Graph, store: Store, corpus: Corpus, counts: StoreReport
) -> None:
    for record in store.records["gold_relationship"]:
        node = assertion_node(record["id"])
        subject = _term(str(record["subject"]))
        predicate = URIRef(TMK[record["predicate"]])
        obj = _term(str(record["object"]))

        # Both forms, always. The direct triple is what SPARQL and OWL RL work
        # on; the assertion is what an audit works on. A shape fails if either
        # appears without the other (ADR-0058).
        #
        # The direct triple is identical whichever store the record came from,
        # and it lands in that store's named graph. That is the separation
        # working as designed: a query over the approved graph sees only signed
        # edges, a query over the union sees both, and neither can be written by
        # accident (ADR-0007, ADR-0080).
        graph.add((subject, predicate, obj))
        graph.add((node, RDF.type, store.assertion_class))
        graph.add((node, TMK.assertionSubject, subject))
        graph.add((node, TMK.assertionPredicate, predicate))
        graph.add((node, TMK.assertionObject, obj))
        graph.add((node, TMK.supportingText, _lit(record["supporting_text"])))
        # Absent means not supplied, and stays absent. Never inferred from the
        # sentence's grammar — that is a legal reading (guide §5.4).
        if record.get("modality"):
            graph.add((node, TMK.modality, _lit(record["modality"])))
        _provenance(graph, node, record, store, corpus, counts)
    counts.relationships = store.records.count("gold_relationship")


def _build_mentions(
    graph: Graph, store: Store, corpus: Corpus, counts: StoreReport
) -> None:
    for record in store.records["gold_entity"]:
        node = assertion_node(record["id"])
        graph.add((node, RDF.type, TMK.EntityMention))
        graph.add((node, TMK.surface, _lit(record["surface"])))
        graph.add((node, TMK.mentionType, _lit(record["type"])))
        # The type on the record, applied as the class it names. This is the
        # only place tmk:ManualInstruction and tmk:LegislativeProvision are
        # asserted over a mention. On a signed record a person typed it; on an
        # authored one a model did, and the node's tmk:origin says which.
        if record["type"] in {"ManualInstruction", "LegislativeProvision", "LegalConcept", "Role"}:
            graph.add((node, TMK.mentionClass, URIRef(TMK[record["type"]])))
        if record.get("resolves_to"):
            graph.add((node, TMK.resolvesTo, ref_node(record["resolves_to"])))
        _provenance(graph, node, record, store, corpus, counts)
    counts.mentions = store.records.count("gold_entity")


def _not_labels(*stores: Store) -> dict[str, tuple[URIRef, ...]]:
    """Every *not*-label in either store, folded, to the concepts that exclude it.

    `not_labels` is the field the schema calls the most valuable on the record:
    the forms that look similar and are deliberately not this concept. A
    question's expected concept matching one of these is therefore not a hole in
    the vocabulary — it is the vocabulary saying, in a record somebody signed,
    that the term belongs somewhere else.

    The owner ruled exactly that on OQ-0002: *"It belongs to section 44 — keep it
    out, the question is using it as a boundary marker"* (ADR-0075).
    """
    index: dict[str, list[URIRef]] = {}
    for store in stores:
        for record in store.records["gold_concept"]:
            node = concept_node(record["id"])
            for label in _each(record, "not_labels"):
                index.setdefault(label.casefold(), []).append(node)
    return {label: tuple(nodes) for label, nodes in index.items()}


def _concept_labels(*stores: Store) -> dict[str, tuple[URIRef, ...]]:
    """Every label in either store, folded, to the concepts carrying it.

    A tuple rather than a single node because two concepts may legitimately
    share an alt label, and collapsing that to one would be this module picking
    which concept a question meant.

    **Both stores, deliberately, and this is the one place the separation is
    crossed on purpose.** The index answers "does the vocabulary have a concept
    for this label", and after ADR-0079 the vocabulary is in two directories. A
    signed question naming a label only an authored concept carries is not a
    hole in the vocabulary, and reporting it as one would send an expert looking
    for something that is already written. What the crossing does not do is
    launder anything: the *edge* it produces lands in the named graph of the
    store whose question drew it, and the concept it points at carries its own
    origin.
    """
    index: dict[str, list[URIRef]] = {}
    for store in stores:
        for record in store.records["gold_concept"]:
            node = concept_node(record["id"])
            for label in (record["pref_label"], *_each(record, "alt_labels")):
                index.setdefault(label.casefold(), []).append(node)
    return {label: tuple(nodes) for label, nodes in index.items()}


def _build_questions(
    graph: Graph,
    store: Store,
    counts: StoreReport,
    labels: dict[str, tuple[URIRef, ...]],
    excluded: dict[str, tuple[URIRef, ...]],
) -> None:
    for record in store.records["competency_question"]:
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
                # A label no concept carries, but one an approved concept
                # explicitly excludes, is the question naming the boundary it
                # tests. Recorded as such rather than counted as a missing
                # concept, which is what it looked like until OQ-0002 settled it.
                boundary = excluded.get(label.casefold(), ())
                if boundary:
                    graph.add((node, TMK.expectsBoundaryLabel, _en(label)))
                    for concept in boundary:
                        graph.add((node, TMK.testsBoundaryOf, concept))
                    counts.boundary_concept_labels.append(f"{record['id']}:{label}")
                else:
                    counts.unmatched_concept_labels.append(f"{record['id']}:{label}")
        _origin(graph, node, record, store)
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))

    for record in store.records["gold_retrieval_question"]:
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
        _origin(graph, node, record, store)
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))

    for record in store.records["gold_search_question"]:
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
        _origin(graph, node, record, store)
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))

    counts.questions = (
        store.records.count("competency_question")
        + store.records.count("gold_retrieval_question")
        + store.records.count("gold_search_question")
    )


def _build_reasoning(
    graph: Graph, store: Store, corpus: Corpus, counts: StoreReport
) -> None:
    for record in store.records["reasoning_expectation"]:
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
        _provenance(graph, node, record, store, corpus, counts)


def _build_prohibitions(graph: Graph, store: Store, counts: StoreReport) -> None:
    for record in store.records["prohibited_use"]:
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
        _origin(graph, node, record, store)
        if record.get("approved_by"):
            graph.add((node, TMK.approvedBy, _lit(record["approved_by"])))
    counts.prohibited_uses = store.records.count("prohibited_use")


def _build_store(
    corpus: Corpus,
    store: Store,
    counts: StoreReport,
    labels: dict[str, tuple[URIRef, ...]],
    excluded: dict[str, tuple[URIRef, ...]],
) -> Graph:
    """One store's records as RDF. Run once per store, over the same mapping.

    There is deliberately no `_build_authored` beside this. A second builder
    would be a second answer to "what does a concept look like in RDF", and the
    two would drift — which is the failure the repo already fenced against by
    having exactly one ref parser, one IRI minter and one gold-set reader
    (CLAUDE.md §5). What differs between the stores is carried by `store`, and
    is limited to what the graph asserts *about* each node.
    """
    graph = bind_all(Graph())
    _build_concepts(graph, store, counts)
    _build_relationships(graph, store, corpus, counts)
    _build_mentions(graph, store, corpus, counts)
    _build_questions(graph, store, counts, labels, excluded)
    _build_reasoning(graph, store, corpus, counts)
    _build_prohibitions(graph, store, counts)
    return graph


# ---------------------------------------------------------------------------
# the whole thing
# ---------------------------------------------------------------------------


def build(
    corpus: Corpus | None = None,
    gold: goldset.GoldSet | None = None,
    authored: authored_module.AuthoredSet | None = None,
    rule: ScopeRule | None = None,
) -> tuple[Dataset, BuildReport]:
    """The dataset and what the build saw.

    The TBox goes into the default graph rather than a named one: it is the
    schema every named graph is read under, and a query that had to name it
    would be a query that could forget to.

    Both stores are built, into two named graphs (ADR-0080). An empty
    `authored/` therefore produces an empty-but-declared `authored` graph, which
    is the honest state of a repo that has authored nothing yet — and one that
    stops being empty without any code changing.
    """
    corpus = corpus or load_corpus()
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_module.load()
    rule = rule or ScopeRule()
    report = BuildReport()
    report.authored_refused = [entry.record_id for entry in authored.refused]

    dataset = Dataset()
    bind_all(dataset)

    for triple in load_tbox():
        dataset.add(triple)

    signed = approved_store(gold)
    machine = authored_store(authored)

    # One label index over both stores, built before either graph, because the
    # question "does the vocabulary hold this label" spans them (see
    # `_concept_labels`).
    labels = _concept_labels(signed, machine)
    excluded = _not_labels(signed, machine)

    source = _build_source(corpus, rule, report)
    approved = _build_store(corpus, signed, report.approved, labels, excluded)
    authored_graph = _build_store(corpus, machine, report.authored, labels, excluded)

    in_scope = {
        str(ref) for ref in source.subjects(RDF.type, TMK.Chunk)
    }
    for record_type, record in gold.all_records():
        ref = record.get("source_ref")
        if ref and _is_manual(ref) and str(ref_node(ref)) not in in_scope:
            report.out_of_scope_sources.append(record["id"])

    for graph, name in (
        (source, SOURCE_GRAPH),
        (approved, signed.graph_name),
        (authored_graph, machine.graph_name),
    ):
        target = dataset.graph(name)
        for triple in graph:
            target.add(triple)

    dataset.graph(INFERRED_GRAPH)  # declared and empty until a rule runs

    report.triples = {
        "source": len(source),
        "approved": len(approved),
        "authored": len(authored_graph),
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
        (AUTHORED_GRAPH, "authored.ttl"),
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
    # what the file says (Q-45).
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

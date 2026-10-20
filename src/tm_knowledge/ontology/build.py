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
`tmk:authorityKind "practice"` and is a `tmk:ManualPassage`, by the same
structural rule (review F1); a provision carries `"law"`; a decision carries
`"decision"` and is administrative, judicial or unclassified by its case id's
series (review C7). `tmk:ManualInstruction` is asserted only where an expert
typed a mention that way in `eval/gold/entities.yaml` — the class is theirs to
apply, not this module's (CLAUDE.md rule 5).

**A missing judgement stays missing.** A relationship with no modality gets no
`tmk:modality` triple. Five approved relationships are in that state and the
graph says nothing about their modality, because inferring one from the
sentence's grammar is a legal reading (guide §5.4).

Staleness is computed, not asserted: a gold record whose `source_content_hash`
no longer matches the pinned snapshot gets `tmk:isStale true` and is reported.
"""

from __future__ import annotations

from decimal import Decimal

import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Container, Iterable

from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, PROV, RDF, RDFS, SKOS, TIME, XSD

from tm_knowledge.authored import corrections as corrections_module
from tm_knowledge.authored import definitions as definitions_module
from tm_knowledge.authored import procedure as procedure_module
from tm_knowledge.authored import store as authored_module
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.ontology import conditions
from tm_knowledge.ontology import decisions as decisions_module
from tm_knowledge.ontology import hygiene
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
    element_node,
    evidence_node,
    proposition_node,
    ref_node,
)
from tm_knowledge.ontology.tbox import load as load_tbox
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.worksheet import cited_refs, select_evidenced
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

#: The scheme every concept is `skos:inScheme`. One scheme, because a second
#: would be a claim that the vocabulary divides, and nobody has ruled on that.
#: The IRI keeps the name it was minted under when the work was section 43 alone:
#: an identifier does not change when its label does (`docs/IDENTIFIERS.md` §3).
#: The label said "Section 43 … pilot" until the review response's F12.
SCHEME = URIRef(TMKC["scheme-s43"])

#: The scheme's label. The whole Manual has been in scope since ADR-0081.
SCHEME_LABEL = "Trade marks examination vocabulary"

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
    #: Concepts sorted into one of the kinds (ADR-0071, widened by
    #: ADR-0098 and ADR-0124). The gap between this and `concepts` is what OQ-0001 exists to
    #: close on the signed side.
    concept_types: int = 0
    relationships: int = 0
    mentions: int = 0
    questions: int = 0
    prohibited_uses: int = 0
    #: Corrections to signed records stated in this store's graph (ADR-0122).
    #: Always 0 for the approved store: a correction is machine-written.
    corrections: int = 0
    #: Concepts this store's graph defines (ADR-0137). Always 0 for the approved
    #: store: every definition is machine-written.
    definitions: int = 0
    #: Structured tests and process templates (ADR-0142). Always 0 for the approved store.
    procedures: int = 0
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
    #: Gold records whose source chunk is not in the source graph. Since
    #: ADR-0097 this should always be empty by construction — the source graph is
    #: selected *from* what the records cite — so a non-empty list means a record
    #: names a Manual ref the snapshot does not hold, which is a different and
    #: worse problem than being outside a fence.
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
    #: Corrections refused at load (ADR-0122) — reported, never applied.
    corrections_refused: list[str] = field(default_factory=list)
    #: Definitions refused at load (ADR-0137) — reported, never stated.
    definitions_refused: list[str] = field(default_factory=list)

    # The signed store's counters, under the names they have always had. Read
    # only: a caller that needs to set one is building a store, and building a
    # store goes through `StoreReport`.

    @property
    def concepts(self) -> int:
        return self.approved.concepts

    @property
    def total_concepts(self) -> int:
        """Concepts in the project, both stores.

        The one place the two counts are added, and it is legitimate: ids are
        one sequence across the stores, so this is a count of distinct concepts
        rather than a merge of signed and authored knowledge. ADR-0080
        consequence 3 forbids presenting authored records *as* signed ones — it
        does not forbid counting how many concepts exist. Every line that uses
        this prints the split beside it.
        """
        return self.approved.concepts + self.authored.concepts

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
            # The denominator is every concept in the project, both stores, because
            # that is what a typing points at: `concept-types.yaml` names a GC- id
            # and there is one GC- sequence across the two stores (ADR-0080 c1).
            #
            # It has now been wrong twice in opposite directions, which is why
            # this comment is longer than the line. First it divided the authored
            # half by `authored.concepts` — the count of concepts a *machine*
            # wrote — which was structurally 0 and printed "45 of 0" (Q-50). Then
            # it divided both halves by `self.concepts`, the signed count, which
            # was right until a machine authored concepts of its own and printed
            # "130 of 52". Read a counter before you make it non-zero.
            f"concept types  {self.concept_types:>7}  of {self.total_concepts} "
            f"concepts sorted into a group by a person; "
            f"{self.authored.concept_types} of {self.total_concepts} by a machine, "
            "validated by nobody "
            f"({self.concepts} of those concepts are signed, "
            f"{self.authored.concepts} authored)",
        ]
        for label, items in (
            (
                "gold records whose source chunk is not in the graph — since "
                "ADR-0097 this means the ref is not in the snapshot at all",
                self.out_of_scope_sources,
            ),
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
    #: signed relationship id -> the authored relationship serving in its place
    #: (ADR-0122). The signed assertion stays, as history; its direct triple does not.
    replaced: dict[str, str] = field(default_factory=dict)
    #: (narrower, broader) -> the written reason a "kind of" link stands beside a
    #: not-label (review D4, ADR-0125). Authored store only.
    affirmed: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    #: The pinned snapshot, against which each evidence anchor's hash is checked.
    #: None only for a store built without one, whose anchors then say nothing
    #: about staleness or version (and fail the anchor shape, as they should).
    corpus: Any = None

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


def approved_store(gold: goldset.GoldSet, replaced: dict[str, str] | None = None) -> Store:
    return Store(
        name="approved",
        records=gold,
        graph_name=APPROVED_GRAPH,
        assertion_class=TMK.ApprovedAssertion,
        replaced=dict(replaced or {}),
    )


def authored_store(authored: authored_module.AuthoredSet, corpus: Corpus | None = None) -> Store:
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
        affirmed=hygiene.affirmations(authored.root),
        corpus=corpus,
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


def _version_iri(corpus: Corpus) -> URIRef:
    return URIRef(TMK[f"snapshot-{corpus.pin.commit[:12]}"])


def _held(corpus: Corpus, ref: str) -> Any:
    """The passage, page, provision or unit a ref names in the snapshot, or None."""
    return (
        corpus.chunks.get(ref) or corpus.provisions.get(ref)
        or corpus.units.get(ref) or corpus.pages.get(ref)
    )


def _compilation(graph: Graph, instrument_node: URIRef, code: str, held: Any) -> URIRef:
    """The held compilation as a node of its own (A03): the enduring instrument apart from
    its versioned text, and when the text was law apart from when it was read. The
    interval's end is not stated: it is not known until the next compilation is held."""
    node = URIRef(TMK[f"doc/{code}/compilation/{held.compilation_number}"])
    interval = URIRef(f"{node}/in-force")
    begins = URIRef(f"{interval}/begins")
    graph.add((instrument_node, TMK.heldCompilation, node))
    if held.title_id:
        graph.add((instrument_node, TMK.registerTitleId, _lit(held.title_id)))
    graph.add((node, RDF.type, TMK.Compilation))
    graph.add((node, RDFS.label, _en(f"{held.name}, compilation {held.compilation_number}")))
    graph.add((node, TMK.compilationOf, instrument_node))
    graph.add((node, TMK.compilationNumber, _lit(held.compilation_number)))
    graph.add((node, TMK.registerId, _lit(held.register_id)))
    graph.add((node, TMK.capturedAt, _lit(held.captured_at)))
    if held.status is not None and held.has_unincorporated_amendments is not None:
        current = held.status == "InForce" and not held.has_unincorporated_amendments
        graph.add((node, TMK.currentAtCapture, _lit(current, XSD.boolean)))
    graph.add((node, TMK.inForceDuring, interval))
    graph.add((interval, RDF.type, TIME.Interval))
    graph.add((interval, TIME.hasBeginning, begins))
    graph.add((begins, RDF.type, TIME.Instant))
    graph.add((begins, TIME.inXSDDate, _lit(held.compilation_start, XSD.date)))
    return node


def _version_node(corpus: Corpus, graph: Graph) -> URIRef:
    node = _version_iri(corpus)
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


def source_chunks(
    corpus: Corpus,
    gold: goldset.GoldSet,
    authored: authored_module.AuthoredSet,
    extra: Iterable[tuple[str, dict, dict | None]] = (),
) -> tuple:
    """Which passages of the Manual the source graph holds.

    **This is where the section 43 boundary stood longest and mattered most.**
    Until ADR-0097 the source graph was built over `select(corpus, ScopeRule())`
    — every chunk citing `TMA1995/s43`, plus page-mates, 216 of 2,460 — so an
    approved record naming a passage outside that fence had nothing in the graph
    to attach to, and the build reported it under "gold records outside the
    worksheet scope". The owner withdrew the boundary; the graph kept it.

    The rule now is: **every Manual passage any record cites, plus its
    page-mates.** It selects on what this repository has said something about
    rather than on which provision a passage happens to mention. Three
    consequences, and the third is the reason it is a rule and not a fence:

    1. It has no boundary in it. No section, no Part, no exclusion list.
    2. It grows as knowledge is authored. Authoring a concept about Part 22 puts
       Part 22's passages in the graph, with no code change and no re-decision.
    3. It never needs re-deciding when scope changes, because it is not a scope
       rule — scope is the whole Manual (ADR-0081) and this is a question about
       what the graph is *for*.

    **Every chunk carrying an `ambiguous` provision edge is in, cited or not.**
    That is not a second scope rule, it is Q-07: upstream refused to choose
    between instruments on purpose, and an ambiguous edge is a reason to put a
    passage in front of a human, never a reason to drop one. Under the citation
    fence they arrived by accident, because the ones near section 43 happened to
    be selected. Making the rule evidence-driven would otherwise have dropped
    one of the two ambiguous edges to `TMA1995/s43` — dropped for not being
    spoken about rather than for being ambiguous, which is a distinction the
    graph could not show anybody. 39 chunks corpus-wide carry one.

    **What it costs, stated because it is a real cost.** A source graph over the
    whole corpus would be about 7.7 times the text and would put `dataset.nq`
    somewhere near 40MB, regenerated on every build and committed on every
    commit (ADR-0070, OQ-0005). This rule holds a little over 400 chunks where
    the fence held 216, and some of the fence's chunks leave: passages that cite
    section 43 and that no record in either store says anything about. They are
    not excluded — nothing is excluded — they are simply not yet spoken about,
    and the moment a record cites one it is back.
    """
    refs = cited_refs(
        [
            *((record_type, record, None) for record_type, record in gold.all_records()),
            *(
                (entry.record_type, entry.record, entry.envelope)
                for entry in authored.all_entries()
                if entry.sound
            ),
        ]
    )
    # Corrections and definitions (`extra`): their own readers, and no gold
    # schema to name their ref fields, so their evidence and `source_ref`.
    refs |= _evidence_refs(None, extra)
    refs |= {
        chunk.chunk_ref
        for chunk in corpus.chunks.values()
        if any(edge.needs_a_human for edge in chunk.provisions)
    }
    return select_evidenced(corpus, refs)


def _evidence_refs(
    authored: authored_module.AuthoredSet | None,
    extra: Iterable[tuple[str, dict, dict | None]] = (),
) -> set[str]:
    """Every ref an authored record's evidence names, and a correction's or
    definition's `source_ref`."""
    found: set[str] = set()
    envelopes = [entry.envelope for entry in authored.all_entries() if entry.sound] if authored else []
    for _, record, envelope in extra:
        envelopes.append(envelope)
        for key in ("source_ref", "provision"):  # a structured test's provision (ADR-0142)
            if isinstance(record.get(key), str):
                found.add(record[key])
    for envelope in envelopes:
        for item in (envelope or {}).get("evidence") or ():
            if isinstance(item, dict) and isinstance(item.get("ref"), str):
                found.add(item["ref"])
    return found


def _build_source(
    corpus: Corpus, chunks: tuple, report: BuildReport, also: Iterable[str] = ()
) -> Graph:
    """The pinned snapshot as RDF. `also` adds provisions a record rests on
    directly — a relationship whose sentence is the Act's own (s 205, s 206) —
    beside the ones the chunks cite, so its source is a node the graph holds."""
    graph = bind_all(Graph())
    version = _version_node(corpus, graph)
    known = corpus.provisions.keys() | corpus.units.keys()

    compilations: dict[str, URIRef] = {}
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
        # Which compilation the snapshot holds, as upstream recorded it. The pin
        # names a commit; this names the law a reader can look up (F09).
        held = corpus.instruments.get(instrument)
        if held is not None:
            graph.add((node, TMK.compilationNumber, _lit(held.compilation_number)))
            graph.add((node, TMK.registerId, _lit(held.register_id)))
            graph.add((node, TMK.compilationStart, _lit(held.compilation_start, XSD.date)))
            graph.add((node, TMK.capturedAt, _lit(held.captured_at)))
            compilations[instrument] = _compilation(graph, node, instrument, held)

    report.chunks = len(chunks)
    pages_seen: set[str] = set()
    provisions_seen: set[str] = {ref for ref in also if ref in known}
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
        # the Manual states the Registrar's practice (CLAUDE.md rule 5). The class
        # says the same, by the same rule, so the practice/law disjointness has a
        # real node to guard (review F1).
        graph.add((node, TMK.authorityKind, _lit("practice")))
        graph.add((node, RDF.type, TMK.ManualPassage))
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
            # Who decided, read off the case id's series and nothing else (review
            # C7): the Registrar's own delegate is not a court. A series that
            # reports both stays a bare tmk:Decision rather than a guess.
            decided = decisions_module.classify(case.id)
            graph.add((case_node, RDF.type, TMK.Decision))
            if decided.kind in _DECISION_CLASSES:
                graph.add((case_node, RDF.type, _DECISION_CLASSES[decided.kind]))
            graph.add((case_node, TMK.decisionKind, _lit(decided.kind)))
            if decided.jurisdiction:
                graph.add((case_node, TMK.jurisdiction, _lit(decided.jurisdiction)))
            if decided.level:
                graph.add((case_node, TMK.decidedAt, _lit(decided.level)))
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
        compilation = compilations.get(instrument)
        if compilation is not None:
            graph.add((node, TMK.textFrom, compilation))
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
                if compilation is not None:
                    graph.add((unit_node, TMK.textFrom, compilation))
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
        # A decimal, as tmk:confidence declares: rdflib types a float xsd:double,
        # and the two are disjoint value spaces under OWL (the review response, F07).
        graph.add((node, TMK.confidence, _lit(Decimal(str(envelope["confidence"])), XSD.decimal)))
    for ordinal, item in enumerate(envelope.get("evidence") or (), start=1):
        if isinstance(item, dict) and isinstance(item.get("ref"), str):
            # The shortcut, kept so the competency queries and RULE-0002 read as
            # they did; the anchor beside it is the evidence itself.
            graph.add((node, TMK.sourcePassage, ref_node(item["ref"])))
            _anchor(graph, node, ordinal, item, store.corpus)


def _anchor(graph: Graph, record: URIRef, ordinal: int, item: dict, corpus: Corpus | None) -> None:
    """One evidence item as a node: which passage, which sentence in it, which text.

    Until S041 only `tmk:sourcePassage` reached the graph, so the span, hash and
    quote of every concept, typing, correction and definition (634 items) stayed in
    the record files, and a downstream reader of the RDF could name the passage a
    statement rests on but not the sentence (the second review response, R03).
    Everything here is copied off the record; `tmk:isStale` and
    `tmk:checkedAgainst` are computed, as they are for a relationship.
    """
    anchor = evidence_node(record, ordinal)
    ref = item["ref"]
    graph.add((record, TMK.evidence, anchor))
    graph.add((anchor, RDF.type, TMK.EvidenceAnchor))
    graph.add((anchor, TMK.ordinal, _lit(ordinal, XSD.integer)))
    graph.add((anchor, TMK.sourcePassage, ref_node(ref)))
    graph.add((anchor, TMK.upstreamRef, _lit(ref)))
    span = item.get("span")
    if isinstance(span, (list, tuple)) and len(span) == 2:
        graph.add((anchor, TMK.spanStart, _lit(span[0], XSD.integer)))
        graph.add((anchor, TMK.spanEnd, _lit(span[1], XSD.integer)))
    recorded = item.get("content_hash")
    if recorded:
        graph.add((anchor, TMK.sourceContentHash, _lit(recorded)))
    if item.get("quote"):
        graph.add((anchor, TMK.quote, _lit(str(item["quote"]))))
    if corpus is None:
        return
    graph.add((anchor, TMK.checkedAgainst, _version_iri(corpus)))
    held = _held(corpus, ref)
    if held is not None and recorded:
        graph.add((anchor, TMK.isStale, _lit(recorded != held.content_hash, XSD.boolean)))


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
    held = corpus.chunks.get(source_ref) or corpus.provisions.get(source_ref) or corpus.units.get(source_ref)
    if held is None:
        counts.unresolvable_sources.append(record["id"])
        return
    stale = bool(recorded) and recorded != held.content_hash
    graph.add((node, TMK.isStale, _lit(stale, XSD.boolean)))
    if stale:
        counts.stale.append(record["id"])


#: label property -> the comparison keys stated beside it (review F2, ADR-0125).
_KEYS = {
    SKOS.prefLabel: (TMK.prefLabelKey, TMK.labelKey),
    SKOS.altLabel: (TMK.labelKey,),
    TMK.notLabel: (TMK.notLabelKey,),
}


def _name(graph: Graph, node: URIRef, prop: URIRef, value: str) -> None:
    """A label, and the key it folds to (`ontology.hygiene.fold`).

    The key is computed, like `tmk:isStale`, and shown to nobody. It is there so
    the SHACL gate can find two concepts answering to one name, or a "kind of"
    beside a "not the same as", with an equality join: folding every label inside
    SPARQL made the gate take over ten minutes.
    """
    graph.add((node, prop, _en(value)))
    key = hygiene.fold(value)
    if key:
        for key_prop in _KEYS[prop]:
            graph.add((node, key_prop, _lit(key)))


def _build_concepts(graph: Graph, store: Store, counts: StoreReport) -> None:
    # Declared by whichever store contributes a concept, and by neither when
    # neither does. A store with no concepts writes an empty graph rather than a
    # graph holding only a scheme nobody is in — `authored graph 0 triples` is a
    # true statement about a repo that has authored nothing, and `3 triples` is
    # a puzzle.
    if store.records.count("gold_concept"):
        graph.add((SCHEME, RDF.type, TMK.ConceptScheme))
        graph.add((SCHEME, RDFS.label, _en(SCHEME_LABEL)))
        graph.add((SCHEME, SKOS.prefLabel, _en(SCHEME_LABEL)))

    for record in store.records["gold_concept"]:
        node = concept_node(record["id"])
        graph.add((node, RDF.type, SKOS.Concept))
        graph.add((node, RDF.type, TMK.LegalConcept))
        graph.add((node, SKOS.inScheme, SCHEME))
        _name(graph, node, SKOS.prefLabel, record["pref_label"])
        graph.add((node, TMK.goldRecord, _lit(record["id"])))
        for label in _each(record, "alt_labels"):
            _name(graph, node, SKOS.altLabel, label)
        # No SKOS property means "must not be confused with this", and it is the
        # most valuable field on the record. tmk:notLabel exists for it.
        for label in _each(record, "not_labels"):
            _name(graph, node, TMK.notLabel, label)
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
#:
#: A kind says what a concept is (ruling B1, ADR-0126). `tmk:RelevantFactor`,
#: `tmk:Exception` and `tmk:Remedy` are no longer asserted from a typing: they are
#: what a concept does, said by the edge that does so (`qualifies`,
#: `isAnExceptionTo`, `isOvercomeBy`; ADR-0135). Every kind here is a
#: subclass of `tmk:LegalConcept` on the same footing, so a query that walks the
#: concept hierarchy reaches every kind without knowing which family it is in.
#:
#: **`process_role` maps to `tmk:ProcessRole`, not to `tmk:Role`.** A
#: `tmk:Role` in `examination.ttl` is a person or office that acts — an
#: examiner. A `tmk:ProcessRole` is the *concept* of that office as the
#: vocabulary holds it. Merging them would make the concept record for
#: "examiner" an examiner, and the model would then have no way to say that one
#: is a term in a vocabulary and the other is somebody who signs a report
#: (ADR-0098 consequence 3).
CONCEPT_CLASSES: dict[str, str] = {
    "ground_of_refusal": "GroundOfRefusal",
    "legal_test": "LegalTest",
    "principle": "Principle",
    "subject_matter": "SubjectMatter",
    "sign_content": "SignContent",
    "context": "Context",
    "use_in_trade": "UseInTrade",
    "process_role": "ProcessRole",
    "procedural_step": "ProceduralStep",
    "instrument_or_record": "InstrumentOrRecord",
    "external_instrument": "ExternalInstrument",
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
        # does assert is that somebody looked and said none of the kinds
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
        for ref in record.get("basis") or ():
            graph.add((typing, TMK.typingBasis, ref_node(ref)))
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


#: Relationship predicates written as SKOS relations rather than tmk: terms.
SKOS_PREDICATES = {"broader": SKOS.broader, "narrower": SKOS.narrower, "related": SKOS.related}


def _qualifiers(graph: Graph, node: URIRef, record: dict[str, Any]) -> None:
    """What a relationship's sentence qualifies it with, on the reified record.

    The modality, and since S036 the condition or hedge the sentence states it under
    (`applies_when`, the review response F14). Absent means not supplied, and stays
    absent. Never inferred from the sentence's grammar — that is a legal reading
    (guide §5.4). The direct triple carries neither: it is a navigation edge, and a
    reader who needs the qualification reads the assertion.
    """
    if record.get("modality"):
        graph.add((node, TMK.modality, _lit(record["modality"])))
    if record.get("applies_when"):
        graph.add((node, TMK.appliesWhen, _en(" ".join(str(record["applies_when"]).split()))))
    if record.get("hedge"):
        graph.add((node, TMK.hedge, _en(" ".join(str(record["hedge"]).split()))))
    # Computed, like tmk:isStale: whether a condition was stated, none is in the
    # sentence, or nobody has looked; and the proceeding and kind of mark the source's
    # Part fixes (the second review response, R07; `ontology.conditions`).
    graph.add((node, TMK.conditionState, _lit(conditions.state(record))))
    if record.get("no_condition"):
        graph.add((node, TMK.noConditionBecause, _en(" ".join(str(record["no_condition"]).split()))))
    for prop, value in ((TMK.proceeding, conditions.proceeding(record)), (TMK.markType, conditions.mark_type(record))):
        if value:
            graph.add((node, prop, _lit(value)))


def _build_relationships(
    graph: Graph, store: Store, corpus: Corpus, counts: StoreReport
) -> None:
    for record in store.records["gold_relationship"]:
        node = assertion_node(record["id"])
        subject = _term(str(record["subject"]))
        # `broader` and `related` are SKOS's, not the relation dictionary's: the
        # relationship job writes them for "is a kind of" and "connected, no
        # dictionary predicate fits" (ADR-0113). Everything else is a tmk: term.
        predicate = SKOS_PREDICATES.get(str(record["predicate"])) or URIRef(TMK[record["predicate"]])
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
        replacement = store.replaced.get(str(record["id"])) if store.signed else None
        if replacement:
            # Corrected on the owner's instruction (ADR-0122): the signed record is
            # kept as history, flagged the way a stale one is, and its triple no
            # longer serves. The authored replacement carries the corrected one.
            graph.add((node, TMK.isCorrected, _lit(True, XSD.boolean)))
            graph.add((node, TMK.replacedBy, assertion_node(replacement)))
        else:
            graph.add((subject, predicate, obj))
        graph.add((node, RDF.type, store.assertion_class))
        graph.add((node, TMK.assertionSubject, subject))
        graph.add((node, TMK.assertionPredicate, predicate))
        graph.add((node, TMK.assertionObject, obj))
        graph.add((node, TMK.supportingText, _lit(record["supporting_text"])))
        affirmed = store.affirmed.get((str(record["subject"]), str(record["object"])))
        if affirmed and record["predicate"] == "broader":
            graph.add((node, TMK.kindOfAffirmed, _en(" ".join(str(affirmed.get("why", "")).split()))))
        _qualifiers(graph, node, record)
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
    signed_labels: Container[str] | None = None,
) -> None:
    signed_labels = labels if signed_labels is None else signed_labels
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
            if label.casefold() not in signed_labels:
                # A label no signed concept carries, but one a concept explicitly
                # excludes, is the question naming the boundary it tests.
                # Recorded as such rather than counted as a missing concept,
                # which is what it looked like until OQ-0002 settled it. Asked of
                # the signed vocabulary only: since ADR-0079 a machine may write a
                # concept carrying the label (GC-0154 "deceptively similar"), and
                # writing a concept must never change what a signed question says
                # (ADR-0116).
                boundary = excluded.get(label.casefold(), ())
                if boundary:
                    graph.add((node, TMK.expectsBoundaryLabel, _en(label)))
                    for concept in boundary:
                        graph.add((node, TMK.testsBoundaryOf, concept))
                    counts.boundary_concept_labels.append(f"{record['id']}:{label}")
                elif label.casefold() not in labels:
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


#: decision kind -> the class a cited case is put in (review C7). "unclassified"
#: has none: the case stays a bare tmk:Decision.
_DECISION_CLASSES = {
    "administrative": TMK.AdministrativeDecision,
    "judicial": TMK.JudicialDecision,
}


#: correction field -> how an added value is stated on the corrected node.
_ADDED = {
    "alt_labels": lambda graph, node, value: _name(graph, node, SKOS.altLabel, value),
    "not_labels": lambda graph, node, value: _name(graph, node, TMK.notLabel, value),
    "legislative_basis": lambda graph, node, value: graph.add((node, TMK.legislativeBasis, ref_node(value))),
    "definition_sources": lambda graph, node, value: graph.add((node, TMK.definitionSource, ref_node(value))),
}


def _build_corrections(
    graph: Graph, corrections: Any, counts: StoreReport, corpus: Corpus | None = None
) -> None:
    """Corrections to signed records, stated where machine output lives (ADR-0122).

    Each correction is a node carrying the authoring envelope like any authored
    record, naming what it corrects and the owner's ruling it acts on. What it
    withdrew is recorded on it as text, so the graph says what changed without
    restating the withdrawn value as live. What it added is stated on the
    corrected node *in this graph* — never in the approved one — which is the same
    footing an authored typing of a signed concept has always had.
    """
    store = Store(
        name="authored", records=None, graph_name=AUTHORED_GRAPH,
        assertion_class=TMK.AuthoredAssertion,
        envelopes={c.id: c.envelope for c in corrections.sound if c.envelope},
        corpus=corpus,
    )
    for correction in corrections.sound:
        record = correction.record
        node = assertion_node(correction.id)
        target = str(record["corrects"])
        target_node = concept_node(target) if target.startswith("GC-") else assertion_node(target)
        graph.add((node, RDF.type, TMK.Correction))
        graph.add((node, TMK.goldRecord, _lit(correction.id)))
        graph.add((node, TMK.corrects, target_node))
        graph.add((node, TMK.ruling, _lit(record["ruling"])))
        graph.add((node, TMK.extractionMethod, _lit(AUTHORING)))
        if record.get("notes"):
            graph.add((node, RDFS.comment, _en(record["notes"])))
        for name, values in sorted((record.get("remove") or {}).items()):
            for value in values:
                graph.add((node, TMK.withdrawnValue, _lit(f"{name}: {value}")))
        for name, values in sorted((record.get("add") or {}).items()):
            for value in values:
                graph.add((node, TMK.addedValue, _lit(f"{name}: {value}")))
                _ADDED[name](graph, target_node, value)
        for name, value in sorted((record.get("set") or {}).items()):
            graph.add((node, TMK.addedValue, _lit(f"{name}: {value}")))
            if name == "resolves_to":
                graph.add((target_node, TMK.resolvesTo, _term(str(value))))
        if record.get("replaced_by"):
            graph.add((node, TMK.replacedBy, assertion_node(str(record["replaced_by"]))))
        _origin(graph, node, record, store)
    counts.corrections = len(corrections.sound)


def _build_definitions(
    graph: Graph, definitions: Any, counts: StoreReport, corpus: Corpus | None = None
) -> None:
    """Definitions, stated where machine output lives (ADR-0137).

    Two forms, as a relationship has (ADR-0058): the record, a `tmk:Definition`
    carrying the authoring envelope and saying where its words come from; and the
    direct `skos:definition` (and `skos:scopeNote`) on the concept, for navigation.
    Both in the authored graph, never the approved one, signed concept or not: a
    definition of a signed concept is still machine-written.
    """
    store = Store(
        name="authored", records=None, graph_name=AUTHORED_GRAPH,
        assertion_class=TMK.AuthoredAssertion,
        envelopes={d.id: d.envelope for d in definitions.sound if d.envelope},
        corpus=corpus,
    )
    for definition in definitions.sound:
        record = definition.record
        node = assertion_node(definition.id)
        concept = concept_node(definition.concept)
        text = _en(record["text"])
        graph.add((node, RDF.type, TMK.Definition))
        graph.add((node, TMK.goldRecord, _lit(definition.id)))
        graph.add((node, TMK.defines, concept))
        graph.add((node, SKOS.definition, text))
        graph.add((node, TMK.definitionBasis, _lit(record["basis"])))
        graph.add((node, TMK.extractionMethod, _lit(AUTHORING)))
        graph.add((concept, SKOS.definition, text))
        if record.get("scope_note"):
            graph.add((node, SKOS.scopeNote, _en(record["scope_note"])))
            graph.add((concept, SKOS.scopeNote, _en(record["scope_note"])))
        if record.get("scope"):
            graph.add((node, TMK.definitionScope, _lit(record["scope"])))
        _origin(graph, node, record, store)
    counts.definitions = len(definitions.sound)


def _build_procedures(graph: Graph, tests: Any, processes: Any, counts: StoreReport,
                      corpus: Corpus | None = None) -> None:
    """Structured tests and process templates (ADR-0142), as records in the authored graph.

    The record and its envelope, each evidence item an anchor, as a definition's are, so
    every machine-written record type carries its envelope in the RDF (R03, R04). Since
    S043 the inner structure is there too: the condition tree with its joins and its fact
    and evaluative leaves, the effect and its kind, the exceptions, evidence requirements
    and routes of a test; the steps, transitions and time rules of a template. Each
    element is a `tmk:RecordElement` of its record, stamped as the record is, saying
    whether its source is law or practice, and anchored to the evidence item it quotes,
    so a consumer reaches the exact words without the record file (ADR-0144)."""
    for found, kind in ((tests, TMK.StructuredTest), (processes, TMK.ProcessTemplate)):
        store = Store(
            name="authored", records=None, graph_name=AUTHORED_GRAPH,
            assertion_class=TMK.AuthoredAssertion,
            envelopes={entry.id: entry.envelope for entry in found.sound if entry.envelope},
            corpus=corpus,
        )
        for entry in found.sound:
            node = assertion_node(entry.id)
            graph.add((node, RDF.type, kind))
            graph.add((node, TMK.goldRecord, _lit(entry.id)))
            graph.add((node, RDFS.label, _en(entry.record["title"])))
            graph.add((node, TMK.extractionMethod, _lit(AUTHORING)))
            if entry.record.get("provision"):
                graph.add((node, TMK.readsProvision, ref_node(entry.record["provision"])))
            if entry.record.get("ground"):
                graph.add((node, TMK.testsGround, concept_node(entry.record["ground"])))
            _origin(graph, node, entry.record, store)
            elements = _Elements(graph, node, entry, store)
            if kind == TMK.StructuredTest:
                elements.test(entry.record)
            else:
                elements.process(entry.record)
        counts.procedures += len(found.sound)


class _Elements:
    """One record's elements as nodes. Kept in one place so a test and a template map
    their shared parts (a statement, a source, an anchor) the same way."""

    def __init__(self, graph: Graph, record: URIRef, entry: Any, store: Store) -> None:
        self.graph, self.record, self.store, self.id = graph, record, store, entry.id
        evidence = (entry.envelope or {}).get("evidence") or ()
        self.anchors: dict[tuple[str, str], URIRef] = {}
        for ordinal, item in enumerate(evidence, start=1):
            self.anchors.setdefault((str(item.get("ref")), str(item.get("quote"))), evidence_node(record, ordinal))

    def node(self, cls: URIRef, *path: str | int, element: dict | None = None) -> URIRef:
        g, node = self.graph, element_node(self.record, *path)
        g.add((node, RDF.type, cls))
        g.add((node, TMK.elementOf, self.record))
        g.add((node, TMK.origin, _lit(self.store.name)))
        g.add((node, TMK.reviewStatus, _lit(self.store.review_status(self.id))))
        element = element or {}
        if element.get("id"):
            g.add((node, TMK.elementId, _lit(str(element["id"]))))
        label = element.get("label")
        if label:
            g.add((node, RDFS.label, _en(str(label))))
        if element.get("text"):
            g.add((node, TMK.statement, _en(str(element["text"]))))
        ref, quote = element.get("ref"), element.get("quote")
        if isinstance(ref, str):
            g.add((node, TMK.sourcePassage, ref_node(ref)))
            g.add((node, TMK.sourceAuthority, _lit(
                "law" if ref.startswith(("TMA1995/", "TMR1995/")) else "practice")))
            anchor = self.anchors.get((ref, str(quote)))
            if anchor is not None:
                g.add((node, TMK.anchoredBy, anchor))
        for concept in element.get("concepts") or ():
            g.add((node, TMK.turnsOn, concept_node(str(concept))))
        return node

    def condition(self, tree: dict, *path: str | int) -> URIRef:
        if "all" in tree or "any" in tree:
            join = "all" if "all" in tree else "any"
            node = self.node(TMK.ConditionGroup, *path, element=tree)
            self.graph.add((node, TMK.conditionJoin, _lit(join)))
            for ordinal, child in enumerate(tree[join], start=1):
                child_path = ("element", child["id"]) if child.get("id") else (*path, ordinal)
                part = self.condition(child, *child_path)
                self.graph.add((node, TMK.conditionPart, part))
                self.graph.add((part, TMK.ordinal, _lit(ordinal, XSD.integer)))
            return node
        cls = TMK.EvaluativeCondition if tree["kind"] == "evaluative" else TMK.FactCondition
        node = self.node(cls, *path, element=tree)
        if tree.get("ask"):
            self.graph.add((node, TMK.clarifyingQuestion, _en(str(tree["ask"]))))
        return node

    def effect(self, effect: dict, *path: str | int) -> URIRef:
        node = self.node(TMK.LegalEffect, *path, element=effect)
        self.graph.add((node, TMK.effectKind, _lit(effect["kind"])))
        return node

    def test(self, record: dict) -> None:
        g, root = self.graph, self.record
        g.add((root, TMK.hasEffect, self.effect(record["effect"], "effect")))
        tree = record["condition"]
        g.add((root, TMK.hasCondition, self.condition(
            tree, *(("element", tree["id"]) if tree.get("id") else ("condition",)))))
        for exception in record.get("exceptions") or ():
            node = self.node(TMK.TestException, "element", exception["id"], element=exception)
            g.add((root, TMK.hasException, node))
            g.add((node, TMK.hasEffect, self.effect(exception["effect"], "element", exception["id"], "effect")))
            inner = exception["condition"]
            g.add((node, TMK.hasCondition, self.condition(
                inner, *(("element", inner["id"]) if inner.get("id") else ("element", exception["id"], "condition")))))
        for requirement in record.get("evidence_requirements") or ():
            node = self.node(TMK.EvidenceRequirement, "element", requirement["id"], element=requirement)
            g.add((root, TMK.hasEvidenceRequirement, node))
            g.add((node, TMK.requirementKind, _lit(requirement["kind"])))
            for condition in requirement["for"]:
                g.add((node, TMK.requirementFor, element_node(root, "element", condition)))
        for route in record.get("routes") or ():
            node = self.node(TMK.ResponseRoute, "element", route["id"], element=route)
            g.add((root, TMK.hasRoute, node))
            if route.get("scope"):
                g.add((node, SKOS.scopeNote, _en(str(route["scope"]))))

    def process(self, record: dict) -> None:
        g, root = self.graph, self.record
        for ordinal, step in enumerate(record["steps"], start=1):
            node = self.node(TMK.ProcessStep, "element", step["id"], element=step)
            g.add((root, TMK.hasStep, node))
            g.add((node, TMK.ordinal, _lit(ordinal, XSD.integer)))
            g.add((node, TMK.stepKind, _lit(step["kind"])))
            g.add((node, TMK.actorCapacity, _lit(step["actor"])))
            if step.get("continues_in"):
                g.add((node, TMK.continuesIn, assertion_node(str(step["continues_in"]))))
        for ordinal, transition in enumerate(record.get("transitions") or (), start=1):
            node = self.node(TMK.ProcessTransition, "transition", ordinal,
                             element={**transition, "text": transition["when"]})
            g.add((root, TMK.hasTransition, node))
            g.add((node, TMK.ordinal, _lit(ordinal, XSD.integer)))
            g.add((node, TMK.fromStep, element_node(root, "element", transition["from"])))
            g.add((node, TMK.toStep, element_node(root, "element", transition["to"])))
            for need in transition.get("needs") or ():
                g.add((node, TMK.needs, _en(str(need))))
            for ground in transition.get("grounds") or ():
                g.add((node, TMK.onlyForGround, ref_node(str(ground))))
        for rule in record.get("deadlines") or ():
            node = self.node(TMK.TimeRule, "element", rule["id"], element=rule)
            g.add((root, TMK.hasTimeRule, node))
            for step in rule["from"]:
                g.add((node, TMK.timeRuleFrom, element_node(root, "element", step)))


def _build_store(
    corpus: Corpus,
    store: Store,
    counts: StoreReport,
    labels: dict[str, tuple[URIRef, ...]],
    excluded: dict[str, tuple[URIRef, ...]],
    signed_labels: Container[str] | None = None,
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
    _build_questions(graph, store, counts, labels, excluded, signed_labels)
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
    chunks: tuple | None = None,
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
    report = BuildReport()
    report.authored_refused = [entry.record_id for entry in authored.refused]

    dataset = Dataset()
    bind_all(dataset)

    for triple in load_tbox():
        dataset.add(triple)

    corrections = corrections_module.load(authored.root, gold=gold, authored=authored)
    report.corrections_refused = [entry.id for entry in corrections.refused]
    definitions = definitions_module.load(authored.root, gold=gold, authored=authored)
    report.definitions_refused = [entry.id for entry in definitions.refused]
    tests = procedure_module.load_tests(authored.root, gold=gold, authored=authored)
    processes = procedure_module.load_processes(authored.root, gold=gold, authored=authored)
    signed = approved_store(
        corrections_module.in_force_gold(gold, corrections), corrections.replacements()
    )
    machine = authored_store(authored, corpus)

    # One label index over both stores, built before either graph, because the
    # question "does the vocabulary hold this label" spans them (see
    # `_concept_labels`).
    labels = _concept_labels(signed, machine)
    excluded = _not_labels(signed, machine)
    signed_labels = frozenset(_concept_labels(signed))

    # The source graph is closed over every ref any record rests on, in every
    # store: corrections and definitions as well as the record types the gold
    # schema knows. Until S041 a definition resting on a unit no chunk cites
    # (GD-0060, GD-0112, GD-0138) pointed at a node the graph did not hold (the
    # second review response, R03).
    extra = [
        *(("correction", c.record, c.envelope) for c in corrections.sound),
        *(("definition", d.record, d.envelope) for d in definitions.sound),
        *(("legal_test", t.record, t.envelope) for t in tests.sound),
        *(("process", p.record, p.envelope) for p in processes.sound),
    ]
    if chunks is None:
        chunks = source_chunks(corpus, gold, authored, extra)
    record_provisions = {
        str(r.get("source_ref"))
        for store in (gold, authored) for r in store["gold_relationship"]
        if str(r.get("source_ref", "")).startswith(("TMA", "TMR"))
    }
    record_provisions |= {
        ref for ref in _evidence_refs(authored, extra) if ref.startswith(("TMA", "TMR"))
    }
    source = _build_source(corpus, chunks, report, also=record_provisions)
    approved = _build_store(corpus, signed, report.approved, labels, excluded, signed_labels)
    authored_graph = _build_store(corpus, machine, report.authored, labels, excluded, signed_labels)
    _build_corrections(authored_graph, corrections, report.authored, corpus)
    _build_definitions(authored_graph, definitions, report.authored, corpus)
    _build_procedures(authored_graph, tests, processes, report.authored, corpus)

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


#: The release manifest's schema (A11). Bump it when a field changes meaning.
MANIFEST_VERSION = "tmk-release/1"


def manifest(dataset: Dataset) -> dict[str, Any]:
    """What a downstream consumer needs to know about this build, from the build itself
    (the second review response, A11): the pin and the compilations it holds, the record
    schemas, the profile, and per named graph its triples, its record classes and its
    review states. Deterministic, so it is committed beside the graph and drift-checked
    with it; the site's `build.json` adds the date and the revision."""
    import json

    pin = json.loads((REPO_ROOT / "data" / "pin.json").read_text(encoding="utf-8"))
    source = dataset.graph(SOURCE_GRAPH)
    law = sorted(
        ({"label": str(source.value(node, RDFS.label)),
          "compilation": str(source.value(node, TMK.compilationNumber)),
          "register_id": str(source.value(node, TMK.registerId)),
          "in_force_from": str(source.value(node, TMK.compilationStart))}
         for node in source.subjects(RDF.type, TMK.Legislation)
         if source.value(node, TMK.compilationNumber) is not None),
        key=lambda row: row["label"])
    graphs = {}
    for name, label in ((SOURCE_GRAPH, "source"), (APPROVED_GRAPH, "approved"),
                        (AUTHORED_GRAPH, "authored"), (INFERRED_GRAPH, "inferred")):
        graph = dataset.graph(name)
        classes: dict[str, int] = {}
        for _, kind in graph.subject_objects(RDF.type):
            if str(kind).startswith(str(TMK)):
                key = str(kind)[len(str(TMK)):]
                classes[key] = classes.get(key, 0) + 1
        states: dict[str, int] = {}
        for status in graph.objects(None, TMK.reviewStatus):
            states[str(status)] = states.get(str(status), 0) + 1
        graphs[label] = {"triples": len(graph), "classes": dict(sorted(classes.items())),
                         "review_status": dict(sorted(states.items()))}
    schemas = sorted(json.loads(path.read_text(encoding="utf-8")).get("$id", path.name)
                     for path in (REPO_ROOT / "eval" / "schemas").glob("*.schema.json"))
    return {
        "manifest": MANIFEST_VERSION,
        "upstream": {k: pin[k] for k in ("repo", "commit", "manual_extractor_version",
                                         "legislation_extractor_version", "tree_sha256")},
        "law": law,
        "profile": "RDF 1.1 named graphs, SKOS, SHACL shapes and the approved SPARQL rules; no OWL "
                   "profile is claimed and no OWL inference is licensed (ADR-0134). A direct edge is "
                   "navigation only; the reified assertion is the reading (ADR-0134, R07).",
        "graphs": graphs,
        "schemas": schemas,
        "states": "approved: a named person signed it; unreviewed: a machine wrote it and nobody has "
                  "read it; candidate: a rule derived it. They never share a named graph (CLAUDE.md "
                  "rule 4). Silence never promotes a record (ADR-0085).",
    }


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

    import json

    release = directory / "manifest.json"
    release.write_text(json.dumps(manifest(dataset), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(release)
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

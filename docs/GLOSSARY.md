# GLOSSARY

Orientation for a session that arrives cold. Two halves: the domain, and the
project's own vocabulary.

> **The domain half is not authoritative.** These are working descriptions to make
> the documents readable, not legal definitions. Nothing here may be promoted into
> `vocab/` or used as a concept definition — those are expert-owned (CLAUDE.md
> rule 1). Where a term matters legally, the Act, the Regulations and the Manual
> govern, in that order of authority.

## Domain

**Trade Marks Act 1995 (`TMA1995`)** — the governing Commonwealth Act. Upstream
holds 316 provisions from the compiled version.

**Trade Marks Regulations 1995 (`TMR1995`)** — the regulations made under the Act.
447 provisions. Regulation numbers always contain dots (`r 3A.3`); Act sections
never do — this is an enforced invariant, not a stylistic habit.

**The Manual** — the IP Australia *Trade Marks Manual of Practice and Procedure*.
Records the Registrar's examination practice. **It is not law**, and it does not
bind the Registrar's discretion (Q-12). Published as HTML; 500 pages across 54
Parts.

**Registrar** — the Registrar of Trade Marks. Examination is conducted under
delegated authority.

**Examination** — the process of assessing whether a filed application meets the
requirements of the Act, including whether any ground of refusal applies.

**Ground of refusal** — a statutory basis on which an application may be refused.

**Objection** — an examiner's raised concern, which must identify a legislative
basis.

**Distinctiveness / s 41** — whether a sign is capable of distinguishing the
applicant's goods or services. The roadmap's suggested pilot area (unconfirmed —
HANDOFF Q1). Note that s 41 was renumbered in 2012, so older Manual text may cite
numbering that no longer resolves (Q-06).

**Acquired distinctiveness** — distinctiveness established through use rather than
inherent in the sign. Appears in the roadmap as a worked example of a concept with
several surface forms ("distinctiveness acquired through use", "factual
distinctiveness").

**Evidence of use** — evidence going to how a sign has actually been used in
trade. A category, not a conclusion.

**Neutral citation** — court-assigned, medium-independent: `[2018] FCAFC 109`.

**Reported citation** — series-based: `(1954) 71 RPC 43`. Upstream records both
styles and a canonical `case_id`.

**AustLII / TimeBase** — legal publishers whose links appear in Manual text.
Upstream reads AustLII path-form and TimeBase query-form hrefs as provision
evidence; Federal Register links are deliberately not read.

**Federal Register of Legislation** — the authoritative source for compiled
Commonwealth legislation, and the API upstream uses to fetch `.docx` compilations.

**OPC** — the Office of Parliamentary Counsel, whose Word stylesheet
(`w:pStyle`) upstream uses to derive provision structure. The style name travels
with each unit as evidence.

## Corpus and upstream

**Snapshot** — the committed, offline, deterministically extracted corpus produced
by `manual-XtrACTor`. The deliverable of Stage 1; read-only from here.

**Page** — one Manual page. `page_ref` = `TMM/Part22/1`. Part membership comes
from the nav tree, never from the URL.

**Chunk** — one retrievable passage, normally the prose under one heading.
`chunk_ref` = `TMM/Part22/1/1/2`. The addressable unit for retrieval. Kinds:
`body` (1,683), `annex` (725), `landing` (52), plus `note` and `table`.

**Block** — the structural pieces a chunk's flat `text` was flattened from:
paragraph, list_item, table, heading, image, text.

**Provision** — a section, regulation or Schedule clause. `ref` = `TMA1995/s41`.

**Unit** — a numbered subdivision of a provision. `ref` = `TMA1995/s41(3)(a)`.

**The join** — a chunk's `provisions[].id` is literally a provision `ref`. No
transformation, no lookup table. 97% of in-scope edges resolve.

**`extraction`** — how an edge was found: `href` (the Manual's authors linked it)
or `regex` (upstream inferred it from prose).

**`certainty`** — for regex edges only: `explicit` (instrument named adjacent),
`default` (bare "section N", resolved to the Act by convention — an inference),
`ambiguous` (several instruments in scope; human queue only). See Q-07.

**`content_hash`** — per-page, per-chunk, per-provision, per-unit. The mechanism
for detecting that an assertion's supporting passage has changed (ADR-0011).

## Project

**Candidate** — machine-generated, unapproved. Lives in `review/`. Never read as
if approved (ADR-0007).

**Assertion** — a statement in the graph, carrying provenance: method, confidence,
source ref, source span, source content hash, review status.

**Competency question** — an ordinary question the finished system must be able to
answer. Stage 0; the basis of every later measurement.

**Gold standard** — the expert-created set of trusted examples that every
automated component is measured against. Stage 0.

**Prohibited use / prohibited inference** — conclusions the system must *not*
produce. Tested as explicitly as the positive cases.

**Tier 1 / 2 / 3** — the confidence-and-risk tiers governing what may be
auto-accepted. Tier 3 always needs a human (ADR-0008).

**SKOS** — W3C model for controlled vocabularies: preferred label, alternative
labels, broader, narrower, related.

**OWL 2 RL** — the OWL profile chosen for scalable rule-based reasoning, trading
expressiveness for tractability.

**SHACL** — W3C constraint language for validating RDF, run via pySHACL before
publication.

**PROV-O** — W3C provenance ontology: entities, activities, agents.

**Named graph** — a subdivision of the triple store used here to keep source data,
candidates, approved assertions, inferred assertions and superseded assertions
apart.

**SPARQL `CONSTRUCT` rule** — an explicit, approved derivation producing new
triples from existing ones. Each needs an approval record and a test.

**YAKE** — unsupervised statistical keyphrase extraction. Produces candidates
only.

**`DependencyMatcher`** — spaCy component matching patterns over dependency parse
trees; used for recurring relation phrasing.

**Hybrid search** — combining BM25 keyword scoring with vector similarity, then
fusing the scores (OpenSearch fusion, reciprocal rank fusion, or a cross-encoder
rerank).

**ADR** — architecture decision record. `docs/DECISIONS.md`. Append-only.

## Modelling

Added S011 so the dashboard's tooltips and this file draw on one set of words.
Ordinary technical vocabulary, aimed at a reader who knows trade marks and not
knowledge engineering.

**Knowledge graph** — the data itself, held as a web of small statements rather
than as rows in a table. Its shape comes from the ontology.

**Ontology** — the model: which kinds of thing exist, what may be said about
each, and what may be inferred. It says nothing about any particular trade mark;
it says what a statement about one is allowed to look like.

**Triple** — one statement, in three parts: subject, predicate, object.
*TMM/Part29/1#1 — states — connotation.* Everything in the graph is triples, and
counting them is how its size is reported.

**Class** — a kind of thing the ontology declares: a legal concept, a passage, a
citation. A class with nothing in it is a slot nobody has filled.

**Predicate** — the middle part of a triple: the relationship being asserted.
This project keeps a closed list of them, generated from approved relationships,
so extraction cannot invent a new one.

**IRI** — the globally unique name of something in the graph, written as a web
address. It need not open a page; it needs to be unambiguous and stable
(`docs/IDENTIFIERS.md`, HANDOFF Q7).

**TBox / ABox** — the two halves of a graph: the TBox is the model (classes and
predicates), the ABox is the content said with it. `ontology/draft/` is the
TBox; `graph/` is the ABox.

**RDF** — the W3C standard the graph is written in. Triples, IRIs and named
graphs are its vocabulary, and SKOS, OWL and SHACL are all layered on it.

**SPARQL** — the query language for RDF. A competency query is a SPARQL query
stored in a file with a header saying what it does and does not answer
(ADR-0061).

**Inference** — a statement derived from others by a rule rather than read from
a source. Everything inferred here names the rule that produced it and stays
quarantined until an expert approves the rule (Stage 9).

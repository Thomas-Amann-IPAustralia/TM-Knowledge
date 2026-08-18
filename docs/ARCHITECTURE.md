# ARCHITECTURE — intended shape of the system

What the system is meant to become, where each piece lives, and which roadmap
stage produces it. Nothing here is built yet; this is the target that the
directory skeleton is holding open. Status per stage: `ROADMAP-STATUS.md`.

## 1. Position in the programme

```
IP Australia Trade Marks Manual        Trade Marks Act & Regulations 1995
   (rendered HTML, no API)             (Federal Register API, compiled .docx)
              │                                         │
              └─────────────┬───────────────────────────┘
                            ▼
              manual-XtrACTor  —  Stage 1, ANOTHER REPO
              deterministic extraction · byte-stable output · no LLM
                            │
                snapshot/ (pages, chunks, provisions, units)
                stable refs: TMM/Part22/1/1/2 · TMA1995/s41(3)(a)
                            │
                            ▼  read-only, pinned  (ADR-0002, ADR-0004)
              ┌──────────────────────────────────────────┐
              │  TM-Knowledge  —  Stages 0, 2–10         │
              │  everything interpretive                 │
              └──────────────────────────────────────────┘
```

Upstream refuses, by design, to produce anything interpretive: no concepts, no
topics, no summaries, no rules, no relevance scores, no defined-term vocabulary,
no resolved amendment edges, no embeddings, no retrieval. All of it is this
repo's work.

## 2. Internal flow

```
data/upstream/            pinned snapshot, not committed
        │
        ▼
src/tm_knowledge/         loader → candidate generation → RDF emission
        │
        ├──▶ review/      candidates awaiting a human   (Tier 2 low-conf, all Tier 3)
        │        │
        │        ▼        recorded approval decision
        ├──▶ vocab/       SKOS concept scheme           (Stage 3)
        ├──▶ ontology/    RDF/RDFS/OWL 2 RL modules     (Stage 5)
        │        │
        │        ▼
        ├──▶ graph/       named graphs, PROV-O          (Stage 6)
        │        │
        │        ├── shapes/    SHACL validation        (Stage 6)
        │        └── queries/   SPARQL, incl. CONSTRUCT rules  (Stages 6, 9)
        │
        └──▶ search index + retrieval API               (Stages 7, 8)
                 │
                 ▼
        eval/    measures all of the above              (Stage 0, run continuously)
```

The one-way rule: `review/ → vocab|ontology|graph` only, and only through a
recorded decision (ADR-0007). Nothing flows back into `data/upstream/`.

## 3. Directory map

| Directory | Holds | Stages | Notes |
|---|---|---|---|
| `docs/` | All project documentation, plus the two source documents | — | Start at `HANDOFF.md` |
| `eval/` | Pilot scope, competency questions, gold set, prohibited uses, harness | 0, and every stage after | **Expert-owned content.** The current blocker |
| `data/` | Pinned upstream snapshot and derived intermediates | 1 (consumed) | Git-ignored except the pin manifest |
| `src/` | `tm_knowledge` Python package — all pipeline code | 2–10 | No code yet |
| `review/` | Candidate registers awaiting human decision | 2, 3, 4 | Never read as if approved |
| `vocab/` | SKOS controlled vocabulary | 3 | Approved only |
| `ontology/` | RDF/RDFS/OWL 2 RL modules | 5 | Approved only |
| `graph/` | Generated RDF, by named graph | 6 | Generated; reproducible from `src/` + inputs |
| `shapes/` | SHACL shapes | 6 | Gate before publication |
| `queries/` | SPARQL queries, `CONSTRUCT` rules, regression queries | 6, 9 | Each rule needs an approval record |
| `tests/` | pytest: unit, SPARQL regression, retrieval benchmarks | all | Includes the prohibited-inference tests |

## 4. Ontology modules (Stage 5)

Six modules from the roadmap, kept separate so that reasoning scope can be
controlled per module:

- **Examination** — TradeMarkApplication, Examination, Examiner, Objection, ExaminationOutcome
- **Legal concepts** — GroundOfRefusal, LegalTest, RelevantFactor, Exception, LegalProposition
- **Evidence** — Evidence, EvidenceCategory, EvidenceSubmission, EvidentiaryProposition
- **Authority** — Legislation, LegislativeProvision, JudicialDecision, ManualInstruction, Guidance, AuthorityStatus
- **Document** — Document, DocumentVersion, Chapter, Paragraph, Passage
- **Time** — effective date, superseded date, decision date, version applicability
- **Provenance** — PROV-O plus the project fields in ADR-0011

Two constraints that fall out of the corpus rather than the roadmap:

- `ManualInstruction` and `LegislativeProvision` must be disjoint and must stay
  visibly distinct all the way into retrieval output (Q-12).
- The Document module maps onto upstream's page/chunk/provision/unit shapes, not
  onto an idealised chapter tree. Upstream headings are unreliable as structure
  (Q-10); `chunk_ref` is the addressable unit, not "paragraph 4.3.12".

## 5. Reference technology stack

From roadmap §3. Agency-approved equivalents may be substituted; substitutions are
ADR-worthy.

| Function | Technology |
|---|---|
| Language | Python |
| Basic NLP | spaCy |
| Keyphrase extraction | **TextRank + YAKE + KeyBERT**, run in parallel over the same text (ADR-0019) |
| Candidate-term metadata | spaCy NER — annotates candidates, never the entity taxonomy (ADR-0019, Q-16) |
| Rule-based entity recognition | spaCy `EntityRuler`, `PhraseMatcher`, regex |
| Relation patterns | spaCy `DependencyMatcher` |
| Similarity and clustering | Sentence Transformers; agglomerative / HDBSCAN; cross-encoder rerank |
| Complex structured extraction | Agency-approved LLM, schema-constrained JSON (HANDOFF Q3) |
| Vocabulary | SKOS |
| Ontology | RDF, RDFS, OWL 2 RL |
| Ontology editing | Protégé / WebProtégé |
| Provenance | PROV-O + project fields |
| Graph processing | RDFLib |
| Validation | SHACL via pySHACL |
| Triple store | Apache Jena Fuseki (prototype) |
| Query | SPARQL |
| Search and vectors | OpenSearch (BM25 + vector, hybrid) |
| Scheduling | GitHub Actions, or agency scheduler / Prefect / Airflow |
| Review interface | Streamlit or a light internal web app |
| Testing | pytest, SPARQL regression queries, retrieval benchmarks |

Docling, Tika and OCR appear in the roadmap for Stage 1 and are **not** used —
see Q-03. They would only become relevant for new source formats.

Two notes on the keyphrase row. The roadmap names YAKE alone; the owner extended
it to three extractors because they fail differently and their **agreement is a
confidence signal** available before any expert grading (ADR-0019). And KeyBERT
is the one non-deterministic component in an otherwise deterministic candidate
pipeline — its sentence-transformer and version are pinned alongside the snapshot
pin and recorded on every candidate, because a silent model upgrade invalidates
every baseline measured before it.

## 6. Design constraints that outrank convenience

1. **Traceability.** Every assertion resolves to an exact passage in a versioned
   source. An assertion whose `source_content_hash` no longer matches upstream is
   stale and must be re-reviewed, not silently carried forward.
2. **Separation of candidate from approved** (ADR-0007), enforced by named graph
   and by directory.
3. **Reproducibility.** `graph/` is generated. Given the pinned snapshot, the
   approved inputs and the code, a rebuild produces the same graph. Hand-edited
   RDF in `graph/` breaks this and is prohibited.
4. **Explainability.** Every inferred assertion identifies its source facts, the
   axiom or rule that produced it, the date, and whether review is required.
5. **Prohibited inferences are tested.** The roadmap requires examples of
   conclusions the system must *not* draw. Those are test cases in `tests/`, and
   they are as important as the positive ones.

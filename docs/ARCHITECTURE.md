# ARCHITECTURE — intended shape of the system

What the system is meant to become, where each piece lives, and which roadmap
stage produces it. This is the target; `ROADMAP-STATUS.md` says how much of it
exists.

**Since S010 it is no longer all target.** Stages 5, 6 and 9 have a working
draft — modules in `ontology/draft/`, a built graph, a SHACL gate that passes and
thirteen competency queries (ADR-0056). Nothing is approved. Stages 7, 8 and 10
remain unbuilt.

**Two structural changes on 2026-09-08 (ADR-0079 to ADR-0088), and they reach
every section below.** The scope is now the **whole Manual**, not section 43 —
there is no boundary rule and no in-scope judgement for any passage (ADR-0081).
And an agent now **authors legal content** directly, stamped as never validated,
into a new `authored/` store, while `eval/gold/` freezes at the 190 expert-signed
records as the measurement yardstick (ADR-0079, ADR-0080). Stages 2, 3 and 4 are
open (ADR-0083). Where a paragraph below still reads as though section 43 were a
fence, it is stale and ADR-0081 wins.

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
src/tm_knowledge/         loader → candidate generation → authoring → RDF emission
        │
        ├──▶ review/      candidates awaiting a human   (a proposal with a score)
        │        │
        │        ▼        an agent commits to a judgement
        ├──▶ authored/    machine-authored legal content, stamped `unreviewed`
        │        │        (ADR-0079, ADR-0080)
        │        │
        │        ▼        recorded human decision, via tmk-transcribe
        ├──▶ eval/gold/   190 expert-signed records — FROZEN as the yardstick
        │        │
        │        ├──▶ vocab/       SKOS concept scheme           (Stage 3)
        │        ├──▶ ontology/    RDF/RDFS/OWL 2 RL modules     (Stage 5)
        │        │        │
        │        │        ▼
        │        └──▶ graph/       named graphs, PROV-O          (Stage 6)
        │                 │        reads BOTH stores; stamps every node
        │                 ├── shapes/    SHACL validation        (Stage 6)
        │                 └── queries/   SPARQL, incl. CONSTRUCT rules  (Stages 6, 9)
        │
        └──▶ search index + retrieval API               (Stages 7, 8)
                 │                must show review status at the point of use
                 ▼                (ADR-0082 — the constraint that replaced the gate)
        eval/    measures all of the above              (Stage 0, run continuously)
```

The one-way rule holds and gained a stage: `review/ → authored/ → eval/gold/`,
and only the last hop needs a recorded human decision (ADR-0007, ADR-0080).
Nothing flows back into `data/upstream/`.

**The graph reads both stores**, and since S016 it does (ADR-0091). One mapping,
run twice, into two named graphs: `graph/approved.ttl` from `eval/gold/` and
`graph/authored.ttl` from `authored/`. Every node of both carries `tmk:origin`
and `tmk:reviewStatus`; an authored relationship is a `tmk:AuthoredAssertion` and
never a `tmk:ApprovedAssertion`, so a query naming the second class cannot reach
the first. A fully populated ontology does not wait for review — but no figure
anywhere sums signed and authored records into one count (ADR-0080
consequence 3).

## 3. Directory map

| Directory | Holds | Stages | Notes |
|---|---|---|---|
| `docs/` | All project documentation, plus the two source documents | — | Start at `HANDOFF.md` |
| `eval/` | Competency questions, gold set, prohibited uses, harness, schemas | 0, and every stage after | `eval/gold/` **frozen** at 190 signed records as the measurement yardstick (ADR-0080). No pilot scope — the whole Manual is in scope (ADR-0081) |
| `data/` | Pinned upstream snapshot and derived intermediates | 1 (consumed) | Git-ignored except the pin manifest |
| `src/` | `tm_knowledge` Python package — all pipeline code | 2–10 | Stage 0 apparatus built; nothing for 2+ |
| `authored/` | **Machine-authored legal content, stamped `unreviewed`** (ADR-0079) | 0, 3, 4, 5 | The main knowledge store since 2026-09-08. Never read as validated. Read by `tm_knowledge.authored.store` and by nothing else; a record whose envelope does not validate is refused and named, never skipped (ADR-0089) |
| `review/` | Candidate registers awaiting human decision | 2, 3, 4 | A proposal with a score, not a committed judgement |
| `review/seed/` | Stage 0 example records, machine-written for expert correction (ADR-0043) | 0 | **Retired** — backlog resolved by authoring (ADR-0084) |
| `review/returned/` | Marked-up artefacts a person handed back (ADR-0050) | 0 | Inputs. Never edited, never regenerated |
| `review/decisions/` | What each returned artefact was taken to mean (ADR-0049) | 0, and 10 | Derived from `returned/`; verdicts and corrections verbatim |
| `vocab/` | SKOS controlled vocabulary | 3 | Approved only. Empty — the concepts are in `graph/approved.ttl`, built from `eval/gold/`, not promoted here |
| `ontology/` | RDF/RDFS/OWL 2 RL modules | 5 | Approved only. **Empty** |
| `ontology/draft/` | The candidate ontology — 9 modules, none approved | 5 | ADR-0057. Promoted one module at a time, on a recorded decision |
| `graph/` | Generated RDF, by named graph | 6 | Generated, and all of it committed (ADR-0070, supersedes ADR-0060). Four graphs: `source`, `approved`, `authored` (ADR-0091), `inferred` |
| `shapes/` | SHACL shapes | 6 | Gate before publication. Every shape has a violating fixture |
| `queries/` | SPARQL queries, `CONSTRUCT` rules, regression queries | 6, 9 | Each rule needs an approval record; both current rules are `PENDING` |
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

The draft in `ontology/draft/` implements all seven, plus two the roadmap does
not name. `relations.ttl` holds the closed predicate list and is generated from
the approved relationship register. `evaluation.ttl` holds the competency
questions, prohibited uses and relevance judgements, and it earns its place by
making PU-0004 structurally detectable: the prohibition, the question it attaches
to and the passages involved all have to be in one graph before a shape can see
the conflation.

The Document module also drops `Chapter` and `Paragraph` outright. They are in
the roadmap's list and the corpus does not carry them — some Manual subsections
are bold text that was never marked up as a heading (Q-10), so a class named
`Paragraph` would promise a structure that is not there.

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
| Complex structured extraction | **Gemini 3.8 Flash**, schema-constrained JSON (ADR-0087, ADR-0088 — HANDOFF Q3 closed in both halves). Credential in `GEMINI_API_KEY`; the model id lives in `config.DEFAULT_AUTHORING_MODEL` and nowhere else. Corpus text may be sent; an expert's review notes may not |
| Vocabulary | SKOS |
| Ontology | RDF, RDFS, OWL 2 RL |
| Ontology editing | Protégé / WebProtégé — not used; the modules are hand-written Turtle and `relations.ttl` is generated |
| Provenance | PROV-O + project fields |
| Graph processing | RDFLib — **in use since S010**, as the optional `[rdf]` extra (ADR-0056) |
| Validation | SHACL via pySHACL — **in use since S010** |
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
   and by directory — and since ADR-0079 the separation that matters most is
   signed from authored, enforced the same two ways plus a third: a stamp on
   every node, because a triple copied out of its named graph into a report, a
   prompt or a flattened union has left the boundary behind and the stamp is
   what survives (ADR-0091).
3. **Reproducibility.** `graph/` is generated. Given the pinned snapshot, the
   approved inputs and the code, a rebuild produces the same graph. Hand-edited
   RDF in `graph/` breaks this and is prohibited.
4. **Explainability.** Every inferred assertion identifies its source facts, the
   axiom or rule that produced it, the date, and whether review is required.
5. **Prohibited inferences are tested.** The roadmap requires examples of
   conclusions the system must *not* draw. Those are test cases in `tests/`, and
   they are as important as the positive ones.

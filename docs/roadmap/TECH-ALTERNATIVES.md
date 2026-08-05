# TECH-ALTERNATIVES — review of the roadmap's recommended stack

**Status:** advisory. **Authority:** derived, from public evidence about the tools
as at 2026-08-05. Nothing here changes a decision; it exists so that when a stage
starts, the choice is made once, deliberately, and against measurement.

The roadmap's own §3 permits this: *"Equivalent agency-approved products may be
substituted."* The roadmap is a source document and is not edited (ADR-0003,
`docs/README.md`) — this file annotates around it, in the same way `QUIRKS.md`
does for the data.

**Headline:** the stack has aged well. Nothing in it is abandonware and nothing is
a bad choice. Four items are genuinely worth revisiting, and one whole category of
tooling — encoder-based zero-shot information extraction — did not exist in usable
form when the roadmap's "rules vs. custom NER model vs. LLM" trichotomy was
written, and now sits squarely between the second and third options.

---

## 1. Verdict table

| Roadmap component | Verdict | Note |
|---|---|---|
| Python | **keep** | Not a question. |
| Docling | **moot for now** | Stage 1 is done by other means (Q-03). Revisit only for case law PDFs (Q-11). |
| Apache Tika | **moot for now** | As above. |
| spaCy (pipeline, `EntityRuler`, `PhraseMatcher`, regex) | **keep** | The deterministic components are the point and have no successor. §3.2. |
| spaCy custom NER model (Stage 2.3) | **consider replacing** | GLiNER-class models. **§2.1** |
| YAKE (keyphrase) | **keep — and measure against KeyBERT** | Not abandoned. Both are cheap. **§2.2** |
| spaCy `DependencyMatcher` (Stage 4.1) | **keep, add a middle tier** | GLiREL between patterns and the LLM. §3.3 |
| Sentence Transformers | **keep the library, update the models** | The library is the standard interface; the 2026 models are much better. §3.1 |
| Agglomerative / HDBSCAN clustering | **keep** | Fine as specified. §3.1 |
| Cross-encoder reranking | **keep, name a model** | `bge-reranker-v2-m3` / Qwen3-Reranker, still via the ST `CrossEncoder` API. §3.1 |
| LLM with schema-constrained JSON | **keep, sharpen the mechanism** | Constrained decoding is now standard; say so. §3.4 |
| SKOS, RDF, RDFS, OWL 2 RL, PROV-O, SPARQL, SHACL | **keep** | W3C standards, not products. No successors. |
| WebProtégé / Protégé Desktop | **keep for inspection; change the authoring flow** | The ontology is script-generated. **§2.3** |
| RDFLib | **keep** | Slow at scale, irrelevant at this scale. §3.5 |
| pySHACL | **keep** | Effectively the only Python option, and adequate here. §3.5 |
| Apache Jena Fuseki | **keep** | Stage 9 depends on Jena's reasoner. Oxigraph is the alternative to know. §3.5 |
| OpenSearch | **defer, behind an interface** | The corpus is 2,460 chunks. **§2.4** |
| Prefect / Airflow / GitHub Actions | **keep GH Actions; the real need is different** | Stage 10 wants content-hash incrementalism, not a scheduler. §3.6 |
| Streamlit review interface | **keep as UI, but the artefact is git-shaped** | §3.7 |
| pytest | **keep, add IR metric libraries** | Don't hand-roll nDCG. §3.8 |

---

## 2. The four worth an actual decision

### 2.1 Custom spaCy NER → GLiNER-class zero-shot extractors

**Where.** Roadmap Stage 2.3, "new entity discovery": *a custom spaCy
named-entity recognition model; an agency-approved LLM*.

That trichotomy — rules, or train a model, or call an LLM — has a fourth member
now. GLiNER is a sub-500M-parameter encoder that takes entity type names as
*input* at inference and extracts spans for them zero-shot, on CPU. GLiNER2 adds
a schema-driven interface covering extraction, classification and structured
fields in one model. There is a spaCy pipeline wrapper, so it drops into the
architecture the roadmap already describes rather than replacing it.

**Pros of swapping**

- Removes the training-data problem entirely. A custom spaCy NER model needs
  hundreds of annotated spans per type before it beats the `EntityRuler`, and
  Stage 0's gold set is 100–300 entities *in total* — nowhere near enough to
  train on, and it must be spent on evaluation, not training (ADR-0010).
- Type inventory becomes a config value. `GroundOfRefusal`, `EvidenceCategory`,
  `LegalTest` (roadmap Stage 5) can be tried, renamed and dropped in an
  afternoon. Retraining a spaCy NER model for each revision cannot.
- Runs locally on CPU. It sidesteps HANDOFF **Q3** — which LLM is agency-approved
  and whether Manual text may be sent to it — for the whole Tier 2 workload.
  That is a governance win, not just an engineering one.
- Apache-2.0, self-hostable, version-pinnable. `model` in ADR-0011's provenance
  block becomes a real, reproducible value rather than a drifting API endpoint.
- Still a candidate generator. Nothing about the review gate changes.

**Cons of swapping**

- Unverified on this domain. Its training distribution is general-web; Australian
  trade marks examination prose is not in it. Zero-shot ≠ accurate, and legal
  span boundaries ("ordinary signification", "honest concurrent use") are exactly
  where generalist extractors get sloppy.
- Type-name sensitivity. Output quality depends on the wording of the label
  passed in. That is prompt engineering wearing a different hat, and it needs the
  same discipline: pin the label set, version it, record it.
- Another model dependency, another ~500MB artefact, another thing to pin and
  patch.
- It does not replace §2.2's rules. Provisions, citations, dates and application
  numbers stay regex/`EntityRuler` — Tier 1 deterministic (ADR-0008). Only the
  *discovery* half moves.

**Recommendation.** Do not drop the custom-NER option from the roadmap; treat it
as superseded in practice. Order of attempt at Stage 2: rules → GLiNER →
LLM-under-schema. That ordering also happens to be CLAUDE.md rule 7 in ascending
order of cost and descending order of determinism.

---

### 2.2 YAKE vs KeyBERT — the one you asked about

First, two corrections to the assumption the question rests on.

**YAKE is not abandoned.** It looked dormant for years (0.4.8, April 2021) and
that reputation stuck. It shipped 0.6.0 in June 2025 and 0.7.3 on 9 February
2026, and now requires Python 3.10+. The upstream repository is `INESCTEC/yake`
(formerly `LIAAD/yake`). PyPI still carries `Development Status :: 3 - Alpha`.
See Q-16.

**KeyBERT is not newer technology than YAKE in any meaningful sense.** It is a
2020-era design — embed the document, embed candidate n-grams, rank by cosine
similarity, diversify with MMR or Max Sum. Its latest PyPI release is 0.9.0
(February 2025) with repository activity into April 2026. It is well maintained
and widely used; it is not a generational leap.

So this is not "outmoded vs. modern". It is a genuine trade-off, and it is the
cleanest possible example of a decision that should be *measured* rather than
argued — which is precisely what Stage 0 exists to make possible (ADR-0010).

**Pros of swapping YAKE → KeyBERT**

- Better reported accuracy where it has been compared head to head — one 2025
  evaluation put KeyBERT at 82.6% accuracy / 73.3% F1 against YAKE's 80.1% /
  71.1%, at roughly an order of magnitude more compute.
- **The strongest argument, and it is architectural, not accuracy-based:** Stage
  3 already requires Sentence Transformers embeddings of candidate terms for
  clustering. KeyBERT reuses that exact model. Candidate terms then arrive in the
  same vector space they will be clustered in, so the Stage 2 → Stage 3 boundary
  stops being a lossy hand-off between a statistical scorer and a semantic one.
  One model to pin, one embedding to record in provenance.
- Semantic coherence. YAKE will happily surface a frequent-but-empty phrase;
  KeyBERT ranks by similarity to the document's meaning, which suits the
  roadmap's target outputs ("acquired distinctiveness", "ordinary signification")
  better than raw statistics do.
- Composes with `KeyphraseVectorizers`, which generates candidates from
  part-of-speech patterns rather than fixed n-gram windows — materially better at
  multi-word legal noun phrases than either tool's defaults.
- Same author as BERTopic, so if Stage 3 ever wants topic modelling over the
  corpus the tooling is coherent.

**Cons of swapping**

- **It gives up determinism for the cheapest step in the pipeline.** YAKE is pure
  statistics: no model, no GPU, byte-identical output on the same input forever.
  KeyBERT's output is tied to a model version and to floating-point behaviour on
  the hardware that ran it. CLAUDE.md rule 7 prefers determinism where
  determinism is possible, and here it demonstrably is.
- **Scores are harder to threshold.** ADR-0008 permits Tier 2 auto-accept above a
  confidence threshold. KeyBERT scores are cosine similarities that are not
  comparable across documents of different length or topic; a fixed threshold
  means different things on a 3-sentence annex chunk and a long Part 22 chunk.
  The corpus is lopsided this way already (Q-10: 725 of 2,460 chunks are annex).
  YAKE's scores have the same limitation but its cost profile makes per-document
  top-*k* selection trivially affordable.
- ~100× slower, per the same comparison. Irrelevant at 2,460 chunks; relevant to
  Stage 10, which reprocesses on every upstream change.
- It inherits the general-domain embedding model's blind spots. Terms of art that
  look ordinary — "use", "mark", "goods" — are exactly where a general model's
  similarity judgements are weakest, and exactly where this corpus's meaning
  lives.
- The stated benefit is not free of the cost it claims to avoid: reusing the
  Stage 3 model means Stage 2 output silently changes whenever that model is
  upgraded. Two coupled stages, one pinned artefact.

**Also worth knowing, since neither is obviously right**

- **Contrastive term extraction.** Neither tool knows what "normal" English looks
  like. Ranking by *termhood* — a phrase's burstiness in this corpus against a
  background corpus — is the classical answer to domain terminology extraction
  and often beats both on exactly this task. Cheap to add, fully deterministic.
- **GLiNER2 / LLM-under-schema.** If a phrase must be typed as well as found
  ("this is an `EvidenceCategory`"), a schema-driven extractor does in one pass
  what YAKE + Stage 3 classification does in two.
- **Union, not choice.** These are Tier 2 candidate generators feeding a
  clustering step that deduplicates and a human who reviews clusters, not terms
  (roadmap Stage 3). Extra recall is cheap; missed terms are not. Running two
  extractors and unioning the output, with the generating method recorded per
  candidate, is very likely better than either alone — and it turns the question
  into data: after Stage 3, count which extractor's candidates survived review.

**Recommendation.** Don't swap. Put both behind one `KeyphraseExtractor`
interface, run both, record `extraction_method` per candidate (ADR-0011 requires
it anyway), and let the Stage 0 gold set decide. The bake-off costs a day.
Deciding by argument costs the ability to ever revisit it.

---

### 2.3 WebProtégé → ontology-as-files with ROBOT, Protégé for inspection

**Where.** Roadmap §3 and Stage 5, "Ontology editing: WebProtégé or Protégé
Desktop".

WebProtégé is maintained by Stanford's BMIR under NIH funding and is not going
anywhere. The problem is not the tool's health; it is that it does not fit the
workflow the same roadmap describes two paragraphs later — *"Python scripts should
generate draft ontology content from approved vocabulary records"* — nor ADR-0007,
which requires a recorded human decision for every promotion.

A collaborative web editor holds the ontology in its own datastore with its own
revision history. This repo's whole governance model is that the record of
approval is a reviewed commit.

**Pros of swapping to files + ROBOT in CI**

- The ontology becomes a diffable Turtle file. Review of an ontology change is a
  pull request, which is what ADR-0007's "recorded human decision" actually looks
  like here.
- ROBOT gives `report`, `reason`, `diff`, `template` and `verify` as CI steps, so
  malformed axioms and unintended entailments fail a build instead of being
  noticed later.
- `robot template` builds OWL from spreadsheets. Domain experts can supply class
  and property definitions in the medium they already use — the same medium
  Stage 0 uses for the gold set — without learning an ontology editor.
- One source of truth. Generated-from-vocabulary and hand-authored content live
  in the same tree under the same review gate; no export/import drift.

**Cons of swapping**

- ROBOT is Java and OBO-flavoured. Its conventions assume biomedical ontology
  practice, and some of its checks will be noise here.
- No editing UI for experts. WebProtégé's threaded notes, watches and permissions
  are real collaboration features, and "write Turtle" is not a substitute for
  them.
- Loses WebProtégé's per-entity discussion threads, which are a decent audit
  trail in their own right.
- A second Java dependency alongside Fuseki.

**Recommendation.** Not either/or. Files in git are the source of truth and the
place approval is recorded; Protégé Desktop is the inspection and visualisation
tool experts open to *read* the model; WebProtégé only earns its place if
multi-person concurrent editing turns out to be a real requirement. Decide at
Stage 5, not before.

---

### 2.4 OpenSearch — right answer, possibly the wrong stage

**Where.** Roadmap §3, Stage 7 and Stage 8.

OpenSearch remains a good fit and nothing has outclassed it for this shape of
problem: BM25 plus vector plus filters plus aggregations plus hybrid score
normalisation, in one system an agency can already be running. The 2026 field —
Elasticsearch, Qdrant, Weaviate, Milvus, Vespa — has converged on native hybrid
query support with RRF fusion, so the differentiator is no longer capability.

The observation is about scale. **The corpus is 2,460 chunks and 763 provisions.**
That is roughly a spreadsheet. A distributed search cluster is not required to
search it, and standing one up early buys operational burden before Stage 0 has
produced a single relevance judgement to tune against.

**Pros of deferring / starting smaller (SQLite FTS5 + an in-process vector index)**

- Zero infrastructure. The whole index rebuilds in seconds in CI, which makes the
  Stage 7 benchmark a test rather than an environment.
- Reproducible: the index is a file, so a retrieval regression is bisectable.
- Forces the search layer behind an interface, which is what makes the eventual
  OpenSearch decision cheap.
- Postgres + `pgvector` is a third option worth naming if Postgres is already the
  agency default — it collapses the store and the index into infrastructure that
  is already approved and supported.

**Cons of deferring**

- Two implementations eventually, and the second one always reveals that the
  interface leaked.
- No hybrid score fusion, field weighting, aggregations or analyzers out of the
  box — you rebuild small pieces of them, badly.
- If OpenSearch is already the agency's approved search platform, deferring is
  pure detour; the approval process is the long pole, not the code.
- Learned-sparse retrieval (SPLADE, ELSER) is a real capability on the mature
  platforms and has no small-scale equivalent.

**Recommendation.** Keep OpenSearch as the named target. Build Stage 7 behind a
`Retriever` interface with a local implementation first, and stand up OpenSearch
when there is a benchmark to justify the tuning. If procurement lead time is the
binding constraint, start the procurement now and the code later.

---

## 3. Everything else — keep, with notes

### 3.1 Sentence Transformers: keep the library, name the models

Version 5.6.1 (July 2026), actively developed, and still the standard interface
for embeddings, sparse encoders and cross-encoders. Nothing has displaced it.

What *has* moved is the models, and the roadmap names none. Current
self-hostable, Apache-2.0 candidates worth benchmarking at Stage 3:

- **Qwen3-Embedding** — leads the multilingual MTEB board; supports
  instruction-conditioned embeddings and Matryoshka output dimensions.
- **BGE-M3** — the safe production default; multi-vector and sparse output.
- **EmbeddingGemma-300M** — 300M parameters, CPU-viable, for constrained
  environments.
- Reranking: **`bge-reranker-v2-m3`** as the default, **Qwen3-Reranker** where
  the notion of relevance needs to be stated in an instruction — plausibly
  useful here ("relevant to a distinctiveness objection" is not generic
  relevance).

Pin the model and record it in every provenance block (ADR-0011). An unpinned
embedding model means yesterday's clusters are unreproducible.

### 3.2 spaCy: keep

3.8.14 (March 2026), still on the v3 line — v4 has been in progress a long while,
which is worth knowing but is not a reason to move. Nothing replaces
`EntityRuler`, `PhraseMatcher`, the `Matcher` or the tokenisation and sentence
segmentation the rest of the stack sits on. Stage 10's active-learning loop
("accepted entity labels become EntityRuler patterns") depends on it directly.

### 3.3 `DependencyMatcher` (Stage 4.1): keep, and add a middle tier

Dependency patterns are the right tool for the recurring wording the roadmap
lists (`[Paragraph] cites [Case]`), and they are deterministic and auditable.
**GLiREL** — zero-shot relation extraction over pre-identified entity pairs, from
the GLiNER family — is worth trialling between patterns and the LLM, for the same
reasons as §2.1.

Caveat specific to this corpus: legal relation labels (`interprets`, `overrules`,
`qualifies`) sit in Tier 3 (ADR-0008), so nothing here shortens the review path.
The gain is recall on candidate generation, not throughput of approval.

### 3.4 LLM structured extraction: keep, sharpen the mechanism

The roadmap says "schema-constrained JSON output", which was aspirational when
written and is now table stakes. Worth stating explicitly in any implementation:

- **Constrained decoding** (XGrammar, llguidance) makes malformed output
  impossible rather than retried — default in vLLM/SGLang for self-hosted models.
- **Hosted structured outputs** do the same server-side for API models.
- **Instructor** or **BAML** at the application layer for Pydantic-validated
  parsing with retry; the schema *is* the contract.
- Evidence spans are the part that no library enforces. Requiring exact
  `source_span` offsets that must verify against the upstream `text` before a
  record is written is this repo's job, and it is the single most important
  control on the LLM steps (CLAUDE.md rule 8, ADR-0011).

Blocked on HANDOFF **Q3** regardless of tooling.

### 3.5 RDFLib, pySHACL, Fuseki: keep

- **RDFLib** 7.6.0 (Feb 2026). Slow on large graphs; irrelevant at this corpus
  size. If it ever bites, `oxrdflib` swaps the store for Oxigraph's Rust engine
  without changing the API.
- **pySHACL** 0.40.1 (July 2026). Effectively the only maintained Python SHACL
  implementation, and adequate here. SHACL-AF also covers the "decision tables
  for bounded procedural logic" of §7/ADR-0009 without new dependencies.
- **Fuseki.** Keep — and note *why*, because it is not obvious: **Stage 9 depends
  on Jena's inference and rule engine**, so swapping the server swaps the
  reasoner too. **Oxigraph** is the alternative to know (single Rust binary, no
  JVM, fast bulk load, trivial in CI) but it has no reasoner and no SHACL, and
  cannot cancel a running query. For a production successor, **GraphDB** or
  **RDFox** are the products that would collapse Stages 6, 7 and 9 into one
  supported system — commercial licences, and the roadmap already anticipates
  exactly this substitution.

### 3.6 Scheduling: keep GitHub Actions; the real Stage 10 need is different

Prefect, Airflow and Dagster are all healthy, and Dagster's asset orientation
maps neatly onto ADR-0006's artefact-typed directories. But Stage 10's actual
requirement is *"process only the affected passages"*, keyed on upstream
`content_hash` — that is content-addressed incremental rebuild, not scheduling.
A `Makefile` or a build tool with content-hash dependency tracking gets closer to
it than any scheduler, and GitHub Actions is enough to run it. Revisit only when
there is something long-running enough to need orchestration.

### 3.7 Streamlit review interface: keep the UI, but the artefact is git-shaped

Streamlit 1.61.0 (August 2026), healthy. Alternatives that are *purpose-built*
for this and worth a look at Stage 2:

- **Argilla** — review queues, roles, annotator agreement, Python SDK. Closest
  fit to "expert reviews clusters, not terms". Now under Hugging Face; check its
  maintenance cadence before depending on it.
- **Label Studio** — the mature general-purpose option, self-hostable, broadest
  task-type support.
- **Prodigy** — commercial, spaCy-native, scriptable; the natural home for Stage
  10's active-learning loop if a licence is acceptable.
- **Gradio** / **FastHTML** — if the objection to Streamlit is only ergonomic.

The thing none of them give you is the artefact ADR-0007 and HANDOFF **Q4**
actually require: a *recorded decision* that lives where the approved knowledge
lives. Every one of them ends in an export back to this repo. So consider the
lightweight inversion first — candidates land in `review/` as YAML/JSONL, review
is a pull request, approval is the merge, and the reviewer and date come from git
for free. Then a UI is a rendering of the queue rather than the system of record.

### 3.8 pytest: keep, and don't hand-roll the metrics

Roadmap §5 asks for Recall@10, Precision@10, MRR and nDCG. Use **`ranx`**,
**`ir_measures`** or **`pytrec_eval`** rather than implementing them — nDCG in
particular has several defensible definitions, and an evaluation harness whose
metric implementation is itself untested is not a measurement (ADR-0010).

---

## 4. Gaps — things the roadmap does not name at all

Not substitutions. Absences, listed here because they surface at the same moment
a stack decision does.

1. **Model version pinning and an LLM evaluation harness.** ADR-0011 requires
   `model` on every record. That field is meaningless against a moving API
   endpoint. Whatever is chosen under Q3 needs a pinned version, and the LLM
   steps need regression tests over fixed inputs (`promptfoo`, `inspect-ai`, or
   plain pytest with recorded fixtures).
2. **Retrieval strategy, as distinct from retrieval infrastructure.** Upstream
   has already chunked the corpus, and Q-10 warns that the chunks are lopsided.
   Contextual retrieval — prefixing each chunk with generated context before
   embedding — and late-interaction models are Stage 7/8 design choices with more
   effect on Recall@10 than the choice of search engine.
3. **A background corpus.** Needed for the contrastive term extraction in §2.2,
   and useful for calibrating "is this phrase a term of art or ordinary English".
   Nothing in the programme currently holds general Australian legal English.
4. **Case law acquisition tooling.** HANDOFF **Q6** / Q-11. If decision texts
   ever come in scope, that is where Docling, Tika and OCR stop being moot, and
   the licensing problem is larger than the parsing one.

---

## 5. How to decide any of this

Every question in §2 has the same shape: two defensible options, no way to choose
by argument, and a cheap experiment that settles it. The programme already has
the mechanism — it is Stage 0, and it is the reason ADR-0010 puts a failing
harness before any extraction work.

So the operative rule is not "prefer KeyBERT" or "prefer YAKE". It is:

> Name the interface before the implementation. Record `extraction_method` on
> every candidate. Run the alternatives side by side against the gold set. Let
> the measurement pick, and write the result up as an ADR so the next session
> does not reopen it.

Which is only the roadmap's own operating principle applied to the roadmap's own
technology choices.

---

## Sources

Checked 2026-08-05.

- YAKE releases and Python support — [PyPI `yake`](https://pypi.org/project/yake/), [INESCTEC/yake](https://github.com/INESCTEC/yake)
- KeyBERT — [PyPI `keybert`](https://pypi.org/project/keybert/), [MaartenGr/KeyBERT](https://github.com/MaartenGr/KeyBERT)
- YAKE/KeyBERT head-to-head — [Evaluation of Keyword Extraction using YAKE and KeyBERT (2025)](https://jurnal.usk.ac.id/riwayat/article/view/48626/24657)
- Contrastive/burstiness term extraction — [A statistical significance testing approach for measuring term burstiness](https://arxiv.org/pdf/2310.15790)
- GLiNER — [urchade/GLiNER](https://github.com/urchade/GLiNER), [GLiNER2](https://arxiv.org/html/2507.18546v1), [spaCy wrapper](https://spacy.io/universe/project/gliner-spacy)
- GLiREL — [GLiREL: Generalist Model for Zero-Shot Relation Extraction (NAACL 2025)](https://aclanthology.org/2025.naacl-long.418/)
- Embedding and reranker models — [Open-source embedding models 2026](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models), [Reranker comparison 2026](https://docs.bswen.com/blog/2026-02-25-best-reranker-models/)
- Hybrid search convergence — [Hybrid search: BM25, vector and reranking (2026)](https://www.digitalapplied.com/blog/hybrid-search-bm25-vector-reranking-reference-2026)
- Structured output and constrained decoding — [LLM structured output libraries ranked (2026)](https://techsy.io/en/blog/best-llm-structured-output-libraries)
- Fuseki vs Oxigraph — [SPARQLoscope DBLP benchmark results](https://labs.flur.ee/blog/sparqloscope-dblp-benchmark-results)
- Protégé / WebProtégé maintenance — [protege.stanford.edu](https://protege.stanford.edu/software/), [protegeproject/webprotege](https://github.com/protegeproject/webprotege)
- Argilla — [argilla-io/argilla](https://github.com/argilla-io/argilla)
- Library versions (spaCy 3.8.14, sentence-transformers 5.6.1, RDFLib 7.6.0, pySHACL 0.40.1, Streamlit 1.61.0) — PyPI JSON API, 2026-08-05

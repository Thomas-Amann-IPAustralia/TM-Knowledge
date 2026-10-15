# Trade Mark Ontology Review

TM Knowledge  \|  Technical quality, legal meaning and practical value

15 October 2026  •  Repository snapshot 6a75eefadd98

### Executive judgement

Continue developing this demonstrator, with a focused repair programme before relying on its graph as a source of current legal propositions. The repository has unusually explicit provenance, a preserved expert baseline, useful review tooling and a substantial reproducible test suite. Those are valuable foundations. The present ontology and serving paths nevertheless contain reproducible semantic and validation defects.

The most consequential issues are that the declared OWL semantics can identify a Manual passage with a statutory provision; production validation omits the inferred graph; corrected historical relationships remain available through current competency queries; and several current machine-authored relationships lose conditions or negation from their evidence.

The evidence also does not establish a general search improvement. In the latest stored benchmark, ontology search with a model reading the question scores 0.701 against keyword search at 0.702 on nDCG@10. This is compatible with useful benefits elsewhere, but those benefits need direct measurement.

| **Dimension** | **Assessment** |
| --- | --- |
| Demonstrator and review workbench | Worth continuing. Preserve the source and review architecture. |
| Current legal propositions | Targeted source checks reveal errors that require correction and a broader expert review. |
| Validation and RDF interoperability | Repairs required before the graph can support the stated governance and OWL claims. |
| Operational examiner use | Use only within the declared demonstrator scope until the priority gates are met. |
| Measured added value | Search advantage is unproven overall; evaluate explanation, source tracing and change impact separately. |

### First actions

- Fix evidence cardinality, validate all graphs, and make deployment depend on those checks.

- Create one current-assertion view and route queries, exports and search through it.

- Correct the six identified relationship examples; preserve conditions, polarity and source scope.

- Freeze the evaluation inputs and rerun a fair comparison after the semantic repairs.

This report contains 12 prioritised findings, concrete acceptance tests and a staged implementation backlog. It reviews the repository as a demonstrator, not as an intended automated examination decision system.

## 1  Scope and evidence

The review covers the nine draft ontology modules, generated RDF, source and authorship records, correction overlays, SHACL and Python validation, competency queries, inference rules, search integration, evaluation artefacts and publication workflow. Repository documentation and its earlier 8 October ontology review were considered, but findings were checked against the later code and data actually reviewed.

| **Baseline** | **Reviewed value** |
| --- | --- |
| Repository | Thomas-Amann-IPAustralia/TM-Knowledge |
| Exact commit | 6a75eefadd982c29190b1f92f451de5168a29508 |
| Commit date | 12 October 2026, 22:24:36 +11:00 |
| Pinned upstream | manual-XtrACTor at c490a9927f1ab67c1c2fe4afdc758c79f35430c8 |
| Review approach | Read-only code and data inspection; rebuilds; existing tests; isolated malformed-data probes; targeted official-source checks. |
| No changes or model expenditure | Repository records were not edited. No fresh paid extraction, reading, judging or answering calls were made. |

### What was verified

The committed graph reproduces from its pinned corpus. The harness and SHACL commands were run, the test suite was exercised in snapshot and non-snapshot partitions, and the stored search measurements were recomputed offline. Independent probes checked source identity under OWL rules, inferred-graph validation, graph placement, missing evidence fields and SKOS hierarchy integrity.

The semantic review checked all record structures and graph-wide counts, then examined selected legally consequential relationships against their exact supporting passages. Selected examples were also checked on the official IP Australia Manual and Federal Register of Legislation. These checks establish specific defects; they do not estimate the error rate of all 352 authored relationships.

### Evidence labels used in the findings

| **Label** | **Meaning** |
| --- | --- |
| Reproduced | Observed by executing the relevant code, query, graph analysis or controlled probe. |
| Source comparison | Current relationship compared with its cited passage; legal implications remain subject to expert adjudication. |
| Static inspection | Confirmed in implementation or configuration; no live deployment failure was induced. |
| Design recommendation | A proposed improvement, distinguished from an existing defect. |

The review does not certify the ontology’s substantive legal completeness, audit every case citation, test live account configuration, or assert that the pinned legislation is current. Full case texts are not present in the corpus. Source references at the end of the report identify the reviewed files and official materials.

## 2  What exists and what works

| **Layer** | **Current inventory** | **Interpretation** |
| --- | --- | --- |
| Source corpus | 500 pages; 54 Parts; 2,460 chunks; 763 provisions; 5,813 legislative units | Searchable corpus and curated RDF coverage are different quantities. |
| Draft schema | 9 modules; 89 declared OWL classes; 52 dictionary predicates | A broad conceptual framework, including intentionally unpopulated future modules. |
| Concept vocabulary | 164 concepts: 52 signed and 112 authored | All 164 type assignments are machine-authored. Concept approval does not approve its added type. |
| Relationships | 35 historical signed assertions; 352 authored assertions | 15 signed assertions are marked corrected. There are 20 remaining current signed relationships. |
| Authored records | 628 concepts, types and relationships; 36 correction records separately | Authorship, review status and currentness must remain distinct. |
| Source RDF | 65,322 triples; 1,056 chunks; 208 pages | A selected subset, not a graph representation of every corpus passage. |
| Other RDF | Approved 3,575; authored 13,940; inferred 2,315; schema 2,104 triples | Named graphs provide useful provenance boundaries if consumers enforce them. |
| Inference output | 192 assertion nodes: 5 candidate and 187 approved-rule results | These are bounded outputs, not legal examination decisions. |

### Strengths to retain

The frozen 190-record signed baseline and correction overlay preserve human decisions without silently rewriting history. Source references, offsets, hashes, model identities, reasoning and review status make errors inspectable. The current authored concept, type and relationship evidence entries all include spans, hashes and quotes; the defects described later concern enforcement and export fidelity, not a blanket absence of evidence.

The predicate dictionary now supplies explicit readings and expected subject and object kinds. Keeping those expectations separate from narrow OWL domains and ranges avoids accidental reclassification. Recent duplicate cleanup and the October structure review are real improvements; earlier findings should not be carried forward without retesting.

The project distinguishes law from Manual practice, extraction confidence from legal confidence, and candidate rules from approved rules. The UI exposes machine-authored and unreviewed status. Negative fixtures and a deterministic rebuild provide a solid base for the additional tests proposed here.

Empty evidence, examination and role classes are intentional scaffolding. Populating them merely to improve counts would add risk without proving value. The present priority is coherence of the content already served.

Evidence: \[R1–R3, R7, R10\]; graph rebuild and independent counts at the reviewed commit. The builder’s 671 resolved legislative targets include provisions and finer units; they are not 671 distinct section-level provisions.

## 3  Prioritised findings

P1 means resolve before a trusted pilot or downstream use of graph assertions. P2 means complete in the next development cycle before making broader quality or value claims. Priority reflects the current demonstrator’s intended use; it is not a vulnerability severity score.

| **ID** | **Priority and finding** | **Primary owner** | **Completion evidence** |
| --- | --- | --- | --- |
| F01 | P1  Functional evidence property merges sources | Ontology engineer | Multiple evidence sources remain distinct under supported reasoning. |
| F02 | P1  Validation misses inferred data and graph placement | Validation engineer | Production-path malformed-graph probes fail. |
| F03 | P1  Publication has no dependency on validation | Build maintainer | Invalid data at a commit blocks publication of that commit. |
| F04 | P1  Corrected relationships leak into queries | Graph and query owner | All current views exclude superseded assertions. |
| F05 | P1  Edges lose legal conditions and polarity | Trade mark expert with modeller | Identified records adjudicated; scoped propositions preserve their meaning. |
| F06 | P2  Concepts lack definitions and consistent boundaries | Vocabulary editor and expert | Definitions and scope notes for the 164 concepts, with review provenance. |
| F07 | P1 before OWL use; otherwise P2  Datatype, SKOS and profile defects | Ontology engineer | Datatype checks, SKOS integrity and declared profile checks pass. |
| F08 | P2  Evidence export and schema are weaker than the source records | Data engineer | Span-level provenance round-trips and incomplete textual evidence fails. |
| F09 | P2  Coverage and currency are not interchangeable | Corpus and product owners | Separate coverage views and explicit source versions in releases. |
| F10 | P2  Search value is not established overall | Evaluation and search owners | Held-out task results support a specific, bounded benefit claim. |
| F11 | P2  Historical scores are not reproducible from current grades | Evaluation engineer | Immutable experiment bundles reproduce published scores. |
| F12 | P2  Documentation and release status disagree | Maintainer | A generated status manifest agrees with documentation and artefacts. |

F01, F02, F04 and parts of F07 are demonstrated technical defects. F05 supplies six source-entailment cases for corrective action. F06, F09 and F10 also involve design and product decisions: the recommendations make those decisions explicit instead of treating every modelling choice as an error.

## 4  F01  Keep evidence sources distinct

Priority P1  •  Reproduced  •  Confidence high

### Finding and consequence

tmk:sourcePassage is declared an owl:FunctionalProperty, while build.\_origin adds one sourcePassage link for every evidence item. The current graph has 67 subjects with multiple distinct targets; 21 have both a Manual passage and a legislative provision. In OWL, a functional object property does not reject the second value. It entails that the two values denote the same individual.

A focused reasoning probe on GC-0054, prohibited sign, reproduced this consequence using the actual schema and record. Its evidence includes TMM/Part31/1#1 and TMA1995/s39. OWL RL rule closure added owl:sameAs between those two sources, then reported that the explicitly disjoint ManualPassage and LegislativeProvision classes shared individuals.

This is a latent interoperability and reasoning defect. The current validator uses no OWL inference, and the search implementation is custom; this review does not claim that today’s search physically merges the two documents. It does show that the exported ontology contradicts the project’s central separation of legislation and practice when its declared semantics are used.

### Recommended change

- Remove functionality from the multi-valued source-support property. Do not discard legitimate sources to satisfy cardinality.

- Represent each evidence span as a separate node linked to its assertion or definition. Give that node exactly one source passage, plus its offsets, quote, content hash and evidence role.

- Keep authority kind on the source. Keep extraction basis and review decisions on the assertion. A second supporting source must not alter either source’s identity.

### Acceptance checks

| **Test** | **Required result** |
| --- | --- |
| GC-0054 regression | Both source links remain. No source-to-source owl:sameAs or authority-class contradiction appears. |
| Two Manual passages | Both are preserved as independent evidence items with separately checkable spans. |
| Mixed Manual and Act support | The UI and RDF retain distinct authority kinds and exact source locations. |
| Malformed evidence span | A span node with two source targets fails validation; its parent assertion may have several evidence spans. |

The smallest immediate patch is to remove the incorrect functional declaration and add a regression test. Evidence nodes are the durable repair and also address F08.

Evidence: \[R2\] ontology/draft/provenance.ttl:74; src/tm\_knowledge/ontology/build.py:684–716. Probe used owlrl 7.6.2 with OWLRL\_Semantics; \[S1\] specifies functional-property semantics.

## 5  F02 and F03  Enforce the gates

### F02  Validate the full dataset and its graph boundaries

Priority P1  •  Reproduced. validate.\_flatten includes source, approved, authored and default graphs, but omits the inferred graph. InferredAssertionShape and the bounded-reasoning checks therefore cannot inspect assertions that exist only where inference output belongs.

| **Controlled input to validate.run** | **Observed result** |
| --- | --- |
| InferredAssertion in inferred graph, with no rule, derivation or review status | Passes: conforms true, exit 0, no findings. |
| The same node added to the default graph | Fails: conforms false, exit 1, three findings. |
| Machine-authored assertion with a complete unreviewed envelope placed in approved graph | Passes: conforms true, exit 0, no findings. |

The third probe exposes a separate issue: flattening loses graph membership. A shape checking an authored stamp against an ApprovedAssertion type does not check which named graph contains the record. Current shape-unit tests that call pySHACL directly on a flat Graph do not establish that the production dataset path enforces either boundary.

Include inferred output in the validation view, then add dataset-level checks using GRAPH patterns or explicit graph-aware Python checks. Validate assertion origin, review status and permitted placement before flattening. Do not require each concept IRI to appear in only one graph: a signed concept can legitimately acquire a machine-authored type or correction overlay.

Acceptance: run the exact three probes above through the CLI or production entry point; all must fail for the intended reason. Add positive fixtures for legitimate cross-graph concept enrichment, plus inferred legal-outcome and missing-provenance negatives. Retain candidate-rule quarantine after every export.

### F03  Make publication depend on successful validation

Priority P1  •  Static inspection. The Pages workflow fetches the corpus and generates explorer and workbench data, then deploys. It has no dependency on the separate harness workflow and does not run the harness, SHACL or graph-drift checks itself. A separate failing workflow is not a deployment gate.

Create a reusable validation job or run the same required commands in the Pages workflow before generation and upload. Require the pinned corpus for this gate; a release must not treat skipped source checks as verified. Preserve the distinction between known completeness gaps and genuine defects, but publish their counts in a manifest.

Acceptance: introduce an invalid fixture on a test branch and demonstrate that no publication artefact can reach deployment for that SHA. A valid build must record the tested SHA, corpus pin, validator versions, result counts and explicit waivers for any accepted gaps.

Evidence: \[R3\] validate.py:121–145; shapes/inference.ttl and origin shapes; \[R4\] .github/workflows/pages.yml and harness.yml. Live deployment was not triggered.

## 6  F04  Serve current assertions consistently

Priority P1  •  Reproduced

### Finding

The correction system correctly preserves signed history. The graph builder marks 15 of the 35 signed relationship assertions as corrected and suppresses their old direct relationship triples. However, several competency queries select the historical reified assertions from the approved graph without excluding isCorrected records. They can consequently return propositions the serving overlay has already withdrawn.

| **Query** | **Observed exposure** |
| --- | --- |
| CQ-0009 | Returns GR-0008, connotation requiresElement reputation, and corrected GR-0056. GR-0008 has a replacement, GR-0680, with a different reading and direction. |
| CQ-0011 | Returns corrected GR-0042 when answering the descriptive-term question. |
| CQ-0021 | Returns corrected GR-0001 in the source-provenance query. |
| CQ-0024 | Summarises all 35 historical signed relationships, rather than the 20 remaining current signed ones. |

Approval is a historical review decision; it is not a complete currentness predicate. Retaining the record is correct. Presenting it without correction status in a current answer is not. Query comments acknowledge some limits, but comments do not protect consumers of the result rows.

### Recommended change

- Define a single effective-assertion view. Its policy should combine correction status, rejection, staleness, origin and review status, while keeping those fields separate.

- Offer explicit current and historical query modes. Current results exclude withdrawn assertions; historical results include correction links, status and replacements.

- Reuse that view in SPARQL, rule inputs, search relationship extraction, UI payloads and exports. Approved-only mode must not silently include an unreviewed replacement; it should show the gap or link to the proposed replacement.

- Add exact-result tests for these queries. Checking that a query executes or returns a row is insufficient when the wrong historical row can satisfy the test.

### Change impact also needs a declared view

RULE-0002 draws on approved-graph dependencies. That can be a valid bounded contract, but it does not cover all authored concepts, types and relationships. State whether a result means recorded approved dependencies or the broader active knowledge view. A zero-result query must not imply that a statutory change has no legal consequences.

Acceptance: every corrected ID remains retrievable historically, disappears from current assertion results, and resolves to the correct replacement or explicit withdrawal. Show distinct counts for historical signed, current signed and current machine-authored records.

Evidence: \[R5\] build.py correction handling; queries/competency/CQ-0009.rq, CQ-0011.rq, CQ-0021.rq, CQ-0024.rq; queries/rules/RULE-0002-change-impact.rq.

## 7  F05  Preserve the proposition in the source

Priority P1  •  Targeted source comparison  •  Six current records identified

A source citation can be perfectly accurate while its extracted relationship is wrong. The following records exist in the current authored set and retain valid supporting text. The problems arise when the subject, predicate or object compresses that text into a stronger or different proposition. They remain labelled unreviewed, which is helpful but does not make them suitable for unqualified reuse.

### GR0432  Assignment requires Commission consent

The edge links the general assignment concept to Commission consent. The cited passage concerns recording an assignment of an unregistered certification trade mark after the relevant documents have been sent to the Commission. Manual 35.10 expressly distinguishes the earlier stage, when assignment may occur without that consent. The current Act’s section 180A also makes the procedural stage material. \[R6, S5, S6\]

Action: replace the unconditional projection with a scoped assertion containing mark category, registration stage, document-referral condition and the recordal requirement. Test the before-referral and after-referral cases separately. Do not infer that every assignment requires Commission consent.

### GR0167  Revocation of acceptance precedes examination

The cited sentence is a negative statement about the procedure available after cessation of protection of a protected international trade mark. It does not assert the positive, generally applicable sequence represented by this edge. Other domestic procedures may involve re-examination; that possibility does not justify this extraction from this source. \[R6, S7\]

Action: withdraw this positive edge for the cited passage. Represent the excluded sequence within the PITM context, or retain it only as a qualified textual proposition pending review. Any positive domestic sequence needs its own supporting passage and scope.

### GR0521  Old register becomes Register of Trade Marks

The source says that disclaimers recorded under the repealed Act became particulars on the new Register. The edge makes the registers themselves the subject and object of the transition. This is a subject-object extraction error, not merely a missing qualifier. \[R6, S8\]

Action: withdraw or replace it with a proposition about disclaimer particulars and the commencement transition. If the required concept does not exist, leave a reviewable proposition rather than forcing it into an unsuitable pair of existing concepts.

### Acceptance across these cases

A reviewer should be able to read the complete assertion, compare it with its evidence and reject a plausible but stronger paraphrase. Test at least one near case that changes the controlling condition. Neither graph connectivity nor a more specific predicate is evidence that a relationship is legally supported.

## 8  F05  Repair the representation

| **Record and current edge** | **Problem** | **Action** |
| --- | --- | --- |
| GR-0140<br>Owner or authorised user owns internet domain name | A disjunctive role is reduced to ownership. Being an authorised user does not establish ownership of the domain. | Separate registrant and authorised-user conditions, and preserve the section 43 context. |
| GR-0437<br>Owner or authorised user owns phoneword<br>Modality must | The source describes reconsidering a ground when either ownership or authorised use is confirmed. It does not impose ownership on every authorised user. | Represent the alternative evidence conditions and procedural consequence; remove the ownership obligation. |
| GR-0495<br>Acceptance resultsIn condition of registration | A discretion to accept subject to conditions under section 44(3) becomes an unconditional result. Stored modality is not part of the direct triple. | Represent conditional acceptance as an available decision, with power, actor and context; withhold the general causal projection. |

These cases support a review of the entire current relationship set, with particular attention to must, may, if, unless, only, not, disjunctions and transitions. An earlier model audit predates some October restructuring; its error rate cannot be applied to the present 352 records. Structural edits need a renewed semantic review, even when they make the map more connected.

### A minimal qualified assertion pattern

Extend the existing reified assertion instead of replacing the whole architecture. For GR-0432, the following is a proposed representation to be adjudicated by a trade mark expert, not a newly approved legal rule.

| **Field** | **Illustrative content** |
| --- | --- |
| Core proposition | Recording the specified assignment requires evidence of Commission consent. |
| Scope | Australian certification trade mark; application pending; not yet registered. |
| Condition | Required documentation has already been sent to the Commission. |
| Polarity and modality | Positive requirement; keep separate from its conditions and evidence. |
| Evidence and authority | Individual Manual and Act evidence spans, independently identified. |
| Lifecycle and review | Current or superseded; authored or signed; unreviewed or approved. |
| Projection policy | No unconditional assignment-to-consent triple outside the stated scope. |

For the demonstrator, structured scope fields plus human-readable conditions are sufficient. Full executable legal logic is not necessary. Navigation edges can remain useful if clearly identified as topical links and never silently promoted into general legal rules. Later rule execution would require separately approved semantics for alternatives, exceptions, temporal applicability and unknown facts.

Evidence: \[R6, R13\]; Manual 29.8, 29.7 and 28.5 \[S9–S11\]. Search currently expands neighbouring concepts without using relationship polarity, modality or direction as a retrieval policy.

## 9  F06  Define the concepts being related

Priority P2  •  Reproduced inventory and design recommendation

### Finding

None of the 164 LegalConcept nodes has a skos:definition. The authored concept format contains labels, boundary labels, definition sources and notes, but no explicit definition field. The 51 skos:definition statements in the RDF describe predicates, not the legal concepts. This is a deliberate historical design choice, not a missing-file accident.

A source list establishes where to investigate meaning; it does not specify the intended meaning of the concept in this vocabulary. Without definitions, reviewers can agree on a label while disagreeing about its extension, category or permissible relationships. The current policy already permits clearly labelled machine-authored content, so definitions can be proposed and reviewed without inventing human approval.

### Recommended vocabulary record

| **Element** | **Purpose** |
| --- | --- |
| Preferred and alternative labels | Control wording and retrieval variants without asserting equivalence between distinct legal ideas. |
| Concise definition | State what the concept denotes in this ontology and its jurisdictional scope. |
| Scope note and counterexample | Explain nearby concepts that are excluded and how to distinguish them. |
| Evidence spans | Support the definition and record any synthesis across sources. |
| Review provenance | Keep approval of the definition separate from approval of the concept label, type or relationship. |

### Resolve document and process ambiguity

GC-0043, divisional application, and GC-0142, application for removal, are typed procedural\_step. GC-0131, trade mark application, and GC-0111, convention application, are typed instrument\_or\_record. These may reflect defensible senses of “application”, but those senses are not explicitly defined. Decide whether each node denotes a filed record, a request, a proceeding or an act of applying. Split senses only where a real competency question needs the distinction.

Prioritise connotation versus denotation; deception versus deceptive similarity; trade mark ownership versus domain registration or authorised use; assignment versus transmission; acceptance versus registration; and application documents versus application procedures. Keep the existing three-family, eleven-kind navigation system if it helps users, while making its classification rules explicit.

### Acceptance

Produce a review pack for all 164 concepts with definitions, source spans, proposed types and disputed boundary cases. The expert should adjudicate the full set as a coherent vocabulary. Track approval at the statement level so that an approved label does not confer approval on a newly authored definition. Do not mass-populate empty classes or equate a SKOS concept hierarchy with an OWL subclass hierarchy.

Evidence: \[R7\] authored/concepts.yaml, authored/concept-types.yaml, eval/gold/concepts.yaml and their schemas; \[R8\] legal-concepts.ttl. Governance wording in ontology/draft/README.md needs reconciliation with the later authorship policy.

## 10  F07  Align the declared semantics

Priority P1 before OWL reasoning or semantic reuse; otherwise P2  •  Reproduced and static inspection

### Datatype declarations disagree with emitted literals

Every confidence literal found in the union graph is xsd:double: 647 statements. The declared range is xsd:decimal, because build.\_origin converts values through Python float. The GC-0054 reasoning probe reported a decimal/double datatype contradiction for 0.85. Separately, twelve properties declared with xsd:string ranges carry language-tagged text. Examples include authoringReasoning, expertShouldCheck and notLabel.

Choose the intended literal types and enforce them at build time. For decimal confidence, use Decimal from the textual value and an explicit xsd:decimal datatype. Use rdf:langString or another deliberately chosen literal range for language-tagged prose, and xsd:string for identifiers and enumerations. Add SHACL datatype and range checks; do not rely on inference to repair literals. \[R2, R8, S2\]

### One SKOS semantic integrity conflict remains

GC-0017, geographical reference, is skos:related to GC-0018, geographical indication, while GC-0018 is skos:broader-linked to GC-0017. SKOS S27 makes associative relatedness disjoint with hierarchical broaderTransitive relationships. No hierarchy cycle was found when broader and inverse narrower edges were combined. \[R7, S3\]

Adjudicate whether the pair is hierarchical or associative, preserving the signed original through the correction overlay. Validate the effective graph for this conflict and for cycles across both broader and inverse narrower paths. The existing broader-only cycle check is narrower than that combined integrity test.

### The strict OWL 2 RL claim needs a conformance decision

The draft README claims an OWL 2 RL boundary. RelevantFactor, Exception and Remedy are defined through equivalent classes involving existential restrictions. The RL grammar does not permit those existential expressions in EquivalentClasses. The schema also uses xsd:date, which is outside the profile’s listed datatype set. A successful RDF parse or application of some RL rules is not a formal profile-conformance check. \[R8, S1\]

Choose and document one supported contract: a formally checked OWL 2 RL subset, or RDF/SKOS plus SHACL and the project’s bounded CONSTRUCT rules. If RL is retained, rewrite the relevant axioms with a profile-aware modeller and add a real profile checker in CI. If the bounded graph contract is chosen, remove the stronger conformance claim while still repairing harmful axioms such as F01.

Do not enable unrestricted reasoning merely to satisfy a label. Separate standards conformance, data validation and legally approved inference. Each answers a different question, and none substitutes for reviewing whether a proposition follows from its source.

## 11  F08  Preserve and require exact evidence

Priority P2  •  Reproduced

### The YAML is richer than the RDF export

All current evidence items for the 112 authored concepts, 164 type assignments and 352 relationships contain spans, hashes and quotes. However, \_origin exports their evidence as sourcePassage links only. This collapses individual evidence locations for concepts and type assignments and does not preserve the full envelope of supporting evidence on corrections. Relationship records separately export their top-level supporting text, span and hash, so the loss is not uniform across record kinds.

Consumers of the YAML can inspect evidence that consumers of the RDF cannot reconstruct. A paragraph-level source pointer is also less precise than the statement-level evidence the review workflow expects. The multiple-source cardinality problem in F01 is a further symptom of representing distinct evidence items with a single direct property.

### The validator permits weaker evidence than the stated contract

The authored-envelope schema requires only ref within an evidence item. In \_evidence\_findings, a missing hash is not compared, a missing span ends validation of that item, and a missing quote is not checked. In an isolated probe, an authentic envelope copied with its evidence reduced to a valid ref passed both envelope validation and the evidence checker without findings.

This is an acceptance gap, not a claim that the current authored records are all missing these fields. A future producer could silently lower provenance quality while keeping the build green.

### Recommended change

- Require ref, span, content\_hash and quote for evidence referring to held text. Enforce sensible offsets and an exact quote match against the pinned source.

- Model non-textual evidence explicitly, such as a case citation where no decision text is held. That exception should have its own evidence kind and limits, not a silent omission of required fields.

- Export one EvidenceSpan node per item and link it to the specific relationship, definition or type assignment it supports. Preserve the source document version and each item’s authority role.

- Add round-trip tests from YAML to RDF to a review payload. Compare item counts, references, spans, hashes, quotes and review provenance.

### Acceptance

The stripped-evidence probe must fail for textual sources. A valid citation-only case must remain representable without implying access to the judgment. A multi-source concept and a type assignment must expose their exact evidence in the graph and review UI. Rebuilding from an unchanged pin must not refresh a stale evidence hash or manufacture a quote.

Evidence: \[R9\] eval/schemas/authored-envelope.schema.json; stage0/harness.py:910–985. \[R2\] build.\_origin and \_provenance. The probe changed only an in-memory copy.

## 12  F09  Separate coverage from currency

Priority P2  •  Reproduced counts and design recommendation

### Whole corpus scope does not mean complete knowledge coverage

| **Coverage measure** | **Observed** | **Meaning** |
| --- | --- | --- |
| Corpus available to search | 500 pages; 2,460 chunks | Text may be retrieved even when it has no curated graph assertions. |
| Manual source nodes in RDF | 208 pages, 41.6%; 1,056 chunks, 42.9% | The graph intentionally selects evidence-related passages and related material. |
| Concepts and types | 164 concepts; all types machine-authored | Connectivity and type coverage do not establish legal review coverage. |
| Case material | 325 decision/citation nodes | Citation metadata is held; judgment text is not. |
| Unresolved citations | 63 of 2,236 citation records | A citation-edge count, not 63 distinct missing authorities. |

Sparse graph selection is a reasonable demonstrator optimisation. It becomes misleading if a whole-Manual label or a zero-result impact query is read as evidence of complete legal coverage. Report four separate measures by Part: source availability, graph representation, substantive assertion coverage and human review coverage. Include unresolved references and known exclusions.

### Reproducibility is not legal currency

The upstream commit and tree hash support a reproducible snapshot. They do not establish that the snapshot matches the current law. The inspected metadata records a July 2026 legislative capture; the current Federal Register displayed compilation C2026C00421 from 19 September 2026 when checked. The review did not perform a provision-by-provision amendment diff and does not assert which reviewed propositions changed. \[R10, S5\]

Record instrument identity, compilation identity, effective dates, retrieval date and source URL separately from ingestion time and assertion review date. Manual parse time should not be presented as its page retrieval time, especially where a batch reuses earlier raw captures.

### Practical release policy

- Keep an immutable reproducibility release and an explicitly maintained current-source release. Do not overwrite the evidence underlying historical review decisions.

- On an upstream change, identify altered source hashes, mark affected assertions for re-review and expose unresolved impact. Do not automatically carry approval across changed text.

- Broaden impact traversal to the intended active assertion view, including definitions and type evidence if the product claims those dependencies. Display its coverage boundary.

Acceptance: a controlled change to one provision identifies all recorded dependent assertions in the chosen view, marks their review need and leaves unrelated evidence intact. A zero result states that no recorded dependency was found within the declared coverage; it does not certify that no legal impact exists.

## 13  F10  Demonstrate a specific benefit

Priority P2  •  Stored results independently recomputed

### Latest measurement does not show an overall search gain

The 12 October reading experiment uses 129 questions: 119 model-written questions and ten signed retrieval questions. It compares the browser configuration without vectors. Recomputing the stored rankings and grades reproduces its report, apart from a trailing newline. No new readings or judgments were generated.

| **System** | **Overall nDCG at 10** | **Interpretation** |
| --- | --- | --- |
| Keyword | 0.702 | Baseline. |
| Ontology using names | 0.661 | Below keyword: difference −0.041, paired 95% interval \[−0.067, −0.014\]. |
| Ontology plus model reading | 0.701 | Improves on names by +0.040 \[0.009, 0.070\], but is not established as better than keyword. |
| Reading minus keyword | −0.001 | 95% interval \[−0.039, 0.036\]. A near-zero estimate is not proof of equivalence. |
| Lookup questions only | −0.066 versus keyword | 95% interval \[−0.127, −0.007\]; a meaningful warning for routine lookup use. |

The ten signed questions show a more favourable reading result, but are too few to support a general claim. Model-generated questions, model grades, one reading per question and three ungraded pooled passages further limit inference. The report itself acknowledges these limitations; retain that candour.

### Make the retrieval use of relationships explicit

search.index.trace walks adjacent edges in either direction. relations\_from carries the predicate and origin, but not modality; expansion then treats neighbours as search terms without a predicate-specific policy. Thus a negative or contrast relationship can expand a question much like a supportive one. This is a plausible contributor to noise, not a demonstrated sole cause of the benchmark losses.

Ablate keyword, keyword-plus-vectors, label expansion, typed relationship expansion and model reading under the same configuration and corpus. Separate contrast discovery from supporting-evidence retrieval; cap or downweight generic hubs. Retain the best baseline as a fallback until an enhancement earns its place.

### Measure the ontology where it may be most useful

Use independently authored examiner tasks to measure time to find the right authority, correct identification of conditions and exceptions, source-trace accuracy and recall of recorded change dependencies. Include negative and near cases. Predefine success criteria and report uncertainty by task type. A vocabulary can be useful for navigation or explanation without improving aggregate ranking; those are claims to test directly.

Evidence: \[R11, R13\]. nDCG rewards ranking relevant passages near the top; these scores do not measure answer correctness or examiner decision quality.

## 14  F11 and F12  Make results auditable

### F11  Freeze evaluation inputs with the result

Priority P2  •  Reproduced. The archived 9 October search report gives keyword 0.725, hybrid 0.844 and ontology 0.803 on overall nDCG@10. Recomputing its stored rankings against the current shared judgments gives 0.702, 0.812 and 0.773. The recorded grade count changes from 2,344 to 2,892. The direction of the ontology-versus-hybrid comparison remains negative, but the published numbers are not reproduced from the present inputs.

The evaluator uses all current grades for each question to calculate the ideal ranking and recall denominator. Later additions to a shared judgments file can therefore change an older experiment even when its rankings have not changed. Using a broader judgment set is defensible for a new comparison; silently applying it to an old result is not reproducibility.

Create immutable experiment bundles containing questions, pooled documents, complete judgments, rankings, corpus and graph hashes, code SHA, prompts, model identifiers, configuration and random seeds. Hash each input in the results manifest. Publish re-scoring as a new experiment that names the old rankings and new judgments. The acceptance test is exact regeneration from a bundle after unrelated judgments have been added elsewhere.

### F12  Reconcile documentation with the current release

Priority P2  •  Static inspection. The root README says the apparatus is built but the content is not, while also describing the end of the section 43 pilot boundary. The draft ontology README still describes that pilot and prohibits definitions under an older authorship policy. The committed ontology report lists 78 authored concepts where the current graph has 112. Its generation template also retains historical status prose.

Regenerating counts alone will not fix hard-coded narratives. Establish one release manifest with scope, source pin, schema version, content counts by origin and review status, current correction counts, coverage and evaluation bundle IDs. Generate status sections from it, and identify historical reports as historical. Add an explicit version IRI or equivalent release identifier and document the namespace publication policy before promising interoperability.

### Adjacent operational issue

The Pages configuration and explorer builder explicitly retain a fallback that publishes a recoverable masked API key if a key is configured without a proxy endpoint. The repository records that this was accepted for the demonstrator. Before broader operation, remove that fallback from production builds and require the proxy path. No live key, repository secret or deployed payload was inspected, so this is a configuration-path finding, not a claim of current credential exposure. \[R4\]

Acceptance for F12: a clean build emits one consistent status manifest; documentation and generated artefacts agree on it; a reader can distinguish frozen demonstrations, current sources, signed history and machine proposals without reading the decision log.

Evidence: \[R12, R14\]. The older vector-enabled search experiment and the latest browser reading experiment are different configurations and must not be presented as one longitudinal score series.

## 15  Delivery plan

The following sequence minimises rework. Effort bands are planning estimates, not commitments: small is roughly one to three engineer-days; medium is roughly four to ten; large requires a coordinated engineering and expert-review cycle. Owner roles can be combined in a small team.

| **Package** | **Work and dependency** | **Owner and effort** | **Exit criterion** |
| --- | --- | --- | --- |
| A  Restore trust boundaries | F01–F04; immediate datatype repair from F07. Fix cardinality, include inferred data, enforce graph placement, centralise currentness, gate publication. | Ontology and validation engineers; medium. | All targeted malformed-data probes fail; current queries exclude corrected assertions; valid graph rebuilds. |
| B  Repair legal meaning | F05–F06. Adjudicate six examples; review all current relations and concept boundaries. Add qualified assertions and definitions. Can begin while A is implemented. | Trade mark expert and modeller; large, expert time dominant. | Review pack records verdict, rationale, scope and evidence for each item; no approval inherited from a neighbouring statement. |
| C  Preserve evidence and standards | F07–F09. EvidenceSpan export, required textual evidence, profile decision, SKOS checks, source-version and coverage reporting. | Ontology and data engineers with corpus owner; medium to large. | Round-trip evidence and integrity tests pass; release declares its semantic contract and coverage. |
| D  Prove and publish the benefit | F10–F12. Freeze evaluation bundles, rerun baselines after B, run independent tasks, regenerate status documents. | Evaluation owner and maintainer; medium plus examiner study time. | Results reproduce exactly; benefit claims match measured task outcomes; release manifest is consistent. |

### A review workflow that fits the existing project

Use the existing review-pack and transcription machinery. Add columns for proposition scope, polarity, modality, evidence sufficiency, concept sense, disposition and replacement ID. Present the whole vocabulary and relationship set coherently, with high-risk examples flagged, so reviewers can see cross-record inconsistencies. Do not turn a structural pass or an unchanged row into implied expert approval.

### Decisions to record explicitly

- Is the supported semantic contract strict OWL 2 RL, or a bounded RDF and SHACL application?

- Which machine-authored propositions may appear in each user-facing view, and how are qualifications preserved?

- What does “current” mean for a source, a reviewed assertion and a published release?

- Which measured task benefit justifies using ontology expansion instead of the strongest baseline?

A new triple-store platform, a wholesale ontology rewrite or a full legal-rule language is not required to address the identified defects. The current codebase can support the proposed repairs if the same assertion and provenance policies are used end to end.

## 16  Acceptance checklist

These checks are intended to become executable release criteria. They supplement the existing suite by testing the exact failure modes found during review.

| **Area** | **Positive case** | **Negative or boundary case** |
| --- | --- | --- |
| Evidence identity | One assertion has several independent evidence spans. | Mixed Manual and statutory evidence never creates source identity. |
| Inference validation | A rule result has its derivation, status and producing rule. | An inferred node without those fields fails through the production CLI. |
| Graph placement | A signed concept receives a separately labelled authored type. | An authored assertion placed in the approved graph is rejected. |
| Currentness | A replacement is returned with its own review status. | A corrected signed assertion is absent from every current-answer view. |
| Legal scope | A qualified record retains the decisive condition. | Changing the condition does not yield an unconditional rule or unsupported positive sequence. |
| Evidence completeness | Exact text, offsets and hash match the pinned source. | A ref-only textual evidence item fails; citation-only cases declare their limits. |
| Datatype integrity | Confidence and prose use the declared datatypes. | Double-versus-decimal and language-tag-versus-string mismatches fail. |
| SKOS integrity | Hierarchy and association have distinct purposes. | Related/broaderTransitive conflict and mixed-direction hierarchy cycles fail. |
| Source change | A changed provision marks all recorded dependants for review. | Approval is not silently copied to changed evidence; no recorded impact is not no legal impact. |
| Evaluation | A frozen bundle recreates metrics and intervals. | Adding unrelated judgments cannot change a published experiment. |
| Deployment | A validated SHA and manifest are published together. | A defect, missing required snapshot or failed gate blocks publication. |

### Recommended release judgement

Continue demonstrating the map and review workflow with explicit status labels. Complete Package A before inviting users to trust graph outputs as current assertions. Complete expert adjudication of the identified legal errors and verify qualified serving before an examiner pilot. Make any wider search-benefit claim contingent on Package D results, rather than graph size, connectivity or the number of automated checks.

## 17  Reproduction and limitations

### Commands and observed outcomes

Commands were run in a local Python 3.12 virtual environment after checking out the exact reviewed commit and installing the repository’s test and RDF extras. RDFLib 7.6.0, pySHACL 0.40.1 and owlrl 7.6.2 were present. The pinned upstream snapshot was fetched using the repository command.

| **Command or check** | **Outcome** |
| --- | --- |
| pytest -q -m "not snapshot" | 511 passed; 24 skipped; 170 deselected. This partition began before the corpus fetch completed. |
| pytest -q -m snapshot | 170 passed; 535 deselected. One RDFLib deprecation warning. |
| pytest -q -rs tests/unit/test\_explorer.py -m "not snapshot" | 15 passed when rerun after the snapshot was available. This overlaps the earlier partition; it is not an additional unique-test total. |
| tmk-harness --allow-incomplete | 0 defects, 12 gaps, 14 notes. Completeness gaps are explicitly allowed by this invocation. |
| tmk-graph --rules --check | Committed dataset matches the rebuild; 5 candidate-rule and 187 approved-rule assertion results. |
| tmk-shacl --rules | 0 defects, 0 gaps, 259 notes. This clean result is subject to the production validation omissions in F02. |
| tmk-bulk measure --reading --allow-ungraded 3 | Latest stored reading report reproduced, apart from a trailing newline. |
| tmk-bulk measure | Re-scoring older rankings with current grades differs from the archived report, as described in F11. |
| Independent graph and mutation checks | F01 source equality reproduced; F02 malformed graph probes passed unexpectedly; F08 ref-only evidence passed; one SKOS conflict found. |

### How to repeat the independent probes

For F01, load the draft schema, GC-0054’s triples and its source targets’ types and authority kinds into a small graph; apply OWLRL\_Semantics closure and inspect source owl:sameAs links and disjointness errors. For F02, create an otherwise empty Dataset with one InferredAssertion in the inferred graph and call validate.run; move it to the default graph for the control. For the placement probe, supply a complete authored envelope in the approved graph. For F08, copy an authored concept envelope, retain only a valid evidence ref, and run validate\_envelope plus \_evidence\_findings.

The remaining initial skips were not claimed as passing. No live API-answer benchmark, browser usability study, full OWL profile checker, exhaustive legal audit or provision-by-provision currency diff was performed. Passing the existing tests demonstrates implementation stability; the independent negative probes show why it does not establish the missing safeguards.

## 18  Repository evidence

All links in this section are pinned to the reviewed commit. File and function names in the findings identify the relevant implementation; record IDs identify the data rows. Historical reports are cited as historical evidence, not as current inventories.

**R1  Purpose, governance and development state**

[CLAUDE.md](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/CLAUDE.md)

[Current handoff](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/docs/HANDOFF.md)

[Earlier ontology review](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/docs/ONTOLOGY-REVIEW.md)

**R2  Provenance declarations and graph construction**

[Provenance module, including sourcePassage and confidence](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/provenance.ttl#L74)

[Graph builder, \_origin and \_provenance](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/ontology/build.py#L684)

**R3  Production validation and inference shapes**

[Dataset flattening and validation](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/ontology/validate.py#L121)

[Inference shapes](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/shapes/inference.ttl)

[Shape regression tests](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/tests/unit/test_shapes_fire.py)

**R4  Publishing and live-answer configuration**

[Pages workflow](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/.github/workflows/pages.yml)

[Harness workflow](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/.github/workflows/harness.yml)

[Explorer data builder](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/explorer/build.py)

**R5  Corrections, competency queries and change impact**

[Correction overlay implementation](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/authored/corrections.py)

[CQ-0009](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/queries/competency/CQ-0009.rq)

[CQ-0011](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/queries/competency/CQ-0011.rq)

[CQ-0021](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/queries/competency/CQ-0021.rq)

[CQ-0024](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/queries/competency/CQ-0024.rq)

[Change-impact rule](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/queries/rules/RULE-0002-change-impact.rq)

**R6  Current authored relationship evidence**

[Relationships including the six reviewed records](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/authored/relationships.yaml)

[Structure review ledger](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/data/derived/audit/restructure.yaml)

**R7  Concepts and type assignments**

[Signed concepts](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/eval/gold/concepts.yaml)

[Authored concepts](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/authored/concepts.yaml)

[Authored type assignments](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/authored/concept-types.yaml)

**R8  Ontology semantics and stated profile**

[Legal concept axioms](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/legal-concepts.ttl)

[Draft ontology contract](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/README.md)

[Evaluation datatype declarations](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/evaluation.ttl)

## 19  Further evidence and standards

**R9  Evidence requirements and checking**

[Authored envelope schema](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/eval/schemas/authored-envelope.schema.json)

[Evidence checker](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/stage0/harness.py#L910)

**R10  Corpus, versions and coverage**

[Pinned corpus manifest](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/data/pin.json)

[Source and graph builder](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/ontology/build.py)

[Time and currency module](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/time.ttl)

**R11  Latest stored reading measurement**

[Reading measurement report](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/data/derived/reports/measure-reading.md)

[Reading rankings and pools](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/data/derived/bench/reading-pools.yaml)

**R12  Older measurement and current shared grades**

[Archived search measurement](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/data/derived/reports/measure.md)

[Shared judgments](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/data/derived/bench/judgements.yaml)

[Metric implementation](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/search/measure.py)

**R13  Search integration**

[Trace, expansion and relationship extraction](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/search/index.py#L166)

**R14  Documentation and report generation**

[Root README](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/README.md)

[Committed ontology report](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/data/derived/reports/ontology.md)

[Ontology report generator](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/ontology/report.py)

### Primary technical standards

**S1  W3C OWL 2 Profiles**

[OWL 2 RL grammar, datatypes and rule semantics](https://www.w3.org/TR/owl2-profiles/)

**S2  W3C RDF 1.1 Concepts**

[Literal datatypes and language-tagged strings](https://www.w3.org/TR/rdf11-concepts/)

**S3  W3C SKOS Reference**

[Hierarchical and associative integrity, including S27](https://www.w3.org/TR/skos-reference/)

**S4  W3C SHACL**

[Validation over an explicitly supplied data graph](https://www.w3.org/TR/shacl/)

Standards explain the consequences of the declared model. The repository-specific counts, counterexamples and recommendations are independent review findings.

## 20  Official legal source checks

Official sources were checked during this review for the selected relationship examples and the legislation-version observation. The legal conclusions in the findings are deliberately limited to whether the recorded edge faithfully expresses its cited passage. They do not replace expert approval of a repaired proposition.

**S5  Trade Marks Act 1995**

[Federal Register entry and compilation history](https://www.legislation.gov.au/C2004A04969/latest)

[Compilation from 19 September 2026, including section 180A](https://www.legislation.gov.au/C2004A04969/2026-09-19/2026-09-19/text/original/epub/OEBPS/document_1/document_1.html)

**S6  Manual 35.10 Assignment of unregistered certification trade marks**

[Referral stage and Commission consent](https://manuals.ipaustralia.gov.au/trademark/10.-assignment-of-unregistered-certification-trade-marks)

**S7  Manual 62.8 Protected international trade marks**

[Amendment or cessation of protection by the Registrar](https://manuals.ipaustralia.gov.au/trademark/8.-amendment-or-cessation-of-protection-by-registrar-of-protected-international-trade-marks-pitms)

**S8  Manual 24.3 Effect of a disclaimer on registration**

[Transition of disclaimer particulars](https://manuals.ipaustralia.gov.au/trademark/3.-effect-of-a-disclaimer-on-registration)

**S9  Manual 29.8 Internet domain names**

[Registrant and authorised-user context](https://manuals.ipaustralia.gov.au/trademark/8.-internet-domain-names)

**S10  Manual 29.7 Phonewords and phone numbers**

[Ownership or authorised use and reconsideration](https://manuals.ipaustralia.gov.au/trademark/7.phonewords-and-phone-numbers)

**S11  Manual 28.5 Conditions and limitations**

[Applications proceeding under subsection 44(3)](https://manuals.ipaustralia.gov.au/trademark/5.-conditions-and-limitations-to-applications-proceeding-under-subsection-443)

### Boundary of the recommendation

The recommended next step is a repair and validation cycle around the existing demonstrator: enforce its provenance boundaries, retain the full meaning of its assertions, and measure its practical contribution. The findings do not establish that every authored record is wrong, nor that ontology-based assistance has no value. They identify specific reasons the current implementation cannot yet support stronger claims, and provide concrete ways to resolve them.

# Trade Mark Ontology Review — Structural Addendum

TM Knowledge  |  Process, applicability and the representation of legal reasoning

15 October 2026  •  Repository snapshot 6a75eefadd98  •  Findings F13–F19

### Executive judgement

The further review supports the concern about temporality and identifies a broader architectural issue: the ontology needs to express **the circumstances in which a relationship holds**, as well as the concepts it connects. Procedural stage is one such circumstance. Other consequential qualifications include the applicable legal route, the actor and capacity involved, the goods or services affected, the logical structure of a test, and the distinction between a possible evidentiary contribution and an established conclusion.

The repository already contains relevant foundations. It defines procedural concepts and several process predicates, distinguishes legal propositions from extraction records, records modality and provenance, and deliberately limits automated reasoning. The gap is therefore one of incomplete and sometimes inconsistent representation, rather than a complete absence of these ideas.

These omissions have different implications. Qualifications needed to preserve the meaning of relationships already published require attention now. A complete case history, operational deadline calculator or evidence assessment system would be a substantial scope extension and is not required to make the current demonstrator useful.

One additional semantic defect is directly reproducible: the ontology identifies something that does not establish a ground **by itself** as an `Exception`. Insufficiency and exception are different meanings. Further source comparisons also show why generic `establishes` relationships require review before they are presented as statements about evidentiary sufficiency.

| **Dimension** | **Assessment** |
| --- | --- |
| Procedural representation | Partial vocabulary and isolated relationships exist; they do not constitute a coherent step-wise process model. |
| Applicability of propositions | Decisive conditions often remain in source text or reviewer notes rather than structured proposition content. |
| Logical and normative meaning | Necessary conditions, exceptions, permission, possibility and discretion need clearer separation. |
| Identity and scope | Concept definitions must distinguish documents, acts, states, parties and the particular subject matter affected. |
| Evidence and contested knowledge | Provenance is a strength; case evidence, competing interpretations and coverage limits require separate treatment. |
| Development direction | Add a modest layer of qualified propositions and generic process structure; retain human judgement and the existing governance boundaries. |

### First actions

- Extend the original F05 repair work to preserve procedural stage, applicability conditions, polarity and normative meaning throughout authoring, review, export and serving.
- Correct the `Exception` equivalence and review all relationships whose meaning depends on “by itself”, alternatives, conditions or exceptions.
- Define a small generic process model that separates states, activities, events, prerequisites and clock effects.
- Review the three authored `establishes` relationships and reconcile their use with the evidence module’s stated boundaries.
- Add paired acceptance scenarios showing that a change in stage, scope or available knowledge changes the response appropriately.

This addendum supplements the initial review without replacing its findings or release gates. It follows the same organisation: scope and evidence, existing strengths, prioritised findings, detailed recommendations, delivery plan, acceptance criteria and sources. Finding numbers continue from F12.

## 1  Scope and evidence

The additional review examines the temporal and structural concerns raised after the initial report: whether the ontology describes examination as a process, and whether other fundamental gaps limit reliable legal guidance.

| **Baseline** | **Reviewed value** |
| --- | --- |
| Repository | Thomas-Amann-IPAustralia/TM-Knowledge |
| Exact commit | 6a75eefadd982c29190b1f92f451de5168a29508 |
| Relationship to initial review | Same repository snapshot; additional analysis, not a review of a subsequent release. |
| Additional inspection | Process and time modules, proposition and evidence classes, predicate definitions, relationship schema, selected authored records and reasoning boundaries. |
| Additional execution | Predicate counts, schema-field inspection and an isolated OWL inference probe with a negative control. |
| Source checking | Existing relationship evidence and a targeted recheck of the official Manual’s certification-mark assignment guidance. |
| Change boundary | No ontology, repository record or application behaviour was changed. No new model-based extraction or evaluation was commissioned. |

### What was verified

The authored relationship file contains four `precedes`, five `prevents`, three `isCommencedBy`, two `becomes`, three `resultsIn` and one `isAssessedIn` relationships. These counts describe that file, not every temporal statement in the corpus or a measure of process completeness. The dictionary also includes date-related predicates such as `runsFrom`, `isFixedBy` and `keepsEarlierDate`.

The relationship schema was checked for its available fields and modality values. The declared `Exception` equivalence was tested using a minimal synthetic graph. The three authored `establishes` records were compared with their stored supporting passages.

### Evidence labels used in the findings

| **Label** | **Meaning** |
| --- | --- |
| Reproduced | Confirmed through counts, schema inspection or the controlled inference probe described in section 13. |
| Source comparison | A recorded relationship compared with its supporting passage; a proposed replacement still requires expert adjudication. |
| Static inspection | Confirmed in the reviewed schema, definitions, data or documentation. |
| Design recommendation | Proposed capability or modelling approach; not an assertion that a live system has already produced an incorrect answer. |

The earlier report’s test results remain evidence about the original audit. This addendum does not claim that the entire suite was rerun. It does not establish that every omitted capability belongs within the current product scope.

## 2  What exists and what works

| **Existing foundation** | **What it provides** | **Remaining limitation** |
| --- | --- | --- |
| `ProcessElement` and `ProceduralStep` | Vocabulary for process participants and steps, including events that change state. | No consistent representation of the states, triggering conditions and resulting states of each transition. |
| Process and date predicates | Selected ordering, commencement, prevention, transformation and date relationships. | Different temporal effects are sometimes combined; isolated edges do not define a complete procedure. |
| `time.ttl` | Authority status, capture dates, amendment metadata and source staleness. | These concern source currency; they do not provide an application’s procedural history or applicable-law history. |
| `LegalProposition` and `Assertion` | An explicit distinction between what a source says and the project’s record of extracting or reviewing it. | The active record format does not give applicability and compound conditions corresponding structured treatment. |
| Modality and predicate dictionary | `must`, `may`, `should` and explicit predicate readings. | Lexical modality alone cannot distinguish permission, possibility, obligation or discretion. |
| Roles and `Principle` | Role vocabulary and concepts concerning matters such as onus, discretion and office practice. | Their existence does not supply a complete contextual model of responsibility or legal reasoning. |
| Evidence and examination scaffolding | Declared classes and explicit restrictions on automated evaluative conclusions. | These remain largely future capabilities; documentation about unused evidence predicates no longer matches all authored data. |

### Strengths to retain

Preserve source-level provenance, correction history, review status, the separation of law and practice, and the limits on automated examination outcomes. These make the proposed additions reviewable.

The initial report was right to describe unpopulated case classes as intentional scaffolding. That judgement remains valid. A generic description of when a procedural rule applies can be modelled without importing individual applications or calculating their outcomes. The two development decisions should be recorded separately.

Evidence: [A1–A5, A8].

## 3  Prioritised findings

P1 retains the original meaning: resolve before a trusted pilot or downstream use of graph assertions. P2 identifies the next development cycle before broader capability claims. Where a finding includes a possible future case system, that work is explicitly conditional on an agreed expansion of scope.

| **ID** | **Priority and finding** | **Primary owner** | **Completion evidence** |
| --- | --- | --- | --- |
| F13 | P1 for stage-sensitive assertions; P2 for a coherent generic process model. Process context is insufficiently represented. | Trade mark expert and process modeller | Stage-qualified propositions and reviewed transition scenarios; distinct order, prerequisite and clock semantics. |
| F14 | P1 for conditional assertions already served. Applicability needs structured representation. | Ontology and data engineers with expert reviewer | Conditions survive authoring, review, RDF export, queries and answer presentation. |
| F15 | P1 for the `Exception` defect and misleading logical readings; P2 for richer compound expressions. | Ontology engineer and expert | Insufficiency is not inferred to be an exception; necessity, sufficiency and alternatives remain distinct. |
| F16 | P1 where normative assertions support guidance; P2 for the broader vocabulary. Normative force and responsibility need qualification. | Trade mark expert and vocabulary editor | Permission, possibility, obligation and discretion can be distinguished without guessing from wording. |
| F17 | P2, with affected current records repaired under F05/F14. Identity, role and subject-matter boundaries need definition. | Vocabulary editor and modeller | Reviewed concept boundaries and tests against whole-application or whole-mark overgeneralisation. |
| F18 | P1 for the existing `establishes` records; P2 for generic evidence guidance. Case-specific assessment remains a separate scope decision. | Evidence specialist and ontology engineer | Reviewed evidence relationships; source provenance and filed evidence remain distinct; no unsupported evaluative conclusion. |
| F19 | P1 for honest limits on current answers; P2 for structured competing interpretations. Knowledge state and legal disagreement need separate treatment. | Product, query and review owners | Missing knowledge cannot become a negative legal conclusion; disputed propositions retain their support and status. |

F13–F16 develop the underlying representation problem identified in F05. F17 extends F06. F18 complements F08 but concerns evidence used in a matter, rather than just evidence supporting an extraction. F19 extends the coverage concerns in F09. None displaces the original validation, currentness or publication findings.

## 4  F13  Represent process and temporal applicability

**Priority:** P1 for affected current propositions; P2 for generic process coverage.  
**Evidence:** Static inspection and reproduced counts [A1–A4].

### Finding and consequence

A step-wise process is represented only partially. The ontology has procedural concepts and relationships, including examination preceding acceptance and proceedings being commenced by documents. It lacks a coherent representation of how a matter enters a state, what enables a transition, what changes, and which conditions continue to hold afterwards.

Two dictionary definitions expose a more immediate ambiguity. `precedes` combines chronological ordering with a prerequisite: its reading says the later step cannot happen until the earlier step has happened. `prevents` covers both blocking a step and stopping its time from running. Those meanings require different checks and can produce different practical advice.

Four forms of time should be distinguished:

| **Temporal dimension** | **Question it answers** |
| --- | --- |
| Procedural order and state | Has the relevant step occurred, and which procedural conditions currently apply? |
| Deadlines and intervals | What starts, suspends, resumes or ends a specified period? |
| Legal applicability over time | Which version of a rule governs the relevant event or circumstances? |
| Knowledge and source history | When was a source captured, changed, reviewed or superseded? |

The existing time module primarily addresses the last dimension. A source capture date cannot answer the other three.

The certification-mark assignment example in F05 illustrates why this matters. The Manual differentiates the position before documentation is sent to the Commission from recordal after it is sent but before registration. A general consent relationship loses the procedural condition that determines its application. Section 16 identifies the official source and the limited conclusion drawn from it.

### Recommended change

Introduce a small generic process model with **activity**, **event**, **state**, **transition**, **trigger**, **precondition** and **effect**. Define these terms and map existing procedural concepts to them before adding more sequence edges.

Distinguish temporal order from legal prerequisite; distinguish an unavailable action from a suspended clock. Record the applicable route, actor and source of each transition. Permit branches, repetition and concurrent matters instead of imposing one linear sequence on every application.

Start with the transitions needed to explain existing relationships. Add a deadline-rule structure only where supported guidance requires it; operational date calculation needs a separately reviewed calendar and computation policy. Historic applicable-law questions likewise require source-version data that the current snapshot does not provide.

### Acceptance checks

- A stage-sensitive proposition identifies its stage and source; changing that stage changes its applicability or produces an explicit unknown.
- A chronological order does not become a legal prerequisite unless separately supported.
- A blocked action does not automatically suspend a deadline, and a suspended deadline does not automatically block every action.
- A process description supports a branch and a repeated examination activity without corrupting an earlier event.
- No output presents the small initial process model as an exhaustive map of examination.

## 5  F14  Make applicability part of the proposition

**Priority:** P1 for conditional assertions already served.  
**Evidence:** Static inspection and earlier source comparisons [A1–A5]; design recommendation [S1].

### Finding and consequence

The relationship schema records subject, predicate and object alongside evidence, tier, modality and approval metadata. It provides no dedicated representation of compound applicability conditions, scoped negation or alternatives. Supporting text and notes can preserve these in prose, but a consumer following the edge alone cannot reliably recover them.

The ontology already declares `LegalProposition` and distinguishes it from an extraction `Assertion`. The improvement is to carry that distinction through the working representation. Adding more provenance to a broad edge does not itself narrow the edge’s meaning.

For example, a statement applying to a particular type of mark, at a particular stage, in respect of specified goods or services cannot safely become an unqualified relation between two general concepts. This is the common architectural issue behind several F05 examples.

### Recommended change

Give a qualified proposition its own identity and attach its substantive conditions to it. Link the extraction and review record to that proposition, preserving the existing source envelope. Extend and version the current schemas and export contract; do not overload free-text notes as the only machine-readable source of applicability.

| **Proposed component** | **Purpose** |
| --- | --- |
| Core statement | The relationship being asserted, including its direction and polarity. |
| Applicability | Relevant mark or application type, legal route, procedural state, territory and subject matter. |
| Condition expression | Required conditions, alternatives, exceptions and any limits on what the expression claims. |
| Participants and capacities | Who acts, who is affected, and in which role. |
| Temporal scope | Relevant event or period, kept separate from source capture and review dates. |
| Normative meaning | Obligation, permission, power, discretion or another reviewed interpretation. |
| Authority and review | Supporting passages, source versions, attribution and independent review status. |

Not every proposition needs every component. Each potentially decisive component must have a defined treatment: supplied, reviewed as inapplicable, or unresolved. Missing scope must never silently mean universal scope.

A relation node is a recognised RDF modelling option for a relationship with additional participants or qualifications. W3C’s n-ary relations note describes the pattern and its trade-offs; it does not prescribe this particular legal schema. [S1]

### Acceptance checks

- Conditions survive a complete round trip from source record to RDF and back to a displayed answer.
- Two propositions with the same subject, predicate and object but different conditions remain distinguishable.
- A convenience edge used for navigation cannot be presented as the complete legal proposition.
- Unsupported or unresolved scope prevents a definitive applicability claim.
- Approval of an original extraction is not inherited automatically by newly authored qualifications.

## 6  F15  Separate necessity, sufficiency and exception

**Priority:** P1 for the demonstrated semantic defect; P2 for a fuller expression model.  
**Evidence:** Reproduced inference, static inspection and source comparison [A1–A4].

### Finding and consequence

`doesNotGiveRiseTo` is defined as saying that its subject does not establish its object by itself; its guidance explicitly allows the subject still to contribute. However, `Exception` is declared equivalent to a restriction on that property and is described as a case a ground or test does not reach.

An isolated reasoning probe confirmed that an otherwise unclassified subject with a `doesNotGiveRiseTo` relationship to a `LegalConcept` acquires the type `Exception`. A control using `qualifies` did not. This demonstrates the declared classification consequence; it does not establish that the production answering path currently executes this inference.

The distinction matters in an actual record. GR-0688 concerns an image of a person and a section 43 ground. Its supporting passage cautions against raising the ground merely because the image is present. That does not create a general exemption for trade marks containing such images.

Related distinctions also need explicit treatment. A `requiresElement` edge expresses necessity, not that the element is sufficient, that every required element has been listed, or that several edges form an exhaustive conjunction. Separate edges cannot by themselves distinguish “A and B” from “A or B”.

### Recommended change

Remove or replace the equivalence that turns insufficiency into `Exception`, subject to the project’s expert review process. Keep a predicate for “insufficient by itself” if useful; define genuine exceptions independently with their scope and the proposition they qualify.

Add only the logical structures demanded by reviewed sources: conjunction, alternatives, necessary conditions, supported sufficient conditions, scoped negation and explicit exceptions. Mark whether a listed set of conditions is complete. Preserve generalisations such as “usually” as qualified claims; they must not become categorical exclusions.

Review the other edge-defined classes for the same pattern of unintended strengthening. This is a targeted semantic review, not a recommendation to implement a general automated legal reasoner.

### Acceptance checks

- “A alone is insufficient for B” does not classify A as an exception to B or imply that B is impossible when A is present.
- A necessary condition cannot be used as a sufficient condition.
- An alternative can be met by the relevant branch without requiring every branch.
- A conjunction with an unknown component remains unresolved.
- A genuine exception identifies its target proposition and applicable circumstances.
- An incomplete condition list cannot support a claim that every legal requirement has been satisfied.

## 7  F16  Distinguish normative force and responsibility

**Priority:** P1 for normative guidance already served; P2 for vocabulary expansion.  
**Evidence:** Static inspection [A2, A3, A5, A6].

### Finding and consequence

The schema permits `must`, `may`, `should` and null. Its own description correctly warns that the meaning of “may” requires legal interpretation. This is an existing safeguard worth retaining, but the stored values do not resolve the ambiguity they identify.

An obligation, a permission, the conferral of a power, an exercise of discretion, a recommendation and a statement of possibility have different consequences. Likewise, a condition necessary for a legal test is not automatically a duty imposed on a person. The actor and action must be identified before the system can explain who is required or permitted to do what.

Role and `Principle` concepts already cover parts of this territory. The gap is the consistent attachment of reviewed normative meaning and responsibility to the proposition being served.

### Recommended change

Retain the existing modality values and source wording for traceability. Add a separately reviewed interpretation where needed, with a responsible actor or role, action, beneficiary or affected party where relevant, and applicability conditions.

Allow unresolved interpretation. Do not translate every occurrence of “may” into permission or every “must” into an obligation. Distinguish the source’s legal or practice status from its wording; a forceful sentence in practice guidance does not, by its wording alone, become a statutory obligation.

### Acceptance checks

- A possibility statement cannot be returned as permission to act.
- A discretion cannot become a mandatory outcome merely because its preconditions are met.
- A necessary element of a test cannot become a duty on an unspecified party.
- A normative response identifies the actor, action, source and material conditions, or states what remains unresolved.

## 8  F17  Clarify identity, roles and the scope of effects

**Priority:** P2; repair affected current records under F05/F14.  
**Evidence:** Static inspection and the original concept-boundary findings [A1, A4, A6, A7].

### Finding and consequence

The initial review identified undefined concepts and ambiguity between documents and processes. The wider issue is whether a relationship applies to a vocabulary concept, a real-world participant, a document, an activity, a state or a particular portion of the subject matter.

The distinction between a role concept and a role class already exists through `roleConcept`; it should be retained. A future case model would additionally need to express who occupies a role, for which matter and during which period. That is different from improving the current vocabulary’s definitions.

Scope also determines the reach of a conclusion. An issue concerning one component of a mark or a subset of goods or services must not silently become a conclusion about the whole mark or application. The model should be able to express a limited effect whenever a reviewed source supports one.

### Recommended change

| **Distinction to define** | **Practical treatment** |
| --- | --- |
| Application request, application document and filing act | Separate senses where their properties differ; link them explicitly. |
| Acceptance act and accepted state | Represent the act or event separately from the state it produces. |
| Role and role holder | Keep vocabulary roles; introduce contextual role assignments only if case instances enter scope. |
| Mark and mark component | Identify which sign or component a proposition concerns. |
| Specification and relevant goods or services | Attach the affected subset to a proposition or effect where needed. |
| Concept and instance | Do not treat a vocabulary node as an actual submission, person or application merely because it participates in a broad predicate. |

Prioritise distinctions implicated by current records. Publish definitions, scope notes and examples in the review pack. Do not create numerous classes solely because a theoretical distinction is possible.

### Acceptance checks

- A filing document is not inferred to be the proceeding it initiates.
- An event and the resulting state have separate meanings and identifiers where represented.
- A limited subject-matter effect does not expand to the entire application without supporting authority.
- If case data is later introduced, one participant can occupy different roles in different matters without identity or classification conflicts.

## 9  F18  Separate source provenance from evidence in a matter

**Priority:** P1 for current `establishes` records; P2 for generic evidence guidance. Case-specific assessment requires an explicit scope decision.  
**Evidence:** Static inspection, reproduced counts and source comparison [A2, A4, A5, A8].

### Finding and consequence

There are two distinct evidentiary questions: **what supports the ontology’s statement?** and **what material supports a fact or legal contention in an application?** The project’s source provenance addresses the first. It does not itself represent the second.

The evidence module deliberately declares unpopulated classes, including `EvidenceSubmission` and `EvidentiaryProposition`, and excludes automated evaluative conclusions. Those are legitimate boundaries. However, the module describes `establishes` as unused while three authored relationships use it:

| **Record** | **Recorded relationship** | **Concern from its supporting passage** |
| --- | --- | --- |
| GR-0163 | Evidence of use establishes honest concurrent use. | The passage identifies honesty as an issue to consider. It does not establish that the generic evidence category satisfies the conclusion. |
| GR-0206 | Evidence of use establishes capability to distinguish. | The passage describes a particular situation involving use in particular colours; the edge omits that context. |
| GR-0248 | Evidence of use establishes use of a trade mark. | The stored supporting text is an instructional heading. It does not establish an evaluative conclusion about any submitted material. |

These are conceptual relationships, not findings about real applications. Nevertheless, the unqualified predicate risks suggesting sufficiency that its evidence does not support. The immediate issue is the meaning of existing records, not the absence of a full case-evidence system.

### Recommended change

Adjudicate the three records and reconcile the evidence module, dictionary and reasoning policy. For generic guidance, represent what a type of evidence may be relevant to proving and under which circumstances, without treating every item in that category as proof.

If case assistance is later authorised, distinguish the submitted material, the fact claimed, the party making the claim, the assessment of support, the legal element addressed and the human decision or reasons. Record contrary material and the limits of the assessment. An evidence item’s existence must not automatically establish a fact or satisfy a legal test.

### Acceptance checks

- A source passage supporting an extraction is distinguishable from an applicant’s evidence submission.
- An evidence category does not automatically establish a factual or legal conclusion.
- A relationship supported only by an instructional heading cannot pass review as an assertion of sufficiency.
- Generic evidence guidance can be returned without stating an examination outcome.
- Any future recorded human assessment identifies its assessor, materials, scope and reasoning; it is not represented as an automatic inference.

## 10  F19  Represent knowledge limits and competing interpretations

**Priority:** P1 for current answer limits; P2 for a fuller model of disagreement.  
**Evidence:** Static inspection and design recommendation [A5, A8, A9; S2].

### Finding and consequence

Review status, extraction confidence, source availability, legal applicability and substantive disagreement answer different questions. The repository already distinguishes some of them. A complete serving policy should prevent any one from standing in for the others.

An approved extraction is not proof that a proposition applies to every matter. A missing relationship is not evidence that a requirement or exception does not exist. A low extraction score is not the same as a disputed legal interpretation. Two differently scoped propositions need not be contradictory.

This matters especially when a partial graph supports answers to questions such as “Are there any exceptions?” or “Is anything else required?” OWL’s open-world semantics do not make an absent fact false. A closed set used for a particular validation task must be explicitly justified and must not become an assumed complete statement of the law. [S2]

The current authority and role vocabulary provides useful distinctions. A generic source hierarchy or the existing role-oriented `prevailsOver` relation would not, by itself, resolve every apparent conflict between legal propositions.

### Recommended change

Track independent dimensions rather than creating one overloaded certainty field: review state, source availability and currency, coverage, applicability, and any recorded legal dispute. Permit “not assessed”, “unknown” and “not applicable” where they have distinct meanings.

Preserve competing propositions with their sources, scope, reasons and review history. First check whether different dates, routes or facts explain the apparent conflict. Where a conflict remains, expose it for expert resolution; do not choose a winner automatically from document type or extraction confidence.

Define an answer policy for completeness-sensitive questions. Unless a reviewed, bounded set is known to be complete, describe what is recorded and identify the limit. This is a preventive recommendation; the addendum does not claim to have reproduced a deployed false-negative answer.

### Acceptance checks

- An empty result is not rendered as “there is no requirement” or “there are no exceptions”.
- An unknown applicability condition does not become false, true or irrelevant by default.
- High extraction confidence cannot resolve substantive legal disagreement.
- Conflicting assertions remain separately inspectable, including qualifications and supporting authority.
- A completeness claim names the bounded domain, review basis and source version to which it applies.

## 11  Delivery plan

Integrate this work into the original packages rather than creating a separate ontology rewrite. Owner roles may be combined. Effort bands retain the original planning meaning: small is approximately one to three engineer-days; medium is four to ten; large requires a coordinated engineering and expert-review cycle. They exclude any commitment to model every trade mark procedure.

| **Package** | **Additional work and dependency** | **Owner and effort** | **Exit criterion** |
| --- | --- | --- | --- |
| A  Restore trust boundaries | Retain F01–F04 and the original datatype repairs. Add the F15 inference regression and explicit limits on completeness-sensitive answers. | Ontology, validation and query owners; small to medium incremental work. | Known semantic and serving failures are blocked through the supported production path. |
| B  Repair legal meaning | Extend F05–F06 with F13–F18. Review stage, scope, logical structure and normative meaning; adjudicate the three evidence relationships. | Trade mark expert, modeller and data engineer; large. | Qualified propositions retain the source meaning and have their own review disposition. |
| C  Preserve evidence and standards | Version schemas and exports; separate provenance, process time and legal applicability; document unresolved context and vocabulary boundaries. | Ontology and data engineers with corpus owner; medium to large. | Qualification and provenance round-trip; documentation matches implemented capability. |
| D  Prove and publish the benefit | Extend F10–F12 with paired scenarios and expert tasks for applicability, procedure and uncertainty. | Evaluation owner and maintainer; medium plus expert time. | Evaluation measures the claimed improvement and captures unsafe overgeneralisation. |

### A review workflow that fits the existing project

Extend the existing review pack with procedural state, route, subject-matter scope, actor, condition structure, polarity, normative interpretation and completeness status. Keep “unresolved” available. Present the original passage beside each proposed qualification and record its reviewer and rationale.

Start with the original six F05 examples, the `Exception` definition and the three `establishes` records. Then review other records using the same high-risk predicates. This supplies an initial migration set without treating those examples as exhaustive coverage.

### Decisions to record explicitly

- Is the next release a concept navigation tool, a source-grounded explanation tool, or a provider of case-specific guidance?
- Which generic procedures and applicability questions are in scope, and which remain explicitly uncovered?
- Which inferences are licensed, and which qualified structures are retained only for retrieval and human explanation?
- What evidence is required before a list of conditions or exceptions can be described as complete?

A case history store, deadline engine and case-evidence assessment layer should be separate work packages if the intended use expands. The current repairs do not depend on building them.

## 12  Acceptance checklist

These checks extend the original release checklist. Use expert-reviewed fixtures for actual legal propositions and clearly labelled synthetic fixtures for logical behaviour. Pair near-identical scenarios so that changing one condition reveals whether it has been preserved.

| **Area** | **Positive case** | **Negative or boundary case** |
| --- | --- | --- |
| Procedural stage | A reviewed proposition is returned for its stated stage. | A different or unknown stage does not receive the same unconditional answer. |
| Process semantics | Order, prerequisite, blocked action and clock suspension retain distinct meanings. | One is not inferred solely from another. |
| Qualification | Conditions remain attached throughout export, retrieval and display. | Flattening a qualified proposition cannot create an unconditional legal rule. |
| Logic | Reviewed alternatives and conjunctions are represented faithfully. | Necessary, sufficient and insufficient-by-itself statements are not interchanged. |
| Exception | A genuine exception identifies the proposition it qualifies. | `doesNotGiveRiseTo` alone does not classify its subject as an exception. |
| Normative force | The response identifies the reviewed meaning, actor and action. | Possibility is not permission; discretion is not a mandatory outcome. |
| Identity and scope | A document, event, state or affected subset is identified correctly. | A limited effect does not automatically reach the whole application or mark. |
| Evidence | A reviewed generic relevance relationship retains its limitations. | A heading or evidence category cannot establish satisfaction of a legal test. |
| Knowledge limits | An unresolved condition or incomplete coverage is visible. | No matching edge cannot become a categorical negative legal answer. |
| Disagreement | Competing propositions retain separate sources and review histories. | A confidence score or broad source label cannot silently settle the conflict. |
| Governance | Every new qualification has its own provenance and review state. | Old approval cannot be copied to a materially changed proposition. |

### Recommended release judgement

Continue demonstrating the vocabulary, sources and review workflow within their stated limits. Before a trusted examiner pilot, retain the original Package A gates and verify that current legal assertions preserve their decisive conditions. Resolve the `Exception` defect and adjudicate the evidence examples before those meanings are relied upon.

A full operational process engine is not a prerequisite for a useful knowledge demonstrator. A truthful account of procedural applicability and knowledge limits is a prerequisite for guidance that users may rely on.

## 13  Reproduction and limitations

### Commands and observed outcomes

| **Check** | **Observed outcome at the reviewed commit** |
| --- | --- |
| Parse `authored/relationships.yaml` and group by predicate | 352 authored records; selected process counts reported in section 1; three `establishes` records. |
| Inspect `gold-relationship.schema.json` | Core relation and provenance fields; modality enum `must`, `may`, `should`, null; no dedicated condition-expression or applicability fields. |
| Minimal OWL probe using RDFLib 7.6.0 and owlrl 7.6.2 | `doesNotGiveRiseTo` case inferred `Exception`: true. `qualifies` control inferred `Exception`: false. |
| Compare selected records with stored supporting text | Specific concerns described for GR-0688, GR-0163, GR-0206 and GR-0248. |
| Recheck official Manual 35.10 | The pre-referral and post-referral distinctions remain visible in the retrieved page. |

### How to repeat the independent probe

Run the following from a checkout of the reviewed commit with RDFLib and owlrl installed. It uses only the two relevant schema subjects, so unrelated graph content cannot account for the result.

```python
from rdflib import Graph, Namespace, RDF, URIRef
from owlrl import DeductiveClosure, OWLRL_Semantics

tmk = Namespace("https://data.ipaustralia.gov.au/tmk/ns/")
schema = Graph().parse("ontology/draft/legal-concepts.ttl")
x, y = URIRef("urn:probe:x"), URIRef("urn:probe:y")

for predicate in (tmk.doesNotGiveRiseTo, tmk.qualifies):
    graph = Graph()
    for subject in (tmk.Exception, tmk.GivesRiseToNoConceptByItself):
        for triple in schema.triples((subject, None, None)):
            graph.add(triple)
    graph.add((x, predicate, y))
    graph.add((y, RDF.type, tmk.LegalConcept))
    DeductiveClosure(OWLRL_Semantics).expand(graph)
    print(str(predicate), (x, RDF.type, tmk.Exception) in graph)
```

This tests the effect of the declared axioms under that implementation. It is not a certification of the entire ontology’s OWL profile, nor proof that the live application performs the inference. The original F07 profile finding remains separate.

The additional analysis is targeted. It does not estimate a corpus-wide error rate, adjudicate every legal proposition, validate operational deadlines or test real application histories. Recommendations concerning future case data are conditional on scope expansion. No ontology repairs or new production tests were implemented as part of preparing this document.

## 14  Repository evidence

All links are pinned to the same commit as the initial report. Record IDs identify the relevant rows in the linked files.

**A1  Legal concepts, propositions and the exception equivalence**

[Legal concept definitions and axioms](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/legal-concepts.ttl)

**A2  Predicate meanings and generated relation declarations**

[Predicate dictionary](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/src/tm_knowledge/ontology/predicates.py)

[Relations module](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/relations.ttl)

**A3  Relationship record and authoring envelope**

[Relationship schema](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/eval/schemas/gold-relationship.schema.json)

[Authored envelope schema](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/eval/schemas/authored-envelope.schema.json)

**A4  Authored relationships and their supporting passages**

[Authored relationship records](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/authored/relationships.yaml)

**A5  Time, source currency and assertion provenance**

[Time module](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/time.ttl)

[Provenance module](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/provenance.ttl)

**A6  Examination classes and roles**

[Examination and role module](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/examination.ttl)

**A7  Vocabulary records**

[Signed concepts](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/eval/gold/concepts.yaml)

[Authored concepts](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/authored/concepts.yaml)

**A8  Evidence and reasoning boundaries**

[Evidence module](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/ontology/draft/evidence.ttl)

[Query scope and bounded reasoning](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/queries/README.md)

[Inference shapes](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/shapes/inference.ttl)

**A9  Project governance and intended use**

[Project instructions and scope](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/6a75eefadd982c29190b1f92f451de5168a29508/CLAUDE.md)

## 15  Further evidence and standards

### Primary technical standards

**S1  W3C — Defining N-ary Relations on the Semantic Web**

[Working Group Note, 12 April 2006](https://www.w3.org/TR/swbp-n-aryRelations/)

Supports the proposed option of using an explicit relation instance to hold additional arguments or qualifications. This is informative design guidance, not a requirement to adopt a particular legal ontology or rule language.

**S2  W3C — OWL 2 Web Ontology Language Primer, Second Edition**

[OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)

Explains OWL’s declarative and open-world semantics. It supports the distinction between a missing assertion and a false assertion, and the need to separate logical inference from application validation and completeness policy.

## 16  Official legal source checks

**L1  IP Australia Manual — 35.10, Assignment of unregistered certification trade marks**

[Official Manual page](https://manuals.ipaustralia.gov.au/trademark/10.-assignment-of-unregistered-certification-trade-marks)

The retrieved page distinguishes assignment before documentation is sent to the Commission from recordal after referral and before registration, when evidence of consent is required. That distinction supports the modelling conclusion that procedural stage can determine the applicability of a relationship. It does not justify a universal consent rule for assignment.

The page states a publication date of 11 February 2026 and was checked on 15 October 2026. The current web page is a cross-check; the repository finding remains tied to the pinned record and its evidence.

### Boundary of the recommendation

The proposed structures make legal qualifications explicit and reviewable. They do not supply approved replacement legal rules, certify a complete examination workflow or authorise automated examination outcomes. The immediate objective is that the graph and its consumers preserve the meaning, limits and status of the material they already hold.

# Trade Mark Ontology Consolidated Review

**Technical findings and implementation recommendations**  
**Review date:** 18 October 2026, Australia/Sydney  
**Original review revision:** `3ecf410101c341a678be126ad85916b824aec482`  
**Follow-up review revision:** `e6985e9286c4a9f36befb8fbe82255fc94ecba01`  
**Common upstream snapshot:** `308bfd9162ebea3e0213e6299516ee314d6f2eca`

Repository: [Thomas-Amann-IPAustralia/TM-Knowledge](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/e6985e9286c4a9f36befb8fbe82255fc94ecba01), with the [original reviewed revision](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/3ecf410101c341a678be126ad85916b824aec482) retained for comparison.

## 1 Executive assessment

TM-Knowledge provides a promising, auditable vocabulary and source-navigation foundation. Its strongest features are explicit source provenance, separation of expert-signed and machine-authored records, preservation of corrections, and a restrained reasoning contract. These choices make the work inspectable and give it a credible route to expert review.

Improvement is needed before presenting the content as a dependable account of trade mark law and practice. Several sampled relationships and definitions say more than their supporting passages. Definition records are incompletely integrated into RDF export, validation and change-impact analysis. Passing the automated checks establishes substantial structural consistency, but does not establish legal fidelity or completeness.

The intended operational uses also require additional foundations. The repository does not yet provide the contextual model needed to explain an individual objection, represent a complete examination process, apply rules to facts, or compare the effects of alternative policies. These capabilities require more than additional concepts and relationships.

The recommended course is to retain the layered architecture, correct the content and integration defects, and extend the model around **matters, scoped propositions, events, evidence and explanations**. Those extensions should share identifiers and source anchors with the existing vocabulary. A wholesale replacement of RDF/SKOS or introduction of unrestricted OWL reasoning is unnecessary.

**Process, applicability, objection and evidence modelling should begin now.** The earlier recommendation to defer these areas was appropriate to a concept-navigation demonstrator, but the immediate customer use case requires a minimum model of them. A full operational case-management system can wait. Representing a report, a recorded human assessment or a hypothetical scenario does not require the chatbot to decide an application.

This report retains all **22 findings**, including their detailed evidence, corrective actions and completion or acceptance examples. R01–R10 retain the original implementation and semantic findings; A01–A12 retain the additional or strengthened findings against the intended uses. Their identifiers remain stable for issue tracking and cross-reference. Overlapping findings address different levels of the same problem: for example, R05 concerns incomplete dependency analysis, while A10 explains what is additionally required for policy simulation.

The immediate priorities are R01, R02, R03 and R05, together with the concrete retrieval and answer-verification weaknesses in A06 and A08. Establish the minimal process and matter model in parallel. Future decision automation and quantified policy forecasting need additional evidence and separate capability validation.

|Decision area|Assessment|Recommended decision|
|-|-|-|
|Architecture and provenance|Sound foundation with specific integration gaps|Retain the layered design and fix evidence export and dependency indexing|
|Legal and conceptual fidelity|Some sampled records overstate or narrow their sources|Correct the identified records and review similar predicates and definitions systematically|
|Automated assurance|Strong structural checks with important blind spots|Add negative fixtures and semantic answer tests|
|Demonstration scope|Useful for source navigation and explaining recorded relationships|State coverage and review status precisely|
|Search improvement|Not established over the strongest tested baseline|Preserve the baseline and evaluate graph expansion as an optional contribution|
|Operational decision support|Not established by the demonstrator|Begin a minimal matter, process, applicability and role model for the immediate examiner and customer uses|

## 2 Purpose scope and evidence

### Intended uses

The ontology is intended as a foundational layer for future machine learning, machine decision-making, customer service delivery and policy-writing support, including exploration of the flow-on effects of amendments. Its immediate examiner role is research and decision support: quickly identifying relevant guidance, legislation and related material. Its immediate customer role is explaining trade mark requirements, the application process and objections, potentially through an LLM chatbot with visual explanations.

The assessment therefore distinguishes the repository's current demonstrator scope from the foundation required by those intended uses. A useful examiner search tool need not wait for every future capability. However, the model should not permanently exclude the objects and context that later services will need.

### Review revisions and changes

The original review examined revision `3ecf410101c341a678be126ad85916b824aec482`, including the merge that introduced 149 machine-written definitions. It considered the stated whole-Manual demonstrator scope and the plan for examiner review of the assembled work at the end. The earlier review and the repository's response were examined to distinguish resolved issues from defects still present; their conclusions were checked against the implementation. \[S01–S03]

The follow-up examined revision `e6985e9286c4a9f36befb8fbe82255fc94ecba01`. Eight files changed between these revisions. The update exposes four signed concept-record hierarchy links in the explorer and adds definition display to table details and CSV export. This improves presentation consistency. The underlying ontology modules, record schemas, answer contract, retrieval engine and change-impact rule are unchanged. The semantic findings R01–R10 therefore remain relevant. \[S24]

The evidence below remains attached to the revision at which it was checked. This consolidation does not represent a new repository audit or a rerun of the full test suite. References to the current implementation mean the latest reviewed revision above; they are not claims about subsequent changes to the repository.

### Method and interpretation

The original work combined source-code inspection, ontology and schema inspection, a fresh upstream fetch, rebuild checks, the repository's tests, execution of all competency queries, and targeted in-memory mutation tests. The source review focused on high-risk legal predicates, qualifications, definitions and source boundaries. It is a purposive semantic review, not a claim that every authored statement has received independent legal approval.

The follow-up compared the revisions, examined the additional modelling requirements, reproduced passage-truncation and citation-verifier behaviours, and ran the current explorer tests. No repository content was changed. No new paid model evaluation, live customer data or automatic legal decisions were used. The reported retrieval results are the repository's existing, revision-specific measurements, not fresh measurements of either reviewed revision.

The assessment distinguishes four properties: whether a record is structurally valid; whether its quoted evidence is recoverable; whether the evidence supports the asserted meaning; and whether the model covers the question being asked. A record can satisfy the first two and fail the latter two. That distinction explains several findings below.

Architectural gaps are assessed against the inspected repository, not against every other IP Australia system. Public guidance supports the design examples but is not substituted for legislative authority. Fictional acceptance scenarios describe proposed tests, not conclusions about an actual application.

### Separate foundation scope from application permissions

The repository still describes a demonstrator with intentionally unpopulated application, examination and evidence objects. `ExaminationOutcome` is required to remain empty, and point-in-time questions are explicitly out of scope. Those are understandable product boundaries for the original demonstrator, but they are inappropriate as permanent restrictions on a reusable foundation. \[S25, S26]

Revise the architecture decisions and scope documents to distinguish **representing a recorded decision**, **explaining a rule**, **evaluating a hypothetical scenario**, **predicting an observed outcome**, and **making an operative decision**. They are different activities. A foundation can represent all five while each application is permitted to perform only its authorised activities.

Use explicit application profiles over the shared model:

|Profile|Immediate purpose|Required boundary|
|-|-|-|
|Examiner research|Find and compare relevant authorities and guidance|Preserve source context, currency and uncertainty; leave case assessment with the examiner|
|Customer explanation|Explain requirements, report contents, process and possible responses|Distinguish stated facts from assumptions; clarify missing context; do not convert an option into a promised outcome|
|Policy scenarios|Compare a baseline with a proposed rule or guidance version|Keep proposals separate from operative material; expose assumptions and unmodelled effects|
|ML and decision services|Develop future prediction or rule-application capabilities|Distinguish observed labels, legal propositions, predictions and authorised decisions; maintain separate release criteria|

## 3 Observed state and verified checks

The inventory and full-suite results in this section were measured at the original review revision. The follow-up results are labelled separately. The revision comparison found no changes to the underlying records and ontology modules.

### Inventory

|Item|Observed state|
|-|-|
|Ontology modules|9 draft modules; 90 declared classes|
|Relation vocabulary|53 project predicates, excluding SKOS broader; 14 used in signed relationships and 51 in authored relationships|
|Concepts|52 expert-signed concepts and 112 machine-authored concepts|
|Concept typing|164 machine-authored typings; none expert-signed|
|Relationships|35 signed records, of which 20 are current and 15 corrected; 337 authored records|
|Definitions|149 machine-authored definitions: 53 statutory definitions, 22 statutory-provision summaries and 74 Manual-based definitions|
|Definition review status|All unreviewed; 45 define concepts whose labels were signed|
|Corrections|37 unreviewed correction records affecting 36 signed records|
|Graph sizes|Source 64,644; approved 3,574; authored 16,107; inferred 2,315 triples|
|Graph source coverage|1,053 of 2,460 Manual chunks, or 42.8%; 204 of 500 pages, or 40.8%|
|Legislative and case references|670 provision or provision-unit nodes and 311 case-citation nodes in the source graph|
|Citation resolution|2,206 citation occurrences, including 63 unresolved occurrences|
|Competency queries|13 implemented for 20 competency questions; six deferred to retrieval approaches and one missing|
|Inference rules|One approved dependency rule and one pending mixed-authority rule|

These counts describe different types of work. A signed concept label does not approve its machine-written type or definition. Case-citation nodes do not supply judgment text. The 670 legislative nodes include subunits and should not be described as 670 complete provisions. The graph subset is also distinct from the whole-Manual search corpus. \[S04–S06]

### Reproduced results

|Check|Result|Interpretation|
|-|-|-|
|Repository unit tests|782 passed, 2 warnings, in 8 minutes 25 seconds|Software regression coverage at the reviewed revision|
|Gold and authored record harness|0 defects, 12 gaps, 15 notes; Stage 0 incomplete|Schema and evidence checks pass, while evaluation inputs remain incomplete|
|RDF rebuild|Committed graph matches the fresh build|Reproducible output from the pinned inputs|
|Ontology report rebuild|Committed report matches the fresh build|Report counts are generated consistently|
|SHACL validation|0 defects, 0 gaps, 259 notes|The notes concern not-labels matching other concepts' labels|
|Unbacked authored edge mutation|Rejected|The direct-edge provenance check catches this tested violation|
|Definition provenance mutation|Accepted with zero defects after deleting author and source links|The Definition class is outside the required-envelope shape's effective coverage|
|Inferred assertion comparison|Five mismatches, all in RULE-0001|The reified object differs from the emitted triple's object|

The harness's 12 gaps and SHACL's zero gaps are results from different checks. They should not be combined into a single assertion that the project is either wholly complete or wholly invalid. The harness reports missing evaluation material, five unsigned modality judgements, and absent metric thresholds. It also reports 21 legislative-basis citations as unverified by its evidence checks, which is a review queue rather than proof that those citations are wrong. \[S04–S07]

### Follow up checks

At revision `e6985e9286c4a9f36befb8fbe82255fc94ecba01`, `python -m pytest tests/unit/test\_explorer.py -q` completed with **19 passed in 84.20 seconds**. This scoped run is separate from the original result of 782 passing tests and is not a full-suite result for the newer revision.

The source-context probe reproduced the 1,600-character truncation described in A06. The browser verifier probes reproduced the empty-citation, invalid-citation and outside-excerpt behaviours described in A08. No live model call was needed. Passing explorer tests establish the checked implementation behaviours, not legal completeness or customer comprehension.

## 4 Strengths to preserve

The separation of source, approved, authored and inferred graphs is appropriate. It makes provenance and review status visible and avoids treating a machine's assertion as expert approval. Keeping a signed record unchanged while recording a correction separately is also valuable: it preserves the original evaluation evidence and makes later intervention inspectable. The current competency queries now exclude corrected signed relationships from their current results.

The source pipeline retains citation extraction method and certainty, references a pinned upstream snapshot, and verifies quoted spans and hashes in the authoring stores. This is materially better than attaching an undifferentiated URL to a generated sentence. The existing source and record validators catch many errors before publication, and the fresh graph and report matched their committed versions.

The explicit distinction between legislation and Manual practice is essential. The project also keeps prohibited uses, records uncertainty and preserves unresolved citations rather than silently repairing them. The pending mixed-authority rule remains marked as a candidate. Those are useful controls even though the authority detector and shape coverage need further work.

The current RDF, SKOS, SHACL and bounded SPARQL-rule contract is suitable for this stage. The repository no longer claims an OWL profile or licenses unrestricted OWL inference. This avoids confusing a browsable concept map with a legal decision engine. SKOS hierarchy also remains distinct from class inheritance, which should continue to be the case.

The recent response has addressed several earlier concerns, including explicit conditional text on selected relationships, weaker wording for evidence that may support a conclusion, correction filtering in competency queries, and automated rebuild gates. R01 and R07 concern the remaining semantic limitations of those fixes, rather than treating the earlier state as unchanged. \[S02–S07]

## 5 Detailed implementation and semantic findings

R01–R10 retain the original technical and semantic findings. Their evidence comes from the original review revision; the follow-up comparison found that the relevant underlying implementation remained unchanged. Where a finding refers to the demonstrator, that describes the inspected implementation, not the limit of the intended foundation.

### R01 Exception relationships still overstate their evidence

**Priority: High. Evidence: current records and their complete source context.**

The four current uses of `isAnExceptionTo` do not consistently express a legal exception. The predicate describes a case a ground or test does not reach. Several sources instead describe an outcome as unlikely, or require reconsideration after additional evidence. A factor that tends to make a test fail is different from a rule that disapplies the test.

|Record|Current modelling|Problem shown by the evidence|
|-|-|-|
|GR-0699|Business identifier is an exception to the generic ground for rejection|The Part 29 passage says a ground will rarely apply where the identifier characterises the business. The generic target also loses the section 43 context|
|GR-0700|Deceased person is an exception to the section 43 ground|The passage concerns long-deceased historical figures and uses a general tendency, not all deceased persons or an unconditional exclusion|
|GR-0701|Fanciful or ambiguous geographical reference is an exception to likely confusion|The passage says deception or confusion is unlikely in those circumstances; the ordinary test still supplies the reasoning|
|GR-0702|Owner or authorised user is an exception to the section 43 ground|The quoted sentence promises reconsideration when phoneword ownership or authorisation is confirmed. The preceding sentence supplies useful context, but the broad concept and exception edge still compress that context too far|

For GR-0699 and GR-0700, the `applies\_when` value largely repeats the predicted outcome. That is not a clean statement of the factual antecedent. The added qualifier therefore does not resolve the predicate's overstatement.

**Action.** Re-read the four records together with their adjacent paragraphs. Separate the relevant circumstance from the degree of support and the procedural consequence. Use a weaker existing relation such as `qualifies` when that is accurate; introduce a narrowly defined likelihood or reconsideration relation only if needed. Restrict any section 43 relation to that ground, and reserve an exception relation for a source that actually excludes a case from a rule's operation. Keep the replacement records unreviewed until the planned expert review.

**Completion check.** The rendered reading of each replacement must preserve the source's scope, uncertainty and consequence. Include near-miss examples covering a recently deceased person, a business identifier challenged on another ground, and evidence that prompts reconsideration without establishing acceptance. \[S08, S09]

### R02 Some new definitions omit material qualifications

**Priority: High. Evidence: sampled GD records and the provisions or Manual passages they cite.**

Making definitions independent records is a good design decision. Their present content nevertheless includes examples where a locally accurate quotation produces an overbroad or incomplete definition.

|Definition|Finding|Required correction|
|-|-|-|
|GD-0146 for adverse report|Defines the concept through a report following an applicant response and makes inclusion of a lapsing date unconditional|Distinguish initial and further reports. Regulation 4.10 includes a qualification where acceptance is deferred; scope that obligation separately from the concept definition|
|GD-0050 for capable of distinguishing|Combines a general description with an unqualified section 41 rejection consequence|Preserve the certification-mark qualification stated immediately after the quoted passage; distinguish the concept from the applicable rejection rule|
|GD-0128 for pending application|Compresses refusal and appeal termination into final refusal, while evidence omits section 11(1)(c)|State the appeal-related ending events precisely and include the omitted supporting limb|

GD-0050 is particularly instructive: the hash and quoted span are valid, yet the nearby passage limits the generalisation. Quotation accuracy alone cannot detect this error. GD-0146 likewise illustrates why an operational Manual description should not silently become the full definition of a broader procedural concept.

**Action.** Keep a short conceptual definition separate from obligations, consequences and procedural steps. Add scope notes for mark type, proceeding and relevant statutory context where needed. Review each statute-derived definition against the complete applicable subsection and each Manual-derived definition against its parent section and adjacent qualifications. Prioritise all 22 statutory summaries, the 74 Manual-derived definitions, and definitions of signed concepts that users may assume are also approved. A justified missing definition is preferable to an unsupported one.

**Completion check.** Correct the three examples, retain precise supporting anchors for each material limb, and record whether the definition is complete only within a stated scope. The expert review pack should expose the complete source context beside the proposed definition, not only the selected sentence. \[S10, S20]

### R03 The RDF export loses definition evidence detail

**Priority: High. Evidence: graph inspection and builder code.**

All 149 Definition nodes lack exported `sourceContentHash`, span and supporting-quote fields, despite 230 evidence items in their YAML records. The builder emits authoring metadata and `sourcePassage` links through `\_origin`, but `\_build\_definitions` does not preserve the full evidence anchors.

There are also eight referenced source nodes absent from the source graph, associated with GD-0060, GD-0112 and GD-0138. Examples include `TMA1995/s14(1)(a)`, `TMR1995/r2.1/art` and the certificate-of-verification definition and its subunits. These references exist in the pinned upstream corpus. The defect is export coverage, not fabricated source material.

An RDF-only consumer cannot reconstruct the definition evidence as it appears in YAML. Where an assertion has multiple evidence items, flattening refs, hashes and spans onto one assertion would also lose the pairing between a particular quote and its source.

**Action.** Introduce an evidence-anchor resource for each evidence item. Link the assertion to the anchor, and the anchor to its source reference, quoted text, offsets, hash and document version. Use this representation consistently for definitions and other authored record types. Build the source graph from the union of evidence references across every supported store, including definitions and corrections.

**Completion check.** Every one of the 230 definition evidence items can be reconstructed from the RDF with its original associations; every evidence reference resolves to a source node or an explicitly classified external reference. Add an export round-trip test and a fixture whose only source use is in a definition. \[S10, S11]

### R04 Validation misses a new record type and an inference inconsistency

**Priority: Medium. Evidence: reproducible in-memory mutations and triple comparison.**

The required authored-envelope shape targets `tmk:AuthoredAssertion`. Definitions are represented as `tmk:Definition`, a subclass of `Assertion`, and do not receive the same check. Removing `authoredBy` and every `sourcePassage` from GD-0001 in memory still yields a successful validation with zero defects. The normal YAML harness does validate definition evidence, so this finding is specifically about the exported graph's validation coverage.

Separately, all five RULE-0001 inference records declare their `assertionObject` as the chunk URI. The actual conclusion is `chunk mixedAuthority true`, whose object is the Boolean literal. The reified statement and the emitted statement therefore disagree. SHACL accepts this graph. RULE-0001 is pending and its output remains candidate material, which limits the current impact, but the provenance record should still describe the conclusion accurately.

**Action.** Apply reusable envelope constraints to all authored record categories and add a Definition shape covering its subject concept, text, basis and evidence anchors. Correct RULE-0001's reified object to Boolean true. Add a check that each reified inference exactly matches its emitted subject-predicate-object triple, and that each emitted conclusion has an appropriate inference record.

**Completion check.** Negative fixtures deleting a definition author, definition source, required basis or definition target fail. A deliberately mismatched inference object fails. The corrected committed dataset passes. Retain the existing unbacked-edge test, which successfully rejected the mutation tested in this review. \[S11–S13]

### R05 Change impact omits current authored dependencies

**Priority: High for the whole-Manual change-impact claim. Evidence: rule results and explorer builder.**

RULE-0002 traverses only the approved graph. Its original limits describe that narrow scope honestly, but the resulting impact view is incomplete for the current demonstrator. None of the 149 definitions is an impact dependant. All 15 corrected signed relationship records remain in its dependency output, while authored replacements are outside the query.

The browser's `stability` builder is broader in other respects, but still gathers concept, typing and relation references without traversing the newly added definition evidence. A source change can therefore require re-reading a displayed definition without that definition appearing in the impact list. The two implementations also answer different versions of the same question.

**Action.** Build one shared dependency index over every evidence item and every current record type. Represent the affected record ID, record type, review status, source version and reason for dependency. Provide an effective-current view and a separately labelled historical view so that preserved signed records remain available without crowding out their replacements. Preserve the rule's existing warning that unrecorded dependencies remain invisible.

**Completion check.** A synthetic change to a passage used only by a GD record returns that definition. A passage used by a correction and its replacement exposes the current affected record and the historical link. RDF and browser impact results agree for the same declared scope. A result with no recorded dependants is described as no recorded impact, not no possible impact. \[S13, S14]

### R06 Executable competency queries do not always answer their questions

**Priority: Medium. Evidence: execution of all 13 queries.**

CQ-0009 asks what must be established before a standalone geographical reference is treated as likely to cause confusion. It returns only GR-0005 and GR-0052: an excluded basis concerning connotation and an extension to the specification of goods and services. It returns no `requiresElement` statement, and one object has no concept label in the result. Those rows do not constitute the required-elements answer described in the query header.

The correction filter correctly removes superseded signed records, but the query only reads the approved graph and does not return authored replacements. This makes the trust choice visible in code but not sufficient as an answer contract. CQ-0024 similarly reports counts grouped by modality, rather than answering whether a particular statement is a requirement or usual practice. Its comment refers to authority, but authority is not an output variable.

**Action.** Define an answer contract for each competency question: supported scope, expected records or propositions, required qualifications, source authority and treatment of corrected or unreviewed content. Distinguish a reviewed-only answer from an effective-current answer. The former may properly report insufficient reviewed material; the latter must display the status of authored replacements. Label the report's measure as queries implemented until semantic answer checks pass.

**Completion check.** Add expected-result fixtures for CQ-0009 and CQ-0024 that assess relevance and required fields, not merely parseability or non-empty output. Apply the same approach to every supported competency question. Keep the deliberate refusal to decide a particular mark's connotation strength in CQ-0012. \[S15, S16]

### R07 Conditions need an explicit representation and consumption contract

**Priority: Medium. Evidence: authored relationship inventory and graph construction.**

Only 26 of the 337 authored relationships carry `applies\_when`. The other 311 are not automatically errors: some relations are genuinely unconditional or taxonomic. However, the current representation does not distinguish no condition needed from a condition not yet assessed.

GR-0319 describes precedence between opposition and defence notices in a non-use proceeding; the passage conditions the applicant's duty on wishing to continue. GR-0206 concerns evidence of use and capability to distinguish in particular colours for a mark lacking inherent adaptation. Both have context that a general relation between their concept labels can obscure.

The RDF builder emits an ordinary subject-predicate-object edge even when the corresponding reified assertion has a condition. RDF reification describes a statement; it does not turn the separately asserted direct triple into a conditional proposition. The current absence of unrestricted reasoning limits the immediate effect, but consumers can still read the navigation edge too strongly.

**Action.** Treat the qualified assertion as the canonical legal reading. Document direct edges as a navigation projection and keep them out of legal entailment. Add a condition-assessment state such as not assessed, none required or specified. For the highest-risk relations, record minimal proceeding, mark-type and applicability context alongside readable condition text. Review exception, requirement, prevention, outcome and temporal predicates first.

**Completion check.** The same assertion exposes its conditions and review status in the browser, answer context, query output and RDF. Negative examples demonstrate that an edge for one proceeding or mark type is not presented as a universal rule. This can be achieved without introducing a general legal rules engine. \[S08, S11, S22]

### R08 The authority detector is a warning heuristic

**Priority: Medium. Evidence: deterministic detector probes, not observed live model failures.**

The answer-authority detector catches an assertion that legislation requires a proposition when only Manual material is cited. It does not establish that a cited provision supports the proposition. In the probes, adding a section 43 citation caused the warning to disappear even though the tested wording attributed the Manual's obvious-direct-immediate formulation to legislation. A generic Act-requires sentence with a section 6 citation also passed. Prefixing the sentence with an explanation that the Manual says it could bypass the warning.

This behaviour is understandable for a lightweight detector. The risk is treating absence of a warning as verified authority alignment. The detector receives a collection of answer citations rather than a complete claim-by-claim proof. SHACL constraints over graph records do not validate the entailment of arbitrary answer prose.

**Action.** Describe the check as a heuristic warning. Pair each substantive answer claim with its specific source anchors and distinguish statutory text, Manual explanation, case citation and authored interpretation. Add adversarial cases where the cited provision exists but does not support the claim, and cases where practice is presented as binding despite a Manual attribution. Soften any absolute capability wording that implies the distinction is guaranteed everywhere.

**Completion check.** The documented detector contract describes both what it detects and what a clean result means. PU-0004 tests include irrelevant legislative citations and mixed-attribution sentences. Expert answer review measures authority errors directly; a clean heuristic result does not itself count as a correct answer. \[S17]

### R09 Existing measurements do not establish a retrieval advantage

**Priority: Medium. Evidence: stored measurements at their own revisions.**

The project deserves credit for retaining negative results. They should govern how the ontology's value is described.

|Measurement|Result|Supported conclusion|
|-|-|-|
|9 October hybrid comparison, 129 questions|nDCG@10: keyword 0.725, hybrid 0.844, ontology 0.803|Ontology expansion improved on keyword search but underperformed hybrid search in this experiment|
|Paired ontology-minus-hybrid difference|-0.041, 95% interval \[-0.067, -0.017]|The measured overall reduction was established under this benchmark|
|Expert evidence-list cross-check, 10 questions|Ontology-minus-hybrid +0.001, interval \[-0.105, +0.101]; Recall@10 0.583 for all three|No dependable advantage was established on this small independent evidence check|
|12 October browser comparison, 129 questions and no vectors|Keyword 0.702, names 0.661, reading 0.701; reading-minus-keyword -0.001, interval \[-0.039, +0.036]|Reading the question improved on name matching, but did not establish an overall improvement over keyword search|

The two experiments use different systems and grading pools, so their absolute scores should not be compared as a time series. Most benchmark questions and relevance grades are model-generated. They are useful engineering signals, while the expert evidence check is smaller and tests a narrower criterion. None of these measurements validates the latest semantic revisions.

**Action.** Keep the strongest available baseline available independently of ontology expansion. Investigate broad concepts, undirected neighbour expansion and equal-ranking contributions as possible sources of irrelevant results; these are hypotheses to test through ablations. Measure the ontology's other intended benefits separately, including source tracing, cross-part navigation and finding affected records. Honour the existing decision to defer remeasurement until the content is ready.

**Completion check.** At the next agreed evaluation point, freeze questions and relevant-source judgments before tuning; include examiner-authored cases, ordinary user wording and near misses. Report query categories and uncertainty alongside the overall score. Claim search improvement only for configurations and populations where the evidence supports it. \[S18, S19]

### R10 Coverage and source currency need clearer boundaries

**Priority: Medium. Evidence: corpus inventory, graph coverage and source metadata.**

The source graph contains 42.8% of Manual chunks and 40.8% of pages. Five of the 54 Parts have no chunk in that graph: Parts 1, 4, 8, 41 and 61. Seven have no authored relationship: those five plus Parts 7 and 45. This can be a legitimate consequence of selective graph construction. It does mean that a connected concept map, whole-Manual text search and comprehensive semantic coverage are different achievements.

The Manual capture is dated 3 August 2026. The Act snapshot is compilation 48, in force from 19 September 2026, and the Regulations snapshot is compilation 53, in force from 18 December 2025. A successful hash check proves agreement with those stored inputs; it does not prove that Manual practice has been reconciled with the later Act compilation or that a particular application's transitional regime is represented. The official register identifies the same Act compilation. \[S20]

The 311 case nodes supply references, not the judgments and their holdings. The 21 unverified legislative-basis citations also warrant a focused source review. Neither limitation should be obscured by the number of graph edges.

**Action.** Publish separate coverage measures for source availability, concept coverage, relation coverage, definition coverage and expert review. Show source capture and legislative version dates beside the relevant views. Maintain a scoped list of supported questions and known source exclusions. Resolve the legislative-basis queue by adding evidence, correcting the association or retaining an explicit unresolved status.

**Completion check.** A user can tell whether a query concerns text that is searchable, meaning that is modelled, and content that has been reviewed. The source graph's absent Parts are visible in the coverage report. Current-source and historical-applicability claims are only made when the required reconciliation or version evidence exists. \[S04–S06, S20]

## 6 Foundations for the intended uses

A01–A12 extend the assessment to examiner research, customer explanations, future ML and decision services, and policy scenarios. A06 and A08 identify concrete implementation weaknesses. The remaining findings describe missing or incomplete capabilities that should be developed in the sequence appropriate to the intended use.

### A01 Model the matter and each objection not only the vocabulary

**Priority: immediate design foundation; implement a small example before customer trials.**

**Issue and evidence.** The examination module declares `TradeMarkApplication`, `Examination` and `Objection`, but leaves them unpopulated. It does not supply the relationships needed to connect a report's separate objections to the relevant sign, goods/services, findings and response options. Role classes also mix actors and capacities: their comments describe people or bodies, while global disjointness separates parties, representatives and delegates. This is a latent problem when real people are introduced, rather than an observed inconsistency in the present empty instance model. \[S25]

**Why it matters.** A customer can receive several objections concerning different parts of an application. Explaining a section in general does not explain which issue the examiner raised, which goods/services are affected, or which part of the application could progress. Similarly, one person can occupy different capacities across different matters or times.

**Suggested solution.** Add a small matter model separating the sign and its representations, application, claimed goods/service items, examination, report, objection and registration. Link each objection to its cited ground, stated reasons, affected items and current disposition. Represent a person or organisation separately from a `RoleAssignment` scoped to a matter and time. Keep classification codes distinct from the actual specification of goods/services; do not use class membership as a proxy for a legal similarity assessment.

**Acceptance example.** A fictional report has two objections affecting overlapping but different goods. The system explains each separately, shows what remains unresolved, and does not mark the whole application accepted when one objection is resolved. A person acting in two capacities can be represented without contradictory typing. Public guidance already distinguishes options affecting only part of an application. \[S35]

### A02 Represent process stages events and conditional response paths

**Priority: immediate customer functionality.**

**Issue and evidence.** The examination classes are placeholders rather than a process model. There is no executable or declarative transition model tying a report, response, further report, deferment, acceptance or other event to its prerequisites and effects. A concept graph can retrieve descriptions of these stages, but cannot establish a customer's position in the process. \[S25, S26]

**Why it matters.** “What happens next?” depends on what has happened already. A response is not necessarily resolution of an objection; an acceptance-related deadline is not interchangeable with every response timeframe. Different application routes and procedural circumstances may require different branches. A static timeline can mislead if it hides these conditions.

**Suggested solution.** Start with reviewed process templates: stages, events, permissible transitions, responsible roles, required inputs and source-backed conditions. Separate these templates from an individual matter's event history. For time limits, model the triggering event, applicable rule version, duration, extension/deferment effects and any calendar convention. A supplied deadline should retain its source, such as the actual report, rather than being silently recalculated from a generic rule.

**Acceptance example.** Given a first report, a subsequent response and a deferment event, the explanation identifies the applicable branch and the information still needed. It does not infer lapse from a generic elapsed period. Initially, explain deadline rules and missing inputs; enable calculated dates only for branches whose rules and boundary cases have been reviewed.

### A03 Make applicability and meaning depend on context and time

**Priority: define now; required before date-specific guidance or amendment comparison.**

**Issue and evidence.** `time.ttl` explicitly excludes point-in-time questions and holds one compilation per instrument. Capture times and content hashes track source changes, but do not determine which rule applies to a matter. The definition schema provides one definition per concept and an optional textual scope note, rather than machine-queryable definitions with different scopes or effective periods. \[S26, S27]

**Why it matters.** A current provision may not govern every older application. A definition can apply only within a particular instrument, Part or proceeding. Selecting the newest source or preferring a statutory definition does not resolve those questions. This affects present customer explanations as well as future simulations.

**Suggested solution.** Separate the enduring identity of an instrument or concept from its versioned text and scoped statements. Record legal effective intervals, the dates or events governing applicability, and separately when the repository captured or learned the information. Model transitional rules explicitly. Allow several definition records where scope or period differs, with a reviewed disambiguation rule and an unresolved state. Use OWL-Time for temporal primitives where useful; it does not supply trade mark transition law by itself. \[S38]

**Acceptance example.** Two otherwise identical fictional applications on opposite sides of a stipulated transition date select different rule versions with an explanation. An unknown filing date produces a clarification request. The same term in two scopes resolves to the relevant definition rather than whichever definition was loaded most recently.

### A04 Introduce structured legal tests alongside conceptual relationships

**Priority: capture structure for priority topics now; execute only reviewed rule subsets later.**

**Issue and evidence.** Relationship records are primarily binary links, with `must`, `may` or `should` and an optional free-text `applies\_when`. They do not constitute a model of compound legal tests, alternatives, negation, exceptions, conflicting rules or discretionary powers. The first review's R07 identified the immediate condition-loss problem; this is the broader representational gap. \[S27]

**Why it matters.** “Evidence may establish X” and “the Registrar may do X” use the same word for different purposes. A legal test can require several facts jointly, permit alternatives, or be displaced by an exception. Traversing a relationship does not demonstrate that those conditions hold.

**Suggested solution.** Keep the concept graph for terminology and navigation. Add identifiable norm or test records with an actor where relevant, conditions, legal effect, modality meaning, scope, authority, applicable period and explicit exceptions or priority relationships. Conditions should support AND/OR and distinguish an unknown fact from a false one. Keep evaluative predicates, such as a legal similarity assessment, visible as assessments requiring an authorised method or human judgment. Each encoded test should trace back to exact source units and its reviewed interpretation.

LegalRuleML offers a useful reference model for defeasible rules, normative effects and contextual qualifications; adopting its full serialization is optional. Select a small, tested subset before choosing a rule engine. \[S37]

**Acceptance example.** A reviewed test has two necessary conditions and an exception. Missing one condition yields “not established from the available facts,” rather than an automatic negative decision. A discretionary power is not converted into an obligation merely because its prerequisites are present.

### A05 Separate case evidence factual claims and assessed conclusions

**Priority: needed for useful evidence-of-use and objection explanations.**

**Issue and evidence.** `evidence.ttl` contains four unpopulated classes. It does not model the chain from an exhibit to a factual assertion, to a legally relevant issue, to a recorded assessment. Its prohibition on populating evaluative propositions also needs the representation/execution distinction described earlier. The repository's excellent concern for source-quotation evidence is a different kind of evidence from material filed by an applicant. \[S28]

**Why it matters.** A sales document is not itself a conclusion that a legal requirement has been met. The relevant date, sign, territory and goods/services matter. IP Australia's customer guidance illustrates why context is necessary: it distinguishes the treatment of use and intended use for section 41(3) and section 41(4) issues. \[S36]

**Suggested solution.** Model an `EvidenceItem`, its submission, the claims it supports or challenges, the relevant period and goods/services, and a separate `Assessment` identifying who made it and on what basis. Keep applicant assertions, verified facts, hypothetical facts and examiner conclusions distinct. Attach any burden or standard to the relevant issue and proceeding rather than imposing a universal default. Distinguish evidence relevance from sufficiency.

**Acceptance example.** The system can explain which question an exhibit may help address and what dates or links are missing, without declaring that the evidence succeeds. A later assessment can disagree with an earlier one without overwriting either. A stored human conclusion remains distinguishable from a model-generated suggestion.

### A06 Retrieve complete legal context not fixed-length passage prefixes

**Priority: immediate defect to address before relying on generated explanations.**

**Issue and evidence.** The Python answer renderer and browser prompt truncate each selected passage to its first 1,600 characters. The current section 44 text is 3,785 characters long: subsection (3) starts at character 2,390 and subsection (4) at 2,962, using zero-based offsets. Both substantive qualifications fall outside that prefix. Conversely, the extracted `s44(1)` unit contains only the opening conditional clause; its criteria are in child units. \[S29, S30, S39]

The local probe also found 372 of 2,460 Manual chunks and 101 of 763 full legislative provisions exceed this limit. These are counts of potentially truncated source objects, not measured counts of incorrect answers. Other passages could independently supply the missing context; the failure is that completeness is not guaranteed.

**Suggested solution.** Assemble a source-context bundle around the selected legal test: parent scope, required child units, qualifications, explicit cross-references and relevant definitions. Retrieve the correct subsection directly where possible, then include the context needed to understand it. Allocate prompt space to complete units and disclose omissions. Raising the character limit alone is an incomplete remedy.

**Acceptance example.** A question about section 44 retrieves the relevant conditions and subsections (3)/(4), or explicitly reports which parts are unavailable. A subsection lead-in is never presented as the complete test. Add a regression fixture for this exact truncation, plus a case where an exception is on another page.

### A07 Broaden source access while preserving proposition-level authority

**Priority: immediate for examiner research; expand coverage by task.**

**Issue and evidence.** The keyword index searches Manual chunks. Legislative material is added through concept and passage associations rather than having an equivalent independent full-text search route in that index. The authority module deliberately holds cases at citation level without judgment reasons. Customer service guidance is not a populated, equivalent source collection. The existing law/practice distinction is valuable, but it does not establish the authority of a particular case proposition or the current service instruction. \[S30, S31]

**Why it matters.** An examiner's question may use wording from legislation that the concept map has not captured. A related case citation does not establish what the court held. A customer may need an official form or response procedure rather than another Manual passage. Public-facing guidance can simplify legal and procedural distinctions; it should retain that source status.

**Suggested solution.** Add direct exact-reference and text retrieval over the held legislation, alongside Manual search. Build a task-based source register identifying which judgments, official customer pages, forms and other materials are required. Link to source material before attempting exhaustive ingestion. When judgment explanations are supported, capture paragraph-level propositions, court, date, procedural context and reviewed subsequent treatment where relevant. Preserve whether a proposition is quoted, paraphrased or inferred, and distinguish a Manual account of a case from the judgment itself.

**Acceptance example.** A section-number query can retrieve the legislation independently of concept coverage. A question about a case's holding returns the relevant judgment paragraphs when held, otherwise identifies the limitation and provides the authoritative link. Conflicting guidance remains visible for resolution rather than being flattened into one authoritative statement.

### A08 Make support verifiable for each claim before displaying the answer

**Priority: immediate answer-quality defect; extends the first review's authority finding.**

**Issue and evidence.** `\_ANSWER\_SCHEMA` contains one answer string and a separate citation list, without claim-to-evidence links. `Engine.verify` checks whether quotations occur in a selected source. It accepts an empty list as no kept and no dropped citations. If a quote fails, `ask.js` passes the original answer to the display with the remaining citations and a removal notice. Answer text is also streamed before this check. These behaviours were confirmed by code inspection and a deterministic verifier probe. No live model was needed. \[S29, S30]

**Why it matters.** A real quotation can be irrelevant to a claim. Removing a bad citation does not remove its unsupported assertion. A customer-facing explanation can therefore look complete even when the verification step supplies no support for its central statement. This is more specific than the general risk of hallucination.

The verifier also checks the full stored source rather than the excerpt actually supplied. A real section 44 quotation outside the 1,600-character prompt passed this check in a local probe. This does not prove model misconduct; it shows that the present check cannot establish what source context the model actually saw.

**Suggested solution.** Return an explanation object containing discrete claims, claim type, scope, supporting or challenging source spans, and any assumptions or missing facts. Validate source identity and quoted span against the version and context actually supplied, then evaluate whether the evidence supports the claim and its qualifications. Use reviewed templates for recurring legal explanations and expert-labelled tests for more flexible generation. If support fails, omit or repair the affected claim, or state the evidence gap; do not merely discard its citation. Do not display substantive legal claims as validated while the check is incomplete.

**Acceptance example.** Inject an invented quote, an irrelevant authentic quote and a claim with no evidence. None appears as a supported conclusion. Where one claim fails, supported claims and useful source links can still be shown. Store the final validated claim/source mapping with the answer.

### A09 Build customer explanations and visuals from a shared explanation model

**Priority: immediate customer design; reuse the same foundation for examiner views.**

**Issue and evidence.** The answering instructions explicitly target an examiner. The repository has useful everyday-language recognition, aliases and a graph/search trace, but it lacks a structured customer task/context contract. A trace explains how passages were found; it does not establish why an objection applies or what the customer should understand next. \[S29, S30]

**Why it matters.** “They rejected my name” may refer to an objection in an examination report, another procedural outcome, or a different registration system. Assigning a concept label immediately can select the wrong explanation. A visually persuasive graph can also imply a legal inference where it shows only retrieval associations.

**Suggested solution.** Define customer intents and a small set of relevant context slots: report wording or cited ground, application route, stage, affected goods/services and dates where necessary. Ask only for facts that change the explanation; allow general guidance without personal case data. Keep plain-language explanations as reviewed, versioned views of scoped propositions, not alternative legal definitions. Use the A08 explanation object to generate both prose and visuals.

Provide three views: an issue card connecting the report wording to the requirement and source; a conditional process timeline; and an evidence-to-issue view showing what material may help address. Each visual should expose sources and conditions, label unknowns, and have an equivalent readable text view. Distinguish “why this was retrieved” from “why this proposition is supported.”

**Acceptance example.** A customer can identify the issue, its affected scope, an available response route and the missing information after reading the explanation. Changing a relevant fact changes both the prose and diagram consistently. Test understanding with customers, rather than treating a clear-looking diagram as proof of explainability.

### A10 Separate dependency analysis legal scenarios and real world policy effects

**Priority: architecture now; phased implementation for policy support.**

**Issue and evidence.** `RULE-0002` identifies recorded source dependencies and explicitly limits its interpretation. It is not an amendment simulator. The first report's R05 addresses incomplete dependency coverage; even complete dependency coverage would not show how an amendment changes outcomes or behaviour. \[S32]

**Why it matters.** “Which guidance needs review?”, “Would this hypothetical matter be treated differently?” and “How many applicants would change behaviour?” are three different questions. The last cannot be answered from ontology connectivity alone.

**Suggested solution.** Implement three distinguishable analyses:

* **Editorial impact:** trace a proposed amendment to dependent propositions, definitions, guidance, forms, examples, explanations and tests. Report uncovered dependencies and the reason for every included item.
* **Normative scenarios:** compare isolated baseline and proposal versions on reviewed fictional or permitted historical cases. Include commencement, transitions, assumptions, discretionary assessments and unresolved interpretations. Report changed reasoning as well as changed results.
* **Behavioural or operational effects:** add a separate empirical model when estimating volumes, workload, cost or applicant responses. Declare data, assumptions, uncertainty and sensitivity; calibrate and validate the model before presenting quantified forecasts.

**Acceptance example.** A fictional amendment to an exception changes the relevant guidance dependencies and specified scenario results, while unrelated scenarios stay unchanged. The system can state that a workload consequence is unknown unless a separate model supports it. Draft policy remains visibly distinct from operative law throughout the comparison.

### A11 Create versioned reuse contracts for ML and other downstream consumers

**Priority: define before external consumers depend on the graph.**

**Issue and evidence.** The repository carefully distinguishes signed, machine-authored and corrected material. However, its records and outputs primarily serve the demonstrator. The first review found that evidence does not survive every projection; the latest commit also illustrates that hierarchy links and definitions can appear differently across interfaces. A consumer needs a stable semantic contract, not assumptions inferred from a UI badge. \[S24, S33]

**Why it matters.** ML systems may treat a historical examiner outcome as legal truth, an unreviewed relation as a training label, or a later decision as information available at an earlier prediction date. Documents from the same matter can leak between training and evaluation. A single “confidence” value cannot distinguish extraction accuracy, legal interpretation and uncertainty about case facts.

**Suggested solution.** Publish versioned releases with an ontology version, source snapshot identifiers, schema versions, corrections, review states, source coverage and application profile. Preserve identifiers and deprecation/migration mappings. Export assertion-level provenance and applicability in every format, with explicit missing values. Keep authoring origin, review approval, legal authority and confidence about facts as separate dimensions. PROV-O can support lineage across source, review and generation activities. \[S40]

For future training datasets, distinguish observed decisions, reviewed rule interpretations, model predictions and hypothetical outcomes. Record the knowledge available at the relevant time. Split evaluation by matter and time where appropriate, and exclude subsequent outcomes or reasons from earlier-stage features. Keep the historical frozen benchmark; create an independently reviewed new version for changed operational targets rather than silently changing its answers.

**Acceptance example.** A downstream consumer reproduces an answer or training example from an identified release, traces a correction, and excludes material outside its review/applicability profile. A data split check catches two records from the same matter crossing the train/test boundary.

### A12 Test the intended tasks including missing and conflicting information

**Priority: immediate evaluation redesign, alongside the first implementation slice.**

**Issue and evidence.** The existing competency questions, retrieval benchmarks and unit tests are useful, but mainly reflect the demonstrator and the information it currently holds. Successful query execution, graph connectivity or quotation matching does not establish that an examiner found the governing qualification, a customer understood an objection, or a scenario comparison is legally coherent. The first report's R06 and R09 remain the starting point. \[S34]

**Suggested solution.** Add expert-reviewed scenario fixtures and task-level expected answers. Specify required authorities, necessary qualifications, allowed conclusions, missing facts and required abstentions. Use independently reviewed expected results rather than treating generated answers as their own benchmark. Measure examiner time and missed material; customer comprehension and misplaced confidence; and scenario consistency and traceability. Evaluate the actual deployed retrieval/prompt/profile configuration.

Include at least these scenarios: multiple objections with different affected goods; the section 44 context bundle; two application dates separated by a transition; ambiguous everyday wording; conflicting sources; evidence covering the wrong period; a missing judgment; and a proposed amendment affecting an exception. Measure correct clarification or abstention as a successful result when the evidence is insufficient.

**Acceptance example.** Agree numerical targets after a baseline with examiners and customers. Regardless of the aggregate score, maintain explicit release-blocking fixtures for unsupported operative claims, wrong temporal applicability, and omitted outcome-changing qualifications. Report errors by task and severity so a high average retrieval score cannot hide a serious explanation defect.

## 7 Integrated ontology design

### Concept identity and hierarchy

Stable concept IDs, preferred and alternative labels, explicit not-labels, and separately recorded type judgements provide a useful vocabulary foundation. The current thin hierarchy is not itself a defect. A flat vocabulary can work well when its typed relations answer real questions. Adding broader links merely to make the graph look hierarchical would introduce weak semantics.

Retain the separation between a SKOS concept, a class used to classify concepts, a source passage, and an assertion about a concept. A concept labelled ground for rejection is an abstract legal idea; it is not an actual objection raised against an application. A future operational model should introduce case-level instances explicitly rather than reusing concept nodes as events or decisions.

The generated count of 53 empty classes should be interpreted carefully. It counts direct population in the inspected graphs; it does not establish that all superclass or schema terms are useless. Keep a small register identifying terms as populated, structural, or reserved for a specific future competency question. Deprecate terms without a credible use case, but do not populate classes merely to improve a count. \[S04, S05]

### Relations and legal meaning

The richer predicate vocabulary is an improvement over generic related links. Its next development should focus on semantic precision rather than additional names. For each legally consequential predicate, maintain a short statement of direction, permissible subject and object kinds, conditions, strength, examples and near misses. Eleven predicates currently appear only once, so their boundaries are lightly exercised.

Distinguish evidential support, legal requirement, discretionary power, procedural consequence and factual tendency. The exception examples show why these distinctions matter. A confidence number from the authoring model cannot substitute for a correct relation or a scoped proposition. Record expert disagreements as review issues rather than averaging incompatible interpretations.

SKOS broader expresses a concept hierarchy, not OWL subclassing. W3C SKOS also separates associative links from hierarchical links through integrity conditions. The repository's explicit checks are useful here. If a future release enables OWL semantics, review domain, range, disjointness, property types and equality behaviour under a declared profile; do not assume that familiar RDF vocabulary automatically creates the intended legal logic. \[S09, S21]

### Procedure and time

The current model contains useful process vocabulary and a small number of precedence and clock relations, including three authored `precedes` relationships and two `suspendsTimeFor` relationships. It does not yet represent a complete procedural workflow. That supports the original concept-navigation demonstrator, but is insufficient for reliable next-step guidance in the immediate customer use case.

For the immediate procedural explanation use case, start with one sourced process template: initial examination report, applicant response, reconsideration, further report or acceptance, and the relevant deferment or lapse branches. Regulations 4.8 to 4.10 provide a useful bounded starting point. Model the conditions and loops explicitly. Keep the template separate from any actual applicant's case events.

Keep three kinds of time separate: when a source was captured or changed; when a legal provision applies to a class of matters; and when a procedural event starts, pauses or ends a deadline. Content hashes address the first problem. A compilation date alone does not solve the other two. The clarified intended questions now require the basic applicability and event model. Implement historical selection and deadline calculation only for reviewed, supported branches, and retain explicit unknowns where the necessary rules or facts are missing. \[S05, S08, S20]

### Actors and roles

The explicit modelling of decision-makers, delegates, powers and control relationships is useful. Before introducing real people and organisations, distinguish the actor from the capacity in which the actor acts. A person can hold different capacities in different matters or periods. Global class disjointness should not accidentally make those situations contradictory.

A role-assignment record can connect a person or organisation, a role, a matter or institution, a time interval and the source of authority. Define this pattern with the minimal matter model now; it can be tested with fictional examples without introducing an operational case-data collection. \[S05]

### Maintenance and portability

The modular code, generated reports and pinned inputs support reproducibility. The most useful maintenance improvement is a common record and evidence interface used by exporters, browser views, dependency analysis and answer construction. R03 and R05 are symptoms of a new record type reaching some consumers but not others.

Refresh documentation from executable metadata where possible. For example, `graph/README.md` still describes an empty authored graph, and `eval/README.md` retains earlier statements about the gold stage and machine authorship. These statements conflict with the current implementation. A release manifest should identify the ontology revision, upstream snapshot, schema version, rule approvals and supported query scope. Public namespace publication and broader ontology alignment can wait until there is an external consumer with a concrete need. \[S23]

### Shared information model

The following is a proposed extension, not a claim about existing repository classes. It identifies the responsibilities to keep separate and the links that make the foundation reusable.

|Layer|Main objects|Links that matter|
|-|-|-|
|Source and authority|Instrument/version, passage, judgment paragraph, guidance version|Text anchors, provenance, authority, capture and effective dates|
|Meaning and norms|Concept, scoped definition, proposition, legal test, exception|Meaning, condition structure, source support, interpretation and applicability|
|Matter and process|Sign, application, goods/service item, report, objection, event, role assignment|Subject matter, affected scope, event history, responsibility and conditional transitions|
|Evidence and assessment|Evidence item, factual claim, assessment, argument|Supports/challenges, relevant time/scope, assessor, reasoning and unknowns|
|Explanation and scenarios|Claim, response option, visual view, baseline/proposal scenario|Claim-level support, missing facts, alternatives, versioned assumptions and differences|

Do not turn navigation edges directly into decision rules. Connect the layers through explicit, reviewed statements. This allows examiner search, public explanations and later analytical services to share a foundation while using different interfaces and execution policies.

## 8 Implementation roadmap

The practical next step is a narrow, complete vertical slice: explaining a report with two issues, including an evidence-of-use question, from the relevant legislation and guidance through to a sourced customer explanation. Section 41/44 examples are suitable candidates because they exercise different grounds, evidential questions and response paths. The legal content and expected outcomes of the fixtures should be reviewed by the relevant specialists.

|Stage|Concrete deliverable|Completion criterion|
|-|-|-|
|1. Repair current foundations|Address the first report's critical semantic/provenance issues; fix A06 and A08; revise permanent demonstrator restrictions|Complete context and claim support survive retrieval, export and display|
|2. Demonstrate the immediate use cases|Minimal matter, objection, process, applicability and evidence schemas; reviewed explanation objects; examiner/customer views|One realistic end-to-end scenario supports distinct objections, missing facts and conditional next steps|
|3. Establish dependable reuse|Task benchmark, versioned release manifest, source coverage register and consumer profiles|Another service can reproduce results and select permitted, applicable assertions without UI assumptions|
|4. Extend policy support|Complete dependency coverage and isolated baseline/proposal scenario execution|A proposed change produces traceable differences and explicit unknowns; proposals never enter operative output|
|5. Develop ML or automated decisions|Appropriate case data, reviewed labels, tested assessment methods and separate deployment controls|Prediction quality and decision validity are evaluated separately; every output retains its source and model lineage|

These stages need not be strictly sequential. Source improvements and customer testing can proceed while the domain model develops. The dependencies matter: reliable simulation needs applicability and structured tests; reliable case explanations need matter context and evidence; all of them need source and assertion provenance.

### Detailed work packages for foundation repair

The following eight work packages retain the original repair backlog, suggested owners, effort estimates and completion conditions. They support the broader stages above. The original end-of-work review plan concerns the demonstrator; reviewed operational profiles additionally require appropriate semantic review before relying on the material for their intended tasks.

The roles below are suggested owners, not existing commitments. Relative effort is an estimate of implementation breadth: small means a local change; medium crosses several consumers; larger requires sustained domain review or a new capability.

|No|Work package|Suggested owner|Relative effort|Done when|
|-|-|-|-|-|
|1|Correct the four exception records and three definition examples|Ontology author, followed by planned expert review|Small code change; substantive source reading|R01 and R02 acceptance checks pass and proposed readings preserve their sources|
|2|Repair evidence export and source closure|RDF and data-pipeline maintainer|Medium|All 230 definition anchors survive export and all source targets resolve as specified|
|3|Extend validation and correct RULE-0001|Validation maintainer|Small to medium|New negative fixtures fail and inference records match emitted conclusions|
|4|Unify change-impact dependency indexing|Data-pipeline and explorer maintainer|Medium|GD-only changes are detected and current and historical dependencies are distinguishable|
|5|Define semantic competency answers and condition handling|Ontology author and query maintainer|Medium|Expected propositions, qualifications and trust states are tested for supported questions|
|6|Make authority and coverage claims precise|Answer and documentation maintainers|Small to medium|Heuristic limits, graph coverage and source dates are visible and accurate|
|7|Prepare the end-of-work expert review pack|Project owner and domain reviewer|Larger review effort|Reviewer can inspect high-risk records in context and decisions remain separately recorded|
|8|Evaluate added value at the agreed milestone|Evaluation owner and domain reviewer|Medium to larger|Independent questions and source judgments test the current configuration against its baseline|

For the expert review, prioritise exceptions and negative relations, requirements and powers, temporal consequences, the new definition summaries, singleton predicates and the 21 unverified legislative bases. Then use a stratified sample across Parts, concept kinds and predicate families to detect systematic errors before deciding the depth of the remaining review. Add a stale-source prohibited-use example and complete the missing evaluation thresholds as part of this preparation.

The release decision should be tied to the claimed use. A research demonstration can show unreviewed material when its status and scope are explicit. A reviewed knowledge release needs recorded semantic review outcomes and meaningful question-level acceptance evidence. Case-specific procedural explanations require the process and applicability modelling in A01–A05 and A09, which now belongs in the immediate foundation work. Automated outcome guidance remains a separate capability requiring further modelling and validation.

### How the findings fit together

|Work area|Findings to implement together|Reason|
|-|-|-|
|Legal meaning and qualifications|R01, R02, R07, A03, A04|Correct the current statements while establishing scoped definitions, applicability and structured legal tests|
|Evidence provenance and reuse|R03, R04, A05, A11|Preserve source anchors and distinguish case evidence, assessed facts, review status and downstream labels|
|Change and policy analysis|R05, A03, A10|Repair dependencies before comparing temporal rule versions or modelling real-world effects|
|Retrieval and supported explanations|R06, R08, R09, R10, A06, A07, A08|Retrieve complete relevant sources, validate claim support and measure the actual configuration|
|Matter and customer experience|A01, A02, A05, A09|Explain separate objections, relevant evidence and conditional next steps through consistent prose and visuals|
|Evaluation and release decisions|R06, R09, R10, A11, A12|Combine semantic task tests, coverage, versioned releases and use-specific completion criteria|

## 9 Reproduction and evidence limits

### Original review environment and commands

The local review used Python 3.12.14, RDFLib 7.6.0, pySHACL 0.40.1 and pytest 9.1.1. Dependencies were installed from the repository's test and RDF extras. The repository was fetched at the reviewed commit, and its upstream fetch command obtained the pinned snapshot with digest verification.

Core checks used `python -m pytest`, `tmk-harness`, `tmk-graph --rules --check` and `tmk-ontology-report --check`. The committed N-Quads dataset was also loaded into RDFLib for direct inspection. The targeted mutations were confined to in-memory graphs; they were not written to the repository.

The definition mutation removed `tmk:authoredBy` and all `tmk:sourcePassage` values from the assertion URI ending in `GD-0001`, then called the repository's `ontology.validate.run`. The inference comparison extracted `assertionSubject`, `assertionPredicate` and `assertionObject` from every InferredAssertion and checked whether the resulting triple existed in the inferred graph. Five records failed that equality check, all produced by RULE-0001.

The authority probes called the existing `search.authority.conflations` function with controlled answer text and citation lists. They demonstrate limitations of the detector, not the frequency of those failures in generated answers. Coverage counts compare `upstreamRef` values in the source graph with chunk and page identifiers in the pinned corpus.

### Follow up probes and limitations

The follow-up used the same pinned upstream corpus and the newer repository revision. Section 44 offsets and source-object lengths were calculated using the repository's loader and passage renderer. The browser quotation checks called `Engine.verify` deterministically, including a real quotation that occurred in the full stored section 44 text but outside the supplied 1,600-character excerpt. These probes establish the specific implementation behaviours in A06 and A08; they do not measure their frequency in generated answers.

The original full-suite result and the follow-up explorer result must remain separate. Neither validates the capabilities proposed in A01–A12. The acceptance examples are recommended completion tests, and numerical task-performance targets should be agreed after a baseline with the intended users.

Public IP Australia pages and the cited standards were consulted during the reviews on 18 October 2026. External standards explain relevant modelling semantics or optional design patterns; they are not mandatory product requirements. All source references below retain their original revision or publication URL.

## 10 Source register

S01–S23 retain the original review's references. S24–S40 retain the supplementary review's references under a unified numbering scheme. The pinned repository links preserve the distinction between reviewed revisions. Record IDs and named functions identify evidence inside larger files. All source entries from both reports are retained.

### Original review evidence

* **S01** [Project README and scope](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/README.md).
* **S02** [Architecture](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/docs/ARCHITECTURE.md) and [decisions](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/docs/DECISIONS.md), especially ADR-0080, ADR-0109, ADR-0120, ADR-0122, ADR-0134 and ADR-0137.
* **S03** [Response to the earlier ontology review](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/docs/ONTOLOGY-REVIEW-RESPONSE.md).
* **S04** [Generated ontology report](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/data/derived/reports/ontology.md), reproduced during this review.
* **S05** [Draft ontology modules](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/3ecf410101c341a678be126ad85916b824aec482/ontology/draft).
* **S06** [Committed graph dataset](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/graph/dataset.nq) and [upstream contract](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/docs/UPSTREAM.md). Fresh measurements are described in this report.
* **S07** [Validation shapes](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/3ecf410101c341a678be126ad85916b824aec482/shapes) and [test suite](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/3ecf410101c341a678be126ad85916b824aec482/tests).
* **S08** [Authored relationships](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/authored/relationships.yaml), particularly GR-0206, GR-0319 and GR-0699 to GR-0702. These records include the precise source refs, quotes, offsets and hashes.
* **S09** [Predicate definitions](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/src/tm_knowledge/ontology/predicates.py).
* **S10** [Authored definitions](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/authored/definitions.yaml), particularly GD-0050, GD-0060, GD-0112, GD-0128, GD-0138 and GD-0146; [definition loader](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/src/tm_knowledge/authored/definitions.py).
* **S11** [RDF builder](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/src/tm_knowledge/ontology/build.py), especially `\_origin`, `\_build\_source`, relationship construction and `\_build\_definitions`.
* **S12** [Provenance shapes](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/shapes/provenance.ttl) and [inference shapes](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/shapes/inference.ttl).
* **S13** [RULE-0001 mixed authority](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/queries/rules/RULE-0001-mixed-authority.rq) and [RULE-0002 change impact](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/queries/rules/RULE-0002-change-impact.rq).
* **S14** [Explorer builder](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/src/tm_knowledge/explorer/build.py), particularly `stability`.
* **S15** [CQ-0009](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/queries/competency/CQ-0009.rq) and [CQ-0024](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/queries/competency/CQ-0024.rq).
* **S16** [Competency question records](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/eval/gold/competency-questions.yaml).
* **S17** [Answer authority detector](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/src/tm_knowledge/search/authority.py) and [prohibited uses](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/eval/gold/prohibited-uses.yaml), especially PU-0004.
* **S18** [Hybrid and ontology retrieval measurement](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/data/derived/reports/measure.md), scored at `a255063dbe1b` on 2,344 grades.
* **S19** [Browser reading measurement](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/data/derived/reports/measure-reading.md), scored at `d248c18271ed`; report distinguishes 2,219 pooled grades from 2,892 in its stored grade manifest.
* **S20** [Official Trade Marks Act series](https://www.legislation.gov.au/Series/C2004A04969) and [Trade Marks Regulations compilation 53](https://www.legislation.gov.au/F1996B00084/2025-12-18/2025-12-18/text/original/epub/OEBPS/document_1/document_1.html), especially regulations 4.8 to 4.10. Definition checks also use the repository's pinned Act section 11 and Manual Part 22.1 and Part 16.2 source records.
* **S21** [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/), especially semantic relations and integrity conditions; [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/); [Shapes Constraint Language](https://www.w3.org/TR/shacl/).
* **S22** [W3C note on n-ary relations](https://www.w3.org/TR/swbp-n-aryRelations/), an informative modelling pattern for assertions with additional participants or attributes.
* **S23** [Graph README](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/graph/README.md) and [evaluation README](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/3ecf410101c341a678be126ad85916b824aec482/eval/README.md).

### Follow up evidence and modelling references

* **S24 — Revision comparison and presentation changes.** [Changes since the first review](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/compare/3ecf410101c341a678be126ad85916b824aec482...e6985e9286c4a9f36befb8fbe82255fc94ecba01); [HANDOFF](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/docs/HANDOFF.md). Eight changed files; hierarchy and definition display changes.
* **S25 — Examination scope and roles.** [examination.ttl](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/ontology/draft/examination.ttl); [CLAUDE.md](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/CLAUDE.md). Process placeholders, outcome restriction and role disjointness.
* **S26 — Temporal model.** [time.ttl](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/ontology/draft/time.ttl). Point-in-time exclusion; compilation and capture metadata; hash-based staleness.
* **S27 — Relationship and definition contracts.** [gold-relationship.schema.json](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/eval/schemas/gold-relationship.schema.json); [definition.schema.json](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/eval/schemas/definition.schema.json).
* **S28 — Case evidence.** [evidence.ttl](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/ontology/draft/evidence.ttl). Unpopulated evidence classes and evaluative-proposition boundary.
* **S29 — Answer contract and rendering.** [bulk/jobs.py](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/src/tm_knowledge/bulk/jobs.py). `passage\_block`, `\_answer\_render`, `\_ANSWER\_INSTRUCTIONS`, `\_ANSWER\_SCHEMA`, `\_answer\_accept`.
* **S30 — Search and live explanations.** [search/index.py](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/src/tm_knowledge/search/index.py); [engine.js](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/site/js/engine.js); [ask.js](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/site/js/ask.js). `KeywordIndex`, `Systems`, browser `prompt` and `verify`, streamed and final answer display.
* **S31 — Authority and case coverage.** [authority.ttl](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/ontology/draft/authority.ttl). Citation-only decisions, authority categories, `statedIn` and `attributedTo`.
* **S32 — Existing change-impact rule.** [RULE-0002-change-impact.rq](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/queries/rules/RULE-0002-change-impact.rq). Recorded dependency scope and explicit limits.
* **S33 — Lineage and export architecture.** [provenance.ttl](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/ontology/draft/provenance.ttl); [ontology/build.py](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/src/tm_knowledge/ontology/build.py). Read with R03–R05 of the original review.
* **S34 — Evaluation scope.** [competency-questions.yaml](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/eval/gold/competency-questions.yaml); [queries/README.md](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/queries/README.md); [benchmark reports](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/e6985e9286c4a9f36befb8fbe82255fc94ecba01/data/derived/reports).
* **S35 — Customer process example.** IP Australia, [How to respond to an examination report](https://www.ipaustralia.gov.au/trade-marks/how-to-respond-to-an-examination-report), particularly response options, deferment and divisional applications.
* **S36 — Customer evidence example.** IP Australia, [How to provide evidence of use](https://www.ipaustralia.gov.au/trade-marks/how-to-respond-to-an-examination-report/how-to-provide-evidence-of-use), particularly section 41(3)/(4), dates and goods/services.
* **S37 — Legal-rule reference model.** OASIS, [LegalRuleML Core Specification 1.0](https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/legalruleml-core-spec-v1.0-os.html), sections 4.1–4.2 on normative effects, defeasibility and contextual qualification.
* **S38 — Temporal primitives.** W3C, [Time Ontology in OWL](https://www.w3.org/TR/owl-time/), section 3.1 and the vocabulary for intervals and instants.
* **S39 — Reproduced source-context example.** [Pinned upstream section 44](https://github.com/Thomas-Amann-IPAustralia/manual-XtrACTor/blob/308bfd9162ebea3e0213e6299516ee314d6f2eca/snapshot/legislation/TMA1995/provisions/pt4/TMA1995-s44.json); [TM-Knowledge pin](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/blob/e6985e9286c4a9f36befb8fbe82255fc94ecba01/data/pin.json). Counts and offsets were calculated from the local pinned snapshot, using the repository's loader and passage renderer.
* **S40 — Provenance reference model.** W3C, [PROV-O](https://www.w3.org/TR/prov-o/), entities, activities, agents and derivations.


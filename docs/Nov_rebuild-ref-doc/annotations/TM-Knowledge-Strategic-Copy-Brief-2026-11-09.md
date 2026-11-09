# TM Knowledge: strategic language and claims review

**Implementation brief for Claude Code**  
**Prepared:** 9 November 2026  
**Scope:** Public-facing TM Knowledge explorer at `site/`; editorial framing, navigation copy, page introductions, capability descriptions, trust language and supporting microcopy. No change to the underlying ontology, rules, graph, data, AI prompts or source quotations.  
**Reference revision:** `cd0e6571f6100f42b81c7ca00632c4ff79a7c784` on `main` when reviewed.  
**Inputs:** The supplied paper, *TM-Knowledge: Enabling Trade Marks Strategic and Operational Objectives* (365 lines); the published explorer; repository source and ADRs; existing copy guide, UX audit and after-action reports.  
**Decision requested:** An editorial refinement, not a new product proposition or wholesale copy rewrite.

> **Instruction to Claude Code:** Read `CLAUDE.md`, `docs/RULES-IN-FORCE.md`, the latest handoff and ADR-0138, ADR-0145, ADR-0148, ADR-0150, ADR-0151 and ADR-0152 before editing. Treat the **Recommended copy** in this brief as an editorial specification, not an instruction to change records or legal conclusions. First reconcile each recommendation against the branch you are working on. Where the wording is already changed, do not overwrite a newer correction. Implement the priority 0 and 1 items that remain appropriate, log substitutions and disagreements, and submit a diff and a brief after-action report for owner review. Do not merge or publish without the owner's decision.

## 1. Editorial verdict

**Keep the overall approach. Change the claims and the benefit explanations.** The present site is considerably clearer than its earlier iterations. It has three explicit audiences, a working demonstration for each, progressive disclosure of technical details, and unusually visible safeguards. The section 44 demonstration, **“One rule, from words to structure”**, is a strong explanation of the underlying method and should remain intact.

The attached paper makes a useful argument that is not yet fully apparent to a visitor: **the reusable asset is the structured connection between law, practice, concepts and processes**. A research answer, a customer explanation and an early list of guidance affected by a change are different uses of the same records. Maintaining that common foundation could, subject to review and integration, reduce duplicated work across later services. This is more substantive than a generic promise of “AI transformation”.

The paper is **a strategic rationale, not evidence that the benefits have occurred**. It repeatedly describes improved productivity, consistency, governance and customer outcomes as expected or immediate benefits. The website must not convert those proposals into demonstrated results. Today it is a **proof of concept with working demonstrations**; it is not a validated enterprise knowledge service, an operational Manual governance system, an automatic legal impact assessment or a customer-tested advice service.

**Editorial thesis to carry across the site:**

> TM Knowledge connects Australian trade mark law, examination guidance and related ideas in a structured, source-linked form. The current proof of concept shows how the same material can help people find relevant guidance, understand requirements and identify records to review when something changes. It also shows the limits of those demonstrations and what would be required before broader use.

The desired visitor reaction is not “this system has solved trade marks”. It is: **“I understand the problem this foundation addresses, I have seen one relevant thing it can do, I can inspect its sources, and I understand what is still unproven.”**

### The balance to strike

| Aspect | Preserve or strengthen | Avoid |
|---|---|---|
| Educational experience | One concrete question, example or action before the explanation of the technology | Opening with an ontology definition, standards catalogue or list of benefits |
| Asynchronous pitch | Name a practical job, show the present demonstration, explain the plausible value and the next dependency | Unqualified “faster”, “better”, “safer”, “consistent” or “trusted” outcomes |
| Technical integrity | Source passage, authorship, review status, law versus Manual, missing data and scope | A citation described as proof of correctness, or a record count presented as an impact score |
| Strategic positioning | A reusable knowledge **foundation** that might support several initiatives | A deployed, governed, enterprise-wide knowledge platform |
| Tone | Calm, useful, candid, technically precise, Australian English | “Supercharging”, transformational rhetoric, vague customer-centric slogans and future commitments disguised as roadmaps |

## 2. Evidence and claim boundaries

These distinctions are the most important instructions in this brief. They apply to headings, captions, illustrations, accessibility labels, tooltips, SEO descriptions and dynamically generated UI copy, not only prose paragraphs.

| Claim tier | What this project supports | Permitted formulation | Not yet justified |
|---|---|---|---|
| **A. Working demonstration** | Concept explorer; research assistant with saved questions and source-linked AI answers; fictional applicant explanations; dependency lookup; fictional GI what-if; rules representation | “This demonstration shows …”, “You can trace the records linked to …” | “This is ready for operational examination”, “it finds every relevant authority” |
| **B. Tested, narrow result** | Ranking of relevant passages in the research evaluation. On the current published overview: ontology-guided search is **7.9 nDCG points higher than keyword search** and **4.1 points lower than meaning-based/hybrid search**, with stated intervals, on the evaluated questions | “In this test, this method ranked relevant passages …” with **both comparators**, interval and benchmark caveats | “It saves examiners time”, “it is the best search”, “answers are more accurate”, “it improves decisions” |
| **C. Plausible operational value** | Easier discovery; fewer independent lookups; more visible provenance; clearer training links; better candidate lists for Manual maintenance | “Could reduce time spent looking for guidance; this has not been measured with examiners” | “Has reduced effort / improved consistency / increased quality” |
| **D. Possible future capability** | Manual governance workflows, alerts, approved expert knowledge, case similarity, report drafting, policy comparison, GI implementation support, analytics | “Could support, if the necessary sources, expert review, controls and evaluation are added” | “The foundation already delivers” these services |
| **E. Out of scope** | Final examination decisions, legal advice, predictions of outcomes, autonomous legal interpretation | “The system does not decide applications or replace examiner judgement” | Any suggestion that rules-as-code determines a real application outcome |

**Other non-negotiable distinctions**

1. The **Trade Marks Act 1995** and **Trade Marks Regulations 1995** are law. The **Trade Marks Manual of Practice and Procedure** describes examination practice; it is not law. Do not casually group them as equally authoritative “rules”.
2. A **quotation match** confirms that words occur in a source. It does not verify that the answer correctly interprets those words or that the source is current.
3. An AI-written relationship remains **unreviewed** until a named expert approves it. A source link, schema validation, or absence of a correction is not expert endorsement.
4. A dependency count is a count of **recorded links in this version**, not a measure of legal effect, change risk, cost, importance, implementation effort or completeness.
5. The geographical indications scenario is **fictional**, with policy questions written by AI and not reviewed. It does not apply an actual proposed law or model behavioural or economic impacts.
6. Public-facing examples use **invented matters** and have **not been formally tested with customers**. A publicly accessible proof of concept is not a production customer service.
7. “Current” means **current within the saved source snapshot** when that is what the tool uses. The site does not yet automatically maintain the latest law and Manual.
8. “Governance-ready” may describe a design intention; “governed” may only describe specific mechanisms demonstrably present, such as provenance and review-state separation. It must not imply completed institution-wide review and maintenance.

## 3. Translate the attached strategic paper into visitor value

The supplied paper has ten or more benefit themes, many overlapping. **Do not create a new top-level page for each.** Fold them into the three existing audiences and the shared-foundation narrative.

| Strategic theme from paper | Audience and practical question | Site today | How to communicate it honestly | Missing before a stronger claim |
|---|---|---|---|---|
| Research efficiency, examination quality | Examiner: “Where are the relevant law and Manual passages, and how do they connect?” | Concept explorer and AI-assisted research demonstration | **Show:** one concept, connected guidance and its source. **Value to test:** less searching, fewer overlooked references | Examiner task study, relevance/recall testing, citation review, comparison with normal workflow |
| Capability, onboarding, knowledge retention | New examiner: “How do I understand an unfamiliar legal issue?” | Concept definitions, relationships, test diagrams, fictional matters | **Show:** a guided path from term to legal test and Manual. **Potential:** learning aids and recorded expert interpretations | Training content review, learning tests, expert approvals, maintenance ownership |
| Manual revitalisation and governance | Manual owner: “What guidance might need re-reading after a change?” | Citation/quote-based dependency lookup and page amendment history | **Show:** an initial review list, with source paths and gaps. **Potential:** systematic triage and maintenance | Complete dependency coverage, version updates, owned review workflow, connected templates/training assets |
| Responsible AI and report-writing assistance | Service owner: “Can another tool retrieve the same identified authorities?” | Structured records, provenance, review states, cited response prototype | **Show:** multiple demos read one data foundation. **Potential:** source-grounded drafting aids | Expert-reviewed corpus, controlled prompts, security/privacy design, end-to-end accuracy assessment |
| Public understanding and service delivery | Applicant: “What does this objection mean, and what information matters?” | Invented objection, requirements and process explanations | **Show:** a step-by-step explanation with open uncertainties and source links. **Potential:** clearer comprehension | Customer usability/comprehension testing, legal expert review, real-world integration and approval |
| Geographical indications and regulatory reform | Policy officer: “Where might a new right intersect existing examination practice?” | Five-touchpoint fictional scenario | **Show:** existing records that might need review, and open policy questions. **Potential:** an earlier reform scoping exercise | Actual legislative proposal, broader source coverage, expert policy analysis and options evaluation |
| Data-driven continuous improvement | Operations/policy leader: “Can we compare the same concepts across matters or years?” | Common concept labels and record identifiers; no real case analytics | **Potential only:** consistent classifications for linked operational data | Real data permission, schemas, linkage, representativeness, statistical analysis and governance |
| Shared infrastructure / duplication | Executive: “Why build one foundation?” | Different demonstrations reading the same structured records | **Show:** one provision supports several audience journeys. **Potential:** reusable interpretations and less duplicated maintenance | Integration design, ownership, cost-benefit analysis and proof of reuse across actual services |

The single best executive example is not a list of strategic objectives. It is a **before-and-after work question** such as: “If section 44 changes, which records and Manual passages should someone check first?” Use the existing trace demo to answer the **narrow** question it can answer, then describe what a genuine policy impact assessment would still require. This is a credible bridge from operational utility to strategic purpose.

## 4. Recommended editorial rules for every page

1. **Lead with the visitor's job.** “Find guidance on an unfamiliar issue” is clearer than “use the semantic layer”.
2. **Put a demonstration next to the promise.** For each audience: problem → action → what the demonstration returns → what remains untested → a possible next step.
3. **Use one clear present/potential contrast.** Prefer “Working demonstration” versus “Possible future use” rather than repeatedly alternating “now”, “coming next”, “within reach” and “supercharging”. Existing horizon detail can remain within future cards.
4. **Name the output, not a mysterious capability.** “List records linked to a provision” is precise; “simulate legal consequences” is not true of the current website.
5. **Make benefits hypotheses until measured.** “Could help an examiner find relevant material” is allowed; “helps examiners work faster” suggests unobserved real-world use. “Faster” should be reserved for a properly measured time comparison.
6. **Quantify only what is counted.** “114 records linked to selected sources” is a count; “114 affected rules” or “114 impacts” would be a different, unsupported claim.
7. **Avoid universal words.** Replace unqualified “every”, “all”, “always”, “complete”, “guarantees”, “single source of truth”, “trusted” where the underlying implementation cannot establish them.
8. **Keep concrete nouns.** Act, Regulations, Manual, provision, record, legal test and quotation are useful. Explain “ontology”, “graph”, “predicate”, “inference” and “SHACL” on first use outside For nerds, or place them later.
9. **Avoid presenting the paper's organisational aspirations as endorsements.** The paper describes alignment with Trade Marks Division priorities. Do not imply the Division has adopted, commissioned or assessed the solution without a source that establishes it.
10. **Do not oversoften trade mark law.** Plain English is an orientation alongside source material. Preserve formal legal terms and qualifiers in the record, quoted provision and linked detail. No legal paraphrase should be introduced solely by an interface-copy change.
11. **Write in Australian English**, short sentences and active voice. Avoid em dashes in public copy. Use “trade mark” consistently; retain formal Act/Regulations/Manual titles where needed.
12. **Make uncertainty local to the claim.** A banner at the top cannot substitute for a note beside a speculative capability, unreviewed explanation or impact count.

### Terms to standardise

| Prefer | Use for | Avoid unless technically necessary |
|---|---|---|
| **Knowledge foundation** | The common source-linked representation, once introduced | “Enterprise platform”, “single source of truth”, “trusted knowledge layer” |
| **Knowledge map** | The visible graph of ideas and their links | “Ontology” on audience landing pages |
| **Record** | An individual concept, relationship, definition, rule or other explicitly represented item | Unexplained “node”, “triple” |
| **Recorded link** | What the index can actually trace | “Dependency” when readers may hear causal or legal necessity |
| **Possible change to review** | The result of trace/scenario work | “Impact”, “consequence”, “effect” without qualification |
| **Working demonstration** | Present proof-of-concept feature | “Live service”, “production tool”, generic “working now” when this could imply readiness |
| **Possible future use** | Illustrated capability not built as a user-facing service | “Coming next”, “on the roadmap” without approval |
| **Source quotation** | A retrievable extract from legislation or Manual | “Verified answer” |
| **AI-written · not reviewed by a trade marks expert** | Provenance status | “Validated”, “approved”, “trusted” |
| **Question for policy review** | Fictional scenario output | “Simulated policy outcome” |

Do not change canonical concept labels, legal predicates or authored records to match these editorial preferences. Apply them to surrounding UI descriptions and explanations only.

## 5. Priority 0: correct the remaining high-risk implications

These edits are more important than stylistic polish. **The existing safeguards stay.** A replacement should be rejected if it makes the site sound more certain than the current text.

| Route / source location | Current wording or pattern | Recommended replacement | Why / implementation note |
|---|---|---|---|
| `#/` · `site/js/home.js` · foundation heading | “Build it once, use it for every tool” | **“One foundation, several possible uses”** | The platform is not integrated into every future tool. Keep the interactive selector, including separate working/future groups. |
| `#/` · `home.js` · explanatory callout | “By making the rules explicit, every tool built on them can explain itself” | **“Shared records can make a tool's sources easier to inspect”** | Explicit structure enables source trails, not guaranteed explainability or answer correctness. |
| `#/` · `home.js` · callout paragraph | “An answer, an explanation or a flag can always show … That is what would let future AI tools give a traceable account of their output.” | “The demonstrations link their outputs to recorded concepts, rules and source passages. A future tool could reuse those links to help a person inspect the material behind an output. That would still need testing for accuracy and completeness.” | Avoid “always”; distinguish provenance from correct reasoning. |
| `#/examiners` · `site/js/examiners.js` · H1 | “Find the law and the guidance faster, and see how it fits together” | **“Find relevant law and examination guidance, and see how they connect”** | Time saving has not been measured with examiners. |
| `#/examiners` · `examiners.js` · future H2 | “Supercharging experienced examiners” | **“Possible tools for more complex examination work”** | Removes promotional promise. Keep future cards and their dependencies. |
| `#/direction` · `site/js/direction.js` · lead | “The Act, the Regulations and the Manual depend on one another in ways no one can hold in their head.” | “Trade mark law and examination guidance refer to many related provisions, concepts and procedures. A change to one source may mean other material needs review.” | The Manual is not a legal foundation on which the Act depends. Remove unsupported universal statement about cognitive limits. |
| `#/direction` · `direction.js` · promise | “Every dependency is traceable” | **“Recorded links can be followed back to their sources”** | There are unrecorded and ambiguous links. |
| `#/direction` · `direction.js` · demo card | “See every record that rests on it …” | “See records this version links to the selected provision or Manual page, directly or through recorded citations.” | The count is bounded by model and snapshot. |
| `#/change` · `site/js/change.js` · lead | “See every record in the knowledge foundation that rests on it … If it changed, these are what would need re-reading first.” | “See the records this version links to that source, including links through Manual passages. This is a starting list for checking what might need updating; it is not a full impact assessment.” | Do not claim an exhaustive or prioritised legal review list. |
| `#/whatif` · `site/js/whatif.js` · micro-heading | “New right impact modelling” | **“Explore a fictional policy scenario”** | Current feature is question and dependency mapping, not impact simulation or measurement. |
| `#/whatif` · `whatif.js` · count labels | “records to re-read first, and … after them” | **“records linked directly to the selected sources, plus … linked through Manual citations”** | Sequence is only a suggested review order, not assessed urgency. Keep the exact distinctions and any technical details in the expanded view. |
| Global future cards · `site/js/{examiners,public,direction}.js` | “Coming next” | **“Possible future uses”** | An ideas catalogue is not a delivery commitment. The existing “possibilities, not commitments” qualification remains. |
| Shared horizon · `site/js/illustrations.js` | “Within reach · Could be built on the foundation as it stands” | **“Builds on current work · Would need further development and review”** | Expert review and integration remain needed even if a prototype has the necessary entities. Preserve the “Needs more data” category, with a clear definition. |

**Important:** Some current wording already makes the right distinctions. Keep “A matching quotation shows where the words come from, not that the answer is right”, “Counts are links, not importance or risk”, the “no recorded dependency” warning, and the neutral **recorded: met / recorded: not met / not known** state language. Those were hard-won corrections under ADR-0152.

## 6. Priority 1: make the purpose worth caring about

These are ready-to-use blocks for each entry page. They add specific relevance without making benefits into results. Where headings are protected owner choices, the main proposal changes the **supporting language**, not the heading.

### 6.1 Overview `#/`

**Preserve the owner-chosen H1:** “Trade mark law and guidance, turned into rules and code”. Also preserve the section 44 **“One rule, from words to structure”** demonstration, its data and its visual explanation. The headline may be tested later, but changing it now is not necessary to make the page more persuasive.

**Replace the hero lead (`site/js/home.js`, `.ld-copy .lede`) with:**

> Trade mark decisions draw on legislation, examination guidance and the way legal ideas connect. TM Knowledge records some of those connections in a form people and software can inspect. This proof of concept shows three ways those records could be useful: finding relevant guidance, explaining requirements and identifying material to review when something changes.

**Why:** It starts with the information problem and gives a reason to explore each audience path. “Records some” is intentionally narrower than “a structured model of the rules” over the entire corpus. The short source paragraph and law/Manual distinction immediately below should stay.

**Replace** the eyebrow “Discover what it might enable” over the audience doors with **“See the demonstrations”**. **Replace** “One foundation, three groups it can serve today” with **“Three questions, one shared foundation”**. Suggested accompanying line:

> Each path starts with something you can try. It also shows where a similar tool might be useful later, and what would need to be checked or built first.

**Replace the three audience door titles and their short benefits only:**

| Door | Title | Working demonstration summary | Future summary |
|---|---|---|---|
| For examiners | **“Find and connect relevant examination material”** | “Follow a legal idea to related concepts and source passages. Try an AI-written research answer and check its quotations.” | “Potential: guided learning, better-managed knowledge and tools that surface related matters.” |
| For the public | **“Understand requirements, objections and next steps”** | “Explore fictional applications to see the legal questions, the examination process and what remains uncertain.” | “Potential: customer-tested guidance linked to an applicant's own stage or report.” |
| For direction setting | **“See what may need review when the system changes”** | “Trace recorded links from a provision and explore questions raised by a fictional new right.” | “Potential: maintenance workflows, option comparison and broader policy analysis.” |

These summaries replace promotional phrases such as “get the most out of it”. They do not require additional UI sections. Keep the three audience choices immediately below the first screen.

**The shared foundation panel:** Change its H2 as in priority 0. Its introductory paragraph could become:

> The demonstrations use the same source-linked records. That is the reason for making a shared foundation: different tools can draw on the same definitions and relationships, while the provenance and review status travel with them. Reuse across operational services is a possible next step, not something tested here.

**Do not introduce enterprise cost savings or ROI claims** in this panel. A shared model is a credible architecture argument, not proof of lower maintenance cost.

**The trust section:** Keep the five checks and “What still needs work”. In its introduction, prefer **“What you can check, and what remains untested”** to “Can it be trusted?” if the owner accepts the tonal shift. This is optional because the existing sceptical framing is effective. Keep all actual warnings. Consider changing “Each statement is linked to its source” to **“Source links are shown, but they do not prove an answer is correct”** only if the existing explanatory paragraph is retained. No trust panel should be deleted to make room for sales copy.

### 6.2 Examiners `#/examiners`

**Recommended H1:** “Find relevant law and examination guidance, and see how they connect”.

**Replace the lead with:**

> Examination often involves checking more than one source: what the Act or Regulations require, what the Manual says about practice, and how the legal issues relate. Here you can follow a concept to its recorded connections and source passages, or try a research answer that shows its quotations. These are working demonstrations, not an assessed replacement for an examiner's normal research or judgement.

**Working section H2:** “Explore an issue and check the sources” (instead of “Helping new examiners find their way”). Suggested one-line subcopy:

> Start with a legal concept or a question. The value to test is whether this makes relevant material easier to find and review.

**Concept explorer card:** Keep examples of distinctiveness, deceptive similarity and honest concurrent use. Change the final benefit list to focus on what is inspectable now: linked sources, other terms and nearby concepts, conditions attached to relationships. Avoid “everything connected to it” if scope means “everything this version records”.

**Research assistant card:** Keep the explicit quote-matching caveat. Add a short sentence, preferably near the action:

> The answer is AI-written and unreviewed. Open its sources and check whether they support each statement.

**Future section H2:** “Possible tools for more complex examination work”. Its first three visible cards should prioritise: (1) evidence/guidance discovery, (2) knowledge change management, (3) recorded expert interpretations and learning support. Related-matter and consistency tools must remain in **Needs more data** because the current foundation has no approved real examination records. If the current ordering changes, keep the cards' underlying limitations and do not expand the visible catalogue beyond three.

**Potential added future card (only if it replaces, not adds to, an overlapping card):**

> **Manual review and guidance consistency**  
> *Possible future use.* Flag passages that may overlap or depend on changed provisions, so a Manual owner can decide what needs updating. **Builds on:** the current record links and amendment history. **Still needs:** expert-reviewed relationships, scheduled source updates, an ownership and approval process, and a method for detecting conflicting guidance.  
> This consolidates the supplied paper's Manual revitalisation and knowledge-governance theme. Prefer this to a second, near-identical change-alert card.

### 6.3 Public `#/public`

**Recommended H1:** “Understand trade mark requirements and what happens during examination”.

**Replace the lead with:**

> An applicant may need to understand a legal requirement, an objection from an examiner or the next step in the application process. These fictional examples show how the same source-linked rules can be explained one step at a time, with the facts, judgements and unknowns kept apart. They are not advice about a real application and have not been formally tested with customers.

**Replace generic promise “get the most out of the system”.** The benefit hypothesis is **understanding**, not registration success, avoidance of objections or better case outcomes. A future customer study could ask whether people can explain the objection in their own words and identify appropriate sources or questions to ask. The present demo does not establish those results.

**Keep** the three demonstrations: objection, legal requirements, application journey. Keep the explicit section **“What we may test with customers”** and its requirements for expert review, invented matters and owner approval. Do not reframe these as product launch tasks already approved.

**Future assistant card:** Change “a conversation that explains” to **“A possible conversational guide that could explain”** and ensure the “Still needs” field includes expert review, customer testing, appropriate operational controls and permission before any real application data is used. Keep the low-confidence and unknown-facts behaviour visible.

### 6.4 Direction setting `#/direction`

**Keep H1 if desired:** “Find what a legal change might affect”. It is now cautious. The lead can do much more explanatory work.

**Replace the lead with:**

> A change to legislation or examination practice can require other material to be reconsidered. The first task is to find the connections: which records cite the source, which Manual passages refer to it, and which legal questions might follow. This proof of concept produces starting points for review. It does not determine the legal, operational or customer consequences of a policy choice.

**Replace the working-section title** “Two ways to see what a change might touch” with **“Two starting points for reviewing change”**. Proposed description:

> Trace existing source links, or use a fictional policy scenario to reveal questions and material a team might examine. Neither is a complete policy impact assessment.

**Retain** the six-bar provision chart, its denominator and the explanation that links are not importance or risk. The actual number of links gives a useful sense of scale, but not the number or severity of flow-on effects. **Do not call the fictional what-if “simulation” in the current-feature label.** “Scenario mapping” or “policy questions and linked guidance” is accurate.

**Reframe future cards around a believable maturity sequence:**

1. **Identify material for review**: working now, citation and quotation based, incomplete.
2. **Compare draft options**: possible next, requiring explicit change representations and reviewed policy assumptions.
3. **Understand outcomes**: longer-term research requiring operational data, behaviour models, cost/time analysis, legal and subject-matter validation. Do not imply a graph alone can predict these outcomes.

**Suggested replacement for the future section H2:** “From a list of links to better-informed policy choices”. Supporting paragraph:

> A review list can help a policy team ask better questions. Comparing options, estimating effort or anticipating changes in behaviour would require additional evidence and methods beyond this knowledge map.

This is the heart of the asynchronous pitch: valuable direction without claiming predictive powers.

## 7. Priority 1: detailed-page edits

These are targeted adjustments. Do not repeat the audience-page pitch at the top of every detail page. Each detail page should tell the reader **what to do, what they will see and what it cannot establish** in roughly two to four sentences.

| Route | What to retain | Recommended title / introduction / microcopy change | Source |
|---|---|---|---|
| `#/concepts` | Bow-tie diagram, predicates' exact labels, connection provenance, concept states and tests | Current “what the foundation records about it” is sound. Where it says “what overcomes it”, prefer “which recorded exceptions or other issues may be relevant” **only in generic descriptive UI**. Avoid implying a generic connection resolves a legal objection. Add a short caption: “These are recorded links, many AI-written and unreviewed; they are not a complete checklist for an examination.” | `site/js/concepts.js` |
| `#/ask` | Answer-first hierarchy, source separation, claim-by-claim quote checks, “Why these sources?” folded, sample questions | Replace “You get … the legal test your question reaches” with “Where the records contain one, the page also shows a related legal test.” Avoid promising a matching test for every question. Preserve the explicit caveat that a matching quote does not validate the answer. | `site/js/ask.js` |
| `#/customers/objection` | Fictional example, six-step structure, one-case default, neutral recorded-state marks, uncertainties | In any preview/button that says “Explain my objection”, prefer “Walk through a fictional objection” unless the copy immediately clarifies it is a made-up case. Keep the distinction between a report's statements, the invented case facts and the tool's own unknowns. No “likely to succeed” language. | `site/js/customers.js`, `site/js/public.js` |
| `#/customers/requirements` | Full conditions, effects, exception wording and source provisions | Intro: “See how selected sections of the Act have been set out as conditions, possible exceptions and actions. These representations are AI-written and unreviewed. They are not a determination of any application.” Do not say “the law requires” in explanatory prose where it might imply complete coverage; it can remain a navigation label. | `site/js/customers.js` |
| `#/customers/process` | Interactive journey, condition-dependent branches, actor labels, no deadline calculation | Intro: “Explore one general path through the application process. Your application's path may differ, and this demonstration does not work out deadlines or predict an outcome.” Keep “may proceed to” language on the branches. | `site/js/customers.js` |
| `#/change` | Counts-first layout, ripple, source list, ambiguous citations, optional guess, Manual history | Lead replacement in §5. In summary, “may need checking” is correct. Keep “a starting list for review, not a measure of legal impact, risk or effort”. Where a count includes automatically matched names, label that separately from quote/citation-based records. Prefer “Review recorded links” to “See all effects”. | `site/js/change.js` |
| `#/whatif` | Fictional premise above line, existing records below, five touchpoints, unanswered questions, unknown behavioural effects | Change generic “New right impact modelling” to “Fictional policy scenario”. Add one orienting sentence near the graph: “Select a question to see today's related passages and the issues a policy team would have to investigate.” Make count labels explicitly about **linked records**. Retain the no-draft and no-behavioural-evidence warnings. | `site/js/whatif.js`, `site/js/direction.js` |
| `#/nerds` | Four-step foundation explanation, standards, map, tables and results | Existing opening largely works. Replace “everything … is built from what is described here, and nothing is hidden” with “This section describes the records and methods behind the demonstrations, along with their known limits.” Avoid an unverifiable absolute. | `site/js/nerds.js` |
| `#/how` | Nine-step search walkthrough, example question | The existing “A search, step by step” scope is accurate. Add “This is one example of the research search, not a description of every capability the foundation might support” only if the current text is not already doing so. Do not broaden to an all-purpose “How everything works”. | `site/js/how.js` |
| `#/map` | Whole graph as interactive technical exploration, shapes/key, size-is-not-importance note | Keep. Add one concise note near the map key: “The map displays recorded relationships; it does not assess whether an interpretation is legally correct.” Keep its existing data-specific counts. | `site/js/map.js` |
| `#/rules` | “may”/“must” distinction, conditions, exceptions, technical detail | Keep the page. Where an introduction says “the tool records those parts separately”, make clear it is **selected represented rules**, not all provisions. No new legal paraphrase outside record-backed data. | `site/js/rules.js` |
| `#/standards` | Open standards and actual graph fragments | Current copy is sufficient. Do not add promises of interoperability, government adoption or standards compliance beyond the actual conformance checks. Consider adding: “Other systems would still need integration and governance work to reuse these records.” | `site/js/standards.js` |
| `#/table` | Technical lists, downloadable CSV, review status, exact source refs | Keep descriptions neutral: “browse records” rather than “browse authoritative knowledge”. Ensure source passage, AI explanation and signed assertion remain visibly distinct. | `site/js/table.js` |
| `#/about` | Balanced result, intervals, limitations, authorship and exact source snapshots | Retain the substantive two-way performance comparison and benchmark limitations. Consider H1 **“What the prototype has shown, and what it has not”**. Place a one-sentence note above evidence: “These tests measured retrieval ranking, not examiner time saved, decision quality or customer understanding.” | `site/js/about.js` |
| `#/glossary` | Plain-language definitions alongside technical names | Keep. Add or verify short entries for “working demonstration”, “recorded link”, “source quotation”, “review status” and “policy scenario” **only if glossary entries are UI-only and do not create unsupported ontology records**. | `site/js/glossary-view.js`, `site/js/glossary.js` |

### Global header, footer and metadata

- `site/index.html`: keep the prominent **Proof of concept** strip, authorship and testing warnings, title and audience navigation. The current five-part IA is an owner decision; do not propose another top-level menu in a copy pass.
- Consider replacing the footer's generic one-sentence proposition with: **“A proof of concept connecting Australian trade mark law, examination guidance and related concepts so their sources and relationships can be explored.”** Keep its separate explanation that the Manual is practice rather than law.
- Suggested meta description: **“Explore a proof of concept linking Australian trade mark law and examination guidance. Try research, fictional applicant explanations and change-tracing demonstrations, with sources and limits shown.”**
- Keep the owner-chosen labels **For direction setting** and **For nerds**, with “policy and strategy” as a clarifying subtitle. Do not rename sections without explicit author approval.
- Maintain consistency in `site/js/layers.js`, `site/js/illustrations.js`, shared component labels and the footer if a section caption changes. Do not change canonical legal terms or router addresses merely to make surrounding copy consistent.

## 8. Proposed self-contained executive explanation

**Use this only in an appropriate progressive-disclosure area**, such as the shared foundation panel or a compact “Why this matters” disclosure. Do not add a large new section to the first screen.

> **Why make a shared knowledge foundation?**  
> The same provision can matter to several jobs. An examiner may need to find the guidance that interprets it. An applicant may need a plain-language explanation of the issue. A policy officer may need to know which records to check if it changes.  
>  
> TM Knowledge connects these references in one structured model, with their sources and review status attached. The current website demonstrates those three uses. If the records are reviewed, kept up to date and connected to operational systems, the same foundation could support further services without each one starting its knowledge model from scratch. Whether that actually saves time or improves outcomes remains to be tested.

This conveys the strategic paper's strongest argument while retaining the distinction between an architecture hypothesis and measured organisational benefit. Prefer this to a table claiming alignment with every strategic objective.

### A short, truthful pitch paragraph for a non-technical visitor

> TM Knowledge is an early attempt to make trade mark law and examination practice easier for people and software to explore together. It shows how a shared set of source-linked records might support examiner research, applicant explanations and the first stage of policy change review. The demonstrations work, but much of the content is AI-written and unreviewed, most benefits have not been measured, and the system does not make legal decisions.

This paragraph can inform future external descriptions, but do not silently publish it as an agency-endorsed statement.

## 9. What **not** to import from the strategic paper

The paper is valuable for identifying use cases. The following claims would oversell the present project if copied into website copy without new evidence:

| Paper language / implication | Editorial treatment |
|---|---|
| “Single, governed knowledge model” / “trusted knowledge layer” | A **source-linked model with provenance and review mechanisms**, but most AI records are unreviewed and ongoing maintenance is not established. |
| “Immediate operational benefits”, “faster”, “improved consistency”, “reduced research effort” | **Benefits to evaluate** in an examiner study. No examiner productivity or consistency test has been established by the repository's measured retrieval ranking. |
| “Improves reliability of AI outputs” | **May help a reviewer locate supporting sources**. Quotation existence is not a legal or factual correctness test. |
| “Identify duplicate or overlapping guidance” and “highlight content requiring review” | **Possible Manual governance use**; current link tracing is a narrower proof of concept, not a validated inconsistency detector. |
| “Manage change in a controlled and transparent manner” | Current site can **list linked records to consider**. Actual governance needs source updates, ownership, approvals and complete asset mappings. |
| “Customer information can be more transparent and easier to maintain” | A plausible design aim; existing public explanations are **fictional and untested with customers**. |
| “Supporting GI implementation” | A fictional all-goods GI scenario poses questions; it is **not** an approved implementation design or assessed reform proposal. |
| “Enhanced analytics capability” | The ontology may give shared categories to future linked operational data; the graph **does not itself provide** quality, productivity or economic analytics. |
| “Future report-writing solutions” | A possible later integration, dependent on reviewed content and testing; **not a feature demonstrated today**. |
| “Reusable enterprise knowledge platform” | Architectural ambition, not current deployment status. “Foundation that could be reused” is sufficiently strong. |

## 10. Implementation map for Claude Code

| Priority | Main files | Requested work | Boundary |
|---|---|---|---|
| **P0** | `site/js/home.js`, `examiners.js`, `direction.js`, `change.js`, `whatif.js`, `illustrations.js` | Correct absolutes, unmeasured speed/quality claims, “impact modelling”, future certainty | No changes to counts, tests, evidence spans or scenarios |
| **P1** | `site/js/home.js`, `examiners.js`, `public.js`, `direction.js` | Add clear audience value, using the ready-to-use leads and door summaries above | Preserve IA, hero animation, interaction logic, disclaimers |
| **P1** | `site/js/{ask,concepts,customers,nerds,about}.js`, `site/index.html` | Specific local caveats and bounded descriptions; align footer and SEO | Do not re-author legal content or alter explanation objects |
| **P2** | `site/js/{map,rules,standards,table,how,glossary-view,glossary}.js`, `site/js/layers.js` | Light cleanup and terminology consistency | Technical pages may remain technical; avoid needless changes |
| **P2, optional** | `site/js/{examiners,direction}.js`, `site/js/illustrations.js` | Consolidate overlapping future cards; add a more explicit Manual governance story without increasing card count | No feature addition; no implied commitments |

**Safe scope:** Copy and labels in `site/`. Do not edit `authored/`, `ontology/`, `graph/`, `scenarios/`, `src/tm_knowledge/explain/`, prompts, approved/reviewed records, source snapshots or generated `site/data/` as part of this editorial task. Some display copy may live in builders; if changing it would alter record content or legal assertions, report it as a follow-up instead of patching it silently. Existing legal quotations and their provenance remain byte-for-byte unchanged.

### Recommended work sequence

1. Inspect the current branch and audit each proposed “current wording” against the actual source. **Do not blindly apply this brief to an older or newer revision.**
2. Implement P0 corrections and inspect every affected view, including cards, hover text, accessibility labels and mobile/narrow layouts where applicable.
3. Implement P1 audience leads and the shared-foundation explanation. Preserve owner decisions and the first-screen interaction flow.
4. Make P2 refinements only where they eliminate a real inconsistency. Fewer, clearer words are preferable to a new layer of sales material.
5. Run the normal site build and relevant tests; update literal-text assertions only when they still test the same safeguard, not merely to make a failure disappear.
6. Provide a compact change log: implemented, modified or declined recommendations, each with reason and route. Highlight every claim whose factual basis requires owner/expert validation.
7. Stop before merge, publication, changed legal meaning, changing permitted model outputs, or exposing real customer data. Those remain owner decisions under `CLAUDE.md`.

### QA checklist

**First-time reader comprehension**

- [ ] Without opening For nerds, a reader can say **what the foundation connects**, **why that might matter**, and **what is working today**.
- [ ] Each audience lands on a relevant problem and has one clear demonstration to try.
- [ ] The first screen does not become a corporate strategy catalogue.
- [ ] The section 44 “One rule, from words to structure” demonstration remains legible, interactive and substantively unchanged.

**Accuracy and evidence**

- [ ] No page claims time saving, quality uplift, consistent decisions, improved customer outcomes or enterprise reuse as **observed results**.
- [ ] Any retrieval measurement is tied to the assessed questions and includes the **keyword and meaning-based comparisons**, intervals and limitations.
- [ ] All AI-written content still shows authorship and expert-review state; approved and unreviewed states remain distinct.
- [ ] Every description of a verified quotation is restricted to **word matching/source traceability**, not accuracy of legal interpretation.
- [ ] Law and examination practice stay separate everywhere, including examples, tooltips and source drawers.
- [ ] Change counts are clearly **recorded links in a snapshot**, not legal impacts or risk scores; empty results are **not** “no impact”.
- [ ] A fictional GI scenario asks policy questions but does not predict legal effects, user behaviour or operational costs.
- [ ] No new paraphrase changes “may” to “must”, erases a condition or exception, or changes a legal assessment into an automatically decidable fact.

**Content and behaviour**

- [ ] “Working demonstration” and “possible future use” are distinguished, with required work visible on future cards.
- [ ] Audience page titles, cards, linked headings, site navigation, breadcrumbs, metadata and footer use consistent language.
- [ ] No “every”, “always”, “complete”, “trusted” or “impact simulation” survives in an unqualified capability claim.
- [ ] The three public examples remain clearly fictional; no real case deadline or outcome is calculated.
- [ ] The original controls, routes, deep links, counts, data downloads and diagrams still work.
- [ ] Source citations, labels, reviewed-state badges, provisions and generated values are not changed merely for tone.
- [ ] Keyboard focus, screen-reader labels and long replacement headings are checked on key interactions; reduced-motion behaviour remains.

### Suggested verification commands

Follow the repository's current `CLAUDE.md` and development instructions. As relevant, use:

```bash
git diff --check
node --check site/js/home.js
node --check site/js/examiners.js
node --check site/js/public.js
node --check site/js/direction.js
node --check site/js/change.js
node --check site/js/whatif.js
python -m pytest -q tests/unit/test_explorer.py tests/unit/test_whatif.py tests/unit/test_dependencies.py
```

Run the project's actual site generation and Chromium route checks as specified in `docs/HANDOFF.md` and `site/README.md`. Tests should preserve legal/provenance safeguards, not turn into brittle assertions for marketing phrases. Inspect both static and expanded or selected states.

## 11. Decisions to put back to the owner

The remaining decisions are not blockers to most edits:

1. **Homepage H1:** I recommend **keeping** “Trade mark law and guidance, turned into rules and code” and strengthening the sentence beneath. A more user-led headline such as “One source-linked foundation for three trade mark questions” can be tested later. The current phrase is an explicit owner choice, reinforced by the section 44 demonstration.
2. **Sceptical trust headline:** Keep “Not blindly, and it never asks you to” unless the owner prefers the more functional “What you can check, and what remains untested”. Both are reasonable. Do not remove safeguards as a side effect.
3. **Manual governance as a fourth story:** I recommend **not** creating a fourth primary audience. Manual owners fit under examiners and policy/strategy; an optional future-use card or a link from Trace a change is enough until there is a validated governance workflow.
4. **Strength of external performance claims:** The current two-way test result should remain in the results section, with its limits. Whether those figures become claims in wider executive or agency communications is the owner's decision.
5. **Testing desired benefits:** If the aim is eventually to claim reduced time, improved comprehension or more consistent work, commission small, task-based evaluations with representative examiners, applicants and Manual owners. The present paper is a useful hypothesis list for that study, not its conclusion.

## 12. Definition of done

The language pass is successful when a first-time visitor can answer five questions without relying on a pitch meeting:

1. **What is it?** A source-linked, structured proof of concept about Australian trade mark law and examination practice.
2. **Why would I care?** It demonstrates a task relevant to my role: finding guidance, understanding an objection, or identifying recorded links for policy review.
3. **What can I actually try?** A working demo, with a clear action and inspectable sources.
4. **What should I not assume?** That the AI is expert-approved, that citations establish correctness, that counts predict impacts, or that the system decides a case.
5. **What could it become?** A reusable basis for further tools, if the content is reviewed, maintained, integrated and tested for the outcomes the project hopes to improve.

**Bottom line:** The strongest pitch is the working proof of a common, traceable knowledge model used in several distinct ways. The strongest editorial change is to tell that story plainly, and then be equally plain about what the demonstrations do not yet prove.

---

## Sources inspected and context for this brief

- Supplied attachment: *TM-Knowledge: Enabling Trade Marks Strategic and Operational Objectives*. Treated as a proposal for benefits and strategic alignment, not independent validation.
- Public explorer: <https://thomas-amann-ipaustralia.github.io/TM-Knowledge/#/> and its policy/direction page, observed 9 November 2026.
- Source repository: <https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/tree/main>, inspected at `cd0e6571f6100f42b81c7ca00632c4ff79a7c784`.
- `CLAUDE.md`; `docs/DECISIONS.md`, especially ADR-0138, ADR-0145, ADR-0148, ADR-0149, ADR-0150, ADR-0151 and ADR-0152; `docs/HANDOFF.md`.
- `docs/feedback-inbox/TM-Knowledge-copy-guide.md` and `docs/feedback-inbox/2026-11-09-ux-audit-after-action-report.md`.
- The existing `site/js/*.js`, `site/index.html` and current browser-visible wording. The published pages and repository wording were checked against each other on the overview and direction pages.

**Review limitation:** This is an editorial and claims assessment, not a legal expert review, a user study, or a full runtime test of every site route. The document deliberately avoids introducing new interpretations of provisions or changing any authored legal content.

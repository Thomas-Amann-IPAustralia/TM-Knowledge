# Ontology review response

**As at:** 2026-10-16 · session S035 · responding to `docs/Trade Mark Ontology Review-15.10.md`
(written by ChatGPT, dated 15 October 2026, about commit `6a75eef`)
**Checked against:** `fce501f`, which differs from the reviewed commit only by the review file,
with the pinned snapshot `c490a9927f1a`
**Written by:** an agent (Claude Code), at the owner's request. Machine-written and reviewed by
no one; every judgement in it is the agent's and can be wrong.
**Changed:** nothing. No record, graph, query, prompt or page was edited, and no paid model call
was made. Every number below was re-run in this session, with the library versions ChatGPT used
(rdflib 7.6.0, pySHACL 0.40.1, owlrl 7.6.2).

The task: for each problem ChatGPT identified, say whether it is right; where it is, say whether
its proposed fix is right; and where the fix is wrong for this project, say what should be done
instead, and why.

## In short

- **The review is accurate.** I did not take it on trust. I re-ran each of its probes with my own
  scripts, read every record it cites beside the full passage it rests on, and checked its
  legislation claim on the Federal Register. Every technical defect it reports is real. In two
  places the problem is wider than it says (F04, F15), and a few of its counts and record-level
  verdicts need correcting (F01, F09, F18).
- **I agree with 16 of its 19 findings outright and with the other 3 in part.** I reject none.
- **Where I part company is mostly the fixes.** Of its 20 proposed fixes (counting the API key
  item) I agree with 3 outright, 14 in part, and disagree with 3. Many are sized for a production
  legal system rather than a pitch demonstrator; several assume a trade marks expert adjudicates
  now, which the owner's waterfall ruling (ADR-0120) places at the end; and it does not notice
  that the owner has already ruled on three of its items (definitions, stale documents, and the
  senses of "application").
- **Examiners are less exposed than the headline suggests, with one exception.** The explorer and
  search read the corrected records (`served_gold()`) and run no OWL reasoning. Most defects sit
  in the graph's declared logic, the publication gate and the SPARQL queries. The exception is the
  meaning of some machine-written relationships, which the explorer does show (labelled
  "Machine · unreviewed"); that is the most urgent repair.
- **It missed some things**, listed under "What the review missed". The most important: the
  published workbench's map draws 14 of the 15 corrected signed relationships as reviewed edges;
  124 of the 130 relationships re-read on 9 October have never been checked by anyone but their
  author; and the pinned Trade Marks Act is now one compilation behind the law.
- **Almost all of the repair is agent work that costs nothing.** Nine decisions need the owner;
  they are listed near the end.

## Verdicts at a glance

| # | ChatGPT's finding, in plain English | Finding | Its fix | What I would do |
|---|---|---|---|---|
| F01 | The graph's logic says a record's Manual source and its Act source are the same thing | Agree | In part | Remove the "one source only" rule and the over-narrow domains now; evidence nodes later |
| F02 | The validator never checks inferred results, or which store a record sits in | Agree | Agree | A one-line fix and a graph-aware check, tested through the real entry point |
| F03 | The site can publish when the checks fail | Agree | In part | Deploy only after the existing checks pass; skip the release manifest |
| F04 | Queries still return signed relationships that were corrected | Agree, wider | In part | Fix the workbench map and the SPARQL queries; the serving view already exists |
| F05 | Six machine-written relationships say more than their sentence | Agree | In part | The agent withdraws or re-reads now; a prioritised re-check; one condition field |
| F06 | Concepts have no definitions | Agree | In part | The definition record type the owner approved and deferred |
| F07 | Datatypes, one SKOS conflict, and an untrue "OWL 2 RL" claim | Agree | Agree | Plus a check generated from the ontology's own declarations |
| F08 | Evidence can be thinner than the rules require; the RDF drops detail | Agree | In part | Enforce the four evidence fields now; a richer RDF export later |
| F09 | Coverage is partial and the law may not be current | Agree | In part | Show the Act's compilation on every answer; re-pin upstream; one coverage table |
| F10 | Search is not shown to be better overall | Agree | In part | A pre-declared fix for hub concepts; polarity belongs to answering, not retrieval |
| F11 | Older measurement numbers no longer reproduce | Agree | Disagree | Git already freezes inputs; record the commit and grade hash in each report |
| F12 | The documents describe an older project | Agree | In part | Regenerate and correct, with a drift check, not a manifest system |
| Key | A masked API key can still be published as a fallback | Agree | Agree | Remove it once the proxy serves; the owner's decision (ADR-0118) |
| F13 | Process and time are barely modelled | Agree | In part | Split two overloaded predicates now; no process model for the pitch |
| F14 | A relationship has nowhere to hold its conditions | Agree | In part | One optional `applies_when` field, shown wherever the edge is |
| F15 | "Not on its own" is treated as "an exception" | Agree, wider | In part | A real `isExceptionTo` edge and a relabelled decision tree; an agent can do it |
| F16 | "may" and "must" cannot tell permission from discretion | In part | Disagree | First fix the modalities copied from the wrong clause |
| F17 | Documents, acts, states and roles are not told apart | In part | Disagree | Settle it in definitions and scope notes, not new classes |
| F18 | "Evidence establishes X" overstates three records | In part | In part | Read the predicate as "may show"; withdraw one, re-read one, keep one |
| F19 | A missing edge could read as "there is none" | Agree | In part | One answering rule; no model of competing interpretations |

## How I checked

- **The same code and data.** `fce501f` with the pinned snapshot fetched by `tmk-fetch-upstream`.
- **Re-ran every probe myself**: OWL RL closure over the draft schema and GC-0054; `validate.run`
  on the three controlled datasets; validation of the real graph with the inferred graph added;
  every competency query that reads signed assertions; `tmk-bulk measure` without `--write`
  (it reads committed grades and spends nothing); datatype, SKOS and profile checks over the
  union graph; the cut-down evidence probe; the search trace over all 129 benchmark questions.
- **Read the records against their sources**: each record the review cites, beside the full Manual
  chunk; and a seeded random sample of 24 other relationships re-read on 9 October.
- **Checked the law's currency**: one read-only fetch of the Federal Register's page for the Act.

## Finding by finding

### F01: a record's Manual source and Act source become "the same thing"

**ChatGPT says.** `tmk:sourcePassage` is declared functional (one value only), but the builder
writes one per evidence item. In OWL a second value is not an error: it means the two values are
the same individual. So a concept resting on both a Manual chunk and a section of the Act makes the
two identical, which contradicts the separation of law and practice.

**Finding: agree.** Reproduced exactly. 67 subjects carry more than one source passage (30
concepts, 29 typing records and 8 correction records; no relationship does). OWL RL closure over
the draft schema and GC-0054 adds `owl:sameAs` between `TMA1995/s39` and `TMM/Part31/1#1` and
reports the Manual and legislation disjointness clash twice. One count needs correcting: 21
subjects mix a Manual chunk with a section of the Act, and 4 more mix one with a finer legislative
unit, so 25 in all. Nothing that serves examiners runs a reasoner (`validate.run` uses
`inference="none"`; search is custom code), so the harm today falls on anyone who loads the graph
into a standard tool: for a pitch about ontologies, the audience most likely to try.

**Its fix: agree in part.** The immediate patch (drop `owl:FunctionalProperty`, add a regression
test) is right but incomplete, because the same probe shows a second problem it does not mention
(below). One evidence node per span is the right long-term design, but nothing reads evidence from
the RDF today (the explorer reads the record files) and a triple store is "future state" in
CLAUDE.md; it can wait until the RDF is handed to someone as a deliverable.

**What I would do.** (1) Remove the functional declaration. (2) Remove `rdfs:domain tmk:Assertion`
from the provenance properties that `_origin` stamps on every node (`origin`, `reviewStatus`,
`authoredBy`, `authoredDate`, `authoringBasis`, `authoringReasoning`, `expertShouldCheck`,
`supersedesRejected`, `confidence`, `sourcePassage`; `origin` and `reviewStatus` are stamped on
signed concepts too). Under the same rules they make every concept a `tmk:Assertion`
(the GC-0054 probe shows it), which `ontology/draft/README.md` itself warns against ("a domain
assertion reclassifies every subject of the property"). (3) Rather than add owlrl as a dependency,
add a test that checks the data against the ontology's own declarations without a reasoner: no
functional property with two values on one subject; every literal of its declared datatype; every
subject of a domain-declared property in that class. That one test catches F01, the domain problem
and F07's datatypes, and any recurrence.

### F02: the validator does not check inferred results or graph placement

**ChatGPT says.** `validate._flatten` merges the source, approved, authored and default graphs but
not the inferred graph, so the shapes for inferred results never see real ones; and flattening
loses which named graph a record sits in.

**Finding: agree.** All three probes reproduce through `validate.run`. An inferred node with no
rule, premises or status passes in the inferred graph (exit 0) and fails with three defects in the
default graph; a machine-written assertion with a complete envelope placed in the approved graph
passes, indistinguishable from the same node in the authored graph. It matters more than it looks:
`BoundedReasoningShape`, the enforcement point for "no rule derives an evaluative conclusion",
currently guards nothing. Two mitigations ChatGPT does not weigh: rule output is well formed by
construction (`rules.construct` stamps it), and placement is enforced by the builder (one mapping
per store) and the drift check on `graph/`. So this is a missing safety net, not a present failure.

**Its fix: agree.** I checked the cost: with the inferred graph included, the real graph still
validates (0 defects, 0 gaps, 259 notes), so the first half is a one-line change that hides
nothing. For placement, a few lines of Python over the dataset before flattening (no authored
origin or `AuthoredAssertion` in the approved graph, no `ApprovedAssertion` in the authored graph)
are simpler than SPARQL `GRAPH` shapes. ChatGPT is right that a concept may legitimately appear in
both graphs (a signed concept with a machine-written type). The tests must call `validate.run` on
a `Dataset`, not pySHACL on a flat graph as the current shape tests do.

### F03: publication does not depend on the checks

**ChatGPT says.** The Pages workflow fetches the corpus, builds the site and deploys; the tests,
harness, SHACL and drift checks run in a separate workflow that nothing waits on.

**Finding: agree.** Confirmed by reading both workflows, and `main` is not a protected branch
(GitHub reports `protected: false`), so a direct push or a merge with red checks would still
deploy. It has not bitten: every harness run on `main` since 7 October passed.

**Its fix: agree in part.** Gating deployment on the checks is right. The simplest way is for the
Pages workflow to run when the harness workflow completes successfully on the same commit
(`workflow_run`), rather than duplicate ten minutes of tests; the owner can also turn on branch
protection requiring the harness (a GitHub setting, the owner's to change). The release manifest
(tested SHA, validator versions, waivers) is more than a demonstrator needs: the deploy summary
already records the commit and the build output. A small `build.json` on the site (commit, pin,
counts) would be a cheap nice-to-have for the pitch.

### F04: corrected signed relationships leak into queries

**ChatGPT says.** 15 of the 35 signed relationships have been corrected and their direct triples
suppressed, but several competency queries read the historical records without excluding the
corrected ones.

**Finding: agree, and it is wider than reported.** Eight of the 13 competency queries read
`tmk:ApprovedAssertion` and none filters `tmk:isCorrected`. Six currently return corrected
records: CQ-0009 (GR-0008, GR-0056), CQ-0011 (GR-0042), CQ-0018 (GR-0034), CQ-0021 (GR-0001),
CQ-0023 (GR-0056, five rows) and CQ-0024 (counts all 35, including the 15 corrected). More
important, and missed: the published workbench's map is built from the uncorrected records
(`dashboard/build.py` passes `goldset.load()` to `views.network`), so it draws 14 of the 15
corrected signed relationships as reviewed edges; with `served_gold()` it would draw none. The
examiner-facing explorer and search use `served_gold()` and are not affected.

**Its fix: agree in part.** Exact-result tests are right. A new cross-cutting "effective-assertion
view" with current and historical modes is not needed: the serving view exists (`served_gold()`,
whose own docstring names the workbench as one of its users). The workbench simply does not use
it, and SPARQL has no equivalent. Pass `served_gold()` to the workbench's map and decision tree
(two lines). Add
`FILTER NOT EXISTS { ?assertion tmk:isCorrected true }` to the eight queries, with an `OPTIONAL`
naming the replacement where useful; make CQ-0024 count the 20 current records; and add one test
that runs every competency query and fails if a row names a corrected record, which also covers
future queries. RULE-0002 already states its limit in its header ("Reading a nil result as
'nothing is affected' is the error this limits line exists to prevent") and is owner-approved;
covering machine-written records would be a new candidate rule, low priority for the pitch.

### F05: six machine-written relationships say more than their sentence

**ChatGPT says.** GR-0432, GR-0167, GR-0521, GR-0140, GR-0437 and GR-0495 each compress a
qualified or negative sentence into a stronger, unconditional edge.

**Finding: agree.** I read each beside its full chunk:

| Record | Edge | My reading |
|---|---|---|
| GR-0432 | assignment requires the consent of the Commission | Right. The sentence is about recording an assignment of a certification trade mark after the reg 16.2 documents have gone to the Commission and before registration; the paragraph before it says assignment before referral needs no consent. The second model's audit created this reading; the first had the certification trade mark as its subject |
| GR-0167 | revocation of acceptance comes before examination | Right. A negative sentence about protected international trade marks became a positive sequence, and by the predicate's own reading ("cannot happen until") it says examination cannot happen until acceptance is revoked |
| GR-0521 | old register becomes the Register of Trade Marks | Right. The sentence is about disclaimers becoming particulars on the new Register, which GR-0536, GR-0624 and GR-0625 already say |
| GR-0140 | owner or authorised user owns internet domain name | In part. GC-0035 is a signed role meaning the registrant or authorised user of the thing referred to, so the edge is close to circular rather than false; but `owns` contradicts its own counter-example ("not for a person who only uses the mark with the owner's authority"), and the real proposition (the s 43 ground applies if the applicant is not that person) is already GR-0142 |
| GR-0437 | owner or authorised user must own phoneword | Right, and the sentence contains no "must". Its proposition is already GR-0440 and GR-0702 |
| GR-0495 | acceptance results in condition of registration | Right. A discretion under s 44(3) became an outcome; the "may" is on the reified record but not on the direct triple |

The repository already knew about five of the six: `HANDOFF.md` lists GR-0167, GR-0521 and
GR-0495 among the weakest judgements of the 9 October restructure, and GR-0140 and GR-0437 under
"What to distrust". I found a seventh of the same kind: GR-0454 turns "the Registrar may consider
that it is not reasonable to revoke acceptance if the applicant agrees..." into "condition of
registration prevents revocation of acceptance".

**Its fix: agree in part.** Withdrawing or replacing these is right, and so is looking again at
the whole set. Three differences:

1. **An agent does this now, not an expert.** These are machine-written records; withdrawing or
   re-reading them is routine agent work (ADR-0127, ADR-0131), stamped unreviewed. The owner has
   ruled that examiners review everything together when it ships and that no question goes to the
   expert singly (ADR-0120); adjudicating six records with an expert now would contradict that.
2. **Prioritise rather than re-review all 352 at once.** The risk is concentrated. 124 of the 130
   edges re-read on 9 October (S029) were judged by the second model's audit only in their earlier
   form, so nobody but their author has checked their current reading; only 199 of the 352 current
   triples have ever been judged. In a seeded sample of 24 of those re-reads I found 16 sound, 4
   with a material problem (GR-0526 drops "in most cases"; GR-0379 drops "if the application is in
   a non-English language"; GR-0240 misreads `extendsTo`; GR-0249 rests on a heading) and 4 with a
   smaller one (three carry a modality belonging to another verb in the sentence; one is slightly
   imprecise). The worklist, in order: the seven records above; the 14 current edges the audit
   judged wrong that still serve (several could not be applied because the audit proposed
   `related`, since retired); the 30 re-reads carrying a modality inherited from their earlier
   reading; the five edges whose only evidence is a heading (GR-0239, GR-0248, GR-0249, GR-0504,
   GR-0505); then the remaining unjudged re-reads. All of it through the existing ledger
   (`data/derived/audit/restructure.yaml`, `tmk-bulk restructure`), spending nothing.
3. **One condition field, not a seven-part pattern.** ChatGPT's "minimal qualified assertion
   pattern" (scope, condition, polarity, modality, authority, lifecycle and projection policy as
   separate fields) is a production design. For the demonstrator, one optional field,
   `applies_when`, holding the sentence's condition in its own words, is enough, provided it is
   shown wherever the edge is shown and given to the answering model (F14). An edge whose meaning
   cannot survive even with that field is withdrawn. Most of the seven records above should simply
   be withdrawn, since other edges already carry their proposition; GR-0432 can return with its
   condition once the field exists. I checked that withdrawing all seven, and GR-0248 (F18), still
   leaves all 164 concepts in one connected piece.

### F06: the concepts have no definitions

**ChatGPT says.** None of the 164 concepts has a definition; a list of sources is not a definition;
and the senses of "application" are typed inconsistently.

**Finding: agree.** Confirmed: no concept carries `skos:definition` (the 51 in the graph are all on
predicates), and the builder omits them on purpose. ChatGPT missed that this has been ruled on: the
8 October review raised it as item F4 ("Definitions were the expert's first request"), and the
owner ruled "Approved but defer for now as its a lower priority" (CHAT-0055). The senses of
"application" are that review's item B2, which the owner postponed (CHAT-0025). Thirty
machine-written concepts still carry a definition-like summary in `notes` under the doubled prefix
"Summary, not a definition: Summary:".

**Its fix: agree in part.** Agree that definitions should be written now under the authoring rules
(ADR-0079), with evidence and their own review status, and that approving a label must not imply
approving a definition. Three differences. Build them as the separate record type F4 approved
(their own id series, as a concept's type is its own record under ADR-0071), not as a field on the
concept, because signed concepts cannot be edited. Draft them from the `definition_sources` every
concept already has, preferring the Act's own definitions as the owner asked (CHAT-0045); that
needs no model spend. And leave adjudication to the examiners' review at ship time (ADR-0120)
rather than an expert pack now. On "application" I agree with ChatGPT's own restraint: write the
definitions with scope notes first, and split a concept only where a question needs it. Lifting
the deferral is the owner's decision; with two reviews now naming it, and the pitch being about an
ontology, I recommend it.

### F07: datatypes, a SKOS conflict and the OWL 2 RL claim

**ChatGPT says.** Confidence values are doubles where the schema says decimal; 12 properties
declared as plain strings carry language-tagged text; GC-0017 and GC-0018 are both "related" and
"broader"; and the "OWL 2 RL" claim is untrue because of three existential equivalences and
`xsd:date`.

**Finding: agree.** Every detail reproduces. All 647 confidence literals are `xsd:double` against
an `xsd:decimal` range; exactly 12 string-ranged properties carry `@en-AU` text
(`authoringReasoning` 664 times, `expertShouldCheck` 631, `notLabel` 407, and nine others);
GC-0017 (geographical reference) is `skos:related` to GC-0018 (geographical indication), while
GC-0018 is recorded as a kind of GC-0017 (`skos:broader`), with no cycle once inverse `narrower`
links are added; and `RelevantFactor`, `Exception` and `Remedy` are equivalences to existential
restrictions. Two details: `xsd:date` is
outside OWL 2's datatype map altogether, not just the RL profile, and some reasoners refuse it;
and both SKOS triples are in the approved graph, that is, signed.

**Its fix: agree.** Choose the bounded contract: RDF, SKOS, SHACL and the SPARQL rules. Nothing in
the product runs OWL inference, so drop the "OWL 2 RL" claim (an agent-proposed ADR, since the
draft README says leaving the profile needs one) and keep `xsd:date`, the right type for a date.
Emit confidence as `Decimal(str(value))` with `xsd:decimal`, and declare the prose properties
`rdf:langString`. Two additions. The declaration check proposed under F01 enforces all of this in
the existing gate. And the SKOS fix has to be a correction record, because both triples are
signed; the owner's D2 ruling ("correct known defects", CHAT-0041) covered the defects known on 8
October, and a one-line confirmation that it extends to this one is worth having. Rewriting the
three equivalences in an RL-legal form would not help: the RL-legal half (the restriction implies
the class) is exactly what produces F15.

### F08: evidence can be thinner than the rules, and the RDF drops detail

**ChatGPT says.** The envelope schema requires only `ref` in an evidence item; the checker skips a
missing hash, stops at a missing span and never requires a quote; and the RDF keeps only the
reference.

**Finding: agree.** Confirmed: the schema requires only `ref`; `_evidence_findings` behaves as
described; and a copy of GC-0054's envelope cut down to a bare `ref` passes both checks. The data
itself is complete (all 709 current evidence items carry span, hash and quote), so this is a gap in
enforcing a rule the repository states (ADR-0045, ADR-0090 c3: a ref, a span, the content hash,
and a quote that is exactly the text at the span).

**Its fix: agree in part.** Require span, hash and quote for every evidence item whose ref is a
chunk, provision or unit, in both the schema and the checker. No new "evidence kind" field is
needed for case citations: they are recognisable from their ref (`CASE/...`), the checker already
treats them separately, and no current evidence item cites one. The per-span RDF export and the
round-trip tests are the right design for when the RDF becomes a deliverable (F01), not now.

### F09: coverage is not completeness, and the snapshot is not the current law

**ChatGPT says.** The graph holds 42.9% of chunks; citation and case coverage is partial; and the
pinned legislation predates the current compilation of the Act.

**Finding: agree.** The counts reproduce: 1,056 of 2,460 chunks and 208 of 500 pages in the source
graph; 325 decision nodes; 2,236 citation records. One correction: the 63 unresolved citations are
provision citations, 63 of 1,545 (24 of them marked `ambiguous` upstream, which rule 6 says stay
unresolved); the 403 case citations never resolve because no judgment text is held. On currency I
went further. The pinned Act is compilation 47 (`C2024C00545`, in force from 14 October 2024,
captured 29 July 2026); the Federal Register's current compilation is 48 (`C2026C00421`, from 19
September 2026), made by Schedule 1 items 1 and 8 to 12 of the Regulatory Reform Omnibus Act 2026.
I have not established which provisions changed. Upstream records the compilation number, register
id and capture date for both instruments; the graph keeps only the upstream commit.

**Its fix: agree in part.** Agree on keeping capture time apart from review time, and on never
carrying approval across changed text; the second already exists (a changed content hash makes a
record stale, and the harness refuses to refresh it silently). The differences: one current,
pinned release is enough for a demonstrator, because git and the pin already make any past state
reproducible, so no separate "reproducibility release"; carry upstream's compilation details into
the graph and show them on every answer and on the pitch's limits page ("the Act as in force from
14 October 2024"); ask upstream to re-capture so the pin can move to compilation 48, then let the
staleness check show what moved; and one coverage table by Part (searchable, in the graph, cited
by a signed record) rather than four separate measures.

### F10: search value is not established overall

**ChatGPT says.** In the latest measurement, ontology search with the model's reading scores 0.701
against keyword search's 0.702, and by names alone it is worse; benefits should be measured
elsewhere, for example with examiner tasks.

**Finding: agree.** The figures reproduce, and the repository's own report says the same. One
point ChatGPT plays down: the only questions no model wrote, the expert's ten, are where the
ontology does best (reading against keyword +0.094 [+0.003, +0.189]; in the older measurement with
vectors, ontology against hybrid +0.030 [+0.008, +0.055]). Ten questions are too few for a claim,
but the direction matters, because the model-written questions "often use its names" (the report's
own caveat).

**Its fix: agree in part.**
- **Agree** on keeping the best baseline as the fallback and testing any change once, declared in
  advance (the HANDOFF already requires that). I found a concrete candidate for that change.
  Generic hub concepts are filtered from the recognised ideas but not from their neighbours, so
  "trade mark" (1,003 mentions) or "applicant" (542) enters the expansion in 15 of the 76
  questions that have neighbours; each mention adds weight to the linked list; and in the page's
  configuration (no vectors) ties in that list are broken by reference order. That plausibly feeds
  the "linked passages crowd out good hits" problem the HANDOFF already names.
- **Disagree** that polarity should steer retrieval. For finding passages, "X does not by itself
  give rise to Y" is as relevant as "X gives rise to Y", and the negative passage is often the one
  an examiner needs. CQ-0011's own note shows where the risk really lies: a system citing the
  negative passage in support of the positive claim, which is an answering error. Polarity belongs
  to F14 and F19.
- **Examiner task studies** are the right measure of the ontology's real value, but sending tasks
  to examiners is outward-facing (an owner gate), and ADR-0120 has examiners see the work together
  at ship time; the study belongs there. For the pitch, show explanation and traceability with
  worked examples labelled as illustrations, and keep ranking claims to what was measured (the
  owner's call, OQ-0029). An ablation needs new passages graded, which is spend the owner must
  approve.

### F11: older measurement numbers do not reproduce

**ChatGPT says.** Re-scoring the 9 October rankings against today's shared grades gives 0.702,
0.812 and 0.773, not the published 0.725, 0.844 and 0.803, because the grade file has grown.

**Finding: agree.** `tmk-bulk measure` (without `--write`) gives exactly those figures from 2,892
grades against the report's 2,344. The cause is ordinary pooled evaluation: the 548 grades added
on 12 October for the reading run raise each question's ideal ranking. The comparisons barely move
(ontology against hybrid -0.041 then, -0.040 now; against keyword +0.079 then, +0.071 now), so the
conclusions stand and only the absolute levels shift.

**Its fix: disagree.** Bespoke immutable "experiment bundles" duplicate what git already does:
every input (questions, pools, grades, rankings, code, prompts, the response cache) is committed,
so a commit is the bundle. What is missing is a pointer. Each report should record the commit it
was taken at, plus a hash and count of the grade file, and `measure --write` should refuse to
overwrite a report whose inputs have changed, writing a new dated report instead that names the
old rankings and the new grades. Reproduction is then `git checkout <commit>` and
`tmk-bulk measure`. Any number in the pitch should cite the report and commit it came from.

### F12: the documents describe an older project

**ChatGPT says.** The root README, the draft ontology README and the committed ontology report
contradict the current state.

**Finding: agree.** Confirmed. The README says "the apparatus is built and the content is not";
`ontology/draft/README.md` describes "nine OWL 2 RL modules over the section 43 pilot" and forbids
writing definitions under a rule ADR-0079 replaced; and `data/derived/reports/ontology.md` was
generated on 9 September (78 machine-written concepts, 50 classes, 14 predicates; today 112, 89
and 52). One more it missed: every concept sits in a scheme labelled "Section 43 examination
vocabulary — pilot". This too was ruled on: item F5 of the 8 October review, "Approved but defer
for now" (CHAT-0056).

**Its fix: agree in part.** Regenerate the report, correct the stale sentences and the scheme
label, and add a drift check for the generated report like the one on `graph/`. A manifest from
which all status prose is generated is more machinery than a demonstrator needs. On namespaces,
say plainly that the `data.ipaustralia.gov.au` IRIs are neither published nor dereferenceable (the
base IRI question is still open) rather than design a publication policy now. The deferral is the
owner's to lift; it is about an hour of agent work, and a pitch reviewer will read these files.

### The masked API key fallback

**ChatGPT says.** The Pages build can still publish a recoverable, masked key if one is configured
without a proxy; remove the fallback before wider use.

**Finding: agree.** Confirmed in `explorer/build.py` and `pages.yml`. It is a risk the owner
accepted knowingly (ADR-0118, authority human), and S033 built the proxy that removes the need for
it.

**Its fix: agree.** Once the proxy is deployed and `TMK_LIVE_ENDPOINT` is set, remove the fallback
and revoke the old key, as the HANDOFF already plans. Because it reverses part of ADR-0118, it is
the owner's decision.

### F13: process and time

**ChatGPT says.** There is no coherent model of procedural states and transitions; `precedes`
mixes order with prerequisite, and `prevents` mixes blocking a step with stopping its clock.

**Finding: agree.** The definitions say so ("which cannot happen until the subject has"; "cannot
happen, or its time stops running"), and current records use both meanings of `prevents`: GR-0394
(a ground for rejection blocks acceptance) and GR-0534 (a deferment stops the time that would make
an application lapse). The counts reproduce (4 `precedes`, 5 `prevents`, 3 `isCommencedBy`, 2
`becomes`, 3 `resultsIn`, 1 `isAssessedIn`).

**Its fix: agree in part.** Split the overloaded predicates now: `prevents` into a blocking
predicate and a clock-stopping one, re-reading its five edges; and narrow `precedes` to say plainly
that the first step must happen before the second, which is what all its sound uses mean. A
generic process model (activities, events, states, transitions, triggers, preconditions, effects)
is outside the demonstrator's scope (D1 to D4). Say in the pitch's limits that the ontology names
procedural steps and some orderings, and is not a process model.

### F14: a relationship has nowhere to hold its conditions

**ChatGPT says.** A relationship record has subject, predicate, object, evidence, tier and
modality, and nowhere to hold the conditions under which it is true, so they survive only in
prose.

**Finding: agree.** The relationship schema has thirteen fields and none for a condition. ChatGPT
does not mention what limits the harm on screen: the explorer's relationship card shows the quoted
source sentence and the modality beside every edge, so an examiner sees the condition. Where it
bites is the answering model: the "GRAPH PATH" lines it is given are bare triples, with no
modality, condition or sentence.

**Its fix: agree in part.** A qualified proposition with seven components is right for a
production rules system and too much here. The `applies_when` field from F05, carried into the RDF
on the reified record, shown on every card, and added with the modality to the answering model's
path lines, covers every case found that is worth keeping. The direct triple can stay as a
navigation edge (ADR-0058 requires both forms), described as such.

### F15: "not on its own" is treated as "an exception"

**ChatGPT says.** `doesNotGiveRiseTo` means "does not by itself give rise to", yet `Exception` is
defined as anything with such an edge, so insufficiency is promoted to exception.

**Finding: agree, and it is live, not only latent.** The probe reproduces: a `doesNotGiveRiseTo`
edge makes its subject an `Exception`, and a `qualifies` control does not. ChatGPT says it did not
show a production path using this meaning, but one exists: `typing.FUNCTIONS` defines the
exception function as "something that takes a case out of a ground or test", and the published
workbench's decision tree (`dashboard/views.py`, `FUNCTION_EDGES`) labels every such subject an
exception. The explorer describes functions only in prose. The predicate is also overloaded: of
its six edges, two state insufficiency (GR-0015, "the mere presence..."; GR-0688, "merely
because..."), three state hedged exceptions (GR-0699, GR-0700, GR-0701), and one cites a
procedural sentence (GR-0702: the ground is "reconsidered" when the applicant shows they are the
owner or authorised user), when the sentence before it states the exception itself.

**Its fix: agree in part.** Agree on removing the equivalence and on not building a general logic
layer. Disagree that it waits on expert review: the owner decided only that functions are edges
(ADR-0126); choosing `doesNotGiveRiseTo` to carry "exception" was the agent's part of that ADR,
which an agent may revise by a new ADR. A fix that keeps the owner's decision: add an
`isExceptionTo` predicate meaning a case the ground or test does not reach; re-read the three
hedged exceptions onto it, with their hedges in `applies_when`; keep `doesNotGiveRiseTo` for
insufficiency and show it in the tree as "not on its own"; and re-read GR-0702 onto `isExceptionTo`,
citing the sentence that states the condition ("will apply if the applicant ... is not also the
owner (or authorised user)"). Keep it rather than withdraw it: once GR-0140 and GR-0437 go, it is
the only relationship left on GC-0035. The richer structures ChatGPT lists (conjunctions, alternatives,
completeness markers) are outside the demonstrator; F19's answering rule covers the main risk they
address.

### F16: normative force

**ChatGPT says.** `must`, `may` and `should` cannot tell obligation, permission, power, discretion
and possibility apart; add a reviewed interpretation with an actor and an action.

**Finding: agree in part.** True, and the schema already warns that reading a "may" is a legal
judgement. But the defect actually visible in the data is plainer: modality attached to the wrong
verb. Thirty of the 130 re-read edges kept the modality of their earlier reading, because the
restructure copies every field of a record and changes only the triple. In my sample, GR-0460's
"should" belongs to "a citation should be raised", not to "examiner performs examination"; and
GR-0437's "must" is in no verb of its sentence at all.

**Its fix: disagree, for now.** A normative-interpretation layer (actor, action, beneficiary,
conditions) is a production feature. Re-check the 30 inherited modalities against the verb their
predicate reads, and make the restructure clear the modality whenever it changes a predicate. Keep
the source's own word, shown with its sentence, and rely on the rule already in force (the system
never states an examination outcome) to stop a "may" becoming a result.

### F17: identity, roles and scope

**ChatGPT says.** Documents, acts, states, parties, marks and parts of marks, and concepts and
instances all need telling apart.

**Finding: agree in part.** The distinctions are real, and a few touch current concepts (the
"acceptance" concept takes "accepted" as an alternative label, merging the act and the state). Most
matter only if case data comes into scope, which ChatGPT itself makes conditional, and the split
between a role and its holder that it praises already exists (`tmk:roleConcept`).

**Its fix: disagree, as separate work.** Settle these in the definitions and scope notes of F06,
where saying "this concept is the act of accepting, not the accepted state" costs one sentence.
Add no classes, and leave case instances out of scope.

### F18: "evidence establishes X"

**ChatGPT says.** The evidence module calls `establishes` unused, yet three records use it, and
each overstates its sentence.

**Finding: agree in part.** Confirmed that `evidence.ttl` declares `tmk:establishes` "UNUSED" with
domain `tmk:Evidence`, while the generated `relations.ttl` declares the same property again with
domain `tmk:LegalMatter`. On the records: GR-0248 rests on an all-capitals heading and should go;
GR-0163's sentence says honesty is the first criterion to consider, not that evidence establishes
honest concurrent use. I disagree on GR-0206: its sentence says a mark "is shown through evidence
of use to be capable of distinguishing", almost word for word the predicate's own example
("Evidence of use may show a trade mark to be capable of distinguishing"); the colours are where
the endorsement applies, not a limit on the proposition.

**Its fix: agree in part.** The fault is mainly the predicate's reading: its example says "may
show" while its reading says "establishes". Read it, or rename it, as "may show"; withdraw GR-0248;
re-read or withdraw GR-0163; keep GR-0206; and remove the stale duplicate declaration from
`evidence.ttl`. Agree that a case-evidence model is a separate scope decision, and not one for now.

### F19: knowledge limits

**ChatGPT says.** A missing relationship must never become "there is no requirement" or "there are
no exceptions"; review state, coverage, applicability and disagreement need separate treatment;
and competing interpretations need structured support.

**Finding: agree.** The answering instructions say "If the passages do not answer it, say so" and
nothing about absence, and a question such as "are there any exceptions?" invites exactly the
inference ChatGPT warns against.

**Its fix: agree in part.** Agree with the urgent part, as one instruction to the answering model
(in Python and `engine.js` together): never conclude that a requirement, exception or step does
not exist because the passages or the graph path do not mention it; say what they record, and that
they may not be complete. Add matching words to the page where nothing is found ("Gathered 0
passages linked to those ideas" is already on the HANDOFF's list). Disagree with modelling
competing interpretations: the corpus is one Manual and two instruments with no judgment text, so
there is little to compete, and the case data that would supply it is out of scope. Changing what
the live chatbot says is an owner gate, so the instruction needs the owner's approval.

## What the review missed

1. **The workbench map shows corrected signed relationships as reviewed.** It draws 14 of the 15
   from the uncorrected records (F04).
2. **Every concept is classified as an "assertion"** by the provenance properties' domains, under
   the same OWL rules the review used; and `tmk:establishes`'s domain in `evidence.ttl` makes
   "evidence of use" a `tmk:Evidence` (F01, F18).
3. **The pinned Act is one compilation behind**, and the graph discards the compilation details
   upstream provides (F09).
4. **124 of the 130 relationships re-read on 9 October have never been checked by anyone but their
   author**, and 14 edges the audit judged wrong still serve (F05).
5. **Thirty re-read edges carry a modality copied mechanically from their earlier reading**, and
   five rest only on a heading (F05, F16).
6. **Generic hub concepts enter search expansion as neighbours**, and in the page's configuration
   the linked list breaks ties by reference order (F10).
7. **The "exception" reading is live** in the workbench's decision tree, not only in unused OWL
   (F15).
8. **Six competency queries leak corrected records, not four** (F04).
9. **Three items were already ruled on** in the 8 October review: definitions (F4, approved and
   deferred), stale documents (F5, approved and deferred) and the senses of "application" (B2,
   postponed). Those rulings stand; lifting a deferral is the owner's decision.
10. **A seventh flattened discretion** (GR-0454) and a stale concept-scheme label.

## Where its remedies do not fit this project

- **Expert adjudication now.** The owner has ruled that no expert signs anything until the
  ontology ships, when a group of examiners reviews it all at once, and that no question goes to
  the expert singly (ADR-0120). Repairs to machine-written records are agent work, stamped
  unreviewed; adjudication happens in the examiners' review at ship time.
- **Production machinery for a pitch.** Release manifests, bespoke bundle formats, a parallel
  "current-source release", a generic process model, a normative-interpretation layer and a model
  of competing interpretations would each be reasonable in production. This project's purpose is
  "a system that works, soon, not every nuance" (ADR-0109) and its scope is D1 to D4 (ADR-0110).
  Each belongs on the pitch's honest-limits page, not in the build.
- **Spend.** Recorded spend (US$9.63) is above the cap (US$9.49), so every paid call is refused
  until the owner names an amount. Packages 1 and 2 below make no model calls; re-measurement and
  an ablation would.
- **Who may act.** Several fixes ChatGPT routes to an expert are agent work under the repository's
  own rules: the `Exception` mapping (the agent's part of ADR-0126), withdrawing machine-written
  edges (ADR-0127, ADR-0131), and the datatype and gate fixes.

## Recommended order of work

**Package 1: the gates, the serving views and the declared logic** (agent, no spend, about one
session). The workbench's map and decision tree on `served_gold()` (F04); the competency-query
filters and the every-query test (F04); the functional and domain declarations, with the
declaration check (F01); the inferred graph, the placement check, and tests through `validate.run`
(F02); deployment after the harness passes (F03); decimal confidence, `rdf:langString` ranges, the
OWL 2 RL claim dropped by ADR, and broader-with-narrower cycle and S27 checks (F07); the four
evidence fields required (F08); the commit and grade hash in report headers, with no silent
overwrite (F11). Then `tmk-graph --write --rules`.

**Package 2: what the edges say** (agent, no spend, one or two sessions). The F05 worklist in the
order given there, through the restructure ledger, with the restructure fixed to clear a re-read's
modality; F13's split of `prevents` and narrowing of `precedes`; F15's `isExceptionTo` and the
decision tree's label; F18's reading of `establishes`; F14's `applies_when` field on the schema,
the builder and the cards. Then rebuild the graph. This package changes what the explorer shows
examiners, so it goes first if time is short.

**Package 3: the owner's decisions** (next section).

**Package 4: after those decisions.** Regenerate and correct the documents (F12) and write the
definitions (F06) if the deferrals are lifted; re-pin upstream and let the staleness check show
what moved; re-measure with a pre-declared change to the blend, if the owner names an amount; the
pitch's claims (OQ-0029); the examiners' review pack (ADR-0120).

## Decisions for the owner

1. **Re-capture the legislation upstream and move the pin** to the Act's compilation 48. Until
   then I recommend showing "the Act as in force from 14 October 2024" on every answer.
2. **Lift the deferral on definitions** (8 October item F4) before the pitch. Recommended.
3. **Lift the deferral on the stale documents** (item F5). Recommended; about an hour of work.
4. **Approve two changes to what the live chatbot is given and told**: the modality and condition
   on each graph path line (F14), and the rule against concluding absence (F19). Recommended.
5. **Remove the masked-key fallback** once the proxy serves, and revoke the old key; this reverses
   part of ADR-0118.
6. **Confirm that the D2 ruling ("correct known defects") covers the GC-0017 and GC-0018 SKOS
   conflict**, which sits inside signed records.
7. **Turn on branch protection for `main`**, requiring the harness checks (a GitHub setting).
8. **Choose which measured results the pitch claims** (OQ-0029). On this evidence: the ontology
   does not beat the best plain search on model-written questions; it does, modestly, on the
   expert's ten; the reading recovers the loss from names alone; and its clearer value is
   explanation and traceability, which can be shown but has not been measured.
9. **Name an amount for re-measurement**, if wanted, after packages 1 and 2.

## ChatGPT's "decisions to record", answered

| Question | Answer |
|---|---|
| Strict OWL 2 RL, or bounded RDF and SHACL? | Bounded RDF, SKOS, SHACL and SPARQL rules; an agent can record it (ADR, agent-proposed) |
| Which machine-written propositions may appear in each view? | Already decided: all of them, labelled at the point of use (ADR-0082) |
| What does "current" mean? | For content, the records with corrections applied (`served_gold()`); for sources, the pin, which should show its compilation |
| Which measured benefit justifies ontology expansion? | The owner's (OQ-0029) |
| Navigation tool, explanation tool, or case guidance? | Navigation and source-grounded explanation; never case outcomes (CLAUDE.md §2) |
| Which procedures and applicability questions are in scope? | None as a process model; say so as a limit |
| Which inferences are licensed? | The approved CONSTRUCT rules only; no OWL inference |
| When may a list of conditions be called complete? | Never, in this demonstrator (F19) |

## How to repeat the checks

The probes were scratch scripts and are not committed; each is a few lines. After
`pip install -e ".[rdf,test]"`, `pip install owlrl` (for F01 and F15 only) and
`tmk-fetch-upstream`:

- **F01**: load `ontology/draft/*.ttl`, GC-0054's triples from `graph/dataset.nq` and its two
  sources' types; run `owlrl.DeductiveClosure(OWLRL_Semantics).expand`; look for `owl:sameAs`
  between the sources, the error messages, and GC-0054's types. Count subjects with two or more
  `tmk:sourcePassage` values across the named graphs.
- **F02**: put one bare `tmk:InferredAssertion` in the inferred graph of an empty `rdflib.Dataset`
  (then in the default graph) and call `validate.run(dataset)`; for placement, a complete authored
  envelope (with `authoredDate` and `authoringReasoning`) in the approved graph. For the cost,
  `build()`, `rules.apply_rules`, then `_flatten` plus the inferred graph through pySHACL.
- **F04**: run each `queries/competency/*.rq` over `graph/dataset.nq` and compare `?record` with
  the subjects of `tmk:isCorrected true`; for the workbench, `views.network(goldset.load(), ...)`
  against `views.network(served_gold(), ...)`.
- **F05**: print each record with its full chunk (`load_corpus().chunks[ref]`); for the audit,
  compare the `judged` triple in `data/derived/audit/edges.yaml` with each record's current one.
- **F07**: the datatypes of `tmk:confidence`; language tags on properties whose `rdfs:range` is
  `xsd:string`; `skos:related` pairs inside the `broader` closure, with inverse `narrower`.
- **F08**: copy an authored envelope, cut its evidence to `[{"ref": ...}]`, and run
  `authored.store.validate_envelope(envelope, record_id=...)` and `harness._evidence_findings`.
- **F09**: `data/upstream/snapshot/legislation/TMA1995/instrument.json` for the pinned
  compilation; the Federal Register's `C2004A04969/latest` page for the current one.
- **F10**: `Systems.trace` over the 129 benchmark questions (context from `bulk.cli._context()`),
  counting neighbours that are in `links.generic`.
- **F11**: `tmk-bulk measure`, without `--write`.
- **F15**: the review's own snippet, or the full draft schema with one `doesNotGiveRiseTo` edge and
  a `qualifies` control.

# Ontology review response 2

**As at:** 2026-10-19 · session S040 · responding to `docs/Trade-Mark-Ontology-Consolidated-Review.md`
(written by ChatGPT, dated 18 October 2026, about commits `3ecf410` and `e6985e9`)
**Checked against:** `c6a0f0e`, which differs from `e6985e9` only by the review file, with the pinned
snapshot `308bfd9` (the Act at compilation 48)
**Written by:** an agent (Claude Code), at the owner's request. Machine-written and reviewed by no one;
every judgement in it is the agent's and can be wrong.
**Changed:** no record, graph, query, prompt, shape or page. No paid model call was made. Every
number below was re-run in this session with the library versions ChatGPT used (rdflib 7.6.0,
pySHACL 0.40.1).

The task: for each problem ChatGPT identified, say whether it is right; where it is, say whether its
proposed fix is right; and where the fix is wrong for this project, say what should be done instead,
and why. The first response (`docs/ONTOLOGY-REVIEW-RESPONSE.md`, S035) answered ChatGPT's earlier
review of 15 October; this one answers the consolidated review, which keeps that review's
implementation findings as R01 to R10 and adds A01 to A12 against a wider set of intended uses.

## In short

- **The technical findings are accurate.** I re-ran every probe it describes, read each cited
  record beside its full passage and the provision behind it, and checked every count. All ten
  implementation findings (R01 to R10) reproduce. In four places the problem is wider than reported
  (R02, R03, R04, R08), and in one the headline says more than its own table (R09).
- **Findings: I agree with 19 of the 22 and with the other 3 in part. I reject none.**
- **Fixes: I agree with 5 outright, 13 in part, and disagree with 4.** The disagreements are mostly
  about scope and timing, not about the design. Where a fix calls for hand-written work and the
  repository already has a signed yardstick (R06) or a deterministic check would do (R02, R07), I
  use that instead; R06's fix as written would have an agent write the expected answers it is then
  graded against.
- **The A-series is a sound gap analysis against uses this repository has not adopted.** ChatGPT
  writes as though the ontology's immediate purpose includes explaining objections to customers, and
  later ML, decision services and policy simulation. The repository records a different purpose: a
  pitch demonstrator for examiners, D1 to D4 (ADR-0109, ADR-0110), with nothing about customers.
  Whether the purpose widens is the owner's decision, and it decides most of the A-series. I
  recommend it does not widen yet, and that the A-series becomes the pitch's account of what the
  foundation would need next.
- **Two A findings are live defects in the examiner chatbot today, whatever the scope.** A06: the
  1,600-character cut removes exactly the exceptions in section 44 (subsections (3) and (4) start at
  characters 2,390 and 2,962), so the model is shown the rule without its exceptions. A08: the
  citation check runs against the full stored text rather than the excerpt the model saw, an answer
  with no citations passes silently, and dropping a bad citation leaves its sentence on the page.
- **It missed some things.** The most important: the 37 correction records share the definitions'
  validation gap (R04); the RDF drops span, hash and quote for 634 evidence items across four record
  types, not 230 in one (R03); the signed competency-question records already contain the answer
  contract R06 asks someone to write; and three of the pitch pack's six capability claims currently
  say more than the implementation does.
- **Almost all of the repair is agent work that costs nothing.** Four decisions need the owner;
  they are listed near the end.

## Verdicts at a glance

| # | ChatGPT's finding, in plain English | Finding | Its fix | What I would do |
|---|---|---|---|---|
| R01 | Four "is an exception to" edges overstate their sentences | Agree | In part | Re-read three as `qualifies`, re-anchor the fourth; a hedge field, not new predicates; fix the predicate's own example |
| R02 | Three definitions drop a qualification their source states | Agree, wider | In part | Deterministic triage of all 149 first, then re-read what it flags |
| R03 | The RDF loses the definitions' evidence detail | Agree, wider | Agree | One evidence-anchor node per evidence item, for every record type |
| R04 | Validation skips definitions; RULE-0001's record is wrong | Agree, wider | Agree | Add the targets (corrections too); fix RULE-0001; an equality check |
| R05 | Change impact misses machine-written records and definitions | Agree | In part | One dependency index in Python, keyed by any ref; leave the approved RULE-0002 alone |
| R06 | Competency queries do not answer their questions | Agree | In part | Test each query against its own signed record, which already holds the contract |
| R07 | Conditions are rare, and "none" cannot be told from "not checked" | Agree | In part | Set the state by rule where a machine can; split hedge from condition |
| R08 | The authority check is a heuristic | Agree, wider | Agree | Say so, test its misses, soften the pitch's wording |
| R09 | The measurements do not establish a retrieval advantage | In part | Agree | They establish one over keyword search, not over hybrid; owner gates on re-measurement |
| R10 | Coverage and source currency need clearer boundaries | Agree | Agree | The coverage table already planned, plus the Manual's capture date |
| A01 | No model of a matter, its objections or role assignments | Agree | In part | Not now; reword roles as capacities now |
| A02 | No process or event model | Agree | Disagree | Not now; regs 4.8 to 4.10 if the owner adopts customer guidance |
| A03 | Applicability does not depend on context or time | Agree | In part | Show the Manual's capture date now; versioning when a dated question is in scope |
| A04 | No structured legal tests | Agree | Disagree | Not now (ADR-0009); keep the two principles that matter in the answer rules |
| A05 | No model of case evidence and assessments | Agree | Disagree | Not now; no case evidence is in scope or held |
| A06 | Passages are cut at 1,600 characters | Agree | In part | Whole provisions (90% are under 1,800 characters), cuts around the match, every cut marked |
| A07 | Legislation is not directly searchable; cases are citations only | Agree | In part | Exact-reference lookup and provision search now; judgments and customer pages are upstream's and out of scope |
| A08 | Support is not verified claim by claim | Agree | In part | Check against what was sent; claims with their own quotes; mark what fails. No paid entailment check yet |
| A09 | No customer explanation model | In part | Disagree | Not a defect of an examiner tool; the owner's decision |
| A10 | Dependency, scenarios and real-world effects are different questions | Agree | In part | Agree with the distinction; build only the first (R05) |
| A11 | No versioned contract for downstream consumers | In part | In part | A small build manifest now; R03 is the real precondition |
| A12 | Tests do not cover the intended tasks | Agree | In part | Deterministic release-blocking fixtures now; examiner-written scenarios are the owner's call |

## How I checked

- **The same code and data.** `c6a0f0e` (equal to `e6985e9` plus the review file) with the pinned
  snapshot fetched by `tmk-fetch-upstream` and verified against `data/pin.json`.
- **The baseline.** `tmk-graph --rules --check` (the committed graph matches a rebuild), `tmk-shacl`
  (0 defects, 0 gaps, 259 notes) and `tmk-harness` (0 defects, 12 gaps, 15 notes; 21 unverified
  legislative bases) all reproduce ChatGPT's figures.
- **Its probes, re-run with my own scripts**: the GD-0001 mutation through `validate.run` on the
  committed `Dataset`, and the same mutation on a correction; the inferred-assertion equality check;
  every competency query in R06; the authority detector on ChatGPT's sentences and four of mine;
  the section 44 offsets and passage-length counts through the repository's loader; the evidence
  fields exported for every authored node type; the RULE-0002 dependants against the corrected
  records; Part coverage of the source graph.
- **Read the records against their sources**: each record ChatGPT cites, beside its full chunk or
  provision, and the concept records behind them; the browser's `Engine.verify` and `ask.js` by
  reading, not in a browser.
- **A deterministic triage of all 149 definitions** (R02), to test whether a check could find what
  ChatGPT found by reading.
- **Not run**: the full test suite (nothing changed), any live model call, any browser session.

## Whose purpose? The review's framing

**ChatGPT says** (its sections 1 and 2). The ontology is meant as a foundation for machine learning,
machine decision-making, customer service and policy-writing; its immediate customer role is
explaining requirements, the application process and objections, possibly through a chatbot with
visuals. So process, applicability, objection and evidence modelling should begin now; the
`ExaminationOutcome` restriction and the exclusion of point-in-time questions are inappropriate as
permanent restrictions; and the scope documents should distinguish representing a recorded
decision, explaining a rule, evaluating a hypothetical, predicting an outcome and making a decision,
with application profiles over a shared model.

**My view.** The five-activity distinction is right and useful, and I would adopt its vocabulary.
Representing a recorded outcome is not deciding one, and the `ExaminationOutcome` class comment
("UNPOPULATED, and it must stay that way") blurs the two by citing the rule against deciding as the
reason for not representing. But the uses the framing rests on are not recorded anywhere in this
repository. Its purpose, set by the owner on 7 October, is "a pitch that demonstrates the value of
an ontology for the Trade Marks Manual; a system that works, soon, not every nuance" (ADR-0109); its
scope is D1 to D4 (ADR-0110); the published site and its chatbot are for trade marks examiners; and
the rest of the roadmap is "future state, context only, do not build yet" (`CLAUDE.md` §0). A search
of the repository finds no customer-facing use. If the uses ChatGPT names are the owner's intention,
they change the project's purpose and what the system says to whom, which only the owner can decide
(`CLAUDE.md` §3a). Two of the restrictions it calls permanent are also not the agent's to relax: the
signed prohibited uses PU-0001 and PU-0002 stand as approved knowledge, and no agent may widen the
product's scope (ADR-0082 consequence 4).

So for A01 to A05 and A09 to A11, my verdict on each finding is whether it correctly describes what
is missing for the uses it names, and my verdict on each fix turns on the owner's decision about
scope (decision 1 below). I recommend the demonstrator scope stays for now. ChatGPT's A-series is a
good, specific account of what a production foundation would need next, and that account is itself
worth putting in the pitch.

## Implementation and semantic findings

### R01: exception relationships still overstate their evidence

**ChatGPT says.** The four `isAnExceptionTo` edges describe likelihood or reconsideration rather
than a case a ground does not reach; GR-0699's object loses the section 43 context; GR-0699's and
GR-0700's `applies_when` repeats the outcome rather than stating the circumstance.

**Finding: agree, with one record in part.** I read each record beside its whole chunk.

| Record | Edge | My reading |
|---|---|---|
| GR-0699 | business identifier is an exception to ground for rejection | Right. The sentence is in Part 29, section 43's Part, and says a ground "will rarely apply": a tendency, not an exclusion. The object, GC-0006, is every ground for rejection. The `applies_when` is the outcome clause itself ("A ground for rejection will rarely apply in these cases"), not the circumstance |
| GR-0700 | deceased person is an exception to the section 43 ground | Right, and the evidence is stronger than ChatGPT gives. The span stops at character 195; the same chunk then says "However, a relevant connotation may arise if the deceased person's estate ... has continued to control the use of the person's name/image", and "the more recently they died ..., the more likely". The subject is the signed concept "deceased person", not "long deceased historical figures" |
| GR-0701 | fanciful or ambiguous reference is an exception to likely to deceive or cause confusion | Right. "Deception or confusion is not likely to occur if ..." is the test's own outcome on those facts. It is the closest of the four to an exclusion (a fanciful reference carries no geographical connotation for the test to act on), but the source frames it as likelihood |
| GR-0702 | owner or authorised user is an exception to the section 43 ground | In part. Read with the sentence before it ("A section 43 ground for rejection will apply if the applicant ... is not also the owner (or authorised user) of that phoneword"), being the owner does take the case out of the phoneword ground, so an exception edge is defensible. What is wrong is the evidence, which quotes the reconsideration sentence (a procedural consequence), and the scope: GC-0035 is the generic signed role, so the edge reads as true of any mark |

Two things it missed. First, the predicate dictionary teaches the error: `isAnExceptionTo`'s worked
example in `src/tm_knowledge/ontology/predicates.py` is GR-0700's own sentence, and its definition
admits hedged cases ("as far as the source says and qualified as it qualifies it"). The dictionary is
rendered into the relate prompt, so correcting the records without the entry invites the same
reading next time. Second, `applies_when` holds a hedge rather than a condition on three more
records: GR-0565 ("usually"), GR-0574 ("... will usually have sufficient inherent adaptation to
distinguish") and GR-0608 ("usually the person named in a subpoena").

**Its fix: agree in part.** Agree: re-read each with its adjacent paragraphs; use `qualifies` where
that is accurate; restrict section 43 relations to that ground; keep the exception edge for a source
that excludes a case; keep the replacements unreviewed; add near-miss tests. Disagree: introducing a
likelihood or reconsideration predicate. Eleven predicates already have exactly one use
(`data/derived/reports/ontology.md`), and a predicate per degree of hedging multiplies thin
categories. The degree belongs on the record, beside the condition, where it can be copied verbatim.

**What I would do.**
1. Re-read the four in a restructure ledger, as S036 did: GR-0699 as GC-0020 `qualifies` GC-0168
   (condition "where business identifiers are included in a trade mark", hedge "rarely"); GR-0700 as
   GC-0027 `qualifies` GC-0168, quoting the "However" and "more recently they died" sentences as
   well; GR-0701 as GC-0048 `qualifies` GC-0002 (hedge "not likely"); GR-0702 kept as an exception,
   re-anchored to the conditional sentence plus the reconsideration sentence, with the phoneword
   scope in its condition.
2. Split `applies_when` into a condition (the antecedent, verbatim) and a hedge (the strength word,
   verbatim: generally, rarely, usually, not likely), and move the five hedges.
3. Replace the dictionary's example with a sentence that does exclude a case, for example Part 29.6:
   "If the trade mark application is submitted by the well-known person, ... a section 43 ground for
   rejection does not arise."
4. Add ChatGPT's three near misses as unit tests, and an agent-proposed ADR superseding ADR-0135's
   treatment of the three hedged records.

### R02: some new definitions omit material qualifications

**ChatGPT says.** GD-0146 (adverse report), GD-0050 (capable of distinguishing) and GD-0128
(pending application) each compress or drop a qualification their source states.

**Finding: agree, and it is wider.**
- **GD-0050.** Confirmed: "Section 41 does not apply to certification trade marks" is the sentence
  immediately after the quoted span in `TMM/Part22/1#1`. The hash and span are valid; the
  definition is still wrong for certification marks.
- **GD-0146.** Confirmed: regulation 4.10(3) begins "Unless acceptance of an application is
  deferred". Wider: the narrowing is also in the concept record. GC-0179's notes say the same thing,
  its legislative basis is regulation 4.10 only, and its alternative label is "further adverse
  report"; but the Manual also uses "adverse report" for the first report under regulation 4.8
  (`TMM/Part18/3/3/1/2`: "Reg 4.8 ... requires the Registrar to issue an adverse report to the
  applicant if they reasonably believe that a ground for rejection exists"). The definition fixes
  the concept to its alternative label's sense.
- **GD-0128.** Confirmed: the evidence quotes section 11(1), (a), (b) and (d), and omits (c), refusal
  confirmed on appeal. "Finally refused" also blurs (b), where pendency runs to the end of the appeal
  period.
- **A fourth.** GD-0084 (extension of time) says an extension is granted "under a specific
  provision or the general provision in section 224"; the passage continues "unless the act or
  document has been listed (prescribed) in reg.21.28 as one to which section 224 does not apply".
  The triage below found it.

**Its fix: agree in part.** Agree: keep a short definition apart from obligations, consequences and
steps; add scope notes; show the complete source beside each definition in the review pack; prefer
no definition to an unsupported one. One refinement: for a concept that is itself a ground for
rejection (GD-0049, GD-0054, GD-0055, GD-0139, GD-0148, GD-0149), the rejection is the meaning, not
an added consequence. The rule bites on concepts like capable of distinguishing and adverse report.

I disagree with the method: re-reading the 96 non-verbatim definitions, and the 45 that define signed
concepts, against their complete sources by hand before anything else. The project's rule is
deterministic first (`CLAUDE.md` rule 7), and here it works. I ran three checks over all 149 in
seconds:

- (a) a statutory definition quoting some of a provision's child units but not all of them;
- (b) Manual evidence followed, in the same chunk, by a qualifier ("However", "But", "Unless",
  "does not apply");
- (c) a definition of a concept that is not a ground whose text states an obligation or a
  consequence ("must", "rejected").

(a) and (b) raised six flags: three real omissions (GD-0050, GD-0128, GD-0084), one borderline
(GD-0045) and two false positives (GD-0003, GD-0136). (c) lists ten definitions, GD-0050 and GD-0146
among them, which is the set ChatGPT's separation rule applies to. GD-0146 is caught only by (c), for
its "must"; its narrowing to further reports and the missing "unless deferred" are in the Regulation
and in the Manual's usage elsewhere, which no check over the quoted passage can see. That is the case
for ChatGPT's own suggestion of putting the concept's legislative basis beside each Manual
definition in the review pack.

**What I would do.** Make (a) to (c) harness notes, so every future definition is triaged too. Then
re-read what they flag, the three ChatGPT names, GD-0084, and the 45 definitions of signed concepts
(a reader may assume a signed concept's definition is signed). GC-0179 is a machine-written
concept, so its notes and legislative basis are re-read with GD-0146 in the same pass.

### R03: the RDF export loses definition evidence detail

**ChatGPT says.** The 149 `tmk:Definition` nodes have no exported span, hash or quote for their 230
evidence items, and eight referenced source nodes are missing from the source graph.

**Finding: agree, and it is wider.** Confirmed: 230 evidence items, none with span, hash or quote in
the graph; eight dangling refs (two for GD-0060, one for GD-0112, five for GD-0138), because
`build.py` adds only relationships' `source_ref` to the source graph beyond what chunks cite. But
the loss is not specific to definitions. `_origin` writes only `tmk:sourcePassage` for each evidence
item of every authored record; span and hash are written only for a relationship's single
top-level `source_ref`. So concepts (155 evidence items), typings (202), corrections (47) and
definitions (230) all export without span, hash or quote: 634 items. The 337 relationships are the
only nodes that keep theirs. D1's own done-test says "every machine-written record carries its
envelope", and rule 8 lists the source span as part of it; in the RDF, most records do not.

Nothing in the repository reads evidence from the RDF today (the explorer and the harness read the
record files), so the harm falls on someone who loads the graph into a standard tool, who for a pitch
about ontologies is the audience most likely to try.

**Its fix: agree.** One evidence-anchor node per evidence item (ref, span, hash, quote, and the
snapshot or compilation it was read from), linked from the record, built once in `_origin` so every
store gets it; and a source graph closed over every store's evidence refs. Two implementation notes:
mint the anchor IRIs from the record's own IRI (for example `.../assertion/GD-0050/evidence/1`) and
record the pattern in `docs/IDENTIFIERS.md`; and keep `tmk:sourcePassage` on the record as the
navigation shortcut, so the competency queries and RULE-0002 keep working unchanged. The round-trip
test and the definition-only fixture are right.

### R04: validation misses a new record type and an inference inconsistency

**ChatGPT says.** The authored-envelope shapes target `tmk:AuthoredAssertion`; a `tmk:Definition`
with its author and sources deleted validates with zero defects. RULE-0001's reified object is the
chunk, but the emitted triple's object is `true`.

**Finding: agree, and it is wider.** Both reproduce through `validate.run` on the committed
`Dataset`: deleting `authoredBy`, `sourcePassage`, `authoringReasoning` and `defines` from GD-0001
leaves 0 defects; 5 of the 192 inferred assertions fail the equality check, all RULE-0001. Missed: a
correction (`tmk:Correction`, also a subclass of `tmk:Assertion` rather than `AuthoredAssertion`)
passes the same way. I deleted GK-0001's author, date, reasoning and sources and validation still
conformed. The 37 corrections are the records that change what 36 signed records serve, so an
unlabelled one is the more serious gap. `graph/README.md` says of authored nodes that "a SHACL shape
refuses one that does not" carry the envelope; for definitions and corrections it does not.

**Its fix: agree.** The cheapest correct form is to add `tmk:Definition` and `tmk:Correction` as
further `sh:targetClass` values on `AuthoredAssertionShape` and `AuthoredEvidenceShape` (a shape may
have several), plus a small Definition shape for `defines`, text, basis and, after R03, its anchors.
Correct RULE-0001's `assertionObject` to `true` (it is a candidate rule, so the agent may), add the
equality check in both directions, and test it all through `validate.run` on a `Dataset`, not
pySHACL on a flat graph (the lesson of the first review's F02).

### R05: change impact omits current authored dependencies

**ChatGPT says.** RULE-0002 traverses only the approved graph, so no definition is a dependant and
all 15 corrected signed records are; the explorer's `stability` builder is broader but skips
definitions; the two answer different versions of the same question.

**Finding: agree.** Confirmed: RULE-0002's 142 dependants include all 15 corrected signed
relationships and no `GD-` record; `explorer.build.stability` gathers concept and typing evidence,
each relationship's single `ref` and the mention index, and no definitions or corrections. Both start
from a Manual chunk, so neither starts from a provision. The only route from an amended section is
CQ-0017, which is fixed to section 43 and counts the Manual passages citing it by Part; it names no
concept, relationship or definition. That matters because the pitch pack's fifth claim is that "an
amendment to a section reaches the passages, concepts and connections that rest on it".

Two mitigations it does not weigh. The harness's staleness check compares every evidence item's
hash with the pinned snapshot, definitions included (ADR-0137), so once a changed source is pinned,
a stale definition is found; what is missing is the forward view ("what would this change touch?"),
not detection. And RULE-0002's limits line already says a nil result is not "nothing is affected".

**Its fix: agree in part.** Agree: one dependency index over every evidence item and record type,
with record id, type, review status, source version and reason; an effective-current view and a
separately labelled historical one; "no recorded impact", never "no impact"; RDF and browser
agreeing. Disagree with doing it through RULE-0002 or through the RDF first. RULE-0002 is approved
by the owner for its stated scope (OQ-0004); widening it would be a different rule, needing its own
approval. And the RDF cannot carry the dependency until R03 lands.

**What I would do.** One Python function, reading the stores the way the staleness check does (reuse
it), keyed by any ref (chunk, provision or unit), feeding `explorer.stability` (adding definitions,
corrections and provisions) and a generated report. Keep RULE-0002 as it is, labelled "signed records
only". A SPARQL rule over authored records can follow R03 as a candidate if the owner wants one in the
graph. Until this is done, correct the pitch's fifth claim.

### R06: executable competency queries do not always answer their questions

**ChatGPT says.** CQ-0009 returns GR-0005 and GR-0052, neither a required element; CQ-0024 counts
modalities rather than answering whether a statement is a requirement or practice. Define an answer
contract for each question and test against expected results.

**Finding: agree.** Run against the committed dataset: CQ-0009 returns GR-0005 (`excludesBasis`, its
object unlabelled) and GR-0052 (`extendsTo`); CQ-0024 returns counts (9 must, 5 may, 1 should, 5
with none) and no authority column.

What it missed: **the answer contract already exists, and it is signed.** Each record in
`eval/gold/competency-questions.yaml` carries `expected_sources` (required and supporting),
`expected_concepts` and an `answer_shape`, approved by the expert on 25 August 2026. CQ-0009's says
"Must present the criteria as a set that must all be met, must include the mitigating-elements
criterion", and names `TMM/Part29/9/9/3~1` as required; the query returns neither. CQ-0024's says
"Must separate what the Act requires from what the Manual records as practice".

**Its fix: agree in part.** Agree: a reviewed-only answer and an effective-current answer, kept
apart; the report's measure relabelled "queries implemented"; CQ-0012's refusal kept. Disagree with
writing expected-result fixtures: an agent writing the expected answers to its own queries is machine
output grading machine output, which is the circularity ChatGPT itself warns against in A12.

**What I would do.** Test each query against its own signed record: the rows' sources include the
required sources, the expected concepts appear, and whatever of the answer shape a query can show
(an authority column for CQ-0024). Where the signed graph cannot meet the contract (for CQ-0009,
GR-0008 was corrected away by GK-0017, so no signed record states the elements), the query says so,
and an effective-current variant over the authored graph returns the machine-written records,
labelled unreviewed. Report an unmet contract as a gap in the ontology report, as the harness reports
gaps, rather than as a failing or skipped test.

### R07: conditions need an explicit representation and consumption contract

**ChatGPT says.** Only 26 of 337 authored relationships carry `applies_when`, and "no condition
needed" cannot be told from "not assessed"; the builder emits an unconditional direct edge beside a
conditional reified one.

**Finding: agree.** 26 of 337 confirmed. To size "not assessed": of the 311 without a condition, 103
have a conditional marker ("if", "where", "unless", "when", "except") in their supporting sentence.
That is a crude count and overstates, but it shows the gap is not small. And five of the 26 hold a
hedge or an outcome rather than a condition (R01). GR-0319 and GR-0206 are as described: the
non-use proceeding and the "if it wishes to continue" condition are not on GR-0319, and the
mark-type and colour context is not on GR-0206.

**Its fix: agree in part.** Agree: the qualified assertion is the legal reading and the direct edge a
navigation projection; an assessment state; negative examples for the risky predicates. ADR-0134
already licenses no inference from the direct edges; say so plainly in `graph/README.md` and the
header of `relations.ttl`. Where I differ is how the state is set and where the context comes from.

**What I would do.** Set the state by rule where a machine can: no conditional marker in the
sentence gives `none_stated` (a fact about the sentence, not a legal judgement); a marker and no
condition gives `not_assessed`; then the agent assesses the hundred or so flagged. Split hedge from
condition (R01). Derive the proceeding from the source Part with a small lookup table rather than
hand-writing it on each record, and hand-write it only where a Part covers several proceedings. Add a
mark-type field only when a question needs one.

### R08: the authority detector is a warning heuristic

**ChatGPT says.** The detector catches "the Act requires" with only Manual citations, but any
citation of the named section clears it, a generic "the Act requires" with a section 6 citation
passes, and naming the Manual exempts a sentence.

**Finding: agree, and it is wider.** All three reproduce. Two more misses: a negation anywhere before
the match suppresses the flag ("The legislation does not say anything else, but section 41 requires
use evidence" passes with no citations), and phrasing outside the verb list is never examined
("Under section 43 the connotation must be obvious, direct and immediate"; "It is a legal requirement
that ..."). The module's docstring already calls the check "deliberately narrow"; the overstatement
is in the pitch pack ("It keeps the law and the practice apart at every point").

**Its fix: agree.** Document what a clean result means; add the adversarial cases as tests that
record the known misses; soften the pitch's wording. Claim-level anchoring belongs with A08 and
should be done there. Two cheap tightenings worth making in both engines: apply the Manual exemption
only when the legislative verb is attributed to the Manual in the same clause, and the negation check
only within the matched clause. It stays a warning.

### R09: existing measurements do not establish a retrieval advantage

**ChatGPT says.** Ontology expansion beat keyword search but trailed hybrid search; the expert's
ten-question check shows no dependable difference; the browser reading did not beat keyword search.
Keep the strongest baseline, test ablations, measure other benefits separately, freeze questions
before tuning.

**Finding: agree in part.** Every number in its table matches `measure.md` and `measure-reading.md`
at their commits. The headline does not: the measurements do establish one advantage, over keyword
search (ontology minus keyword +0.079 [+0.042, +0.116] on all 129 questions, +0.201 on the problem
questions), which is the first of the two claims the owner chose for the pitch (OQ-0029). They do not
establish one over hybrid. ChatGPT's own first row says so; its title does not.

**Its fix: agree,** with two owner gates. Re-measurement is deferred by the owner until more re-work
is done (CHAT-0084), and who writes and judges a new benchmark is the owner's to choose (`CLAUDE.md`
§3a); examiner-authored questions would need the examiners. The ablations it suggests are the
handoff's first next action (hub concepts entering expansion, ties broken by ref order), designed
before measuring and never tuned on the benchmark. Measuring tracing, cross-Part navigation and
impact separately is right.

### R10: coverage and source currency need clearer boundaries

**ChatGPT says.** The source graph holds 42.8% of chunks; five Parts are absent and seven have no
authored relationship; the Manual capture predates the Act compilation; case nodes are references;
21 legislative bases are unverified.

**Finding: agree.** All reproduce: 1,053 of 2,460 chunks; Parts 1, 4, 8, 41 and 61 absent, Parts 7
and 45 also without an authored relationship; the Manual captured on 3 August 2026, the Act at
compilation 48 (in force from 19 September 2026), the Regulations at compilation 53 (from 18 December
2025); 21 unverified bases (the handoff says 22; the harness, which is right, says 21).

**Its fix: agree.** One generated table by Part (searchable, in the graph, concepts, relationships,
definitions, reviewed) is the handoff's third next action. Answers already name the compilation they
read; add the Manual's capture date beside it, and say on the About page that a Manual captured on 3
August 2026 may not reflect compilation 48. Reconciling the two is for the examiners at the
end-of-work review (ADR-0120), not an agent. The 21 bases are agent work: re-cite each from a quoted
passage, or mark it unresolved.

## Foundations for the intended uses

Read these with the framing section above: each finding is judged as a description of what those
uses would need; each fix is judged against this project's recorded scope.

### A01: model the matter and each objection, not only the vocabulary

**Finding: agree.** `TradeMarkApplication`, `Examination` and `Objection` are unpopulated. `tmk:Role`
is described as "a person, office or body", while `examination.ttl` (lines 210 to 212) declares
offices, delegates, parties and representatives disjoint. Once individuals are typed, an attorney
applying in their own name (party and representative) or an examiner filing a personal application
(delegate and party) is a contradiction. It is latent: no individuals exist and no OWL inference is
licensed (ADR-0134).

**Its fix: agree in part.** Not the matter model now; that is the scope decision. The role point is
worth fixing now in its cheap form: say in the class comments that a role is a capacity, not the
person who holds it, and either scope the disjointness to capacities or drop it (no check uses it).
If the owner adopts customer explanation, ChatGPT's minimal shape (sign, application, goods and
services items, report, objection with its ground, affected items and disposition, and a role
assignment scoped to a matter and time) is the right one, tested on fictional data.

### A02: represent process stages, events and conditional response paths

**Finding: agree.** There is no transition model; three `precedes` and two `suspendsTimeFor` edges
are the extent of it.

**Its fix: disagree, for now.** For the examiner use, "what does the Manual say happens next" is
answered from the passages and those edges. If the owner adopts customer guidance, a template from
regulations 4.8 to 4.10, separate from any matter's events, is a sound first slice, and it must keep
the owner's rule that the procedural spine is not made binary (ADR-0105, ADR-0106).

### A03: make applicability and meaning depend on context and time

**Finding: agree.** `time.ttl` excludes point-in-time questions and holds one compilation per
instrument; ADR-0137 allows one definition per concept (`tmk:defines` is declared functional).

**Its fix: agree in part.** Now: show the Manual's capture date beside the compilation (R10), so a
reader sees the gap between them. Later, when a dated question is in scope: versioned text,
applicability intervals, transitional rules, OWL-Time for the primitives. Several scoped definitions
only where a question needs them; the owner postponed splitting "application" by sense (CHAT-0025),
so scope notes stay.

### A04: introduce structured legal tests alongside conceptual relationships

**Finding: agree.** Binary edges with a modality and a free-text condition cannot hold conjunctions,
alternatives, exceptions with priority, or discretion.

**Its fix: disagree, for now.** Representing defeasible rules (LegalRuleML) is deferred by ADR-0009
and listed in `CLAUDE.md` §6 as not done here; reversing that is the owner's. Two of its principles
matter today and cost nothing, and both are already in force: an unknown fact is not a false one (the
`answer-v3` rule against concluding absence, ADR-0136), and a discretion is not an obligation (the
first review's work on "may"). Keep them in the answer rules; do not build a norm layer.

### A05: separate case evidence, factual claims and assessed conclusions

**Finding: agree.** The four evidence classes are unpopulated and nothing links an exhibit to a
claim, an issue and an assessment.

**Its fix: disagree, for now.** No case evidence is in scope or held, and the evidentiary-proposition
boundary in `evidence.ttl` is honest for a vocabulary over the Manual. If the uses are adopted,
ChatGPT's chain (evidence item, the claims it supports or challenges, its period and goods, and a
separate assessment naming who made it) is right, and the section 41(3) and 41(4) evidence-of-use
example is a good first fixture.

### A06: retrieve complete legal context, not fixed-length passage prefixes

**Finding: agree; the most important of the A-series, because it affects the examiner chatbot
today.** Reproduced through the repository's loader: section 44 is 3,785 characters; subsection (3)
starts at 2,390 and (4) at 2,962; both are cut by the 1,600-character limit
(`explorer/build.py` line 729, `bulk/jobs.py` lines 1117 and 1122, `site/js/engine.js` line 260). They
are the honest concurrent use and prior continuous use carve-outs, the exceptions to (1) and (2),
and the `s44(1)` unit opens "Subject to subsections (3) and (4)". So a live answer about section 44 is
written from the rule without its exceptions, and the rule against concluding absence cannot help,
because the model never sees them. 372 of 2,460 chunks and 101 of 763 provisions exceed the limit.

**Its fix: agree in part.** Agree: complete units, disclosed omissions, a regression fixture for
section 44 and one for an exception on another page. Disagree that a general context-bundle model is
needed first. The sizes make a simpler fix sufficient: the median provision is 576 characters, 90%
are under 1,800 and only 10 exceed 4,000.

**What I would do.** In `jobs.py` and `engine.js` together (a test holds them identical):
1. give legislation whole up to a budget (say 6,000 characters), and for the few larger provisions
   the matched units plus any unit a lead-in names ("Subject to subsections (3) and (4)");
2. cut a long Manual chunk around the match rather than from its start (`passage_block` already takes
   `around`; answers do not use it);
3. mark every cut, in the prompt and on the page ("subsections (3) and (4) not shown");
4. add the section 44 fixture.

This changes what the live chatbot is given, so it goes to the owner with A08 (decision 2). The 129
prepared answers were written from cut passages; re-writing them costs money and the cap is spent, so
they should say so (decision 3).

### A07: broaden source access while preserving proposition-level authority

**Finding: agree.** `KeywordIndex` indexes Manual chunks only. Legislation reaches an answer only as
a recognised concept's legislative basis or a provision one of the top three passages cites
(`Engine.prepare`). Cases are held at citation level; no customer guidance is held.

**Its fix: agree in part.** Agree, now: exact-reference lookup ("section 44(3)", "reg 4.10" to the
unit) and keyword search over the 763 held provisions beside the Manual. Both are deterministic and
cheap; both change the measured system, so label them unmeasured until the next measurement.
Disagree, for this repository: a register and ingestion of judgments, customer pages and forms.
Crawling and extraction are upstream's (`CLAUDE.md` rule 2 and §6), judgment text exists nowhere in
the programme (Q-11), and customer pages serve a use not in scope. Its points about cases (the
Manual's account of a case is not the judgment; quoted, paraphrased and inferred differ) are right
and partly encoded already (`statedIn`, `attributedTo`).

### A08: make support verifiable for each claim before displaying the answer

**Finding: agree.** Confirmed by reading the code: the answer schema is one string and a citation
list; `Engine.verify` checks each quote against `this.text(ref)`, the full stored text, not the
excerpt the model was given; an empty list returns nothing kept and nothing dropped, with no warning;
`ask.js` streams the answer as it arrives and, after checking, shows the same text with the kept
citations and a note that others were removed.

**Its fix: agree in part.** Agree with four changes, all deterministic and cheap: verify against the
excerpt actually sent; return claims, each with its own quotes, so a failed quote marks its claim
rather than vanishing from the list; show a claim with no surviving quote as unsupported, and an
answer with none as "no checked support"; stream as a visibly unchecked draft. Disagree, for now,
with a model-judged support check (does this quote support this sentence): it is a paid call per
answer, its own accuracy is unmeasured, and the cap is spent. Say instead, on the page, that the check
proves a quote exists in the passage, not that it supports the sentence. Reviewed explanation
templates belong to the customer track. The schema change alters what the live chatbot is told, so it
goes to the owner with A06, as the path-line change did (CHAT-0080).

### A09: build customer explanations and visuals from a shared explanation model

**Finding: agree in part.** Accurate that there is no customer task or context contract, but the
answering instructions target an examiner by design: the site and its chatbot are for examiners. The
one point that applies now is its distinction between "why this was retrieved" and "why this
proposition is supported"; the Ask page's trace explains retrieval scoring and should never read as
support.

**Its fix: disagree, for now.** The owner's decision (decision 1). If adopted, its three views (an
issue card, a conditional timeline, an evidence-to-issue view), each with a text equivalent, and its
insistence on testing comprehension with customers, are sensible.

### A10: separate dependency analysis, legal scenarios and real-world policy effects

**Finding: agree.** "Which guidance needs review?", "would this matter be treated differently?" and
"how would applicants behave?" are different questions, and connectivity answers only the first.

**Its fix: agree in part.** Agree with the distinction; build only the first now (R05). Normative
scenarios need A03 and A04; behavioural effects need data nobody holds. Put the distinction on the
pitch's limits page, so "what would this change touch" is not heard as "what would this change do".

### A11: create versioned reuse contracts for ML and other downstream consumers

**Finding: agree in part.** No downstream consumer exists. ChatGPT's own section 7 says namespace
publication and alignment "can wait until there is an external consumer with a concrete need", which
is equally true here. Its evidence of drift between interfaces (hierarchy links, definitions) was
found and fixed in S039.

**Its fix: agree in part.** A small `build.json` on the site and a matching graph header (commit, pin,
compilations, counts by review state) are cheap and useful for the pitch. R03 is the real
precondition for any RDF consumer. Its rules for training data (split by matter and time, no
later outcomes in earlier features, keep the frozen benchmark) are right, and there is nothing yet to
apply them to.

### A12: test the intended tasks, including missing and conflicting information

**Finding: agree.** Query execution, connectivity and quote matching do not show that an examiner
found the governing qualification.

**Its fix: agree in part.** Agree with task-level fixtures, abstention counted as success, and
release-blocking fixtures that an average score cannot hide. Two constraints: who writes and judges a
benchmark is the owner's (`CLAUDE.md` §3a), and expert-reviewed fixtures wait for the examiners'
review at the end (ADR-0120). What an agent can add now, deterministic and labelled unreviewed: the
section 44 context fixture (A06), the unsupported-claim display (A08), the compilation named on every
answer, the absence rule; and, of its scenarios, those inside the examiner demonstrator (the section
44 bundle, ambiguous everyday wording, conflicting sources, a missing judgment). Multiple objections,
transitions, evidence periods and amendments belong to the customer and policy tracks.

## Other points in the review

- **Stale documents (its section 7): agree; fix now.** `graph/README.md` says the authored graph "is
  empty today" (it holds 16,107 triples) and that a shape refuses an authored node without its
  envelope (not for definitions or corrections, R04). `eval/README.md` still says an agent "must not
  author" legal judgements, citing a rule 1 that now says the opposite, and frames Stage 0 as the
  blocker.
- **Predicate boundaries (section 7): already largely done.** Every predicate in `predicates.py`
  carries a definition, a reading, an example, a counter-example, an authority and the kinds it
  joins (ADR-0123, ADR-0131). The gap is the eleven singletons' thin use, not missing statements.
- **A register of empty classes (section 7): agree, low priority.** The ontology report already lists
  the 53; a status column (populated, structural, reserved) is a small addition.
- **Strengths to preserve (section 4): agree** with all of them, and with keeping RDF, SKOS, SHACL
  and bounded SPARQL rules rather than unrestricted OWL.

## What the review missed

1. **Corrections share R04's validation gap.** All 37 can lose their author, date, reasoning and
   sources without a defect.
2. **R03 spans four record types and 634 evidence items**, not one type and 230.
3. **The signed competency-question records already hold the answer contract** R06 asks for.
4. **The predicate dictionary's example for `isAnExceptionTo` is GR-0700's sentence**, and it is
   rendered into the relate prompt.
5. **A fourth definition omits a qualification** (GD-0084), and **GD-0146's narrowing is in its
   concept record** too (GC-0179).
6. **Three of the pitch pack's six capability claims say more than the implementation.** Claim 2
   ("keeps the law and the practice apart at every point") rests on a heuristic (R08); claim 4
   ("quotes the passage it rests on with an exact span and hash") is true in the record files and on
   the site, but not in the RDF for anything but relationships (R03); claim 5 ("an amendment to a
   section reaches ... what rests on it") has no view that starts from a provision; CQ-0017 counts
   the passages citing section 43 and names no record (R05). The owner has seen this pack (D4's done-test), so these should be
   corrected and the owner told.
7. **Two more authority-detector misses** (an earlier negation; phrasing outside the verb list).
8. **Five conditions are hedges** (GR-0565, GR-0574, GR-0608, GR-0699, GR-0700).
9. **The section 44 cut removes exactly the exceptions**, which the answer rule against concluding
   absence cannot repair, because the model never sees them.

## Recommended order of work

**Package 1: the records and their checks** (agent, no spend, about one session). R04 (shape targets
including corrections, a Definition shape, RULE-0001 and the equality check); R03 (evidence anchors
for every record type, source closure); R01 (the four re-reads, the hedge field, the dictionary
example, an ADR superseding ADR-0135's reading); R02 (the triage as harness notes, then the flagged
re-reads and GC-0179); R07 (the condition state set by rule); the stale READMEs; the role comments
(A01) and the `ExaminationOutcome` comment's reason. Then `tmk-graph --write --rules` and
`tmk-ontology-report --write`.

**Package 2: what is served and what is claimed** (agent, no spend, about one session). R05 (the
dependency index; the change view gains definitions, corrections and provisions); R06 (each query
tested against its signed record; CQ-0009 and CQ-0024 rewritten); R08 (documented limits, tests, the
two tightenings); R10 (the coverage table, the Manual's capture date); A07 (exact-reference lookup
and provision search, labelled unmeasured); the pitch pack's claims 2, 4 and 5 made accurate.

**Package 3: the live chatbot, after decision 2.** A06 and A08 together in `jobs.py` and
`engine.js`, as a new answer version; the prepared answers labelled as written from cut passages.

**Package 4: the owner's decisions** (next section).

## Decisions for the owner

1. **Does the project's purpose widen?** ChatGPT writes as though the ontology must now serve
   customer explanations of objections and the application process, and later ML, decision services
   and policy simulation. The repository records a pitch demonstrator for examiners (ADR-0109,
   ADR-0110). I recommend keeping that scope now, and putting the A-series in the pitch as what the
   foundation would need next. If you want one customer-style demonstration in the pitch, a single
   fictional slice (a report with two objections, the regulations 4.8 to 4.10 template) after
   packages 1 to 3.
2. **Approve two changes to what the live chatbot is given and how its answers are shown**: complete
   legislative units with every cut marked (A06); and claims carrying their own quotes, checked
   against what was sent, unsupported ones marked, streamed as an unchecked draft (A08).
   Recommended.
3. **The 129 prepared answers were written from cut passages.** Leave them, labelled (recommended; no
   spend), or name an amount to re-write them at the next measurement.
4. **When re-measurement comes** (deferred, CHAT-0084), who writes and judges the new questions:
   R09 and A12 ask for examiner-written cases and near misses, which would need the examiners.

## How to repeat the checks

The probes were scratch scripts and are not committed; each is a few lines. After
`pip install -e ".[rdf,test]"` and `tmk-fetch-upstream`:

- **R01, R02**: print each record beside its full chunk (`load_corpus().chunks[ref].text`) or
  provision (`corpus.resolve_provision(ref).text`); for GD-0146, the units of `TMR1995/r4.10`.
- **R02 triage**: for each definition, (a) compare its cited child units with
  `[k for k in corpus.units if k.startswith(parent + "(")]`; (b) match the 200 characters after each
  Manual span against a qualifier pattern; (c) search the text of non-ground definitions for "must"
  or "rejected".
- **R03**: in `graph/dataset.nq`, list the predicates on `tmk:Definition` nodes; for every authored
  node with `tmk:sourcePassage`, whether it also has `tmk:spanStart` and `tmk:sourceContentHash`;
  definition `sourcePassage` targets with no triple in the source graph.
- **R04**: remove `authoredBy`, `sourcePassage`, `authoringReasoning` and `defines` from GD-0001 (and
  author, date, reasoning and sources from GK-0001) in the loaded `Dataset` and call
  `ontology.validate.run(dataset)`; for each `tmk:InferredAssertion`, test whether its subject,
  predicate and object form a triple in the inferred graph.
- **R05**: the subjects of `tmk:impactedBy` in the inferred graph against the approved nodes with
  `tmk:isCorrected true`.
- **R06**: run `queries/competency/CQ-0009.rq` and `CQ-0024.rq` over the dataset; compare with the
  records in `eval/gold/competency-questions.yaml`.
- **R07**: count authored relationships with `applies_when`, and those without whose
  `supporting_text` matches `\b(if|where|unless|when|except)\b`.
- **R08**: `search.authority.conflations(text, cited)` on the sentences quoted above.
- **A06**: offsets of `(3)` and `(4)` in `corpus.provisions["TMA1995/s44"].text`; counts of chunks
  and provisions over 1,600 characters; the length distribution of provisions.
- **A07, A08**: `KeywordIndex.__init__` in `search/index.py`; `prepare`, `prompt` and `verify` in
  `site/js/engine.js`; the streaming and `showAnswer` call in `site/js/ask.js`.

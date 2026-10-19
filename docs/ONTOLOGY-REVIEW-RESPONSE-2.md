# Ontology review response 2

**As at:** 2026-10-19 · session S040 · responding to `docs/Trade-Mark-Ontology-Consolidated-Review.md`
(written by ChatGPT, dated 18 October 2026, about commits `3ecf410` and `e6985e9`)
**Revised:** the same day, after the owner stated the ontology's purpose (CHAT-0085, ADR-0138). The
first version (commit `8d4c6ef`) judged the A-series against the purpose then recorded, a pitch
demonstrator; this version judges every finding against the purpose the owner has now stated.
"What changed from the first version" lists each verdict that moved.
**Checked against:** `c6a0f0e`, which differs from `e6985e9` only by the review file, with the pinned
snapshot `308bfd9` (the Act at compilation 48)
**Written by:** an agent (Claude Code), at the owner's request. Machine-written and reviewed by no one;
every judgement in it is the agent's and can be wrong.
**Changed:** no record, graph, query, prompt, shape or page. No paid model call was made. Every
number below was re-run in this session with the library versions ChatGPT used (rdflib 7.6.0,
pySHACL 0.40.1).

The task: for each problem ChatGPT identified, say whether it is right; where it is, say whether its
proposed fix is right; and where the fix is wrong for this project, say what should be done instead,
and why.

## The purpose this response judges against

In the owner's words (ADR-0138): *"The ontology is being written to operate as a foundational layer
for any future machine learning, machine decision making, customer service delivery or policy
writing aid (simulating flow on affects of amendments). In the immediate, for examiners, it must
operate as a research and decision-support tool, helping them quickly identify relevant sections of
guidance, legislation and related material. The immediate use case for IP Australia's 'customers' is
about improving understanding of trade mark requirements, the application process and objections
raised during examination (likely an LLM driven chatbot with clear visuals for explainability)."*

So there are two immediate users (examiners researching; customers trying to understand) and four
future consumers (machine learning, decision services, customer service, policy simulation) that the
foundation must not preclude. The rules that do not change: no system states an examination
outcome; the Act and the Manual stay distinguishable everywhere; what a machine wrote is never
mistaken for what a person signed. A future "machine decision making" use means the foundation must
be able to represent a recorded decision; it does not license any product here to make one.

## In short

- **The technical findings are accurate, and against the stated purpose all 22 stand.** I re-ran
  every probe ChatGPT describes, read each cited record beside its full passage and the provision
  behind it, and checked every count. In four places the problem is wider than reported (R02, R03,
  R04, R08). One headline needs a correction (R09), which does not change the verdict.
- **Fixes: I agree with 17 and with 5 in part. I disagree with none.** In the first version I
  disagreed with four (A02, A04, A05, A09), each for one reason: "not now; outside the recorded
  scope". The owner has removed that reason. What remains are five genuine differences of method,
  where a deterministic check, a signed yardstick or a simpler mechanism does the job better (R01,
  R02, R06, R07, A06).
- **My main difference with ChatGPT now is order, not content.** It recommends starting the matter,
  process, test and evidence models in parallel with the repairs. I would design them in parallel
  but populate them only after the repairs, because an explanation of a section 43 objection is
  composed from exactly the records R01 and R02 show to be overstated. Built first, those errors
  would reach customers in plain language.
- **Two defects in the examiner chatbot come first, because they will carry into any customer
  chatbot built the same way.** A06: the 1,600-character cut removes exactly the exceptions in
  section 44 (subsections (3) and (4) start at characters 2,390 and 2,962). A08: the citation check
  runs against the full stored text rather than the excerpt the model saw, an answer with no
  citations passes silently, and dropping a bad citation leaves its sentence on the page.
- **It missed some things.** The 37 correction records share the definitions' validation gap (R04);
  the RDF drops span, hash and quote for 634 evidence items across four record types, not 230 in one
  (R03), which matters now that downstream consumers are a stated use; and the signed
  competency-question records already contain the answer contract R06 asks someone to write.
- **Almost all of the work is agent work that costs nothing.** The two decisions it put to the owner
  were approved on 2026-10-19 (ADR-0139); four gates are named for later.

## Verdicts at a glance

| # | ChatGPT's finding, in plain English | Finding | Its fix | What I would do |
|---|---|---|---|---|
| R01 | Four "is an exception to" edges overstate their sentences | Agree | In part | Re-read three as `qualifies`, re-anchor the fourth; a hedge field, not new predicates; fix the predicate's own example |
| R02 | Three definitions drop a qualification their source states | Agree, wider | In part | Deterministic triage of all 149 first, then re-read what it flags |
| R03 | The RDF loses the definitions' evidence detail | Agree, wider | Agree | One evidence-anchor node per evidence item, for every record type |
| R04 | Validation skips definitions; RULE-0001's record is wrong | Agree, wider | Agree | Add the targets (corrections too); fix RULE-0001; an equality check |
| R05 | Change impact misses machine-written records and definitions | Agree | Agree | One dependency index, keyed by any ref; RULE-0002 left as the signed-only view |
| R06 | Competency queries do not answer their questions | Agree | In part | Test each query against its own signed record, which already holds the contract |
| R07 | Conditions are rare, and "none" cannot be told from "not checked" | Agree | In part | Set the state by rule where a machine can; split hedge from condition; proceeding from the Part |
| R08 | The authority check is a heuristic | Agree, wider | Agree | Say so, test its misses, tighten two rules |
| R09 | The measurements do not establish a retrieval advantage | Agree, with a correction | Agree | Keep the best search as the baseline; add the ontology to it |
| R10 | Coverage and source currency need clearer boundaries | Agree | Agree | One coverage table by Part, and the Manual's capture date beside the compilation |
| A01 | No model of a matter, its objections or role assignments | Agree | Agree | A minimal schema and fictional fixtures, after the repairs; roles as capacities now |
| A02 | No process or event model | Agree | Agree | One template, regulations 4.8 to 4.10; explain deadlines, do not compute them |
| A03 | Applicability does not depend on context or time | Agree | Agree | Define identity and version now; select versions when a second one is held |
| A04 | No structured legal tests | Agree | Agree | Test records as data for sections 41, 43 and 44, within ADR-0009 |
| A05 | No model of case evidence and assessments | Agree | Agree | General evidence requirements from the Manual first; case evidence as schema only |
| A06 | Passages are cut at 1,600 characters | Agree | In part | Whole provisions and marked cuts now; the context bundle drawn from A04's test records |
| A07 | Legislation is not directly searchable; cases are citations only | Agree | Agree | Exact-reference and provision search now; customer pages and judgments captured upstream |
| A08 | Support is not verified claim by claim | Agree | Agree | Claims with their own quotes, checked against what was sent; a support check before any customer release |
| A09 | No customer explanation model | Agree | Agree | Intents, context slots and three views built on A08's explanation object |
| A10 | Dependency, scenarios and real-world effects are different questions | Agree | Agree | Build the first (R05) now, the second once A03 and A04 exist |
| A11 | No versioned contract for downstream consumers | Agree | Agree | A release manifest and full provenance in every export (R03 first) |
| A12 | Tests do not cover the intended tasks | Agree | Agree | Task fixtures for both users, abstention counted as success; owner gates named |

## What changed from the first version

| # | First version (finding / fix) | Now | Why |
|---|---|---|---|
| R05 | Agree / In part | Agree / Agree | A dependency index is the first layer of the policy aid (A10); my one reservation (leave the approved RULE-0002 alone) is an implementation note, not a disagreement |
| R09 | In part / Agree | Agree / Agree | For an examiner research tool the comparison that matters is the best search, not keyword search; against that, ChatGPT's headline is right |
| A01 | Agree / In part | Agree / Agree | Explaining an objection a customer received needs its ground, affected goods and options |
| A02 | Agree / Disagree | Agree / Agree | "The application process" is a stated immediate customer use |
| A03 | Agree / In part | Agree / Agree | Policy simulation is a stated future use; the model must be defined now |
| A04 | Agree / Disagree | Agree / Agree | Explaining an objection, and later deciding and simulating, need tests as structure; ADR-0009 already allows it as data |
| A05 | Agree / Disagree | Agree / Agree | Evidence of use is one of the commonest objection responses a customer must understand |
| A07 | Agree / In part | Agree / Agree | Examiner research needs legislation and cases found directly; customers need official guidance |
| A08 | Agree / In part | Agree / Agree | A customer-facing answer must not show an unsupported claim as supported; a support check is owed before release |
| A09 | In part / Disagree | Agree / Agree | The customer explanation aid is now D4 |
| A10 | Agree / In part | Agree / Agree | Simulating flow-on effects of amendments is a stated future use |
| A11 | In part / In part | Agree / Agree | Machine learning and decision services are stated future consumers |
| A12 | Agree / In part | Agree / Agree | Customer tasks are now in scope; the gates remain, as process, not disagreement |

Everything about the pitch pack is removed: the owner has left it to go stale (CHAT-0086).

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

## The review's framing

**ChatGPT says** (its sections 1 and 2). The model should distinguish representing a recorded
decision, explaining a rule, evaluating a hypothetical, predicting an outcome and making a decision,
and serve each user through an application profile over one shared model (examiner research,
customer explanation, policy scenarios, ML and decision services). The `ExaminationOutcome`
restriction and the exclusion of point-in-time questions are inappropriate as permanent
restrictions on a foundation.

**My view: agree.** With the purpose stated, this is the right frame, and it fits the rules that
stay. "Never state an examination outcome" is a rule about what a product says; it does not forbid
the foundation from representing an outcome someone recorded, which future ML needs. The
`ExaminationOutcome` class comment ("UNPOPULATED, and it must stay that way") cites the rule against
deciding as the reason for not representing, which conflates the two; it should say instead that no
outcome is ever generated, and that a recorded one may be represented once case data is in scope
(an owner gate). The signed prohibited uses PU-0001 and PU-0002 stand, and bind every profile.
Point-in-time questions are A03.

On profiles: the examiner explorer and the customer aid should be two profiles over one model, not
two models. They differ in what they may show (an examiner sees unreviewed records stamped; a
customer explanation should rest on fewer, better-evidenced statements), in register, and in what
they ask for, never in what the underlying records say.

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

**Why it matters now.** A customer explanation built on GR-0700 would tell someone that naming a
mark after any deceased person avoids section 43, which is wrong for the recently deceased whose
estate controls the name. An examiner can weigh a stamped machine edge; a customer cannot.

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
categories. The degree belongs on the record, beside the condition, where it can be copied verbatim,
and where A04's test records can read it.

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

**Why it matters now.** "Adverse report", "pending application" and "extension of time" are the
words a customer meets in their own correspondence. A definition that is right for the further
report but wrong for the first one misleads exactly the reader the customer aid is for.

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

**Why it matters now.** In the first version I noted that nothing reads evidence from the RDF today.
That is still true, but the stated future consumers (ML, decision services, a policy aid) will read
exports, not this repository's YAML. A foundation whose exports cannot say which sentence a statement
rests on is not yet a foundation; this is core work, not polish.

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
pySHACL on a flat graph (the lesson of the first review's F02). Every record type added for the
A-series (test records, process templates, matters) gets the same targets from the start.

### R05: change impact omits current authored dependencies

**ChatGPT says.** RULE-0002 traverses only the approved graph, so no definition is a dependant and
all 15 corrected signed records are; the explorer's `stability` builder is broader but skips
definitions; the two answer different versions of the same question.

**Finding: agree.** Confirmed: RULE-0002's 142 dependants include all 15 corrected signed
relationships and no `GD-` record; `explorer.build.stability` gathers concept and typing evidence,
each relationship's single `ref` and the mention index, and no definitions or corrections. Both start
from a Manual chunk, so neither starts from a provision. The only route from an amended section is
CQ-0017, which is fixed to section 43 and counts the Manual passages citing it by Part; it names no
concept, relationship or definition. For a policy aid, the amendment it simulates is usually to a
provision, so this is the gap that matters most.

Two mitigations it does not weigh. The harness's staleness check compares every evidence item's
hash with the pinned snapshot, definitions included (ADR-0137), so once a changed source is pinned,
a stale definition is found; what is missing is the forward view ("what would this change touch?"),
not detection. And RULE-0002's limits line already says a nil result is not "nothing is affected".

**Its fix: agree.** One dependency index over every evidence item and record type, with record id,
type, review status, source version and reason; an effective-current view and a separately labelled
historical one; "no recorded impact", never "no impact"; RDF and browser agreeing. This is the first
of A10's three layers. Implementation notes: build it in Python first, reading the stores the way the
staleness check does (reuse it), keyed by any ref (chunk, provision or unit), feeding
`explorer.stability` and a generated report. Leave RULE-0002 as it is, labelled "signed records
only": it is approved by the owner for its stated scope (OQ-0004), and widening it would be a
different rule. Once R03 lands, put the same index into the graph as a candidate rule over every
store, so a downstream policy tool can read it.

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
gaps, rather than as a failing or skipped test. CQ-0009 is also a natural first customer for A04: a
structured section 43 test record would answer it directly.

### R07: conditions need an explicit representation and consumption contract

**ChatGPT says.** Only 26 of 337 authored relationships carry `applies_when`, and "no condition
needed" cannot be told from "not assessed"; the builder emits an unconditional direct edge beside a
conditional reified one.

**Finding: agree.** 26 of 337 confirmed. To size "not assessed": of the 311 without a condition, 103
have a conditional marker ("if", "where", "unless", "when", "except") in their supporting sentence.
That is a crude count and overstates, but it shows the gap is not small. And five of the 26 hold a
hedge or an outcome rather than a condition (R01). GR-0319 and GR-0206 are as described: the
non-use proceeding and the "if it wishes to continue" condition are not on GR-0319, and the
mark-type and colour context is not on GR-0206. Both are the kind of context a customer explanation
must carry, or it tells one applicant what applies to another.

**Its fix: agree in part.** Agree: the qualified assertion is the legal reading and the direct edge a
navigation projection; an assessment state; negative examples for the risky predicates. ADR-0134
already licenses no inference from the direct edges; say so plainly in `graph/README.md` and the
header of `relations.ttl`. Where I differ is how the state is set and where the context comes from.

**What I would do.** Set the state by rule where a machine can: no conditional marker in the
sentence gives `none_stated` (a fact about the sentence, not a legal judgement); a marker and no
condition gives `not_assessed`; then the agent assesses the hundred or so flagged. Split hedge from
condition (R01). Derive the proceeding from the source Part with a small lookup table rather than
hand-writing it on each record, and hand-write it only where a Part covers several proceedings. Add
mark type (standard, certification, collective, defensive) the same way, from the Part where it
determines it. These become the applicability fields A03 and A04 read.

### R08: the authority detector is a warning heuristic

**ChatGPT says.** The detector catches "the Act requires" with only Manual citations, but any
citation of the named section clears it, a generic "the Act requires" with a section 6 citation
passes, and naming the Manual exempts a sentence.

**Finding: agree, and it is wider.** All three reproduce. Two more misses: a negation anywhere before
the match suppresses the flag ("The legislation does not say anything else, but section 41 requires
use evidence" passes with no citations), and phrasing outside the verb list is never examined
("Under section 43 the connotation must be obvious, direct and immediate"; "It is a legal requirement
that ..."). The module's docstring already calls the check "deliberately narrow". For customers the
distinction matters more, not less: a customer told that the Act requires what is only the
Registrar's practice may argue the wrong point.

**Its fix: agree.** Document what a clean result means; add the adversarial cases as tests that
record the known misses; remove absolute wording wherever the site or the documents describe the
separation as guaranteed. Claim-level anchoring belongs with A08, where each claim names whether its
source is the Act, the Regulations, the Manual or a case. Two cheap tightenings worth making in both
engines: apply the Manual exemption only when the legislative verb is attributed to the Manual in the
same clause, and the negation check only within the matched clause. It stays a warning.

### R09: existing measurements do not establish a retrieval advantage

**ChatGPT says.** Ontology expansion beat keyword search but trailed hybrid search; the expert's
ten-question check shows no dependable difference; the browser reading did not beat keyword search.
Keep the strongest baseline, test ablations, measure other benefits separately, freeze questions
before tuning.

**Finding: agree, with a correction.** Every number in its table matches `measure.md` and
`measure-reading.md` at their commits. The correction: the measurements do establish one advantage,
over keyword search (ontology minus keyword +0.079 [+0.042, +0.116] on all 129 questions, +0.201 on
the problem questions). But for an examiner research tool, the comparison that matters is against
the best search available, and there the ontology system trails hybrid search by −0.041
[−0.067, −0.017]. Judged by the stated use, ChatGPT's headline is right.

**Its fix: agree.** The ontology's place in examiner research is on top of the best search, not
instead of it: keep hybrid search as the baseline and measure what expansion adds to it. The
ablations it suggests are the handoff's first next action (hub concepts entering expansion, ties
broken by ref order), designed before measuring and never tuned on the benchmark. Measuring the
other benefits separately is right, and they are the ones most specific to the stated uses: tracing
a statement to its source, reaching the right provision and its exceptions, and finding what an
amendment touches. Two owner gates remain: re-measurement is deferred (CHAT-0084), and who writes
and judges a new benchmark is the owner's (`CLAUDE.md` §3a).

### R10: coverage and source currency need clearer boundaries

**ChatGPT says.** The source graph holds 42.8% of chunks; five Parts are absent and seven have no
authored relationship; the Manual capture predates the Act compilation; case nodes are references;
21 legislative bases are unverified.

**Finding: agree.** All reproduce: 1,053 of 2,460 chunks; Parts 1, 4, 8, 41 and 61 absent, Parts 7
and 45 also without an authored relationship; the Manual captured on 3 August 2026, the Act at
compilation 48 (in force from 19 September 2026), the Regulations at compilation 53 (from 18 December
2025); 21 unverified bases (the handoff said 22; the harness, which is right, says 21).

**Its fix: agree.** One generated table by Part (searchable, in the graph, concepts, relationships,
definitions, reviewed) is the handoff's coverage action. Answers already name the compilation they
read; add the Manual's capture date beside it, and say that a Manual captured on 3 August 2026 may
not reflect compilation 48. Reconciling the two is for the examiners at the end-of-work review
(ADR-0120), not an agent. A customer aid must say what it does not cover in words a customer
understands. The 21 bases are agent work: re-cite each from a quoted passage, or mark it unresolved.

## Foundations for the intended uses

### A01: model the matter and each objection, not only the vocabulary

**Finding: agree.** `TradeMarkApplication`, `Examination` and `Objection` are unpopulated, and
nothing connects a report's objections to their ground, affected goods or response options.
`tmk:Role` is described as "a person, office or body", while `examination.ttl` (lines 210 to 212)
declares offices, delegates, parties and representatives disjoint; once individuals are typed, an
attorney applying in their own name, or an examiner filing a personal application, is a
contradiction.

**Its fix: agree.** A small matter schema (sign and its representations, application, claimed goods
and services items, examination, report, objection with its ground, stated reasons, affected items
and disposition, registration) and a role assignment scoped to a matter and a time. Keep
classification separate from the specification, and never use class membership for similarity.
Three notes. Populate it only with fictional cases until the owner allows real data (a gate). Model
it after Package 1, because each objection's ground will link to the records Package 1 repairs.
And fix the role point now, in its cheap form: say in the class comments that a role is a capacity,
not the person who holds it, and scope the disjointness to capacities.

### A02: represent process stages, events and conditional response paths

**Finding: agree.** There is no transition model; three `precedes` and two `suspendsTimeFor` edges
are the extent of it, and nothing can establish where a customer is in the process.

**Its fix: agree.** Start with one template, regulations 4.8 to 4.10 (report, response,
reconsideration, further report or acceptance, deferment and lapse), each step with its source,
prerequisites, effect and responsible role, kept separate from any matter's event history. Explain
deadline rules and the inputs they need; compute dates only for branches whose rules and edge cases
have been reviewed, and never recalculate a date the customer's own report states. One caution: the
explorer's grounds tree is a binary tree of questions by the owner's ruling (ADR-0106); that is a
view of the grounds, not the process, and the process template should not be built by stretching
it.

### A03: make applicability and meaning depend on context and time

**Finding: agree.** `time.ttl` excludes point-in-time questions and holds one compilation per
instrument; ADR-0137 allows one definition per concept (`tmk:defines` is declared functional).

**Its fix: agree.** Define now: an instrument's or concept's enduring identity apart from its
versioned text; legal effective intervals apart from capture dates (the repository already records
both for each instrument); scoped statements; an explicit unknown when a filing date matters and is
not given. Relax "one definition per concept" to "one per concept per scope", with a disambiguation
rule and an unresolved state (an agent-proposed ADR superseding that part of ADR-0137; the owner's
postponement on splitting "application", CHAT-0025, is about splitting concepts, not scoping
definitions). Selecting between versions needs a second version to be held: historical compilations
and transitional provisions would have to be captured upstream (`CLAUDE.md` rule 2). OWL-Time for
the primitives, as it says.

### A04: introduce structured legal tests alongside conceptual relationships

**Finding: agree.** Binary edges with a modality and a free-text condition cannot hold conjunctions,
alternatives, exceptions with priority, or discretion, and traversing an edge does not show that its
conditions hold.

**Its fix: agree.** Keep the concept graph for terminology and navigation, and add test records:
the actor, the conditions (with AND and OR, and unknown kept apart from false), the legal effect,
the modality's meaning (an obligation, a discretion, or evidence that may establish something),
scope, authority, period, and exceptions, each element citing its exact unit and quote. Start with
sections 41, 43 and 44, which cover the commonest objections and exercise every feature (41's
evidence routes in (3) and (4), 43's connotation and its factors, 44's carve-outs in (3) and (4) and
the discretion they give). ADR-0009 already allows this: it defers LegalRuleML, not structure, and
permits "decision tables for bounded procedural logic". A superseding ADR is owed only when a named
use needs defeasibility or rule priorities executed by an engine (machine decision-making, later).
Evaluative steps stay as assessments for a person, never computed.

### A05: separate case evidence, factual claims and assessed conclusions

**Finding: agree.** The four evidence classes are unpopulated, and nothing links an exhibit to a
claim, an issue and an assessment. "Evidence" here (material an applicant files) is a different
thing from the repository's source-quotation evidence, and the two must never share a class.

**Its fix: agree.** In two steps. First, what customers need now: the Manual's general requirements
for evidence that addresses an objection (for section 41(3) and 41(4): the sign as used, the goods
and services, the dates relative to the filing date, use in Australia), written as authored records
from the Manual, distinguishing relevance from sufficiency. Second, for later ML and decision
services, the schema ChatGPT describes (evidence item, its submission, the claims it supports or
challenges, its period and goods, and a separate assessment naming who made it and on what basis),
populated with fictional fixtures only.

### A06: retrieve complete legal context, not fixed-length passage prefixes

**Finding: agree; the most urgent of the A-series, because it affects the examiner chatbot today
and would carry into a customer chatbot built the same way.** Reproduced through the repository's
loader: section 44 is 3,785 characters; subsection (3) starts at 2,390 and (4) at 2,962; both are
cut by the 1,600-character limit (`explorer/build.py` line 729, `bulk/jobs.py` lines 1117 and 1122,
`site/js/engine.js` line 260). They are the honest concurrent use and prior continuous use
carve-outs, the exceptions to (1) and (2), and the `s44(1)` unit opens "Subject to subsections (3)
and (4)". So a live answer about section 44 is written from the rule without its exceptions, and the
rule against concluding absence cannot help, because the model never sees them. 372 of 2,460 chunks
and 101 of 763 provisions exceed the limit.

**Its fix: agree in part.** Agree with the end state: complete units, the context a test needs,
omissions disclosed, a regression fixture for section 44 and one for an exception on another page.
I differ on the route. A general context-bundle model is not the first step, and once A04 exists it
need not be a separate one.

**What I would do.**
1. Now, in `jobs.py` and `engine.js` together (a test holds them identical): give legislation whole
   up to a budget (the median provision is 576 characters, 90% are under 1,800 and only 10 exceed
   4,000), and for the few larger ones the matched units plus any unit a lead-in names ("Subject to
   subsections (3) and (4)"); cut a long Manual chunk around the match rather than from its start
   (`passage_block` already takes `around`; answers do not use it); mark every cut, in the prompt and
   on the page; add the section 44 fixture.
2. Then, as A04's test records are written, draw the bundle from them: a test record already names
   its units, its exceptions and the concepts it turns on, so its definitions and cross-references
   come with it, and the bundle has one source of truth rather than a second retrieval model.

This changes what the live chatbot is given, so it goes to the owner with A08 (decision 1). The 129
prepared answers on the Ask page were written from cut passages; label them as such (no spend).

### A07: broaden source access while preserving proposition-level authority

**Finding: agree.** `KeywordIndex` indexes Manual chunks only. Legislation reaches an answer only as
a recognised concept's legislative basis or a provision one of the top three passages cites
(`Engine.prepare`). Cases are held at citation level; no customer guidance is held.

**Its fix: agree.** Now: exact-reference lookup ("section 44(3)", "reg 4.10" to the unit) and keyword
search over the 763 held provisions beside the Manual, both deterministic and cheap, both labelled
unmeasured until the next measurement. A task-based source register here, naming which judgments,
customer pages and forms each task needs, linking out before ingesting. One note on where the
ingestion happens: crawling and extraction belong upstream (`CLAUDE.md` rule 2 and §6), so a small,
named set of IP Australia's customer pages (how to respond to an examination report; how to provide
evidence of use) should be raised with `manual-XtrACTor`, kept as their own source kind, distinct
from the Manual and the legislation. Judgment text is held nowhere in the programme (Q-11), and its
licence terms need checking before any capture. Its points about cases (the Manual's account of a
case is not the judgment; quoted, paraphrased and inferred differ) are right and partly encoded
already (`statedIn`, `attributedTo`).

### A08: make support verifiable for each claim before displaying the answer

**Finding: agree.** Confirmed by reading the code: the answer schema is one string and a citation
list; `Engine.verify` checks each quote against `this.text(ref)`, the full stored text, not the
excerpt the model was given; an empty list returns nothing kept and nothing dropped, with no warning;
`ask.js` streams the answer as it arrives and, after checking, shows the same text with the kept
citations and a note that others were removed.

**Its fix: agree.** An explanation object of discrete claims, each with its type, scope, source
kind, quotes, assumptions and missing facts; quotes validated against the excerpt actually sent; a
claim with no surviving quote shown as unsupported (or omitted, or stated as a gap), and an answer
with none shown as having no checked support; the answer streamed as a visibly unchecked draft; the
final claim-to-source mapping stored with the answer. All of that is deterministic and costs
nothing. The support check proper (does this quote support this claim and its qualifications?) needs
a model judge or expert labels. For the examiner tool, saying plainly that the check proves a quote
exists, not that it supports the sentence, is an honest interim. For any customer release it is
owed first, and a model judge needs a quote and the owner's spend (the cap is spent). Reviewed
templates for recurring explanations are right; under the owner's waterfall ruling (ADR-0120) they
are reviewed at ship time, so until then they are templates stamped unreviewed. The schema change
alters what the live chatbot is told, so it goes to the owner with A06 (decision 1).

### A09: build customer explanations and visuals from a shared explanation model

**Finding: agree.** The answering instructions target an examiner, and there is no customer task or
context contract. A retrieval trace explains how passages were found, not why a proposition holds,
and "they rejected my name" can mean several things.

**Its fix: agree.** Customer intents and a few context slots (the report's wording or cited ground,
the application route, the stage, the affected goods and services, dates where they change the
answer); ask only for facts that change the explanation, and allow general guidance without
personal data. Plain-language text as versioned views of scoped propositions, never alternative
definitions. A08's explanation object generating both prose and visuals, and its three views (an
issue card, a conditional process timeline, an evidence-to-issue view), each exposing sources,
conditions and unknowns, each with a text equivalent, and each separating "why this was retrieved"
from "why this is supported". The repository's everyday-language reading (ADR-0132) is a good start
for intents, provided it asks when a phrase could mean several things rather than choosing. Testing
comprehension with customers is right and is an owner gate (outward-facing).

### A10: separate dependency analysis, legal scenarios and real-world policy effects

**Finding: agree.** "Which guidance needs review?", "would this matter be treated differently?" and
"how would applicants behave?" are different questions, and connectivity answers only the first.

**Its fix: agree.** Build the editorial-impact layer now (R05, keyed by provision so an amendment can
start it). Normative scenarios once A03 (versions) and A04 (tests) exist for a small set of
provisions, run on fictional matters, with draft text kept out of anything operative. Behavioural
and operational effects need a separate empirical model and data nobody here holds; until then the
system says such effects are unknown.

### A11: create versioned reuse contracts for ML and other downstream consumers

**Finding: agree.** The records serve the explorer, and the projections do not all carry the same
semantics: R03 shows evidence lost in the RDF, and S039 found hierarchy links and definitions
missing from some views.

**Its fix: agree.** A release manifest per build (ontology revision, pin and compilations, schema
versions, corrections, review-state counts, coverage, profile) as `build.json` on the site and a
header in the graph; assertion-level provenance and applicability in every export, with explicit
missing values (R03 and R07 first); authoring origin, review state, legal authority and authoring
confidence kept as separate fields, which the records mostly do already. Identifiers and their
retirements are already stable (`authored/retired-ids.yaml`, `eval/gold/retired-ids.yaml`); a
migration map for re-read records (old triple to new) would complete it, and the restructure ledgers
hold the data for one. PROV-O alignment is optional. Its rules for training data (split by matter
and time, no later outcomes in earlier features, the frozen benchmark kept and a new one versioned)
are right, and apply when case data exists.

### A12: test the intended tasks, including missing and conflicting information

**Finding: agree.** Query execution, connectivity and quote matching do not show that an examiner
found the governing qualification or that a customer understood an objection.

**Its fix: agree.** Task-level fixtures for both users, abstention and clarification counted as
success, and release-blocking fixtures that no average can hide (an unsupported operative claim,
the wrong compilation, an omitted outcome-changing qualification). Its scenario list is a good one.
Three constraints on how, none on what: who writes and judges a benchmark is the owner's
(`CLAUDE.md` §3a); expert review of expected answers happens at the examiners' review at ship time
(ADR-0120), so until then the fixtures test behaviour and consistency, not legal correctness, and
say so; and customer comprehension testing needs customers (an owner gate). What an agent can write
now: the section 44 context fixture, the unsupported-claim display, the compilation on every answer,
the absence rule, and fictional versions of its scenarios (two objections over different goods,
evidence covering the wrong period, ambiguous everyday wording).

## Other points in the review

- **The integrated design (its section 7): agree.** Keep SKOS concepts, classes, source passages and
  assertions apart, and introduce case-level instances explicitly rather than reusing concept nodes.
  Its five-layer information model (source and authority; meaning and norms; matter and process;
  evidence and assessment; explanation and scenarios) is a sound target, and the order of work
  below follows it.
- **Stale documents: agree; fix now.** `graph/README.md` says the authored graph "is empty today" (it
  holds 16,107 triples) and that a shape refuses an authored node without its envelope (not for
  definitions or corrections, R04). `eval/README.md` still says an agent "must not author" legal
  judgements, citing a rule 1 that now says the opposite, and frames Stage 0 as the blocker.
- **Predicate boundaries: already largely done.** Every predicate in `predicates.py` carries a
  definition, a reading, an example, a counter-example, an authority and the kinds it joins
  (ADR-0123, ADR-0131). The gap is the eleven singletons' thin use.
- **A register of empty classes: agree.** The ontology report lists the 53; a status column
  (populated, structural, reserved for a named use) is now worth having, because the A-series will
  populate several of them.
- **Its roadmap (section 8): agree with the stages and the vertical slice**, with the sequencing
  difference above: design the slice's schema in parallel with the repairs, populate it after.
- **Strengths to preserve (its section 4): agree** with all of them, and with keeping RDF, SKOS,
  SHACL and bounded SPARQL rules rather than unrestricted OWL.

## What the review missed

1. **Corrections share R04's validation gap.** All 37 can lose their author, date, reasoning and
   sources without a defect.
2. **R03 spans four record types and 634 evidence items**, not one type and 230.
3. **The signed competency-question records already hold the answer contract** R06 asks for.
4. **The predicate dictionary's example for `isAnExceptionTo` is GR-0700's sentence**, and it is
   rendered into the relate prompt.
5. **A fourth definition omits a qualification** (GD-0084), and **GD-0146's narrowing is in its
   concept record** too (GC-0179).
6. **Two more authority-detector misses** (an earlier negation; phrasing outside the verb list).
7. **Five conditions are hedges** (GR-0565, GR-0574, GR-0608, GR-0699, GR-0700).
8. **The section 44 cut removes exactly the exceptions**, which the answer rule against concluding
   absence cannot repair, because the model never sees them.
9. **ADR-0009 already permits structured tests as data** (decision tables); A04 needs no reversal of
   it.
10. **The order matters.** The customer slice composes the very records R01, R02 and R07 show to be
    overstated or unconditioned; repairing them first is cheaper than correcting explanations after.

## Recommended order of work

Both owner decisions below were approved on 2026-10-19 (ADR-0139), so the live-answer package moves
up: Package 1, then Package 3, then Package 2, then Packages 4 and 5. Package 3 waits on Package 1
because the definitions it adds to the prompt are the ones Package 1 repairs.

**Package 1: repair the foundation** (agent, no spend, about one session). R04 (shape targets
including corrections, a Definition shape, RULE-0001 and the equality check); R03 (evidence anchors
for every record type, source closure); R01 (the four re-reads, the hedge field, the dictionary
example, an ADR superseding ADR-0135's reading); R02 (the triage as harness notes, then the flagged
re-reads and GC-0179); R07 (the condition state set by rule; proceeding and mark type from the
Part); the stale READMEs; the role comments (A01) and the `ExaminationOutcome` comment (represent,
never generate). Then `tmk-graph --write --rules` and `tmk-ontology-report --write`.

**Package 2: what examiners use** (agent, no spend, about one session). R05 (the dependency index,
keyed by any ref; the change view gains definitions, corrections and provisions); R06 (each query
tested against its signed record; CQ-0009 and CQ-0024 rewritten); R08 (documented limits, tests, two
tightenings); R10 (the coverage table, the Manual's capture date); A07 (exact-reference lookup and
provision search; the source register); A11's release manifest.

**Package 3: the live answer, approved (ADR-0139); second, after Package 1.** A06 step 1 and A08's
deterministic parts together in `jobs.py` and `engine.js`, as a new answer version; the definitions
given to the model, each with its basis and stamp; the prepared answers labelled as written from cut
passages.

**Package 4: the first customer slice, fictional** (agent, no spend, one or two sessions; schema
design may start during Package 1). Test records for sections 41, 43 and 44 (A04); the regulations
4.8 to 4.10 process template (A02); the matter, objection and role-assignment schema (A01); the
evidence requirements for section 41(3) and 41(4) (A05); the explanation object and its three views
(A08, A09), on a page separate from the examiner explorer and not published to customers; fixtures
from ChatGPT's acceptance examples, every record stamped unreviewed, every case fictional. A06 step
2 follows from the test records.

**Package 5: the later foundations.** The versioning model defined (A03), with version selection
once upstream holds a second version; the dependency index in the graph as a candidate rule (R05,
A10); normative scenarios on fictional matters (A10).

## Decisions for the owner

Both approved by the owner on 2026-10-19: *"I approve both the decision points you raised."*
(CHAT-0087, CHAT-0088, ADR-0139).

1. **Approve two changes to what the live examiner chatbot is given and how its answers are shown**:
   complete legislative units with every cut marked (A06); and claims carrying their own quotes,
   checked against what was sent, unsupported ones marked, streamed as an unchecked draft (A08).
   Recommended; the customer chatbot would be built the same way.
2. **Let the answering model see definitions** (open since S038), once Package 1 has re-read the
   flagged ones. Explaining requirements to customers leans on definitions more than any other
   record. Recommended.

Gates ahead, to be asked when reached: publishing anything to customers, or testing with them; using
real customer or case data (`CLAUDE.md` §3a, ADR-0138); spend for a model-judged support check
(A08) and for re-measurement (the cap is spent); and who writes and judges the next benchmark (R09,
A12).

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
  `tmk:isCorrected true`; `queries/competency/CQ-0017.rq` for the provision route.
- **R06**: run `queries/competency/CQ-0009.rq` and `CQ-0024.rq` over the dataset; compare with the
  records in `eval/gold/competency-questions.yaml`.
- **R07**: count authored relationships with `applies_when`, and those without whose
  `supporting_text` matches `\b(if|where|unless|when|except)\b`.
- **R08**: `search.authority.conflations(text, cited)` on the sentences quoted above.
- **A06**: offsets of `(3)` and `(4)` in `corpus.provisions["TMA1995/s44"].text`; counts of chunks
  and provisions over 1,600 characters; the length distribution of provisions.
- **A07, A08**: `KeywordIndex.__init__` in `search/index.py`; `prepare`, `prompt` and `verify` in
  `site/js/engine.js`; the streaming and `showAnswer` call in `site/js/ask.js`.

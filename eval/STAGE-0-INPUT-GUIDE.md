# STAGE 0 — what you need to provide, and in what shape

**Audience:** the repo owner and the examiners advising them. This is the
expert-facing companion to `eval/README.md`, which is written for agents.

**Purpose:** to make concrete what "complete Stage 0" means. It walks every
deliverable, shows the shape of each record with a worked example, states what
makes a record good or useless, and lists the questions an agent will ask you to
elicit each one.

**What this document is not.** It contains **no trade marks law**. Every example
below is shape-only: legal substance is replaced with `«placeholder»` and example
records are numbered `XXX` so they can never be mistaken for project content.
That is not caution for its own sake — CLAUDE.md rule 1 means an agent cannot
author the content of a competency question, a gold answer, a concept definition
or a prohibited use, and a plausible-looking invented example is exactly the
thing that gets copied forward and treated as approved. What follows is the
container. You supply what goes in it.

---

## 1. Stage 0 in one page

Stage 0 is where you write the exam before building the candidate.

Everything in Stages 2–10 — terminology extraction, the vocabulary, the
relationship set, the graph, search, AI retrieval, reasoning — is justified by a
measurement. The measurement needs a trusted answer to compare against. That
trusted answer is the only thing in the entire programme that cannot be
generated, inferred, or bought: it has to come from someone who knows the
practice.

The consequence of skipping it is specific and well documented. Without a gold
set, the first plausible-looking extraction output becomes the de facto standard
purely because it arrived first, and nobody can later tell whether a change made
the system better or worse. ADR-0010 therefore blocks all Stage 2+ work until
Stage 0 exists.

Stage 0 produces five deliverables plus a harness:

| # | Deliverable | File | Who supplies the content |
|---|---|---|---|
| 1 | Pilot scope | `eval/pilot-scope.md` | You |
| 2 | Competency-question catalogue | `eval/competency-questions.md` | You |
| 3 | Gold-standard dataset | `eval/gold/` | You (six record types) |
| 4 | Prohibited-use list | `eval/prohibited-uses.md` | You |
| 5 | Evaluation measures | `eval/measures.md` | You set thresholds; agents propose the metric list |
| 6 | Evaluation harness | `eval/` + `tests/` | Agents, entirely |

The intended end state of Stage 0 is a test suite that **runs and fails**,
because there is nothing yet for it to pass against. A red harness is the
correct first output of this repo, and it should be defended when it looks like
slow progress.

---

## 2. The pilot: section 43

The pilot area is **s 43 of the *Trade Marks Act 1995***, decided by the repo
owner on expert advice and recorded as ADR-0013. It was chosen against the
roadmap's five selection criteria — important to examiners, spread across
multiple Manual sections, connected to legislation and case law, containing
relationships and exceptions, and small enough to be contained — with
geographical indications noted as an area of growing discourse.

That decision closes HANDOFF Q1 at the level of *which area*. It does not by
itself fix the **boundary**, and the boundary is the first thing Stage 0 needs
from you. Deliverable 1 exists to answer these questions, all of which are
judgement calls an agent must not make:

- Which Manual Parts and pages are in scope? Is scope defined by "Parts that
  discuss s 43" or "chunks that cite `TMA1995/s43`"? These give different sets,
  and the second is machine-derivable while the first is not.
- Which neighbouring provisions come in because they cannot be separated in
  practice, and which are explicitly out even though they will be cited in the
  same breath?
- Are geographical indications treated as the pilot's centre of gravity, a
  sub-area within it, or simply one of several sub-topics?
- Is the ground's interaction with other grounds of rejection in scope, or does
  the pilot stop at the boundary of s 43 itself?
- Are Registrar's decisions and court decisions in scope as *cited authorities*
  only? (They can be nothing more — see §8, Q-11.)

**Write the boundary as an exclusion list, not only an inclusion list.** "Out of
scope: «…»" is what stops the pilot growing quietly, and it is what lets a
competency question be marked `pilot_in_scope: false` and parked rather than
argued about.

### What the pilot scope record looks like

Copy this into `eval/pilot-scope.md` and fill it in. Prose is fine — this is the
one deliverable that is a document rather than a set of records.

```markdown
# Pilot scope

**Area:** s 43, Trade Marks Act 1995
**Decided by:** «name / role» · **Date:** «YYYY-MM-DD» · **ADR:** 0013

## Why this area
«against the five criteria — one line each»

## In scope
- Provisions: TMA1995/s43, «…»
- Manual material: «Parts, or the rule that defines the chunk set»
- Sub-topics: «…»

## Out of scope, deliberately
- «…and why. This list is as important as the one above.»

## Boundary cases and how they are resolved
- «the thing that is arguably in and is being treated as out, and the reason»

## Point-in-time
Is "what guidance was current on «date»" in scope for the pilot? «yes/no»
(See §8 — this is only partly answerable and the decision belongs here, not in
Stage 8.)
```

---

## 3. Two passes: what you can write now, and what needs the corpus open

The single biggest practical constraint: several fields cannot be filled from
memory. `source_ref`, `span` (character offsets) and `source_content_hash` all
require the actual upstream snapshot in front of you, and this repo does not
hold it yet (HANDOFF Q2 / ADR-0004).

This splits the work cleanly, and the split is worth respecting because Pass A
is the part only you can do, and it is not blocked on anything.

**Pass A — from your own expertise, no data needed.**
Pilot scope · competency questions · concept labels and the near-miss terms that
must *not* cluster with them · search questions phrased as a user would type
them · AI retrieval questions and the qualifications a correct answer must carry
· the prohibited-use list · acceptance thresholds.

**Pass B — needs the corpus open in front of you.**
Entity spans · which chunks are relevant to which question, and at what grade ·
supporting sentences for relationships · content hashes · the "tempting but
irrelevant" refs that a keyword match will wrongly surface.

**You will not type a single ref or hash by hand.** Once the snapshot is
pinned, an agent will generate a *worksheet* for Pass B: every chunk in the s 43
scope, printed with its `chunk_ref`, `heading_path`, `content_hash` and full
text, in a spreadsheet or annotation-friendly form. You highlight and comment;
the agent transcribes into the record shapes below and validates that every ref
resolves and every offset lands where you said it does.

Do Pass A first. It is not blocked, and it defines what the Pass B worksheet
should even contain.

---

## 4. The measurement rule that shapes everything

One methodological point, because it changes how much work Stage 0 is and it is
the mistake most easily made:

**Precision can be measured from a sample. Recall cannot.**

If you annotate "some good examples" scattered across the corpus, you can ask
"of the things the system found, how many were right?" You can never ask "of the
things that were there, how many did the system find?" — because you never
established what was there.

So for the entity and relationship record types, pick a **bounded set of chunks
and annotate them exhaustively**: every entity of the listed types, every
relationship in scope, in every chunk of that set, including the boring ones.
Twenty exhaustively-annotated chunks are worth more than two hundred
cherry-picked examples. Cherry-picked examples also skew hard towards the
interesting cases, which makes the measured accuracy meaningless in both
directions.

For the question-shaped record types (search, retrieval, competency), the
opposite applies — those *should* be chosen deliberately to cover the hard
cases, because each one is its own test.

---

## 5. The record types, one by one

Six gold record types plus competency questions and prohibited uses. Templates
live in `eval/templates/`; this section explains them and shows what a filled
record looks like.

Conventions used below:
- `«…»` — you supply this.
- `XXX` in an id — this is an example, not a real record.
- Refs follow `docs/IDENTIFIERS.md`: `TMM/Part22/1/1/2` for a Manual chunk,
  `TMA1995/s43` or `TMA1995/s43(1)(a)` for legislation. Store refs, never IRIs.

---

### 5.1 Competency questions

**Template:** `eval/templates/competency-question.template.yaml`
**Target:** no fixed count; cover every category. Expect 15–30 for a pilot.
**Pass:** A

An ordinary question the finished system must be able to answer — phrased as the
person who needs it would actually ask it, not as a query and not as a
restatement of a Manual heading. These are the top-level statement of what the
system is *for*; everything else in Stage 0 exists to test whether they are
answered.

The roadmap's eight illustrative questions are worth reading as a coverage
checklist (roadmap §Stage 0): what guidance discusses X, which provisions are
the legislative basis, what evidence may be relevant, which cases interpret the
test, what Manual material cites a case, what was current on a date, what is
affected if a provision changes, what exact passage supports an AI answer. Those
are the *categories*. The questions themselves must be yours and must be about
the pilot area.

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
id: CQ-XXX
question: >
  «the question, in the words an examiner would use»
asked_by: examiner            # examiner | applicant | AI assistant | maintainer | other
category: retrieval           # retrieval | search | reasoning | currency | impact | provenance
pilot_in_scope: true

expected_sources:
  required:                   # missing any of these = wrong answer
    - TMM/Part«NN»/«n»/«n»/«n»
  supporting:                 # contributes to recall, not to pass/fail
    - TMA1995/s43

expected_concepts: []         # labels for now; SKOS ids once vocab/ exists
must_not_include: []          # refs or claims whose presence makes the answer wrong

answer_shape: >
  «structural requirements: must it separate legislation from Manual practice,
  must it cite, must it flag uncertainty — not the answer itself»

caveats: >
  «known limits on answering this — see §8»

measured_by: [recall_at_10, citation_correctness]
approved_by: «name»
approved_date: «YYYY-MM-DD»
```

**What makes one good**

- It is a question someone actually asks. If no examiner has ever needed it, it
  will not detect a failure anyone cares about.
- `expected_sources.required` is short and defensible. If you cannot say "this
  answer is wrong without this passage", it belongs in `supporting`.
- `answer_shape` constrains the *form*, and this is where the authority
  distinction gets enforced. "Must state whether the requirement comes from the
  Act or from the Manual" is a testable structural demand.
- The set as a whole spans the categories, including the awkward ones
  (`currency`, `impact`, `provenance`). Those are the questions a
  retrieval-only system silently fails.

**Failure modes**

- Questions that are really search strings. "s 43 evidence" is not a competency
  question.
- Questions whose correct answer is the whole Part. They cannot discriminate.
- Loading `required` with everything relevant, which makes every answer wrong
  and the metric useless.

**What an agent will ask you**

> Who asks this, and what do they do with the answer? · What would make you
> reject an answer that contained the right passage? · Is there a passage that
> looks responsive but is the wrong one to rely on? · Does a correct answer have
> to distinguish law from practice here, or is that not at stake?

---

### 5.2 Gold entities

**Template:** `eval/templates/gold-record.template.yaml` §1
**Target:** 100–300 · **Pass:** B · **Measures:** precision / recall / F1

Every mention, in a bounded chunk set, of a thing the system must recognise:
legal concepts, provisions, decisions, evidence categories, Manual instructions,
roles, dates. This is the annotation that measures Stage 2 extraction. Annotate
the chosen chunks **exhaustively** (see §4).

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
entity:
  id: GE-XXX
  surface: "«the text exactly as it appears in the chunk»"
  type: LegalConcept          # LegalConcept | LegislativeProvision | JudicialDecision
                              # EvidenceCategory | ManualInstruction | Role | Date | Other
  source_ref: TMM/Part«NN»/«n»/«n»/«n»
  span: [«start», «end»]      # char offsets into that chunk's `text`
  source_content_hash: "«from the worksheet»"
  resolves_to: TMA1995/s43    # where the mention refers to something with a ref
  notes: >
    «why this one is instructive — an abbreviation, a pronoun standing in for a
    concept, a form a naive matcher will get wrong»
```

**What makes one good**

- `surface` is copied verbatim, including odd casing and any typo in the source.
  A "cleaned up" surface form measures nothing.
- The hard cases are annotated rather than skipped: abbreviations, anaphora
  ("that ground", "the section"), terms split across a line, a concept named
  only by a synonym.
- `notes` says what a machine will get wrong. That sentence is what makes the
  record diagnostic rather than merely correct.

**Failure modes**

- Annotating only the obvious mentions, producing a recall figure that flatters.
- Annotating a paraphrase rather than a span. If it is not literally in the
  text, it is not an entity — it may be a concept (§5.3).
- Skipping a chunk because it is dull. The bounded set must be complete.

---

### 5.3 Gold concepts

**Template:** `eval/templates/gold-record.template.yaml` §2
**Target:** 50–100 · **Pass:** mostly A · **Measures:** clustering accuracy

The distinct ideas in the pilot area, each with the surface forms that mean it —
and, critically, the forms that look like it and do not.

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
concept:
  id: GC-XXX
  pref_label: "«the term you would use in a practice note»"
  alt_labels: ["«synonym»", "«abbreviation»", "«the phrasing the Act uses»"]
  not_labels: ["«the near-miss that must NOT cluster here»"]
  broader: [GC-XXX]
  narrower: []
  related: []
  definition_sources:
    - TMM/Part«NN»/«n»/«n»/«n»
  legislative_basis: [TMA1995/s43]
  notes: >
    «where the term has shifted meaning, or means different things in different
    Parts»
```

**`not_labels` is the most valuable field in Stage 0.** Everything clusters the
obvious synonyms correctly. Systems fail on the near-miss — the term that shares
most of its words, or that an examiner knows means something materially
different, and that no distributional model will separate. Every one of those
you record is a test that will actually fire.

Aim for at least one `not_label` on every concept where a plausible near-miss
exists. If you find yourself unable to name one, that is worth noting too.

**Failure modes**

- Treating `pref_label` as a definition. It is a label; the definition lives in
  the passages you cite.
- Empty `not_labels` throughout, which makes the clustering metric trivially
  passable.
- Concepts with no `definition_sources`, which cannot be grounded and cannot be
  tested.

---

### 5.4 Gold relationships

**Template:** `eval/templates/gold-record.template.yaml` §3
**Target:** 50–100 · **Pass:** B · **Measures:** relation precision / recall

A statement the corpus makes connecting two things, with the exact sentence that
says it. This is the record type that most directly tests whether the system can
read, and it is where Tier 3 (ADR-0008) lives.

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
relationship:
  id: GR-XXX
  subject: "«ref or concept id»"
  predicate: interprets       # from the approved relationship dictionary only
  object: "«ref or concept id»"
  source_ref: TMM/Part«NN»/«n»/«n»/«n»
  supporting_text: "«the exact sentence, verbatim»"
  span: [«start», «end»]
  source_content_hash: "«from the worksheet»"
  tier: 3                     # 1 deterministic | 2 low-risk | 3 legally significant
  modality: must              # must | may | should — where the relation is normative
  notes: >
    «if this is a "may" that means possibility rather than permission, or a
    "must" that is explanatory rather than obligatory, that is exactly why this
    record belongs here»
```

**On `modality`, and why it is not a grammar exercise.** The distinction between
an instruction that creates an obligation and one that describes what is
possible is a legal reading, not a parse. Records where the two come apart are
the highest-value ones in the whole gold set, because they are where an
extraction system will confidently produce a wrong assertion in a well-formed
shape.

**On the predicate list.** There is no approved relationship dictionary yet.
Building one is Stage 4 work, but the pilot needs a starting list, and the list
must come from what the corpus actually says rather than from an ontology
textbook. The practical route: write the relationships in your own words first,
let an agent group them into a candidate predicate list, then approve or rewrite
that list. Do not let an agent invent predicates and then have you fit
relationships to them.

---

### 5.5 Gold search questions

**Template:** `eval/templates/gold-record.template.yaml` §4
**Target:** 20–50 · **Pass:** A then B · **Measures:** Recall@10, P@10, MRR, nDCG

What a user types into a search box, with graded relevance judgements.

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
search_question:
  id: GS-XXX
  query: "«as a user would type it, including if that is clumsy»"
  uses_manual_terminology: false    # false is the interesting case
  relevant:
    - {ref: TMM/Part«NN»/«n»/«n»/«n», grade: 3}   # 3 highly · 2 relevant · 1 marginal
  irrelevant_but_tempting: []       # what a keyword match will wrongly surface
  must_exclude: []                  # superseded or withdrawn material
```

**Set `uses_manual_terminology: false` on most of them.** A search test using
the Manual's own words tests string matching, which already works. The point of
an ontology-enhanced search is that an applicant's phrasing, an examiner's
shorthand and the Manual's formal term all reach the same passage. Questions
phrased in the *wrong* vocabulary are the ones that measure whether the
vocabulary work was worth doing.

`irrelevant_but_tempting` is the search equivalent of `not_labels`: the passage
that shares the query's words and is the wrong answer. Every one you supply is a
precision test that will fire.

---

### 5.6 Gold AI retrieval questions

**Template:** `eval/templates/gold-record.template.yaml` §5
**Target:** 20–50 · **Pass:** A then B · **Measures:** coverage, grounding, citation

A question put to an AI assistant, specified by what its evidence package must
contain — not by a model answer. You are not writing the answer; you are writing
what a correct answer cannot omit.

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
retrieval_question:
  id: GA-XXX
  question: "«the question as put to an assistant»"
  required_evidence: [TMM/Part«NN»/«n»/«n»/«n»]
  required_provisions: [TMA1995/s43]
  required_cases: []                    # citation level only — see §8, Q-11
  qualifications_expected: >
    «the exceptions, conditions or limits a correct answer must carry. An answer
    that states the general position and omits these is wrong, even though every
    sentence in it is true.»
  authority_distinction_required: true  # must not present practice as law
  prohibited_conclusions: [PU-XXX]
```

`qualifications_expected` is the field that catches the characteristic AI
failure: a fluent, correct-sounding, unqualified statement of a general rule.
Write it as a list of things whose *absence* makes the answer wrong.

---

### 5.7 Expected reasoning results

**Template:** `eval/templates/reasoning-expectation.template.yaml` (new — see §10)
**Target:** roadmap says "expected reasoning results"; suggest 10–20 · **Pass:** A/B
**Measures:** expected inferences produced, prohibited inferences produced

The roadmap lists this among the gold-set components and the existing templates
did not cover it. It is the Stage 9 test: given a starting position, what should
the system conclude, and — more importantly — what must it never conclude.

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
reasoning_expectation:
  id: GX-XXX
  given:                        # the starting facts, as refs or concept ids
    - "«…»"
  expected_inferences:
    - conclusion: "«what the system should derive»"
      basis: [TMA1995/s43, TMM/Part«NN»/«n»/«n»/«n»]
      kind: classification      # classification | impact | consistency | currency
  must_not_infer: [PU-XXX]      # ids from eval/prohibited-uses.md
  tier: 3
  notes: >
    «why this inference is safe to automate, or why the neighbouring one is not»
```

Keep these strictly to inferences that follow from what the corpus *says*.
Anything that requires weighing evidence or exercising discretion is not a
reasoning expectation — it is a prohibited use (§5.8). The line between the two
is itself the most useful thing in this record type.

---

### 5.8 Prohibited uses

**Template:** `eval/templates/prohibited-use.template.yaml`
**Target:** roadmap says "examples"; suggest 10–20 · **Pass:** A
**Measure:** rate over the gold set, threshold zero

The conclusions the system must never produce. These are tested as explicitly as
the positive cases: each becomes a test that fails if the output ever appears.

```yaml
# EXAMPLE — SHAPE ONLY. NOT PROJECT CONTENT.
id: PU-XXX
prohibited: >
  «the output, stated as the system would produce it — not as a policy
  abstraction. "The system must be careful about X" is not testable;
  "«a sentence the system might emit»" is.»
kind: evaluative_conclusion
# evaluative_conclusion | authority_conflation | unsupported_inference
# stale_source | overreach | ambiguity_collapse
why: >
  «whose decision this is, what harm follows, or which rule it breaks»
detectable_by: test           # test | shacl | eval | human
test_ref:                     # filled in by an agent once the test exists
related_questions: [CQ-XXX, GA-XXX]
approved_by: «name»
approved_date: «YYYY-MM-DD»
```

**State each one as an utterance, not a principle.** The difference between "the
system must not decide the application" and a specific sentence the system might
plausibly emit is the difference between a value statement and a test.

The six `kind` values are a good coverage checklist — aim for at least one of
each, particularly `authority_conflation` (Manual practice presented as
legislation) and `ambiguity_collapse` (an ambiguous citation silently resolved),
which are the two failure modes this corpus makes structurally likely.

---

### 5.9 Evaluation measures

**File:** `eval/measures.md` · **Pass:** A · **Who:** you set thresholds

`eval/README.md` lists the metric dimensions from roadmap §5. What is missing is
the number attached to each: what score is good enough to ship, and what score
means stop.

Agents will propose the metric list and can compute baselines once anything
runs. The thresholds are yours, because they encode risk appetite rather than
statistics. Three kinds:

- **Zero-tolerance.** Prohibited inferences. The threshold is 0 and it is not
  negotiable by measurement.
- **Legally-loaded.** Citation correctness, authority distinction, currency.
  High, and justified in a sentence.
- **Operational.** Recall@10, expert minutes per 100 passages, share accepted
  without intervention. These are business calls about how much review time the
  agency will fund.

A useful framing when setting each: *what would you have to see before you let
an examiner rely on this without checking the source?*

---

## 6. How to hand it over

**Do not write YAML.** The shapes above are how records end up stored; they are
not how you have to produce them.

**There is now a workbook.** Run `tmk-workbook` (or ask an agent to) and you get
`data/derived/stage0-intake.xlsx`: one sheet per record type, in the order this
section explains them, with every fixed-vocabulary field as a dropdown so an
out-of-vocabulary value cannot be typed by accident. It ships **empty** — there
are no example rows, deliberately, because a plausible filled row is the thing
most likely to be copied. The rules for filling it in are on its first sheet.
Hand it back and `tmk-transcribe` turns it into validated records, reporting
every blank judgement field rather than filling one.

Two sheets are continuations rather than record types: `GS--relevant` holds a
search question's graded passages and `GX--expected_inferences` holds a
reasoning expectation's inferences, one row each, linked by `parent_id`.

Any of these also work, and an agent will transcribe, validate and file:

- A spreadsheet of your own, one sheet per record type. Probably the best fit
  for entities and relationships.
- Prose in a document, or a marked-up copy of the Pass B worksheet.
- A recorded or transcribed conversation. Interview-style elicitation is often
  faster than form-filling for concepts and prohibited uses, and it captures the
  reasoning that would otherwise be lost.
- Comments and highlights on the worksheet.

What the transcription **cannot** invent: any field that is a judgement. If you
leave `not_labels` empty, it stays empty and gets reported as a coverage gap. If
your relationship has no `modality`, an agent will ask rather than guess. This is
now enforced rather than promised: a row whose value sits outside a fixed
vocabulary is rejected and listed by sheet and row number, never snapped to the
nearest allowed value.

Every record needs `approved_by` and `approved_date`. That is the recorded human
decision required by CLAUDE.md rule 4 — it is what distinguishes this content
from a candidate, and it is the reason these files can be trusted downstream.

---

## 7. Definition of done

Stage 0 is complete when all of the following hold. The harness will check
everything mechanically checkable in this list.

**Content**

- [ ] `eval/pilot-scope.md` states the boundary, including exclusions.
- [ ] Competency questions cover all six categories; each has `expected_sources`
      and an `answer_shape`; each is approved.
- [ ] Gold entities: a bounded chunk set annotated exhaustively, within the
      100–300 band.
- [ ] Gold concepts: 50–100, with `not_labels` populated wherever a near-miss
      exists.
- [ ] Gold relationships: 50–100, each with a verbatim supporting sentence and a
      tier.
- [ ] Search questions: 20–50, majority not using Manual terminology.
- [ ] AI retrieval questions: 20–50, each with `qualifications_expected`.
- [ ] Reasoning expectations recorded, each with `must_not_infer`.
- [ ] Prohibited uses recorded, covering all six `kind` values.
- [ ] `eval/measures.md` has a threshold against every metric.

**Mechanical (the harness asserts these)**

- [ ] Every record validates against its schema.
- [ ] Every `source_ref` resolves in the pinned snapshot.
- [ ] Every `span` lands within its chunk's `text`, and the text at that offset
      matches the recorded `surface` / `supporting_text` exactly.
- [ ] Every `source_content_hash` matches the pinned snapshot's current hash.
- [ ] Every cross-reference resolves: `prohibited_conclusions` → `PU-*`,
      `broader`/`narrower` → `GC-*`, `related_questions` → `CQ-*`/`GA-*`.
- [ ] No id is duplicated or reused.
- [ ] Every record carries `approved_by` and `approved_date`.
- [ ] The suite runs and **fails**, because nothing has been built to pass it.

That last line is the deliverable. A green suite at the end of Stage 0 would
mean the tests are not testing anything.

---

## 8. Limits to design around

Four constraints from `docs/QUIRKS.md` that will otherwise be discovered late,
in Stage 8, when they are expensive.

**Point-in-time questions are only partly answerable (Q-05).** The snapshot
holds current text. There is no corpus-level version stamp; the amendment log is
the upstream repo's git history. "What guidance was current on «date»" is
answerable only against a full-history clone. Decide in `pilot-scope.md` whether
it is in scope — do not write competency questions that assume it and leave the
assumption implicit.

**Case questions stop at the citation (Q-11).** 519 case edges across 411
distinct decisions exist as citations. **No decision text exists anywhere in the
programme.** "Which cases interpret this test" is answerable. "What did the
court hold" is not, and no amount of Stage 0 work changes that. Write case
questions at citation level, or record the acquisition of decision texts as a
scope question (HANDOFF Q6). This bites on any pilot with a developing case law
dimension, which is worth weighing given why s 43 was chosen.

**Ambiguous provision edges must not be treated as errors (Q-07).** Where
upstream records `certainty: ambiguous`, it is refusing to guess between several
instruments, deliberately. A gold record that "corrects" one to a single
provision is asserting something the corpus does not support and will train the
system to do the same. Record it as ambiguous, or leave it out.

**Superseded provision numbering (Q-06).** Some Manual text cites legislation by
numbering that no longer exists; the pre-2012 s 41 renumbering is called out
upstream by name as a cause of unresolved edges. Before finalising gold records
against s 43, check whether any in-scope refs sit in upstream's unresolved set —
a record that binds guidance to today's provision text when the Manual meant an
earlier numbering will look perfectly well-formed and be wrong. An agent can
produce that list from the snapshot; whether a given case is a renumbering
problem is your call.

---

## 9. What agents will and will not do

**Will:** build and validate schemas, generate the Pass B worksheet, transcribe
your input into records, check every ref and offset, report coverage gaps
("eleven concepts have no `not_labels`"), flag internal contradictions between
records, build the harness and the tests, and keep the documentation current.

**Will not, ever:** write a competency question, decide what a concept means,
judge whether two terms are synonyms, decide a modality, choose a relevance
grade, set a threshold, or decide what is legally impermissible. If you find any
of those already filled in without your name on `approved_by`, treat it as a
defect and tell us — that is CLAUDE.md rule 1 being broken, and the record
should be deleted rather than reviewed.

An agent may say "we have no question testing point-in-time currency". An agent
may not write that question.

---

## 10. Suggested order of work, and rough effort

Order matters more than speed. Each step makes the next one cheaper.

1. **Pilot scope** — half a day, including the exclusions. Unblocks everything.
2. **Competency questions** — a working session. They tell you which chunks
   matter, which defines the Pass B worksheet.
3. **Prohibited uses** — same session if possible. They are easier to elicit
   while the questions are fresh, and they bound the retrieval questions.
4. *(Agents: pin the snapshot, generate the worksheet and the intake
   workbook — `tmk-fetch-upstream`, `tmk-worksheet`, `tmk-workbook`. All three
   are done and re-runnable.)*
5. **Concepts** — Pass A labels first, then attach `definition_sources` from the
   worksheet.
6. **Entities** — the bulk of the volume, but fast per record with the worksheet
   open.
7. **Relationships** — slower; each needs a verbatim sentence and a tier.
8. **Search and retrieval questions** — draft in Pass A, grade in Pass B.
9. **Reasoning expectations and thresholds** — last, because they depend on
   everything above.

Rough per-record effort, as an agent's estimate rather than a commitment:
entities 1–2 min each once the worksheet is open; concepts 10–15 min;
relationships 5–10 min; search questions ~10 min; retrieval questions 15–20 min;
prohibited uses ~10 min. At the low end of every target band that is on the
order of a week of expert time, spread over sessions. At the high end,
considerably more — which is the argument for keeping the pilot boundary tight
and the chunk set bounded.

**Where to start if you have one hour:** write the pilot scope's *exclusion*
list, and three prohibited uses. Both are pure Pass A, both are things only you
can write, and both immediately constrain everything an agent might otherwise
get wrong.

---

## Related

`eval/README.md` (agent-facing) · `eval/templates/` (the schemas) ·
`docs/ROADMAP-STATUS.md` §Stage 0 (status board) · `docs/DECISIONS.md` ADR-0010
(why Stage 0 blocks) and ADR-0013 (the pilot area) · `docs/QUIRKS.md` (the
limits in §8) · `docs/roadmap/AUTOMATION-FIRST-ROADMAP.md` §Stage 0 (the source).

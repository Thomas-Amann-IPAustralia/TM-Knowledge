# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-09-12 · session S023 · branch `claude/gracious-edison-vu5avc`

---
## 0. What S023 did, in one paragraph

**The owner asked whether `ontology/README.md` was still right to say the
ontology is built from section 43. It was — in one place, and it was the place
that mattered.** The class skeleton never was section 43: `document.ttl`,
`authority.ttl`, `provenance.ttl`, `time.ttl` and `evaluation.ttl` model
upstream's shapes and would be identical for any Part. The concept layer stopped
being section 43 in S018. **The relational layer had not moved at all.**
`relations.ttl` is the closed list of predicates extraction may draw from, and
it was generated from `eval/gold/relationships.yaml` alone — 35 signed records
whose **37 source refs all point at `TMM/Part29`**. So the ontology's entire
relational expressiveness was whatever section 43 had happened to need: 14
terms, 6 used exactly once, with no way to say that a concept is *defined by* a
provision, that a step is *performed by* an office, or that one *must occur
within* a period. That is why the graph was in 44 pieces with 0 authored
relationships.

**`tmk-relationships` is the pass that fixes it (ADR-0109).** Deterministic,
seven patterns, each one fixing where the subject and the object sit in the
sentence before it fires. **219 relationships across 45 Parts and both
instruments**, every record stamped `unreviewed` with its span, its
`content_hash`, its reasoning, the readings it rejected and the thing it most
expects to have got wrong. `relations.ttl` is now generated from both registers:
`tmk:ApprovedRelation` keeps its meaning and its 14 terms, `tmk:AuthoredRelation`
holds the 7 a machine used, 4 of them new. The counters are never added. Two
modules stopped explaining their own emptiness by naming the withdrawn boundary
(ADR-0110), and two real defects fell out of the first build (ADR-0111, Q-64,
Q-65).

**Nothing was signed and `eval/gold/` is byte-identical.** The store went from
208 authored records to **427**, and the honest headline is the one on every one
of them: *no expert has read a single relationship in this repository outside
the 35 signed ones.* What the pass produces is evidenced, stamped and
correctable — **not correct**. A sample of the first run found inverted edges on
the active *overcome*, role words read as subjects, and a flattened annex table
read as one sentence; each is now a guard with a test, and
`expert_should_check` on every record names the failure mode its own pattern
still has.

---
## 0a. What S022 did, in one paragraph

**S021 drew the records and the owner came back with three objections, all of
them about the drawing rather than the data: the decision tree was not shaped
like a decision tree, the knowledge graph was not behaving or looking as he
expected, and the content still seemed abstract.** All three are fixed and none
of them needed a record to change. **The grounds spine is now a binary tree of
questions** — each of the 11 anchoring sections asks whether a ground under it
arises, *no* runs the spine straight down to the next section, *yes* opens that
section's questions, and each `legal_test` is a question of its own because that
is what the group already means. 31 questions, 32 leaves, 17 deep, drawn on a
pan-and-zoom canvas where a node can be dragged and its branch comes with it
(ADR-0106). **The map opens on one idea and what it is joined to**, and grows a
hop at a time as the reader opens nodes; every node drags and stays dropped; the
254-node picture is still one button away and still says the graph is in 44
pieces (ADR-0107). **And every concept node now carries the passage its record
quotes**, with the ref and whose evidence it is — which is the whole of the
abstraction fix, and it needed nothing authored: all 130 already had one, four
clicks down (ADR-0108).

**Nothing was authored as legal content and no record changed.** The 190 signed
and the 208 authored records are byte-identical to how S021 left them. The one
thing to hold lightly is the question wording: *Is <label> made out?* is a
mechanical template over a recorded label, and no expert has read a single
question on that page — see ADR-0106 for exactly where the line between
transcription and authorship was drawn, and why the factors hang off the section
rather than off a question.

---
## 0b. What S021 did, in one paragraph

**The project could be counted and could not be seen, and the owner said the
tables and the abstractions were making it hard to comprehend and hard to explain
to stakeholders.** Two pages now render the records rather than tallying them:
**the map** (`#/map`), every concept and every provision it cites as a node
network with a record panel behind each node, and **the examination path**
(`#/tree`), the reasoning groups hung off the Act's sections as a decision tree
and the process groups hung off the 21 procedural steps. Both are generated by
`dashboard/views.py` on every build, from the same two stores everything else
reads, and both say on their face that the *arrangement* is an agent's and
unreviewed. ADR-0103 is the decision that let the site arrange rather than
restate, and it carries three conditions that keep the arrangement checkable.

**What the pictures show that the tables did not.** The graph is in **44 separate
pieces** — one holding 86 of 254 nodes, the rest mostly a single authored concept
beside the provisions it cites — because there are still 0 authored relationships.
**Three sections carry a test and no concept typed as the ground it serves**
(s 14, s 41, s 51). And **5 of 31 non-step process concepts join any step at
all**. None of these is new information; all three were invisible.

**Nothing was authored as legal content and no record changed.** `PU-0003` is the
one thing to read before building on the tree: it prohibits the system stating a
confidence that a ground applies, which is exactly what a probabilistic model
trained on this shape would want to do. It is signed, and only a person can
change it (ADR-0105 consequence 3).

---
## 0c. What S020 did, in one paragraph

**The question "what does the trade marks expert need to look at" had no
answer in the repo, and the two obvious places to look were both wrong in
opposite directions.** The dashboard's *Waiting on a trade marks expert*
heading implies four items and holds one — `OQ-0017`, parked, low urgency;
the other four were answered or withdrawn by the owner on 2026-09-08.
`blockers.md` implies ten decisions are owed to a reviewer and, since
ADR-0084, none is. Meanwhile the largest thing genuinely waiting — 208
records nobody has read — existed only as a *question to the owner*
(OQ-0027), never as a description of the work itself.
`docs/EXPERT-REVIEW-SCOPE.md` now states it in one place: seven items in
priority order, each with **whether an artefact to review actually exists**
(two do, three are agent work first), and an equally long list of what is
*not* the expert's — the frozen 190, the eight rejected records, the eight
unapplied amendments, the ten critical-path decisions. ADR-0100.

**Two findings came out of writing it, and the second is the one to learn
from.** *(a)* **Ten authored concepts reuse a signed concept's preferred
label; seven say so and three do not** — `GC-0053`/`GC-0006` (ground for
rejection), `GC-0100`/`GC-0014` (endorsement), `GC-0101`/`GC-0041`
(evidence of use). Nothing caught it because the harness compares ids and
the ids are correct; nothing anywhere compares labels across the two stores.
The three are the expert's to resolve and an agent may not edit either side
(Q-59, ADR-0101, which also fixes the future check's severity at *note*).
*(b)* **`eval/STAGE-0-INPUT-GUIDE.md` — the repo's only other expert-facing
document — tells its reader that a filled-in record without their name on
`approved_by` is a defect that "should be deleted rather than reviewed".**
Applied today that instruction destroys all 208 authored records. ADR-0079
reached `CLAUDE.md`, `review/README.md` and `authored/README.md` — every
file an agent opens every session — and did not reach the one file whose
audience is not in the session. Banner added; a rewrite is owed (Q-60).

**Then the owner set a constraint that changed the shape of the answer:**
*"assume we only have one more request to send to the subject matter expert."*
Under that assumption the seven-item list is not a plan, it is a
prioritisation problem — three of the seven had no artefact a reviewer could
open, and two of those could not be drafted by an agent at all. `tmk-expert-pack`
generates the consolidated request: `data/derived/expert-request.xlsx` and
`docs/EXPERT-REQUEST.md`, produced in one run from one set of counts so the note
and the workbook cannot disagree. Seven sheets, ordered so that stopping early
still answers the questions that decide the most: 8 cross-cutting questions, then
10 duplicate labels, 9 role words, 5 unjudged modalities, 11 accuracy targets,
then the 78 concepts and the 130 typings. **`concepts` and `concept-types` keep
the intake layout and round-trip through `tmk-transcribe`** — pinned by a test,
because a pack whose answers cannot be read back wastes the one request. The
other five return as words, through the instruction-file route (ADR-0051).
ADR-0102.

**Nothing was authored as legal content and no record changed.** The 190
signed and the 208 authored records are byte-identical to how S019 left them,
and `approved_by` is emptied by the pack in every row it writes.

---
## 0d. What S019 did, in one paragraph

**The taxonomy stopped creaking, and the dashboard stopped contradicting
itself.** The owner asked what was waiting on him or on the trade marks expert
and whether the published site said so. It mostly did, with four faults — and one
omission that mattered more than the four. He then instructed: *"Please create
new groups which most effectively capture the 53 unassigned concepts these will
all be reviewed in one go."* So the four groups became **nine**. Five were added
on a second axis — `process_role` (8), `subject_matter` (14), `procedural_step`
(21), `instrument_or_record` (7), `external_instrument` (2) — and all 53
concepts that had fitted nowhere were retyped in a single pass, each with its
reasoning, the readings it rejected and the thing it most expects to have got
wrong. **One concept stays `none_of_these` on purpose** and that is a finding,
not an oversight: `GC-0051`, *mandatory application of the section*, is a rule
*about* a ground and fits none of the nine. A tenth group to hold one record
would be fitting the taxonomy to the data. ADR-0098, ADR-0099. **No expert has
read any of it, every record says so, `approved_by` is null in all 130 typings,
and 0 of 130 concepts are sorted by a person.**

**The four site faults, and the third is the one to learn from.** The Overview
lede said *"Everything here was signed off by a person before it was modelled.
Nothing on this page was written by an AI as legal content"* — while a stat tile
two blocks below it read *"Records a machine wrote: 208."* That sentence was true
when it was written and ADR-0079 falsified it; ADR-0082 had meanwhile moved the
entire honesty burden onto exactly this surface. The same lede still called the
project a section 43 pilot. **"Six of them unblock the next piece of work" was
hardcoded** and had been wrong since five of the six were answered — the second
count on this site to go stale in prose after Q-46, and now computed. And
`blockers.md` presented ten decisions as waiting on a reviewer when ADR-0084 had
made them agent work eight days earlier.

**The omission was bigger than any of them.** The page that exists to list what
is waiting on a person held ten questions and no mention of the **208 authored
records that no person has read**. A signature is the one thing no amount of
agent time produces, and under ADR-0086 silence never produces one either. That
is now **OQ-0027**, the only `high` on the queue. **OQ-0026** puts the five new
groups and all 53 assignments up for review in one go, as he asked, naming the
four weakest — classification, an IRDA, the divisional/series pair, and
conditions or limitations. OQ-0024 closes.

**What it cost, and what to distrust.** 0 harness defects, 0 SHACL defects, the
graph rebuilds, the dashboard is current, 528 tests pass. Three things to hold
lightly. **The five groups are one model's reading of 53 concepts and nothing
about the owner's instruction settles them** — he asked for groups, not for these
groups. **One concept carries one group**, so where the two axes overlap the
sheet forces a choice: *acceptance* is filed as a step and section 33's
presumption of registrability inside it is filed nowhere. Two columns would fix
it and doubles what a reviewer reads; it is an option on OQ-0026, not a decision
taken. And **`tmk:ProcessRole` is not `tmk:Role`** — a collision that is
invisible today only because the six classes in `examination.ttl` are all
UNDEFINED. Q-58.

---
## 0e. What S018 did, in one paragraph

**The rules stopped saying section 43 in S015. The artefacts stopped saying it in
S018.** The owner asked for the boundary's removal to reach
`data/derived/concept-typing.xlsx` "and throughout the repo", and the honest
answer was that nothing had yet gone looking outside the fence: every concept in
the project was one found inside it, the sorting sheet read
`eval/gold/concepts.yaml` and nothing else, and the knowledge graph was still
built over 216 of the corpus's 2,460 passages. Three passes fixed that.
`tmk-concepts` finds **1,715 candidates** deterministically across all 54 Parts.
**78 concepts** are authored from the 53 Parts the boundary hid, each with its
passages, its argument and the thing it most expects to have got wrong.
`tmk-typing` reads both stores, so the spreadsheet now holds **130 rows** instead
of 52. Then the machinery: `tmk-boundary` deleted, `tmk-recon` re-scoped to the
corpus, the graph's selection rule replaced, `eval/pilot-scope.md` taken off the
completeness gate. ADR-0095 to ADR-0097. **No expert has read any of it, every
record says so, and `approved_by` is null in all 78.**

**Two findings, and the second is worth more than the vocabulary.**

**53 of the 130 concepts fit none of the owner's four groups.** The first 52 came
back 30 `relevant_factor` and 1 `ground_of_refusal`, and OQ-0023 asked whether the
lopsidedness meant the taxonomy was wrong. The wider set answers that: the
lopsidedness was an artefact of a one-ground vocabulary and it evened out. What
did not go away is the pile that fits nowhere, which grew from 7 of 52 to 53 of
130 — the people, the documents, the proceedings, the outcomes and the remedies.
The four groups describe *reasoning about* an application; about two fifths of the
Manual describes *what happens to* one. That is OQ-0024 and it should be settled
before a review round, not after.

**1,551 of the 2,460 chunks — 63% — cite no provision at all.** The old scope rule
selected passages that *cite* a provision, so nearly two thirds of the Manual was
structurally invisible to it. That is the mechanism behind Q-28 and it is now
Q-53: any rule keyed on citation edges inherits the blindness however wide the
provision list, and the candidate pass reads headings and definition text
precisely so it does not.

**What it cost, and what to distrust.** 0 harness defects, 0 SHACL defects, the
graph builds and the dashboard is current. Three things a reader should hold
lightly. The 78 concepts are one model's judgement of a corpus it read once —
several records say in `expert_should_check` that their preferred label is an
invention because the Manual names no term for the idea, and *other traders'
legitimate desire to use* and *protected wine expression* are the two clearest.
Eight of the 78 cover ground a signed record already claims and none of them
displaces it; the overlap is named, not resolved. And ADR-0097's graph rule is
`agent-proposed`: 41 chunks left the graph, the alternative was a 40MB file, and
the trade-off is OQ-0025 rather than a settled thing.

## 1. Where the project actually is

**S015 changed the rules the project runs on, and nothing else. Read this section
before anything, including the rest of this file — most of what is below it was
written under the old rules.**

The owner made two decisions in chat on 2026-09-08, and answered four clarifying
questions about how they land. His words are transcribed verbatim at
`review/returned/260908-owner-chat-scope-and-authoring.md`; the machine-readable
index is `review/rulings/2026-09-08-chat-authoring-mandate.yaml`; the reasoning
is **ADR-0079 to ADR-0088**.

**Decision one — the section 43 boundary is gone.** *"I would like to completely
remove the s43 barrier."* The whole Manual is in scope: 500 pages, 54 Parts,
2,460 chunks. There is no boundary rule, no exclusion list, and no in-scope
judgement for any passage. Section 43 is now the area worked **first**, not a
fence (ADR-0081, supersedes ADR-0022 and ADR-0072).

**Decision two — an agent may author legal content.** *"I would like you to
update your rule so that you can make higher risk decisions AS LONG AS you record
it has not been reviewed or approved by an expert yet."* CLAUDE.md rule 1 is
rewritten from *never invent legal content* to *author, but never launder*. An
agent now writes definitions, concept types, relationships, modality readings,
competency questions, rules and exceptions — each stamped `unreviewed` with its
model, date, evidence and authoring basis (ADR-0079).

**The four clarifications, and they matter more than the headline:**

| | His answer | Where |
|---|---|---|
| Where authored content lives | **Separate; graph reads both.** `eval/gold/` **freezes** at the 190 signed records as the only uncontaminated yardstick; authored content goes to `authored/` | ADR-0080 |
| Whether unreviewed content may be served | **Labelling is enough.** Tier 3 stops being a gate | ADR-0082, supersedes ADR-0008 |
| Whether extraction opens | **Yes — Stages 2–4**, across all 54 Parts | ADR-0083, supersedes ADR-0010 |
| The 178 held seed records | **Resolve them all now, marked unreviewed** | ADR-0084 |

**Then he corrected himself, and tightened the record.** Shown ADR-0085's
four-state reading of *"if it isn't corrected, assume it's valid"*, he withdrew
the premise rather than the reading: *"I think I may have been overzealous… I
would prefer to simply retain 'unreviewed', 'rejected' and 'approved' states."*
So there are **three states and no intermediate credit for having been looked at**
— a record a reviewer saw and did not change stays `unreviewed`, and only a
signature moves it (ADR-0086, supersedes ADR-0085). This is stricter than what he
first asked for, not looser, and it is worth noticing that the correction went
that way.

**And the model question was answered the day it started blocking, in both
halves.** Gemini 3.8 Flash, credential in the `GEMINI_API_KEY` repository secret
(ADR-0087). Corpus text cleared to send — published material, his explicit
permission — with a standing cost rule: *"Things should only really be sent to
Gemini if we're pretty confident that we'll be getting valuable output from it"*
(ADR-0088). HANDOFF Q3 had been open since S001 and was a real blocker for about
four hours.

**He also confirmed the one limit S015 preserved without being asked.** The system
still may not state an examination outcome to an examiner: *"I understand and I
agree with you. We should not change the rule about what the system may say to an
examiner… We can simply move forward with the existing controls."* No change was
made and none is owed — the eleven signed prohibited-use records are the control.

**What S015 actually did: the paperwork, and only the paperwork.** `CLAUDE.md`
rewritten; seven ADRs; the ruling and its transcription; `authored/` created with
its README and its envelope schema; `eval/gold/`, `review/seed/` and `review/`
READMEs re-headed; `ARCHITECTURE.md` and `ROADMAP-STATUS.md` brought into line;
seven questions withdrawn, answered or re-graded on the owner's queue; and
`config.py` gained the authoring-model constants. **No legal content has been
authored yet. No record has moved. The graph is untouched and still holds exactly
what it held at S014.** The next session is the one that uses any of this.

**Three things that did *not* change, and a session that assumes otherwise will
do damage:**

1. **Provenance is untouched and now load-bearing.** Rules 2, 3, 5, 7 and 8 stand
   word for word. The owner was explicit: *"I want to ensure all of the existing
   rules around references to the Act, Regulations and Handbook remain in tact."*
   Rule 8 — no machine output goes anywhere unlabelled — was hygiene before today
   and is now the only thing separating authored content from expert knowledge.
2. **`approved_by` is never written by an agent.** Not with a name, not with a
   model id, not with the owner's initials. Every other guard can be argued
   about; this one cannot.
3. **The product may still not state an examination outcome.** This was flagged to
   the owner in the same exchange and he gave no instruction to lift it. ADR-0082
   removed a *review gate on knowledge*; it did not widen what the system may say
   to an examiner, and the eleven expert-approved prohibited-use records still
   stand as approved knowledge (ADR-0082 consequence 4).

**The honest risk, stated where it will be read.** Before today a wrong statement
in this repo meant an expert made a mistake, and there were 190 of them. From
today a wrong statement means a model made one, and there may be thousands. The
mitigation is the stamp, the evidence requirement and the frozen yardstick — not
confidence in the model. If `authored/` ever fills with `general_knowledge`
records carrying no spans, the scheme has failed quietly and this paragraph is
where somebody should have looked.

### The numbers as at S023

Superseding the S018 table below wherever the two disagree. The S018 figures are
kept because the prose around them explains how each was arrived at.

| | |
|---|---|
| Ontology modules | 9, OWL 2 RL, in `ontology/draft/` — **none approved** |
| Classes declared | **59** (was 50) — three evidence stages added, and more of them hold nothing than before, which is the honest direction (ADR-0110) |
| Predicates | **18** — 14 `tmk:ApprovedRelation` (35 signed records, every source ref `TMM/Part29`) and 7 `tmk:AuthoredRelation` (219 records, read by nobody). 4 of the 7 are new terms. **Never summed** (ADR-0109) |
| Source graph | **53,168 triples over 892 chunks** (was 32,922 over 508). No rule changed — the records now speak about 45 Parts and both instruments |
| Approved graph | 3,243 triples, unchanged, every one traceable to a signed record |
| Authored graph | **8,568 triples** (was 3,441) |
| SHACL | **0 defects, 0 gaps**, 209 notes |
| Harness | **0 defects**, 12 gaps, 10 notes |
| Tests | **573 passing** (was 528), 22 of them new |
| Signed records | **190, frozen, byte-identical** |
| Authored records | **427** (was 208): 78 concepts, 130 typings, **219 relationships**. All `unreviewed`, 0 refused. **0 `general_knowledge`** — 131 `corpus_explicit`, 88 `corpus_inferred` on the relationships |
| Relationship modality | **181 of 219 null**, 38 `must`. Only `must` is read from grammar and every null is reported as a gap (ADR-0109 c3) |
| Relationship sources | **45** Parts and instruments. `Part29` is 10 of 219 |

### The numbers as at S018

Everything about the vocabulary moved, and the source graph moved with it. The
rest is the baseline the next session's work is measured against.

| | |
|---|---|
| Ontology modules | 9, OWL 2 RL, in `ontology/draft/` — **none approved** |
| Classes declared | **50** · **27 hold nothing**. The four typing classes fill in the authored graph only, so no query asking for signed knowledge reaches them |
| Predicates | 14, generated from the 35 approved relationships |
| Source graph | **32,922 triples over 508 chunks** (was 16,405 over 216). The rule changed: every Manual passage any record cites, plus page-mates, plus every chunk carrying an `ambiguous` edge — no provision in it at all (ADR-0097) |
| Approved graph | 3,243 triples, every one traceable to a signed record |
| Authored graph | **3,441 triples** (was 698). 78 concepts and 130 concept typings, every node stamped `tmk:origin "authored"`, its model, its date, its basis and its reasoning |
| SHACL | **0 defects, 0 gaps**, 209 notes — the notes are almost all near-miss pairs, which is what a near-miss is for |
| Competency queries | 13 of 20 questions. All eight that name `tmk:ApprovedAssertion` answer over signed content only, by design. **CQ-0017 now answers over held passages rather than all citing ones** and says so — 56 of 67 for section 43 (Q-57) |
| CONSTRUCT rules | 2. RULE-0002 approved; RULE-0001 pending — **and an agent may not approve it** |
| Signed records | **190, frozen** |
| Authored records | **208** (was 52): 78 concepts, 130 concept typings. All `unreviewed`, **0 refused**. 91 `corpus_explicit`, 117 `corpus_inferred`, **0 `general_knowledge`** |
| Concepts in the project | **130** — 52 signed, 78 authored. Never summed anywhere a reader could mistake one for the other (ADR-0080 c3) |
| Concepts typed | **130 of 130 by a machine · 0 of 130 by a person.** The completeness gate still reads `0 of 50–100` and is right to: it counts `eval/gold/` |
| The typing distribution | `none_of_these` 53 · `relevant_factor` 41 · `legal_test` 17 · `exception` 11 · `ground_of_refusal` 8. **The shape is a finding** — OQ-0024 |
| Concept candidates | **1,715**, in `review/candidates/concepts.yaml`. Not concepts, not authored, no ids — never counted beside the two figures above |
| Authors in the store | **1** — `claude-opus-5`. Not the configured `gemini-3.8-flash`, and the difference is deliberate (ADR-0094) |
| Chunks citing no provision | **1,551 of 2,460 — 63%** (Q-53). No citation-based rule reaches them, and that is why the old scope rule could not see a definition |

Three findings worth carrying, all measured:

- **The vocabulary was a Part 29 vocabulary and no longer is.** 86 of ~95
  definition-source references across the 52 signed concepts point at Part 29.
  The 78 authored ones draw on Parts 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17,
  19A, 19B, 20, 21, 22, 23, 24, 26, 27, 28, 30, 31, 32A, 32B, 33, 34, 35, 38, 40,
  42, 43, 46, 47, 48, 51, 52, 60 and 62.
- **Four of the nine role terms the expert named were absent** — Delegate, Office
  Practise, Subject Matter Expert, Adverse Report. Two of the four are still
  absent: this pass authored *Registrar of Trade Marks*, *applicant*, *opponent*
  and *registered owner*, and did not reach Delegate or Adverse Report. Q-28's
  cause is now Q-53.
- **Eight authored concepts overlap a signed one** — GC-0007, GC-0012, GC-0016,
  GC-0035, GC-0042, GC-0043, GC-0046, GC-0050. Each names the overlap in
  `expert_should_check`. None displaces the signed record and an agent may not
  retire one (ADR-0080 c2 runs the other way).

## 2. The next action

**Nothing is blocked on a human.** OQ-0007 — which model, and may Manual text be
sent to it — was answered on 2026-09-08: **Gemini 3.8 Flash**, credential in the
`GEMINI_API_KEY` repository secret (ADR-0087).

**Three things to know before the first model-backed run.**

1. **Confirm the model id.** `config.DEFAULT_AUTHORING_MODEL` is set to
   `gemini-3.8-flash` and must be checked against Google's current model list
   before it is trusted. A wrong id fails loudly at the API, which is fine; a
   silently substituted one stamps records with a model that did not write them,
   which is unrecoverable.
2. **The key is a repository secret, so it reaches GitHub Actions and not a local
   container.** `config.authoring_api_key()` raises rather than returning empty —
   a run producing nothing for want of a key looks exactly like a run that found
   nothing, and only one of those is a finding.
3. **A call has to earn itself** (ADR-0088). Deterministic pass first, send only
   what is left; batch related judgements into one call rather than one call per
   record; never re-send material whose authored record already exists and is not
   stale. Corpus text may be sent freely. An expert's review notes in
   `review/returned/` and `review/decisions/` may **not** — that was not what the
   permission covered, and it is worth asking about specifically if a prompt
   genuinely needs one.

**The section 43 boundary is gone from the artefacts as well as the rules.**
S015 rewrote the rules, S018 rewrote what they produce. There is no fence left in
code: `tmk-boundary` is deleted, `tmk-recon` costs the corpus, the graph selects
on what the records cite, and the sorting sheet carries concepts from 39 Parts.
`ScopeRule` and `PILOT_PROVISION` still exist and are now a *selector* and a
*default argument* — read Q-55 before assuming either is a boundary.

Everything below is an agent's to do.

**S020 added four, and they are grouped here because they share one cause:
each is a thing standing between the trade marks expert and something they
could otherwise review.** `docs/EXPERT-REVIEW-SCOPE.md` §5 is the readiness
table they come from.

- ~~**Render a review workbook for the 78 authored concepts.**~~ **Done** —
  `tmk-expert-pack` renders them as the `concepts` sheet, pre-filled, with each
  record's evidence and its own "most likely wrong" note beside it, and the
  sheet round-trips through `tmk-transcribe` (ADR-0102).
- **Give a definition a record type — but read the answer first.**
  `authored/definitions.yaml` still has no schema, no id prefix and no place in
  `RECORD_TYPES`. **The pack now asks for the nine role definitions as prose
  instead**, deliberately: building the container before knowing what goes in it
  is how the container ends up the wrong shape. Three of the nine terms are
  absent from every store (*office practice*, *subject matter expert*, *adverse
  report*) and *delegate* exists only inside "the registrar's delegate". Watch
  the `FILE_FOR` ripple (item 5 below).
- **Draft the examiner-conduct rule — after they answer, not before.** Same
  reasoning. It is question 3 on the pack's first sheet, asked rather than
  authored, because a machine paraphrase of their August note is the one version
  of it nobody needs. The structure exists (ADR-0073) and is empty.
- **Write the cross-store label check.** Ten authored concepts reuse a signed
  concept's `pref_label` and nothing compares labels across the stores.
  `expertpack.duplicate_labels()` is the detector and already judges disclosure
  across the whole store, not just the concept's own record — lift it rather
  than writing a second one. **ADR-0101 fixes its severity at *note*, not
  defect** — seven of the ten are the design working — so do not relitigate
  that. `alt_labels` are deliberately not covered and that gap is open.

**In order of value:**

1. ~~**Relationships, and they are the biggest hole in the graph.**~~ **Done in
   S023** — `tmk-relationships` authored 219 across 45 Parts and both
   instruments (ADR-0109). What is left of it, and what to do next:

   - **Read `data/derived/reports/relationships.md` §4 first.** It lists the 25
     weakest edges, lowest confidence first. `requiresElement` and
     `isPerformedBy` are the two patterns to distrust: the first reads the
     direction of a requirement off word order, and the second's 9
     applicant-performs edges are the ones most likely to be passives it could
     not see.
   - **Three predicates in the authored half are barely used** —
     `isOvercomeBy` 2, `requiresElement` 7, `doesNotGiveRiseTo` 0. The corpus
     states more of all three than that; the patterns are narrow on purpose
     after the first run produced inversions. Widening one is a pattern change
     with a test, not a threshold tweak.
   - **The `modality` trap is unchanged.** Signed `GR-` records have five blank
     modality fields and an agent may not fill a field inside a signature. A new
     authored relationship carries its own and is fine; an old signed one is
     not, and needs a record type that does not exist (ADR-0071's shape).
   - **Concept-to-concept edges from the concept records themselves.** Every
     concept authored in S018 names near-misses and several name a broader or
     narrower *in prose* that no record carries. This pass read the corpus, not
     the records, so none of that was picked up — and it is cheaper and better
     evidenced than anything sentence matching can do.

2. **The record types still furthest under their band**, all additions needing no
   new machinery: `search-questions.yaml` (1 of 20–50),
   `retrieval-questions.yaml` (10 of 20–50), `entities.yaml` (55 of 100–300).
   Entities in particular are now cheap in a way they were not: the source graph
   reaches 508 chunks across most of the Manual, so a mention has somewhere to
   land.

3. **The 1,715 candidates are sitting in `review/candidates/concepts.yaml` and
   78 of them became concepts.** The next pass over them should start with the
   137 the corpus actually *defines* — strength 2 and 3 — of which roughly half
   are still unauthored, and it should skip the 348 Part 14 class headings, which
   are goods categories rather than legal ideas and are ranked low for that
   reason.

4. **Nothing retires an authored record when a signed one covers it**, and there
   are now 208 authored records waiting to need it rather than 52. Q-52 is
   unchanged and is the next real design question in this area: the reviewer's
   row keeps the authored record's id, so the first signed typing puts one `GT-`
   id in both stores and the harness reports a defect naming both. That is
   designed. Do not resolve it by minting a fresh id or deleting the authored
   record.

5. **`authored/definitions.yaml` still has no record type.** It needs a schema in
   `eval/schemas/`, an id prefix in `docs/IDENTIFIERS.md` §3, and entries in
   `RECORD_TYPES`, `ID_PREFIXES` and `goldset.GOLD_FILES`. Watch the ripple:
   `goldset.FILE_FOR[record_type]` is read in message text, so a record type
   added to one map and not the others raises `KeyError` inside a message.

6. **The eight competency queries still name `tmk:ApprovedAssertion`** and
   therefore answer over signed content only. That is under-reporting rather than
   laundering and it is safe, but it now hides 78 concepts rather than 0.
   Whether they should also serve authored content — labelled, per ADR-0082 — is
   a Stage 7–8 question about the retrieval surface and it needs deciding before
   anything is built on those queries.

7. **Then extraction** (ADR-0083), deterministic paths first, measured against
   the frozen 190. `tmk-concepts` is the first deterministic pass and the shape
   the others should copy: lookups only, evidence cut from the snapshot, and a
   candidate file that authors nothing.

**Three things flagged for the owner, none blocking.** ~~OQ-0024 asks whether the
four groups should grow~~ — **answered 2026-09-09: they did, and OQ-0026 replaces
it.** OQ-0026 puts the five new groups and all 53 assignments up for review in one
pass, which is how he asked for them; its four named weak points are the ones to
read first. OQ-0027 asks how the 208 unreviewed records reach a signature and is
the only `high` on the queue — not because anything breaks without it, but because
it is the one piece of work no amount of agent time can do and it had never been
put to him. OQ-0025 asks whether the graph should carry the whole Manual at a cost
of about 30MB, because ADR-0097's rule is `agent-proposed` and his to overturn.

**A note for whoever picks up the next authoring pass.** The nine groups are now
the taxonomy, and `typing.GROUPS` is the one place they are written down —
`REASONING_GROUPS` are the owner's four and untouchable without him,
`PROCESS_GROUPS` are the agent's five and provisional until OQ-0026 comes back.
Anything new that types a concept reads that tuple; do not hardcode a group name
anywhere else. The schema enum, the workbook dropdown, the ontology classes and
the harness label all already follow it.

### What the plumbing gives you, in the order you will meet it

Written out because the next session starts cold and the alternative is reading
four modules to find out.

| You write | It happens | Where |
|---|---|---|
| a record with no `authored:` block | **refused** — kept, named, reported as a defect, in no count and no graph | `authored/store.py`, `tmk-harness` |
| `approved_by: "TC"` | defect, twice — once over the store, once as a SHACL violation over the graph | ADR-0090, ADR-0091 |
| an id `eval/gold/` already uses | defect naming the other store and the file | ADR-0080 c1 |
| `review_status: approved` | defect. Approval moves a record to `eval/gold/` and only `tmk-transcribe` writes it | ADR-0090 |
| `authoring_basis: general_knowledge` | note, listed per record and as a proportion of the store. Never a defect | ADR-0079 guard 2 |
| `authoring_basis: corpus_explicit` with no evidence | envelope fails — refused | the schema's own conditional |
| an evidence `quote` that was retyped | defect: the quote must be exactly the text at its span | ADR-0090 c3 |
| 78 authored concepts | the board still reads `0 of 50–100` in the **Signed** column and `78` in **Authored** | ADR-0080 c3 |
| an authored typing naming a concept in neither store | defect, `authored-cross-reference`. Added S018 — the schema had promised this check since ADR-0071 and nothing performed it | ADR-0095 c4 |
| a concept only `authored/` holds | it reaches `data/derived/concept-typing.xlsx` like any other, with `[concept authored by a machine, unreviewed]` in its `notes` cell | ADR-0095 |
| a record citing a Manual passage nothing else cites | the passage joins `graph/source.ttl` on the next build, with its page-mates. No scope decision, no code change | ADR-0097 |
| a record citing an Act or Regulations ref as its `source_ref` | resolves, and staleness is checked against the unit or provision. It did **not** until S023 — the lookup read `corpus.chunks` only and reported 46 perfectly good refs as "naming a source not held" | ADR-0111, Q-64 |
| an authored relationship using a predicate no signed record uses | `relations.ttl` gains the term on the next `tmk-ontology-relations --write`, typed `tmk:AuthoredRelation` and **not** `tmk:ApprovedRelation`. A test fails if the committed file has drifted from a regeneration | ADR-0109 |
| `modality` on an authored relationship | only `must` is ever written from grammar. `may` and `should` stay null and are reported as gaps — 181 of 219 are | ADR-0109 c3 |

`tmk-harness --authored-dir <dir>` and `tmk-coverage --authored-dir <dir>` point
the checks somewhere else, which is how the fixtures are exercised.

**Do not** fill `approved_by`. **Do not** write into `eval/gold/`. **Do not**
approve RULE-0001 — a rule's `approved-by` line is the same artefact as a
record's, and ADR-0079 does not license filling either. **Do not** widen what the
product may say to an examiner. **Do not** author a record with no evidence and no
`general_knowledge` flag. **Do not** relax `additionalProperties: false` on a
record schema to make an envelope validate — the envelope is split off the record
before validation, and that strictness is what catches a misspelt field in a gold
record (Q-48).

## 3. Open questions — need a human

> **Most of this table was written under rules that no longer apply (ADR-0079 to
> ADR-0085), and it is kept rather than rewritten because the reasoning in it is
> still the best account of how each question arose.** Read it with three
> corrections in mind:
>
> - **Q8 is closed, and as of S018 the code agrees.** It asked where section 43
>   stops. It does not have to — the boundary is withdrawn, the whole Manual is
>   in scope (ADR-0081), and `tmk-boundary` is deleted rather than left computing
>   an answer to a withdrawn question (ADR-0096).
> - **Every question marked "expert content, and nothing here may write it" is
>   wrong now.** Q16, Q17 and Q19 name things an agent may author today, stamped
>   `unreviewed`. Q19 is the one to be careful with: the *judgement* is now
>   authorable, but reading through an ambiguity upstream deliberately refused to
>   resolve is still forbidden (CLAUDE.md rule 6, second half). The two halves of
>   Q19 come apart and a session that misses that will resolve the wrong one.
> - **Q3 is answered.** It moved from "blocks nothing today" to blocking when
>   Stages 2–4 opened, and was settled the same day: Gemini 3.8 Flash, credential
>   in `GEMINI_API_KEY` (ADR-0087). Its second half — the agency's data-handling
>   conditions — is outstanding and named as such.
>
> The confirmation questions — Q12, Q15, Q18, Q20 to Q26 — are unaffected and
> still change nothing structural.
>
> - **S020: do not read this table as the expert's worklist, and do not read the
>   dashboard's expert theme as one either.** Of the five questions marked
>   `needs: expert` in `open-questions.yaml`, four were answered or withdrawn by
>   the owner on 2026-09-08 and only `OQ-0017` is live. What a trade marks
>   expert is actually being asked to look at — including three items with no
>   artefact rendered yet — is `docs/EXPERT-REVIEW-SCOPE.md` (ADR-0100).

| # | Question | Blocks | Raised |
|---|---|---|---|
| ~~Q1~~ | ~~What is the pilot scope?~~ **Answered S002: s 43** (ADR-0013). The *boundary* is deliverable 1 — see Q8. | — | S001 |
| ~~Q8~~ | **Closed S018.** The question was *what is the s 43 boundary*, and the owner answered it by withdrawing it (ADR-0081). The code that kept computing one — `tmk-boundary` and `data/derived/reports/boundary.md` — is deleted, the deliverable is off the completeness gate, and `review/seed/pilot-scope.seed.md` is re-headed as withdrawn (ADR-0096). His one-hop rule is preserved in ADR-0072 and in `review/returned/260908-owner-notes-issue-12.md`; what is gone is anything still applying it. **OQ-0021 — whether a bare "section 41" citation reaches the whole provision — went with it**: it was a question about where a boundary stopped. | — | S002 |
| ~~Q2~~ | ~~How does this repo get the upstream snapshot?~~ **Answered S003, built S004** (ADR-0004, ADR-0021, ADR-0026). | — | S001 |
| Q3 | Which LLM is "agency-approved" for the Stage 2–4 extraction steps, and under what data-handling conditions may Manual text be sent to it? **Now also touches Stage 0:** `review/seed/` records carry `model: null` because naming one would pre-empt this (ADR-0043 consequence 4). If the agency requires the model recorded, it is a provenance field and a one-line change. | Stages 2, 3, 4 | S001 |
| Q4 | ~~What does "approved" look like as a recorded artefact?~~ **Answered S006: the workbook's `approved_by`/`approved_date` columns are the artefact** — a name and a date, no separate signed-off file or external register (ADR-0039). **Still open: who are the approving experts?** — expected to arrive with the experts' own content. | Nothing structural; who-question blocks nothing today | S001 |
| ~~Q5~~ | ~~Does ADR-0005 hold?~~ **Answered S003: yes** (ADR-0021). | — | S001 |
| Q6 | **Answered in principle S012, and the answer opened a bigger question.** The owner said in scope, from `IP-Decision-Data`. Checked: 15 of our 58 in its index, 43 not, and no decision text committed anywhere. OQ-0018. Original question: is acquiring decision texts in scope for this repo? **Costed for the pilot:** 58 distinct decisions are cited from the 216 in-scope chunks. The harness reports a case ref as a NOTE — checked for grammar, resolvable by nothing (Q-11). | Stage 2 citation resolution, Stage 8 retrieval | S001 |
| Q7 | What base IRI may the project mint under? `docs/IDENTIFIERS.md` proposes `https://data.ipaustralia.gov.au/tmk/`; persistent IRIs need control of that domain, which is an organisational call. Still not blocking: one constant in `config.py`, overridable by `TMK_BASE_IRI`. | RDF serialisation only | S001 |
| ~~Q9~~ | ~~Does the owner accept **ADR-0016** and **ADR-0018**?~~ **Answered S006: yes, both** (ADR-0038). | — | S003 |
| ~~Q11~~ | ~~Five S004 ADRs are agent-proposed: 0024, 0026, 0027, 0028, 0029.~~ **Answered S006, in part:** 0024, 0026, 0027 confirmed (ADR-0040); 0028 reversed, not confirmed (ADR-0042, `data/derived/` is now committed). **0029 still open** — owner had no context for it ("I have no idea what this means"); it needs none, since it already reflects current practice and nothing hinges on ruling it either way. | Nothing | S004 |
| Q12 | Six S005 ADRs are agent-proposed: **0030** (three severities, three exit codes), **0032** (one named gold file per record type), **0033** (the retired-id ledger), **0035** (`openpyxl` as an optional extra — *the only one that is a dependency decision*), **0036** (the workbook's cell encoding), **0037** (how transcription writes). ADR-0031 and ADR-0034 are `derived`. Owner has seen a plain summary of these (S006) but has not yet ruled on them. | Nothing | S005 |
| ~~Q13~~ | ~~Does upstream need a token in CI?~~ **Answered S006: no.** `manual-XtrACTor` is public (QUIRKS Q-13, amended S004) and GitHub Actions clones public repos anonymously, so `tmk-fetch-upstream` works in CI with `UPSTREAM_TOKEN` unset. Leave the secret unset unless the repo's visibility changes. | — | S005 |
| Q15 | **New, S007.** Does the owner confirm **ADR-0043** as recorded, including its six guards and its reversal condition? The decision to seed was the owner's; the *guards* — quarantine, the envelope, the null-and-checked `approved_by`, the single door out, the untouched harness, the delete-after-review rule — are the agent's reading of what makes it safe, and they are what an audit will be judged against. **ADR-0044** and **ADR-0045** are `derived` and need no ruling. | Nothing today; the seed set is usable either way | S007 |
| Q16 | **Answered S012 by the owner, not the expert.** He said it may go in a glossary and to adopt a Must/May predicate if a glossary does not capture the examiner/registrar relation. It does not; the predicate already existed (`tmk:modality`) and what was missing was a role as a term, now fixed (ADR-0073). **No conduct rule has been written** — that is still expert content, as OQ-0022. Original: **expert content.** The expert's note says the seed set carries the *presumption of registrability* and the idea of "doubt", but not the office's actual bar for applying it: it is not enough for the individual examiner to doubt a connotation exists — the Registrar as a whole must, and an examiner is expected to consult their team leader and the s 43 SMEs before accepting on that basis. They cite *Blount Inc v Registrar of Trade Marks* (1998) 40 IPR 498, 503 (*Oregon*) on s 33 and the reversed burden. **This is a rule about examiner conduct, and no record type currently holds it**: it is not a concept, not a relationship between provisions and not a prohibited use. Whether it becomes one, a new record type, or an entry in the scope document is an expert-and-owner call. Full text at `review/returned/260826-expert-feedback.md`. | The s 43 vocabulary's usefulness, and any later rule modelling | S008 |
| Q17 | **Answered S012 by the owner.** Scope covers what the ontology needs, a glossary is permitted, and a definition must come from the Manual, the legislation or the IP First Response glossary — and from nothing else (ADR-0074). The third source is not held; acquiring it is part of OQ-0018's territory. Original: **expert content.** The same note: the seed vocabulary was drawn from Part 29 alone, which is "not wrong" but gives "a limited view on what some of the roles are". Nine terms named as needing high-level definitions — Registrar, Delegate, Examiner, Decision Maker, Office Practise, Subject Matter Expert (SME), Oppositions, Grounds for Rejection, Adverse Report — "and there are likely more". Two row corrections say the same thing sharply (`GE-0010`, `GE-0047` on decision maker vs the Registrar). **The structural trap is Q-28**: ADR-0022's scope rule selects passages that *cite* s 43, and a term's definition is usually not in a passage that cites anything. Fix is a scope exception, a separate definitional pass, or a glossary import — expert and owner, not an agent. | Stage 3's vocabulary, and the entity type taxonomy | S008 |
| Q18 | **New, S008. Partly answered.** ADR-0048 gates `eval/gold/` on the reviewer's verdict. The rule itself — *a row crosses only on `correct` **with a name in `approved_by`*** — follows from rule 4 and ADR-0039 and needs no ruling. Three things inside it were the agent's judgement, and in plain terms they are: **(a)** if a record you signed points at one you did not, the signed one is held too — because a gold record naming a record that is not in the gold set is a pointer to nothing, which the harness calls a defect; **(b)** if a record is signed but one of its *sub-rows* (a relevance grade, an expected inference) is marked `amend` or left blank, the whole record is held — because that sub-row is part of the record, so writing it would certify a value the reviewer said was wrong; **(c)** a verdict cell that is not exactly `correct`/`amend`/`reject` — `corrrect` — stops the row rather than being read as the value it resembles. **(c) is now settled in practice** (ADR-0052): the tool stayed strict and a person overrode that one cell by name, which cost one line. (a) and (b) still stand as written and are what "18 held, then 20" in §1 is measuring. **ADR-0047, ADR-0049 and ADR-0050 are `derived`.** | Nothing today; the loop works either way, the yield changes | S008 |
| Q20 | **New, S008.** Does the owner confirm **ADR-0051**? A reviewer's decision that arrives as words is applied from an instruction file in `review/returned/`, never by editing or generating a workbook, and the instruction may do exactly two things: sign a **blank** `approved_by` on a row already marked `correct`, and settle a verdict on a **named** record. The two-operation limit is the judgement — it is what stops "they confirmed the corrections" becoming a blank cheque over 368 rows. Widening it (a pattern, a typo table, "sign everything") should be a decision, not a convenience. | Nothing; every future round that settles anything by email | S008 |
| Q19 | **New, S008.** The expert rejected both `ambiguity_collapse` prohibitions on a principle worth recording: inferring that a bare "section 15(1)" means the *Trade Marks Act 1995* "is acceptable due to the TM focused nature of the tool", and the tool "should be allowed to clarify if a passage is specifically sourced from the legislation". That sits against Q-07 and upstream's refusal to auto-resolve an ambiguous edge. They are not quite the same claim — upstream's `ambiguous` is about *which of several instruments in scope*, not about a bare section in a TM-only tool — but a session must not quietly assume either reading. Does the distinction hold, and where is the line? | Stage 2 citation resolution; the prohibited-use set's sixth kind now rests on one record | S008 |
| Q21 | **New, S009.** Does the owner confirm **ADR-0054** — what counts as a decision on the critical path? Three kinds are on the worklist (holds something and is directly resolvable; names a rejected record; held only by a marked child row) and two things are deliberately off it (a record dangling on something merely unreviewed, and a rejected record as a source of edges). The judgement being flagged is that a root need **not** be unblocked: `GA-0002`, `PU-0013` and `PU-0014` name each other in a triangle, an "unblocked roots only" rule finds none of them, and that would have hidden the largest chain on the queue. | Nothing; the report is right either way, the worklist changes length | S009 |
| Q22 | **New, S009.** Does the owner confirm **ADR-0055**'s third guard? A scoped round's pack and workbook state on their face that they are scoped, with the count they were narrowed from. The alternative — a ten-record workbook that looks exactly like a 368-record one — is how a partial review comes to be filed as a complete one. Guards 1 (the checks never narrow) and 2 (an unmatched name refuses the run) follow from rule 6 and need no ruling. | Nothing; every scoped round from here | S009 |
| ~~Q23~~ | **Answered S012: commit everything** (OQ-0005, ADR-0070, supersedes ADR-0060). Original: does the owner confirm **ADR-0060** — that `graph/approved.ttl` and `graph/inferred.ttl` are committed while `graph/source.ttl` and `graph/dataset.nq` are not? The line drawn is *what a file restates*: the first two are this repo's own decisions in RDF, the second two are 6.5MB of the pinned corpus, and committing those is `data/upstream/` by another route (ADR-0004). Arguable the other way — committing everything would make the graph reviewable without a snapshot fetch, at 6.5MB per rebuild in the history. | Nothing; it is one line of `.gitignore` either way | S010 |
| Q24 | **New, S010.** Does the owner confirm **ADR-0061** — that a competency query is *refused* without a `limits:` header saying what it does not answer? The requirement is the agent's reading of what `queries/README.md` implies rather than what it says, and the 60-character threshold is arbitrary. What argues for it: three limits lines are load-bearing today and each would have been a wrong answer without one — CQ-0017 measures reviewing effort and not outcome, CQ-0019 finds recorded dependencies and not subject matter, CQ-0023's most important row is a blank one. | Nothing today; every query written from here | S010 |
| Q25 | **New, S011. Four dashboard judgements.** All are `agent-proposed` and none blocks anything. **(a) ADR-0063** — the site reads committed artefacts only and never the snapshot, which costs it the best single figure in the corpus (five Manual Parts carried into the s 43 impact set entirely by inferred citations) in exchange for a build that cannot fail on a network. **(b) ADR-0064** — eight block kinds is a guess at what the site will need; the risk is a page that wanted a real visualisation getting a table because a table was easy. **(c) ADR-0065** — the 17 entries in `open-questions.yaml` are an agent's reading of which handoff questions are the owner's and how to phrase them, and an option list can steer. **(d) ADR-0066** — a prefilled issue URL has a length limit, and `author_association` is a coarse answer to "may this person write here". Each is answerable by using the thing and saying what is wrong with it. | Nothing | S011 |
| Q14 | **New, S006.** Owner asked for more plain-language guidance on **constructing the ontology**, beyond what `STAGE-0-INPUT-GUIDE.md` covers (which is scoped to Stage 0 elicitation, not Stage 5 ontology formalisation). Not scoped or drafted yet — needs its own session: who is the audience (the Trade Mark experts already working from the input guide, or a wider group?), and what specifically is unclear in the existing docs. | Nothing yet; would help the experts' ongoing work | S006 |

**S010 changed which thread is blocked, and it is worth being precise about
what it did not change.** The owner's instruction paused the expert round; it did
not answer Q8, Q16, Q17 or Q19, and those four are still expert content that
nothing here may write. What it did do is make Q4's who-half answerable in a new
way — the owner has now signed nothing, but has undertaken to rule, and their
approvals go in `approved_by` exactly like the expert's, with no separate marker
(their choice, S010). **A consequence worth stating plainly: once the owner signs
a record, owner review and TM-expert review become indistinguishable in the
record.** That was the owner's call, made knowing it; it is recorded here rather
than in an ADR because nothing has been signed yet.

| Q27 | **New, S016.** **ADR-0090** is `agent-proposed` in one part only, and it is a small one. That a filled `approved_by` in `authored/` is a defect follows from ADR-0079 guard 3; that an id in both stores is a defect follows from ADR-0080 consequence 1; that `general_knowledge` is a note follows from ADR-0079 guard 2. The judgement is the fourth check: **`review_status: approved` in `authored/` is treated as a defect**. ADR-0080 says a record moves to `eval/gold/` through `tmk-transcribe` and by no other route, so an approved record sitting in `authored/` is either a transcription that did not finish or a status an agent wrote — but ADR-0080 does not say that in terms, and a future flow that wants to stamp `approved` in place and move the record afterwards will hit this check. `rejected` is deliberately *not* a defect, because a rejected record has nowhere else to live. **Deliberately not put in `open-questions.yaml`**: it changes nothing the owner can see, it is answerable by the session that first hits it, and the new bar (CLAUDE.md §3 step 6) reserves his queue for what an agent genuinely cannot settle. | Nothing today; the first flow that transcribes an authored record | S016 |

| Q28 | **New, S017.** **ADR-0092** is `agent-proposed` in one part, and it is the part with a real downside. That the 52 concepts get typed is not a judgement — the owner ruled the four groups right on OQ-0001 and ADR-0079 says who may fill them in. **The judgement is pre-filling the reviewer's workbook with the machine's answers.** The argument for it is ADR-0079's own premise, that experts correct faster than they compose, and that withholding the answers while publishing them in a YAML file next door is the premise with none of the benefit. The argument against is concrete: **a pre-filled sheet is the one place in this design where a person could sign a machine's answer without engaging with it**, and 52 signatures obtained that way would be indistinguishable in the record from 52 considered ones. Four guards are in place — the banner, `approved_by` left empty by the code, a refused record pre-filling nothing, and `tmk-transcribe` still the only door — and none of them can make somebody read. **Not put in `open-questions.yaml` as its own entry**: OQ-0023 already puts the typing pass in front of him and the third option there is "do not decide until an expert has read the 52", so a reviewer who wants the conservative route has it. If he answers OQ-0023 and says the pre-fill was wrong, the fix is one line in `typing.rows()`. | Nothing today; the first review round that uses the sheet | S017 |

| Q26 | **New, S013.** **ADR-0076** is `agent-proposed` in one part only. That the form must not present a settled question as one waiting on you is not a judgement — it is rule 6, and the owner reported it himself. What he has *not* been asked is whether answered questions should fold away behind a summary line, stay expanded in place, or leave the page once they are settled. The fold was chosen because the queue's value is that nothing quietly disappears and the top of every section should still be actionable; reading what he decided costs one click. **Deliberately not put in `open-questions.yaml`**: adding an eleventh question about the ergonomics of the question list works against the problem he reported. A word on any submission changes it. | Nothing | S013 |

**S012's own ADRs.** `human`: **0068** (RULE-0002 approved), **0070** (commit the
whole graph), **0071** (concept types), **0072** (the one-hop boundary), **0073**
(a glossary does not capture it), **0074** (three sources for a definition),
**0075** (a boundary is not a gap) — each quotes the owner's words and names the
ruling file. `derived`: **0067** (repairing the ruling path), **0069**
(conclusions and triples counted apart). **None of S012's ADRs is
`agent-proposed`**, which is what it looks like when a session is acting on
decisions rather than making them.

Agent-proposed ADRs awaiting human confirmation: **0011** (deferred, not
declined — see ADR-0041), **0029, 0030, 0032, 0033, 0035, 0036, 0037**,
**0043's guards** (the decision to seed was the owner's; how it is fenced is
Q15), **0048's first two judgement calls** (Q18; the third is answered by
ADR-0052), **0051's two-operation limit** (Q20), **0054** (Q21), **0055's
third guard** (Q22), **0060** (Q23), **0061** (Q24) and **0063, 0064, 0065,
0066** (Q25), **0076's fold** (Q26), **0090's one judgement** (Q27) and
**0092's pre-fill** (Q28). **ADR-0093 and ADR-0094 are `derived`** — the first
because collapsing an answer into an absence is rule 6, the second because a
model id that is not the model that wrote the record is unfalsifiable
afterwards. **ADR-0095 and ADR-0096 are `derived`** — the first because the
owner asked for the boundary's removal to reach the artefacts, the second
because code answering a withdrawn question is worse than code that fails, and
`docs/ROADMAP-STATUS.md` had said so since S015. **ADR-0097 is
`agent-proposed`** and it is the one to look at: it decides how much of the
Manual the graph carries, the alternative is a 40MB artefact, and OQ-0025 puts
the trade-off to the owner.
**ADR-0098 is `human` in one half and `agent-proposed` in the other**, and the
split is the thing to keep straight: *that* there are new concept groups is the
owner's instruction and cannot be overturned by an agent; *which five, called
what, holding which of the 53* is one model's judgement, is stamped `unreviewed`
on all 53 records, and is asked as OQ-0026. A session that reads it as settled
will build on a taxonomy nobody has agreed. **ADR-0099 is `human`** — the four
site fixes are his instruction, quoted in the ADR.
**ADR-0100 is `derived`** — nothing in it decides anything; it states in one
place what was already true across six files. **ADR-0102 is `human`** — the
one-request constraint and the two deliverables are the owner's instruction,
quoted in the ADR; the five judgements inside it about how to satisfy it are the
agent's and are named there as such. **ADR-0101 is `agent-proposed`**
and the judgement is one line: a duplicate `pref_label` across the two stores
will be reported as a *note* and not a defect. The argument against is in the
ADR — a note is easy to ignore, and this one survived two authoring sessions and
a zero-defect harness run unnoticed.
**ADR-0062 is `human`** — the dashboard is the owner's
instruction, quoted in the ADR. ADR-0044, ADR-0045, ADR-0047, ADR-0049, ADR-0050 and
**ADR-0053** are `derived`. **ADR-0052 is `human`.** **ADR-0089 and ADR-0091 are
`derived`** — the first follows from the record schemas and from rule 6, the
second from ADR-0080's own words.
(0006, 0012, 0014, 0024, 0026, 0027 confirmed S006 — ADR-0040; 0016 and 0018
confirmed S006 — ADR-0038; 0028 superseded S006 — ADR-0042. ADR-0023,
ADR-0025, ADR-0031 and ADR-0034 are `derived`.)

**What S012 changed about being blocked.** The four rulings S010 named as the
shortest path to a better ontology are answered, and three of the four are done.
The fourth — typing the 52 — is now blocked on one pass of a spreadsheet rather
than on a decision, which is a different and much shorter kind of waiting.

**No agent work is blocked on a human decision.** Every remaining open question
is expert content (Q8, Q16, Q17, Q19), organisational (Q3, Q7, the who-half of
Q4 — though Q4's who-half is now half-answered: the reviewer signs `TC`), scope
for later (Q6, Q14), or a confirmation that changes nothing structural (Q12,
Q18, Q20, Q23, Q24, and 0029/0030/0032/0033/0035/0036/0037 within them).

**But the highest-value work now *is* blocked on a human, and that is new.** The
four rulings in §2 are the shortest path to a better ontology, and none of them
is an agent's to make. Typing the 52 concepts is one pass over a list for someone
who knows the domain; it is unavailable to any amount of agent time.

> **Overtaken by ADR-0079, and the paragraph above is kept because it is the
> best account of what changed.** An agent may author the typings now, and did:
> S017 typed the 52, S018 typed 130. What is still unavailable to any amount of
> agent time is a *signature* — `approved_by` is null on every one of them and an
> agent may never fill it. The waiting moved from "somebody must compose this" to
> "somebody must correct and sign this", which is the whole of the bet ADR-0079
> made.

**What is blocked is the gold set, and the critical path is ten decisions.**
`data/derived/reports/blockers.md` is the live version and this file is not —
read it there. In outline: `GA-0002`, `CQ-0013` and `CQ-0014` are three chains
holding 17 records between them; `PU-0012`, `GA-0016`, `GA-0021` and `GX-0002`
name records the reviewer rejected and so must repoint or withdraw; and
`GS-0001`, `GS-0002` and `GS-0004` are signed search questions held by a
relevance grade each. The scoped workbook for all ten is rendered.

## 4. Do not redo these

> **Six entries below were reversed on 2026-09-08 and are struck through in
> place.** Everything not struck through still holds, and the provenance entries
> hold harder than before: they are now the only thing separating machine-authored
> content from expert knowledge.

- **Do not re-parse the Manual HTML or the legislation `.docx`.** ADR-0002.
- **Do not rebuild the decision tree on a shared Manual Part, or on the nearest
  ground concept.** Both were built and measured in S021 and both are wrong in a
  way that is invisible unless you count. Greedy nearest-ground gave `GC-0006`
  59 children and `GC-0053`, which carries the same label, none. Joining on a
  shared Part put all 30 of Part 29's factors under section 33 as well as section
  43, because one concept cites both sections and the Part is the join. The rule
  that works is in ADR-0105 and the numbers are in `views.py`.
- **Do not turn the grounds spine back into an outline, and do not make a factor
  a branch point.** The bands — *Ground of refusal*, *Legal test*, *Relevant
  factor* — read as steps and are not: a reader met three headings before they
  met anything they could answer. A `legal_test` is a question because the group
  is defined as one; a `relevant_factor` is *something that feeds into that
  answer* and is read **at** a branch point, hanging off the section rather than
  off a question. Section 33 settles it independently — it holds factors and no
  test, so a factor filed against a question is a factor nobody can reach.
  ADR-0106, and three tests pin it.
- **Do not make the procedural spine binary.** A step is reached, not decided.
  `test_the_process_spine_asks_nothing` fails if a gate ever appears on it.
- **Do not join two records on a definition ref.** `TMA1995/s6/assignment` says
  where a word is defined, not where a step happens; every defined term in the
  Act cites the same provision, so joining on one joins the dictionary to itself.
  `ConceptView.joinable_sections` is the filter and a test pins it.
- **Do not fit, measure or lay out inside a renderer's first pass.** A block is
  built detached and every measurement reads 0 until the router appends it, with
  no error anywhere. Measure in a `requestAnimationFrame` after returning the
  block, and let the "already done" flag record whether the measurement
  *succeeded*. Q-63.
- **Do not retune the map's force constants without checking the result.** The
  first plausible set diverged: positions grew without bound and the picture
  rendered as a diagonal streak. Divergence in a spring model is silent — the
  maths runs and only the rendering looks odd. The comment above the constants in
  `site/network.js` says what to measure.
- **Do not design a new identifier scheme.** ADR-0005, and `refs.py` implements
  it. Argue with the ADR, don't invent a third.
- **Do not write a second ref parser, IRI minter, snapshot reader, gold-set
  reader, authored-store reader or workbook layout.** There is exactly one of
  each, and the whole point of `stage0/intake.py` is that the workbook's columns
  exist in one place.
- **Do not write a second graph builder for authored content.** `_build_store`
  is one mapping run twice, parameterised by a `Store`. A second builder would
  be a second answer to "what does a concept look like in RDF", and the two
  would drift (ADR-0091).
- **Do not add an attribute that sums the two stores.** Not on `Report`, not on
  `BuildReport`, not in a report template. The moment one exists, something
  prints it, and the number it prints is the flattering one (ADR-0080 c3).
- **Do not "fix" a ref that fails validation.** `InvalidRef` means the ref was
  constructed rather than read. Find the construction.
- **Do not commit anything under `data/upstream/`** (ADR-0004) — that would
  vendor another repo's corpus into this one's history. `data/derived/` is the
  opposite as of S006: it **is** committed, on purpose, as a paper trail
  (ADR-0042, supersedes ADR-0028). Regenerate and commit the diff; don't
  hand-edit what's on disk.
- ~~**Do not put an example row in the intake workbook.**~~ **Reversed by ADR-0084** — the seed apparatus is retired. The underlying trap is real and general: in a spreadsheet, copying a row is one keystroke, so never put a specimen row in a sheet somebody fills in.
- **Superseded, kept for the trap:** Not even a marked one.
  In a spreadsheet, copying a row is one keystroke. The seed examples live in a
  *different file* — `stage0-seed-review.xlsx` — for exactly this reason
  (ADR-0044). `stage0-intake.xlsx` stays empty.
- ~~**Do not move a seed record into `eval/gold/` by hand**~~ **Half reversed.** The seed directory is retired (ADR-0084). The second half stands and is now absolute: **never fill an `approved_by` to make something pass**, in any store.
- **Original:**, and do not fill an
  `approved_by` in `review/seed/` to make something pass. Both are defects that
  `tmk-seed` catches, and the second is the specific failure ADR-0043's guards
  exist to prevent.
- **Do not hand-write a `span` or a `source_content_hash` in a seed record.**
  They are computed from the snapshot at render time (ADR-0045). If a surface
  will not locate, the surface was retyped rather than copied — fix the surface.
- ~~**Do not maintain a seed file after its record type has been reviewed.**~~ **Moot — `review/seed/` is retired** (ADR-0084).
- **Original:**
  `tmk-reconcile` does this — per *record*, not per file, because a round is
  partial (ADR-0049). Do not delete a seed record by hand.
- **Do not remove a rejected seed record.** It has no approved twin, so it is
  not the duplication the rule is about, and things point at it
  (`must_not_infer: PU-0017`). The rejection is recorded in
  `review/decisions/`; the record stays where the pointers are.
- **Do not edit anything in `review/returned/`.** Not a typo, not a verdict, not
  a date. `corrrect` stays typed and the ledger reports it; deciding what a
  reviewer meant is the one thing an agent may never do here (ADR-0050).
- **Do not re-serialise a seed file.** Its comments carry the entity annotation
  rule and the candidate predicate list. `tmk-reconcile` removes lines and then
  parses the result back and compares it before writing, and that verification
  is the only reason line surgery is acceptable.
- **Amended.** The check may now look in `authored/` — an authored record naming another authored record is the ordinary case. It must still never let a record in `eval/gold/` rest on one that is not signed: that would put unreviewed content inside the yardstick (ADR-0080).
- **Original:**
  That would let approved knowledge rest on unapproved candidates — rule 4
  inverted. The gate holds the record instead (ADR-0048).
- **Do not read through a misspelt verdict or an ambiguous date.** Both are
  refused by name on purpose (ADR-0047, ADR-0048), and both cost a reviewer
  seconds to fix. When a person *does* rule on one, it goes in an addendum
  naming that record — not into a typo table, and not into the workbook
  (ADR-0051, ADR-0052).
- **Do not generate a file into `review/returned/`.** That directory holds what
  a person produced. An instruction file written up from their words is the one
  exception, and it says on its face who said it, when, and who relayed it.
- **Do not fill a judgement field to make a check pass.** Null is a reportable
  gap; a plausible value is a lie the harness will then certify.
- **Do not make `pytest` fail to satisfy "the suite must fail".** That is
  `tmk-harness`'s job, and collapsing them hides every future regression (Q-23).
- **Do not hand-maintain a blocker list.** `tmk-blockers` computes it, and the
  hand-written one in this file was wrong in two of three chains before anything
  was checking (ADR-0053). Quote the report; do not restate it.
- **Do not walk `CROSS_REFERENCES` recursively.** The real seed set contains
  reference cycles — `GA-0002` ↔ `PU-0013` (Q-30) — so a naive walk hangs on
  content rather than on a fixture and passes its tests first.
- **Do not treat a rejected record as waiting on what it names.** It is a sink in
  the dependency graph, not a source. Getting it backwards inverts every chain
  that touches a rejection and looks entirely plausible (Q-31).
- **Do not let `--only` narrow a check.** It narrows what is *rendered* and
  nothing else. A round scoped to ten records must not scope the defect report to
  ten records (ADR-0055).
- **Do not run bare `pytest` in a container.** The image's `uv`-installed pytest
  shadows the project environment and reports `ModuleNotFoundError` for packages
  that are installed. `python3 -m pytest -q` (Q-29).
- **Do not build a vector store or search index yet.** Stage 7 is five stages
  away and untestable without Stage 0.
- **Do not hand-edit `ontology/draft/relations.ttl`.** It is generated from
  `eval/gold/relationships.yaml` and a test compares the committed file against a
  regeneration. To add a predicate, have a reviewer approve a relationship that
  uses it, then `tmk-ontology-relations --write`.
- ~~**Do not write a `skos:definition`.** Anywhere.~~ **Reversed by ADR-0079** — writing definitions is now the job. Each one carries its evidence span and its `unreviewed` stamp, and a definition with no source in the corpus is flagged `general_knowledge` rather than dressed up as one that has a source.
- **Original:** The approved concept records
  carry definition *sources* and no definition text, so the graph carries sources
  and no text. The absence is the honest report and `tmk-ontology-report` counts
  it.
- ~~**Do not type a concept into `GroundOfRefusal`, `LegalTest`, `RelevantFactor` or `Exception`.**~~ **Reversed by ADR-0079 and now the top of the worklist.** The classes fill from `authored/concept-types.yaml` as well as from signed records. What has not changed: an agent may not write the result into `eval/gold/concept-types.yaml`, which stays empty until a person signs one.
- **Original:** Unchanged by ADR-0071, which built the *container* and typed
  nothing. The classes fill from signed `concept_type` records and from nothing
  else; which group a concept belongs in is a legal judgement (ADR-0056
  consequence 4), and a machine-filled taxonomy reads as authoritative and was
  authored by nobody. If you find `eval/gold/concept-types.yaml` populated by
  anything other than a transcribed workbook, that is a defect.
- **Do not assert a narrow `rdfs:domain` or `rdfs:range` from observed usage.**
  Under OWL 2 RL a domain assertion reclassifies every subject of the property.
  The observed types are annotations that infer nothing; the asserted domain and
  range are `tmk:LegalMatter`. Tightening one is an expert ruling.
- **Do not promote a module out of `ontology/draft/`** without a recorded human
  decision, and not the directory as a block — one module at a time (ADR-0057).
- **Do not loosen a SHACL shape to make a run pass.** A failing shape is a
  finding. If a constraint is wrong, that is an ADR.
- **Do not add a shape, a rule or an ontology module without adding it to its
  fixed list** — `tbox.MODULES`, `validate.SHAPE_FILES`. None of the three is a
  glob, because a file picked up silently is how an unreviewed constraint joins
  the gate and a deleted one stops being noticed.
- **Do not write a competency query without a `limits:` line.** It is refused
  rather than run (ADR-0061), and the reason is that a query returning rows
  always looks like an answer.
- **Do not mark a CONSTRUCT rule approved** because it works. Stage 9 requires an
  expert to approve every reasoning template; `approved-by: PENDING` is the
  current state of both and the runner quarantines their output accordingly.
- **Do not write a ref as a prefixed name in SPARQL or Turtle.** `tmkr:TMM/Part29/1#1`
  parses, warns once, and matches nothing — so the query returns no rows and
  reads as a fact about the data (Q-32). Full IRI, `#` as `%23`.
- **Do not resolve the `deceptively similar` collision** by adding the concept or
  by editing the question. ~~It is an expert's call (Q-37).~~ **Settled S012**
  (OQ-0002, ADR-0075): it belongs to s 44, the question is naming a boundary, and
  neither record changed. The prohibition held and still holds — the fix was a
  derivation over the not-labels already signed, not an edit to either side.
- **Do not assert `tmk-recon`'s counts against the graph's.** Recon is s 43-scoped
  and held-instrument-scoped; the graph is neither. Both are right and they do not
  match (Q-38).
- **Do not build a retrieval layer or a search index to close the six deferred
  competency questions.** They are deferred because Stages 7 and 8 do not exist,
  and a query that returned rows for them would measure the wrong thing while
  looking like coverage.
- **Do not quote a rule's triple count as a count of findings.** They differ by
  more than an order of magnitude, and doing it cost the owner two wrong numbers
  to answer against (Q-44). `Yield` carries `assertions` and `triples` under
  names that cannot be swapped; quote `assertions`, and carry the column heading
  with any number you lift out of a generated table.
- **Do not let a rule body set its own `reviewStatus`.** Approval lives in the
  `approved-by:` header and `construct()` stamps it; a body that sets it is
  refused. Two sources of truth for whether a rule is approved can drift to the
  point where an approval the owner gave changes nothing in the data (ADR-0068).
- **Do not hand-edit anything under `graph/`.** All four files are committed now
  (ADR-0070), which makes them look editable and they are not. `tmk-graph
  --write --rules`, then commit; `tmk-graph --rules --check` is in CI.
- **Do not write an rdflib serialisation to a committed file without checking it
  is stable across processes.** Turtle sorts, N-Quads does not (Q-45).
- **Do not add a module-scope import to `dashboard/` or `stage0/` without asking
  what it makes heavier.** `tmk-ruling` needed rdflib it never used, and the
  owner's first submission died on it (Q-42). The commands in one package do not
  share a dependency footprint.
- **Do not write `eval/pilot-scope.md` from ADR-0072.** The owner gave the
  boundary *rule*; the document also needs whether GI is the centre or a corner
  and whether point-in-time questions are in scope, and he answered neither.
  Answering part of a question is not answering it.
- **Do not add LegalRuleML.** ADR-0009.
- **Do not hand-edit anything under `site/data/`.** It is regenerated by
  `tmk-dashboard --write` on every deploy, so an edit there is a change that
  vanishes on the next push. Change `src/tm_knowledge/dashboard/build.py`.
- **Do not put a number on the dashboard that the committed artefacts do not
  support.** ADR-0063. If a figure needs the snapshot, render the generated
  report that computes it — the site restates nothing it can render.
- **Do not add a page's content to the JavaScript.** `blocks.js` renders eight
  kinds of block and knows nothing about trade marks; all content is composed in
  Python (ADR-0064). A ninth block kind is fine; a domain word in `blocks.js` is
  not.
- **Do not put a jargon word in `open-questions.yaml`.** Not SHACL, not TBox, not
  ADR-nnnn as a bare reference. The owner said it plainly: *"I'm far from being a
  system engineer."* A question they cannot act on is a question that was not
  asked.
- **Do not write an option that asserts legal content.** Asking whether
  "connotation" is a test or a factor is a question. An option reading *yes, it
  is a legal test — approve this* is rule 1 broken through a form control.
- **Do not generate a file into `review/rulings/` by hand** to record something
  said in a meeting. That directory holds transcriptions of dashboard
  submissions, produced by `tmk-ruling` from an issue. Words arriving another way
  go to `review/returned/` under ADR-0051's two-operation rule.
- **Do not act on a ruling and leave it open.** `applied:` in the ruling file, an
  ADR with authority `human`, and `status: answered` on the question. Three
  places, because "decided" and "acted on" are different states and the queue is
  the only thing the owner sees.

## 5. Session log

Newest first. One short entry per session: what changed, what it cost, what it
revealed. Keep entries to a few lines — detail belongs in ADRs and QUIRKS.

### S023 — 2026-09-12 — the relational layer came off section 43

**Branch** `claude/gracious-edison-vu5avc`

The owner asked whether `ontology/README.md` was still right that the ontology is
built from section 43. Reading the nine `.ttl` files against the stores: **partly,
and the part still true was the load-bearing one.** The class skeleton never was;
the concept layer stopped being in S018; `relations.ttl` — the closed predicate
list — still was, because it was generated from the 35 signed relationships and
all 37 of their source refs point at `TMM/Part29`.

**219 relationships, 45 sources (ADR-0109).** `tmk-relationships` is a
deterministic pass over the whole corpus and both instruments. Seven patterns,
each fixing where subject and object sit before it fires: `isDefinedIn` (46, from
the Act's and the Regulations' own definition provisions), `hasStatutoryBasis`
(85, from the Manual's own hyperlinks introduced by *under* / *pursuant to*),
`mayGiveRiseTo` (37), `isPerformedBy` (31), `mustOccurWithin` (11),
`requiresElement` (7), `isOvercomeBy` (2). `relations.ttl` now generates from both
registers with `tmk:AuthoredRelation` beside `tmk:ApprovedRelation`, counters
never summed.

**Two defects fell out of the first build (ADR-0111).** The concept scheme's label
was `"Section 43 examination vocabulary — pilot"` on all 130 concepts in the
committed graph; corrected, while the IRI `tmkc:scheme-s43` was deliberately kept
(IDENTIFIERS.md §3 — labels get revised, identifiers must not). And `_provenance`
resolved `source_ref` against `corpus.chunks` only, so the first 46 records ever
to cite legislation as their *source* all reported as "naming a source not held";
it now reads units and provisions too (Q-64).

**Cost:** 573 passing (was 528), 22 new tests, 0 defects in the harness, 0 in
SHACL. **Distrust the precision, not the provenance.** A sample of the first run
found inverted edges on the active *overcome*, roles read as subjects and a
flattened annex table read as one sentence; each is a guard with a test now, and
what survives is evidenced and correctable rather than correct. Q-65 records the
trap worth carrying: a withdrawn boundary survives in prose and in hardcoded
labels long after the code that enforced it is deleted, and grepping for `s43`
does not find a paraphrase.

### S022 — 2026-09-12 — the tree became a tree, the map became walkable, the nodes learned to quote

**Branch** `claude/gallant-maxwell-nua5rd`

Three objections from the owner, all about the drawing: the decision tree was not
shaped like one, the knowledge graph was not behaving or looking as expected, and
the content still seemed abstract. No record changed and nothing was authored.

**The tree is binary now (ADR-0106).** Bands went; questions came. Each anchoring
section asks whether a ground under it arises, *no* chains down the spine, *yes*
opens the section's `legal_test` concepts as questions in their own right — which
is licensed by the group's own definition, *a question the decision maker has to
answer*, and by nothing else. Factors hang off the **section**, not off a
question, because no record says which test a factor feeds and section 33 holds
factors and no test at all. Three tests pin the shape: two answers per question,
every path ending on the outcome leaf, and the process spine asking nothing.

**The map walks (ADR-0107).** It opens on one concept and its neighbours and
grows a hop at a time; nodes drag and stay dropped, and only newly drawn nodes
settle, so an arrangement made by hand survives the next expansion. The whole
254-node canvas is one button away, unchanged.

**Every node quotes its passage (ADR-0108).** All 130 concepts had one already,
in the `evidence` of the envelope that authored or typed them. A test fails if a
character of a quote does not appear verbatim, against the same ref, in the
store — it is a quotation, never a definition.

**Cost:** 432 passing, 3 new tests, 0 new failures. Q-63 records the trap that
cost the most: a block measures zero until the router appends it, and a layout
built on that overlaps silently.

### S021 — 2026-09-12 — two visualisations, and what the picture shows that the tables did not

**Branch** `claude/knowledge-graph-decision-tree-7h8ec6`

Asked for a node network over the knowledge graph and the examination process as
a decision tree, both clean, both explorable, both straightforward to update as
the vocabulary moves. The site now has two more pages, built the same way every
other page is built: generated from the records on every `tmk-dashboard --write`,
with nothing stored and nothing hand-maintained.

**The decision that had to be made first was whether the site may do this at
all.** Every other page *restates* a record; these two *arrange* records, and an
arrangement looks like a claim. ADR-0103 allows it on three conditions — the rule
is computed in `dashboard/views.py`, every node and edge carries the rule that put
it there, and the page says nobody has reviewed the arrangement. ADR-0104 records
the map's three choices (four edge kinds, all of them record fields; colour
carries signed-versus-authored and never the nine groups; a provision node is the
address the record cites, with rolling-up a toggle in the browser). ADR-0105
records the tree's spine and the two rules that were built, measured and thrown
out first.

**Three findings came out of the arrangement, and they are on the pages rather
than in a report.** *(a)* **The graph is in 44 separate pieces.** One holds 86 of
254 nodes and is the signed section 43 vocabulary; almost every other piece is a
single authored concept with the provisions it cites and nothing else, because
`authored/relationships.yaml` does not exist. Rendered, that is unmissable in a
way "0 authored relationships" in a table was not. *(b)* **Three sections have a
test and no ground concept** — s 14, s 41 and s 51 — and section 41 is the largest
branch of the three. Anchoring the tree on grounds alone would have hidden it, so
tests anchor a branch too. *(c)* **5 of 31 non-step process concepts join any
step at all**, which is the same hole as (a) seen from the procedural side.

**Nothing was authored as legal content and no record changed.** The 190 signed
and the 208 authored records are byte-identical to how S020 left them.

**Cost:** one new module (`dashboard/views.py`), two new site modules, two block
kinds, two pages, 28 new tests. 569 tests pass, dashboard current, 0 harness
defects.

**One thing to carry forward, and it is the reason ADR-0105 consequence 3 exists.**
The owner's stated purpose for the tree is a framework for training a
probabilistic model on historical decisions. The tree is shaped for it. `PU-0003`
— signed, approved — prohibits the system stating a confidence that a ground
applies, on the reasoning that no probability here is calibrated against
examination outcomes. A decision corpus changes that premise and not the record.
Only a person can change the record, and no agent may.

### S020 — 2026-09-09 — what the expert is for, written down, and two things found while writing it

**Branch** `claude/tm-expert-review-scope-zpgjv7`

Asked to clarify what the trade marks expert needs to look at. No file said, and
the two that looked like they said were wrong in opposite directions: the
dashboard's expert heading implies four items and holds one (`OQ-0017`, parked);
`blockers.md` implies ten decisions are owed and, since ADR-0084, none is. The
real answer — 208 records nobody has read — existed only as a question to the
owner. `docs/EXPERT-REVIEW-SCOPE.md`, ADR-0100: seven items, readiness stated per
item, and what is *not* theirs at the same length.

**Revealed, and both are in QUIRKS.** Q-59 — ten authored concepts reuse a signed
concept's `pref_label`, three of them silently (`GC-0053`, `GC-0100`, `GC-0101`);
no check compares labels across the stores, and the three are the expert's to
resolve (ADR-0101). Q-60 — `eval/STAGE-0-INPUT-GUIDE.md` §9 tells its reader to
delete exactly the 208 records they were brought in to correct. ADR-0079 reached
every file an agent opens and missed the one whose audience is not in the session.
Banner added; the rewrite is owed.

**Then the one-request pack.** Told to assume a single remaining request to the
expert, the seven-item list became a prioritisation problem. `tmk-expert-pack`
(ADR-0102) generates `data/derived/expert-request.xlsx` and
`docs/EXPERT-REQUEST.md` together from one set of counts. Ordered by value, not
size; two sheets round-trip through `tmk-transcribe` and five come back as
words; eleven empty record sheets deleted rather than shipped; `approved_by`
emptied in every row it writes. A test asserts the covering note contains none of
this project's vocabulary — no ADR numbers, no store paths, no field names —
because the reader is an examiner, not a contributor.

**Cost:** no record changed, no legal content authored. One new module and
command, 11 new tests, three ADRs, two quirks, one banner. 0 harness defects
(12 gaps, 10 notes, snapshot fetched), 541 tests pass, dashboard current.

**A note on running the tests cold:** from a bare clone 13 tests fail and 40
error before `tmk-fetch-upstream` has run, all of them on `SnapshotMismatch`.
That is ADR-0004 working, not breakage — but it looks exactly like breakage, and
`.[test]` (not `.[intake]` or `.[rdf]` alone) is the extra that installs enough
to reach the failure.

### S019 — 2026-09-09 — the taxonomy got five more groups, and the front page stopped lying

**Branch** `claude/stoic-brahmagupta-a6aq2g`

Asked what was waiting on him or on the expert. Answer: eleven questions on his
queue, none blocking agent work; **one** genuine expert question (OQ-0017,
parked) rather than the four the dashboard's expert theme implied; and the real
waiting is 208 authored records nobody has read, which appeared nowhere.

He instructed two things and both are done. **Nine groups instead of four**
(ADR-0098): `process_role` 8, `subject_matter` 14, `procedural_step` 21,
`instrument_or_record` 7, `external_instrument` 2, and `none_of_these` retained
holding exactly one — `GC-0051`, which is a rule about how a ground operates and
genuinely fits nothing. The 53 were retyped in one pass so they can be reviewed
together; only `type`, `confidence`, `reasoning`, `alternatives_considered`,
`expert_should_check` and `authored_date` moved, because the evidence on each was
already verified against the pinned snapshot and the passage showing what a
concept *is* is the passage showing what part it plays. Every one keeps
`none_of_these` in `alternatives_considered`, marked superseded rather than
refuted, so the change stays auditable. **And four site faults fixed**
(ADR-0099), the largest being an Overview lede that denied any AI-written content
on a page counting 208 machine-written records.

Two questions added: **OQ-0027** (how do the 208 reach a signature — the only
`high` on the queue, and the first inbox item about work rather than a decision)
and **OQ-0026** (the five groups and the 53 assignments, in one pass). OQ-0024
closes against the ruling.

**Cost:** 0 harness defects, 0 SHACL defects, 528 tests pass, dashboard current.
**Revealed:** `tmk:Role` in `examination.ttl` and the new `tmk:ProcessRole` will
carry the same four labels if anybody ever defines the former — Q-58. And the
`none_of_these` bucket surviving with exactly one member is the evidence that it
was an answer all along rather than a place to put things.

### S018 — 2026-09-09 — the boundary left the artefacts, and the taxonomy started creaking

**Branch** `claude/busy-goldberg-gewifv`

**The work.** The owner asked for the section 43 barrier's removal to reach the
concept-typing spreadsheet "and throughout the repo". Three passes and a
retirement. `tmk-concepts`, a deterministic candidate pass over all 54 Parts —
statutory defined terms, Manual definitions, Manual subject headings, usage
counts — **1,715 candidates**, every quote cut from the snapshot with its span
and hash, writing `review/candidates/concepts.yaml` and an evidence pack and
authoring nothing. **78 concepts** authored into `authored/concepts.yaml` from
the 53 Parts the boundary hid, with 78 typings beside them. `tmk-typing` reads
both stores, so the workbook holds **130 rows** and each says whether its concept
was signed or authored. Then: `tmk-boundary` and `boundary.md` deleted,
`tmk-recon` re-scoped to the corpus, the graph's source selection replaced,
`eval/pilot-scope.md` off the completeness gate, the worksheet re-headed, and the
seed scope draft marked withdrawn. ADR-0095, ADR-0096, ADR-0097.

**What it cost.** 0 harness defects, 0 SHACL defects. Source graph 16,405 → 32,922
triples over 216 → 508 chunks; `dataset.nq` 5.4MB → 10MB. Authored store 52 → 208
records, still 0 `general_knowledge` and 0 refused.

**What it revealed, and the second one is bigger than the vocabulary.**

- **53 of the 130 concepts fit none of the owner's four groups**, against 7 of the
  first 52. They are the roles, documents, proceedings, outcomes and remedies:
  the four groups describe *reasoning about* an application and about two fifths
  of the Manual describes *what happens to* one. OQ-0023 asked whether the
  lopsidedness meant the taxonomy was wrong; the wider set says the lopsidedness
  was an artefact and this is the real question. OQ-0024.
- **63% of the corpus cites no provision at all** — 1,551 of 2,460 chunks. Every
  rule this repository has ever used to select passages was keyed on citation
  edges, so two thirds of the Manual was structurally invisible to all of them.
  That is the mechanism behind Q-28, now Q-53.
- **Two counters and one promised check.** The concept-types line in the build
  report was wrong again, in the opposite direction to ADR-0093's fix (Q-54).
  `concept-type.schema.json` had promised a dangling-cross-reference check since
  ADR-0071 and nothing performed it — free while every typing named a signed
  concept, not free the moment one named an authored one. And the harness tests
  were reading the live `authored/` while overriding only `gold_dir`, so they
  asserted what the repository held that day (Q-51, again).

**Two things the graph change surfaced on its way out.** `CQ-0007` had been
quadratic since S010 — two independent patterns in one `GRAPH` block make rdflib
build a cross product — costing 103 seconds at 216 chunks, 409 at 508, and the
test module ran it twice. Split into two blocks it takes 0.3 seconds and returns
the same rows; the module went from over thirteen minutes to eleven seconds
(Q-56). And `CQ-0017` stopped being complete: it counted all 67 passages citing
section 43 *because the graph was fenced to exactly those chunks*, so it was
complete for one provision and silently incomplete for every other. It returns 56
of 67 now and says so (Q-57).

**What is provisional.** ADR-0097's graph rule is `agent-proposed`: 41 chunks
left the graph because nothing says anything about them, the alternative was a
40MB artefact, and OQ-0025 puts the trade-off to the owner with three measured
options. Several authored
records say in `expert_should_check` that their preferred label is an invention
because the Manual names no term for the idea — *other traders' legitimate desire
to use* and *protected wine expression* are the clearest, and both should be
renamed by somebody who knows the field rather than accepted.

### S017 — 2026-09-08 — the store got content, and the content found two bugs

**Branch** `claude/next-phase-gd2x7i`

**The work.** All 52 approved concepts typed into `authored/concept-types.yaml`,
`unreviewed`, 90 evidence entries, 0 defects (ADR-0092). `tmk-typing` taught to
read the authored store, so the reviewer's workbook arrives pre-filled and the
evidence pack carries each proposal's argument. `none_of_these` fixed to count as
a typing rather than a skipped record, and the build report's concept-types line
corrected (ADR-0093). `authored_by` settled as naming the model that wrote the
record (ADR-0094). Q-50 to Q-52. OQ-0023 put to the owner. 505 tests pass; SHACL
still 0 defects, 0 gaps, 29 notes.

**What went as expected.** S016's claim that the plumbing was finished held
exactly: the file was written and `tmk-harness`, `tmk-coverage`, `tmk-graph`, the
dashboard and every count picked it up with no code change. Running the harness
after the first three records — S016's advice — was worth taking; it is what
caught the envelope shape before 52 records carried it.

**What did not, and both are worth carrying.**

1. **A quote I had transcribed by hand would not locate.** The generator slices
   every quote out of the snapshot at the offset its needle lands at, so a
   mis-transcription fails at authoring time rather than in the harness. It
   caught one immediately: a sentence I had ended with a full stop the Manual
   does not have. **Build content generators this way.** The alternative is
   discovering it in a defect list, or not at all — the check exists precisely
   because a retyped passage is not evidence (ADR-0045).
2. **Two counters were wrong and could not have been caught before** (Q-50). A
   `none_of_these` record was skipped before its typing node and the counter,
   contradicting the comment three lines above it; the report line beside it
   divided typings of signed concepts by the number of concepts a machine wrote,
   which is structurally zero. Both had been unreachable since S010 because both
   stores held zero typings. The lesson generalises: **a branch that only runs on
   data the repository does not hold yet is untested by construction, and its
   comment is the only specification it has.**

**The judgement I would most like corrected.** 30 of 52 concepts came out
`relevant_factor` and exactly 1 `ground_of_refusal`. I believe that is what a
section 43 vocabulary honestly looks like when sorted by role — but the same
distribution is what you would see if I had read the four groups wrongly, and
nothing in the corpus settles it. It is OQ-0023 rather than a note, because a
fifth group would move roughly a third of the answers and correcting 52 rows
twice is how a review round stops happening.

**What I did not do.** I did not run the review round — that is a person's. I did
not build the retirement path from `authored/` to `eval/gold/`, which is now
overdue rather than hypothetical (Q-52). I did not touch `tmk-boundary`, the
worksheet re-scope or the 178 seed records.

### S016 — 2026-09-08 — the store got a reader, and it refuses

Built the plumbing S015 specified and did not build. `tm_knowledge.authored.store`
reads `authored/` the way `goldset.py` reads `eval/gold/`, with one difference
that is the whole point: a record whose envelope does not validate is **refused,
named and reported**, never skipped. `tmk-harness` gained seven `authored-*`
checks — four of them with no counterpart on the signed side, including the
inverted one where a filled `approved_by` is a defect rather than the gap it is
on a gold record. `tmk-coverage` grew an *Authored* column and a store section,
the dashboard reports the pair on every record card, and the graph grew a fourth
named graph built by the same mapping run twice. **ADR-0089, ADR-0090, ADR-0091.**

**Cost:** one module, ~250 lines of harness, a `Store` parameter threaded through
eight graph builders, three SHACL shapes, seven TBox properties and a class, two
fixture stores and 39 tests. `graph/approved.ttl` grew by 284 triples — the
origin and review-status stamps — and that is the only change to signed content.

**Revealed:** two things worth the QUIRKS entries. An authored record cannot be
validated while it is still wearing its envelope, because every record schema is
`additionalProperties: false`, and the error you get says "unknown field" — a
true statement about the wrong problem (Q-48). And the `tmk:origin` stamp looks
redundant with the named graph until you notice that pySHACL validates a single
graph, so `validate._flatten` unions the three before running, and at that moment
the stamp is the only thing telling signed from authored apart (Q-49).

**Not done, deliberately:** no legal content was authored. The store had to be
able to refuse a bad record before anything at volume went into it — a thousand
records written against a store nothing validates is a thousand records to
re-check. `authored/definitions.yaml` was left without a schema for the same
reason at smaller scale: deciding what fields a definition carries is a
record-type design pass, not something to settle by accident inside a plumbing
change.

### S015 — 2026-09-08 — the rules changed, and only the rules

The owner removed the section 43 boundary and amended CLAUDE.md rule 1 so an
agent may author legal content stamped as never validated. Both decisions were
made in chat, which he confirmed is a legitimate route as long as it is recorded:
words verbatim in `review/returned/260908-owner-chat-scope-and-authoring.md`,
index in `review/rulings/2026-09-08-chat-authoring-mandate.yaml`, reasoning in
**ADR-0079 to ADR-0085**. Four clarifications settled where authored content
lives (`authored/`, with `eval/gold/` frozen at the 190 signed records as the
measurement yardstick), whether it may be served (yes, labelled — Tier 3 stops
being a gate), whether extraction opens (yes, Stages 2–4 over all 54 Parts), and
what happens to the 178 held seed records (resolved by authoring).

**Cost:** the paperwork only. `CLAUDE.md`, seven ADRs, `authored/` with its README
and envelope schema, four directory READMEs re-headed, `ARCHITECTURE.md` and
`ROADMAP-STATUS.md` brought into line, six owner questions withdrawn or re-graded.
The ruling loader learned to read a chat ruling — it refused one, correctly,
because a hand-written file was not a shape it knew.

**Revealed:** the repo's own guard caught the first mistake of the new era.
Marking three questions `answered` when they had actually been *withdrawn* failed
`test_an_answered_question_can_show_what_the_answer_was` (ADR-0077's test), which
exists because a question that says "answered" with no answer under it reads as an
open question that lost its control. Withdrawn is not answered, and the record now
says which it was.

**Then three corrections in the same session, all the owner's.** He read ADR-0085
back and withdrew the premise behind it — three review states, not four, and no
credit for having been looked at (ADR-0086). He answered HANDOFF Q3, open since
S001 and blocking for about four hours: Gemini 3.8 Flash, key added as a
repository secret (ADR-0087), then the data-handling half too — corpus text
cleared to send, with a standing rule that a call must be worth making (ADR-0088).
And he confirmed the examination-outcome limit S015 had preserved unasked, which
is the one place this session guessed at his intent and guessed right.

**Not done, deliberately:** no legal content was authored, no record moved, the
graph is untouched. A session that changes the rules and then immediately acts on
them at volume leaves nobody able to tell which of the two broke anything.

### S014 — 2026-09-08 — the sorting sheet says what a concept is also called

The owner asked for one thing: the `notes` column of `concept-typing.xlsx` states
the concept and what it is explicitly *not*, and he wanted *also called* in there
too. He was pointing at a real asymmetry — the near-misses are there to stop a
sorter typing by label, which assumes they recognise the label, and `pref_label`
is one of several forms of words the Manual uses. The alternatives were already
approved and already in the evidence pack; the spreadsheet, where the sorting
actually happens, was the one place showing less than it had.

`typing.summarise()` now builds `pref_label — also called: … — not: …`, dropping a
clause whose list is empty, and the column is widened and wrapped because the cell
roughly tripled in length — a clipped cell loses the `not:` half, which is the
half that does the work. Six tests, one of which fails if any label stops being
verbatim (ADR-0078). 460 pass. **Nothing was typed**: `eval/gold/`, the ontology,
the graph and the queue are byte-identical, and OQ-0020 is still the open ask.

### S013 — 2026-09-08 — the count was right, the list under it was not

The owner asked why the dashboard said ten decisions were waiting on him when the
first one he opened said *"You answered this"*, and whether the published site
was simply stale. **Checking that first was the whole value of the session.** It
was not stale: `pages` had run on the merge commit and the live
`data/inbox.json` matched the repo byte for byte. The count was right as well.
What was wrong was the list — it filtered on nothing, so answered questions sat
above open ones wearing the same chips, and a `parked` boolean meaning *"not open
and yours"* printed **needs a trade marks expert** on questions he had answered
himself.

Fixed by giving a question one state, derived once and read everywhere: state on
the collapsed row, settled ones behind a fold, and a tally per theme so no blurb
counts its own questions (ADR-0076). Three questions answered by hand carried
their only evidence in a YAML comment; `answered:` now names the record, and a
test refuses `status: answered` that nothing can back (ADR-0077).

**Two things this cost nothing to learn.** GitHub Pages has been on since S011,
and `pages.yml` has always had `workflow_dispatch` — §2 item 6 said otherwise for
two sessions. And a `#` in an unquoted YAML scalar silently ate half a sentence
on the way in (Q-47). 454 tests pass; nothing in the ontology, graph, gold set or
queue contents moved.

### S012 — 2026-09-08 — the loop closed, and the numbers in it were wrong

The owner's first submission came back — issue #12, seven answers through the
form and three typed in by hand — and none of it had been recorded, because the
transcription workflow crashed on a dependency `tmk-ruling` never uses and then
told him his answer block was probably malformed. An answer with a note and no
option chosen was being dropped in silence too, and that was OQ-0009, the most
substantive thing in the submission. Repaired and tested first (ADR-0067),
because nothing else could be recorded until it was.

Then every answer acted on: RULE-0002 approved and released, the whole graph
committed, a ninth record type holding a concept's type with the 52 laid out for
sorting, the `deceptively similar` collision settled as a boundary rather than a
gap, and the owner's one-hop scope rule implemented and computed.

**What it revealed is worth more than what it built.** Two figures the owner was
asked to decide on were triple counts dressed as counts of findings — 71 flags
that are 5 passages, 2,244 links that are 187. And running his boundary rule
showed it does not do what he expected for section 41, because the Manual cites
the section bare in 32 passages. Both went back to him as questions rather than
being quietly absorbed. 452 tests pass; 9 ADRs; 4 quirks.

### S011 — 2026-09-04 — the questions got a front door

The owner asked for a dashboard: explain the shape of the work to people who are
trade marks experts and not engineers, and let them answer what is waiting on
them without reading the repo. Both jobs, on GitHub Pages, at
`thomas-amann-ipaustralia.github.io/TM-Knowledge/`.

**Nothing about the ontology moved.** No record was added, no concept typed, no
rule approved; `tmk-harness` and `tmk-shacl` are exactly where S010 left them.
432 tests pass, 23 of them new.

Built: a nine-page static site (`site/`, no framework, no package manager, no
CDN — a test asserts the last one), a generator (`tmk-dashboard`), a validated
plain-language question queue (`review/questions/open-questions.yaml` — 13 asked,
4 parked), and a round trip that brings an answer back (form → prefilled GitHub
issue → `.github/workflows/ruling.yml` → `review/rulings/`).

**Three decisions are the substance of it.** The site reads **committed artefacts
only** and never the snapshot (ADR-0063), so a deploy cannot fail on a network
and the page cannot show a figure it did not measure — the cost is that the best
number in the corpus lives in a rendered report rather than on a card. A page is
**a list of blocks** and the JavaScript holds no domain vocabulary (ADR-0064), so
changing what the dashboard says is a change to one Python function. And an
answer comes back as **an issue that is transcribed** (ADR-0066), with the issue
as the artefact and the file as the transcription — the same split ADR-0050 draws
for `review/returned/`, which is why a generated file is allowed in
`review/rulings/` and forbidden in `returned/`.

**The part that took the longest was the language, not the code.** Turning *"does
the owner confirm ADR-0055's third guard?"* into a sentence someone can act on
means saying what would change if they answered — and several of the honest
answers are "nothing is blocked", which is why the queue carries an urgency and
not a uniform alarm. Two questions became tick-lists where every unticked box is
a confirmation, because twelve provisional ADRs are twelve confirmations and one
page of prose.

Three quirks, and two of them are the same shape as Q-38: a number that is right
twice. "How many classes hold nothing" is 30 or 39 depending on which graph it
was counted over (Q-40), and the site labels its scope rather than picking one.

**Result: the dashboard is done and published on the next push to `main`; one
repository setting is needed to make the URL live; the thirteen questions are the
next thing to happen and none of them is an agent's.**

### S010 — 2026-09-03 — the owner stopped waiting, and there was enough to build with

The instruction was to stop going back to the expert and demonstrate that a full
ontology is feasible. Reading the repo cold, the answer looked like *no*: the
parallel track says the container is finished and empty, ADR-0010 forbids Stage
2, Stage 0 is 12 gaps short.

That reading was out of date by two sessions. **Stage 0 has 190 approved
records** — concepts with not-labels and a hierarchy, relationships with verbatim
sentences and tiers and modalities, prohibited uses with reasons, reasoning
expectations — all signed, all resolving, 0 defects. Enough to build an ontology
from, and building one is not the thing ADR-0010 forbids: **that prohibition is
on extraction, not on modelling.** Stage 2 generates new candidate knowledge and
would anchor a measurement by arriving first; transforming records a person
already signed generates no candidate and measures nothing new. ADR-0056 is the
owner's decision and states that distinction, because a future session will read
`ontology/` existing and reach for YAKE.

Built: 9 OWL 2 RL modules in `ontology/draft/` (not `ontology/` — nothing is
approved, ADR-0057), a graph of 16,405 source and 2,942 approved triples, 5 SHACL
files, 13 competency queries, 2 CONSTRUCT rules, and 97 tests. `tmk-shacl` reports
**0 defects, 0 gaps, 29 notes**; `tmk-harness` is unchanged at 0 and 12, because
nothing in Stage 0 moved.

**Three results the work produced that reading the records would not have.**
CQ-0017 reproduces `tmk-recon`'s Part distribution exactly and then adds the
column recon lacks: five Manual Parts are in the s 43 impact set *entirely* on
citations upstream inferred from a bare "section 43" — that is what preserving
`extraction` and `certainty` as a node instead of an edge bought. CQ-0023 returns
a blank first row: the passage stating that a connotation must arise from the
mark itself cites no decision at all, which an inner join would have hidden.
And **PU-0004 stopped being a paragraph** — the reviewer marked it
`detectable_by: shacl` and it now blocks a publish, with a fixture carrying a
conforming twin, because a constraint that fires on both passes its test and is
useless.

**The finding that matters most is a gap nobody had stated.** `GroundOfRefusal`,
`LegalTest`, `RelevantFactor` and `Exception` are declared and empty: all 52
concepts are bare `tmk:LegalConcept` because the record has no type field, and 39
of them sit outside any hierarchy. That is the single largest thing wrong with
the draft, it is one pass over a list for someone who knows the domain, and it is
now the top of §2.

The build also caught a live inconsistency in the approved set: **`CQ-0007` names
`deceptively similar` as an expected concept and `GC-0002` records it as a
not-label** (Q-37). Both approved, neither obviously wrong, and not an agent's to
resolve.

Seven quirks, five of them SHACL and SPARQL traps that fail *silently* — a ref
written as a prefixed name matches nothing and reads as a fact about the data
(Q-32); `sh:severity` inside a SPARQL constraint is ignored and turned an
informational check into 29 build-breaking defects (Q-33); a fixture without the
TBox **passes**, for a reason unrelated to the constraint (Q-35). Each of those
is the "reads as coverage" failure arriving by a different door.

**Result: Stages 5, 6 and 9 move to partial; Stage 0 unchanged; 409 tests pass;
the next four decisions are the owner's and none of them needs the expert.**

### S009 — 2026-09-02 — the queue was a graph and nobody could see it

S008 left the critical path stated as six records in a paragraph of this file.
Generating the same analysis found the paragraph wrong in two of its three
chains — `GX-0006` missing under `GA-0002`, `GA-0021` and `GX-0014` missing
under `CQ-0014` — and nothing had detected that, because nothing was checking. A
hand-derived dependency analysis over an interlinked set is wrong on arrival and
stale by the next round, which is the whole argument for ADR-0053.

`tmk-blockers` reads three committed artefacts — the ledgers, `review/seed/`,
`eval/gold/` — and needs no workbook, because `tmk-reconcile` had been writing
every child-row mark into the ledger since S008 and nothing had ever read them
back. That is where the session's most useful finding came from: **`GS-0001`,
`GS-0002` and `GS-0004` are signed search questions held by nothing but a
relevance grade the reviewer marked `amend`.** Three child rows, on the record
type at 1 of a target 20–50. No reading of the workbook had surfaced them.

The judgement in it is ADR-0054 — what counts as a decision. Ten, out of 178.
The two exclusions carry as much weight as the rule: twelve records are correct,
signed and held only by a pointer at something already on the worklist, so
asking a reviewer to look at them is asking them to answer an answered question;
and a rejected record is a **sink** in the graph, not a source (Q-31) — the first
version of the table reported `GA-0016` as *holding* `PU-0016`, which is exactly
backwards and looked entirely plausible.

Rule 1 was the thing to be careful about, and the line held: the report says a
record names one that was rejected and that the gate allows two responses —
repoint or withdraw — and that choosing is an expert's call. It quotes the
reviewer's own words and paraphrases none of them.

Then `tmk-seed --only` (ADR-0055), so the ten can be handed over as ten rather
than as 178. The checks still run over the whole set; only the rendering
narrows; and both artefacts say on their face that they are scoped, because a
scoped workbook that looks complete is how a partial review gets filed as a
finished one.

**Result: 10 decisions on the board instead of a 178-row workbook, a scoped
round rendered and ready to send, 312 tests passing, harness unchanged at 0
defects / 12 gaps.** Nothing moved in `eval/gold/` and nothing was meant to —
every record on that worklist needs a person.

Two container lessons in QUIRKS. **Q-29**: the image's `uv`-installed `pytest`
shadows the project environment, so nine collection errors named packages that
were plainly installed; `python3 -m pytest`. **Q-30**: the seed set contains real
reference cycles, so every walk over `CROSS_REFERENCES` must be cycle-safe or it
hangs on content rather than on a fixture.

### S008 — 2026-09-02 — the first workbook back, and a loop that would have run backwards

The marked-up seed workbook arrived and the loop was one command from doing the
opposite of its job. Two faults, and they compounded into the same failure.
`approved_date` came back as `25/08/2026` and as Excel date cells; both fail the
schema's ISO pattern, and **only a signed row carries a date**, so every row the
expert had approved was rejected and the 233 that would have been written into
`eval/gold/` were exactly the ones nobody had approved. Underneath that, the
transcriber read `verdict` as an annotation and dropped it — so a record the
expert had just *rejected* would have been written into approved space alongside
one they had signed.

That second one is the interesting failure, because nothing was wrong. ADR-0044
correctly called the review columns "annotations about a record, never fields of
one", the transcriber correctly ignored them, and `HOW-TO-CORRECT.md` had
already promised the opposite — "the records that carry your name become the
gold set". Nobody had implemented the sentence. A guard described in three
documents and present in none.

Fixed both. Dates are a schema-derived column kind that converts what has one
reading and refuses what does not, by name (ADR-0047). The verdict is now the
gate, and the gate is **transitive**: approval does not distribute over an
interlinked set, so a signed prohibition naming an unsigned question is held
too, to a fixed point (ADR-0048). That cost 18 records this round and is the
honest number — `eval/gold/` with a pointer to nothing is not a measurement
standard, and the alternative, letting the harness resolve pointers into
`review/seed/`, is rule 4 inverted.

Added `tmk-reconcile`, the missing half of the door (ADR-0049). It records the
round in `review/decisions/` — every verdict and every correction verbatim,
because a rejection with a reason is what Stage 10 reads and a deleted row is
nothing — then retires the seed copies of what reached `eval/gold/`. Per record,
not per file: a partial round makes ADR-0043 consequence 6 unfollowable as
written. Rejected records stay, because they have no approved twin and other
records point at them. The prune removes lines rather than re-serialising, since
the seed files' comments carry the entity annotation rule and the predicate
list, and every rewrite is parsed back and compared field by field before it is
written.

**Result: 108 approved records, and `tmk-harness` at 0 defects / 16 gaps.** The
red harness is still red and now for a much better reason — it is red about real
content rather than about an empty directory.

Then the owner put the two open questions back to the reviewer and returned with
both answers: the 83 rows marked `correct` and left unsigned are signed **TC**,
and the cell reading `corrrect` means `correct` (ADR-0052). A returned workbook
is never edited, so the instruction was filed as its own artefact and applied by
`--addendum`, under two operations narrow enough to state on one line: sign a
**blank** `approved_by` on a `correct` row, settle a verdict on a **named**
record (ADR-0051). 84 rows touched, every one printed and marked *by
instruction* in the ledger.

**That took the gold set from 108 to 190**, and it released 8 further records
that had been held only because they pointed at unsigned ones.
`eval/gold/entities.yaml` and `reasoning-expected.yaml` exist for the first
time. `tmk-harness`: **0 defects, 12 gaps**. `review/seed/` is down to 178.
287 tests pass.

The most useful output is not the 190. It is that the blocker went from
eighty-three rows to **six records**: `CQ-0013`, `CQ-0014`, `CQ-0016`,
`GA-0002`, `PU-0016` and `PU-0017` hold 20 records between them, and three of
those are held because they point at something the reviewer *rejected* — which
is a kind of blocker the gate could not have produced before it was transitive.

Two corpus-independent lessons, both in QUIRKS. **Q-26**: a validation rule on a
field that only appears on approved records fails closed for the approved and
open for the rest — check that before trusting any gate. **Q-27**: partial
approval of an interlinked set yields less than its verdict count, concentrated
in the record types that point outward, so ask for review in closed clusters
rather than in sheet order.

The expert's covering note is filed verbatim at
`review/returned/260826-expert-feedback.md` and raises two things an agent may
not touch: the office's real bar for the presumption of registrability, which no
record type currently holds (Q16), and a vocabulary drawn from Part 29 alone
(Q17, Q-28) — the structural half of which is that ADR-0022 selects passages
that *cite* s 43, and a definition is rarely in a passage that cites anything.
A third fell out of two rejections: the expert holds that resolving a bare
"section 15(1)" to the Act is acceptable in a TM-focused tool, which sits close
enough to Q-07's never-auto-resolve rule to need a ruling (Q19).

Returned artefacts moved to `review/returned/` and are never edited (ADR-0050).
The one thing an agent may write into that directory is an instruction file, and
it says on its face who decided, when, and who relayed it.

No legal content authored. No Stage 2 extraction run.

### S007 — 2026-08-21 — a 368-record seed set, for the experts to correct rather than compose

Owner reported the real blocker, and it was not availability: the Trade Mark
experts could not readily **articulate** the judgements the Stage 0 record types
ask for, because those judgements are the tacit part of their practice. A blank
form is the wrong instrument for that. Recognising a wrong answer is a different
and much cheaper act, so the owner asked for an extensive example set to be
corrected, and accepted that it cuts against CLAUDE.md rule 1.

Built `review/seed/`: **368 machine-written candidate records** over s 43 — 24
competency questions, 18 prohibited uses (all six kinds), 52 concepts, 153
entities exhaustively annotated over a bounded 14-chunk set, 58 relationships,
26 search questions, 22 retrieval questions, 15 reasoning expectations — plus
draft `pilot-scope` and `measures` documents. Every record is grounded in the
pinned snapshot: every ref resolves, every span lands on its recorded text, every
cross-reference points at something. `tmk-seed` exits 0.

The decision is ADR-0043 and the *guards* are the substance of it, because the
risk is not that the content is wrong — it is meant to be wrong in places — but
that it stops looking like a candidate. Six: quarantine under `review/`;
`.seed.yaml` names the gold loader will not read; an envelope carrying
provenance and a verdict around every record; `approved_by` null **and checked**,
with a test over the shipped directory; one door out (`tmk-transcribe`); and an
untouched harness, which still exits 3 and still names all 22 absent
deliverables. A seed record moves no counter.

Two smaller decisions fell out. The seed workbook had to be a **separate file**
from the intake workbook, because HANDOFF §4's no-example-row rule protects a
blank form and does not argue against a differently-named file whose whole
purpose is correction (ADR-0044) — `tmk-transcribe` now tolerates three review
columns rather than a second reader existing. And seed **spans are computed,
never written**: the tool locates the surface in the chunk and fills the offsets
and the hash, and refuses to guess which mention is meant when a surface repeats
(ADR-0045). That means an expert who corrects a surface gets a correct span for
free.

The round trip is proven end to end: the corrected workbook reads back through
`tmk-transcribe` with 368 records, 0 rejected rows and 767 blank judgement
fields reported rather than filled. 247 tests pass.

Two corpus findings, both inside the pilot scope and both now in QUIRKS. **Q-24**:
`TMM/Part29/3/3/1~2` cites section 114 of the *Trade Marks Act 1905* and only two
instruments are held, so that ref resolves to nothing by construction — 35 such
edges exist in the provisional scope, and it makes the `stale_source` prohibition
a live risk rather than a hypothetical one. **Q-25**: a term of art arrives broken
across a line as `International Non- Proprietary Name`, which is the sharpest
instance of why a surface is copied and never retyped.

The most useful output is not the record count. It is that **the two decisions
that shape everything downstream are now stated at the tops of two files rather
than implied by hundreds of records**: the entity annotation rule (which
deliberately annotates one chunk under a stricter rule so the densities can be
compared) and the candidate predicate list (fourteen predicates, invented in
defiance of the guide's own advice, and labelled as such).

Owner then found the flaw in the hand-over and it was a real one: the workbook
gave a reviewer two character offsets and no sentence, so the entity and
relationship sheets were not judgeable without the pack open beside them. Fixed
in the same session — `REVIEW_COLUMNS` grew from three to five, and every row now
prints its passage (span in bold, via rich text) and its `why_this_example`
alongside the verdict and correction cells (ADR-0046). The round trip is
unaffected; 252 tests pass.

**What to hand an expert is exactly two files** — the pack and the workbook.
Everything else under `review/seed/` is supplementary: `README.md` is for agents,
`HOW-TO-CORRECT.md` is the covering note, and `pilot-scope.seed.md` and
`measures.seed.md` are separate one-hour tasks that beat record review on value.
The two highest-leverage questions — the entity annotation rule and the
predicate list — are still stated only in the YAML file headers, which is the one
place an expert should not be sent. **Lifting them into the pack's front matter
is the obvious next improvement** and was not done this session.

Legal content authored — deliberately, as unapproved candidates, for the first
time in this repo. No Stage 2 extraction run. `eval/gold/` untouched.

### S006 — 2026-08-19 — closed Q13, Q9, Q4's format-half and 6 more ADRs; reversed ADR-0028

Owner asked what could be unblocked before the experts report back. Closed
**Q13**: `manual-XtrACTor` is public (already established in QUIRKS Q-13,
S004) and GitHub Actions clones public repos anonymously, so no CI secret is
needed — the open question was stale, not open, nothing needed asking.

Put the genuinely organisational questions (Q4, Q7, Q9, Q11/Q12) to the owner
directly rather than guessing at them, and recorded the answers:

- **Q9** closed outright — owner confirmed **ADR-0016** and **ADR-0018**
  (ADR-0038). Both were already load-bearing; this only lifts the provisional
  flag.
- **Q4** half-closed — the approval artefact **is** the workbook's
  `approved_by`/`approved_date` columns, no separate file or register
  (ADR-0039). *Who* the approving experts are is still open and expected to
  arrive with the experts' own content.
- **Q7** (base IRI) — owner not ready to decide; left open, no action taken.
- **Q11/Q12** — owner asked for a plain summary rather than a yes/no;
  provided one in chat, then the owner ruled on eight of them directly:
  **confirmed** ADR-0006, ADR-0012, ADR-0014, ADR-0024, ADR-0026, ADR-0027
  (ADR-0040, with two live triggers worth remembering — ADR-0026 invites a
  better upstream-pinning proposal if one exists, ADR-0027 may tighten if a
  CI/CD gating policy is ever added); **deferred** ADR-0011's provenance field
  list until Stage 2's actual output shape is known (ADR-0041); **reversed**
  ADR-0028 outright — the owner wants `data/derived/` **committed** as a paper
  trail, not git-ignored (ADR-0042). ADR-0029 stays open; the owner had no
  context for it and none is needed — it already reflects current practice.

Acted on ADR-0042 immediately rather than leaving it as a paper decision:
updated `.gitignore`, `data/README.md`, `cli.py`'s docstring and this file's
§4, then ran the full pipeline for the first time this session
(`pip install -e ".[test,intake]"`, `tmk-fetch-upstream` — snapshot at
`c490a9927f1a` — `tmk-recon`, `tmk-worksheet`, `tmk-coverage`, `tmk-workbook`)
and committed the output: the s 43 worksheet, the recon report, the coverage
report (0 defects, 22 gaps) and the empty intake workbook are now in git.
219 tests pass; the harness is sound and exits 3, exactly as designed.

The owner also asked (via ADR-0014) for more plain-language guidance on
**constructing the ontology**, beyond the existing input guide. Not drafted
this session — logged under §3 as a new open item needing its own scoping
pass, not squeezed in alongside eight other decisions. And noted: a work
order referencing `STAGE-0-INPUT-GUIDE.md` has already gone to the Trade Mark
experts, so that guide is now live reference material, not a draft.

No legal content authored.

### S005 — 2026-08-19 — the last five packages; the track is exhausted

Built P5, P7, P8, P10 and P11. The repo went from a corpus it could read to a
Stage 0 apparatus that is complete: a harness that checks everything §7 says is
mechanically checkable, a workbook the expert fills in with dropdowns instead of
YAML, a transcriber that reads it back without inventing anything, a coverage
report that turns an hour of expert time into a moved counter, and CI that stays
green while reporting Stage 0 as incomplete. 219 tests pass.

Three things were decisions rather than implementations, and each has an ADR.
The harness needed a **third severity** — `not_labels` is required "wherever a
near-miss exists", which no machine can judge, so gating on it would have made
Stage 0 uncompletable and dropping it would have lost the guide's best field
(ADR-0030). A run that never opened the snapshot **must not report Stage 0
complete**, because unverified is not sound and one report cannot mean both
(ADR-0031). And an array of objects in a spreadsheet had to become its own sheet
rather than parallel lists in one cell, because parallel lists pair the third
grade with the third ref by convention and nothing notices when that stops being
true (ADR-0036).

The most useful output is not the harness. It is that **the expert's path is now
two commands wide in each direction**: worksheet and workbook out,
`tmk-transcribe` back in, `tmk-coverage` to see what moved. Nothing between the
expert and the gold set requires anyone to type a ref, a hash or a line of YAML.

Recorded ADR-0030 to ADR-0037 and QUIRKS Q-22, Q-23. One dependency raised for
the owner rather than assumed: `openpyxl`, added as an optional extra (ADR-0035,
Q12). No legal content authored. No Stage 2 extraction run.

### S004 — 2026-08-18 — phase one of the parallel track: seven packages, and a worksheet

Built P1, P2, P3, P4, P6, P9 and P12. The repo went from documentation and an
empty skeleton to a package that fetches a pinned corpus, loads it without losing
a field, validates eight record types, and prints an annotation worksheet. 165
tests, of which the corpus-wide ones skip cleanly without a snapshot.

The most useful output is not the code. It is that **the expert critical path is
now one command shorter**: `tmk-worksheet` prints 216 chunks with every ref and
hash already on the page, and `tmk-recon` costs each candidate boundary rule, so
Q8 can be answered against numbers instead of impressions.

Three documented facts turned out not to hold against the corpus (Q-17, Q-18,
Q-20), and one small thing about the pilot is worth knowing before gold records
are written: s 43 has no numbered subsections, so a citation to "s 43(1)"
resolves to nothing at all (Q-21). None of these was visible from prose.

Two mechanisms earned their place immediately. The pin's corpus-count check
rejected a wrong number in the first pin written; the template/schema drift check
found that five gold record templates had no `approved_by`/`approved_date`,
though the definition of done requires them on every record.

Recorded ADR-0023 to ADR-0029, and QUIRKS Q-17 to Q-21. No legal content
authored. No Stage 2 extraction run.

### S003 — 2026-08-17/18 — the parallel track; Stage 2 stack; four decisions closed

Owner reported the experts are slow and asked what could proceed meanwhile.
Wrote `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` (ADR-0016): twelve agent-side
packages P1–P12, five gates, an explicit not-to-do list, and a statement of
where the track runs out. Added `docs/roadmap/README.md` because that directory
now mixes a source document with an editable one.

Two things fell out of writing it that are more useful than the package list.
The Pass B worksheet does **not** have to wait on the pilot boundary — an
over-inclusive provisional scope rule the owner can set alone releases it, and
the error costs are asymmetric enough to make that clearly right (ADR-0017).
And the red harness is not free: with no gold records every mechanical check
passes vacuously, so the redness has to come from an explicit completeness gate,
which also has to be distinguishable in CI from a genuine failure (ADR-0018).

Owner then fixed the Stage 2 candidate-generation stack: TextRank + YAKE +
KeyBERT in parallel, spaCy NER as metadata on candidates (ADR-0019, human).
Recording it surfaced two consequences worth having before code exists. The
candidate-id formula in `IDENTIFIERS.md` §3 hashes `method`, so three extractors
mint three ids for one span and the cross-method agreement the ensemble exists
to produce is invisible — ADR-0020 proposes dropping `method`, and P3 must wait
on Q10. And spaCy's OntoNotes labels collide by name with two gold entity types
while meaning something else (Q-16), which is how NER output would quietly
become the taxonomy.

Owner then answered four open questions when asked (ADR-0021, authority human):
Q2 pinned release download, Q5 upstream refs canonical, Q10 drop `method` from
the candidate id, and ADR-0017 confirmed with its rule set in ADR-0022 — every
chunk citing `TMA1995/s43` or a unit beneath it, plus page-mates, at every
`certainty` value. `IDENTIFIERS.md` §3 went from proposal to operative formula.

That leaves the board in a shape worth noticing: **no agent work is blocked on a
human decision**, P1 is the critical path, and all four remaining gates are
expert content. From here the only lever on the schedule is making that content
cheaper to produce — P6, P7, P9, P10.

No legal content authored. No code, no data. Nothing executed.

### S002 — 2026-08-06 — pilot area fixed; Stage 0 input guide

Owner selected **s 43** as the pilot area on expert advice (ADR-0013), closing
Q1. Wrote `eval/STAGE-0-INPUT-GUIDE.md`: the expert-facing walkthrough of all
Stage 0 deliverables, with shape-only worked examples, elicitation prompts, a
definition of done and the order of work (ADR-0014).

Found a gap while writing it — the roadmap names seven gold-standard components
and the templates covered six. Added
`eval/templates/reasoning-expectation.template.yaml` (ADR-0015).

Two points in the guide are load-bearing and not obvious: recall is unmeasurable
unless a bounded chunk set is annotated **exhaustively** rather than
cherry-picked (§4), and Stage 0 splits into a pass that needs no data and a pass
that cannot start until the snapshot is pinned (§3). The second makes Q2 the
next agent-side blocker.

No legal content authored. No code, no data. Nothing executed.

### S001 — 2026-08-04 — repo structure and agent documentation

First working session. Repo contained only the roadmap, the upstream index and a
licence. Built the documentation set (`CLAUDE.md`, this file, `DECISIONS.md`,
`QUIRKS.md`, `ARCHITECTURE.md`, `IDENTIFIERS.md`, `ROADMAP-STATUS.md`,
`GLOSSARY.md`) and the directory skeleton with a README per directory. Relocated
the two source documents into `docs/` unaltered.

Recorded ADRs 0001–0012. Found and logged four discrepancies between the roadmap
and the upstream reality (QUIRKS Q1–Q4), the sharpest being that the roadmap's
illustrative identifier scheme cannot be reconciled with the identifiers upstream
actually emits.

No code, no data, no dependencies. Nothing has been executed because there is
nothing to execute.

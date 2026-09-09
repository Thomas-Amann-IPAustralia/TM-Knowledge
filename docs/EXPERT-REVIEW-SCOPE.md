# What the trade marks expert needs to look at

**Written:** 2026-09-09, session S020. **Authored by a machine, validated by
nobody** — like almost everything it describes. It states counts and names
records; it decides no point of trade marks law.

**Audience:** the trade marks expert who signs the workbook `TC`, and the repo
owner briefing them. **Purpose:** to say precisely what is waiting on a trade
marks expert, what is not, and in what order it is worth their time.

> **Read this before `eval/STAGE-0-INPUT-GUIDE.md`.** That document is the
> repo's only other expert-facing file and it describes an operating model the
> owner abandoned on 2026-09-08. It tells you that a filled-in record without
> your name on it is a defect and should be deleted. There are now **208** such
> records and they are the deliverable. See §6 and Q-60.

---

## 1. The short answer

Nothing in this repository is *blocked* on a trade marks expert. One question is
formally waiting on one, and it is low urgency. What is actually waiting is
different and larger:

**208 records have been written by a machine and no person has read a single
one.** A signature is the only thing in this project no amount of agent time can
produce, and under ADR-0086 silence never produces one either. The expert's job
is no longer to compose records from a blank form — it is to interrogate and
correct records that already exist, and to sign the ones that survive.

| | Records | Signed by a person | Frozen |
|---|---|---|---|
| `eval/gold/` | 190 | yes — `TC`, on a date | **yes** (ADR-0080) |
| `authored/` | 208 | **no — `approved_by` is null on every one** | no |

The 190 are frozen deliberately, so they stay an independently produced
reference set against which the 208 can be measured (ADR-0080). What the freeze
forbids is an *agent* writing into them; it does not forbid the expert revisiting
their own earlier record. It does mean the yardstick moves if they do, so it is
worth being deliberate about — and it is not where the next hour is best spent.

---

## 2. What is waiting, in order of value

### A. The 130 concept typings — the readiest thing, and the one to do first

**Artefact:** `data/derived/concept-typing.xlsx`, sheet `concept-types`.
**Source of truth:** `authored/concept-types.yaml`.
**Reasoning behind each row:** `data/derived/reports/concept-typing.md`.

One row per concept, one dropdown, and every `type` cell is **already filled in
by a machine**. `approved_by` and `approved_date` are blank and the tooling
refuses to fill them. Correcting a wrong group is one dropdown; signing a right
one is a name and a date.

The nine groups and what landed in each:

| Group | Rows | What it means |
|---|---|---|
| `relevant_factor` | 41 | something that feeds the answer |
| `procedural_step` | 21 | an act or event moving an application between states |
| `legal_test` | 17 | a question the decision maker must answer |
| `subject_matter` | 14 | the thing the process operates on |
| `exception` | 11 | something that takes a case out of the rule |
| `ground_of_refusal` | 8 | a reason an application can be refused |
| `process_role` | 8 | a person or body that acts |
| `instrument_or_record` | 7 | a document, entry or endorsement produced |
| `external_instrument` | 2 | a treaty or scheme Australia adopts rather than makes |
| `none_of_these` | 1 | `GC-0051`, deliberately — see below |

**The first four groups are the owner's and were ruled on** (OQ-0001,
2026-09-08). **The five process groups are a machine's proposal from
2026-09-09** and are provisional (ADR-0098, OQ-0026). Disagreeing with the
*existence* or *boundaries* of those five is in scope and is wanted.

**Where to spend the first hour.** Not row 1 to row 130. Every row carries an
`expert_should_check` note naming the one thing that record most expects to have
got wrong, and 120 of the 130 notes are distinct. Four kinds of row repay
attention first:

1. **The four the machine names as weakest** (OQ-0026): *classification of goods
   and services* (`GT-0121`, the lowest-confidence typing among the 53
   process-group assignments — the concept conflates a scheme, an act and a set
   of classes, and the record suggests splitting the concept would be a better
   answer than moving it); *an
   international registration designating Australia*; the *divisional
   application* / *series of trade marks* pair, which should be decided
   together; and *conditions or limitations*, which has a real claim on the
   owner's own `exception` group — if it does, the two ways of sorting are not
   cleanly separable at all.
2. **The nine typings below 0.6 confidence**, of which two sit at 0.50:
   `GT-0007` and `GT-0014`, both typed `exception`. The others are `GT-0005`,
   `GT-0028`, `GT-0035`, `GT-0039`, `GT-0111`, `GT-0121`, `GT-0126`.
3. **The family judgements**, where one answer settles many rows. The largest
   covers fifteen: `GT-0017` to `GT-0023`, `GT-0025`, `GT-0026`, `GT-0030` to
   `GT-0034`, `GT-0036` and `GT-0037` are all typed `relevant_factor` because
   they name material rather than a reason to refuse. **If that reading is
   wrong it is wrong for all fifteen**, and a single sentence settles them.
   Smaller families: the three ownership branches (`GT-0031` phoneword,
   `GT-0032` domain name, `GT-0034` radio call sign) with `GC-0035` beside them.
4. **`GC-0051` — *mandatory application of the section*** — deliberately left in
   `none_of_these`. It is a rule *about* a ground rather than a ground, a test,
   a factor or an exception, and it is not a person, a thing, an act, a document
   or a treaty either. Whether the taxonomy should hold such a thing at all is a
   domain question, and inventing a tenth group for one record was refused as
   fitting the taxonomy to the data.

**Questions only the expert can settle here**, drawn from the records
themselves:

- Whether *connotation* and *likely to deceive or cause confusion* are genuinely
  two questions in practice or one run together (`GT-0001`/`GT-0002`/`GT-0003` —
  if they collapse, three typings change).
- Whether *denotation* does any work of its own in examination or appears only
  in quoted case law. If the latter, `none_of_these` is the honest answer.
- Whether an exception that is discretionary (*may accept*) is the same kind of
  thing as one that is mandatory — s 44(4) prior use is mandatory and is typed
  identically in this pass (`GT-0066`).
- Whether *examiner*, *decision maker* and *Registrar* are three roles or three
  names used loosely for one. `GC-0044`, `GC-0045` and `GC-0046` hold them
  apart; the expert's own 2026-08-26 note argues they are distinct and
  load-bearing.
- Whether an event nobody performs (*lapsing*) belongs beside acts somebody does
  (*withdrawal*) — `GT-0098` against `GT-0123`.

### B. The 78 authored concepts — vocabulary drawn from 37 Manual Parts

**Source:** `authored/concepts.yaml`. **No review workbook exists for these
yet** — the `concepts` sheet of the workbook ships empty. Rendering one is agent
work and has not been done; see §5.

Written 2026-09-08/09 after the section 43 boundary was withdrawn (ADR-0081,
ADR-0095), from the Parts that boundary had hidden; their definition sources span
37 Manual Parts. 75 rest on a passage that states the term explicitly; 3 are
inferred.
Each carries its passages with spans and content hashes, its argument, the
readings it rejected, and one named thing it most expects to have got wrong — 71
distinct such notes across 78 records.

**What an expert is being asked about each one:** is the preferred label the term
practice actually uses; are the `alt_labels` genuinely the same idea; are the
`not_labels` genuinely different ideas; is the passage cited the right passage
to define it from.

Representative open points the records raise themselves:

- `GC-0054` *prohibited sign* — is that the right preferred label? Part 31's
  title pairs it with *prescribed*, and the Act uses neither word for s 39(1).
- `GC-0055` *prescribed sign* — should the six prescribed types each be a
  narrower concept? An examiner reasons about them individually.
- `GC-0056` *so nearly resembling* — does practice in fact apply the s 10 case
  law to this test?
- `GC-0057` *cannot be represented graphically* — the definition is taken from
  Part 10.3, which is about representing the mark on the application; a Part 21
  passage discussing s 40 directly may be the better source.
- `GC-0087` *transmission* — the passage defines assignment and transmission
  together and never separates them, so the record is evidenced for the pair and
  not for this half of it. Lowest-confidence concept in the set.

### C. Three duplicate concept pairs that nothing discloses — **new finding, S020**

Ten authored concepts carry a preferred label identical to a signed concept's.
Seven say so on their own record. **Three do not**, and each is a signed record
and an unreviewed record claiming the same term with different sources:

| Authored | Signed | Term | The difference |
|---|---|---|---|
| `GC-0053` | `GC-0006` | ground for rejection | The signed record ties the term to s 43 and treats *objection* as a variant; the authored one treats the grounds as a closed set fixed by the Act and asks whether a s 33(1)(a) formality failure is a ground in the same sense. |
| `GC-0100` | `GC-0014` | endorsement | The signed record is about endorsement *wording* under s 43 practice; the authored one is about what goes on the Register to record acceptance on evidence. |
| `GC-0101` | `GC-0041` | evidence of use | The signed record separates evidence a party files from material an examiner gathers — a distinction its note calls load-bearing under s 43. The authored one is formal evidence filed to overcome a s 41 ground. |

**The question, precisely, is whether each pair covers the same ground** — and
the answer decides itself from there. ADR-0080 consequence 2 already settles what
happens if it does: the signed record wins and the authored one is retired, on
the reasoning that a signed record is strictly better evidence of the same thing.
If it does not — if these are two senses of one term — both stand and the labels
need to distinguish them, which is what the seven disclosed collisions assert
about themselves.

**An agent may not answer it**, because answering means deciding that a signed
record does or does not cover a case its author did not address, and that is
reading a judgement into somebody's signature. Recorded as `Q-59` and ADR-0101.

### D. The examiner-conduct rule the expert wrote and the repo never stored

On 2026-08-26 the expert wrote, in `review/returned/260826-expert-feedback.md`:

> It is not merely sufficient for the examiner to have doubt that a connotation
> exist, but rather the registrar as a whole. […] It would be generally expected
> that an examiner consult with their team leader and the s43 SMEs before
> allowing a trade mark to proceed to registration based solely on doubt about
> if a connotation exists.

with *Blount Inc v Registrar of Trade Marks* (1998) 40 IPR 498, 503 (*Oregon*) on
s 33 and the reversed burden.

**That is still in the file it arrived in and in no record.** The structure to
hold it now exists — a relationship can be *about* a role and can carry `must`,
`may` or `should` (ADR-0073) — and nothing has been written into it. Under the
amended rules an agent may now draft the rule and stamp it unreviewed
(OQ-0022 was withdrawn on that basis), but it has not drafted it. **What the
expert should look at is whatever it drafts**, and the prior question of whether
a rule about people belongs in a structure built for rules about legal ideas at
all.

### E. Definitions, and the three role terms that exist nowhere

The expert's second point on 2026-08-26 was that the vocabulary was drawn from
Part 29 alone and gives "a limited view on what some of the roles are", naming
nine terms needing high-level definitions.

Position today, checked against every store:

| Term | Status |
|---|---|
| Registrar | present as a concept |
| Examiner | present as a concept |
| Decision Maker | present as a concept |
| Oppositions | present as a concept |
| Grounds for Rejection | present as a concept |
| **Delegate** | **only as an alternative label under *Registrar*** |
| **Office Practice** | **absent from every store** |
| **Subject Matter Expert (SME)** | **absent from every store** |
| **Adverse Report** | **absent from every store** |

And the structural point underneath it: **no concept in this repository carries a
written definition.** A concept record holds labels, near-misses and
`definition_sources` — pointers to passages — and nothing else. There is no
definition record type at all: `authored/definitions.yaml` has no schema, no id
prefix and no place in the record-type registry. Until that exists, the
"high-level definitions" the expert asked for have nowhere to be stored, and no
amount of reviewing will produce them. That is agent work and it is listed as
such in `docs/HANDOFF.md` §2 item 5.

### F. `OQ-0017` — the one question formally waiting on an expert

Status `parked`, urgency low. **May a bare "section 15(1)" be read as the *Trade
Marks Act 1995*?**

The expert rejected two draft prohibitions on the principle that inferring the
Act from a bare section reference "is acceptable due to the TM focused nature of
the tool", and that the tool "should be allowed to clarify if a passage is
specifically sourced from the legislation". That sits against the upstream
position, which refuses to resolve an ambiguous citation at all — though the two
are not quite the same claim: upstream's ambiguity is about *which of several
instruments in scope* is meant, not about a bare section in a trade-marks-only
tool. Where the line falls between a safe inference and an invented one is the
question, and one kind of prohibited use currently rests on a single record
because of it.

### G. Evaluation thresholds — expert input, owner's decision

`review/seed/measures.seed.md` holds draft numbers, every one invented by a
machine. They encode risk appetite, not statistics: what score is good enough
for an examiner to rely on something without checking the source, and what score
means stop. The owner decides; the expert is the person who knows what an
examiner does when a tool is wrong.

---

## 3. What is *not* the expert's, so their time is not spent on it

- **The 190 signed records.** Frozen as the measurement yardstick (ADR-0080).
  The freeze stops an *agent* writing into them, not the expert revisiting their
  own record — but the yardstick moves if they do, and nothing here asks them to.
- **The eight records they rejected in round 1.** They stay rejected. A signed
  rejection is a human decision and nothing in the amended rules licenses
  reversing one (ADR-0084 consequence 2).
- **The eight records marked *amend* whose amendment has not been applied.** The
  correction is already recorded in their words; applying it is agent work.
- **The "ten decisions on the critical path"** in
  `data/derived/reports/blockers.md`. That report is honest about its data and
  was, until 2026-09-09, misleading about whose data it is: since ADR-0084 every
  decision on it is an agent's to author, not an expert's to sign.
- **The four other items under the dashboard's "Waiting on a trade marks expert"
  heading** — `OQ-0014`, `OQ-0015`, `OQ-0016`, `OQ-0022`. All four were answered
  or withdrawn by the owner on 2026-09-08. Only `OQ-0017` remains.
- **Which model may be used, what base IRI the project mints under, who may
  sign, how much of the Manual the graph carries.** Owner and agency decisions.
- **Anything about examination outcomes.** The system does not state one and no
  agent may widen that. The expert's own approved prohibited-use records are
  part of what holds that line.

---

## 4. What a signature actually does, and what it does not

Three states, and they never blur (CLAUDE.md rule 4, ADR-0085, ADR-0086):

- **authored** — a machine wrote it; nobody has read it. Usable, servable, and
  labelled as never validated. **Permanently so, unless somebody signs it.**
- **approved** — a named person read it and signed it on a date.
- **rejected** — a named person threw it out.

**Reading a record and leaving it alone does not sign it.** Silence is never
approval, an old record never becomes approved by being old, and no agent may
ever write into `approved_by` — that field existing untouched is the single
thing the whole scheme is built to protect.

**The one door.** A correction becomes a record through `tmk-transcribe`, from a
workbook with `approved_by` filled in, and by no other route. Marked-up
spreadsheets, prose, a marked-up worksheet or a recorded conversation all work
as input — an agent transcribes them and the transcription is filed unmodified
in `review/returned/` alongside what it was taken to mean.

---

## 5. Readiness — and the pack that closed it

**Superseded on 2026-09-09 by `tmk-expert-pack`** (ADR-0102). Every item below
is now a sheet in one workbook, `data/derived/expert-request.xlsx`, with a
plain-English covering note at `docs/EXPERT-REQUEST.md`. The table is kept
because the *shape* of the gap it recorded is what the pack was built around:
three of the seven items had nothing a reviewer could open, and two of those
three could not be drafted by an agent at all.

| Item | Was | Is now |
|---|---|---|
| A — 130 concept typings | Ready | Sheet `concept-types`, pre-filled, transcriber-readable |
| B — 78 authored concepts | **Not ready** — no workbook rendered | Sheet `concepts`, pre-filled, transcriber-readable |
| C — three duplicate pairs | Ready | Sheet `2 same word twice`, all ten pairs with the three undisclosed sorted first |
| D — examiner-conduct rule | **Not ready** — nothing drafted | Question 3 on sheet `1 the big ones`. Still not drafted, and deliberately: it is asked rather than authored |
| E — definitions and missing roles | **Not ready** — no record type | Sheet `3 missing words`. The record type is still owed; the definitions are collected as prose first |
| F — `OQ-0017` | Ready | Question 6 on sheet `1 the big ones` |
| G — thresholds | Ready | Sheet `5 how accurate`, in a form that needs no metric vocabulary |

**Two of these are collected as words rather than as records, on purpose.** A
definition and an examiner-conduct rule both need a record type that does not
exist, and building the container before knowing what goes in it is how the
container ends up the wrong shape. The answers come back in the reviewer's own
words, filed verbatim, and the record type is designed against what they wrote.

---

## 6. Before handing over `eval/STAGE-0-INPUT-GUIDE.md`

That document was written for the operating model in force until 2026-09-08 and
has not been revised. Three parts of it are now actively misleading to an expert:

1. **Its opening** says an agent "cannot author the content of a competency
   question, a gold answer, a concept definition or a prohibited use". Since
   ADR-0079 an agent authors exactly those, stamped unreviewed.
2. **§9 tells the reader** that a filled-in record without their name on
   `approved_by` is "CLAUDE.md rule 1 being broken, and the record should be
   deleted rather than reviewed". Applied today, that instruction would have the
   expert delete all 208 records they were brought in to correct.
3. **§2 and §10** frame the work as a section 43 pilot and make drawing the
   pilot boundary the expert's first half-day. The boundary was withdrawn by the
   owner on 2026-09-08 and the machinery that computed one is deleted.

A dated amendment banner now sits at the top of that file pointing here.
Rewriting it properly is a session's work and has not been done.

---

## Related

- `authored/README.md` — the authored store and the one door out of it
- `review/questions/open-questions.yaml` — the live queue, and who each item needs
- `docs/DECISIONS.md` ADR-0079 to ADR-0088, ADR-0098 — the amended operating model
- `docs/QUIRKS.md` Q-59, Q-60 — the duplicate labels and the stale guide
- `review/returned/260826-expert-feedback.md` — the expert's own words, unedited

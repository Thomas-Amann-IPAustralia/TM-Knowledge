# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-09-08 · session S017 · branch `claude/next-phase-gd2x7i`

---
## 0. What S017 did, in one paragraph

**S016 built the store and wrote nothing into it. S017 wrote the first content
into it, and the store behaved as advertised.** All 52 approved concepts are now
sorted into the owner's four groups, in `authored/concept-types.yaml`, each
record carrying the passages it rests on, a written argument for the group, the
reading it rejected and the thing it most expects to have got wrong. **No expert
has read a word of it, every record says so in a field a machine can read, and
`approved_by` is null in all 52.** ADR-0092 to ADR-0094. The gap that had stood
at 0 of 52 for five sessions is now an afternoon of correction rather than an
afternoon of composition — which was the entire bet ADR-0079 made.

**What the numbers say, and the second one is the finding.** 52 records, 90
evidence entries, 0 harness defects, 0 SHACL defects. Every one is
`corpus_inferred` and none is `corpus_explicit`, because the Manual never states
a concept's group in terms — it says what a decision maker must be satisfied of,
and the group is a reading of that. **Then: 30 of the 52 came out
`relevant_factor` and exactly 1 came out `ground_of_refusal`.** That is what a
vocabulary built around a single ground looks like when it is sorted by the role
each concept plays in that ground's decision. It is reported under the tally in
the evidence pack and asked as OQ-0023, because a reviewer who thinks the group
is too empty is disagreeing with the taxonomy rather than with any row.

**The reviewer's sheet now arrives filled in, and says so twice.**
`data/derived/concept-typing.xlsx` pre-fills the `type` column from the authored
store; the banner on it states how many cells a machine wrote, that nobody has
read them, and that a row left alone stays `unreviewed`.
`data/derived/reports/concept-typing.md` carries each proposal's argument beside
the passages. **What did not move is the door:** `approved_by` leaves
`typing.rows()` empty whatever an authored record says about itself, a refused
record pre-fills nothing, and `tmk-transcribe` reading a signed workbook is still
the only way into `eval/gold/`.

**Two bugs, both invisible until there was something to count.** A
`none_of_these` record was skipped before its typing node, its provenance and the
counter, which contradicted the comment three lines above it and printed `45`
instead of `52` (ADR-0093, Q-50). The line beside it read `45 of 0 authored ones`
— dividing typings of signed concepts by the number of concepts a machine wrote,
which is structurally zero. Both are fixed and both are the same shape: a branch
that only runs on data the repository does not hold yet is untested by
construction, and its comment is the only specification it has. **Expect the
first record of every new kind to find one of these.**

**One decision was forced and is worth reading before authoring anything else.**
`authored_by` names the model that *wrote the record*, so these 52 carry
`claude-opus-5` and not the configured `gemini-3.8-flash`. ADR-0087 pinned the
model for API-backed extraction; no key reaches this container, so the session
agent authored directly. Stamping the configured model would have been provenance
corruption nothing could undo — unfalsifiable afterwards, because nothing in the
artefact distinguishes a truthful stamp from an invented one (ADR-0094). The
store may now hold work from more than one author, and **any measurement over it
splits by `authored_by` before it means anything.**

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

### The numbers as at S017

Five moved and none of them is plumbing: this is the first session whose numbers
changed because content was written. The rest is the baseline the next session's
work is measured against.

| | |
|---|---|
| Ontology modules | 9, OWL 2 RL, in `ontology/draft/` — **none approved** |
| Classes declared | **50** · **27 hold nothing**. Four filled this session — `tmk:GroundOfRefusal`, `tmk:LegalTest`, `tmk:RelevantFactor` and `tmk:Exception` — and they filled **in the authored graph only**, so no query asking for signed knowledge reaches them. They had been declared and empty since S010 |
| Predicates | 14, generated from the 35 approved relationships |
| Source graph | 16,405 triples over 216 chunks, 529 reified citations |
| Approved graph | **3,230 triples** (was 2,946), every one traceable to a signed record. The 284 new ones are the `tmk:origin` and `tmk:reviewStatus` stamps every node now carries — see Q-49 for why that is not redundant with the named graph |
| Authored graph | **698 triples** (was 0). `graph/authored.ttl` — 52 concept typings, every node stamped `tmk:origin "authored"`, its model, its date, its basis and its reasoning |
| SHACL | 0 defects, 0 gaps, 29 notes — unchanged by 698 authored triples arriving, which is the point of having run it over an empty authored graph first |
| Competency queries | 13 of 20 questions. All eight that name `tmk:ApprovedAssertion` answer over signed content only, by design |
| CONSTRUCT rules | 2. RULE-0002 approved; RULE-0001 pending — **and an agent may not approve it** |
| Signed records | **190, frozen** |
| Authored records | **52**, all concept typings, all `unreviewed`, **0 refused**. 90 evidence entries; every record `corpus_inferred`, none `general_knowledge` |
| Concepts typed | **52 of 52 by a machine · 0 of 52 by a person.** The completeness gate still reads `0 of 50–100` and is right to: it counts `eval/gold/` (ADR-0080 c3) |
| The typing distribution | `relevant_factor` 30 · `exception` 8 · `none_of_these` 7 · `legal_test` 6 · `ground_of_refusal` 1. **The shape is a finding, not a tally** — OQ-0023 |
| Authors in the store | **1** — `claude-opus-5`. Not the configured `gemini-3.8-flash`, and the difference is deliberate (ADR-0094) |

Two findings from the S015 conversation that are worth carrying, both measured:

- **The vocabulary is a Part 29 vocabulary.** 86 of ~95 definition-source
  references across the 52 concepts point at Part 29. One each from Parts 12, 22,
  23, 47, 51; two from Part 20.
- **Four of the nine role terms the expert named are absent entirely** — Delegate,
  Office Practise, Subject Matter Expert, Adverse Report. Q-28 explains why: the
  old scope rule selected passages that *cite* section 43, and a term's definition
  sits in a passage that cites nothing. That blindness is gone with the boundary.

## 2. The next action

**Nothing is blocked on a human.** OQ-0007 — which model, and may Manual text be
sent to it — became a blocker when ADR-0083 opened Stages 2–4 and was answered the
same day: **Gemini 3.8 Flash**, credential in the `GEMINI_API_KEY` repository
secret (ADR-0087).

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

Everything below is an agent's to do.

**In order of value:**

1. **~~Type the 52 concepts~~ — done in S017** (ADR-0092). 52 records, 90
   evidence entries, 0 defects, and the claim that the plumbing was finished held:
   writing the file was all it took, and `tmk-harness`, `tmk-coverage`,
   `tmk-graph` and the dashboard picked it up with no code change. Two things it
   *did* need, both of which the next content pass will need too:

   - **The pass that produces the reviewer's artefacts had to learn about the
     store.** `tmk-typing` now reads `authored/` and pre-fills the workbook. Any
     other place that renders work for a person to correct has the same gap
     until somebody closes it — check before assuming a report shows authored
     content.
   - **Two counting bugs surfaced the moment there was something to count**
     (Q-50). Read the comments around any counter you are about to make non-zero
     for the first time; the comment is its only specification.

   **What is left here is the review round, and it is not an agent's to run.**
   The workbook and the evidence pack are rendered and waiting. OQ-0023 asks the
   owner whether the taxonomy itself survives contact with the result — 30 of 52
   in one group, 1 in another — because correcting 52 rows inside a taxonomy he
   would have changed is the way to make a review round not happen.

2. **The next content pass.** Do it the way this session did the typings —
   evidence sliced out of the snapshot rather than retyped, `corpus_inferred`
   unless the corpus really does state it in terms, and an `expert_should_check`
   that names something specific rather than a disclaimer. Two candidates, and
   the obvious one has a trap in it:

   - **New records, in the record types furthest under their band:**
     `search-questions.yaml` (1 of 20–50), `retrieval-questions.yaml` (10 of
     20–50), `relationships.yaml` (35 of 50–100). These are additions, they need
     no new machinery, and the typings just proved the path end to end.
   - **The five blank `modality` fields are *not* the cheap win they look
     like.** They sit on signed `GR-` records, and an agent may not fill a field
     inside a signature — that is exactly why a concept's type became a separate
     record instead of a field on the concept (ADR-0071). Authoring them needs a
     record type that holds a modality apart from the relationship it belongs
     to, which does not exist. The harness message said "nothing here may supply
     it" until this session and now says what is actually true; read it before
     assuming the field is fillable.

   **One thing to settle first, because it is cheaper before more records exist
   than after:** the retirement path in item 3 below. The typings will hit it as
   soon as one comes back signed.

3. **~~Build the authored-store plumbing~~ — done in S016** (ADR-0089 to
   ADR-0091). What is left of it, and item two is now urgent rather than
   theoretical:

   - **`authored/definitions.yaml` has no record type.** It needs a schema in
     `eval/schemas/`, an id prefix in `docs/IDENTIFIERS.md` §3, and entries in
     `RECORD_TYPES`, `ID_PREFIXES` and `goldset.GOLD_FILES`. Until then the store
     reports the file as unreadable, which is correct and is not a bug. Watch the
     ripple: `RECORD_TYPES` is iterated by the harness, the workbook and the
     intake path, and `goldset.FILE_FOR[record_type]` is read in message text, so
     a record type added to one map and not the others raises `KeyError` in a
     message rather than failing usefully.
   - **The eight competency queries still name `tmk:ApprovedAssertion`** and
     therefore answer over signed content only. That is under-reporting rather
     than laundering, and it is safe. Whether they should also serve authored
     content — labelled, per ADR-0082 — is a Stage 7–8 question about the
     retrieval surface, and it needs deciding before anything is built on top of
     those queries.
   - **Nothing moves a record from `authored/` to `eval/gold/` yet, and there
     are now 52 records waiting to need it.** `tmk-transcribe` writes gold
     records from a workbook; it does not know about the authored store, and
     nothing retires an authored record when a signed one covers the same ground
     (ADR-0080 consequence 2). The reviewer's row **keeps the authored record's
     id**, so the first signed typing puts one `GT-` id in both stores and the
     harness reports a defect naming both. **That is designed, not broken** —
     read Q-52 before trying to make it quiet, and in particular do not resolve
     it by minting a fresh id or by deleting the authored record. It is the next
     real design question in this area and it is no longer hypothetical.
4. **Resolve the 178 seed records** into `authored/` (ADR-0084). Honour the
   reviewer's `amend` instructions where they exist. Do **not** resurrect the
   eight rejected records; where an authored record covers the same ground, it
   cites the rejection in `authored.supersedes_rejected` and says why it differs
   in `reasoning` — the envelope has a field for exactly this.
5. **Retire `tmk-boundary`** and `data/derived/reports/boundary.md`. The code
   still runs and computes a boundary that no longer exists — which is worse than
   code that fails, because it produces a plausible answer to a withdrawn
   question.
6. **Re-scope the worksheet and recon to the whole Manual** (ADR-0081 consequence
   1). `tmk-recon` currently costs section 43; it should cost the corpus, ordered
   by working priority.
7. **Then extraction** (ADR-0083), deterministic paths first, measured against the
   frozen 190. That recall figure is the number ADR-0010 wanted to exist and never
   got.

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
| 60 authored concepts | the board still reads `0 of 50–100` in the **Signed** column and `60` in **Authored** | ADR-0080 c3 |

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
> - **Q8 is closed.** It asked where section 43 stops. It does not have to —
>   the boundary is withdrawn and the whole Manual is in scope (ADR-0081).
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

| # | Question | Blocks | Raised |
|---|---|---|---|
| ~~Q1~~ | ~~What is the pilot scope?~~ **Answered S002: s 43** (ADR-0013). The *boundary* is deliverable 1 — see Q8. | — | S001 |
| Q8 | **Half answered S012.** The owner gave the boundary *rule* on issue #12 (one hop, landing on the chunk; ADR-0072), implemented as `tmk-boundary`. The *document* is still not written — he did not say whether GI is the centre or a corner, or whether point-in-time questions are in scope, and OQ-0021 asks about bare citations. Original question: what is the s 43 **boundary**? **A draft to correct now exists** at `review/seed/pilot-scope.seed.md` (S007), with the recon numbers and an exclusion list. Which Manual Parts/chunks, which neighbouring provisions, is GI the centre of gravity or a sub-topic, are point-in-time questions in scope? Prompted for in `eval/STAGE-0-INPUT-GUIDE.md` §2. **Answerable against numbers** — `tmk-recon` reports where the citing chunks sit and what each candidate rule costs. | All remaining Stage 0 **content**. Does not block the worksheet — ADR-0017, ADR-0022 | S002 |
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
afterwards.
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

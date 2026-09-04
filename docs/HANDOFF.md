# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-09-03 · session S010 · branch `claude/trademark-ontology-draft-ou3vnj`

---

## 1. Where the project actually is

**The owner changed the plan, and the plan was right to change.** Their
instruction, in their words: *"I'm not going to go back to the TM expert for
now. We're just going to have to work with what we have… Our goal is to
demonstrate the value and feasibility of a full ontology. We need to make
progress on this."*

So S010 built the thing the programme was waiting to build. **There is a section
43 ontology, a knowledge graph under it, a SHACL gate that passes, and thirteen
competency questions answered by SPARQL with citations.** Not approved — see
below — but running, tested and reproducible from a clean checkout in three
commands.

```bash
pip install -e ".[test,intake,rdf]"     # note the new `rdf` extra
tmk-fetch-upstream                      # the pinned snapshot (~4s)
tmk-graph --write --rules               # build the graph, run the candidate rules
tmk-shacl                               # the gate. 0 defects, 0 gaps, 29 notes. Exit 0
tmk-ask                                 # 13 competency questions, answered
tmk-ask CQ-0017                         # just one
tmk-ontology-report --write             # what it holds and what it cannot do
tmk-harness                             # unchanged: 0 defects, 12 gaps. Exit 3
python3 -m pytest -q                    # 409 pass (312 before, 97 new) — `python3 -m` (Q-29)
```

| | |
|---|---|
| Ontology modules | 9, OWL 2 RL, in `ontology/draft/` — **none approved** |
| Classes declared | 49 · **30 of them hold nothing**, and that is reported not hidden |
| Predicates | 14, **generated** from the 35 approved relationships, regeneration-checked |
| Source graph | 16,405 triples over 216 chunks, 529 reified citations |
| Approved graph | 2,942 triples, every one traceable to a signed record |
| SHACL | 0 defects, 0 gaps, 29 notes |
| Competency queries | 13 of 20 questions; 6 need Stages 7–8; 1 could be written |
| CONSTRUCT rules | 2, **both PENDING approval**, output quarantined as `candidate` |

**Nothing in Stage 0 moved and nothing was meant to.** `tmk-harness` still reports
0 defects and 12 gaps. 190 approved records, 178 seed records still awaiting
correction, 10 decisions holding 168 of them — all exactly as S009 left it. The
ontology work is a *transformation* of the 190, not an addition to them.

**How this stayed inside rule 1.** Every node in the graph came out of
`eval/gold/`, where a named reviewer signed it on a date. No concept was defined,
no modality inferred, no relationship authored. `relations.ttl` is generated
rather than written for exactly this reason — a hand-written predicate dictionary
would be an agent choosing the vocabulary — and a test compares the committed
file against a regeneration. ADR-0056 is the owner's decision to proceed and sets
out why this is not the Stage 2 work ADR-0010 forbids: **that prohibition is on
extraction, not on modelling**, and nothing here generated a candidate or
measured a recall.

**Three things are worth looking at before anything else.**

*The trust metadata paid off.* Citations are nodes carrying upstream's
`extraction` and `certainty`, not flattened edges — and CQ-0017 shows why that
mattered. It reproduces `tmk-recon`'s Part distribution exactly (33 Part 29, 10
Part 32A, 5 and 5 …) and adds a column recon does not have: **Parts 12, 23, 31,
47 and 52 are carried into the section 43 impact set entirely by citations
upstream inferred from a bare "section 43"**, not by links the Manual's authors
wrote. "This Part needs reviewing" is a materially weaker claim there.

*A prohibition became a constraint.* PU-0004 — *"Section 43 of the Act requires
the connotation to be obvious, direct and immediate"* — was marked
`detectable_by: shacl` and was a paragraph in a YAML file. It now blocks a
publish. The model separates where words are (`tmk:statedIn`) from what they are
presented as coming from (`tmk:attributedTo`), and the shape fails a proposition
stated in a practice passage and attributed to the Act. Its fixture carries a
**conforming twin** — the same words, the same passage, honestly attributed —
because a constraint that fires on both passes a fires-test and is useless.

*CQ-0023 returns a blank first row on purpose.* Asked which decisions the Manual
relies on for the proposition that a connotation must arise from the mark itself,
the answer is: **none.** The passage stating it, `TMM/Part29/2/2/3`, cites no
decision at all. An inner join would have hidden that by returning only the rows
that happened to have cases.

**The largest gap the work exposed was not on any list.** `GroundOfRefusal`,
`LegalTest`, `RelevantFactor` and `Exception` are declared and **empty**. All 52
approved concepts are bare `tmk:LegalConcept`, because the gold concept record
has no type field and deciding that *connotation* is a test rather than a factor
is a legal judgement. 39 of the 52 also sit outside any hierarchy — no broader,
no narrower. A vocabulary that is mostly flat is a list with extra steps.

Read `data/derived/reports/ontology.md` §5 rather than this paragraph: it is
generated from the same run that builds the graph, it counts every gap, and it
will not go stale the way this file will.

## 2. The next action

**Thread A — the owner, and it is four rulings.** These are the things only a
person can settle, ordered by how much each unblocks. None needs the TM expert;
all four are judgement calls the owner said they were willing to make.

| # | Ruling | Effect |
|---|---|---|
| 1 | **Type the 52 concepts** into `GroundOfRefusal` / `LegalTest` / `RelevantFactor` / `Exception` — or say the taxonomy is wrong | The single largest gap. One pass over a list, no new records, and it is what turns a flat vocabulary into a hierarchy the retrieval stages can generalise over |
| 2 | **Rule on the four unmatched question labels** (Q-37) — `deceptively similar` first | `CQ-0007` names as an expected concept a term `GC-0002` records as a **not-label**. Either the vocabulary needs the s 44 concept, or the question is using it as a boundary marker |
| 3 | **Approve or reject the two CONSTRUCT rules** | Both `PENDING`; everything they produce is quarantined until one way or the other |
| 4 | **Confirm or overturn ADR-0060 and ADR-0061** (Q23, Q24) | What gets committed under `graph/`, and whether a query file must declare its limits |

Ruling 1 has a shape to fill: the concept record has no `type` field today, so
taking it needs either a schema addition or a separate register. That is one
session's work once the answer exists, and **it should not be built before the
answer exists** — building the container first is how the container ends up
shaping the content.

**Thread B — the experts. Paused by the owner, not abandoned.**
`data/derived/stage0-blockers-review.xlsx` is still rendered and still correct:
ten records, with `data/derived/reports/blockers.md` as the covering note. When
the expert is back in the loop it goes out unchanged. Nothing in S010 invalidated
it, and nothing in S010 should be read as replacing it — the 178 seed records
still need a person, and `eval/pilot-scope.md` and `eval/measures.md` still do not
exist.

**Thread C — agents.** In rough order of value:

1. **Write `CQ-0010`'s query, or record why it cannot be written.** It is the one
   answerable question with no query. (*Why BALI on bras raised no ground and
   SHETLAND on clothing did* — it may genuinely need case reasoning the corpus
   cannot support, in which case saying so is the deliverable.)
2. **Run the loop if a workbook arrives.** Unchanged: `tmk-transcribe FILE
   --write`, `tmk-reconcile FILE --write`, then `tmk-harness`, `tmk-coverage`,
   `tmk-blockers` — and now also `tmk-graph --write`, `tmk-shacl`,
   `tmk-ontology-report --write`, because new approved records change the graph.
3. **Regenerate and commit the reports.** `tmk-ontology-report` joins
   `tmk-coverage` and `tmk-blockers` as generated status. Do not hand-edit any of
   the three.
4. **Keep the pin current.** Bumping it makes every `source_content_hash` stale by
   design — and now the graph says so too, per-assertion, via `tmk:isStale`.

**Do not** build a retrieval layer, a search index or a vector store. Stages 7
and 8 are what the six deferred competency questions need, and building either
now fixes design choices no measurement has justified. **Do not** start Stage 2 —
ADR-0010 is untouched by ADR-0056 and the temptation is unchanged. **Do not**
promote a module from `ontology/draft/` to `ontology/` without a recorded human
decision (ADR-0057).

## 3. Open questions — need a human

| # | Question | Blocks | Raised |
|---|---|---|---|
| ~~Q1~~ | ~~What is the pilot scope?~~ **Answered S002: s 43** (ADR-0013). The *boundary* is deliverable 1 — see Q8. | — | S001 |
| Q8 | What is the s 43 **boundary**? **A draft to correct now exists** at `review/seed/pilot-scope.seed.md` (S007), with the recon numbers and an exclusion list. Which Manual Parts/chunks, which neighbouring provisions, is GI the centre of gravity or a sub-topic, are point-in-time questions in scope? Prompted for in `eval/STAGE-0-INPUT-GUIDE.md` §2. **Answerable against numbers** — `tmk-recon` reports where the citing chunks sit and what each candidate rule costs. | All remaining Stage 0 **content**. Does not block the worksheet — ADR-0017, ADR-0022 | S002 |
| ~~Q2~~ | ~~How does this repo get the upstream snapshot?~~ **Answered S003, built S004** (ADR-0004, ADR-0021, ADR-0026). | — | S001 |
| Q3 | Which LLM is "agency-approved" for the Stage 2–4 extraction steps, and under what data-handling conditions may Manual text be sent to it? **Now also touches Stage 0:** `review/seed/` records carry `model: null` because naming one would pre-empt this (ADR-0043 consequence 4). If the agency requires the model recorded, it is a provenance field and a one-line change. | Stages 2, 3, 4 | S001 |
| Q4 | ~~What does "approved" look like as a recorded artefact?~~ **Answered S006: the workbook's `approved_by`/`approved_date` columns are the artefact** — a name and a date, no separate signed-off file or external register (ADR-0039). **Still open: who are the approving experts?** — expected to arrive with the experts' own content. | Nothing structural; who-question blocks nothing today | S001 |
| ~~Q5~~ | ~~Does ADR-0005 hold?~~ **Answered S003: yes** (ADR-0021). | — | S001 |
| Q6 | Case law is cited by the corpus but is not held as documents anywhere. Is acquiring decision texts in scope for this repo? **Costed for the pilot:** 58 distinct decisions are cited from the 216 in-scope chunks. The harness reports a case ref as a NOTE — checked for grammar, resolvable by nothing (Q-11). | Stage 2 citation resolution, Stage 8 retrieval | S001 |
| Q7 | What base IRI may the project mint under? `docs/IDENTIFIERS.md` proposes `https://data.ipaustralia.gov.au/tmk/`; persistent IRIs need control of that domain, which is an organisational call. Still not blocking: one constant in `config.py`, overridable by `TMK_BASE_IRI`. | RDF serialisation only | S001 |
| ~~Q9~~ | ~~Does the owner accept **ADR-0016** and **ADR-0018**?~~ **Answered S006: yes, both** (ADR-0038). | — | S003 |
| ~~Q11~~ | ~~Five S004 ADRs are agent-proposed: 0024, 0026, 0027, 0028, 0029.~~ **Answered S006, in part:** 0024, 0026, 0027 confirmed (ADR-0040); 0028 reversed, not confirmed (ADR-0042, `data/derived/` is now committed). **0029 still open** — owner had no context for it ("I have no idea what this means"); it needs none, since it already reflects current practice and nothing hinges on ruling it either way. | Nothing | S004 |
| Q12 | Six S005 ADRs are agent-proposed: **0030** (three severities, three exit codes), **0032** (one named gold file per record type), **0033** (the retired-id ledger), **0035** (`openpyxl` as an optional extra — *the only one that is a dependency decision*), **0036** (the workbook's cell encoding), **0037** (how transcription writes). ADR-0031 and ADR-0034 are `derived`. Owner has seen a plain summary of these (S006) but has not yet ruled on them. | Nothing | S005 |
| ~~Q13~~ | ~~Does upstream need a token in CI?~~ **Answered S006: no.** `manual-XtrACTor` is public (QUIRKS Q-13, amended S004) and GitHub Actions clones public repos anonymously, so `tmk-fetch-upstream` works in CI with `UPSTREAM_TOKEN` unset. Leave the secret unset unless the repo's visibility changes. | — | S005 |
| Q15 | **New, S007.** Does the owner confirm **ADR-0043** as recorded, including its six guards and its reversal condition? The decision to seed was the owner's; the *guards* — quarantine, the envelope, the null-and-checked `approved_by`, the single door out, the untouched harness, the delete-after-review rule — are the agent's reading of what makes it safe, and they are what an audit will be judged against. **ADR-0044** and **ADR-0045** are `derived` and need no ruling. | Nothing today; the seed set is usable either way | S007 |
| Q16 | **New, S008. Expert content.** The expert's note says the seed set carries the *presumption of registrability* and the idea of "doubt", but not the office's actual bar for applying it: it is not enough for the individual examiner to doubt a connotation exists — the Registrar as a whole must, and an examiner is expected to consult their team leader and the s 43 SMEs before accepting on that basis. They cite *Blount Inc v Registrar of Trade Marks* (1998) 40 IPR 498, 503 (*Oregon*) on s 33 and the reversed burden. **This is a rule about examiner conduct, and no record type currently holds it**: it is not a concept, not a relationship between provisions and not a prohibited use. Whether it becomes one, a new record type, or an entry in the scope document is an expert-and-owner call. Full text at `review/returned/260826-expert-feedback.md`. | The s 43 vocabulary's usefulness, and any later rule modelling | S008 |
| Q17 | **New, S008. Expert content.** The same note: the seed vocabulary was drawn from Part 29 alone, which is "not wrong" but gives "a limited view on what some of the roles are". Nine terms named as needing high-level definitions — Registrar, Delegate, Examiner, Decision Maker, Office Practise, Subject Matter Expert (SME), Oppositions, Grounds for Rejection, Adverse Report — "and there are likely more". Two row corrections say the same thing sharply (`GE-0010`, `GE-0047` on decision maker vs the Registrar). **The structural trap is Q-28**: ADR-0022's scope rule selects passages that *cite* s 43, and a term's definition is usually not in a passage that cites anything. Fix is a scope exception, a separate definitional pass, or a glossary import — expert and owner, not an agent. | Stage 3's vocabulary, and the entity type taxonomy | S008 |
| Q18 | **New, S008. Partly answered.** ADR-0048 gates `eval/gold/` on the reviewer's verdict. The rule itself — *a row crosses only on `correct` **with a name in `approved_by`*** — follows from rule 4 and ADR-0039 and needs no ruling. Three things inside it were the agent's judgement, and in plain terms they are: **(a)** if a record you signed points at one you did not, the signed one is held too — because a gold record naming a record that is not in the gold set is a pointer to nothing, which the harness calls a defect; **(b)** if a record is signed but one of its *sub-rows* (a relevance grade, an expected inference) is marked `amend` or left blank, the whole record is held — because that sub-row is part of the record, so writing it would certify a value the reviewer said was wrong; **(c)** a verdict cell that is not exactly `correct`/`amend`/`reject` — `corrrect` — stops the row rather than being read as the value it resembles. **(c) is now settled in practice** (ADR-0052): the tool stayed strict and a person overrode that one cell by name, which cost one line. (a) and (b) still stand as written and are what "18 held, then 20" in §1 is measuring. **ADR-0047, ADR-0049 and ADR-0050 are `derived`.** | Nothing today; the loop works either way, the yield changes | S008 |
| Q20 | **New, S008.** Does the owner confirm **ADR-0051**? A reviewer's decision that arrives as words is applied from an instruction file in `review/returned/`, never by editing or generating a workbook, and the instruction may do exactly two things: sign a **blank** `approved_by` on a row already marked `correct`, and settle a verdict on a **named** record. The two-operation limit is the judgement — it is what stops "they confirmed the corrections" becoming a blank cheque over 368 rows. Widening it (a pattern, a typo table, "sign everything") should be a decision, not a convenience. | Nothing; every future round that settles anything by email | S008 |
| Q19 | **New, S008.** The expert rejected both `ambiguity_collapse` prohibitions on a principle worth recording: inferring that a bare "section 15(1)" means the *Trade Marks Act 1995* "is acceptable due to the TM focused nature of the tool", and the tool "should be allowed to clarify if a passage is specifically sourced from the legislation". That sits against Q-07 and upstream's refusal to auto-resolve an ambiguous edge. They are not quite the same claim — upstream's `ambiguous` is about *which of several instruments in scope*, not about a bare section in a TM-only tool — but a session must not quietly assume either reading. Does the distinction hold, and where is the line? | Stage 2 citation resolution; the prohibited-use set's sixth kind now rests on one record | S008 |
| Q21 | **New, S009.** Does the owner confirm **ADR-0054** — what counts as a decision on the critical path? Three kinds are on the worklist (holds something and is directly resolvable; names a rejected record; held only by a marked child row) and two things are deliberately off it (a record dangling on something merely unreviewed, and a rejected record as a source of edges). The judgement being flagged is that a root need **not** be unblocked: `GA-0002`, `PU-0013` and `PU-0014` name each other in a triangle, an "unblocked roots only" rule finds none of them, and that would have hidden the largest chain on the queue. | Nothing; the report is right either way, the worklist changes length | S009 |
| Q22 | **New, S009.** Does the owner confirm **ADR-0055**'s third guard? A scoped round's pack and workbook state on their face that they are scoped, with the count they were narrowed from. The alternative — a ten-record workbook that looks exactly like a 368-record one — is how a partial review comes to be filed as a complete one. Guards 1 (the checks never narrow) and 2 (an unmatched name refuses the run) follow from rule 6 and need no ruling. | Nothing; every scoped round from here | S009 |
| Q23 | **New, S010.** Does the owner confirm **ADR-0060** — that `graph/approved.ttl` and `graph/inferred.ttl` are committed while `graph/source.ttl` and `graph/dataset.nq` are not? The line drawn is *what a file restates*: the first two are this repo's own decisions in RDF, the second two are 6.5MB of the pinned corpus, and committing those is `data/upstream/` by another route (ADR-0004). Arguable the other way — committing everything would make the graph reviewable without a snapshot fetch, at 6.5MB per rebuild in the history. | Nothing; it is one line of `.gitignore` either way | S010 |
| Q24 | **New, S010.** Does the owner confirm **ADR-0061** — that a competency query is *refused* without a `limits:` header saying what it does not answer? The requirement is the agent's reading of what `queries/README.md` implies rather than what it says, and the 60-character threshold is arbitrary. What argues for it: three limits lines are load-bearing today and each would have been a wrong answer without one — CQ-0017 measures reviewing effort and not outcome, CQ-0019 finds recorded dependencies and not subject matter, CQ-0023's most important row is a blank one. | Nothing today; every query written from here | S010 |
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

Agent-proposed ADRs awaiting human confirmation: **0011** (deferred, not
declined — see ADR-0041), **0029, 0030, 0032, 0033, 0035, 0036, 0037**,
**0043's guards** (the decision to seed was the owner's; how it is fenced is
Q15), **0048's first two judgement calls** (Q18; the third is answered by
ADR-0052), **0051's two-operation limit** (Q20), **0054** (Q21), **0055's
third guard** (Q22), **0060** (Q23) and **0061** (Q24). ADR-0044, ADR-0045, ADR-0047, ADR-0049, ADR-0050 and
**ADR-0053** are `derived`. **ADR-0052 is `human`.**
(0006, 0012, 0014, 0024, 0026, 0027 confirmed S006 — ADR-0040; 0016 and 0018
confirmed S006 — ADR-0038; 0028 superseded S006 — ADR-0042. ADR-0023,
ADR-0025, ADR-0031 and ADR-0034 are `derived`.)

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

- **Do not re-parse the Manual HTML or the legislation `.docx`.** ADR-0002.
- **Do not design a new identifier scheme.** ADR-0005, and `refs.py` implements
  it. Argue with the ADR, don't invent a third.
- **Do not write a second ref parser, IRI minter, snapshot reader, gold-set
  reader or workbook layout.** There is exactly one of each, and the whole point
  of `stage0/intake.py` is that the workbook's columns exist in one place.
- **Do not "fix" a ref that fails validation.** `InvalidRef` means the ref was
  constructed rather than read. Find the construction.
- **Do not commit anything under `data/upstream/`** (ADR-0004) — that would
  vendor another repo's corpus into this one's history. `data/derived/` is the
  opposite as of S006: it **is** committed, on purpose, as a paper trail
  (ADR-0042, supersedes ADR-0028). Regenerate and commit the diff; don't
  hand-edit what's on disk.
- **Do not put an example row in the intake workbook.** Not even a marked one.
  In a spreadsheet, copying a row is one keystroke. The seed examples live in a
  *different file* — `stage0-seed-review.xlsx` — for exactly this reason
  (ADR-0044). `stage0-intake.xlsx` stays empty.
- **Do not move a seed record into `eval/gold/` by hand**, and do not fill an
  `approved_by` in `review/seed/` to make something pass. Both are defects that
  `tmk-seed` catches, and the second is the specific failure ADR-0043's guards
  exist to prevent.
- **Do not hand-write a `span` or a `source_content_hash` in a seed record.**
  They are computed from the snapshot at render time (ADR-0045). If a surface
  will not locate, the surface was retyped rather than copied — fix the surface.
- **Do not maintain a seed file after its record type has been reviewed.**
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
- **Do not relax the harness's cross-reference check to look in `review/seed/`.**
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
- **Do not write a `skos:definition`.** Anywhere. The approved concept records
  carry definition *sources* and no definition text, so the graph carries sources
  and no text. The absence is the honest report and `tmk-ontology-report` counts
  it.
- **Do not type a concept into `GroundOfRefusal`, `LegalTest`, `RelevantFactor`
  or `Exception`.** The classes are empty on purpose. Which one a concept belongs
  in is a legal judgement (ADR-0056 consequence 4), and a machine-filled taxonomy
  reads as authoritative and was authored by nobody.
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
  by editing the question. Both records are approved, neither is obviously wrong,
  and it is an expert's call (Q-37).
- **Do not assert `tmk-recon`'s counts against the graph's.** Recon is s 43-scoped
  and held-instrument-scoped; the graph is neither. Both are right and they do not
  match (Q-38).
- **Do not build a retrieval layer or a search index to close the six deferred
  competency questions.** They are deferred because Stages 7 and 8 do not exist,
  and a query that returned rows for them would measure the wrong thing while
  looking like coverage.
- **Do not add LegalRuleML.** ADR-0009.

## 5. Session log

Newest first. One short entry per session: what changed, what it cost, what it
revealed. Keep entries to a few lines — detail belongs in ADRs and QUIRKS.

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

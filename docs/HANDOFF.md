# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-09-02 · session S008 · branch `claude/ontology-stage-0-loop-s7sruh`

---

## 1. Where the project actually is

**Stage 0 has approved content, and it nearly doubled on the day it arrived.**
The seed workbook came back from the Trade Mark expert, went through the loop,
and **190 records are now in `eval/gold/`** carrying a name and a date:

| file | records | target (guide §7) |
|---|---|---|
| `concepts.yaml` | 52 | 50–100 ✅ |
| `entities.yaml` | 55 | 100–300 |
| `relationships.yaml` | 35 | 50–100 |
| `competency-questions.yaml` | 20 | all six categories |
| `prohibited-uses.yaml` | 11 | all six kinds — 5 of 6 |
| `retrieval-questions.yaml` | 10 | 20–50 |
| `reasoning-expected.yaml` | 6 | at least 1 ✅ |
| `search-questions.yaml` | 1 | 20–50 |

`tmk-harness` reports **0 defects, 12 gaps, 10 notes — exit 3**, which is the
designed state: sound, and incomplete. Read that pair carefully, because it is
the whole status report. *0 defects* means every ref resolves, every span lands
on its recorded text, every hash matches the pin and nothing points at nothing.
*12 gaps* means four record types are still short of the roadmap's targets and
neither the scope document nor the measures exists.

```bash
pip install -e ".[test,intake]"
tmk-fetch-upstream    # pinned snapshot into data/upstream/ (~4s)
tmk-harness           # 0 defects, 12 gaps. Exit 3
tmk-coverage          # the same, as a worklist → data/derived/reports/
tmk-seed              # the 178 seed records that are left. Exit 0
pytest -q             # 287 pass
```

**The loop the last session promised did not work, and fixing it was the
session.** Run as it stood, `tmk-transcribe --write` would have done the reverse
of its job. Two faults, compounding:

- `approved_date` arrived as `25/08/2026` and as Excel date cells; both fail the
  schema's ISO pattern. So every row the expert had **signed** was rejected —
  only a signed row carries a date — and the 233 rows that would have been
  written were exactly the ones nobody had approved (Q-26, ADR-0047).
- The transcriber read `verdict` as an annotation and dropped it. A record the
  expert had just **rejected** would have gone into approved space (ADR-0048).

Both fixed. Dates convert where they have one reading and are refused by name
where they do not. The verdict is the gate: a row crosses only on a `correct`
carrying a name in `approved_by`, and the gate is **transitive** — a signed
record naming an unsigned one is held, because `eval/gold/` with a dangling
pointer is not a measurement standard (Q-27).

**`tmk-reconcile` is new and is the other half of the door.** It writes the
round into `review/decisions/` — every verdict and every correction verbatim —
and then retires the seed copies of whatever reached `eval/gold/`, so no record
is ever present twice (ADR-0049). `review/seed/` went from 368 records to 178.

**Then the reviewer settled two things in words**, and that is why the number is
190 rather than 108. They confirmed that every row they marked `correct` and
left unsigned is approved by **TC**, and that the one cell reading `corrrect`
means `correct` (ADR-0052). A returned workbook is never edited (ADR-0050), so
the instruction is filed as its own artefact —
`review/returned/260902-expert-confirmation.yaml` — and applied by
`--addendum` under two narrow operations: sign a **blank** `approved_by` on a
`correct` row, and settle a verdict on a **named** record (ADR-0051). 84 rows
were touched; each is printed by the tool and marked *by instruction* in the
ledger.

**The round in numbers.** 229 of 368 rows carried a verdict. 190 approved, 170
held, 8 rejected. The held rows sort into reasons a person can act on:

| held because | rows |
|---|---|
| never reached | 139 |
| approved, but names a record that is not | 20 |
| marked `amend`, amendment not applied | 8 |
| rejected by the reviewer | 8 |
| a child row is unsettled | 3 |

**The expert also sent a covering note**, filed verbatim at
`review/returned/260826-expert-feedback.md`. Two points, both about content and
neither answerable by an agent: the seed set has the *presumption of
registrability* and "doubt" in it but not the office's actual bar for applying
it (Q16), and the vocabulary was drawn from Part 29 alone, which gives a
too-narrow view of nine named roles and office terms (Q17, Q-28).

## 2. The next action

**Thread B — the experts. Six records now hold twenty.** The signature backlog
is gone; what is left is small and specific:

1. **`CQ-0013` and `CQ-0014` were never reviewed.** They hold `PU-0010` and
   `PU-0011`, which hold `GA-0015`, `GA-0017`, `GX-0003`, `GX-0007` and
   `GX-0008`. `PU-0010`–`PU-0012` are also the only `stale_source` prohibitions,
   which is the one kind the gold set is still missing entirely.
2. **`GA-0002` needs its amendment applied** — the expert wrote what is wrong
   with it, the record has not been changed to match. It holds `PU-0013` and
   `PU-0014`, and through them `GA-0006`, `GA-0014`, `GA-0019`, `GA-0020` and
   `GA-0022`.
3. **Three records point at rejected records and cannot go in as they stand:**
   `PU-0012` names `CQ-0016`; `GA-0016` and `GA-0021` name `PU-0016`/`PU-0017`;
   `GX-0002` names `PU-0017`. Each needs its pointer changed or the record
   withdrawn. Expert call, not an agent's.
4. **The remaining 139 unreviewed rows**, of which 91 are entities — the record
   type furthest from its target (55 of 100–300).

The three from earlier still stand and still beat record review per hour:
`review/seed/pilot-scope.seed.md` (the boundary, Q8),
`review/seed/measures.seed.md` (the thresholds), and the nine definitions the
expert asked for in their note.

**Thread C — agents. Maintenance.** What is legitimately left:

0. **Run the loop when the next workbook arrives.** Three commands:
   `tmk-transcribe FILE --write`, `tmk-reconcile FILE --write`, then
   `tmk-harness` and `tmk-coverage`. File the returned workbook in
   `review/returned/` first and never edit it (ADR-0050). If a decision arrives
   as words rather than as cells, write an addendum — do not edit a workbook,
   and do not generate one (ADR-0051).
1. **One verdict cell is still misspelt** — `rejext` on a `GS--relevant` row.
   Nothing infers what it meant, and nobody has ruled on it. It holds nothing:
   its parent `GS-0007` is unreviewed anyway.
2. **Report the state honestly.** `tmk-coverage` is the answer to "what is
   Stage 0 waiting on", and it is now generated from real content.
3. **Keep the pin current if upstream moves** — bumping it makes every
   `source_content_hash` stale by design (`IDENTIFIERS.md` §5). The harness will
   say so. Do not silently refresh a hash.
4. **Confirm the agent-proposed ADRs** when a human is available (§3, Q12, Q15,
   Q18, Q20).

**Do not** build more apparatus. **Do not** start Stage 2 — no TextRank, YAKE,
KeyBERT or spaCy run, not even "just to see the output" (ADR-0010). The
temptation is sharper than ever now that entities exist in the gold set. 55 of a
target 100–300, over a chunk set that is not yet exhaustively annotated, is not
a recall denominator; a Stage 2 number measured against it would look like a
result and be an artefact of how far the review got.

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
| Q14 | **New, S006.** Owner asked for more plain-language guidance on **constructing the ontology**, beyond what `STAGE-0-INPUT-GUIDE.md` covers (which is scoped to Stage 0 elicitation, not Stage 5 ontology formalisation). Not scoped or drafted yet — needs its own session: who is the audience (the Trade Mark experts already working from the input guide, or a wider group?), and what specifically is unclear in the existing docs. | Nothing yet; would help the experts' ongoing work | S006 |

Agent-proposed ADRs awaiting human confirmation: **0011** (deferred, not
declined — see ADR-0041), **0029, 0030, 0032, 0033, 0035, 0036, 0037**,
**0043's guards** (the decision to seed was the owner's; how it is fenced is
Q15), **0048's first two judgement calls** (Q18; the third is answered by
ADR-0052) and **0051's two-operation limit** (Q20). ADR-0044, ADR-0045,
ADR-0047, ADR-0049 and ADR-0050 are `derived`. **ADR-0052 is `human`.**
(0006, 0012, 0014, 0024, 0026, 0027 confirmed S006 — ADR-0040; 0016 and 0018
confirmed S006 — ADR-0038; 0028 superseded S006 — ADR-0042. ADR-0023,
ADR-0025, ADR-0031 and ADR-0034 are `derived`.)

**No agent work is blocked on a human decision.** Every remaining open question
is expert content (Q8, Q16, Q17, Q19), organisational (Q3, Q7, the who-half of
Q4 — though Q4's who-half is now half-answered: the reviewer signs `TC`), scope
for later (Q6, Q14), or a confirmation that changes nothing structural (Q12,
Q18, Q20, and 0029/0030/0032/0033/0035/0036/0037 within them).

**What is blocked is the gold set, and it is now blocked on six records.**
`CQ-0013`, `CQ-0014`, `CQ-0016`, `GA-0002`, `PU-0016` and `PU-0017` between them
hold 20 records that are otherwise ready (§2). That is the whole critical path.

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
- **Do not build a vector store or search index yet.** Stage 7 is five stages
  away and untestable without Stage 0.
- **Do not add LegalRuleML.** ADR-0009.

## 5. Session log

Newest first. One short entry per session: what changed, what it cost, what it
revealed. Keep entries to a few lines — detail belongs in ADRs and QUIRKS.

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

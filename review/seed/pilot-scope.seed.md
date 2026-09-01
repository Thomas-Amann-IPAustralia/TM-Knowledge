# DRAFT pilot scope — s 43. NOT A DECISION.

> **This is a machine-written draft for you to correct, not a proposal from
> anyone qualified to make one.** It is deliverable 1 of Stage 0
> (`eval/STAGE-0-INPUT-GUIDE.md` §2) and the boundary it describes is a set of
> judgement calls an agent must not make (CLAUDE.md rule 1, ADR-0043).
>
> When you are content with it, it moves to `eval/pilot-scope.md` with your name
> and a date on it. Until then it lives here and counts for nothing — the
> harness reports deliverable 1 as absent, because it is.

**Area:** s 43, *Trade Marks Act 1995*
**Decided by:** «name / role» · **Date:** «YYYY-MM-DD» · **ADR:** 0013

---

## What the numbers say, before any judgement

From `data/derived/reports/recon.md`, against the pinned snapshot. These are
counts of what upstream already records; none of them is a scope proposal.

| Candidate rule | Chunks | Share of corpus | Words |
|---|---:|---:|---:|
| Chunks citing `TMA1995/s43` or a unit beneath it | 67 | 2.7% | 14,114 |
| Pages holding at least one of those | 36 | — | — |
| Those chunks plus every page-mate (the worksheet rule, ADR-0022) | 216 | 8.8% | 40,020 |

The citing chunks sit across thirteen Parts. Part 29 holds 33 of the 67; the
next largest is Part 32A with 10, then Part 20 and Part 22 with 5 each. Nine
other Parts contribute one to three chunks apiece.

Of the 67 edges, 36 were links the Manual's authors wrote themselves and 31 were
read out of prose by upstream. Of those 31, 27 were resolved to the Act by
convention from a bare "section 43" — an inference, not a statement by IP
Australia — and 2 are marked ambiguous and must not be resolved at all (Q-07).

## Why this area

Against the roadmap's five selection criteria. **Each line needs a sentence from
you; what follows is a machine's reading of the corpus, not of the practice.**

- *Important to examiners* — «…»
- *Spread across multiple Manual sections* — 13 Parts cite the provision; the
  substantive treatment is concentrated in Part 29 with subject-matter
  applications in Parts 32A and 32B.
- *Connected to legislation and case law* — 67 provision edges; the Part 29
  material cites some 30 distinct decisions.
- *Contains relationships and exceptions* — the deceased-persons material states
  a general position and the conditions that reverse it; the descriptive-matter
  material states a rule and its inverse.
- *Small enough to be contained* — between 2.7% and 8.8% of the corpus,
  depending on the rule chosen.

## Draft: in scope

- **Provisions:** `TMA1995/s43`, `TMA1995/s33(3)` (the presumption of
  registrability, which Part 29.2.4 applies to this section by name).
- **Manual material:** the whole of Part 29, plus the section 43 material in
  Part 32A (plants) and Part 32B (wines).
- **Sub-topics:** connotation and denotation; deception and confusion;
  descriptions of goods and services; INNs and INN stems; names and images of
  persons, including deceased persons; phonewords; internet domain names and
  radio call signs; geographical references; claims to Indigenous origin;
  European Union geographical indications.
- **Case law:** in scope **as cited authorities only** — citation, party names
  and the Manual's own account of them. No decision text exists anywhere in the
  programme and none can be acquired within this pilot (Q-11, HANDOFF Q6).

## Draft: out of scope, deliberately

**This list matters more than the one above.** It is what stops the pilot
growing quietly, and it is what lets a competency question be marked
`pilot_in_scope: false` and parked rather than argued about.

- **Section 44 and Part 26 — conflict with other signs.** Cited constantly in
  the same breath, and the Manual states expressly that a comparison between
  marks is not section 43's business. Excluding it is what makes CQ-0007 and
  GA-0011 testable.
- **Section 41 and Parts 22 and 23 — capable of distinguishing, and evidence of
  use.** Five Part 22 chunks cite section 43 and the vocabulary overlaps
  heavily. Excluded, with GC-0039's `not_labels` carrying the boundary.
- **Section 42 and Part 30 — scandalous signs and use contrary to law.**
  Neighbouring ground, three citing chunks.
- **Part 31 — prescribed and prohibited signs.** One citing chunk.
- **Opposition, hearings and revocation of acceptance** — Parts 47, 51 and 52,
  five citing chunks between them. Part 29.3.4 discusses what emerges at
  opposition, and that *discussion* is in scope; the procedure is not.
- **Divisional applications** — Part 12, one chunk, which names section 43 in a
  list of grounds and discusses it not at all. It is the clearest case of a
  chunk that the citation rule catches and the topic rule does not.
- **Point-in-time questions.** See below.

## Boundary cases, and how this draft resolves them

Each of these is arguable, and the resolution offered is a machine's guess.

| Case | Draft resolution | Why it is arguable |
|---|---|---|
| Geographical indications | A **sub-topic** within the pilot, not its centre of gravity | ADR-0013 notes GIs as an area of growing discourse. The Part 29 material on them mostly points elsewhere: 29.1.1 sends the reader to Part 32B in a single sentence. Treating GIs as the centre would make Part 32B the pilot. |
| Part 32A and Part 32B | **In**, limited to their section 43 sub-sections | They apply this ground to particular goods. If the pilot is "Part 29", they are out; if it is "the section 43 practice", they are in. |
| Part 20.5 — grounds and the presumption | **In** | Part 29.2.4 depends on it explicitly, so excluding it leaves GC-0007 ungrounded. |
| Ground interaction | **Out**, with one exception | Part 29.8.3 tells examiners to consider a section 41 ground on the same material, and 29.5.4 says the INN endorsement will not answer a section 41 or 44 ground. Both are *in scope as statements about section 43's limits*; the other grounds themselves are not. |
| The INN stem annex | **Out** | Twenty-odd chunks of bare word fragments with no sentences. GS-0007 treats them as tempting wrong answers rather than as answers. |
| Section 114 of the *Trade Marks Act 1905* | **In as a citation, unresolvable by construction** | Part 29.3.1 cites it and the instrument is not held anywhere in the programme (Q-24). It cannot be excluded — the Manual relies on it — and it cannot be resolved. |

## Point-in-time

**Draft: out of scope.**

"What guidance was current on «date»" is only partly answerable. The snapshot
holds current text; there is no corpus-level version stamp, and the amendment log
is the upstream repository's git history (Q-05). Answering properly needs a
full-history clone, which is a different data strategy rather than a different
query.

CQ-0014 is marked `pilot_in_scope: false` on the strength of this line. If the
pilot does promise point-in-time answers, that record becomes in scope and the
snapshot strategy has to change to support it — which is a decision with a cost,
and it belongs here rather than being discovered in Stage 8.

## What this draft does not settle, and cannot

- **Who the approving experts are.** HANDOFF Q4's remaining half. The workbook's
  `approved_by` column is the approval artefact (ADR-0039); whose names go in it
  is not an agent's question.
- **Whether the exclusion list above matches how the office actually divides
  this work.** It was drawn from what the corpus cites, which is a different
  thing from what practitioners treat as one subject.

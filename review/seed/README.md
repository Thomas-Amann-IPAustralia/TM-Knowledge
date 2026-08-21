# review/seed/ — machine-written examples, for correction

**Nothing here is approved. Nothing here is project content.** Every record in
this directory was written by an agent to show a Trade Mark expert what a
Stage 0 record looks like when it is filled in, so that the expert's job becomes
*correcting a draft* rather than *composing from a blank form*.

That inversion is deliberate, it was asked for by the repo owner, and it runs
against the grain of CLAUDE.md rule 1. **ADR-0043** records the decision, the
reasoning and the conditions attached to it. Read that ADR before you change
anything in here.

---

## Why this exists

The Stage 0 record types ask experts to write down judgements that are the tacit
part of their practice: which two terms are near-misses, whether a "may" is
permission or possibility, which passage an answer is wrong without. The experts
advising this project reported that they could not readily *articulate* those
judgements from a blank form — not because they do not know them, but because
knowing them and stating them are different skills.

Recognising a wrong answer is cheap for them. Composing a right one is not.

So this directory holds a large, deliberately fallible draft. The expert reads
it, marks each record *correct*, *amend* or *reject*, and the corrections become
the gold set. What survives that pass carries a human's name on it and is
approved knowledge; what does not, is not.

## What belongs here

Machine-written Stage 0 example records over the s 43 pilot, grounded in the
pinned upstream snapshot, each inside an envelope carrying its provenance and a
review verdict. That is all.

## What must never be here

- A record with `approved_by` or `approved_date` filled in. `tmk-seed` reports
  that as a **defect** and refuses to pass the set. The whole risk of a seed set
  is that it starts to look approved.
- Anything that has been through expert review. Corrected records leave via
  `tmk-transcribe` and land in `eval/gold/`; they do not get updated in place
  here.
- A hand-typed `span` or `source_content_hash`. Both are computed. See below.

## The files

| File | Records | Guide |
|---|---|---|
| `competency-questions.seed.yaml` | 24 | §5.1 |
| `prohibited-uses.seed.yaml` | 18 | §5.8 |
| `concepts.seed.yaml` | 52 | §5.3 |
| `entities.seed.yaml` | 153 | §5.2 |
| `relationships.seed.yaml` | 58 | §5.4 |
| `search-questions.seed.yaml` | 26 | §5.5 |
| `retrieval-questions.seed.yaml` | 22 | §5.6 |
| `reasoning-expected.seed.yaml` | 15 | §5.7 |
| `pilot-scope.seed.md` | a draft boundary, for deliverable 1 | §2 |
| `measures.seed.md` | draft thresholds, for deliverable 5 | §5.9 |
| `HOW-TO-CORRECT.md` | the expert-facing instructions | — |

`§` references are to `eval/STAGE-0-INPUT-GUIDE.md`, which explains each record
type. This directory is that guide's examples section, filled in.

The `.seed.yaml` infix is load-bearing: `goldset.py` reads eight fixed
filenames and treats an unrecognised `.yaml` in `eval/gold/` as an error, so a
seed file misfiled into the gold directory **stops the harness** rather than
being quietly counted (ADR-0032).

## The envelope

Each file is a mapping with `defaults` and `seeds`. The defaults carry the
provenance block once, at the top, where it is the first thing a reader sees;
the loader materialises it onto every envelope, so nothing downstream ever meets
a record whose provenance is implicit (rule 8).

```yaml
- seed_id: SEED-GE-0001          # stable handle; quote this in a correction
  record_type: gold_entity
  why_this_example: >
    What this record is here to demonstrate. Never empty — an example whose
    point nobody wrote down can only be copied, not judged.
  provenance:
    confidence: 0.9              # the agent's own confidence, per record
  locate:
    occurrence: 2                # which mention, where the surface repeats
  record:
    id: GE-0001                  # exactly the shape eval/schemas/ describes
    ...
    approved_by: null            # always null here, and checked
    approved_date: null
```

`review.status` is one of `unreviewed`, `correct`, `amend`, `reject`. A verdict
of `correct` or `amend` without a named expert is a defect: a verdict with
nobody's name on it is not a recorded human decision (rule 4).

**`model` is null on every record, on purpose.** HANDOFF Q3 — which LLM is
agency-approved, and under what data-handling conditions Manual text may be sent
to it — is still open. Stamping a model name into the repository would pre-empt
an organisational decision that has not been made. The `generator` and
`generated_on` fields identify the run; the session log in `docs/HANDOFF.md`
identifies the session. If the agency later requires the model recorded, it can
be added to the provenance block without touching a record.

## Spans are computed, never typed

Every `span` and `source_content_hash` is `null` on disk. `tmk-seed` finds the
recorded `surface` (or `supporting_text`) in the chunk and fills both from the
pinned snapshot. Correct a surface form and the offsets follow it.

Where a surface appears more than once in its chunk, `locate.occurrence` says
which mention is meant. Where it is **missing** on an ambiguous surface, the
tool reports it and stops — it never resolves to the first hit (rule 6).

## Commands

```bash
tmk-seed                    # check the set; exits 1 on a defect
tmk-seed --pack             # → data/derived/seed-review-pack.md
tmk-seed --workbook         # → data/derived/stage0-seed-review.xlsx
```

The pack is the readable version: every record with the passage it rests on
quoted underneath and the span in bold. The workbook is the correctable
version — the intake workbook's own layout, pre-filled, plus `seed_id`,
`verdict` and `correction` columns at the right-hand end.

`stage0-intake.xlsx` stays **empty**. HANDOFF §4's rule against example rows in
the intake workbook has not changed; this is a different file with a different
name and a verdict column on every row (ADR-0044).

## How a record leaves this directory

There is exactly one door, and it is the one that already existed:

```bash
tmk-transcribe data/derived/stage0-seed-review.xlsx --write
```

The corrected workbook, with an expert's name in `approved_by`, goes back
through the transcriber into `eval/gold/`. The transcriber reshapes and never
supplies: a blank judgement field stays blank and is reported. Nothing in this
directory is promoted, copied or moved by any other means.

Once a record type has been through that pass, its seed file has done its job.
Delete it rather than maintaining two versions of the same records — a stale
seed file that disagrees with `eval/gold/` is worse than no seed file.

## Reading a seed record

Never as fact, and never as a proposal from anyone who knows trade marks law.
Some of these records are wrong; a few are wrong in ways that read entirely
plausibly, which is the failure mode the whole set is built to surface. If that
distinction is inconvenient somewhere, the inconvenience is the point.

# review/decisions/ — what was approved, what was not, and why

The audit trail `review/README.md` promised: *"what was approved, by whom, when,
and why the rejections were rejected"*. One file per record type, written by
`tmk-transcribe` from a returned workbook. **Nothing here is approved
knowledge.** Approved records live in `eval/gold/`, and the two never share a
file or a directory (CLAUDE.md rule 4, ADR-0007).

## Why this directory has content when `eval/gold/` is mostly empty

The workbook that came back on 2026-08-25 is a **seed pack**, not a form. It
held 368 machine-written example records over s 43, handed to a Trade Marks
examiner for correction on the reasoning that correcting a wrong answer is
cheaper than composing a right one from a blank page. That is a sound way to
spend expert time and it creates one hazard: a filled-in seed pack is
indistinguishable from an authored one by inspection. The records validate, the
refs resolve, the spans land on their recorded text, the hashes match the
snapshot. None of that says a person read the row.

So the `verdict` column is a gate, not a note. A row reaches `eval/gold/` only
when the expert marked it `correct` **and** signed it with `approved_by` and
`approved_date` — the approval artefact of ADR-0039. Of 368 rows, 105 cleared
that bar. The other 263 are here, each with the reason it was held.

## The routing rule (ADR-0043)

| verdict | signed | goes to | because |
|---|---|---|---|
| `correct` | yes | `eval/gold/` | reviewed and approved |
| `correct` | no | here | reviewed is not approved |
| `correct` | yes, but a correction was also written | here | the two disagree; a person settles it |
| `amend` | either | here | the correction is prose, and applying it would be authoring |
| `reject` | either | here | kept as evidence, never as a record |
| blank | either | here | machine writing nobody has read |

A parent record whose child rows (`GS--relevant`, `GX--expected_inferences`) are
not all `correct` is held too, however the parent row itself was marked: the
child sheets carry no `approved_by` of their own, so a disputed entry in the
list means the list is not settled.

## What a row here carries

The verdict, the reason it was held, the expert's `correction` verbatim, and the
**whole seed record** — including on a rejection. A rejection recorded as an id
and nothing else is not evidence of anything. With the record attached it
answers "why is this term not in the vocabulary", and it is the negative example
Stage 10's active learning consumes (`review/README.md`).

`origin: machine_seed` is on every entry, because rule 8 says model output is
labelled wherever it is stored.

## What must not happen here

- **Do not apply a correction.** `"Must, while the usage of the word should
  might be confusing…"` is an expert's sentence, not a field value; reading it
  as `modality: must` is a legal judgement made by whoever does the reading.
  Corrections go back to the expert, in the workbook, and return as a verdict.
- **Do not promote a record by editing YAML.** Approval enters through a
  workbook and `tmk-transcribe`, so that every approved record has a signed row
  behind it in `data/intake/`. A record hand-copied into `eval/gold/` has no
  such row and cannot be traced to anyone.
- **Do not delete a rejection** to tidy the file. Rejections are as valuable as
  approvals.

## Regenerating

Deterministic and idempotent — re-transcribing an unchanged workbook leaves git
clean:

```bash
tmk-transcribe data/intake/2026-08-25-stage0-seed-review.xlsx --write
```

# review/returned/ — what came back from an expert, exactly as it arrived

Inbound artefacts. A workbook a Trade Mark expert marked up, a note they wrote,
a printed pack somebody scanned. They are **inputs**, and they are kept
unmodified so that anything derived from them can be checked against them.

```
260825-ontology-stage-0-seed.xlsx    the seed review workbook, returned marked up
260826-expert-feedback.md            the covering note that came with it
260902-expert-confirmation.yaml      two things the reviewer settled afterwards, in words
```

## Why they are not in `data/derived/`

`data/derived/` holds derivations — things `tmk-*` regenerates from the pinned
snapshot and from `eval/gold/`, committed as a paper trail so the diff shows what
moved (ADR-0042). An artefact a person sent us is the opposite of that: nothing
regenerates it, and a tool run must never overwrite it. Mixing the two makes
"delete `data/derived/` and rebuild" — a thing somebody will eventually do —
destructive (ADR-0050).

## Why they are not in `review/seed/`

`review/seed/` holds what *we* wrote for an expert to correct. This holds what
the expert did with it. `tmk-seed` reads the first directory and would report a
returned workbook as a file it does not recognise.

## What belongs here

Anything a person outside this repo produced and handed back: marked-up
workbooks, annotated packs, written feedback, an email pasted into a file with
its date and sender at the top.

## What does not

Anything a tool wrote (`data/derived/`). Anything an agent wrote for review
(`review/seed/`). Anything approved (`eval/gold/`, `vocab/`, `ontology/`).

## When a decision arrives as words rather than as cells

It happens, and it is not a lesser kind of decision: "everything I marked
correct is signed TC" is a recorded human judgement about a defined set of rows.
It is written up as an **instruction file** here — a YAML addendum naming the
reviewer, the date, who relayed it and the words themselves — and applied with
`tmk-transcribe --addendum` / `tmk-reconcile --addendum` (ADR-0051).

It is the one thing in this directory an agent writes, and it is still an
inbound artefact: what it records is what a person said. It may do exactly two
things — sign a **blank** `approved_by` on a row already marked `correct`, and
settle a verdict on a **named** record. No patterns, no typo tables, no
"sign everything". Every row it touches is printed by the tool and marked *by
instruction* in the ledger.

What it must never be is a rewritten workbook. Filling the cells in and saving a
new `.xlsx` here would put an agent-authored artefact where the expert's own
sits, indistinguishable at a glance — which is exactly what this directory
exists to prevent.

## Do not edit what is in here

Not to fix a typo, not to correct a verdict, not to tidy a date. A returned
artefact is evidence, and the record of what was decided is
`review/decisions/`, which is derived from it and may be regenerated. If a
reviewer typed `corrrect` in a verdict cell, that stays typed — the ledger
reports it as unreadable, and it is settled by the reviewer saying what they
meant, in an instruction file naming that record. Never by an agent deciding
(CLAUDE.md rule 6).

A second pass over the same workbook arrives as a **new file** with its own
date in the name. Never overwrite the first one.

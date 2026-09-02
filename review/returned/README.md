# review/returned/ — what came back from an expert, exactly as it arrived

Inbound artefacts. A workbook a Trade Mark expert marked up, a note they wrote,
a printed pack somebody scanned. They are **inputs**, and they are kept
unmodified so that anything derived from them can be checked against them.

```
260825-ontology-stage-0-seed.xlsx    the seed review workbook, returned marked up
260826-expert-feedback.md            the covering note that came with it
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

## Do not edit what is in here

Not to fix a typo, not to correct a verdict, not to tidy a date. A returned
artefact is evidence, and the record of what was decided is
`review/decisions/`, which is derived from it and may be regenerated. If a
reviewer typed `corrrect` in a verdict cell, that stays typed — the ledger
reports it as unreadable and the fix comes back from the reviewer, because
nobody here may decide what they meant (CLAUDE.md rule 6).

A second pass over the same workbook arrives as a **new file** with its own
date in the name. Never overwrite the first one.

# review/decisions/ — what was approved, rejected or deferred, and why

The audit trail `review/README.md` promises. One pair of files per review round,
named after the artefact it came back on:

```
260825-ontology-stage-0-seed.md      readable — every decision, with the reviewer's own words
260825-ontology-stage-0-seed.yaml    the same, as data
```

Both are written by `tmk-reconcile` from a returned workbook in
`review/returned/`, so both regenerate. Do not hand-edit either: correct the
returned artefact's *successor* — a new marked-up file — and re-run.

## Why this is data and not paperwork

A rejection is the most expensive judgement in a round and the easiest to lose.
Delete the row and it is gone; the same wrong candidate comes back next round
and costs the same hour again. Stage 10 active learning reads this directory:
accepted labels become `EntityRuler` patterns, **rejected ones become negative
examples**, corrected records become training data, and a decision that recurs
becomes a deterministic rule.

The `correction` text matters more than the verdict. "Lacks specific context to
be useful. The words *This Section* are contextually used throughout the manual
to describe different points" is a rule about what may be annotated at all.
Quote it; never paraphrase it into a tidier sentence.

## The states a decision can be in

| outcome | meaning |
|---|---|
| `approved` | signed, and in `eval/gold/`. Its seed copy has been retired |
| `rejected` | the record should not exist. Kept in `review/seed/` carrying the rejection, because other records point at it |
| `held` | read, not approved: unreviewed, awaiting an amendment, marked correct but unsigned, or naming a record that is not approved |
| `unparseable` | the verdict cell holds something that is not one of the three. Nothing was inferred from it |

`held` is not a failure. It is the honest state of a partial round, and the
coverage report turns it into the next ask.

A row marked **by instruction** took its verdict or its signature from an
addendum in `review/returned/` rather than from the reviewer's own cell
(ADR-0051). How a record came to be approved is part of the record of its
approval, so the ledger says so per row and names the instruction file in its
front matter.

## What does not belong here

The returned artefact itself (`review/returned/`). The records
(`review/seed/`, `eval/gold/`). Anything written by hand — if a decision was
made in a meeting rather than on a workbook, write it into `docs/DECISIONS.md`
as an ADR, which is where decisions *about the project* live. This directory is
only for decisions **about records**.

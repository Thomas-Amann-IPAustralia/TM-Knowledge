# data/intake/ — workbooks received back from the experts, exactly as received

The **inputs** to the return leg. `data/derived/` holds what this repo generates
and must stay fully rebuildable from `data/upstream/` plus `src/` (ADR-0042); a
workbook a person filled in is rebuildable from nothing, so it cannot live
there. It lives here, tracked, unaltered, and named by the date it arrived.

```
YYYY-MM-DD-<what-it-is>.xlsx    one received workbook, byte-for-byte as sent
```

## Why it is committed

Every record in `eval/gold/` and every decision in `review/decisions/` is
derived from a file in this directory, and both name their source. If the source
is not in git, the audit trail points at a file that exists only in somebody's
downloads folder, and "who approved GC-0001, and against what text" stops being
answerable. Storing the workbook makes the whole chain re-derivable:

```bash
tmk-transcribe data/intake/2026-08-25-stage0-seed-review.xlsx   # dry run
tmk-transcribe data/intake/2026-08-25-stage0-seed-review.xlsx --write
```

## Rules

- **Never edit a file here.** Not to fix a typo, not to correct a verdict, not
  to add a missing `approved_by`. It is a record of what a person actually sent,
  and correcting it destroys the only evidence of what they actually said. A
  correction comes back as a new workbook with a new date.
- **Never hand-write a file here.** A workbook in this directory is one that
  arrived from outside. One an agent produced belongs in `data/derived/`.
- Re-transcribing an unchanged workbook rewrites nothing, so it is safe to run
  at any time and is the way to check the chain still holds.

## What is here

| File | Arrived | What it is |
|---|---|---|
| `2026-08-25-stage0-seed-review.xlsx` | 2026-08-25 | The s 43 seed review pack: 368 machine-written example records with a Trade Marks examiner's verdict against each. **Not an authored workbook** — every row began as LLM output, and the `verdict` column is what separates the reviewed from the rest. See `review/decisions/README.md` for how it was routed. |

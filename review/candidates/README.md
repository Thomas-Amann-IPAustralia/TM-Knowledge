# review/candidates/ — proposals with a score, before anybody commits to them

A **candidate** is the output of an extraction pass: a term, a passage, a
relationship the corpus appears to support, with the evidence that made the pass
propose it and nothing else. It is not knowledge. Nobody — machine or person —
has said it is right.

`authored/README.md` draws the line this directory sits on:

> **Extraction candidates.** A candidate is a proposal with a score and lands in
> `review/candidates/`. An authored record is a judgement an agent committed to.
> Promoting a candidate to an authored record is itself an act of authorship and
> takes the full envelope (ADR-0083 consequence 3).

## What belongs here

Output of a candidate pass, in YAML, one file per pass:

| file | written by | what it holds |
|---|---|---|
| `concepts.yaml` | `tmk-concepts` | terms the corpus defines or the Manual files passages under, with where and how often |

Every file here is **generated and regenerable**. Delete one and re-run its
command; the same pin produces the same bytes. That is why a candidate file
carries no `authored:` envelope, no `approved_by` and no id from the project's
sequence: none of those would mean anything on a record nobody has committed to,
and an id in particular would be a claim on the shared `GC-`/`GT-` sequence that
a later regeneration might quietly reassign.

## What does not belong here

- **Anything with an authoring envelope.** That is a judgement, and it goes in
  `authored/`.
- **Anything signed.** That is `eval/gold/`.
- **Hand edits.** A candidate you disagree with is not corrected here — the
  correction is an authored record that says something different, or a change to
  the pass that produced it. Editing a generated file makes the next
  regeneration a silent revert.
- **A `GC-`, `GT-` or any other project id.** Candidates are addressed by their
  term and their upstream refs.

## How a candidate becomes knowledge

```
tmk-concepts --write          # the pass: deterministic, no judgement
   ↓  review/candidates/concepts.yaml
an agent reads it, decides, and writes an authored record with an envelope
   ↓  authored/concepts.yaml          review_status: unreviewed
a person reviews the workbook and signs a row
   ↓  tmk-transcribe --write
eval/gold/concepts.yaml                approved_by: a name, on a date
```

Nothing skips a step. In particular, **a high-scoring candidate is not thereby
an authored record**: the score says how much of the candidate a lookup
established, never whether the idea is worth holding or what its labels should
be.

## Reading a candidate anywhere else

Never as knowledge, and never as a count of what the project holds. A report
that says "952 concepts" when 952 is a candidate count has overstated the
repository by about eighteen times. Candidates are counted as candidates,
authored records as authored, signed records as signed — three numbers, never
summed (ADR-0080 consequence 3).

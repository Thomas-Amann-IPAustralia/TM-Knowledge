# review/rulings/ — what the owner decided, transcribed

One file per submission from the dashboard's decision form. Written by
`tmk-ruling`, run by `.github/workflows/ruling.yml` when the owner submits the
issue the form composed for them.

## The split this directory keeps

The **GitHub issue is the artefact** — the owner's own submission, with their
account and GitHub's timestamp on it, and nothing in this repository ever edits
it. The **YAML file is a transcription**, and it names the issue it came from on
its face.

That is the same split `review/returned/` (what a person handed back,
unmodified) and `review/decisions/` (what it was taken to mean) already draw
— ADR-0050. It is why a generated file is allowed here and is not allowed in
`review/returned/`.

## Reading one

```yaml
schema: tmk-ruling/1
received_utc: '2026-09-04T09:12:03Z'
issue: {number: 12, url: …, author: …, title: …}
applied: null            # a session fills this in when it has acted
answers:
  - id: OQ-0001
    question: Are these four groups the right way to sort the 52 legal ideas?
    kind: choice
    value: four_groups_right
    label: Use those four groups — come back to me with the list of 52 to sort
    notes: …
```

The question and the chosen wording are copied in beside the machine value so
the file reads on its own, without anyone having to line it up against a version
of the question queue that has since moved on.

## For a session picking one up

1. Read `review/rulings/` before anything else — a ruling is a `human` decision
   and outranks any `agent-proposed` ADR it touches.
2. Act on it.
3. Record it: a new ADR in `docs/DECISIONS.md` with **authority `human`**,
   quoting the answer and naming the ruling file.
4. Set `applied:` in the ruling file — who acted, when, and what changed.
5. Set the question's `status: answered` in
   `review/questions/open-questions.yaml`.

`applied: null` and "answered" are deliberately two different states. A decision
that has been made and not yet acted on is a real and common condition, and
collapsing the two would hide it.

## What must not happen here

- **Do not hand-edit the answers.** They are a transcription of what a person
  submitted. If a transcription is wrong, the issue is the record — fix
  `tmk-ruling` and re-run it, or ask the owner to submit again.
- **Do not write a ruling file by hand** to record something said in a meeting
  or an email. Words that arrive some other way belong in `review/returned/`,
  under the two-operation rule of ADR-0051.
- **Do not act on a ruling from an account without write access.** The workflow
  refuses to transcribe one, and so should a session reading an issue directly.

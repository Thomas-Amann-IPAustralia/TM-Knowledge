# review/ — candidates awaiting a human decision

Everything the machines propose lands here and stays here until a person
decides. This directory is the boundary that ADR-0007 exists to protect: nothing
moves from `review/` into `vocab/`, `ontology/` or `graph/` without a recorded
decision.

```
review/candidates/terms/          Stage 2 — YAKE keyphrases, new entity proposals
review/candidates/citations/      Stage 2 — unresolved and ambiguous citations
review/candidates/clusters/       Stage 3 — proposed synonym groups and hierarchy edges
review/candidates/relations/      Stage 4 — relationships, propositions, candidate rules
review/decisions/                 the record of what was approved, rejected or deferred
review/returned/                  what a person handed back, unmodified
review/seed/                      Stage 0 — machine-written example records, for expert correction
review/questions/                 what is waiting on a person, in plain language
review/rulings/                   what the owner decided, transcribed from the dashboard
```

Three of those are occupied, and together they are the round trip: `seed/` is
what we sent, `returned/` is what came back, `decisions/` is what it was taken
to mean. Each has its own README.

**The round trip is partial by design, so the queue is a graph rather than a
list.** A round settles some records and not others, and approval does not
distribute over an interlinked set (ADR-0048): a signed record naming an unsigned
one is held too. `tmk-blockers` reads all three directories and reports who is
waiting on whom, which decision releases the most, and which records need no
decision at all — `data/derived/reports/blockers.md` (ADR-0053). Read it before
assembling a round; `tmk-seed --only` renders one scoped to exactly the records
it names (ADR-0055).

`questions/` and `rulings/` are the owner's half of the same round trip, and
they are new in S011. `questions/open-questions.yaml` is the queue the dashboard
renders as a form; a submitted answer becomes a GitHub issue, and
`.github/workflows/ruling.yml` transcribes it into `rulings/` (ADR-0065,
ADR-0066). **A session reads `rulings/` before it does anything else** — a ruling
is a `human` decision and outranks any `agent-proposed` ADR it touches. The issue
is the artefact and the file is the transcription, exactly as with `returned/`
and `decisions/`.

`seed/` is unusual enough to have its own ADR: it holds candidate **legal
content**, written by an agent so that an expert can correct it rather than
compose it from a blank form (ADR-0043).
Read `seed/README.md` before touching it. The rules that keep it safe are the
ones this directory exists for — quarantine, an envelope on every record, a
null `approved_by` that is checked, and exactly one door out.

## What belongs here

Any machine output that is not Tier 1, plus every Tier 3 output regardless of
confidence (ADR-0008). Each candidate carries method, model and version,
confidence, the exact supporting span, the source `content_hash`, and
`review_status`.

Upstream's own review-queue material belongs here too — in particular the
`certainty: "ambiguous"` provision edges, which upstream deliberately declined to
resolve and which must not be auto-resolved here either (Q-07).

## What does not

Approved knowledge. Anything an agent decided was "obviously fine". Records
without a supporting span.

## Decisions are data

`review/decisions/` is the audit trail: what was approved, by whom, when, and why
the rejections were rejected. It is not paperwork — Stage 10 active learning
consumes it. Accepted entity labels become `EntityRuler` patterns, rejected terms
become negative examples, corrected relationships become training data, and
recurring decisions become deterministic rules. A decision recorded only in a
person's memory cannot do any of that.

Rejections are as valuable as approvals; keep them.

## Reading a candidate

Never as fact. A candidate in a prompt, a report or an evidence package must be
labelled as unapproved. If that distinction is inconvenient somewhere, the
inconvenience is the point.

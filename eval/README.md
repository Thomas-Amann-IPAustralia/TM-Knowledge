# eval/ — the evaluation set and harness

**Roadmap Stage 0, then run continuously.** This is the current blocker on the
whole programme (ADR-0010) and the most valuable use of expert time in it.

Every automated component in Stages 2–10 is justified by a measurement taken
here. Without this, the first plausible-looking extraction output becomes the de
facto standard purely because it arrived first.

## Contents

| Path | What it is | Status |
|---|---|---|
| `pilot-scope.md` | The bounded examination area the pilot covers, and what is out | not started — HANDOFF Q1 |
| `competency-questions.md` | Ordinary questions the finished system must answer | not started |
| `gold/` | The expert-created trusted examples | not started |
| `prohibited-uses.md` | Conclusions the system must **not** produce | not started |
| `measures.md` | Which metric applies to which component, and the pass thresholds | not started |
| `templates/` | Record shapes for the above | present |

Target sizes, from the roadmap: 100–300 recognised entities, 50–100 approved
concepts, 50–100 known relationships, 20–50 search questions, 20–50 AI retrieval
questions, expected reasoning results, and examples of prohibited conclusions.

## Who writes what

**Experts own the content.** Competency questions, gold answers, concept
approvals, relationship judgements and the prohibited-use list are legal
judgements. An agent must not author them (CLAUDE.md rule 1).

**Agents own the container.** Templates, schemas, loaders, the harness, internal
consistency checks, coverage reports, and prompting the expert for what is
missing. An agent may also *draft the questions' structure* — "we need a question
covering point-in-time currency" — without writing the legal substance of an
answer.

## Metrics

From roadmap §5. `measures.md` will fix the thresholds; these are the dimensions:

- **Extraction** — entity precision/recall/F1, citation-resolution accuracy,
  relation precision/recall, synonym-clustering accuracy, share of records
  requiring review, expert rejection rate.
- **Search** — Recall@10, Precision@10, MRR, nDCG, retrieval via *alternative*
  terminology, retrieval of current rather than superseded material.
- **AI retrieval** — expected source coverage, precision, noise in the evidence
  package, citation correctness, grounding, authority weighting, currency.
- **Reasoning** — expected inferences produced, **prohibited inferences produced**,
  consistency-check accuracy, impact-analysis coverage, explanation completeness,
  expert agreement.
- **Operational** — passages processed automatically, expert minutes per 100
  passages, share accepted without intervention, cost, time from source change to
  publication.

## Known constraints on question design

- **Point-in-time questions are only partly answerable.** A snapshot holds current
  text; the amendment log is the upstream repo's git history (Q-05). Decide during
  Stage 0 whether "what guidance was current on date X" is in scope, rather than
  discovering the limitation in Stage 8.
- **Case questions stop at the citation.** No decision text exists anywhere in the
  programme (Q-11). "Which cases interpret this test" is answerable; "what did the
  court hold" is not.
- **Ambiguous provision edges are not resolvable** and must not be treated as
  errors in a gold set (Q-07).

## The harness

Lives here plus `tests/`. It should be runnable, and **failing**, before any
Stage 2 work begins — a red harness is the intended first output of this repo
(ADR-0010).

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
| `STAGE-0-INPUT-GUIDE.md` | **Expert-facing.** What the owner must supply, in what shape, with worked shape-only examples and elicitation prompts | present |

`STAGE-0-INPUT-GUIDE.md` is the human companion to this file. Point the repo
owner at it rather than at the templates — it explains the templates, the order
of work, the two-pass split (what needs the snapshot open and what does not),
and the definition of done. Keep the two in step: a change to a template or a
target is a change to that guide.

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
  requiring review, expert rejection rate. Entity figures need a **per-method**
  breakdown plus union and intersection: ADR-0019 runs three keyphrase
  extractors, and without per-method numbers there is no evidence for weighting
  the ensemble or retiring an extractor that is not earning its place.
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

Note how it fails, because the obvious implementation gets it wrong. With no
gold records, every mechanical check iterates an empty collection and passes
**vacuously** — green for the worst possible reason. The redness has to come
from an explicit **completeness gate** that fails while any Stage 0 deliverable
is absent or under its target band, and names what is missing. That gate is a
reported state; a malformed record, an unresolvable ref or a span that does not
land on its recorded text is a genuine build failure. ADR-0018.

## While Stage 0 content is pending

`docs/roadmap/PARALLEL-TRACK-ROADMAP.md` (ADR-0016) lists the agent-side work
that needs no expert content — schemas, harness, loader, worksheet, intake path
— and the five gates at which expert input actually becomes required. Four of
its packages exist specifically to reduce how much expert time Stage 0 costs.

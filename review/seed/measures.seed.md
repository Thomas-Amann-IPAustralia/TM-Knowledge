# DRAFT evaluation measures — NOT A DECISION.

> **Every number in this file was invented by a machine and none of them is a
> measurement.** Thresholds encode risk appetite, not statistics: what score is
> good enough to let an examiner rely on something without checking the source,
> and what score means stop. That is an organisational judgement
> (`eval/STAGE-0-INPUT-GUIDE.md` §5.9, ADR-0043).
>
> Correct the numbers. When you are content with them, this moves to
> `eval/measures.md` with your name and a date on it. Until then the harness
> reports deliverable 5 as absent, because it is.

The metric dimensions come from roadmap §5 and are already fixed; what is
missing is the number against each. Three kinds, and the kind matters more than
the number.

---

## 1. Zero-tolerance

Not negotiable by measurement. A single occurrence is a failure, and no
accuracy figure anywhere else compensates.

| Metric | Draft threshold | Note |
|---|---|---|
| Prohibited inferences produced | **0** | Every record in `prohibited-uses.seed.yaml` becomes a test with this threshold. |
| Fabricated citations | **0** | Fully mechanical: every emitted case citation must appear in the corpus's case set (PU-0015). |
| Ambiguous citations silently resolved | **0** | Upstream refused to choose; nothing downstream may (Q-07, PU-0016). |

**The question for you:** is that all three, or are some of these operational
rather than absolute? A threshold of zero on a metric nobody can hold at zero
trains everyone to ignore the report.

## 2. Legally loaded

High, and each needs a sentence of justification rather than a number alone.

| Metric | Draft threshold | Draft justification — replace this |
|---|---|---|
| Citation correctness | ≥ 0.99 | A wrong citation sends an examiner to the wrong passage and is not visibly wrong. |
| Authority distinction (law vs practice) | ≥ 0.99 | Presenting Manual practice as statutory requirement is wrong in a way that matters legally, not just structurally (Q-12). |
| Currency — no unqualified claim of current practice | ≥ 0.98 | The snapshot is a point-in-time capture and says nothing about what has changed since (Q-05). |
| Grounding — every assertion traceable to a span | ≥ 0.98 | An assertion with no span is not checkable, and unverifiable output is worse than absent output. |
| Expected source coverage on retrieval questions | ≥ 0.95 | A `required_evidence` ref is one the answer is wrong without, by definition. |

**The question for you:** 0.99 means one error in a hundred. Over a year of
examination volume, is that acceptable, or does anything in this table need to
be in section 1?

## 3. Operational

Business calls about how much review time the agency will fund. These are the
numbers most likely to be badly wrong here, because nothing in the corpus
informs them.

| Metric | Draft threshold | What it is really asking |
|---|---|---|
| Recall@10 (search) | ≥ 0.85 | How often the right passage is in the first ten results. |
| Precision@10 (search) | ≥ 0.60 | How much noise an examiner will tolerate around a correct hit. |
| MRR | ≥ 0.70 | How often the right passage is at or near the top. |
| nDCG@10 | ≥ 0.75 | Whether the ranking respects the relevance grades. |
| Entity precision / recall / F1 | ≥ 0.85 / ≥ 0.80 / ≥ 0.82 | Measured per method as well as in union and intersection (ADR-0019). |
| Relation precision / recall | ≥ 0.80 / ≥ 0.70 | Tier 3 relations are reviewed regardless of score (ADR-0008). |
| Synonym clustering accuracy | ≥ 0.80 | Measured against `not_labels` as much as against `alt_labels`. |
| Share of candidates accepted without intervention | ≥ 0.60 | The number that decides whether the pipeline saves time at all. |
| Expert minutes per 100 passages | ≤ 45 | If review costs more than annotation, automation is not paying. |
| Time from source change to publication | ≤ 5 working days | Stage 10's whole justification. |

**The question for you:** the last three are the ones the programme's value case
rests on, and they are the three a machine has no basis for at all.

## 4. What is not measured, and should be

Named here because an absent metric is invisible in a report that only lists
what it measured.

- **Whether an answer's qualifications are present.** `qualifications_expected`
  is a list of things whose absence makes an answer wrong, and no standard
  metric captures it. It probably needs a rate of its own with a high threshold.
- **Whether a rejection was right.** The gold set measures what the system
  produces. It does not measure what an expert rejected and why, and
  `review/decisions/` is where that would live.
- **Cost.** Roadmap §5 names it; nothing in this repo has any basis for a
  number.

## 5. A framing that may help

For each threshold above, the question the guide suggests: *what would you have
to see before you let an examiner rely on this without checking the source?*

If the answer is "I would always check the source", that is a legitimate answer
and it changes the design rather than the number — it means the system is a
retrieval aid and not an answering system, and several of the metrics above stop
mattering.

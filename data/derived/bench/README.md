# data/derived/bench/ — the value measurement's test set and results (D3)

`needs.yaml` — benchmark questions a model wrote from sampled passages.
`pools.yaml` — each question's top ten from the three search systems, fixed
before any grading; the judge grades exactly these pools.
`judgements.yaml` — relevance grades (0–3) per question.
`results.json` — per-question scores and the summary `data/derived/reports/measure.md`
renders. `answers.yaml` — "Ask the Manual" answers with verified citations.
All machine-written and unreviewed.

**Kept apart from `eval/gold/` on purpose**: the 190 signed records stay frozen
as the one independent yardstick (ADR-0080), and the expert's 10 signed retrieval
questions are run alongside these as a cross-check, not merged into them.

Not here: anything a person signed, and any record that states an examination
outcome — the answer job declines that part of a question.

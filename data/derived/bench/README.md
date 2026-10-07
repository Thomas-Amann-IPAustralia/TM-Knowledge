# data/derived/bench/ — the value measurement's test set and results (D3)

`needs.yaml` — benchmark questions a model wrote from sampled passages.
`judgements.yaml` — relevance grades per question. `answers.yaml` — "Ask the
Manual" answers with verified citations. All machine-written and unreviewed.
**Kept apart from `eval/gold/` on purpose**: the 190 signed records stay frozen
as the one independent yardstick (ADR-0080), and the expert's 10 signed retrieval
questions are run alongside these as a cross-check, not merged into them.

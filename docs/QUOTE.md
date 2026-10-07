# Quote — what the model work costs, and what each spend buys

Generated 2026-10-07 by `tmk-bulk quote` from measured smoke runs. **Spent so far: $0.181 of the $1.00 cap** (ADR-0111). Each line is a measured cost per call × the number of calls the full run makes, + 25% for retries, re-asks and one prompt fix. Prices are OpenAI's on 2026-10-07; the knowledge model runs on the **flex** tier, which is half the standard price on the same endpoint.

## The recommended package: **$6.41** (flex) · $12.52 at standard prices

| # | Spend | What you get | Model | Calls | Per call (measured) | Full run |
|---|---|---|---|---|---|---|
| 1 | `define` | Up to 46 new concepts — each with its group, the passage that defines it, its legislative basis, its reasoning and what an expert should check — for the 46 defined terms the Manual uses at least 3 times that no concept covers yet | `gpt-6.1-sol` | 46 | $0.004 — 2 measured, ~1,868 tokens in, 413 out | **$0.253** |
| 2 | `relate` | Typed relationships between concepts the Manual mentions together, each resting on a quoted sentence; about five per call. **This is what joins the graph:** today it is 44 separate pieces, the largest holding 86 of 254 nodes; if only half the candidate pairs hold up it becomes 3, with 246 in one. Counted over the ~176 concepts there will be after the line above | `gpt-6.1-sol` | 170 | $0.012 — 3 measured, ~4,231 tokens in, 1,316 out | **$2.52** |
| 3 | `aliases` | The everyday words people use for each concept ("oppose", "brand name"), so search meets plain-language questions | `gpt-6.1-sol` | 15 | $0.006 — 1 measured, ~1,081 tokens in, 1,008 out | **$0.120** |
| 4 | `needs` | 120 realistic benchmark questions in four kinds, written by a *different* model from the one that writes the everyday words, so the test cannot flatter the ontology | `gpt-5.4-mini` | 30 | $0.008 — 1 measured, ~1,427 tokens in, 1,510 out | **$0.295** |
| 5 | `judge` | Relevance grades (0–3) for ~30 passages per question, for all 130 questions — what turns search results into a score. On the expert's question it agreed with both of the expert's required passages | `gpt-6.1-sol` | 130 | $0.009 — 1 measured, ~3,508 tokens in, 389 out | **$1.54** |
| 6 | `answer` | A cited "Ask the Manual" answer for each of the 130 questions, shown on the demo page beside plain search | `gpt-6.1-sol` | 130 | $0.010 — 1 measured, ~5,176 tokens in, 762 out | **$1.67** |
| 7 | `embed` | Vectors for every Manual passage, so search finds meaning as well as words | `text-embedding-3-small` | 1 pass, ~466,702 tokens | measured on a probe | **$0.009** |

**Cheaper variant:** answers for 30 hand-picked demo questions instead of all of them saves $1.28.

## Alternatives priced but not recommended

| Spend | Why not | Model | Full run |
|---|---|---|---|
| `needs` | The same questions written by the knowledge model instead — cheaper, but it shares a voice with the everyday words it is testing | `gpt-6.1-sol` | $0.155 |
| `judge` | The same grades from the smaller model — it agreed with the expert too, but reasoned at length and cost more per question | `gpt-5.4-mini` | $5.53 |

## What the smoke runs showed

- **Relationships:** 15 judgements over 3 calls; every accepted one rests on a quote found verbatim in the Manual. 0 said "no relationship" and 0 fell back to a generic link, so the model may over-relate — the first thing to sample after the full run.
- **Judging:** pools averaged 20 passages; the full run assumes 30, and the per-call cost above is scaled to that.
- **Answers:** careful and honest — Manual practice and the Act kept apart, no outcome stated — but retrieval missed the expert's key passages for the one question asked. That is what the relationships, everyday words and vectors are for, and what the measurement will show.
- **Prompts were fixed before quoting:** v2 of the everyday-words prompt asks for short phrases (v1 wrote sentences search could not match); v2 of the question prompt stops the search wording copying the source passage (v1 would have flattered keyword search).

- **Of the $0.181 spent, $0.049 is four calls the session proxy cut off before they answered** (QUIRKS Q-66). They are booked as billed in case OpenAI finished them; long calls now run in background mode, which avoids it.

## Not in the price

- A *prompt* change re-asks every item in that step, at the price above; repeating an unchanged run is free (the cache).
- Session time. A model call is the only thing the quote counts.
- Live questions during the pitch: about $0.010 each, the measured cost of one answer.

The per-call measurements, refusals and outputs behind every line are in `data/derived/reports/bulk-<job>.md` and the cache in `data/llm/cache/`.

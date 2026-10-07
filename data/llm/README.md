# data/llm/ — every paid model response, cached and committed

`cache/<job>/<prompt version>/<key>.json`, one file per call, written by
`tm_knowledge.bulk.client` and nothing else (ADR-0111). Committed on purpose: a
re-run with the same inputs is free, a fresh clone can rebuild every record
without paying again, and **the cache is the spend ledger** — `tmk-bulk spend`
sums `cost_usd` across it and the cap is checked against that sum.

Each entry holds the job, the prompt version, the item, the model requested and
the model the API reported, the effort, the tier, the usage, the cost, and the
response text. It holds a hash of the request, not the request: the prompt is
rebuilt from code and the pinned snapshot, so the hash proves which one was sent.

**Never edit or delete an entry.** A wrong answer is fixed by a new prompt
version, which is a new key; the old entry stays, because it was paid for and
the ledger must keep counting it.

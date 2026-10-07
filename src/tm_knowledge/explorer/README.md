# tm_knowledge.explorer — the data behind the examiner explorer

`tmk-explorer --write` builds `site/data/` from the two knowledge stores, the benchmark
files in `data/derived/bench/` and the pinned upstream snapshot (ADR-0117). It writes no
knowledge: it copies records with their provenance and computes arrangements — counts,
kind-to-kind roll-ups, what rests on each page, the browser's search index.

What belongs here: building the explorer's JSON, and nothing the workbench
(`tm_knowledge.dashboard`) or the pipeline (`tm_knowledge.bulk`) already owns. The
answer prompt is read from `bulk.jobs`, never restated; the search patterns from
`bulk.links`; the rankings' constants from `search.index`.

What must not: write into the stores or the snapshot, fill `approved_by`, or put a key in
any file but `site/data/live.json` — which is git-ignored and only written when
`TMK_LIVE_OPENAI_KEY` (or `TMK_LIVE_ENDPOINT`) is set, as the Pages workflow does from its
secret (ADR-0118).

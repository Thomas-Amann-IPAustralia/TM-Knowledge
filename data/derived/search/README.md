# data/derived/search/ — what ontology-enhanced search reads

- `aliases.yaml` — how people who are not trade marks specialists refer to each
  concept, written by a model so search can meet plain-language questions. Every
  entry is stamped with its model, date, `general_knowledge` and `unreviewed`.
  **Search aids, never legal content** — nothing here is shown as a definition.
- `passages.npy` / `passages.json` — a 512-dimension vector for every Manual
  passage (`text-embedding-3-small`), float16, with the passage ref and its
  `content_hash`. A vector is re-made only when the passage's hash changes.
- `queries.npy` / `queries.json` — the same for every benchmark question, keyed
  by a hash of the question text.

**The vectors are not committed** (`.gitignore`: embeddings are rebuildable).
`tmk-bulk embed --confirm` rebuilds both for about a cent. What they produced is
committed: the pooled rankings in `data/derived/bench/pools.yaml` and the answers.

Written by `tmk-bulk embed` and `tmk-bulk run aliases`; read by `search.index`.

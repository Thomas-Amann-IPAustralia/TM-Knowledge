# HANDOFF

**Last updated:** 2026-10-07 · S023 · branch `claude/compassionate-pasteur-19firi`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

- **The project is a pitch** (ADR-0109). Current scope is the demonstrator, D1–D4
  in `CLAUDE.md` §0. The owner adopted `docs/PITCH-PROPOSAL.md` in full, with
  OpenAI's `gpt-6.1-sol` at medium effort for knowledge work instead of Gemini
  (ADR-0110, ADR-0111).
- **Spend is capped at US$1 until the owner approves `docs/QUOTE.md`.** Recorded:
  **$0.181**, of which $0.049 is four calls the proxy cut off, booked as billed
  (Q-66). `tmk-bulk spend` is the live figure.
- **The pipeline exists** — `src/tm_knowledge/bulk/`, command `tmk-bulk`:
  - `links` — free: 130 concepts name something in 1,640 of 2,460 passages; 523
    candidate pairs in 125 relationship calls.
  - `run JOB` — `define`, `relate`, `aliases` (knowledge, `gpt-6.1-sol`);
    `needs`, `judge`, `answer` (measurement — the model is the owner's choice).
    Dry-run, `--confirm`, `--limit`, committed cache, cap checked per call,
    background mode, flex tier. Code locates every quote; a quote that does not
    land is refused (ADR-0113).
  - `quote` — prices the full runs from measured calls.
- **Search exists, untuned**: keyword (SQLite FTS5) and ontology-expanded, in
  `src/tm_knowledge/search/`.
- **Written from the smoke runs** (all unreviewed): 15 relationships, GR-0059 to
  GR-0073, in `authored/relationships.yaml`; everyday phrasings for 12 concepts in
  `data/derived/search/aliases.yaml`; 4 benchmark questions, 1 judged pool and 1
  answer in `data/derived/bench/`. Harness 0 defects, SHACL 0 defects, 589 tests
  pass, graph rebuilt.
- **The map draws machine-written relationships**, dashed and labelled. Still 44
  pieces: the smoke run's anchors were already in the largest piece.
- **The site rebuilds on deploy**; `site/data/` is not committed (ADR-0112).

## Waiting on the owner

1. **Approve the quote**, all of it or some lines. Recommended package **$6.41** at
   flex prices ($12.52 standard). Raising the cap is the owner's word, recorded as
   a ruling and an ADR, then `config.SPEND_CAP_USD`.
2. **Model for measurement work**: questions by `gpt-5.4-mini` (recommended — a
   different voice from the one that writes the everyday phrasings) or
   `gpt-6.1-sol` (cheaper); judging by `gpt-6.1-sol` (recommended — cheaper than
   mini and agreed with the expert on both required passages it was shown).
3. **Answers for all 130 questions or 30 demo questions** (saves $1.28).

## Next actions, once the quote is approved — in this order

1. `tmk-bulk run define --confirm --write` (46 terms the Manual uses 3+ times),
   then `tmk-bulk links --write` so the new labels link.
2. `tmk-bulk run relate --confirm --write`, then `tmk-graph --write --rules`, then
   check the map's piece count (`views.network(...)["counts"]`). Forecast: about 3
   pieces if half the pairs hold. **Sample 20 relationships by hand first** — see
   "what to distrust".
3. `tmk-bulk run aliases --confirm --write` (prompt v2, short phrases).
4. **Embeddings — build before running.** `client.embed` keeps vectors in the JSON
   cache entry: fine for the 5-text probe (150 KB), not for the corpus (~75 MB).
   Write vectors to a binary file keyed by passage, cache only the hash.
5. D3: `needs` (120 questions), then pools from **both** systems (keyword and
   ontology-expanded, plus vectors once built), then `judge`, then nDCG@10 and
   Recall@20 per kind of question with paired bootstrap intervals (KB SOP §7).
   Fix the comparison rule before looking at test numbers.
6. D2: `answer`, then an "Ask the Manual" page — pre-computed answers on the site
   (a static page cannot hold a key); live questions from a local command.
7. D4: the pitch pack.

## What to distrust

- **Over-relating.** 15 of 15 relationship judgements accepted, none "no
  relationship", 9 of 15 `mayGiveRiseTo`. The first three anchors are dense
  section 43 concepts, so it may be real — sample before relying on it.
- **The quote extrapolates from one to three calls per job.** `define`'s
  acceptance (2 of 2) is an upper bound; the judge cost is scaled from a
  17-passage pool to 30.
- **Retrieval missed GA-0001's key passages** (Part 29 §1 and §3). The answer said
  so honestly. Search has had no tuning at all.
- **`answer` never shows the Act's text** when a question names a section — add the
  provision as a passage. **`define` gets "has the meaning given by X" definitions
  without X's text** — the model flagged it; add X.
- `pairs()` keeps each concept's top six partners, so writing relationships
  surfaces the next-best pairs: the relationship job is a pass, not a closure.

## Things a session will trip on

- **Q-65**: the proxy supplies OpenAI credentials; no key is needed in a session.
- **Q-66**: a request held open ~30 s is cut (HTTP 502) and may still be billed —
  the client uses background mode; never call the API directly for long work.
- **The signed retrieval questions are GA-0001, 0003–0005, 0007, 0009–0013.**
  GA-0002 was held at review and is not in `eval/gold/`.
- **Write order matters for cached runs**: judge and answer pools come from search,
  which reads the aliases and authored relationships — write those *after* any
  cached judge/answer you want to replay, or the prompt changes and the cache misses.
- `define`'s two cached outputs (*accredited course of study*, *AFS request*) are
  not written: both terms fall below the job's usage threshold.

## Open items (agent-proposed, provisional)

- ADR-0113 — how the pipeline writes knowledge (SKOS for generic links, aliases as
  search aids, background mode).
- ADR-0112 is `derived`; ADR-0110 and ADR-0111 are `human`.

# HANDOFF

**Last updated:** 2026-10-07 · S024 (end) · branch `claude/affectionate-lamport-8g14rj`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The demonstrator is built (D1–D3 met, D4 drafted), and the published site is now
for trade marks examiners.** Everything machine-written is unreviewed.

- **S024 rebuilt the front end on the owner's instruction** (ADR-0118, ruling
  `review/rulings/2026-10-07-chat-examiner-explorer.yaml`). `site/` is the explorer:
  - `#/` home — the four levels, kinds → ideas → connections → text;
  - `#/tour` — seven steps: text, one idea in many wordings, connections, kinds, the
    text changing, retrieval (a real benchmark question), limits;
  - `#/map/{kinds,ideas,text}` — the ontology at three levels; kinds open into ideas,
    an idea opens into its passages (Manual left, Act/Regs right);
  - `#/ask` — a question's recognised ideas, connections and passages drawn hop by
    hop, plain keyword search beside it, then a cited answer (live, or one of the
    129 prepared ones);
  - `#/change` — every Manual page as a heat map; pick one to see what a rewrite
    touches, layer by layer (kinds: never);
  - `#/about` — what it is, how it works, the measurement both ways, limits.
- **Libraries are allowed (owner, ADR-0119)** and vendored in `site/vendor/` with a
  checksum manifest: Cytoscape.js (the map — kinds are boxes that open and close and
  roll their connections up while closed), D3 (home circle packing; Manual treemap),
  Observable Plot (amendment timeline; measurement intervals), marked + DOMPurify
  (answers), Fuse.js (fuzzy idea search), Inter + Source Serif 4. Loaded per view.
- **Live answers stream**; real event names checked against the API (a few tokens).
- **The old dashboard is at `site/workbench/`** (`/workbench/`), unlinked.
- **Data:** `tmk-explorer --write` (`src/tm_knowledge/explorer/`) builds `site/data/`
  from the stores, the bench files and the **pinned snapshot** (ADR-0117).
- **Browser search = Python search, minus vectors.** `site/js/engine.js` reproduces
  `search.index` keyword and ontology systems; `tests/unit/test_explorer.py` checks
  identical top tens, recognised concepts and paths on all 129 questions and an
  identical answer prompt on 12. Building it found Q-69 (BM25 heading weight).
- **Live answers** need the owner to add the secret (below). The browser path is
  tested with the API mocked; CORS from any origin is confirmed; one real smoke call
  went through `bulk` (job `live-answer`, 20 s, US$0.028, declined the outcome part,
  cited Act and Manual apart).
- **Pages workflow** is one job under the `github-pages` environment: fetch snapshot,
  build workbench, build explorer (with `OPENAI_API_KEY` → masked key in
  `data/live.json`), deploy.
- **Spend: US$3.49 of the $6.60 cap.** Live answers spend the owner's key outside it.
- 611 tests pass (600 before + 11 explorer).

## Waiting on the owner

1. **Add the key** as an environment secret: Settings → Environments → `github-pages`
   → Environment secrets → `OPENAI_API_KEY`. Then Actions → pages → Run workflow.
   Advised: a dedicated OpenAI project, key restricted to the Responses endpoint and
   `gpt-6.1-sol`, with a monthly budget — the key is recoverable from the page.
2. **Merge this branch** to `main` to publish (no PR opened — not asked for).
3. **OQ-0029 — which results the pitch claims.** Unchanged; the About page reports
   both directions and claims nothing.

## Next actions

1. After the first live deploy, ask one question on the published site and read the
   answer; check `data/live.json` is served and the Actions summary says "live chat: on".
2. **An examiner feedback route** is still missing. The workbench's form only accepts
   owners (the ruling workflow refuses non-writers). Something simple — a per-answer
   "wrong / partly / right + note" that composes an email or a downloadable file —
   would turn exploring into testing. Expert notes must never reach a model (ADR-0088).
3. If abuse of the key shows up: a small proxy holding the key (e.g. a Cloudflare
   Worker; set repository variable `TMK_LIVE_ENDPOINT`) — the page already supports it.
4. Carried over from S023: OQ-0029's "test the fix first" option (spec in git history
   of this file, S023); 12 "same concept" merge candidates for a person.

## What to distrust

- **The live configuration was not measured.** Live = keyword + ontology, no vectors;
  the measured "ontology" system also fused vectors. The page says so.
- **Concept recognition is label matching**, now visible to examiners: "register"
  matches *Register of Trade Marks*; everyday phrasings (machine-written) widen it.
- **The kinds view is an arrangement**: kind-to-kind arrows count relationship
  records; the tour's sentence "factors feed tests; tests and factors give rise to
  grounds" reads the top arrows, which are mostly machine-written relationships.
- **The all-open map is dense** when fitted: names appear only as you zoom in, and
  lines between boxes are many. Opening two or three kinds reads best.
- The benchmark is model-written and model-graded (unchanged from S023).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** — the bare one is another interpreter (Q-29).
- **The explorer needs the snapshot**: `tmk-fetch-upstream` first, or
  `tmk-explorer` fails. Its tests skip without it.
- **`engine.js` and `search/index.py` must change together** — the parity test fails
  otherwise. So must `bulk.jobs._answer_render` and `engine.prompt`.
- **`site/data/live.json` can hold a key.** It is git-ignored; keep it that way. The
  build only writes a key when `TMK_LIVE_OPENAI_KEY` is set (not `OPENAI_API_KEY`).
- **The map's positions are computed** (`map.js` `graphPositions`/`textPositions`).
  Do not reach for a force layout: fcose overlapped the compound kind boxes. The
  Cytoscape instance is on `.cy` as `container.cy` for browser checks.
- **Updating a vendored library**: copy the same dist file, then update its `sha256`,
  `bytes` and `version` in `site/vendor/manifest.json` — the test fails otherwise.
- Vectors are not committed (ADR-0115); flex tier overloads (Q-67); never kill a
  relate run (Q-68) — all unchanged.

## Open items (agent-proposed, provisional)

- ADR-0117 (explorer reads the snapshot; browser search without vectors).
- ADR-0118's agent part: environment secret, masking, low effort for live answers,
  40-a-day courtesy limit. ADR-0119's agent part: vendoring, the library choices,
  computed map positions, streaming.
- ADR-0113 and ADR-0115 from S023.

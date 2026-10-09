# HANDOFF

**Last updated:** 2026-10-09 · S027 (end) · branch `claude/ecstatic-cray-shk5k4`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The owner approved and S027 actioned B1, A5, A6, B4, D4, F2, F6 and D5**
(`review/returned/261009-owner-chat-approvals.md`, ruling file
`review/rulings/2026-10-09-chat-approvals.yaml`, ADR-0125 to ADR-0127). Waterfall delivery
still holds: nobody signs anything until the ontology ships to the examiners (ADR-0120).

- **B1 — what a thing is, what it does** (ADR-0126). A concept's kind says what it *is*:
  ten kinds in three families (the law's questions; what they ask about — subject
  matter, sign content, context, use in trade; the process) and `none_of_these`. Factor,
  exception and remedy are edges — `qualifies`/`mayGiveRiseTo`/`statesThresholdFor`,
  `doesNotGiveRiseTo`, `isOvercomeBy` — never kinds. 52 typings re-judged; the decision
  tree, workbench and explorer read functions off edges.
- **B4** — the s 41 ground (GC-0181) and s 39 ground (GC-0182); prohibited and
  prescribed signs are sign content.
- **A5, A6, D4, F2, F6** (ADR-0125) — names compared folded (`ontology.hygiene`);
  implied endorsement and endorsement kept apart (`authored/merge-candidates.yaml`);
  four contradicting "kind of" links withdrawn, and a kind-of beside a not-label refused
  unless `authored/kind-of-affirmed.yaml` says why both hold (11 do); three SHACL shapes
  on folded label keys; a test forbids ranking by confidence across authors.
- **D5 step 1 — the edge audit** (ADR-0127). Gemini 3.1 Pro (batch-only client in
  `bulk.client`) judged all 571 machine-written relationships: **346 sound, 13 vague, 212
  wrong (37%, 95% 33–41%)**; `appliesTo` wrong 55 times in 61. `tmk-bulk audit-apply`:
  69 re-read, 135 withdrawn, 8 kept — four of them serve for the expert's signed s 43
  edges and go to a person, never overruled by a model.
- **D5 step 2 — search re-measured** (ADR-0127, `data/derived/reports/measure.md`), same
  judge, only new passages graded. nDCG@10: ontology − hybrid **−0.041 [−0.067,
  −0.017]**; on the expert's ten questions **+0.030 [+0.008, +0.055]**; ontology −
  keyword +0.079. Since 2026-10-07: +0.010 (not established). **The audit's effect on
  search: +0.001 [−0.007, +0.009] — none.** No model judge, expert's own evidence lists:
  ontology and hybrid tie (ten questions, wide interval).
- **No more intelligent model was used**, and why: the current judge already grades all
  21 passages the expert requires as relevant, so no judge could show a measurable gain;
  one judge keeps the before/after comparable; a Gemini re-grade (~$5) would pass the
  envelope; and the audit itself moved search by nothing (ADR-0127, decision 6).

Counts: concepts 52 signed + 112 authored; relationships 20 signed serving (15 replaced
by corrections) + 436 authored. 158 of 164 concepts in one piece (96%; six isolated:
geographical qualifier, services of a person, wine GI, the GI Register, IP Australia,
office practice). Harness 0 defects; SHACL 0 defects, 0 gaps; graph matches a rebuild.
**Spend US$6.70 of the US$9.49 cap; D5 spent US$3.21 of its US$6.00.**

## Waiting on the owner

1. **OQ-0029 — which results the pitch claims.** Now current: the ontology helps on the
   expert's questions and against keyword search, trails hybrid on the benchmark.
2. **The four disputed signed readings** (`edge-audit.md`, "Disputes of a reading an
   expert signed") — a person's call; nothing changed.
3. **Prepared answers are stale** — written 2026-10-07; 105 relationship ids their
   paths cite are now withdrawn. A re-run of the answer job is ~129 flex calls, about
   US$0.40 by the last run's cost. Not D5's purpose, so quote first.
4. If not done: the key as an environment secret (`github-pages` → `OPENAI_API_KEY`).

## Next actions

1. **Search is where the value is lost, not edge quality.** The audit's precision gain
   moved nDCG by +0.001; the losses are questions where concept-linked passages push
   out hybrid's good hits ("notice to produce" 0.90 → 0.24, "more than one class"
   0.87 → 0.28; `measure.md`, "Where it hurt most"). Look at how `search.index` blends
   them before any more knowledge work — free to try, and re-measuring now costs only
   the new passages. `engine.js` changes with it.
2. Show each relationship's audit verdict on its explorer card ("checked by a second
   model: sound / vague"), and a re-read's first reading — free, from `edges.yaml`.
3. The 27 withdrawn relationships whose correction named a concept the sentence does
   not: corrections kept in `data/derived/audit/edges.yaml`; a relate pass, or labels
   such as "lack of inherent adaptation to distinguish", could restore the right ones.
4. Re-run `tmk-bulk run relate` (v2, 125 calls queued) only with a quote; the audit
   says the relate prompt over-uses `appliesTo` — fix the prompt first.
5. B2, B3, B6 stay postponed; D7, F4, F5 deferred (F5: `ontology.md` report,
   `legal-concepts.ttl` sections beyond B1, `GUIDE.md`).
6. Carried over: an examiner feedback route (notes never reach a model, ADR-0088).

## What to distrust

- **Everything machine-written is unreviewed**: S026's and S027's records
  (`claude-code-agent-S026`, `-S027`), `gpt-6.1-sol`'s, and now 69 re-reads stamped
  `gemini-3.1-pro-preview` with `confidence: null`. The audit is a model judging
  models, not a review.
- **The audit reads sentences literally.** In a 12-verdict sample 2 removals looked
  sound with their passage (GR-0306 expedited examination, GR-0651 acceptance
  officer), and GR-0698 (endorsement as a remedy for the s 43 ground) was re-read as a
  factor. Withdrawals are recoverable from the ledger.
- **GC-0001's signed `narrower: [GC-0045]`** looks wrong (connotation is not broader
  than what it names); untouched — it is signed.
- **GR-0684 and GR-0685 state the same triple**, as corrections of two different
  signed records. Left as is.
- **Hybrid moved on 7 questions when the vectors were rebuilt** (Q-84): compare
  systems only within one run.
- **22 legislative bases are unverified** (harness note) — not wrong, not checked.
- The benchmark is model-written and model-graded; only the ten signed questions and
  their evidence lists are a person's.

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); about eight minutes, 687 tests.
- **Edit record files block by block**, never a YAML round-trip (Q-76).
  `jobs.rewrite_records` does it for code.
- **Gemini ignores its schema** (Q-83); read its answers tolerantly, never change the
  request (the cache key is the request).
- **Vectors are not committed**: `tmk-bulk embed --confirm` costs about a cent each
  time (no vector cache).
- **`tmk-bulk pools --keep-previous`** carries the *current* pools forward as "previous";
  run it once per measurement, or the comparison is with itself.
- **`tmk-graph --check` needs `--rules`** when the graph was written with them.
- **Pass `authored.root` to `corrections.load`** wherever an `AuthoredSet` is in hand (Q-77).
- **`served_gold()` for what serves; `goldset.load()` for what measures.**
- **`engine.js` and `search/index.py` change together**, as do `links.find_mentions`
  and `Recogniser`, and `search.authority` and `authorityFlags`.
- **The explorer needs the snapshot**: `tmk-fetch-upstream`, `tmk-explorer --write`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- Name every node in `ontology/draft/*.ttl` (Q-80); fold labels in the build, not in
  SPARQL (Q-81); a not-label is "not the same concept" (Q-82).

## Open items (agent-proposed, provisional)

- ADR-0127 entire: the apply rules (paraphrase allowance, widening kept, signed
  stand-ins kept), incremental grading, the judge decision.
- ADR-0125's and ADR-0126's agent parts: the affirmation ledger, folded keys, the three
  new kinds' names, the presumption of registrability as `none_of_these`.
- ADR-0122 (corrections); the agent parts of ADR-0120, ADR-0123, ADR-0124.
- Which labels are "too general" (E1); the decision-series table; ADR-0113, ADR-0115,
  ADR-0117, and the agent parts of ADR-0118 and ADR-0119.

# HANDOFF

**Last updated:** 2026-10-08 · S026 (end) · branch `claude/practical-edison-quroky`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The demonstrator is built (D1–D3 met, D4 drafted), the published site is for trade
marks examiners, and everything machine-written is unreviewed.** S025's work — the mini
maps, the Part rows, the tour's squares, "how the ontology chose" — is on `main` (PR 26).

**S026 reviewed the ontology at the owner's request and changed nothing in it.** The
owner had found duplication and miscategorisation and asked for an in-depth review, each
issue with a suggested resolution in a table, with attention to the power structure
between the defined roles. The result is **`docs/ONTOLOGY-REVIEW.md`**: 40 issues in six
groups — A duplication, B the nine groups, C roles and power, D relationships, E labels
and recognition, F the model's own gates and documentation — each with evidence by
record id, a resolution, and who can act (agent, expert or owner). The headline:

1. **13 ideas exist twice**, signed and machine-written: 11 the same idea, GC-0006 /
   GC-0053 a scope split, GC-0050 / GC-0130 a homonym. 40% of relationships hang off one
   side of a pair. The expert-pack check reports 10 (preferred labels only — Q-72).
2. **The vocabulary inverts the delegation chain.** "The Registrar's delegate" is an
   alternative label of the Registrar (GC-0046); the examiner excludes "delegate" and
   "decision maker" (GC-0044) — against s 206, Part 18.2.2.2 and the expert's own held
   corrections GE-0010 / GE-0047. Both signed records were seeded to invite that
   correction and were marked correct. No edge joins examiner and Registrar.
3. **Power is flattened**: 101 of 120 role edges are `related`, including sentences that
   state a power exactly (s 205; the ART "stands in the shoes"). The 14 predicates have
   no word for delegation, review, consent or control — and no definitions at all.
4. **One group per concept from two axes**: duplicates got different groups, siblings
   split, and the presumption of registrability is typed `exception`.
5. **Labels leak**: 21 shared labels; search aliases contradict 19 not-labels; all five
   of *Board*'s passage links are wrong.
6. **`tmk:ManualInstruction` and `tmk:LegalProposition` have no instances**, so two of the
   practice/law shapes guard nothing (Q-74); SHACL passes regardless (0 defects, 300 notes).
7. **A seeded sample of 25 machine-written edges**: 13 sound, 5 too vague, 7 wrong (28%,
   95% interval about 14–48%; judged by one model).

No record, graph, prompt or page changed, so nothing was rebuilt and the tests were not
re-run (no code changed). No paid call. Spend: US$3.49 of the $6.60 cap.

## Waiting on the owner

1. **Which of the review's recommendations to act on.** Its suggested order: (1) hygiene
   an agent can do now without touching a signature; (2) on a go-ahead, the role layer
   and the retirement of the 11 authored duplicates (needs an ADR superseding ADR-0101
   decision 2); (3) owner decisions — two-column typing (OQ-0026), whether an expert's
   note may be cited as evidence (C6), the capacity a signer signs in (C9), who judges
   the edge-precision sample (D5); (4) one short list for the expert.
2. If not already done: **add the key** as an environment secret (Settings →
   Environments → `github-pages` → `OPENAI_API_KEY`), then run the pages workflow.
   Advised: a dedicated, restricted, budget-limited key — it is recoverable from the page.
3. **OQ-0029 — which results the pitch claims.** Unchanged. The review's D5 bears on it:
   claim nothing about edge quality without a judged sample.

## Next actions

1. **On the owner's word, step 1 of the review's order:** A3 (relabel GC-0130 *reputation
   of a trade mark*, re-point GR-0084 / GR-0315), the authored half of A4, A5 (label check
   over every label, folded), B6, C7 (administrative vs judicial decisions), C8
   (longest-match recognition — `links.find_mentions` and `engine.js` together), D4, D6,
   E2, E4, F2, F3, F5. Then `tmk-graph --write --rules`; CI fails on graph drift.
2. **Re-open OQ-0022.** It is marked applied, but the examiner-conduct rule it promised
   ("an agent writes the examiner-conduct rule itself") was never written (review C6).
3. Carried over from S025: an examiner feedback route (per-answer "wrong / partly /
   right + note"; expert notes must never reach a model, ADR-0088); a packing of a
   question's ideas on Ask if the owner meant the home page's circle packing; a small
   proxy for the key if abuse shows up (`TMK_LIVE_ENDPOINT`).

## What to distrust

- **The review is machine-written and unreviewed.** Its D5 figure is one model's
  judgement on 25 edges; every other finding cites record ids and can be checked.
- **`data/derived/links/mentions.json`** covers 130 of 167 concepts (Q-71). Build links
  fresh from the snapshot for any count.
- **The 12 "same concept" merge candidates**: GC-0028 = GC-0014 is wrong (review A6), and
  two real duplicates (*reputation* is a homonym; *conditions or limitations* was linked
  as `broader`) are not among them.
- **The relate prompt's predicate "definitions"** are the first signed example of each,
  and two are inverted (Q-73).
- **The twelve connections in the prompt are an accident of identifier order** (Q-70).
- **Concept recognition is label matching**: "register" matches *Register of Trade
  Marks*, "mark" matches *trade mark*, "Registrar" matches inside "Deputy Registrar".
- **The live configuration was not measured** — keyword + ontology, no vectors.
- **The kinds view is an arrangement**; kind-to-kind arrows count relationship records.
- The benchmark is model-written and model-graded (unchanged from S023).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); install with `pip install -e ".[test,rdf]"`.
- **The explorer and any label analysis need the snapshot**: `tmk-fetch-upstream`, then
  `tmk-explorer --write`, then serve `site/` (e.g. `python3 -m http.server` inside it).
- **`engine.js` and `search/index.py` must change together** — the parity test fails
  otherwise. So must `bulk.jobs._answer_render` and `engine.prompt`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- **The main map's positions are computed** (`map.js`). Do not reach for a force layout
  there: fcose overlapped the compound kind boxes. `minimap.js` uses a seeded D3 force
  run only for Change, where there are no boxes.
- **A `data-ref` attribute opens the passage drawer** (app.js listens on the document).
  The Change page's tiles use `data-page` for that reason.
- **Updating a vendored library**: copy the dist file, then update `sha256`, `bytes`,
  `version` in `site/vendor/manifest.json`.
- **An agent may not edit a signed record.** Every review item marked "Expert" goes to
  the expert pack; the agent's half of a mixed item is the authored side only.
- Vectors are not committed (ADR-0115); flex tier overloads (Q-67); never kill a
  relate run (Q-68).

## Open items (agent-proposed, provisional)

- Every recommendation in `docs/ONTOLOGY-REVIEW.md` is a proposal; none is a decision.
- ADR-0101 (the review recommends superseding decision 2 for identical-label pairs).
- S025's reading of "the Cytoscape map … elsewhere", and the treemap's replacement by
  Part rows — layout calls, recorded in the commits.
- ADR-0117; ADR-0118's and ADR-0119's agent parts; ADR-0113 and ADR-0115.

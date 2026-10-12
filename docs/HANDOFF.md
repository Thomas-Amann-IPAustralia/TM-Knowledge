# HANDOFF

**Last updated:** 2026-10-12 · S034 (end) · branch `claude/keen-clarke-o43tnq`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S034: a typed question now drives the graph the way a prepared one does** (ADR-0132).
The owner's screenshot: "Can I trade mark a smell?" drew only a grey "trade mark" and a fan of
keyword passages. Live answers work. Recognition is by names only, and people do not use
the map's names: 5 of 20 typed questions found a specific idea, against 76 of 129 benchmark
questions. Feeding keyword hits back into recognition, with no model, picked noise.
- **The reading**: before the search, the live model reads the question against the ontology
  map (`jobs._READING_INSTRUCTIONS`, `reading-v1`; published in `chat.json` as `reading`) and
  names up to four ideas, each with its words and a reason. `Engine.reading` keeps a pick only
  if it is on the map, specific, new, and its words are in the question; kept ideas start the
  search exactly as names do (`trace`/`ontology`/`prepare` take `read`, default empty, so the
  measured path and the parity test are unchanged).
- **The page**: the question appears, then a column of faint dots "reading the question…",
  then the hop diagram as before. Read ideas carry a dashed ring and "“smell” · read by the
  model"; "How it chose" explains the reading, lists what it set aside, and says the prepared
  answers used names alone; the footnote gives the reading's share of the cost. A failed
  reading falls back to names and says so. Checked in Chromium with stand-in replies (Q-90).
- **The proxy** counts readings apart from answers (`text.format.name`), output capped at
  2,000. An old proxy still works; it just counts a question twice against its limits.
- **Smoke run on the real model**: 10 questions, US$0.12 (`data/llm/cache/live-reading/`), about
  1.2¢ and 6 s each; 7 of 10 found an idea. **Spent from the cap's remainder without asking**
  (approved for nothing); told the owner.

**S034, after the owner's answers (ADR-0133, CHAT-0074 to 0076):** "read by the model" stands, the
cost per question is approved, and US$1.60 was approved to measure the reading on all 129
benchmark questions. Spent US$1.13 of it (reading US$0.79, judging 551 new passages US$0.33), held
by `TMK_SPEND_CAP_USD`. Measured the page's own configuration (no vectors), report
`data/derived/reports/measure-reading.md`:
- **The reading helps**: nDCG@10 reading − names **+0.040 [+0.009, +0.070]**; +0.051 on the 101
  questions it changed. No pick failed a check.
- **The page's ontology search by names is below plain keyword search**: −0.041 [−0.067, −0.014];
  with the reading it is level (−0.001). Same pattern as the measured system against hybrid.
- New: `tmk-bulk run reading`, `reading-pools`, `run judge --pools`, `measure --reading`;
  `Systems.reading` and `find_words` (Python twins of the page's), parity-tested.
- **Recorded spend US$9.63, above the US$9.49 cap**: every paid call is refused until the owner
  names an amount.

**S033 built `live-proxy/`** (Render, holds the key) and the build publishes no key when
`TMK_LIVE_ENDPOINT` is set. **S031** labelled every line on the map's text level. **S030**
added "As a table". **S029 restructured the ontology** (ADR-0131): three families as classes, 23
predicates, "is related to" retired, `principle` added, 164 of 164 concepts connected. Counts:
52 signed + 112 authored concepts; 20 signed + 352 authored relationships. Harness 0 defects;
SHACL 0 defects.

## Waiting on the owner

1. **Merge this branch** to publish the reading; the Pages workflow rebuilds `chat.json`. If the
   proxy is on Render with auto-deploy, it picks up the separate counting on merge.
2. **OQ-0029 — which results the pitch claims**, now with ADR-0133's two findings: the reading
   helps, and the page's ontology search alone does not beat keyword search on these questions.
3. **Whether to change the page's blend** (next action 1) — a design change, so the owner's to
   order; then it needs re-measuring, which needs an amount (the cap is spent).
4. **Is the restructure what you meant?** (ADR-0131, agent-proposed inside your instruction.)
5. **The four disputed signed readings** (`edge-audit.md`) — a person's call; unchanged.
6. **Proxy deployment** (S033): if not done, `live-proxy/README.md` has the steps; revoke the
   old key once the proxy serves.

## Next actions

1. **The blend**: concept-linked passages crowd out good keyword and vector hits (ADR-0133 c4,
   ADR-0127). Candidates: weight the linked list below keyword, or drop it when the expansion
   already holds the ideas. Any change must be fixed before re-measuring, never tuned on these
   questions; `engine.js` and `search/index.py` change together.
2. **Re-measure search** (`tmk-bulk pools --keep-previous`, judge new passages, `measure`):
   S029 withdrew 96 edges and re-typed 130. Needs a quote.
3. **The prepared answers** (`answers.yaml`) predate S029; their "followed connections" text may
   name `related`. Re-run only with a quote.
4. Ideas the reading could not find: the map has nothing for a personal name or surname, a
   slogan, or how long registration lasts. Candidates for `define`, if the owner wants them.
5. Show each relationship's audit verdict on its explorer card; type the signed `related` lists
   if the owner wants them (77 links).
6. `map.js`'s `showConcept` draws a `CASE/…` ref as a Manual chip; `table.js` draws it grey.
7. Small: live answers off, step 5 of a typed question still says "Wrote an answer…"; and
   "Gathered 0 passages linked to those ideas" reads oddly when nothing was recognised.
8. B2, B3, B6 postponed; F4, F5 deferred.

## What to distrust

- **The reading is a model's judgement per question, unreviewed.** Measured once on model-written
  questions with a model judge (ADR-0133); each question read once. BN-0015's three passages are
  ungraded, scored 0 (the judge's answer was refused); it moves nothing.
- **A live answer is no longer what the measured system would have produced** when the reading
  found an idea: different starting ideas, different passages. The footnote says so.
- **Every S029 judgement is one agent's reading of one sentence**, unreviewed. Weakest:
  GR-0122, GR-0167, GR-0521, GR-0495. `owns` from "owner or authorised user" (GR-0140, GR-0437).
- **The published `site/data/ontology.json` still carries the reviewer's initials** (S028).
- **Neither key is tested by a session** (Q-88); the proxy was tested against a stand-in.
- **22 legislative bases are unverified** (harness note). The benchmark is model-written.

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); install with `pip install -e ".[rdf,test]"`;
  about ten minutes.
- **Test the page after `tmk-explorer --write`**, then restore a stand-in `live.json` (Q-90).
- **`engine.js` and `search/index.py` change together**, as do `links.find_mentions` and
  `Recogniser`, and `search.authority` and `authorityFlags`. The reading (`read`) is the one
  live-only input; leave its default empty.
- **The reading's prompt lives in `bulk/jobs.py`**, its input is built twice
  (`jobs.reading_input`, `live.readingInput`); `test_explorer.py` holds them equal.
- **Re-scoring the reading**: `tmk-bulk measure --reading --allow-ungraded 3 --write` (BN-0015's three
  passages are ungraded); `reading-pools` needs `bench/readings.yaml`, which is spend to rebuild.
- **Off-kind edge? Check the kinds first** (Q-86). **Relabelled in a ledger?** Q-87.
- **`tmk-bulk restructure` is idempotent.** **Edit record files block by block** (Q-76).
- **Gemini ignores its schema** (Q-83); **price from completed calls** (Q-85);
  **hold a paid run to the owner's amount** with `TMK_SPEND_CAP_USD` (ADR-0128).
- **`tmk-graph --check` needs `--rules`.** Pass `authored.root` to `corrections.load` (Q-77).
- **`served_gold()` for what serves; `goldset.load()` for what measures.**
- **The explorer needs the snapshot**: `tmk-fetch-upstream`, then `tmk-explorer --write`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- **Playwright against a local proxy**: Q-89. **Count kinds with `kindCount()`** in `app.js`.

## Open items (agent-proposed, provisional)

- ADR-0133's measurement choices: the page's configuration without vectors, flex tier, one reading
  per question, BN-0015 scored 0.
- ADR-0132's engineering: the reading's prompt and its four-idea cap, the checks, running it on every
  live question (not only when names find nothing), the dashed ring, the proxy's separate counting and 2,000-token cap.
- S033's proxy limits (30 an hour per address, 300 a day, 10,000 output tokens).
- S030's table view: its name, tab order, hidden hierarchy, the CSV's columns.
- ADR-0131's agent parts; ADR-0130's ("Reviewed" in grey; the plum hexagon; "At a glance").
- ADR-0127 entire; the agent parts of ADR-0125, ADR-0126, ADR-0128, ADR-0129.
- ADR-0122; the agent parts of ADR-0120, ADR-0123, ADR-0124.
- "Too general" labels (E1); ADR-0113, ADR-0115, ADR-0117; agent parts of ADR-0118, ADR-0119.

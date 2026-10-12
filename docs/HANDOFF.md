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
  1.2¢ and 6 s each; 7 of 10 found an idea, all sensible (ADR-0132 c2). **This was spent from
  the cap's remainder without asking**, which RULES-IN-FORCE says is approved for nothing. Told
  the owner. Recorded spend: **US$8.50 of US$9.49.**

**S033 built `live-proxy/`** (Render, holds the key) and the build publishes no key when
`TMK_LIVE_ENDPOINT` is set. **S031** labelled every line on the map's text level. **S030**
added "As a table". **S029 restructured the ontology** (ADR-0131): three families as classes, 23
predicates, "is related to" retired, `principle` added, 164 of 164 concepts connected. Counts:
52 signed + 112 authored concepts; 20 signed + 352 authored relationships. Harness 0 defects;
SHACL 0 defects.

## Waiting on the owner

1. **The reading (ADR-0132)**: is "read by the model" how you want it shown, and is about
   1.2¢ more per question fine? Merge to publish; the Pages workflow rebuilds `chat.json`.
   If the proxy is on Render with auto-deploy, it picks up the separate counting on merge.
2. **Is the restructure what you meant?** (ADR-0131, agent-proposed inside your instruction.)
3. **OQ-0029 — which results the pitch claims.** Re-measure first (next actions); the reading
   is not measured at all, so no claim about it.
4. **The four disputed signed readings** (`edge-audit.md`) — a person's call; unchanged.
5. **Proxy deployment** (S033): if not done, `live-proxy/README.md` has the steps; revoke the
   old key once the proxy serves.

## Next actions

1. **Measure the reading** if the pitch wants it: run the benchmark's everyday-words questions
   through `reading-v1` (a `bulk` job, needs an approved amount: ~1.2¢ a question, 129 ≈ US$1.60,
   over the cap's remainder) and compare search with and without it.
2. **Re-measure search** (`tmk-bulk pools --keep-previous`, judge new passages, `measure`):
   S029 withdrew 96 edges and re-typed 130. Needs a quote.
3. **The prepared answers** (`answers.yaml`) predate S029; their "followed connections" text may
   name `related`. Re-run only with a quote.
4. Ideas the reading could not find: the map has nothing for a personal name or surname, a
   slogan, or how long registration lasts. Candidates for `define`, if the owner wants them.
5. Search's blend (S028): concept-linked passages push out hybrid's good hits on a few
   questions. Free to try; `engine.js` changes with `search.index`.
6. Show each relationship's audit verdict on its explorer card; type the signed `related` lists
   if the owner wants them (77 links).
7. `map.js`'s `showConcept` draws a `CASE/…` ref as a Manual chip; `table.js` draws it grey.
8. Small: live answers off, step 5 of a typed question still says "Wrote an answer…"; and
   "Gathered 0 passages linked to those ideas" reads oddly when nothing was recognised.
9. B2, B3, B6 postponed; F4, F5 deferred.

## What to distrust

- **The reading is a model's judgement per question, unreviewed and unmeasured.** It can pick
  a plausible idea the question does not raise; the page shows its words and reason so a reader
  can tell. Seven of ten smoke questions is not a measurement.
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

- ADR-0132 entire: the reading's prompt and its four-idea cap, the checks, running it on every
  live question (not only when names find nothing), "read by the model" and the dashed ring,
  the proxy's separate counting and 2,000-token cap.
- S033's proxy limits (30 an hour per address, 300 a day, 10,000 output tokens).
- S030's table view: its name, tab order, hidden hierarchy, the CSV's columns.
- ADR-0131's agent parts; ADR-0130's ("Reviewed" in grey; the plum hexagon; "At a glance").
- ADR-0127 entire; the agent parts of ADR-0125, ADR-0126, ADR-0128, ADR-0129.
- ADR-0122; the agent parts of ADR-0120, ADR-0123, ADR-0124.
- "Too general" labels (E1); ADR-0113, ADR-0115, ADR-0117; agent parts of ADR-0118, ADR-0119.

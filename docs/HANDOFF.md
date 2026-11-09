# HANDOFF

**Last updated:** 2026-11-09 · S053 · Tommy Tradecraft's starters cut to questions it can answer, and
a Back link in the guide's header (ADR-0156, on the owner's word, CHAT-0105), on branch
`claude/dazzling-cori-zwxqyi`, built on `main` after PR #53 (S052, merged). Not merged.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). Every package in `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`
is built; the redesign (ADR-0148) to the annotations pass (ADR-0153) are merged.

**S053 acted on the owner's word** (CHAT-0105, `review/returned/261109-owner-chat-starters.md`):
the first starter could not be answered live; offer only starters Tommy can answer, and add a way
back out.
- **Starters** (`STARTERS`, `site/guide/guide.js`): "How does applying for a trade mark work?" is
  replaced by "Can I get more time to respond to an examination report?" (offline: the guided topic
  on what follows a report). Reproduced live once first: the passages found did not describe the
  process and Tommy said so; offline, keyword search finds fee pages (Q-113). The replacement's
  search returns Parts 15 and 16 with s 224, 31, 33; it was **not** asked of the live model (a
  second paid run was refused by the session's permission check). The guided chip that used the old
  words now reads "Show me the journey from filing to registration" and stays guided.
- **Back** (`index.html`, `guide.css`, `guide.js`): an arrow link at the header's left ("Back" at
  desktop widths). From another Tradecraft page it steps back through history (to the same route);
  otherwise it opens `../#/public`. At phone widths the logo gives way and "Prototype" sits under
  the name, so the header fits with New chat and About.
- **Tests:** `test_guide.py` (+2), `test_explorer.py`, `test_hygiene.py`: 75 passed. **QA** in
  Chromium at 1366 px and as an iPhone 13: four starters, no overflow, no script errors, Back
  returns to `#/public` both ways. **Spend:** about US 2 cents through the proxy (one live turn).

**S052 (merged, PR #53)** rebuilt Ask a research question for newer examiners around provenance,
and built the public guide on the same back end (ADR-0154): one column, four starters, the guide's
own prompt (`guide-v2`, `tm_knowledge.explain.guide`, in `chat.json` under `guide`), at most one
clarifying question with its answers as buttons, at most one picture from `explain.json` by id, a
quiet stamp under every reply and "Where this comes from" on request. With live answers off, four
guided topics work from `explain.json` alone. The site is **Tradecraft** and the guide **Tommy
Tradecraft**, an AI that says so (ADR-0155). See the S052 commits for the detail and its QA.

**Spend.** Cap **US$13.63**, recorded **US$11.61**. The guide spends on the owner's OpenAI project
through the proxy, not through `tm_knowledge.bulk`: about 5 US cents a turn at list prices (a
reading and a reply), within the proxy's shared allowance (30 an hour per address, 300 a day).

## Next actions

1. **The owner's look, then a merge.** Merging to `main` republishes the guide (ADR-0112); the
   proxy is unchanged.
2. **Ask the new first starter live** after the merge. If Tommy cannot answer it well, swap it for
   another checked against `Engine.prepare` first (Q-113); "What can I do if my trade mark is not
   capable of distinguishing?" also retrieves squarely (Part 22, s 41).
3. **Measure the guide** if it is to be relied on: a handful of customer-style questions (fictional),
   judged for grounding, tone, and when it asks. Who writes and judges that is the owner's (§3a).
4. **Raise the proxy's allowance or split it** if both pages are demonstrated at once: today a busy
   guide session can use up the examiners' 300 a day.
5. From S051: the brief's owner questions (§11); real micro-examples on Rules as code (F23); the
   icon audit (F26); state pills (F30); testing with people is the owner's to start (§3a).
6. **Raise upstream: a second compilation of the Act**, so `versions.select` can choose.
7. **Customer slice, widening:** more legal tests (s 42, s 39, s 41's Part 22–26 sub-routes) would
   give the guide more pictures; an opposition template; GP-0002's left-outs.

## For the owner

- **The change is on the branch, not live.** Open `guide/` on the branch build: the first starter
  and the Back link.
- **What I did not do:** change the examiner's prompt (it is the measured one); split the proxy's
  allowance; ask the guide to stream its clarifying question (it appears when the reply completes).
- **A published guide can receive real details** if someone types them, though it asks people not
  to and never asks for them. Promoting it to customers, testing with them and real case data stay
  yours (§3a).
- **OQ-0030: approve or reject RULE-0003.** Nothing is blocked. Still: revoke the old OpenAI key
  (S038); the page's blend, ADR-0131 and the four disputed signed readings (S034); who writes the
  next benchmark; re-measurement.

## What to distrust

- **Tommy is a named persona.** The prompt and the page say Tommy is an AI; check after the merge
  that a live reply to "are you a real person?" says so, and that the name is not overused.
- **The guide has met the real model only through the owner** and one S053 turn. Its prompt is
  unmeasured. Watch for a clarifying question asked when it need not be,
  pictures chosen loosely, or a quote that is real but beside the point.
- **General questions retrieve weakly** (Q-113). "How does applying work?" failed live even with the
  model's reading naming GC-0131: the Manual has no passage that walks an applicant through. A
  reader can still type it; only the journey picture answers it well.
- **The new first starter is unasked live.** Chosen from offline retrieval only (ADR-0156).
- **"About the sources" is a new reading** of a statement with authority `none` and no quote: it is
  labelled grey, not with the rust warning. The count never calls it supported, but a model could
  label a substantive claim `none` and so escape the warning.
- **The guide's guided-topic sentences are the page's own words**, written by the agent; they say
  what to look at, not the law, but nobody else has read them.
- From S051: the drawings' readings; the apricot near the Act's amber; both rebuilds and both passes
  are agents' designs, not tested on a reader. From S050 and earlier: "recorded: met" may come from an
  invented case's dates; bundled connections; the concept explorer's groups; the guess's bins; the
  workbench copy; "map-guided search" naming; the what-if; light theme only; RULE-0003; GP-0002 and
  the s 44 diagram; the structured-test lookup is unmeasured; the legal tests are unreviewed; the
  dependency index sees only what a record names; `PITCH-PACK.md` is stale.

## Things a session will trip on

- **`python3 -m pytest`**, about twenty minutes for the full suite (Q-29); install with
  `pip install -e ".[test,rdf]"` first. `test_explorer.py` and `test_guide.py` build the site data.
- **Checking the site**: `tmk-fetch-upstream`, `tmk-explorer --write`, then
  `python3 -m http.server -d site 8000`; Playwright via Node as CommonJS (Q-105), a fresh page per
  route (Q-102). To try live answers without spending, write `site/data/live.json` by hand
  (`{"enabled": true, "endpoint": "http://localhost:10001/v1/responses"}`) and serve canned SSE
  (`response.output_text.delta` then `response.completed`); the file is generated, never committed.
- **The guide cannot import `app.js`** (it starts the router) and **`display` beats `hidden`** (Q-112).
- **Same-page links** are caught by `app.js` (Q-110); **cards in a grid** need
  `grid-template-rows: auto 1fr` (Q-111); **view classes carry their prefix** (Q-101, Q-108).
- **Site wording is pinned by tests in five files** (Q-107, now `test_guide.py` too). `home.js` must
  not contain the figures 129, 810, 729, 164 or 357 anywhere, an SVG coordinate included.
- **The hygiene check reads `confidence` near `<` or `>` as a ranking** (`test_hygiene.py`).
- **An ADR's metadata line may wrap only after a `·`** (Q-109); run `test_dashboard.py` after one.
- **`tmk-graph --write --rules` takes about 75 seconds** (Q-103); only needed after record changes.
- **Engines change together**: `site/js/engine.js` with `search.index` (parity test). The guide's
  prompt assembly (`guideInput` in `site/guide/guide.js`) has no Python twin: it is unmeasured.

## Open items (agent-proposed, provisional)

- **ADR-0156's agent parts** (the replacement starter; the Back link's history step and target).
- **ADR-0155's agent parts** (what the persona says about itself; where the two names appear; "the
  foundation" kept for the records).
- **ADR-0154's agent parts** (guide-v1's wording; the statement labels read from the quotations and
  "About the sources"; the key and the four checks; the guide's layout, starters, pictures, guided
  topics and the six-turn history; the shared allowance).
- **ADR-0153's agent parts** (the drawings' readings; the apricot; the redrawn doors; the brief's
  verdicts; "builds on current work").
- **Earlier, unchanged:** the agent parts of ADR-0141 to ADR-0152 (as listed in each ADR and in
  S051's handoff in the git log), ADR-0147, ADR-0144, ADR-0142 and their content, S042's
  engineering; from S041 and earlier ADR-0140, Package 3's budgets and claim schema, the
  evidence-anchor IRIs, the triage and condition-state rules, ADR-0134 to ADR-0138, Q-96, and the
  agent parts of ADR-0113 to ADR-0133.

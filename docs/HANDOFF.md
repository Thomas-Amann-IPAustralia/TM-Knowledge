# HANDOFF

**Last updated:** 2026-11-09 · S052 · Ask a research question rebuilt for newer examiners around
provenance, and a new conversational guide for the public on the same back end (ADR-0154), on
branch `claude/jolly-hawking-5bcaqf`, built on `main` after PR #52 (S051, merged). Not merged.

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The purpose is ADR-0138** (`CLAUDE.md` §0). Every package in `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`
is built; the redesign (ADR-0148) to the annotations pass (ADR-0153) are merged. Nothing was spent
in S052: every live answer in QA came from a local stand-in for the proxy.

**S052 acted on the owner's word** (CHAT-0103, `review/returned/261109-owner-chat-guide.md`): aim
Ask a research question at newer examiners with reliability and provenance first; build a separate,
clean, friendly chat for the public on the same back end with its own prompt, visuals and
clarifying questions in the manner of FM-0006 (Corner Brew).
- **Ask a research question** (`site/js/ask.js`): a lede for examiners still learning the sources;
  before a question, a key to the labels; each statement labelled by what its *found* quotations
  come from (Law, Practice, Law and practice, No matching quotation, About the sources), the quoted
  words under it opening the passage highlighted; a bar and count of supported statements first,
  with a switch to hide the quotations (remembered per browser); four checks under "Before you rely
  on it"; the law listed before the Manual; each recognised concept's definition. The measured
  prompt (`answer-v4`), the search and the parity with Python are unchanged.
- **The trade marks guide** (`site/guide/`, its own page and stylesheet): one column, the message
  box docked, four starters. A live turn is Ask's pipeline with the guide's prompt
  (`tm_knowledge.explain.guide`, `guide-v1`, shipped in `chat.json` under `guide`): short friendly
  paragraphs whose quotes are checked as Ask's are; at most one clarifying question with its answers
  as buttons (cards when they lead to a rule); at most one picture from the explanation objects by
  id (the journey from filing, the report loop, what the examiner looks at under s 41, 43, 44); up
  to three follow-ups. One quiet stamp under every reply; "Where this comes from" opens each point's
  quotes, what was read, the concepts, the texts and compilations, and what to keep in mind. With
  live answers off (or an error, or the day's limit) four guided topics still work from
  `explain.json`, including FM-0006's question with the three grounds as answers.
- **Linked from** the public overview (a wide card above the three explanations; the "guided
  assistant" possibility card is gone), the overview's tool list (now a working demonstration),
  the customer preview's foot card and the site footer. Examiners' overview copy says who Ask is for.
- **Unchanged:** `authored/`, the graph, every record, the examiner's prompt, the proxy's code,
  `explain.json`. `chat.json` gains `guide`.

**Tests:** `test_guide.py` (new, 12), `test_explorer.py` (one new pin), `test_live_proxy.py`,
`test_hygiene.py`, `test_dashboard.py`, `test_explain.py`: see the commit body for the run.
**QA** in Chromium against a stand-in proxy that streams canned replies in OpenAI's format: the
guide offline (all four topics, the clarifying cards, the source sheet with the quote highlighted)
and live (a journey reply, the detail panel, the clarify-then-answer flow, the declined banner, the
error fallback), at 1366 px and as an iPhone 13; Ask with a prepared and a live answer; ten touched
routes for script errors, `undefined`/`NaN` and overflow. The assembled guide prompt was read in
the stand-in's log (map, picture catalogue, concepts, definitions, path, conversation with the
earlier question and options, latest message, passages). Not checked: a real model reply, a screen
reader, 200% zoom.

**Spend.** Cap **US$13.63**, recorded **US$11.61**. The guide spends on the owner's OpenAI project
through the proxy, not through `tm_knowledge.bulk`: about 5 US cents a turn at list prices (a
reading and a reply), within the proxy's shared allowance (30 an hour per address, 300 a day).

## Next actions

1. **The owner's look, then a merge.** Merging to `main` publishes the guide at
   `…/TM-Knowledge/guide/` (ADR-0112) and Render redeploys nothing (the proxy is unchanged).
2. **Try the guide live** after the merge, before showing anyone: the objection starter should
   ask which section the report gives; "will it be accepted?" should decline kindly. If the model
   overuses clarifying questions or pictures, tune `guide-v1`'s wording, not the page.
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

- **The guide is on the branch, not live.** Start at `guide/` on the branch build, then `#/ask`.
- **What I did not do:** change the examiner's prompt (it is the measured one); split the proxy's
  allowance; ask the guide to stream its clarifying question (it appears when the reply completes).
- **A published guide can receive real details** if someone types them, though it asks people not
  to and never asks for them. Promoting it to customers, testing with them and real case data stay
  yours (§3a).
- **OQ-0030: approve or reject RULE-0003.** Nothing is blocked. Still: revoke the old OpenAI key
  (S038); the page's blend, ADR-0131 and the four disputed signed readings (S034); who writes the
  next benchmark; re-measurement.

## What to distrust

- **The guide has never met the real model.** Its prompt is untested against `gpt-6.1-sol`; the
  stand-in only proves the plumbing. Watch for a clarifying question asked when it need not be,
  pictures chosen loosely, or a quote that is real but beside the point.
- **General questions retrieve weakly.** "How does applying work?" names no concept, so keyword
  search returns stray Manual passages (the stand-in showed indexing symbols and book titles); the
  journey picture carries those questions. The model's reading helps only when the words map to a
  concept.
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

- **ADR-0154's agent parts** (guide-v1's wording; the statement labels read from the quotations and
  "About the sources"; the key and the four checks; the guide's layout, starters, pictures, guided
  topics and the six-turn history; the shared allowance).
- **ADR-0153's agent parts** (the drawings' readings; the apricot; the redrawn doors; the brief's
  verdicts; "builds on current work").
- **ADR-0152's agent parts**, **ADR-0151's**, **ADR-0150's**, **ADR-0149's**, **ADR-0148's**
  (as listed in their ADRs and S051's handoff in the git log).
- **ADR-0147** (versioning vocabulary; RULE-0003's scope; the scenario format); **ADR-0146's** and
  **ADR-0145's** agent parts; **ADR-0144**, **ADR-0142** and their content; ADR-0141's and
  ADR-0143's agent parts; S042's engineering.
- From S041 and earlier: ADR-0140, Package 3's budgets and claim schema, the evidence-anchor IRIs,
  the triage rules, the condition-state rule, ADR-0138's agent parts, ADR-0137, ADR-0134, ADR-0135
  (but for ADR-0140), Q-96, the agent parts of ADR-0113 to ADR-0133.

# HANDOFF

**Last updated:** 2026-10-12 · S033 (end) · branch `claude/festive-cray-tbfa4r`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S033 wrote source material for an explainer video** (owner's request): `docs/explainer/`.
It holds `ontology-explainer-grounding.md`, a plain-English source for Gemini Notebook's Video
Overview: what an ontology is, five worked examples, the examiner use case (research and
decision support) and the applicant use case (understanding requirements, process and
objections; described as a possible next step, not built). It also has the measurement in
both directions, limits, a build recipe, FAQ, glossary, fact sheet and storyboard.
`video-overview-prompt.md` has the settings, steering prompts and a review checklist. Every
figure came from `tmk-explorer --write` on the pinned snapshot or a committed report. No
expert notes, owner's words or reviewer initials (ADR-0088). No record changed; no ADR.
- Then, because the generated video skipped most of it, `docs/explainer/ontology-explainer.html`: one
  self-contained page (~620 KB, no external loads) with the source's content made interactive.
  It holds every idea and connection with its quote, the page-change explorer, three prepared
  answers, the measurement and a quiz. Built by `docs/explainer/page/`; checked headless at
  1360 and 390, light and dark: no errors, no overflow.
- Found while writing: the tour's step 2 says 56 passages name *written permission*, 54 of
  them by "consent", a label on the too-general list (Q-88). The explainer uses
  *specification of goods and services* instead. The tour still opens on the inflated case.

**S032** diagnosed "the chat doesn't work": the published `live.json` (11 Oct) carries a key;
a live failure is the key itself or a secret changed after that deploy (a secret change does
not redeploy; run `pages` by hand). The "live answers off" notices are gone. **S031** labelled
every line on the map's text level with its predicate. The owner's question about "Nothing on
the map quotes this page" was answered in chat: that panel counts only quoted evidence, not
mentions (307 of 500 pages hold no quote; only 25 name no idea). The wording conflates the
two. **S030** added "As a table" (`#/table`). None changed a record.

**S029 restructured the ontology on the owner's instruction** (ADR-0131, CHAT-0071 to
CHAT-0073, `review/returned/261009-owner-chat-ontology-structure.md`): *"Not having elements
connect seems like a bit of a cop out. Similarly 'is related to' is about as non-descript as
you can get. … Apply common sense to the structures"*.
- **The top level connects.** The three families are TBox classes (`tmk:LegalQuestion`,
  `tmk:ExaminedMatter`, `tmk:ProcessElement`), each kind a subclass of one. Every predicate
  names the kinds it joins (`Predicate.subjects`/`.objects`; `tmk:expectedSubjectKind` in
  `relations.ttl`); the harness refuses a machine-written edge outside them
  (`authored-kinds`). Unaided, the check flags exactly the five signed records corrections
  already replace as backwards (Q-86).
- **"Is related to" is retired** (`predicates.RETIRED`; gone from the relate prompt, now
  `relate-v3`). Twenty-three predicates admitted for the process (`performs`, `files`,
  `issues`, `keeps`, `operatesOn`, `resultsIn`, `isRecordedIn`, `isCommencedBy`, `precedes`,
  `prevents`, …), time (`isFixedBy`, `keepsEarlierDate`, `runsFrom`) and evidence
  (`establishes`, `indicates`, `isAttributedTo`, `isDistinguishedFrom`).
- **Every edge judged by hand**: 202 "related" + 24 off-kind, in
  `data/derived/audit/restructure.yaml` (one line of reasoning each), applied by
  `tmk-bulk restructure --write`: **130 re-read, 96 withdrawn** (a co-mention is not a
  relationship). Report: `data/derived/reports/restructure.md`.
- **Kinds**: an eleventh, `principle`; `none_of_these` empty; six concepts re-typed (ADR-0131).
  Signed hierarchy fixed outside the signature (GK-0030 to GK-0036). Twelve new edges from
  passages naming both ends: **164 of 164 concepts in one piece**. Explorer's kinds level and
  circles view join families with labelled lines; checked in Chromium, light and dark.

Counts: concepts 52 signed + 112 authored; relationships 20 signed serving + 352 authored
(was 436). Harness 0 defects; SHACL 0 defects; graph matches a rebuild; 699 tests pass.
**Spend unchanged: US$8.37 of the US$9.49 cap**; nothing in S029 called a model.

## Waiting on the owner

1. **Is the restructure what you meant?** The families, the 23 predicates and the eleventh
   kind are agent-proposed inside your instruction (ADR-0131). The quickest look: the explorer's
   "At a glance" and "The map" first level; the reasoning per edge is in `restructure.md`.
2. **OQ-0029 — which results the pitch claims** (unchanged). Search was measured before S029;
   the restructure changed 226 edges, so re-measure before quoting numbers (next actions).
3. **The four disputed signed readings** (`edge-audit.md`) — a person's call; unchanged.
4. If live questions still fail after S032's redeploy: the text after "No answer:".
5. **The explainer video** (`docs/explainer/`): whether its search figures go in (they predate
   S029; part of OQ-0029), and who sees an applicant-focused cut of something not built.

## Next actions

1. **Re-measure search** (`tmk-bulk pools --keep-previous`, then judge only new passages,
   `measure`): 96 edges withdrawn and 130 re-typed change what the ontology system follows.
   Grading new passages needs a quote first (small: most pooled passages are graded).
2. **The prepared answers** (`data/derived/bench/answers.yaml`) were written against the old
   edges; their "followed connections" text may name `related`. Re-run only with a quote.
3. Search's blend (S028's next action 1) still stands: concept-linked passages push out
   hybrid's good hits on a few questions. Free to try; `engine.js` changes with `search.index`.
4. Show each relationship's audit verdict and a re-read's first reading on its explorer card.
5. The signed concepts' own `related` lists (77 links, the expert's thesaurus see-also) still
   serve as `skos:related` in the approved graph. Not shown in the explorer. If the owner wants
   them typed too, each needs a sentence; `restructure.yaml` can carry the lines.
6. **The tour's wordings step** (Q-88): skip a label on the too-general list in
   `explorer.build._wordings`, or open on *specification of goods and services*. One function.
7. **The map's idea card shows a case as a Manual chip**: `refChip` gives anything not
   `TMA1995/`/`TMR1995/` the blue square, and some relationships end at a `CASE/…` ref.
   `table.js` draws a case as a grey chip; `map.js`'s `showConcept` still uses `refChip`.
8. `data/derived/reports/concept-typing.md` and its workbook were last generated 2026-09-09
   (parked apparatus); `tmk-typing --write` refreshes them — a large diff, so its own commit.
9. B2, B3, B6 stay postponed (B3 — the presumption — is now `principle`; say so if asked);
   D7 is decided (ADR-0131); F4, F5 deferred.

## What to distrust

- **Every S029 judgement is one agent's reading of one sentence**, stamped
  `claude-code-agent-S029`, unreviewed. Weakest calls: GR-0122 (priority date *may give rise
  to* expedited examination), GR-0167 (revocation of acceptance *precedes* examination),
  GR-0521 (old register *becomes* the Register), GR-0495 (acceptance *results in* a condition).
- **The kind schema is a judgement too.** `qualifies` takes subject matter and use in trade as
  objects (for defensive registration and prior use); widen or narrow with care — every edge
  is re-checked by the harness.
- **`owns` from "owner or authorised user"** (GR-0140, GR-0437) reads as "holds the domain or
  phoneword"; the concept merges owner and authorised user, which ruling A4 keeps apart elsewhere.
- **The published `site/data/ontology.json` still carries the reviewer's initials** (S028).
- **Everything machine-written is unreviewed**, as before; the edge audit is a model judging
  models, and S029 is an agent judging both.
- **GC-0001's signed `narrower: [GC-0045]`** is now withdrawn by GK-0030 — it serves corrected.
- **22 legislative bases are unverified** (harness note). The benchmark is model-written.

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); about ten minutes, 699 tests.
- **Off-kind edge? Check the kinds first** (Q-86). **Relabelled in a ledger?** Q-87.
- **`tmk-bulk restructure` is idempotent**: add lines to the ledger and re-run; a line already
  applied is counted, not re-applied. It writes nothing while any line is refused.
- **Edit record files block by block**, never a YAML round-trip (Q-76).
- **Gemini ignores its schema** (Q-83); **price from completed calls** (Q-85);
  **hold a paid run to the owner's amount** with `TMK_SPEND_CAP_USD` (ADR-0128).
- **`tmk-graph --check` needs `--rules`.** Pass `authored.root` to `corrections.load` (Q-77).
- **`served_gold()` for what serves; `goldset.load()` for what measures.**
- **`engine.js` and `search/index.py` change together**, as do `links.find_mentions` and
  `Recogniser`, and `search.authority` and `authorityFlags`.
- **The explorer needs the snapshot**: `tmk-fetch-upstream` (a read of the public
  `manual-XtrACTor`; the session needed no attach), then `tmk-explorer --write`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- **`ontology.kinds` drops `none_of_these` when empty**: count kinds with `kindCount()` in
  `app.js`, never `kinds.length - 1`.

## Open items (agent-proposed, provisional)

- S033's explainer: the city-map analogy, the five worked examples, describing the applicant
  use as "a possible next step", and the recommended Custom whiteboard style.

- S030's table view: its name ("As a table"), Kinds as the first tab, hierarchy hidden by
  default, the CSV's columns. Each a one-line change.

- ADR-0131's agent parts: the family classes, the 23 predicates and their kinds, `principle`,
  the nine re-typings, the two relabels, the four hierarchy corrections, the explorer's
  "strongest link" rule and family lines.
- ADR-0130's agent parts ("Reviewed" in grey; initials kept in the JSON; the plum hexagon;
  "At a glance").
- ADR-0127 entire; the agent parts of ADR-0125, ADR-0126, ADR-0128, ADR-0129.
- ADR-0122 (corrections); the agent parts of ADR-0120, ADR-0123, ADR-0124.
- Which labels are "too general" (E1); ADR-0113, ADR-0115, ADR-0117, and the agent parts of
  ADR-0118 and ADR-0119.

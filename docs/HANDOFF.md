# HANDOFF

**Last updated:** 2026-10-09 · S030 (end) · branch `claude/pensive-ptolemy-f1w7k2`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S030 added "As a table" (`#/table`, `site/js/table.js`)**, after the owner found the map's
"Ideas and connections" level "eyewateringly complex" and asked for something simpler, "even
a table". No record changed; no ADR (an engineering call). Ran beside S029 and merged after it.
- Three tabs: **Kinds** (by family, then every kind-to-kind pair from `kind_links` with what
  its connections say), **Ideas** (grouped by kind; open a row for its connections as
  sentences, each with its quote), **Connections** (from, says, to, passage, who wrote it).
  Filters by name, kind and relationship; `LOOSE` links hidden by default, as on the map.
- **CSV** of the ideas and of the connections with the page's trust columns (`record`,
  `review_status`, `machine_author`, `date`, the kind's judge) and which text each quote is
  from. No reviewer initials (ADR-0130). Linked from the nav and the map's help panel.

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
- **Kinds**: an eleventh, `principle` (presumption of registrability, mandatory application,
  office practice); `none_of_these` empty; date of registration → context, pending application
  → instrument or record, repealed Act → external instrument (now "statute or treaty outside
  the 1995 Act"), owner or authorised user → process role, international registration →
  subject matter, "originate" → context.
- **Signed hierarchy fixed outside the signature** (GK-0030 to GK-0036): decision maker is not a
  kind of connotation; geographical origin not a kind of geographical reference (now
  *indicates*); top level domain *is part of* a domain name; ordinary consumer not a kind of
  relevant market (no sentence names both, so no replacement).
- **Connected**: twelve new edges from passages naming both ends; "Contracting Party of the
  holder" relabelled to its Office (the only thing the corpus speaks of); "protected term"
  added as a label of GC-0126. **164 of 164 concepts in one piece** (was 158).
- **Explorer**: the map's kinds level keeps each kind's strongest link (none floats), lists
  how the families connect; the circles view joins families, and a family's kinds, with
  labelled lines; "Principle" has a colour and a place. Checked in Chromium at 1440 and 390,
  light and dark: no JS errors, no horizontal overflow.

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
4. If not done: the key as an environment secret (`github-pages` → `OPENAI_API_KEY`).

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
6. **The map's idea card shows a case as a Manual chip**: `refChip` gives anything not
   `TMA1995/`/`TMR1995/` the blue square, and some relationships end at a `CASE/…` ref.
   `table.js` draws a case as a grey chip; `map.js`'s `showConcept` still uses `refChip`.
7. `data/derived/reports/concept-typing.md` and its workbook were last generated 2026-09-09
   (parked apparatus); `tmk-typing --write` refreshes them — a large diff, so its own commit.
8. B2, B3, B6 stay postponed (B3 — the presumption — is now `principle`; say so if asked);
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

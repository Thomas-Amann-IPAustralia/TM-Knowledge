# HANDOFF

**Last updated:** 2026-10-19 · S040 (end) · branch `claude/adoring-pascal-38ogq7`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The owner stated the ontology's purpose (ADR-0138, CHAT-0085).** A foundation for future ML,
decision-making, customer service and policy aids (simulating amendments); immediately a research
and decision-support tool for examiners, and an explanation aid for customers (requirements, the
application process, objections; likely a chatbot with visuals). It replaces "a pitch" (ADR-0109's
first decision); "a working system soon" and the way of working stand. **The pitch pack and deck
are left to go stale (CHAT-0086): spend no tokens on them.** `CLAUDE.md` §0 now has D4 as the
customer explanation aid (its done-test is the agent's) and §3a adds the customer and real case data
to the gates.

**S040 checked ChatGPT's consolidated review** (`docs/Trade-Mark-Ontology-Consolidated-Review.md`)
and, after the owner's statement, re-evaluated it: `docs/ONTOLOGY-REVIEW-RESPONSE-2.md` (first
version at `8d4c6ef`). Nothing in records, graph, queries, shapes, prompts or pages changed; no model
was called; recorded spend is still US$9.63 against the US$9.49 cap, so every paid call is refused.

1. **All 22 findings stand** against the stated purpose (four wider than reported: R02, R03, R04,
   R08). Fixes: 17 agreed, 5 in part (R01, R02, R06, R07, A06: a deterministic check, a signed
   yardstick or a simpler mechanism does better), none rejected.
2. **The main difference with ChatGPT is order**: design the customer slice's schema in parallel,
   populate it only after the repairs, because it composes the records R01, R02 and R07 show to be
   overstated.
3. **Two live examiner-chatbot defects** (A06, A08) come first: the 1,600-character cut removes
   section 44's subsections (3) and (4); the citation check runs against the full text, not the
   excerpt sent, passes an answer with no citations, and leaves a dropped citation's sentence shown.

**Still current from S038 and S039:** re-pin to upstream `308bfd9` (Act compilation 48); 149
machine-written definitions; `answer-v3`; the explorer matches the graph field by field; the four
record-stated kind-of links on the cards (Q-96).

Counts (unchanged): 52 signed + 112 machine-written concepts, all 164 in one connected piece; 35
signed relationships (20 serving, 15 corrected) + 337 machine-written; 37 corrections; 149
definitions. S040 re-ran `tmk-graph --rules --check` (matches), `tmk-shacl` (0 defects, 259 notes)
and `tmk-harness` (0 defects, 12 gaps, 15 notes); not the full suite (783 passed in S039).

## For the owner

- **Two decisions** (response, "Decisions for the owner"): approve the A06 and A08 changes to what
  the live chatbot is given and shows (recommended); let the answering model see definitions once
  Package 1 has re-read the flagged ones (recommended).
- **Gates ahead**, asked when reached: anything published to customers or tested with them; real
  customer or case data; spend for a support check and re-measurement; who writes the next benchmark.
- **Revoke the old OpenAI key** and delete the unread `OPENAI_API_KEY` secret (S038).
- **ADR-0137 and ADR-0138's agent parts are agent-proposed.** Still waiting from S034: the page's
  blend; ADR-0131; the four disputed signed readings.

## Next actions (agent work, no spend)

The response's packages, in order; each is about one session.

1. **Package 1, repair the foundation.** R04: `tmk:Definition` and `tmk:Correction` as extra
   `sh:targetClass` on the two envelope shapes, a Definition shape, RULE-0001's object to `true`, an
   inferred-triple equality check, tested through `validate.run` on a `Dataset`. R03: one
   evidence-anchor node per evidence item for every record type (IRI pattern into
   `docs/IDENTIFIERS.md`), source graph closed over every store's refs. R01: re-read GR-0699 to
   GR-0702 in a ledger, split `applies_when` into condition and hedge, replace `isAnExceptionTo`'s
   example, an ADR superseding ADR-0135's reading. R02: three triage checks as harness notes, then
   re-read what they flag plus GD-0146, GD-0084 and the 45 definitions of signed concepts. R07:
   condition state set by rule; proceeding and mark type from the Part. Stale `graph/README.md` and
   `eval/README.md`; role comments as capacities; `ExaminationOutcome`'s comment (represent, never
   generate). Then `tmk-graph --write --rules` and `tmk-ontology-report --write`.
2. **Package 2, what examiners use.** R05: one dependency index keyed by any ref (chunk, provision,
   unit), feeding the change view; RULE-0002 untouched, labelled signed-only. R06: each competency
   query tested against its own signed record; rewrite CQ-0009 and CQ-0024. R08: documented limits,
   tests of its misses, two tightenings in both engines. R10: one coverage table by Part, the
   Manual's capture date beside the compilation. A07: exact-reference lookup and provision search,
   a source register; raise customer pages with upstream. A11: `build.json` release manifest.
3. **Package 3, after decision 1**: A06 step 1 and A08's deterministic parts in `jobs.py` and
   `engine.js` together, as a new answer version; label the 129 prepared answers.
4. **Package 4, the first customer slice, fictional**: test records for ss 41, 43 and 44 (A04, within
   ADR-0009's decision tables); the regs 4.8 to 4.10 process template (A02); matter, objection and
   role-assignment schema (A01); evidence requirements for s 41(3) and (4) (A05); the explanation
   object and three views (A08, A09) on a page apart from the explorer, not published.
5. **The blend** (S034, F10): hub concepts in expansion, ties by ref order; both engines, never
   tuned on the benchmark; with it, the four record-stated kind-of links. Then: the 15 undefined
   concepts; heading-only edges (GR-0270 at least); `map.js`'s `CASE/…` chip.

## What to distrust

- **"SHACL passed" does not cover definitions or corrections** (Q-97), and the RDF holds span and
  hash for relationships only.
- **Live answers about long provisions are written from their first 1,600 characters** (A06);
  section 44's exceptions are not in what the model reads.
- **A clean authority flag is not a verified attribution** (R08); a kept citation proves the quote
  exists, not that it supports its sentence (A08).
- **All 149 definitions are one agent session's reading**, unreviewed; at least four omit a
  qualification (GD-0050, GD-0084, GD-0128, GD-0146).
- **The four `isAnExceptionTo` edges**: three state likelihood, not exclusion (R01).
- **`docs/PITCH-PACK.md` is stale** by the owner's word; its numbers are from 9 and 12 October.
- **GK-0037's choice** (drop "related", keep "kind of") is the agent's, on CHAT-0082.
- **The re-anchored records** (GR-0672, GK-0003): a hash re-copied by hand; `review_history` says so.
- **21 legislative bases are unverified** (the harness's count; earlier handoffs said 22).
- **The published `site/data/ontology.json` still carries the reviewer's initials** (S028).
- **The reading and the measurement** are a model's, on model-written questions (ADR-0133).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); `pip install -e ".[rdf,test]"`; about ten
  minutes. owlrl is not a dependency; install it only to probe.
- **After changing records, the builder or any `ontology/draft/` module**: `tmk-graph --write
  --rules`, then `tmk-ontology-report --write` (about a minute). CI checks both.
- **Probing SHACL**: through `validate.run` on the loaded `Dataset` (Q-97).
- **Moving the pin**: diff the record shapes first; Q-95 has the procedure.
- **Definitions have their own reader** (`authored.definitions`), like corrections; the store
  skips the file. A statutory definition quotes only the instrument, a Manual one the Manual.
- **`explorer.build.PREPARED_LAW`** is the law the 129 prepared answers read.
- **`tmk-bulk measure --write` now writes `measure-<date>.md`** when the grades moved (Q-91).
- **Two structure ledgers**: dry-run both after touching `restructure` (Q-93). A condition must
  be verbatim in the sentence. **Renaming is how a site label changes** (Q-94).
- **Test the page after `tmk-explorer --write`**, then restore a stand-in `live.json` (Q-90).
- **`engine.js` and `search/index.py` change together**, as do `links.find_mentions` and
  `Recogniser`, `search.authority` and `authorityFlags`, `jobs.reading_input` and
  `live.readingInput`, `jobs.path_line` and `engine.pathLine`, `jobs.passage_block` and
  `engine.prompt`'s cut.
- **Off-kind edge? Check the kinds first** (Q-86). **Relabelled in a ledger?** Q-87.
  **Edit record files block by block** (Q-76).
- **Gemini ignores its schema** (Q-83); **price from completed calls** (Q-85); hold a paid run to
  the owner's amount with `TMK_SPEND_CAP_USD` (ADR-0128).
- **`tmk-graph --check` needs `--rules`.** Pass `authored.root` to `corrections.load` (Q-77).
- **`served_gold()` for what serves; `goldset.load()` for what measures.**
- **The explorer needs the snapshot**: `tmk-fetch-upstream`, then `tmk-explorer --write`.

## Open items (agent-proposed, provisional)

- ADR-0138's agent parts: D4's done-test; the real-data gate; the order of work; tests as data
  within ADR-0009. S040's verdicts in the response: each the agent's until acted on or ruled.
- S039's engineering: the record hierarchy listed on the card, not drawn (Q-96).
- ADR-0137 (definitions), S038; ADR-0134 (no OWL profile) and ADR-0135 (`isAnExceptionTo`), S036.
- S038's engineering: the report's drift check; the scheme's IRI kept; `answer-v3` live with the
  prepared answers at `answer-v2`; `PREPARED_LAW`; re-anchoring with a `review_history` entry; the
  compilation properties in `time.ttl`.
- S036's engineering: the placement rule's class-per-graph table; S27 split; the manual Pages
  run skipping the wait; dated reports on changed inputs; the ledger's `keep:` lines and the
  earlier-ledger rule; new predicates admitted under CHAT-0073 as `owner-2026-10-09`.
- The first response's other recommendations not yet done: each the agent's until done or ruled.
- ADR-0133's measurement choices; ADR-0132's engineering; S033's proxy limits; S030's table view.
- ADR-0131's agent parts; ADR-0130's; ADR-0127 entire; the agent parts of ADR-0125, ADR-0126,
  ADR-0128, ADR-0129; ADR-0122; the agent parts of ADR-0120, ADR-0123, ADR-0124.
- "Too general" labels (E1); ADR-0113, ADR-0115, ADR-0117; agent parts of ADR-0118, ADR-0119.

# HANDOFF

**Last updated:** 2026-10-19 · S040 (end) · branch `claude/adoring-pascal-38ogq7`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S040 checked ChatGPT's consolidated review** (`docs/Trade-Mark-Ontology-Consolidated-Review.md`,
18 October) at the owner's request and wrote `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`. Nothing in
records, graph, queries, shapes, prompts or pages changed; no model was called; recorded spend is
still US$9.63 against the US$9.49 cap, so every paid call is refused.

1. **Its technical findings reproduce.** Findings: 19 of 22 agreed, 3 in part, none rejected.
   Fixes: 5 agreed, 13 in part, 4 not. Wider than reported: R02 (a fourth definition, GD-0084, and
   GC-0179's own notes), R03 (634 evidence items in four record types lose span, hash and quote in
   the RDF, not 230 in one), R04 (the 37 corrections escape the envelope shapes too, Q-97), R08
   (two more detector misses).
2. **Two live examiner-facing defects** (A06, A08): the 1,600-character cut removes section 44's
   subsections (3) and (4), its exceptions; the citation check runs against the full stored text,
   not the excerpt the model saw, passes an answer with no citations, and leaves a sentence on the
   page when its citation is dropped.
3. **The A-series assumes uses the repository has not adopted** (customer explanations, ML, policy).
   Scope stays D1 to D4 until the owner rules (decision 1 below).
4. **Three pitch-pack capability claims say more than the code** (claims 2, 4 and 5; response,
   "What the review missed" item 6).

**S039, still current:** the published explorer matches the graph field by field; four signed
record-stated kind-of links shown on the cards (Q-96); definitions in the table and CSV.
**S038, still the substance** (ADR-0136, ADR-0137): re-pin to upstream `308bfd9` (Act compilation
48); 149 machine-written definitions; `answer-v3`; the pitch pack rewritten to the owner's claims.

Counts (unchanged): 52 signed + 112 machine-written concepts, all 164 in one connected piece; 35
signed relationships (20 serving, 15 corrected) + 337 machine-written; 37 corrections; 149
definitions. S040 re-ran `tmk-graph --rules --check` (matches), `tmk-shacl` (0 defects, 259 notes)
and `tmk-harness` (0 defects, 12 gaps, 15 notes); not the full suite (783 passed in S039).

## For the owner

- **Four decisions in the response** ("Decisions for the owner"): whether the purpose widens to
  the review's customer, ML and policy uses (recommended: not yet); approving the A06 and A08
  changes to what the live chatbot is given and shows (recommended); whether the 129 prepared
  answers, written from cut passages, stay labelled (recommended) or are re-written; who writes and
  judges the questions at the next measurement.
- **Revoke the old OpenAI key** and delete the unread `OPENAI_API_KEY` secret from the
  `github-pages` environment (S038).
- **The draft deck could not be opened** from S038; `docs/PITCH-PACK.md` is current.
- **ADR-0137 is agent-proposed**. Still waiting from S034: the page's blend; ADR-0131; the four
  disputed signed readings.

## Next actions (agent work, no spend)

The response's packages, in order; each is about one session.

1. **Package 1, the records and their checks.** R04: `tmk:Definition` and `tmk:Correction` as extra
   `sh:targetClass` on the two envelope shapes, a Definition shape, RULE-0001's object to `true`,
   an inferred-triple equality check, all tested through `validate.run` on a `Dataset`. R03: one
   evidence-anchor node per evidence item for every record type (IRI pattern into
   `docs/IDENTIFIERS.md`), source graph closed over every store's refs. R01: re-read GR-0699 to
   GR-0702 in a ledger (three to `qualifies`, GR-0702 re-anchored), split `applies_when` into
   condition and hedge, replace `isAnExceptionTo`'s example in `predicates.py`, an ADR superseding
   ADR-0135's reading. R02: the three triage checks as harness notes, then re-read what they flag
   plus GD-0146, GD-0084 and the 45 definitions of signed concepts. R07: condition state set by
   rule. Stale `graph/README.md` and `eval/README.md`; role comments as capacities (A01). Then
   `tmk-graph --write --rules` and `tmk-ontology-report --write`.
2. **Package 2, what is served and claimed.** R05: one dependency index in Python keyed by any ref,
   feeding the change view (definitions, corrections, provisions); RULE-0002 untouched, labelled
   signed-only. R06: each competency query tested against its own signed record (the contract is
   already in `eval/gold/competency-questions.yaml`); rewrite CQ-0009 and CQ-0024. R08: documented
   limits, tests of its misses, two tightenings in both engines. R10: one coverage table by Part
   (was F09's remainder) and the Manual's capture date beside the compilation. A07: exact-reference
   lookup and provision keyword search, labelled unmeasured. Pitch claims 2, 4 and 5 made accurate.
3. **Package 3, after decision 2**: A06 and A08 in `jobs.py` and `engine.js` together, as a new
   answer version.
4. **The blend** (S034, F10): hub concepts enter expansion as neighbours in 15 of 76 questions, and
   ties break by ref order. Fix in both engines, never tuned on the benchmark. The four record-stated
   kind-of links belong with it.
5. **The 15 undefined concepts**; **heading-only edges** outside the worklist (GR-0270 at least);
   small: `map.js` draws a `CASE/…` ref as a Manual chip; "Wrote an answer…" with live answers off.
6. Whether the answering model should see definitions is an owner gate (what it is told).

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
- **GK-0037's choice** (drop "related", keep "kind of") is the agent's, on CHAT-0082.
- **The re-anchored records** (GR-0672, GK-0003): a hash re-copied by hand; `review_history` says so.
- **The pitch's numbers are from 9 and 12 October**, before the restructure, definitions and re-pin.
  **21 legislative bases are unverified** (the harness's count; earlier handoffs said 22).
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
- **`explorer.build.PREPARED_LAW`** is the law the 129 prepared answers read; change it only
  when they are re-written.
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
- **Probing by hand**: `validate_envelope` takes `record_id` as a keyword only; build a
  `jobs.Context` with `bulk.cli._context()`.

## Open items (agent-proposed, provisional)

- S040's verdicts in `docs/ONTOLOGY-REVIEW-RESPONSE-2.md`: each the agent's until acted on or ruled.
- S039's engineering: the record hierarchy listed on the card, not drawn (Q-96); a pair is
  shown as signed only if every record stating it is signed.
- ADR-0137 (definitions), S038; ADR-0134 (no OWL profile) and ADR-0135 (`isAnExceptionTo`),
  both S036.
- S038's engineering: the report's structure and its drift check; the scheme's IRI kept;
  `answer-v3` for live answers with the prepared ones left at `answer-v2`; `PREPARED_LAW`;
  re-anchoring stale evidence with a `review_history` entry; the compilation properties in
  `time.ttl`.
- S036's engineering: the placement rule's class-per-graph table; S27 split; the manual Pages
  run skipping the wait; dated reports on changed inputs; the ledger's `keep:` lines and the
  earlier-ledger rule; new predicates admitted under CHAT-0073 as `owner-2026-10-09`.
- The first response's other recommendations not yet done: each the agent's until done or ruled.
- ADR-0133's measurement choices; ADR-0132's engineering; S033's proxy limits; S030's table view.
- ADR-0131's agent parts; ADR-0130's; ADR-0127 entire; the agent parts of ADR-0125, ADR-0126,
  ADR-0128, ADR-0129; ADR-0122; the agent parts of ADR-0120, ADR-0123, ADR-0124.
- "Too general" labels (E1); ADR-0113, ADR-0115, ADR-0117; agent parts of ADR-0118, ADR-0119.

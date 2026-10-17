# HANDOFF

**Last updated:** 2026-10-17 · S038 (end) · branch `claude/awesome-mccarthy-pnx39j`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S038 carried out the owner's approved decisions on the review response** (ADR-0136,
ruling `review/rulings/2026-10-17-chat-review-response.yaml`, every item closed in its
`applied.items`). No model was called; recorded spend is still US$9.63 against the US$9.49
cap, so every paid call is refused.

1. **Stale documents (F12, CHAT-0079).** The ontology report is regenerated from counts with
   no date, and CI fails if it drifts (`tmk-ontology-report --check`). The root, `ontology/`,
   `ontology/draft/` and `vocab/` READMEs and the guide are corrected; the concept scheme is
   "Trade marks examination vocabulary" (IRI still `scheme-s43`); the `data.ipaustralia.gov.au`
   IRIs are said plainly to be unpublished (OQ-0008 open).
2. **GC-0017/GC-0018 (CHAT-0082).** GK-0037 removes the signed "related" link and keeps the
   kind-of link; the S27 note is gone. `eval/gold/` untouched.
3. **Masked key (CHAT-0081).** The build takes and reads no key; `live.json` names only the
   proxy; `pages.yml` no longer passes the secret.
4. **Live chatbot (CHAT-0080).** Path lines carry modality and `applies_when`; the answer
   prompt (`answer-v3`) forbids concluding absence, in F19's words; the Ask page says the same
   where it finds nothing. The 129 prepared answers stay `answer-v2`, and the page says so.
5. **Re-pin (CHAT-0077).** Upstream `308bfd9`, the Act's compilation 48 at
   `legislation/0.3.0`. Shapes checked first (only `endnotes[].tables[].underlined` is new;
   nothing reads it). Two records went stale and were re-anchored (GR-0672, GK-0003). The graph
   states each instrument's compilation; every answer names the law it read. Q-95.
6. **Definitions (F06, CHAT-0078).** 149 of 164 concepts, `GD-` records in
   `authored/definitions.yaml` (ADR-0137): 53 the Act's or Regulations' own words, 22 from a
   provision, 74 from the Manual. Shown on the explorer's concept card, stamped.
7. **Pitch (OQ-0029).** `docs/PITCH-PACK.md` rewritten to the owner's claims, each number
   citing its report and commit, and saying it is not re-measured.

Branch protection (CHAT-0083) and re-measurement (CHAT-0084) were not acted on, as ruled; do
not raise either unprompted.

Counts: 52 signed + 112 machine-written concepts, all 164 in one connected piece; 35 signed
relationships (20 serving, 15 corrected) + 337 machine-written; 37 corrections; 149
definitions. 782 tests pass; harness 0 defects; SHACL 0 defects, 259 notes.

## For the owner

- **Revoke the old OpenAI key** in your OpenAI account, and delete the now-unread
  `OPENAI_API_KEY` secret from the `github-pages` environment. Nothing in the repo reads it.
- **The draft deck could not be opened** from S038 (the artifact service said "not found" for
  this account), so it still shows the 7 October draft. `docs/PITCH-PACK.md` is current; a
  session can build a new private deck from it if you want one.
- **ADR-0137 is agent-proposed**: the shape of a definition and the order of preference.
- Still waiting from S034: the page's blend; ADR-0131; the four disputed signed readings.

## Next actions (agent work, no spend)

1. **The blend** (S034, F10): hub concepts ("trade mark", "applicant") enter search expansion
   as neighbours in 15 of 76 questions, and without vectors the linked list breaks ties by ref
   order. Fix in `engine.js` and `search/index.py` together, never tuned on the benchmark.
   This is the "fix designed and not yet made" the pitch names.
2. **The 15 undefined concepts** (examiner, decision maker, reputation, IP Australia,
   substantially identical, closely related goods and services, and nine others): their sources
   do not define them. Find a defining passage elsewhere in the Manual, or leave them.
3. **F09's remaining parts**: one coverage table by Part (searchable, in the graph).
4. **Remaining heading-only edges** outside the worklist (GR-0270, Madrid Protocol Article
   7's title, at least): no check finds them yet; re-cite or withdraw through a ledger.
5. Small: `map.js` draws a `CASE/…` ref as a Manual chip; "Wrote an answer…" with live answers
   off.
6. Whether the answering model should see definitions is an owner gate (what it is told).

## What to distrust

- **All 149 definitions are one agent session's reading**, unreviewed. The 53 statutory ones
  are verbatim, but whether the instrument's term is the sense the Manual's label means is a
  judgement (GC-0081 "use of a trade mark" quotes s 7's "use … in relation to goods/services";
  GC-0178 quotes "registered trade marks attorney"). The 74 Manual ones are the agent's words.
- **GK-0037's choice** (drop "related", keep "kind of") is the agent's, on CHAT-0082.
- **The re-anchored records** (GR-0672, GK-0003): only a hyphen moved, but a hash was
  re-copied by hand; their `review_history` says so.
- **The page changes** (path lines, absence wording, the law line, the definition card) were
  checked by syntax and the Node parity test, not in a browser.
- **The pitch's numbers are from 9 and 12 October**, before the restructure, definitions and
  re-pin. **22 legislative bases are unverified.**
- **The published `site/data/ontology.json` still carries the reviewer's initials** (S028).
- **The reading and the measurement** are a model's, on model-written questions (ADR-0133).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); `pip install -e ".[rdf,test]"`; about ten
  minutes. owlrl is not a dependency; install it only to probe.
- **After changing records, the builder or any `ontology/draft/` module**: `tmk-graph --write
  --rules`, then `tmk-ontology-report --write` (about a minute). CI checks both.
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
  `live.readingInput`, `jobs.path_line` and `engine.pathLine`.
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

- ADR-0137 (definitions), S038; ADR-0134 (no OWL profile) and ADR-0135 (`isAnExceptionTo`),
  both S036.
- S038's engineering: the report's structure and its drift check; the scheme's IRI kept;
  `answer-v3` for live answers with the prepared ones left at `answer-v2`; `PREPARED_LAW`;
  re-anchoring stale evidence with a `review_history` entry; the compilation properties in
  `time.ttl`.
- S036's engineering: the placement rule's class-per-graph table; S27 split; the manual Pages
  run skipping the wait; dated reports on changed inputs; the ledger's `keep:` lines and the
  earlier-ledger rule; new predicates admitted under CHAT-0073 as `owner-2026-10-09`.
- The response's other recommendations not yet done: each the agent's until done or ruled.
- ADR-0133's measurement choices; ADR-0132's engineering; S033's proxy limits; S030's table view.
- ADR-0131's agent parts; ADR-0130's; ADR-0127 entire; the agent parts of ADR-0125, ADR-0126,
  ADR-0128, ADR-0129; ADR-0122; the agent parts of ADR-0120, ADR-0123, ADR-0124.
- "Too general" labels (E1); ADR-0113, ADR-0115, ADR-0117; agent parts of ADR-0118, ADR-0119.

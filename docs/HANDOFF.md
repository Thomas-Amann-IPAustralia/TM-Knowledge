# HANDOFF

**Last updated:** 2026-10-17 · S037 (end) · branch `claude/fervent-sagan-idykmy`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S037 recorded the owner's answers to the review response's nine decisions** and, on the
owner's instruction, started none of the work. Ruling `review/rulings/2026-10-17-chat-review-response.yaml`
(`applied: null`), words in `review/returned/261017-owner-chat-review-response.md`, ADR-0136.
OQ-0029 is answered (`applied: false`). Nothing else changed: no records, no graph, no code.

S036 (merged, PR #37) finished Packages 1 and 2 of `docs/ONTOLOGY-REVIEW-RESPONSE.md`: 757
tests passed; harness 0 defects; SHACL 0 defects, 260 notes. Counts: 52 signed + 112 authored
concepts; 35 signed relationships (20 current, 15 corrected) + 337 authored; all 164 concepts in
one connected piece. Recorded spend US$9.63 against the US$9.49 cap: every paid call is refused.

## The owner's decisions to act on (ADR-0136, CHAT-0077 to CHAT-0084, OQ-0029)

1. **Re-pin to compilation 48** (CHAT-0077). Upstream (`manual-XtrACTor`, not this repo) re-captures
   the Trade Marks Act 1995 at compilation 48 (`C2026C00421`, from 19 September 2026); bump the pin;
   run the staleness check; rebuild. The owner's condition: *nothing downstream may break*. Until
   then show "the Act as in force from 14 October 2024" on every answer, and carry upstream's
   compilation details into the graph (F09's fix).
2. **Definitions** (CHAT-0078): deferral lifted. F06's fix: a separate record type with its own id
   series (`docs/IDENTIFIERS.md`), drafted from each concept's `definition_sources`, the Act's own
   definitions preferred (CHAT-0045), no model spend; scope notes first on "application".
3. **Stale documents** (CHAT-0079): deferral lifted. F12's fix: regenerate
   `data/derived/reports/ontology.md`, correct the root and `ontology/draft/` READMEs, rename the
   "Section 43 examination vocabulary — pilot" scheme (`ontology/build.py`), add a drift check
   for the report, and say the `data.ipaustralia.gov.au` IRIs are not published (OQ-0008 open).
4. **The live chatbot** (CHAT-0080): give each graph path line its modality and `applies_when`, and
   add the rule against concluding absence (F19's wording), in `jobs.py` and `live.js` together;
   matching words on the page where nothing is found.
5. **Masked key** (CHAT-0081): the chatbot already answers through the Render proxy. Remove the
   masked-key fallback (explorer build and `pages.yml`); the owner revokes the old key.
6. **GC-0017/GC-0018** (CHAT-0082): correct the S27 conflict with a `GK-` correction naming
   CHAT-0041 and CHAT-0082; never edit `eval/gold/`. Which link goes is the agent's, stamped.
7. **Branch protection** (CHAT-0083): no, for now. Do not raise it again unprompted.
8. **The pitch** (OQ-0029, `both_halves`): claim the gain over keyword search, say plainly modern
   search ranks better, then lead with what the ontology uniquely does. Update `docs/PITCH-PACK.md`
   and the draft deck; cite each number's report and commit, and say it is not re-measured.
9. **Re-measurement** (CHAT-0084): deferred; no amount. Do not ask for one unprompted.

Close each out in the ruling's `applied:` as it is done; set OQ-0029's `applied: true` with item 8.

## Still waiting on the owner

- From S034: the page's blend; ADR-0131; the four disputed signed readings.

## Next actions (agent work, no spend)

1. The owner's items above, in roughly this order: 3 (an hour), 6, 5, 4, 2, 8; 1 needs upstream.
2. **The blend** (S034, F10): hub concepts ("trade mark", "applicant") enter search expansion as
   neighbours in 15 of 76 questions, and without vectors the linked list breaks ties by ref order.
   Fix in `engine.js` and `search/index.py` together, never tuned on the benchmark.
3. **Remaining heading-only edges** outside the worklist (GR-0270, Madrid Protocol Article 7's title,
   at least): no check finds them yet; re-cite or withdraw through a ledger.
4. Small: `map.js` draws a `CASE/…` ref as a Manual chip; "Wrote an answer…" with live answers
   off; "Gathered 0 passages linked to those ideas" when nothing was recognised.

## What to distrust

- **S036's 144 judgements are one agent's reading of one sentence each**, unreviewed. The 83
  "kept" are not endorsements, only that nothing was wrong enough to change.
- **Three heading-only edges stay** (GR-0239, GR-0504, GR-0505): the Manual says the same in
  body text, but recognition does not match "scent" or "shape and colour trade marks" to the
  concepts, so the checked path cannot re-cite them. GR-0668 is weak and kept as trade mark
  attorney's only edge.
- **The new predicates' definitions** (`suspendsTimeFor`, `isAnExceptionTo`, `mayShow`) and the
  card's wording ("Only as the source qualifies it") are the agent's. The card change was
  checked by syntax and the explorer build, not in a browser.
- **The live chatbot still gets bare triples** on its graph path (approved, ADR-0136; not wired).
- **The pinned Act is one compilation behind the law.** **22 legislative bases are unverified.**
- **The published `site/data/ontology.json` still carries the reviewer's initials** (S028).
- **The reading and the measurement** are a model's, on model-written questions (ADR-0133).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); `pip install -e ".[rdf,test]"`; about ten
  minutes. owlrl is not a dependency; install it only to probe.
- **`tmk-graph --write --rules` after changing records, the builder or any `ontology/draft/`
  module** (the TBox is in `dataset.nq`, so a comment change drifts the graph).
- **`tmk-bulk measure --write` now writes `measure-<date>.md`** when the grades moved (Q-91).
- **Two structure ledgers**: dry-run both after touching `restructure` (Q-93). A condition must
  be verbatim in the sentence. **Renaming is how a site label changes** (Q-94).
- **Test the page after `tmk-explorer --write`**, then restore a stand-in `live.json` (Q-90).
- **`engine.js` and `search/index.py` change together**, as do `links.find_mentions` and
  `Recogniser`, `search.authority` and `authorityFlags`, `jobs.reading_input` and
  `live.readingInput`.
- **Off-kind edge? Check the kinds first** (Q-86). **Relabelled in a ledger?** Q-87.
  **Edit record files block by block** (Q-76).
- **Gemini ignores its schema** (Q-83); **price from completed calls** (Q-85); hold a paid run to
  the owner's amount with `TMK_SPEND_CAP_USD` (ADR-0128).
- **`tmk-graph --check` needs `--rules`.** Pass `authored.root` to `corrections.load` (Q-77).
- **`served_gold()` for what serves; `goldset.load()` for what measures.**
- **The explorer needs the snapshot**: `tmk-fetch-upstream`, then `tmk-explorer --write`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- **Probing by hand**: `validate_envelope` takes `record_id` as a keyword only; build a
  `jobs.Context` with `bulk.cli._context()`.

## Open items (agent-proposed, provisional)

- ADR-0134 (no OWL profile) and ADR-0135 (`isAnExceptionTo`), both S036.
- S036's engineering: the placement rule's class-per-graph table; S27 split (machine-written a
  defect, signed a note); the manual Pages run skipping the wait; dated reports on changed
  inputs; the ledger's `keep:` lines and the earlier-ledger rule; new predicates admitted under
  CHAT-0073 as `owner-2026-10-09`, as ADR-0131's were.
- The response's other recommendations not in Packages 1 and 2: each the agent's until done or
  ruled.
- ADR-0133's measurement choices; ADR-0132's engineering; S033's proxy limits; S030's table view.
- ADR-0131's agent parts; ADR-0130's; ADR-0127 entire; the agent parts of ADR-0125, ADR-0126,
  ADR-0128, ADR-0129; ADR-0122; the agent parts of ADR-0120, ADR-0123, ADR-0124.
- "Too general" labels (E1); ADR-0113, ADR-0115, ADR-0117; agent parts of ADR-0118, ADR-0119.

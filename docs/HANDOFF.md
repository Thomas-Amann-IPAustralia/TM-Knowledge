# HANDOFF

**Last updated:** 2026-10-16 · S036 (end) · branch `claude/youthful-turing-4x4xa6`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S036 implemented Packages 1 and 2 of `docs/ONTOLOGY-REVIEW-RESPONSE.md`**, on the owner's
instruction: agent work only, no spend, nothing from its "Decisions for the owner". Each probe
in its "How to repeat the checks" is now a test that failed before its fix. Full suite 757
passed; harness 0 defects; SHACL 0 defects, 260 notes; graph rebuilt.

**Package 1 (gates, serving views, declared logic): all done.**
- **F04** Workbench map and decision tree on `served_gold()` (they drew 14 corrected signed
  relationships as reviewed). Nine competency queries filter `tmk:isCorrected`; a test runs
  every query. CQ-0019 also leaked, which the response missed.
- **F01** Functional `tmk:sourcePassage` and the reclassifying domains removed: the provenance
  stamps, and also `approvedBy`/`approvedDate`, `derivedFrom`, `authorityKind`, `conceptGroup`
  and `evidence.ttl`'s stale `establishes`. `test_declarations.py` checks functional, domain and
  datatype declarations without a reasoner. owlrl on GC-0054: no `sameAs`, no errors.
- **F02** `_flatten` includes the inferred graph; `validate.placement` checks each record class
  and origin stamp against its named graph; tests call `validate.run` on a `Dataset`.
- **F03** Pages runs on the harness workflow's success for a push to `main` (`workflow_run`,
  the commit the harness checked). Takes effect once merged: `workflow_run` reads `main`'s file.
- **F07** Decimal confidences; 12 prose ranges `rdf:langString`; **ADR-0134** drops the OWL 2 RL
  claim (no profile, no OWL inference); the cycle shape walks inverse `narrower`; SKOS S27
  check, which reports the signed GC-0017/GC-0018 pair as a note (decision 6).
- **F08** Span, hash and quote required in the envelope schema and the harness.
- **F11** Reports name commit, grade hash and count, rankings hash; `measure --write` writes a
  dated report rather than overwrite one scored on other inputs. Both reports stamped.

**Package 2 (what the edges say): all done**, except what the response itself sends to the owner.
- **F05** The worklist through a second ledger, `data/derived/audit/review-response.yaml`
  (report `data/derived/reports/review-response-edges.md`): 144 lines, 43 re-read or
  re-qualified, 18 withdrawn, 3 new (GR-0705 to GR-0707), 83 checked and kept. Every S029
  re-read is now judged in its current form. Of the seven: six withdrawn, GR-0432 kept with its
  condition. The four audit-disputed replacements of signed records stay the owner's.
  `restructure` now drops a copied modality on a predicate change, takes `--ledger`, `keep:`
  lines and conditions, and never lets an earlier ledger read back a later one's record (Q-93).
- **F13** `prevents` only blocks; `suspendsTimeFor` stops the clock (GR-0259, GR-0534);
  `precedes` reads "must come before".
- **F15** `isAnExceptionTo` (**ADR-0135**); GR-0699 to GR-0702 moved onto it, hedges in
  `applies_when`. `doesNotGiveRiseTo` is "not on its own" in the tree; the equivalence is gone.
- **F18** `establishes` renamed `mayShow` (labels come from names, Q-94) and retired; GR-0206
  moved, GR-0163 and GR-0248 withdrawn.
- **F14** `applies_when` on the schema, harness (verbatim in the sentence), graph
  (`tmk:appliesWhen`), explorer card, table, CSV and workbench map; 26 records carry one. **Not**
  given to the live answering model: decision 4.

Counts: 52 signed + 112 authored concepts; 35 signed relationships (20 current, 15 corrected)
+ 337 authored; all 164 concepts in one connected piece. No spend; recorded US$9.63 against the
US$9.49 cap, so every paid call is still refused.

## Waiting on the owner

1. **The response's nine decisions**, unchanged: re-pin to the Act's compilation 48; lift the
   deferrals on definitions (F4) and stale documents (F5); the two live-chatbot changes (4: modality
   and `applies_when` on the graph path, ready to wire; the rule against concluding absence);
   remove the masked-key fallback; confirm D2 covers GC-0017/GC-0018 (now an S27 note in every
   gate run); branch protection on `main`; the pitch's claims (OQ-0029); an amount to re-measure.
2. **Merge this branch.** It changes records, the graph and the site's code; with F03 in place,
   Pages deploys only once the harness passes on `main`.
3. From S034: the page's blend; ADR-0131; the four disputed signed readings; deploy the proxy.

## Next actions

1. **The blend** (S034, F10): hub concepts ("trade mark", "applicant") enter search expansion
   as neighbours in 15 of 76 questions, and without vectors the linked list breaks ties by ref
   order. Fix before re-measuring, never tuned on the benchmark; `engine.js` and
   `search/index.py` together.
2. **Re-measure** (needs an amount): the measured systems predate S029's and S036's edges.
3. **Remaining heading-only edges** outside the worklist (GR-0270, Madrid Protocol Article 7's
   title, at least, found by reading): no check finds them yet; re-cite or withdraw through a
   ledger.
4. After decision 4: give the answering model each path line's modality and `applies_when`, in
   `jobs.py` and `live.js` together.
5. Package 4 of the response once the owner decides: F12's documents, F06's definitions,
   re-pin and let the staleness check show what moved.
6. Small: `map.js` draws a `CASE/…` ref as a Manual chip; "Wrote an answer…" with live answers
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
- **The live chatbot still gets bare triples** on its graph path (decision 4).
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

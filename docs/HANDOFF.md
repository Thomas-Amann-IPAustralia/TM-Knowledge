# HANDOFF

**Last updated:** 2026-10-16 · S035 (end) · branch `claude/blissful-gauss-f2ygfe`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**S035 checked ChatGPT's ontology review and answered it** in `docs/ONTOLOGY-REVIEW-RESPONSE.md`
(the review: `docs/Trade Mark Ontology Review-15.10.md`). Nothing else changed: no record, graph,
prompt, query or page, and no spend. Every probe was re-run independently, with ChatGPT's library
versions. The review is accurate: 16 of 19 findings agreed outright, 3 in part, none rejected; of
its 20 fixes, 3 agreed, 14 in part, 3 not (sized for production, or sent to an expert whom
ADR-0120 puts at the end). Verified, most urgent first:
- **Machine-written edges that overstate their sentence**, which the explorer shows: GR-0432,
  GR-0167, GR-0521, GR-0140, GR-0437, GR-0495, GR-0454. 124 of the 130 S029 re-reads have never
  been judged in their current form; 30 carry a modality inherited from their earlier reading
  (`restructure` copies every field but the triple); 5 rest on a heading; 14 audit "wrong"
  verdicts still serve. A sample of 24 re-reads: 16 sound, 4 material problems, 4 smaller.
- **The workbench map draws 14 of the 15 corrected signed relationships as reviewed**
  (`dashboard/build.py` passes `goldset.load()` to `views.network`), and 6 of the 8 SPARQL
  competency queries that read signed assertions return corrected records. The explorer and
  search use `served_gold()` and are not affected.
- **Declared logic**: the functional `tmk:sourcePassage` makes Manual and Act sources
  `owl:sameAs` (25 subjects); the provenance domains type every concept as a `tmk:Assertion`; 647
  confidences are `xsd:double` against `xsd:decimal`; 12 `xsd:string` ranges hold `@en-AU` text;
  GC-0017 and GC-0018 are both related and broader (signed); "OWL 2 RL" is claimed and untrue; and
  `Exception ≡ ∃doesNotGiveRiseTo` turns "not on its own" into "exception", live in the workbench's
  decision tree (Q-92).
- **Gates**: `validate._flatten` omits the inferred graph (adding it still gives 0 defects, 259
  notes); placement is invisible after flattening; Pages deploys without waiting for the harness;
  `main` is unprotected; an evidence item needs only a `ref`.
- **Currency**: the pinned Act is compilation 47 (`C2024C00545`, from 14 Oct 2024); the Federal
  Register's current one is 48 (`C2026C00421`, from 19 Sep 2026; Regulatory Reform Omnibus Act
  2026, Sch 1 items 1 and 8 to 12). What changed is not yet known.
- **Measurement**: `tmk-bulk measure` now gives 0.702 / 0.812 / 0.773 against `measure.md`'s
  0.725 / 0.844 / 0.803, because the grade file grew; the comparisons stand (Q-91).

**S034 (still current).** Before searching, the live model reads a typed question against the map
(`reading-v1`) and names up to four ideas, each checked and marked "read by the model" (ADR-0132);
the owner approved it and its cost (ADR-0133). On the page's configuration: reading against names
+0.040 [+0.009, +0.070]; names against keyword -0.041; reading level with keyword. Recorded spend
US$9.63 against the US$9.49 cap, so every paid call is refused until the owner names an amount.
**S033** built `live-proxy/`; **S029** restructured the ontology (ADR-0131). Counts: 52 signed +
112 authored concepts; 35 signed relationships (20 current, 15 corrected) + 352 authored. Harness 0
defects; SHACL 0 defects (but see the gates above).

## Waiting on the owner

1. **The nine decisions in the response** (its "Decisions for the owner"): re-pin upstream to the
   Act's compilation 48; lift the deferrals on definitions (F4) and stale documents (F5); approve
   two live-chatbot changes (modality and conditions on its graph path; never conclude absence);
   remove the masked-key fallback once the proxy serves; confirm D2 covers the GC-0017/GC-0018
   correction; branch protection on `main`; the pitch's claims (OQ-0029); an amount for
   re-measurement.
2. **Merge this branch**: documents only, so nothing deploys.
3. From S034: whether to change the page's blend (next action 3); is the restructure what you
   meant (ADR-0131); the four disputed signed readings (`edge-audit.md`); deploy the proxy and
   revoke the old key (`live-proxy/README.md`).

## Next actions

1. **Package 1 of the response** (agent, no spend, about a session): the workbench's map and
   decision tree on `served_gold()`; `FILTER NOT EXISTS { ?a tmk:isCorrected true }` in the eight
   competency queries, and a test that no query returns a corrected record; drop the functional
   declaration and the `tmk:Assertion` domains, with a test of the data against the ontology's own
   declarations; the inferred graph in `_flatten`, a placement check, tests through
   `validate.run`; Pages after the harness (`workflow_run`); `Decimal` confidence, `rdf:langString`
   ranges, the OWL 2 RL claim dropped by ADR, S27 and two-way cycle checks; span, hash and quote
   required in evidence; report headers carrying the commit and grade hash. Then
   `tmk-graph --write --rules`.
2. **Package 2** (agent, no spend; it changes what examiners see, so first if time is short): the
   F05 worklist through the restructure ledger (the seven edges; the 14 standing audit verdicts;
   the 30 inherited modalities, with `restructure` fixed to clear them; five heading-only edges;
   then the unjudged re-reads); split `prevents`, narrow `precedes`; `isExceptionTo` and the
   tree's "not on its own"; `establishes` read as "may show"; an `applies_when` field. Rebuild.
3. **The blend** (S034): concept-linked passages crowd out good hits (ADR-0133 c4). A candidate
   from the response: generic hubs ("trade mark", "applicant") enter as neighbours in 15 of 76
   questions, and without vectors the linked list breaks ties by ref order. Fix it before
   re-measuring, never tuned on these questions; `engine.js` and `search/index.py` together.
4. **Re-measure** after packages 1 and 2 (needs an amount).
5. The prepared answers (`answers.yaml`) predate S029; re-run them only with a quote.
6. Ideas the reading could not find (a personal name, a slogan, how long registration lasts):
   candidates for `define`, if the owner wants them.
7. Small: `map.js` draws a `CASE/…` ref as a Manual chip; "Wrote an answer…" shows with live
   answers off; "Gathered 0 passages linked to those ideas" when nothing was recognised.
8. B2, B3, B6 postponed; F4, F5 deferred (the response recommends lifting F4 and F5).

## What to distrust

- **The response is one agent's re-run and reading**, unreviewed; its record verdicts (GR-0206
  kept, GR-0140 "in part") and its 24-edge sample are judgements.
- **The workbench map** shows corrected signed relationships as reviewed, until package 1.
- **An OWL reasoner over `graph/`** reports contradictions that are declaration bugs (Q-92).
- **The pinned Act is one compilation behind the law.**
- **The reading is a model's judgement per question**, measured once on model-written questions
  with a model judge; a live answer differs from the measured system when the reading finds an
  idea.
- **Every S029 judgement is one agent's reading of one sentence**, unreviewed, and most were never
  audited in their current form.
- **The published `site/data/ontology.json` still carries the reviewer's initials** (S028).
- **Neither key is tested by a session** (Q-88). **22 legislative bases are unverified.**

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); install with `pip install -e ".[rdf,test]"`;
  about ten minutes. owlrl is not a dependency; install it only to probe (Q-92).
- **`tmk-bulk measure` does not reproduce `measure.md`** (Q-91).
- **Test the page after `tmk-explorer --write`**, then restore a stand-in `live.json` (Q-90).
- **`engine.js` and `search/index.py` change together**, as do `links.find_mentions` and
  `Recogniser`, and `search.authority` and `authorityFlags`. The reading (`read`) is the one
  live-only input; leave its default empty. Its prompt is in `bulk/jobs.py`; its input is built
  twice (`jobs.reading_input`, `live.readingInput`), held equal by `test_explorer.py`.
- **Re-scoring the reading**: `tmk-bulk measure --reading --allow-ungraded 3 --write`.
- **Off-kind edge? Check the kinds first** (Q-86). **Relabelled in a ledger?** Q-87.
- **`tmk-bulk restructure` is idempotent**, and a re-read keeps every field but the triple,
  modality included. **Edit record files block by block** (Q-76).
- **Gemini ignores its schema** (Q-83); **price from completed calls** (Q-85); **hold a paid run
  to the owner's amount** with `TMK_SPEND_CAP_USD` (ADR-0128).
- **`tmk-graph --check` needs `--rules`.** Pass `authored.root` to `corrections.load` (Q-77).
- **`served_gold()` for what serves; `goldset.load()` for what measures.** The workbench's map
  breaks this today.
- **The explorer needs the snapshot**: `tmk-fetch-upstream`, then `tmk-explorer --write`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- **Playwright against a local proxy**: Q-89. **Count kinds with `kindCount()`** in `app.js`.
- **Probing by hand**: `validate_envelope` takes `record_id` as a keyword only; build a
  `jobs.Context` with `bulk.cli._context()`.

## Open items (agent-proposed, provisional)

- The response's recommendations: none acted on; each is the agent's judgement until done or ruled.
- ADR-0133's measurement choices: the page's configuration without vectors, flex tier, one
  reading per question, BN-0015 scored 0.
- ADR-0132's engineering: the reading's prompt and four-idea cap, the checks, running it on every
  live question, the dashed ring, the proxy's separate counting and 2,000-token cap.
- S033's proxy limits (30 an hour per address, 300 a day, 10,000 output tokens).
- S030's table view: its name, tab order, hidden hierarchy, the CSV's columns.
- ADR-0131's agent parts; ADR-0130's ("Reviewed" in grey; the plum hexagon; "At a glance").
- ADR-0127 entire; the agent parts of ADR-0125, ADR-0126 (including the `Exception` mapping the
  response says to revise), ADR-0128, ADR-0129.
- ADR-0122; the agent parts of ADR-0120, ADR-0123, ADR-0124.
- "Too general" labels (E1); ADR-0113, ADR-0115, ADR-0117; agent parts of ADR-0118, ADR-0119.

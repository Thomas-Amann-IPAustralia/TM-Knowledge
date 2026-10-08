# HANDOFF

**Last updated:** 2026-10-08 · S026 (end) · branch `claude/practical-edison-quroky`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The operating model changed: waterfall** (ADR-0120). Nobody signs anything until the
ontology ships to a group of trade marks examiners, who review it all at once. Until
then the bar is "as close to production ready as we can".

**S026 reviewed the ontology (`docs/ONTOLOGY-REVIEW.md`, 40 issues), the owner ruled on
every item (ADR-0121, `review/rulings/2026-10-08-chat-ontology-review.yaml`), and S026
acted on the approved ones.** What changed, in one place each:

- **Duplicates** — 11 authored duplicates withdrawn (A1); the section 43 ground GC-0168
  split from the general GC-0006 (A2); GC-0130 is *reputation of a trade mark* (A3);
  owner ≠ authorised user, wine GIs GC-0169 and the Wine Register GC-0170 (A4).
- **Corrections to signed records** — 29 `GK-` records in `authored/corrections.yaml`,
  outside the signature (D2, ADR-0122). `eval/gold/` is byte-for-byte unchanged. What
  serves uses `corrections.served_gold()`; the approved graph states removals only.
- **Withdrawals** — 105 ids in `authored/retired-ids.yaml`, never reused.
- **Roles and power** (C1–C6, ADR-0123) — role concepts GC-0171 to GC-0180; 12 authority
  predicates (delegation, direction, review, appeal, consent, control, consult,
  escalate …), each `law` or `practice`; consult/escalate edges quote the Manual, never
  the expert's note; `examination.ttl` restructured into offices, delegates, advisers,
  parties, representatives, review bodies, co-regulators; `tmk:roleConcept` bridges.
- **Predicates are defined** (D1) — `ontology/predicates.py`; `relations.ttl` generated
  from it; relate prompt `relate-v2`; an authored edge on an undefined predicate fails.
- **Groups** — a tenth, `remedy` (B5, ADR-0124), placed on the decision tree.
- **Recognition** — longest label wins (C8); not-labels veto (E2); nine too-general
  labels skipped (`authored/too-general-labels.yaml`, E1); aliases narrowed to the
  source's own phrasings, 57 of 725 (E2); apostrophes fold. Python and `engine.js` match.
- **Quality** — 51 duplicate edges withdrawn (D3); 6 dictionary-word concepts withdrawn,
  3 relabelled, define needs two uses in the defined sense (E3); the D5 sample's wrong
  edges fixed and two template-built edges withdrawn; relate now refuses a template quote
  or one that does not name both concepts (D5).
- **Practice vs law** — every chunk is a `tmk:ManualPassage`; answers are checked for
  PU-0004 (`search.authority`, `engine.js`), flagged never removed (F1). Cases are
  administrative, judicial or unclassified by series (C7). Wrong legislative bases fixed;
  22 unverified ones listed by the harness (F3).

Counts: concepts 52 signed + 110 authored; relationships 35 signed (15 replaced by
corrections) + 563 authored. Harness 0 defects; SHACL 0 defects, 0 gaps; graph rebuilt.
No paid call this session. **Spend US$3.49 of the $6.60 cap.**

## Waiting on the owner

1. **The D5 quote** (given in chat 2026-10-08): judge every machine-written edge with a
   second model (Gemini 3.8 Flash recommended, ~US$1.10, ~US$0.55 in batch) and
   re-measure search, which C8/E1/E2 changed (~US$1.50 with the same judge). Nothing
   is spent until he approves. A Gemini client must be added to `tm_knowledge.bulk`
   first (dry-run, `--confirm`, cache, cap, prices in `config.PRICES_PER_MTOK`).
2. **Explained in chat, awaiting a word**: A5, A6, B1 (and so B2, B3, B6), B4, D4, F2, F6.
3. **OQ-0029 — which results the pitch claims.** Unchanged; the measurement is stale
   until re-run (item 1).
4. If not done: the key as an environment secret (`github-pages` → `OPENAI_API_KEY`).

## Next actions

1. On approval of the quote: add the Gemini client, smoke-run 3 calls, read them, run
   the edge audit, fix or withdraw what it finds wrong (by ruling D5), re-measure.
2. Re-run `tmk-bulk run relate` only after the audit: v2 prompt, 125 calls queued.
3. Deferred by the owner: D7 (`related` is now 198 of 563), F4 (definitions as a record
   type), F5 (stale docs — `ontology.md` report, `legal-concepts.ttl` and `GUIDE.md`
   sections beyond §1 and §7).
4. Carried over: an examiner feedback route (notes must never reach a model, ADR-0088).

## What to distrust

- **Everything S026 wrote is machine-written and unreviewed**, stamped
  `claude-code-agent-S026` (Q-75) — concepts GC-0168 to GC-0180, edges GR-0632 to
  GR-0690, 21 re-judged edges, the 29 corrections, the too-general list, the predicate
  definitions, the role class comments.
- **The search measurement describes the old recognition.** Do not quote it as current.
- **238 of 562 concept-to-concept edges quote a sentence that names only one end, or
  neither.** The new relate rule stops more; the existing ones wait for the audit.
- **22 legislative bases are unverified** (harness note) — not wrong, not checked.
- **The prepared answers** were written before the PU-0004 check; none is flagged now.
- The benchmark is model-written and model-graded; the twelve connections in the
  prompt are an accident of identifier order (Q-70).

## Things a session will trip on

- **`python3 -m pytest`, not `pytest`** (Q-29); install with `pip install -e ".[test,rdf]"`.
  The full unit suite takes about nine minutes.
- **Edit record files block by block**, never a YAML round-trip (Q-76).
- **Pass `authored.root` to `corrections.load`** wherever an `AuthoredSet` is in hand (Q-77).
- **`served_gold()` for what serves; `goldset.load()` for what measures.** Never swap them.
- **`engine.js` and `search/index.py` change together**, as do `links.find_mentions`
  and `Recogniser`, and `search.authority` and `authorityFlags` — parity tests fail
  otherwise.
- **The explorer needs the snapshot**: `tmk-fetch-upstream`, `tmk-explorer --write`.
- **`site/data/live.json` can hold a key.** Git-ignored; keep it that way.
- **An agent may not edit a signed record** — write a correction (ADR-0122), and never
  for a preferred label.
- Vectors are not committed (ADR-0115); flex tier overloads (Q-67); never kill a relate
  run (Q-68).

## Open items (agent-proposed, provisional)

- ADR-0122 (the correction mechanism) — agent-proposed.
- The agent parts of ADR-0120, ADR-0123 and ADR-0124: what "production ready" means;
  the role families and the `roleConcept` bridge; honest concurrent use, prior use and
  other circumstances left as exceptions rather than remedies.
- Which labels are "too general" (E1) — a judgement; the `kept` list says why six stayed.
- The decision-series table (`ontology/decisions.py`): IPR, RPC, FSR, AIPC left
  unclassified rather than guessed.
- ADR-0117; ADR-0118's and ADR-0119's agent parts; ADR-0113 and ADR-0115.

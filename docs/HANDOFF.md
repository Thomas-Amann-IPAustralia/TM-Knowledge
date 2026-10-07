# HANDOFF

**Last updated:** 2026-10-07 · S023 (end) · branch `claude/compassionate-pasteur-19firi`,
open as [PR #24](https://github.com/Thomas-Amann-IPAustralia/TM-Knowledge/pull/24) into `main`

Rewritten every session, under 150 lines (ADR-0110). History is in the git log and
`docs/history/`. Rules are in `docs/RULES-IN-FORCE.md`.

## Where things stand

**The demonstrator is built: D1–D3 meet their tests, and D4 is drafted.**
Everything machine-written is unreviewed.

- **D1, the map.** 167 concepts (52 signed, 115 machine-written: GC-0131 to
  GC-0167 plus the earlier authored set) and 608 relationships (35 signed, 573
  machine-written, GR-0059 to GR-0631). **163 of 167 concepts sit in one connected piece**; the map
  has 3 islands, 308 of 312 nodes in the largest. Outside it: GC-0072 *trade mark*
  and GC-0116 *applicant* (generic, never paired by design), GC-0146 *Board* (six
  pairs, all judged unrelated), GC-0126 *protected wine expression* (its label
  never appears verbatim). SHACL 0 defects, harness 0 defects, graph rebuilt.
- **D2, Ask the Manual.** `data/derived/bench/answers.yaml`: 129 answers, each
  with verbatim-located citations (4.7 on average); 81 also cite the Act or
  Regulations; 14 declined the part of a question that asked for an outcome. The
  site's *Ask the Manual* page shows them beside plain keyword search.
- **D3, the measurement.** `data/derived/reports/measure.md`. 129 questions (119 by
  `gpt-5.4-mini` + the expert's 10 signed), 2,236 pooled passages graded by
  `gpt-6.1-sol`. nDCG@10: keyword 0.726, hybrid 0.845, ontology 0.795. Ontology −
  keyword **+0.069 [+0.031, +0.108]** (everyday questions +0.132); ontology −
  hybrid **−0.050 [−0.079, −0.024]**: established *worse*. Expert's 10: nothing
  established.
- **D4, the pitch pack.** `docs/PITCH-PACK.md` (repo copy, screenshots in
  `docs/pitch/`) and a private 12-slide deck only the owner can open:
  <https://claude.ai/artifact/A8w4WZ99aFkm1w4MyfQrFA>. It reports and claims
  nothing; **which results to claim is the owner's (OQ-0029)**.
- **Spend: US$3.46 of the $6.60 cap** (ADR-0114). `tmk-bulk spend` is live.
- 600 tests pass.

## Waiting on the owner

1. **OQ-0029 — which results the pitch claims.** Options in the question; nothing
   else is blocked by it.
2. Whether a design system should restyle the deck (one exists, "Design System",
   not set as default; the deck uses its own neutral look).

## Next actions

1. **If the owner picks "test the fix first" (OQ-0029):** implement the
   exploratory variant as a fourth system, pool its top ten on the *test* half
   only (`sha256("split-" + key) % 2 == 1`), grade the new passages (a few cents),
   report it beside the pre-registered result — never instead of it. The variant:
   a recognised concept counts only if named in ≤ 100 passages; the expanded and
   linked lists get RRF weight 0.25; expansion uses the concept's labels plus its
   neighbours' preferred labels. Development-half score: +0.004 to +0.008 vs
   hybrid, 99% of its top tens already graded. The script was scratch; rebuild
   it from `cli.search_systems` and `search.index.Systems`.
2. Merge-candidates for a person: 12 relate judgements said "same concept" (e.g.
   GC-0046 *Registrar* / GC-0115 *Registrar of Trade Marks*, which double-counts in
   search). Listed in the relate cache; `jobs.judged_pairs` shows how to read it.
3. An expert sample of the machine's work (pitch step 1) — needs the owner to
   arrange an expert; nothing an agent can do alone.

## What to distrust

- **The benchmark is model-written and model-graded.** The expert's 10 questions
  are the only human yardstick and are too few to establish anything.
- **The search finding is about this configuration.** Two of the ontology
  system's four fused lists come from recognised concepts, however common;
  "Registrar" (442 passages) floods results. Diagnosed after measuring.
- **Concept recognition is label matching.** "who has to *sign*" matches the
  concept *sign*; everyday phrasings (`aliases.yaml`) widen it further.
- **`define` judged 8 terms "not a concept"** and they are now skipped for good
  (`Context.defined`); a session that wants them re-asked must say so.
- **The bulk reports in `data/derived/reports/bulk-*.md` describe the last run
  of each job**, not the whole job: relate's latest covers its final 7-call pass.
  The judge report was replayed from cache to cover all 129.

## Things a session will trip on

- **Vectors are not committed** (ADR-0115). A fresh container runs
  `tmk-bulk embed --confirm` (about a cent) before `pools` or `answer`; both refuse
  without vectors.
- **Flex is the default tier**; on 2026-10-07 most attempts (65–85%) came back
  "overloaded", free, and were retried up to 12 times (Q-67). Batches stalled.
- **Never kill a relate run**: it writes only at the end, and the pairs it has
  answered count as judged, so a re-run would not write them (Q-68).
- **A relate pass beside another** must use `--touching <ids>` or it duplicates
  the other's pairs (Q-68).
- **The approved graph points at one authored concept** (CQ-0007 → GC-0154) by
  design; the boundary ruling stands (ADR-0116).
- **Q-65/Q-66**: the proxy supplies OpenAI credentials; long requests use
  background mode.

## Open items (agent-proposed, provisional)

- ADR-0113 (how the pipeline writes knowledge) and ADR-0115 (numpy extra, vectors
  not committed). ADR-0116 is `derived`; ADR-0114 is `human`.
- The "129 not 130" correction is recorded in the quote-approval ruling.

# Stage 0 — coverage and gaps

**Generated** 2026-09-02 · **Source** `eval/gold/` against the pinned snapshot `c490a9927f1a` · **Regenerate** `tmk-coverage`

This report is **derived**. It counts what `eval/gold/` holds against the definition of done in `eval/STAGE-0-INPUT-GUIDE.md` §7, and it names what is absent. It does not propose content for any gap, and it must not be read as doing so: every field it reports as empty is one only a domain expert may fill (CLAUDE.md rule 1, guide §9).

**Status:** 0 defect(s), 16 gap(s), 1 note(s); Stage 0 incomplete.

## 1. The board

| Deliverable | Target | Have | Status |
|---|---|---|---|
| Pilot scope, with exclusions | eval/pilot-scope.md | — | not written |
| Competency questions, covering all six categories | at least 6 | 19 | in band |
| Prohibited uses, covering all six kinds | at least 6 | 2 | 4 short |
| Gold concepts | 50–100 | 52 | in band |
| Gold entities, over an exhaustively annotated chunk set | 100–300 | 0 | 100 short |
| Gold relationships | 50–100 | 34 | 16 short |
| Search questions | 20–50 | 1 | 19 short |
| AI retrieval questions | 20–50 | 0 | 20 short |
| Reasoning expectations | at least 1 | 0 | 1 short |
| A threshold against every metric | eval/measures.md | — | not written |

## 2. Defects

None. Everything in `eval/gold/` is well formed and lands where it says.

## 3. Gaps

### Deliverables not yet delivered

- **eval/pilot-scope.md** — Pilot scope, with exclusions — not written
- **prohibited-uses.yaml** — Prohibited uses, covering all six kinds — 2 of at least 6
- **entities.yaml** — Gold entities, over an exhaustively annotated chunk set — 0 of 100–300
- **relationships.yaml** — Gold relationships — 34 of 50–100
- **search-questions.yaml** — Search questions — 1 of 20–50
- **retrieval-questions.yaml** — AI retrieval questions — 0 of 20–50
- **reasoning-expected.yaml** — Reasoning expectations — 0 of at least 1
- **eval/measures.md** — A threshold against every metric — not written

### Coverage the definition of done requires

- **prohibited-use kind 'authority_conflation'** — no record carries it. §7 requires the set to span all 6
- **prohibited-use kind 'unsupported_inference'** — no record carries it. §7 requires the set to span all 6
- **prohibited-use kind 'stale_source'** — no record carries it. §7 requires the set to span all 6
- **prohibited-use kind 'ambiguity_collapse'** — no record carries it. §7 requires the set to span all 6

### Judgement fields left empty — only an expert may close these

- **GR-0006** — modality is null — it needs the expert, and nothing here may supply it
- **GR-0013** — modality is null — it needs the expert, and nothing here may supply it
- **GR-0015** — modality is null — it needs the expert, and nothing here may supply it
- **GR-0040** — modality is null — it needs the expert, and nothing here may supply it

## 4. Coverage by category

Both lists are read from the schemas, not restated here. §7 requires the set as a whole to span each of them; which value a given record carries is the expert's call.

**Competency questions**

| `category` | records |
|---|---|
| retrieval | 2 |
| search | 4 |
| reasoning | 4 |
| currency | 1 |
| impact | 4 |
| provenance | 4 |

**Prohibited uses**

| `kind` | records |
|---|---|
| evaluative_conclusion | 1 |
| authority_conflation | 0 |
| unsupported_inference | 0 |
| stale_source | 0 |
| overreach | 1 |
| ambiguity_collapse | 0 |

## 5. Worth an eye, gating nothing

- **PU-0015** (test_ref) — detectable_by: test, but no test_ref yet

## 6. Where the records are

| Record type | File | Records |
|---|---|---|
| competency_question | `eval/gold/competency-questions.yaml` (present) | 19 |
| gold_concept | `eval/gold/concepts.yaml` (present) | 52 |
| gold_entity | `eval/gold/entities.yaml` (absent) | 0 |
| gold_relationship | `eval/gold/relationships.yaml` (present) | 34 |
| gold_retrieval_question | `eval/gold/retrieval-questions.yaml` (absent) | 0 |
| gold_search_question | `eval/gold/search-questions.yaml` (present) | 1 |
| prohibited_use | `eval/gold/prohibited-uses.yaml` (present) | 2 |
| reasoning_expectation | `eval/gold/reasoning-expected.yaml` (absent) | 0 |


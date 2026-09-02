# Stage 0 — coverage and gaps

**Generated** 2026-09-02 · **Source** `eval/gold/` against the pinned snapshot `c490a9927f1a` · **Regenerate** `tmk-coverage`

This report is **derived**. It counts what `eval/gold/` holds against the definition of done in `eval/STAGE-0-INPUT-GUIDE.md` §7, and it names what is absent. It does not propose content for any gap, and it must not be read as doing so: every field it reports as empty is one only a domain expert may fill (CLAUDE.md rule 1, guide §9).

**Status:** 0 defect(s), 12 gap(s), 10 note(s); Stage 0 incomplete.

## 1. The board

| Deliverable | Target | Have | Status |
|---|---|---|---|
| Pilot scope, with exclusions | eval/pilot-scope.md | — | not written |
| Competency questions, covering all six categories | at least 6 | 20 | in band |
| Prohibited uses, covering all six kinds | at least 6 | 11 | in band |
| Gold concepts | 50–100 | 52 | in band |
| Gold entities, over an exhaustively annotated chunk set | 100–300 | 55 | 45 short |
| Gold relationships | 50–100 | 35 | 15 short |
| Search questions | 20–50 | 1 | 19 short |
| AI retrieval questions | 20–50 | 10 | 10 short |
| Reasoning expectations | at least 1 | 6 | in band |
| A threshold against every metric | eval/measures.md | — | not written |

## 2. Defects

None. Everything in `eval/gold/` is well formed and lands where it says.

## 3. Gaps

### Deliverables not yet delivered

- **eval/pilot-scope.md** — Pilot scope, with exclusions — not written
- **entities.yaml** — Gold entities, over an exhaustively annotated chunk set — 55 of 100–300
- **relationships.yaml** — Gold relationships — 35 of 50–100
- **search-questions.yaml** — Search questions — 1 of 20–50
- **retrieval-questions.yaml** — AI retrieval questions — 10 of 20–50
- **eval/measures.md** — A threshold against every metric — not written

### Coverage the definition of done requires

- **prohibited-use kind 'stale_source'** — no record carries it. §7 requires the set to span all 6

### Judgement fields left empty — only an expert may close these

- **GR-0006** — modality is null — it needs the expert, and nothing here may supply it
- **GR-0013** — modality is null — it needs the expert, and nothing here may supply it
- **GR-0015** — modality is null — it needs the expert, and nothing here may supply it
- **GR-0017** — modality is null — it needs the expert, and nothing here may supply it
- **GR-0040** — modality is null — it needs the expert, and nothing here may supply it

## 4. Coverage by category

Both lists are read from the schemas, not restated here. §7 requires the set as a whole to span each of them; which value a given record carries is the expert's call.

**Competency questions**

| `category` | records |
|---|---|
| retrieval | 3 |
| search | 4 |
| reasoning | 4 |
| currency | 1 |
| impact | 4 |
| provenance | 4 |

**Prohibited uses**

| `kind` | records |
|---|---|
| evaluative_conclusion | 3 |
| authority_conflation | 3 |
| unsupported_inference | 3 |
| stale_source | 0 |
| overreach | 1 |
| ambiguity_collapse | 1 |

## 5. Worth an eye, gating nothing

- **PU-0003** (test_ref) — detectable_by: test, but no test_ref yet
- **PU-0005** (test_ref) — detectable_by: test, but no test_ref yet
- **PU-0015** (test_ref) — detectable_by: test, but no test_ref yet
- **GA-0007** (resolution) — .required_cases[0] = CASE/1968/HCA/72 is a case citation. No decision text exists anywhere in the programme, so it is checked for grammar only (Q-11)
- **GA-0007** (resolution) — .required_cases[1] = CASE/2003/ATMO/7 is a case citation. No decision text exists anywhere in the programme, so it is checked for grammar only (Q-11)
- **GA-0009** (resolution) — .required_cases[0] = CASE/2017/FCAFC/174 is a case citation. No decision text exists anywhere in the programme, so it is checked for grammar only (Q-11)
- **GA-0009** (resolution) — .required_cases[1] = CASE/2010/ATMO/85 is a case citation. No decision text exists anywhere in the programme, so it is checked for grammar only (Q-11)
- **GA-0011** (resolution) — .required_cases[0] = CASE/2000/FCA/720 is a case citation. No decision text exists anywhere in the programme, so it is checked for grammar only (Q-11)
- **GA-0012** (resolution) — .required_cases[0] = CASE/2009/FCA/428 is a case citation. No decision text exists anywhere in the programme, so it is checked for grammar only (Q-11)
- **GA-0013** (resolution) — .required_cases[0] = CASE/2012/ATMO/117 is a case citation. No decision text exists anywhere in the programme, so it is checked for grammar only (Q-11)

## 6. Where the records are

| Record type | File | Records |
|---|---|---|
| competency_question | `eval/gold/competency-questions.yaml` (present) | 20 |
| gold_concept | `eval/gold/concepts.yaml` (present) | 52 |
| gold_entity | `eval/gold/entities.yaml` (present) | 55 |
| gold_relationship | `eval/gold/relationships.yaml` (present) | 35 |
| gold_retrieval_question | `eval/gold/retrieval-questions.yaml` (present) | 10 |
| gold_search_question | `eval/gold/search-questions.yaml` (present) | 1 |
| prohibited_use | `eval/gold/prohibited-uses.yaml` (present) | 11 |
| reasoning_expectation | `eval/gold/reasoning-expected.yaml` (present) | 6 |


# Stage 0 — coverage and gaps

**Generated** 2026-09-09 · **Source** `eval/gold/` and `authored/` against the pinned snapshot `c490a9927f1a` · **Regenerate** `tmk-coverage`

This report is **derived**. It counts what `eval/gold/` holds against the definition of done in `eval/STAGE-0-INPUT-GUIDE.md` §7, and it names what is absent. It does not propose content for any gap, and it must not be read as doing so: every field it reports as empty is one only a domain expert may fill (CLAUDE.md rule 1, guide §9).

**Status:** 0 defect(s), 12 gap(s), 10 note(s); Stage 0 incomplete.

## 1. The board

**Signed** counts `eval/gold/` — records a named expert put their name to. **Authored** counts `authored/` — records a machine wrote that nobody has read. The two are never added, and only the signed column is measured against the target: a band met by unreviewed records would report Stage 0 finished on the strength of work nobody has looked at (ADR-0080).

| Deliverable | Target | Signed | Authored | Status |
|---|---|---|---|---|
| Competency questions, covering all six categories | at least 6 | 20 | 0 | in band |
| Prohibited uses, covering all six kinds | at least 6 | 11 | 0 | in band |
| Gold concepts | 50–100 | 52 | 78 | in band |
| Gold entities, over an exhaustively annotated chunk set | 100–300 | 55 | 0 | 45 short |
| Gold relationships | 50–100 | 35 | 0 | 15 short |
| Search questions | 20–50 | 1 | 0 | 19 short |
| AI retrieval questions | 20–50 | 10 | 0 | 10 short |
| Reasoning expectations | at least 1 | 6 | 0 | in band |
| Concepts sorted into one of the four groups | 50–100 | 0 | 130 | 50 short |
| A threshold against every metric | eval/measures.md | — | — | not written |

## 2. Defects

None. Everything in `eval/gold/` and `authored/` is well formed and lands where it says.

## 3. Gaps

### Deliverables not yet delivered

- **entities.yaml** — Gold entities, over an exhaustively annotated chunk set — 55 of 100–300
- **relationships.yaml** — Gold relationships — 35 of 50–100
- **search-questions.yaml** — Search questions — 1 of 20–50
- **retrieval-questions.yaml** — AI retrieval questions — 10 of 20–50
- **concept-types.yaml** — Concepts sorted into one of the four groups — 0 of 50–100
- **eval/measures.md** — A threshold against every metric — not written

### Coverage the definition of done requires

- **prohibited-use kind 'stale_source'** — no record carries it. §7 requires the set to span all 6

### Judgement fields left empty — only an expert may close these

- **GR-0006** — modality is null in a signed record. An agent may author this judgement (ADR-0079) but may not write it here — that would put unreviewed content inside a signature. It needs either the expert or a record type of its own, the way a concept's type got one (ADR-0071)
- **GR-0013** — modality is null in a signed record. An agent may author this judgement (ADR-0079) but may not write it here — that would put unreviewed content inside a signature. It needs either the expert or a record type of its own, the way a concept's type got one (ADR-0071)
- **GR-0015** — modality is null in a signed record. An agent may author this judgement (ADR-0079) but may not write it here — that would put unreviewed content inside a signature. It needs either the expert or a record type of its own, the way a concept's type got one (ADR-0071)
- **GR-0017** — modality is null in a signed record. An agent may author this judgement (ADR-0079) but may not write it here — that would put unreviewed content inside a signature. It needs either the expert or a record type of its own, the way a concept's type got one (ADR-0071)
- **GR-0040** — modality is null in a signed record. An agent may author this judgement (ADR-0079) but may not write it here — that would put unreviewed content inside a signature. It needs either the expert or a record type of its own, the way a concept's type got one (ADR-0071)

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

## 6. Where the signed records are

| Record type | File | Records |
|---|---|---|
| competency_question | `eval/gold/competency-questions.yaml` (present) | 20 |
| concept_type | `eval/gold/concept-types.yaml` (absent) | 0 |
| gold_concept | `eval/gold/concepts.yaml` (present) | 52 |
| gold_entity | `eval/gold/entities.yaml` (present) | 55 |
| gold_relationship | `eval/gold/relationships.yaml` (present) | 35 |
| gold_retrieval_question | `eval/gold/retrieval-questions.yaml` (present) | 10 |
| gold_search_question | `eval/gold/search-questions.yaml` (present) | 1 |
| prohibited_use | `eval/gold/prohibited-uses.yaml` (present) | 11 |
| reasoning_expectation | `eval/gold/reasoning-expected.yaml` (present) | 6 |

## 7. The authored store

**208 record(s), none of them validated by a trade marks expert.** They may be relied on and they may be served, always carrying that status at the point of use (ADR-0082). None of them becomes approved by being old, by being unchallenged, or by having appeared in a review round somebody worked through — only a signature moves a record, and only `tmk-transcribe` writes one (ADR-0086).

| Record type | File | Authored | Signed |
|---|---|---|---|
| competency_question | `authored/competency-questions.yaml` (absent) | 0 | 20 |
| concept_type | `authored/concept-types.yaml` (present) | 130 | 0 |
| gold_concept | `authored/concepts.yaml` (present) | 78 | 52 |
| gold_entity | `authored/entities.yaml` (absent) | 0 | 55 |
| gold_relationship | `authored/relationships.yaml` (absent) | 0 | 35 |
| gold_retrieval_question | `authored/retrieval-questions.yaml` (absent) | 0 | 10 |
| gold_search_question | `authored/search-questions.yaml` (absent) | 0 | 1 |
| prohibited_use | `authored/prohibited-uses.yaml` (absent) | 0 | 11 |
| reasoning_expectation | `authored/reasoning-expected.yaml` (absent) | 0 | 6 |

**What each record rests on**

| `authoring_basis` | records | means |
|---|---|---|
| corpus_explicit | 91 | the corpus states it in terms; the span shows where |
| corpus_inferred | 117 | the corpus supports it, but the reading is the agent's |
| general_knowledge | 0 | **the corpus does not say this** — written from what the model knows about trade marks law. Unevidenced, not thereby wrong, and a reviewer reaches these first |


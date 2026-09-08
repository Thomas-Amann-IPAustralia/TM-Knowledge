# eval/gold/ — the gold-standard dataset

The expert-approved trusted examples, one file per record type. **No longer
empty** — the first review round landed 108 records here on 2026-09-02
(ADR-0048). The names are fixed, because `tm_knowledge.stage0.goldset` reads
them by name:

| File | Record type | Target (guide §7) |
|---|---|---|
| `competency-questions.yaml` | competency question | all six categories covered |
| `prohibited-uses.yaml` | prohibited use | all six `kind` values covered |
| `concepts.yaml` | gold concept | 50–100 |
| `entities.yaml` | gold entity | 100–300 |
| `relationships.yaml` | gold relationship | 50–100 |
| `search-questions.yaml` | gold search question | 20–50 |
| `retrieval-questions.yaml` | AI retrieval question | 20–50 |
| `reasoning-expected.yaml` | reasoning expectation | recorded, each with `must_not_infer` |
| `concept-types.yaml` | concept type | one per approved concept |

Each file is a **YAML list of records**, validated against `../schemas/`. There is
no other layout: a record type split across two files, or a file with a name not
in that table, **stops the harness** rather than being skipped. A gold file
quietly ignored because its name was misspelt is a set of expert judgements that
silently did not count.

`concept-types.yaml` is the ninth and is not one of the guide's eight. It was
added on 2026-09-08 when the owner confirmed the four groups (OQ-0001,
ADR-0071). Each record puts one approved concept into one of them, and it is a
separate record rather than a field on the concept because the concept was
signed by one person on one date and the typing is a second judgement — writing
it into the signed record would put unsigned content inside a signature.
`tmk-typing` lays the pass out as a spreadsheet; `tmk-transcribe` reads it back
through the same single door as everything else here.

`retired-ids.yaml` is the one non-record file, and it is optional. It lists ids
withdrawn from service so that a later allocation cannot walk back into one —
`IDENTIFIERS.md` §3 allocates by appending and never fills a gap left by a
withdrawal. Its absence means nothing has been withdrawn, which is the normal
state.

```yaml
# retired-ids.yaml
- id: GC-0042
  retired_on: "2026-08-19"
  reason: "why the record was withdrawn"
```

**Belongs here:** records approved by a domain expert, each citing an exact
passage by upstream ref, span and `content_hash`.

**How a record gets here.** One door only: `tmk-transcribe` reading a workbook
in which a person wrote `correct` in the `verdict` column **and** put their name
in `approved_by`. Nothing else — not a hand copy out of `review/seed/`, not an
agent deciding a candidate is obviously fine. And a record is refused even with
a signature if it names a record that is not itself approved, because a gold set
with a dangling pointer is not a measurement standard (ADR-0048).

**Does not belong here:** machine-generated candidates (they go to `review/`),
records without a supporting passage, records an agent authored. A gold set
contaminated by model output measures the model against itself and will look
excellent while being worthless. The fixtures in `tests/fixtures/harness/` are
not examples to copy — every judgement field in them is a placeholder on purpose.

Records are versioned in git. When a record changes, the change should be
reviewable as a diff, so keep one record per block and avoid reformatting whole
files.

A record whose `source_content_hash` no longer matches upstream is **stale**: the
passage it rests on has changed. Stale records fail the harness and return to the
expert; they are not silently refreshed.

## Checking what is here

```bash
tmk-harness    # every check, and what Stage 0 is still waiting on
tmk-coverage   # the same, rendered as a worklist → data/derived/reports/
```

A gap is not a failure — it is work that has not arrived. A **defect** is: a
record that does not validate, a duplicated or retired id, a dangling
cross-reference, a `source_ref` that resolves to nothing, a `span` that does not
land on its recorded text, or a stale hash. ADR-0018.

# eval/gold/ — the gold-standard dataset

Empty. The expert-created trusted examples go here, one file per record type.
The names are fixed, because `tm_knowledge.stage0.goldset` reads them by name:

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

Each file is a **YAML list of records**, validated against `../schemas/`. There is
no other layout: a record type split across two files, or a file with a name not
in that table, **stops the harness** rather than being skipped. A gold file
quietly ignored because its name was misspelt is a set of expert judgements that
silently did not count.

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

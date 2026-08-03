# eval/gold/ — the gold-standard dataset

Empty. The expert-created trusted examples go here, one file per record type,
using the schemas in `../templates/gold-record.template.yaml`:

```
entities.yaml          100–300 recognised entities
concepts.yaml           50–100 approved concepts
relationships.yaml      50–100 known relationships
search-questions.yaml   20–50
retrieval-questions.yaml 20–50
reasoning-expected.yaml  expected inferences
```

**Belongs here:** records approved by a domain expert, each citing an exact
passage by upstream ref, span and `content_hash`.

**Does not belong here:** machine-generated candidates (they go to `review/`),
records without a supporting passage, records an agent authored. A gold set
contaminated by model output measures the model against itself and will look
excellent while being worthless.

Records are versioned in git. When a record changes, the change should be
reviewable as a diff, so keep one record per block and avoid reformatting whole
files.

A record whose `source_content_hash` no longer matches upstream is **stale**: the
passage it rests on has changed. Stale records fail the harness and return to the
expert; they are not silently refreshed.

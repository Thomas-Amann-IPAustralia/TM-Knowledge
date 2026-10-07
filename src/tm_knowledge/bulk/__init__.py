"""The pipeline that fills the ontology in bulk (ADR-0110, ADR-0111).

Two halves, in the order the KB SOP and CLAUDE.md rule 7 both insist on:

- `links` — **free and deterministic.** Which Manual passages name which concept,
  and which concept pairs are worth asking a model about. No model, no spend, no
  judgement, so nothing in it needs review.
- `client` and `jobs` — **the one paid stage.** OpenAI's `gpt-6.1-sol` at medium
  effort, JSON-schema output, every response cached in `data/llm/cache/` and
  committed, every call checked against the spend cap before it is made. Code,
  not the model, writes the provenance: it finds each quote verbatim in the
  snapshot, computes the span and hash, and stamps the record `unreviewed`.

`quote` turns what the smoke runs measured into a price for the full runs.
`tmk-bulk` is the command line.
"""

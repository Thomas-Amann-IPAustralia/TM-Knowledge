# eval/schemas/ — the machine-checkable face of the templates

One JSON Schema per Stage 0 record type, plus `common.schema.json` for the
definitions they share. `eval/templates/*.yaml` is what a person reads; this is
what the validator enforces. `tests/unit/test_stage0_schemas.py` asserts the two
describe the same record, so neither can drift from the other unnoticed.

| Schema | Records | Id series |
|---|---|---|
| `competency-question.schema.json` | Competency questions | `CQ-` |
| `gold-entity.schema.json` | Recognised entities | `GE-` |
| `gold-concept.schema.json` | Approved concepts | `GC-` |
| `gold-relationship.schema.json` | Known relationships | `GR-` |
| `gold-search-question.schema.json` | Search questions | `GS-` |
| `gold-retrieval-question.schema.json` | AI retrieval questions | `GA-` |
| `reasoning-expectation.schema.json` | Expected reasoning results | `GX-` |
| `prohibited-use.schema.json` | Prohibited uses | `PU-` |
| `concept-type.schema.json` | Which of four groups a concept is in | `GT-` |
| `authored-envelope.schema.json` | **Not a record type** — the block every record in `authored/` carries | — |

## What belongs here

Shape: field presence, types, enum membership, id patterns, ref syntax, and the
presence of `approved_by` / `approved_date`.

**`authored-envelope.schema.json` is the odd one and worth reading first.** It
validates a block *inside* a record rather than a record, and it is what makes
ADR-0079's prohibition on laundering mechanical: a record that cannot declare
its model, its date, its evidential basis and its reasoning is not written. It
is reached through `schemas.validator_for_file`, on the same registry as every
record type, so its `evidence[].ref` gets exactly the `upstream-ref` check a
signed record's `source_ref` gets. There is no second validator.

## What must never go here

**A judgement.** A schema may say a `modality` is one of three words; it may
never say which one is right. If a schema could reject a record an expert wrote
correctly, it has encoded a legal reading, and writing one is outside this
repo's authority (CLAUDE.md rule 1).

Two consequences that look like laxity and are deliberate:

- **Judgement fields are required-but-nullable.** The key must be there, so the
  gap is visible; the value may be null, so an agent transcribing an expert's
  words never has to invent the parts they did not say (parallel track P8). Null
  is what the coverage report counts as a gap (P10) and what the completeness
  gate fails on (P5) — different checks, on purpose.
- **`predicate` is not an enum.** The approved relationship dictionary is
  expert-owned and does not exist yet. Listing plausible predicates here would
  be an agent authoring it. When the dictionary lands, the enum is generated
  from it rather than written by hand.

## Conventions

`$id`s sit under `https://ipaustralia.gov.au/schemas/tmk/…`, matching upstream's
`schema/*.json`. That is deliberately **not** the project base IRI: the base is
unconfirmed (HANDOFF Q7) and lives in one constant read by `refs.py`, and a
schema id is a name for a document, not a resource this project publishes.

Cross-schema `$ref`s use `common.schema.json`'s absolute `$id`. Relative refs
resolve against the referring schema's own `$id` and silently miss.

The `format: upstream-ref` keyword is checked by `tm_knowledge.refs.parse_ref`,
so the ref grammar has one authority and the schemas do not restate it.

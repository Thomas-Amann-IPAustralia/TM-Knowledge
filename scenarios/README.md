# scenarios/ — fictional matters for the customer explanation aid

**Everything here is invented.** Each file holds fictional applications, examination
reports and histories, written to build and test the customer slice (the second review
response's Package 4; ADR-0138, ADR-0142). Every record says `fictional: true`, names
the acceptance example it exercises, and is validated by
`eval/schemas/fictional-matter.schema.json` and `tm_knowledge.explain.matters`.

## What belongs here

- `matters.yaml` — fictional matters (`FM-` ids, their own series: they are fixtures,
  not knowledge, and never enter the graph or a measurement).

## What must not go here

- **No real application, examination report, applicant, attorney or examiner**, in
  whole or in part, until the owner allows real customer or case data (`CLAUDE.md`
  §3a). A name that might be a real business is changed, not kept.
- No legal content. A matter refers to the legal tests (`GL-`) and the process template
  (`GP-`) in `authored/`; it never states what the law requires.
- No outcome. A matter records what its fictional report says the Registrar believes and
  what has happened; the explanation built from it never says what will happen.

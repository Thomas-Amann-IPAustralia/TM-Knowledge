# scenarios/ — fictional matters and fictional amendments

**Everything here is invented.** Each file holds fictional applications, examination
reports and histories, written to build and test the customer slice (the second review
response's Package 4; ADR-0138, ADR-0142). Every record says `fictional: true`, names
the acceptance example it exercises, and is validated by
`eval/schemas/fictional-matter.schema.json` and `tm_knowledge.explain.matters`.

## What belongs here

- `matters.yaml` — fictional matters (`FM-` ids, their own series: they are fixtures,
  not knowledge, and never enter the graph or a measurement). FM-0001 to FM-0004 are the
  review's acceptance examples (S042); FM-0005 (evidence covering the wrong period) and
  FM-0006 (an objection known only from the customer's everyday words) are from A12's
  list (S043). An objection whose ground is not known says `test: null` and carries the
  customer's words; it may record no facts, assessments or exhibits, because those belong
  to a test.

- `amendments.yaml` — fictional amendments (`FS-`, S045, ADR-0147): normative scenarios
  (the second review response, A10). Each is an invented draft of one provision, read as
  edits to that provision's legal test (`GL-`), naming the compilation whose text it
  amends, and run on fictional matters: `tmk-explain --scenario FS-0001` (or `all`) prints
  the records resting on the provision, how each matter's reading would change, and that
  the behavioural effect is unknown. Validated by
  `eval/schemas/fictional-amendment.schema.json` and `tm_knowledge.explain.scenarios`.

## What must not go here

- **No real draft, bill, exposure draft or policy proposal.** A scenario is invented to
  show the mechanism; a real one is policy content the owner has not asked for, and its
  words would sit beside the law. A draft's words never enter the graph, the search index,
  the site or a prompt (a test checks the graph, the site's data and `authored/`).

- **No real application, examination report, applicant, attorney or examiner**, in
  whole or in part, until the owner allows real customer or case data (`CLAUDE.md`
  §3a). A name that might be a real business is changed, not kept.
- No legal content. A matter refers to the legal tests (`GL-`) and the process template
  (`GP-`) in `authored/`; it never states what the law requires.
- No outcome. A matter records what its fictional report says the Registrar believes and
  what has happened; the explanation built from it never says what will happen.

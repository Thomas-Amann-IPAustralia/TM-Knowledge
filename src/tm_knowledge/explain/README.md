# tm_knowledge.explain — the customer explanation aid's engine (Package 4)

Builds one **explanation object** for a fictional matter from the legal tests and the
process template in `authored/` (ADR-0142), and renders it as plain text. Every view the
customer page draws comes from the same object, so a changed fact changes the prose and
the picture together (A09).

- `matters.py` — reads `scenarios/matters.yaml` and checks each matter against the
  tests and the template it names.
- `engine.py` — the three-valued reading of a test, the matter's place in the process,
  the evidence view, and `explain()` / `render_text()`. With no matter (S043):
  `requirements()` / `render_requirements()` explain one test as the law and the Manual
  state it, and `walkthrough()` / `render_walkthrough()` one process template step by
  step. An objection known only from the customer's words is never matched to a ground:
  the explanation names the grounds it holds tests for and asks which the report cites.
- `scenarios.py` (S045, A10) — a fictional amendment (`scenarios/amendments.yaml`, `FS-`)
  read as edits to a copy of one legal test, every changed element labelled draft; each
  of its fictional matters explained under the test as held and as drafted, and the two
  compared element by element; beside that, the records resting on the amended provision
  (the dependency index) and the behavioural effect stated unknown. Three layers, never
  summed. The draft never reaches the graph, the index, the site or a prompt.
- Each explanation also says which text of the law it quotes and what can be said of the
  text in force on the filing date (`tm_knowledge.versions`, A03): held, earlier than any
  held, after the capture, or not known because no date is given.
- `page.py` — the three views (issue card, process timeline, evidence-to-issue), each
  with its text equivalent, then the general views (each test's requirements, and the
  process from filing drawn as a flow), as one standalone page.
- `cli.py` — `tmk-explain [--matter FM-0001] [--test GL-0001] [--process GP-0002]
  [--html PATH] [--scenario FS-0001|all]`. The page is written to a file for the owner.

The same objects are on the examiner site as a preview (`#/customers`, ADR-0146):
`tmk-explorer` writes them to `site/data/explain.json` and the page draws them under a
banner. That is not showing them to customers; testing with customers or publishing to
them stays the owner's decision (`CLAUDE.md` §3a).

What it must never do: state an outcome, compute a date, turn a "may" into a "must",
make an evaluative assessment, or ask for a fact that would not change the explanation.
`tests/unit/test_explain.py` holds each of these; `tests/unit/test_scenarios.py` holds the
same for a scenario, and that its draft stays out of everything operative.

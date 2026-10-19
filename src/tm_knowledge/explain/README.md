# tm_knowledge.explain — the customer explanation aid's engine (Package 4)

Builds one **explanation object** for a fictional matter from the legal tests and the
process template in `authored/` (ADR-0142), and renders it as plain text. Every view the
customer page draws comes from the same object, so a changed fact changes the prose and
the picture together (A09).

- `matters.py` — reads `scenarios/matters.yaml` and checks each matter against the
  tests and the template it names.
- `engine.py` — the three-valued reading of a test, the matter's place in the process,
  the evidence view, and `explain()` / `render_text()`.

What it must never do: state an outcome, compute a date, turn a "may" into a "must",
make an evaluative assessment, or ask for a fact that would not change the explanation.
`tests/unit/test_explain.py` holds each of these.

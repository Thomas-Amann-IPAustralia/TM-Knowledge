# data/derived/audit/ — a second model's verdict on the machine-written relationships

`edges.yaml` — one verdict per machine-written relationship in `authored/`, written by
`tmk-bulk run audit` (review item D5, ADR-0127): **sound**, **vague** or **wrong**, the
main problem, a one-or-two-sentence reason an examiner can check against the quoted
sentence, and for a wrong one a corrected reading or a recommendation to remove it.

The judge is a different model from the one that wrote the relationships — the owner
chose Gemini 3.1 Pro (ADR-0125) — so this is a second machine opinion, not a review. It
measures nothing a person signed, and nothing here is approved.

`tmk-bulk audit-apply` acts on it: a wrong relationship is re-read as the corrected
triple when that triple passes every check a new relationship must pass, and withdrawn
into `authored/retired-ids.yaml` otherwise. Vague ones are reported and left alone; so is
a correction that only widens an end the record already entails. A record serving in place
of a signed one (`authored/corrections.yaml`) is never changed: its verdict is listed in
`data/derived/reports/edge-audit.md` for a person, because a model does not overrule an
expert.

Each verdict carries the triple it judged (`judged`), so a verdict is never applied to a
record that has changed since. Gemini returned no confidence, so `confidence` is empty.

Regenerable from the committed response cache (`data/llm/cache/audit/`), so a re-run
is free. Do not hand-edit: a verdict you disagree with is a finding for a person, not
a cell to change.

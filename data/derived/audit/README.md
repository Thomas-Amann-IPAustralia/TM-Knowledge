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

## `restructure.yaml` — the structure review (ADR-0131)

Not a model's verdicts: an agent session's own judgements (`claude-code-agent-S029`), one
per line, on the owner's instruction of 2026-10-09 to connect the ontology's top level and
retire "is related to". It holds every machine-written relationship that was re-read
(`to:`) or withdrawn (`withdraw:`), new relationships with the passage and quote that state
them, concepts re-typed or relabelled, and corrections to signed "is a kind of" links.

`tmk-bulk restructure` checks every line the way a new relationship is checked — a defined
predicate, a sentence naming both ends, no "kind of" beside a "not the same as", ends that
are kinds the predicate joins, no duplicate triple — and writes nothing while any line is
refused; `--write` applies it and writes `data/derived/reports/restructure.md`. It is
idempotent: a line an earlier run applied is counted, not re-applied, so the ledger can grow.
A line you disagree with is a finding for a person; change the ledger, not the records.

## `review-response.yaml` — the review response's worklist (S036)

The same kind of ledger, applied by the same checked applier
(`tmk-bulk restructure --ledger data/derived/audit/review-response.yaml`): an agent
session's judgements (`claude-code-agent-S036`) on every machine-written relationship the
review response named (`docs/ONTOLOGY-REVIEW-RESPONSE.md`, F05, F13, F15, F16, F18) and on
every S029 re-read that had never been judged in its current form. A line re-reads a record
(`to:`), re-qualifies it on the same triple (`modality:`, `applies_when:` — the sentence's
own condition or hedge), withdraws it, or records that it was checked and kept (`keep:`).
Three new relationships restate heading-only ones from body text. The report is
`data/derived/reports/review-response-edges.md`. A later ledger's re-read is never undone by
running an earlier one.

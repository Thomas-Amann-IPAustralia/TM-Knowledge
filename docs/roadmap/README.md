# docs/roadmap/ — the programme document and its annotations

| File | What it is | May it be edited? |
|---|---|---|
| `AUTOMATION-FIRST-ROADMAP.md` | The full programme, Stages 0–10. Arrived by upload from the repo owner. | **Never.** Source document (ADR-0003). |
| `TECH-ALTERNATIVES.md` | Review of the roadmap's recommended technology stack against what the tools actually are now. Advisory. | Yes — supersede findings in place, and date them. |

## What belongs here

Documents *about the programme as designed*: the roadmap itself, and annotations
that sit alongside it without altering it.

## What must not

- Edits to `AUTOMATION-FIRST-ROADMAP.md`. Where it disagrees with reality, the
  disagreement is recorded in `docs/QUIRKS.md` and resolved in
  `docs/DECISIONS.md`. Editing the roadmap to match current thinking destroys the
  information that it once said something else.
- Current state. That is `docs/HANDOFF.md` and `docs/ROADMAP-STATUS.md`.
- Decisions. An ADR goes in `docs/DECISIONS.md`; this directory holds analysis
  that an ADR may cite, never the decision itself.

## Note on `TECH-ALTERNATIVES.md`

It recommends nothing be swapped today. Its conclusions are keyed to tool
versions as at a stated date and to the fact that no stage past 0 has started.
Re-check it when a stage actually opens, and record whatever is chosen as an ADR.

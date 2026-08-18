# docs/roadmap/ — the programme, and the plans that sit beside it

Two kinds of file live here and they have opposite editing rules. Check which
kind you are looking at before changing anything.

| File | Kind | Edit it? |
|---|---|---|
| `AUTOMATION-FIRST-ROADMAP.md` | **Source document** — arrived by upload from the repo owner (ADR-0003) | **Never.** Where it disagrees with reality, record the disagreement in `docs/QUIRKS.md` and the resolution in `docs/DECISIONS.md` |
| `PARALLEL-TRACK-ROADMAP.md` | Project-authored — the agent-side work available while Stage 0 content is pending (ADR-0016) | Yes, as the track moves |

## What belongs here

Plans that span multiple stages or multiple sessions: the programme itself, and
any subsidiary plan that organises work across it.

## What does not

- **Status.** `docs/ROADMAP-STATUS.md` holds the stage-by-stage board, and
  `docs/HANDOFF.md` holds current state. A plan here says what the work *is*;
  those two say where it has got to. Duplicating status into a plan guarantees
  one of the two goes stale.
- **Decisions.** A choice made while planning is an ADR in `docs/DECISIONS.md`.
  This directory may cite an ADR; it must not be the only place a decision is
  recorded.
- **Expert-facing instructions.** Those live in `eval/`, next to the templates
  they describe.
- **Edits to a source document.** See the table above.

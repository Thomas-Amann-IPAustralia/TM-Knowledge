# docs/ — project documentation

Read in this order when arriving cold. `CLAUDE.md` at the repo root comes first
of all.

| File | Read it for | Update it |
|---|---|---|
| `HANDOFF.md` | **Current state, the next action, open questions.** Authoritative | Every session, before finishing |
| `DECISIONS.md` | What is settled and why — numbered ADRs | Append when you decide something |
| `QUIRKS.md` | Traps, and where the roadmap and reality disagree | The moment you hit one |
| `ARCHITECTURE.md` | Intended shape of the system; what lives where | When the target shape changes |
| `IDENTIFIERS.md` | Refs, IRI minting, naming. Before writing any identifier | Rarely; via ADR |
| `ROADMAP-STATUS.md` | Stage-by-stage status board | When a deliverable moves |
| `GLOSSARY.md` | Domain and project terms | When you meet a term you had to look up |
| `UPSTREAM.md` | The upstream data contract — record shapes, the join, its refusals | Only when upstream changes |
| `roadmap/AUTOMATION-FIRST-ROADMAP.md` | The full programme, Stages 0–10 | **Never** — source document |

## The two source documents

`UPSTREAM.md` and `roadmap/AUTOMATION-FIRST-ROADMAP.md` arrived by upload from the
repo owner. Their content is unaltered; only their filenames and locations changed
(ADR-0003). Treat them as source material: annotate around them in `QUIRKS.md`,
never edit them to match current thinking. Where the roadmap and reality disagree,
reality is recorded in `QUIRKS.md` and the resolution in `DECISIONS.md` — that
disagreement is information, and editing the roadmap would destroy it.

## Why this much documentation for an empty repo

The work is done in ephemeral sessions that start with no memory. What is not
written down is re-derived, guessed at, or silently contradicted. The documented
state *is* the project's continuity — see `CLAUDE.md` §3.

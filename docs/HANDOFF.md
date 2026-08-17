# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-08-17 · session S003 · branch `claude/trademark-stage-0-dataset-gzmszn`

---

## 1. Where the project actually is

**Stage 1 is done, upstream, in another repo.** `manual-XtrACTor` holds a
deterministic snapshot of the Manual (500 pages, 2,460 chunks) and the
legislation (763 provisions), joined at 97% coverage. That repo is finished work
and is read-only from here — see `docs/UPSTREAM.md`.

**This repo holds nothing but documentation and an empty skeleton.** No code, no
data, no vocabulary, no ontology. Everything below the top-level directories is
a `README.md` describing what will live there.

**Stage 0 has an area and a container, and no content.** The pilot area is
**s 43** (ADR-0013, human decision, S002) — that closes Q1 at the level of
*which area*. `eval/templates/` now holds seven record types and
`eval/STAGE-0-INPUT-GUIDE.md` explains to the owner exactly what to supply.
Still missing: every piece of actual content — the scope boundary, competency
questions, gold set, prohibited uses, thresholds — and the harness. The upstream
repo's `ROADMAP-STAGE-1.md` names this as the real blocker on the programme, not
any missing extraction capability.

**The experts are slow, so S003 wrote down what proceeds anyway.**
`docs/roadmap/PARALLEL-TRACK-ROADMAP.md` (ADR-0016) holds twelve agent-side work
packages needing no legal judgement, and — more usefully — the five **gates**
saying where expert input actually becomes required. Read that file before
concluding the repo is blocked. It is not; not yet.

## 2. The next action

Two threads run in parallel. Neither waits on the other.

**Thread A — the owner, and only the owner.** Two decisions that are
engineering or organisational, not legal, and therefore not blocked on the
experts at all:

1. **Resolve Q2** — how the snapshot is acquired. ADR-0004 proposes the answer
   and needs only confirmation. This blocks more agent work than anything else
   in the repo.
2. **Approve a provisional worksheet scope rule** (ADR-0017). Not the pilot
   boundary — just which chunks get printed for annotation. Deliberately
   over-inclusive. This releases gate G1 without the experts.

**Thread B — the experts.** Unchanged: Pass A content, in the order at
`eval/STAGE-0-INPUT-GUIDE.md` §10. Pilot scope boundary first, then competency
questions and prohibited uses. Guide §3 explains why none of it is blocked.
If only one hour is available, guide §10 says what to spend it on.

**Thread C — agents.** Work the parallel track. P3 (identifiers), P4 (record
schemas) and P12 (provenance model) are unblocked right now and need no
decision from anyone. Then P1 → P2 → P6 → P9, which is the chain that ends in a
printed worksheet the experts can annotate. Prioritise the four packages marked
*shortens the expert critical path* (P6, P7, P9, P10) over the ones that merely
advance the code — a week of specialist time is itself part of why this is
stuck.

Do not start Stage 2 (YAKE/spaCy extraction). ADR-0010, and it is the mistake
the roadmap's final recommendation warns against — it is tempting precisely
because it is the first thing that produces visible output.

## 3. Open questions — need a human

| # | Question | Blocks | Raised |
|---|---|---|---|
| ~~Q1~~ | ~~What is the pilot scope?~~ **Answered S002: s 43** (ADR-0013). The *boundary* is now deliverable 1 — see Q8. | — | S001 |
| Q8 | What is the s 43 **boundary**? Which Manual Parts/chunks, which neighbouring provisions, is GI the centre of gravity or a sub-topic, are point-in-time questions in scope? Prompted for in `eval/STAGE-0-INPUT-GUIDE.md` §2. | All remaining Stage 0 **content**. No longer blocks the Pass B worksheet — ADR-0017 | S002 |
| Q2 | How does this repo get the upstream snapshot — git submodule, pinned release download, or vendored copy? ADR-0004 proposes pinned download; unconfirmed. | Any code that reads data | S001 |
| Q3 | Which LLM is "agency-approved" for the Stage 2–4 extraction steps, and under what data-handling conditions may Manual text be sent to it? | Stages 2, 3, 4 | S001 |
| Q4 | Who are the approving experts, and what does "approved" look like as a recorded artefact — a signed-off file in git, or an external register? | Stage 3 onward | S001 |
| Q5 | Does ADR-0005 (adopt upstream refs as canonical IDs, drop the roadmap's `tmem:manual/2026-01/...` form) hold? It contradicts the roadmap text. | Everything with an identifier | S001 |
| Q6 | Case law is cited by the corpus but is not held as documents anywhere. Is acquiring decision texts in scope for this repo? | Stage 2 citation resolution, Stage 8 retrieval | S001 |
| Q7 | What base IRI may the project mint under? `docs/IDENTIFIERS.md` proposes `https://data.ipaustralia.gov.au/tmk/`; persistent IRIs need control of that domain, which is an organisational call. | RDF serialisation only — deliberately not blocking anything else | S001 |
| Q9 | Does the owner accept the parallel track and its two load-bearing calls — ADR-0017 (worksheet printed from an over-inclusive provisional scope rule, approved by the owner without the experts) and ADR-0018 (Stage 0 incompleteness reported, malformed data fails the build)? ADR-0017 also needs the rule itself. | P9's real run (gate G1); the harness's CI semantics | S003 |

Agent-proposed ADRs awaiting human confirmation: **0004, 0005, 0006, 0011, 0012,
0014, 0016, 0017, 0018**.

Q2 has been promoted in priority: it now blocks the Pass B worksheet, which is
the next substantial agent deliverable. It is an infrastructure decision, not a
legal one — it does not wait on the experts, and it is the cheapest thing on the
board to close.

## 4. Do not redo these

- **Do not re-parse the Manual HTML or the legislation `.docx`.** Upstream does it
  deterministically and better. ADR-0002.
- **Do not design a new identifier scheme.** ADR-0005 settled it against the
  roadmap's illustrative form; argue with the ADR, don't invent a third.
- **Do not build a vector store or search index yet.** Stage 7 is five stages
  away and untestable without Stage 0.
- **Do not add LegalRuleML.** Explicitly deferred, roadmap §7 / ADR-0009.
- **Do not move or rename the two source documents again.** They were relocated
  in S001 (ADR-0003); their content is unaltered.

## 5. Session log

Newest first. One short entry per session: what changed, what it cost, what it
revealed. Keep entries to a few lines — detail belongs in ADRs and QUIRKS.

### S003 — 2026-08-17 — the parallel track

Owner reported the experts are slow and asked what could proceed meanwhile.
Wrote `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` (ADR-0016): twelve agent-side
packages P1–P12, five gates, an explicit not-to-do list, and a statement of
where the track runs out. Added `docs/roadmap/README.md` because that directory
now mixes a source document with an editable one.

Two things fell out of writing it that are more useful than the package list.
The Pass B worksheet does **not** have to wait on the pilot boundary — an
over-inclusive provisional scope rule the owner can set alone releases it, and
the error costs are asymmetric enough to make that clearly right (ADR-0017).
And the red harness is not free: with no gold records every mechanical check
passes vacuously, so the redness has to come from an explicit completeness gate,
which also has to be distinguishable in CI from a genuine failure (ADR-0018).

No legal content authored. No code, no data. Nothing executed.

### S002 — 2026-08-06 — pilot area fixed; Stage 0 input guide

Owner selected **s 43** as the pilot area on expert advice (ADR-0013), closing
Q1. Wrote `eval/STAGE-0-INPUT-GUIDE.md`: the expert-facing walkthrough of all
Stage 0 deliverables, with shape-only worked examples, elicitation prompts, a
definition of done and the order of work (ADR-0014).

Found a gap while writing it — the roadmap names seven gold-standard components
and the templates covered six. Added
`eval/templates/reasoning-expectation.template.yaml` (ADR-0015).

Two points in the guide are load-bearing and not obvious: recall is unmeasurable
unless a bounded chunk set is annotated **exhaustively** rather than
cherry-picked (§4), and Stage 0 splits into a pass that needs no data and a pass
that cannot start until the snapshot is pinned (§3). The second makes Q2 the
next agent-side blocker.

No legal content authored. No code, no data. Nothing executed.

### S001 — 2026-08-04 — repo structure and agent documentation

First working session. Repo contained only the roadmap, the upstream index and a
licence. Built the documentation set (`CLAUDE.md`, this file, `DECISIONS.md`,
`QUIRKS.md`, `ARCHITECTURE.md`, `IDENTIFIERS.md`, `ROADMAP-STATUS.md`,
`GLOSSARY.md`) and the directory skeleton with a README per directory. Relocated
the two source documents into `docs/` unaltered.

Recorded ADRs 0001–0012. Found and logged four discrepancies between the roadmap
and the upstream reality (QUIRKS Q1–Q4), the sharpest being that the roadmap's
illustrative identifier scheme cannot be reconciled with the identifiers upstream
actually emits.

No code, no data, no dependencies. Nothing has been executed because there is
nothing to execute.

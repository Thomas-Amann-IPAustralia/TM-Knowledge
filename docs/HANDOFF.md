# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-08-18 · session S003 · branch `claude/trademark-stage-0-dataset-gzmszn`

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
packages needing no legal judgement, and — more usefully — the **gates** saying
where expert input actually becomes required. Read that file before concluding
the repo is blocked. It is not.

**Four decisions were closed in S003** (ADR-0021, ADR-0022): the snapshot is a
pinned download, upstream refs are canonical, the candidate id drops `method`,
and the worksheet scope rule is set. Gate G1 is released and P1 is now the
critical path. The corollary is worth seeing clearly: **every gate that remains
is expert content**, so nothing but expert time is between here and Stage 0.

## 2. The next action

**Thread A is done.** The owner closed Q2, Q5 and Q10 and set the worksheet
scope rule, in S003 (ADR-0021, ADR-0022). Nothing on the agent side is waiting
on an owner decision any more. Two threads remain.

**Thread B — the experts.** Now the *only* thread with a queue. Pass A content,
in the order at `eval/STAGE-0-INPUT-GUIDE.md` §10: pilot scope boundary first,
then competency questions and prohibited uses. Guide §3 explains why none of it
is blocked. If only one hour is available, guide §10 says what to spend it on.

**Thread C — agents. Start with P1; it is now the critical path.** Q2 is
closed, so pinning the snapshot is buildable today, and P2, P6 and P9 all wait
behind it. P3 (identifiers, candidate id included — Q10 closed), P4 (record
schemas) and P12 (provenance model) are unblocked in full and need no decision
from anyone.

Then P1 → P2 → P6 → P9, which now runs all the way to a **printed worksheet**,
because G1 is released and ADR-0022 states the rule. Prioritise the four
packages marked *shortens the expert critical path* (P6, P7, P9, P10): with G1
closed, every remaining gate is expert content, so the only lever left on the
schedule is making that content cheaper to produce.

Keep §6 of the parallel track in mind — the Stage 2 stack is fixed (ADR-0019)
and three packages must be built to accommodate it, even though Stage 2 itself
stays behind G5.

Do not start Stage 2 extraction — no TextRank, YAKE, KeyBERT or spaCy run, not
even "just to see the output". ADR-0010, and it is the mistake the roadmap's
final recommendation warns against — tempting precisely because it is the first
thing that produces visible output.

## 3. Open questions — need a human

| # | Question | Blocks | Raised |
|---|---|---|---|
| ~~Q1~~ | ~~What is the pilot scope?~~ **Answered S002: s 43** (ADR-0013). The *boundary* is now deliverable 1 — see Q8. | — | S001 |
| Q8 | What is the s 43 **boundary**? Which Manual Parts/chunks, which neighbouring provisions, is GI the centre of gravity or a sub-topic, are point-in-time questions in scope? Prompted for in `eval/STAGE-0-INPUT-GUIDE.md` §2. | All remaining Stage 0 **content**. Does not block the worksheet — ADR-0017, ADR-0022 | S002 |
| ~~Q2~~ | ~~How does this repo get the upstream snapshot?~~ **Answered S003: pinned release download** (ADR-0004, confirmed by ADR-0021). | — | S001 |
| Q3 | Which LLM is "agency-approved" for the Stage 2–4 extraction steps, and under what data-handling conditions may Manual text be sent to it? | Stages 2, 3, 4 | S001 |
| Q4 | Who are the approving experts, and what does "approved" look like as a recorded artefact — a signed-off file in git, or an external register? | Stage 3 onward | S001 |
| ~~Q5~~ | ~~Does ADR-0005 hold?~~ **Answered S003: yes** — upstream refs are canonical (confirmed by ADR-0021). | — | S001 |
| Q6 | Case law is cited by the corpus but is not held as documents anywhere. Is acquiring decision texts in scope for this repo? | Stage 2 citation resolution, Stage 8 retrieval | S001 |
| Q7 | What base IRI may the project mint under? `docs/IDENTIFIERS.md` proposes `https://data.ipaustralia.gov.au/tmk/`; persistent IRIs need control of that domain, which is an organisational call. | RDF serialisation only — deliberately not blocking anything else | S001 |
| Q9 | **Narrowed S003.** ADR-0017 is confirmed and its rule is set (ADR-0022) — gate G1 released. Still open: does the owner accept **ADR-0016** (the parallel track itself) and **ADR-0018** (Stage 0 incompleteness reported as a state, malformed data fails the build)? | The harness's CI semantics only | S003 |
| ~~Q10~~ | ~~Does ADR-0020 hold — drop `method` from the candidate id?~~ **Answered S003: yes** (confirmed by ADR-0021). `IDENTIFIERS.md` §3 now states the operative formula. | — | S003 |

Agent-proposed ADRs awaiting human confirmation: **0006, 0011, 0012, 0014,
0016, 0018**. Confirmed in S003 by ADR-0021: **0004, 0005, 0017, 0020**.

**No agent work is blocked on a human decision any more.** Every remaining open
question is either expert content (Q8), organisational (Q3, Q4, Q7), a scope
question for later (Q6), or narrow enough not to block (Q9 — it changes how CI
reports, not what gets built).

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

### S003 — 2026-08-17/18 — the parallel track; Stage 2 stack; four decisions closed

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

Owner then fixed the Stage 2 candidate-generation stack: TextRank + YAKE +
KeyBERT in parallel, spaCy NER as metadata on candidates (ADR-0019, human).
Recording it surfaced two consequences worth having before code exists. The
candidate-id formula in `IDENTIFIERS.md` §3 hashes `method`, so three extractors
mint three ids for one span and the cross-method agreement the ensemble exists
to produce is invisible — ADR-0020 proposes dropping `method`, and P3 must wait
on Q10. And spaCy's OntoNotes labels collide by name with two gold entity types
while meaning something else (Q-16), which is how NER output would quietly
become the taxonomy.

Owner then answered four open questions when asked (ADR-0021, authority human):
Q2 pinned release download, Q5 upstream refs canonical, Q10 drop `method` from
the candidate id, and ADR-0017 confirmed with its rule set in ADR-0022 — every
chunk citing `TMA1995/s43` or a unit beneath it, plus page-mates, at every
`certainty` value. `IDENTIFIERS.md` §3 went from proposal to operative formula.

That leaves the board in a shape worth noticing: **no agent work is blocked on a
human decision**, P1 is the critical path, and all four remaining gates are
expert content. From here the only lever on the schedule is making that content
cheaper to produce — P6, P7, P9, P10.

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

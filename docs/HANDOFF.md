# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-08-05 · session S002 · branch `claude/roadmap-tech-alternatives-0vkk98`

---

## 1. Where the project actually is

**Stage 1 is done, upstream, in another repo.** `manual-XtrACTor` holds a
deterministic snapshot of the Manual (500 pages, 2,460 chunks) and the
legislation (763 provisions), joined at 97% coverage. That repo is finished work
and is read-only from here — see `docs/UPSTREAM.md`.

**This repo holds nothing but documentation and an empty skeleton.** No code, no
data, no vocabulary, no ontology. Everything below the top-level directories is
a `README.md` describing what will live there.

**The technology stack has been reviewed and nothing was swapped.**
`docs/roadmap/TECH-ALTERNATIVES.md` (S002) checks every component the roadmap
names against what the tools actually are in 2026. Nothing is abandoned, nothing
is badly chosen. Four items warrant a decision at the stage that uses them, and
the rule for making those decisions is ADR-0013: interface first, both
implementations behind it, gold set picks. Read that file before proposing any
substitution — including the YAKE→KeyBERT one, which is a real trade-off and not
a straightforward upgrade.

**Stage 0 was never done.** No competency questions, no gold-standard set, no
prohibited-use list, no evaluation harness. The upstream repo's own
`ROADMAP-STAGE-1.md` names this as the real blocker on the programme, not any
missing extraction capability. Nothing downstream can be *measured* until it
exists, which means nothing downstream should be *built* first.

## 2. The next action

**Get the Stage 0 inputs out of a human's head and into `eval/`.**

Concretely, in order:

1. Confirm the pilot scope with the repo owner. The roadmap suggests
   distinctiveness (s 41) and says the real choice is operational — that is a
   human decision, not an agent's. See open question Q1.
2. Once scope is fixed, the owner drafts competency questions and the gold set
   using the templates in `eval/templates/`. An agent may *prompt* for these,
   structure them, and check them for internal consistency. An agent must not
   author their content (CLAUDE.md rule 1).
3. Build the evaluation harness (`eval/` + `tests/`) that runs the gold set
   against whatever exists. It should be runnable and *failing* before Stage 2
   work starts — a red harness is the point.

Do not start Stage 2 (YAKE/spaCy extraction) before step 3. It is tempting
because it is the first thing that produces visible output, and it is exactly the
mistake the roadmap's final recommendation warns against.

If the owner is unavailable and you need to make progress, the useful
agent-only work is: the harness skeleton, the upstream loader
(`src/tm_knowledge/` — read `snapshot/` into Python records, preserving
`extraction`/`certainty`), and the identifier minting module from
`docs/IDENTIFIERS.md`. All three are pure plumbing with no legal content.

## 3. Open questions — need a human

| # | Question | Blocks | Raised |
|---|---|---|---|
| Q1 | What is the pilot scope? Distinctiveness/s 41 is the roadmap's suggestion, not a decision. | All of Stage 0, and therefore everything | S001 |
| Q2 | How does this repo get the upstream snapshot — git submodule, pinned release download, or vendored copy? ADR-0004 proposes pinned download; unconfirmed. | Any code that reads data | S001 |
| Q3 | Which LLM is "agency-approved" for the Stage 2–4 extraction steps, and under what data-handling conditions may Manual text be sent to it? | Stages 2, 3, 4 | S001 |
| Q4 | Who are the approving experts, and what does "approved" look like as a recorded artefact — a signed-off file in git, or an external register? | Stage 3 onward | S001 |
| Q5 | Does ADR-0005 (adopt upstream refs as canonical IDs, drop the roadmap's `tmem:manual/2026-01/...` form) hold? It contradicts the roadmap text. | Everything with an identifier | S001 |
| Q6 | Case law is cited by the corpus but is not held as documents anywhere. Is acquiring decision texts in scope for this repo? | Stage 2 citation resolution, Stage 8 retrieval | S001 |
| Q7 | What base IRI may the project mint under? `docs/IDENTIFIERS.md` proposes `https://data.ipaustralia.gov.au/tmk/`; persistent IRIs need control of that domain, which is an organisational call. | RDF serialisation only — deliberately not blocking anything else | S001 |
| Q8 | Is any stack component already fixed by agency procurement or an existing platform — OpenSearch, a triple store, a scheduler, an annotation tool? If so it is not a measurement question and ADR-0013 does not apply to it. | Stages 6–10 infrastructure; procurement lead time is likely the long pole | S002 |

Agent-proposed ADRs awaiting human confirmation: **0004, 0005, 0006, 0011, 0012, 0013**.

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

- **Do not swap a stack component on a staleness argument.** The review in
  `docs/roadmap/TECH-ALTERNATIVES.md` already checked every one against current
  releases. YAKE in particular looks dead and is not (Q-16).

## 5. Session log

### S002 — 2026-08-05 — technology stack review

Reviewed the roadmap's §3 stack against the state of each tool in 2026, prompted
by a question about KeyBERT as a YAKE replacement. Wrote
`docs/roadmap/TECH-ALTERNATIVES.md` and the missing `docs/roadmap/README.md`.

Findings: nothing in the stack is abandoned or outclassed outright. Four items
warrant a decision at their stage — custom spaCy NER (GLiNER-class models now sit
between rules and an LLM, and sidestep Q3), YAKE vs KeyBERT (genuine trade-off,
determinism against semantic coherence), WebProtégé (healthy tool, wrong workflow
for a script-generated ontology under git-recorded approval), and OpenSearch
(right choice, possibly too early for a 2,460-chunk corpus). Recorded ADR-0013,
Q-16, Q-17 and open question Q8. No code, no dependencies, nothing executed.

Newest first. One short entry per session: what changed, what it cost, what it
revealed. Keep entries to a few lines — detail belongs in ADRs and QUIRKS.

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

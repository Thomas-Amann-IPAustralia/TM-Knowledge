# Proposal: what to take from the KB SOP to reach a working pitch, fast

**Status: adopted, 2026-10-07 — this is the plan** (ADR-0110, answering
OQ-0028). **One amendment: no Gemini.** Wherever this page says Gemini, read
OpenAI — `gpt-6.1-sol` at medium effort for the knowledge work, OpenAI
embeddings for search — and spend is capped at US$1 until the owner approves
`docs/QUOTE.md` (ADR-0111).
**Answers:** the owner's request to *"consider the approach and come back with
some suggestions for anything we could/should adopt to speed up the ontology
creation"*, and the purpose set in ADR-0109 — *"this whole project is to merely
pitch the concept… I really just need a system that works (and SOON!)"*.
**Source method:** `docs/KB-SOP.md`.

---

## 1. Why this project is slow, measured

| What | Measured (2026-10-07) | What the SOP did instead |
|---|---|---|
| **No finish line** | The target is the roadmap's full programme, Stages 0–10, including OpenSearch, a triple store and a maintenance pipeline. Nothing says "the demo is done when…" | A deliverables table and a definition of done per phase. Build only the current phase |
| **Content is hand-written inside sessions** | All 208 authored records were written by the session agent directly. The approved model has never been called. Content records were added in **4 of 22** merged pull requests | Deterministic stages, then **one** model stage run in bulk, cached and schema-checked. A wrong call costs a re-run, not a rebuild |
| **Paperwork per session** | The read order points a new session at ~8,000 lines before it acts (`CLAUDE.md` 205, `HANDOFF.md` 1,794, `DECISIONS.md` 4,884, `QUIRKS.md` 1,210) and ends with a seven-step protocol. **108 ADRs** and ~16,000 lines of prose added across 22 pull requests; six ADRs went to two dashboard pages | Act by default, record instead of asking. A decision entry only for a non-obvious choice. Handover notes short, per topic, deleted when done |
| **Effort in production governance** | About 6,400 of ~19,700 lines of code are the expert-review loop (intake, seed packs, transcription, reconciliation, blockers, expert pack, typing sheet). 11 questions open on the owner's queue | Stop and ask only at a few named gates; everything else is decided and logged |
| **The value is not shown anywhere** | No search or retrieval code exists. 0 authored relationships; the graph is in **44 separate pieces**. Nothing measures whether the ontology helps | A test set and measured comparisons, so claims rest on numbers |

None of this was careless. The expert apparatus was the right build while only
an expert could write content; ADR-0079 removed that constraint on 2026-09-08,
and the apparatus kept growing after it.

**Two findings from today make the fast path cheap.**

- **The model is reachable.** The session proxy carries the Gemini credential;
  `gemini-3.8-flash` is a current model id with batch support, and Gemini
  embeddings are available too. A free model-list call confirmed it (QUIRKS
  Q-64). ADR-0094's reason for never calling the model does not hold here.
- **The vocabulary already reaches most of the Manual.** Matching the 130
  concepts' labels against the 2,460 passages — no model, no spend — finds at
  least one non-generic concept in **62%** of them, against 37% reachable
  through provision citations. The whole Manual is ~1.9 million characters
  (roughly half a million tokens), so a full model pass over it is small.

## 2. What to adopt

In order of how much faster each makes the project.

### P1 — A finish line: the demonstrator, and a definition of done (SOP §1, §15)

Replace "Stages 0–10" as the working target with four deliverables.

| | Deliverable | Done when |
|---|---|---|
| D1 | **A connected ontology over the whole Manual** — concepts with labels and synonyms, their groups, relationships between them, and links from each concept to the passages and provisions that discuss it | The graph builds with 0 SHACL defects; most concepts sit in one connected piece rather than 44; every machine-written record carries its envelope |
| D2 | **"Ask the Manual"** — a question goes in; the page shows the concepts recognised, the path through the graph, the passages and provisions retrieved with the Act and the Manual labelled apart, a cited answer, and the unreviewed stamp. Plain search alongside, for contrast | Runs on every benchmark question; refuses to state an examination outcome |
| D3 | **A value measurement** — plain search against ontology-enhanced search on the same questions, in one table | Numbers with intervals, per kind of question |
| D4 | **A pitch pack** — one page or a short deck: the numbers, screenshots, and the honest limits | The owner has seen it |

**Parked, not deleted:** the expert-review loop, new rounds of owner questions,
formal reasoning beyond the two existing rules, Stage 10, and deploying
OpenSearch or a triple store. `CLAUDE.md` would name D1–D4 as the current scope
and the roadmap as "future state — context only, do not build yet", which is how
the SOP keeps every session pointed the same way.

### P2 — Generate the ontology with a pipeline, not by hand (SOP §4.1, §4.6, §11)

The single biggest lever. Two steps, in this order.

1. **Deterministic first, at no cost.** Link every concept to the passages that
   name it, by its labels (the 62% above), stored with the label and span that
   matched. Propose candidate concept pairs from shared passages, shared
   provisions and one label containing another. None of this needs review —
   rule 7's first reason — and it is what the search in P4 expands through.
2. **Then one model stage, in bulk.** Gemini judges the candidate pairs and
   types the relationship (the 14 existing relation types, plus broader and
   narrower); writes synonyms and the everyday words an examiner or applicant
   would use; and authors concepts for the terms the corpus itself defines that
   no concept covers yet — 104 of 144, by the candidate file. The model returns
   JSON against a schema. **Code, not the model, does the provenance:** it finds
   every quote verbatim in the snapshot, computes the span and hash, writes the
   envelope (`unreviewed`, `authored_by` = the model id the API reports) and
   refuses any reply that fails.

**The money mechanics, straight from the SOP:** a `--dry-run` that estimates and
spends nothing; `--confirm` for any paid run; a `--limit N` smoke test on the
real transport before the full run (the SOP's first build lost a whole batch to
a transport that ignored the JSON schema); a response cache keyed by input, prompt
version and model, **committed**, so re-runs are free; versioned prompts; and a
budget cap checked before each run. This is ADR-0088 made mechanical: the
deterministic pass first, only what is left goes to the model, related judgements
batched, and the dry-run plus smoke test are how a session becomes "confident of
valuable output" before spending.

**What it changes about deciding.** Because a cached run is cheap to repeat, a
judgement — four groups or nine, which relation types — stops needing to be
settled in prose before anything is built. Change the prompt, re-run, compare.

### P3 — Measure the ontology's value; that is the pitch's evidence (SOP §6–7, scaled down)

- **A test set, the SOP's way.** About 100–150 realistic questions in four kinds:
  a lookup; an everyday-language problem; a question that crosses Parts; and
  "what is affected if this provision changes". Each in the examiner's words and
  as a search query. A model writes them from sampled passages — a *different*
  model from the one that authored the ontology, so the test does not share its
  voice. A model grades the pooled results 0–3; a stronger model re-grades a
  sample, and the agreement is the set's error bar. Kept apart from
  `eval/gold/`, which stays frozen.
- **A human-validated cross-check.** The 10 retrieval questions and 20
  competency questions an expert signed are run too — exactly what ADR-0080 froze
  them for.
- **Three systems compared:** keyword search; keyword plus vectors; and that plus
  the ontology (the question's concepts, their synonyms, related concepts, linked
  passages and provisions). nDCG@10 and Recall@20 per kind, with paired bootstrap
  intervals, choosing on a dev half and reporting on a test half.
- **A second number:** run the relationship pass over the passages behind the 35
  signed relationships and count how many the machine reproduces. "The machine
  finds X of what the expert signed" is the automation-first claim, measured.
- **Be ready for the honest answer.** On the SOP's corpus, alias expansion added
  nothing to a good hybrid baseline. The ontology's edge is likeliest on
  everyday-language and cross-Part questions, and on what search cannot do at
  all — impact analysis, where RULE-0002 is already approved. Measuring first
  tells you which story to tell before stakeholders do.
- **Skip the SOP's deep tuning** — fusion weight grids, diversity re-ranking,
  graph lanes, top-up judging, re-ranker ceilings. One baseline and one
  ontology configuration is enough for a pitch.

### P4 — Build "Ask the Manual" on what is already here (SOP §7.4, lite)

SQLite full-text search plus Gemini embeddings (no local model downloads), the
concept expansion from P3, and a cited answer from the model. **A compact map of
the ontology** — one line per concept, like the SOP's `map.md` — goes in the
answerer's prompt, so the model reads a question in the Manual's own terms; that
is the AI-retrieval half of the value story. Each answer shows the concepts it
recognised, the graph path, every passage with its ref, Act versus Manual
practice, and the unreviewed stamp, with the plain-search result beside it.

The published site is static and cannot hold an API key, so it shows pre-computed
answers for the benchmark and demo questions; live questions run from a small
local app. The answer step inherits the eleven signed prohibited uses — no
examination outcome, no confidence that a ground applies (PU-0003) — and those
become its test cases.

### P5 — Cut the per-session overhead (SOP §2, §8) — *changes `CLAUDE.md`*

- **Read order:** `CLAUDE.md`, `review/rulings/`, and a `HANDOFF.md` held under
  ~150 lines (state, next actions, open items), rewritten each session rather
  than appended to. The session log moves to an archive nobody reads at the start.
- **A one-page "rules in force"** so no session needs `DECISIONS.md`'s 4,884
  lines to act. `DECISIONS.md` stays append-only; nothing is deleted.
- **ADRs only for an owner decision or a genuinely non-obvious choice**, in the
  SOP's four-part template. Engineering and layout calls are made, not flagged:
  the "agent-proposed, awaiting confirmation" list stops growing.
- **End of session:** update the handoff, commit, push. Generate the site data in
  the Pages workflow at deploy time, so no session has to remember to.

### P6 — Ask the owner only at named gates (SOP §2.1) — *changes `CLAUDE.md`*

Stop and ask for: spending beyond the agreed cap; anything outward-facing or
irreversible (publishing somewhere new, sending to the expert, making the repo
public); changing what the system may say to an examiner; putting an expert's
own notes into a model prompt (ADR-0088); and which measured results become
claims in the pitch. **Everything else: decide, log it in a line, move on.** The
next session sorts the 11 open owner questions into *decide it*, *park it*, and
*still the owner's*.

### P7 — Keep the guardrails, in code rather than re-argued prose

The unreviewed stamp, `approved_by` never filled by an agent, the frozen 190 as
the yardstick, the Act and the Manual kept apart, no examination outcome, an
expert's notes never sent to a model. All are already enforced by schemas, the
harness and SHACL, and a pipeline writes the envelope for free. For a government
audience they are a selling point — *the system knows what an expert signed and
what a machine wrote* — so they belong in the pitch, not in the way of it. What
goes is re-litigating them in every session's prose.

## 3. What not to take from the SOP

- **Its ingestion phases** — fetch, security sweep, clean, structure. Upstream
  (`manual-XtrACTor`) already did this deterministically; rule 2 says consume it.
- **Its full manifest machinery.** A committed cache and a short summary per paid
  run is enough for a pitch.
- **Its deep retrieval tuning** (see P3) and **a local embedding stack** — the
  API embeddings keep CI light.

## 4. A suggested sequence

| Session | Work | Leaves behind |
|---|---|---|
| A | Adopt P5–P6 if agreed. Deterministic concept–passage links. The batch command with dry-run, cache and budget guard; a 20-item smoke test; then the relationship pass within the cap | A connected graph (D1) |
| B | Search index, ontology expansion, the generated test set and judging, the comparison table | The measurement (D3) |
| C | The "Ask the Manual" page and the pitch pack | D2 and D4 |

Three sessions is the shape; the estimate is the agent's, unmeasured, and it
assumes P5–P6 — under the current protocol each session spends a large share of
itself on records about records.

## 5. What the owner needs to decide (OQ-0028)

1. **The finish line** — adopt D1–D4 as the target, or change it.
2. **A spend cap** for model calls (authoring, judging, embeddings, answers), so
   a session spends within it without asking run by run.
3. **The process cuts** — P5 and P6 change `CLAUDE.md`, which is the owner's
   rulebook, so they wait on the owner's word.

P2–P4 need no rule change: Stages 2–4 are open (ADR-0083), corpus text may go to
the model (ADR-0088) and unreviewed content may be served if it is labelled
(ADR-0082). They wait only on the spend cap.

# CLAUDE.md — operating rules for this repo

Loaded into every session. Read it fully before touching anything.

`TM-Knowledge` is the **downstream ontology and knowledge-graph repo** for the
Australian trade marks examination corpus. The upstream extraction repo
(`manual-XtrACTor`) already produced a deterministic, offline snapshot of the
Manual and the legislation. This repo does everything *interpretive* on top of
it: vocabulary, ontology, relationships, graph, search, retrieval, reasoning.

**Two changes of operating model, and this file carries both.** On 2026-09-08 an
agent became free to author legal content, stamped as never validated by an
expert, across the whole Manual (ADR-0079 to ADR-0088). On 2026-10-07 the owner
set the project's purpose — *a pitch that demonstrates the value of an ontology
for the Trade Marks Manual; a system that works, soon, not every nuance* — and
adopted a faster way of working: a finish line, a model pipeline instead of
hand-authoring, lighter paperwork, and questions to the owner only at named gates
(ADR-0109 to ADR-0111). What changed neither time is every rule about provenance,
citation and the separation of what a machine wrote from what a person signed.

## 0. Current scope: the demonstrator

Build only this (ADR-0110). Done when each line's test holds.

| | Deliverable | Done when |
|---|---|---|
| D1 | A connected ontology over the whole Manual — concepts, labels, groups, relationships, and links from concepts to passages and provisions | The graph builds with 0 SHACL defects; most concepts sit in one connected piece; every machine-written record carries its envelope |
| D2 | "Ask the Manual" — concepts recognised, graph path, passages with the Act and the Manual kept apart, a cited answer, the unreviewed stamp; plain search beside it | Runs on every benchmark question; never states an examination outcome |
| D3 | The value measurement — plain search against ontology-enhanced search | Numbers with intervals, per kind of question |
| D4 | A pitch pack — the numbers, screenshots, the honest limits | The owner has seen it |

`docs/PITCH-PROPOSAL.md` is the plan and `docs/QUOTE.md` what the model work
costs. **Future state — context only, do not build yet:** the rest of
`docs/roadmap/AUTOMATION-FIRST-ROADMAP.md` (OpenSearch, a triple store, Stage 10
maintenance) and the expert-review apparatus in `src/tm_knowledge/stage0/`, which
is parked, not deleted.

## 1. Read order for a new session

1. This file.
2. `review/rulings/` — anything the owner decided that nobody has acted on
   (`applied: null`). A ruling outranks any `agent-proposed` ADR it touches.
3. `docs/HANDOFF.md` — under 150 lines: where things stand and what is next.
4. `docs/RULES-IN-FORCE.md` — one page of what 112 decisions add up to.
   **Do not read `docs/DECISIONS.md` or `docs/QUIRKS.md` end to end.** Search
   them (`grep -n`) when your task touches something they cover.
5. Then only what your task needs: `authored/README.md` before writing legal
   content; `docs/IDENTIFIERS.md` before minting an id; `docs/UPSTREAM.md` for
   record shapes; `docs/ARCHITECTURE.md` for where things live.

## 2. Hard rules

1. **Author, but never launder.** You *may* write concept definitions, synonym
   and near-miss judgements, concept types, relationships, modality readings,
   competency questions, prohibited uses, rules and exceptions. That was
   forbidden until 2026-09-08 and is now the job (ADR-0079). What you may never
   do is let something you wrote be mistaken for something an expert signed.
   Every authored record carries `review_status: unreviewed`, an
   `authored_by` naming the model and version, the date, and the evidence it
   rests on. A record that cannot carry those is not written.
2. **Consume upstream, never re-derive it.** `chunk_ref` and provision `ref` are
   stable keys. Do not re-parse the Manual HTML, do not write into a vendored
   snapshot, do not "fix" upstream data here. If upstream is wrong, record it in
   `docs/QUIRKS.md` and raise it upstream. **Unchanged by ADR-0079.**
3. **Preserve the trust metadata.** Upstream `extraction` (`href` vs `regex`) and
   `certainty` (`explicit` / `default` / `ambiguous`) must survive every transform.
   Collapsing them destroys the only thing separating an author's assertion from
   an inference. Anything this repo adds carries its own provenance: method,
   confidence, exact source span, review status. **Unchanged by ADR-0079, and
   more load-bearing than before it.**
4. **Three states, and they never blur: authored, approved, rejected.**
   *Authored* is what a machine wrote and no person has looked at. *Approved* is
   what a named expert signed on a date. *Rejected* is what a named expert threw
   out. They never share a file, a directory or a named graph. An authored record
   becomes approved only through a recorded human decision — never by being old,
   never by being unchallenged, never by an agent deciding it is obviously fine
   (ADR-0080, ADR-0085).
5. **The Manual is practice, not law.** It states the Registrar's practice; it does
   not bind the Registrar's discretion and it is not legislation. Any model over
   both must keep the two distinguishable at every point, including in retrieval
   output. **Unchanged.**
6. **Decide loudly; never resolve someone else's ambiguity silently.** Two
   different things, and ADR-0079 changed only the first. A *judgement* — is this
   a test or a factor, does this "may" mean permission — you now make, record and
   stamp. An *ambiguity in the source data* — which of several instruments a bare
   "section 15(1)" names, an upstream edge marked `ambiguous` — you still never
   resolve by guessing. Upstream refused to choose on purpose; inheriting that
   refusal is rule 3, not rule 1 (Q-07).
7. **Determinism where determinism is possible.** Prefer regex/structural/lookup
   extraction over a model. Reach for an LLM only for what genuinely needs
   judgement, always with a constrained schema and required evidence spans.
   **Unchanged** — a deterministic answer needs no review, and every judgement
   you author is review debt somebody eventually pays. Since ADR-0088 there is a
   second reason pointing the same way: a model call costs money, and the owner's
   rule is that something goes to the model *only where you are confident of
   valuable output back*. Keep the two reasons distinct even though they agree —
   a session that merges them will start defending a call on cost grounds when the
   real objection was review debt. Corpus text may be sent to the API without
   further clearance; an expert's own review notes may not (ADR-0088).
8. **No machine output goes anywhere unlabelled.** Every model-produced record
   carries `extraction_method`, `model`, `confidence`, `source_span`,
   `review_status`. **Unchanged, and it is now the rule the whole model rests
   on.** Before ADR-0079 an unlabelled record was a process failure. Now it is
   indistinguishable from expert knowledge, which is the one outcome this repo
   exists to prevent.

### What is still off limits

ADR-0079 removed a restriction on *authorship*. It removed nothing about
*honesty*, and it did not widen what the product may do:

- **Do not write a definition, a type or a relationship you cannot evidence.**
  Every authored record names the passages it rests on, by upstream ref, with a
  span and a `content_hash`. "I know this from trade marks law generally" is not
  a source. If the corpus does not support it, the record says so or is not
  written (ADR-0079 guard 2).
- **Do not fill `approved_by`.** Not with a name, not with `claude`, not with the
  owner's initials. That field means a person read this record and signed it. An
  agent writing into it is the single failure the whole scheme is built to stop.
- **Do not move a record into `eval/gold/`.** That directory is frozen as the 190
  records a human signed, and it is the only independent yardstick left for
  measuring authored output (ADR-0080).
- **Do not let the system state an examination outcome.** The programme does not
  automate a final examination decision, and the expert-approved prohibited-use
  records still stand as approved knowledge. ADR-0082 removed the *review gate*
  on serving unreviewed content; it did not widen the product's scope, and no
  agent may widen it (ADR-0082 consequence 4).
- **Do not treat silence as approval.** An unreviewed record may be relied on and
  may be served. It never becomes approved by not being corrected, and the record
  of it never having been validated is permanent (ADR-0085).

## 3. Session protocol

Act by default and record instead of asking (ADR-0110). A session that asks
permission for every design choice, or writes an essay where a line would do,
is failing this file.

**During:** a trap that would cost the next session time goes in
`docs/QUIRKS.md`, a paragraph, when you hit it.

**Before you finish:**

1. **Rewrite `docs/HANDOFF.md`** — do not append. Under 150 lines: state, next
   actions, open items, what to distrust. History goes in the git log.
2. **An ADR only for an owner decision or a genuinely non-obvious choice**, in the
   four-part form of §4. Engineering, layout and naming calls are made and, at
   most, mentioned in a commit body.
3. **Close out any ruling you acted on**: `applied:` in the file, an ADR with
   authority `human`, `status: answered` on the question.
4. If you changed authored or signed records, rebuild the graph
   (`tmk-graph --write --rules`); CI fails on graph drift (ADR-0070). The site
   rebuilds itself on deploy (ADR-0112).
5. Commit and push. An unpushed container is a lost container.

## 3a. When to stop and ask the owner

Only at these gates (ADR-0110, P6). Everything else: decide, log it, move on.

- **Spending** beyond the cap in force (`config.SPEND_CAP_USD`, ADR-0111). Give
  the dry-run estimate and wait.
- **Anything outward-facing or irreversible** — publishing somewhere new, sending
  anything to the expert, making the repository public, rewriting history.
- **Changing what the system may say to an examiner.**
- **Putting an expert's own notes into a model prompt** (ADR-0088).
- **Which measured results become claims in the pitch.**
- **Model choice for measurement work** — the owner chose the model for knowledge
  work; who writes and judges the benchmark is theirs to choose from the quote.

Ask in the chat when the owner is there; otherwise one entry in
`review/questions/open-questions.yaml`, in the plain language its README sets out.

## 4. Writing decisions

`docs/DECISIONS.md` is append-only. Never edit or delete a past ADR — supersede
it with a new one and mark the old `Superseded by ADR-nnn`. Four parts, short:
**Context** (what prompted it, with numbers), **Decision** (whose, and precisely
enough to reproduce), **What it does not decide** (if anything), **Consequences**.
Every ADR records its **authority**:

- `inherited` — from the roadmap or the upstream contract. Binds agents, not the
  owner (ADR-0082, ADR-0083 overturned two).
- `derived` — forced by evidence in the repo or upstream data.
- `agent-proposed` — a judgement call an agent made to keep moving. Provisional;
  name it in the handoff's open items.
- `human` — a decision the owner made. **A decision made in a chat window counts**:
  the words verbatim in `review/returned/`, a ruling file, and an ADR quoting them.

## 5. Conventions

- Australian English throughout (`organise`, `recognised`, `licence` the noun).
  The corpus is Australian government text; matching it matters for extraction.
- Identifiers, IRIs and file naming: `docs/IDENTIFIERS.md`. No ad-hoc ID schemes.
  Authored records use the same id grammar as approved ones and draw from the
  same sequence — one `GC-0123` in the project, wherever it lives.
- Directory names are lowercase, hyphenated. No spaces in filenames — the repo
  started with one and it caused friction.
- Python, if and when there is code: `src/tm_knowledge/`, `pytest` in `tests/`.
  Match upstream's style — it is the sibling codebase and the same people read both.
- Commits: imperative subject, one concern per commit, and say *why* in the body
  when the change encodes a decision.
- Every directory carries a `README.md` saying what belongs in it and what must
  not. If you create a directory, write its README in the same commit.
- **Paid model calls** go through `tm_knowledge.bulk` and nowhere else: a dry-run
  that estimates and spends nothing, `--confirm` to spend, `--limit N` for a smoke
  run, a response cache committed to the repo so a re-run is free, and a hard cap
  checked before every call (ADR-0111). Read the smoke run's output yourself
  before a full run.

## 6. What this repo does not do

Not here, deliberately: crawling or re-extracting source documents; editing the
snapshot; deciding examination outcomes; automating a final examination decision;
representing complex defeasible legal rules (LegalRuleML is explicitly deferred —
ADR-0009).

**Two things left this list on 2026-09-08** and are now core work: authoring
legal content (ADR-0079) and covering the whole Manual rather than section 43
alone (ADR-0081).

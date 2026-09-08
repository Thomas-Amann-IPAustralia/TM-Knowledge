# CLAUDE.md — operating rules for this repo

Loaded into every session. Read it fully before touching anything.

`TM-Knowledge` is the **downstream ontology and knowledge-graph repo** for the
Australian trade marks examination corpus. The upstream extraction repo
(`manual-XtrACTor`) already produced a deterministic, offline snapshot of the
Manual and the legislation. This repo does everything *interpretive* on top of
it: vocabulary, ontology, relationships, graph, search, retrieval, reasoning.

**The operating model changed on 2026-09-08 and this file is the amended
version.** Until that date an agent was forbidden to author legal content at all
and the pilot was fenced to section 43. Both restrictions are gone. An agent now
authors legal content directly, stamped as never validated by an expert, across
the whole Manual. What did **not** change is every rule about provenance,
citation and the separation of what a machine wrote from what a person signed —
those got stricter, because they are now the only thing holding the line.
ADR-0079 to ADR-0085 record the change and why.

## 1. Read order for a new session

1. This file.
2. `review/rulings/` — **anything the owner has decided and nobody has acted on.**
   A ruling outranks any `agent-proposed` ADR it touches. Empty is the normal
   state; a file with `applied: null` is work waiting for you.
3. `docs/HANDOFF.md` — **where the last session stopped and what to do next.**
4. `docs/DECISIONS.md` — what has already been settled, and why. Do not relitigate.
   **Start at ADR-0079** if you only read part of it: seven decisions there
   rewrote the operating model and supersede rules stated elsewhere in older files.
5. `docs/QUIRKS.md` — traps that have already cost someone time.
6. Then, only what your task needs:
   - `authored/README.md` — **the authored knowledge store. Read before writing
     any legal content.** What an authoring envelope must carry, and the one door
     from authored to approved.
   - `docs/ARCHITECTURE.md` — intended shape of the system and what lives where.
   - `docs/IDENTIFIERS.md` — the identifier and IRI rules. Read before writing any ID.
   - `docs/ROADMAP-STATUS.md` — stage-by-stage status board.
   - `docs/UPSTREAM.md` — the upstream data contract: record shapes, the join, what upstream refuses to do.
   - `docs/roadmap/AUTOMATION-FIRST-ROADMAP.md` — the full programme (Stages 0–10). Long; consult sections, don't re-read whole.
   - `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` — what proceeds while Stage 0 content is pending, and the gates where expert input becomes required. **Largely superseded by ADR-0083** — read it for the package list, not for the gates.
   - `docs/GLOSSARY.md` — domain and project terms.

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
   you author is review debt somebody eventually pays.
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

**At the start:** read `docs/HANDOFF.md` first. It is authoritative on current
state — more so than your reading of the file tree.

**During:** if you discover a trap, a surprising upstream behaviour, or a wrong
assumption, write it into `docs/QUIRKS.md` *when you find it*, not at the end.

**Before you finish, always:**

1. Update `docs/HANDOFF.md`: state now, next action, new open questions, and a
   new dated entry in the session log.
2. Add any decision you made to `docs/DECISIONS.md` as a new numbered ADR.
   Include the ones you made implicitly by choosing an approach.
3. Update the relevant row of `docs/ROADMAP-STATUS.md` if a deliverable moved.
4. If you acted on a ruling, close it out: `applied:` in the ruling file, an ADR
   with authority `human`, and `status: answered` on the question.
5. If anything you changed is on the dashboard — a gold record, an authored
   record, the ontology, the graph, an ADR, the status board — run
   `tmk-dashboard --write` and commit the result. CI fails on drift, because the
   published site reads only what is committed.
6. Ask the owner anything you needed and could not get: add it to
   `review/questions/open-questions.yaml`, in the plain language its README sets
   out. **The bar for this moved on 2026-09-08.** A question you can answer
   yourself and stamp `unreviewed` is no longer a question for the owner — author
   it. Reserve the queue for what an agent genuinely cannot settle: agency
   permissions, priorities, resourcing, and anything where being wrong is
   expensive and the corpus holds no evidence either way.
7. Commit and push. An unpushed container is a lost container.

A session that produced work but left `HANDOFF.md` stale has failed the next
session. Treat step 1 as part of the task, not as paperwork.

## 4. Writing decisions

`docs/DECISIONS.md` is append-only. Never edit or delete a past ADR — supersede
it with a new one and mark the old `Superseded by ADR-nnn`. Every ADR records its
**authority**:

- `inherited` — comes from the roadmap or the upstream contract; you may not
  overturn it, only surface a conflict. **Note ADR-0082 and ADR-0083: two
  `inherited` decisions were overturned by the owner on 2026-09-08. `inherited`
  binds agents, not him.**
- `derived` — forced by evidence in the repo or upstream data; defensible without
  a human.
- `agent-proposed` — a judgement call an agent made to keep moving. **Provisional.**
  Flag it in `HANDOFF.md` under open questions until a human confirms it.
- `human` — a decision the repo owner made.

**A decision the owner makes in a chat window counts** (his instruction,
2026-09-08). It is recorded the same way anything else is: his words transcribed
into `review/returned/` with the date and who relayed them, a ruling file, and an
ADR with authority `human` quoting him. The route does not change the weight; the
absence of a record does.

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

## 6. What this repo does not do

Not here, deliberately: crawling or re-extracting source documents; editing the
snapshot; deciding examination outcomes; automating a final examination decision;
representing complex defeasible legal rules (LegalRuleML is explicitly deferred —
ADR-0009).

**Two things left this list on 2026-09-08** and are now core work: authoring
legal content (ADR-0079) and covering the whole Manual rather than section 43
alone (ADR-0081).

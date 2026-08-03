# CLAUDE.md — operating rules for this repo

Loaded into every session. Read it fully before touching anything.

`TM-Knowledge` is the **downstream ontology and knowledge-graph repo** for the
Australian trade marks examination corpus. The upstream extraction repo
(`manual-XtrACTor`) already produced a deterministic, offline snapshot of the
Manual and the legislation. This repo does everything *interpretive* on top of
it: vocabulary, ontology, relationships, graph, search, retrieval, reasoning.

## 1. Read order for a new session

1. This file.
2. `docs/HANDOFF.md` — **where the last session stopped and what to do next.**
3. `docs/DECISIONS.md` — what has already been settled, and why. Do not relitigate.
4. `docs/QUIRKS.md` — traps that have already cost someone time.
5. Then, only what your task needs:
   - `docs/ARCHITECTURE.md` — intended shape of the system and what lives where.
   - `docs/IDENTIFIERS.md` — the identifier and IRI rules. Read before writing any ID.
   - `docs/ROADMAP-STATUS.md` — stage-by-stage status board.
   - `docs/UPSTREAM.md` — the upstream data contract: record shapes, the join, what upstream refuses to do.
   - `docs/roadmap/AUTOMATION-FIRST-ROADMAP.md` — the full programme (Stages 0–10). Long; consult sections, don't re-read whole.
   - `docs/GLOSSARY.md` — domain and project terms.

## 2. Hard rules

1. **Never invent legal content.** Do not write competency questions, gold-standard
   answers, concept definitions, synonym judgements, rules or exceptions out of
   your own knowledge of trade marks law and present them as project content.
   Every such artefact is *expert-owned*. You may build the templates, schemas,
   harnesses and pipelines that hold them, and you may generate clearly-labelled
   **candidates with evidence spans**. See rule 4.
2. **Consume upstream, never re-derive it.** `chunk_ref` and provision `ref` are
   stable keys. Do not re-parse the Manual HTML, do not write into a vendored
   snapshot, do not "fix" upstream data here. If upstream is wrong, record it in
   `docs/QUIRKS.md` and raise it upstream.
3. **Preserve the trust metadata.** Upstream `extraction` (`href` vs `regex`) and
   `certainty` (`explicit` / `default` / `ambiguous`) must survive every transform.
   Collapsing them destroys the only thing separating an author's assertion from
   an inference. Anything this repo adds carries its own provenance: method,
   confidence, exact source span, review status.
4. **Candidate ≠ approved.** Machine output is a candidate until a human approves
   it. Candidates and approved knowledge never share a file, a directory or a
   named graph. Nothing moves from `review/` to `vocab/`, `ontology/` or `graph/`
   without a recorded human decision.
5. **The Manual is practice, not law.** It states the Registrar's practice; it does
   not bind the Registrar's discretion and it is not legislation. Any model over
   both must keep the two distinguishable at every point, including in retrieval
   output.
6. **Fail loud, never guess.** Inherited from upstream and it still holds. Ambiguity
   is recorded and queued, never silently resolved.
7. **Determinism where determinism is possible.** Prefer regex/structural/lookup
   extraction over a model. Reach for an LLM only for what genuinely needs
   judgement, always with a constrained schema and required evidence spans.
8. **No LLM output goes anywhere unlabelled.** Every model-produced record carries
   `extraction_method`, `model`, `confidence`, `source_span`, `review_status`.

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
4. Commit and push. An unpushed container is a lost container.

A session that produced work but left `HANDOFF.md` stale has failed the next
session. Treat step 1 as part of the task, not as paperwork.

## 4. Writing decisions

`docs/DECISIONS.md` is append-only. Never edit or delete a past ADR — supersede
it with a new one and mark the old `Superseded by ADR-nnn`. Every ADR records its
**authority**:

- `inherited` — comes from the roadmap or the upstream contract; you may not
  overturn it, only surface a conflict.
- `derived` — forced by evidence in the repo or upstream data; defensible without
  a human.
- `agent-proposed` — a judgement call an agent made to keep moving. **Provisional.**
  Flag it in `HANDOFF.md` under open questions until a human confirms it.
- `human` — a decision the repo owner made.

## 5. Conventions

- Australian English throughout (`organise`, `recognised`, `licence` the noun).
  The corpus is Australian government text; matching it matters for extraction.
- Identifiers, IRIs and file naming: `docs/IDENTIFIERS.md`. No ad-hoc ID schemes.
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

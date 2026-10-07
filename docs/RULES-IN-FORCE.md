# Rules in force — what 112 decisions add up to

Read this instead of `DECISIONS.md` (ADR-0110). It is a summary, so when a line
matters to your task, `grep -n` the ADR it cites and read that one. If this page
and an ADR disagree, the ADR wins and this page is the bug — fix it.

**As at:** 2026-10-07, ADR-0119.

## Purpose and scope

- **The project is a pitch** that demonstrates the value of an ontology for the
  Trade Marks Manual; a working system soon outranks completeness (ADR-0109).
  Current scope is the demonstrator, D1–D4, in `CLAUDE.md` §0 (ADR-0110).
- **The whole Manual is in scope.** There is no section 43 boundary (ADR-0081).
- **Never state an examination outcome**, and never a confidence that a ground
  applies (PU-0003). The eleven signed prohibited uses stand (ADR-0082 c4).
- **The Manual is practice, not law.** Keep the Manual and the legislation
  distinguishable everywhere, including in an answer (CLAUDE.md rule 5).
- **The published site is for trade marks examiners** (`site/`, the explorer); the
  owner's workbench is at `/workbench/`, linked from nothing an examiner opens. A live
  chatbot answers examiners' own questions with the owner's key, unprotected — the
  owner's decision, and the key is recoverable from the page (ADR-0118).

## Knowledge: who wrote it, and the three states

- **An agent may author legal content**, stamped `unreviewed` with its model,
  date, basis, evidence and reasoning (ADR-0079). Never launder it.
- **Two stores, never summed.** `eval/gold/` is frozen at the 190 records a person
  signed and is the only independent yardstick; `authored/` is machine-written
  (ADR-0080). No count, attribute or report adds the two (ADR-0080 c3).
- **Three states**: `unreviewed`, `approved`, `rejected`. Silence never promotes a
  record (ADR-0086). Only `tmk-transcribe` moves a record to `eval/gold/`.
- **`approved_by` is never written by an agent.** Not a name, not initials, not a
  model id. A filled one in `authored/` is a defect (ADR-0090).
- **Evidence is quoted, not retyped**: a ref, a span, the content hash, and a quote
  that is exactly the text at the span (ADR-0045, ADR-0090 c3). `general_knowledge`
  is allowed and always flagged (ADR-0079 guard 2).
- **A malformed authored record is refused, never skipped** (ADR-0089).
- **`authored_by` is the model the API reported**, not the configured one
  (ADR-0094). The store holds more than one author; counts split by author.
- **Ids are one sequence across both stores** — one `GC-0123` in the project
  (ADR-0080 c1). A withdrawn id goes in the ledger and is never reused (ADR-0033).
- **A concept's type is its own record** (`GT-`), not a field (ADR-0071). Nine
  groups: the owner's four reasoning groups, untouchable without the owner, and
  five process groups an agent proposed (ADR-0098, `typing.GROUPS`).
- **Unreviewed content may be served** if its review status shows at the point of
  use (ADR-0082). A surface that cannot show it must not serve it.

## Source data

- **Consume upstream; never re-derive it.** No re-parsing the Manual HTML, no
  writing into the snapshot, no "fixing" upstream data here (ADR-0002).
- **The snapshot is fetched and pinned, never committed** (`tmk-fetch-upstream`,
  ADR-0004, ADR-0026).
- **Upstream's `extraction` and `certainty` pass through unchanged**, and an
  `ambiguous` edge is never resolved by guessing (ADR-0011, rule 6).
- **Refs are the identifiers**; IRIs are minted from them by `refs.py` and nothing
  else (ADR-0005, `docs/IDENTIFIERS.md`).

## Models and money

- **Bulk knowledge work: OpenAI `gpt-6.1-sol`, medium reasoning effort**, through
  the session proxy (ADR-0111, Q-65). No Gemini.
- **Spend cap: US$6.60**, the approved quote (`config.SPEND_CAP_USD`, ADR-0114).
  Every paid call goes through `tm_knowledge.bulk`: dry-run, `--confirm`,
  `--limit`, a committed cache, the cap checked before each call. **One exception:**
  the explorer's live answers are made from readers' browsers on the owner's key,
  outside `bulk` and the cap (ADR-0118).
- **Corpus text may go to the API; an expert's own notes may not** (ADR-0088).
- **A call must be worth making**: deterministic first, batch related judgements,
  never re-send what already has a current record (ADR-0088 c2).

## Artefacts and builds

- **`data/derived/` and the whole `graph/` are committed**; CI fails on graph
  drift, so rebuild with `tmk-graph --write --rules` after changing records
  (ADR-0042, ADR-0070).
- **The site rebuilds itself on deploy**; `site/data/` is not committed (ADR-0112).
  The explorer's build reads the pinned snapshot; the workbench's does not (ADR-0117).
- **The explorer may use libraries, vendored** under `site/vendor/` with a checksum
  manifest a test enforces, loaded per view by `site/js/lib.js` — never from a CDN
  (ADR-0119). The workbench keeps its no-library rule.
- **The browser's search is a copy of `search.index`** (`site/js/engine.js`, no
  vectors). A test holds the two identical, prompt included; change both or neither.
  The measured BM25 weights the heading in full, not by half (Q-69).
- **The graph reads both stores through one mapping**, every node stamped with its
  origin; an authored relationship is a `tmk:AuthoredAssertion`, never a
  `tmk:ApprovedAssertion` (ADR-0091).
- **The harness's exit 3 is "Stage 0 incomplete"**, a reported state, not a
  failure (ADR-0018, ADR-0030).

## Process

- **Act, record, or ask** — ask only at the gates in `CLAUDE.md` §3a (ADR-0110).
- **A decision made in chat counts**: verbatim words in `review/returned/`, a
  ruling file, an ADR quoting them (CLAUDE.md §4).
- **`DECISIONS.md` is append-only.** Supersede, never edit.

## Do not redo

- **Do not write a second** ref parser, IRI minter, snapshot reader, gold-set
  reader, authored-store reader, graph builder or workbook layout. There is one of
  each.
- **Do not rebuild the decision tree on a shared Manual Part or the nearest
  ground**, and do not make a factor a branch point or the procedural spine
  binary (ADR-0105, ADR-0106).
- **Do not join records on a definition ref** — every defined term in the Act
  cites the same provision (`ConceptView.joinable_sections`).
- **Do not "fix" a ref that fails validation.** `InvalidRef` means it was
  constructed rather than read; find the construction.
- **Do not relax `additionalProperties: false`** on a record schema to make an
  envelope validate; the envelope is split off before validation (Q-48).
- **Do not measure or lay out in a renderer's first pass** (Q-63), and do not
  retune the map's force constants without measuring (Q-62).

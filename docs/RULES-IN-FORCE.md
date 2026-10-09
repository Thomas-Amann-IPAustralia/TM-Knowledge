# Rules in force — what 123 decisions add up to

Read this instead of `DECISIONS.md` (ADR-0110). It is a summary, so when a line
matters to your task, `grep -n` the ADR it cites and read that one. If this page
and an ADR disagree, the ADR wins and this page is the bug — fix it.

**As at:** 2026-10-09, ADR-0131.

## Purpose and scope

- **The project is a pitch** that demonstrates the value of an ontology for the
  Trade Marks Manual; a working system soon outranks completeness (ADR-0109).
  Current scope is the demonstrator, D1–D4, in `CLAUDE.md` §0 (ADR-0110).
- **Waterfall delivery.** Nobody signs anything until the ontology ships to a group
  of trade marks examiners, who review it all at once; until then, make it as close
  to production ready as possible. No question goes to "the expert" singly
  (ADR-0120).
- **The whole Manual is in scope.** There is no section 43 boundary (ADR-0081).
- **Never state an examination outcome**, and never a confidence that a ground
  applies (PU-0003). The eleven signed prohibited uses stand (ADR-0082 c4).
- **The Manual is practice, not law.** Keep the Manual and the legislation
  distinguishable everywhere, including in an answer (CLAUDE.md rule 5).
- **The published site is for trade marks examiners** (`site/`, the explorer); the
  owner's workbench is at `/workbench/`, linked from nothing an examiner opens. A live
  chatbot answers examiners' own questions with the owner's key, unprotected — the
  owner's decision, and the key is recoverable from the page (ADR-0118).
- **On the site, an expert's review is marked, never featured.** Machine-written
  records keep "Machine · unreviewed" everywhere; reviewed ones say "Reviewed", grey,
  with no name; pictures draw every record alike. The Manual, the Act and the
  Regulations each have their own colour and mark — square, diamond, hexagon (ADR-0130).

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
  (ADR-0094). A record an agent session writes by hand carries the session's stamp
  (`claude-code-agent-S026`), never a model identifier (Q-75). The store holds more
  than one author; counts split by author, and a confidence is never ranked, filtered
  or thresholded across authors — a test enforces it (ADR-0125, F6).
- **Ids are one sequence across both stores** — one `GC-0123` in the project
  (ADR-0080 c1). A withdrawn id is never reused: signed ones in
  `eval/gold/retired-ids.yaml`, authored ones in `authored/retired-ids.yaml`, each
  with its reason and ruling (ADR-0033, ADR-0122).
- **A known defect in a signed record is corrected outside the signature** — a
  `GK-` record in `authored/corrections.yaml`, unreviewed, naming the owner's ruling.
  `eval/gold/` is never edited. What serves (`served_gold()`) applies corrections;
  the harness and every measurement read the records as signed (ADR-0122).
- **A concept's type is its own record** (`GT-`), not a field (ADR-0071), and it says
  what the concept *is*: eleven kinds in three families — the law's questions (ground,
  test, principle), what they are asked about (subject matter, sign content, context, use in
  trade), the process (role, step, instrument or record, external instrument) — and
  `none_of_these` (`typing.GROUPS`). What it *does* is an edge to the ground or test it
  acts on: a factor `qualifies` (or `mayGiveRiseTo`, `statesThresholdFor`), an exception
  `doesNotGiveRiseTo`, a ground `isOvercomeBy` its remedy — never a kind (ADR-0126).
  An eleventh kind, `principle` (the presumption of registrability, mandatory application,
  office practice), sits with the law's questions; `none_of_these` is empty (ADR-0131).
- **The top level connects** (ADR-0131). The families are classes; every predicate names
  the kinds it joins (`Predicate.subjects`/`.objects`), and a machine-written edge whose ends
  are not those kinds is a harness defect. Adding a predicate means naming its kinds.
- **No "is related to".** `related` is retired as a relationship; a passage that only
  mentions two ideas is not a relationship (the mention index records it). The relate
  prompt offers a predicate that fits or `none`. A signed concept's own `related` list stays.
- **Names are compared folded** — case, apostrophes, hyphens, a leading article,
  plurals (`ontology.hygiene.fold`). A shared name is a note, a shared preferred label a
  SHACL violation; merging a pair the owner kept apart (`authored/merge-candidates.yaml`)
  is a defect; a "kind of" link beside a not-label is refused unless
  `authored/kind-of-affirmed.yaml` says why both hold (ADR-0125).
- **Every predicate is defined** in `ontology/predicates.py` — definition, reading,
  example, counter-example, `law` or `practice` — and `relations.ttl` is generated
  from it. An authored edge on an undefined predicate is a defect; a triple that does
  not read the way its predicate reads is recorded the wrong way round (ADR-0123).
- **Roles are distinct and their power is on edges**: the Registrar (an office) is
  not a delegate, a delegate is not the Registrar, the owner is not the authorised
  user; who delegates to, directs, reviews or is consulted by whom is an edge on a
  sentence of the Act or the Manual, never the expert's note (ADR-0123).
- **Unreviewed content may be served** if its review status shows at the point of
  use (ADR-0082). A surface that cannot show it must not serve it.
- **A second model's verdict re-reads or withdraws a machine-written relationship**
  (`tmk-bulk audit-apply`, from `data/derived/audit/edges.yaml`) — never one serving
  for a signed record: a model does not overrule an expert, so that verdict goes to a
  person (ADR-0127).

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
  the session proxy (ADR-0111, Q-65). Gemini may be proposed, but "you still must come
  to me first with a quote for expenditure" (ADR-0121, D5). Gemini 3.1 Pro was
  approved for the D5 audit (ADR-0125); Gemini goes through its Batch API only, and
  its answers ignore the schema they are sent (Q-83).
- **Spend cap: US$9.49** — the US$6.60 quote plus the owner's US$2.89 for D5, which
  spent US$3.21 of its US$6.00 (`config.SPEND_CAP_USD`, ADR-0114, ADR-0125, ADR-0127).
  An amount the owner names binds, not the count a quote estimated: hold the run to it
  with `TMK_SPEND_CAP_USD` (ADR-0128, ADR-0129). Price from completed calls, never
  attempts (Q-85). Recorded US$8.37; the rest under the cap is not approved for anything.
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
- **Recognition**: the longest label wins its span; a concept's not-labels veto it;
  labels on `authored/too-general-labels.yaml` are skipped; apostrophes fold.
  Search aliases are narrowed to phrasings the source itself uses
  (`jobs.load_aliases`). Python and `engine.js` apply the same rules (ADR-0121).
- **Practice and law at answer time**: every Manual chunk is a `tmk:ManualPassage`;
  an answer sentence that says the legislation requires something it cites no
  provision for is flagged as PU-0004, never silently removed (`search.authority`,
  `engine.js`). A cited case is administrative (the Registrar's delegate), judicial
  or unclassified by its series, never guessed (`ontology.decisions`) (ADR-0121).
- **The graph reads both stores through one mapping**, every node stamped with its
  origin; an authored relationship is a `tmk:AuthoredAssertion`, never a
  `tmk:ApprovedAssertion` (ADR-0091).
- **The harness's exit 3 is "Stage 0 incomplete"**, a reported state, not a
  failure (ADR-0018, ADR-0030).
- **The measurement grades a passage once.** A re-measurement re-takes every system's
  pools the same day (Q-84), sends only ungraded passages to the judge, and can score
  other rankings on the same grades (`tmk-bulk pools --keep-previous --variant`). The
  judge stays `gpt-6.1-sol` unless a stronger one is shown more accurate on a yardstick
  no model touched (ADR-0127).

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
- **Do not edit `eval/gold/` to correct a signed record**, and do not correct a
  preferred label at all — write a correction (ADR-0122).
- **Do not relax `additionalProperties: false`** on a record schema to make an
  envelope validate; the envelope is split off before validation (Q-48).
- **Do not measure or lay out in a renderer's first pass** (Q-63), and do not
  retune the map's force constants without measuring (Q-62).

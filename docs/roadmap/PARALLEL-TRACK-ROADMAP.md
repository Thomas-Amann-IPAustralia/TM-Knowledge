# PARALLEL TRACK — what proceeds while Stage 0 content is pending

**Status:** project-authored. Not a source document — unlike
`AUTOMATION-FIRST-ROADMAP.md`, this file may be edited as the track moves.
**Progress:** S004 delivered **P1, P2, P3, P4, P6, P9 and P12**; S005 delivered
**P5, P10 and P11** — see the per-package **Done** lines and `docs/HANDOFF.md`
§5. Remaining: **P7 and P8**, the intake path.
**Governing decisions:** ADR-0016 (this track exists), ADR-0017 + ADR-0022
(over-inclusive worksheet scope, and the rule), ADR-0018 (how the harness
fails), ADR-0021 (the owner's confirmations). §6 records what ADR-0019's Stage 2
stack changes here.

---

## 1. Why this file exists

Stage 0's content is expert-owned and the experts are not yet delivering. The
question this file answers is: *what is genuinely available to build in the
meantime, in what order, and at what point does the wait become a hard stop?*

Two things it is not.

It is **not a way around Stage 0.** ADR-0010 stands: no Stage 2 extraction work
begins before Stage 0 is complete. Every package below is container, plumbing or
measurement apparatus. None of it produces vocabulary, concepts, relationships
or extracted terminology, and none of it is a partial substitute for the gold
set.

It is **not indefinite runway.** The track holds roughly six to ten working
sessions. After that the repo is genuinely blocked, and the honest report is
that it is blocked rather than that it is busy. Section 7 says where the wall
is.

There is also a third purpose, and on current evidence it is the most valuable
one: **four of these packages exist to make the expert's job smaller.** If the
experts are dragging, part of the reason is that Stage 0 as described in
`eval/STAGE-0-INPUT-GUIDE.md` §10 is on the order of a week of specialist time.
P6, P7, P8 and P10 are aimed squarely at reducing that number. They are worth
prioritising over the packages that merely advance the code.

---

## 2. The gates — when expert input actually becomes required

The single most useful thing in this file. There is not one gate; there were
five, and only the last is a hard wall. **G1 was released on 2026-08-18** — four
remain, all of them expert content.

| Gate | Needs from a human | Releases | What stalls without it |
|---|---|---|---|
| ~~**G1**~~ | ~~A scope rule for the worksheet~~ **Released 2026-08-18** — owner set the rule, ADR-0022 | The real Pass B worksheet run | — |
| **G2** | Pass A content: competency questions, prohibited uses, concept labels and `not_labels` | Content for the prohibited-inference tests; the first coverage report with anything in it | Nothing structural. The harness runs, and reports Stage 0 as incomplete |
| **G3** | Pass B content: gold entities, relationships, graded relevance judgements | The harness's most valuable checks — ref resolution, span-lands-on-text, content-hash currency | Those checks exist but have nothing to check |
| **G4** | Thresholds in `eval/measures.md` | Pass/fail semantics for every metric | Metrics can be computed but not judged. Nothing may be called "good enough" |
| **G5** | **All of Stage 0**, to the definition of done in `STAGE-0-INPUT-GUIDE.md` §7 | Stage 2 and everything after | **The hard wall.** ADR-0010 |

Read that table as: the experts' first deliverable does not block agent work at
all, their content becomes *useful* at G2–G3, and the programme only actually
stops at G5.

**G1 is closed and it never needed the experts.** The owner set a machine rule
for which chunks get printed on the annotation worksheet (ADR-0022) —
deliberately over-inclusive, and not the pilot boundary. What that leaves is
worth stating plainly: **every remaining gate is expert content**, so from here
the only lever on the schedule is making that content cheaper to produce, which
is what P6, P7, P9 and P10 are for.

---

## 3. What this track must not do

The temptations, listed because each one looks like progress.

- **No Stage 2 extraction.** No YAKE run "just to see the output", no spaCy
  pipeline, no clustering. ADR-0010, and the roadmap's own closing
  recommendation. The first plausible output becomes the standard by arriving
  first, which is the exact failure Stage 0 exists to prevent.
- **No drafting of expert content.** Not competency questions, not concept
  definitions, not synonym judgements, not prohibited uses — not even as
  "candidates for the expert to correct". CLAUDE.md rule 1. A plausible draft is
  worse than a blank, because it anchors the reviewer and it gets copied
  forward.
- **Nothing written into `vocab/`, `ontology/` or `graph/`.** Those hold
  approved content, and there is none. ADR-0007.
- **No search index, no vector store, no embeddings.** Stage 7 is untestable
  before Stage 0 and building it early fixes design choices no measurement has
  justified.
- **No LegalRuleML.** ADR-0009.
- **No filling of a gold record's judgement fields to make a test pass.** If a
  field needs a human, it stays empty and is reported as a gap. A harness made
  green with invented content measures nothing and lies about it.

A useful test before starting anything not listed in §4: *would this artefact
change if the expert content came back different from what I assume?* If yes, it
belongs after a gate, not on this track.

---

## 4. Work packages

Twelve packages. Each states what it is, why it is on this track, what it is
blocked by, what it unblocks, and what "done" means. Sizes are agent sessions:
**S** ≈ part of a session, **M** ≈ a session, **L** ≈ more than one.

Nothing in P1–P12 requires a legal judgement. Where a human decision is needed
it is an engineering or organisational one, marked **owner decision**.

---

### P1 — Pin the upstream snapshot

**DONE — S004.** `tmk-fetch-upstream`; pin is a commit sha, no upstream releases exist (Q-19, ADR-0026).

**Size** M · **Blocked by** nothing — **Q2 closed, ADR-0021** · **Unblocks** P2,
P6, P9, half of P5 · **Now the critical path**

Settled and ready to build. ADR-0004, confirmed by ADR-0021: fetch a pinned
upstream release into `data/upstream/`, keep the directory out of git, record
`extractor_version` and the upstream commit SHA in a tracked manifest.

This is now the **critical path**. Three packages and the worksheet run wait
behind it, and nothing waits behind them except expert time.

The fetch must be **scripted, not documented as manual steps** (ADR-0004's own
consequence clause). A bare clone plus one command must produce a working
`data/upstream/`, because agent containers are ephemeral (Q-14) and any manual
step will be skipped or done differently each time.

**Done when** a script fetches the pinned release, verifies it against the
recorded SHA, refuses to run against an unpinned or mismatched snapshot, writes
the pin manifest, and a test asserts the corpus counts match `UPSTREAM.md` §2
for the pinned version.

---

### P2 — Upstream loader

**DONE — S004.** `tm_knowledge.upstream.loader`; round-trip byte-equal over the whole corpus; join measured at 2,615/2,691 (Q-20).

**Size** L · **Blocked by** P1 for its acceptance tests · **Unblocks** P6, P9,
the resolution half of P5

`src/tm_knowledge/upstream/`: read `snapshot/` into typed Python records — page,
chunk, provision, unit — preserving every field in `UPSTREAM.md` §4. The work
can start against upstream's `schema/*.json` contract with small fixtures before
P1 lands; only the acceptance run needs the real snapshot.

Three requirements that are not negotiable and are easy to get wrong:

1. **`extraction` and `certainty` survive intact** on every provision, case and
   internal ref (CLAUDE.md rule 3). No default value, no collapsing `default`
   into `explicit`, no dropping `ambiguous`. A loader that returns a bare list of
   provision ids has destroyed the trust metadata and is worse than no loader.
2. **Refs pass through byte-for-byte.** No lowercasing, stripping, padding or
   re-splitting — that breaks the string-equality join (`IDENTIFIERS.md` §1).
   A test should assert the join holds across the whole corpus after loading.
3. **`content_hash` travels with the record**, because staleness detection in
   every later stage depends on it.

**Done when** the whole pinned corpus loads, a round-trip test shows no field
loss, the join reproduces upstream's 97% coverage figure exactly, and
`certainty: ambiguous` edges are still ambiguous at the far end.

---

### P3 — Identifier module

**DONE — S004.** `tm_knowledge.refs`; `#` must be escaped in an IRI after all (Q-17, ADR-0023), and 228 refs are level-undecidable (Q-18, ADR-0025).

**Size** S · **Blocked by** nothing — **Q10 closed, ADR-0021** · **Unblocks**
every later package that writes an id

`IDENTIFIERS.md` made fully executable: ref parsing and validation (including
upstream's two invariants — instrument-can-hold-kind and
instrument-can-express-number), IRI minting as the single function in §2, the
content-addressed candidate id from §3, and the sequential allocator for
human-facing ids.

Deliberately **not blocked by Q7** (the base IRI). The base is one configuration
constant; nothing else hard-codes it, and refs — not IRIs — are what gets stored
everywhere except RDF (`IDENTIFIERS.md` §4). Ref handling and IRI minting can be
finished in full while the domain question stays open.

**The candidate id is now settled** and `IDENTIFIERS.md` §3 states the
operative formula: `source_ref | span_start | span_end | normalised_value`, with
the methods that found a span as a set field. Implement it as written — the
`method` term is out on purpose (ADR-0020), and putting it back scatters one
candidate across three `review/` entries.

**Done when** the `ref → IRI → ref` round-trip test passes without
percent-encoding, invalid refs are rejected with a loud error rather than
normalised, the content-addressed id is stable across re-runs over unchanged
input, and no module outside this one constructs an IRI by concatenation.

---

### P4 — Machine-checkable record schemas

**DONE — S004.** `eval/schemas/`, eight types; judgement fields required-but-nullable (ADR-0027).

**Size** M · **Blocked by** nothing · **Unblocks** P5, P7, P8, P10

The seven templates in `eval/templates/` are YAML documents with comments. Turn
each into a schema a validator can enforce, keeping the templates as the
human-readable face and generating or checking one against the other so they
cannot drift.

Schemas cover **shape only**: field presence, types, enum membership
(`kind`, `tier`, `modality`, `category`, `grade`), id patterns
(`CQ-`, `GE-`, `GC-`, `GR-`, `GS-`, `GA-`, `GX-`, `PU-`), ref syntax via P3,
and the presence of `approved_by` / `approved_date`. They must never encode a
judgement — a schema cannot say which `modality` is correct, only that one of
the three is present.

**Done when** every template validates against its own schema, a deliberately
malformed fixture fails for the stated reason, and the enum lists match the
guide §5 text exactly.

---

### P5 — Evaluation harness

**DONE — S005.** `tmk-harness`. Three severities and three exit codes (ADR-0030); a run without the snapshot is never "complete" (ADR-0031).

**Size** L · **Blocked by** P4; the resolution checks additionally need P1+P2 ·
**Unblocks** P10, P11

The Stage 0 deliverable that is entirely agent-owned. It asserts the mechanical
list in `STAGE-0-INPUT-GUIDE.md` §7. Split the checks by what they need:

**Structural — no snapshot required.** Schema validation, id uniqueness and
non-reuse, cross-reference resolution (`prohibited_conclusions` → `PU-*`,
`broader`/`narrower` → `GC-*`, `related_questions` → `CQ-*`/`GA-*`),
`approved_by`/`approved_date` present on every record, competency-question
category coverage, prohibited-use `kind` coverage.

**Resolution — needs the pinned snapshot.** Every `source_ref` resolves; every
`span` lands inside its chunk's `text`; the text at that offset equals the
recorded `surface` or `supporting_text` **exactly**; every `source_content_hash`
matches the snapshot's current hash.

The point at which this design usually goes wrong is worth stating plainly.
With zero gold records, every check above passes **vacuously** — a suite that
iterates an empty collection is green. A green Stage 0 harness is the one
outcome the guide explicitly says is wrong. So the harness carries a
**completeness gate**: a check that fails while any Stage 0 deliverable is
absent or below its target band, naming what is missing. That is what makes the
harness red today, and it is what turns it green only when Stage 0 is genuinely
finished. See ADR-0018.

**Done when** the suite runs on a clean checkout, fails, and its failure output
is a legible list of exactly which Stage 0 deliverables are missing — usable as
a status report, not just as a test failure.

---

### P6 — Corpus reconnaissance for the scope decision

**DONE — S004.** `tmk-recon`. s 43: 67 citing chunks, 36 pages, 216 with page-mates, 17 unresolved refs, 2 ambiguous edges, 58 cases.

**Size** M · **Blocked by** P1, P2 · **Unblocks** the owner's boundary decision
(G1) · **Shortens the expert critical path**

Machine-derived, purely factual reports about the candidate pilot area, produced
so the boundary decision is made against numbers instead of impressions. Every
output is a count or a listing of what upstream already records. None of it
interprets anything, and the report must say so on its face.

Useful reports:

- Chunks whose `provisions[]` cite `TMA1995/s43`, with counts by Part and by
  chunk `kind`, plus the same for any neighbouring provisions the owner names.
- The **volume implication**: how many chunks, and therefore roughly how many
  annotation-hours, each candidate boundary rule implies. This is the number
  that turns "which Parts are in scope" from an abstract question into a
  costed one.
- In-scope refs sitting in upstream's 76 unresolved edges, so the s 41
  renumbering trap (Q-06) is found before gold records are built on it, not
  after.
- In-scope edges with `certainty: ambiguous`, which must be recorded as
  ambiguous and never "corrected" (Q-07).
- Cases cited from in-scope chunks — **citation level only**, with the standing
  caveat that no decision text exists anywhere in the programme (Q-11).

**Done when** the reports regenerate deterministically from the pinned snapshot,
each carries a header stating it is derived counts and not a scope proposal, and
the volume implication is expressed per candidate rule.

---

### P7 — Intake workbook generator

**Size** M · **Blocked by** P4 · **Shortens the expert critical path**

`STAGE-0-INPUT-GUIDE.md` §6 tells the owner not to write YAML. This package
makes that true. Generate a spreadsheet workbook from the P4 schemas: one sheet
per record type, columns in the guide's order, enum fields as dropdowns,
free-text judgement fields left plainly open, and the shape-only guidance from
the guide as sheet-level notes rather than as example rows.

No example rows containing legal content. The guide's `«placeholder»` convention
carries over — a plausible filled row in a workbook is the same trap as a
plausible example in a document, and it is more likely to be copied.

**Done when** the workbook regenerates from the schemas (so a schema change
cannot leave it stale), enum cells reject out-of-vocabulary values, and a
round-trip through P8 preserves every field.

---

### P8 — Transcription and validation path

**Size** M · **Blocked by** P4, P7; P3 for ref checks · **Shortens the expert
critical path**

The return leg: workbook, marked-up worksheet or prose in, validated YAML
records in `eval/gold/` out. This is the mechanism by which "an agent will
transcribe and validate" stops being a promise and becomes a command.

The rule that makes it safe: **transcription may reshape, never supply.** An
empty judgement field stays empty and is reported by P10 as a gap. If a
relationship arrives without a `modality`, the record is written without one and
the gap is queued for the expert — it is never inferred from the sentence's
grammar, because that distinction is a legal reading (guide §5.4).

**Done when** a filled fixture workbook transcribes to schema-valid records,
every missing judgement field appears in the gap report rather than being
filled, and the transcription is idempotent — re-running over unchanged input
rewrites nothing.

---

### P9 — Pass B worksheet generator

**DONE — S004.** `tmk-worksheet`; 216 chunks printed, deterministic, header states the rule and its provisionality.

**Size** M · **Blocked by** P1, P2 — **G1 is released** (ADR-0022) ·
**Shortens the expert critical path**

The highest-value expert-facing artefact in Stage 0: every in-scope chunk
printed with its `chunk_ref`, `heading_path`, `content_hash` and full text, in a
form that can be highlighted and commented. The owner should never type a ref or
a hash by hand, and with this they never do.

**The scope rule exists — build it and run it.** ADR-0022 sets it: every chunk
whose `provisions[]` carries `TMA1995/s43` **or any unit beneath it**, matched on
the ref grammar rather than by substring, plus every chunk sharing a `page_ref`
with one of those. Edges of every `extraction` and `certainty` value are in —
`ambiguous` is a reason to print a chunk, never a reason to drop one (Q-07).

The output is marked provisional and its header states the rule and the pinned
`extractor_version`. Worksheet scope is not pilot scope; when the expert
boundary lands the worksheet is regenerated and the delta reported, and
annotations against rows later ruled out are parked rather than deleted.

If the volume comes out unworkable, report the number and ask — do not quietly
tighten the rule (ADR-0022).

**Done when** the worksheet regenerates deterministically, every printed ref
resolves, every printed hash matches the pinned snapshot, and the header states
the scope rule used and that it is provisional.

---

### P10 — Coverage and gap reporter

**DONE — S005.** `tmk-coverage`. A board of every deliverable against its band, then the gaps as a worklist.

**Size** S · **Blocked by** P4, P5 · **Shortens the expert critical path**

Reports on whatever Stage 0 content exists, against the targets and the
definition of done: how many records of each type against its band, which
concepts have no `not_labels`, which competency-question categories are
unrepresented, which prohibited-use `kind` values are missing, which records
lack `approved_by`, and which fields came back empty through P8.

This is what makes **incremental** expert delivery worthwhile. A single
elicitation session that produces four concepts should visibly move a number.
The guide's advice to the owner is "if you have one hour, write the exclusion
list and three prohibited uses" — P10 is what makes that hour show up as
progress rather than disappearing into a directory.

It reports gaps; it never fills them (guide §9).

**Done when** it runs against an empty `eval/gold/` and produces a complete
to-do list, and against a partial one and produces a shorter one.

---

### P11 — CI wiring

**DONE — S005.** `.github/workflows/harness.yml`, plus a canary job that fails if the harness ever accepts the deliberately corrupted fixture gold set.

**Size** S · **Blocked by** P5

Run the harness on every push. The design question is that this repo's harness
is *supposed* to fail, and a permanently red pipeline trains everyone to ignore
it — at which point a real regression goes unnoticed.

Separate the two: **Stage 0 incompleteness is an expected, reported state**
(the completeness gate from P5, surfaced as a status summary), while **a
malformed record, an unresolvable ref, a span that does not land, a broken
round-trip, or a loader that drops trust metadata is a genuine failure** that
breaks the build. ADR-0018.

**Done when** CI is green on a clean checkout while still reporting Stage 0 as
incomplete, and goes red when a fixture is deliberately corrupted.

---

### P12 — Provenance record model

**DONE — S004.** `tm_knowledge.provenance`; a candidate cannot be constructed without a complete block.

**Size** S · **Blocked by** nothing

ADR-0011's fields as a typed structure with tests: `extraction_method`, `model`,
`confidence`, `source_span`, `review_status`, plus the PROV-O mapping named in
`ARCHITECTURE.md` §4. Nothing may be constructed without them (CLAUDE.md rule
8), which is far easier to enforce from the first record than to retrofit.

**Done when** a candidate record cannot be constructed without a complete
provenance block, and a test asserts that.

---

## 4a. What S004 changed about the track

Seven of the twelve packages are built, and the two facts worth carrying forward
are not in the package list.

**The volume question ADR-0022 asked is answered.** Its rule selects 216 of the
corpus's 2,460 chunks — 8.8%, about 40,000 words, on 36 pages. That is workable,
so the rule stands as written and nothing needs tightening. The worksheet exists
and regenerates deterministically, which is what makes the promised delta
computable when the expert boundary lands.

**Building against the corpus contradicted the documents three times**, and each
would have been expensive later: `#` in 498 chunk refs breaks IRI minting as
`IDENTIFIERS.md` §2 specified it, 228 legislation refs cannot be placed by
grammar, and `UPSTREAM.md`'s join figure does not reproduce at the pinned commit.
None was visible from documentation. The lesson for the remaining packages is the
one the track already half-states: assert against the corpus, not against the
prose about it.

**P5, P7, P8, P10 and P11 remain**, and none is blocked. P5 (harness) is the
critical path now — P10 and P11 sit behind it, and it is the Stage 0 deliverable
that is entirely agent-owned.

## 5. Suggested order

Dependencies allow several orders. This one front-loads the packages that
shorten the expert's critical path, because that is the binding constraint.

```
   ┌─ P3 identifiers ──┐  DONE S004
   ├─ P4 schemas ──────┤  DONE S004
   └─ P12 provenance ──┘  DONE S004
              │
   P1 pin snapshot        DONE S004
              │
   P2 loader              DONE S004
              │
      ┌───────┴────────┐
   P6 recon  DONE    P9 worksheet  DONE — 216 chunks printed
      │                │
      │                └──▶ expert annotation can begin NOW
      │
   P7 workbook ─▶ P8 transcription        ← remaining
              │
   P5 harness ─▶ P10 coverage ─▶ P11 CI   ← remaining, P5 now the critical path
```

1. **P1** — now the critical path, and unblocked. Everything below waits on it.
2. **P3, P4, P12** — unblocked, no decision needed, and P3's candidate id is
   settled.
3. **P2**, then **P6**. P6's volume numbers are what make the boundary decision
   answerable — and they are now also the check on whether ADR-0022's rule
   selects a workable number of chunks.
4. **P9**, built and run. G1 is released, so this ends in a printed worksheet:
   the point at which Pass B stops being hypothetical and the experts have
   something in front of them.
5. **P7, P8** — the intake path, so expert output has somewhere to land.
6. **P5**, then **P10, P11**.

---

## 6. What the Stage 2 stack decision changes here

ADR-0019 fixed the candidate-generation stack — TextRank, YAKE and KeyBERT in
parallel, with spaCy NER as metadata on the candidates. **Stage 2 itself is
still behind G5 and none of it may be built.** But three packages on this track
have to be built to accommodate it, and getting that wrong is cheap to fix now
and expensive later.

- **P3** — the candidate id must not carry the method. See the package note and
  ADR-0020. Blocked on Q10.
- **P4, P12** — `extraction_method` is a set, not a scalar. A term found by all
  three extractors is one record with three methods and three scores, because
  **agreement across methods is the confidence signal the ensemble exists to
  produce**, and it is only visible if the methods land on one record. The
  schema must also carry the KeyBERT model identifier and version, since that
  is what makes a candidate reproducible.
- **P5, P10** — entity precision, recall and F1 need a **per-method** breakdown,
  plus union and intersection. Without it there is no evidence for weighting the
  ensemble or for retiring an extractor that is not earning its place, and the
  ensemble becomes three tools nobody can compare. Agents propose these metrics;
  the thresholds stay the owner's (guide §5.9).

One thing this decision does **not** change: `data/upstream/` remains the source
of provisions, cases and internal refs. spaCy NER does not go near them — Q-16
and ADR-0019 consequence 4.

## 7. Where the track runs out

After P1–P12 the repo has: a pinned snapshot, a loader, identifiers, schemas, a
red harness, CI, a worksheet, an intake path and a gap report. It has no
vocabulary, no concepts, no relationships, no graph and no measurements —
because every one of those needs either expert content or a Stage 2 run that
ADR-0010 forbids.

That is the wall, and it is G5. When the track is exhausted the correct status
report is *"the container is finished and empty; the programme is waiting on
Stage 0 content"* — not a search for further plumbing to build. Manufacturing
work at that point means building things no measurement has justified, which is
the failure mode the whole roadmap is arranged to avoid.

The mitigation is not more agent work. It is that P6, P7, P9 and P10 will by
then have cut the expert's cost substantially: the boundary decision comes with
volume numbers attached, the annotation surface is printed and pre-populated,
nobody has to write YAML, and an hour of expert time visibly moves a counter.

---

## Related

`AUTOMATION-FIRST-ROADMAP.md` (the programme — source document, do not edit) ·
`eval/STAGE-0-INPUT-GUIDE.md` (what the experts supply; §7 the definition of
done, §10 the order of work) · `docs/ROADMAP-STATUS.md` (the status board) ·
`docs/HANDOFF.md` §3 (the open questions, including Q2) ·
`docs/DECISIONS.md` ADR-0010, ADR-0016 to ADR-0022 ·
`docs/QUIRKS.md` Q-05, Q-06, Q-07, Q-11, Q-14, Q-16

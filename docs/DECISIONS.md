# DECISIONS — architecture decision record

Append-only. **Never edit or delete a past entry.** To change a decision, write a
new ADR and mark the old one `Superseded by ADR-nnnn`. The point of this file is
that a future session can tell the difference between a settled question and an
open one, and can find out *why* without re-deriving the reasoning.

Each entry carries an **authority**:

| Authority | Meaning | Can an agent overturn it? |
|---|---|---|
| `inherited` | From the roadmap or the upstream contract | No — surface the conflict, don't resolve it |
| `derived` | Forced by evidence in the repo or the upstream data | Only with contrary evidence |
| `agent-proposed` | A judgement call made to keep moving | Provisional; needs human confirmation |
| `human` | The repo owner decided | No |

Provisional decisions must also appear in `HANDOFF.md` §3 until confirmed.

---

## ADR-0001 — This repo is the interpretive layer; `manual-XtrACTor` is the source

**Date** 2026-08-04 · **Authority** inherited · **Status** accepted

**Context.** The programme has two repos. `manual-XtrACTor` produced Stage 1: a
committed, offline, deterministically extracted snapshot of the Manual and the
legislation, with no embeddings, no retrieval, no API and no LLM anywhere in its
pipeline. Its own documentation states that everything interpretive is
"deliberately left to a downstream repo — i.e. probably yours".

**Decision.** `TM-Knowledge` implements roadmap Stages 0 and 2–10: evaluation set,
terminology, controlled vocabulary, relations and rules, ontology, knowledge
graph, search, AI retrieval, reasoning, maintenance. Stage 1 is not reimplemented
here.

**Consequences.** Every capability the upstream repo refuses to provide —
concepts, topics, summaries, rules, conditions, exceptions, difficulty ratings,
relevance scores, defined-term vocabulary, resolved amendment edges — is this
repo's responsibility. The split is a governance feature: extraction stays
auditable and byte-stable, interpretation stays reviewable and versioned
separately.

---

## ADR-0002 — Consume upstream; never re-derive it

**Date** 2026-08-04 · **Authority** inherited · **Status** accepted

**Decision.** `chunk_ref` (`TMM/Part22/1/1/2`) and provision `ref`
(`TMA1995/s41`, `TMA1995/s41(3)(a)`) are treated as stable foreign keys.
Enrichment is keyed on them and regenerated on this repo's own cadence. Nothing
here writes back into `snapshot/`, re-parses the Manual HTML, or re-reads the
compiled `.docx`.

**Consequences.** If upstream data is wrong, the fix belongs upstream. Log it in
`QUIRKS.md`, work around it explicitly and visibly, and raise it there. A local
"correction" that is not in the snapshot is an invisible fork of the corpus and
will silently diverge at the next upstream release.

---

## ADR-0003 — Documentation-first repo, with the two source documents relocated

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** accepted

**Context.** The repo contained exactly three files: the roadmap, an index of the
upstream repo, and a licence. Nothing told a new agent session what to do, what
had been decided, or where anything should go.

**Decision.** Establish the documentation set and directory skeleton before any
code. Move the two source documents into `docs/` with their content unaltered:

- `REPO_INDEX.md` → `docs/UPSTREAM.md` (it describes *another* repo; the old name
  read as if it indexed this one)
- `Automation-First Roadmap for a Trade Marks Examination Knowledge System.md` →
  `docs/roadmap/AUTOMATION-FIRST-ROADMAP.md` (the space-laden filename is hostile
  to shell tooling)

Both moves used `git mv`, so history follows the files.

**Consequences.** External links to the old paths break; the repo has three
commits and no published links, so the cost is nil. Do not move them again.

---

## ADR-0004 — The upstream snapshot is fetched, pinned and not committed here

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0021** (was provisional, HANDOFF Q2)

**Context.** Three options: git submodule, a pinned release archive downloaded
into an ignored directory, or a vendored copy committed into this repo.

**Decision.** Fetch a pinned upstream release into `data/upstream/` and keep that
directory out of git. Record the pinned `extractor_version` and the upstream
commit SHA in a small tracked manifest so a run is reproducible.

**Rationale.** Vendoring duplicates a large corpus into a second git history and
invites exactly the local edits ADR-0002 prohibits. Submodules pin correctly but
are a recurring source of half-initialised checkouts in CI and in ephemeral agent
containers. A pinned download keeps one copy of the truth and makes the version
an explicit, reviewable value.

**Consequences.** Nothing works from a bare clone until a fetch step runs; that
step must be scripted, not documented as manual instructions. Corpus counts in
this repo's docs are only meaningful next to the pinned version.

---

## ADR-0005 — Upstream refs are the canonical identifiers; IRIs are minted from them

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0021** (was provisional, HANDOFF Q5)

**Context.** The roadmap illustrates stable identifiers as
`tmem:manual/2026-01/chapter-4/section-3/paragraph-12`. Upstream already emits
`TMM/Part22/1/1/2` for a chunk and `TMA1995/s41(3)(a)` for a legislative unit,
and the join between the two corpora *is* string equality on those refs. The two
schemes cannot both be canonical.

**Decision.** Upstream refs win. This repo mints IRIs by prefixing them and never
by re-coining an identifier from document structure. The roadmap's form is
treated as illustrative of the *requirement* (stable, addressable, versioned),
not as a specification. Full rules in `docs/IDENTIFIERS.md`.

**Rationale.** Re-coining loses the free join, needs a lookup table nobody
maintains, and embeds a date (`2026-01`) that the corpus does not actually
version by — upstream versions per page via `content_hash` and `last_amended`,
not by a monthly corpus stamp.

**Consequences.** A human should confirm this before the first IRI is written to
disk; it is cheap now and expensive after the graph exists. The roadmap text
should be annotated rather than rewritten — it is a source document.

---

## ADR-0006 — Organise by artefact type, not by roadmap stage

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** accepted

**Decision.** Top-level directories are `eval/`, `vocab/`, `ontology/`, `shapes/`,
`queries/`, `graph/`, `review/`, `src/`, `data/`, `tests/`, `docs/` — not
`stage2/`, `stage3/`, and so on.

**Rationale.** Stages are a sequence of *activities*; the artefacts they produce
are long-lived and are revised by later stages. The SKOS vocabulary is created in
Stage 3, extended in Stage 4, consumed in Stage 7 and re-run in Stage 10; filing
it under `stage3/` would be wrong within a month. `ROADMAP-STATUS.md` carries the
stage view, and each directory README names the stages that touch it.

---

## ADR-0007 — Candidates and approved knowledge are physically separated

**Date** 2026-08-04 · **Authority** inherited · **Status** accepted

**Decision.** Machine-generated candidates live in `review/`. Approved knowledge
lives in `vocab/`, `ontology/` and `graph/`. In RDF, the separation is by named
graph: authoritative source data, machine-extracted candidates, expert-approved
assertions, inferred assertions, superseded assertions. Promotion between them
requires a recorded human decision.

**Rationale.** Roadmap Stage 6: named graphs exist so that machine suggestions
never become indistinguishable from approved knowledge. If they mix once, no
later audit can unmix them.

---

## ADR-0008 — Three-tier confidence policy; Tier 3 always needs a human

**Date** 2026-08-04 · **Authority** inherited · **Status** accepted

**Decision.** Tier 1 (deterministic: citations, identifiers, dates, versions) may
be auto-accepted once the method has demonstrated accuracy. Tier 2 (probabilistic,
low risk: keyphrases, topics, proposed synonyms) may be auto-accepted above a
threshold with sample auditing. Tier 3 (legally significant: overruling,
exceptions qualifying rules, evidence being required rather than relevant,
obligations, legal conclusions) requires expert approval, indefinitely.

**Consequences.** No amount of measured accuracy moves an output out of Tier 3
without an explicit human policy change recorded as a new ADR. "The model is
reliable now" is not that change.

---

## ADR-0009 — LegalRuleML is deferred

**Date** 2026-08-04 · **Authority** inherited · **Status** accepted

**Decision.** Not in the initial implementation. Reasoning uses OWL 2 RL for
classification, SHACL for validation, SPARQL (including `CONSTRUCT`) for explicit
derivations, and decision tables for bounded procedural logic.

**Consequences.** Before anyone introduces it, they must demonstrate that the
simpler stack is inadequate for a *named* use case involving obligations,
defeasibility, rule priorities or complex temporal applicability. Record that
demonstration as the superseding ADR.

---

## ADR-0010 — Stage 0 is completed before any Stage 2 extraction work

**Date** 2026-08-04 · **Authority** derived · **Status** accepted

**Context.** The upstream repo's `ROADMAP-STAGE-1.md` reaches a blunt verdict:
Stage 1 is substantially complete, but **Stage 0 was skipped entirely** — no
competency questions, no gold standard, no prohibited-use list, no evaluation
harness anywhere in the programme. It argues that this, not any extraction gap,
is the real blocker.

**Decision.** No Stage 2+ pipeline work begins until `eval/` holds a pilot scope,
a competency-question catalogue, a gold-standard set, a prohibited-use list and a
runnable harness.

**Rationale.** Every automated component in Stages 2–10 is justified by a
measurement. Without the gold set the measurements do not exist, and the first
plausible-looking extraction output becomes the de facto standard purely because
it arrived first. The roadmap's own final recommendation puts the expert-created
test set first for this reason.

**Consequences.** The first visible output of this repo is a *failing* test
harness. That is the intended state, and it should be defended when it looks like
slow progress.

---

## ADR-0011 — Every assertion carries provenance; upstream signals pass through unchanged

**Date** 2026-08-04 · **Authority** agent-proposed (field list) · **Status** provisional

**Decision.** Provenance uses PROV-O plus project fields. Every record this repo
generates carries, at minimum:

`extraction_method` · `model` (and version, where a model was used) ·
`confidence` · `source_ref` (upstream `chunk_ref` or provision `ref`) ·
`source_span` (exact character offsets into the upstream `text`) ·
`source_content_hash` · `review_status` · `reviewer` and `review_date` where
applicable · `created_at`.

Upstream's own `extraction` (`href` / `regex`) and `certainty` (`explicit` /
`default` / `ambiguous`) are carried through **verbatim** and are never merged
into this repo's `confidence`.

**Rationale.** The upstream signals distinguish an author's own hyperlink from
our inference about their prose. A single blended confidence number destroys that
distinction permanently and there is no way to recover it short of re-running
extraction. `source_content_hash` is what lets a later run detect that the
passage an assertion rests on has changed.

**Consequences.** Records are verbose. Accept it. The field list itself is an
agent's proposal and should be reviewed against the eventual SHACL shapes.

---

## ADR-0012 — Working conventions

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** accepted

**Decision.** Australian English in all prose and in any extraction lexicon — the
corpus is Australian government text and spelling variants matter to matching. No
spaces in filenames. Lowercase hyphenated directory names. Every directory carries
a `README.md`, written in the same commit that creates the directory, stating what
belongs there and what must not.

**Rationale.** The last item is the one that matters: an empty directory with no
README is an invitation for the next session to guess, and agent sessions guess
consistently but not correctly.

---

## ADR-0013 — The pilot area is s 43 of the Trade Marks Act 1995

**Date** 2026-08-06 · **Authority** human · **Status** accepted

**Context.** HANDOFF Q1 asked for the pilot scope and blocked all of Stage 0. The
roadmap suggests distinctiveness (s 41) but states that the final selection
should follow operational need, against five criteria: important to examiners,
spread across multiple Manual sections, connected to legislation and case law,
containing relationships and exceptions, and contained enough for a pilot.

**Decision.** The pilot area is **s 43**. The repo owner selected it on expert
advice, noting that it touches geographical indications — an area of growing
discourse — while meeting the roadmap's other criteria.

**Consequences.** Q1 is closed at the level of *which area*. The **boundary** is
not yet fixed and is the first Stage 0 deliverable: which Manual Parts and chunks
are in scope, which neighbouring provisions come with it, whether geographical
indications are the centre of gravity or a sub-topic, and whether point-in-time
questions are in scope. Those remain expert-owned and are prompted for in
`eval/STAGE-0-INPUT-GUIDE.md` §2.

Q-06 (superseded provision numbering) was logged against s 41 because s 41 was
the roadmap's suggested pilot. It is no longer on the critical path for that
reason, but the underlying trap is general: any in-scope ref appearing in
upstream's unresolved set is suspect. Check s 43's refs against that set before
gold records are finalised.

---

## ADR-0014 — Stage 0 gets an expert-facing input guide, distinct from the templates

**Date** 2026-08-06 · **Authority** agent-proposed · **Status** accepted

**Context.** `eval/templates/` holds the record schemas and `eval/README.md`
explains the directory, but both are written for an agent. The repo owner asked
what Stage 0 actually requires of them, which the repo could not answer: the
templates state field names, not what makes a record worth having, in what order
to produce them, or what can be written without the snapshot.

**Decision.** Add `eval/STAGE-0-INPUT-GUIDE.md` as the expert-facing document.
It carries no legal content: every example is marked shape-only, ids are
numbered `XXX`, and legal substance is a `«placeholder»`. It adds three things
the templates do not have — a two-pass split (Pass A needs nothing, Pass B needs
the pinned snapshot), the exhaustive-annotation rule for recall measurement, and
a definition of done separating what a human must judge from what the harness
asserts.

**Rationale.** The plausible-example trap is real: an illustrative record with
invented legal content gets copied forward and treated as approved. Marking every
example as shape-only is what makes a worked walkthrough compatible with
CLAUDE.md rule 1. Stating explicitly that the owner need not write YAML also
removes a barrier that has nothing to do with the expertise being sought.

**Consequences.** Two files now describe the same deliverables for two audiences
and can drift. `eval/README.md` names the guide and says to keep them in step. A
change to a template or a target size is a change to both.

---

## ADR-0015 — Expected reasoning results get their own record template

**Date** 2026-08-06 · **Authority** derived · **Status** accepted

**Context.** The roadmap lists seven gold-standard components. `eval/templates/`
covered six: five in `gold-record.template.yaml` and prohibited uses in their
own file. **Expected reasoning results had no template**, so a Stage 0 declared
complete against the existing templates would have been missing a named roadmap
deliverable.

**Decision.** Add `eval/templates/reasoning-expectation.template.yaml`
(`GX-nnn`). Kept separate from `gold-record.template.yaml` because it is tested
by a different mechanism — Stage 9 inference rather than extraction or retrieval
— and because it pairs one-to-one with `eval/prohibited-uses.md` through its
`must_not_infer` field.

**Consequences.** The record's scope is confined to inferences that follow from
what the corpus states; anything needing evidence to be weighed or discretion
exercised is a prohibited use instead. That boundary is expert-owned, and it is
the most valuable judgement the record captures. The field list is an agent's
proposal and should be reviewed against the eventual SHACL shapes alongside
ADR-0011.

---

## ADR-0016 — A parallel track is defined for work that does not need expert content

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** provisional — see HANDOFF Q9

**Context.** Stage 0's content is expert-owned (CLAUDE.md rule 1) and the
experts advising the owner have not yet delivered. The repo held no statement of
what could proceed meanwhile, which leaves two bad outcomes available: idling on
the assumption that everything is blocked, or drifting into Stage 2 because it
is the first thing that produces visible output — the mistake the roadmap's
closing recommendation names.

**Decision.** Add `docs/roadmap/PARALLEL-TRACK-ROADMAP.md`: twelve work packages
(P1–P12) that require no legal judgement, a five-gate table stating exactly
where expert input becomes required, an explicit list of what the track must not
do, and a statement of where the track runs out. ADR-0010 is untouched — the
track ends at Stage 0 completion and does not reach Stage 2.

**Rationale.** Two things needed writing down and neither existed. First, the
gates: the experts' content is not one undifferentiated blocker, and the
distinction between "nothing agent-side is blocked" (G2–G4) and "the programme
stops" (G5) is what lets the owner chase the right thing at the right time.
Second, the leverage: four of the twelve packages exist to reduce expert effort
rather than to advance the code, on the reasoning that a week of specialist time
is itself a cause of the delay, and that shortening it is more useful than
finding more plumbing to build.

Also recorded deliberately: the track's finite length. A plan that cannot say
where it ends invites manufactured work, and work no measurement justifies is
what Stage 0 exists to prevent.

**Consequences.** `docs/roadmap/` now mixes a source document with a
project-authored one; a `README.md` there states which is which and their
opposite editing rules. The package list will need revision as packages land —
unlike its neighbour, this roadmap is editable. Sizes are agent-session
estimates, not commitments.

---

## ADR-0017 — The Pass B worksheet is generated from an over-inclusive provisional scope rule

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0021**; the rule itself is ADR-0022 (was provisional, HANDOFF Q9)

**Context.** The Pass B worksheet — every in-scope chunk printed with its
`chunk_ref`, `heading_path`, `content_hash` and text — is the artefact that lets
the expert annotate without typing a ref or a hash by hand. It appears to
require `eval/pilot-scope.md`, which does not exist and is the deliverable most
clearly awaiting expert advice. That reading makes the single most useful
expert-facing artefact wait on the very people it is meant to unblock.

**Decision.** Generate the worksheet from a deliberately **over-inclusive**
machine rule — chunks citing the pilot provision, plus their page-mates —
approved by the owner alone, and mark the output provisional in its header
alongside the rule used. The worksheet's scope is not the pilot's scope, and
choosing it does not pre-empt the boundary decision.

**Rationale.** The error costs are asymmetric. An over-inclusive worksheet costs
the expert a scroll past rows they ignore. An under-inclusive one silently
removes material from the annotated set, which breaks the exhaustive-annotation
rule that recall measurement depends on (`STAGE-0-INPUT-GUIDE.md` §4) and does
so invisibly. Given that asymmetry, printing too much early beats printing
nothing until the boundary is settled.

This does not breach CLAUDE.md rule 1. The rule governs what content is
*printed for review*, not what is in scope for the pilot; it is derived
mechanically from upstream's own `provisions[]` edges; and it is set by the
owner, a human, not by an agent.

**Consequences.** Two scope notions now coexist and must not be conflated —
worksheet scope and pilot scope. The worksheet header carries the distinction.
Annotations made against rows later ruled out of scope are not wasted: they are
recorded and parked, exactly as `pilot_in_scope: false` handles competency
questions. When the boundary lands, the worksheet is regenerated and the delta
reported.

---

## ADR-0018 — Stage 0 incompleteness is a reported state; malformed data is a build failure

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** provisional — see HANDOFF Q9

**Context.** ADR-0010 and `STAGE-0-INPUT-GUIDE.md` §7 require the harness to run
and **fail** before Stage 2 begins. Two problems follow. With no gold records,
every mechanical check iterates an empty collection and passes **vacuously**, so
the suite is green for the worst possible reason. And once the suite does fail
by design, a permanently red pipeline trains everyone to ignore it, which is
where a genuine regression hides.

**Decision.** Separate the two failure kinds.

- **The completeness gate** — a harness check that fails while any Stage 0
  deliverable is absent or below its target band, naming what is missing. This
  is what makes the suite red today rather than vacuously green, and its output
  doubles as a status report. In CI it is surfaced as a reported state, not as a
  broken build.
- **Genuine failures** — a malformed record, a duplicated id, an unresolvable
  `source_ref`, a `span` that does not land on its recorded text, a stale
  `source_content_hash`, a broken IRI round-trip, or a loader that drops
  `extraction`/`certainty`. These break the build.

**Rationale.** Both signals are needed and they mean opposite things: one says
"the expected work has not arrived yet", the other says "something that did
arrive is wrong". Collapsing them loses the second, which is the one that costs
money. Naming the missing deliverables also turns the red harness from an
apparent lack of progress into a legible answer to "what is Stage 0 waiting
on" — a defence the guide says the red harness will need.

**Consequences.** The completeness gate encodes the target bands from
`STAGE-0-INPUT-GUIDE.md` §7 and must be updated with them; it is a second place
those numbers live. It must fail on *absence*, never on content quality, which
stays expert-judged. When Stage 0 completes, the gate goes quiet on its own and
the remaining failures are all real.

---

## ADR-0019 — Keyphrase extraction is an ensemble of TextRank, YAKE and KeyBERT; spaCy NER is metadata

**Date** 2026-08-17 · **Authority** human · **Status** accepted

**Context.** The roadmap's Stage 2 §2.1 names **YAKE** alone for keyphrase
extraction, and puts a statistical spaCy NER model under §2.3 as one route to
*new entity discovery*. `ARCHITECTURE.md` §5 carried that stack unchanged, noting
that substitutions are ADR-worthy.

**Decision.** The repo owner has decided the Stage 2 candidate-generation stack:

- **Three keyphrase extractors run over the same text, in parallel:**
  **TextRank** (graph-based, co-occurrence), **YAKE** (statistical, single
  document), **KeyBERT** (embedding similarity to the document).
- **spaCy NER output is attached to candidate terms as additional metadata.**
  It is not a keyphrase extractor and it is not the entity taxonomy. It
  annotates; it does not decide.

This extends the roadmap rather than contradicting it — §2.1's YAKE is retained
and joined, and §2.2's rule-based recognition (`EntityRuler`, `PhraseMatcher`,
regex, authoritative lists) is untouched.

**Rationale.** The three methods fail differently: YAKE on frequency and position
statistics within one document, TextRank on graph centrality in a co-occurrence
network, KeyBERT on distance in embedding space. That is the point of running
all three — **agreement across methods is itself a confidence signal**, and it is
a cheap one, available before any expert has graded anything. A term all three
find is a different proposition from a term only KeyBERT finds, and Stage 3's
review queue can be ordered by that without a model.

The corpus argues for it too. Legal drafting is repetitive and formulaic, which
flatters frequency-based methods and lets a boilerplate phrase outrank a term of
art. An embedding-based method and a graph-based one fail in a different
direction, so the disagreements are informative rather than noise.

**Consequences.**

1. **Provenance must record which extractor produced a candidate**, per CLAUDE.md
   rule 8 and ADR-0011. `extraction_method` becomes an enum including
   `textrank`, `yake`, `keybert` and the rule-based paths, and a term found by
   several methods is **one record carrying several methods**, not several
   records. That is not free: the candidate-id formula in `IDENTIFIERS.md` §3
   hashes `method`, so as written it mints three ids for one span. ADR-0020
   addresses it, and it must be settled before parallel-track P3 implements the
   formula.

2. **KeyBERT introduces an embedding model into a pipeline that was otherwise
   deterministic.** TextRank and YAKE are deterministic; KeyBERT's output depends
   on which sentence-transformer is loaded. The model **and its version must be
   pinned** alongside the snapshot pin (ADR-0004) and recorded on every candidate,
   because a silent model upgrade changes candidate output and therefore
   invalidates every measured baseline taken before it. This is CLAUDE.md rule 7
   holding: the deterministic methods stay deterministic and are not to be
   replaced by the embedding one.

3. **KeyBERT is local inference, not an LLM API call.** It does not engage
   HANDOFF Q3, provided the model runs in the agency's own environment. If it is
   ever served from a hosted endpoint, Manual text leaves the environment and Q3
   applies in full.

4. **spaCy NER must not be used for provisions, cases or internal refs.** Upstream
   already extracts those deterministically, with `extraction` and `certainty`
   attached. Re-deriving them from a statistical model would breach CLAUDE.md
   rule 2 and would replace trust metadata with a confidence score — strictly
   worse. Upstream's edges win wherever they exist; NER metadata is for the text
   upstream says nothing about. See Q-16 for the label trap this creates.

5. **Stage 0 measurement gains a dimension.** Entity precision, recall and F1 must
   be computable **per method**, and for the union and the intersection, or there
   is no evidence on which to weight the ensemble or to retire a method that is
   not earning its place. Agents may propose these metrics; thresholds remain the
   owner's (guide §5.9).

6. The stack rows in `ARCHITECTURE.md` §5 are updated. The roadmap text is not —
   it is a source document (ADR-0003), and the divergence is recorded here.

---

## ADR-0020 — The candidate id is content-addressed without the method

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0021** (was provisional, HANDOFF Q10)

**Context.** `IDENTIFIERS.md` §3 mints a machine-generated candidate id as
`sha256(source_ref | span_start | span_end | method | normalised_value)`, so that
re-running a pipeline over unchanged input is a no-op. With one extractor that
works. ADR-0019 introduces three, plus rule-based paths, and the same term at the
same span now mints a different id per method — three `review/` entries for one
candidate, and the cross-method agreement that ADR-0019 exists to capture is
invisible on every one of them.

**Decision.** Drop `method` from the hash. A candidate is identified by
**`source_ref | span_start | span_end | normalised_value`**, and the methods that
found it are a **set-valued field** on the record — `extraction_methods: [yake,
textrank]` — alongside each method's own score. One span, one candidate, N pieces
of evidence for it.

**Rationale.** The identifier should answer "which thing is this", and the thing
is the term at that span. Which detectors fired is evidence *about* it, not part
of its identity. Keeping method in the id also makes the no-op property false in
the way that matters: adding a fourth extractor would re-mint every candidate in
the repo rather than adding a method to existing ones.

The alternative — per-method ids plus a merge step — was rejected because the
merge would have to run before any human sees the queue, which makes it the real
identity function while leaving a second, misleading one in the id.

**Consequences.** Records gain a set field, so provenance is per method inside
one record: each entry carries its own method, score and model version (ADR-0019
consequence 2), while `source_span` and `review_status` stay at record level. An
approval decision then attaches to the candidate, not to one detector's view of
it, which is the correct grain — the reviewer is judging a term, not a detector.

Re-running with a new extractor mutates existing records rather than creating
new ones, so the byte-stability check becomes "unchanged input plus unchanged
extractor set produces byte-identical output". Adding an extractor is a
deliberate, visible change to every affected record, which is the honest
representation of what it is.

`IDENTIFIERS.md` §3 is annotated with this proposal rather than rewritten, since
this is agent-proposed and provisional. Parallel-track **P3 must not implement
the §3 formula until Q10 is closed** — it is one of the few genuinely
order-dependent things on that track.

---

## ADR-0021 — Owner confirmations: ADR-0004, ADR-0005, ADR-0017 and ADR-0020

**Date** 2026-08-18 · **Authority** human · **Status** accepted

**Context.** Six agent-proposed ADRs stood provisional, each flagged in
`HANDOFF.md` §3 as awaiting the owner. Provisional decisions are load-bearing —
code gets written against them — so leaving them open indefinitely means the
repo is built on assumptions nobody has ratified.

**Decision.** The repo owner confirmed four, in session S003:

| ADR | Now settled as | Closes |
|---|---|---|
| **0004** | The upstream snapshot is a **pinned release download** into `data/upstream/`, out of git, with `extractor_version` and the upstream commit SHA in a tracked manifest | **Q2** |
| **0005** | **Upstream refs are canonical.** `TMM/Part22/1/1/2` and `TMA1995/s43` are the identifiers; IRIs are minted by prefixing them; the roadmap's `tmem:manual/2026-01/…` form is not used | **Q5** |
| **0017** | The Pass B worksheet is printed **now**, from an over-inclusive provisional scope rule set by the owner, without waiting on the expert boundary. The rule itself is ADR-0022 | **Q9, in part** — gate G1 released |
| **0020** | The content-addressed candidate id **drops `method`** from the hash; the methods that found a span become a set field | **Q10** |

Each of the four keeps its original text and reasoning; what changed is its
authority, from `agent-proposed` to confirmed. Rather than edit four past
entries — `DECISIONS.md` is append-only — each carries a one-line
`Confirmed by ADR-0021` annotation, which is the same mechanism the file's
header already sanctions for `Superseded by`.

**Still open, deliberately.** The owner was asked about ADR-0017 only, so the
rest of Q9 stands: **ADR-0016** (the parallel track itself) and **ADR-0018**
(Stage 0 incompleteness reported, malformed data fails the build) remain
agent-proposed. So do **ADR-0006**, **ADR-0011**, **ADR-0012** and **ADR-0014**,
which were not put. Q3, Q4, Q6, Q7 and Q8 are untouched.

**Consequences.** Parallel-track **P1 is unblocked** and is now the critical
path — it gates P2, P6 and P9. **P3 is unblocked in full**, candidate id
included. `IDENTIFIERS.md` §3 is updated from a proposal to the operative
formula. Nothing here touches Stage 0's content or ADR-0010: the wall at G5
stands exactly where it did.

---

## ADR-0022 — The provisional worksheet scope rule

**Date** 2026-08-18 · **Authority** human · **Status** accepted — provisional by design

**Context.** ADR-0017 established that the Pass B worksheet is printed from a
deliberately over-inclusive machine rule the owner sets alone, rather than
waiting on `eval/pilot-scope.md`. It did not say what the rule is. Parallel-track
P9 cannot run on a principle.

**Decision.** The worksheet prints:

1. Every chunk whose `provisions[]` contains a ref for **`TMA1995/s43`** —
   matching the provision **and any unit beneath it**, so `TMA1995/s43(1)`,
   `TMA1995/s43(1)(a)` and the bare `TMA1995/s43` all qualify. Matching is on
   the ref grammar (`IDENTIFIERS.md` §1), not on a substring: `TMA1995/s430`
   must not match if the corpus ever grows one.
2. Plus **every other chunk sharing a `page_ref`** with a chunk selected by (1)
   — the page-mates.

Edges of **every** `extraction` and `certainty` value are included: `href` and
`regex`, `explicit`, `default` and `ambiguous` alike. An `ambiguous` edge is a
reason to print a chunk, never a reason to drop one.

**Rationale.** Page-mates are in because the Manual's guidance frequently sits in
the chunks around the one that carries the citation — an instruction, then its
exceptions, then a worked example, with the provision named once at the top.
Selecting only citing chunks would print the sentence and drop the practice.

Including ambiguous and default edges follows Q-07: those are upstream refusing
to guess, and a worksheet that silently omits them hides exactly the material a
human is needed for.

**Consequences.** Worksheet scope is **not** pilot scope, and the two must never
be conflated — the worksheet header states the rule, the pinned
`extractor_version`, and that it is provisional. When the expert boundary lands
in `eval/pilot-scope.md`, the worksheet is regenerated and the delta reported;
annotations made against rows later ruled out of scope are parked, not deleted,
exactly as `pilot_in_scope: false` parks a competency question.

The rule is expected to over-select, and that is the design. If P6's counts show
it selecting an unworkable volume, the answer is to report the number and ask,
not to quietly tighten the rule.

---

## ADR-0023 — `#` is percent-encoded when minting an IRI; nothing else is

**Date** 2026-08-18 · **Authority** derived · **Status** accepted

**Context.** `IDENTIFIERS.md` §2 mints an IRI as `<BASE>ref/<ref verbatim>` and
says explicitly not to percent-encode, because `(` and `)` are legal in an IRI
path and some tooling encodes them anyway. That reasoning is right about
parentheses. It is wrong about `#`, and 498 of the corpus's 2,460 chunk refs
contain one (`TMM/Part26/6#3~2`). A `#` opens a fragment (RFC 3986 §3.5), so the
minted IRI names `<BASE>ref/TMM/Part26/6` plus a fragment — a different subject,
silently, for one chunk in five.

**Decision.** `to_iri` escapes `#` as `%23` and escapes nothing else. `from_iri`
reverses it. The round-trip is asserted over every ref in the pinned corpus, and
a separate test asserts that no other character is ever encoded.

**Rationale.** Forced, not chosen: an IRI containing an unescaped `#` is not an
IRI for that resource, whatever anyone intends. Confining the exception to one
character keeps `IDENTIFIERS.md` §2's actual point — that parentheses and tildes
survive — intact, and keeps the encoding reversible so refs remain the stored
form everywhere outside RDF (§4).

**Consequences.** `IDENTIFIERS.md` §2's "do not percent-encode" is now "escape
`#`, and nothing else". A future serialiser that percent-encodes more will fail
`test_percent_encoding_is_confined_to_the_hash` rather than quietly producing a
second set of IRIs for the same resources. Recorded as Q-17.

---

## ADR-0024 — Candidate value normalisation is mechanical and stops there

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** provisional

**Context.** `IDENTIFIERS.md` §3 hashes `normalised_value` into the candidate id
without saying what normalisation is. It decides when two spans are one
candidate, so it cannot be left undefined once code exists.

**Decision.** NFKC, casefold, collapse internal whitespace, strip. Nothing else.
No stemming, no lemmatising, no article-stripping, no synonym folding.

**Rationale.** Anything cleverer is a claim that two surface forms *mean* the
same thing, which is Stage 3's question and an expert's answer — not a hash
function's. A blunt normaliser splits candidates that a human would merge, and
that error is visible and cheap to fix in review; a clever one merges candidates
a human would have kept apart, and that error is invisible and permanent.

**Consequences.** "the marks" and "mark" mint different ids. Accept it. If a
normalisation change is ever wanted it re-mints every affected candidate, so it
is a deliberate, breaking act and belongs in its own ADR.

---

## ADR-0025 — A ref whose level the grammar cannot decide is reported, not guessed

**Date** 2026-08-18 · **Authority** derived · **Status** accepted

**Context.** Building `refs.py` against the corpus turned up two collisions the
documents do not mention. A Manual page ref and a chunk ref share a grammar
(`TMM/Part14/4/4/5` could be either). A provision ref and the ref of a defined
term inside a provision share a grammar too — `TMR1995/sch3/item1` is a
provision, `TMA1995/s128/prescribed-period` is a unit. 228 legislation refs in
the pinned corpus are undecidable this way.

**Decision.** `parse_ref` returns `RefKind.MANUAL` or `RefKind.LEGISLATION` for
these — well-formed, level not settled — rather than picking the likelier
reading. A caller that read the ref out of a known field (`page_ref`, `units[]`)
may state the level and is believed. Deciding it otherwise requires the snapshot
and belongs to the loader.

**Rationale.** CLAUDE.md rule 6. The available heuristics all work until they
do not: segment counts differ per ref, and telling `sch3/item1` from
`s128/prescribed-period` means guessing that a slug with digits is structural
and one without is a definition. A wrong guess here attaches an annotation to
the wrong level of the corpus and nothing downstream would notice.

**Consequences.** Consumers must handle a third answer. That is the honest
shape of the data. Recorded as Q-18.

---

## ADR-0026 — The pin is a commit, a receipt and a tree digest

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** provisional

**Context.** ADR-0004 (confirmed by ADR-0021) fixes a "pinned release download".
Upstream publishes no releases and no tags (Q-19), and its default branch is not
even its newest state — scheduled crawl branches run ahead of `main`.

**Decision.** The pin is a **commit sha**, fetched by sha with
`git fetch --depth 1 origin <sha>`. `data/pin.json` is tracked and holds only
properties of the pinned release — repo, commit, extractor versions, the paths
taken, the corpus counts and a tree digest. What a given container actually
fetched goes in a git-ignored receipt, `data/upstream/.fetch.json`. Verification
checks all three: receipt commit, corpus counts, tree digest.

Separately: an upstream field the loader does not know about **stops the load**.

**Rationale.** Fetching by sha is what makes the pin a pin; cloning a branch and
hoping is not. Splitting pin from receipt keeps a tracked file from churning on
every fetch while still letting a session prove what it is reading. The tree
digest is the only check that catches a hand edit inside `data/upstream/`, which
`data/README.md` calls an invisible fork of the corpus. And schema drift is
precisely the event the pin exists to make visible, so it should be loud rather
than absorbed.

**Consequences.** Bumping the pin means recomputing the digest and the counts
(`tmk-fetch-upstream --write-digest`) in a deliberate commit that says what
moved. The counts check earned itself immediately by rejecting a wrong number in
the first pin written. `data/README.md`'s illustrative `pin.json` (which carried
a `fetched_at`) is superseded by this shape.

---

## ADR-0027 — Stage 0 schemas check shape; judgement fields are required-but-nullable

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** provisional

**Context.** P4 asks for machine-checkable schemas that "must never encode a
judgement". Two questions fall out immediately and neither is answered by the
templates: what happens to a record an expert has not finished, and what
constrains a field whose vocabulary is itself expert-owned.

**Decision.**

1. Every field is **required as a key**; judgement fields are **nullable as a
   value**. A record missing `modality` fails validation; a record with
   `modality: null` passes and is reported as a gap.
2. `predicate` is **not enumerated**. The approved relationship dictionary does
   not exist, and listing plausible predicates would be an agent writing it.
   When the dictionary lands the enum is generated from it.
3. Ref-shaped fields are checked by `tm_knowledge.refs`, via a `format:
   upstream-ref` checker, so the grammar has one authority.
4. Schema `$id`s sit under `https://ipaustralia.gov.au/schemas/tmk/…`, matching
   upstream's convention and deliberately *not* the project base IRI, which is
   unconfirmed (Q7) and belongs to resources rather than documents.

**Rationale.** (1) is the difference between a schema that helps and one that
makes transcription impossible: an agent must be able to write down exactly what
an expert said, no more, and have the gaps counted (P8, P10). Making the key
mandatory is what keeps the gap visible instead of absent. (2) is CLAUDE.md
rule 1 applied to a vocabulary rather than to prose.

**Consequences.** Schema validity and Stage 0 completeness are different checks,
on purpose — the completeness gate (P5, ADR-0018) is where a null becomes a
failure. Writing the drift check also found that five gold record templates had
no `approved_by`/`approved_date` at all, though the guide's definition of done
requires them everywhere; the templates now carry them.

---

## ADR-0028 — Generated artefacts live in `data/derived/` and are not committed

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** provisional

**Context.** P6's reconnaissance report and P9's worksheet are both documents
for a human to read, and both are pure functions of the pinned snapshot plus the
code.

**Decision.** They are written to `data/derived/`, which is git-ignored, by
`tmk-recon` and `tmk-worksheet`. `--out` puts a copy anywhere. Their rendering
takes an injected date so that everything except that date is a function of the
pin, and two runs are byte-identical.

**Rationale.** `data/README.md`'s own rule: if it can be rebuilt from
`data/upstream/` plus `src/`, it belongs in `data/derived/`. Committing a
worksheet would put a second, dateable copy of 40,000 words of the corpus in
this repo's history, and the copy would go stale silently the moment the pin
moved. Determinism is what makes ADR-0022's promise — regenerate when the expert
boundary lands and report the delta — actually computable.

**Consequences.** The owner cannot read the worksheet from GitHub without
running one command. That is the cost, and the alternative costs more. Headline
numbers that inform a decision belong in `HANDOFF.md`, where they are read
without running anything.

---

## ADR-0029 — Code layout: `upstream/` and `stage0/` subpackages

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** provisional

**Context.** `src/README.md` sketched `refs.py` and `loader.py` at package top
level. The parallel track's P2 names `src/tm_knowledge/upstream/`, and Stage 0's
apparatus (schemas, recon, worksheet, and later the harness and coverage report)
is a second cluster with the same cohesion.

**Decision.** `tm_knowledge/refs.py`, `config.py` and `provenance.py` stay at top
level — they are used by everything. Snapshot reading lives in
`tm_knowledge/upstream/` (`pin`, `fetch`, `records`, `loader`); the Stage 0
apparatus lives in `tm_knowledge/stage0/` (`schemas`, `recon`, `worksheet`,
`cli`). Python package directories document themselves in their `__init__.py`
docstring rather than carrying a `README.md`.

**Rationale.** The subpackage split follows the parallel track's own package
boundaries, so a work package maps to a module rather than to a scattering of
files. On the README point: ADR-0012 requires a README per directory so the next
session does not have to guess what belongs there — a package whose `__init__.py`
opens with that answer satisfies the intent, and a README beside it would be a
second copy to drift. Non-package directories (`tests/unit/`, `eval/schemas/`,
`tests/fixtures/stage0/`) carry READMEs as ADR-0012 requires.

**Consequences.** `src/README.md` is updated to the real layout. If a future
session finds a package whose purpose is not stated in its `__init__.py`, that
is the bug — not the missing README.

---

## ADR-0030 — The harness has three severities, and three exit codes

**Date** 2026-08-19 · **Authority** agent-proposed · **Status** provisional — implements ADR-0018

**Context.** ADR-0018 fixed the principle: Stage 0 incompleteness is a reported
state, malformed data is a build failure. P5 had to turn that into something a
shell can act on. Two severities and two exit codes turned out to be one short.

**Decision.** Every harness finding carries one of three severities:

- **DEFECT** — something that arrived is wrong. A record that does not validate,
  a duplicated or retired id, a dangling cross-reference, a `source_ref` that
  resolves to nothing, a `span` that does not land on its recorded text, a stale
  `source_content_hash`, a gold file whose name is not recognised.
- **GAP** — something expected has not arrived. A deliverable missing, a count
  under its band, an unapproved record, a judgement field still null.
- **NOTE** — an observation no machine can judge. A concept with no `not_labels`;
  a case ref, which no corpus in this programme can resolve (Q-11).

`tmk-harness` exits **1** on any defect, **3** when the findings are only gaps,
and **0** when there are none and the resolution checks actually ran. CI passes
`--allow-incomplete`, which maps 3 to 0 and never touches 1.

**Rationale.** The third severity exists because of `not_labels`. The guide asks
for it "wherever a near-miss exists", and whether one exists is an expert's
reading. Gating on it would make Stage 0 uncompletable; dropping it would lose
the guide's most valuable field. A severity that reports and gates nothing is the
honest third option, and once it existed the case refs wanted it too.

The third *exit code* exists because `--allow-incomplete` has to forgive one
thing and not the other, and a boolean cannot express "forgive the gaps and keep
failing on the defects".

**Consequences.** Anything reading the harness's exit status must treat 3 as a
report, not a failure. The severity of a check is a decision, not an
implementation detail: moving a check between DEFECT and GAP changes whether it
breaks a build, and is an ADR-worthy change rather than a tweak.

---

## ADR-0031 — A run that did not open the snapshot never reports Stage 0 complete

**Date** 2026-08-19 · **Authority** derived · **Status** accepted

**Context.** Half the harness's checks need `data/upstream/`, which is
git-ignored and may be absent — on a bare clone, or in CI when the fetch fails.
The easy behaviour is to run the structural half, find nothing wrong, and report
success.

**Decision.** `Report.complete` is false whenever the resolution checks did not
run, regardless of what the structural half found, and the absence is itself
recorded as a gap naming what could not be checked.

**Rationale.** This is the vacuity trap of ADR-0018 in a second costume. A
gapless report from a run that never opened the corpus has verified no ref, no
span and no hash; calling that "complete" is exactly the green-for-the-wrong-
reason outcome the guide forbids. Unverified is not sound, and the distinction
disappears the moment one report can mean both.

**Consequences.** CI's snapshot fetch is best-effort and its failure is visible
rather than silent: the tests that need the corpus skip, the harness says the
resolution checks did not run, and the run summary carries a warning. A green CI
run without a snapshot is a degraded run and reads as one.

---

## ADR-0032 — One gold file per record type, named; an unrecognised file is an error

**Date** 2026-08-19 · **Authority** agent-proposed · **Status** provisional

**Context.** `eval/gold/README.md` named six files and the repo has eight record
types. The harness has to find records before it can check them, and "whatever
YAML is in the directory" is not a contract.

**Decision.** `eval/gold/` holds exactly one file per record type, at a fixed
name (`entities.yaml`, `concepts.yaml`, `relationships.yaml`,
`search-questions.yaml`, `retrieval-questions.yaml`, `reasoning-expected.yaml`,
and the two the README had not named: `competency-questions.yaml`,
`prohibited-uses.yaml`). Each is a YAML list of records. A `.yaml` file whose
name is not in that table is a **defect**, not a file to skip. `retired-ids.yaml`
is the single exception and is optional.

**Rationale.** Rule 6, applied to a directory listing. The failure mode being
prevented is specific and silent: an expert's records land in `entites.yaml`, the
harness sees no entities, the coverage report says `0 of 100–300`, and a day of
specialist work reads as work never done. Refusing to guess makes that a
one-line error instead.

One file per type rather than a directory per type because `eval/gold/README.md`
already asks for record changes to be reviewable as diffs, and a file per record
makes a rename look like a deletion and an addition.

**Consequences.** A gold set large enough to want splitting will need this ADR
superseded rather than worked around. At the top of the entity band that is 300
records in one file, which is a long file and still one diff.

---

## ADR-0033 — Withdrawn ids are recorded in a ledger, not remembered

**Date** 2026-08-19 · **Authority** agent-proposed · **Status** provisional

**Context.** `IDENTIFIERS.md` §3 requires human-facing ids to be allocated by
appending and never to fill a gap left by a withdrawal. The harness has to check
non-reuse, and a withdrawn record is by definition not in `eval/gold/` any more —
so nothing in the live data records that `GC-0042` was ever used.

**Decision.** `eval/gold/retired-ids.yaml` lists withdrawn ids with the date and
the reason. Reusing one is a defect. The file is optional: its absence means
nothing has been withdrawn.

**Rationale.** The alternative is deriving the highest allocated id from the live
set, which silently re-issues the id of every record withdrawn from the tail. Git
history holds the answer but no check can reasonably read it, and a rule that is
only enforceable by archaeology is not enforced.

**Consequences.** Withdrawing a record is two edits — remove it, and record the
id. Forgetting the second is not detectable, which is why it belongs in the same
commit and is stated in `eval/gold/README.md`.

---

## ADR-0034 — Ref-valued fields are read off the schemas, not listed

**Date** 2026-08-19 · **Authority** derived · **Status** accepted

**Context.** The resolution checks need to know where in a record an upstream ref
sits. There are fourteen such places across the eight types, some nested two
levels down (`relevant[].ref`, `expected_inferences[].basis[]`).

**Decision.** `schemas.ref_paths(record_type)` walks the JSON Schema, follows its
`$ref`s into `common.schema.json`, and returns every path whose definition
carries `format: upstream-ref`. Nothing lists those fields by hand.

**Rationale.** A hand-maintained list is a second place the schema lives, and its
failure mode is silence: a new ref-valued field simply never gets resolved, and
the harness reports a clean gold set it did not fully check. Deriving the list
means adding a ref field to a schema automatically puts it under the checks.

**Consequences.** The walker must understand every construct the schemas use to
express a ref — `$ref` by `$id`, `$ref` by fragment, `items`, `properties`,
`oneOf`. A schema that expresses one some other way would go unchecked, so
`test_ref_paths_find_the_nested_ones` pins the four shapes that exist today.

---

## ADR-0035 — `openpyxl` is an optional extra, not a core dependency

**Date** 2026-08-19 · **Authority** agent-proposed · **Status** provisional — the dependency is the owner's call

**Context.** P7 requires a spreadsheet workbook with enum dropdowns.
`pyproject.toml` carries a standing note that adding a dependency is a decision
to raise rather than to make, and the core install is three packages.

**Decision.** `openpyxl` is declared under two optional extras — `intake`, for
anyone using the workbook, and `test`, so CI exercises the round trip. Neither
`pip install -e .` nor any module outside `workbook.py` and `transcribe.py`
touches it, and both import it inside the function that needs it so a missing
install produces one sentence of advice rather than an ImportError at startup.

**Rationale.** `.xlsx` with real dropdowns is the format the guide's §6 promise
depends on — "do not write YAML" is only true if the alternative validates as
you type — and openpyxl is the only maintained pure-Python writer for it. CSV
would drop the dropdowns, which is precisely the part that stops an
out-of-vocabulary value being invented. But nothing else in the repo needs it,
so it does not belong in the core install.

**Consequences.** If the owner would rather not carry the dependency at all, the
fallback is CSV plus a validation pass after the fact, which moves the error
from the moment of typing to the moment of transcription. Raised in HANDOFF §3.

---

## ADR-0036 — How a record becomes a spreadsheet: dotted columns, newline lists, child sheets

**Date** 2026-08-19 · **Authority** agent-proposed · **Status** provisional

**Context.** Three record shapes do not fit a flat grid: nested objects
(`expected_sources.required`), arrays of scalars (`alt_labels`, every ref list),
and arrays of objects (`relevant[]`, `expected_inferences[]`).

**Decision.**

- A nested object becomes **dotted columns** — `expected_sources.required`.
- An array of scalars becomes **one cell, one value per line**.
- An array of objects becomes **its own sheet**, one row per entry, linked by a
  `parent_id` column (`GS--relevant`, `GX--expected_inferences`).
- `span` is written as two integer columns, `span.start` and `span.end`, and a
  row with one of them filled is rejected rather than half-read.

The layout lives in `stage0/intake.py`, derived from the schemas, and both the
generator and the transcriber read it — a column exists in exactly one place.

**Rationale.** Newlines rather than a separator character because upstream refs
contain `/`, `(`, `)`, `~`, `#` and `.`, and any separator that can occur inside
a value is a data-loss bug waiting for the first value that uses it. A test
covers a value containing both a comma and a semicolon.

Child sheets rather than parallel lists in one cell because parallel lists pair
the third ref with the third grade *by convention*, and nothing notices when
that stops being true. A graded relevance judgement silently attached to the
wrong passage is a corrupted measurement standard, and it would be invisible.

**Consequences.** An expert filling in graded passages works across two sheets
and repeats an id. That is the cost, and it buys a link a machine can check: a
`parent_id` naming no record is rejected and reported.

---

## ADR-0037 — Transcription writes every required key, optional keys only when filled, and nothing at all without `--write`

**Date** 2026-08-19 · **Authority** agent-proposed · **Status** provisional

**Context.** P8 writes into `eval/gold/`, which is approved space (CLAUDE.md
rule 4). Three questions had to be answered before it could write anything: what
to do with a blank cell, what to do with a row that is not yet a record, and
whether writing should be the default.

**Decision.**

1. **A required key is always written, even as null.** That null is the gap the
   coverage report names (ADR-0027). An **optional** key that arrived empty is
   dropped, because `notes: null` on every record buries the real gaps.
2. **A row is rejected, not stubbed,** when a non-nullable required field is
   blank, when a value is outside its enum, when half a span is given, or when
   the assembled record does not validate. Rejections are listed with the sheet
   and row number.
3. **`tmk-transcribe` is a dry run** and reports what would change. `--write` is
   required to touch `eval/gold/`.
4. **An empty sheet leaves its file untouched.** It means "I have nothing for
   this yet", never "delete what is there".

**Rationale.** (2) is the rule that keeps transcription honest: every rejection
listed is a case where the only way to proceed would be to choose a value, and
choosing between `must`, `may` and `should` is a legal reading (guide §5.4). A
tool that stubs the row has made that reading and hidden it.

(3) because a command that writes into the measurement standard should not do it
as a side effect of being run to see what it would do.

**Consequences.** Records are written in the schema's property order and compared
before writing, so re-running over unchanged input leaves git status clean. A
record type can only be *emptied* by editing its file directly, which is
deliberate — deleting approved records is not something a spreadsheet import
should be able to do by omission.

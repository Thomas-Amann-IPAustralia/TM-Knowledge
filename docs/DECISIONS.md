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

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0040**

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

**Date** 2026-08-04 · **Authority** agent-proposed (field list) · **Status** provisional — **field list deferred by owner, see ADR-0041**

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

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0040**

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

**Date** 2026-08-06 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0040**

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

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0038** (was provisional, HANDOFF Q9)

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

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0038** (was provisional, HANDOFF Q9)

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

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0040**

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

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** **accepted — confirmed by ADR-0040**

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

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** **accepted for now — confirmed by ADR-0040**

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

**Date** 2026-08-18 · **Authority** agent-proposed · **Status** **superseded by ADR-0042** — owner wants a committed paper trail

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

---

## ADR-0038 — Owner confirmations: ADR-0016 and ADR-0018

**Date** 2026-08-19 · **Authority** human · **Status** accepted

**Context.** ADR-0021 confirmed four of the six agent-proposed ADRs standing
against HANDOFF Q9 in session S003; ADR-0016 (the parallel track itself) and
ADR-0018 (the harness's completeness-gate/genuine-failure split) were left open
because the owner was not asked about them at the time. Both are load-bearing —
ADR-0018 is CI's actual pass/fail logic today — so leaving them open indefinitely
means the repo runs on an assumption nobody has ratified.

**Decision.** The repo owner confirmed both, asked directly in session S006:

| ADR | Now settled as | Closes |
|---|---|---|
| **0016** | The parallel track exists as described: twelve work packages needing no legal judgement, the five-gate table, the not-to-do list | **Q9, remainder** |
| **0018** | Stage 0 incompleteness is a reported state (the completeness gate); a malformed record, dangling ref, unlanded span or stale hash is a genuine build failure | **Q9, remainder** |

Each keeps its original text and reasoning; only its authority changes, from
`agent-proposed` to confirmed, via a one-line `confirmed by ADR-0038` annotation
on its Status line — the same mechanism ADR-0021 used.

**Consequences.** HANDOFF Q9 is fully closed. Nothing structural changes: both
ADRs were already governing the build (P5, P11) as written: this removes their
provisional flag, not their effect.

---

## ADR-0039 — The approval artefact is a name and a date, in the workbook's own columns

**Date** 2026-08-19 · **Authority** human · **Status** accepted

**Context.** HANDOFF Q4 asked what "approved" should look like as a recorded
artefact — a signed-off file in git, or an external register — for the
`approved_by`/`approved_date` fields every gold record schema already requires
(ADR-0027) and every intake workbook sheet already carries as columns
(ADR-0036). Nothing writes a meaningful value into either column without an
answer.

**Decision.** The approval record **is** the two columns: an approving expert's
name in `approved_by` and a date in `approved_date`, carried straight through by
`tmk-transcribe` into `eval/gold/*.yaml`. No separate signed-off file, no
external register — the git history of the gold YAML (who committed the
transcription, and the review that merged it) is the audit trail behind the two
values, not a second artefact alongside them.

**Rationale.** This is the option that needs no new tooling: P7 and P8 already
build it exactly this way, so the decision confirms existing behaviour rather
than requiring a change. It keeps the approval record next to the thing it
approves rather than in a system this repo cannot version alongside its data.

**Consequences.** A record with `approved_by`/`approved_date` both null is
reported by the completeness gate (ADR-0018) as a gap, same as before — the
mechanism does not change. **Still open:** *who* the approving experts are is
unanswered — that half of Q4 stands and is expected to arrive with the experts'
Stage 0 content itself.

---

## ADR-0040 — Owner confirmations: ADR-0006, ADR-0012, ADR-0014, ADR-0024, ADR-0026, ADR-0027

**Date** 2026-08-19 · **Authority** human · **Status** accepted

**Context.** Session S006 put the remaining agent-proposed ADRs to the owner as
a plain-language summary rather than a yes/no form, per the owner's request.
Six came back confirmed, each with its original text and reasoning kept intact;
only the authority changes, via a one-line `confirmed by ADR-0040` annotation on
each entry's Status line — the mechanism ADR-0021 and ADR-0038 already used.

**Decision.**

| ADR | Confirmed as | Owner's added note |
|---|---|---|
| **0006** | Organise by artefact type, not roadmap stage | none |
| **0012** | Working conventions (Australian English, lowercase-hyphenated dirs, a README per directory) | none |
| **0014** | A separate expert-facing Stage 0 input guide | **A work order referencing the guide has already been issued to the Trade Mark experts.** The owner also asked for more plain-language guidance on *constructing the ontology* specifically — that is new work, not yet scoped or drafted, and is logged as an open item in `HANDOFF.md` rather than written speculatively here |
| **0024** | Candidate normalisation is mechanical only (NFKC, casefold, whitespace) | Owner's own words: normalisation "should occur mechanically and based on a consistent and explainable ruleset" — matches the decision as written |
| **0026** | The pin is a commit sha, receipt and tree digest | **Standing invitation, not an action:** if a better pinning method exists — e.g. upstream adding releases or tags — the owner wants it proposed on the roadmap for consideration, since upstream infrastructure itself may be amended if the case is good enough. Nothing changes until such a case is made |
| **0027** | Schemas check shape only; judgement fields required-but-nullable | **Conditional:** confirmed *for now*. If a CI/CD gating policy is added later, a null judgement field may become a loud failure instead of a silent gap — that would be a new ADR superseding this one, not a reinterpretation of it |

**Consequences.** Two of the six carry a live trigger rather than a flat
acceptance, and both are worth remembering rather than acting on now: ADR-0026
stays as written until someone makes a documented case for a different upstream
pinning mechanism; ADR-0027 stays nullable until a CI/CD policy decision is
made and recorded as its own ADR. Neither is scheduled work.

---

## ADR-0041 — ADR-0011's provenance field list stays open until Stage 2's actual output is known

**Date** 2026-08-19 · **Authority** human · **Status** deferred — revisit before the Stage 2 candidate schema is finalised

**Context.** ADR-0011 proposed a fixed provenance field list —
`extraction_method`, `model`, `confidence`, `source_span`, `source_content_hash`,
`review_status`, `reviewer`, `review_date`, `created_at` — as an agent's best
guess ahead of any extraction actually running. ADR-0019's ensemble decision
already complicated it once: `extraction_method` has to become a set with a
per-method score and model version (ADR-0019 consequence 1; ADR-0020's
candidate-id rework is the identifier-side half of the same problem).

**Decision.** The owner declined to confirm the field list now. **Wait until
Stage 2's candidate generation actually runs** (TextRank, YAKE, KeyBERT,
ADR-0019) and its real output shape is visible, and check whether any
additional fields can be **derived deterministically** — rather than fixing
the schema on a guess and having to revise it once real metadata exists.

**Rationale.** This is not a rejection of the field list; it is a sequencing
call the owner is better placed to make than an agent inventing plausible
fields ahead of any evidence. It also keeps CLAUDE.md rule 7 (prefer
deterministic derivation over judgement) live at the schema-design stage, not
just at extraction time.

**Consequences.** ADR-0011 stays `provisional` rather than moving to
`accepted`, with a pointer to this entry. Nothing currently reads or writes
against the field list — P12's provenance module (ADR-0011's own
implementation) predates this deferral and should be reviewed against
whatever Stage 2 actually emits before the field list is finalised, **not**
before Stage 2 exists. ADR-0010's wall (no Stage 2 before Stage 0 is complete)
means this cannot be revisited until then regardless.

---

## ADR-0042 — Stage 0's generated reports and derived artefacts are committed to the repository

**Date** 2026-08-19 · **Authority** human · **Status** accepted — **supersedes ADR-0028**

**Context.** ADR-0028 kept `data/derived/` (the worksheet, the recon report,
the coverage report, the intake workbook) git-ignored and always rebuildable,
on the reasoning that a committed copy would go stale silently and duplicate
what `data/upstream/` plus `src/` can already regenerate. The owner wants the
opposite: a committed paper trail of what these reports said and when.

**Decision.** `data/derived/` is now **tracked**, not git-ignored. Every
regeneration (`tmk-recon`, `tmk-worksheet`, `tmk-coverage`, `tmk-workbook`) is
committed like any other change, and its diff — or its absence, when nothing
moved — is the paper trail: when the worksheet's chunk count changed, when
recon's volume numbers moved, when coverage's gap list shrank.

**This does not touch `data/upstream/`**, which stays git-ignored. That is a
different question — ADR-0004's decision not to vendor a second copy of
another repo's corpus into this repo's git history — and nothing about wanting
a paper trail of *this repo's own* generated output argues for duplicating
*upstream's* data as well. The two directories now have different policies for
different reasons, and that split is deliberate, not an oversight.

**Consequences.**

1. `.gitignore` drops the `data/derived/` line; `data/README.md` and the
   `stage0/cli.py` module docstring — both of which stated the old "never
   commit, always rebuildable" rule — are updated to match.
2. Determinism (byte-identical output for unchanged input, already required by
   P6/P9/P10's own "done when" criteria) now matters even more than it did
   under ADR-0028: it is what keeps a re-run's diff clean when nothing
   substantive changed, rather than noise from incidental reordering.
3. The intake workbook (`stage0-intake.xlsx`) is a binary file generated
   purely from the schemas — committing it is **agent-proposed**, not part of
   what the owner asked for by name, on the reasoning that treating all of
   `data/derived/` under one policy is simpler than splitting it further, and
   it only changes when a schema changes. Flagged in `HANDOFF.md` in case the
   owner would rather exclude it.
4. `HANDOFF.md` §4's "do not commit anything under `data/` except `pin.json`
   and the README" is now wrong and is corrected in the same commit as this
   ADR.

---

## ADR-0043 — A machine-written seed example set is produced for expert correction

**Date** 2026-08-21 · **Authority** human · **Status** accepted

**Context.** Stage 0 has been unblocked on the agent side since S005: the
worksheet prints 216 chunks, the intake workbook ships empty with a dropdown on
every fixed vocabulary, the transcriber reads it back without inventing a field,
and the coverage report turns an hour of expert time into a moved counter. None
of that produced content. The owner reports the reason, and it is not
availability: **the Trade Mark experts cannot readily articulate the judgements
the record types ask for**, because those judgements are the tacit part of their
practice. A blank form asks them to state — cold, in writing, in a schema — what
they normally exercise without stating. Recognising a wrong answer is a
different and much cheaper act.

**Decision.** An agent produces a large **seed example set** over the s 43
pilot: candidate records in every Stage 0 shape, grounded in the pinned
snapshot, deliberately fallible, for the experts to mark *correct*, *amend* or
*reject*. The corrected set becomes the gold set. A later, larger set is then
generated in the same shapes and the experts' second pass is validation rather
than correction.

**This runs against CLAUDE.md rule 1** — "never invent legal content" — and the
owner made that trade knowingly. The rule is not repealed. What changes is
narrow and the boundary is enforced mechanically rather than promised:

1. **Quarantine.** The set lives in `review/seed/`, inside the boundary ADR-0007
   exists to protect. It is not in `eval/`, `vocab/`, `ontology/` or `graph/`.
2. **Filenames that cannot be misread.** `*.seed.yaml`. `goldset.py` reads eight
   fixed names and treats an unrecognised `.yaml` in `eval/gold/` as an error
   (ADR-0032), so a misfiled seed file **stops the harness** rather than being
   counted as expert judgement.
3. **An envelope, not a bare record.** Every record sits inside a `seed_id`, a
   `why_this_example`, a provenance block and a review verdict. A record cannot
   be lifted out of the file and mistaken for one an expert wrote.
4. **`approved_by` and `approved_date` are null, and checked.** A seed record
   carrying either is a **defect** that stops `tmk-seed`, and a test asserts it
   over the shipped directory. This is the load-bearing guard: the whole risk of
   a seed set is that it quietly starts looking approved.
5. **One door out.** A corrected record leaves only through
   `tmk-transcribe --write`, with an expert's name in `approved_by`. Nothing is
   promoted, copied or moved by any other route, and `tmk-seed` never writes to
   `eval/gold/`.
6. **The harness is untouched.** `tmk-harness` still exits 3 and still reports
   all 22 Stage 0 deliverables as absent, because they are. The seed set moves
   no counter.

**Rationale.** The failure mode rule 1 guards against is a plausible-looking
invented record being copied forward and treated as approved. That risk is
highest when the invented content is *indistinguishable* from expert content —
which is exactly what the six guards above prevent. Against it stands a
programme that has been stalled at its first stage for four sessions with a
complete apparatus and no content, and a named reason for the stall that more
apparatus cannot fix.

**Consequences.**

1. `review/seed/` holds 368 records: 24 competency questions, 18 prohibited
   uses, 52 concepts, 153 entities, 58 relationships, 26 search questions, 22
   retrieval questions, 15 reasoning expectations, plus draft `pilot-scope` and
   `measures` documents. All expert-owned content, none of it approved.
2. `tmk-seed` checks the set, resolves every span against the snapshot and
   renders it two ways — a Markdown review pack and a pre-filled review
   workbook (ADR-0044).
3. **The entity annotation rule and the relationship predicate list are the two
   highest-value corrections**, and both are stated at the top of their files
   rather than buried in records. `entities.seed.yaml` annotates one chunk under
   a stricter rule than the rest so the two densities can be compared;
   `relationships.seed.yaml` opens with fourteen invented predicates and says in
   terms that the guide forbids inventing them.
4. **`model` is null on every record.** HANDOFF Q3 — which LLM is
   agency-approved, and under what data-handling conditions — is open, and
   stamping a model name into the repository would pre-empt an organisational
   decision. `generator` and `generated_on` identify the run; the session log
   identifies the session. If the agency later requires the model recorded, it
   is a provenance field, not a record change.
5. `eval/STAGE-0-INPUT-GUIDE.md` §9's promise — "an agent may say *we have no
   question testing point-in-time currency*; an agent may not write that
   question" — is now qualified for `review/seed/` and holds everywhere else.
   The guide is updated to say so rather than left to contradict the tree.
6. **A seed file is deleted once its record type has been through review.** Two
   versions of the same records, one approved and one not, is worse than no seed
   file at all.

**What would reverse this.** Evidence that the seed set is anchoring rather than
prompting — an expert marking records `correct` at a rate that suggests reading
rather than judging, or corrections that only ever adjust wording and never
reject a shape. Both are visible in the verdict distribution, which is why the
verdict is a recorded field rather than a marked-up document.

---

## ADR-0044 — The seed review workbook is a separate file; the intake workbook stays empty

**Date** 2026-08-21 · **Authority** derived · **Status** accepted

**Context.** ADR-0043 needs the seed set in a medium an expert will actually
correct, and the intake workbook is already that medium — same layout, same
dropdowns, and `tmk-transcribe` already reads it back. But P7's rule, restated
in HANDOFF §4, is absolute: **no example row in the intake workbook, not even a
marked one**, because in a spreadsheet copying a row is one keystroke.

**Decision.** Two files, one layout.

- `data/derived/stage0-intake.xlsx` — generated by `tmk-workbook`, **empty**,
  unchanged. Still the right thing for someone composing from scratch.
- `data/derived/stage0-seed-review.xlsx` — generated by `tmk-seed --workbook`,
  the same sheets pre-filled with seed records, plus three columns at the
  right-hand end: `seed_id`, `verdict`, `correction`. Different filename,
  different first sheet, and a verdict cell on every row.

`tmk-transcribe` is taught to **tolerate** those three headers rather than
reject them as unknown columns. They are annotations *about* a record, never
fields *of* one, so they are dropped on the way into `eval/gold/`: a verdict is
how a record came to be approved, not something the record asserts.

**Rationale.** P7's rule protects a blank form from being contaminated by a
plausible filled row. It does not argue against a *differently named file whose
entire purpose is to be corrected*, where every row carries a verdict column
that is empty until a person fills it. Keeping one workbook and adding a mode
flag would have collapsed the distinction the rule depends on.

Teaching the transcriber three extra headers rather than writing a second reader
follows the same reasoning as `intake.py` itself: there is exactly one place the
workbook layout lives, and a second reader would eventually be a second layout.

**Consequences.**

1. `intake.REVIEW_COLUMNS` is the single definition of the three headers, read
   by both `seedpack.py` and `transcribe.py`. A test asserts they collide with
   no schema field name.
2. The corrected seed workbook round-trips: 368 records read back with zero
   rejected rows and every blank `approved_by` reported rather than filled.
3. `tmk-seed --pack` renders the same records as Markdown with the source
   passage quoted under each and the span in bold, for experts who would rather
   mark up a document than a spreadsheet. Both are regenerated from the same
   YAML and neither is authoritative over it.

---

## ADR-0045 — Seed spans are computed from the snapshot, never written by hand

**Date** 2026-08-21 · **Authority** derived · **Status** accepted

**Context.** A gold entity or relationship carries `span` — character offsets
into the chunk `text` — and `source_content_hash`. The guide promises the expert
will never type either (§3). The seed set creates the same problem in the other
direction: an agent writing 211 span-bearing records by hand would get some of
them wrong, and every correction to a `surface` would silently invalidate its
offsets.

**Decision.** Seed records carry `span: null` and `source_content_hash: null` on
disk. `tmk-seed` locates the recorded `surface` (or `supporting_text`) in the
chunk and fills both from the pinned snapshot at render time. Where a surface
appears more than once, the envelope's `locate.occurrence` says which mention is
meant; where the hint is **missing on an ambiguous surface, the tool reports it
and stops** rather than resolving to the first hit (rule 6).

`review/seed/*.seed.yaml` is never rewritten by the tool. The files carry the
comments that make them readable, and a round trip through a YAML dumper would
eat them; the resolved records live in the pack and the workbook instead.

**Rationale.** Offsets are mechanical and a hand-written one is a defect waiting
to be discovered by the harness. Making them derived means an expert who
corrects a surface form gets a correct span for free — which is the difference
between a correction costing ten seconds and costing a round trip.

The refusal to guess an occurrence is the same refusal upstream makes on an
ambiguous citation (Q-07): picking the first hit would be right most of the time
and wrong invisibly.

**Consequences.**

1. `harness.passage_at` exists so the seed resolver and the harness's span check
   use one resolver. A seed record that passes here cannot fail there for a
   reason a reader could not see.
2. A surface that has been retyped rather than copied fails loudly, naming the
   record. The corpus contains typographic quotation marks, an en dash where a
   hyphen appears elsewhere, a term broken across a line as "International Non-
   Proprietary Name" (Q-25) and at least one sentence with a word missing
   (`TMM/Part29/8/8/3`), and every one of those has to survive verbatim.
3. Nothing in `review/seed/` needs regenerating when the pin moves — the spans
   were never stored. The records go stale in the same way gold records do, and
   the tool says so on the next run.

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

**Date** 2026-08-21 · **Authority** derived · **Status** accepted — **column list amended by ADR-0046**

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

---

## ADR-0046 — The seed review workbook prints the passage and the reason beside every row

**Date** 2026-08-21 · **Authority** human (owner asked for it) · **Status** accepted — **amends ADR-0044's column list**

**Context.** ADR-0044 gave the seed review workbook three review columns:
`seed_id`, `verdict`, `correction`. Handing the pair of artefacts to the owner
exposed the flaw immediately. On the entity and relationship sheets a reviewer
gets `surface`, `source_ref` and two integer character offsets — and no way to
see the sentence those offsets point into. They would be judging blind. The
passage and the record's rationale existed only in the Markdown review pack, so
the honest instruction was "read in one file, write in the other", which is two
windows and a lookup per row for 211 rows.

That is not a documentation problem. A workbook that cannot be judged from is
not a correction surface, and ADR-0043's whole premise is that correcting must
be cheaper than composing.

**Decision.** `intake.REVIEW_COLUMNS` becomes five, in this order:

| Column | Written by | Holds |
|---|---|---|
| `seed_id` | the tool | the record's stable handle |
| `why_this_example` | the tool | what the record is there to demonstrate |
| `passage` | the tool | the Manual text the row rests on, span in **bold** |
| `verdict` | the reviewer | correct · amend · reject |
| `correction` | the reviewer | what is wrong, in their words |

`intake.REVIEW_WRITABLE` names the last two. The read-only three are grey; the
two a reviewer fills in are the only coloured columns on the sheet.

**Where `passage` comes from, per row.** A span-bearing record (entity,
relationship) gets its own passage centred on the span. A record with no span
gets the text of its **first** ref, prefixed with that ref and a count —
`TMM/Part29/2/2/1~1 — definition_sources (1 of 2): …` — because a concept with
three definition sources must not read as though it had one. A `GS--relevant`
continuation row gets the text at its own `ref`, which is what makes regrading
possible at all. `GX--expected_inferences` rows name a list of bases rather than
one ref and stay blank; the parent row's passage carries them.

**Consequences.**

1. **The span is bolded with rich text, not bracketed.** The Manual's own text
   is full of brackets — `[2000] FCA 720`, `(or authorised user)`, `<stem>` — so
   a marker that can occur in the data is a reader's problem the first time it
   does. `openpyxl`'s `CellRichText` round-trips; where the module is absent the
   cell falls back to plain text, because a workbook that will not open is worse
   than one without bold, and `tmk-transcribe` reads either form identically.
2. **Nothing about the round trip changes.** The transcriber already ignored the
   review columns; it now ignores five instead of three. A test fills `verdict`
   and `correction` and asserts neither reaches the transcribed record. 368
   records still read back with zero rejected rows.
3. **The passage is regenerated, never stored.** It is rebuilt from the pinned
   snapshot on every `tmk-seed --workbook`, so it cannot drift from the record —
   the same reasoning as ADR-0045, applied to the display rather than the offset.
   A reviewer who corrects a `surface` sees the passage catch up next run.
4. **The pack is still the better read and is no longer the only judgeable
   artefact.** Both are regenerated from the same YAML; neither is authoritative
   over it. An expert can now work entirely in the workbook, entirely in the
   pack, or in both.
5. Rows carrying a passage get a fixed height of 78 points — five or six wrapped
   lines. Enough to read the sentence, short enough that 153 rows still scroll.

---

## ADR-0047 — `approved_date` is a typed date column, and an ambiguous one is refused

**Date** 2026-09-02 · **Authority** derived · **Status** accepted

**Context.** The first marked-up workbook came back and `tmk-transcribe` rejected
270 rows. Every rejection was the same field: the schema wants
`^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, and the sheet held `25/08/2026` on some sheets
and a real Excel date cell — which `openpyxl` hands over as a `datetime` and
`str()` renders as `2026-08-25 00:00:00` — on others.

The consequence was worse than a failed run, and it is the reason this has an
ADR rather than a one-line fix. The rows that failed were **exactly the rows the
expert had signed**, because only a signed row carries a date at all. The 233
rows that passed and would have been written into `eval/gold/` were precisely
the ones nobody had approved. A field intended to record authority had inverted
the gate.

Three readings were available for `25/08/2026`: day/month (Australian, and what
the reviewer meant), month/day, or refuse. The repo is Australian throughout
(CLAUDE.md §5), which argues for the first. Rule 6 argues for the third.

**Decision.** `approved_date` becomes a `date` column kind, derived from the
schema's `format: "date"` rather than from the field's name, and it is read in
this order:

1. a `datetime`/`date` object — Excel already parsed it under the typist's
   locale, so it is unambiguous by the time it arrives; convert it;
2. an ISO string — pass it through, after checking it is a real date;
3. a slashed string whose first number **cannot** be a month (`25/08/2026`) —
   convert it, because it has only one reading;
4. anything else, `05/08/2026` included — **refuse**, naming the cell and saying
   to write `YYYY-MM-DD`.

The generated workbook formats the column `yyyy-mm-dd`, so Excel resolves the
ambiguity at typing time and case 4 rarely arises.

**Consequences.**

1. **Australian-first is a reading rule, not a parsing rule.** Case 3 supplies
   nothing — it reformats a value with one possible meaning. Case 4 is the one
   where being Australian would be a guess, and a wrong `approved_date` is the
   worst kind of provenance defect: nothing downstream cross-checks it, so it
   would look correct for ever. Refusing costs one email; guessing costs the
   audit.
2. **The column format is help, not a guarantee.** `openpyxl` writes the column
   style but not `customFormat`, and a reviewer can always paste text over a
   formatted cell. The guarantee stays on the read side.
3. **The format is set on the column dimension, not on a block of cells.**
   Formatting a thousand cells materialises a thousand rows, and the intake
   workbook must ship with none (ADR-0044).
4. The same kind now covers any future `format: "date"` field, because it is
   read from the schema. Nothing hard-codes `approved_date`.

---

## ADR-0048 — The verdict column is the gate into `eval/gold/`, and the gate is transitive

**Date** 2026-09-02 · **Authority** agent-proposed · **Status** accepted

**Context.** ADR-0044 called the review columns "annotations *about* a record,
never fields *of* one", and the transcriber implemented that by tolerating them
and dropping them. Correct as far as it went, and it left the actual door
unlocked: `tmk-transcribe --write` wrote every row that validated, so a record
an expert had just marked **reject** would have gone into `eval/gold/` alongside
one they had approved. `review/seed/HOW-TO-CORRECT.md` had already promised the
opposite — "the records that carry your name become the gold set" — and nothing
implemented it.

The first returned workbook made the shape of the problem concrete: 368 rows,
229 carrying a verdict, 8 rejections, 8 amendments, 83 marked correct with
nobody's name against them, and 139 never reached.

**Decision.** When a workbook carries a `verdict` column it is a seed review
workbook, and a row enters `eval/gold/` only on a `correct` verdict **with a
name in `approved_by`**. Every other row is *held* — read, understood, and
deliberately not written — under one of five reasons:

| reason | what it means |
|---|---|
| not reviewed | the verdict cell is empty |
| rejected by the reviewer | the record should not exist |
| amendment not applied | marked `amend`; the correction has not been worked in |
| correct but unsigned | a judgement was made and not signed |
| names a record that is not approved | see below |

A verdict cell holding anything else — `corrrect` — is a **rejected row**, not a
held one: nothing infers the value it resembles (rule 6).

On a child sheet, where approval lives on the parent, a `reject` **drops the
entry** from the parent's list, because that is what the reviewer decided; any
other unsettled verdict **holds the parent whole**, because the list is part of
the record.

The gate is closed **transitively**. Approval does not distribute over an
interlinked set: `PU-0001` is a true prohibition on its own terms, and its
`related_questions` names `GA-0003`, which is unsigned. Sign the first and not
the second and `eval/gold/` acquires a pointer to nothing — which `tmk-harness`
reports as a DEFECT, correctly, because a measurement standard with a dangling
reference is not one. So any record naming an unapproved record is held too, to
a fixed point.

**A workbook with no `verdict` column is unaffected.** The plain intake workbook
has none, and every row goes through as before.

**Consequences.**

1. **The first run cost 18 records to the transitive rule** — 15 prohibited uses
   pointing at unsigned questions, and 3 retrieval questions that then pointed
   at those prohibitions. 126 records passed the per-row gate; 108 landed. That
   gap is the honest number and it makes the next ask precise: signing
   `GA-0001`–`GA-0018` and `CQ-0013`/`CQ-0014` releases 18 more records with no
   further judgement.
2. **"Correct but unsigned" is reported as its own state**, not lumped in with
   the unread rows. It is a judgement that was made and not recorded, which is a
   different and much cheaper thing to fix — and 83 of the round's rows are in
   it.
3. **The alternative was worse.** Relaxing the harness's cross-reference check
   to also look in `review/seed/` would let approved knowledge rest on
   unapproved candidates, which is rule 4 inverted.
4. This is not the harness's job. The harness reports the state of what is in
   `eval/gold/`; the gate decides what gets there. A defect the gate can prevent
   should not be left for the harness to find.

**Confirm.** `agent-proposed`. The rule "signed `correct` only" follows from
rule 4 and ADR-0039, but three choices inside it are judgements: holding a
signed record because an unsigned one is pointed at, holding a parent for an
unsettled child, and treating a misspelt verdict as a rejected row rather than
reading through the typo. Flagged in `HANDOFF.md` §3 as Q18.

---

## ADR-0049 — A review round is recorded in `review/decisions/`; the seed copies are then retired

**Date** 2026-09-02 · **Authority** derived · **Status** accepted

**Context.** ADR-0043 consequence 6 says to delete a seed file once its record
type has been reviewed, because two versions of one record — approved and not —
is worse than none. `tmk-seed` enforces it: a seed record whose id is in
`eval/gold/` is a DEFECT, since an id is never used twice (`IDENTIFIERS.md` §3).

A partial round breaks the rule as stated. 108 of 368 records were approved, so
whole-file deletion applies to one record type and leaves collisions in five.
And two things resist deletion at all: a **rejection with a reason** is the
round's most expensive output and would vanish with the row, and other seed
records point at rejected ones (`must_not_infer: PU-0017`).

**Decision.** `tmk-reconcile WORKBOOK --write`, run after
`tmk-transcribe --write`:

1. writes the round into `review/decisions/<workbook slug>.md` and `.yaml` —
   every record, its verdict, the reviewer's correction **verbatim**, and what
   became of it;
2. removes from `review/seed/` every record whose id is now in `eval/gold/`,
   and only those. Unreviewed, amended, unsigned and **rejected** records all
   stay;
3. deletes a seed file left holding nothing.

Two supporting changes. `seed._cross_references` now resolves a pointer against
`eval/gold/` as well as `review/seed/` — a promoted target was not deleted, and
without this every promotion would break the records left behind. And
`seed.coverage` reads the ledgers, so it reports 139 unreviewed of 242 rather
than 242 of 242, which was false the moment a round came back.

**Consequences.**

1. **Rejected records stay, on purpose.** They have no approved twin, so they
   are not the duplication the rule is about, and removing them would turn a
   recorded rejection into a dangling pointer. The rejection lives in the
   ledger; the record stays where things point at it.
2. **The prune is line surgery, and it is verified.** Seed files are
   hand-written and their comments carry the entity annotation rule and the
   candidate predicate list — the two decisions the whole set turns on — so
   re-serialising the YAML would destroy the most valuable part of the file.
   Entries are removed by line range instead; the result is parsed back and
   every surviving record compared field by field before anything is written. A
   mismatch refuses the file and writes nothing.
3. **A verdict is not written back into the seed file.** The file is the
   expert's input; the ledger is the record of their answer. Keeping them apart
   means one author per document, and it is the only arrangement that still
   works once an approved record has left the seed file entirely.
4. **The ledger regenerates.** It is derived from the returned workbook, which
   is kept unmodified in `review/returned/`, so a re-run reproduces it. Nothing
   in `review/decisions/` is hand-edited.

---

## ADR-0050 — A returned artefact lives in `review/returned/`, unmodified

**Date** 2026-09-02 · **Authority** derived · **Status** accepted

**Context.** The marked-up workbook and the expert's covering note arrived in
`data/derived/`. That directory is committed on purpose (ADR-0042), but for one
reason: it holds **derivations** — what `tmk-*` regenerates from the pinned
snapshot and from `eval/gold/` — and the diff of each regeneration is the paper
trail. An inbound artefact is the opposite. Nothing regenerates it, a tool run
must never overwrite it, and "delete `data/derived/` and rebuild" is a thing
somebody will eventually do.

`review/seed/` is not right either: `tmk-seed` reads that directory and would
report a returned workbook as a file it does not recognise.

**Decision.** `review/returned/` holds what a person outside this repo produced
and handed back, unmodified and dated in the filename. The two artefacts of the
first round are
`review/returned/260825-ontology-stage-0-seed.xlsx` and
`review/returned/260826-expert-feedback.md`.

**Consequences.**

1. **A returned artefact is not edited, ever** — not to fix a typo, not to
   correct a verdict. `corrrect` in a verdict cell stays typed; the ledger
   reports it as unreadable and the correction comes back from the reviewer,
   because nobody here may decide what they meant. A second pass arrives as a
   new file with its own date.
2. The covering note gained a provenance header — who, when, filed when — above
   the untouched text. Provenance about an artefact is not a modification of it,
   but the header says explicitly that nothing below it changed.
3. `review/` now holds three kinds of thing and each has a README saying which:
   `seed/` what we wrote for review, `returned/` what came back, `decisions/`
   what was decided.

---

## ADR-0051 — A reviewer's instruction is applied from `review/returned/`, never by editing a workbook

**Date** 2026-09-02 · **Authority** agent-proposed · **Status** accepted

**Context.** The first round left 83 records marked `correct` with `approved_by`
blank, and one verdict cell reading `corrrect`. The reviewer then settled both
in words, relayed by the owner: those 83 are signed `TC`, and the misspelt cell
means `correct`.

Both are recorded human decisions. Neither is in a spreadsheet. Three ways to
act on them were available and two are wrong:

- **Edit the returned workbook.** Forbidden by ADR-0050, and rightly: a binary
  file an agent has altered, sitting where the expert's own artefact sits, is
  the exact confusion that directory exists to prevent.
- **Generate a new "returned" workbook** with the 84 cells filled in. Same
  problem wearing a different filename — `review/returned/` would then hold an
  agent-authored artefact indistinguishable at a glance from a human one.
- **Record the instruction as its own artefact and apply it.** The instruction
  *is* what the person handed back; it is text rather than a spreadsheet.

**Decision.** An **addendum** is a YAML file in `review/returned/` naming the
reviewer, the date, the words as relayed, and exactly what is to be applied.
`tmk-transcribe --addendum` and `tmk-reconcile --addendum` apply it as if the
reviewer had typed it into the cells. Two operations, and no others:

- `sign_unsigned_correct: true` — fill a **blank** `approved_by` on a row whose
  verdict is `correct`, with the reviewer's name and the instruction's date.
- `verdicts: {GE-0031: correct}` — settle a verdict on a **named** record.

**Consequences.**

1. **The signing rule is deliberately the narrowest thing that does the job.**
   It never overwrites a name already present, and it signs nothing whose
   verdict is not `correct` — not an `amend`, not a `reject`, not an unreviewed
   row. Widening it to "sign everything" would make the instruction a blank
   cheque rather than a decision about a defined set.
2. **`verdicts` names records one at a time. There is no pattern, no fuzzy match
   and no typo table.** `corrrect` is read as `correct` because a person said so
   about `GE-0031`, not because it resembles it. ADR-0048's refusal to read
   through a near-miss is unchanged and still fires for anything not named —
   the `rejext` on a `GS--relevant` row is still a rejected row, because nobody
   has ruled on it.
3. **An addendum cannot reach a child row.** Child rows carry no id to name and
   no `approved_by` of their own. Changing one costs a workbook, which is the
   right price for it.
4. **An instruction it cannot act on exactly is refused**, not partially
   applied: no reviewer, no date, an ambiguous date, or a verdict the
   instruction itself misspells. The strictness applies to the instruction as
   much as to the workbook.
5. **Every application is reported and recorded.** `tmk-transcribe` prints each
   row and what was done to it; the ledger names the addendum in its front
   matter and marks each affected row *by instruction*. How a record came to be
   approved is part of the record of its approval.
6. `--addendum` must be passed to **both** commands or the ledger describes a
   different run from the one that produced `eval/gold/`.

**Confirm.** `agent-proposed`. The mechanism follows from ADR-0050 plus the need
to act on a real decision, but the two-operation limit is a judgement about what
words may safely stand in for keystrokes. Flagged in `HANDOFF.md` §3 as Q20.

---

## ADR-0052 — Reviewer ruling: the 83 unsigned `correct` rows are signed TC; `GE-0031` reads `correct`

**Date** 2026-09-02 · **Authority** human · **Status** accepted

**Context.** Put to the owner after the first round: 83 records had a verdict and
no signature, and one verdict cell was misspelt. `tmk-transcribe` had held all
84 rather than guess.

**Decision**, relayed by the owner from the reviewer:

- every row marked `correct` with a blank `approved_by` is approved by **TC**;
- the cell on `GE-0031` reading `corrrect` means `correct`.

Recorded as `review/returned/260902-expert-confirmation.yaml` and applied under
ADR-0051.

**Consequences.**

1. **The gold set went from 108 records to 190** — and the 82 extra approvals
   released 8 more records that had been held only because they pointed at
   unsigned ones. `eval/gold/entities.yaml` and `reasoning-expected.yaml` exist
   for the first time.
2. **This settles ADR-0048's third judgement call in practice rather than in
   principle.** The tool still refuses a misspelt verdict; a person overrode it
   by name. That is the arrangement the refusal was designed to produce, and it
   cost one line in an instruction file. It is **not** a ruling that a near-miss
   may be read through generally — if that is wanted it needs its own decision,
   and it would be a worse one, because the set of things `corrrect` could mean
   is only obvious to a reader who already knows the answer.
3. **The remaining blockers are now six records, not eighty-three**: `CQ-0013`
   and `CQ-0014` (never reviewed), `CQ-0016`, `PU-0016` and `PU-0017` (rejected,
   so records pointing at them need the pointer changed) and `GA-0002` (an
   amendment not yet applied). Between them they hold 20 records that are
   otherwise ready.
4. The `rejext` on a `GS--relevant` row is **not** covered by this ruling and
   was left alone. It holds nothing — its parent `GS-0007` is unreviewed anyway.

---

## ADR-0053 — The review queue is a graph, and the report that says so is generated

**Date** 2026-09-02 · **Authority** derived · **Status** accepted

**Context.** ADR-0048 made the gate transitive, and the arithmetic stopped being
readable. After round 1: 213 records carried `correct`, 190 reached
`eval/gold/`, and the 23 that did not were held by six records scattered
elsewhere in a 368-row workbook. S008 worked out which six **by hand**, wrote
them into `HANDOFF.md` §2, and got two of the three chains slightly wrong — the
list under `GA-0002` omitted `GX-0006`, and the list under `CQ-0014` omitted
`GA-0021` and `GX-0014`. A hand-derived dependency analysis over an interlinked
set is wrong on arrival and stale by the next round.

**Decision.** `tmk-blockers` computes it. It reads three committed artefacts —
the ledgers in `review/decisions/`, the survivors in `review/seed/`, and
`eval/gold/` — and reports, for every record not yet approved: the gate's own
reason for holding it, what it names that is not approved, and the transitive
set of records it is holding. Output: `data/derived/reports/blockers.md`.

It is the pair to `tmk-coverage`. Coverage says what Stage 0 is missing; this
says which decision on the queue releases the most.

**Why this is `derived` and not a judgement.** Three things force it:

- ADR-0048 made holding transitive, so the queue is a graph rather than a list.
  Nothing else in the repo reports a graph.
- ADR-0042 made `data/derived/` committed, so a generated report is the repo's
  established way of stating a fact about itself.
- Rule 6. The hand-written version was wrong in two of three chains, and nothing
  detected that, because nothing was checking.

**Consequences.**

1. **It reads no workbook.** The ledger already carries every parent verdict,
   every reviewer sentence, and every child-row mark including the unreadable
   one — `tmk-reconcile` was writing all of it and nothing was reading it back.
   So the report needs no `.xlsx` reader, runs from a bare checkout with no
   optional extra, and stays true after the workbook that produced it is closed.
2. **It imports the gate's reason constants from `transcribe`** rather than
   restating them. A report describing a gate that does not exist is worse than
   no report, and `test_every_gate_reason_has_a_statement_of_what_is_needed`
   fails the moment a seventh reason appears.
3. **It proposes nothing.** Where a record names one that was rejected it gives
   the two options the gate allows — repoint or withdraw — and says the choice
   is an expert's. That is arithmetic about the door, not an opinion about trade
   marks law (rule 1).
4. `HANDOFF.md` §2 stops carrying a hand-maintained blocker list. It points at
   the report.
5. **CI runs it**, beside `tmk-coverage`, and its exit 1 breaks the build. That
   is not a duplicate of the harness: the harness reads `eval/gold/` only, so a
   *seed* record naming an id that exists nowhere is invisible to it. Such an id
   was constructed rather than read, which is a defect under ADR-0018's meaning
   of the word, not a gap.

---

## ADR-0054 — What counts as a decision on the critical path

**Date** 2026-09-02 · **Authority** agent-proposed · **Status** provisional

**Context.** A report that lists 178 held records has told a reviewer nothing.
The useful output is the much smaller set where *their* pen changes something,
and picking that set is a judgement about what "actionable" means.

**Decision.** A held record is on the critical path when any of three things is
true, and only then:

1. **It holds at least one other record and its own state is one a reviewer
   resolves directly** — unreviewed, awaiting an amendment, or unsigned.
2. **It names a record the reviewer rejected.** No amount of reviewing anything
   else can satisfy that pointer, so this record repoints or it withdraws.
3. **It is signed and held only by a marked row on its own child sheet.** The
   cheapest kind there is: the parent is already approved.

Two exclusions carry as much weight as the rule:

- **A record held only by a pointer at something merely unreviewed is not a
  decision.** It is correct, signed, and it enters `eval/gold/` on the next
  transcription after the record it names does. Twelve records are in that
  position; putting them on a worklist asks a reviewer to read records that are
  already answered. The report lists them separately, under *Carried by a
  decision above*, with the decision that settles each.
- **A rejected record is not waiting on anything.** It is finished, negatively.
  It stays in `review/seed/` so the rejection and its reason survive, and it is a
  sink in the dependency graph, never a source. Counting it as a dependent
  reported `GA-0016` as *holding* `PU-0016`, which is backwards: the rejection is
  why `GA-0016` has to change, not something `GA-0016` releases.

**The judgement being flagged.** Rule 1 does **not** require the root to be
unblocked. `GA-0002` awaits an amendment and names `PU-0013` and `PU-0014`, both
of which name `GA-0002` straight back; nothing outside that triangle releases any
of it, and the amendment releases all of it. An "unblocked roots only" rule is
simpler, defensible, and would have hidden the largest single decision on the
queue. Flagged in `HANDOFF.md` §3 as Q21.

**Consequences.**

1. Round 1's queue of 178 becomes **10 decisions**, and the report says what each
   one releases: `GA-0002` (8), `CQ-0014` (6), `CQ-0013` (3), `PU-0012` (2), then
   six that release nothing further but are themselves stuck.
2. `tmk-blockers --ids` prints exactly those ten, in that form, so the scoped
   round is one shell pipeline rather than a transcribed list.
3. **Three search questions surface that no hand analysis had found.** `GS-0001`,
   `GS-0002` and `GS-0004` are signed and held only by relevance-grade rows the
   reviewer marked `amend`. Search questions stand at 1 of a target 20–50, so
   three child rows are worth four times the current count of the record type
   furthest from its band.
4. Any change to what "actionable" means changes what a reviewer is asked to do.
   It is a decision, not a tuning parameter.

---

## ADR-0055 — A review round may be scoped, and both artefacts must say so

**Date** 2026-09-02 · **Authority** agent-proposed · **Status** provisional

**Context.** The blocker analysis is only worth having if the reviewer can be
handed the ten records rather than the 178. `tmk-seed` rendered the whole of
`review/seed/` or nothing.

**Decision.** `tmk-seed --only ID,ID,…` narrows the **rendering** to the named
records, accepting either id form (`CQ-0013` or `SEED-CQ-0013`). Three guards:

1. **The checks never narrow.** `check()` and `coverage()` run over the whole of
   `review/seed/` regardless, because a subset cannot tell you the set is sound,
   and a round scoped to ten records must not also scope the defect report to
   ten records.
2. **A name that matches nothing refuses the run.** A round scoped to ten records
   and silently rendered over nine is a loss nobody looks at again (rule 6).
3. **Both artefacts declare the scope on their face** — the pack in its banner,
   the workbook on its `how to use this` sheet — with the count it was narrowed
   from and a pointer to `blockers.md` for why these records. A scoped round that
   does not say it is scoped is indistinguishable from a complete one, and a
   reviewer who believes they have seen everything stops looking.

**The judgement being flagged.** Guard 3 is the agent's, and it is the one that
matters: the alternative — a scoped workbook that looks exactly like a full one
— is how a partial review comes to be recorded as a complete one. Flagged in
`HANDOFF.md` §3 as Q22.

**Consequences.**

1. The return leg is unchanged. A scoped workbook goes back through
   `tmk-transcribe` and `tmk-reconcile` like any other, because ADR-0049 already
   reconciles per record rather than per file.
2. `data/derived/` gains two artefacts per scoped round —
   `blockers-review-pack.md` and `stage0-blockers-review.xlsx` — beside the full
   pair, which stay as they are.
3. Nothing about `--only` may be used to narrow what the harness or the seed
   checks look at. If a future flag wants that, it is a different decision.

---

## ADR-0056 — Formalising approved content is not Stage 2, and may proceed

**Date** 2026-09-03 · **Authority** derived · **Status** accepted

**Context.** ADR-0010 stops Stage 2 and everything after it until Stage 0 is
complete, and it is right to: the first plausible output becomes the standard by
arriving first, which is the failure the whole roadmap is arranged around. But
Stage 0 now holds **190 approved records** — 52 concepts with synonyms and
non-synonyms, 55 typed mentions with character spans, 35 relationships with
modality and tier — and the owner needs a working demonstration of what an
ontology buys, over one section, without waiting on further expert time.

**Decision.** Building the vocabulary, the ontology and the knowledge graph
**from records that already carry a name and a date** is a different activity
from Stage 2 extraction, and is permitted. `tmk-graph` does it.

**The distinction, stated so it cannot be blurred later.** Stage 2 *creates*
content: it runs an extractor over raw text and produces candidates nobody has
seen. This *changes the form* of content a person already signed. The test is
whether the output could contain a proposition no reviewer approved. For an
extractor the answer is yes and that is the point of it; for this build the
answer is no, and three guards keep it no:

1. `tmk-graph` **refuses to run** against a gold set holding any record with a
   blank `approved_by`, and a test asserts the refusal.
2. Every emitted node carries `tmk:approvedBy`, `tmk:approvedDate` and
   `tmk:goldRecord`, so any triple can be traced to the row that was signed.
3. The classes whose membership would be a legal judgement are declared and
   **provably empty**, with a test that they stay that way.

**Consequences.**

1. **ADR-0010 is untouched.** No TextRank, YAKE, KeyBERT or spaCy run has
   happened or may happen. `docs/ROADMAP-STATUS.md` still reports Stage 2 as not
   started, because it has not started.
2. **The stage order is departed from, deliberately.** The roadmap assumes Stage
   2 supplies the vocabulary that Stage 3 organises. Here Stage 3's input is the
   approved gold set instead. That is a smaller and better-founded vocabulary
   than an extractor would produce, and it is 52 concepts rather than hundreds.
3. **The demonstration is exactly as complete as the review got**, and the
   report says so at the top rather than in a footnote.
4. What this does **not** license: populating a class, resolving a conflict
   between two approved records, or filling a judgement field. All three stay
   with a person.

---

## ADR-0057 — A concept keeps its gold id; there is no second register

**Date** 2026-09-03 · **Authority** agent-proposed · **Status** provisional

**Context.** `IDENTIFIERS.md` §3 sketches SKOS concepts as `tmkc:c-0042`,
allocated sequentially in a register file. The approved concepts already have
stable ids — `GC-0001` and up — allocated in `eval/gold/concepts.yaml`.

**Decision.** The concept IRI is `tmkc:GC-0001`. No `c-nnnn` register is created.

**Why.** The rule in §3 exists so that a label can be revised without the
identifier moving. `GC-0001` already satisfies that. Minting a second identifier
for the same concept would create two registers with no allocator between them
and one obvious failure mode: they drift, and then a query returns half a
vocabulary. One register, one identifier, nothing to reconcile.

**The judgement being flagged.** This is a deviation from a governing document,
and the argument against it is real: gold records are *evaluation* records, and
using their ids as vocabulary ids conflates the thing being measured with the
measuring stick. Today they are the same thing, because the gold concepts are
the only concepts. If Stage 3 ever produces concepts that are not gold records,
this has to be revisited — and it is one function, `model.concept_iri`, and a
rebuild. Flagged in `HANDOFF.md` §3 as Q23.

---

## ADR-0058 — Turtle is emitted without a library; rdflib is optional

**Date** 2026-09-03 · **Authority** derived · **Status** accepted

**Context.** `graph/` is committed (ADR-0042) so that the diff between two
builds is the paper trail. Serialisers do not promise stable output ordering.

**Decision.** A small deterministic writer in `graph/turtle.py` emits every
generated `.ttl`: subjects sorted, `a` first, then predicates alphabetically,
then objects. `rdflib` is an **optional extra** (`[graph]`), used to read the
result back, validate it and run SPARQL — never to write it.

**Consequences.**

1. Two builds over unchanged input are byte-identical, and a test asserts it. A
   one-concept change is a one-concept diff.
2. The core install stays at three dependencies. Emitting needs nothing;
   querying needs the extra. Same shape as `openpyxl` and `[intake]` (ADR-0035).
3. **The risk is a file that looks right and will not parse**, so every module
   and every named graph is parsed back in the test suite, and the writer's
   reported triple count is asserted equal to what rdflib finds.
4. One trap paid for immediately: Turtle's `PN_LOCAL` does not admit `/`, so
   `tmkr:TMM/Part29/1` is not valid Turtle. Everything derived from a ref is
   written as a full IRI in angle brackets and `PN` refuses an unsafe local
   name (QUIRKS Q-32).

---

## ADR-0059 — The ontology is generated from Python, and there is no Protégé round trip

**Date** 2026-09-03 · **Authority** agent-proposed · **Status** provisional

**Context.** `ARCHITECTURE.md` §5 names Protégé for ontology editing, which
implies hand-authored Turtle. But `IDENTIFIERS.md` says the base IRI lives in
one constant and that changing it must be a config change and a rebuild, "not a
find-and-replace across serialised RDF" (HANDOFF Q7, still unconfirmed) — and a
hand-authored `.ttl` bakes the base into its `@prefix` line.

**Decision.** The ontology design lives in `src/tm_knowledge/graph/ontology.py`
and `ontology/*.ttl` is generated from it.

**Consequences.**

1. Q7 stays a one-line change. Set `TMK_BASE_IRI`, rebuild, done.
2. Each class and property carries its reasoning next to it, which a `.ttl`
   comment would not have held as well.
3. **The cost is real: opening the ontology in Protégé now means editing a
   generated file, and edits do not come back.** For a pilot of 21 classes and
   32 properties that is acceptable. It stops being acceptable the moment a
   domain expert wants to edit the ontology directly, and the fix then is a
   reader that parses `ontology/*.ttl` back into the module — not to start
   hand-editing and lose the guarantee quietly. Flagged as Q24.

---

## ADR-0060 — Endpoint constraints go in SHACL, never in `rdfs:domain`

**Date** 2026-09-03 · **Authority** derived · **Status** accepted

**Context.** The fourteen approved predicates stand between concepts,
provisions, cases and Manual passages. The obvious thing is to declare
`rdfs:domain` and `rdfs:range` on each.

**Decision.** No relation property declares either. The endpoints are
constrained in `shapes/s43-shapes.ttl` instead, and a test asserts that no
domain or range appears in the relations module.

**Why this is `derived` and not a preference.** `rdfs:domain` is an inference
rule, not a check. Declaring `tmk:requiresElement rdfs:domain tmk:LegalConcept`
does not verify that subjects are legal concepts — it asserts that everything
appearing there **is** one. Over this graph, whose subjects include
`TMA1995/s43` and `CASE/2000/FCA/720`, that would silently manufacture the claim
that a section of the Act is a legal concept: content no reviewer approved,
produced by an ontology axiom, indistinguishable in the output from content they
did. That is CLAUDE.md rule 1 broken by a modelling convenience.

**Consequences.** A violation is reported and names the node, rather than being
believed or turning the whole graph inconsistent. pySHACL is **not** a
dependency — running the shapes as a gate is a decision to raise, and the shapes
are written and waiting.

---

## ADR-0061 — The pilot proceeds without further expert review, and the owner is the reviewer of record

**Date** 2026-09-03 · **Authority** human · **Status** accepted

**Context.** The first review round returned 190 approved records and left ten
decisions holding another 30 (ADR-0054). The owner has decided not to go back to
the Trade Mark expert for now, and to develop a working draft over one section
themselves in order to demonstrate the value of a full ontology.

**Decision**, the owner's: the programme continues on the content that exists.
Anything approved from here is approved by the owner, who is not a specialist and
has said so.

**Consequences, and they matter more than the decision.**

1. **`approved_by` already carries this.** The gold set records *who* signed each
   record, so records signed `TC` and records signed by the owner are
   distinguishable for ever, without a new field. Nothing is lost and nothing
   needs migrating. An expert can re-review later and the diff will be visible.
2. **The unreviewed 149 stay unreviewed.** Not going back to the expert is not
   the same as approving what they did not reach, and nothing may be promoted
   because the queue is now inconvenient.
3. **The demonstration must state its own provenance.** A graph built from
   190 records signed by one Trade Mark expert is a different artefact from one
   signed by a non-specialist, and any report that goes further than this repo
   must say which it is.
4. This does **not** relax rule 1 for agents. Content is still expert-owned;
   what has changed is who the approving human is, not that there is one.

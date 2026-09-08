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

## ADR-0056 — Ontology drafting proceeds from approved Stage 0 content, ahead of Stage 2

**Date** 2026-09-03 · **Authority** human · **Status** accepted

**Context.** The owner's instruction, in their words: *"I'm not going to go back
to the TM expert for now. We're just going to have to work with what we have…
Our goal is to demonstrate the value and feasibility of a full ontology."*

The programme's shape said the repo was blocked. `PARALLEL-TRACK-ROADMAP.md` §7
records the container as finished and empty, waiting on Stage 0 content; ADR-0010
forbids Stage 2 before Stage 0 is complete; and Stage 0 is not complete — 12 gaps,
four record types below their bands, no scope document, no measures.

What that reading missed is that **Stage 0 is no longer empty.** 190 records are
approved and signed: 52 concepts with labels, not-labels and a hierarchy; 35
relationships with verbatim supporting sentences, tiers and modalities; 20
competency questions; 11 prohibited uses; 6 reasoning expectations. `tmk-harness`
reports 0 defects against them. That is enough content to build an ontology from.

**Decision.** Build the section 43 ontology draft and the graph under it, now,
from the approved records. Stage 2 stays shut.

The distinction that makes this consistent rather than a carve-out: **ADR-0010
forbids extraction, not modelling.** Stage 2 generates *new* candidate knowledge
from the corpus — keyphrases, entities, relations a model proposed — and doing
that before the gold set exists means the first plausible output becomes the
standard by arriving first. Nothing in this work generates a candidate. It is a
structural transformation of records a person already signed, and running it
early cannot anchor a measurement because it measures nothing new.

`ontology/README.md`'s own rule already contemplated this: *"Draft modules may be
generated by script from approved vocabulary and relationship registers."*

**Consequences.**

1. `rdflib` and `pyshacl` enter as an optional `[rdf]` extra, following ADR-0035's
   pattern so the core install stays at three dependencies. Both are the
   roadmap's own choices (`ARCHITECTURE.md` §5), so this is the reference stack
   rather than a substitution and needs no separate technology decision.
2. **The Stage 2 prohibition is untouched.** No TextRank, YAKE, KeyBERT, spaCy or
   clustering run, not to see the output. `graph/candidates.nq` does not exist,
   because there are no candidates.
3. The gaps do not close. Building over 52 concepts does not make them 100, and
   the ontology report counts what is short rather than reporting a pilot as
   finished. Stage 0's completeness gate is unchanged and still red.
4. The largest gap the work exposed is one nobody had stated: **the concept
   records carry no type**, so `GroundOfRefusal`, `LegalTest`, `RelevantFactor`
   and `Exception` are declared and empty and all 52 concepts are bare
   `tmk:LegalConcept`. That is a legal judgement and remains expert-owned.

---

## ADR-0057 — The ontology draft lives in `ontology/draft/` and is promoted one module at a time

**Date** 2026-09-03 · **Authority** human · **Status** accepted

**Context.** `ontology/` holds approved content (ADR-0007, CLAUDE.md rule 4) and
`ontology/README.md` requires approval by an ontology specialist *and* a domain
expert. The draft has neither. Writing it into `ontology/` would need an ADR
overturning that rule; the owner chose the alternative when asked.

**Decision.** Draft modules live in `ontology/draft/`. A module moves up to
`ontology/` only when a person signs it, individually — not the directory as a
block. Every file carries `owl:versionInfo "draft — not approved"` so the marker
survives being copied out of the repository.

**Consequences.**

1. The path is the marker. Nothing is inferred from a file's location beyond
   what the location says, and a reader who has only the file still sees the
   version info.
2. `graph/` is built against a draft TBox and says so in `graph/README.md`. The
   *content* in `graph/approved.ttl` is genuinely approved — it comes from
   `eval/gold/` — while the schema it is expressed in is not, and those are two
   different claims that must not be collapsed.
3. Promotion is a future decision with its own ADR. It will need to say what
   "an ontology specialist approved this" is recorded as, which is ADR-0039's
   question over again for a different artefact.

---

## ADR-0058 — Every approved relationship is emitted twice: as a triple and as an assertion

**Date** 2026-09-03 · **Authority** derived · **Status** accepted

**Context.** `graph/README.md` requires every assertion to carry its source
passage, version, hash, method, confidence, review status, reviewer and date.
A plain RDF triple carries none of that. The usual answers are RDF-star, which
is outside OWL 2 RL and unevenly supported, or reification, which makes every
query traverse three extra hops.

**Decision.** Both forms, always, in the same named graph:

- the direct triple `tmkr:TMA1995/s43 tmk:requiresElement tmkc:GC-0002`, which is
  what SPARQL and OWL RL work on;
- `tmka:GR-0003 a tmk:ApprovedAssertion` carrying subject, predicate, object and
  the whole provenance block, which is what an audit works on.

`tmk:UnreifiedRelationShape` fails the graph if a direct triple uses an approved
predicate with no assertion behind it.

**Why the shape is the load-bearing part.** Without it the pair is a convention,
and a convention that is cheap to break is broken eventually. The failure it
prevents is specific: an edge nobody signed, sitting in the approved graph,
indistinguishable from one that was.

**Consequences.**

1. The approved graph is roughly twice the size it would otherwise be. Cheap:
   2,942 triples.
2. A query that only wants the fact writes the natural triple pattern; a query
   that wants the evidence joins through the assertion. Neither pays for the
   other.
3. Entity mentions are assertions with no direct triple, because a mention is
   not a relation between two things. The shape allows that — it constrains
   triples that exist, not assertions that must produce one.

---

## ADR-0059 — A SKOS concept's IRI uses its gold-set id, not a newly minted one

**Date** 2026-09-03 · **Authority** derived · **Status** accepted

**Context.** `IDENTIFIERS.md` §3 illustrates a concept IRI as `tmkc:c-0042`,
allocated sequentially from a register file. The concepts already have
identifiers — `GC-0001` … `GC-0052` — allocated once in
`eval/gold/concepts.yaml` under exactly the rule §3 states: allocate by
appending, never reuse, never derive from the label.

**Decision.** `GC-0001` becomes `tmkc:GC-0001`. No second identifier is minted.
`eval/gold/concepts.yaml` **is** the register file §3 describes; `c-0042` is
illustrative form, not a required prefix.

**Consequences.**

1. One answer to "which concept is this", not two. A second id would need a
   mapping table, and a mapping table between two ids for the same thing is a
   thing that goes stale.
2. The gold record id is legible in every query result, so an answer names the
   record a reviewer signed without a lookup.
3. The same rule extends to the other human-facing ids: `tmka:GR-0003`,
   `tmkp:PU-0004`, `tmkp:CQ-0017`. Content-addressed ids stay as `IDENTIFIERS.md`
   §3 specifies and are unaffected — nothing here has produced a candidate.

---

## ADR-0060 — `graph/approved.ttl` and `graph/inferred.ttl` are committed; `source.ttl` and `dataset.nq` are not

**Date** 2026-09-03 · **Authority** agent-proposed · **Status** provisional

**Context.** ADR-0042 committed `data/derived/`, generated reports included, as a
paper trail — `worksheet.md` carries 40,000 words of Manual text and is in git.
ADR-0004 keeps `data/upstream/` out of git, so that another repo's corpus is not
vendored into this one's history. The graph sits across that line: `source.ttl`
is 1.3MB and `dataset.nq` 5.2MB, and both are restatements of the pinned corpus.

**Decision.** Commit `approved.ttl` (164KB) and `inferred.ttl` (127KB). Ignore
`source.ttl` and `dataset.nq`.

The line is what a file *restates*. `approved.ttl` is this repo's own work — a
reviewer's decisions, in RDF — and a diff of it is a diff of what a reviewer
changed, which is the paper trail ADR-0042 is about. `source.ttl` restates the
snapshot, and 6.5MB of the corpus in this history is `data/upstream/` by another
route. Both rebuild in one command.

**Why `worksheet.md` is not the counter-example.** It was produced to be handed
to a person and marked up; it had to exist as a file. `source.ttl` is
regenerated by `tmk-graph` and read by nothing but a query engine.

**The judgement being flagged.** Where the line falls is the agent's, and it is
arguable in the other direction: committing everything would make the graph
reviewable without a snapshot fetch, at 6.5MB per rebuild in the history.
Flagged in `HANDOFF.md` §3 as Q23.

**Consequences.**

1. CI must fetch the snapshot before the ontology job can do anything, and the
   job **fails rather than passes** when the fetch fails — a green tick that
   meant "the checks did not run" is the outcome the canary job exists to
   prevent elsewhere.
2. A reviewer reading `approved.ttl` in the browser sees this repo's decisions
   without the corpus around them, which is the more legible artefact anyway.

---

## ADR-0061 — A competency query declares what it does not answer, and is refused without it

**Date** 2026-09-03 · **Authority** agent-proposed · **Status** provisional

**Context.** `queries/README.md` requires one query per competency question. It
does not say what a query file must contain, and the failure mode is specific
and quiet: **a query that returns rows always looks like an answer.** CQ-0017
returns a Part distribution, and the natural reading is "these are the Parts an
amendment would affect" when what it measured is "these are the Parts that cite
the provision" — a different claim, and weaker where the citations are upstream's
inference from a bare "section 43" rather than a link the Manual's authors wrote.

**Decision.** Every `.rq` in `queries/competency/` carries a three-line header —
`question`, `answers`, `limits` — and `tm_knowledge.ontology.ask` raises rather
than running a file missing any of them. A test fails a limits line under 60
characters. `tmk-ask` prints the limits under every result table, so the caveat
travels with the answer instead of living in a document nobody opens.

Rule files carry the same discipline plus two more fields: `fires-test` and
`near-miss-test`, and a test asserts both names resolve to real tests.

**The judgement being flagged.** The length threshold is arbitrary and the
requirement itself is the agent's reading of what `queries/README.md` implies
rather than what it says. Flagged in `HANDOFF.md` §3 as Q24.

**Consequences.**

1. Writing a query costs more, and the extra cost is writing down what it does
   not establish — which is the part that is hard and the part that is worth
   having.
2. Three limits lines are load-bearing today and would each have been a wrong
   answer without them: CQ-0017 measures reviewing effort and not outcome,
   CQ-0019 finds recorded dependencies and not subject matter, and CQ-0023's
   most important row is a blank one.
3. A query nobody can write a limits line for is a query that has not been
   understood, and refusing it is the right outcome rather than an obstacle.

---

## ADR-0062 — There is a public dashboard, and it has exactly two jobs

**Date** 2026-09-04 · **Authority** human · **Status** accepted

**Context.** Everything this repo produces is a file: YAML records, Turtle, a
SHACL report, four generated Markdown reports and 61 ADRs. That is right for the
work and wrong for the reader. Two audiences cannot use it. Trade marks experts
cannot see what the ontology says or why a decision was made without reading
Turtle. And the owner, who is the only person who can settle a growing list of
questions, has had those questions delivered as a table inside a 400-line handoff
document written for the next agent.

**Decision.** The owner's instruction, in their words: a dashboard at
`https://thomas-amann-ipaustralia.github.io/TM-Knowledge/`, *"beautiful, clean
and fun"*, with two core functions —

1. **Explain the shape of the ontology, the graph and the related data**, simply
   and elegantly, easy to amend as the ontology changes, with tooltips and
   explanatory features for readers who are trade marks experts and not systems
   engineers.
2. **Let the owner respond to outstanding issues** through a templated form with
   radio buttons, dropdowns and free text, whose answers are saved where the next
   session can read them. The items must be written in straightforward language:
   *"I'm becoming more knowledgeable, but I'm far from being a system engineer."*

They also set the constraint that shapes ADR-0065: the form will be updated after
almost every session, so the part that changes must stay lightweight — their own
suggestion was static scripts reading a dynamic JSON or YAML file.

**Consequences.**

1. The dashboard is a deliverable of this repo, not a side artefact. It has a
   directory, a README, generated data, tests and CI like anything else.
2. Its audience is not an agent. Language that is precise for a session — "the
   TBox is drafted, not promoted" — is a failure on the page.
3. It is published, so a wrong number on it is worse than a missing page. Every
   figure is generated (ADR-0063) and CI fails when the published data no longer
   matches the repository.
4. Publishing needs one repository setting the agent cannot make: **Settings →
   Pages → Build and deployment → Source: GitHub Actions**. Without it the
   workflow runs green and publishes nothing.

## ADR-0063 — The dashboard is generated from committed artefacts only, and never from the snapshot

**Date** 2026-09-04 · **Authority** agent-proposed · **Status** provisional

**Context.** The site needs numbers. Some of them — 52 concepts, 2,942 approved
triples, 49 classes, 61 decisions — come from files this repo commits. Others —
216 in-scope chunks, 529 citations, 16,405 source triples — exist only in
`graph/source.ttl`, which is deliberately not committed (ADR-0060) and is rebuilt
from the pinned upstream snapshot.

Three options. Fetch the snapshot during the page build and report everything;
hard-code the figures the snapshot would give; or report only what the committed
artefacts support and say so.

**Decision.** `tm_knowledge.dashboard` reads **committed artefacts only**:
`eval/gold/`, `ontology/draft/`, `graph/approved.ttl`, `graph/inferred.ttl`,
`shapes/`, `queries/`, `data/pin.json`, and the three documents in `docs/` that
the site restates. It never fetches or reads the snapshot.

Figures that only the source graph holds are **not restated on the site at all**.
Instead the site renders `data/derived/reports/` — produced by the runs that do
have the snapshot — in full, in place, unsummarised.

`tmk-dashboard --check` regenerates in memory and fails if what is committed
under `site/data/` differs, ignoring only the build stamp. CI runs it.

**The judgement being flagged.** Refusing the snapshot costs the site its most
striking single figure — the five Manual Parts carried into the section 43 impact
set entirely by inferred citations. It is recoverable in prose, and the report
that computes it is one click away. Flagged in `HANDOFF.md` §3 as Q25.

**Consequences.**

1. A deploy cannot fail because upstream was unreachable, and cannot take four
   seconds plus a clone on every push.
2. The site cannot show a figure it did not measure. Where a count is over a
   subset — classes populated in the *approved* graph, not the source graph — the
   page says which subset, because "39 classes hold nothing" and "30 classes hold
   nothing" are both true over different scopes and neither is wrong.
3. The drift check is a real cost: a session that moves a record and does not run
   `tmk-dashboard --write` fails CI. That is the intended trade — the alternative
   is a public page quoting a number the repository no longer holds.
4. `site/data/reports/` is git-ignored: those four files are byte copies of files
   already committed under `data/derived/reports/`, and committing them would put
   the same text in the history twice.

## ADR-0064 — A page is a list of blocks; the JavaScript knows nothing about trade marks

**Date** 2026-09-04 · **Authority** agent-proposed · **Status** provisional

**Context.** The owner asked for a site that is easy to amend, *"because the
ontology is in its infancy and will certainly undergo changes."* The failure mode
to design against is the ordinary one: a change to what the ontology holds
becoming a change to markup, so that the site drifts behind the data because
updating it is a chore.

**Decision.** Every page is `{id, title, lede, blocks: [...]}`, and every block is
one of eight kinds — `stats`, `prose`, `callout`, `table`, `cards`, `bars`,
`list`, `report`. `site/blocks.js` has one renderer per kind and contains no
domain vocabulary. All content is composed in
`src/tm_knowledge/dashboard/build.py`.

Tooltips come from `docs/GLOSSARY.md`, parsed at build time: prose carries
`{{term}}` markers, and **a marker naming a term the glossary does not define
fails the build**.

The site is hand-written HTML, CSS and ES modules — no framework, no package
manager, no build step, and nothing loaded from a CDN. A test asserts the last of
those.

**The judgement being flagged.** Eight block kinds is a guess at what the site
will need. A ninth is cheap; the risk is the opposite — a page that wants a real
visualisation and gets a table because the vocabulary made a table easy. Flagged
in `HANDOFF.md` §3 as Q25.

**Consequences.**

1. Changing what a page says is a change to one Python function. Adding a page is
   a builder plus a line in `PAGES`. Neither touches JavaScript.
2. One glossary, two readers: the term a session reads on arriving cold is the
   term an expert sees in a tooltip, so an explanation cannot drift into two.
   Adding a term to the site means adding it to `docs/GLOSSARY.md`.
3. No supply chain. Everything served is in this repository, which matters for
   something published under a government domain.
4. A silently-missing tooltip is impossible: the marker is either defined or the
   build fails.

## ADR-0065 — Questions for the owner live in one validated, plain-language file

**Date** 2026-09-04 · **Authority** agent-proposed · **Status** provisional

**Context.** `HANDOFF.md` §3 holds 24 open questions in a table, written for the
next agent, in the repo's own vocabulary — "does the owner confirm ADR-0055's
third guard?" The owner cannot act on that, and it is not their failing: nothing
in the sentence says what would change if they answered it. The owner asked for
the form to stay lightweight to update, since it changes after nearly every
session.

**Decision.** `review/questions/open-questions.yaml`, validated against
`review/questions/schema.json`. Each entry carries `plain` (what is going on),
`why_you` (why nobody else can settle it), `if_unanswered` (what stays stuck),
and an answer control — single choice, multiple choice, short text or long text —
plus optional background links and a notes prompt. The schema enforces what a
machine can: a question put to the owner must carry a control; `plain` cannot be
one line; a parked question must not carry one.

`status` and `needs` decide what reaches the form. `needs: expert` and
`needs: organisation` are shown as context and never acquire a radio button,
because a control under something the owner cannot decide invites an answer that
then has to be unpicked.

**The judgement being flagged.** The initial 17 entries are an agent's reading of
which of the 24 handoff questions are the owner's to settle and how to phrase
them. The phrasing carries an option list, and an option list can steer.
Flagged in `HANDOFF.md` §3 as Q25.

**Consequences.**

1. Updating what is asked is editing one YAML file — the lightweight path the
   owner asked for. `HANDOFF.md` §3 stays the agent-facing record; this is the
   owner-facing one, and the two cross-reference by `tracked_as`.
2. Every realistic answer must be on the list, including *leave it alone*, *I
   have no view* and *show me an example first*. An option list that only allows
   agreement is an agent deciding.
3. Legal content may be *asked about* and never answered here. "Is 'connotation'
   a legal test or a relevant factor?" is a question; an option asserting the
   answer would be rule 1 violated through a form control.
4. A question is not deleted when answered — it is marked `answered`, so the
   ruling and the question it settles stay readable side by side.

## ADR-0066 — An answer returns as a GitHub issue and is transcribed; the issue is the artefact

**Date** 2026-09-04 · **Authority** agent-proposed · **Status** provisional

**Context.** The dashboard is a static page on GitHub Pages. It cannot write to
the repository, and any design where it could would need a credential sitting in
a browser. The owner suggested a button that fires a GitHub Action, and left the
mechanism open. Three candidates: a prefilled "new file" URL committing straight
through GitHub's web editor; a token pasted into the page; or a prefilled issue
with a workflow behind it.

**Decision.** The form composes a GitHub issue: a human-readable summary, and the
machine-readable answers in a fenced block behind a `<!-- tmk-ruling:v1 -->`
marker. The owner presses submit. `.github/workflows/ruling.yml` transcribes it
with `tmk-ruling` into `review/rulings/<date>-issue-<n>.yaml`, commits it, links
the file back on the issue and closes it.

The **issue is the artefact** and is never edited by this repo; the YAML file is
a transcription that names its issue — the same split ADR-0050 draws between
`review/returned/` and `review/decisions/`, and the reason a generated file is
allowed in `review/rulings/` and forbidden in `review/returned/`.

Two refusals are load-bearing. A submission from an account **without write
access** is left as an issue with a comment and nothing is written: a ruling
becomes repository content, so it must come from someone who could have committed
it anyway. And a submission naming a question or an option that does not exist is
**reported and refused**, never matched to the nearest one — that would be an
agent deciding what a person meant (rule 6).

**The judgement being flagged.** Also flagged as Q25. A prefilled issue URL has a
practical length limit; past it the form switches to copy-and-paste rather than
silently truncating. And `author_association` is GitHub's own answer to "may this
person write here", which is the right question but not a fine-grained one.

**Consequences.**

1. No token in the browser, and no write credential anywhere near the page. The
   owner's own account, their own words, GitHub's timestamp.
2. An edited submission **replaces** its earlier transcription rather than
   sitting beside it: two files for one issue would be two versions of one
   decision with nothing saying which the owner meant.
3. `applied: null` and `status: answered` are two states on purpose. Decided-but-
   not-yet-acted-on is a real and common condition; collapsing them hides it.
4. A session's first act is now to read `review/rulings/`. A ruling is a `human`
   decision and outranks any `agent-proposed` ADR it touches; acting on one means
   a new ADR with authority `human` quoting the answer.

---

## ADR-0067 — The route an answer takes back into the repo is repaired, and a crash no longer reads as the owner's mistake

**Date** 2026-09-08 · **Authority** derived · **Status** accepted

**Context.** The owner submitted issue #12 on 2026-09-08 — seven answers, the
first use of the loop S011 built. Nothing was recorded. The workflow commented
that it could not record the submission and that *"the usual cause is that the
answer block was edited by hand"*, which was untrue and unactionable.

Three separate faults, each sufficient on its own to lose a submission.

1. **`tmk-ruling` could not start.** `dashboard/cli.py` imported the graph
   builder at module scope, so the transcription command pulled in rdflib — the
   optional `[rdf]` extra — while `.github/workflows/ruling.yml` installs the
   core three dependencies and nothing else. `ModuleNotFoundError: No module
   named 'rdflib'`, before a line of transcription ran (Q-42).
2. **An answer with a note but no chosen option was dropped in silence.** The
   form writes such an answer into the machine-readable block and counts it in
   the issue title; both the form's prose summary and `transcribe()` skipped it.
   On issue #12 that answer was OQ-0009 — a new data source the owner wants
   consumed — and the title says seven while the summary lists six (Q-43).
3. **The failure message blamed the owner.** Re-submitting would have failed
   identically.

**Decision.** The `build` import moves into `dashboard()`, the only function
that uses it, so the transcription path needs the core install and nothing more;
a test blocks the extras and imports the CLI, because the coupling is invisible
on any machine that has them. An answer carrying a note but no option is kept,
labelled *no option chosen — the answer is in the note*, on both sides; an
answer with neither is still dropped, because that is a scrolled-past question
rather than a decision. And the workflow distinguishes a refusal — which
`tmk-ruling` marks with `refused:` on stderr, and which re-submitting does fix —
from a crash, which it names as this repository's fault and links to the run.

`tmk-ruling --received` is added so an issue transcribed after the fact carries
GitHub's timestamp for the submission rather than the clock of whichever
container got round to it.

**Consequences.**

1. Issue #12 is transcribed at `review/rulings/2026-09-08-issue-12.yaml`, seven
   answers, stamped with the issue's own submission time.
2. The lesson generalises past this bug: **the paths a non-engineer depends on
   are the ones with no second chance.** The owner cannot debug a workflow, and
   an unhelpful failure message on the one route into the repository is worse
   than a crash on a developer command.
3. Not done: adding `[rdf]` to the workflow's install. That would have fixed the
   symptom and hidden the coupling.

---

## ADR-0068 — A rule's approval lives in its header, and nowhere else

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** The owner approved RULE-0002 on OQ-0004: *"Approve it — its links
may be relied on"* (issue #12, `review/rulings/2026-09-08-issue-12.yaml`). It was
the first rule anyone had approved.

Acting on it exposed a design fault. Each rule's CONSTRUCT body wrote
`tmk:reviewStatus "candidate"` and `tmk:requiresHumanReview true` into its own
output, while the `approved-by:` header carried the approval record. Two sources
of truth for the same fact, and they can drift in either direction — the
dangerous one being a body still emitting `candidate` after a person approved the
rule, so an approval the owner gave changes nothing in the data and nobody
notices.

**Decision.** RULE-0002 is approved, recorded in its `approved-by:` header with
the owner's name, the date and the ruling file. The header is the **only** thing
that decides an output's review status: `Rule.construct()` stamps it on every
inference, and refuses a body that sets either predicate itself. A rule does not
get to declare its own approval.

The owner's approval is recorded exactly as a trade marks expert's would be,
which is his own ruling on OQ-0010 applied here.

**What this settles and what it does not.** It settles that RULE-0002's 187
impact links may be relied on. It does not make them expert-reviewed trade marks
content, and it does not touch the rule's `limits:` line — impact by *recorded
dependency* and nothing else, so a nil result still never means "nothing is
affected" (Q-28).

**A correction the owner should see.** He approved it believing it drew 2,244
links. It draws 187. See ADR-0069; the difference does not bear on whether the
derivation is sound, which is what he was asked, but he was given a wrong number
and can revisit on the right one.

**Consequences.**

1. RULE-0002's output leaves quarantine; RULE-0001's does not.
2. `is_approved` stops being decorative. It gated nothing before this — the
   dashboard displayed it and no code branched on it.
3. Approval does not promote an inference into the approved graph. Both rules'
   output stays in `graph/inferred.ttl`: approval says an inference may be
   relied on, not that it became a signed record.

---

## ADR-0069 — Conclusions and triples are counted separately, and the report says which to read

**Date** 2026-09-08 · **Authority** derived · **Status** accepted

**Context.** OQ-0003 told the owner RULE-0001 *"produced 71 flags"* and asked him
to review 71 flagged passages. It flags **five**. OQ-0004 told him RULE-0002
produced *"2,244 of them"*. It draws **187**.

Both figures are triple counts. `data/derived/reports/ontology.md` reports them
in a column correctly headed *triples produced*; S011 read them off that table
and wrote them into the owner's questions as counts of findings. Every
conclusion carries eight to fourteen triples of provenance with it, so the two
numbers differ by more than an order of magnitude and neither looks obviously
wrong beside the other (Q-44).

**Decision.** `apply_rules` returns a `Yield` carrying `assertions` and `triples`
under names that cannot be swapped. The report prints both columns and says in
words which to read. A test over `review/questions/open-questions.yaml` fails if
a rule's triple count ever again sits next to a word like *flags*, *links* or
*passages*.

**Why this is worth an ADR rather than a fix.** The number was not wrong by
accident of arithmetic; it was wrong because a number crossed from a context
where it was correctly labelled into one where nothing labelled it. **Any figure
put in front of the owner is a figure he will act on**, and the correction
changed what he was being asked: a rule firing on 5 passages in 216 is selective,
one firing on 71 in 216 is barely narrowing anything.

**Consequences.**

1. OQ-0003 is re-asked as OQ-0019, against `data/derived/reports/rule-0001-flags.md`
   and the corrected count.
2. OQ-0004's approval stands on the same reasoning it always did, and the owner
   is told the real number (ADR-0068).
3. The general rule: a generated report may print any number it likes, as long
   as the column says what it is. A hand-written document quoting that number
   must carry the label with it.

---

## ADR-0070 — The whole graph is committed, and `dataset.nq` is written sorted

**Date** 2026-09-08 · **Authority** human · **Status** accepted · **Supersedes** ADR-0060

**Context.** The owner ruled on OQ-0005: *"Store everything, so the graph can be
read without building it."* ADR-0060 had committed `approved.ttl` and
`inferred.ttl` and kept `source.ttl` and `dataset.nq` out, on the ground that
they restate the pinned corpus.

**Decision.** All four are committed, about 6.5MB. `data/upstream/` stays out
under ADR-0004 and that is not in tension: the snapshot is another repository's
corpus, and this is a derivation of it — the line `data/derived/` already draws.

Two things had to be true first, and only one of them was.

**A committed generated file can go stale, and a stale one is worse than an
absent one** because it reads as current. So `tmk-graph --rules --check` rebuilds
into a temporary directory and compares bytes; CI runs it, and so does
`test_the_committed_graph_matches_a_rebuild`.

**`dataset.nq` was not reproducible.** rdflib's Turtle serialiser sorts; its
N-Quads serialiser emits in set-iteration order, which moves with
`PYTHONHASHSEED`. Two builds of an identical dataset produced two different 5MB
files. Uncommitted nobody noticed; committed, it would have put a 5MB diff in the
history on **every rebuild**, signifying nothing — a far larger cost than the one
the owner weighed. Line order carries no meaning in N-Quads, so the file is
written sorted, which canonicalises without changing what it says (Q-45).

**Consequences.**

1. `graph/` can be read, diffed and reviewed without a snapshot fetch, which is
   what the owner asked for.
2. A rebuild that changes nothing produces no diff, so a diff under `graph/`
   means something moved.
3. ADR-0060 is superseded, not reversed on its reasoning: its cost estimate was
   right and the owner chose to pay it.

---

## ADR-0071 — A concept's type is a record of its own, not a field on the concept

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** The owner ruled on OQ-0001: *"Use those four groups — come back to
me with the list of 52 to sort."* `GroundOfRefusal`, `LegalTest`,
`RelevantFactor` and `Exception` had been declared and empty since S010, because
the gold concept record has no type field and typing a concept is a legal
judgement (ADR-0056 consequence 4).

The obvious move — add `type` to `gold-concept.schema.json` — is wrong. The 52
concept records are signed by a named reviewer on a date, and that signature
covers the record as it stood. Adding a field and filling it later would put
unsigned content inside somebody's signature, and would make the concept and its
typing inseparable when they are two judgements, possibly by two people.

**Decision.** A ninth Stage 0 record type: `concept_type`, id prefix `GT`, file
`eval/gold/concept-types.yaml`, one record per concept, each carrying its own
`approved_by` and `approved_date`. `basis` is optional and `notes` is where the
reasoning goes.

`none_of_these` is one of the five values and is a real answer, not a refusal to
answer: it says the four groups do not fit this concept, which is evidence about
the taxonomy. It asserts no class. A blank stays blank and is reported as
still-to-do.

**How the pass reaches the owner and comes back.** `tmk-typing --write` renders
`data/derived/concept-typing.xlsx` — an ordinary intake workbook with the
`concept-types` sheet pre-filled, `type` empty, the five groups as a dropdown —
and `data/derived/reports/concept-typing.md`, the evidence to sort by. Because
the pass is intake-shaped, **`tmk-transcribe` reads it back with no new code**,
so the single door into `eval/gold/` stays single (ADR-0048).

`workbook.fill()` has existed since P7 and was deliberately not a command:
*"generating an empty workbook and pre-filling one with content are different
decisions, and only the first has been made."* The owner has now made the second,
and only for this file — `stage0-intake.xlsx` stays empty (ADR-0044).

**Consequences.**

1. The four classes fill from signed records and from nothing else. Each typed
   concept carries `tmk:typedBy` back to the record that typed it, so a typing
   can be traced to a person and a date rather than appearing to have always
   been so.
2. Every build prints how many of the 52 are sorted, so the largest gap in the
   draft is a number that moves rather than a paragraph someone remembers.
3. The harness gains a deliverable row, so an unsorted vocabulary is a reported
   gap rather than a silence.
4. Nothing was typed. If a later session finds `concept-types.yaml` populated by
   anything other than a transcribed workbook, that is a defect.

---

## ADR-0072 — The section 43 boundary is one hop, landing on the chunk and not its parent

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** OQ-0014 — where section 43 stops — had been open since S002 and
parked for an expert. The owner answered it himself on issue #12, in prose
outside the form's answer block; his words are at
`review/returned/260908-owner-notes-issue-12.md`.

**Decision.** Three structural parts, implemented in `tm_knowledge.stage0.boundary`
and reported by `tmk-boundary`:

1. **One hop.** What the section 43 material cites is in scope; what *that* cites
   is not. The boundary is the citation graph at radius one.
2. **The hop lands on what was named, not on its parent.** A citation of
   `TMA1995/s41(2)` puts that unit in scope and leaves section 41 out.
3. **Case law inherits the same rule.** A decision cited from section 43 material
   is in scope; what the decision discusses is not — which costs nothing today,
   because no decision text exists anywhere in the programme (Q-11), and the
   report says so rather than implying a closure it never computed.

**A fourth part is recorded and deliberately not implemented.** He added that the
s 43 / s 41 relationship is "more diffuse", and that s 43 should refer to s 41
only in that resolving an s 43 ground has no impact on the s 41 ground. That is a
statement about how two grounds of refusal interact — trade marks law, not a
selection rule — and this repo does not author those (rule 1). It belongs in a
relationship record an expert signs.

**What running it revealed, and it is the reason this ADR matters.** Part 2 keeps
12 parent provisions out. But **section 41 is not one of them**: the section 43
material cites `TMA1995/s41` *bare* in 32 passages as well as citing `s41(3)` and
`s41(4)`, and a bare citation names the parent, so section 41 comes in whole and
part 2 never engages. Twenty-two provisions behave this way. The rule meets a
corpus that cites more loosely than the rule assumes. That is put back to the
owner as OQ-0021 rather than resolved here, because choosing between "accept it",
"treat a bare citation as reaching only the units actually discussed" and "make
section 41 a special case" is a scope judgement.

**Consequences.**

1. `tmk-boundary` reports the boundary as a committed artefact: 216 passages at
   the centre, 152 provisions and units, 58 decisions and 34 further Manual
   passages one hop out; 460 refs in scope.
2. **This does not write `eval/pilot-scope.md`.** That deliverable also asks
   whether geographical indications are the centre of the topic or a corner of
   it, and whether point-in-time questions are in scope. The owner did not answer
   those, the harness still reports the document missing, and answering some of
   a question is not answering it.
3. ADR-0022's worksheet scope rule is unchanged. This is a layer over it, not a
   replacement: the centre is still what ADR-0022 selects.

---

## ADR-0073 — A glossary does not capture the examiner/registrar relation; a role becomes something a statement can be about

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** OQ-0015 carried a conditional the owner put directly: *"If you do
not believe that the glossary captures the conceptual relationship between an
examiner and a registrar, please make a note of this and adopt the Must/May
predicate."*

The content in question is the expert's note (Q16/OQ-0015): it is not enough for
the individual examiner to doubt a connotation exists — the Registrar as a whole
must — and an examiner is expected to consult their team leader and the s 43
specialists before accepting on that basis.

**The note, as instructed: a glossary does not capture it.** A glossary holds one
entry per term. That content is a *normative relation between two roles*, with a
required step attached. An entry for "Examiner" and an entry for "Registrar"
cannot between them hold "an examiner must consult a team leader before
accepting on doubt"; the statement's subject is a role, its object is another
role or an act, and it carries a deontic force. No arrangement of definitions
holds a relation.

**Decision.** Adopt the Must/May predicate — and the finding on inspection is
that **it already exists**. `tmk:modality` carries `must` | `may` | `should` on
any approved relationship, has since S010, and is never inferred from grammar
because whether a "may" is possibility or permission is a legal reading. What was
missing was not the modality but the *subject*: only concepts and upstream refs
were terms, so no relationship could be about a role at all.

So `_term` now resolves a `GE-` entity mention as a term. Roles are already
recorded as entity mentions typed `Role`, and `tmk:Examiner`, `tmk:Delegate` and
`tmk:DecisionMaker` are already declared classes. An expert can now sign a
relationship whose subject is a role, whose object is a role or an act, and whose
`modality` is `must` or `may`.

**Nothing was written.** No MUST or MAY statement about examiner conduct exists
in this repository, and none may be authored here. The expert's note stays where
it is, in `review/returned/260826-expert-feedback.md`. What changed is that there
is now a shape for it.

**Consequences.**

1. The conditional is answered in the branch the owner named, not the easier one.
2. A glossary may still be useful, and the owner permitted one — but as
   disambiguation, not as the home for this content.
3. Whether examiner-conduct statements should in fact be relationship records
   with role subjects is put to the expert and owner as OQ-0022; the shape being
   available is not the same as it being the right shape.

---

## ADR-0074 — A definition comes from the Manual, the legislation, or the IP First Response glossary — and from nothing else

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** OQ-0016 asked what to do about nine role terms with no definitions,
against the trap that ADR-0022's scope rule selects passages that *cite* section
43, and a term's definition is usually not in a passage that cites anything
(Q-28). The owner answered: scope should include the subjects, objects and
predicates needed to construct the section's ontology; a glossary is permitted
where it disambiguates; and — the operative sentence — *"Your definitions of
subjects objects and predicates must be identified in the TM Manual, TM
Legislations/Acts or on the IP First Response Glossary page."*

**Decision.** The permission is that scope may reach a term the model depends on
even where its defining passage cites nothing. The **constraint** is a closed
list of three sources for any definition: the Manual, the legislation, or
IP Australia's IP First Response glossary. Nothing else — and in particular not
an agent's own knowledge of trade marks law, which is CLAUDE.md rule 1 restated
by the owner in his own words.

**The third source is not held.** `https://ipfirstresponse.ipaustralia.gov.au/glossary-terms`
is outside the pinned snapshot and outside anything this repo may consume without
a decision about acquisition — it is a live web page, and ADR-0002 and ADR-0004
between them mean this repository does not crawl and does not vendor. Whether it
is acquired, how, and by whom is OQ-0018.

**Consequences.**

1. Until that question is answered, a definition may come from the Manual or the
   legislation only, because those are the two of the three that exist here.
2. `skos:definition` stays unwritten. This ADR names where a definition may come
   from; it does not authorise an agent to write one.
3. The scope permission is not yet implemented as a change to ADR-0022's
   selection rule. Widening it needs to know which terms the model depends on,
   and that list does not exist until the concepts are typed (ADR-0071).

---

## ADR-0075 — A label the vocabulary deliberately excludes is a boundary, not a gap

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** CQ-0007 lists `deceptively similar` as an expected concept; three
approved concepts list it under `not_labels`. Both sides are signed. The build
counted it among "expected-concept labels matching no concept", so every
measurement using CQ-0007 reported a miss that was not a miss (Q-37).

The owner ruled on OQ-0002: *"It belongs to section 44 — keep it out, the
question is using it as a boundary marker."* CQ-0007 asks *"Confusion between my
mark and someone else's — which section is that?"*, whose answer is section 44.

**Decision.** Neither approved record changes. What changes is that the build
joins them: an expected-concept label matching no concept, where an approved
concept records that same label under `not_labels`, is reported as a **boundary**
and not as a gap. The question carries `tmk:expectsBoundaryLabel`, and
`tmk:testsBoundaryOf` names the concepts whose not-labels drew the edge — so the
claim can be traced to the signed records behind it rather than resting on this
decision.

**Why the derivation and not a hardcoded exception.** `not_labels` is the field
the schema calls the most valuable on the record. A label appearing there is the
vocabulary already saying, in a signed record, that the term belongs elsewhere.
The owner's ruling confirms that reading is right; it does not need to be the
mechanism. Three of the four unmatched labels have no such record and stay
reported as gaps, which is the check that the rule is not just softening bad news.

**Consequences.**

1. One label moves from gap to boundary. `CQ-0010:purchasing decision`,
   `CQ-0012:obvious, direct and immediate` and `CQ-0020:superseded legislation`
   remain gaps.
2. The prohibition in HANDOFF §4 — do not resolve this by adding the concept or
   editing the question — held, and neither happened.
3. Any future question naming an excluded term gets the same treatment
   automatically, which is right: naming the boundary is a legitimate thing for a
   test question to do.

---

## ADR-0076 — A question's state is on its collapsed row, and settled questions fold away

**Date** 2026-09-08 · **Authority** agent-proposed · **Status** accepted

**Context.** The owner reported that the form said ten decisions were waiting on
him and that the first question he opened told him he had already answered it.
Both were true. The count filtered on `status: open` and `needs: owner`; the list
below it rendered every question in the theme, in file order, with identical
chips (Q-46). Five answered questions therefore sat above the three still open in
the first theme. Worse, the card computed a single `parked` boolean as *"not open
and mine"* and printed **needs a trade marks expert** under it — so an answered
question was labelled as waiting on someone who was never asked.

**Decision.** Three states — `waiting`, `parked`, `answered` — derived in one
place from `status` and `needs`, and every rendering reads that:

1. The collapsed row leads with a chip naming the state. Urgency (*unblocks
   work*) is shown only while a question is still open, because an urgency on
   something settled is the same false claim in a smaller font.
2. Within a theme, open questions come first, parked next, and answered ones go
   behind a fold labelled *"n questions here are settled — kept for the record"*.
3. Each theme heading carries a computed tally. No blurb states a count of its
   own questions, and a test fails if one does.
4. Only a `waiting` question gets an answer control, which was already true and
   is now expressed as the same state rather than as a second boolean.

**Why answered questions stay on the page.** Removing them would make the page
agree with itself for the wrong reason. The queue's value is that nothing quietly
disappears — the owner can see what he decided, when, and whether it has been
acted on. Folding costs one click and keeps the top of every section actionable.

**What is provisional.** The requirement is not: a page that presents a settled
question as waiting is making a claim the repository does not support, and that
is rule 6. The *fold* is a judgement about the owner's attention that he has not
been asked about, and it is flagged in `HANDOFF.md` under open questions rather
than sent to the queue — adding an eleventh question about the queue's ergonomics
works against the problem he actually reported.

**Consequences.**

1. `site/inbox.js` no longer has a `parked` boolean meaning *"not yours"*. Cards
   carry `data-question` and a `s-<state>` class, so the rendering is checkable.
2. `PARKED_LABEL` distinguishes `expert` from `organisation`. Nothing in the
   queue is `organisation` today; the label exists because the schema allows it
   and the previous code would have mislabelled it.
3. The header badge, the stat tiles and the per-theme tallies now all count the
   same predicate.

---

## ADR-0077 — A question answered outside the form must record where the answer is

**Date** 2026-09-08 · **Authority** derived · **Status** accepted

**Context.** Ten questions carry `status: answered`. Seven are evidenced by
`review/rulings/2026-09-08-issue-12.yaml`, which the form composed and
`tmk-ruling` transcribed. The other three — OQ-0014, OQ-0015, OQ-0016 — the owner
typed into issue #12 by hand, and they are transcribed at
`review/returned/260908-owner-notes-issue-12.md` (ADR-0072 to ADR-0074).

Nothing joined those two facts. The only record that those three had been
answered was a `#` comment beside `status:` in the question file, invisible to
the schema and to the site. The dashboard rendered them as answered, showed no
answer, and — because they are `needs: expert` — offered no control either. A
question in that state is indistinguishable from an open one that has lost its
form.

**Decision.** A question may carry an optional `answered:` block — `date`, `how`,
`record`, and an optional `applied` — naming the file that holds the answer. The
card renders it in the same *"You answered this"* panel as a ruling entry.
`test_an_answered_question_can_show_what_the_answer_was` fails if a question is
marked answered and neither a ruling nor an `answered:` block says what the
answer was, and fails if the named record does not exist.

**What this is not.** It is a **pointer**, not a second transcription. The
owner's words live in one place and this names it. `review/rulings/` remains the
only thing `tmk-ruling` writes and the only thing that may not be hand-edited;
`answered:` is a session recording, in the question file, that a decision was
made somewhere else.

**Consequences.**

1. `status: answered` is now a checkable claim rather than an assertion a session
   can make on its own say-so, which is rule 4 applied to the queue itself.
2. The three questions are visibly answered on the site, with a link to the
   owner's own words.
3. A future answer arriving off-form — a meeting, an email, a decision recorded
   in `review/decisions/` — has somewhere to be recorded without pretending it
   came through the form.

## ADR-0078 — The typing sheet's `notes` cell names a concept three ways: what it is, what else it is called, and what it is not

**Date** 2026-09-08 · **Authority** derived · **Status** accepted

**Context.** The owner asked for it. The `notes` column of the `concept-types`
sheet in `data/derived/concept-typing.xlsx` held the concept's `pref_label` and
its `not_labels` — *"connotation — not: denotation, deceptively similar,
descriptive meaning"* — and he asked that it also carry what the concept is
*also called*.

He is right about the asymmetry. The near-misses were put there to stop a sorter
typing by label (ADR-0071), which assumes the sorter recognises the label in the
first place. `pref_label` is one form of words out of the several the Manual
uses; the record already holds the others in `alt_labels`, they are already
approved, and the evidence pack at `data/derived/reports/concept-typing.md`
already prints them under *Also called*. The spreadsheet is where the sorting
actually happens, and it was the one place showing less than it had.

**Decision.** The cell is `pref_label — also called: … — not: …`, built by
`typing.summarise()`, with a clause omitted when its list is empty. The
`also called` clause sits before the `not` clause: it says what the concept is,
and the near-misses then bound it.

Because the cell is now several times longer, the `notes` column on that sheet is
widened to 72 characters and wrapped, and the workbook's front sheet says what
the column holds and that it is the one column the sorter should not need to
touch. Only the pre-filled rows are restyled; the sheet is still an ordinary
intake sheet that `tmk-transcribe` reads back unchanged (ADR-0048).

**What this is not.** Not a judgement about any concept. Every label in the cell
is a string an approved `gold_concept` record already holds, copied character for
character — `test_the_summary_quotes_the_labels_verbatim` fails if that stops
being true. Nothing is paraphrased, merged or ranked, because choosing which of a
concept's names to show, or wording one differently, would be a machine making a
vocabulary judgement (CLAUDE.md rule 1).

**Consequences.**

1. The 52 rows waiting on OQ-0020 read from the spreadsheet alone. The evidence
   pack is still the place for the passages, and the front sheet now points at it.
2. A row already signed keeps the notes its signer left; `summarise()` runs only
   on rows nobody has ruled on.
3. `data/derived/concept-typing.xlsx` is regenerated. Nothing in `eval/gold/`,
   the ontology, the graph or the dashboard moved — no concept has been typed.

---

## ADR-0079 — An agent may author legal content, stamped as never validated

**Date** 2026-09-08 · **Authority** human · **Status** accepted ·
**Amends CLAUDE.md rule 1**

**Context.** Rule 1 forbade an agent to write legal content of any kind:
definitions, synonym judgements, concept types, modality readings, relationships,
rules, exceptions. Every such artefact was expert-owned. The consequence, measured
after fourteen sessions, was an ontology with 30 of 49 classes empty, 0 of 52
concepts typed, no definition anywhere, 39 of 52 concepts outside any hierarchy,
and 168 records parked behind ten decisions nobody had time to make. The
expert thread had been paused by the owner since S010.

The rule also rested on an observation that turned out to cut the other way.
ADR-0043 already recorded it: experts *"could not readily articulate those
judgements from a blank form — not because they do not know them, but because
knowing them and stating them are different skills. Recognising a wrong answer is
cheap for them. Composing a right one is not."* That argument was used once, to
justify a 368-record seed set. It generalises to the entire corpus.

**Decision.** The owner's, in chat on 2026-09-08, transcribed at
`review/returned/260908-owner-chat-scope-and-authoring.md`:

> *"I would like you to update your rule so that you can make higher risk
> decisions AS LONG AS you record it has not been reviewed or approved by an
> expert yet… In reality, you're still not making a decision. You're making a
> best effort attempt given everything you know and have available to you which
> is then validated/invalidated by a subject matter expert. It also makes it less
> burdensome on the experts because then it's a matter of correcting problems
> rather than writing solutions."*

An agent may author any record type in this repo, including every judgement rule 1
previously reserved. Rule 1 is rewritten from a prohibition on authorship into a
prohibition on **laundering** — letting authored content be mistaken for signed
content.

**The four guards, and they are not optional.**

1. **Every authored record carries `review_status: unreviewed`,
   `authored_by` (model and version), `authored_date`, and `authoring_basis`.**
   A record that cannot carry them is not written. This is CLAUDE.md rule 8,
   which was a hygiene rule before today and is now the only thing standing
   between authored and approved content.
2. **Evidence or abstention.** An authored record names the passages it rests on
   by upstream ref, with span and `content_hash`, exactly as an approved one
   does. Where the corpus does not support a judgement, the record says so in
   `authoring_basis` — `corpus_explicit`, `corpus_inferred` or
   `general_knowledge` — and `general_knowledge` is a flag for a reviewer, not a
   licence. It is the honest label for "I wrote this from what I know about trade
   marks law and the corpus does not say it", and a record carrying it is not
   thereby wrong; it is thereby unevidenced, and the difference must stay
   visible.
3. **`approved_by` is never written by an agent.** Not with a name, not with a
   model identifier, not with the owner's initials. It means a person read this
   record and signed it.
4. **Authored content is physically separate from signed content** — ADR-0080.

**Rationale.** The owner's, and it is an argument about where review effort is
best spent rather than about what a model knows. A fully populated ontology an
expert can interrogate and correct produces more correct knowledge per hour of
expert time than an empty one they must fill. It also produces engagement: *"Having
a working version will motivate them to engage with the process because the value
will become clear."*

**Consequences.**

1. Everything the old rule 1 forbade is now ordinary work. The four empty concept
   classes fill. Definitions get written. The 39 flat concepts get a hierarchy.
   All of it stamped, none of it signed.
2. **The repo's risk profile changes and this ADR is where that is recorded.**
   Before today, a wrong statement in `eval/gold/` meant an expert made a
   mistake. From today, a wrong statement in `authored/` means a model made one,
   and there may be thousands. The mitigation is the stamp, the evidence
   requirement, and ADR-0080's separation — not confidence in the model.
3. `review/questions/open-questions.yaml` shrinks sharply. A question an agent can
   answer and stamp is no longer an owner question (CLAUDE.md §3 step 6).
4. ADR-0043's seed apparatus is superseded in purpose. Its guards existed to fence
   off machine-written legal content as a one-off exception; that content is now
   the normal case and `authored/` holds it under a permanent version of the same
   guards.
5. This does not touch rules 2, 3, 5, 7 or 8, and it explicitly does not touch the
   product-scope limit in §6 — see ADR-0082 consequence 4.

---

## ADR-0080 — Authored knowledge lives in `authored/`; `eval/gold/` is frozen as the signed set

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** ADR-0079 lets an agent author legal content. Where it lands decides
whether the project can ever measure how good that content is. Three options were
put to the owner: merge everything into `eval/gold/` with per-record status; keep
them separate; or keep them separate and migrate on review.

**Decision.** The owner chose separation with the graph reading both.

- **`eval/gold/`** is **frozen** at the 190 records a named expert signed. Nothing
  an agent authors is written there, ever. It remains the gold standard in the
  measurement sense: an independently produced reference set, uncontaminated by
  model output.
- **`authored/`** holds everything an agent writes, mirroring the same record
  types and the same schemas, each record wrapped in an authoring envelope.
- **The graph reads both** and stamps every node with where it came from. The
  ontology is fully populated regardless of which store a record sits in.
- **A record moves from `authored/` to `eval/gold/` only through
  `tmk-transcribe`** — the same single door, the same requirement of a verdict
  and a name. An agent never carries a record across.

**Rationale.** A merged set is simpler to read exactly once, and then permanently
unable to answer "how good is the authored content?" — because the benchmark
would contain the thing being benchmarked. Keeping 190 independently-produced
records intact preserves the only yardstick the project has. It costs one
directory and one flag on every graph node.

**Consequences.**

1. Ids are allocated from one sequence across both stores (`docs/IDENTIFIERS.md`
   §3). One `GC-0123` in the project, wherever it lives. A duplicate id across
   stores is a defect the harness reports.
2. Where an authored record and a signed record cover the same ground, the signed
   one wins and the authored one is retired — the reverse of the ordinary rule
   that a record is never deleted, and it is right here because the signed record
   is strictly better evidence of the same thing.
3. `tmk-harness` and `tmk-coverage` report the two stores separately and never
   sum them into a single "records we have" figure. A count that hides the split
   is the merged set arriving by the back door.
4. Every dashboard figure gains a signed/authored split. A reader must be able to
   see, without asking, how much of what they are looking at a person has read.

---

## ADR-0081 — The whole Manual is in scope; the section 43 boundary is withdrawn

**Date** 2026-09-08 · **Authority** human · **Status** accepted ·
**Supersedes ADR-0022 and ADR-0072; amends ADR-0013**

**Context.** ADR-0013 fixed the pilot area as section 43 in S002. The *boundary* —
which Manual Parts and chunks come with it — was the first Stage 0 deliverable and
was never delivered. Seven sessions later `eval/pilot-scope.md` still did not
exist. In the meantime the boundary produced: a one-hop selection rule (ADR-0072),
a 12-provision exclusion table, a 12KB generated report, and OQ-0021 — a question
back to the owner asking him to adjudicate how loosely the Manual cites
provisions, after the rule met the corpus and failed to do what he expected.
Section 41 is cited bare in 32 passages; 22 provisions behave that way.

The owner, in chat on 2026-09-08: *"I would like to completely remove the s43
barrier."*

**Decision.** The whole Trade Marks Examination Manual is in scope — 500 pages,
54 Parts, 2,460 chunks — together with the legislation already loaded. There is
no boundary rule, no exclusion list, and no in-scope/out-of-scope judgement for
any passage. **Section 43 becomes a starting point rather than a fence**: it is
what gets worked first, not what defines what may exist.

**Rationale.** The boundary was doing two jobs and only one of them needed doing.
Job one — controlling how much material a person is asked to look at — is real,
permanent, and better done by an ordered work queue, which the tooling already
supports (`tmk-seed --only`). Job two — defining what the ontology is allowed to
contain — was generating every artefact listed above, and did not need doing at
all: an ontology that admits a concept it has not collected yet costs nothing,
as the 30 currently-empty classes demonstrate.

Three further findings argued for it, all measured rather than assumed:

- **The ontology was never section-43-shaped.** The 49 classes came from the
  roadmap. Narrowing to s 43 did not shrink the class list; it left 30 of 49 empty.
- **A third of the existing vocabulary is already Manual-wide** — *examiner,
  decision maker, Registrar, opposition, priority date, divisional application,
  revocation of acceptance, endorsement, specification of goods and services* and
  more, collected accidentally and out of context because they appeared in a
  passage that cited s 43.
- **The selection rule was structurally blind to definitions** (Q-28). It selected
  passages that *cite* section 43; a term's definition sits in a passage that
  cites nothing. That is why no concept has a definition and why four of the nine
  role terms the expert named — Delegate, Office Practise, Subject Matter Expert,
  Adverse Report — are absent.

**Consequences.**

1. **ADR-0022 is superseded.** The worksheet no longer selects by citation of
   `TMA1995/s43` plus page-mates. It covers the corpus, ordered by working
   priority.
2. **ADR-0072 is superseded.** The one-hop rule, the parent/unit distinction and
   the exclusion table describe a boundary that no longer exists.
   `tmk-boundary` and `data/derived/reports/boundary.md` are retired; the code
   stays until the next session removes it, and must not be cited as current.
3. **ADR-0013 is amended, not reversed.** Section 43 remains the first area
   worked and the reason the existing 190 records exist. It is no longer a limit.
4. **OQ-0021 is withdrawn** — it asked the owner to adjudicate bare citations for
   a rule that no longer runs. Q8, open since S002, is closed the same way:
   the question was "where does s 43 stop", and the answer is that it does not
   have to.
5. `eval/pilot-scope.md` is not written and is no longer owed. What replaces it is
   a priority ordering, which is a work-management artefact rather than a legal
   one.
6. The 725 annex chunks now in scope are low-value and known to be so (Q-10).
   Ordering handles them; exclusion does not.

---

## ADR-0082 — Tier 3 no longer gates output; the label is the control

**Date** 2026-09-08 · **Authority** human · **Status** accepted ·
**Supersedes ADR-0008**

**Context.** ADR-0008 was `inherited` from the roadmap: legally significant
outputs — obligations, exceptions qualifying rules, overruling, legal conclusions
— require expert approval *indefinitely*, and no measured accuracy moves an
output out of Tier 3 without an explicit human policy change recorded as a new
ADR. This is that ADR.

**Decision.** The owner was asked whether unreviewed content stays out of what
the system eventually presents to an examiner, or whether visible labelling is
sufficient. He chose **labelling is enough**: unreviewed content may be served
like anything else, provided it is visibly marked as never validated by an
expert.

**Rationale.** His, and consistent with ADR-0079: the value of a populated system
that experts correct exceeds the value of an empty system that waits for them,
and the label carries the honesty burden. Deferring the question was offered and
declined.

**Consequences.**

1. Tier 3 remains a **descriptive** field on a record — it still says "this is
   legally significant" and still drives review priority. It is no longer a
   **gate**. `tier: 3` does not stop anything.
2. **The weight is now entirely on the label being seen.** Any surface that
   presents knowledge to a person — retrieval output, evidence package, the
   dashboard, an API response — must show review status at the point of use, not
   in a footnote or a legend. A surface that cannot show it must not serve
   unreviewed content. This is the operative constraint that replaces the gate,
   and Stages 7–8 inherit it as a build requirement.
3. Stages 7 and 8 do not exist yet, so nothing changes operationally today. The
   decision is recorded now because it must be built into those stages rather
   than retrofitted.
4. **This did not widen the product's scope.** The programme still does not
   automate a final examination decision, and the eleven expert-approved
   prohibited-use records still stand as approved knowledge — PU-0001's
   *"this trade mark should be rejected under section 43 because…"* remains
   prohibited output. ADR-0082 removes a review gate on knowledge; it does not
   authorise the system to decide a case. An agent may not widen that scope; the
   owner may, and has not been asked to.

---

## ADR-0083 — Stages 2–4 open over the whole Manual

**Date** 2026-09-08 · **Authority** human · **Status** accepted ·
**Supersedes ADR-0010**

**Context.** ADR-0010 held that no Stage 2+ pipeline work begins until `eval/`
holds a pilot scope, a competency-question catalogue, a gold-standard set, a
prohibited-use list and a runnable harness. Its reasoning was sound and remains
worth reading: without a gold set the measurements do not exist, and *"the first
plausible-looking extraction output becomes the de facto standard purely because
it arrived first."*

**Decision.** The gate is lifted. Terminology extraction, entity recognition,
clustering and relation extraction (Stages 2, 3 and 4) may run across all 54
Parts. The owner's answer, when asked whether the rule change opened extraction
or only hand-authoring: **open Stages 2–4.**

**Rationale.** Hand-authoring across 2,460 chunks does not scale even for an
agent, and ADR-0079's goal — a fully fleshed-out ontology for experts to
interrogate — is not reachable without extraction. The measurement concern that
motivated ADR-0010 is now addressed differently rather than ignored: ADR-0080
freezes the 190 signed records as an uncontaminated reference set, so extraction
output can be measured against something a machine did not write. That is the
protection ADR-0010 was reaching for, and it now exists, which it did not in
August.

**Consequences.**

1. The Stage 2 stack stands as fixed by ADR-0019 — TextRank, YAKE and KeyBERT in
   parallel, spaCy NER as candidate metadata only. Nothing about *how* extraction
   runs is reopened here, only *whether*.
2. **HANDOFF Q3 becomes urgent and is now a real blocker.** Which LLM is
   agency-approved, and under what data-handling conditions Manual text may be
   sent to it, was a Stage 2–4 question that nothing was waiting on. Stage 2–4
   now start. Deterministic extraction (rule 7) proceeds without it; anything
   model-backed does not.
3. Extraction output is *candidate* output and lands in `review/candidates/`, not
   in `authored/`. The two are different: a candidate is a proposal with a score,
   an authored record is a judgement an agent committed to. Promotion from
   candidate to authored is itself an act of authorship and carries the ADR-0079
   envelope.
4. The first extraction run is measured against the 190 before anything is built
   on it. A recall figure against a frozen reference set is the number ADR-0010
   wanted to exist and never got.
5. `docs/roadmap/PARALLEL-TRACK-ROADMAP.md`'s five gates are largely moot. Its
   package list stays useful; its gating does not apply.

---

## ADR-0084 — The seed backlog is resolved by authoring, not by waiting

**Date** 2026-09-08 · **Authority** human · **Status** accepted

**Context.** 178 seed records sat in `review/seed/` awaiting expert correction,
with 168 of them held behind ten decisions on the critical path (ADR-0053,
ADR-0054). The expert round that would settle them was paused by the owner in
S010 and has not resumed. `tmk-blockers` has been reporting the same ten
decisions for six sessions.

**Decision.** Every held seed record is resolved by an agent under ADR-0079,
stamped `unreviewed`, and moved into `authored/`. The critical path clears
without an expert round. The owner chose this over leaving the backlog parked and
over separating out the ten decisions his expert's review had specifically
flagged.

**Consequences.**

1. `review/seed/` empties. Its purpose — machine-written examples awaiting
   correction — is now served by `authored/` for the whole corpus, so the
   directory is retired rather than maintained.
2. **The eight rejected seed records are not resurrected.** A named expert threw
   each of them out on a recorded date; that is a signed human decision and
   ADR-0079 does not license reversing one. They stay rejected, they stay where
   the pointers to them resolve, and an authored record may not silently occupy
   the ground a rejected record was rejected from — if it covers the same
   assertion, it cites the rejection and says why it differs.
3. **The reviewer's marked corrections are honoured, not re-decided.** Where a
   record was marked `amend` with an instruction, the authored version applies
   that instruction. Where it was marked `amend` with no instruction, the
   authored version is a fresh judgement and says so.
4. The ten critical-path decisions are recorded as resolved-by-authoring, naming
   the record each one released, so a later expert can find the exact points
   where their colleague had doubts and a machine proceeded anyway.
5. ADR-0043's guards lapse with the directory they fenced. ADR-0079's guards
   replace them and are stricter in the one way that matters: they are permanent
   rather than a time-limited exception.

---

## ADR-0085 — Silence is not validation

**Date** 2026-09-08 · **Authority** derived · **Status** accepted

**Context.** The owner's instruction includes: *"If something is not corrected, it
can be assumed that it's valid (though we'll retain a record that it has never
been validated by an expert)."* Both halves of that sentence have to be
implemented, and they pull in opposite directions.

**Decision.** Four review states, and the difference between the last two is
never collapsed:

| state | means | set by |
|---|---|---|
| `unreviewed` | authored; no person has looked at it | an agent, on writing it |
| `seen_uncorrected` | a person had it in front of them and did not change it | a review round that covered it |
| `approved` | a person read it and signed it | `tmk-transcribe`, with a name and a date |
| `rejected` | a person read it and threw it out | the same |

An unreviewed or uncorrected record **may be relied on and may be served**
(ADR-0082). It **never becomes approved by the passage of time**, by not being
challenged, or by an agent's assessment that it is obviously right.

**Rationale.** The operational half of the owner's sentence is a decision about
*usability* — do not block on review — and it is his to make. The archival half is
a decision about *record-keeping*, and treating "nobody objected" as equivalent to
"an expert confirmed" would destroy exactly the distinction ADR-0080 spent a
directory preserving. `seen_uncorrected` is what makes both halves true at once:
it is stronger evidence than `unreviewed`, weaker than `approved`, and it is a
fact about what happened rather than an inference about what someone thought.

**Consequences.**

1. Review status is permanent and monotonic. A record's history shows every state
   it held and when. Nothing is overwritten.
2. `seen_uncorrected` requires evidence that the person actually saw the record —
   a review round that listed it — not that they saw a page it was on.
3. Any figure quoting "validated" content counts `approved` only. A dashboard
   number that adds `seen_uncorrected` to `approved` is the error this ADR exists
   to prevent.
4. This is `derived` rather than `human`: the four-state model is an agent's
   reading of how to make the owner's two clauses simultaneously true. If he
   would rather `seen_uncorrected` count as approved, that is a one-line change
   and a superseding ADR.

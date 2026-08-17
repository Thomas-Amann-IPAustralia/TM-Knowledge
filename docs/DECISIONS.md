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

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** provisional — see HANDOFF Q2

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

**Date** 2026-08-04 · **Authority** agent-proposed · **Status** provisional — see HANDOFF Q5

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

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** provisional — see HANDOFF Q9

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

**Date** 2026-08-17 · **Authority** agent-proposed · **Status** provisional — see HANDOFF Q10

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

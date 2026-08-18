# QUIRKS — traps, discrepancies and hard-won facts

Things that will cost you time if you meet them cold. Append as you find them,
**when** you find them. Each entry gets a stable `Q-nn`; never renumber. If an
entry is fixed or superseded, mark it rather than deleting it — the fact that it
was once true is itself useful.

Sources: the roadmap, `docs/UPSTREAM.md`, and — from S004 — the pinned snapshot
itself. Entries marked *unverified* were inferred from documentation and have
not been checked against the corpus. **That excuse expired in S004**: the
snapshot is fetchable in one command (`tmk-fetch-upstream`) and section E was
measured against it. If you rely on an unverified entry from section B, check it
and say so here.

---

## A. Where the roadmap and reality disagree

### Q-01 — The roadmap has eleven stages; `UPSTREAM.md` says seven

`docs/UPSTREAM.md` §6 describes the roadmap as "Stages 0–7". The roadmap document
actually runs **Stage 0 through Stage 10**: 7 is ontology-enhanced search, 8 is
graph-aware AI retrieval, 9 is automated reasoning, 10 is automated maintenance.
The summary line simply stops early. Stage names in `UPSTREAM.md` (5 = formalise
the ontology, 6 = knowledge graph + SHACL, 7 = search) are correct as far as they
go. Cite stage numbers from the roadmap itself, not from the summary.

### Q-02 — The roadmap's identifier example cannot be used

The roadmap illustrates stable identifiers as
`tmem:manual/2026-01/chapter-4/section-3/paragraph-12`. Upstream emits
`TMM/Part22/1/1/2` and `TMA1995/s41(3)(a)`, and the Manual↔legislation join is
plain string equality on those refs. Adopting the roadmap's form would discard a
join that already works at 97% coverage. Settled by ADR-0005 in favour of the
upstream refs; see `docs/IDENTIFIERS.md`. The roadmap is a source document — do
not rewrite it, annotate around it.

Note also that `2026-01` in that example implies a monthly corpus version stamp.
No such thing exists (Q-05).

### Q-03 — Docling, Tika and OCR are moot for the existing corpus

Roadmap Stage 1 specifies Docling as the primary parser, Tika as fallback and OCR
for scanned sources. None of that was used, and none of it applies:

- The **Manual** has no PDF and no API. It is rendered HTML, scraped and parsed
  structurally.
- The **legislation** comes from the Federal Register of Legislation API as
  compiled `.docx`, parsed via the OPC `w:pStyle` stylesheet — the style name is
  retained on each unit as evidence. Upstream's `LEGISLATION_NOTES.md` documents
  why `.docx` and not PDF, and why not to scrape the site.

If you are ever asked to "implement Stage 1 with Docling", the answer is that
Stage 1 is done by other means and re-doing it would violate ADR-0002. Docling
and Tika may become relevant only for *new* source types — case law PDFs being
the obvious candidate (Q-11).

### Q-04 — Stage 1's missing artefacts are missing here too

Upstream's `ROADMAP-STAGE-1.md` assesses 4 of 6 Stage 1 deliverables complete. The
**version register** and the **source-quality report** exist as data (manifests,
content hashes, test results) but not as the named artefacts the roadmap asks for.
If a Stage 1 sign-off is ever needed, that is the gap, and it is cheap to close.

---

## B. Upstream data traps

*All of section B is from `docs/UPSTREAM.md`; unverified against the snapshot.*

### Q-05 — There is no corpus-level version, and no historical page text

Versioning is per-page and per-instrument, not per-corpus: a page carries
`content_hash`, `date_published`, `last_amended` and `amendment_note` (IP
Australia's own words); an instrument records which compilation is held.
`snapshot/retired.json` records pages that left the Manual and when. **A single
checkout holds only the current text** — the amendment log is the upstream repo's
git history.

This bites directly on the roadmap's competency question *"what guidance was
current on a specified date?"* Answering it properly needs the upstream git
history, not just a snapshot. Do not promise point-in-time answers from a shallow
clone. Scope this explicitly during Stage 0 rather than discovering it in Stage 8.

### Q-06 — Superseded provision numbering: the s 41 renumbering

Some Manual text cites legislation by numbering that no longer exists — pre-2012
`s 41` is called out by name upstream as a cause of unresolved edges. A graph that
naively attaches such guidance to today's `TMA1995/s41` will bind commentary to
the wrong provision text while looking perfectly well-formed.

Distinctiveness is also the roadmap's suggested pilot area, so if the pilot is
s 41 this trap is on the critical path, not at the margin. Treat provision refs
appearing in the unresolved set as suspect and route them to review.

### Q-07 — `certainty: "default"` is an inference, not an author's statement

The three values mean different things and only one is an assertion by IP
Australia:

- `explicit` — the instrument was named adjacent to the reference.
- `default` — bare "section N", resolved to the Act **by convention**. This is
  upstream's inference. It is usually right and it is still an inference.
- `ambiguous` — several instruments of that kind are in scope. Feeds a human
  review queue and nothing else. **Never auto-resolve an ambiguous edge**; that
  is the exact behaviour upstream refused to implement.

Separately, `extraction: "href"` means the Manual's authors linked it themselves;
`"regex"` means upstream inferred it from prose. Federal Register links are
deliberately not read; AustLII path-form and TimeBase query-form links are.

Every legislation-to-legislation edge is `regex` by necessity — compiled
instruments contain zero hyperlinks.

### Q-08 — Unresolvable internal refs are dropped, not recorded

`internal_refs[]` only contains refs that resolved to a `page_ref` or `chunk_ref`.
Unresolvable ones are discarded. So absence of an internal ref is *not* evidence
that the source text made none — a link-density or cross-reference metric built on
this field is measuring resolution success, not the Manual's actual cross
referencing. Self-page refs are deliberately kept (25 chunks), so filter them if
you are building a page-to-page graph.

Provision edges behave differently: 76 of 2,687 in-scope edges do not resolve and
those failures are visible. Watch the coverage figure (97%), not the individual
failures — most are Manual citation defects, superseded numbering (Q-06), or the
Part 22.1 anaphora case where "s 26" means the *1955* Act.

### Q-09 — Fields that are absent because they are derivable

Not bugs, and not to be requested upstream: `part_id` on a chunk, `heading`,
`instrument`/`root_id` (parse the ref), `token_count`, `previous`/`next`. Derive
them in this repo. Note that a chunk's Part comes from the **nav tree**, never
from the URL — upstream is explicit that the URL lies about Part membership.

### Q-10 — Headings are not always markup

`heading_source` is `markup` or `emphasis`: some subsections are bold text that
looks like a heading but is not marked up as one, and heading numbering across the
Manual is inconsistent. `heading_path` is therefore a useful retrieval signal but
a weak structural guarantee. Corpus shape is also lopsided — of 2,460 chunks, 725
are `annex` and 52 are `landing`; only 1,683 are `body`. Retrieval that treats all
chunks alike will surface a lot of annex material.

Upstream's `SOURCE_NOTES.md` holds 35 numbered sections of this kind of detail and
is described as the single most valuable file if you re-read the HTML. **It is not
in this repo.** Fetch it (Q-13) before doing anything that depends on Manual
structure.

### Q-11 — There is no case law, only citations

519 case edges across 411 distinct decisions, exported as `exports/cases.csv` with
neutral (`[2018] FCAFC 109`) and reported (`(1954) 71 RPC 43`) citation styles and
a canonical `case_id`. **No decision text exists anywhere in the programme.**
Competency questions of the form "which cases interpret this test" can be answered
at citation level; "what did the court hold" cannot. Acquiring decision texts is
an open scope question (HANDOFF Q6) with its own licensing and access problems.

---

## C. Domain traps

### Q-12 — The Manual states practice; it is not law

It records the Registrar's practice. It does not bind the Registrar's discretion
and it is not legislation. Any model, index or retrieval response that lets a
Manual paragraph read as if it were statutory text is wrong in a way that matters
legally, not just structurally. Keep `ManualInstruction` and `LegislativeProvision`
distinct classes, keep authority type on every indexed passage, and make the
distinction visible in retrieval output rather than only in the graph.

The same care applies to the roadmap's Tier 3 list — overruling, exceptions
qualifying general rules, evidence being *required* rather than merely relevant,
instructions creating obligations. These are the judgements that look like
extraction problems and are not.

### Q-16 — spaCy NER labels are not the gold entity types, and two of them collide by name

*Unverified — recorded when ADR-0019 added spaCy NER as candidate metadata, before
any code exists.*

A stock spaCy model emits OntoNotes labels: `PERSON`, `ORG`, `GPE`, `DATE`,
`LAW`, `NORP`, `EVENT` and the rest. The gold entity taxonomy in
`eval/templates/gold-record.template.yaml` is `LegalConcept`,
`LegislativeProvision`, `JudicialDecision`, `EvidenceCategory`,
`ManualInstruction`, `Role`, `Date`, `Other`. **These are different vocabularies
that happen to share two spellings**, and the overlap is the trap rather than the
convenience it looks like:

- **`DATE` is not `Date`.** OntoNotes `DATE` covers any temporal expression,
  including "recently", "the last three years" and "the 1990s". The gold `Date`
  is a date that matters to examination. A 1:1 map imports the first as if it
  were the second and inflates every entity count.
- **`LAW` is not `LegislativeProvision`.** OntoNotes `LAW` means "named documents
  made into laws" — it will happily tag *Trade Marks Act 1995* and miss "s 43"
  entirely, which is the thing that actually needs recognising. Meanwhile
  upstream has already extracted every provision edge deterministically, with
  `extraction` and `certainty` attached.

Hence ADR-0019 consequence 4: **NER metadata must not be used for provisions,
cases or internal refs.** Upstream's edges win wherever they exist. Replacing
`certainty: ambiguous` with a model's confidence score is not an upgrade — it is
the loss of the only signal that distinguishes an author's assertion from an
inference (CLAUDE.md rules 2 and 3).

Treat NER output as what ADR-0019 calls it: metadata on a candidate, stored under
its own key with its own label vocabulary, never written into an `entity.type`
field. If a mapping between the two vocabularies is ever wanted, it is an
expert-approved lookup, not a rename.

---

## D. Environment and tooling

### Q-13 — The upstream repo is not attached to an agent session by default

Session repository scope covers `Thomas-Amann-IPAustralia/tm-knowledge` only.
`manual-XtrACTor` is a separate repo and must be attached deliberately (`add_repo`
with owner `Thomas-Amann-IPAustralia`, repo `manual-XtrACTor`) before you can read
`SOURCE_NOTES.md`, `SCHEMA.md`, `ARCHITECTURE.md` or the snapshot itself. Do not
pre-check with `curl` or `git ls-remote` first — an unauthenticated 404 on a
private repo is meaningless and will mislead you into concluding it does not
exist.

`docs/UPSTREAM.md` is a summary, not a substitute. It is accurate but it is
roughly 200 lines standing in for several thousand.

**Amended S004.** `manual-XtrACTor` is **public**, and this environment's git
proxy serves anonymous clones and fetches of it with nothing attached — which is
why `tmk-fetch-upstream` works from a bare checkout. What still needs a
deliberate attachment is the GitHub **API**: `api.github.com` refuses
releases, tags and issues for an unattached repo, so use `git ls-remote` for
refs and `add_repo` only when the API is genuinely needed. The advice not to
pre-check with `curl` stands, and now for a second reason: a 404 or a refusal
from the API says nothing about whether git can read the repo.

### Q-14 — Agent containers are ephemeral; upstream history is the amendment log

Two consequences that compound. Anything not committed and pushed is lost when the
container is reclaimed — hence the `HANDOFF.md` discipline in `CLAUDE.md` §3. And
because upstream's git history *is* its amendment log (Q-05), a shallow clone of
it silently discards the temporal dimension of the corpus. If you clone upstream
for historical work, clone it with full history and expect it to be large.

### Q-15 — The repo started with a space in a filename

`Automation-First Roadmap for a Trade Marks Examination Knowledge System.md`
required quoting in every shell command that touched it. Renamed in S001
(ADR-0003). Mentioned here because the source documents arrive by upload from a
human and the next one will probably have spaces too — rename on arrival, with
`git mv`, and record it.

---

## E. Found by building against the snapshot (S004)

*Everything in this section is **verified**: measured against the pinned
snapshot, `manual-XtrACTor` @ `c490a99` (`ingest/0.11.0`, `legislation/0.2.0`),
and asserted in `tests/unit/`. That is the difference between section B and this
one — B was read out of documentation, E was run.*

### Q-17 — A chunk ref can contain `#`, and `IDENTIFIERS.md` §2 breaks on it

`IDENTIFIERS.md` §2 says to mint an IRI by concatenation and **never** to
percent-encode. 498 of the corpus's 2,460 chunk refs contain a `#`
(`TMM/Part9/2#1~1`, `TMM/Part26/6#3~2`), and 333 contain a `~`. A `#` opens an
IRI fragment (RFC 3986 §3.5), so `<BASE>ref/TMM/Part26/6#3~2` names the resource
`<BASE>ref/TMM/Part26/6` and a fragment of it — a *different subject*, and
silently. One in five chunks in the corpus would have been given the wrong IRI.

`~`, `(`, `)`, `.` and `-` are all legal in an IRI path and are left verbatim, so
the no-encoding rule holds everywhere it can. Only `#` is escaped, as `%23`, and
`from_iri` reverses it. ADR-0023, and
`tests/unit/test_refs_corpus.py::test_percent_encoding_is_confined_to_the_hash`
is what keeps the exception to one character.

### Q-18 — A ref does not say what level it addresses

Two collisions, both real and neither documented:

- **Page vs chunk.** A page ref is a prefix of the chunk refs cut from it, both
  admit slug segments (`TMM/Part9/x-relevant-legislation23`), and in the pinned
  corpus page refs carry 2–3 slashes while chunk refs carry 2–7. `TMM/Part14/4/4/5`
  cannot be placed by grammar.
- **Provision vs unit.** `TMR1995/sch3/item1` is a provision record;
  `TMA1995/s128/prescribed-period` is a *unit* — a defined term inside s 128 —
  and they share a shape. 39 provisions and 189 units (228 refs) are undecidable
  this way.

`refs.parse_ref` reports `RefKind.MANUAL` / `RefKind.LEGISLATION` for these
rather than guessing, and a caller that read the ref out of a known field may
state the level. Resolving one otherwise needs the snapshot, which is the
loader's job. ADR-0025.

Related: the legislation ref grammar reaches well past the four forms
`IDENTIFIERS.md` §1 tabulates. Real refs include `TMA1995/front`,
`TMR1995/pt17a/div8`, `TMR1995/sch1/pt2`, `TMR1995/sch3/item1`,
`TMR1995/sch3/item1/designated-owner(a)` and the `~N` ordinal form
`TMA1995/front~1`. The instrument invariants only assert against section and
regulation addresses, exactly as upstream's own `instrument_holds` does.

### Q-19 — Upstream publishes no releases and no tags

ADR-0004 and the parallel track both say "pinned release". `git ls-remote --tags`
on `manual-XtrACTor` returns nothing, and the repo has no GitHub releases
(checked 2026-08-18). So "pinned release" is realised as a **pinned commit**
fetched by sha — which is what ADR-0004 records in the manifest anyway.

Fetching by sha rather than cloning a branch is load-bearing, not stylistic: the
default branch moves, and a branch clone would silently re-point the corpus under
a repo whose entire provenance story rests on knowing which text an assertion was
made against. Note also that `main` is not the newest branch — scheduled crawl
branches (`crawl/2026-08-16-r9`) run ahead of it, so "latest" is ambiguous
upstream and the pin has to be explicit. ADR-0026.

### Q-20 — `UPSTREAM.md`'s join figure does not reproduce at the pinned commit

`docs/UPSTREAM.md` §2 and §5 quote **2,611 of 2,687** in-scope provision edges
resolving. Computed at `c490a99` by upstream's own definition — every
`provisions[].id` whose instrument is `TMA1995` or `TMR1995`, matched by string
equality against the provision and unit refs held — the figure is **2,615 of
2,691 (97.2%)**. The unresolved count is identical at **76**; the difference is
four more edges in scope.

Nothing is wrong: the doc's number was measured against an earlier corpus.
`UPSTREAM.md` is a source document (ADR-0003) and is annotated here rather than
edited. Cite the measured figure from `Corpus.join_report()`, which is asserted
in `tests/unit/test_loader.py`, and treat any quoted corpus count as meaningless
without a pin beside it — ADR-0004 said exactly this and this is the first case
of it biting.

### Q-21 — s 43 has no numbered subsections, so "s 43(1)" resolves to nothing

The pilot provision (ADR-0013) is a single unnumbered sentence. Its only unit is
`TMA1995/s43~1` — the ordinal form — and there is no `TMA1995/s43(1)`,
`s43(a)` or anything below it in the corpus.

Two consequences for Stage 0. A gold record or competency question citing
"s 43(1)" cites a ref the corpus cannot resolve, and the harness will say so
rather than silently accept it. And ADR-0022's worksheet rule matches units
beneath the provision, which for s 43 means the `~1` form and nothing else — the
rule is right, but the "or any unit beneath it" clause does almost no work here
and will do a great deal for a provision like s 41.

Measured for the pilot area at the pinned commit: **67 chunks cite s 43** across
**36 pages**, and ADR-0022's rule selects **216 chunks** (8.8% of the corpus,
~40,000 words) once page-mates are included. 17 in-scope refs cited from those
chunks resolve to nothing, 2 edges are `certainty: ambiguous`, and 58 distinct
decisions are cited at citation level.

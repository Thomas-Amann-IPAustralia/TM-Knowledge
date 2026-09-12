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

### Q-22 — The record schemas `$ref` the shared definitions two different ways

`eval/schemas/*.schema.json` names shared definitions by their `$id`
(`https://ipaustralia.gov.au/schemas/tmk/stage0/common/1.0.0#/$defs/upstream_ref`),
but `common.schema.json` names its own by fragment alone (`#/$defs/upstream_ref`
— that is how `ref_list` reaches `upstream_ref`). `jsonschema` resolves both
without noticing; anything that walks the schemas itself must handle both, or it
silently finds no refs inside a `ref_list` and reports a gold set it never fully
checked.

`schemas._deref` handles both spellings. This is the kind of failure that costs
nothing to fix and everything to find: the walker returned fewer paths, the
resolution checks ran over fewer fields, and every report still said "clean".

### Q-23 — A green pytest and a red harness are two different signals; keep them apart

The guide's §7 says "the suite runs and **fails**". The tempting reading is to
leave a failing test in `pytest`. Do not: a permanently red `pytest` cannot
distinguish "Stage 0 has not arrived" from "the code is broken", which is exactly
the collapse ADR-0018 forbids, and it makes every future regression invisible.

The split built in S005: `pytest` tests the harness and is green; `tmk-harness`
runs the gate and exits 3. The test that guards the redness asserts the *gate*
goes red on an empty gold set built in `tmp_path` and quiet on a full one — so it
keeps working, unchanged, on the day Stage 0 finally completes. A test that
asserts today's state has to be deleted the day the project succeeds, which is
the worst possible day to be editing tests.

### Q-24 — The Manual cites the *Trade Marks Act 1905* and only two instruments are held

*Verified S007 against the pinned snapshot.*

`TMM/Part29/3/3/1~2` — inside the s 43 pilot scope — carries a provision edge to
`TMA1905/s114`, extracted by regex with `certainty: explicit`, because the
Manual names the instrument in terms: *"these comments were made in deciding an
opposition under section 114 of the Trade Marks Act 1905"*. The corpus holds
exactly two instruments, `TMA1995` and `TMR1995`, so that ref **resolves to
nothing** and cannot be made to.

It is not the only one. Inside the 216-chunk provisional scope there are 35
edges to instruments the programme does not hold or to units that do not exist,
including `TMA1955/s28`, `TMA1955/s131(1)(a)`, `AIA1901/s13`, `DR2016/r74` and
several `PBRA1994` sections.

Three consequences worth having before Stage 8:

- This is **unresolvable by construction, not by error**. Do not file it as an
  upstream bug, and do not treat an unresolved foreign-instrument edge as a
  citation defect.
- A ref-typed schema field cannot hold it: putting `TMA1905/s114` in
  `required_provisions` makes the harness report a defect, correctly. Where a
  gold record needs to name it, it goes in a free-text field and the record says
  why (see `SEED-GR-0021`, `SEED-GA-0017`).
- It is a live `stale_source` risk on the critical path, not a hypothetical one:
  a system that reports "section 114 provides the test" has handed an examiner a
  test from a repealed Act, and every word of it came from the corpus.

### Q-25 — A term of art in the corpus is broken across a line and arrives with a space in it

*Verified S007 against the pinned snapshot.*

`TMM/Part29/5/5/5` contains the string `International Non- Proprietary Name
stem` — hyphen, space, capital P. It is the same term as the `International
Non-Proprietary Names` in its own heading path and in `TMM/Part29/5/5/1`, broken
across a line in the source and flattened into the chunk text with the break
preserved as a space.

Nothing normalises this away safely. Stripping a space after a hyphen would join
words that belong apart elsewhere in the corpus, and the Manual's own INN-stem
material is full of hyphens that are meaningful (`-profen`, `CEF-`, `-kef-`).

The general lesson is the one guide §5.2 already states and this is the sharpest
instance of: **a surface form is copied out of the corpus, never retyped.** The
same trap is set by typographic quotation marks (`‘Earthhaven Confest’`), by an
en dash in `Part 26 – Conflict with Other Signs` where a hyphen appears in
`Part 32A - Examination of Trade Marks for Plants`, and by a missing word in
`TMM/Part29/8/8/3` ("any trade mark which could viewed as a radio call sign").
Each of them is annotated in `review/seed/entities.seed.yaml` so the trap is on
the record rather than in someone's memory.

### Q-26 — A signed row is the *only* row carrying a date, so a date bug inverts the gate

*Found S008, on the first returned workbook.*

`approved_date` arrived as `25/08/2026` on some sheets and as an Excel date cell
on others. Both fail the schema's ISO pattern, so `tmk-transcribe` rejected 270
rows — and every one of them was a row the expert had **signed**, because an
unsigned row has no date to be malformed. The 233 rows that passed and would
have been written into `eval/gold/` were exactly the ones nobody had approved.

The general shape is worth carrying into any future gate: **a validation rule on
a field that only appears on approved records fails closed for the approved ones
and open for the rest.** If a check can only fire on the rows you want, satisfy
yourself that failing it does not admit the rows you do not. Fixed in ADR-0047;
the read side now converts what it can read exactly and refuses what it cannot.

Two smaller facts from the same file, both live traps:

- **`openpyxl` returns a `datetime`, not a string, from a date-formatted cell.**
  `str()` on it gives `2026-08-25 00:00:00`, which passes a "is it text" check
  and fails every date pattern. Convert before stringifying, not after.
- **Excel writes a date under the typist's locale.** The same keystrokes give a
  different stored value in a different Windows region setting. That is why the
  column is formatted `yyyy-mm-dd` in the generated workbook — so the ambiguity
  is resolved by Excel, at typing time, rather than guessed at here.

### Q-27 — Approval does not distribute over an interlinked record set

*Found S008, measured against the first round.*

108 of 368 seed records were approvable row by row. 18 of those could not be
written anyway, because they named records that were not approved:
`prohibited_use.related_questions` pointing at unsigned retrieval questions, and
then retrieval questions pointing back at the prohibitions that had just been
held. The cascade needs a fixed point, not one pass.

This is not a defect in anyone's review. It is a property of a gold set whose
record types reference each other: a reviewer signs records, and what
`eval/gold/` needs is a **closed set**. Expect a partial round to yield fewer
records than its verdict count suggests, and expect the shortfall to be
concentrated in the record types that point outward most —
`prohibited_use` (`related_questions`), `gold_retrieval_question`
(`prohibited_conclusions`), `reasoning_expectation` (`must_not_infer`).

The practical consequence for planning: **ask for review in closed clusters, not
in sheet order.** Signing `GA-0001`–`GA-0018` releases 18 already-signed records
that are currently held, which is a better hour than reviewing 18 new ones.

### Q-28 — The seed set reads Part 29 and only Part 29, and the expert says that is too narrow

*Reported by the reviewing expert, S008. Not yet acted on.*

The seed concepts and entities were drawn from the s 43 citing chunks, which are
overwhelmingly `TMM/Part29/*`. The expert's covering note
(`review/returned/260826-expert-feedback.md`) names the consequence: roles and
office terms are defined *as Part 29 uses them*, which is "not wrong" but gives
"a limited view on what some of the roles are". They name nine that need
high-level definitions instead — Registrar, Delegate, Examiner, Decision Maker,
Office Practise, Subject Matter Expert (SME), Oppositions, Grounds for
Rejection, Adverse Report — and say there are likely more.

Two row-level corrections in the same round say the same thing sharply:
`GE-0010` and `GE-0047` both amend the machine's treatment of *decision maker*
and *the Registrar*, and the expert's words are "The registrar and the decision
maker are different entities. The decision maker (examiner) operates using
delegated authority from the registrar but they are not the same."

The trap for a later session: **ADR-0022's scope rule selects passages that
*cite* s 43, and a term's definition is usually not in a passage that cites
anything.** A vocabulary built only from the pilot's citing set will be
internally consistent and externally wrong. Whether the fix is a scope
exception, a separate definitional pass, or a Part-2 glossary import is Q17 in
`HANDOFF.md` and needs the expert, not an agent.

---

### Q-29 — `pytest` on `PATH` in the agent container is not the project's pytest

Symptom, on a container that has just run `pip install -e ".[test,intake]"`
successfully:

```
tests/unit/test_harness.py:25: in <module>
    import yaml
E   ModuleNotFoundError: No module named 'yaml'
E   ModuleNotFoundError: No module named 'tm_knowledge'
```

Nine collection errors, and every one of them names a package that is plainly
installed. `tmk-harness` runs fine in the same shell.

The cause is not the project:

```
$ which pytest
/root/.local/bin/pytest
$ head -1 $(which pytest)
#!/root/.local/share/uv/tools/pytest/bin/python
```

The image ships a `uv tool install pytest`, and its shim sits ahead of the
environment `pip` installed into. That pytest runs against its own isolated
interpreter, which has neither `tm_knowledge` nor `PyYAML` in it.

**Run `python3 -m pytest -q`**, which uses the interpreter that owns the
install. `pip install pytest` does not fix it — the shim still wins on `PATH`.
Worth knowing before spending twenty minutes on an installation that was never
broken: a `ModuleNotFoundError` for a package you can `import` in `python3` is
an interpreter mismatch, not a packaging fault.

`README.md` and the docs say `pytest -q` because that is what a normal checkout
runs. On a container, prefix it.

---

### Q-30 — The seed set contains genuine reference cycles

`GA-0002` names `PU-0013` in `prohibited_conclusions`; `PU-0013` names `GA-0002`
back in `related_questions`. Same for `GA-0002` ↔ `PU-0014`, and `GA-0016` ↔
`PU-0016`. These are not errors — a retrieval question naming the prohibition it
must not conclude, and a prohibition naming the question it arises on, is the
shape the schemas ask for.

The consequence is that **any walk over `CROSS_REFERENCES` must be cycle-safe.**
A plain recursive "what does this hold" over the real data does not terminate.
`transcribe.close_over_cross_references` is safe because it iterates to a fixed
point rather than recursing; `blockers._closure` is safe because it accumulates
into a visited set. A third one written naively will hang, and it will hang on
real content rather than on a fixture, so it will pass its tests first.

A second consequence, subtler: **a record in a cycle cannot be released by
anything outside the cycle.** `GA-0002`, `PU-0013` and `PU-0014` are held only by
each other, and the amendment on `GA-0002` releases all three. Anything that
looks for an "unblocked root" to start from will find none and report the
largest chain on the queue as unreachable (ADR-0054).

---

### Q-31 — In a review dependency graph, a rejected record is a sink, not a source

When inverting "who is waiting on whom" over review state, the temptation is to
treat every unsatisfied pointer as an edge. That produces a report saying
`GA-0016` *holds* `PU-0016` — because `PU-0016` names `GA-0016` and `PU-0016` is
not in `eval/gold/`.

It is exactly backwards. `PU-0016` was **rejected**; it is finished, negatively,
and it is in `review/seed/` only so the rejection and the reviewer's reason
survive (ADR-0049). It is not waiting for anything and nothing releases it. What
is true is the reverse: the rejection is why `GA-0016` has to change.

So: a record whose verdict is `reject` contributes no outgoing edges. It still
receives them — the records that name it are exactly the ones that need a
decision, and they are the point of the report. Getting this wrong does not
crash anything; it inverts the direction of every chain that touches a rejected
record, and the resulting table looks entirely plausible.

---

## F. Found by building the RDF layer (S010)

### Q-32 — An upstream ref cannot be a prefixed name in SPARQL or Turtle

`tmkr:TMM/Part29/1#1` does not work and does not fail loudly. A SPARQL prefixed
local name may not contain `/`, and `#` starts a comment in Turtle and a
fragment in an IRI. rdflib parses `tmkr:TMA1995\/s43` without complaint, warns
once on stderr that the result "does not look like a valid URI", and then matches
nothing — so the query returns zero rows and reads as a fact about the data.

Every ref-addressed node in a `.rq` file or a fixture is therefore written as a
full IRI:

```sparql
<https://data.ipaustralia.gov.au/tmk/ref/TMM/Part29/1%231>
```

with `#` percent-encoded exactly as `refs.to_iri` encodes it (ADR-0023). That
puts the base IRI into every query file, which is why `ask.py` rewrites it when
`TMK_BASE_IRI` differs — the base still lives in one constant.

**The symptom to recognise:** a query you are confident about returning `(no
rows)`. Check for a `\/` in a prefixed name before you doubt the data.

### Q-33 — `sh:severity` on a SPARQL constraint is ignored; it belongs on the shape

Written inside the `sh:sparql [ … ]` block, `sh:severity sh:Info` has no effect
and every result comes back as `sh:Violation`. Severity is a property of the
*shape*, and the shape is the node the constraint hangs off.

This turned a deliberately informational check — a concept whose not-label is
another concept's preferred label, which is what a not-label is *for* — into 29
build-breaking defects. The fix is one line moved up a level. The reason it
matters is that the obvious response to 29 spurious defects is to delete the
constraint.

### Q-34 — A SHACL property violation names a blank node as its source shape

`sh:sourceShape` on a property-constraint result is the **property shape**, and a
property shape is a blank node with no `rdfs:label`. A report built by looking up
the label of the source shape is a list of `n4ce10a23afba4c278f1435132c36e502b3`,
which tells a reviewer nothing.

`validate._label_for` walks up the `sh:property` (and `sh:sparql`) link to the
node shape that carries the name. Any future reporting over pySHACL results needs
the same walk.

### Q-35 — `sh:targetClass` needs the class hierarchy in the data graph

SHACL target selection follows `rdfs:subClassOf`, but only over triples the
validator can see. A fixture asserting `:x a tmk:Chunk` is invisible to a shape
targeting `tmk:Passage` unless the TBox is loaded alongside it.

The trap is that the fixture then **passes**, for a reason that has nothing to do
with the constraint — which is precisely the "reads as coverage" failure
`shapes/README.md` warns about, arriving through the test rather than through the
shape. `tests/unit/test_shapes_fire.py::check` loads the TBox with every fixture,
as the real gate does.

### Q-36 — `sh:hasValue false` fires on absence as well as on `true`

`sh:hasValue` requires at least one matching value, so a node with **no** value
for the path violates it. A staleness constraint written as
`sh:path tmk:isStale ; sh:hasValue false` therefore reports "this passage has
moved" about an assertion whose staleness was never checked — two different
findings under one message, and the wrong one on the more common case.

Split them: `sh:not [ sh:hasValue true ]` for "not stale", and a separate
`sh:minCount 1` for "staleness was actually checked". An assertion the build
could not check is *unknown*, and reporting it as stale is as wrong as reporting
it as fresh.

### Q-37 — `deceptively similar` is both a not-label and an expected concept

`GC-0002` records `deceptively similar` as a **not-label** — it belongs to
section 44, and a retrieval system treating it as a synonym of *likely to deceive
or cause confusion* routes an examiner to the wrong test (GX-0005). `CQ-0007`
lists the same string in `expected_concepts`.

So a competency question names a concept the vocabulary deliberately excludes.
Both records are approved and neither is obviously wrong: the question may be
using the term as a boundary marker ("the answer must say this is *not* it"), or
the vocabulary may need the s 44 concept — which the pilot scope draft puts out
of scope. **Do not resolve this by adding the concept, and do not resolve it by
editing the question.** It is an expert's call; `tmk-ontology-report` §5 names it
alongside three other unmatched labels (`purchasing decision`, `obvious, direct
and immediate`, `superseded legislation`).

### Q-38 — `tmk-recon`'s counts are s 43-scoped; the graph's are not, and both are right

Two pairs of numbers that look like they should match and do not:

| | recon | graph |
|---|---:|---:|
| ambiguous citation edges | 2 | 42 |
| refs resolving to nothing | 17 | 35 |

Neither is wrong. `tmk-recon` §5 counts ambiguous edges **to s 43**, because the
report is about that provision. The graph holds every citation on all 216
in-scope chunks, so it also carries ambiguous edges to s 15, s 42 and s 83. And
recon §4 counts unresolved refs in the **held instruments** only (`TMA1995`,
`TMR1995` — the loader's `HELD_INSTRUMENTS`), because a citation to the Acts
Interpretation Act is not a coverage failure; the graph's 35 additionally
includes the 1905 and 1955 Acts, the *Plant Breeder's Rights Act* and the
Designs Regulations, which are unresolvable by construction.

Restrict to the same scope and they agree exactly — `CQ-0020` returns 17 rows
for `TMA1995`/`TMR1995`. Before asserting one figure against the other, check
which scope each was computed over; `test_ambiguous_edges_are_not_resolved`
carries the working.

### Q-39 — The ADR metadata line is not fixed-width: the authority can carry a qualifier

`docs/DECISIONS.md` entries carry
`**Date** … · **Authority** … · **Status** …`, and a parser that reads the
authority as "everything up to the next `·`" works on 60 of the 61 entries and
fails on ADR-0011, which reads `**Authority** agent-proposed (field list)`. The
qualifier is legitimate — it says which *part* of the decision is provisional —
and it will happen again.

`dashboard/sources.py` reads the authority as the leading `[a-z-]+` and lets the
rest fall into the status prose. It also **raises** on an ADR with no metadata
line rather than skipping it: the dashboard's decisions page is generated from
these headings, and a reformat that quietly emptied the page would be worse than
one that broke the build.

### Q-40 — "How many classes hold nothing" has two right answers

`data/derived/reports/ontology.md` says 30 declared classes are unpopulated; the
dashboard says 39. Both are correct and they measure different things. The report
counts over the whole built dataset, which includes the source graph and
therefore populates `Chunk`, `Page`, `Citation`, `JudicialDecision` and the rest.
The dashboard reads committed artefacts only (ADR-0063), so it counts over
`graph/approved.ttl` alone.

Neither is the number to quote without its scope. The site labels its column
*approved instances* and says so in the note under the table; before asserting
one figure against the other, check which graph it was computed over. Same shape
as Q-38.

### Q-41 — The dashboard will not run from `file://`

Opening `site/index.html` by double-clicking it gives a page that renders its
chrome and then reports that the data is missing. The site fetches
`data/*.json`, and browsers block `fetch` on `file://` origins. It is not a
broken build: `python3 -m http.server -d site 8000` and the same files work.

### Q-42 — `tmk-ruling` needed the `[rdf]` extra it never used, and that cost a submission

`dashboard/cli.py` imported `dashboard.build` at module scope. `build` imports
rdflib — the optional `[rdf]` extra — and `tmk-ruling` does not use `build` at
all, so the transcription command carried a dependency on nothing it touched.
`.github/workflows/ruling.yml` installs `pip install -e .`, the core three
dependencies. On 2026-09-08 the owner's first submission (issue #12) died on
`ModuleNotFoundError: No module named 'rdflib'` before a line of transcription
ran.

**Invisible on any developer machine**, because every developer machine has the
extras installed — the repo's own quickstart says
`pip install -e ".[test,intake,rdf]"`. Fixed by moving the import into the one
function that uses it, and guarded by
`test_the_transcription_path_does_not_need_the_rdf_extra`, which blocks the
extras and imports the CLI.

Generalises: **an optional extra is only optional if something checks.** Before
adding a module-scope import to a package whose commands have different
dependency footprints, check which commands you have just made heavier.

### Q-43 — A dashboard answer with a note and no option chosen used to vanish

The form lets you type a note without picking an option, writes that answer into
the machine-readable block, and counts it in the issue title. Both the prose
summary the form composes and `ruling.transcribe()` skipped it. So issue #12 was
titled "7 answers", listed six, and would have transcribed six.

The one that vanished was OQ-0009, whose note is the substantive part of the
whole submission: *"In scope, use the queryable DB listed in this repo … Extract
the relevant rulings and store them."* An answer with no option and a long note
is not an edge case — it is what someone does when none of the options fit and
they have something to say.

Both sides now keep it, labelled *no option chosen — the answer is in the note*.
An answer with neither an option nor a note is still dropped, because that is a
scrolled-past question.

### Q-44 — A rule's triple count is not its finding count, and the questions quoted the wrong one

`data/derived/reports/ontology.md` had a column headed *triples produced*: 71 for
RULE-0001, 2,244 for RULE-0002. Those numbers went into
`review/questions/open-questions.yaml` as *"It produced 71 flags"* and
*"It produced 2,244 of them"*.

RULE-0001 flags **5 passages**. RULE-0002 draws **187 links**. Every conclusion
carries eight to fourteen triples of provenance, so the two counts differ by more
than an order of magnitude, and neither looks obviously wrong beside the other.

The owner was asked to review 71 flagged passages that do not exist, and approved
a rule believing it drew twelve times as many links as it does. `apply_rules` now
returns a `Yield` with `assertions` and `triples` under names that cannot be
swapped, and a test fails if a rule's triple count sits next to *flags*, *links*
or *passages* in the question file.

The trap is not arithmetic. **A number crossed from a context where it was
correctly labelled into one where nothing labelled it.** When quoting a figure
out of a generated table into prose, carry the column heading with it.

### Q-45 — rdflib serialises Turtle sorted and N-Quads unsorted

Two builds of an identical dataset produce byte-identical `.ttl` files and
*different* `dataset.nq` files. rdflib's Turtle serialiser sorts; its N-Quads
serialiser emits in set-iteration order, which moves with `PYTHONHASHSEED` — so
the difference is invisible within one process and appears between two.

It cost nothing while `dataset.nq` was git-ignored. The moment ADR-0070
committed it, it meant a 5MB diff in the history on **every rebuild**, signifying
nothing, and would have made `tmk-graph --check` fail immediately after a
successful `--write`. Line order carries no meaning in N-Quads, so the file is
written sorted; `test_the_quads_file_is_sorted` checks the committed one.

Worth knowing before committing any other rdflib output: check reproducibility
across *processes*, not across calls.

### Q-46 — a count and the list under it can disagree, and only the list is read

The dashboard's decision form said **"10 waiting on you"**, and it was right: ten
questions carry `status: open`, `needs: owner`. Under that heading it then
rendered every question in the theme — answered, parked and open alike — in file
order, with the same chips and no state on the collapsed row. `OQ-0001` was
answered in issue #12 and sat first. Opening it said *"You answered this."*

The owner's reading was the obvious one: the number must be stale, so the
published site must be behind the branch. It was not. `pages` had run on the
merge commit and the deployed `data/inbox.json` matched the repository byte for
byte. **The build was correct, the count was correct, and the page was still
wrong** — which is why the first instinct was to go looking at the pipeline.

Two lessons worth more than the fix:

- A summary count and the list beneath it are two renderings of one fact, and
  nothing was checking they agreed. The count filtered on state; the list did
  not filter at all.
- A stale-looking page is not evidence of a stale build. Check what the site is
  actually serving — `curl <site>/data/<page>.json` against the committed file —
  before touching the workflow. The footer's *"Generated …"* stamp answers the
  same question in one glance.

The theme blurb had the same shape of error in prose: *"Six things nothing can
move past"*, hand-written when there were six, still saying it when five were
answered. Counts belong in the renderer, which cannot go stale.

### Q-47 — an unquoted `#` in YAML eats the rest of the line

`how: You typed the answer into issue #12 by hand, outside the form.` loads as
`You typed the answer into issue`. A `#` preceded by whitespace opens a comment
anywhere in a plain scalar, so the sentence lost its second half silently — no
error, valid YAML, schema satisfied because the truncated string still cleared
`minLength`.

It was caught only because the generated JSON was read back after writing. Quote
any scalar containing `#`, and be aware that issue and pull request references
(`#12`) are the common way this arrives in a repository's own prose.

### Q-48 — an authored record cannot be validated while it is still wearing its envelope

Every record-type schema in `eval/schemas/` is `additionalProperties: false`. An
authored record carries its provenance under `authored:`, on the record. Validate
it as it sits on disk and every single record fails with

```
GC-0901 at <root>: Additional properties are not allowed ('authored' was unexpected)
```

which is a true statement about the wrong problem, and one that would send a
session looking for a malformed record rather than a validation order. The
envelope is split off the record on read — `store.load` does it once, in
`_split`, and everything downstream sees a record its own schema recognises.

The temptation on meeting that error is to relax `additionalProperties` on the
record schemas. Don't: the strictness is what catches a misspelt field name in a
gold record, which is the more common and more expensive failure.

### Q-49 — the graph's `origin` stamp is not redundant with the named graph

It looks redundant. `graph/authored.ttl` is the authored graph; why does every
node in it also say `tmk:origin "authored"`?

Because the two answer different questions, and the second question is the one
that keeps being asked. A named graph tells you where a triple *lives*; the stamp
tells you what a triple *is* after it has been copied out — into a report, an
evidence pack, a model prompt, a flattened union for SHACL. SHACL is the concrete
case: pySHACL validates a single graph, so `validate._flatten` unions the three
named graphs before running, and at that moment the only thing distinguishing
signed from authored content is the stamp. `tmk:OriginConsistencyShape` is the
constraint that exists purely because flattening happens.

Adding 284 triples to `graph/approved.ttl` for this — one origin and one review
status per node that did not already carry them — is the price, and it is why the
approved graph grew from 2,946 to 3,230 triples in a session that authored
nothing.

### Q-50 — a counter that could not be wrong until there was something to count

`_apply_concept_types` skipped any record whose group was not one of the four
that map to an OWL class, which meant a `none_of_these` record was skipped
entirely — no typing node, no provenance, and no increment. The comment three
lines above it said the opposite: that such a concept *"is counted as sorted
rather than as waiting."*

Both stores held zero concept typings from S010 to S016, so the counter printed
`0` whichever behaviour was right, and the tests could not tell them apart
either. The first 52 authored typings made it print `45`.

The general shape is worth carrying: **a branch that only executes on data the
repository does not hold yet is untested by construction, and its comment is the
only specification it has.** Two others in this repo are in the same position
today — the transcription path for an authored record (nothing has ever come
back signed) and every count that splits by `authored_by` (there is one author).
Expect the first record of a new kind to find a bug of this shape, and read the
comments around the code it touches before trusting the numbers.

Fixed in ADR-0093. The same session found the report line beside it was wrong
too — `45 of 0 authored ones`, dividing typings of signed concepts by the count
of concepts a machine wrote, which is structurally zero.

### Q-51 — `rows()` loads the real store, and a test that lets it is testing the repo

`stage0.typing.rows()` takes both stores as arguments and loads the real ones
when they are omitted. `test_typing.py` had always passed a synthetic `GoldSet`
and omitted the authored one, which was harmless while `authored/` was empty and
started failing the moment it held a record for `GC-0001`.

The failure is the good case. The bad one is the test that keeps passing: a
suite that reads live repository content asserts what the repository happens to
hold on the day it runs, and it goes green again when somebody deletes the data.
Every test in that module now builds both stores explicitly.

Worth checking anywhere a helper defaults to `load()`. The pattern reads as
convenience and behaves as a hidden global.

### Q-52 — the first signed typing will make the harness go red, and that is the design

`tmk-typing` pre-fills the reviewer's workbook from `authored/concept-types.yaml`
and the row **keeps the authored record's id** (ADR-0092 consequence 4): one
`GT-0007` exists in the project and it moves between stores rather than being
minted twice.

So when the first typing comes back signed, `tmk-transcribe` writes `GT-0007`
into `eval/gold/concept-types.yaml` while `GT-0007` is still sitting in
`authored/`. The harness reports that as a defect naming both stores, and it is
right to: ADR-0080 consequence 2 says the signed record wins and the authored one
is **retired**, and nothing in the repository does the retiring yet.

Do not resolve it by minting a fresh id for the signed record — that leaves two
records about one concept and loses the link between the machine's answer and the
correction. Do not resolve it by deleting the authored record quietly either.
Build the retirement: it is named in `HANDOFF.md` §2 and it is where the next
real design question in this area lives.

### Q-53 — 63% of the Manual cites no provision, so no citation rule can reach it

`tmk-recon` over the whole corpus: **1,551 of the 2,460 chunks carry no
`provisions[]` edge at all.** Not a defect in upstream and not a gap in the
snapshot — most of the Manual explains practice without naming a section.

It is the mechanism behind Q-28, which noticed the symptom without naming the
cause. ADR-0022's rule selected passages that *cite* `TMA1995/s43`, so nearly two
thirds of the corpus was structurally invisible to it, and a term's definition
almost never sits in a passage that cites anything. That is why four of the nine
role terms the expert named — Delegate, Office Practise, Subject Matter Expert,
Adverse Report — were absent from a 52-concept vocabulary built with it.

**The trap for a future session:** any new selection rule keyed on provision
edges inherits the same blindness, however wide the provision list. The concept
candidate pass reads headings and definition text precisely so it does not
(ADR-0095), and `tmk-recon` prints this figure at the top of its report so
nobody has to rediscover it.

### Q-54 — the same counter has now been wrong in both directions

The build report's concept-types line has been fixed twice for opposite reasons.

ADR-0093 fixed it from `45 of 0`: it divided the authored half by
`authored.concepts`, the number of concepts a *machine* had written, which was
structurally 0 while machines wrote typings and not concepts. The fix was to
divide both halves by the signed concept count.

S018 fixed it from `130 of 52`: that denominator was right until a machine
authored concepts of its own. It now divides by the count across both stores and
prints the split beside it.

Q-50 already said to read a counter's comment before making it non-zero, and this
is the same lesson with the numerator and denominator swapped: **a denominator
that is correct today is correct because of something that is currently true.**
The comment on the line is its only specification, and it is now three times
longer than the line.

### Q-55 — `ScopeRule` is not a scope rule any more, and the name is kept anyway

`tm_knowledge.stage0.worksheet.ScopeRule` selects chunks citing a given
provision. Under ADR-0022 that was a boundary: everything outside it was out of
scope. The owner withdrew the boundary (ADR-0081), so what the class does now is
*select* — "print me the passages about section 41" — which is a working choice
and not a claim about scope.

The name was left alone deliberately. Renaming a class does not change what reads
it, and the two things that mattered were fixed instead: the worksheet header no
longer says the printed rows are the scope, and the graph stopped using the class
altogether (ADR-0097). If you meet `ScopeRule` and read "scope", read the module
docstring first.

`PILOT_PROVISION` is the same shape of leftover. It is `TMA1995/s43` and it is
now a *default argument*, not a boundary.

### Q-56 — one SPARQL block cost 409 seconds; two cost 0.3

`CQ-0007` ended with two triple patterns in a single `GRAPH tmkg:source` block,
each joining on a variable already bound in the block above it:

```sparql
  GRAPH tmkg:source {
    ?passage tmk:upstreamRef ?sourceRef .
    ?target  tmk:upstreamRef ?allocatedTo .
  }
```

rdflib evaluates that by building the cross product of every `tmk:upstreamRef`
triple in the source graph and *then* joining on `?passage` and `?target`. That
is quadratic in the size of the source graph. Split into two blocks over the same
graph, each pattern joins against the bound variable and the query goes from
**409 seconds to 0.3**. The two forms are semantically identical — `tmkg:source`
is a constant IRI, so `GRAPH g { A . B }` and `GRAPH g { A } GRAPH g { B }` are
the same join — and that was checked rather than argued: both forms were run
against the same dataset and compared row for row. The original took 418.0
seconds and returned the same two rows.

**It was already slow before anybody noticed.** At 216 chunks it took 103
seconds, and the test module ran it twice, so the suite had been spending three
and a half minutes on one query since S010. Growing the source graph to 508
chunks (ADR-0097) took it to 409 and made it impossible to ignore, which is the
only good thing about the regression.

**What to watch:** any competency query with two independent patterns in one
`GRAPH` block. `CQ-0023` looks similar and is not — its second pattern is inside
an `OPTIONAL` and chains off `?passage`, so there is nothing to cross-multiply.
A `pytest --durations=10` run is the cheapest way to find the next one.

### Q-57 — CQ-0017 stopped being complete, and it was only ever complete by accident

`CQ-0017` answers *"if section 43 were amended, which parts of the Manual would
need reviewing?"* by counting citation nodes in the source graph. Until
ADR-0097 it returned all 67 passages the corpus records as citing the provision,
and a test asserted equality with `tmk-recon`'s figure as a cross-check.

**That equality held because the source graph was fenced to exactly those
chunks.** The query was complete for section 43 and incomplete for every other
provision in the Act, and nothing said so. With the fence gone the graph holds
what the repository has spoken about, and the query returns 56 of the 67.

The test now checks the property it was really for — every held citing chunk
counted once, none counted that the corpus does not have — computed against the
loader rather than transcribed. The query's `limits:` header states the
shortfall and points at `tmk-recon --provision` for the corpus figure.

**The trap this leaves:** any other query that counts source-graph nodes is
answering "of what the graph holds", not "of what the corpus contains", and only
this one says so. Check the `limits:` header before quoting a coverage number
out of a competency query.

### Q-58 — `tmk:Role` and `tmk:ProcessRole` are different things and one letter of context apart

`examination.ttl` has declared `tmk:Role` since S003, with `tmk:Registrar`,
`tmk:Delegate`, `tmk:Examiner` and `tmk:DecisionMaker` under it. Those classes
are for **people and offices that act** — the examiner who signs a report. All
six are `UNDEFINED` and have been since they were written (HANDOFF Q17), so
nothing populates them and the collision stayed invisible.

ADR-0098 added `tmk:ProcessRole` for the **concept** of an office as the
vocabulary holds it, and `GC-0044` *examiner* is now an instance of it.

**They are not the same and must not be merged.** `tmk:ProcessRole` is a
subclass of `tmk:LegalConcept`, which is a `skos:Concept` — a term with a
preferred label, variants and near-misses. `tmk:Role` is a class of agents.
Making the concept record for "examiner" an `tmk:Role` would assert that a
vocabulary entry examines trade marks.

**The trap:** a query written to find "everything about examiners" reaches one
or the other depending on which class it names, and both look right. If
somebody eventually defines the `tmk:Role` subclasses, the two hierarchies will
carry the same four labels — Registrar, Delegate, Examiner, Decision maker — and
nothing in the labels will distinguish them. Read the `rdfs:comment` on either
class before writing a query that touches roles; both say which one they are.

### Q-59 — ten authored concepts reuse a signed concept's preferred label, and three of them say nothing about it

`authored/concepts.yaml` holds ten records whose `pref_label` is character-for-
character a signed concept's. Seven name the collision on their own record and
argue for standing beside the signed one. **Three do not mention it at all:**

| Authored | Signed | Term |
|---|---|---|
| `GC-0053` | `GC-0006` | ground for rejection |
| `GC-0100` | `GC-0014` | endorsement |
| `GC-0101` | `GC-0041` | evidence of use |

**Why nothing caught it.** The harness checks that an id is not in both stores
(ADR-0080 c1) and that an authored typing names a concept that exists
(ADR-0095 c4). Neither is an id collision — the ids are distinct and correct.
Nothing anywhere compares *labels* across the two stores, so the two records
coexist, both resolve, and a search on the term returns one signed answer and one
unreviewed answer with different sources.

**Do not resolve it by deleting or retitling either record, and do not reach for
ADR-0080 consequence 2 to do it.** That rule retires an authored record where a
signed one *covers the same ground* — which is precisely the question in doubt
here, since each pair cites different passages and reads differently. Answer the
question first, and it is not an agent's to answer: the signed record cannot be
narrowed by an agent deciding its author did not mean the other case. §2C of
`docs/EXPERT-REVIEW-SCOPE.md`, ADR-0101.

**The check that is missing** is a cross-store label comparison reported as a
note rather than a defect: a duplicate label is a finding for a person, not a
malformed record. Seven of the ten are the system working as designed.

### Q-60 — the one expert-facing document tells the expert to delete the deliverable

`eval/STAGE-0-INPUT-GUIDE.md` was written for the pre-2026-09-08 model and has
not been revised. Its §9 says that a record with `approved_by` unfilled and
content filled in is "CLAUDE.md rule 1 being broken, and the record should be
deleted rather than reviewed". Under ADR-0079 that description now matches every
one of the 208 records in `authored/` — which is the entire body of work a
reviewer would be handed.

Its opening likewise states that an agent cannot author a concept definition or
a prohibited use, and §2 and §10 make drawing the withdrawn section 43 boundary
the reader's first half-day.

**Fixed only by a banner so far** (S020): a dated amendment block at the top
naming the three stale parts and pointing at `docs/EXPERT-REVIEW-SCOPE.md`. The
document's record *shapes* (§5), workbook mechanics (§6), definition of done
(§7) and limits (§8) still hold — those are containers and the containers did
not change. A proper rewrite has not been done.

**The general trap:** ADR-0079 amended `CLAUDE.md` and `review/README.md` and
`authored/README.md`, all of which agents read every session. It did not reach
the document nobody in a session opens, because its audience is not in the
session. When an operating rule changes, grep for the *old rule's wording*
across the tree rather than for the files an agent happens to read.

### Q-61 — every defined term in the Act cites the same provision, so joining records on a shared basis joins the dictionary to itself

Upstream addresses a defined term as a provision with a second segment:
`TMA1995/s6/assignment`, `TMA1995/s6/registrar`, `TMR1995/r2.1/madrid-protocol`.
**25 of the 130 concepts carry at least one of these**, because a concept whose
name the Act defines records where it is defined.

Any rule that joins two records because their `legislative_basis` shares a
provision will therefore join, in one stroke, every concept the Act defines to
every other one. In S021's procedure spine that showed up as *assignment*,
*transmission* and *divisional application* each arriving with **eighteen
children**, none of which had anything to do with them: the join was section 6.

`views.ConceptView.joinable_sections` is the filter — `sections` minus every ref
with a second address segment — and a test pins it. The test is the **ref's
shape**, never its number: nothing in this repository asserts which provision of
which instrument holds the definitions, and a rule that hard-coded `s6` would be
the guess CLAUDE.md rule 6 forbids.

**The general trap:** `legislative_basis` answers two different questions at once
— *what provision does this concept operate under* and *where is this word
defined* — and only the first one joins. Anything new that reasons over that
field needs to decide which of the two it wants before it reads a ref.

### Q-62 — a spring layout that diverges looks like a rendering bug, not a maths bug

The map's force layout was first written with a spring coefficient of 0.6 and a
velocity damping of 0.7. On the 86-node island it looked cramped; on the 149-node
island it produced a **diagonal streak** with everything else scaled to a dot, and
the obvious readings were all wrong — the packing, the label rule, the viewBox.

It was none of those. The simulation was diverging: measured offline against the
real graph, the bounding box of the largest island came out **378,762 × 3,354,174
units** with a median edge length of 30,147. Every subsequent step — the
bounding-box fit, the packing, the label declutter — then did exactly what it was
told with numbers that had already exploded.

Two things made it slow to find. Divergence in a spring model is **silent**: no
error, no warning, nothing in the console; the maths runs and the picture just
looks odd. And a force layout is the kind of code where "it looks wrong" is the
normal state during tuning, so a genuine failure hides inside the ordinary
iteration.

**What to do instead:** tune the constants in a plain Node script against the
real payload and print the bounding box, the mean nearest-neighbour distance and
the median edge length. `3000 / 0.25 / 0.75` over 600 steps gives a roughly
square box and a median edge near 60, which is what the constants in
`site/network.js` are. If they are changed, measure the same three numbers before
looking at the picture.

---
### Q-63 — a block measures zero until the router has appended it, and a layout built on that silently overlaps

`site/blocks.js` builds a block into a **detached** element tree and the router
appends it afterwards. Anything inside a renderer that reads a real measurement —
`offsetHeight`, `offsetWidth`, `getBoundingClientRect()` — gets **0** at build
time, with no error and nothing in the console.

This bit the decision tree twice in one sitting, in two different disguises.

- The tidy layout stacks rows against each node's measured height. With every
  height reading 0, the code fell back to its guess of 56px, the boxes that
  needed 110 were laid 72 apart, and the picture came out as a tree **whose rows
  overlapped by exactly the amount the guess was wrong**. It looked like a
  spacing constant that needed nudging; no constant would have fixed it.
- The fit-to-frame call read a canvas of zero width, correctly declined to divide
  by it, and returned — having already set the *fitted* flag, so nothing ever
  fitted the canvas again.

**What to do instead:** in a renderer that measures anything, do the measuring
pass in a `requestAnimationFrame` after returning the block, and make the
"already done" flag record whether the measurement *succeeded* rather than
whether it was attempted. `site/tree.js` builds once for the DOM and once more on
the next frame for the real heights, which is the cheap and honest version.

---

### Q-64 — a record's source was resolved against the Manual only, and the legislation was invisible to it

`ontology.build._provenance` looked `source_ref` up in `corpus.chunks` and
nowhere else. Anything it could not find was reported as *"naming a source not
held"* — a statement about the corpus, and a false one.

It was correct for four months because it was never wrong: every record in the
project cited a Manual passage, because the vocabulary came out of Part 29 and
Part 29 is Manual text. The first records to cite the Act and the Regulations
as their *source* rather than as their object are the 46 `isDefinedIn`
relationships authored on 2026-09-12, and all 46 came back unresolvable on
their first build. The corpus holds every one of them — in `corpus.units` and
`corpus.provisions`, which the lookup did not consult.

**The trap is the shape of the failure, not the missing dict.** The check
reported a *finding about the data* when what had happened was a gap in the
code, and it reported it in the same words it uses for a genuinely dangling
ref. A session reading `authored records naming a source not held: 46` has
every reason to go and look at the records.

Fixed: chunks, then units, then provisions, and staleness comes from whichever
holds it (ADR-0111). **The lesson generalises to every other lookup in this
repo that assumes a ref is a Manual ref.** `refs.parse_ref` has always known
about four kinds; code downstream of it has mostly only ever seen one.

---

### Q-65 — a boundary removed from the rules survives in generated prose and in a hardcoded label

ADR-0081 withdrew the section 43 boundary on 2026-09-08. S018 removed it from
the artefacts — `tmk-boundary` deleted, the scope rule replaced, the sorting
sheet widened. Four days later three things still said section 43, and none of
them was a scope rule:

1. `evidence.ttl` explained its own emptiness with *"Part 22 is explicitly out
   of the pilot scope draft"* — a withdrawn fence, cited as a live reason, in a
   file nobody had cause to open.
2. `ontology.build.SCHEME_LABEL` was the string
   `"Section 43 examination vocabulary — pilot"`, asserted as `rdfs:label` and
   `skos:prefLabel` on the concept scheme — so **every one of the 130 concept
   nodes was `skos:inScheme` something that called itself a section 43 pilot**,
   in the committed graph, eleven days after the vocabulary reached 39 Parts.
3. `ontology/README.md` described the draft as *"nine OWL 2 RL modules over the
   section 43 pilot"*, which is the sentence that started this session.

**Why prose is the worst place for a withdrawn constraint to hide.** A scope
rule in code gets deleted because something imports it. A scope rule in an
`rdfs:comment` is read by a person, believed, and acted on — and the S018 pass
that swept the artefacts had no way to find it, because grepping for `s43` and
`Part29` finds identifiers, not paraphrases.

The IRI `tmkc:scheme-s43` was **kept**, and that is not an oversight:
`docs/IDENTIFIERS.md` §3 says labels get revised and identifiers must not.
Renaming it would rewrite every `skos:inScheme` triple in the committed graph to
track a label change, which is the practice the rule exists to prevent
(ADR-0111).

# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-08-30 · session S007 · branch `claude/workbook-next-phase-vcfmjx`

---

## 1. Where the project actually is

**The gold set has content.** The first workbook came back on 2026-08-25 and
was transcribed on 2026-08-30. `eval/gold/` now holds **105 expert-approved
records** — 19 competency questions, 52 concepts, 34 relationships — and
`tmk-harness` reports **0 defects** over them: every ref resolves, every span
lands on the text it names, every `source_content_hash` matches the pinned
snapshot. That is the first time the harness has had anything real to check,
and it passed. Gaps fell from 22 to 18.

**Stage 0 is not done.** Five deliverables are still empty (entities, search
questions, retrieval questions, reasoning expectations, prohibited uses), the
pilot scope and measures are still unwritten, and `tmk-harness` still exits 3.
Relationships are 34 of 50–100.

**Read the workbook before you read the counts.** What arrived is not the empty
form `tmk-workbook` produces. It is a **seed pack**: 368 machine-written example
records over s 43, generated outside this repo and handed to an examiner for
correction, on the reasoning that correcting a wrong answer is cheaper than
composing a right one. That is a sound use of expert time and it introduced the
hazard that shaped this session — **a filled-in seed pack cannot be told from an
authored workbook by inspecting it** (Q-24). Every row validates, resolves,
lands and hashes whether or not a person read it. Transcribing the file as if it
were authored would have moved all 368 rows into `eval/gold/` and reported
Stage 0 nearly complete; 165 of them carry no verdict at all.

So `verdict` is now a gate, not a note (**ADR-0043**). A row reaches
`eval/gold/` only if the expert marked it `correct` *and* signed it with
`approved_by` and `approved_date`. The other 263 rows are in
`review/decisions/`, each with its verdict, the reason it was held, the
correction verbatim and the whole record — rejections included, because
`review/README.md` is right that they are as valuable as approvals.

Where the 368 rows went:

| Record type | approved | unread | reviewed, unsigned | amend | reject |
|---|---|---|---|---|---|
| competency questions | **19** | 2 | 1 | 1 | 1 |
| concepts | **52** | 0 | 0 | 0 | 0 |
| relationships | **34** | 20 | 0 | 3 | 0 |
| entities | 0 | 92 | 53 | 2 | 5 |
| retrieval questions | 0 | 0 | 20 | 2 | 0 |
| search questions | 0 | 22 | 4 | 0 | 0 |
| prohibited uses | 0 | 0 | 16 | 0 | 2 |
| reasoning expectations | 0 | 15 | 0 | 0 | 0 |
| **total** | **105** | **151** | **94** | **8** | **8** |

## 2. The next action

**Thread B — the expert, and there is one cheap win sitting in the table
above.** 94 rows are already marked `correct` and are held only because nobody
signed them. They need a name and a date, not a re-reading. Signing them alone
would take retrieval questions from 0 to 20 (in band), prohibited uses from 0 to
16 (in band, if the six kinds are spanned), and entities from 0 to 53. **Ask
first whether those 94 were reviewed and left unsigned, or never reviewed at
all** — the answer decides whether this is ten minutes of work or a fortnight,
and the file cannot say which.

Then, in the order they cost:

1. **Sign or re-review the 94.** As above. Ask before assuming.
2. **The 8 corrections** — printed by `tmk-transcribe` under "CORRECTIONS TO
   APPLY". They are prose and are deliberately not applied (**ADR-0044**); they
   come back as a verdict on a corrected row.
3. **Two flagged rows** need a person: `GE-0053` is marked `correct` with the
   correction "duplicate" — the two cells disagree; `GR-0017` has an
   `approved_date` and no `approved_by`.
4. **Two unreadable verdicts**: `corrrect` (entities row 32) and `rejext`
   (`GS--relevant` row 24). Not repaired, by **ADR-0045**.
5. **The 151 unread rows**, of which 92 are entities — the largest single
   deliverable and the one furthest from its 100–300 target.
6. **Q8, the pilot scope boundary**, still unanswered and still blocking
   `eval/pilot-scope.md`.

**Thread C — agents. Still maintenance.** The loop now works end to end:

```bash
tmk-transcribe data/intake/<new-workbook>.xlsx          # dry run; read the held list
tmk-transcribe data/intake/<new-workbook>.xlsx --write  # gold + review/decisions/
tmk-harness && tmk-coverage
```

Put each received workbook in `data/intake/` unaltered (**ADR-0046**) and never
edit one. Do **not** hand-write into `eval/gold/`: approval enters through a
workbook so that every approved record has a signed row behind it.

**Do not** start Stage 2 (ADR-0010) — the gold set now has 105 records and a
clean harness, which makes "just run YAKE to see" more tempting than it has
ever been. It is still measuring against a set that is a third built and
entirely unbounded on recall: entities, the deliverable recall is computed
from, stands at zero.

## 3. Open questions — need a human

| # | Question | Blocks | Raised |
|---|---|---|---|
| ~~Q1~~ | ~~What is the pilot scope?~~ **Answered S002: s 43** (ADR-0013). The *boundary* is deliverable 1 — see Q8. | — | S001 |
| Q8 | What is the s 43 **boundary**? Which Manual Parts/chunks, which neighbouring provisions, is GI the centre of gravity or a sub-topic, are point-in-time questions in scope? Prompted for in `eval/STAGE-0-INPUT-GUIDE.md` §2. **Answerable against numbers** — `tmk-recon` reports where the citing chunks sit and what each candidate rule costs. | All remaining Stage 0 **content**. Does not block the worksheet — ADR-0017, ADR-0022 | S002 |
| ~~Q2~~ | ~~How does this repo get the upstream snapshot?~~ **Answered S003, built S004** (ADR-0004, ADR-0021, ADR-0026). | — | S001 |
| Q3 | Which LLM is "agency-approved" for the Stage 2–4 extraction steps, and under what data-handling conditions may Manual text be sent to it? | Stages 2, 3, 4 | S001 |
| Q4 | ~~What does "approved" look like as a recorded artefact?~~ **Answered S006: the workbook's `approved_by`/`approved_date` columns are the artefact** — a name and a date, no separate signed-off file or external register (ADR-0039). **Still open: who are the approving experts?** — expected to arrive with the experts' own content. | Nothing structural; who-question blocks nothing today | S001 |
| ~~Q5~~ | ~~Does ADR-0005 hold?~~ **Answered S003: yes** (ADR-0021). | — | S001 |
| Q6 | Case law is cited by the corpus but is not held as documents anywhere. Is acquiring decision texts in scope for this repo? **Costed for the pilot:** 58 distinct decisions are cited from the 216 in-scope chunks. The harness reports a case ref as a NOTE — checked for grammar, resolvable by nothing (Q-11). | Stage 2 citation resolution, Stage 8 retrieval | S001 |
| Q7 | What base IRI may the project mint under? `docs/IDENTIFIERS.md` proposes `https://data.ipaustralia.gov.au/tmk/`; persistent IRIs need control of that domain, which is an organisational call. Still not blocking: one constant in `config.py`, overridable by `TMK_BASE_IRI`. | RDF serialisation only | S001 |
| ~~Q9~~ | ~~Does the owner accept **ADR-0016** and **ADR-0018**?~~ **Answered S006: yes, both** (ADR-0038). | — | S003 |
| ~~Q11~~ | ~~Five S004 ADRs are agent-proposed: 0024, 0026, 0027, 0028, 0029.~~ **Answered S006, in part:** 0024, 0026, 0027 confirmed (ADR-0040); 0028 reversed, not confirmed (ADR-0042, `data/derived/` is now committed). **0029 still open** — owner had no context for it ("I have no idea what this means"); it needs none, since it already reflects current practice and nothing hinges on ruling it either way. | Nothing | S004 |
| Q12 | Six S005 ADRs are agent-proposed: **0030** (three severities, three exit codes), **0032** (one named gold file per record type), **0033** (the retired-id ledger), **0035** (`openpyxl` as an optional extra — *the only one that is a dependency decision*), **0036** (the workbook's cell encoding), **0037** (how transcription writes). ADR-0031 and ADR-0034 are `derived`. Owner has seen a plain summary of these (S006) but has not yet ruled on them. | Nothing | S005 |
| ~~Q13~~ | ~~Does upstream need a token in CI?~~ **Answered S006: no.** `manual-XtrACTor` is public (QUIRKS Q-13, amended S004) and GitHub Actions clones public repos anonymously, so `tmk-fetch-upstream` works in CI with `UPSTREAM_TOKEN` unset. Leave the secret unset unless the repo's visibility changes. | — | S005 |
| Q15 | **New, S007. The most consequential open question in this table.** Were the 94 rows marked `correct` but unsigned actually *reviewed* and left unsigned, or never reached? The file cannot say, and the answer changes the remaining Stage 0 effort by an order of magnitude. Related and larger: **should the seed-pack method continue at all?** It produced 105 sound records fast, and it means the expert is correcting the system's own output rather than annotating independently — which is cheaper, and which biases the gold set toward what the generator already believed. Recall in particular cannot be measured against a set the generator wrote. | The size and the soundness of the remaining Stage 0 work | S007 |
| Q16 | **New, S007.** Should the next pack carry a **structured correction column** — a `corrected_value` the expert fills in as a value — beside the free-text one? Eight corrections came back this round and several were near-machine-appliable (three name a `modality`, thirteen `GS--relevant` ones open with the corrected grade), but ADR-0044 refuses to parse prose. A typed column would collect them as data without anyone reading an expert's sentence. Not built; it is a change to a generator that does not live in this repo. | Nothing today; it would cut a round trip | S007 |
| Q14 | **New, S006.** Owner asked for more plain-language guidance on **constructing the ontology**, beyond what `STAGE-0-INPUT-GUIDE.md` covers (which is scoped to Stage 0 elicitation, not Stage 5 ontology formalisation). Not scoped or drafted yet — needs its own session: who is the audience (the Trade Mark experts already working from the input guide, or a wider group?), and what specifically is unclear in the existing docs. | Nothing yet; would help the experts' ongoing work | S006 |

Agent-proposed ADRs awaiting human confirmation: **0011** (deferred, not
declined — see ADR-0041), **0029, 0030, 0032, 0033, 0035, 0036, 0037**.
S007's four (**0043, 0044, 0045, 0046**) are `derived`, not agent-proposed —
each is forced by rule 4, rule 1 or rule 6 applied to the artefact that
arrived — so none is waiting on a confirmation. What *is* waiting is Q15: not
whether the gate is right, but whether the seed-pack method that made it
necessary should continue.
(0006, 0012, 0014, 0024, 0026, 0027 confirmed S006 — ADR-0040; 0016 and 0018
confirmed S006 — ADR-0038; 0028 superseded S006 — ADR-0042. ADR-0023,
ADR-0025, ADR-0031 and ADR-0034 are `derived`.)

**No agent work is blocked on a human decision.** Every remaining open question
is expert content (Q8), organisational (Q3, Q7, the who-half of Q4), scope for
later (Q6, Q14), or a confirmation that changes nothing structural (Q12, and
0029/0030/0032/0033/0035/0036/0037 within it).

## 4. Do not redo these

- **Do not re-parse the Manual HTML or the legislation `.docx`.** ADR-0002.
- **Do not design a new identifier scheme.** ADR-0005, and `refs.py` implements
  it. Argue with the ADR, don't invent a third.
- **Do not write a second ref parser, IRI minter, snapshot reader, gold-set
  reader or workbook layout.** There is exactly one of each, and the whole point
  of `stage0/intake.py` is that the workbook's columns exist in one place.
- **Do not "fix" a ref that fails validation.** `InvalidRef` means the ref was
  constructed rather than read. Find the construction.
- **Do not commit anything under `data/upstream/`** (ADR-0004) — that would
  vendor another repo's corpus into this one's history. `data/derived/` is the
  opposite as of S006: it **is** committed, on purpose, as a paper trail
  (ADR-0042, supersedes ADR-0028). Regenerate and commit the diff; don't
  hand-edit what's on disk.
- **Do not put an example row in the intake workbook.** Not even a marked one.
  In a spreadsheet, copying a row is one keystroke. This is why `tmk-workbook`
  emits no `verdict` column either, though the transcriber reads one: a
  generator that shipped a verdict column would be asking an expert to review a
  blank form (ADR-0043).
- **Do not transcribe a seed pack as though it were authored.** The rows are
  machine-written and look exactly like expert content once filled in (Q-24).
  Establish where a workbook's rows came from before running `--write`.
- **Do not apply a correction, however machine-appliable it looks.** ADR-0044.
  Thirteen of them open with the corrected grade and it is still prose.
- **Do not edit a file in `data/intake/`.** ADR-0046. It is evidence of what a
  person sent, including their typos.
- **Do not fill a judgement field to make a check pass.** Null is a reportable
  gap; a plausible value is a lie the harness will then certify.
- **Do not make `pytest` fail to satisfy "the suite must fail".** That is
  `tmk-harness`'s job, and collapsing them hides every future regression (Q-23).
- **Do not build a vector store or search index yet.** Stage 7 is five stages
  away and untestable without Stage 0.
- **Do not add LegalRuleML.** ADR-0009.

## 5. Session log

Newest first. One short entry per session: what changed, what it cost, what it
revealed. Keep entries to a few lines — detail belongs in ADRs and QUIRKS.

### S007 — 2026-08-30 — the first workbook came back; the gold set has content

The expert returned the s 43 pack and the return leg could not read it: five
columns the schemas do not describe (`seed_id`, `why_this_example`, `passage`,
`verdict`, `correction`), so `tmk-transcribe` refused every sheet.

Teaching it those columns was the small half. The large half was noticing what
the file *is*. It is a seed pack — 368 machine-written records handed out for
correction — and a filled-in seed pack is indistinguishable from an authored
one by every check this repo has: the records validate, the refs resolve, the
spans land, the hashes match (Q-24). Reading it as authored would have put 368
rows of LLM output into the standard every later stage is scored against, and
the harness would have said 0 defects, because form is the one thing a model
reliably gets right. 165 of those rows carry no verdict at all.

So the verdict column became a gate (ADR-0043): `correct` **and** signed, or it
goes to `review/decisions/` with its reason and its whole record. 105 rows
cleared it. The harness reports 0 defects over them — the first real check it
has ever run — and gaps fell 22 to 18. Competency questions and concepts are
both in band; relationships are 34 of 50.

Three refusals were judgement calls and each has an ADR. Corrections are not
applied (ADR-0044) even where they are nearly machine-appliable — three name a
`modality` outright and thirteen open with the corrected grade — because
reading an expert's sentence as a field value is a legal reading made by
whoever writes the parser. Unreadable verdicts are not repaired (ADR-0045):
`corrrect` and `rejext` are unmistakable and are still reported, because
otherwise a verdict in `review/` is not necessarily one a person gave. The same
line put `25/08/2026` through (the day is past the twelfth, the reading is
forced) and would refuse `05/08/2026`.

Received workbooks now live in `data/intake/`, tracked and never edited
(ADR-0046) — `data/derived/` must stay rebuildable and a filled-in workbook is
rebuildable from nothing, and without the file in git the audit trail points at
somebody's downloads folder.

266 tests pass, 47 of them new; `tmk-harness` exits 3, correctly. No legal
content authored, no correction applied, nothing promoted that a person had not
signed. The sharpest thing found is not in the code: **94 rows are marked
`correct` and unsigned**, and nobody can tell from the file whether they were
reviewed. That is Q15, and it is worth asking before anything else.

### S006 — 2026-08-19 — closed Q13, Q9, Q4's format-half and 6 more ADRs; reversed ADR-0028

Owner asked what could be unblocked before the experts report back. Closed
**Q13**: `manual-XtrACTor` is public (already established in QUIRKS Q-13,
S004) and GitHub Actions clones public repos anonymously, so no CI secret is
needed — the open question was stale, not open, nothing needed asking.

Put the genuinely organisational questions (Q4, Q7, Q9, Q11/Q12) to the owner
directly rather than guessing at them, and recorded the answers:

- **Q9** closed outright — owner confirmed **ADR-0016** and **ADR-0018**
  (ADR-0038). Both were already load-bearing; this only lifts the provisional
  flag.
- **Q4** half-closed — the approval artefact **is** the workbook's
  `approved_by`/`approved_date` columns, no separate file or register
  (ADR-0039). *Who* the approving experts are is still open and expected to
  arrive with the experts' own content.
- **Q7** (base IRI) — owner not ready to decide; left open, no action taken.
- **Q11/Q12** — owner asked for a plain summary rather than a yes/no;
  provided one in chat, then the owner ruled on eight of them directly:
  **confirmed** ADR-0006, ADR-0012, ADR-0014, ADR-0024, ADR-0026, ADR-0027
  (ADR-0040, with two live triggers worth remembering — ADR-0026 invites a
  better upstream-pinning proposal if one exists, ADR-0027 may tighten if a
  CI/CD gating policy is ever added); **deferred** ADR-0011's provenance field
  list until Stage 2's actual output shape is known (ADR-0041); **reversed**
  ADR-0028 outright — the owner wants `data/derived/` **committed** as a paper
  trail, not git-ignored (ADR-0042). ADR-0029 stays open; the owner had no
  context for it and none is needed — it already reflects current practice.

Acted on ADR-0042 immediately rather than leaving it as a paper decision:
updated `.gitignore`, `data/README.md`, `cli.py`'s docstring and this file's
§4, then ran the full pipeline for the first time this session
(`pip install -e ".[test,intake]"`, `tmk-fetch-upstream` — snapshot at
`c490a9927f1a` — `tmk-recon`, `tmk-worksheet`, `tmk-coverage`, `tmk-workbook`)
and committed the output: the s 43 worksheet, the recon report, the coverage
report (0 defects, 22 gaps) and the empty intake workbook are now in git.
219 tests pass; the harness is sound and exits 3, exactly as designed.

The owner also asked (via ADR-0014) for more plain-language guidance on
**constructing the ontology**, beyond the existing input guide. Not drafted
this session — logged under §3 as a new open item needing its own scoping
pass, not squeezed in alongside eight other decisions. And noted: a work
order referencing `STAGE-0-INPUT-GUIDE.md` has already gone to the Trade Mark
experts, so that guide is now live reference material, not a draft.

No legal content authored.

### S005 — 2026-08-19 — the last five packages; the track is exhausted

Built P5, P7, P8, P10 and P11. The repo went from a corpus it could read to a
Stage 0 apparatus that is complete: a harness that checks everything §7 says is
mechanically checkable, a workbook the expert fills in with dropdowns instead of
YAML, a transcriber that reads it back without inventing anything, a coverage
report that turns an hour of expert time into a moved counter, and CI that stays
green while reporting Stage 0 as incomplete. 219 tests pass.

Three things were decisions rather than implementations, and each has an ADR.
The harness needed a **third severity** — `not_labels` is required "wherever a
near-miss exists", which no machine can judge, so gating on it would have made
Stage 0 uncompletable and dropping it would have lost the guide's best field
(ADR-0030). A run that never opened the snapshot **must not report Stage 0
complete**, because unverified is not sound and one report cannot mean both
(ADR-0031). And an array of objects in a spreadsheet had to become its own sheet
rather than parallel lists in one cell, because parallel lists pair the third
grade with the third ref by convention and nothing notices when that stops being
true (ADR-0036).

The most useful output is not the harness. It is that **the expert's path is now
two commands wide in each direction**: worksheet and workbook out,
`tmk-transcribe` back in, `tmk-coverage` to see what moved. Nothing between the
expert and the gold set requires anyone to type a ref, a hash or a line of YAML.

Recorded ADR-0030 to ADR-0037 and QUIRKS Q-22, Q-23. One dependency raised for
the owner rather than assumed: `openpyxl`, added as an optional extra (ADR-0035,
Q12). No legal content authored. No Stage 2 extraction run.

### S004 — 2026-08-18 — phase one of the parallel track: seven packages, and a worksheet

Built P1, P2, P3, P4, P6, P9 and P12. The repo went from documentation and an
empty skeleton to a package that fetches a pinned corpus, loads it without losing
a field, validates eight record types, and prints an annotation worksheet. 165
tests, of which the corpus-wide ones skip cleanly without a snapshot.

The most useful output is not the code. It is that **the expert critical path is
now one command shorter**: `tmk-worksheet` prints 216 chunks with every ref and
hash already on the page, and `tmk-recon` costs each candidate boundary rule, so
Q8 can be answered against numbers instead of impressions.

Three documented facts turned out not to hold against the corpus (Q-17, Q-18,
Q-20), and one small thing about the pilot is worth knowing before gold records
are written: s 43 has no numbered subsections, so a citation to "s 43(1)"
resolves to nothing at all (Q-21). None of these was visible from prose.

Two mechanisms earned their place immediately. The pin's corpus-count check
rejected a wrong number in the first pin written; the template/schema drift check
found that five gold record templates had no `approved_by`/`approved_date`,
though the definition of done requires them on every record.

Recorded ADR-0023 to ADR-0029, and QUIRKS Q-17 to Q-21. No legal content
authored. No Stage 2 extraction run.

### S003 — 2026-08-17/18 — the parallel track; Stage 2 stack; four decisions closed

Owner reported the experts are slow and asked what could proceed meanwhile.
Wrote `docs/roadmap/PARALLEL-TRACK-ROADMAP.md` (ADR-0016): twelve agent-side
packages P1–P12, five gates, an explicit not-to-do list, and a statement of
where the track runs out. Added `docs/roadmap/README.md` because that directory
now mixes a source document with an editable one.

Two things fell out of writing it that are more useful than the package list.
The Pass B worksheet does **not** have to wait on the pilot boundary — an
over-inclusive provisional scope rule the owner can set alone releases it, and
the error costs are asymmetric enough to make that clearly right (ADR-0017).
And the red harness is not free: with no gold records every mechanical check
passes vacuously, so the redness has to come from an explicit completeness gate,
which also has to be distinguishable in CI from a genuine failure (ADR-0018).

Owner then fixed the Stage 2 candidate-generation stack: TextRank + YAKE +
KeyBERT in parallel, spaCy NER as metadata on candidates (ADR-0019, human).
Recording it surfaced two consequences worth having before code exists. The
candidate-id formula in `IDENTIFIERS.md` §3 hashes `method`, so three extractors
mint three ids for one span and the cross-method agreement the ensemble exists
to produce is invisible — ADR-0020 proposes dropping `method`, and P3 must wait
on Q10. And spaCy's OntoNotes labels collide by name with two gold entity types
while meaning something else (Q-16), which is how NER output would quietly
become the taxonomy.

Owner then answered four open questions when asked (ADR-0021, authority human):
Q2 pinned release download, Q5 upstream refs canonical, Q10 drop `method` from
the candidate id, and ADR-0017 confirmed with its rule set in ADR-0022 — every
chunk citing `TMA1995/s43` or a unit beneath it, plus page-mates, at every
`certainty` value. `IDENTIFIERS.md` §3 went from proposal to operative formula.

That leaves the board in a shape worth noticing: **no agent work is blocked on a
human decision**, P1 is the critical path, and all four remaining gates are
expert content. From here the only lever on the schedule is making that content
cheaper to produce — P6, P7, P9, P10.

No legal content authored. No code, no data. Nothing executed.

### S002 — 2026-08-06 — pilot area fixed; Stage 0 input guide

Owner selected **s 43** as the pilot area on expert advice (ADR-0013), closing
Q1. Wrote `eval/STAGE-0-INPUT-GUIDE.md`: the expert-facing walkthrough of all
Stage 0 deliverables, with shape-only worked examples, elicitation prompts, a
definition of done and the order of work (ADR-0014).

Found a gap while writing it — the roadmap names seven gold-standard components
and the templates covered six. Added
`eval/templates/reasoning-expectation.template.yaml` (ADR-0015).

Two points in the guide are load-bearing and not obvious: recall is unmeasurable
unless a bounded chunk set is annotated **exhaustively** rather than
cherry-picked (§4), and Stage 0 splits into a pass that needs no data and a pass
that cannot start until the snapshot is pinned (§3). The second makes Q2 the
next agent-side blocker.

No legal content authored. No code, no data. Nothing executed.

### S001 — 2026-08-04 — repo structure and agent documentation

First working session. Repo contained only the roadmap, the upstream index and a
licence. Built the documentation set (`CLAUDE.md`, this file, `DECISIONS.md`,
`QUIRKS.md`, `ARCHITECTURE.md`, `IDENTIFIERS.md`, `ROADMAP-STATUS.md`,
`GLOSSARY.md`) and the directory skeleton with a README per directory. Relocated
the two source documents into `docs/` unaltered.

Recorded ADRs 0001–0012. Found and logged four discrepancies between the roadmap
and the upstream reality (QUIRKS Q1–Q4), the sharpest being that the roadmap's
illustrative identifier scheme cannot be reconciled with the identifiers upstream
actually emits.

No code, no data, no dependencies. Nothing has been executed because there is
nothing to execute.

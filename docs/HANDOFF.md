# HANDOFF — read this first

The baton between sessions. It is authoritative on current state. If it
disagrees with your reading of the tree, trust it and then fix it.

**Last updated:** 2026-08-19 · session S006 · branch `claude/trademark-expert-blockers-3x8zyc`

---

## 1. Where the project actually is

**The agent-side track is finished.** All twelve parallel-track packages
(P1–P12) are built. S005 delivered the last five: **P5** the evaluation harness,
**P7** the intake workbook, **P8** the transcription path, **P10** the coverage
report and **P11** CI. 219 tests pass. From a bare clone:

```bash
pip install -e ".[test,intake]"
tmk-fetch-upstream    # pinned snapshot into data/upstream/ (~4s)
tmk-worksheet         # 216 chunks to annotate → data/derived/worksheet.md
tmk-workbook          # the intake workbook → data/derived/stage0-intake.xlsx
tmk-harness           # every Stage 0 check. Exits 3 — see below
tmk-coverage          # the same, as a worklist → data/derived/reports/
pytest -q
```

**The red harness exists and it is red for the right reason.** `tmk-harness`
exits **3** and prints 22 gaps naming every absent Stage 0 deliverable. It exits
**1** on a defect — a record that does not validate, a duplicated or retired id,
a dangling cross-reference, a ref that resolves to nothing, a span that does not
land on its recorded text, a stale hash. That separation is ADR-0018, realised in
ADR-0030, and it is what stops a permanently red pipeline from training everyone
to ignore it.

Note where the failure lives, because it is easy to get backwards: **`pytest` is
green** — it tests the harness, and the harness works. The red thing is
`tmk-harness`. A permanently failing pytest would have been a suite that says
nothing about whether the code is sound (Q-23).

**The expert can now hand back a spreadsheet.** `tmk-workbook` generates an
empty ten-sheet workbook from the schemas — dropdowns on every fixed vocabulary,
no example rows anywhere — and `tmk-transcribe` reads it back into validated
records, reporting every blank judgement field instead of filling one. The round
trip preserves every populated field and is a fixed point. Guide §6's promise —
"do not write YAML" — is now a command rather than an intention.

**Stage 0 still has no expert content, and nothing an agent can do will change
that.** What changed is that the last excuse is gone: the boundary decision is
costed, the annotation surface is printed, the intake form exists, and an hour of
expert time visibly moves a counter.

**The parallel track's §7 now applies.** Its own words for this moment: *"the
container is finished and empty; the programme is waiting on Stage 0 content"* —
not a search for further plumbing. A session that finds itself designing new
apparatus should stop and read that section.

## 2. The next action

**Thread B — the experts. It is the only thread with work in it.** Pass A
content in the order at `eval/STAGE-0-INPUT-GUIDE.md` §10: pilot scope boundary
first (Q8), then competency questions and prohibited uses. Pass B needs nothing
from anyone before it starts — hand over `data/derived/worksheet.md` and
`data/derived/stage0-intake.xlsx` and annotation can begin on 216 chunks today.

**Thread C — agents. Maintenance, not construction.** What is legitimately left:

1. **Transcribe whatever arrives.** `tmk-transcribe FILE --write`, then
   `tmk-harness` and `tmk-coverage`. This is the loop the whole track was built
   to serve, and it is now one command per direction.
2. **Report the state honestly.** `tmk-coverage` is the answer to "what is Stage
   0 waiting on". It is a better status report than any prose a session could
   write, and it is generated from the data rather than from an impression.
3. **Keep the pin current if upstream moves** — and remember bumping it makes
   every `source_content_hash` stale by design (`IDENTIFIERS.md` §5). The
   harness will say so. Do not silently refresh a hash.
4. **Confirm the agent-proposed ADRs** when a human is available (§3, Q11/Q12).

**Do not** build more apparatus. **Do not** start Stage 2 — no TextRank, YAKE,
KeyBERT or spaCy run, not even "just to see the output" (ADR-0010). It is more
tempting than ever now that the loader makes it a twenty-line script and the
harness would give it a number to point at. The number would be meaningless: it
would be measured against a gold set that does not exist.

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
| Q14 | **New, S006.** Owner asked for more plain-language guidance on **constructing the ontology**, beyond what `STAGE-0-INPUT-GUIDE.md` covers (which is scoped to Stage 0 elicitation, not Stage 5 ontology formalisation). Not scoped or drafted yet — needs its own session: who is the audience (the Trade Mark experts already working from the input guide, or a wider group?), and what specifically is unclear in the existing docs. | Nothing yet; would help the experts' ongoing work | S006 |

Agent-proposed ADRs awaiting human confirmation: **0011** (deferred, not
declined — see ADR-0041), **0029, 0030, 0032, 0033, 0035, 0036, 0037**.
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
  In a spreadsheet, copying a row is one keystroke.
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

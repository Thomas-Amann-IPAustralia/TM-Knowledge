# authored/ — legal content an agent wrote, that no expert has validated

**Everything in this directory was written by a machine. None of it has been read
by a trade marks expert.** That is not a defect and it is not a temporary state
to be embarrassed about — it is the operating model the repo owner chose on
2026-09-08 (ADR-0079). It is also the single most important fact about this
directory, which is why it is the first line of its README and why every record
inside repeats it in a field a machine can read.

Read `docs/DECISIONS.md` ADR-0079 to ADR-0085 before writing anything here.

## What this is for

Experts are much better at correcting a wrong record than at composing a right
one from a blank form. The project measured that the hard way: fourteen sessions
produced 190 signed records, an ontology with 30 of 49 classes empty, no
definitions at all, and 168 records parked behind ten decisions nobody had time
to make.

So an agent now fills the ontology in full and the expert's job becomes
interrogation and correction. The bet is that a populated system they can argue
with produces more correct knowledge per hour of their time than an empty one
they must fill — and that seeing it work is what gets them engaged.

## The line this directory exists to hold

| | `eval/gold/` | `authored/` |
|---|---|---|
| Written by | a trade marks expert | an agent |
| Signed by | a named person, on a date | nobody |
| May be relied on | yes | yes (ADR-0082) |
| Counts as validated | yes | **never**, until a person signs it |
| Used as a measurement yardstick | yes — frozen for this purpose | no, and never |

`eval/gold/` is **frozen** at 190 records. Nothing here is written there by an
agent, ever. It is the only independently-produced reference set the project has,
and the moment it contains model output it stops being able to measure model
output — permanently, because you cannot unmix them afterwards (ADR-0080).

## What belongs here

Any record type the schemas define, authored by an agent, wrapped in an authoring
envelope. Same record types as `eval/gold/`, same file names, same underlying
schemas:

| File | Record type |
|---|---|
| `concepts.yaml` | gold concept |
| `concept-types.yaml` | concept type |
| `entities.yaml` | gold entity |
| `relationships.yaml` | gold relationship |
| `competency-questions.yaml` | competency question |
| `retrieval-questions.yaml` | AI retrieval question |
| `search-questions.yaml` | gold search question |
| `reasoning-expected.yaml` | reasoning expectation |
| `prohibited-uses.yaml` | prohibited use |
| `definitions.yaml` | concept definitions — new; `eval/gold/` has none |

## The envelope — every record carries all of it

Validated by `eval/schemas/authored-envelope.schema.json`. A record that cannot
carry these fields is not written; that is rule 1's replacement and it is not
negotiable.

```yaml
- id: GC-0107
  pref_label: adverse report
  # … the ordinary record fields, per the record type's own schema …
  approved_by: null                 # NEVER filled by an agent
  approved_date: null
  authored:
    review_status: unreviewed       # unreviewed | seen_uncorrected | approved | rejected
    authored_by: claude-opus-5      # the model, with version
    authored_date: '2026-09-08'
    authoring_basis: corpus_explicit
    evidence:
      - ref: TMM/Part20/5/5/1
        span: [412, 587]
        content_hash: sha256:…
    confidence: 0.8
    reasoning: >-
      One sentence on why this reading and not the obvious alternative. Written
      for the expert who will disagree with it, not for the next agent.
    alternatives_considered:
      - The reading rejected, and what would make it the right one instead.
    expert_should_check: >-
      The specific thing most likely to be wrong. Blank is not permitted on a
      tier 3 record.
```

### `authoring_basis` — the field that carries the honesty

| value | means |
|---|---|
| `corpus_explicit` | the corpus states this in terms; the span shows where |
| `corpus_inferred` | the corpus supports it, but the reading is the agent's |
| `general_knowledge` | **the corpus does not say this.** Written from what the model knows about trade marks law |

`general_knowledge` is not forbidden and it is not a confession — sometimes it is
the only honest label available. It *is* a flag: a record carrying it is
unevidenced, a reviewer should reach it first, and no count of "records we hold"
may present it as equivalent to an evidenced one.

Do not reach for it to avoid the work of finding a span. Do not avoid it to make
a record look better. A `corpus_explicit` claim whose span does not support it is
the worst thing that can be written here, because it is a lie a machine will
later certify.

## What does not belong here

- **Anything an expert signed.** That is `eval/gold/`.
- **Anything an expert rejected.** A signed rejection is a human decision and
  ADR-0079 does not license reversing one. If an authored record covers ground a
  rejected record was rejected from, it cites the rejection and says why it
  differs (ADR-0084 consequence 2).
- **Extraction candidates.** A candidate is a proposal with a score and lands in
  `review/candidates/`. An authored record is a judgement an agent committed to.
  Promoting a candidate to an authored record is itself an act of authorship and
  takes the full envelope (ADR-0083 consequence 3).
- **A record with `approved_by` filled in.** The harness reports it as a defect.
  It is the one failure the whole scheme exists to prevent.
- **A record with no evidence and no `general_knowledge` flag.** Silence about
  where something came from is the laundering rule 1 now prohibits.

## The one door out

A record leaves here for `eval/gold/` exactly the way a seed record did:
`tmk-transcribe`, reading a workbook in which a person wrote a verdict **and**
their name. Not a hand copy. Not an agent's assessment that a record is obviously
right. Not the passage of time.

**Silence never promotes anything** (ADR-0085). A record a reviewer had in front
of them and did not change becomes `seen_uncorrected`, which is stronger evidence
than `unreviewed` and weaker than `approved`, and the difference is permanent.

## Ids

One sequence across both stores (`docs/IDENTIFIERS.md` §3). There is one
`GC-0123` in this project and it is either here or in `eval/gold/`, never both. A
duplicate across stores is a defect the harness reports.

Where an authored record and a later signed record cover the same ground, the
signed one wins and the authored one is retired — the reverse of the ordinary
never-delete rule, and right here because the signed record is strictly better
evidence of the same thing (ADR-0080 consequence 2).

## Reading anything in here

Never as validated. A record from this directory quoted in a report, a prompt, an
evidence package or a dashboard figure carries its review status with it, at the
point of use. A surface that cannot show that status must not serve this content
at all — that is the constraint that replaced the Tier 3 gate when ADR-0082
removed it, and it is the whole of what stands between "the ontology is
populated" and "the ontology is trusted".

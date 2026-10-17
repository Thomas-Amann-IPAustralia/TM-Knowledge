# The ontology — a guide for people, not for parsers

**Draft. Nothing here is approved.** Read `data/derived/reports/ontology.md`
alongside it: this file explains the modelling choices, and that one counts what
they produced and what is still missing. The examples come from section 43, where
the work started; the scope has been the whole Manual since ADR-0081.

---

## 1. The one idea the whole model is arranged around

The Manual is not the Act.

It states the Registrar's practice. It does not bind the Registrar's discretion
and it is not legislation. Every other decision in this ontology falls out of
holding that line, and the line is genuinely hard to hold in this corpus for one
specific reason: **the Manual quotes section 43 in full inside
`TMM/Part29/1#1`.** So a passage can look like the Act and be the Manual quoting
the Act, and an answer can appear to cite the statute while having read only the
practice material. CQ-0001's caveat calls that "a grounding failure that will
not show up as a missing source" — the citation is there, and it is to the right
place, and the answer is still wrong.

Five mechanisms carry the distinction, at different levels:

| level | mechanism |
|---|---|
| the model | `tmk:ManualPassage owl:disjointWith tmk:LegislativeProvision` — and `tmk:ManualInstruction` likewise, for mentions |
| every node | `tmk:authorityKind` — `law`, `practice` or `decision` — and, on every Manual chunk, the class `tmk:ManualPassage` by the same rule |
| the gate | `shapes/authority.ttl` fails a node typed both practice and law, and a proposition stated in practice and attributed to law |
| every query | each competency query returns the authority alongside the passage |
| every answer | `search.authority` (and `engine.js`) flags an answer sentence that says the legislation requires something when the answer cites no provision for it (PU-0004) |

The disjointness alone is not enough, because a projection can drop a type. The
`authorityKind` string is what survives a projection, and the shapes catch an
output that lost it anyway.

**What changed on 2026-10-08** (review F1, ADR-0121). The ontology review found
that two of the four mechanisms then listed guarded nothing on real data:
`tmk:ManualInstruction` is applied to entity mentions, never to a passage, so its
disjointness could not fire; and the PU-0004 shape targets `tmk:LegalProposition`,
which nothing in the build produces. Both fired only on test fixtures. The fix
put a class on every Manual chunk for the disjointness to guard, and moved the
PU-0004 check to where the error happens — the live answer, which the graph never
sees. The proposition shape stays for the day propositions are built.

---

## 2. Two kinds of thing that are easy to confuse

**A proposition** is what the corpus says. **An assertion** is what this project
did about it — the record that somebody extracted it, from a passage, by a
method, and that somebody else approved it on a date.

Every approved relationship is in the graph twice:

```turtle
# the direct triple — what SPARQL works on
tmkr:TMA1995/s43  tmk:requiresElement  tmkc:GC-0002 .

# the assertion — what an audit works on
tmka:GR-0003
    a tmk:ApprovedAssertion ;
    tmk:assertionSubject   tmkr:TMA1995/s43 ;
    tmk:assertionPredicate tmk:requiresElement ;
    tmk:assertionObject    tmkc:GC-0002 ;
    tmk:supportingText     "However for a trade mark to be caught by these
                            provisions it is necessary for a decision maker to be
                            clearly satisfied that…" ;
    tmk:sourcePassage      tmkr:TMM/Part29/1%231 ;
    tmk:spanStart 543 ; tmk:spanEnd 777 ;
    tmk:sourceContentHash  "sha256:b6690f…" ;
    tmk:modality "must" ; tmk:tier 3 ;
    tmk:approvedBy "TC" ; tmk:approvedDate "2026-08-25"^^xsd:date .
```

Why both? Because either alone fails. The direct triple is usable and anonymous;
the assertion is complete and awkward to query. A SHACL constraint fails the
graph if a direct triple appears with no assertion behind it — so an edge nobody
signed cannot sit in the approved graph looking like one that was.

---

## 3. What a citation is, and why it is not an edge

Upstream records, for every reference from a Manual passage to a provision, *how
it was found*:

- `extraction: href` — the Manual's authors linked it themselves. The strongest
  provenance this corpus has.
- `extraction: regex` — upstream read it out of the prose. Then `certainty` says
  how confident that reading was: `explicit`, `default` (inferred from a bare
  "section 43" — an inference, not a statement by IP Australia), or `ambiguous`
  (several instruments were in scope and upstream refused to choose).

If those two fields are flattened into a plain edge they cannot be recovered.
So a citation is a node:

```turtle
tmk:cite/TMM%2FPart29%2F2%2F2%2F1~2/prov/0
    a tmk:Citation ;
    tmk:citingPassage    tmkr:TMM/Part29/2/2/1~2 ;
    tmk:citedAuthority   tmkr:TMA1995/s43 ;
    tmk:extraction       "regex" ;
    tmk:certainty        "default" ;
    tmk:mention          "s 43" ;
    tmk:citationResolves true .
```

This is what makes CQ-0022 — *did the Manual's authors link that section
themselves, or did we work it out from the wording?* — a query rather than a
shrug. It also changes CQ-0017's answer: four Manual Parts are carried into the
section 43 impact set entirely by inferred edges, so "this Part needs reviewing"
is a weaker claim there than the raw count suggests.

The two `ambiguous` edges are never resolved. An ambiguous edge is a reason to
put a passage in front of a person, never a reason to drop it.

---

## 4. The vocabulary, and the field SKOS does not have

Concepts are SKOS. `prefLabel`, `altLabel`, `broader`, `narrower`, `related` —
all standard. One field is not:

```turtle
tmkc:GC-0002
    skos:prefLabel "likely to deceive or cause confusion"@en-AU ;
    skos:altLabel  "deception or confusion"@en-AU ;
    tmk:notLabel   "deceptively similar"@en-AU ;
    tmk:notLabel   "likelihood of confusion between trade marks"@en-AU .
```

**`tmk:notLabel` is the most valuable field on the record.** "Deceptively
similar" belongs to section 44. A retrieval system that treats it as a synonym
routes an examiner to the wrong test — and the misrouting is invisible, because
both destinations are about confusion. GX-0005 is the approved expectation that
says so.

Two constraints follow. A term may not be both a label and a not-label of the
same concept (a defect: the record says at once that it means this and never
means this). A term that is one concept's not-label and another's preferred
label is *reported and not failed* — that is exactly what a not-label is for,
and the pairs the run finds (counted in the report) are the vocabulary's
boundaries drawn in.

**A definition is its own record.** The signed concept records carry definition
*sources* — the passages the meaning is drawn from — and no text, and a signed
record is never edited. So a definition is a `GD-` record in
`authored/definitions.yaml`: machine-written, unreviewed, drafted from those
sources with the Act's own definition preferred where it has one (CHAT-0045), and
quoting the words it rests on. The graph states it as `skos:definition` on the
concept, in the authored graph, beside the record that says who wrote it.
Approving a label approves no definition (the review response, F06).

---

## 5. The kinds, and who chose them

Every concept is sorted into one of eleven kinds in three families (ADR-0126,
ADR-0131): the law's questions (`GroundOfRefusal`, `LegalTest`, `Principle`),
what they are asked about (`SubjectMatter`, `SignContent`, `Context`,
`UseInTrade`), and the process (`ProcessRole`, `ProceduralStep`,
`InstrumentOrRecord`, `ExternalInstrument`). A kind says what a concept *is*.
What it *does* is an edge to the ground or test it acts on: a factor `qualifies`
it, an exception `isAnExceptionTo` it, a ground `isOvercomeBy` its remedy.

**A machine chose every kind.** A typing is its own record (`GT-`, ADR-0071),
and every one is in `authored/concept-types.yaml`, stamped unreviewed; no person
has typed a concept. Deciding that *connotation* is a `LegalTest` rather than a
factor is a legal judgement, so each of these is the agent's, recorded with the
passages it rests on, and the examiners' review at ship time is where it is
checked (ADR-0120).

The roles in `examination.ttl` (the Registrar, a delegate, an applicant and the
rest) are distinct, and their power is on edges read from a sentence of the Act
or the Manual (ADR-0123). `tmk:ExaminationOutcome` stays empty for good: the
system never states one.

Declaring a class empty makes the gap countable. `tmk-ontology-report` counts
them.

---

## 6. Domain and range: what a predicate joins, without a reasoner

Every predicate in `relations.ttl` has `rdfs:domain tmk:LegalMatter` and
`rdfs:range tmk:LegalMatter`, where `LegalMatter` covers concepts, provisions,
passages and decisions. That looks like giving up, and it is not.

A domain is a reasoning commitment: in any tool that applies RDFS or OWL
semantics, anything appearing as the subject of the property **is** a member of
that class. No OWL profile is claimed here and no OWL inference is licensed
(ADR-0134), but a reader can still load the graph into a tool that reasons, and a
narrow domain would silently reclassify every subject that did not fit it.

So what a predicate joins is stated as the kinds it expects —
`tmk:expectedSubjectKind` and `tmk:expectedObjectKind`, annotations that infer
nothing — and the harness fails a machine-written edge whose ends are not those
kinds (ADR-0131). Each predicate is defined in `ontology/predicates.py`, with a
reading, an example and a counter-example (ADR-0123); the report counts how many
are used by one record only, because a term seen once is a term whose boundaries
nobody has tested.

---

## 7. Prohibitions as constraints

`eval/gold/prohibited-uses.yaml` holds eleven outputs the system must never
produce. Most are marked `detectable_by: eval` or `test` — they can be reported
after the fact. Two are marked `shacl`, and that is a stronger claim: a shape
blocks publication, where a test only reports.

PU-0004 is the one that is implemented — as a shape over propositions, and,
since 2026-10-08, as a check over every answer (`search.authority`, §1):

> "Section 43 of the Act requires the connotation to be obvious, direct and
> immediate."

Every word of that formulation is in the corpus. It is the Manual's, and the
Act requires no such thing. The record's own note says why it is structurally
detectable: *the claim attaches a Manual-sourced proposition to a legislative
ref.* So the model separates where words are (`tmk:statedIn`) from what they are
being presented as coming from (`tmk:attributedTo`), and the shape fails any
proposition stated in a practice passage and attributed to a provision.

The fixture that proves it fires carries a conforming twin — the same words,
the same passage, attributed to the Manual. The shape must leave that alone. A
constraint that fired on both would pass its test and be useless.

---

## 8. What the model says about time, which is less than you would like

Staleness works, and it is the mechanism that matters: every assertion carries
the `content_hash` its passage had when it was approved, and an assertion whose
hash no longer matches the pin is stale and returns to review rather than being
carried forward. That is the whole of Stage 10's incremental machinery and it
needs no version stamp.

Point-in-time questions do not work and will not under this snapshot strategy.
There is no corpus-level version stamp; the amendment history is the upstream
repository's git history. "What guidance was current on «date»" needs a
full-history clone, which is a different data strategy rather than a different
query. CQ-0014 carries that limitation and it is out of scope.

The legislation says which state of the law it is. Upstream records the
compilation of each instrument it holds, and the graph states it on the
instrument (`tmk:compilationNumber`, `tmk:registerId`, `tmk:compilationStart`), so
every answer can name "the Act as in force from" that date. When the pin moves to
a new compilation, every record resting on a changed provision goes stale and is
re-read, never refreshed silently.

`tmk:NotHeld` is the third status and the useful one: cited by the corpus, held
nowhere in the programme. Section 114 of the *Trade Marks Act 1905* is cited by
Part 29.3.1, the Manual relies on it, and it can be neither excluded nor
resolved. CQ-0020 asks for exactly the list of citations in that state.

---

## 9. Running it

```bash
pip install -e ".[test,intake,rdf]"
tmk-fetch-upstream                # the pinned snapshot
tmk-graph --write --rules         # build, run the candidate rules, serialise
tmk-shacl --rules                 # the gate. Exit 0: no defects and no gaps
tmk-ask                           # every competency query, with its limits
tmk-ask CQ-0017                   # one of them
tmk-ontology-report --write       # the state of the ontology, counted (--check in CI)
python3 -m pytest -q              # note python3 -m, not bare pytest (Q-29)
```

## 10. If you are the person reviewing this

Nobody signs anything singly before the ontology ships to a group of trade marks
examiners, who review it all at once (ADR-0120). What is worth their time, in
order of how much rests on it:

1. **The kinds.** Every concept's kind is a machine's judgement; a wrong kind
   misroutes everything that hangs off it.
2. **The relationships and their conditions.** Each machine-written edge quotes
   its sentence and carries the sentence's condition in `applies_when`; the card
   in the explorer shows both.
3. **The definitions.** Drafted from each concept's sources, the Act's own words
   first; approving a label approves no definition.
4. **RULE-0001.** Still pending; everything it produces is quarantined as a
   candidate until a person rules.

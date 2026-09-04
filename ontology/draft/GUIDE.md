# The section 43 ontology — a guide for people, not for parsers

**Draft. Nothing here is approved.** Read `data/derived/reports/ontology.md`
alongside it: this file explains the modelling choices, and that one counts what
they produced and what is still missing.

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

Four mechanisms carry the distinction, at four different levels:

| level | mechanism |
|---|---|
| the model | `tmk:ManualInstruction owl:disjointWith tmk:LegislativeProvision` |
| every node | `tmk:authorityKind` — `law`, `practice` or `decision` |
| the gate | `shapes/authority.ttl` fails a proposition stated in practice and attributed to law |
| every answer | each competency query returns the authority alongside the passage |

The disjointness alone is not enough, because a projection can drop a type. The
`authorityKind` string is what survives a projection, and the shape is what
catches an output that lost it anyway.

---

## 2. Two kinds of thing that are easy to confuse

**A proposition** is what the corpus says. **An assertion** is what this project
did about it — the record that somebody extracted it, from a passage, by a
method, and that somebody else approved it on a date.

Every approved relationship is in the graph twice:

```turtle
# the direct triple — what SPARQL and OWL RL work on
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
and the 29 pairs the run finds are the vocabulary's boundaries drawn in.

**No concept has a definition.** `skos:definition` appears nowhere in this repo.
The approved records carry definition *sources* — the passages the meaning is
drawn from — and no text, so the graph carries sources and no text. That is a
gap, it is counted in the report, and filling it is an expert's afternoon.

---

## 5. Why the interesting classes are empty

`tmk:GroundOfRefusal`, `tmk:LegalTest`, `tmk:RelevantFactor`, `tmk:Exception` —
declared, and holding nothing. All 52 approved concepts are bare
`tmk:LegalConcept`.

This is not an oversight and it is the single largest gap in the draft. The gold
concept record has no type field, and deciding that *connotation* is a
`LegalTest` rather than a `RelevantFactor` is a legal judgement. An agent filling
those slots would produce a taxonomy that reads as authoritative and was authored
by nobody — the exact failure the whole repo is arranged to prevent.

The same applies to the roles in `examination.ttl`. `tmk:Registrar`,
`tmk:DecisionMaker`, `tmk:Examiner` and the rest are declared UNDEFINED because
the reviewer's own covering note asks for those definitions and has not had them
(HANDOFF Q17). `tmk:DecisionMaker` carries the sharpest version: the office's bar
for the presumption of registrability is not that the individual examiner doubts
a connotation exists but that the Registrar as a whole does, and a model that
equates the two roles loses that silently.

Declaring a class empty makes the gap countable. `tmk-ontology-report` counts
them.

---

## 6. Domain and range: a decision that looks like laziness and is not

Every predicate in `relations.ttl` has `rdfs:domain tmk:LegalMatter` and
`rdfs:range tmk:LegalMatter`, where `LegalMatter` is a superclass covering
concepts, provisions, passages and decisions. That looks like giving up.

It is not. Under OWL 2 RL, `rdfs:domain` is a *reasoning commitment*: it says
that anything appearing as the subject of this property **is** a member of that
class, and a reasoner will assert it. The approved relationships do not support
a narrow one. `requiresElement` runs Provision→Concept twice, Concept→Concept
three times and Concept→Provision once. `excludesBasis` runs both ways. Asserting
`rdfs:domain tmk:LegalConcept` on that evidence would silently reclassify every
provision it touches.

So the narrow types each predicate has actually been seen with are recorded as
`tmk:observedSubjectType` and `tmk:observedObjectType` — **annotation**
properties, which infer nothing — with the count and the record ids beside them.
Tightening one to a real domain assertion is an expert ruling, and the
annotations are the evidence to rule on.

Six of the fourteen predicates are used exactly once. A term seen once is a term
whose boundaries nobody has tested.

---

## 7. Prohibitions as constraints

`eval/gold/prohibited-uses.yaml` holds eleven outputs the system must never
produce. Most are marked `detectable_by: eval` or `test` — they can be reported
after the fact. Two are marked `shacl`, and that is a stronger claim: a shape
blocks publication, where a test only reports.

PU-0004 is the one that is implemented:

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
query. CQ-0014 carries that limitation and the pilot scope draft puts it out of
scope.

`tmk:NotHeld` is the third status and the useful one: cited by the corpus, held
nowhere in the programme. Section 114 of the *Trade Marks Act 1905* is cited by
Part 29.3.1, the Manual relies on it, and it can be neither excluded nor
resolved. 35 citations are in that state and CQ-0020 asks for exactly the list.

---

## 9. Running it

```bash
pip install -e ".[test,intake,rdf]"
tmk-fetch-upstream                # the pinned snapshot
tmk-graph --write --rules         # build, run the candidate rules, serialise
tmk-shacl                         # the gate. 0 defects, 0 gaps, 29 notes
tmk-ask                           # every competency query, with its limits
tmk-ask CQ-0017                   # one of them
tmk-ontology-report --write       # the state of the draft, counted
python3 -m pytest -q              # note python3 -m, not bare pytest (Q-29)
```

## 10. If you are the person approving this

The four questions worth your time, in order of how much they unblock:

1. **Type the 52 concepts** into `GroundOfRefusal` / `LegalTest` /
   `RelevantFactor` / `Exception`, or say the taxonomy is wrong. One pass over a
   list, no new records, and it is what turns a flat vocabulary into a hierarchy
   the retrieval stages can generalise over.
2. **Rule on the four unmatched question labels**, `deceptively similar` first.
   It is a not-label of an existing concept and a competency question names it as
   an expected concept — so either the vocabulary needs the s 44 concept or the
   question is using it as a boundary marker.
3. **Approve or reject the two CONSTRUCT rules.** Both are `PENDING` and
   everything they produce is quarantined as a candidate until you do.
4. **Say whether a narrow domain is right for any predicate.** The observed
   types are annotated on each one, with counts.

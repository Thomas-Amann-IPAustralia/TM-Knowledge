# ontology/draft/ — the candidate ontology

**Nothing in here is approved.** That is the whole reason the directory exists.

`ontology/` holds approved modules and there are none. These nine modules are a
machine-written modelling proposal over the whole Manual and the two instruments,
drafted from the roadmap's module list and grown with the content since (the
kinds in `legal-concepts.ttl`, the roles in `examination.ttl`, the predicates in
`relations.ttl`). A module moves up to `ontology/` when a person signs it, and
until then this path is the marker that says so (ADR-0057). Examiners review the
whole at ship time (ADR-0120).

```
document.ttl        Passage, Document, DocumentVersion, Page, Chunk
authority.ttl       Legislation, LegislativeProvision, ManualPassage,
                    JudicialDecision, Citation — and the practice/law disjointness
legal-concepts.ttl  LegalConcept, the eleven kinds in three families (ADR-0126,
                    ADR-0131), and the definition record
provenance.ttl      ADR-0011's fields over PROV-O, signed and authored
relations.ttl       GENERATED from ontology/predicates.py — the closed predicate list
examination.ttl     the roles (Registrar, delegate, applicant…) and procedural steps
evidence.ttl        declared, unpopulated, and deliberately so
time.ttl            staleness, the compilation of the law held, and what time
                    questions cannot be asked
evaluation.ttl      competency questions, prohibited uses, relevance judgements
GUIDE.md            the human-readable tour
```

## What belongs here

Class and property declarations, with `rdfs:comment` explaining the modelling
choice. Nothing else.

## What must not

- **A legal definition.** Definitions are records, not modelling: a machine-written
  definition is a `GD-` record in `authored/definitions.yaml`, stamped unreviewed
  and quoting the passages it rests on, and the graph states it in the authored
  graph. A class comment says what a *class* is for; it never defines a legal
  term.
- **A narrow `rdfs:domain` or `rdfs:range` inferred from a handful of examples.**
  In any tool a reader loads the graph into, a domain assertion reclassifies every
  subject of the property. What a predicate joins is stated as the kinds it
  expects (`tmk:expectedSubjectKind`, `tmk:expectedObjectKind`, ADR-0131), which
  the harness checks and which infer nothing; the asserted domain and range are
  `tmk:LegalMatter`, which licenses nothing false.
- **A hand-edit to `relations.ttl`.** It is generated from the relation
  dictionary, `ontology/predicates.py` (definition, reading, example and
  counter-example per predicate, with the kinds it joins), and CI compares the
  committed file against a regeneration. To add a predicate, define it there and
  name its kinds (ADR-0123, ADR-0131) — `tmk-ontology-relations --write`.
- **An OWL reasoning commitment.** No profile is claimed and no OWL inference is
  licensed (ADR-0134); what may be derived is an approved SPARQL rule in
  `queries/rules/`, and what a node must carry is a shape. A construct that needs a
  reasoner to mean anything is an ADR, not an edit. `tests/unit/test_declarations.py`
  holds the graph to its own functional, datatype and domain declarations.
- **A module not in `tbox.MODULES`.** The list is fixed rather than globbed: a
  file appearing on disk and being picked up silently is how an unreviewed
  module joins the ontology.

## The base IRI

Every file names `https://data.ipaustralia.gov.au/tmk/` because a Turtle file
has to name a base. **It is a name, not an address:** nothing is published there
and none of the IRIs dereferences. Which address the project may use is OQ-0008,
still open. `tbox.load()` rewrites the base when `TMK_BASE_IRI` says otherwise, so
it lives in one constant and changing it stays a configuration change plus a
rebuild — never a find-and-replace across serialised RDF (`docs/IDENTIFIERS.md` §2).

## UNPOPULATED and UNDEFINED

Both appear in `rdfs:comment`, and they are load-bearing rather than apologetic.
UNPOPULATED marks a class nothing has been placed in yet; UNDEFINED marks a term
whose meaning nobody has written down. Since ADR-0079 a machine may fill either,
stamped unreviewed, so the words now mean "not yet", not "not allowed".
`tmk-ontology-report` counts the empty classes. A class quietly populated by a
machine *without the stamp* is still the failure the repo is arranged to prevent:
a taxonomy that reads as authoritative and was signed by nobody.

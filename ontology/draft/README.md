# ontology/draft/ — the candidate ontology

**Nothing in here is approved.** That is the whole reason the directory exists.

`ontology/` holds approved modules and there are none. These are a modelling
proposal: nine OWL 2 RL modules over the section 43 pilot, drafted from the
roadmap's own module list and from the 190 approved records in `eval/gold/`. A
module moves up to `ontology/` when a person signs it, one at a time, and until
then this path is the marker that says so (ADR-0057).

```
document.ttl        Passage, Document, DocumentVersion, Page, Chunk
authority.ttl       Legislation, LegislativeProvision, ManualInstruction,
                    JudicialDecision, Citation — and the disjointness
legal-concepts.ttl  LegalConcept and the four subclasses that are still empty
provenance.ttl      ADR-0011's fields over PROV-O
relations.ttl       GENERATED — the closed predicate list
examination.ttl     roles and the process model. Almost entirely unpopulated
evidence.ttl        declared, entirely unpopulated, and deliberately so
time.ttl            currency, staleness, and what time questions cannot be asked
evaluation.ttl      competency questions, prohibited uses, relevance judgements
GUIDE.md            the human-readable tour
```

## What belongs here

Class and property declarations, with `rdfs:comment` explaining the modelling
choice. Nothing else.

## What must not

- **A legal definition.** `skos:definition` appears nowhere in this repo. The
  approved concept records carry definition *sources* and no definition text, so
  the graph carries sources and no text. Writing one would be authoring the
  vocabulary (CLAUDE.md rule 1).
- **A narrow `rdfs:domain` or `rdfs:range` inferred from a handful of examples.**
  Under OWL 2 RL a domain assertion reclassifies every subject of the property.
  The observed types are `tmk:observedSubjectType` annotations, which infer
  nothing; the asserted domain and range are `tmk:LegalMatter`, which licenses
  nothing false. Tightening one is an expert ruling, not an edit.
- **A hand-edit to `relations.ttl`.** It is generated from
  `eval/gold/relationships.yaml` and a test compares the committed file against
  a regeneration. To add a predicate, have an expert approve a relationship that
  uses it — `tmk-ontology-relations --write`.
- **Anything outside OWL 2 RL.** If you need a construct outside the profile,
  that is an ADR, not an edit.
- **A module not in `tbox.MODULES`.** The list is fixed rather than globbed: a
  file appearing on disk and being picked up silently is how an unreviewed
  module joins the ontology.

## The base IRI

Every file names `https://data.ipaustralia.gov.au/tmk/` because a Turtle file
has to name a base and HANDOFF Q7 is still open. `tbox.load()` rewrites it when
`TMK_BASE_IRI` says otherwise, so the base still lives in one constant and
changing it stays a configuration change plus a rebuild — never a find-and-replace
across serialised RDF (`docs/IDENTIFIERS.md` §2).

## UNPOPULATED and UNDEFINED

Both appear in `rdfs:comment` throughout, and they are load-bearing rather than
apologetic. `tmk:GroundOfRefusal` says UNPOPULATED because classifying
*connotation* as a ground rather than a test is a legal judgement; `tmk:Registrar`
says UNDEFINED because the reviewer's own note asks for that definition and has
not had it (HANDOFF Q17). `tmk-ontology-report` counts both. A class that holds
nothing is a gap someone can close in an afternoon; a class quietly populated by
a machine is a taxonomy that reads as authoritative and was authored by nobody.

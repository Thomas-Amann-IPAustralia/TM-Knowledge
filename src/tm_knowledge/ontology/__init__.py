"""Stage 5 and Stage 6 — the ontology draft, the graph built under it, and the
SPARQL that measures both.

Everything in this package is a *transformation* of content approved elsewhere.
It reads the pinned snapshot (`data/upstream/`) and the approved gold set
(`eval/gold/`) and it writes RDF. It never authors a legal proposition, a
concept definition or a modality, because those are expert content and this repo
does not write expert content (CLAUDE.md rule 1).

Three things the modules here are jointly responsible for keeping true:

1. **Practice and law stay disjoint.** `tmk:ManualInstruction` and
   `tmk:LegislativeProvision` are `owl:disjointWith`, and every query that
   returns a passage returns its authority alongside it (CLAUDE.md rule 5).
2. **Upstream's trust metadata survives into the graph.** `extraction` and
   `certainty` are properties of the citation edge, not attributes that get
   flattened into a boolean (CLAUDE.md rule 3).
3. **Every approved assertion is reified with its provenance.** The direct
   triple exists so SPARQL is natural; the `tmk:Assertion` beside it carries the
   source passage, span, hash, reviewer and date, and a SHACL shape fails if one
   is present without the other (ADR-0011, ADR-0058).
"""

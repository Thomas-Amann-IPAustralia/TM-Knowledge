"""Stage 3, 5 and 6: the vocabulary, the ontology and the knowledge graph.

Everything here is built from **approved** records in `eval/gold/` and from the
pinned snapshot. Nothing in this package extracts a candidate from raw text —
that is Stage 2, and ADR-0010 still forbids it. The distinction is the whole
reason this package may exist while Stage 2 may not: formalising content a
person has signed is a transformation, and inventing content for them to sign
is not (ADR-0056).
"""

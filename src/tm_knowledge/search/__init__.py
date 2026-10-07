"""Search over the Manual: plain keyword search, and the same search expanded
through the ontology (D2, D3 in `CLAUDE.md` §0).

`index.KeywordIndex` is SQLite's FTS5 with BM25 — no service, no dependency.
`index.OntologySearch` recognises concepts in a question by their labels and
everyday phrases, then adds what the ontology joins them to: their labels as
query terms, and the passages linked to them and to their neighbours. The two
rankings are fused by reciprocal rank. Comparing the two on one set of questions
is the value measurement.
"""

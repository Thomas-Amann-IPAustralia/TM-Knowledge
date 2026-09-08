"""The authored knowledge store: legal content a machine wrote, that nobody signed.

`authored/README.md` is the contract. This package is the only code that reads
that directory, and it exists so the honesty rules ADR-0079 states in prose are
mechanical: a record that cannot carry its envelope does not load quietly, and a
record that carries a filled-in `approved_by` is a defect rather than a surprise.
"""

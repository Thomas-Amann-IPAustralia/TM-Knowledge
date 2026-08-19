"""Reading the pinned `manual-XtrACTor` snapshot.

Consume, never re-derive (CLAUDE.md rule 2). Nothing in this package writes into
`data/upstream/`, and every field upstream records — `extraction`, `certainty`,
`content_hash` — passes through verbatim (rule 3).
"""

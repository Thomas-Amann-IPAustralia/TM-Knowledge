"""The examiner's explorer: the data behind the site at `site/`.

`build.py` arranges what the repository already holds — concepts, relationships,
the snapshot's passages, the benchmark — into the JSON the explorer reads. It
writes no knowledge. The owner's workbench, the older dashboard, is
`tm_knowledge.dashboard` and lives at `site/workbench/` (ADR-0118).
"""

__all__ = ["build", "cli"]

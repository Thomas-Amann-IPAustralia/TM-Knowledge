# .github/ — repository automation

**Belongs here:** GitHub Actions workflows, and issue or pull-request templates
if the repo ever grows them.

**Does not belong here:** anything that produces project content. CI in this repo
checks and reports; it does not extract, generate or approve. A workflow that
wrote into `vocab/`, `ontology/`, `graph/` or `eval/gold/` would be minting
knowledge without a human decision, which is what CLAUDE.md rule 4 forbids.

## workflows/harness.yml

Runs the test suite and the Stage 0 harness on every push. Read its header
comment before changing it: the split between *this build is broken* and *Stage 0
has not arrived yet* is deliberate and is ADR-0018, not a convenience.

One optional secret, `UPSTREAM_TOKEN`, lets CI fetch the pinned snapshot when the
upstream repository is private. Without it the snapshot step fails, every check
that needs the corpus skips, and the run summary says so. That is a degraded run,
not a passing one — the skips are visible on purpose.

# data/ — the pinned upstream snapshot and derived intermediates

**Nothing in here is committed** except this README and the pin manifest
(ADR-0004). Empty until a fetch step exists.

```
data/upstream/     pinned manual-XtrACTor snapshot   — git-ignored
data/derived/      caches, embeddings, intermediates — git-ignored, always rebuildable
data/pin.json      the pinned upstream version       — tracked
```

## The pin

`pin.json` records which upstream release this working copy is reading, so a run
is reproducible and so corpus counts quoted elsewhere mean something:

```json
{
  "repo": "Thomas-Amann-IPAustralia/manual-XtrACTor",
  "commit": "",
  "manual_ingest_version": "0.11.0",
  "legislation_version": "0.2.0",
  "fetched_at": ""
}
```

Bumping the pin is a deliberate act with consequences: passage `content_hash`
values change, and every assertion resting on a changed passage becomes stale and
returns to review (`docs/IDENTIFIERS.md` §5). Bump it in its own commit, and say
what moved.

## Rules

- **Read-only.** Nothing in this repo writes into `data/upstream/`. If upstream
  data is wrong, log it in `docs/QUIRKS.md` and raise it upstream (ADR-0002).
- **No hand edits, ever** — a local correction that is not in the snapshot is an
  invisible fork of the corpus.
- `data/derived/` must be deletable at any moment without loss. If something in
  there cannot be rebuilt from `data/upstream/` plus `src/`, it is in the wrong
  directory.
- Fetching is scripted, not documented as manual steps. A bare clone plus one
  command should be enough.

## Getting the snapshot

The upstream repo is **not attached to an agent session by default** (Q-13).
Attach it deliberately with `add_repo` (owner `Thomas-Amann-IPAustralia`, repo
`manual-XtrACTor`) — do not pre-check with `curl` or `git ls-remote` first, since
an unauthenticated 404 on a private repo tells you nothing.

If you need the corpus *history* rather than its current state — anything
point-in-time — clone with full history. Upstream's git log **is** the amendment
log (Q-05, Q-14).

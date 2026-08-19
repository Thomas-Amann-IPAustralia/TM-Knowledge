# data/ — the pinned upstream snapshot and derived intermediates

**Nothing in here is committed** except this README and the pin manifest
(ADR-0004). One command fills it: `tmk-fetch-upstream`.

```
data/upstream/            pinned manual-XtrACTor snapshot   — git-ignored
data/upstream/.fetch.json the receipt for THIS fetch        — git-ignored
data/derived/             worksheet, recon and coverage reports — git-ignored, always rebuildable
data/pin.json             the pinned upstream version       — tracked
```

## The pin

`pin.json` records which upstream release this working copy is entitled to read,
so a run is reproducible and so corpus counts quoted elsewhere mean something. It
holds only properties of the *pinned release* — a fetch-time field in a tracked
file churns on every run and says nothing about what was pinned (ADR-0026).

Upstream publishes no releases and no tags, so the pin is a **commit sha**,
fetched by sha (Q-19). Its default branch is not even its newest state: scheduled
crawl branches run ahead of `main`, so "latest" is ambiguous upstream and the pin
must be explicit.

Three checks run before anything is read, and a snapshot failing any of them is
refused: the receipt names the pinned commit, the corpus counts match, and a
tree digest over the pinned paths matches. The digest is the only one that
catches a hand edit.

```bash
tmk-fetch-upstream                  # fetch the pinned commit; verify; write the receipt
tmk-fetch-upstream --verify         # verify what is on disk; no network
tmk-fetch-upstream --force          # discard and re-fetch
tmk-fetch-upstream --write-digest   # record the digest into the pin (deliberate act)
```

Bumping the pin is a deliberate act with consequences: passage `content_hash`
values change, and every assertion resting on a changed passage becomes stale and
returns to review (`docs/IDENTIFIERS.md` §5). Bump it in its own commit, recompute
the digest and the counts, and say what moved.

## Rules

- **Read-only.** Nothing in this repo writes into `data/upstream/`. If upstream
  data is wrong, log it in `docs/QUIRKS.md` and raise it upstream (ADR-0002).
- **No hand edits, ever** — a local correction that is not in the snapshot is an
  invisible fork of the corpus.
- `data/derived/` must be deletable at any moment without loss. If something in
  there cannot be rebuilt from `data/upstream/` plus `src/`, it is in the wrong
  directory.
- Fetching is scripted, not documented as manual steps. A bare clone plus one
  command is enough, and that command is `tmk-fetch-upstream`.
- An upstream field the loader does not recognise **stops the load** rather than
  being dropped. Schema drift is the event the pin exists to make visible.

## Getting the snapshot

`tmk-fetch-upstream` does it, and needs no repository attached: `manual-XtrACTor`
is public and this environment's git proxy serves anonymous reads of it (Q-13, as
amended). GitHub *API* access still needs the repo attached with `add_repo` — the
releases and tags endpoints refuse without it — but nothing in the fetch path
uses the API.

If you need the corpus *history* rather than its current state — anything
point-in-time — clone with full history. Upstream's git log **is** the amendment
log (Q-05, Q-14).

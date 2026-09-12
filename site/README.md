# site/ — the dashboard

A static site, published to
<https://thomas-amann-ipaustralia.github.io/TM-Knowledge/>.

It exists to do two things: let someone who does not read Turtle understand the
shape of the ontology, the vocabulary and the graph — and let the repo owner
answer the questions that are waiting on them.

## What belongs here

Hand-written: `index.html`, `app.css`, `app.js`, `blocks.js`, `md.js`,
`inbox.js`, `network.js`, `tree.js`. That is the whole site. No framework, no
package manager, no build step, nothing loaded from a CDN — this is published by
a government agency and every byte it serves is in this repository. A test
asserts that, and it is why the force layout on the map is about eighty lines of
arithmetic rather than a graph library.

Generated: everything under `data/`, written by `tmk-dashboard --write` from
`src/tm_knowledge/dashboard/`. **Do not hand-edit a file in `data/`.** It is
regenerated on every deploy and a hand edit would be silently overwritten. CI
fails if what is committed there differs from a regeneration.

## What does not belong here

Content. The site restates committed artefacts and authors nothing: if a
sentence on the page is not in `src/tm_knowledge/dashboard/build.py`, in a
generated report, or in `review/questions/open-questions.yaml`, it should not
exist. In particular, no page may state a legal proposition, a definition or a
judgement that is not already in an approved record (CLAUDE.md rule 1).

**Two pages arrange rather than restate, and they are the exception that proves
the rule** (ADR-0103). *The map* and *the examination path* put records next to
each other in an order nothing in the repository states. That is allowed on
three conditions, and a change that breaks any of them is a defect:

1. **The arrangement rule is computed in Python**, in
   `src/tm_knowledge/dashboard/views.py`, on every build. Not stored, not
   hand-maintained, and never decided in the JavaScript.
2. **Every node and every edge carries the rule that put it there** — which
   field of which record, or which of the tree's four attachment rules — so a
   reader can check the arrangement against the records.
3. **The rules are printed on the page**, and the page says in its own lede that
   nobody has reviewed the arrangement.

## How it is put together

    site.json      nav, the build stamp, the upstream pin
    glossary.json  docs/GLOSSARY.md, parsed — the tooltips are the project's
                   own words, so a term cannot be explained two ways
    <page>.json    { title, lede, blocks: [...] }
    reports/*.md   copies of data/derived/reports/, fetched and rendered whole

Ten of the eleven pages are a list of **blocks** — `stats`, `prose`, `callout`,
`table`, `cards`, `bars`, `list`, `report`, `network`, `tree` — and `blocks.js`
has one renderer per kind and knows nothing about trade marks. The eleventh is
the decision form, which has state and owns `inbox.js`.

`network` and `tree` are big enough to own a file each — `network.js` and
`tree.js` — and they are still only renderers: they decide where a dot goes and
what is dimmed, never which dots exist or what joins them. Both are canvases the
reader moves around in: pan, zoom, and **drag a node** — on the map it stays
where it is dropped, on the tree its whole branch travels with it. The map opens
on one idea and grows a hop at a time (ADR-0107); the tree opens on the eleven
section questions with each *yes* branch still folded (ADR-0106). Every concept
node on both shows **the passage its record quotes** (ADR-0108).

Two traps live in these two files and both are recorded. A renderer must not
measure anything on its first pass — a block is detached until the router
appends it, so `offsetHeight` reads 0 with no error (Q-63) — and the map's force
constants must be measured rather than eyeballed after a change (Q-62).

That split is the point, and it is what makes the site cheap to change as the
ontology moves:

| To change… | Edit |
|---|---|
| what a page says or counts | `src/tm_knowledge/dashboard/build.py` |
| what is being asked of the owner | `review/questions/open-questions.yaml` |
| how a kind of block looks | `blocks.js` and `app.css` |
| what a term means in a tooltip | `docs/GLOSSARY.md` |
| adding a page | one builder in `build.py`, one line in `PAGES` |
| which concepts and edges are drawn | `views.py` — never the JavaScript |
| how the map or the tree *looks* | `network.js` / `tree.js` and `app.css` |

Anything in prose may carry a `{{glossary term}}` marker, which becomes a
tooltip. A marker naming a term `docs/GLOSSARY.md` does not define **fails the
build** — a tooltip that silently does not appear is an explanation withdrawn
from the reader who needed it.

## Running it locally

```bash
pip install -e ".[rdf]"
tmk-dashboard --write
python3 -m http.server -d site 8000    # then open http://localhost:8000
```

Opening `index.html` from disk will not work: the browser blocks `fetch` on
`file://`, so the data never loads. Serve the directory.

## Deployment

`.github/workflows/pages.yml` regenerates the data and publishes on every push
to `main` that touches anything the site reads. It needs the repository setting
**Settings → Pages → Build and deployment → Source: GitHub Actions** — which is
set — and without it the workflow would run green and publish nothing.

It also carries `workflow_dispatch`, so the site can be rebuilt on demand from
**Actions → pages → Run workflow** without pushing a commit.

**Before concluding the site is stale, check.** A page showing something the
repository no longer holds is a real failure mode, and a page that merely *looks*
wrong is more often a rendering bug. These two answer it:

```bash
curl -s https://thomas-amann-ipaustralia.github.io/TM-Knowledge/data/inbox.json \
  | diff - site/data/inbox.json          # what is published vs what is committed
tmk-dashboard --write && git status --short site/data/   # committed vs regenerated
```

The footer's *"Generated …"* stamp answers the same question for a reader who has
no checkout.

The build reads committed artefacts only — no upstream snapshot, no network —
so a deploy cannot fail because upstream was unreachable, and the page cannot
show a figure it did not measure. Figures that exist only in the rebuilt source
graph are not restated here at all; the generated reports carry them.

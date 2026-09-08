# site/ — the dashboard

A static site, published to
<https://thomas-amann-ipaustralia.github.io/TM-Knowledge/>.

It exists to do two things: let someone who does not read Turtle understand the
shape of the ontology, the vocabulary and the graph — and let the repo owner
answer the questions that are waiting on them.

## What belongs here

Hand-written: `index.html`, `app.css`, `app.js`, `blocks.js`, `md.js`,
`inbox.js`. That is the whole site. No framework, no package manager, no build
step, nothing loaded from a CDN — this is published by a government agency and
every byte it serves is in this repository. A test asserts that.

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

## How it is put together

    site.json      nav, the build stamp, the upstream pin
    glossary.json  docs/GLOSSARY.md, parsed — the tooltips are the project's
                   own words, so a term cannot be explained two ways
    <page>.json    { title, lede, blocks: [...] }
    reports/*.md   copies of data/derived/reports/, fetched and rendered whole

Eight of the nine pages are a list of **blocks** — `stats`, `prose`, `callout`,
`table`, `cards`, `bars`, `list`, `report` — and `blocks.js` has one renderer
per kind and knows nothing about trade marks. The ninth is the decision form,
which has state and owns `inbox.js`.

That split is the point, and it is what makes the site cheap to change as the
ontology moves:

| To change… | Edit |
|---|---|
| what a page says or counts | `src/tm_knowledge/dashboard/build.py` |
| what is being asked of the owner | `review/questions/open-questions.yaml` |
| how a kind of block looks | `blocks.js` and `app.css` |
| what a term means in a tooltip | `docs/GLOSSARY.md` |
| adding a page | one builder in `build.py`, one line in `PAGES` |

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

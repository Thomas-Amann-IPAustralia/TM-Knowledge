# site/ — the examiner explorer

A static site, published to <https://thomas-amann-ipaustralia.github.io/TM-Knowledge/>.
It exists to show a trade marks examiner, quickly, what the ontology is and what it is
for (ADR-0118). The owner's older dashboard is kept at `site/workbench/` and linked from
nothing here.

## What belongs here

Hand-written: `index.html`, `explorer.css`, and the modules in `js/`. No build step and
no package manager at run time.

Vendored: libraries and fonts in `vendor/` (ADR-0119) — Cytoscape.js, D3, Observable
Plot, marked, DOMPurify, Fuse.js, Inter, Source Serif 4 — each pinned in
`vendor/manifest.json` with its SHA-256 and licence. Nothing is loaded from a CDN; every
byte is in this repository, and `tests/unit/test_explorer.py` asserts both that and the
checksums. `js/lib.js` loads each library only on the view that needs it.

Generated: everything under `data/`, written by `tmk-explorer --write` from
`src/tm_knowledge/explorer/`. **Do not hand-edit it; it is not committed** (ADR-0112).

| File | What it holds |
|---|---|
| `data/ontology.json` | kinds, concepts, relationships, kind-to-kind roll-ups, predicates |
| `data/search.json` | what the browser needs to recognise concepts and rank passages |
| `data/passages.json` | every Manual passage and provision, verbatim (the snapshot's) |
| `data/stability.json` | the Manual's amendment history and what rests on each page |
| `data/tour.json` | the Manual by Part, ideas named many ways, one worked example |
| `data/examples.json` | the 129 prepared answers and each search system's score |
| `data/chat.json` | the measured answer prompt, verbatim, for live questions |
| `data/live.json` | whether live answers are on — and, if so, the masked key. **Never commit it.** |

## What does not belong here

A legal proposition of the page's own. Every concept, relationship, quote and answer
shown is a record that already exists, with who wrote it on its face: *expert-signed*,
or *machine · unreviewed* (CLAUDE.md rules 4 and 8). Every arrangement — which kind an
idea sits in, the kind-to-kind patterns, what rests on a page — is computed in Python by
`tmk-explorer`, never decided in the JavaScript. The page's own prose explains what to
look at; it does not state the law.

## The views

| Route | Module | What it shows |
|---|---|---|
| `#/` | `home.js` | a zoomable circle packing of the ontology (D3): families → kinds → ideas |
| `#/tour/N` | `tour.js` | seven steps: text, wordings, connections, kinds, change, retrieval, limits; in steps 1–2 each square says which passage it is |
| `#/map/{kinds,ideas,text}/GC-…` | `map.js` | Cytoscape: kinds open and close as boxes; an idea opens into Parts, then passages |
| `#/ask/BN-…` | `ask.js` | a question's ideas, connections and passages drawn hop by hop; the same ideas on a mini map (Cytoscape) beside a plain account of how the starting ideas were found and why no connection is preferred; then a streamed, cited answer |
| `#/change/TMM/…` | `change.js` | an amendment timeline (Plot) and every page as a tile in its Part's row, titles in full; pick one to see the ripple, and what rests on it on a mini map |
| `#/about` | `about.js` | what it is, how it works, the measurement as intervals (Plot), the limits |

The map's positions are **computed, not simulated** (`graphPositions`, `textPositions`):
closed kinds sit where the tour draws them, open kinds pack into their family's region,
ideas grid inside each box. A force layout overlapped the boxes (ADR-0119).

`minimap.js` embeds a small Cytoscape map in other views — the same marks as the map,
the caller choosing which records to draw. Its positions are computed too: a ring round
the ideas in the middle (Ask), or a seeded D3 force run to rest (Change), which is safe
there because there are no compound boxes and the same input always gives the same
picture. Wheel-zoom is off so the page still scrolls over it; the buttons zoom.

`engine.js` is the browser's copy of `search.index.Systems` (keyword and ontology, no
vectors) plus the answer prompt and the verbatim quote check. **It must stay identical to
Python**: `tests/explorer_parity.mjs` runs it under Node and the test compares rankings,
recognised concepts, paths and the prompt itself, question by question. Change one side,
change the other. `live.js` makes the streamed model call; `kinds.js` draws the tour's
kinds diagram; `minimap.js` is the embedded map; `graph.js` holds small SVG helpers;
`app.js` routes, loads data and draws the passage drawer.

## Live answers

On when the Pages workflow has the `OPENAI_API_KEY` secret (ADR-0118). The key is then
**in the published page**, masked against scrapers but recoverable by anyone who reads
it — so it should be a dedicated, restricted, budget-limited key. Setting the repository
variable `TMK_LIVE_ENDPOINT` to a proxy that holds the key publishes no key instead. With
neither, the site works with live answers off: retrieval still runs and the 129 prepared
answers still show.

## Running it locally

```bash
pip install -e ".[rdf]"
tmk-fetch-upstream                 # the explorer needs the pinned snapshot (ADR-0117)
tmk-explorer --write               # add TMK_LIVE_OPENAI_KEY=… to try live answers locally
tmk-dashboard --write              # only if you want the workbench too
python3 -m http.server -d site 8000   # then open http://localhost:8000
```

Opening `index.html` from disk will not work: browsers block `fetch` on `file://`.

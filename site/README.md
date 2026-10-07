# site/ — the examiner explorer

A static site, published to <https://thomas-amann-ipaustralia.github.io/TM-Knowledge/>.
It exists to show a trade marks examiner, quickly, what the ontology is and what it is
for (ADR-0118). The owner's older dashboard is kept at `site/workbench/` and linked from
nothing here.

## What belongs here

Hand-written: `index.html`, `explorer.css`, and the modules in `js/`. No framework, no
package manager, no build step, nothing loaded from a CDN, no web fonts — every byte is
in this repository, and `tests/unit/test_explorer.py` asserts it.

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
| `#/` | `home.js` | what this is, and the four levels from kinds down to text |
| `#/tour/N` | `tour.js` | seven steps: text, wordings, connections, kinds, change, retrieval, limits |
| `#/map/{kinds,ideas,text}/GC-…` | `map.js` | the ontology at three levels; the same nodes move between them |
| `#/ask/BN-…` | `ask.js` | a question's ideas, connections and passages drawn hop by hop, then a cited answer |
| `#/change/TMM/…` | `change.js` | pick a page; see what a rewrite would touch, layer by layer |
| `#/about` | `about.js` | what it is, how it works, the measurement both ways, the limits |

`engine.js` is the browser's copy of `search.index.Systems` (keyword and ontology, no
vectors) plus the answer prompt and the verbatim quote check. **It must stay identical to
Python**: `tests/explorer_parity.mjs` runs it under Node and the test compares rankings,
recognised concepts, paths and the prompt itself, question by question. Change one side,
change the other. `live.js` makes the model call; `graph.js` holds the force layout, pan
and zoom; `app.js` routes, loads data and draws the passage drawer.

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

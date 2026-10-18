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
| `data/chat.json` | the measured answer prompt, verbatim, for live questions; and the live-only reading prompt (ADR-0132) |
| `data/live.json` | whether live answers are on, and the proxy they go through. No key, ever |

## What does not belong here

A legal proposition of the page's own. Every concept, relationship, quote and answer
shown is a record that already exists, with who wrote it on its card: *Machine ·
unreviewed*, loud, on every machine-written record (CLAUDE.md rule 8), or a plain grey
*Reviewed*, with no name, on one an expert reviewed (rule 4). The pictures draw every
record alike: the site is shared with many experts and marks one expert's review
without featuring it (ADR-0130). Every arrangement — which kind an
idea sits in, the kind-to-kind patterns, what rests on a page — is computed in Python by
`tmk-explorer`, never decided in the JavaScript. The page's own prose explains what to
look at; it does not state the law.

## The views

| Route | Module | What it shows |
|---|---|---|
| `#/` | `home.js` | what this is, the four levels and the ways in — kept plain |
| `#/circles` | `circles.js` | "At a glance": a zoomable circle packing of the ontology (D3): families → kinds → ideas |
| `#/table/{kinds,ideas,connections}` | `table.js` | "As a table": the same records listed, not drawn — the kinds and how they connect, every idea (open a row for its connections as sentences), every connection; filters, and a CSV of each table with who wrote every row |
| `#/tour/N` | `tour.js` | seven steps: text, wordings, connections, kinds, change, retrieval, limits; in steps 1–2 each square says which passage it is |
| `#/map/{kinds,ideas,text}/GC-…` | `map.js` | Cytoscape: kinds open and close as boxes; an idea opens into Parts, then passages, with the Act and the Regulations in boxes of their own |
| `#/ask/BN-…` | `ask.js` | a question's ideas, connections and passages drawn hop by hop; the same ideas on a mini map (Cytoscape) beside a plain account of how the starting ideas were found and why no connection is preferred; then a streamed, cited answer |
| `#/change/TMM/…` | `change.js` | an amendment timeline (Plot) and every page as a tile in its Part's row, titles in full; pick one to see the ripple, and what rests on it on a mini map |
| `#/about` | `about.js` | what it is, how it works, the measurement as intervals (Plot), the limits |

**An idea's card shows its own record's fields**, on the map and in the table alike: its
labels, its definition (`GD-`, stamped), what it rests on, its legislative basis, and the
"is a kind of" links its record states (`hierarchy`), which no connection carries and so
are listed, never drawn (Q-96).

**The Manual, the Act and the Regulations each have a colour and a mark** — a blue
square, an amber diamond, a plum hexagon — wherever a passage appears: map nodes and
boxes, chips (`refChip`), quotes headed by their source (`quoteBlock`), Ask's diagram.
Use `srcClass`, `quoteBlock` and `legend` from `app.js` in a new view, so the three stay
one system (ADR-0130).

The map's positions are **computed, not simulated** (`graphPositions`, `textPositions`):
closed kinds sit where the tour draws them, open kinds pack into their family's region,
ideas grid inside each box. A force layout overlapped the boxes (ADR-0119).

`table.js` is for anyone the map overwhelms: plain HTML tables, no library. Every row is
a record or a `kind_links` count; a CSV carries the same trust columns as the page —
machine-written and unreviewed, or reviewed, never the reviewer's name (ADR-0130) — and
says whether each quote is from the Manual, the Act or the Regulations.

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

On when the repository variable `TMK_LIVE_ENDPOINT` names the proxy that holds the key
(ADR-0118): `live-proxy/` is that proxy, and its README says how to run it on Render's free
plan. It also gets through networks that block `api.openai.com`. No key is in the page.
Until ADR-0136 a build with the `OPENAI_API_KEY` secret and no proxy published the key,
masked; the owner removed that fallback once the proxy served, and the old key is the
owner's to revoke. Without a proxy the site works with live answers off: retrieval still
runs and the 129 prepared answers still show.

`live.js` turns the browser's bare "Failed to fetch" into words (no reply came back, so the
network or an extension stopped the request; a wrong model or exhausted credit is a reply,
and shows OpenAI's message). The Ask page knocks on the proxy's `/health` as it opens, and
says so when an answer is slow to start, since a free host sleeps when idle.

Before the search, a live question is read by the model against the map (ADR-0132): which
ideas it raises in other words ("a smell" is a scent trade mark). Each pick is checked —
on the map, specific, its words in the question — and starts the search as a name would,
marked "read by the model" in the diagram. The prepared answers, and the measured system
the page is checked against, recognise by names alone.

## Running it locally

```bash
pip install -e ".[rdf]"
tmk-fetch-upstream                 # the explorer needs the pinned snapshot (ADR-0117)
tmk-explorer --write               # add TMK_LIVE_ENDPOINT=<proxy URL> to try live answers locally
tmk-dashboard --write              # only if you want the workbench too
python3 -m http.server -d site 8000   # then open http://localhost:8000
```

Opening `index.html` from disk will not work: browsers block `fetch` on `file://`.

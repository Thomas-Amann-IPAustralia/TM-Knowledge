# site/: the explorer

A static site, published to <https://thomas-amann-ipaustralia.github.io/TM-Knowledge/> from
`main` (ADR-0112). Its job is to communicate the value of the ontology by **leading with what it
makes possible** and explaining how it works simply and visually, with the detail one step behind
a disclosure (ADR-0145; redesigned on the owner's instruction in ADR-0148).

The pages come in four layers, outcomes first, and a card at the foot of each leads one layer
deeper (`layers.js`):

1. **What it does**: the Overview, Research (Ask the Manual), Explain (the customer preview) and
   Trace a change.
2. **What it could do**: What's next, the uses the same foundation could support.
3. **How it works**: a nine-step scrolling story over one picture, the knowledge map, and rules as
   code.
4. **Under the hood**: the standards, the glossary and the data tables.

"Where it stands" (`#/about`) sits across them all. The header names the outcome pages first,
then How it works and the Knowledge map. `glossary.js` holds every term the site explains, and
`term(key)` explains one inline the first time a page uses it. The owner's older dashboard is
kept at `site/workbench/` and linked from nothing here.

Desktop and laptop screens only, by the owner's word: nothing is designed for a phone.

## What belongs here

Hand-written: `index.html`, `explorer.css`, and the modules in `js/`. No build step and no
package manager at run time.

Vendored: libraries and fonts in `vendor/` (ADR-0119): D3, Observable Plot, marked, DOMPurify,
Fuse.js, Inter and Source Serif 4, each pinned in `vendor/manifest.json` with its SHA-256 and
licence. Nothing is loaded from a CDN; every byte is in this repository, and
`tests/unit/test_explorer.py` asserts both that and the checksums. `js/lib.js` loads each library
only on the view that needs it.

Generated: everything under `data/`, written by `tmk-explorer --write` from
`src/tm_knowledge/explorer/`. **Do not hand-edit it; it is not committed** (ADR-0112).

| File | What it holds |
|---|---|
| `data/ontology.json` | kinds, concepts, relationships, kind-to-kind roll-ups, predicates; the structured legal tests and process templates (`structures`) |
| `data/search.json` | what the browser needs to recognise concepts and rank passages |
| `data/passages.json` | every Manual passage and provision, verbatim (the snapshot's) |
| `data/stability.json` | the Manual's amendment history, what rests on each page, and what rests on each provision |
| `data/tour.json` | the Manual by Part, ideas named many ways, one worked example (the Overview's opening question) |
| `data/examples.json` | the 129 prepared answers and each search system's score |
| `data/chat.json` | the measured answer prompt, verbatim, for live questions; and the live-only reading prompt (ADR-0132) |
| `data/live.json` | whether live answers are on, and the proxy they go through. No key, ever |
| `data/explain.json` | the customer preview: every invented matter's explanation, each test's requirements and each process walked through, from `tm_knowledge.explain`, each with its text equivalent and stamp |
| `data/build.json` | the release manifest: what was built from what; the checks (shapes and inference rules, counted from their files); two machine-written blocks of the committed graph for the standards page |

## What does not belong here

A legal proposition of the page's own. Every concept, relationship, quote and answer shown is a
record that already exists, with who wrote it on its card: *Machine · unreviewed*, loud, on every
machine-written record (CLAUDE.md rule 8), or a plain grey *Reviewed*, with no name, on one an
expert reviewed (rule 4). The pictures draw every record alike: the site is shared with many
experts and marks one expert's review without featuring it (ADR-0130). Every arrangement (which
kind an idea sits in, the kind-to-kind patterns, what rests on a page) is computed in Python by
`tmk-explorer`, never decided in the JavaScript. The page's own prose explains what to look at; it
does not state the law, and nothing on the site says how an application will be decided.

A number typed into the page. Every figure is read from `data/`, so the page cannot drift from
the build; the tests pin the few places that matter (the measurement in both directions on the
Overview, the counts on the standards page).

## The design system

One stylesheet, `explorer.css`, light theme only (ADR-0148 says why). Paper and deep green, with
lime as the highlight; Source Serif 4 for headings and quotes, Inter for everything else. Two
colour systems that never mix, both checked for colour-blind readers with the data-visualisation
validator:

- **Ideas are coloured by their family**: the law's questions (orange), what they are asked about
  (teal), the process around them (violet). Each kind takes its family's colour; position and
  label say which kind.
- **Passages are coloured by their source, and each source has its own mark**: the Manual a blue
  square, the Act an amber diamond, the Regulations a plum hexagon, wherever a passage appears
  (chips, quotes, the map's satellites, Ask's diagram). Use `srcClass`, `refChip`, `quoteBlock`,
  `srcShape` and `legend` from `app.js` in a new view, so the three stay one system (ADR-0130).

Machine-written content is a dashed rust stamp everywhere (`trustBadge`, `.stamp`); states are
said in words as well as colour (`statePill`: working, measured, prototype, planned). Every picture
has a text equivalent or says in words what its colours mean. Each view's classes carry a short
prefix (`hm-` Overview, `rs-` Research, `cx-` Explain, `ch-` Trace a change, `fu-` What's next,
`hw-` How it works, `mp-` the map, `rx-` rules, `sd-` standards, `gv-` glossary, `ab-` Where it
stands, `dg-` the shared diagrams), so a view's class never picks up another's layout (Q-101).

## The views

| Route | Module | What it shows |
|---|---|---|
| `#/` | `home.js` | the Overview: one question answered with and without the map of meaning; what it does for examiners, customers and policy; why it works; the measurement in both directions; the foundation; where things stand |
| `#/ask/BN-…` | `ask.js` | Research: a question's ideas, connections and passages drawn hop by hop, the Act and the Regulations kept apart from the Manual, then a streamed, cited answer with the unreviewed stamp; plain search beside it |
| `#/customers/{requirements,process,objection}/…` | `customers.js` | Explain: the customer explanation preview, on invented matters, behind a banner (ADR-0146): what a test requires, the application process drawn as a journey, an objection as a checklist with the full diagram a click away; each with its text equivalent |
| `#/change/…` | `change.js` | Trace a change: pick a page or a provision and see what rests on it, drawn as a ripple, with the amendment timeline (Plot) |
| `#/future/customers?` | `future.js` | What's next: the uses one foundation could support, each with what it stands on, what it would still need and where it stands; what may be tested with customers |
| `#/how` | `how.js` | How it works: nine scrolling steps over one picture, from the text to the answer and who wrote what |
| `#/map`, `#/map/ideas/GC-…`, `#/map/kinds` | `map.js` | the knowledge map (below) |
| `#/rules` | `rules.js` | rules as code: the three forms drawn small; connections with their modality and condition; section 44 drawn as a diagram and the process from filing as a journey (`diagrams.js`), each with its text equivalent; how the rules are checked; what they never do |
| `#/standards` | `standards.js` | the standards stacked as one clickable picture, the four compartments drawn to scale; then each in three parts (plain words, what it does here with a real block of the graph, what it is not) |
| `#/glossary/term?` | `glossary-view.js` | every term from `glossary.js`, grouped and filterable; every inline explanation links to its entry |
| `#/table/{kinds,ideas,connections,tests,processes}/…` | `table.js` | the same records listed, not drawn, with filters and a CSV of each table carrying who wrote every row and which text each quote is from |
| `#/about` | `about.js` | Where it stands: the measurement as intervals said in words (better, worse, not established), the decisions ahead and whose they are, who wrote what, the release manifest, the limits |

Older routes still work: `#/tour` and `#/model` open How it works, and `#/circles` opens the
map's Kinds view (`ALIASES` in `app.js`).

## The knowledge map

Every idea is a dot in its family's colour, sized by how often the Manual names it. The positions
come from a seeded force layout run to rest before anything is drawn (`netlayout.js`, measured
offline, Q-62), shaped to the frame it is drawn in, so the same data always gives the same picture
and nothing moves under the reader. Hover over an idea to see its neighbourhood; click it to focus
it: its connections are labelled with what they say, and the passages and provisions it rests on
gather round it as satellites in their sources' marks. Names are placed so none overlaps another:
the most connected ideas are named first and the rest appear as the reader zooms in; text and
strokes keep their size at any zoom. The card on the right holds everything the idea's record
says: its definition, what it rests on, its basis in the Act and the Regulations, the "is a kind
of" links its record states (`hierarchy`, listed, never drawn, Q-96), the structured tests and
procedures that name it, each connection with the sentence it rests on ("Why?"), and who wrote
it. The Kinds view rolls the connections up between the kinds of idea.

**Structured legal tests and process templates** (Package 4, ADR-0142) are records of their own,
not connections, so the map does not draw them: an idea's card lists those that name it
(`structuresBlock`), rules as code draws two of them, and the table sets each out element by
element. They are shown as written; the page evaluates no condition and computes no date.

## The other modules

`engine.js` is the browser's copy of `search.index.Systems` (keyword and ontology, no vectors)
plus the answer prompt and the verbatim quote check. **It must stay identical to Python**:
`tests/explorer_parity.mjs` runs it under Node and the test compares rankings, recognised
concepts, paths and the prompt itself, question by question. Change one side, change the other.
`live.js` makes the streamed model call; `diagrams.js` draws a legal test and a process;
`netlayout.js` lays out the ideas for the map and How it works; `icons.js` holds the line icons;
`graph.js` holds small SVG helpers for Ask's diagram; `app.js` routes, loads data, holds the
shared helpers and draws the passage drawer.

## Live answers

On when the repository variable `TMK_LIVE_ENDPOINT` names the proxy that holds the key
(ADR-0118): `live-proxy/` is that proxy, and its README says how to run it on Render's free plan.
It also gets through networks that block `api.openai.com`. No key is in the page. Until ADR-0136 a
build with the `OPENAI_API_KEY` secret and no proxy published the key, masked; the owner removed
that fallback once the proxy served, and the old key is the owner's to revoke. Without a proxy the
site works with live answers off: retrieval still runs and the 129 prepared answers still show.

`live.js` turns the browser's bare "Failed to fetch" into words (no reply came back, so the
network or an extension stopped the request; a wrong model or exhausted credit is a reply, and
shows OpenAI's message). The Ask page knocks on the proxy's `/health` as it opens, and says so
when an answer is slow to start, since a free host sleeps when idle.

Before the search, a live question is read by the model against the map (ADR-0132): which ideas it
raises in other words ("a smell" is a scent trade mark). Each pick is checked (on the map,
specific, its words in the question) and starts the search as a name would, marked "read by the
model" in the diagram. The prepared answers, and the measured system the page is checked against,
recognise by names alone.

## Running it locally

```bash
pip install -e ".[rdf]"
tmk-fetch-upstream                 # the explorer needs the pinned snapshot (ADR-0117)
tmk-explorer --write               # add TMK_LIVE_ENDPOINT=<proxy URL> to try live answers locally
tmk-dashboard --write              # only if you want the workbench too
python3 -m http.server -d site 8000   # then open http://localhost:8000
```

Opening `index.html` from disk will not work: browsers block `fetch` on `file://`.

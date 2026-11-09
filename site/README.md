# site/: the explorer

A static site, published to <https://thomas-amann-ipaustralia.github.io/TM-Knowledge/> from
`main` (ADR-0112). Its job is to show what the knowledge foundation makes possible for each group it
serves, with working demonstrations, and to explain how it works for those who want to know
(ADR-0145; redesigned in ADR-0148; organised by audience on the owner's word in ADR-0151).

The pages come in five sections (`layers.js`), and a card at the foot of each page says where to go
next:

1. **Overview** (`#/`): the headline and one real rule turned from the Act's words into structure
   (nothing else in the hero, on the owner's annotations, ADR-0153), a door for each group, one
   foundation under many tools (working demonstrations and possible future uses, in two rows), the
   safeguards and the work still to do.
2. **For examiners**: the overview (`#/examiners`) and two working demonstrations, Explore a legal
   concept (`#/concepts`) and Ask a research question (`#/ask`).
3. **For the public**: the overview (`#/public`), the trade marks guide (`guide/`, a page of its own,
   below) and the customer explanation preview (`#/customers`): an objection step by step, what a
   rule requires, and the application journey, on invented matters.
4. **For direction setting**: the overview (`#/direction`), Trace a change (`#/change`) and the
   what-if, a new right laid over the ontology (`#/whatif`).
5. **For nerds** (`#/nerds`): how the foundation works in four steps, then a search followed step by
   step (`#/how`), the knowledge map, rules as code, the standards, the data tables, results and
   limits (`#/about`) and the glossary.

Each audience section leads with what works and then shows three possibilities, each with a horizon
said in words (working demonstration, builds on current work, needs more data), and folds the rest under "Other
possibilities" (`possibilityGrid`). A deep page carries a breadcrumb back to its section (`crumb` in
`layers.js`). A link to a place on the same page (`href="#id"`) is caught by `app.js` before the
router (Q-110). `glossary.js` holds every term the site
explains, and `term(key)` explains one inline the first time a page uses it. The owner's older
dashboard is kept at `site/workbench/` and linked from nothing here.

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
| `data/chat.json` | the measured answer prompt, verbatim, for live questions; the live-only reading prompt (ADR-0132); and the guide's prompt, schema and picture catalogue (`guide`, ADR-0154) |
| `data/live.json` | whether live answers are on, and the proxy they go through. No key, ever |
| `data/whatif.json` | a what-if (ADR-0149): an invented new right laid over the ontology unchanged, each touch point's quotes, the records it lands on and what would go back to be re-read, from `tm_knowledge.explain.whatif` |
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
colour systems for the records that never mix, both checked for colour-blind readers with the
data-visualisation validator:

- **Ideas are coloured by their family**: the law's questions (orange), what they are asked about
  (teal), the process around them (violet). Each kind takes its family's colour; position and
  label say which kind.
- **Passages are coloured by their source, and each source has its own mark**: the Manual a blue
  square, the Act an amber diamond, the Regulations a plum hexagon, wherever a passage appears
  (chips, quotes, the map's satellites, Ask's diagram). Use `srcClass`, `refChip`, `quoteBlock`,
  `srcShape` and `legend` from `app.js` in a new view, so the three stay one system (ADR-0130).

A third set, **the audiences' tints** (ADR-0151: examiners pastel apricot since ADR-0153, the public
green, direction setting blue, For nerds near-black), is for wayfinding only: the header, the section heroes, the doors and
the cards. It sets `--acc` on `.aud-exam`, `.aud-pub`, `.aud-pol` and on `main` by section; it never
colours a record.

Machine-written content is a dashed rust stamp everywhere (`trustBadge`, `.stamp`); states are
said in words as well as colour (`statePill`; the horizons `horizonPill`, a dot and a label: working
demonstration, builds on current work, needs more data). An evidence statement is plain words (`.evid`), not a badge. In
the customer preview a recorded state is a document mark with words ("recorded: met", `STATE_WORD`
and `stateGlyph` in `diagrams.js`), never a tick: the page restates an invented report and assesses
nothing (ADR-0152). Small meaningful text uses `--ink-3`, at least 4.5:1 on every paper; `--ink-faint`
is for decorative strokes only. A legal test's conditions are marked **Fact** (a square with a tick) or
**Assessment** (a scale) wherever they appear. Every picture has a text equivalent or says in words
what its colours mean. Each view's classes carry a short prefix (`ld-` overview, `ex-` examiners,
`ce-` concept explorer, `rs-` Ask, `gd-` the guide (its own stylesheet), `pu-` public, `cx-` the public demonstrations, `dr-` direction
setting, `ch-` Trace a change, `wi-` the what-if, `nd-` For nerds, `hw-` How it works, `mp-` the
map, `rx-` rules, `sd-` standards, `gv-` glossary, `ab-` results and limits, `dg-` the shared
diagrams, `il-` and `fc-` the drawings and cards, `au-` a section's hero), and so do their state
words (Q-101, Q-108).

## The views

| Route | Module | What it shows |
|---|---|---|
| `#/` | `home.js` | the overview: section 44 from the Act's words to structure, facts and assessments marked; a door for each group; one foundation under the tools; the safeguards, the work still to do and the measurement in both directions; the door to For nerds |
| `#/examiners` | `examiners.js` | for examiners: the two demonstrations, a preview of one concept's connections with one of them and its sentence, and what could come next |
| `#/concepts/GC-…` | `concepts.js` | Explore a legal concept: the connections that lead to and from one concept as a bow-tie, each with its predicate's words, strength and condition, several records of one connection bundled with their count and each listed when selected; its names and not-names; its role in a legal test (fact or assessment); where the Manual names it, Part by Part; what it rests on; a research trail |
| `#/ask/BN-…` | `ask.js` | Ask a research question, for examiners still learning the sources (ADR-0154): a key to the labels before a question; a streamed answer read statement by statement, each labelled by what its found quotations come from (law, practice, both, no matching quotation, about the sources) with the quoted words beneath it, a count of supported statements first and four checks before relying on it; the law listed before the Manual; the concepts the question names with their definitions, and the legal test it reaches; how the sources were found (the hop diagram and keyword search beside it) folded behind "Why these sources?" |
| `#/public/customers?` | `public.js` | for the public: the three demonstrations, a preview of one invented case, what may be tested with customers and on whose decision, and what could come next |
| `#/customers/{objection,requirements,process}/…` | `customers.js` | the customer explanation preview, behind its banner (ADR-0146): an objection in six steps beside a picture of the case that lights the part each step explains, with two cases under one rule compared; what a rule requires; the application journey; each with its text equivalent |
| `#/direction` | `direction.js` | for direction setting: the provisions with the most recorded links (direct and via the Manual, not importance), the two demonstrations, and what could come next |
| `#/change/…` | `change.js` | Trace a change: what rests on a page or a provision, the exact counts first, then drawn as a ripple, with an optional guess and the amendment timeline (Plot) |
| `#/whatif/FW-…/point?` | `whatif.js` | a new right (geographical indications) above a dashed line, the ideas, provisions and legal tests it lands on below it, unchanged (ADR-0149) |
| `#/nerds` | `nerds.js` | For nerds: the build in four figures, how the foundation works in four steps, the contract in one line, and a door to each technical page |
| `#/how` | `how.js` | A search, step by step: one research question in nine scrolling steps over one picture, from the text to the answer and who wrote what |
| `#/map`, `#/map/ideas/GC-…`, `#/map/kinds` | `map.js` | the knowledge map (below) |
| `#/rules` | `rules.js` | rules as code: the three forms drawn small; connections with their modality and condition; section 44 as a diagram and the process from filing as a journey (`diagrams.js`) |
| `#/standards` | `standards.js` | the standards stacked as one clickable picture; each in plain words, with a real block of the graph, and what it is not |
| `#/glossary/term?` | `glossary-view.js` | every term from `glossary.js`, grouped and filterable |
| `#/table/{kinds,ideas,connections,tests,processes}/…` | `table.js` | the same records listed, with filters and a CSV of each table |
| `#/about` | `about.js` | results and limits: the measurement as intervals said in words, the decisions ahead and whose they are, who wrote what, the release manifest, the limits |

Older routes still work: `#/tour` and `#/model` open How it works, `#/circles` opens the map's Kinds
view, and `#/future` (What's next, retired in ADR-0151) opens the public overview (`ALIASES` in
`app.js`).

## The trade marks guide (`guide/`)

A chat for the public, on its own page with its own stylesheet (ADR-0154): `site/guide/README.md`
says what is in it. It shares the generated data and three side-effect-free modules (`engine.js`,
`live.js`, `lib.js`) and nothing else: `app.js` starts this site's router when imported (Q-112). A
live turn is Ask's pipeline with the guide's own prompt, from `chat.json`'s `guide`; its pictures
are `explain.json`'s objects, named by id. With live answers off it walks through four guided
topics from `explain.json` alone. The public overview, the overview's tool list and the footer link
to it.

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
`live.js` makes the streamed model call; `diagrams.js` draws a legal test and a process and lays a
process out (`layoutFlow`, shared with the public journey); `illustrations.js` holds the drawings on
the cards, the demonstration and possibility cards, the horizons and the line every section opens
with; `netlayout.js` lays out the ideas for the map and How it works; `icons.js` holds the line
icons; `graph.js` holds small SVG helpers for Ask's diagram; `app.js` routes, loads data, holds the
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

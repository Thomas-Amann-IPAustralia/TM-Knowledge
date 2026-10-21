# site/js/: the explorer's modules

Plain ES modules, loaded by `../index.html` through `app.js`. One module per view: `home`,
`ask`, `customers`, `change`, `future`, `whatif`, `how`, `map`, `rules`, `standards`, `glossary-view`,
`table` and `about`. Shared by them: `app.js` (router, data, the shared helpers and the passage
drawer), `layers.js` (the four layers and the card at the foot of each page, ADR-0145),
`glossary.js` (every term explained, and `term()`), `diagrams.js` (a legal test drawn as a
diagram and a process as a journey, each with its text equivalent), `netlayout.js` (where each
idea sits, for the map and How it works), `icons.js` (line icons), `graph.js` (SVG helpers for
Ask's diagram), `engine.js` (search and the answer prompt, kept identical to Python by
`tests/explorer_parity.mjs`), `live.js` (the streamed model calls: the reading of a typed
question, then the answer) and `lib.js` (loads vendored libraries per view, ADR-0119). See
`../README.md`.

Must not: decide which concepts or connections exist, author legal text, type a figure that the
data holds, load anything from outside the site (libraries come from `../vendor/` through
`lib.js` only), or fetch anything but `../data/` and the live model endpoint, which comes from
`data/live.json` and never from the code.

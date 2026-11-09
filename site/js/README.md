# site/js/: the explorer's modules

Plain ES modules, loaded by `../index.html` through `app.js`. One module per view: `home` (the
overview), `examiners`, `concepts`, `ask`, `public`, `customers`, `direction`, `change`, `whatif`,
`nerds`, `how`, `map`, `rules`, `standards`, `glossary-view`, `table` and `about`. Shared by them:
`app.js` (router, data, the shared helpers and the passage drawer), `layers.js` (the five sections
and the card at the foot of each page, ADR-0151), `illustrations.js` (the drawings, the cards that
hold them and the horizons), `glossary.js` (every term explained, and `term()`), `diagrams.js` (a
legal test drawn as a diagram and a process as a journey, each with its text equivalent),
`netlayout.js` (where each idea sits, for the map and How it works), `icons.js` (line icons),
`graph.js` (SVG helpers for Ask's diagram), `engine.js` (search and the answer prompt, kept
identical to Python by `tests/explorer_parity.mjs`), `live.js` (the streamed model calls: the
reading of a typed question, then the answer, or the guide's reply) and `lib.js` (loads vendored
libraries per view, ADR-0119). See `../README.md`.

`engine.js`, `live.js` and `lib.js` have no side effects on import, so the trade marks guide
(`../guide/`, ADR-0154) imports them too. Keep them that way: `app.js` starts the router when it
loads, and anything that imports it cannot be shared with the guide (Q-112).

Must not: decide which concepts or connections exist, author legal text, evaluate a condition or
compute a date, type a figure that the data holds, load anything from outside the site (libraries
come from `../vendor/` through `lib.js` only), or fetch anything but `../data/` and the live model
endpoint, which comes from `data/live.json` and never from the code.

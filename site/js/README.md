# site/js/ — the explorer's modules

Plain ES modules, loaded by `../index.html` through `app.js`. One module per view
(`home`, `tour`, `map`, `circles`, `ask`, `change`, `about`), plus `engine.js` (search and the answer
prompt — kept identical to Python by `tests/explorer_parity.mjs`), `live.js` (the
streamed model call), `lib.js` (loads vendored libraries per view, ADR-0119), `kinds.js`
(the tour's kinds diagram), `minimap.js` (a small Cytoscape map embedded in Ask and
Change), `graph.js` (SVG helpers) and `app.js` (router, data, shared helpers). See
`../README.md`.

Must not: decide which concepts or connections exist, author legal text, load anything
from outside the site — libraries come from `../vendor/` through `lib.js` only — or fetch
anything but `../data/` and the live model endpoint, which comes from `data/live.json`
and never from the code.

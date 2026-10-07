# site/js/ — the explorer's modules

Plain ES modules, loaded by `../index.html` through `app.js`. No dependencies and no
dynamic `import()`. One module per view (`home`, `tour`, `map`, `ask`, `change`,
`about`), plus `engine.js` (search and the answer prompt — kept identical to Python by
`tests/explorer_parity.mjs`), `live.js` (the model call), `graph.js` (layout, pan, zoom)
and `app.js` (router, data, shared helpers). See `../README.md`.

Must not: decide which nodes or edges exist, author legal text, or fetch anything that
is not under `../data/` — apart from the live model endpoint, which comes from
`data/live.json` and never from the code.

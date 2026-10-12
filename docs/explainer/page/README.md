# docs/explainer/page/ — the source of `../ontology-explainer.html`

The interactive explainer is one self-contained HTML file. These are its parts:

| File | What it is |
|---|---|
| `template.html` | Markup and styles, with `__DATA__` and `__SCRIPT__` placeholders |
| `app.js` | Every interaction: the waffles, the small maps, the idea inspector, Ask, change, the chart, the quiz |
| `extract.py` | Reads `site/data/` (from `tmk-explorer --write`) and the bench files; writes `data.json` (git-ignored) |
| `build.py` | Puts the three together into `../ontology-explainer.html` |

Rebuild after the counts or records change: `tmk-fetch-upstream`, `tmk-explorer --write`,
then `python3 docs/explainer/page/extract.py` and `python3 docs/explainer/page/build.py`
from the repository root. The measurement table in `app.js` is copied by hand from
`data/derived/reports/measure.md`; update it when the measurement is re-run.

**Must not:** copy a concept's `notes`, a `signed`/`machine` block, a reviewer's name or
initials, or anything from `review/` into the page. `extract.py` takes only labels,
wordings, kinds, origins, counts, Parts, bases, connections and their quotes. Not part of
the `tm_knowledge` package; no tests depend on it.

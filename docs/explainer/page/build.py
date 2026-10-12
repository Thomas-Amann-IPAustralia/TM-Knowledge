"""Assemble ../ontology-explainer.html from template.html, app.js and data.json.

    tmk-fetch-upstream && tmk-explorer --write      # site/data/ from the pinned snapshot
    python3 docs/explainer/page/extract.py           # -> docs/explainer/page/data.json
    python3 docs/explainer/page/build.py             # -> docs/explainer/ontology-explainer.html

Run both from the repository root. The page is one file with no external loads: the data
is embedded as JSON, every '<' escaped so it cannot close the script element.
"""
import json
from pathlib import Path

here = Path(__file__).parent
data = json.loads((here / "data.json").read_text())
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
js = (here / "app.js").read_text()
assert "</script" not in js.lower()
html = (here / "template.html").read_text().replace("__DATA__", blob).replace("__SCRIPT__", js)
out = here.parent / "ontology-explainer.html"
out.write_text(html)
print(out, out.stat().st_size)

"""PU-0004 at answer time (review F1, ADR-0121) — and the browser does the same."""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.search.authority import conflations

CASES = [
    ("Section 43 requires the Registrar to reject a mark that would deceive.", ["TMM/Part29/1#1"], 1),
    ("Section 43 requires the Registrar to reject a mark that would deceive.", ["TMA1995/s43"], 0),
    ("Section 43 requires it.", ["TMA1995/s44"], 1),
    ("Under the Act, regulation 4.4 states how goods are specified.", ["TMR1995/r4.4"], 0),
    ("Under the Act, regulation 4.4 states how goods are specified.", ["TMM/Part14/3#1~1"], 1),
    ("The Act provides for conditions.", ["TMA1995/s33"], 0),
    ("The Act provides for conditions.", ["TMR1995/r4.4"], 1),
    ("The Manual says section 43 requires a connotation.", ["TMM/Part29/3#1~1"], 0),
    ("The passages do not include section 57 or state the burden.", [], 0),
    ("Examiners should consider the current marketplace.", [], 0),
    ("First sentence. The Regulations require an approved form.\nThe Act says nothing more.", [], 2),
]


@pytest.mark.parametrize("answer, cited, flagged", CASES)
def test_a_statutory_attribution_needs_a_provision_behind_it(answer, cited, flagged):
    assert len(conflations(answer, cited)) == flagged


@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node to run the browser engine")
def test_the_browser_flags_exactly_the_same_sentences():
    script = (
        f"import('{(REPO_ROOT / 'site' / 'js' / 'engine.js').as_uri()}').then((m) => {{"
        f"const cases = {json.dumps([[a, c] for a, c, _ in CASES])};"
        "process.stdout.write(JSON.stringify(cases.map(([a, c]) => m.authorityFlags(a, c).map((f) => f.sentence))));"
        "});"
    )
    result = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True,
                            check=True)
    browser = json.loads(result.stdout)
    python = [[f["sentence"] for f in conflations(a, c)] for a, c, _ in CASES]
    assert browser == python

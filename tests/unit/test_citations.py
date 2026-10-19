"""Exact-reference lookup (A07): a question that names a provision gets it, in both engines."""

from __future__ import annotations

import json
import shutil
import subprocess

import pytest

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.search.citations import named_provisions

HELD = {"TMA1995/s41": 1, "TMA1995/s43": 1, "TMA1995/s44": 1, "TMA1995/s4A": 1, "TMA1995/s3": 1,
        "TMR1995/r4.8": 1, "TMR1995/r4.10": 1}

CASES = [
    ("What does section 44(3) say?", ["TMA1995/s44"]),
    ("s 41(4) and s.43", ["TMA1995/s41", "TMA1995/s43"]),
    ("Under reg 4.10 and regulation 4.8(1)", ["TMR1995/r4.10", "TMR1995/r4.8"]),
    ("subsection 41(6), then section 41 again", ["TMA1995/s41"]),
    ("section 4a", ["TMA1995/s4A"]),
    ("44(3) alone names no instrument", []),
    ("it's 3 classes", []),
    ("section 999 is not held", []),
    ("the 2.4 rule", []),
]


@pytest.mark.parametrize("text, expected", CASES)
def test_a_named_provision_is_found_at_the_provision_level(text, expected):
    assert named_provisions(text, HELD) == expected


@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node to run the browser engine")
def test_the_browser_finds_the_same_provisions():
    script = (
        f"import('{(REPO_ROOT / 'site' / 'js' / 'engine.js').as_uri()}').then((m) => {{"
        f"const held = {json.dumps(HELD)}; const cases = {json.dumps([t for t, _ in CASES])};"
        "process.stdout.write(JSON.stringify(cases.map((t) => m.namedProvisions(t, held))));"
        "});"
    )
    result = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True,
                            check=True)
    assert json.loads(result.stdout) == [expected for _, expected in CASES]

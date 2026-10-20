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
    # R08's two tightenings: each exemption reads only the match's own clause.
    ("The legislation does not say anything else, but section 41 requires use evidence.", [], 1),
    ("Section 41 requires use evidence, as the Manual explains.", ["TMM/Part18/2#1"], 1),
    ("According to the Manual, section 41 requires use evidence.", ["TMM/Part18/2#1"], 0),
    ("The Act does not require a search; the Regulations require a fee.", [], 1),
    ("Section 44 does not require identical goods.", [], 0),
]

#: Known misses (R08): each should be flagged and is not. Strict, so a change that
#: catches one fails here and moves it up into CASES on purpose.
KNOWN_MISSES = [
    pytest.param("Section 43 requires the Registrar to refuse every surname.", ["TMA1995/s43"],
                 id="any-citation-of-the-named-section-clears-it"),
    pytest.param("The Act requires evidence of use in every case.", ["TMA1995/s6"],
                 id="a-definition-citation-clears-the-whole-act"),
    pytest.param("Under section 43 the connotation must be obvious, direct and immediate.", [],
                 id="must-is-outside-the-verb-list"),
    pytest.param("It is a legal requirement that the applicant files evidence.", [],
                 id="no-legislation-named"),
]


@pytest.mark.parametrize("answer, cited, flagged", CASES)
def test_a_statutory_attribution_needs_a_provision_behind_it(answer, cited, flagged):
    assert len(conflations(answer, cited)) == flagged


@pytest.mark.xfail(strict=True, reason="a known miss of a warning heuristic (R08); see the module docstring")
@pytest.mark.parametrize("answer, cited", KNOWN_MISSES)
def test_the_known_misses_stay_documented(answer, cited):
    assert conflations(answer, cited)


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

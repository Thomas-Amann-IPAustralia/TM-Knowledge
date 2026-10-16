"""A measurement report names what it was scored on, and is never silently rescored.

The pooled grade file grows: the reading's run on 12 October added 548 grades, so
re-scoring the 9 October rankings today gives 0.702 / 0.812 / 0.773 against the
published 0.725 / 0.844 / 0.803 (the review response, F11). Nothing was wrong with
either number; nothing said which grades each one used. Git already freezes every
input, so a report needs only a pointer: the commit, and a hash and count of the
grades and the rankings. And `measure --write` must not overwrite a report scored on
other inputs; it writes a new dated one and leaves the published one standing.
"""

from __future__ import annotations

import pytest

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.search import measure

REPORTS = REPO_ROOT / "data" / "derived" / "reports"
INPUTS = {"commit": "0123456789ab", "grades": "sha256:" + "a" * 64, "grade_count": 10,
          "rankings": "sha256:" + "b" * 64}


@pytest.mark.parametrize("name", ["measure.md", "measure-reading.md"])
def test_every_committed_measurement_names_its_inputs(name):
    named = measure.read_inputs(REPORTS / name)
    assert named is not None, f"{name} does not say which commit and grades it was scored on"
    assert len(named["commit"]) >= 7 and named["grades"].startswith("sha256:") and named["grade_count"] > 0


def test_a_stamped_report_round_trips_its_inputs(tmp_path):
    path = tmp_path / "measure.md"
    path.write_text(measure.stamp("# Title\n\nBody.\n", INPUTS), encoding="utf-8")
    assert measure.read_inputs(path) == INPUTS
    assert "git checkout 0123456789ab" in path.read_text(encoding="utf-8")


def test_write_overwrites_a_report_on_the_same_inputs(tmp_path):
    path = tmp_path / "measure.md"
    path.write_text(measure.stamp("# Old\n", INPUTS), encoding="utf-8")
    written = measure.write_report(path, measure.stamp("# New\n", INPUTS), INPUTS, today="2026-10-16")
    assert written == path and "# New" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("old", [
    measure.stamp("# Old\n", {**INPUTS, "grades": "sha256:" + "c" * 64}),
    measure.stamp("# Old\n", {**INPUTS, "rankings": "sha256:" + "d" * 64}),
    "# Old, from before reports named their inputs\n",
], ids=["other-grades", "other-rankings", "unnamed"])
def test_write_never_overwrites_a_report_on_other_inputs(tmp_path, old):
    path = tmp_path / "measure.md"
    path.write_text(old, encoding="utf-8")
    written = measure.write_report(path, measure.stamp("# New\n", INPUTS), INPUTS, today="2026-10-16")
    assert written == tmp_path / "measure-2026-10-16.md"
    assert path.read_text(encoding="utf-8") == old, "the published report was overwritten"
    text = written.read_text(encoding="utf-8")
    assert "# New" in text and "measure.md" in text, "the dated report must say what it does not replace"

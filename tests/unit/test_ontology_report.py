"""The ontology report is held to a rebuild, as `graph/` is.

It was generated and still went stale: by October 2026 it called the ontology
"the section 43 draft", counted 78 machine-written concepts against 112, and
asked an expert to type concepts a machine had typed a month before (the review
response, F12). Two causes, each closed here: a generated-on date made every
rebuild differ, so nobody could check it; and nothing checked it.

Rendering the real report builds the graph and runs the SHACL gate, about a
minute, so these tests stand `render` in. CI runs the real check
(`tmk-ontology-report --check` in `harness.yml`).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.rdf


def test_check_passes_on_the_same_text_and_fails_on_any_other(tmp_path):
    from tm_knowledge.ontology import report

    path = tmp_path / "ontology.md"
    report.write("one\n", path)
    assert report.check("one\n", path)
    assert not report.check("two\n", path)
    assert not report.check("one\n", tmp_path / "missing.md")


def test_the_cli_exits_non_zero_on_drift(tmp_path, monkeypatch, capsys):
    from tm_knowledge.ontology import cli, report

    path = tmp_path / "ontology.md"
    path.write_text("committed\n", encoding="utf-8")
    monkeypatch.setattr(report, "REPORT_PATH", path)
    monkeypatch.setattr(report, "render", lambda: "rebuilt\n")
    assert cli.ontology_report(["--check"]) == 1
    assert "no longer matches a rebuild" in capsys.readouterr().err

    path.write_text("rebuilt\n", encoding="utf-8")
    assert cli.ontology_report(["--check"]) == 0


def test_the_report_carries_no_date():
    """A generated-on date makes every rebuild differ from what is committed,
    which is what kept the report from being checked."""
    import inspect

    from tm_knowledge.ontology import report

    source = inspect.getsource(report)
    assert "date.today" not in source
    assert "Generated |" not in source


def test_ci_checks_the_report():
    from tm_knowledge.config import REPO_ROOT

    workflow = (REPO_ROOT / ".github" / "workflows" / "harness.yml").read_text(encoding="utf-8")
    assert "tmk-ontology-report --check" in workflow

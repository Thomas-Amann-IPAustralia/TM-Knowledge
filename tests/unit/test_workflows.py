"""Publication waits on the checks (the review response, F03).

Until S036 the Pages workflow ran on every push to `main` that touched the site's
inputs, beside the harness rather than after it, so a red harness, a failed SHACL
gate or graph drift still published. `main` is not a protected branch either (the
owner's setting), so nothing else stopped it. Pages now runs when the harness
workflow completes, and deploys only when that run succeeded on a push to `main`.
"""

from __future__ import annotations

import yaml

from tm_knowledge.config import REPO_ROOT

WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    document = yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))
    # YAML 1.1 reads the bare key `on` as the boolean True.
    document["on"] = document.pop(True, document.get("on"))
    return document


def test_pages_runs_after_the_harness_and_not_beside_it():
    pages, harness = _load("pages.yml"), _load("harness.yml")
    triggers = pages["on"]
    assert "push" not in triggers, "a push to main would publish without waiting for the checks"
    run = triggers["workflow_run"]
    assert run["workflows"] == [harness["name"]]
    assert run["types"] == ["completed"]
    assert run.get("branches") == ["main"]


def test_pages_deploys_only_what_the_harness_passed():
    deploy = _load("pages.yml")["jobs"]["deploy"]
    condition = " ".join(str(deploy["if"]).split())
    assert "github.event.workflow_run.conclusion == 'success'" in condition
    assert "github.event.workflow_run.event == 'push'" in condition
    checkout = next(step for step in deploy["steps"] if str(step.get("uses", "")).startswith("actions/checkout"))
    assert "workflow_run.head_sha" in str(checkout.get("with", {}).get("ref", "")), (
        "Pages must build the commit the harness checked, not whatever main is now"
    )

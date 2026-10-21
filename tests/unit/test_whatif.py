"""What-ifs (ADR-0149): an invented new right laid over the ontology as it stands. The premise and
questions are a machine's; everything they land on is an existing record, read and never changed."""

from __future__ import annotations

import pytest
import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.explain import whatif

from test_explain import _outcomes  # the one outcome guard, shared

pytestmark = pytest.mark.snapshot


@pytest.fixture(scope="module")
def built():
    from tm_knowledge.explorer import build as explorer

    return explorer.build(generated="2026-01-01")


def test_every_what_if_lands_on_the_snapshot_and_the_records(built):
    from tm_knowledge.upstream.loader import load_corpus

    found = whatif.load(corpus=load_corpus(), onto=built["ontology.json"])
    assert [w.id for w in found] == ["FW-0001"]
    assert all(not w.errors for w in found), [w.errors for w in found]
    assert built["whatif.json"]["left_out"] == []


def test_a_quote_that_does_not_land_is_refused(built, tmp_path):
    from tm_knowledge.upstream.loader import load_corpus

    records = yaml.safe_load(whatif.WHATIF_PATH.read_text(encoding="utf-8"))
    records[0]["touchpoints"][0]["today"][0]["quote"] = "words the Manual never used"
    records[0]["touchpoints"][1]["ideas"].append("GC-9999")
    records[0]["review_status"] = "approved"
    path = tmp_path / "what-if.yaml"
    path.write_text(yaml.dump(records, allow_unicode=True), encoding="utf-8")
    errors = " | ".join(whatif.load(path, corpus=load_corpus(), onto=built["ontology.json"])[0].errors)
    assert "not at its span" in errors and "no idea GC-9999" in errors and "unreviewed" in errors


def test_the_what_if_changes_nothing_in_the_ontology(built):
    """Its id and its own words are in no graph, no authored record and no data file but its own."""
    records = yaml.safe_load(whatif.WHATIF_PATH.read_text(encoding="utf-8"))
    needles = [r["id"] for r in records] + [r["premise"] for r in records] + [
        p["what_if"] for r in records for p in r["touchpoints"]]
    places = [REPO_ROOT / "graph" / "dataset.nq", *sorted((REPO_ROOT / "authored").glob("*.yaml"))]
    for path in places:
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            assert needle not in text, f"{needle[:40]!r} in {path.relative_to(REPO_ROOT)}"
    import json

    for name, data in built.items():
        if name != "whatif.json":
            text = json.dumps(data, ensure_ascii=False)
            assert not any(n in text for n in needles), name


def test_what_would_be_re_read_is_counted_and_a_gap_is_said(built):
    w = built["whatif.json"]["whatifs"][0]
    points = {p["id"]: p for p in w["touchpoints"]}
    assert all(p["recheck"] for p in points.values())
    # No record names section 61: said as no recorded dependency, never as no impact.
    assert points["opposition"]["no_recorded_dependency"] == ["TMA1995/s61"]
    assert w["rests_on_provision"]["TMA1995/s61"] is None
    assert "Unknown" in w["behavioural"] and w["stamp"] == whatif.STAMP


def test_no_what_if_states_an_outcome():
    for r in yaml.safe_load(whatif.WHATIF_PATH.read_text(encoding="utf-8")):
        text = "\n".join([r["premise"], *(p["what_if"] for p in r["touchpoints"]),
                          *(q for p in r["touchpoints"] for q in p["questions"])])
        assert _outcomes(text) == [], r["id"]
        assert r["review_status"] == "unreviewed" and "approved_by" not in r


def test_the_page_says_what_it_is():
    page = (REPO_ROOT / "site" / "js" / "whatif.js").read_text(encoding="utf-8")
    for words in ("An invented premise. The ontology is not changed. Nothing here is decided.",
                  "Text equivalent of the picture", "no recorded dependency"):
        assert words in page, words
    assert 'load("whatif")' in page

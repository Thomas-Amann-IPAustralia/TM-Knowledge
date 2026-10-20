"""The versioning model (A03, ADR-0146): identity apart from text, legal effect apart from
capture, and an explicit unknown. Selection is tested on two invented compilations, because
the snapshot holds one per instrument."""

from __future__ import annotations

from datetime import date

import pytest

from tm_knowledge import versions
from tm_knowledge.config import REPO_ROOT

UPSTREAM_DIR = REPO_ROOT / "data" / "upstream"
needs_snapshot = pytest.mark.skipif(not UPSTREAM_DIR.exists(), reason="needs the pinned snapshot")


def _compilation(number: str, start: str, captured: str, **fields) -> versions.Compilation:
    return versions.Compilation(instrument="TMA1995", number=number, register_id=f"C-{number}",
                                in_force_from=date.fromisoformat(start), captured=date.fromisoformat(captured),
                                title_id="C2004A04969", status_at_capture=fields.get("status", "InForce"),
                                unincorporated=fields.get("unincorporated", False))


#: Two invented compilations: 47 from 1 March 2026, 48 from 19 September 2026.
TWO = [_compilation("48", "2026-09-19", "2026-10-17"), _compilation("47", "2026-03-01", "2026-03-05")]


@pytest.mark.parametrize(("on", "state", "number"), [
    ("2026-02-28", "not_held", None),
    ("2026-03-01", "held", "47"),
    ("2026-09-18", "held", "47"),
    ("2026-09-19", "held", "48"),
    ("2026-10-17", "held", "48"),
    ("2026-10-18", "after_capture", "48"),
    (None, "no_date", None),
])
def test_a_date_selects_the_compilation_in_force_or_says_why_not(on, state, number):
    found = versions.select(TWO, on, "the filing date")
    assert found.state == state
    assert (found.compilation.number if found.compilation else None) == number
    assert found.state in versions.STATES


def test_no_date_is_an_explicit_unknown_never_the_held_text():
    found = versions.select(TWO, None, "the filing date")
    assert found.compilation is None
    assert "not given" in found.reads and "not assumed" in found.reads


def test_the_latest_text_is_confirmed_only_by_what_the_register_said_at_capture():
    """A compilation with amendments left unincorporated, or not shown in force, is held
    but not confirmed as the text in force, even on a day inside its span."""
    for fields in ({"unincorporated": True}, {"status": "Repealed"}, {"unincorporated": None}):
        found = versions.select([_compilation("48", "2026-09-19", "2026-10-17", **fields)], "2026-10-01")
        assert found.state == "unconfirmed", fields


def test_the_states_are_the_ones_the_ontology_names():
    from rdflib.namespace import RDF, RDFS

    from tm_knowledge.ontology.namespaces import TMK
    from tm_knowledge.ontology.tbox import load

    tbox = load()
    labels = {str(tbox.value(node, RDFS.label)) for node in tbox.subjects(RDF.type, TMK.VersionState)}
    assert labels == {s.replace("_", " ") for s in versions.STATES}


@needs_snapshot
def test_the_snapshot_holds_one_compilation_of_each_instrument_with_its_enduring_id():
    held = versions.held()
    assert sorted(held) == ["TMA1995", "TMR1995"]
    act = held["TMA1995"]
    assert len(act) == 1 and act[0].number == "48" and act[0].register_id == "C2026C00421"
    assert act[0].title_id == "C2004A04969", "the instrument's own id, shared by every compilation"
    assert act[0].in_force_from == date(2026, 9, 19) and act[0].captured == date(2026, 10, 17)


@pytest.mark.rdf
@needs_snapshot
def test_the_graph_states_the_compilation_apart_from_the_instrument():
    from rdflib import Dataset, URIRef
    from rdflib.namespace import RDF, TIME

    from tm_knowledge.ontology.namespaces import SOURCE_GRAPH, TMK

    dataset = Dataset()
    dataset.parse(REPO_ROOT / "graph" / "dataset.nq", format="nquads")
    source = dataset.graph(SOURCE_GRAPH)
    act = URIRef(TMK["doc/TMA1995"])
    compilation = source.value(act, TMK.heldCompilation)
    assert compilation == URIRef(TMK["doc/TMA1995/compilation/48"])
    assert (compilation, RDF.type, TMK.Compilation) in source
    assert str(source.value(act, TMK.registerTitleId)) == "C2004A04969"
    interval = source.value(compilation, TMK.inForceDuring)
    begins = source.value(interval, TIME.hasBeginning)
    assert str(source.value(begins, TIME.inXSDDate)) == "2026-09-19"
    assert source.value(interval, TIME.hasEnd) is None, "the end is not known until the next is held"
    assert source.value(compilation, TMK.currentAtCapture).toPython() is True
    for ref in ("TMA1995/s44", "TMA1995/s44(3)"):
        node = URIRef(f"https://data.ipaustralia.gov.au/tmk/ref/{ref}")
        assert source.value(node, TMK.textFrom) == compilation, ref

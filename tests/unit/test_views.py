"""The two derived views arrange records, and must not invent any.

Every other page on the site restates an artefact, and the test that protects
those is `test_committed_data_is_current`: a number on the page must be a number
in the repository. **These two pages are different in kind** — they compute an
arrangement, which is the first thing the site does that a reader could take for
a claim (ADR-0103). So the guards here are about the arrangement:

1. **Every node stands for something that exists.** A node id is a record id in
   one of the two stores, or an upstream ref that parses. A node standing for
   nothing is a picture of something the repository does not hold.
2. **Nothing is merged.** A concept a person signed and a concept a machine
   wrote appear on one canvas, and every node says which it is. This is the one
   place in the repo where the two stores are drawn together, which makes it the
   one place ADR-0080 consequence 3 could be broken by accident.
3. **No machine output goes anywhere unlabelled** (CLAUDE.md rule 8). An
   authored node carries its model, its date, its basis and its review status,
   or the payload is wrong.
4. **The arrangement is a rule, not a memory.** Two builds of the same records
   produce the same bytes, which is what makes the picture citable.
5. **The tree never reaches an outcome.** Every branch ends on the leaf that
   says the system does not state one, and that leaf quotes signed records.
"""

from __future__ import annotations

import json

import pytest

from tm_knowledge import refs
from tm_knowledge.authored import store as authored_store
from tm_knowledge.dashboard import views
from tm_knowledge.stage0 import goldset

pytestmark = []


@pytest.fixture(scope="module")
def stores():
    return goldset.load(), authored_store.load()


@pytest.fixture(scope="module")
def graph(stores):
    return views.network(*stores)


@pytest.fixture(scope="module")
def tree(stores):
    return views.decision_tree(*stores)


# ------------------------------------------------------------------- the refs


@pytest.mark.parametrize(
    "ref,expected",
    [
        ("TMA1995/s43", "TMA1995/s43"),
        ("TMA1995/s41(3)(a)", "TMA1995/s41"),
        ("TMA1995/s84A(6)", "TMA1995/s84A"),
        ("TMR1995/r4.15A", "TMR1995/r4.15A"),
        ("TMA1995/s6/registrar", "TMA1995/s6"),
        ("TMR1995/r2.1/madrid-protocol", "TMR1995/r2.1"),
        ("TMM/Part29/1#1", None),
    ],
)
def test_a_provision_rolls_up_to_its_section(ref, expected):
    assert views.root_provision(ref) == expected


@pytest.mark.parametrize(
    "ref,expected",
    [
        ("TMM/Part29/2/2/1~1", "Part29"),
        ("TMM/Part32A/1/1/1", "Part32A"),
        ("TMM/Part20/5#1", "Part20"),
        ("TMA1995/s43", None),
    ],
)
def test_a_manual_ref_knows_its_part(ref, expected):
    assert views.manual_part(ref) == expected


def test_a_definition_ref_joins_nothing(stores):
    """`TMA1995/s6/assignment` is where a word is defined, not where a step
    happens. Joining on it joined the dictionary to itself: *assignment*,
    *transmission* and *divisional application* each came out of the procedure
    spine with eighteen children, every one of them a defined term."""
    _, authored = stores
    concepts = {view.identifier: view for view in views.concept_views(*stores)}
    assignment = concepts["GC-0086"]
    assert "TMA1995/s6" in assignment.sections
    assert "TMA1995/s6" not in assignment.joinable_sections
    assert assignment.joinable_sections == {"TMA1995/s106"}


# --------------------------------------------------------------- the network


def test_every_node_stands_for_something_the_repo_holds(graph, stores):
    gold, authored = stores
    known = {record["id"] for record in gold["gold_concept"]}
    known |= {record["id"] for record in authored["gold_concept"]}
    for node in graph["nodes"]:
        if node["kind"] == "concept":
            assert node["id"] in known, f"{node['id']} is on the map and in neither store"
        else:
            refs.parse_ref(node["id"])  # raises if it is not an upstream ref


def test_every_edge_joins_two_nodes_that_are_drawn(graph):
    drawn = {node["id"] for node in graph["nodes"]}
    for edge in graph["edges"]:
        assert edge["source"] in drawn and edge["target"] in drawn


def test_every_signed_edge_names_the_record_that_asserts_it(graph, stores):
    gold, _ = stores
    records = {record["id"]: record for record in gold["gold_relationship"]}
    signed = [edge for edge in graph["edges"] if edge["kind"] == "asserted"]
    assert signed, "no signed relationship reached the map"
    for edge in signed:
        record = records[edge["record"]]
        assert edge["source"] == record["subject"]
        assert edge["target"] == record["object"]
        assert edge["predicate"] == record["predicate"]


def test_a_blank_modality_stays_blank(graph, stores):
    """Five signed relationships have no modality and an agent may not fill one
    (CLAUDE.md rule 3). A picture that defaulted it to *may* would be putting a
    reading inside a signature."""
    gold, _ = stores
    blank = {
        record["id"] for record in gold["gold_relationship"] if not record.get("modality")
    }
    assert blank, "the fixture this protects has changed"
    for edge in graph["edges"]:
        if edge.get("record") in blank:
            assert "modality" not in edge


def test_the_two_stores_are_drawn_together_and_never_merged(graph):
    counts = graph["counts"]
    assert counts["signed"] + counts["authored"] == counts["concepts"]
    origins = {node["origin"] for node in graph["nodes"] if node["kind"] == "concept"}
    assert origins == {"approved", "authored"}
    for node in graph["nodes"]:
        assert node["origin"], f"{node['id']} is drawn without saying who wrote it"


def test_no_authored_node_reaches_the_page_unlabelled(graph):
    for node in graph["nodes"]:
        if node["origin"] != "authored":
            continue
        envelope = node["authored"]
        assert envelope["review_status"] == "unreviewed"
        assert envelope["authored_by"]
        assert envelope["authored_date"]
        assert envelope["authoring_basis"]


def test_no_node_carries_an_approval(graph):
    """`approved_by` on an authored record is the one failure the whole scheme
    exists to stop, and a view that copied a field across stores is a way it
    could happen without anyone editing a record."""
    for node in graph["nodes"]:
        if node["origin"] == "authored":
            assert "signed" not in node
        elif node["origin"] == "approved":
            assert node["signed"]["by"]


def test_a_provision_is_never_collapsed_into_its_section(graph, stores):
    """The record cites `TMA1995/s41(3)(a)` and the map draws that node. Rolling
    it up is a thing the reader can turn on in the browser, and `root` is how —
    never a substitution made here (CLAUDE.md rule 2)."""
    gold, authored = stores
    cited = {
        ref
        for record in (*gold["gold_concept"], *authored["gold_concept"])
        for ref in (record.get("legislative_basis") or ())
    }
    drawn = {node["id"] for node in graph["nodes"] if node["kind"] == "provision"}
    assert cited <= drawn
    for node in graph["nodes"]:
        if node["kind"] == "provision":
            assert views.root_provision(node["id"]) == node["root"]


# ------------------------------------------------------------------ the tree


def _walk(node):
    yield node
    for child in node.get("children") or ():
        yield from _walk(child)


def test_every_tree_node_points_at_a_record_or_says_it_is_structure(tree):
    for spine in tree["spines"]:
        for node in _walk(spine["root"]):
            if node.get("record") and node["kind"] != "prohibited":
                assert node["record"] in tree["records"]
            else:
                assert node["kind"] in {
                    "root", "section", "band", "residue", "outcome", "prohibited",
                }


def test_every_concept_on_the_tree_says_why_it_is_there(tree):
    """The four rules are the whole of the claim this page makes. A node that
    arrived without one would be an arrangement nobody could check."""
    for spine in tree["spines"]:
        for node in _walk(spine["root"]):
            if node.get("record") and node["kind"] != "prohibited":
                assert node["basis"], f"{node['id']} is on a branch for no stated reason"


def test_every_branch_ends_on_the_outcome_it_does_not_state(tree, stores):
    gold, _ = stores
    prohibited = {
        record["id"]
        for record in gold["prohibited_use"]
        if record["kind"] == "evaluative_conclusion"
    }
    assert prohibited, "the signed records this leaf rests on have gone"
    sections = [
        node for node in tree["spines"][0]["root"]["children"] if node["kind"] == "section"
    ]
    assert sections
    for section in sections:
        leaves = [child for child in section["children"] if child["kind"] == "outcome"]
        assert len(leaves) == 1, f"{section['id']} does not end on the outcome leaf"
        assert {child["record"] for child in leaves[0]["children"]} == prohibited


def test_a_branch_with_no_ground_concept_says_so(tree):
    """Three sections hold a test and nothing typed as the ground it serves.
    That is a hole in the vocabulary and the tree has to show it: a picture that
    quietly filled it in would be authoring the missing record."""
    sections = [
        node for node in tree["spines"][0]["root"]["children"] if node["kind"] == "section"
    ]
    for section in sections:
        grounds = [
            child
            for band in section["children"]
            for child in (band.get("children") or ())
            if child.get("kind") == "ground_of_refusal"
        ]
        assert bool(grounds) != bool(section["gap"]), section["id"]


def test_a_concept_that_joins_nothing_is_shown_rather_than_filed(tree):
    residue = [
        node for node in tree["spines"][0]["root"]["children"] if node["kind"] == "residue"
    ]
    counts = tree["spines"][0]["counts"]
    if counts["stranded"]:
        assert len(residue) == 1
        assert len(residue[0]["children"]) == counts["stranded"]
    assert counts["placed"] + counts["stranded"] == counts["concepts"]


def test_the_reasoning_and_process_spines_cover_every_concept(tree):
    counts = tree["counts"]
    assert counts["reasoning"] + counts["process"] + counts["outside"] + counts["untyped"] == (
        counts["concepts"]
    )


# ---------------------------------------------------------------- both views


def test_the_arrangement_is_a_rule_and_not_a_memory(stores):
    """Two builds of the same records produce the same bytes. A layout that
    moved between builds would make every screenshot of this page unciteable,
    and `tmk-dashboard --check` would report drift on a repository nobody had
    touched."""
    first = json.dumps(views.network(*stores), sort_keys=True)
    second = json.dumps(views.network(*stores), sort_keys=True)
    assert first == second
    assert json.dumps(views.decision_tree(*stores), sort_keys=True) == json.dumps(
        views.decision_tree(*stores), sort_keys=True
    )


def test_neither_view_carries_a_definition(graph, tree):
    """No record in this project holds the text of a definition — writing one
    would be authoring a legal proposition onto a signed record. Nothing in a
    view may introduce the field either."""
    for payload in (graph, tree):
        blob = json.dumps(payload)
        assert '"definition"' not in blob
        assert '"approved_by"' not in blob

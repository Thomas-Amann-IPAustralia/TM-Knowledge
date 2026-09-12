"""Two derived views over the records: the network, and the decision tree.

Everything else the dashboard publishes *restates* an artefact — a count, a
field, a report rendered whole. These two **arrange** artefacts, and arranging is
the first thing this site has done that a reader could mistake for a claim. So
the arrangement rules live here, in one module, in Python, computed on every
build, and every node and every edge that comes out carries the rule that put it
there (ADR-0103).

**Nothing here authors legal content.** No node holds a definition, a
conclusion or an outcome; a node holds a record id, a label a record already
carries, and the refs that record already cites. If a sentence on either view is
not in a committed record or in this module's own stated rules, it is a defect.

**The two views read both stores and never merge them.** Every node says whether
the record under it was signed by a person or written by a machine, because the
whole point of putting 130 concepts on one canvas is that a reader can see, at a
glance, how much of the picture nobody has checked (ADR-0080 consequence 3).

The arrangement rules, in full:

*The network* draws an edge for four things a record already states — a SKOS
`broader`/`narrower` pair, a `related` pair, a signed `GR-` relationship, and a
concept's `legislative_basis`. It invents no edge of its own, and it never
collapses a provision ref into its root: `TMA1995/s41(3)(a)` is a node, `root`
is an attribute of it, and the rolling-up happens in the browser where the
reader can turn it off.

*The decision tree* is a **binary tree of questions** over the four reasoning
groups. A section of the Act becomes a branch point when a `ground_of_refusal` or
a `legal_test` concept cites it, and asks whether a ground under it arises: *no*
carries the walk to the next section — that chain is the spine — and *yes* opens
the questions recorded at that one, each of them a `legal_test` whose label has
been put into question form. A concept joins a section when it cites the section
itself, or when a signed relationship or a SKOS edge joins it to a concept that
does. A factor is read *at* a branch point rather than being one, and hangs off
the section. A concept that joins nothing is shown beside the tree, and a section
with no ground concept is marked — both of those are findings, and hiding them
would be the whole failure mode of a picture (ADR-0106, superseding ADR-0105 on
shape).

**Turning a label into a question is the furthest this module goes.** It is a
transcription through one of three templates, and nothing here decides how a
question is answered: every path, at every branch point, ends on the leaf that
says the system does not state an outcome.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from tm_knowledge import refs
from tm_knowledge.stage0 import typing as typing_module

__all__ = [
    "ConceptView",
    "EDGE_KINDS",
    "REASONING_GROUPS",
    "concept_views",
    "decision_tree",
    "manual_part",
    "network",
    "root_provision",
]

#: The four groups that sort a concept by the part it plays in *reasoning*
#: towards a decision. Read off `stage0.typing` rather than restated, so the
#: tree cannot drift from the taxonomy the workbook and the ontology use.
REASONING_GROUPS: tuple[str, ...] = tuple(value for value, _ in typing_module.REASONING_GROUPS)
PROCESS_GROUPS: tuple[str, ...] = tuple(value for value, _ in typing_module.PROCESS_GROUPS)
GROUP_MEANING: dict[str, str] = dict(typing_module.GROUPS)

#: The groups that anchor a branch of the decision tree. A ground is the
#: obvious one; a test is here because **three of the ten branches hold tests
#: and no ground concept**, and a rule that anchored on grounds alone would have
#: silently dropped section 41 — the largest of the three — off the picture.
ANCHOR_GROUPS: tuple[str, ...] = ("ground_of_refusal", "legal_test")

#: Edge kind -> (label, what it means, which store asserts it). The browser
#: renders the label and the legend; it decides nothing about what an edge is.
EDGE_KINDS: tuple[tuple[str, str, str], ...] = (
    ("narrower", "contains", "One concept sits under another, as the record's own "
                             "`broader` / `narrower` fields state it."),
    ("related", "related to", "The two concepts are recorded as related — an associative "
                              "link, not a hierarchy."),
    ("asserted", "asserted", "A signed `GR-` relationship record: a named reviewer wrote "
                             "this edge, with the passage it rests on and a modality."),
    ("cites", "cites", "The concept's record names this provision as its legislative basis."),
)

_PART = re.compile(r"^TMM/(Part[0-9]+[A-Za-z]*)(?:/|#|~|$)")


def root_provision(ref: str) -> str | None:
    """The provision a legislation ref sits under — `TMA1995/s41(3)(a)` -> `TMA1995/s41`.

    `refs.Ref.root` answers this for a unit ref and returns `None` for the two
    other shapes that reach here: a bare provision, which *is* its own root, and
    a definition ref (`TMA1995/s6/registrar`), which upstream models as an
    address with a second segment. Both are resolved here rather than in
    `refs.py` — this is a grouping convenience for one picture, not a property
    of the ref, and upstream deliberately does not store it (Q-09).
    """
    try:
        parsed = refs.parse_ref(ref)
    except refs.InvalidRef:
        return None
    if parsed.root:
        return parsed.root
    if parsed.instrument is None:
        return None
    address = parsed.value[len(parsed.instrument) + 1 :]
    head = address.split("/", 1)[0]
    return f"{parsed.instrument}/{head}" if head else None


def manual_part(ref: str) -> str | None:
    """The Manual Part a chunk or page ref sits in — `TMM/Part29/2/2/1~1` -> `Part29`."""
    match = _PART.match(ref)
    return match.group(1) if match else None


def _provision_label(ref: str) -> str:
    """`TMA1995/s43` -> `s 43`. The address as recorded, spaced for reading.

    No instrument title is minted. The repository holds the codes upstream uses
    and nowhere holds the long titles, and a picture is not the place to start
    asserting what an instrument is called.
    """
    instrument, _, address = ref.partition("/")
    if not address:
        return ref
    lead = re.match(r"^([a-z]+)(.*)$", address)
    return f"{lead.group(1)} {lead.group(2)}" if lead else address


# --------------------------------------------------------------------- concepts


@dataclass(frozen=True)
class ConceptView:
    """One concept, from either store, with everything both views need.

    Built once and shared, so the network and the tree cannot disagree about
    what a concept is called or who wrote it.
    """

    identifier: str
    label: str
    origin: str
    group: str | None
    alt_labels: tuple[str, ...]
    not_labels: tuple[str, ...]
    broader: tuple[str, ...]
    narrower: tuple[str, ...]
    related: tuple[str, ...]
    provisions: tuple[str, ...]
    sources: tuple[str, ...]
    notes: str | None
    signed_by: str | None
    signed_date: str | None
    #: The `authored:` envelope of the concept record, where there is one.
    authored: dict[str, Any] | None
    #: The `authored:` envelope of the *typing* record. Every concept in the
    #: project is typed by a machine today, including the 52 a person signed,
    #: and the two provenances are different facts about the same node.
    typed_by: dict[str, Any] | None
    typing_record: str | None
    typing_notes: str | None

    @property
    def sections(self) -> frozenset[str]:
        """Every provision this concept's record names, rolled up to its section."""
        return frozenset(
            root for root in (root_provision(ref) for ref in self.provisions) if root
        )

    @property
    def joinable_sections(self) -> frozenset[str]:
        """The sections that may join this concept to another one.

        `sections` minus every **definition ref** — the `TMA1995/s6/registrar`
        shape, where upstream addresses a defined term inside a provision. Every
        defined term in the Act cites the same provision, so joining on one
        joins the dictionary to itself: before this was excluded, *assignment*,
        *transmission* and *divisional application* each came out with eighteen
        children, all of them things that merely have a definition.

        The test is the ref's shape and not its number. Nothing here asserts
        which section of which instrument holds the definitions.
        """
        return frozenset(
            root
            for ref, root in ((ref, root_provision(ref)) for ref in self.provisions)
            if root and ref.count("/") < 2
        )

    @property
    def parts(self) -> frozenset[str]:
        return frozenset(
            part for part in (manual_part(ref) for ref in self.sources) if part
        )


def _tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def concept_views(gold: Any, authored: Any) -> tuple[ConceptView, ...]:
    """Every concept in the project, signed and authored, in id order.

    The two stores are read separately and stay distinguishable on every record
    (`origin`). They are returned in one sequence because both views need to
    draw one canvas — which is exactly the situation ADR-0080 consequence 3
    covers: never summed into one number, always one picture with the
    difference on its face.
    """
    typings: dict[str, tuple[str, dict[str, Any] | None, str | None, str | None]] = {}
    for record in gold["concept_type"]:
        typings[str(record["concept"])] = (str(record["type"]), None, str(record["id"]),
                                           record.get("notes"))
    for entry in authored.of("concept_type"):
        if not entry.sound:
            continue
        typings[str(entry.record["concept"])] = (
            str(entry.record["type"]),
            entry.envelope,
            str(entry.record["id"]),
            entry.record.get("notes"),
        )

    views: list[ConceptView] = []

    def add(record: dict[str, Any], origin: str, envelope: dict[str, Any] | None) -> None:
        identifier = str(record["id"])
        group, typed_by, typing_record, typing_notes = typings.get(
            identifier, (None, None, None, None)
        )
        views.append(
            ConceptView(
                identifier=identifier,
                label=str(record["pref_label"]),
                origin=origin,
                group=group,
                alt_labels=_tuple(record.get("alt_labels")),
                not_labels=_tuple(record.get("not_labels")),
                broader=_tuple(record.get("broader")),
                narrower=_tuple(record.get("narrower")),
                related=_tuple(record.get("related")),
                provisions=_tuple(record.get("legislative_basis")),
                sources=_tuple(record.get("definition_sources")),
                notes=record.get("notes"),
                signed_by=record.get("approved_by"),
                signed_date=record.get("approved_date"),
                authored=envelope,
                typed_by=typed_by,
                typing_record=typing_record,
                typing_notes=typing_notes,
            )
        )

    for record in gold["gold_concept"]:
        add(record, "approved", None)
    for entry in authored.of("gold_concept"):
        if entry.sound:
            add(entry.record, "authored", entry.envelope)

    return tuple(sorted(views, key=lambda view: view.identifier))


# ---------------------------------------------------------------------- network


def _concept_node(view: ConceptView) -> dict[str, Any]:
    node: dict[str, Any] = {
        "id": view.identifier,
        "kind": "concept",
        "label": view.label,
        "group": view.group,
        "origin": view.origin,
        "provisions": list(view.provisions),
        "sections": sorted(view.sections),
        "sources": list(view.sources),
        "parts": sorted(view.parts),
    }
    if view.alt_labels:
        node["alt"] = list(view.alt_labels)
    if view.not_labels:
        node["not"] = list(view.not_labels)
    if view.notes:
        node["notes"] = str(view.notes)
    quote = _quote(view)
    if quote:
        node["quote"] = quote
    if view.origin == "approved":
        node["signed"] = {"by": view.signed_by, "date": view.signed_date}
    if view.authored:
        node["authored"] = _envelope(view.authored)
    if view.group:
        node["typing"] = {
            "record": view.typing_record,
            "group": view.group,
            "meaning": GROUP_MEANING.get(view.group),
            "reviewed": bool(view.typed_by is None),
            "authored": _envelope(view.typed_by) if view.typed_by else None,
        }
    return node


def _quote(view: ConceptView) -> dict[str, Any] | None:
    """The first passage the record's own envelope quotes, verbatim.

    Every node on both views used to show a label and a group name, and a
    reader who did not already know the vocabulary had nothing concrete to hold
    on to — the owner's word for it was *abstract*. This puts the corpus's own
    sentence on the face of the node.

    It is a **quotation and never a definition** (the distinction the harness
    enforces, and `test_neither_view_carries_a_definition` pins). The text is
    copied from an `evidence` entry a record already carries, with the ref it
    was taken from, and nothing is written, trimmed to a gist or paraphrased. A
    signed concept carries no envelope of its own, so its quote comes from the
    machine typing that sorted it — and `from` says which of the two it was, so
    a reader is never left guessing whose evidence they are reading.
    """
    for envelope, provenance in (
        (view.authored, "the record's own evidence"),
        (view.typed_by, "the evidence for the group it was sorted into"),
    ):
        for item in (envelope or {}).get("evidence") or ():
            text = str(item.get("quote") or "").strip()
            if text:
                return {"ref": str(item.get("ref") or ""), "text": text, "from": provenance}
    return None


def _envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    """The parts of an authoring envelope a reader needs, and no invented field.

    `review_status` is carried verbatim and never defaulted. A record that
    claimed nothing has claimed nothing, and on a picture that is the one thing
    that must not become "unreviewed" by omission.
    """
    return {
        "review_status": envelope.get("review_status"),
        "authored_by": envelope.get("authored_by"),
        "authored_date": envelope.get("authored_date"),
        "authoring_basis": envelope.get("authoring_basis"),
        "confidence": envelope.get("confidence"),
        "reasoning": envelope.get("reasoning"),
        "expert_should_check": envelope.get("expert_should_check"),
        "alternatives_considered": list(envelope.get("alternatives_considered") or ()),
        "evidence": [
            {"ref": item.get("ref"), "quote": item.get("quote")}
            for item in (envelope.get("evidence") or ())
        ],
    }


def _edge(source: str, target: str, kind: str, **extra: Any) -> dict[str, Any]:
    edge = {"source": source, "target": target, "kind": kind}
    edge.update({key: value for key, value in extra.items() if value not in (None, "", [])})
    return edge


def network(gold: Any, authored: Any) -> dict[str, Any]:
    """Nodes and edges for the map.

    Four edge kinds, all of them things a record already states. The function
    adds nothing: a reader who follows an edge back to its `record` finds the
    same claim in the same words.
    """
    views = concept_views(gold, authored)
    by_id = {view.identifier: view for view in views}

    nodes: list[dict[str, Any]] = [_concept_node(view) for view in views]
    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    def push(source: str, target: str, kind: str, **extra: Any) -> None:
        key = (source, target, kind)
        if key in seen:
            return
        seen.add(key)
        edges.append(_edge(source, target, kind, **extra))

    # 1 and 2 — the hierarchy and the associative links, as the records state
    # them. `broader` is drawn as the same edge read the other way, so a pair
    # recorded on one side only still appears; one such pair exists today.
    for view in views:
        for other in view.narrower:
            if other in by_id:
                push(view.identifier, other, "narrower", origin=view.origin)
        for other in view.broader:
            if other in by_id:
                push(other, view.identifier, "narrower", origin=by_id[other].origin)
        for other in view.related:
            if other in by_id:
                pair = tuple(sorted((view.identifier, other)))
                push(pair[0], pair[1], "related", origin=view.origin)

    # 3 — the 35 signed relationship records. These are the only edges in the
    # project a person put their name to, and the modality on them is the field
    # CLAUDE.md rule 3 exists to protect: five are blank and stay blank.
    provisions: dict[str, dict[str, Any]] = {}

    def provision_node(ref: str) -> str | None:
        root = root_provision(ref)
        if root is None:
            return None
        if ref not in provisions:
            instrument = ref.partition("/")[0]
            provisions[ref] = {
                "id": ref,
                "kind": "provision",
                "label": _provision_label(ref),
                "instrument": instrument,
                "root": root,
                "origin": "corpus",
            }
        return ref

    for record in gold["gold_relationship"]:
        subject, obj = str(record["subject"]), str(record["object"])
        for value in (subject, obj):
            if value not in by_id:
                provision_node(value)
        if (subject in by_id or subject in provisions) and (obj in by_id or obj in provisions):
            push(
                subject,
                obj,
                "asserted",
                origin="approved",
                record=str(record["id"]),
                predicate=str(record["predicate"]),
                modality=record.get("modality"),
                tier=record.get("tier"),
                text=record.get("supporting_text"),
                passage=record.get("source_ref"),
                signed={"by": record.get("approved_by"), "date": record.get("approved_date")},
            )

    # 4 — every provision a concept names as its basis, at the address the
    # record uses. Never rolled up: `root` is an attribute, and the browser
    # offers the rolling-up as a filter the reader can turn off.
    for view in views:
        for ref in view.provisions:
            if provision_node(ref):
                push(view.identifier, ref, "cites", origin=view.origin)

    nodes.extend(provisions[ref] for ref in sorted(provisions))

    degree: dict[str, int] = {node["id"]: 0 for node in nodes}
    for edge in edges:
        for end in (edge["source"], edge["target"]):
            if end in degree:
                degree[end] += 1
    for node in nodes:
        node["degree"] = degree[node["id"]]

    # How many separate pieces the graph is in. The browser recomputes this for
    # whatever the reader has filtered to and prints it under the legend; this
    # is the figure for the whole thing, which is what the page's prose quotes.
    adjacency: dict[str, set[str]] = {node["id"]: set() for node in nodes}
    for edge in edges:
        adjacency[edge["source"]].add(edge["target"])
        adjacency[edge["target"]].add(edge["source"])
    unseen = set(adjacency)
    islands: list[int] = []
    while unseen:
        stack = [unseen.pop()]
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbour in adjacency[current]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
        islands.append(size)
    islands.sort(reverse=True)

    return {
        "nodes": nodes,
        "edges": edges,
        "groups": [
            {"id": value, "label": _group_label(value), "meaning": meaning}
            for value, meaning in typing_module.GROUPS
        ],
        "edgeKinds": [
            {"id": value, "label": label, "meaning": meaning}
            for value, label, meaning in EDGE_KINDS
        ],
        "counts": {
            "concepts": len(views),
            "signed": sum(1 for view in views if view.origin == "approved"),
            "authored": sum(1 for view in views if view.origin == "authored"),
            "provisions": len(provisions),
            "edges": len(edges),
            "signed_edges": sum(1 for edge in edges if edge["kind"] == "asserted"),
            "isolated": sum(1 for node in nodes if node["degree"] == 0),
            "islands": len(islands),
            "largest_island": islands[0] if islands else 0,
        },
    }


def _group_label(value: str) -> str:
    return value.replace("_", " ").capitalize()


# ------------------------------------------------------------------------ tree


@dataclass
class _Branch:
    section: str
    members: dict[str, str] = field(default_factory=dict)  # concept id -> how it joined


def _adjacency(views: Sequence[ConceptView], relationships: Iterable[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """concept -> {neighbour: how they are joined}, over the two edge kinds the
    tree is allowed to walk.

    A SKOS edge and a signed relationship, and nothing else. Shared wording,
    shared Manual Part and shared anything-else are **not** here: they were
    tried, and a rule keyed on a shared Part put all 30 of Part 29's factors
    under section 33 as well as section 43, because one concept cites both
    sections and the Part is the join. A picture that wrong is worse than a
    picture with a gap in it.
    """
    by_id = {view.identifier for view in views}
    adjacency: dict[str, dict[str, str]] = {view.identifier: {} for view in views}
    for view in views:
        for other in (*view.broader, *view.narrower, *view.related):
            if other in by_id:
                adjacency[view.identifier][other] = "a recorded link between the two concepts"
                adjacency[other][view.identifier] = "a recorded link between the two concepts"
    for record in relationships:
        subject, obj = str(record["subject"]), str(record["object"])
        if subject in by_id and obj in by_id:
            how = f"the signed relationship {record['id']}"
            adjacency[subject][obj] = how
            adjacency[obj][subject] = how
    return adjacency


def _section_sort(section: str) -> tuple[str, int, str]:
    instrument, _, address = section.partition("/")
    number = re.search(r"[0-9]+(?:\.[0-9]+)?", address)
    return (instrument, int(float(number.group())) if number else 0, address)


def _tree_node(view: ConceptView, *, basis: str, also: Sequence[str] = ()) -> dict[str, Any]:
    """A node on the tree: what to draw, and the id of the record behind it.

    The record's own detail is **not** repeated here. A concept can sit under
    more than one section — nine do — and repeating the evidence at each one
    put the same paragraph in the file up to three times. `decision_tree`
    returns one `records` map and the browser looks a node up in it.
    """
    node: dict[str, Any] = {
        "id": f"{view.identifier}",
        "label": view.label,
        "kind": view.group or "untyped",
        "record": view.identifier,
        "origin": view.origin,
        "basis": basis,
    }
    if also:
        node["also_under"] = list(also)
    return node


# --------------------------------------------------------------- the questions

#: How a record becomes a question, and nothing more than this happens.
#:
#: A `legal_test` is, in the taxonomy's own words, *"a question the decision
#: maker has to answer"* — so the label of one is put into question form and
#: becomes a branch point. A `ground_of_refusal` is *"a reason an application
#: can be refused"*, so the section that holds one becomes the gate that asks
#: whether it arises. An `exception` is *"something that takes a case out of the
#: rule"*, so it is asked after the tests on the path where they were answered
#: yes.
#:
#: The templates are **mechanical**: a label goes in, a question comes out, and
#: nothing anywhere decides how the question is answered. That distinction is
#: the whole licence for this page — putting a recorded label into question form
#: is arranging, and saying what the answer is would be stating an examination
#: outcome, which the programme does not do (CLAUDE.md §2, ADR-0082).
GATE_TEMPLATES: dict[str, str] = {
    "section": "Does a ground under {provision} arise on this application?",
    "test": "Is {label} made out?",
    "exception": "Does an exception recorded at {provision} apply?",
}


def _depth(node: dict[str, Any]) -> int:
    """The longest path from a node to a leaf, in branch points."""
    children = node.get("children") or ()
    return 1 + max((_depth(child) for child in children), default=0)


def _outcome_leaf(identifier: str, *, variant: str, answer: str | None = None) -> dict[str, Any]:
    """The leaf every path ends on. There are two wordings and neither is an outcome.

    `not_stated` closes a path where a gate was answered; `clear` closes the one
    path where every gate on the spine was answered no. They say different
    things about *where the walk got to* and the same thing about what the
    system concludes, which is nothing (ADR-0105, `PU-0003`).
    """
    node: dict[str, Any] = {
        "id": identifier,
        "kind": "outcome",
        "variant": variant,
        "label": (
            "The outcome — which this system does not state"
            if variant == "not_stated"
            else "No ground recorded here is reached — which is still not an outcome"
        ),
    }
    if answer:
        node["answer"] = answer
    return node


def _consideration(
    view: ConceptView,
    *,
    basis: str,
    also: Sequence[str] = (),
) -> dict[str, Any]:
    """A record to read *at* a gate rather than a branch point of its own.

    Grounds, factors and exceptions arrive here. They are not gates: a factor is
    *"something that feeds into that answer"*, and drawing 32 of them as
    branches off section 43 would say the walk turns on each one in turn, which
    is a claim about practice nobody has made.
    """
    node = _tree_node(view, basis=basis, also=also)
    node["group"] = view.group
    return node


def _gate(
    identifier: str,
    *,
    question: str,
    kind: str,
    yes: dict[str, Any],
    no: dict[str, Any],
    **extra: Any,
) -> dict[str, Any]:
    """One branch point: a question, and exactly two answers.

    Every internal node of the grounds spine is built by this function, which is
    what makes the spine a tree in the ordinary sense rather than an outline
    with indentation. A node with three children would be a node that is not a
    question.
    """
    yes = {**yes, "answer": "yes"}
    no = {**no, "answer": "no"}
    node: dict[str, Any] = {
        "id": identifier,
        "kind": "gate",
        "gate": kind,
        "question": question,
        "children": [yes, no],
    }
    node.update({key: value for key, value in extra.items() if value not in (None, "", [])})
    return node


def _grounds_spine(
    views: Sequence[ConceptView],
    relationships: Sequence[dict[str, Any]],
    prohibited: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """The grounds, as a binary tree of questions.

    The shape is the one an examiner's own working order suggests and the Act's
    numbering supplies: take the sections that hold a ground or a test, in order,
    and ask at each whether a ground under it arises. **No** carries the walk to
    the next section — that is the spine. **Yes** opens the questions recorded at
    that section, each of them a `legal_test` put into question form, and then,
    where the records hold one, the exception.

    Two things this deliberately does not do. It does not say that the tests at a
    section are cumulative: they are chained in the order the records list them,
    and the chain is a walk through the questions rather than a claim that all of
    them must be answered yes. And it does not answer a single one of them — every
    path, at every gate, ends on the same leaf.
    """
    reasoning = [view for view in views if view.group in REASONING_GROUPS]
    by_id = {view.identifier: view for view in reasoning}
    anchors = [view for view in reasoning if view.group in ANCHOR_GROUPS]
    sections = {section for view in anchors for section in view.joinable_sections}

    assigned: dict[str, set[str]] = {}
    basis: dict[str, str] = {}
    for view in reasoning:
        joined = view.joinable_sections & sections
        if joined:
            assigned[view.identifier] = set(joined)
            basis[view.identifier] = "its record cites the section"

    adjacency = _adjacency(reasoning, relationships)
    frontier = sorted(assigned)
    while frontier:
        nxt: list[str] = []
        for identifier in frontier:
            for neighbour, how in sorted(adjacency[identifier].items()):
                if neighbour in assigned or neighbour not in by_id:
                    continue
                assigned[neighbour] = set(assigned[identifier])
                basis[neighbour] = f"{how}, which does"
                nxt.append(neighbour)
        frontier = sorted(nxt)

    ordered = sorted(sections, key=_section_sort)

    def at(section: str, group: str) -> list[ConceptView]:
        return [
            view
            for view in reasoning
            if view.group == group and section in assigned.get(view.identifier, ())
        ]

    def considerations(section: str, group: str) -> list[dict[str, Any]]:
        return [
            _consideration(
                view,
                basis=basis[view.identifier],
                also=sorted(assigned[view.identifier] - {section}, key=_section_sort),
            )
            for view in at(section, group)
        ]

    def section_gate(position: int) -> dict[str, Any]:
        """The gate for one section, with the rest of the spine hanging off *no*."""
        section = ordered[position]
        grounds = considerations(section, "ground_of_refusal")
        factors = considerations(section, "relevant_factor")
        exceptions = considerations(section, "exception")
        tests = at(section, "legal_test")

        # The yes path, built from the inside out: the last thing on it is the
        # leaf, then the exception if there is one, then the tests in reverse.
        tail = (
            _gate(
                f"{section}::exception",
                question=GATE_TEMPLATES["exception"].format(provision=_provision_label(section)),
                kind="exception",
                provision=section,
                yes=_outcome_leaf(f"{section}::exception::yes", variant="not_stated"),
                no=_outcome_leaf(f"{section}::exception::no", variant="not_stated"),
                considerations=exceptions,
                note=(
                    "Whether any of these applies is the decision maker's, and either answer "
                    "leaves the outcome where the records leave it."
                ),
            )
            if exceptions
            else _outcome_leaf(f"{section}::outcome", variant="not_stated")
        )
        for order, view in enumerate(reversed(tests)):
            tail = _gate(
                f"{view.identifier}@{section}",
                question=GATE_TEMPLATES["test"].format(label=view.label),
                kind="test",
                record=view.identifier,
                label=view.label,
                origin=view.origin,
                provision=section,
                basis=basis[view.identifier],
                also_under=sorted(assigned[view.identifier] - {section}, key=_section_sort),
                position=len(tests) - order,
                of=len(tests),
                yes=tail,
                no=_outcome_leaf(f"{view.identifier}@{section}::no", variant="not_stated"),
            )

        no_path = (
            section_gate(position + 1)
            if position + 1 < len(ordered)
            else _outcome_leaf("spine::clear", variant="clear")
        )
        return _gate(
            section,
            question=GATE_TEMPLATES["section"].format(provision=_provision_label(section)),
            kind="section",
            provision=section,
            instrument=section.partition("/")[0],
            label=_provision_label(section),
            yes=tail,
            no=no_path,
            #: The grounds **and** the factors, on the gate for the section that
            #: holds them. A factor is read at the branch point, not walked
            #: through: no record says which test a factor feeds, and hanging
            #: them off the first question would say one does. It also has to be
            #: here rather than there because three sections hold factors and no
            #: test at all — section 33 among them — and a factor filed against a
            #: question that does not exist is a factor nobody can reach.
            considerations=grounds + factors,
            count=len([view for view in reasoning if section in assigned.get(view.identifier, ())]),
            tests=len(tests),
            factors=len(factors),
            exceptions=len(exceptions),
            gap=None if grounds else (
                "No concept in either store is typed as a ground for refusal at this section, "
                "although a test or a factor here is. The question above is still asked, "
                "because the Act's section is there; what is missing is the record naming the "
                "ground it asks about. That is a hole in the vocabulary, not a fact about the Act."
            ),
        )

    root = {
        "id": "root",
        "kind": "root",
        "label": "An application under examination",
        "meaning": (
            "The walk starts here and goes section by section. Nothing about the application "
            "itself is held anywhere in this project — the mark, the goods and the applicant "
            "are all outside it — so this node is the starting point and not a record."
        ),
        "children": [section_gate(0)] if ordered else [],
    }

    stranded = [view for view in reasoning if view.identifier not in assigned]

    def walk(node: dict[str, Any]) -> Iterable[dict[str, Any]]:
        yield node
        for child in node.get("children") or ():
            yield from walk(child)

    drawn = list(walk(root))
    return {
        "id": "grounds",
        "label": "Grounds for rejection",
        "lede": (
            "Every concept typed as a **ground**, a **test**, a **factor** or an "
            "**exception**, arranged as the questions they are. Each section of the Act that "
            "holds a ground or a test becomes one branch point: answer **no** and the walk "
            "moves to the next section, answer **yes** and it opens the questions recorded "
            "there. The shape is computed from the records on every build — it is not a "
            "procedure anybody wrote down, and no expert has read it."
        ),
        "root": root,
        "residue": {
            "id": "unattached",
            "label": "Attached to no section, so on no path",
            "kind": "residue",
            "count": len(stranded),
            "children": [
                _consideration(view, basis="nothing joins it to a section that anchors a gate")
                for view in stranded
            ],
            "gap": (
                "These records cite a provision, but no ground or test concept cites the same "
                "one, and nothing joins them to a concept that does. They are shown here, off "
                "the walk, rather than filed somewhere plausible."
            ),
        } if stranded else None,
        "counts": {
            "concepts": len(reasoning),
            "placed": len(assigned),
            "by_citation": sum(1 for value in basis.values() if value.startswith("its record")),
            "by_link": sum(1 for value in basis.values() if not value.startswith("its record")),
            "stranded": len(stranded),
            "sections": len(sections),
            #: Branch points actually drawn, not concepts that could be one. A test
            #: cited by two sections is asked on both paths, and a reader counting
            #: the diamonds on the canvas has to arrive at this number.
            "gates": sum(1 for node in drawn if node["kind"] == "gate"),
            "leaves": sum(1 for node in drawn if node["kind"] == "outcome"),
            "depth": _depth(root),
            "without_a_ground": sum(
                1
                for section in ordered
                if not any(
                    view.group == "ground_of_refusal" and section in assigned.get(view.identifier, ())
                    for view in reasoning
                )
            ),
            "in_more_than_one": sum(1 for value in assigned.values() if len(value) > 1),
        },
    }


def _outcome(prohibited: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """What the leaf means, and the signed records it rests on — held once.

    Every path on the grounds spine ends on an outcome leaf and there are
    thirty-odd of them, so the wording and the records sit here and the leaves
    carry an id. Repeating this at each leaf put the same three approved records
    in the file thirty times.
    """
    conclusions = [record for record in prohibited if record.get("kind") == "evaluative_conclusion"]
    return {
        "label": "The outcome — which this system does not state",
        "meaning": (
            "Whether a ground arises on a given application is the decision maker's "
            "judgement. The project does not automate it, and "
            f"{len(conclusions)} expert-approved prohibited-use records say so in terms."
        ),
        "records": [
            {
                "id": str(record["id"]),
                "label": str(record["prohibited"]),
                "kind": "prohibited",
                "record": str(record["id"]),
                "origin": "approved",
                "notes": str(record.get("why") or ""),
                "signed": {"by": record.get("approved_by"), "date": record.get("approved_date")},
            }
            for record in conclusions
        ],
    }


def _procedure_spine(views: Sequence[ConceptView], relationships: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The five process groups, ordered by the Act's own section numbers.

    The order is the Act's, not a reading of how examination runs. The Act
    happens to number its Parts roughly in process order, which is why this is
    legible at all; where it does not, the tree is wrong about sequence and
    right about content, and the lede says so.

    This spine is **not** binary and must not be drawn as though it were. A step
    is not a question — nothing is decided by reaching *examination* — so the
    steps run one after another and what is recorded at each hangs off it. The
    grounds spine asks; this one sequences.
    """
    process = [view for view in views if view.group in PROCESS_GROUPS]
    steps = [view for view in process if view.group == "procedural_step"]
    adjacency = _adjacency(views, relationships)

    def first_section(view: ConceptView) -> tuple[str, int, str]:
        """Order a step by the **first** provision its own record lists.

        Not the lowest-numbered one. A record's `legislative_basis` is written
        in the order its author put it in, and the first entry is the provision
        the step is about; the later ones are usually a definition or a
        cross-reference. Sorting on the minimum put *removal for non-use* ahead
        of *examination*, because it happens to also cite section 17.
        """
        for ref in view.provisions:
            root = root_provision(ref)
            if root and ref.count("/") < 2:
                return _section_sort(root)
        return ("zz", 10**6, view.identifier)

    attached: set[str] = set()
    children: list[dict[str, Any]] = []
    for order, step in enumerate(sorted(steps, key=first_section), start=1):
        near: list[dict[str, Any]] = []
        for other in process:
            if other.identifier == step.identifier or other.group == "procedural_step":
                continue
            shared = sorted(other.joinable_sections & step.joinable_sections, key=_section_sort)
            if shared:
                near.append(_consideration(other, basis=f"shares {shared[0]} with this step"))
                attached.add(other.identifier)
            elif other.identifier in adjacency.get(step.identifier, {}):
                near.append(
                    _consideration(other, basis=adjacency[step.identifier][other.identifier])
                )
                attached.add(other.identifier)
        node = _tree_node(step, basis="typed as a step in the process")
        node["kind"] = "step"
        node["group"] = step.group
        node["position"] = order
        node["of"] = len(steps)
        node["children"] = near
        node["count"] = len(near)
        children.append(node)

    loose = [view for view in process if view.group != "procedural_step" and view.identifier not in attached]
    return {
        "id": "procedure",
        "label": "The procedural path",
        "lede": (
            f"The {len(process)} concepts typed as part of the **process** rather than the "
            "reasoning: who acts, what is acted on, what act is performed, what it produces. "
            "**Nothing here is a question** — a step is reached, not decided — so this spine "
            "runs in sequence rather than branching. The steps are ordered by the **first "
            "provision each record cites**, which puts them in the Act's order, not "
            "necessarily the order an examiner does them. **Only "
            f"{len(attached)} of the {len(process) - len(steps)} non-step concepts join a step "
            "at all**: the edges that would join the rest have not been written yet, and this "
            "spine is mostly a picture of that."
        ),
        "root": {
            "id": "root",
            "kind": "root",
            "label": "An application, from filing to the Register",
            "meaning": (
                "The 21 steps the records hold, in the Act's order. Following one opens what "
                "the records attach to it."
            ),
            "children": children,
        },
        "residue": {
            "id": "unattached-process",
            "label": "Attached to no step",
            "kind": "residue",
            "count": len(loose),
            "children": [
                _consideration(view, basis="shares no provision and no recorded link with any step")
                for view in loose
            ],
            "gap": (
                "Who acts, what is acted on and what the process produces — held as records, "
                "joined to no step by anything either store states."
            ),
        } if loose else None,
        "counts": {
            "concepts": len(process),
            "steps": len(steps),
            "attached": len(attached),
            "stranded": len(loose),
        },
    }


def decision_tree(gold: Any, authored: Any) -> dict[str, Any]:
    """Both spines, the rules that built them, and what each one left over."""
    views = concept_views(gold, authored)
    relationships = list(gold["gold_relationship"])
    prohibited = list(gold["prohibited_use"])
    grounds = _grounds_spine(views, relationships, prohibited)
    procedure = _procedure_spine(views, relationships)
    untyped = [view for view in views if view.group is None]
    outside = [view for view in views if view.group == "none_of_these"]

    return {
        "records": {view.identifier: _concept_node(view) for view in views},
        "outcome": _outcome(prohibited),
        "spines": [grounds, procedure],
        "rules": [
            "A section of the Act becomes a **branch point** when a concept typed as a "
            "**ground for refusal** or a **legal test** cites it. The question it asks is "
            "whether a ground under that section arises.",
            "**No** goes to the next section, in the Act's numbering. **Yes** opens the "
            "questions recorded at this one.",
            "Each concept typed as a **legal test** becomes a question of its own, because "
            "that is what the group means — *a question the decision maker has to answer*. "
            "Its label is put into question form and nothing else is done to it.",
            "The tests at a section are walked in the order the records list them. **That is "
            "an order, not a claim that they are cumulative** — nothing in the records says "
            "which must be answered before which, or that all of them must be answered yes.",
            "A concept typed as a **factor** is not a branch point: it is read *at* one. "
            "Factors hang off the section that holds them, because no record says which test "
            "a factor feeds.",
            "A concept joins a section when its own record cites it; failing that, when a "
            "**signed relationship** or a recorded `broader` / `narrower` / `related` link "
            "joins it to a concept that does.",
            "A concept that joins nothing is shown beneath the tree, off the walk, and a "
            "section with no ground concept is marked. Both are gaps in the vocabulary.",
            "**Every path ends on the same leaf: the outcome, which this system does not "
            "state.** No answer anywhere in this tree is supplied by the project.",
        ],
        "counts": {
            "concepts": len(views),
            "reasoning": grounds["counts"]["concepts"],
            "process": procedure["counts"]["concepts"],
            "outside": len(outside),
            "untyped": len(untyped),
            "gates": grounds["counts"]["gates"],
        },
        "outside": [
            {
                "id": view.identifier,
                "label": view.label,
                "origin": view.origin,
                "notes": str(view.notes or ""),
            }
            for view in outside
        ],
    }

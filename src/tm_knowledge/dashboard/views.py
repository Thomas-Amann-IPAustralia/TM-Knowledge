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

*The decision tree* hangs the four reasoning groups off the sections of the Act
they cite. A section becomes a branch when a `ground_of_refusal` or a
`legal_test` concept cites it; a concept joins that branch when it cites the
section itself, or when a signed relationship or a SKOS edge joins it to a
concept that does. A concept that joins no branch is shown in a branch of its
own, and a branch holding tests but no ground concept is marked as such —
both of those are findings, and hiding them would be the whole failure mode of
a picture (ADR-0105).
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


def _grounds_spine(
    views: Sequence[ConceptView],
    relationships: Sequence[dict[str, Any]],
    prohibited: Sequence[dict[str, Any]],
) -> dict[str, Any]:
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

    branches: list[dict[str, Any]] = []
    for section in sorted(sections, key=_section_sort):
        members = [view for view in reasoning if section in assigned.get(view.identifier, ())]
        children: list[dict[str, Any]] = []
        for group in REASONING_GROUPS:
            at_group = [view for view in members if view.group == group]
            if not at_group:
                continue
            children.append(
                {
                    "id": f"{section}::{group}",
                    "label": _group_label(group),
                    "kind": "band",
                    "meaning": GROUP_MEANING.get(group),
                    "children": [
                        _tree_node(
                            view,
                            basis=basis[view.identifier],
                            also=sorted(assigned[view.identifier] - {section}, key=_section_sort),
                        )
                        for view in at_group
                    ],
                }
            )
        has_ground = any(view.group == "ground_of_refusal" for view in members)
        children.append(_outcome_node(section, prohibited))
        branches.append(
            {
                "id": section,
                "label": _provision_label(section),
                "kind": "section",
                "instrument": section.partition("/")[0],
                "provision": section,
                "children": children,
                "count": len(members),
                "gap": None if has_ground else (
                    "No concept in either store is typed as a ground for refusal at this "
                    "section, although a test or a factor here is. That is a hole in the "
                    "vocabulary, not a fact about the Act."
                ),
            }
        )

    stranded = [view for view in reasoning if view.identifier not in assigned]
    if stranded:
        branches.append(
            {
                "id": "unattached",
                "label": "Attached to no section",
                "kind": "residue",
                "children": [
                    _tree_node(view, basis="nothing joins it to a section that anchors a branch")
                    for view in stranded
                ],
                "count": len(stranded),
                "gap": (
                    "These records cite a provision, but no ground or test concept cites the "
                    "same one, and nothing joins them to a concept that does. They are shown "
                    "here rather than filed somewhere plausible."
                ),
            }
        )

    return {
        "id": "grounds",
        "label": "Grounds for rejection",
        "lede": (
            "Every concept typed as a **ground**, a **test**, a **factor** or an "
            "**exception**, hung off the section of the Act its record cites. The shape is "
            "computed from the records on every build — it is not a procedure anybody wrote "
            "down, and no expert has read it."
        ),
        "root": {
            "id": "root",
            "label": "An application under examination",
            "kind": "root",
            "children": branches,
        },
        "counts": {
            "concepts": len(reasoning),
            "placed": len(assigned),
            "by_citation": sum(1 for value in basis.values() if value.startswith("its record")),
            "by_link": sum(1 for value in basis.values() if not value.startswith("its record")),
            "stranded": len(stranded),
            "sections": len(sections),
            "without_a_ground": sum(1 for branch in branches if branch.get("gap") and branch["kind"] == "section"),
            "in_more_than_one": sum(1 for value in assigned.values() if len(value) > 1),
        },
    }


def _outcome_node(section: str, prohibited: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The leaf every branch ends on, and the only node the tree adds itself.

    A decision tree with no leaf reads as though the branch above it reaches
    one. This one says, in the signed records' own terms, that it does not —
    and it is the node to read before anything is built on this tree.
    """
    conclusions = [record for record in prohibited if record.get("kind") == "evaluative_conclusion"]
    return {
        "id": f"{section}::outcome",
        "label": "The outcome — which this system does not state",
        "kind": "outcome",
        "meaning": (
            "Whether a ground arises on a given application is the decision maker's "
            "judgement. The project does not automate it, and "
            f"{len(conclusions)} expert-approved prohibited-use records say so in terms."
        ),
        "children": [
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
    for step in sorted(steps, key=first_section):
        near: list[dict[str, Any]] = []
        for other in process:
            if other.identifier == step.identifier or other.group == "procedural_step":
                continue
            shared = sorted(other.joinable_sections & step.joinable_sections, key=_section_sort)
            if shared:
                near.append(_tree_node(other, basis=f"shares {shared[0]} with this step"))
                attached.add(other.identifier)
            elif other.identifier in adjacency.get(step.identifier, {}):
                near.append(
                    _tree_node(other, basis=adjacency[step.identifier][other.identifier])
                )
                attached.add(other.identifier)
        node = _tree_node(step, basis="typed as a step in the process")
        node["children"] = near
        node["count"] = len(near)
        children.append(node)

    loose = [view for view in process if view.group != "procedural_step" and view.identifier not in attached]
    root_children: list[dict[str, Any]] = list(children)
    if loose:
        root_children.append(
            {
                "id": "unattached-process",
                "label": "Attached to no step",
                "kind": "residue",
                "count": len(loose),
                "children": [
                    _tree_node(view, basis="shares no provision and no recorded link with any step")
                    for view in loose
                ],
                "gap": (
                    "Who acts, what is acted on and what the process produces — held as "
                    "records, joined to no step by anything either store states."
                ),
            }
        )

    return {
        "id": "procedure",
        "label": "The procedural path",
        "lede": (
            f"The {len(process)} concepts typed as part of the **process** rather than the "
            "reasoning: who acts, what is acted on, what act is performed, what it produces. "
            "The steps are ordered by the **first provision each record cites**, which puts "
            "them in the Act's order — not necessarily the order an examiner does them, and "
            f"nothing here claims otherwise. **Only {len(attached)} of the "
            f"{len(process) - len(steps)} non-step concepts join a step at all**: the edges "
            "that would join the rest have not been written yet, and this spine is mostly a "
            "picture of that."
        ),
        "root": {
            "id": "root",
            "label": "An application, from filing to the Register",
            "kind": "root",
            "children": root_children,
        },
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
        "spines": [grounds, procedure],
        "rules": [
            "A section of the Act becomes a branch when a concept typed as a **ground for "
            "refusal** or a **legal test** cites it.",
            "A concept joins that branch when its own record cites the section.",
            "Failing that, it joins when a **signed relationship** or a recorded "
            "`broader` / `narrower` / `related` link joins it to a concept that does.",
            "A concept that joins nothing is shown under *Attached to no section*, and a "
            "branch with no ground concept is marked. Both are gaps in the vocabulary.",
            "Every branch ends on the same leaf: the outcome, which this system does not state.",
        ],
        "counts": {
            "concepts": len(views),
            "reasoning": grounds["counts"]["concepts"],
            "process": procedure["counts"]["concepts"],
            "outside": len(outside),
            "untyped": len(untyped),
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

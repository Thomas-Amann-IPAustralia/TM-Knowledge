"""Load the draft ontology modules.

The `.ttl` files are authored against the default base IRI, because a Turtle
file has to name one and the base is still an open organisational question
(HANDOFF Q7). `load()` rewrites every project IRI when `TMK_BASE_IRI` says
otherwise, so `docs/IDENTIFIERS.md`'s rule holds — the base lives in one
constant, and changing it is a configuration change plus a rebuild rather than a
find-and-replace across serialised RDF.

The modules are a fixed, ordered list rather than a glob. A module appearing on
disk and being picked up silently is how an unreviewed file joins the ontology.
"""

from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, URIRef

from tm_knowledge.config import DEFAULT_BASE_IRI, REPO_ROOT, base_iri
from tm_knowledge.ontology.namespaces import bind_all

__all__ = ["DRAFT_DIR", "MODULES", "load", "module_paths"]

DRAFT_DIR = REPO_ROOT / "ontology" / "draft"

#: The modules, in dependency order. `relations.ttl` is generated
#: (`tm_knowledge.ontology.relations`); the rest are authored.
MODULES: tuple[str, ...] = (
    "document.ttl",
    "authority.ttl",
    "legal-concepts.ttl",
    "provenance.ttl",
    "relations.ttl",
    "examination.ttl",
    "evidence.ttl",
    "time.ttl",
    "evaluation.ttl",
)


def module_paths(root: Path | None = None) -> tuple[Path, ...]:
    root = root or DRAFT_DIR
    return tuple(root / name for name in MODULES)


def _rebase(graph: Graph, target: str) -> Graph:
    """Move every IRI under the default base onto the configured one."""
    if target == DEFAULT_BASE_IRI:
        return graph

    def move(term):
        if isinstance(term, URIRef) and str(term).startswith(DEFAULT_BASE_IRI):
            return URIRef(target + str(term)[len(DEFAULT_BASE_IRI) :])
        return term

    rebased = Graph()
    for subject, predicate, obj in graph:
        rebased.add((move(subject), move(predicate), move(obj) if not isinstance(obj, Literal) else obj))
    return rebased


def load(root: Path | None = None) -> Graph:
    """The whole draft TBox as one graph, under the configured base IRI."""
    graph = Graph()
    for path in module_paths(root):
        if not path.exists():
            raise FileNotFoundError(
                f"ontology module {path.name} is missing. MODULES is a fixed list on "
                f"purpose — add the file, or remove it from tbox.MODULES."
            )
        graph.parse(path, format="turtle")
    return bind_all(_rebase(graph, base_iri()))

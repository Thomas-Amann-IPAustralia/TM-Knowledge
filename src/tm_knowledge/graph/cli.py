"""`tmk-graph` — build the vocabulary, the ontology, the graph and the shapes.

Writes into `vocab/`, `ontology/`, `graph/`, `shapes/` and `queries/`, all of
which hold **approved** content (ARCHITECTURE §3). That is only allowed because
every triple comes from a record in `eval/gold/` that carries a name and a date
(ADR-0056); the build refuses outright if it is pointed at a gold set whose
records are not approved, because the one-way rule in ADR-0007 is the whole
architecture and a build command is exactly where it would get quietly broken.

`--demo` runs the demonstration queries against what was built and prints the
answers. It needs the `[graph]` extra; everything else here needs nothing beyond
the three core dependencies.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import goldset

__all__ = ["main", "write_all", "unapproved"]


def unapproved(gold: goldset.GoldSet) -> list[str]:
    """Ids of gold records with no name against them.

    `eval/gold/` is approved space and the harness already checks this, but the
    check is repeated here because this is the command that copies content into
    `vocab/` and `graph/`. A guard that lives only upstream of the door is a
    guard that stops working the first time somebody runs the door directly.
    """
    from tm_knowledge.stage0.schemas import RECORD_TYPES

    missing: list[str] = []
    for record_type in RECORD_TYPES:
        for record in gold[record_type]:
            if not str(record.get("approved_by") or "").strip():
                missing.append(str(record.get("id") or f"<{record_type} with no id>"))
    return sorted(missing)


def write_all(root: Path | None = None, base: str | None = None) -> dict[str, int]:
    """Write every generated artefact. Returns path -> triple or byte count."""
    from tm_knowledge.graph import build as build_module
    from tm_knowledge.graph import ontology, queries, shapes

    root = root or REPO_ROOT
    written: dict[str, int] = {}

    for module, (filename, _, _) in ontology.MODULES.items():
        path = root / "ontology" / filename
        text = ontology.render(module, base)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written[str(path.relative_to(root))] = text.count("\n")

    result = build_module.build(base=base)
    for stem, document in result.documents.items():
        path = root / f"{stem}.ttl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document.render(), encoding="utf-8")
        written[str(path.relative_to(root))] = result.counts[stem]

    shapes_path = root / "shapes" / shapes.SHAPES_FILE
    shapes_path.parent.mkdir(parents=True, exist_ok=True)
    shapes_path.write_text(shapes.render(base), encoding="utf-8")
    written[str(shapes_path.relative_to(root))] = 1

    for query in queries.QUERIES:
        path = root / "queries" / f"{query.name}.rq"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(queries.render(query, base), encoding="utf-8")
        written[str(path.relative_to(root))] = 1

    return written


def _load_dataset(root: Path, base: str | None = None):
    """Every generated Turtle file in one rdflib graph. Needs the [graph] extra."""
    try:
        from rdflib import Graph
    except ModuleNotFoundError as error:  # pragma: no cover - depends on install
        raise SystemExit(
            "running the demonstration queries needs rdflib: "
            'pip install -e ".[graph]"'
        ) from error

    from tm_knowledge.graph import ontology
    from tm_knowledge.graph.model import NAMED_GRAPHS

    graph = Graph()
    for stem in NAMED_GRAPHS:
        graph.parse(root / f"{stem}.ttl", format="turtle")
    for _, (filename, _, _) in ontology.MODULES.items():
        graph.parse(root / "ontology" / filename, format="turtle")
    return graph


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-graph",
        description=(
            "Build the SKOS vocabulary, the ontology modules, the knowledge "
            "graph and the SHACL shapes from the approved gold set. Emits only "
            "what a person has signed."
        ),
    )
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--base",
        default=None,
        help="base IRI to mint under. Defaults to TMK_BASE_IRI, then to the "
        "proposed production base (HANDOFF Q7 — unconfirmed).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="run the demonstration queries against what was built and print "
        "the answers. Needs the [graph] extra.",
    )
    parser.add_argument(
        "--limit", type=int, default=6, help="rows per demonstration query"
    )
    parser.add_argument(
        "--report",
        nargs="?",
        type=Path,
        const=REPO_ROOT / "data" / "derived" / "reports" / "ontology-demonstration.md",
        default=None,
        help="write the demonstration report, with every number computed from "
        "what was just built. Needs the [graph] extra, and the pinned snapshot "
        "for the search comparison.",
    )
    args = parser.parse_args(argv)

    root = args.root or REPO_ROOT
    gold = goldset.load()
    if not gold.total:
        print("eval/gold/ is empty — nothing approved to build from", file=sys.stderr)
        return 2

    missing = unapproved(gold)
    if missing:
        print(
            f"refusing to build: {len(missing)} gold record(s) carry no "
            f"approved_by — {', '.join(missing[:5])}"
            + (" …" if len(missing) > 5 else ""),
            file=sys.stderr,
        )
        return 1

    written = write_all(root, args.base)
    from tm_knowledge.graph import build as build_module

    result = build_module.build(gold, args.base)

    print(f"built from {gold.total} approved records")
    for path in sorted(written):
        if path.endswith(".ttl") and ("graph/" in path or "vocab/" in path):
            print(f"  {path:34} {written[path]:5} triples")
    print(f"  {'ontology/ (6 modules)':34} {len([p for p in written if 'ontology/' in p]):5} files")
    print(f"  {'queries/ (.rq)':34} {len([p for p in written if p.endswith('.rq')]):5} files")
    print(f"\n{result.total} triples over {len(result.documents)} named graphs")

    if result.unpopulated:
        print(
            f"\n{len(result.unpopulated)} class(es) declared and deliberately empty — "
            "membership is a legal judgement no approved record carries:"
        )
        print("  " + ", ".join(result.unpopulated))

    if result.conflicts:
        print(f"\n{len(result.conflicts)} opposed pair(s) among approved records:")
        for first, second, detail in result.conflicts:
            print(f"  {first} vs {second}: {detail}")

    if args.demo:
        print()
        _run_demo(root, args.base, args.limit)

    if args.report is not None:
        from tm_knowledge.graph import report as report_module

        corpus = None
        try:
            from tm_knowledge.upstream.loader import load_corpus

            corpus = load_corpus()
        except Exception as error:  # noqa: BLE001 - the report says so instead
            print(f"\nsnapshot not open: {error}", file=sys.stderr)
            print("the search comparison will be omitted", file=sys.stderr)

        text = report_module.render(
            root, _load_dataset(root, args.base), corpus, limit=args.limit
        )
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
        print(f"\nwrote {args.report}")

    return 0


def _run_demo(root: Path, base: str | None, limit: int) -> None:
    from tm_knowledge.graph import queries as query_module

    dataset = _load_dataset(root, base)
    print(f"dataset loaded: {len(dataset)} triples\n")
    for query in query_module.QUERIES:
        rows = list(dataset.query(query_module.render(query, base)))
        print(f"── {query.title}")
        print(f"   {len(rows)} row(s)")
        for row in rows[:limit]:
            values = [
                _short(str(value), base) for value in row if value is not None
            ]
            print("     " + " · ".join(v for v in values if v)[:200])
        if len(rows) > limit:
            print(f"     … {len(rows) - limit} more")
        print()


def _short(value: str, base: str | None = None) -> str:
    from tm_knowledge.graph.model import project_prefixes

    for prefix, expansion in project_prefixes(base).items():
        if value.startswith(expansion):
            return prefix + ":" + value[len(expansion) :]
    for prefix, expansion in (
        ("skos", "http://www.w3.org/2004/02/skos/core#"),
        ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ):
        if value.startswith(expansion):
            return prefix + ":" + value[len(expansion) :]
    return " ".join(value.split())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

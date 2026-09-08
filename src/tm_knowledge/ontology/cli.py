"""Command line entry points for the ontology and graph layer.

Four commands, and the split between them is the same one `tmk-harness` and
`tmk-coverage` already draw: build, gate, ask, report. Each writes to stdout and
sets an exit code; none of them repairs anything.

Exit codes match the harness (ADR-0030): 0 clean, 1 defects, 3 gaps only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tm_knowledge.ontology import ask as ask_module
from tm_knowledge.ontology import flags as flags_module
from tm_knowledge.ontology import relations as relations_module
from tm_knowledge.ontology import report as report_module
from tm_knowledge.ontology import rules as rules_module
from tm_knowledge.ontology import validate as validate_module
from tm_knowledge.ontology.build import (
    GRAPH_DIR,
    build as build_graph,
    check as check_graph,
    write as write_graph,
)

__all__ = ["graph", "shacl", "ask", "ontology_report"]


def graph(argv: list[str] | None = None) -> int:
    """`tmk-graph` — build the dataset and, with `--write`, serialise it."""
    parser = argparse.ArgumentParser(
        prog="tmk-graph",
        description=(
            "Build the knowledge graph from the pinned snapshot, eval/gold/ and "
            "authored/. The two record stores land in two named graphs and are "
            "never summed (ADR-0080)."
        ),
    )
    parser.add_argument("--write", action="store_true", help="serialise into graph/")
    parser.add_argument("--rules", action="store_true", help="also run the CONSTRUCT rules")
    parser.add_argument("--out", type=Path, default=None, help="output directory (default: graph/)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if what is committed under graph/ differs from a rebuild",
    )
    args = parser.parse_args(argv)

    dataset, report = build_graph()
    print("\n".join(report.lines()))

    if args.rules:
        dataset, counts = rules_module.apply_rules(dataset)
        print("\nCONSTRUCT rules — an unapproved rule's output is stamped review_status=candidate")
        for rule in rules_module.load_rules():
            state = "approved" if rule.is_approved else "candidate — quarantined"
            got = counts.get(rule.rule_id)
            # Both numbers, always. The conclusion count is the one that means
            # something to a person; the triple count is the one that used to be
            # quoted at them as if it did (Q-44).
            print(f"  {rule.rule_id}  {got.assertions if got else 0:>4} conclusions "
                  f"({got.triples if got else 0:>5} triples)  {state}")

    if args.check:
        # The whole graph is committed (ADR-0070), and a committed generated
        # file that has drifted is worse than one nobody committed: it reads as
        # current. `--check` must run with `--rules` to compare inferred.ttl,
        # since without them the inferred graph is empty by construction.
        stale = check_graph(dataset, args.out or GRAPH_DIR)
        if stale:
            print("\nThe committed graph no longer matches a rebuild:", file=sys.stderr)
            for line in stale:
                print(f"  {line}", file=sys.stderr)
            print(
                "\nRun `tmk-graph --write --rules` and commit the result. Someone reading "
                "graph/ without rebuilding is reading what these files say.",
                file=sys.stderr,
            )
            return 1
        print("\nThe committed graph matches a rebuild.")
        return 0

    if args.write:
        for path in write_graph(dataset, args.out or GRAPH_DIR):
            print(f"wrote {path.relative_to(path.parents[1])}")
    else:
        print("\n(dry run — nothing written. Pass --write.)")
    return 0


def shacl(argv: list[str] | None = None) -> int:
    """`tmk-shacl` — the publication gate."""
    parser = argparse.ArgumentParser(
        prog="tmk-shacl", description="Validate the built graph against shapes/."
    )
    parser.add_argument("--rules", action="store_true", help="validate after running the rules")
    args = parser.parse_args(argv)

    dataset, _ = build_graph()
    if args.rules:
        dataset, _ = rules_module.apply_rules(dataset)
    report = validate_module.run(dataset)
    print("\n".join(report.lines()))
    return report.exit_code


def ask(argv: list[str] | None = None) -> int:
    """`tmk-ask` — run the competency queries and print their answers."""
    parser = argparse.ArgumentParser(
        prog="tmk-ask", description="Answer the competency questions from the graph."
    )
    parser.add_argument("question", nargs="?", help="one question id, e.g. CQ-0017")
    parser.add_argument("--rules", action="store_true", help="run the candidate rules first")
    args = parser.parse_args(argv)

    dataset, _ = build_graph()
    if args.rules:
        dataset, _ = rules_module.apply_rules(dataset)

    queries = ask_module.load_queries()
    if args.question:
        queries = tuple(q for q in queries if q.question_id == args.question)
        if not queries:
            print(f"no query for {args.question}", file=sys.stderr)
            return 1
    print("\n".join(ask_module.run(dataset, queries)))
    return 0


def relations(argv: list[str] | None = None) -> int:
    """`tmk-ontology-relations` — regenerate the closed predicate list."""
    parser = argparse.ArgumentParser(
        prog="tmk-ontology-relations",
        description="Regenerate ontology/draft/relations.ttl from eval/gold/relationships.yaml.",
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rendered = relations_module.render(relations_module.collect())
    current = (
        relations_module.RELATIONS_PATH.read_text(encoding="utf-8")
        if relations_module.RELATIONS_PATH.exists()
        else ""
    )
    if rendered == current:
        print("relations.ttl is current")
        return 0
    if args.write:
        print(f"wrote {relations_module.write()}")
        return 0
    print("relations.ttl is STALE — rerun with --write", file=sys.stderr)
    return 1


def ontology_report(argv: list[str] | None = None) -> int:
    """`tmk-ontology-report` — the state of the draft, as a committed report."""
    parser = argparse.ArgumentParser(
        prog="tmk-ontology-report",
        description="What the ontology draft holds, what it answers, and what it cannot.",
    )
    parser.add_argument("--write", action="store_true", help="write into data/derived/reports/")
    args = parser.parse_args(argv)

    text = report_module.render()
    if args.write:
        path = report_module.write(text)
        print(f"wrote {path}")
    else:
        print(text)
    return 0


def flags(argv: list[str] | None = None) -> int:
    """`tmk-flags` — the review pack for RULE-0001, for the owner to rule on."""
    parser = argparse.ArgumentParser(
        prog="tmk-flags",
        description="Every passage RULE-0001 flags, in full, with the expert typing that fired it.",
    )
    parser.add_argument("--write", action="store_true", help="write into data/derived/reports/")
    parser.add_argument(
        "--generated", default=None, help="the build stamp (default: today), for a reproducible run"
    )
    args = parser.parse_args(argv)

    if args.write:
        print(f"wrote {flags_module.write(generated=args.generated)}")
    else:
        print(flags_module.render(args.generated))
    return 0

"""`tmk-explain` — explain a fictional matter, as text or as the prototype page; or run a fictional amendment."""

from __future__ import annotations

import argparse
from pathlib import Path

from tm_knowledge.authored import procedure
from tm_knowledge.explain import engine, matters, page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tmk-explain", description=__doc__)
    parser.add_argument("--matter", help="one fictional matter (FM-0001); default every one")
    parser.add_argument("--test", help="explain one legal test's requirements with no matter (GL-0001)")
    parser.add_argument("--process", help="walk through one process template with no matter (GP-0002)")
    parser.add_argument("--html", type=Path, help="write the prototype page here instead of printing text")
    parser.add_argument("--scenario", help="run one fictional amendment on its fictional matters (FS-0001), or 'all'")
    args = parser.parse_args(argv)
    if args.scenario:
        return _scenario(parser, args.scenario)
    tests = {k: v.record for k, v in procedure.load_tests().by_id().items()}
    processes = {k: v.record for k, v in procedure.load_processes().by_id().items()}
    if args.test or args.process:
        if args.test and args.test not in tests:
            parser.error(f"no sound legal test {args.test}")
        if args.process and args.process not in processes:
            parser.error(f"no sound process template {args.process}")
        if args.test:
            print(engine.render_requirements(engine.requirements(tests[args.test])))
        if args.process:
            print(engine.render_walkthrough(engine.walkthrough(processes[args.process], processes)))
        return 0
    found = matters.load()
    broken = [m for m in found if m.errors]
    for m in broken:
        print(f"{m.id}: " + "; ".join(m.errors))
    if broken:
        return 1
    chosen = [m for m in found if not args.matter or m.id == args.matter]
    if not chosen:
        parser.error(f"no fictional matter {args.matter}")
    explanations = [engine.explain(m, tests, processes[engine.EXAMINATION_PROCESS]) for m in chosen]
    if args.html:
        general = not args.matter
        requirements = [engine.requirements(t) for _, t in sorted(tests.items())] if general else []
        walkthroughs = [engine.walkthrough(p, processes) for p in processes.values()
                        if p["id"] != engine.EXAMINATION_PROCESS] if general else []
        args.html.write_text(page.render_page(explanations, requirements, walkthroughs), encoding="utf-8")
        print(f"wrote {args.html} ({len(explanations)} fictional matter(s), {len(requirements)} test(s), "
              f"{len(walkthroughs)} process(es)); not deployed, not for customers")
    else:
        print("\n".join(engine.render_text(e) for e in explanations))
    return 0


def _scenario(parser: argparse.ArgumentParser, wanted: str) -> int:
    """A normative scenario (A10): the records resting on the amended provision, how each
    fictional matter's reading would change, and the behavioural effect stated unknown.
    Printed only: a draft never reaches the graph, the index or the site."""
    from tm_knowledge.explain import scenarios
    from tm_knowledge.ontology import dependencies
    from tm_knowledge.upstream.loader import load_corpus

    corpus = load_corpus()
    found = scenarios.load(corpus=corpus)
    for s in found:
        if s.errors:
            print(f"{s.id}: " + "; ".join(s.errors))
    if any(s.errors for s in found):
        return 1
    chosen = [s for s in found if wanted == "all" or s.id == wanted]
    if not chosen:
        parser.error(f"no fictional amendment {wanted}")
    index = dependencies.build(corpus)
    print("\n".join(scenarios.render_text(scenarios.run(s, index=index)) for s in chosen))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

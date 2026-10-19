"""`tmk-explain` — explain a fictional matter, as text or as the prototype page."""

from __future__ import annotations

import argparse
from pathlib import Path

from tm_knowledge.authored import procedure
from tm_knowledge.explain import engine, matters, page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tmk-explain", description=__doc__)
    parser.add_argument("--matter", help="one fictional matter (FM-0001); default every one")
    parser.add_argument("--html", type=Path, help="write the prototype page here instead of printing text")
    args = parser.parse_args(argv)
    found = matters.load()
    broken = [m for m in found if m.errors]
    for m in broken:
        print(f"{m.id}: " + "; ".join(m.errors))
    if broken:
        return 1
    chosen = [m for m in found if not args.matter or m.id == args.matter]
    if not chosen:
        parser.error(f"no fictional matter {args.matter}")
    tests = {k: v.record for k, v in procedure.load_tests().by_id().items()}
    process = procedure.load_processes().sound[0].record
    explanations = [engine.explain(m, tests, process) for m in chosen]
    if args.html:
        args.html.write_text(page.render_page(explanations), encoding="utf-8")
        print(f"wrote {args.html} ({len(explanations)} fictional matter(s)); not deployed, not for customers")
    else:
        print("\n".join(engine.render_text(e) for e in explanations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

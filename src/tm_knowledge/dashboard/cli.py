"""Command line entry points for the dashboard.

Two commands, matching the two directions the dashboard moves information.
`tmk-dashboard` writes the site's data out of the repo; `tmk-ruling` reads an
answer back in. Neither repairs anything, and both exit non-zero rather than
producing something half-right.

Exit codes follow the harness (ADR-0030): 0 clean, 1 something is wrong.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.dashboard import build as build_module
from tm_knowledge.dashboard import questions as questions_module
from tm_knowledge.dashboard import ruling as ruling_module

__all__ = ["dashboard", "ruling"]


def dashboard(argv: list[str] | None = None) -> int:
    """`tmk-dashboard` — generate `site/data/`, or check it has not gone stale."""
    parser = argparse.ArgumentParser(
        prog="tmk-dashboard",
        description="Generate the dashboard's data from the committed artefacts.",
    )
    parser.add_argument("--write", action="store_true", help="write into site/data/")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if what is committed differs from a regeneration",
    )
    parser.add_argument("--out", type=Path, default=None, help="output directory")
    parser.add_argument(
        "--generated",
        default=None,
        help="the build stamp (default: today). Set it for a reproducible build.",
    )
    args = parser.parse_args(argv)

    if args.check:
        stale = build_module.check(args.out)
        if stale:
            print("The committed dashboard data no longer matches the repository:")
            for line in stale:
                print(f"  {line}")
            print(
                "\nRun `tmk-dashboard --write` and commit the result. The site reads only what "
                "is committed, so a stale file is a number on a public page that the repository "
                "no longer holds."
            )
            return 1
        print("Dashboard data is current.")
        return 0

    pages = build_module.build(generated=args.generated)
    question_set = questions_module.load()
    print(f"{len(pages)} pages")
    for name, payload in pages.items():
        size = len(json.dumps(payload, ensure_ascii=False))
        print(f"  {name:<18} {size:>8,} bytes")
    print(
        f"\n{len(question_set.asked)} questions waiting on the owner, "
        f"{len(question_set.by_status('parked'))} parked for an expert, "
        f"{len(questions_module.load_rulings())} rulings recorded"
    )

    if args.write:
        written = build_module.write(pages, args.out)
        root = (args.out or build_module.DATA_DIR).parents[1]
        print()
        for path in written:
            print(f"wrote {path.relative_to(root)}")
    else:
        print("\n(dry run — nothing written. Pass --write.)")
    return 0


def ruling(argv: list[str] | None = None) -> int:
    """`tmk-ruling` — transcribe a submitted decision into `review/rulings/`."""
    parser = argparse.ArgumentParser(
        prog="tmk-ruling",
        description="Transcribe a dashboard submission from a GitHub issue body.",
    )
    parser.add_argument(
        "--body",
        type=Path,
        default=None,
        help="file holding the issue body (default: read stdin)",
    )
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--issue-url", required=True)
    parser.add_argument("--author", required=True, help="the GitHub login that submitted it")
    parser.add_argument("--title", default="")
    parser.add_argument("--write", action="store_true", help="write into review/rulings/")
    parser.add_argument("--out", type=Path, default=None, help="output directory")
    args = parser.parse_args(argv)

    body = args.body.read_text(encoding="utf-8") if args.body else sys.stdin.read()

    try:
        payload = ruling_module.parse(body)
        document = ruling_module.transcribe(
            payload,
            issue={
                "number": args.issue_number,
                "url": args.issue_url,
                "author": args.author,
                "title": args.title or None,
            },
        )
    except (ruling_module.MalformedSubmission, questions_module.MalformedQuestions) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1

    print(f"{len(document['answers'])} answers from @{args.author} on issue #{args.issue_number}")
    for answer in document["answers"]:
        print(f"  {answer['id']}  {answer['label']}")
        if answer.get("notes"):
            print(f"            note: {answer['notes']}")

    if args.write:
        path = ruling_module.write(document, args.out)
        try:
            shown = path.relative_to(REPO_ROOT)
        except ValueError:
            shown = path
        print(f"\nwrote {shown}")
    else:
        print("\n(dry run — nothing written. Pass --write.)")
    return 0

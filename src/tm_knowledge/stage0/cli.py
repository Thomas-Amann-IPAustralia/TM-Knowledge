"""Commands: `tmk-recon` and `tmk-worksheet`.

Both write into `data/derived/`, which is git-ignored and always rebuildable —
they are derivations of the pinned snapshot, so committing one would be
committing a second copy of the corpus with a stale date on it. Pass `--out` to
put a copy somewhere a person will read it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import recon as recon_module
from tm_knowledge.stage0 import worksheet as worksheet_module
from tm_knowledge.stage0.worksheet import PILOT_PROVISION, ScopeRule
from tm_knowledge.upstream.loader import load_corpus
from tm_knowledge.upstream.pin import SnapshotMismatch, UnpinnedSnapshot

DERIVED = REPO_ROOT / "data" / "derived"


def _write(text: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def recon(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-recon",
        description=(
            "Derived counts about a candidate pilot area. Not a scope proposal — "
            "the report says so on its face, and means it."
        ),
    )
    parser.add_argument("--provision", default=PILOT_PROVISION)
    parser.add_argument("--out", type=Path, default=DERIVED / "reports" / "recon.md")
    args = parser.parse_args(argv)

    try:
        corpus = load_corpus()
    except (UnpinnedSnapshot, SnapshotMismatch) as error:
        print(f"refusing to run: {error}", file=sys.stderr)
        return 2

    report = recon_module.reconnoitre(corpus, args.provision)
    path = _write(recon_module.render(report, corpus), args.out)
    print(
        f"{args.provision}: {len(report.citing_chunks)} citing chunks on "
        f"{len(report.pages)} pages; {len(report.with_page_mates)} chunks with "
        f"page-mates; {len(report.cases_cited)} cases cited; "
        f"{len(report.unresolved_in_scope)} unresolved refs; "
        f"{len(report.ambiguous_in_scope)} ambiguous edges"
    )
    print(f"wrote {path}")
    return 0


def worksheet(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-worksheet",
        description="The Pass B annotation worksheet (ADR-0022's provisional rule).",
    )
    parser.add_argument("--provision", default=PILOT_PROVISION)
    parser.add_argument(
        "--no-page-mates",
        action="store_true",
        help="print only the citing chunks. Narrower than ADR-0022's rule — use "
        "for comparison, not for the worksheet the expert annotates.",
    )
    parser.add_argument("--out", type=Path, default=DERIVED / "worksheet.md")
    args = parser.parse_args(argv)

    try:
        corpus = load_corpus()
    except (UnpinnedSnapshot, SnapshotMismatch) as error:
        print(f"refusing to run: {error}", file=sys.stderr)
        return 2

    rule = ScopeRule(provision=args.provision, include_page_mates=not args.no_page_mates)
    selected = worksheet_module.select(corpus, rule)
    path = _write(worksheet_module.render(corpus, rule), args.out)
    print(f"{len(selected)} chunks selected by ADR-0022's rule for {args.provision}")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(recon())

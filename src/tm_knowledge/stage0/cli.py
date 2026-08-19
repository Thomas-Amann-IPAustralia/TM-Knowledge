"""Commands: `tmk-recon`, `tmk-worksheet`, `tmk-harness` and `tmk-coverage`.

All four write into `data/derived/`, which is git-ignored and always rebuildable
— they are derivations of the pinned snapshot and of `eval/gold/`, so committing
one would be committing a second copy with a stale date on it. Pass `--out` to
put a copy somewhere a person will read it.

`tmk-harness` is the one with an opinion about its exit code. Three outcomes,
because two of them mean opposite things (ADR-0018):

| code | meaning | what to do |
|---|---|---|
| 0 | sound and Stage 0 complete | nothing |
| 1 | **defects** — something that arrived is wrong | fix it; this breaks a build |
| 3 | sound, Stage 0 incomplete | nothing yet; this is the expected state |

CI passes `--allow-incomplete`, which maps 3 to 0 while still printing every
gap. That is the whole of ADR-0018's separation, in one flag: a permanently red
pipeline trains everyone to ignore it, and the failure that matters is 1.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import coverage as coverage_module
from tm_knowledge.stage0 import harness as harness_module
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


def _run_harness(
    argv: list[str] | None, prog: str, description: str, *, gate_flag: bool
):
    """Shared argument parsing for the two commands that read `eval/gold/`."""
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        "--gold-dir",
        type=Path,
        default=None,
        help="the gold set to check. Defaults to eval/gold/.",
    )
    parser.add_argument(
        "--no-resolution",
        action="store_true",
        help="skip the checks that need the pinned snapshot. The report then says "
        "so, and never reports Stage 0 complete.",
    )
    if gate_flag:
        parser.add_argument(
            "--allow-incomplete",
            action="store_true",
            help="exit 0 when the only findings are gaps. For CI: Stage 0 "
            "incompleteness is a reported state, not a broken build (ADR-0018).",
        )
    else:
        parser.add_argument(
            "--out", type=Path, default=DERIVED / "reports" / "coverage.md"
        )
    args = parser.parse_args(argv)
    report = harness_module.run(
        gold_dir=args.gold_dir, with_resolution=not args.no_resolution
    )
    return args, report


def harness(argv: list[str] | None = None) -> int:
    args, report = _run_harness(
        argv,
        "tmk-harness",
        "The Stage 0 evaluation harness. Prints every defect and every gap, and "
        "distinguishes them: a defect is something that arrived wrong, a gap is "
        "something that has not arrived yet.",
        gate_flag=True,
    )

    for severity, heading in (
        (harness_module.Severity.DEFECT, "DEFECTS — something that arrived is wrong"),
        (harness_module.Severity.GAP, "GAPS — Stage 0 is waiting on these"),
        (harness_module.Severity.NOTE, "NOTES — worth an eye, gating nothing"),
    ):
        findings = report.of(severity)
        if not findings:
            continue
        print(f"\n{heading} ({len(findings)})")
        for finding in findings:
            print(f"  {finding.check}: {finding.subject} — {finding.message}")

    print(f"\n{report.summary()}")
    code = report.exit_code
    if code == 3 and args.allow_incomplete:
        print(
            "Stage 0 is incomplete and nothing is malformed. Reported, not failed "
            "(--allow-incomplete, ADR-0018)."
        )
        return 0
    return code


def coverage(argv: list[str] | None = None) -> int:
    args, report = _run_harness(
        argv,
        "tmk-coverage",
        "The Stage 0 coverage and gap report. Reports gaps; never fills them.",
        gate_flag=False,
    )
    path = _write(coverage_module.render(report), args.out)
    print(report.summary())
    print(f"wrote {path}")
    return 1 if report.defects else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(recon())

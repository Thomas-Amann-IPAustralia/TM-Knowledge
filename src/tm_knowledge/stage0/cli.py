"""Commands: `tmk-recon`, `tmk-worksheet`, `tmk-harness`, `tmk-coverage`,
`tmk-blockers`, `tmk-workbook`, `tmk-transcribe` and `tmk-seed`.

They write into `data/derived/`, which is tracked and committed (ADR-0042,
supersedes ADR-0028) — they are derivations of the pinned snapshot and of
`eval/gold/`, and committing each regeneration is the paper trail: the diff
shows what moved and when. Pass `--out` to put a copy somewhere else instead.

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

`tmk-transcribe` is the other one to read before running: it writes into
`eval/gold/`, which is approved space, so it does a dry run unless given
`--write`.

`tmk-seed` runs the other way round: it checks the machine-written example
records in `review/seed/`, resolves their spans against the snapshot, and
renders them as a review pack and a review workbook for an expert to correct
(ADR-0043). It never writes into `eval/gold/` — the corrected workbook goes
back through `tmk-transcribe`, which is the only door into approved space.

`tmk-blockers` is the pair to `tmk-coverage`. Coverage says what Stage 0 is
missing; this says which decision on the review queue releases the most, because
approval does not distribute over an interlinked set and the queue is therefore
not a list (ADR-0048, ADR-0053). The two compose:

```
tmk-blockers                                   # the worklist
tmk-seed --only "$(tmk-blockers --ids)" \
         --pack data/derived/blockers-review-pack.md \
         --workbook data/derived/stage0-blockers-review.xlsx
```
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
    """`tmk-recon` — derived counts about the corpus, or about one provision in it.

    **The default changed at ADR-0096.** It used to cost section 43 so that a
    boundary could be drawn against numbers; the owner withdrew the boundary, so
    it costs the corpus and `--provision` asks the old question.
    """
    parser = argparse.ArgumentParser(
        prog="tmk-recon",
        description=(
            "Derived counts about the corpus. Not a scope proposal — the report says "
            "so on its face, and means it. Pass --provision to cost one area instead."
        ),
    )
    parser.add_argument(
        "--provision",
        default=None,
        help=(
            "cost this provision alone, the way this command did before the section 43 "
            f"boundary was withdrawn (e.g. {PILOT_PROVISION}). Without it, the whole "
            "corpus is costed"
        ),
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--generated", default=None, help="build stamp, for a reproducible run")
    args = parser.parse_args(argv)

    try:
        corpus = load_corpus()
    except (UnpinnedSnapshot, SnapshotMismatch) as error:
        print(f"refusing to run: {error}", file=sys.stderr)
        return 2

    if args.provision is None:
        found = recon_module.survey(corpus)
        path = _write(
            recon_module.render_survey(found, corpus, generated=args.generated),
            args.out or DERIVED / "reports" / "recon.md",
        )
        print(
            f"{found.total_chunks:,} chunks · {len(found.areas)} provisions cited by at "
            f"least 3 of them · {found.uncited_chunks:,} chunks "
            f"({found.uncited_chunks / found.total_chunks:.0%}) cite no provision at all"
        )
        for area in found.areas[:8]:
            print(f"  {area.provision:<18} {area.chunks:>5} chunks   {area.title[:48]}")
        print(f"wrote {path}")
        return 0

    report = recon_module.reconnoitre(corpus, args.provision)
    path = _write(
        recon_module.render(report, corpus, generated=args.generated),
        args.out or DERIVED / "reports" / f"recon-{args.provision.replace('/', '-')}.md",
    )
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
    """Shared argument parsing for the two commands that read the two stores."""
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        "--gold-dir",
        type=Path,
        default=None,
        help="the gold set to check. Defaults to eval/gold/.",
    )
    parser.add_argument(
        "--authored-dir",
        type=Path,
        default=None,
        help="the authored store to check. Defaults to authored/. Checked "
        "alongside the gold set and never added to it (ADR-0080).",
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
        gold_dir=args.gold_dir,
        authored_dir=args.authored_dir,
        with_resolution=not args.no_resolution,
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
    print(report.stores())
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
    print(report.stores())
    print(f"wrote {path}")
    return 1 if report.defects else 0


def blockers(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-blockers",
        description=(
            "Why each remaining seed record is not in eval/gold/, and what each "
            "one releases if it is settled. Reads the ledgers, the seed set and "
            "the gold set; writes nothing but the report."
        ),
    )
    parser.add_argument("--out", type=Path, default=DERIVED / "reports" / "blockers.md")
    parser.add_argument("--seed-dir", type=Path, default=None)
    parser.add_argument("--gold-dir", type=Path, default=None)
    parser.add_argument("--decisions-dir", type=Path, default=None)
    parser.add_argument(
        "--ids",
        action="store_true",
        help="print only the record ids on the critical path, comma-separated, "
        "and write nothing. Feed them to `tmk-seed --only` to render a review "
        "round scoped to exactly those records.",
    )
    args = parser.parse_args(argv)

    from tm_knowledge.stage0 import blockers as blockers_module
    from tm_knowledge.stage0 import goldset as goldset_module
    from tm_knowledge.stage0 import seed as seed_module

    analysis = blockers_module.analyse(
        seed=seed_module.load(args.seed_dir),
        gold=goldset_module.load(args.gold_dir),
        decisions_dir=args.decisions_dir,
    )

    if args.ids:
        print(",".join(blockers_module.identifiers(analysis)))
        return 0

    if not analysis.total:
        print("review/seed/ is empty — nothing is holding the gold set")
        return 0

    print(
        f"{analysis.total} record(s) still in review/seed/; "
        f"{len(analysis.ranked)} of them hold at least one other; "
        f"{len(analysis.actionable)} decision(s) on the critical path"
    )
    for entry in analysis.actionable:
        held = analysis.holds.get(entry.record_id, ())
        releases = f"releases {len(held)}" if held else "releases nothing further"
        print(f"  {entry.record_id}: {entry.reason} — {releases}")
    if analysis.unparseable_marks:
        print(
            f"\n{len(analysis.unparseable_marks)} verdict cell(s) nothing can read — "
            "a person must rule on them by name (ADR-0051)"
        )
    if analysis.unknown_targets:
        print(
            f"\nDEFECT: {len(analysis.unknown_targets)} pointer(s) name an id that "
            "is neither approved nor waiting"
        )

    path = _write(blockers_module.render(analysis), args.out)
    print(f"\nwrote {path}")
    return 1 if analysis.unknown_targets else 0


def workbook(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-workbook",
        description=(
            "Generate the Stage 0 intake workbook from eval/schemas/. One sheet per "
            "record type, enum cells as dropdowns, and no example rows."
        ),
    )
    parser.add_argument("--out", type=Path, default=DERIVED / "stage0-intake.xlsx")
    args = parser.parse_args(argv)

    from tm_knowledge.stage0 import workbook as workbook_module

    args.out.parent.mkdir(parents=True, exist_ok=True)
    path = workbook_module.write(args.out)
    sheets = workbook_module.sheets()
    print(
        f"{len([s for s in sheets if not s.is_child])} record sheets and "
        f"{len([s for s in sheets if s.is_child])} continuation sheets"
    )
    print(f"wrote {path}")
    return 0


def transcribe(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-transcribe",
        description=(
            "Read a filled intake workbook into eval/gold/. Reshapes; never "
            "supplies. Dry run unless --write is given."
        ),
    )
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--gold-dir", type=Path, default=None)
    parser.add_argument(
        "--addendum",
        type=Path,
        default=None,
        help="an instruction file from review/returned/ that stands in for "
        "keystrokes the reviewer settled after handing the workbook back "
        "(ADR-0051). Every row it touches is reported.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="actually write into eval/gold/. Without it, nothing is written and "
        "the command reports what would change.",
    )
    args = parser.parse_args(argv)

    from tm_knowledge.stage0 import transcribe as transcribe_module

    addendum = None
    if args.addendum is not None:
        try:
            addendum = transcribe_module.read_addendum(args.addendum)
        except transcribe_module.MalformedAddendum as error:
            print(f"refusing to read: {error}", file=sys.stderr)
            return 2

    try:
        result = transcribe_module.read_workbook(args.workbook, addendum)
    except transcribe_module.WorkbookMismatch as error:
        print(f"refusing to read: {error}", file=sys.stderr)
        return 2

    if result.instructed:
        print(
            f"\nBY INSTRUCTION ({len(result.instructed)}) — {args.addendum}, "
            f"recorded {addendum.recorded_on}"
        )
        for identifier, what in result.instructed:
            print(f"  {identifier}: {what}")

    if result.problems:
        print(f"\nREJECTED ROWS ({len(result.problems)}) — not written, and not guessed at")
        for problem in result.problems:
            print(f"  {problem}")

    from tm_knowledge.stage0 import goldset

    gold_dir = args.gold_dir or goldset.GOLD_DIR
    if result.reviewed:
        # What is already approved and not being rewritten by this run. Without
        # it, a second review round would hold every record pointing at one the
        # first round approved.
        existing = goldset.load(gold_dir)
        transcribe_module.close_over_cross_references(
            result,
            frozenset(
                str(record["id"])
                for record_type, record in existing.all_records()
                if record.get("id") and record_type not in result.records
            ),
        )

    if result.held:
        grouped = result.held_by_reason()
        print(
            f"\nHELD ({len(result.held)}) — read, understood, and kept out of "
            "eval/gold/"
        )
        for reason in sorted(grouped, key=lambda r: (-len(grouped[r]), r)):
            entries = grouped[reason]
            print(f"  {reason} — {len(entries)}")
            print("    " + ", ".join(sorted(entry.identifier for entry in entries)))
            for entry in entries:
                if entry.detail:
                    print(f"      {entry.identifier}: {entry.detail}")

    if result.dropped:
        print(
            f"\nDROPPED ENTRIES ({len(result.dropped)}) — a reviewer rejected the "
            "entry, so it is not in its parent's list"
        )
        for record_type, parent_id, where in result.dropped:
            print(f"  {parent_id} ({record_type}): {where}")

    if result.blanks:
        print(f"\nBLANK JUDGEMENT FIELDS ({len(result.blanks)}) — reported, never filled")
        for record_type, identifier, name in result.blanks:
            print(f"  {identifier} ({record_type}): {name}")

    if result.empty_sheets:
        print(
            "\nEMPTY SHEETS — left untouched: "
            + ", ".join(sorted(result.empty_sheets))
        )

    print(f"\n{result.summary()}")
    for path, outcome in transcribe_module.write_records(
        result, gold_dir, write=args.write
    ):
        print(f"  {outcome}: {path}")
    if not args.write and result.records:
        print("\nDry run. Re-run with --write to put these into eval/gold/.")
    if args.write and result.reviewed and result.records:
        print(
            "\nA record now exists in both eval/gold/ and review/seed/. Run "
            "`tmk-reconcile` to record the round's verdicts and retire the seed "
            "copies — two versions of one record is the state ADR-0043 forbids."
        )
    return 1 if result.problems else 0


def reconcile(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-reconcile",
        description=(
            "Record a review round in review/decisions/ and retire the seed "
            "copies of whatever reached eval/gold/. Run it after "
            "`tmk-transcribe --write`. Dry run unless --write is given."
        ),
    )
    parser.add_argument("workbook", type=Path)
    parser.add_argument(
        "--decisions-dir",
        type=Path,
        default=None,
        help="where the ledger goes (default: review/decisions/)",
    )
    parser.add_argument(
        "--addendum",
        type=Path,
        default=None,
        help="the same instruction file passed to `tmk-transcribe`, so the "
        "ledger describes the run that produced eval/gold/ rather than a "
        "second reading of the workbook.",
    )
    parser.add_argument(
        "--as-of",
        default=None,
        help="the date to stamp the ledger with (default: today). Given so a "
        "re-run produces the same file rather than a dated near-duplicate.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="actually write the ledger and prune review/seed/.",
    )
    args = parser.parse_args(argv)

    from tm_knowledge.stage0 import reconcile as reconcile_module
    from tm_knowledge.stage0 import transcribe as transcribe_module

    addendum = None
    if args.addendum is not None:
        try:
            addendum = transcribe_module.read_addendum(args.addendum)
        except transcribe_module.MalformedAddendum as error:
            print(f"refusing to read: {error}", file=sys.stderr)
            return 2

    round_ = reconcile_module.read_round(args.workbook, addendum=addendum)
    print(
        f"{round_.reviewed} of {len(round_.outcomes)} records carry a verdict; "
        + ", ".join(
            f"{len(round_.of(state))} {state}"
            for state in ("approved", "held", "rejected", "unparseable")
        )
    )
    if round_.of("unparseable"):
        print("\nUNREADABLE VERDICTS — nothing was inferred from these")
        for outcome in round_.of("unparseable"):
            print(f"  {outcome.identifier}: {outcome.note}")

    markdown, data = reconcile_module.write_ledger(
        round_, args.decisions_dir, as_of=args.as_of, write=args.write
    )
    print(f"\n{'wrote' if args.write else 'would write'} {markdown}")
    print(f"{'wrote' if args.write else 'would write'} {data}")

    try:
        pruned = reconcile_module.prune(write=args.write)
    except reconcile_module.ReconcileRefused as error:
        print(f"\nrefusing to prune: {error}", file=sys.stderr)
        return 1

    changed = [entry for entry in pruned if entry.outcome != "unchanged"]
    if changed:
        print("\nreview/seed/ — retiring the records that are now approved")
        for entry in changed:
            print(
                f"  {entry.outcome}: {entry.path.name} "
                f"(-{len(entry.retired)}, {entry.remaining} left)"
            )
    else:
        print("\nreview/seed/ — nothing to retire")

    if not args.write:
        print("\nDry run. Re-run with --write to record the round.")
    return 0


def seed(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-seed",
        description=(
            "Check the seed example set in review/seed/ and render it for expert "
            "correction. Nothing here is approved; nothing here is written into "
            "eval/gold/."
        ),
    )
    parser.add_argument(
        "--pack",
        type=Path,
        nargs="?",
        const=DERIVED / "seed-review-pack.md",
        default=None,
        help="render the readable review pack (default: "
        "data/derived/seed-review-pack.md)",
    )
    parser.add_argument(
        "--workbook",
        type=Path,
        nargs="?",
        const=DERIVED / "stage0-seed-review.xlsx",
        default=None,
        help="render the pre-filled review workbook (default: "
        "data/derived/stage0-seed-review.xlsx). Never the intake workbook — that "
        "one stays empty on purpose.",
    )
    parser.add_argument("--seed-dir", type=Path, default=None)
    parser.add_argument(
        "--only",
        default=None,
        metavar="ID,ID,…",
        help="render the pack and the workbook over just these records — record "
        "ids (CQ-0013) or seed ids (SEED-CQ-0013). Use it to put a short, "
        "targeted round in front of a reviewer: `tmk-blockers --ids` prints the "
        "records on the critical path in exactly this form. The checks still run "
        "over the whole seed set, because a subset cannot tell you the set is "
        "sound.",
    )
    args = parser.parse_args(argv)

    from tm_knowledge.stage0 import seed as seed_module
    from tm_knowledge.stage0 import seedpack

    seed_set = seed_module.load(args.seed_dir)
    if not seed_set.envelopes and not seed_set.unreadable:
        print(f"no seed records under {seed_set.root}")
        return 0

    corpus = None
    try:
        corpus = load_corpus()
    except (UnpinnedSnapshot, SnapshotMismatch, FileNotFoundError) as error:
        print(f"snapshot not open: {error}", file=sys.stderr)
        print("spans and refs are unchecked. Run tmk-fetch-upstream.", file=sys.stderr)

    findings = seed_module.check(seed_set, corpus) + seed_module.coverage(seed_set)
    resolutions: tuple = ()
    if corpus is not None:
        resolutions, _ = seed_module.resolve(seed_set, corpus)

    for severity in (
        harness_module.Severity.DEFECT,
        harness_module.Severity.GAP,
        harness_module.Severity.NOTE,
    ):
        selected = [f for f in findings if f.severity is severity]
        if not selected:
            continue
        print(f"\n{severity.value.upper()}S ({len(selected)})")
        for finding in selected:
            print(f"  {finding.check}: {finding.subject} — {finding.message}")

    counts = ", ".join(
        f"{seed_set.count(record_type)} {label}"
        for record_type, (label, _) in seedpack.PACK_HEADINGS.items()
        if seed_set.count(record_type)
    )
    print(f"\n{seed_set.total} seed records — {counts}")

    defects = [f for f in findings if f.severity is harness_module.Severity.DEFECT]

    # The narrowing happens here and nowhere earlier: `check` and `coverage` ran
    # over the whole of `review/seed/` above, because a subset cannot tell you
    # whether the set is sound, and a round scoped to six records must not also
    # quietly scope the defect report to six records.
    rendering, missing, scoped = seed_set, (), None
    if args.only is not None:
        rendering, missing = seed_set.subset(args.only.split(","))
        if missing:
            print(
                f"\nno such record in {seed_set.root}: {', '.join(missing)}",
                file=sys.stderr,
            )
            return 2
        wanted = {e.seed_id for e in rendering.envelopes}
        resolutions = tuple(
            r for r in resolutions if r.envelope.seed_id in wanted
        )
        scoped = seed_set.total
        print(f"rendering {rendering.total} of {seed_set.total} records")

    if args.pack is not None:
        if corpus is None:
            print("cannot render the pack without the snapshot", file=sys.stderr)
            return 2
        path = _write(
            seedpack.render_pack(rendering, resolutions, corpus, subset_of=scoped),
            args.pack,
        )
        print(f"wrote {path}")
    if args.workbook is not None:
        if corpus is None:
            print("cannot render the workbook without the snapshot", file=sys.stderr)
            return 2
        path = seedpack.write_workbook(
            args.workbook, rendering, resolutions, corpus, subset_of=scoped
        )
        print(f"wrote {path}")

    return 1 if defects else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(recon())


def typing(argv: list[str] | None = None) -> int:
    """`tmk-typing` — the concept typing pass, for one person to sort."""
    parser = argparse.ArgumentParser(
        prog="tmk-typing",
        description=(
            "Lay out every concept the repository holds — signed and authored — for "
            "sorting into the four groups. Supplies the shape, the evidence and a "
            "proposal; never a person's signature."
        ),
    )
    parser.add_argument("--write", action="store_true", help="write the workbook and the report")
    parser.add_argument("--out", type=Path, default=None, help="workbook path")
    parser.add_argument("--generated", default=None, help="build stamp, for a reproducible run")
    args = parser.parse_args(argv)

    from tm_knowledge.stage0 import typing as typing_module

    from tm_knowledge.authored import store as authored_store
    from tm_knowledge.stage0 import goldset

    gold = goldset.load()
    authored = authored_store.load()
    prepared = typing_module.rows(gold, authored)
    typed = [row for row in prepared if row.get("type")]
    signed_off = [row for row in typed if row.get("approved_by")]
    print(
        f"{len(prepared)} concepts on the sheet — {len(gold['gold_concept'])} signed by "
        f"an expert, {len(prepared) - len(gold['gold_concept'])} authored by a machine "
        "(never summed elsewhere, ADR-0080 c3)"
    )
    print(
        f"{len(typed)} carry a proposed group, {len(signed_off)} carry a person's name, "
        f"{len(prepared) - len(typed)} are blank"
    )
    for value, meaning in typing_module.GROUPS:
        count = sum(1 for row in typed if row.get("type") == value)
        print(f"  {value:<18} {count:>3}   {meaning}")

    if not args.write:
        print("\n(dry run — nothing written. Pass --write.)")
        return 0

    book = typing_module.write_workbook(args.out, generated=args.generated)
    report = typing_module.write_report(generated=args.generated)
    print(f"\nwrote {book}")
    print(f"wrote {report}")
    print(
        "\nFill the `type` column, sign the row, and hand the file back. "
        "`tmk-transcribe <file> --write` reads it into eval/gold/concept-types.yaml."
    )
    return 0


def concepts(argv: list[str] | None = None) -> int:
    """`tmk-concepts` — concept candidates across the whole Manual.

    The pass the section 43 boundary used to make unnecessary. It finds
    candidates and authors nothing: turning one into a concept is a judgement
    with an envelope, and it happens in `authored/concepts.yaml`.
    """
    parser = argparse.ArgumentParser(
        prog="tmk-concepts",
        description=(
            "Deterministic concept candidates from the whole corpus — statutory "
            "defined terms, Manual definitions, Manual subject headings. Reports "
            "what the corpus offers; never decides what a concept is."
        ),
    )
    parser.add_argument("--write", action="store_true", help="write the candidates and the pack")
    parser.add_argument("--out", type=Path, default=None, help="candidates YAML path")
    parser.add_argument(
        "--report", type=Path, default=None, help="candidate pack path"
    )
    parser.add_argument("--generated", default=None, help="build stamp, for a reproducible run")
    args = parser.parse_args(argv)

    try:
        corpus = load_corpus()
    except (UnpinnedSnapshot, SnapshotMismatch) as error:
        print(f"refusing to run: {error}", file=sys.stderr)
        return 2

    from tm_knowledge.authored import store as authored_store
    from tm_knowledge.stage0 import concepts as concepts_module
    from tm_knowledge.stage0 import goldset

    gold = goldset.load()
    authored = authored_store.load()
    known = [*gold["gold_concept"], *authored["gold_concept"]]
    candidates = concepts_module.extract(corpus, known=known)

    by_strength = {3: 0, 2: 0, 1: 0}
    for candidate in candidates:
        by_strength[candidate.strength] += 1
    covered = sum(1 for candidate in candidates if candidate.covered_by)

    print(f"{len(candidates)} concept candidates from {len(corpus.chunks)} chunks")
    print(f"  strength 3 (legislation and Manual both define it) : {by_strength[3]:>4}")
    print(f"  strength 2 (one of the two defines it)             : {by_strength[2]:>4}")
    print(f"  strength 1 (a Manual heading names it, nothing defines it): {by_strength[1]:>4}")
    print(f"  already claimed by a concept we hold               : {covered:>4}")
    print(f"  concepts held today: {len(gold['gold_concept'])} signed, "
          f"{len(authored['gold_concept'])} authored")

    if not args.write:
        print("\n(dry run — nothing written. Pass --write.)")
        return 0

    written = concepts_module.write_candidates(
        candidates, args.out, generated=args.generated
    )
    report = concepts_module.write_report(
        candidates, args.report, corpus=corpus, generated=args.generated
    )
    print(f"\nwrote {written}")
    print(f"wrote {report}")
    print(
        "\nCandidates are not concepts. Authoring one is a judgement and carries an "
        "envelope — `authored/concepts.yaml`, never `eval/gold/`."
    )
    return 0

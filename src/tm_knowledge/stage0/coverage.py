"""The Stage 0 coverage and gap report (parallel track P10).

The harness decides what is wrong and what is missing; this renders it as a
worklist. The point is not the prose — it is that **an hour of expert time
visibly moves a number**. Four concepts written on a Tuesday should show up as
`4 of 50–100` rather than disappearing into a directory, because the guide's
advice to the owner is to work in whatever hour they have, and advice like that
only survives if the increment is visible.

**It reports gaps; it never fills them** (guide §9). Every line here says what is
absent and who owns it. Nothing in this module may propose a value for a
judgement field, not even as a suggestion — a plausible draft anchors the
reviewer and gets copied forward (CLAUDE.md rule 1).
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.harness import (
    DELIVERABLES,
    Deliverable,
    Finding,
    Report,
    band,
)
from tm_knowledge.stage0.schemas import enum_values

#: The order gaps are printed in, and a heading for each. Completeness first
#: because it is the one an expert acts on; resolution last because it is the
#: one an agent acts on.
GAP_SECTIONS: tuple[tuple[str, str], ...] = (
    ("completeness", "Deliverables not yet delivered"),
    ("coverage", "Coverage the definition of done requires"),
    ("judgement", "Judgement fields left empty — only an expert may close these"),
    ("approval", "Records transcribed but not approved"),
    ("resolution", "Checks that could not run"),
)


def _status(deliverable: Deliverable, report: Report) -> tuple[str, str]:
    """(have, status) for one deliverable row."""
    if deliverable.kind == "document":
        missing = any(
            finding.subject == deliverable.path and finding.check == "completeness"
            for finding in report.gaps
        )
        return ("—", "not written" if missing else "written")

    count = report.gold.count(deliverable.record_type)
    if deliverable.minimum is not None and count < deliverable.minimum:
        return (str(count), f"{deliverable.minimum - count} short")
    if deliverable.maximum is not None and count > deliverable.maximum:
        return (str(count), f"{count - deliverable.maximum} above the band")
    return (str(count), "in band")


def _enum_table(report: Report, record_type: str, field: str) -> str:
    values = [value for value in enum_values(record_type, field) if value is not None]
    counts = Counter(
        record.get(field) for record in report.gold[record_type]
    )
    lines = [f"| `{field}` | records |", "|---|---|"]
    for value in values:
        lines.append(f"| {value} | {counts.get(value, 0)} |")
    return "\n".join(lines)


def _group(findings: tuple[Finding, ...], check: str) -> tuple[Finding, ...]:
    return tuple(finding for finding in findings if finding.check == check)


def render(report: Report, *, generated: str | None = None) -> str:
    """The report, as Markdown."""
    stamp = generated or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    against = (
        f"the pinned snapshot `{report.pin_commit[:12]}`"
        if report.pin_commit
        else "**no snapshot**"
    )

    out: list[str] = []
    out.append("# Stage 0 — coverage and gaps")
    out.append("")
    out.append(
        f"**Generated** {stamp} · **Source** `eval/gold/` against {against} · "
        "**Regenerate** `tmk-coverage`"
    )
    out.append("")
    out.append(
        "This report is **derived**. It counts what `eval/gold/` holds against the "
        "definition of done in `eval/STAGE-0-INPUT-GUIDE.md` §7, and it names what "
        "is absent. It does not propose content for any gap, and it must not be "
        "read as doing so: every field it reports as empty is one only a domain "
        "expert may fill (CLAUDE.md rule 1, guide §9)."
    )
    out.append("")
    out.append(f"**Status:** {report.summary()}.")
    if not report.resolution_ran:
        out.append("")
        out.append(
            f"> The resolution checks did not run — {report.resolution_skipped}. "
            "Every ref, span and hash below is therefore unverified."
        )
    out.append("")

    # -- the board ----------------------------------------------------------
    out.append("## 1. The board")
    out.append("")
    out.append("| Deliverable | Target | Have | Status |")
    out.append("|---|---|---|---|")
    for deliverable in DELIVERABLES:
        have, status = _status(deliverable, report)
        target = deliverable.path if deliverable.kind == "document" else band(deliverable)
        out.append(f"| {deliverable.label} | {target} | {have} | {status} |")
    out.append("")

    # -- defects ------------------------------------------------------------
    out.append("## 2. Defects")
    out.append("")
    if report.defects:
        out.append(
            f"**{len(report.defects)} defect(s).** These are not gaps. Something that "
            "arrived is wrong, and each one breaks the build (ADR-0018)."
        )
        out.append("")
        for finding in report.defects:
            out.append(f"- **{finding.subject}** ({finding.check}) — {finding.message}")
    else:
        out.append("None. Everything in `eval/gold/` is well formed and lands where it says.")
    out.append("")

    # -- gaps ---------------------------------------------------------------
    out.append("## 3. Gaps")
    out.append("")
    if not report.gaps:
        out.append("None. Stage 0 is complete against §7's mechanical checklist.")
        out.append("")
    for check, heading in GAP_SECTIONS:
        group = _group(report.gaps, check)
        if not group:
            continue
        out.append(f"### {heading}")
        out.append("")
        for finding in group:
            out.append(f"- **{finding.subject}** — {finding.message}")
        out.append("")

    # -- enum coverage ------------------------------------------------------
    out.append("## 4. Coverage by category")
    out.append("")
    out.append(
        "Both lists are read from the schemas, not restated here. §7 requires the "
        "set as a whole to span each of them; which value a given record carries is "
        "the expert's call."
    )
    out.append("")
    out.append("**Competency questions**")
    out.append("")
    out.append(_enum_table(report, "competency_question", "category"))
    out.append("")
    out.append("**Prohibited uses**")
    out.append("")
    out.append(_enum_table(report, "prohibited_use", "kind"))
    out.append("")

    # -- notes --------------------------------------------------------------
    out.append("## 5. Worth an eye, gating nothing")
    out.append("")
    if report.notes:
        for finding in report.notes:
            out.append(f"- **{finding.subject}** ({finding.check}) — {finding.message}")
    else:
        out.append("Nothing.")
    out.append("")

    # -- files --------------------------------------------------------------
    out.append("## 6. Where the records are")
    out.append("")
    out.append("| Record type | File | Records |")
    out.append("|---|---|---|")
    for record_type, filename in sorted(goldset.FILE_FOR.items()):
        count = report.gold.count(record_type)
        present = "present" if record_type in report.gold.files else "absent"
        out.append(f"| {record_type} | `eval/gold/{filename}` ({present}) | {count} |")
    out.append("")
    return "\n".join(out) + "\n"

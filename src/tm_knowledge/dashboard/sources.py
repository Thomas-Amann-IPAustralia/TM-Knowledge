"""Read the repo's own Markdown documents as data.

Three documents on the site are written for people and read here by a machine:
the ADR log, the status board and the glossary. Each parser is deliberately
strict — it raises when the shape it expects is not there, rather than
returning an empty list that renders as "no decisions" (rule 6). A document
reformatted in a way that breaks a parser should break the build, not quietly
empty a page.

Nothing here interprets. The ADR parser reads the authority a session wrote; it
does not decide what an ADR means.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tm_knowledge.config import REPO_ROOT

__all__ = ["Adr", "Stage", "read_decisions", "read_stage_board", "read_glossary"]

DOCS = REPO_ROOT / "docs"

_ADR_HEADING = re.compile(r"^## (ADR-(\d{4})) — (.+)$", re.MULTILINE)
# The authority is sometimes qualified in place — `agent-proposed (field list)`
# — so it is read as the leading word and the qualifier is left in the status
# column's prose rather than being dropped or mistaken for a fourth field.
_ADR_META = re.compile(
    r"\*\*Date\*\*\s*(\S+)\s*·\s*"
    r"\*\*Authority\*\*\s*([a-z-]+)[^·\n]*·\s*"
    r"\*\*Status\*\*\s*(.+)"
)
_SUPERSEDED = re.compile(r"[Ss]uperseded by (ADR-\d{4})")
_GLOSSARY_TERM = re.compile(r"^\*\*(.+?)\*\*\s*—\s*(.+)$", re.MULTILINE | re.DOTALL)


class MalformedDocument(ValueError):
    """A document the site reads did not have the shape the parser expects."""


@dataclass(frozen=True)
class Adr:
    number: str
    identifier: str
    title: str
    date: str
    authority: str
    status: str
    summary: str
    superseded_by: str | None


@dataclass(frozen=True)
class Stage:
    number: str
    name: str
    status: str
    status_note: str
    owner: str


def _first_sentence(body: str, *, limit: int = 320) -> str:
    """The Context paragraph's opening, for a one-line summary of an ADR."""
    match = re.search(r"\*\*Context\.\*\*\s*(.+?)(?:\n\n|$)", body, re.DOTALL)
    text = match.group(1) if match else body
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def read_decisions(path: Path | None = None) -> tuple[Adr, ...]:
    """Every ADR in `docs/DECISIONS.md`, in file order."""
    path = path or DOCS / "DECISIONS.md"
    text = path.read_text(encoding="utf-8")
    headings = list(_ADR_HEADING.finditer(text))
    if not headings:
        raise MalformedDocument(
            f"{path.name}: found no `## ADR-nnnn — title` headings. The site's "
            f"decision page is generated from them."
        )

    entries: list[Adr] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end() : end]
        meta = _ADR_META.search(body)
        if meta is None:
            raise MalformedDocument(
                f"{heading.group(1)}: no `**Date** … · **Authority** … · **Status** …` line. "
                f"Every ADR carries one (DECISIONS.md preamble)."
            )
        status = meta.group(3).strip()
        superseded = _SUPERSEDED.search(status) or _SUPERSEDED.search(body)
        entries.append(
            Adr(
                number=heading.group(2),
                identifier=heading.group(1),
                title=heading.group(3).strip(),
                date=meta.group(1).strip(),
                authority=meta.group(2).strip().strip("`"),
                status=status,
                summary=_first_sentence(body),
                superseded_by=superseded.group(1) if superseded else None,
            )
        )
    return tuple(entries)


def read_stage_board(path: Path | None = None) -> tuple[Stage, ...]:
    """The Stages 0–10 board from `docs/ROADMAP-STATUS.md`."""
    path = path or DOCS / "ROADMAP-STATUS.md"
    text = path.read_text(encoding="utf-8")
    section = re.search(r"^## Board\s*$(.+?)^## ", text, re.MULTILINE | re.DOTALL)
    if section is None:
        raise MalformedDocument(f"{path.name}: no `## Board` section.")

    stages: list[Stage] = []
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|---") or "| Stage |" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 4 or not cells[0].isdigit():
            continue
        status = cells[2]
        headline = re.match(r"\*\*(.+?)\*\*\s*(?:—\s*)?(.*)", status)
        stages.append(
            Stage(
                number=cells[0],
                name=cells[1],
                status=headline.group(1) if headline else status,
                status_note=(headline.group(2) if headline else "").strip(),
                owner=cells[3],
            )
        )
    if len(stages) < 11:
        raise MalformedDocument(
            f"{path.name}: the board has {len(stages)} stage rows; the roadmap has 11 "
            f"(Stages 0–10). A row that stopped parsing would disappear from the site."
        )
    return tuple(stages)


def read_glossary(path: Path | None = None) -> dict[str, dict[str, str]]:
    """`docs/GLOSSARY.md` as `{term: {section, text}}`.

    One glossary, two readers. The site's tooltips are the same words a session
    reads when it arrives cold, so a term explained twice cannot drift into two
    explanations.
    """
    path = path or DOCS / "GLOSSARY.md"
    text = path.read_text(encoding="utf-8")
    terms: dict[str, dict[str, str]] = {}
    section = ""
    for chunk in re.split(r"^## ", text, flags=re.MULTILINE)[1:]:
        section, _, body = chunk.partition("\n")
        section = section.strip()
        for paragraph in body.split("\n\n"):
            match = _GLOSSARY_TERM.match(paragraph.strip())
            if match is None:
                continue
            heading = " ".join(match.group(1).split())
            definition = " ".join(match.group(2).split())
            for name in _term_names(heading):
                terms[name] = {"term": heading, "section": section, "text": definition}
    if not terms:
        raise MalformedDocument(f"{path.name}: parsed no `**Term** — definition` entries.")
    return terms


def _term_names(heading: str) -> tuple[str, ...]:
    """The lookup keys for one glossary heading.

    Headings carry their own aliases — ``**Trade Marks Act 1995 (`TMA1995`)**``,
    ``**Prohibited use / prohibited inference**`` — and a tooltip should fire on
    any of them, because the site's prose uses whichever reads better in place.
    """
    names = {heading}
    bare = re.sub(r"\s*\(.*?\)\s*", " ", heading).strip()
    names.add(bare)
    for part in re.findall(r"\(([^)]*)\)", heading):
        names.add(part.strip())
    for name in list(names):
        for piece in name.split(" / "):
            names.add(piece.strip())
    return tuple(sorted({name.strip("` ") for name in names if name.strip("` ")}))

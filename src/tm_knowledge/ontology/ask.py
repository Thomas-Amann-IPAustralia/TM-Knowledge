"""Run the competency queries and render their answers.

`queries/README.md` sets the standard this module exists to enforce: *if a
question has no query and no query has a question, one of the two is wrong.*
`coverage()` is that check, and it reads the competency questions out of the
graph rather than out of a list kept beside it.

Each `.rq` file carries a header block that `parse_header` reads:

    # question: CQ-0017
    # answers: <the question, restated>
    # limits: <what this query does NOT answer>

`limits` is required and is the interesting field. A competency query that
returns rows always looks like an answer; the limits line is where the query
says what it has not established, and a query without one is refused rather than
run.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from rdflib import Dataset
from rdflib.namespace import RDF
from rdflib.query import Result

from tm_knowledge.config import DEFAULT_BASE_IRI, REPO_ROOT, base_iri
from tm_knowledge.ontology.build import build
from tm_knowledge.ontology.namespaces import APPROVED_GRAPH, TMK

__all__ = ["QUERY_DIR", "CompetencyQuery", "load_queries", "run", "coverage"]

QUERY_DIR = REPO_ROOT / "queries" / "competency"

_HEADER = re.compile(r"^#\s*(question|answers|limits)\s*:\s*(.+)$", re.MULTILINE)


class MalformedQuery(ValueError):
    """A query file missing a header field. Refused rather than run."""


@dataclass(frozen=True)
class CompetencyQuery:
    path: Path
    question_id: str
    answers: str
    limits: str
    text: str

    def run(self, dataset: Dataset) -> Result:
        return dataset.query(self.rebased())

    def rebased(self) -> str:
        """The query text under the configured base IRI.

        Query files are written against the default base because a `.rq` file
        has to name one, and an upstream ref cannot be a prefixed local name —
        `TMM/Part29/1#1` has slashes and a hash in it, so every ref-addressed
        node in a query is a full IRI. The base therefore appears in the file,
        and this puts it back under one constant (IDENTIFIERS.md §2)."""
        target = base_iri()
        if target == DEFAULT_BASE_IRI:
            return self.text
        return self.text.replace(DEFAULT_BASE_IRI, target)


def parse_header(path: Path) -> CompetencyQuery:
    text = path.read_text(encoding="utf-8")
    found = {key: value.strip() for key, value in _HEADER.findall(text)}
    missing = {"question", "answers", "limits"} - set(found)
    if missing:
        raise MalformedQuery(
            f"{path.name}: header is missing {sorted(missing)}. `limits` in "
            f"particular is not optional — a query that returns rows always looks "
            f"like an answer, and the limits line is where it says what it has not "
            f"established."
        )
    return CompetencyQuery(
        path=path,
        question_id=found["question"],
        answers=found["answers"],
        limits=found["limits"],
        text=text,
    )


def load_queries(directory: Path | None = None) -> tuple[CompetencyQuery, ...]:
    directory = directory or QUERY_DIR
    return tuple(parse_header(path) for path in sorted(directory.glob("*.rq")))


def render(result: Result, *, limit: int = 25, width: int = 62) -> list[str]:
    """A result as aligned text. Truncates values, never rows silently — the
    row count is printed whether or not every row is shown."""
    rows = list(result)
    if not rows:
        return ["    (no rows)"]
    names = [str(variable) for variable in result.vars or ()]

    def cell(value) -> str:
        if value is None:
            return "—"
        text = str(value)
        text = text.rsplit("/", 1)[-1] if text.startswith("https://data.ipaustralia") else text
        text = " ".join(text.split())
        return text if len(text) <= width else text[: width - 1] + "…"

    table = [[cell(row[index]) for index in range(len(names))] for row in rows[:limit]]
    widths = [
        max(len(names[index]), *(len(row[index]) for row in table))
        for index in range(len(names))
    ]
    out = ["    " + "  ".join(name.ljust(widths[i]) for i, name in enumerate(names))]
    out.append("    " + "  ".join("-" * w for w in widths))
    out.extend("    " + "  ".join(c.ljust(widths[i]) for i, c in enumerate(row)) for row in table)
    if len(rows) > limit:
        out.append(f"    … {len(rows) - limit} more of {len(rows)} rows")
    else:
        out.append(f"    {len(rows)} row(s)")
    return out


#: Categories no graph query can answer, and the stage that would.
#: A `search` question is answered by a ranked index over text and a `retrieval`
#: question by a generated answer over retrieved passages — neither is a SPARQL
#: result, and writing one that returned rows would be measuring the wrong
#: thing while looking like coverage.
DEFERRED_CATEGORIES = {
    "search": "Stage 7 — ranked search over the corpus",
    "retrieval": "Stage 8 — graph-aware AI retrieval",
}


def coverage(dataset: Dataset, queries: tuple[CompetencyQuery, ...]) -> dict[str, list[str]]:
    """Questions with no query, and queries naming no question.

    Both halves matter. A question with no query is unmeasured; a query naming a
    question the gold set does not hold is a query measuring something nobody
    approved.

    Competency questions only. Retrieval and search questions (`GA-`, `GS-`) are
    graded judgements about a system's output, not questions a query answers,
    and counting them here would report a coverage gap against work that is
    deliberately five stages away.
    """
    approved = dataset.graph(APPROVED_GRAPH)
    questions: dict[str, str] = {}
    for node in approved.subjects(RDF.type, TMK.CompetencyQuestion):
        record = approved.value(node, TMK.goldRecord)
        category = approved.value(node, TMK.questionCategory)
        if record is not None:
            questions[str(record)] = str(category) if category else ""
    asked = {query.question_id for query in queries}
    missing = set(questions) - asked
    return {
        "unqueried": sorted(q for q in missing if questions[q] not in DEFERRED_CATEGORIES),
        "deferred": sorted(
            f"{q} ({DEFERRED_CATEGORIES[questions[q]]})"
            for q in missing
            if questions[q] in DEFERRED_CATEGORIES
        ),
        "unknown": sorted(asked - set(questions)),
    }


def run(
    dataset: Dataset | None = None,
    queries: tuple[CompetencyQuery, ...] | None = None,
) -> list[str]:
    if dataset is None:
        dataset, _ = build()
    queries = queries if queries is not None else load_queries()

    out: list[str] = []
    for query in queries:
        out.append(f"\n=== {query.question_id} — {query.answers}")
        try:
            result = query.run(dataset)
        except Exception as error:  # a broken query is a finding, not a crash
            out.append(f"    QUERY FAILED: {error}")
            continue
        out.extend(render(result))
        out.append(f"    limits: {query.limits}")

    gaps = coverage(dataset, queries)
    if gaps["unqueried"]:
        out.append(
            f"\nquestions with no query ({len(gaps['unqueried'])}): "
            + ", ".join(gaps["unqueried"])
        )
    if gaps["deferred"]:
        out.append(
            f"\nquestions no graph query answers ({len(gaps['deferred'])}): "
            + ", ".join(gaps["deferred"])
        )
    if gaps["unknown"]:
        out.append(
            f"\nqueries naming no approved question ({len(gaps['unknown'])}): "
            + ", ".join(gaps["unknown"])
        )
    return out

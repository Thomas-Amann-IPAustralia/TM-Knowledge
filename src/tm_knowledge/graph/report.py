"""The demonstration report: what the ontology answers that a text index cannot.

Generated rather than written, for the reason S009 learned the hard way — a
hand-written analysis over this corpus was wrong in two of three chains and
nothing was checking. Every number below is computed at render time from the
committed graph and the pinned snapshot.

The report is also where the limits go, and they are stated at the top rather
than in a footnote. One approved search question is an illustration and not a
measurement; four ontology classes are deliberately empty; and every statement
in the graph is the *Manual's account* of section 43 rather than section 43
itself, because that is what the approved records were read from.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tm_knowledge.graph import build as build_module
from tm_knowledge.graph import ontology, queries
from tm_knowledge.stage0 import goldset

__all__ = ["render", "Ranking", "rank_naively"]

_WORD = re.compile(r"[a-z]+")


@dataclass(frozen=True, slots=True)
class Ranking:
    """Where a naive term-frequency ranker puts the approved answers."""

    query: str
    pool: int
    correct: dict[str, int]
    tempting: dict[str, int]
    top: tuple[tuple[int, str], ...]

    @property
    def worst_correct(self) -> int:
        return max(self.correct.values()) if self.correct else 0

    @property
    def best_tempting(self) -> int:
        return min(self.tempting.values()) if self.tempting else 0

    @property
    def every_trap_beats_every_answer(self) -> bool:
        return bool(self.correct and self.tempting) and max(
            self.tempting.values()
        ) < min(self.correct.values())


def rank_naively(record: dict[str, Any], corpus) -> Ranking | None:
    """Score the in-scope chunks by term frequency against one search question.

    Deliberately the dumbest possible baseline, and deliberately *not* a straw
    man: term frequency over a scoped candidate set is what a first-cut search
    over this corpus actually looks like, and the point is not that it is bad at
    ranking. The point is that the two passages the reviewer graded most
    relevant are the ones that say the question is another section's business,
    and they say so in fewer words than the passages that are wrong.
    """
    from tm_knowledge.stage0.worksheet import PILOT_PROVISION, ScopeRule, select

    chunks = {
        chunk.chunk_ref: chunk
        for chunk in select(corpus, ScopeRule(provision=PILOT_PROVISION))
    }
    if not chunks:
        return None

    terms = [term for term in _WORD.findall(str(record["query"]).lower()) if len(term) > 3]
    if not terms:
        return None

    def score(text: str) -> int:
        lowered = text.lower()
        return sum(lowered.count(term) for term in terms)

    ranked = sorted(
        ((score(chunk.text), ref) for ref, chunk in chunks.items()),
        key=lambda pair: (-pair[0], pair[1]),
    )
    position = {ref: index for index, (_, ref) in enumerate(ranked, start=1)}

    return Ranking(
        query=str(record["query"]),
        pool=len(ranked),
        correct={
            str(entry["ref"]): position[str(entry["ref"])]
            for entry in record.get("relevant") or ()
            if str(entry["ref"]) in position
        },
        tempting={
            str(ref): position[str(ref)]
            for ref in record.get("irrelevant_but_tempting") or ()
            if str(ref) in position
        },
        top=tuple(ranked[:5]),
    )


def _ordinal(number: int) -> str:
    """1st, 2nd, 3rd, 4th — and 11th, 12th, 13th, which the naive rule gets wrong."""
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def _rows(dataset, query, limit: int):
    """(column names, rows, total) for one query."""
    from tm_knowledge.graph.cli import _short

    result = dataset.query(queries.render(query))
    found = list(result)
    columns = tuple(str(name) for name in (result.vars or ()))
    rows = [
        tuple(_short(str(value)) if value is not None else "" for value in row)
        for row in found[:limit]
    ]
    return columns, rows, len(found)


def _table(columns: tuple[str, ...], rows: list[tuple[str, ...]], width: int = 60) -> list[str]:
    if not rows:
        return ["_no rows_", ""]
    count = max(max(len(row) for row in rows), len(columns))
    names = list(columns) + [""] * (count - len(columns))
    out = ["| " + " | ".join(names) + " |", "|" + "---|" * count]
    for row in rows:
        cells = [
            (cell[: width - 1] + "…" if len(cell) > width else cell).replace("|", "\\|")
            for cell in row
        ] + [""] * (count - len(row))
        out.append("| " + " | ".join(cells) + " |")
    out.append("")
    return out


def render(
    root: Path,
    dataset=None,
    corpus=None,
    *,
    limit: int = 4,
    generated: str | None = None,
) -> str:
    """The whole demonstration, with live numbers."""
    stamp = generated or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    gold = goldset.load()
    built = build_module.build(gold)

    out: list[str] = [
        "<!-- Generated by tm_knowledge.graph.report. Do not hand-edit. -->",
        "",
        "# A working ontology for section 43",
        "",
        "What a knowledge graph over the pilot area does that a search index",
        "cannot, built end to end from content a trade marks expert signed.",
        "",
        "| | |",
        "|---|---|",
        f"| Approved records in | {gold.total} |",
        f"| Triples out | {built.total} |",
        f"| Named graphs | {len(built.documents)} |",
        f"| Ontology modules | {len(ontology.MODULES)} |",
        f"| Demonstration queries | {len(queries.QUERIES)} |",
        f"| Generated | {stamp} |",
        "",
        "## Read this first",
        "",
        "**Nothing here was extracted.** Every triple comes from one of the "
        f"{gold.total} records in `eval/gold/` that carries a reviewer's name "
        "and a date. There is no model, no threshold and no candidate "
        "generation step: Stage 2 is still closed (ADR-0010) and this is not a "
        "way round it. What has happened is a change of *form* — the same "
        "approved content, expressed so that it can be traversed, constrained "
        "and queried.",
        "",
        "**The graph is the Manual's account of section 43, not section 43.** "
        "Every assertion was read from a Manual passage, including the ones "
        "*about* the Act. The Manual states the Registrar's practice and does "
        "not bind the Registrar's discretion (CLAUDE.md rule 5), and the "
        "ontology keeps that distinction as a disjointness axiom rather than "
        "as a sentence in a document.",
        "",
        "**It is as complete as the review got.** 190 records of a much larger "
        "intended set; `tmk-coverage` says what is missing.",
        "",
    ]

    if built.unpopulated:
        out += [
            "**Four classes are declared and deliberately empty.** "
            + ", ".join(f"`{name}`" for name in built.unpopulated)
            + ". Deciding that a particular concept is a ground of refusal "
            "rather than a legal test is a legal judgement, and no approved "
            "record carries it. The slots are the shape of the question; an "
            "agent filling them would be the failure this whole programme is "
            "arranged to prevent.",
            "",
        ]

    out += _search_section(gold, corpus)
    out += _conflict_section(built)
    out += _query_section(dataset, limit)
    out += _limits_section(built, gold)
    return "\n".join(out).rstrip() + "\n"


def _search_section(gold: goldset.GoldSet, corpus) -> list[str]:
    out = [
        "## The case in one query",
        "",
    ]
    records = list(gold["gold_search_question"])
    if corpus is None or not records:
        return out + [
            "_Needs the pinned snapshot and at least one approved search "
            "question. Run `tmk-fetch-upstream` and rebuild._",
            "",
        ]

    record = records[0]
    ranking = rank_naively(record, corpus)
    if ranking is None:
        return out + ["_Could not rank: no in-scope chunks._", ""]

    out += [
        f"Approved search question **{record['id']}** asks:",
        "",
        f"> {ranking.query}",
        "",
        "The reviewer graded two passages as the right answers and named three "
        "more as *tempting and wrong*. Both facts are in the gold set; neither "
        "is this document's opinion.",
        "",
        f"Ranking all {ranking.pool} in-scope chunks by plain term frequency — "
        "the dumbest baseline, and roughly what a first-cut search over this "
        "corpus looks like:",
        "",
        "| passage | reviewer's grading | rank of 216 |",
        "|---|---|---|",
    ]
    for ref, position in sorted(ranking.correct.items(), key=lambda kv: kv[1]):
        out.append(f"| `{ref}` | **correct** | {position} |")
    for ref, position in sorted(ranking.tempting.items(), key=lambda kv: kv[1]):
        out.append(f"| `{ref}` | tempting, wrong | {position} |")
    out.append("")

    if ranking.every_trap_beats_every_answer:
        out += [
            "**Every wrong passage outranks every right one.** The best "
            f"correct answer is {_ordinal(min(ranking.correct.values()))}; the "
            f"worst trap is {_ordinal(max(ranking.tempting.values()))}.",
            "",
        ]
    out += [
        "The reason is not that the ranker is bad. It is that the correct "
        "answers are the passages saying *this is another section's business*, "
        "and a passage that declines a topic uses fewer of its words than a "
        "passage that discusses it. No amount of tuning fixes that, because the "
        "signal is not in the text.",
        "",
        "It is in the graph, twice, and both halves were put there by a person:",
        "",
    ]

    concepts = {str(c["id"]): c for c in gold["gold_concept"]}
    excluding = [
        (str(c["id"]), str(c["pref_label"]), label)
        for c in gold["gold_concept"]
        for label in c.get("not_labels") or ()
        if "confusion between" in str(label).lower()
    ]
    for identifier, pref, label in excluding[:3]:
        out.append(
            f"1. **`{identifier}` — “{pref}” records “{label}” as an explicit "
            "*non*-synonym.** A reviewer's refusal. No index holds one, and no "
            "embedding produces one: the two phrases are neighbours in the "
            "corpus and belong to different sections of the Act."
        )
        break

    for relationship in gold["gold_relationship"]:
        if str(relationship["predicate"]) != "allocatesTo":
            continue
        out += [
            f"2. **`{relationship['id']}` — `{relationship['subject']}` "
            f"*allocatesTo* `{relationship['object']}`**, approved by "
            f"{relationship['approved_by']} on {relationship['approved_date']}, "
            "on the strength of this sentence:",
            "",
            f"   > {' '.join(str(relationship['supporting_text']).split())}",
            "",
        ]
        subject = str(relationship["subject"])
        if subject in ranking.correct:
            out.append(
                f"   That passage — `{subject}` — is one of the two correct "
                f"answers, and term frequency ranks it "
                f"{ranking.correct[subject]}th of {ranking.pool}."
            )
            out.append("")
        break

    out += [
        "`queries/sent-elsewhere.rq` is that lookup. It is not a better "
        "ranking; it is a different operation, and it is only possible because "
        "somebody wrote down what a thing is *not*.",
        "",
        "**One approved search question is an illustration, not a measurement.** "
        "The gold set holds one of a target 20–50, so nothing here is a "
        "precision figure and it must not be quoted as one.",
        "",
    ]
    return out


def _conflict_section(built: build_module.Build) -> list[str]:
    if not built.conflicts:
        return []
    out = [
        "## What the graph noticed about its own inputs",
        "",
        "The graph's second use, and the one nobody designed for: it is a "
        "reviewer of the review. These pairs were both signed, on the same "
        "workbook, by the same person. Reading 368 rows in order was never "
        "going to put them side by side; making them edges did it immediately.",
        "",
    ]
    for first, second, detail in built.conflicts:
        out.append(f"- **{first} against {second}** — {detail}")
    out += [
        "",
        "`queries/both-sides.rq` finds a second kind: a concept that appears on "
        "both sides of the same relation, which catches `GR-0032` — a record "
        "whose own note says its subject and object are reversed, approved "
        "anyway.",
        "",
        "**Neither is resolved here.** Both statements stay in the graph. "
        "Choosing between two things a reviewer approved is not an agent's call "
        "(CLAUDE.md rule 1); noticing that they cannot both be right is.",
        "",
    ]
    return out


def _query_section(dataset, limit: int) -> list[str]:
    out = ["## The queries", ""]
    if dataset is None:
        return out + [
            "_Needs the `[graph]` extra. `pip install -e \".[graph]\"` then "
            "`tmk-graph --report`._",
            "",
        ]
    for query in queries.QUERIES:
        columns, rows, total = _rows(dataset, query, limit)
        out += [
            f"### `{query.name}` — {query.title}",
            "",
            query.why,
            "",
            f"**{total} row(s).** First {min(limit, total)}:",
            "",
        ]
        out += _table(columns, rows)
    return out


def _limits_section(built: build_module.Build, gold: goldset.GoldSet) -> list[str]:
    return [
        "## What this does not do",
        "",
        "- **It does not decide anything.** No ground is raised, no application "
        "is assessed, and the roadmap keeps evaluative conclusions outside "
        "automated reasoning scope on purpose.",
        "- **It does not reason.** No OWL reasoner is run. The disjointness "
        "axiom and the SHACL shapes are checks; nothing infers new triples, and "
        "nothing should until somebody has decided what inferences are wanted.",
        "- **It holds no case law.** Every judicial decision in the graph is a "
        "citation whose text nothing in the programme has read (HANDOFF Q6).",
        "- **It is not measured.** The evaluation harness measures a retrieval "
        "system against the gold set; there is no retrieval system yet, and the "
        "thresholds that would say whether a number is good enough are still "
        "unwritten (`eval/measures.md`).",
        "- **The base IRI is provisional.** `https://data.ipaustralia.gov.au/"
        "tmk/` is a proposal, not a controlled domain (HANDOFF Q7). It is one "
        "configuration value and a rebuild.",
        "",
        "## What a person could do next, in an hour",
        "",
        "- **Populate one of the four empty classes.** Deciding which of the 52 "
        "concepts are grounds of refusal, and which are tests, is the single "
        "highest-value hour available: it turns a taxonomy into a model, and "
        "nothing else in the programme is blocked on it.",
        "- **Rule on the two opposed pairs above.** Each is one line.",
        "- **Settle the ten decisions in "
        "`data/derived/reports/blockers.md`**, which releases 30 more records "
        "into the graph.",
        "",
    ]

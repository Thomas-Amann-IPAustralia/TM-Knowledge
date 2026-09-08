"""The section 43 boundary, as the owner drew it — one hop, on the chunk.

OQ-0014 asked where section 43 stops. The answer, in his words:

    If we consider section 43 the central node in a network, it's network may
    reach out by one hop. That is to say, if section 43 refers to a specific
    chunk of another section, that specific chunk is within scope but its parent
    section is not. Similarly, if a court decision is referred to in S43 then it
    is in scope but any other decisions/information considered in the court
    decision is not in scope.

Three structural parts, and this module is all three:

1. **One hop.** What the section 43 material cites is in. What *that* cites is
   not. The boundary is the citation graph at radius one.
2. **The hop lands on what was named, not on its parent.** A citation of
   `TMA1995/s41(2)` puts `s41(2)` in scope and leaves section 41 out. This is
   the part with teeth — it is what stops the boundary swallowing whole
   neighbouring provisions — and it is expressible exactly against the refs
   upstream already holds.
3. **Case law inherits the same rule.** A decision cited from section 43
   material is in scope; what the decision itself discusses is not. For this
   corpus that second half costs nothing, because no decision text exists
   anywhere in the programme (Q-11) — so the rule bites on the *first* half
   only, and this module says so rather than implying a closure it never
   computed.

**A fourth part of his answer is not implemented here, on purpose.** He added
that the relationship between s 43 and s 41 is "more diffuse", and that s 43
should refer to s 41 only in that resolving an s 43 ground has no impact on the
s 41 ground. That is a statement about how two grounds of refusal interact — a
proposition of trade marks law, not a selection rule — and this repo does not
author those (CLAUDE.md rule 1). It is recorded in ADR-0072 and quoted verbatim
in `review/returned/260908-owner-notes-issue-12.md`, and it is the kind of thing
that belongs in a relationship record an expert signs.

**This does not write `eval/pilot-scope.md`.** That deliverable asks several
things the owner did not answer — whether geographical indications are the
centre of the topic or a corner of it, whether point-in-time questions are in
scope — and answering the ones he did answer is not the same as the document
being written. What this produces is the boundary the rule selects, counted, as
a committed report he can correct.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0.worksheet import PILOT_PROVISION, ScopeRule, select
from tm_knowledge.upstream.loader import Corpus, load_corpus

__all__ = ["REPORT_PATH", "Boundary", "compute", "render", "write"]

REPORT_PATH = REPO_ROOT / "data" / "derived" / "reports" / "boundary.md"


@dataclass(frozen=True)
class Boundary:
    """What one hop from section 43 reaches, and what it deliberately does not."""

    #: The centre: chunks the scope rule already selects (ADR-0022).
    centre: tuple[str, ...] = ()
    #: Provisions and units cited from the centre, as named — never widened.
    provisions: tuple[str, ...] = ()
    #: Court decisions cited from the centre.
    cases: tuple[str, ...] = ()
    #: Manual chunks the centre cites through `internal_refs`.
    internal: tuple[str, ...] = ()
    #: Parent sections deliberately left out by part 2 of the rule, with the
    #: units that pulled them to the edge. This is the rule's whole value, so it
    #: is reported rather than merely not-included.
    parents_excluded: dict[str, tuple[str, ...]] = field(default_factory=dict)
    #: Cited provisions the corpus does not hold at all (Q-06, Q-08).
    unresolved: tuple[str, ...] = ()
    #: Parents that came in whole *anyway*, because the centre cites them bare
    #: as well as citing units within them — with the chunks that did it. The
    #: owner's rule keeps a parent out only when nothing named it directly, and
    #: this is where that turns out not to hold (ADR-0072, OQ-0021).
    parents_cited_bare: dict[str, tuple[str, ...]] = field(default_factory=dict)

    @property
    def in_scope(self) -> tuple[str, ...]:
        """Everything the boundary admits, as refs, deduplicated and sorted."""
        return tuple(sorted({*self.centre, *self.provisions, *self.cases, *self.internal}))


def _parent_of(ref: str) -> str | None:
    """The provision a unit sits under, or None if the ref is already one.

    `TMA1995/s41(2)` -> `TMA1995/s41`. Cut at the first unit separator, which is
    the same grammar `ScopeRule.matches` reads — the boundary rule and the scope
    rule must not disagree about what "beneath" means.
    """
    for index, character in enumerate(ref):
        if character in "(~" and index:
            return ref[:index]
    return None


def compute(corpus: Corpus | None = None, rule: ScopeRule | None = None) -> Boundary:
    corpus = corpus or load_corpus()
    rule = rule or ScopeRule()
    centre = select(corpus, rule)
    centre_refs = {chunk.chunk_ref for chunk in centre}

    provisions: set[str] = set()
    cases: set[str] = set()
    internal: set[str] = set()
    parents: dict[str, set[str]] = {}
    bare: dict[str, set[str]] = {}

    for chunk in centre:
        for edge in chunk.provisions:
            # The pilot provision itself is the centre, not a hop from it.
            if rule.matches(edge.id):
                continue
            provisions.add(edge.id)
            parent = _parent_of(edge.id)
            if parent is not None and parent != edge.id:
                parents.setdefault(parent, set()).add(edge.id)
            else:
                bare.setdefault(edge.id, set()).add(chunk.chunk_ref)
        for edge in chunk.cases:
            cases.add(edge.id)
        for edge in chunk.internal_refs:
            # Only a hop that lands somewhere new is a hop.
            if edge.ref and edge.ref not in centre_refs:
                internal.add(edge.ref)

    known = corpus.provisions.keys() | corpus.units.keys()
    unresolved = {ref for ref in provisions if ref not in known}

    return Boundary(
        centre=tuple(sorted(centre_refs)),
        provisions=tuple(sorted(provisions)),
        cases=tuple(sorted(cases)),
        internal=tuple(sorted(internal)),
        parents_excluded={
            parent: tuple(sorted(units))
            for parent, units in sorted(parents.items())
            # A parent that is itself cited directly is in scope on its own
            # account, and is not an exclusion the rule made.
            if parent not in provisions
        },
        unresolved=tuple(sorted(unresolved)),
        parents_cited_bare={
            parent: tuple(sorted(chunks))
            for parent, chunks in sorted(bare.items())
            if parent in parents
        },
    )


def render(generated: str | None = None, corpus: Corpus | None = None) -> str:
    boundary = compute(corpus)
    stamp = generated or date.today().isoformat()
    parts: list[str] = [
        "<!-- Generated by tm_knowledge.stage0.boundary. Do not hand-edit. -->",
        "",
        "# Where section 43 stops — the boundary, computed",
        "",
        f"**Generated {stamp}** by `tmk-boundary --write` against the pinned snapshot.",
        "",
        "## The rule",
        "",
        "Yours, from OQ-0014 on 2026-09-08, in three structural parts:",
        "",
        "1. **One hop.** What the section 43 material cites is in scope. What *that* "
        "cites is not.",
        "2. **The hop lands on what was named, not on its parent.** A citation of "
        "`TMA1995/s41(2)` puts that subsection in scope and leaves section 41 out.",
        "3. **Case law inherits the same rule.** A decision cited from section 43 "
        "material is in scope; what the decision itself discusses is not.",
        "",
        "A fourth thing you wrote — that the s 43 / s 41 relationship is more diffuse, "
        "and that s 43 should refer to s 41 only in that resolving an s 43 ground has no "
        "impact on the s 41 ground — is **not** implemented here. It is a statement about "
        "how two grounds interact, which is trade marks law rather than a selection rule, "
        "and this repo does not write those. It is recorded in ADR-0072 and belongs in a "
        "relationship record somebody signs.",
        "",
        "## What it selects",
        "",
        "| | count |",
        "|---|---|",
        f"| Manual passages at the centre — they cite `{PILOT_PROVISION}` "
        f"or a unit beneath it | {len(boundary.centre)} |",
        f"| Provisions and units reached in one hop | {len(boundary.provisions)} |",
        f"| Court decisions reached in one hop | {len(boundary.cases)} |",
        f"| Other Manual passages reached in one hop | {len(boundary.internal)} |",
        f"| **In scope in total** | **{len(boundary.in_scope)}** |",
        "",
        "## What part 2 of the rule keeps out",
        "",
        "This is where the rule earns its place. Each of these parent provisions is "
        "**out of scope**, and is out only because you said the hop lands on the unit "
        "and not on its parent. Without that sentence every one of them would have come "
        "in whole, and each carries its own subsections, notes and cross-references.",
        "",
    ]
    if boundary.parents_excluded:
        parts.append("| parent, excluded | the unit that was cited |")
        parts.append("|---|---|")
        for parent, units in boundary.parents_excluded.items():
            parts.append(f"| `{parent}` | {', '.join(f'`{unit}`' for unit in units)} |")
    else:
        parts.append(
            "Nothing — every citation from the centre names a whole provision rather "
            "than a unit within one. The rule costs nothing here and still holds."
        )
    if boundary.parents_cited_bare:
        parts.extend(
            [
                "",
                "## Where the rule does not do what you expected — please read this",
                "",
                "You singled out section 41: *“S43 will be required to refer to a number of "
                "specific chunks within section 41.”* Applied to the corpus, the rule does "
                "not produce that — and section 41 turns out not to be the only one, which "
                "is why this list is longer than you might expect.",
                "",
                "The rule keeps a parent out when the citation named a unit inside it. But "
                "the provisions below are cited **bare** somewhere in the section 43 "
                "material — the Manual writes “section 41”, not “section 41(3)” — as well "
                "as by unit. A bare citation names the parent, so the parent comes in "
                "whole, and part 2 of the rule never engages.",
                "",
                "| provision | units also cited | passages citing it bare |",
                "|---|---|---|",
            ]
        )
        for parent, chunks in boundary.parents_cited_bare.items():
            # From the reached set, not from parents_excluded: a parent cited
            # bare is by definition *not* in the excluded map, and looking there
            # printed an empty column for every row.
            units = ", ".join(
                f"`{ref}`" for ref in boundary.provisions if _parent_of(ref) == parent
            )
            shown = ", ".join(f"`{ref}`" for ref in chunks[:4])
            if len(chunks) > 4:
                shown += f" … and {len(chunks) - 4} more"
            parts.append(f"| `{parent}` | {units or '—'} | {shown} |")
        parts.extend(
            [
                "",
                "This is not a defect in the rule; it is the rule meeting a corpus that "
                "cites more loosely than the rule assumes. Three ways out, and choosing is "
                "yours — it is **OQ-0021** on the dashboard: treat a bare citation as "
                "naming the whole provision and accept it (what happens today); treat a "
                "bare citation as reaching only the units the material actually discusses, "
                "which needs somebody to say which those are; or name section 41 as a "
                "special case and leave the general rule alone.",
                "",
            ]
        )

    parts.extend(
        [
            "",
            "## What it reaches",
            "",
            f"**{len(boundary.provisions)} provisions and units.**",
            "",
            ", ".join(f"`{ref}`" for ref in boundary.provisions) or "none",
            "",
        ]
    )
    if boundary.unresolved:
        parts.extend(
            [
                f"**{len(boundary.unresolved)} of those land on nothing this corpus "
                "holds** — a renumbering, a superseded provision, or an instrument "
                "outside the held set. They are listed rather than dropped, because a "
                "citation that resolves to nothing is a finding about the corpus.",
                "",
                ", ".join(f"`{ref}`" for ref in boundary.unresolved),
                "",
            ]
        )
    parts.extend(
        [
            f"**{len(boundary.cases)} court decisions.**",
            "",
            ", ".join(f"`{ref}`" for ref in boundary.cases) or "none",
            "",
            "The second half of part 3 — that what a decision discusses is out of scope "
            "— costs nothing today, because no decision text exists anywhere in the "
            "programme. We hold the citation and not a word of what any court said. So "
            "the rule is honoured trivially rather than enforced, and this report says "
            "so rather than implying a closure it never computed.",
            "",
            "## What this is not",
            "",
            "**It is not `eval/pilot-scope.md`.** That deliverable asks several things "
            "you did not answer — whether geographical indications are the centre of the "
            "topic or a corner of it, whether questions about how the law stood at an "
            "earlier date are in scope, and which Manual Parts count as in when they "
            "discuss the subject without citing the section. Answering the questions you "
            "did answer is not the same as the document being written, and the harness "
            "still reports it as missing.",
            "",
            "**It selects; it does not judge.** Every ref above is one upstream recorded, "
            "reached by following a citation. Nothing here read a passage and decided it "
            "was about section 43.",
            "",
        ]
    )
    return "\n".join(parts).rstrip() + "\n"


def write(path: Path | None = None, generated: str | None = None) -> Path:
    path = path or REPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(generated), encoding="utf-8")
    return path

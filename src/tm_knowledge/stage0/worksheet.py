"""The Pass B worksheet (parallel track P9), and the selections other passes use.

Every selected chunk printed with its `chunk_ref`, `heading_path`,
`content_hash` and full text, in a form that can be read, highlighted and
commented on. The owner should never type a ref or a hash by hand, and with this
they never do.

**`ScopeRule` is no longer a scope rule, and the name is kept because renaming a
thing does not change what reads it.** It selects every chunk whose
`provisions[]` carries a given provision or a unit beneath it, matched on the ref
grammar rather than by substring, plus every chunk sharing a `page_ref` with one
of those. Under ADR-0022 that was a *boundary* — a claim about what was in scope
— and the whole corpus outside it was out. The owner withdrew the boundary on
2026-09-08 and the whole Manual is in scope (ADR-0081), so what is left is a
**selector**: a way to say "print me the passages about section 41", which is a
working choice and not a claim about scope. It answers "which area am I
annotating today", and every area is available.

Edges of every `extraction` and `certainty` value are in — an `ambiguous` edge is
a reason to print a chunk, never a reason to drop one (Q-07).

Page-mates are in because the Manual's guidance frequently sits in the chunks
around the one carrying the citation: an instruction, then its exceptions, then
a worked example, with the provision named once at the top. Selecting only
citing chunks would print the sentence and drop the practice.

**`select_evidenced` is the other selector, and it is the one the graph uses**
(ADR-0097). It selects on what this repository has said something about rather
than on which provision a passage cites — so it has no provision in it at all,
which is what makes it safe to be a default. `select` still needs somebody to
name a provision, and naming one is a choice a person makes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from typing import Iterable

from tm_knowledge.refs import parse_ref
from tm_knowledge.upstream.loader import Corpus
from tm_knowledge.upstream.records import Chunk

#: The pilot provision (ADR-0013).
PILOT_PROVISION = "TMA1995/s43"


@dataclass(frozen=True, slots=True)
class ScopeRule:
    """ADR-0022's provisional worksheet scope rule, as a predicate.

    Held in one place because two packages read it — the worksheet prints it and
    the reconnaissance report costs it — and a second copy would be a second
    rule the moment either changed.
    """

    provision: str = PILOT_PROVISION
    include_page_mates: bool = True

    def __post_init__(self) -> None:
        parse_ref(self.provision)

    def matches(self, edge_id: str) -> bool:
        """Does a provision edge name the provision, or a unit beneath it?

        Matched on the ref grammar: `TMA1995/s43` selects `TMA1995/s43`,
        `TMA1995/s43(1)`, `TMA1995/s43(1)(a)` and `TMA1995/s43~1`, and must not
        select `TMA1995/s430` if the corpus ever grows one. A substring test
        would, which is exactly what ADR-0022 rules out.
        """
        if edge_id == self.provision:
            return True
        if not edge_id.startswith(self.provision):
            return False
        return edge_id[len(self.provision)] in "(~/"

    def describe(self) -> str:
        rule = (
            f"every chunk whose `provisions[]` carries `{self.provision}` or any unit "
            "beneath it, matched on the ref grammar and not by substring"
        )
        if self.include_page_mates:
            rule += ", plus every chunk sharing a `page_ref` with one of those"
        return rule


def select(corpus: Corpus, rule: ScopeRule | None = None) -> tuple[Chunk, ...]:
    """The chunks the rule selects, in reading order (page, then ordinal)."""
    rule = rule or ScopeRule()
    citing = [
        chunk
        for chunk in corpus.chunks.values()
        if any(rule.matches(edge.id) for edge in chunk.provisions)
    ]
    if not rule.include_page_mates:
        selected = citing
    else:
        pages = {chunk.page_ref for chunk in citing}
        selected = [
            mate for page_ref in pages for mate in corpus.chunks_on_page(page_ref)
        ]
    # Deduplicated by ref, not by value: a loaded record holds read-only mappings
    # and is deliberately unhashable, and the ref is the identity anyway.
    unique = {chunk.chunk_ref: chunk for chunk in selected}
    return tuple(
        sorted(unique.values(), key=lambda chunk: (chunk.page_ref, chunk.ordinal))
    )


def _edge_summary(chunk: Chunk, rule: ScopeRule) -> str:
    parts = []
    for edge in chunk.provisions:
        marker = " ←" if rule.matches(edge.id) else ""
        certainty = f", {edge.certainty}" if edge.certainty else ""
        parts.append(f"`{edge.id}` ({edge.extraction}{certainty}){marker}")
    return "; ".join(parts) if parts else "—"


def render(
    corpus: Corpus, rule: ScopeRule | None = None, *, generated: str | None = None
) -> str:
    """The worksheet, as Markdown.

    `generated` is injectable so that the output is deterministic in the way
    that matters: the same snapshot and the same rule produce byte-identical
    text, and the only thing a re-run on another day changes is the date on the
    header. A worksheet that differed run to run could not be diffed when the
    expert boundary lands, which is exactly what ADR-0022 promises to do.
    """
    rule = rule or ScopeRule()
    selected = select(corpus, rule)
    citing = {
        chunk.chunk_ref
        for chunk in selected
        if any(rule.matches(edge.id) for edge in chunk.provisions)
    }
    pin = corpus.pin

    out: list[str] = []
    out.append("<!-- Generated by tm_knowledge.stage0.worksheet. Do not hand-edit. -->\n")
    out.append(f"# Pass B annotation worksheet — {rule.provision}\n")
    out.append(
        "> **This is one area of the Manual, chosen — not a boundary.** The whole\n"
        "> Manual is in scope: the owner withdrew the section 43 boundary on\n"
        "> 2026-09-08 and there is no exclusion rule anywhere in this repository\n"
        "> (ADR-0081, ADR-0096). The rows below are what a deliberately\n"
        "> over-inclusive machine rule selects for the provision named above, so\n"
        "> that annotation has somewhere to start. Nothing outside them is out of\n"
        "> scope; it is unprinted, and `--provision` prints somewhere else.\n"
    )
    out.append("\n| | |\n|---|---|")
    out.append(f"| Selection rule | {rule.describe()} |")
    out.append(f"| Chunks printed | {len(selected)} of {len(corpus.chunks)} |")
    out.append(f"| — of which cite the provision | {len(citing)} |")
    out.append(f"| — page-mates carried in with them | {len(selected) - len(citing)} |")
    out.append(f"| Pages | {len({chunk.page_ref for chunk in selected})} |")
    out.append(f"| Pinned snapshot | `{pin.repo}` @ `{pin.commit}` |")
    out.append(
        f"| Extractor versions | `{pin.manual_extractor_version}`, "
        f"`{pin.legislation_extractor_version}` |"
    )
    stamp = generated or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out.append(f"| Generated | {stamp} |")

    out.append(
        "\n\n## How to use this\n\n"
        "Read, highlight, and write in the margins. Nothing here needs to be typed\n"
        "into a form: an agent transcribes what you mark into validated records and\n"
        "**never fills a judgement field you left empty** (parallel track P8).\n\n"
        "Every row carries the two things that must not be typed by hand — the\n"
        "`chunk_ref` and the `content_hash` the text had when this was printed. If\n"
        "the corpus moves under an annotation, that hash is what says so.\n\n"
        "A `←` on a provision edge marks the edge that selected the chunk.\n"
        "`href` means the Manual's authors linked the provision themselves; `regex`\n"
        "means upstream read it out of the prose, and `default` on such an edge is\n"
        "upstream's inference from a bare section number rather than anything IP\n"
        "Australia said. `ambiguous` means upstream refused to choose between\n"
        "instruments — those rows are printed **because** they are ambiguous.\n"
    )

    current_page = None
    for chunk in selected:
        if chunk.page_ref != current_page:
            current_page = chunk.page_ref
            page = corpus.pages[current_page]
            out.append(f"\n\n---\n\n## {page.nav_title}\n")
            out.append(f"`{page.page_ref}` · {page.part_id} · <{page.url}>\n")
            if page.last_amended:
                out.append(f"\nLast amended {page.last_amended}. {page.amendment_note or ''}\n")
        marker = " ★" if chunk.chunk_ref in citing else ""
        out.append(f"\n### `{chunk.chunk_ref}`{marker}\n")
        out.append(f"**Heading path** {' › '.join(chunk.heading_path)}\n")
        out.append(
            f"\n| | |\n|---|---|\n"
            f"| kind | `{chunk.kind}` |\n"
            f"| ordinal | {chunk.ordinal} |\n"
            f"| content_hash | `{chunk.content_hash}` |\n"
            f"| provision edges | {_edge_summary(chunk, rule)} |\n"
            f"| case citations | "
            f"{'; '.join(f'{edge.citation}' for edge in chunk.cases) or '—'} |\n"
        )
        out.append("\n> " + re.sub(r"\n", "\n> ", chunk.text) + "\n")

    out.append(
        "\n\n---\n\n*Generated from the pinned snapshot. Selection rule: ADR-0022's, "
        "now a selector rather than a boundary (ADR-0096). Everything not printed here "
        "is in scope and unprinted, not excluded.*\n"
    )
    return "\n".join(out)


def cited_refs(stores: Iterable[tuple[str, dict, dict | None]]) -> set[str]:
    """Every upstream ref a set of records names, record fields and evidence both.

    `stores` yields `(record_type, record, envelope)`; the envelope is None for a
    signed record and the `authored:` block for an authored one. Kept here rather
    than in the graph builder because two callers need it and a second copy would
    be a second answer to "what has this repository spoken about".
    """
    from tm_knowledge.stage0.schemas import read_path, ref_paths

    found: set[str] = set()
    for record_type, record, envelope in stores:
        for path in ref_paths(record_type):
            for _, value in read_path(record, path):
                if isinstance(value, str):
                    found.add(value)
        for item in (envelope or {}).get("evidence") or ():
            if isinstance(item, dict) and isinstance(item.get("ref"), str):
                found.add(item["ref"])
    return found


def select_evidenced(
    corpus: Corpus, refs: Iterable[str], *, include_page_mates: bool = True
) -> tuple[Chunk, ...]:
    """The chunks a set of refs reaches, in reading order.

    **This is the rule that replaced the section 43 fence in the graph**
    (ADR-0097). It selects on what the repository has said something about, not
    on which provision a passage happens to cite — so it has no boundary in it,
    it grows as knowledge is authored, and it never needs re-deciding when scope
    changes, because it is not a scope rule.

    Page-mates come in for the reason they always did: the Manual states an
    instruction, then its exceptions, then a worked example, and a record
    usually cites one of the three. Selecting the cited chunk alone would put
    the sentence in the graph and leave the practice out.

    Refs that are not Manual chunks — provisions, units, case citations — are
    ignored here. They reach the graph by their own paths; this function answers
    only "which passages of the Manual".
    """
    seed = [corpus.chunks[ref] for ref in sorted(set(refs)) if ref in corpus.chunks]
    if not include_page_mates:
        selected = seed
    else:
        pages = {chunk.page_ref for chunk in seed}
        selected = [
            mate for page_ref in sorted(pages) for mate in corpus.chunks_on_page(page_ref)
        ]
    unique = {chunk.chunk_ref: chunk for chunk in selected}
    return tuple(
        sorted(unique.values(), key=lambda chunk: (chunk.page_ref, chunk.ordinal))
    )

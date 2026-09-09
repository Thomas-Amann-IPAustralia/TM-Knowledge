"""Concept candidates across the whole Manual — the pass the boundary used to stop.

Until 2026-09-08 this repository looked at section 43 and nothing else. ADR-0022
drew a worksheet rule around `TMA1995/s43`, ADR-0072 fixed where it stopped, and
every concept in `eval/gold/concepts.yaml` was found inside it: 86 of the 52
concepts' ~95 definition sources point at Part 29 alone. The owner withdrew the
boundary — *"I would like to completely remove the s43 barrier"* — and ADR-0081
put all 54 Parts in scope. **This module is what that costs**: a pass that reads
the whole corpus rather than one neighbourhood of it.

It finds candidates. It does not author concepts. The difference is the whole
design, and `authored/README.md` states it: *"A candidate is a proposal with a
score… An authored record is a judgement an agent committed to."* Nothing here
writes a `pref_label`, decides that two surface forms mean one thing, or types
anything. It says *the corpus defines this term, here, in these words, and the
Manual uses it in these passages* — and every one of those is a lookup.

## Why it is deterministic, and why that is two separate reasons

CLAUDE.md rule 7 asks for determinism where determinism is possible, for a
reason that predates the model budget: **a deterministic answer needs no
review**, and every judgement an agent authors is review debt somebody
eventually pays. ADR-0088 added a second reason pointing the same way — a model
call costs money and must earn itself. The reasons agree here and are still
worth keeping apart. This pass is deterministic because term extraction *is*
deterministic, not because a model call would have been expensive.

So the whole of it is regex, string equality and the refs upstream already
holds. Run it twice on the same pin and it produces the same bytes.

## The three signals

1. **`statutory_definition`** — a unit under a provision whose title begins
   *Definition*, *Definitions* or *Interpretation*, whose text opens with the
   defined term and then `means` / `has the meaning` / `includes`. The Act and
   the Regulations define their own vocabulary and say where; this reads it.
   The strongest signal in the corpus, and the only one that can support a
   `corpus_explicit` authored record.

2. **`manual_definition`** — a Manual passage that defines a term in terms: a
   quoted term followed by `means`, a *What is X?* heading, a *Definition of X*
   heading. Practice defining its own words.

3. **`manual_usage`** — the term occurs in Manual prose. Never a candidate on
   its own: it is what turns a statutory definition nobody in practice uses into
   a lower-ranked candidate than one the Manual leans on 400 times.

**The Manual is practice and the Act is law, and a candidate keeps them apart**
(CLAUDE.md rule 5). `statutory_refs` and `manual_refs` are separate fields, and
nothing here merges them into a single "sources" list. An authored record built
from a candidate inherits that separation: the Manual passages become
`definition_sources`, the provision becomes `legislative_basis`.

## What it deliberately does not do

- **It does not resolve which instrument a bare term belongs to.** `party` is
  defined six times across the Regulations, in six Parts, and this reports six
  defining refs on one candidate rather than choosing (CLAUDE.md rule 6, Q-07).
  Choosing would be resolving somebody else's ambiguity silently, and the
  multiplicity is itself a finding.
- **It does not deduplicate against meaning.** `trade mark` and `registered
  trade mark` are two candidates because the corpus defines two terms. Whether
  they are one concept with a narrower is a judgement, and judgements are
  authored with an envelope, not inferred in an extraction pass.
- **It does not exclude the procedural.** `action period` and `approved form`
  come out beside `deceptively similar`. An examination-only filter would be a
  scope judgement, and the last scope judgement in this repo cost fourteen
  sessions of blindness to four of nine role terms the expert named (Q-28).
  Rank them; do not drop them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.upstream.loader import Corpus, load_corpus
from tm_knowledge.upstream.records import Chunk, Unit

__all__ = [
    "CANDIDATES_PATH",
    "REPORT_PATH",
    "Evidence",
    "Candidate",
    "extract",
    "render",
    "write_candidates",
    "write_report",
]

CANDIDATES_PATH = REPO_ROOT / "review" / "candidates" / "concepts.yaml"
REPORT_PATH = REPO_ROOT / "data" / "derived" / "reports" / "concept-candidates.md"

#: Provision titles that introduce defined terms. Matched on the title upstream
#: recorded, at the start, so `Definition of deceptively similar` counts and
#: `Interpretation of a notice` — were there one — would too. Deliberately
#: coarse: a provision wrongly admitted produces candidates that no term regex
#: matches, and a provision wrongly excluded produces silence.
DEFINING_TITLES = ("definition", "definitions", "interpretation")

#: The defined term, at the head of a definition unit. Upstream keeps the Act's
#: own typography, which sets the term in italics and the rest in roman, but the
#: `text` field is flat — so the grammar is the only handle: a term, an optional
#: `, in relation to …` qualifier, then the verb that makes it a definition.
_STATUTORY_TERM = re.compile(
    r"""^\s*
    (?P<term>[A-Za-z][A-Za-z0-9'’\-\ ]{2,60}?)
    \s*
    (?:,\s*(?P<qualifier>[^,]{1,90}?)\s*,?\s*)?
    (?P<verb>means\b|has\ the\ same\ meaning\b|has\ the\ meaning\b
        |have\ the\ respective\ meanings\b|includes\b|has\ a\ meaning\ affected\b)
    """,
    re.VERBOSE,
)

#: A Manual passage defining a term in terms. Three shapes, kept separate so the
#: report can say which one fired — they are not equally strong evidence.
_MANUAL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "quoted",
        re.compile(
            r"""[‘'"“](?P<term>[A-Za-z][A-Za-z0-9'’\-\ ]{2,50})[’'"”]\s*
                (?:means\b|is\ defined\b|refers\ to\b)""",
            re.VERBOSE,
        ),
    ),
    (
        "term",
        re.compile(
            r"""\b(?:[Tt]he\ term|[Tt]he\ expression|[Tt]he\ word|[Tt]he\ phrase)\s+
                [‘'"“]?(?P<term>[A-Za-z][A-Za-z0-9'’\-\ ]{2,50}?)[’'"”]?\s*
                (?:means\b|is\ defined\b|refers\ to\b|is\ used\ to\b)""",
            re.VERBOSE,
        ),
    ),
    (
        "defined_in",
        re.compile(
            r"""\b(?P<term>[A-Za-z][A-Za-z0-9'’\-\ ]{2,50}?)\s+
                is\ defined\ in\ (?:section|subsection|paragraph|subregulation|regulation|reg)\b""",
            re.VERBOSE,
        ),
    ),
)

#: Leading numbering on a Manual heading — `3.`, `Part 22.4`, `5.2` — stripped
#: so the subject is what is left. Anchored and narrow: a pattern loose enough to
#: eat a leading capital turns *Introduction* into *ntroduction*, which is a
#: silent corruption rather than a visible failure.
_HEADING_NUMBER = re.compile(r"^\s*(?:Part\s*)?(?:\d+[A-Z]?[\d.]*\.?|[A-Z]?\d[\d.]*\.?)\s+")

#: Headings that describe where you are in the document rather than what the
#: document is about. A concept vocabulary built from these would hold
#: *Introduction* fifty times.
_STRUCTURAL_HEADING = re.compile(
    r"^(introduction|background|overview|relevant\ legislation|landing\ page"
    r"|annex|appendix|contents|summary|general|examination|further\ information"
    r"|glossary|references?|notes?|history|see\ also|practice|procedure"
    r"|legislation|the\ act|the\ regulations)\b",
    re.IGNORECASE | re.VERBOSE,
)

#: A definitional heading. `heading_path` is a weak structural guarantee (Q-10),
#: so a heading is evidence that the Manual treats a subject, never proof that
#: the passage beneath it defines one.
_HEADING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "what_is",
        re.compile(
            r"^\s*(?:Part\s*)?[\d.]*\s*What\s+(?:is|are)\s+(?:a|an|the)?\s*"
            r"(?P<term>[^?]{3,60})\??\s*$",
            re.IGNORECASE,
        ),
    ),
    (
        "definition_of",
        re.compile(
            r"^\s*(?:Part\s*)?[\d.]*\s*(?:Definition|Meaning)\s+of\s+(?:a|an|the)?\s*"
            r"(?P<term>.{3,60}?)\s*$",
            re.IGNORECASE,
        ),
    ),
)

#: Terms too general to be a candidate on their own. Every one is a word the
#: corpus does define and that means nothing specific to trade marks practice:
#: admitting them buries the list under `person`, `Act` and `document`. This is
#: the one judgement in the module and it is a *ranking* judgement, not a scope
#: one — the excluded terms are reported, with their refs, so that the decision
#: is visible and reversible rather than silent.
GENERIC_TERMS = frozenset(
    {
        "act", "person", "document", "party", "australia", "regulations",
        "commonwealth", "court", "federal court", "minister", "prescribed",
        "this act", "the act", "state", "territory", "month", "day", "year",
        "week", "file", "word", "company", "director", "secretary", "employee",
        "office", "officer", "written", "writing", "he", "she", "it",
    }
)

#: A heading that is only a citation — *section 41*, *Trade Marks Act 1995*,
#: *subsection 44(3)* — names an instrument or a provision, not a subject. The
#: repo already addresses provisions by ref and a concept called "section 43"
#: would be a second, worse name for `TMA1995/s43`. Dropped rather than ranked
#: low, because there is nothing for a reader to judge: `docs/IDENTIFIERS.md` §4
#: says a provision is named by its ref and by nothing else.
_CITATION_ONLY = re.compile(
    r"""^(?:the\ )?
    (?:subsection|section|sub-?paragraph|paragraph|subregulation|regulation
       |subreg|reg|schedule|sch|part|division|item|chapter|subs|ss|s)\s*
    [0-9]+[A-Za-z0-9()\ .-]*$
    |^(?:the\ )?trade\ marks?\ (?:act|regulations)\ [0-9]{4}$
    |^(?:the\ )?(?:act|regulations)\ [0-9]{4}$""",
    re.IGNORECASE | re.VERBOSE,
)

#: The Manual's house style for a heading: a subject, a dash, and the provision
#: it sits under — *Honest concurrent use - paragraph 44(3)(a)*, *Prohibited
#: signs - subsection 39(1)*, *Evidence of use - general requirements*. The
#: subject is the half worth having, so a heading in this shape offers **both**
#: forms: the whole heading, and the head on its own. Both, not the head alone —
#: dropping the qualifier would assert that it carries no meaning, and
#: *Evidence of use - general requirements* is a narrower subject than *evidence
#: of use*.
_HEADING_TAIL = re.compile(r"\s+[-–—]\s+(?P<tail>.+)$")

#: Tails that qualify a subject rather than naming a different one. A tail that
#: is neither this nor a citation is treated as part of the subject.
_QUALIFYING_TAIL = re.compile(
    r"^(general|general\ requirements?|introduction|overview|background|summary"
    r"|the\ act|act|regulations|continued|cont|part\ [0-9]+[A-Z]?)$",
    re.IGNORECASE | re.VERBOSE,
)

#: How many Manual chunks a term must appear in before the usage index bothers
#: listing them individually. Below this every use is listed; above it the
#: report gives a count and the Parts, because 1,051 refs for `trade mark` is
#: not evidence a reader can hold.
USAGE_LISTING_CAP = 12


@dataclass(frozen=True, slots=True)
class Evidence:
    """One passage, cut from the snapshot rather than retyped.

    `span` indexes the upstream `text` and `quote` is `text[start:end]` exactly —
    the harness compares them character for character and reports a mismatch as
    a defect, because a quote that will not land means somebody retyped the
    surface (ADR-0045). Nothing here builds a quote any other way.
    """

    ref: str
    span: tuple[int, int]
    content_hash: str
    quote: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "span": [self.span[0], self.span[1]],
            "content_hash": self.content_hash,
            "quote": self.quote,
        }


@dataclass(frozen=True)
class Candidate:
    """A term the corpus defines or the Manual defines, with where and how often.

    Not a concept. A concept has a preferred label, synonyms it does mean and
    near-misses it does not, and every one of those is a judgement. This carries
    only what a lookup can establish.
    """

    #: The term as the corpus writes it, case preserved.
    term: str
    #: `statutory_definition` | `manual_definition`. The strongest signal that
    #: fired; `signals` holds them all.
    signal: str
    signals: tuple[str, ...] = ()
    #: Where the Act or the Regulations define it — possibly several times, and
    #: never reduced to one (rule 6).
    statutory: tuple[Evidence, ...] = ()
    #: Where the Manual defines it in terms.
    manual: tuple[Evidence, ...] = ()
    #: Passages the Manual files under this subject in its own outline. The
    #: weakest evidence a candidate can carry, and kept in its own field so a
    #: reader can tell a defined term from a heading at a glance.
    topics: tuple[Evidence, ...] = ()
    #: Manual chunk refs whose text uses the term, in reading order.
    uses: tuple[str, ...] = ()
    #: Manual Parts the term is used in, most-using first.
    parts: tuple[str, ...] = ()
    #: Provisions cited by the chunks that use the term, most-cited first. The
    #: raw material for an authored record's `legislative_basis`, never written
    #: into one here.
    provisions: tuple[str, ...] = ()
    #: The `GC-` id of an approved or authored concept whose labels already
    #: cover this term, when one does.
    covered_by: str | None = None

    @property
    def usage_count(self) -> int:
        return len(self.uses)

    @property
    def strength(self) -> int:
        """How well evidenced the candidate is, 3 down to 1.

        3 — the legislation defines it **and** the Manual defines it in terms.
        2 — one of the two defines it.
        1 — nothing defines it; the Manual only files passages under it as a
        subject heading. A 1 can never support a `corpus_explicit` record.
        """
        if self.statutory and self.manual:
            return 3
        if self.statutory or self.manual:
            return 2
        return 1

    @property
    def rank(self) -> tuple[int, int, str]:
        """Sort key: best evidenced first, then by how much the Manual leans on
        it. Descending on the first two, so they are negated."""
        return (-self.strength, -self.usage_count, self.term.lower())

    def as_dict(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "term": self.term,
            "signal": self.signal,
            "signals": list(self.signals),
            "strength": self.strength,
            "usage_count": self.usage_count,
            "parts": list(self.parts),
        }
        if self.statutory:
            record["statutory"] = [item.as_dict() for item in self.statutory]
        if self.manual:
            record["manual"] = [item.as_dict() for item in self.manual]
        if self.topics:
            record["topics"] = [item.as_dict() for item in self.topics[:6]]
        if self.provisions:
            record["provisions"] = list(self.provisions)
        if self.uses:
            record["uses"] = list(self.uses)
        if self.covered_by:
            record["covered_by"] = self.covered_by
        return record


# ---------------------------------------------------------------------------
# Signal 1 — the statutory dictionary
# ---------------------------------------------------------------------------


def _defining_provisions(corpus: Corpus) -> tuple[str, ...]:
    """Provisions whose title says they define terms, in ref order."""
    return tuple(
        sorted(
            ref
            for ref, provision in corpus.provisions.items()
            if (provision.title or "").strip().lower().startswith(DEFINING_TITLES)
        )
    )


def _is_term_unit(unit: Unit, provision_ref: str) -> bool:
    """Does this unit carry a defined term rather than a numbered paragraph?

    Upstream slugs a defined term into the ref — `TMA1995/s6/deceptively-similar`
    — and numbers an ordinary paragraph — `TMA1995/s6/australia(a)`. The tail of
    the ref is therefore the test, and it is exact rather than heuristic.
    """
    tail = unit.ref[len(provision_ref) + 1 :] if unit.ref.startswith(provision_ref) else ""
    return bool(tail) and re.fullmatch(r"[a-z0-9-]+", tail) is not None


def _statutory_terms(corpus: Corpus) -> dict[str, list[Evidence]]:
    """Defined term (lowercased) -> where the corpus defines it.

    The span is the definition's opening — the term and the verb that makes it
    one — not the whole unit, so a reader following the ref lands on the words
    that do the defining rather than on three subparagraphs of exceptions.
    """
    found: dict[str, list[Evidence]] = {}
    for provision_ref in _defining_provisions(corpus):
        provision = corpus.provisions[provision_ref]
        for unit in provision.units:
            if not _is_term_unit(unit, provision_ref):
                continue
            text = unit.text or ""
            match = _STATUTORY_TERM.match(text)
            if match is None:
                continue
            term = match.group("term").strip()
            if len(term) < 3:
                continue
            end = match.end("verb")
            found.setdefault(term.lower(), []).append(
                Evidence(
                    ref=unit.ref,
                    span=(match.start("term"), end),
                    content_hash=unit.content_hash,
                    quote=text[match.start("term") : end],
                )
            )
    return found


# ---------------------------------------------------------------------------
# Signal 2 — the Manual defining its own words
# ---------------------------------------------------------------------------


def _manual_terms(corpus: Corpus) -> dict[str, list[tuple[str, Evidence]]]:
    """Term (lowercased) -> [(pattern name, evidence)] from Manual prose.

    A heading match spans the *chunk's* first sentence rather than the heading,
    because `heading_path` is not addressable and a span must land in text a ref
    resolves to. That is honest about what the evidence is: the passage sitting
    under a heading that announces a definition.
    """
    found: dict[str, list[tuple[str, Evidence]]] = {}
    for chunk in sorted(corpus.chunks.values(), key=lambda c: (c.page_ref, c.ordinal)):
        for name, pattern in _MANUAL_PATTERNS:
            for match in pattern.finditer(chunk.text):
                term = match.group("term").strip(" '\"‘’“”")
                if len(term) < 3:
                    continue
                start, end = match.start("term"), match.end()
                found.setdefault(term.lower(), []).append(
                    (
                        name,
                        Evidence(
                            ref=chunk.chunk_ref,
                            span=(start, end),
                            content_hash=chunk.content_hash,
                            quote=chunk.text[start:end],
                        ),
                    )
                )
        for heading in chunk.heading_path:
            for name, pattern in _HEADING_PATTERNS:
                match = pattern.match(heading.strip())
                if match is None:
                    continue
                term = match.group("term").strip(" '\"‘’“”.")
                if len(term) < 3 or not chunk.text.strip():
                    continue
                end = min(len(chunk.text), _first_sentence_end(chunk.text))
                found.setdefault(term.lower(), []).append(
                    (
                        f"heading_{name}",
                        Evidence(
                            ref=chunk.chunk_ref,
                            span=(0, end),
                            content_hash=chunk.content_hash,
                            quote=chunk.text[0:end],
                        ),
                    )
                )
    return found


def _manual_topics(corpus: Corpus) -> dict[str, list[Evidence]]:
    """Subject (lowercased) -> the passages the Manual files under it.

    **The weakest signal here, and the one without which the vocabulary stays
    statutory.** The practice concepts an examiner actually reasons with —
    *inherent adaptation to distinguish*, *honest concurrent use*, *prior use*,
    *use contrary to law* — are almost never defined by a sentence beginning
    "X means". They are named by the Manual's own outline: a Part, a numbered
    section within it, a heading. That outline is the closest thing the corpus
    has to a statement of what practice is about.

    So a topic is a heading the Manual wrote, with its numbering stripped and
    the purely structural ones removed. It is evidence that the Manual treats a
    subject at length. It is **not** evidence that the subject is a concept, and
    it can never support a `corpus_explicit` record: the corpus does not say
    "honest concurrent use is a legal test", it says what an examiner must be
    satisfied of under paragraph 44(3)(a) and files it under that heading. An
    authored record built from a topic is `corpus_inferred`, and the inference
    is the agent's.

    Page `nav_title` and chunk `heading_path` are both read. The nav tree is the
    Manual's own answer about where a page sits (Q-09), and the heading path
    reaches a level below it.
    """
    found: dict[str, list[Evidence]] = {}

    def offer(subject: str, chunk: Chunk) -> None:
        cleaned = _HEADING_NUMBER.sub("", subject).strip(" .-–—:")
        if len(cleaned) < 6 or len(cleaned) > 80:
            return
        if _STRUCTURAL_HEADING.match(cleaned) or _CITATION_ONLY.match(cleaned):
            return
        if not chunk.text.strip():
            return
        end = _first_sentence_end(chunk.text)
        entries = found.setdefault(cleaned.lower(), [])
        if any(item.ref == chunk.chunk_ref for item in entries):
            return
        entries.append(
            Evidence(
                ref=chunk.chunk_ref,
                span=(0, end),
                content_hash=chunk.content_hash,
                quote=chunk.text[0:end],
            )
        )

    def offer_both(subject: str, chunk: Chunk) -> None:
        """The heading, and the subject at the head of it where there is one."""
        offer(subject, chunk)
        cleaned = _HEADING_NUMBER.sub("", subject).strip(" .-–—:")
        match = _HEADING_TAIL.search(cleaned)
        if match is None:
            return
        tail = match.group("tail").strip()
        if _CITATION_ONLY.match(tail) or _QUALIFYING_TAIL.match(tail):
            offer(cleaned[: match.start()].strip(), chunk)

    for chunk in sorted(corpus.chunks.values(), key=lambda c: (c.page_ref, c.ordinal)):
        page = corpus.pages.get(chunk.page_ref)
        if page is not None:
            offer_both(page.nav_title, chunk)
        for heading in chunk.heading_path:
            offer_both(heading, chunk)
    return found


def _first_sentence_end(text: str, limit: int = 400) -> int:
    """Where the first sentence ends, or `limit`, whichever comes first.

    Crude on purpose. It bounds a quote; it is not a sentence splitter, and
    nothing downstream treats it as one.
    """
    match = re.search(r"[.:;]\s", text[:limit])
    return match.end() - 1 if match else min(len(text), limit)


# ---------------------------------------------------------------------------
# Signal 3 — what the Manual actually leans on
# ---------------------------------------------------------------------------


def _usage_index(corpus: Corpus, terms: Iterable[str]) -> dict[str, list[Chunk]]:
    """Term -> the Manual chunks whose text uses it, in reading order.

    Whole-word, case-insensitive, on the term as written. Not stemmed and not
    lemmatised: `use` and `used` are different strings and pretending otherwise
    is a language judgement this pass has no business making. The consequence is
    an undercount, which is the safe direction — a term the Manual uses in an
    inflected form only comes out ranked low rather than falsely high.
    """
    patterns = {
        term: re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        for term in terms
    }
    index: dict[str, list[Chunk]] = {term: [] for term in patterns}
    for chunk in sorted(corpus.chunks.values(), key=lambda c: (c.page_ref, c.ordinal)):
        text = chunk.text
        for term, pattern in patterns.items():
            if pattern.search(text):
                index[term].append(chunk)
    return index


def _existing_labels(concepts: Iterable[dict[str, Any]]) -> dict[str, str]:
    """Every surface form an existing concept already claims -> its id.

    `pref_label` and `alt_labels` only. **`not_labels` are deliberately not
    here**: a near-miss is a form the concept explicitly does *not* mean, so a
    candidate matching one is not covered by that concept — it may well be the
    concept the near-miss was pointing at.
    """
    claimed: dict[str, str] = {}
    for concept in concepts:
        identifier = str(concept.get("id", ""))
        labels = [concept.get("pref_label"), *(concept.get("alt_labels") or ())]
        for label in labels:
            if isinstance(label, str) and label.strip():
                claimed.setdefault(label.strip().lower(), identifier)
    return claimed


# ---------------------------------------------------------------------------
# The pass
# ---------------------------------------------------------------------------


def extract(
    corpus: Corpus | None = None,
    *,
    known: Iterable[dict[str, Any]] = (),
) -> tuple[Candidate, ...]:
    """Every candidate the corpus supports, ranked. Deterministic on the pin.

    `known` is the concepts already held — approved and authored both — so a
    candidate can say which record already claims its term. It marks; it never
    filters. A term an existing concept covers is still worth seeing: it is how
    a reader notices that one concept has quietly grown four meanings.
    """
    corpus = corpus or load_corpus()
    statutory = _statutory_terms(corpus)
    manual = _manual_terms(corpus)
    topics = _manual_topics(corpus)

    terms = {
        term
        for term in (*statutory, *manual, *topics)
        if term not in GENERIC_TERMS and len(term) >= 3
    }
    usage = _usage_index(corpus, terms)
    claimed = _existing_labels(known)

    candidates: list[Candidate] = []
    for term in sorted(terms):
        statutory_evidence = tuple(statutory.get(term, ()))
        manual_pairs = tuple(manual.get(term, ()))
        manual_evidence = tuple(evidence for _, evidence in manual_pairs)
        topic_evidence = tuple(topics.get(term, ()))
        chunks = usage.get(term, [])
        if not (chunks or statutory_evidence or manual_evidence or topic_evidence):
            # Nothing defines it, no heading files anything under it, and the
            # Manual never writes the words. That is a regex artefact.
            #
            # Usage alone is deliberately *not* required. A heading is evidence
            # in its own right: *Honest concurrent use — paragraph 44(3)(a)* is
            # a subject the Manual devotes a page to, and the exact heading
            # string never appears in the prose beneath it. Requiring the term
            # to occur literally dropped precisely the compound practice
            # concepts the boundary removal exists to reach.
            continue

        part_counts: dict[str, int] = {}
        provision_counts: dict[str, int] = {}
        for chunk in chunks:
            part_counts[chunk.part_id] = part_counts.get(chunk.part_id, 0) + 1
            for edge in chunk.provisions:
                provision_counts[edge.id] = provision_counts.get(edge.id, 0) + 1

        signals = tuple(
            sorted(
                {
                    *(("statutory_definition",) if statutory_evidence else ()),
                    *(f"manual_{name}" for name, _ in manual_pairs),
                    *(("manual_topic",) if topic_evidence else ()),
                }
            )
        )
        # Display term: the surface the corpus itself used, preferring the
        # statutory spelling because the Act fixes its own capitalisation.
        display = term
        if statutory_evidence:
            display = statutory_evidence[0].quote.split(",")[0].strip()
            display = re.sub(
                r"\s+(means|has the same meaning|has the meaning|includes|"
                r"have the respective meanings|has a meaning affected)$",
                "",
                display,
            ).strip()

        candidates.append(
            Candidate(
                term=display or term,
                signal=(
                    "statutory_definition"
                    if statutory_evidence
                    else "manual_definition"
                    if manual_evidence
                    else "manual_topic"
                ),
                signals=signals,
                statutory=statutory_evidence,
                manual=manual_evidence,
                topics=topic_evidence,
                uses=tuple(chunk.chunk_ref for chunk in chunks),
                parts=tuple(
                    part for part, _ in sorted(part_counts.items(), key=lambda kv: (-kv[1], kv[0]))
                ),
                provisions=tuple(
                    ref
                    for ref, _ in sorted(
                        provision_counts.items(), key=lambda kv: (-kv[1], kv[0])
                    )
                )[:12],
                covered_by=claimed.get(term),
            )
        )

    return tuple(sorted(candidates, key=lambda candidate: candidate.rank))


# ---------------------------------------------------------------------------
# Artefacts
# ---------------------------------------------------------------------------


def write_candidates(
    candidates: tuple[Candidate, ...], path: Path | None = None, *, generated: str | None = None
) -> Path:
    """The candidates, as YAML, for the authoring pass to read.

    `review/candidates/` and not `authored/`: nothing here has an authoring
    envelope, because nothing here is a judgement anybody committed to
    (ADR-0083 consequence 3).
    """
    path = path or CANDIDATES_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = generated or date.today().isoformat()
    header = (
        "# Concept candidates, extracted deterministically from the whole corpus.\n"
        "#\n"
        "# NOT authored records and NOT concepts. No authoring envelope, no\n"
        "# pref_label, no judgement of any kind: every field below is a lookup\n"
        "# against the pinned snapshot (tm_knowledge.stage0.concepts).\n"
        "#\n"
        f"# Generated {stamp} by `tmk-concepts --write`. Do not hand-edit —\n"
        "# a correction belongs in an authored record, which is where judgement\n"
        "# is allowed to live.\n"
    )
    body = yaml.safe_dump(
        [candidate.as_dict() for candidate in candidates],
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )
    path.write_text(header + body, encoding="utf-8")
    return path


def render(
    candidates: tuple[Candidate, ...],
    corpus: Corpus | None = None,
    *,
    generated: str | None = None,
) -> str:
    """The candidate pack — what the corpus defines, and where it is used."""
    corpus = corpus or load_corpus()
    stamp = generated or date.today().isoformat()
    statutory = [c for c in candidates if c.statutory]
    defined = [c for c in candidates if c.statutory or c.manual]
    topic_only = [c for c in candidates if c.strength == 1]
    covered = [c for c in candidates if c.covered_by]
    parts_touched = sorted({part for c in candidates for part in c.parts})
    classification_only = [
        c for c in topic_only if c.parts and set(c.parts) <= {"Part14"}
    ]

    parts: list[str] = [
        "<!-- Generated by tm_knowledge.stage0.concepts. Do not hand-edit. -->",
        "",
        "# Concept candidates — the whole Manual, not one section of it",
        "",
        f"**Generated {stamp}** by `tmk-concepts --write` against the pinned snapshot "
        f"`{corpus.pin.commit[:12]}`.",
        "",
        "## What this is",
        "",
        "The owner withdrew the section 43 boundary on 2026-09-08: *“I would like to "
        "completely remove the s43 barrier.”* Every concept this repository holds was "
        "found inside that boundary — 86 of the 52 approved concepts' ~95 definition "
        "sources point at Part 29 alone. This is the first pass that reads the other 53 "
        "Parts.",
        "",
        "**Nothing here is a concept and nothing here is authored.** A candidate is a "
        "term the corpus defines, with the passages that define it and the passages that "
        "use it. Every field is a lookup; no field is a judgement. Turning a candidate "
        "into a concept — a preferred label, the synonyms it does mean, the near-misses "
        "it does not — is authorship, it carries an envelope, and it happens in "
        "`authored/concepts.yaml`.",
        "",
        "| | count |",
        "|---|---|",
        f"| Candidates | **{len(candidates)}** |",
        f"| — defined by the Act or the Regulations | {len(statutory)} |",
        f"| — defined by the corpus in terms, one way or the other | {len(defined)} |",
        f"| — named only by a Manual heading | {len(topic_only)} |",
        f"| — a term an existing concept already claims | {len(covered)} |",
        f"| Manual Parts they are used in | {len(parts_touched)} of 54 |",
        f"| Corpus read | {len(corpus.chunks)} chunks · {len(corpus.provisions)} "
        f"provisions · {len(corpus.units)} units |",
        "",
        "## How well evidenced each one is",
        "",
        "**Strength is not importance.** It says how much of the candidate a lookup "
        "established, and nothing about whether the idea matters to an examiner.",
        "",
        "| strength | means | count | what an authored record from it may claim |",
        "|---|---|---|---|",
        "| **3** | the legislation defines it *and* the Manual defines it in terms | "
        f"{sum(1 for c in candidates if c.strength == 3)} | `corpus_explicit` |",
        "| **2** | one of the two defines it | "
        f"{sum(1 for c in candidates if c.strength == 2)} | `corpus_explicit` |",
        "| **1** | nothing defines it; the Manual files passages under it as a subject | "
        f"{len(topic_only)} | `corpus_inferred` at best — **never** `corpus_explicit` |",
        "",
        f"**{len(classification_only)} of the {len(topic_only)} strength-1 candidates "
        "occur in Part 14 and nowhere else.** Part 14 is the goods and services "
        "classification, 743 of the corpus's 2,460 chunks, and its headings are class "
        "headings — *packaging*, *materials*, *research*. They are candidates because "
        "the rule that finds a heading cannot tell a class heading from a legal one, "
        "and they are reported rather than filtered because the last scope filter this "
        "repository applied hid four of nine role terms an expert had named (Q-28). "
        "Rank them low; do not pretend the rule excluded them.",
        "",
        "## How to read a row",
        "",
        "**`statutory`** is where the Act or the Regulations define the term, quoted "
        "from the snapshot. Several entries mean the corpus defines the term several "
        "times, in different Parts and for different purposes — `party` is defined six "
        "times. That multiplicity is reported and **not resolved**: upstream refuses to "
        "choose between instruments on purpose and this pass inherits the refusal "
        "(CLAUDE.md rule 6).",
        "",
        "**`manual`** is where the Manual defines it in terms — a quoted term followed "
        "by *means*, or a passage under a *What is …?* heading.",
        "",
        "**`uses`** is every Manual passage whose text carries the term, whole-word and "
        "case-insensitive. Not stemmed: *use* and *used* are different strings here, so "
        "the count runs low rather than high.",
        "",
        "**`covered_by`** names a concept whose `pref_label` or `alt_labels` already "
        "claim this term. Near-misses (`not_labels`) are deliberately excluded from that "
        "test — a concept that says a term is *not* it is not covering it.",
        "",
    ]

    if covered:
        parts += [
            "## Terms an existing concept already claims",
            "",
            f"{len(covered)} of the {len(candidates)} candidates match a label on a "
            "concept this repository already holds. They are listed rather than dropped: "
            "a term claimed by one concept and defined separately by the Act is worth a "
            "second look, because it may be two ideas sharing a word.",
            "",
            "| term | already claimed by | defined at |",
            "|---|---|---|",
        ]
        for candidate in covered:
            where = ", ".join(f"`{item.ref}`" for item in candidate.statutory[:2]) or "—"
            parts.append(f"| {candidate.term} | `{candidate.covered_by}` | {where} |")
        parts.append("")

    parts += [
        "## The candidates the corpus defines",
        "",
        f"The **{len(defined)}** candidates something in the corpus actually defines, "
        "ranked by strength and then by how many Manual passages use the term. The "
        "ranking is arithmetic, not importance — a procedural term the Manual repeats "
        "constantly outranks a substantive one it states once, and that is a property of "
        "the counter rather than of the law.",
        "",
    ]
    for candidate in defined:
        parts += _candidate_block(candidate)

    parts += [
        "## The candidates only a heading names",
        "",
        f"The remaining **{len(topic_only)}**. The Manual files passages under each of "
        "these and defines none of them, so a record authored from one is the agent's "
        "reading of a subject the Manual treats — `corpus_inferred`, never "
        "`corpus_explicit`. Listed in one line each: the term, how much of the Manual "
        "uses it, and the first passage filed under it.",
        "",
        "| term | uses | Parts | first passage |",
        "|---|---|---|---|",
    ]
    for candidate in topic_only:
        first = candidate.topics[0].ref if candidate.topics else "—"
        shown = ", ".join(candidate.parts[:3]) or "—"
        if len(candidate.parts) > 3:
            shown += f" +{len(candidate.parts) - 3}"
        claimed = f" *(claimed by `{candidate.covered_by}`)*" if candidate.covered_by else ""
        parts.append(
            f"| {candidate.term}{claimed} | {candidate.usage_count} | {shown} | "
            f"`{first}` |"
        )
    parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def _candidate_block(candidate: Candidate) -> list[str]:
    """One well-evidenced candidate, laid out with its passages."""
    heading = f"### {candidate.term}"
    if candidate.covered_by:
        heading += f"  *(already claimed by `{candidate.covered_by}`)*"
    block: list[str] = [
        heading,
        "",
        f"*Strength {candidate.strength}* · *signals:* "
        f"{', '.join(f'`{s}`' for s in candidate.signals)} · "
        f"*used in* **{candidate.usage_count}** Manual passages across "
        f"{len(candidate.parts)} Parts"
        + (f" ({', '.join(candidate.parts[:6])})" if candidate.parts else ""),
        "",
    ]
    if candidate.statutory:
        block += ["*Defined by the legislation:*", ""]
        for item in candidate.statutory:
            block.append(f"- **`{item.ref}`** — “{item.quote}…”")
        block.append("")
    if candidate.manual:
        block += ["*Defined by the Manual:*", ""]
        for item in candidate.manual[:4]:
            quote = item.quote if len(item.quote) <= 300 else item.quote[:300] + " …"
            block.append(f"- **`{item.ref}`** — “{quote}”")
        if len(candidate.manual) > 4:
            block.append(f"- … and {len(candidate.manual) - 4} more")
        block.append("")
    if candidate.topics:
        block.append(
            "*Also filed under this heading at:* "
            + ", ".join(f"`{item.ref}`" for item in candidate.topics[:6])
        )
        block.append("")
    if candidate.provisions:
        block.append(
            "*Provisions cited by the passages that use it:* "
            + ", ".join(f"`{ref}`" for ref in candidate.provisions[:8])
        )
        block.append("")
    if candidate.uses:
        if candidate.usage_count <= USAGE_LISTING_CAP:
            block.append("*Used in:* " + ", ".join(f"`{ref}`" for ref in candidate.uses))
        else:
            block.append(
                f"*Used in {candidate.usage_count} passages* — first "
                f"{USAGE_LISTING_CAP}: "
                + ", ".join(f"`{ref}`" for ref in candidate.uses[:USAGE_LISTING_CAP])
            )
        block.append("")
    return block


def write_report(
    candidates: tuple[Candidate, ...],
    path: Path | None = None,
    *,
    corpus: Corpus | None = None,
    generated: str | None = None,
) -> Path:
    path = path or REPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(candidates, corpus, generated=generated), encoding="utf-8")
    return path

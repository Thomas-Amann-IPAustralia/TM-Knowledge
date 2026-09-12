"""Relationships across the whole Manual and both instruments — the edges the
graph did not have.

Until today `eval/gold/relationships.yaml` held 35 records and
`authored/relationships.yaml` did not exist, so the knowledge graph held 130
concepts and **0 authored edges between them**. S021 drew the consequence: the
graph is in 44 separate pieces, one holding 86 of 254 nodes and almost every
other holding a single concept beside the provisions it cites. A vocabulary,
not a knowledge graph.

It is also where the section 43 boundary survived longest. All 37 source refs
in the signed relationship set point at `TMM/Part29`, so the 14 predicates in
`ontology/draft/relations.ttl` — the **closed list extraction may draw from** —
are the predicates one Part of 54 happened to need. The concept layer stopped
being a section 43 layer in S018; the relational layer did not.

This module is the pass that reads the whole corpus for edges, the way
`stage0.concepts` reads it for terms.

## Deterministic, and the reasons are still two

CLAUDE.md rule 7 wants determinism where determinism is possible, for a reason
that predates the model budget: a deterministic answer needs no review, and
every judgement an agent authors is review debt somebody eventually pays.
ADR-0088 added a second reason pointing the same way. Here they agree and are
still worth keeping apart — this pass is regex, string equality and the refs
upstream already holds, not because a model call would have been expensive but
because sentence-level relation extraction over a 14,211-sentence corpus with a
361-label lexicon *is* a lookup. Run it twice on the same pin and it produces
the same bytes.

## The seven patterns, and what each will and will not claim

Every pattern fixes **where the subject and the object sit in the sentence**
before it fires. That is the whole of the discipline: a pass that took the
n-choose-2 of every concept label co-occurring in a sentence would produce
5,103 sentences' worth of plausible-looking edges nobody could check, which is
the laundering CLAUDE.md rule 1 now prohibits by name.

| predicate | subject | object | basis |
|---|---|---|---|
| `isDefinedIn` | the defined concept | the provision or unit that defines it | `corpus_explicit` |
| `hasStatutoryBasis` | a concept named in the sentence | the provision the Manual's own authors linked | `corpus_explicit` |
| `mayGiveRiseTo` | the concept nearest before the ground phrase | the section cited, else the ground concept | `corpus_inferred` |
| `doesNotGiveRiseTo` | as above, negated | as above | `corpus_inferred` |
| `isOvercomeBy` | the concept before *overcome* | the concept after *overcome by* | `corpus_inferred` |
| `requiresElement` | the concept before *requires* | the concept after it | `corpus_inferred` |
| `isPerformedBy` | the step concept in the sentence | the role concept the modal attaches to | `corpus_inferred` |

Four of the seven are new predicates. `relations.ttl` is a closed list and its
README says a predicate is added by having an expert approve a relationship
that uses one — a rule written when rule 1 forbade an agent to author a
relationship at all. ADR-0079 changed that, and the whole-Manual corpus does
not fit a 14-term dictionary drawn from one Part: nothing in it says *this term
is defined by that section*, *this act is performed by that office*, or *this
practice rests on that provision*. So the new terms are authored, and
`relations.ttl` keeps them visibly apart as `tmk:AuthoredRelation` rather than
`tmk:ApprovedRelation` (ADR-0109).

## Modality: `must` only, and the rest stays null

The record schema says modality is *"never inferred from the sentence's
grammar, because whether a 'may' is possibility or permission is a legal
reading"*, and `GR-0001`'s own note records a reviewer reading `mandatory` as
obligation with nothing in the grammar to support it.

ADR-0079 permits an agent to author a modality reading. This pass takes the
narrowest version of that permission it can: **`must` in the matched clause
records `modality: must`, and every other modal records null.** `must` is
unambiguously deontic in Australian legislative drafting; `may` is the word the
guide singles out as ambiguous, and `should` in the Manual is practice
direction whose force is exactly the question CQ-0024 exists to ask. A pass
that mapped all three would be reading grammar and presenting it as law.

## Two collisions it will meet and must not resolve

**A label belonging to two concepts.** Ten authored concepts reuse a signed
concept's preferred label (ADR-0101) — *ground for rejection* is `GC-0006`
signed and `GC-0053` authored, *Registrar* is `GC-0046` and `GC-0115`. Where a
label resolves to more than one concept this pass **takes the signed one**,
because ADR-0080 consequence 2 runs that way, and names the collision in
`expert_should_check` on every record it affects. It does not retire either
record and it does not merge them.

**A term defined more than once.** *notice of opposition* is defined in six
places across the Regulations. Every one becomes its own `isDefinedIn` record.
Collapsing them to a "primary" definition would be resolving an ambiguity
upstream deliberately preserved (CLAUDE.md rule 6, Q-07), and the multiplicity
is itself the finding.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Iterator

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.stage0 import goldset
from tm_knowledge.authored import store as authored_store
from tm_knowledge.upstream.loader import Corpus, load_corpus
from tm_knowledge.upstream.records import Chunk, Provision, Unit

__all__ = [
    "AUTHORED_PATH",
    "REPORT_PATH",
    "NEW_PREDICATES",
    "APPROVED_PREDICATES",
    "Lexicon",
    "Finding",
    "extract",
    "render_records",
    "write_records",
    "write_report",
]

AUTHORED_PATH = REPO_ROOT / "authored" / "relationships.yaml"
REPORT_PATH = REPO_ROOT / "data" / "derived" / "reports" / "relationships.md"

#: The model that wrote these records. Stamped per record and never read from
#: `config.DEFAULT_AUTHORING_MODEL`: that constant names what an API-backed run
#: should use, and this pass is not one (ADR-0094).
AUTHORED_BY = "claude-opus-5"

#: Predicates already on the closed list, because an expert used them
#: (`eval/gold/relationships.yaml`). Restated here only so the report can say
#: which of the terms this pass emits were already approved vocabulary and
#: which are new — the list itself is derived, in `ontology.relations`.
APPROVED_PREDICATES = frozenset(
    {
        "allocatesTo",
        "appliesTo",
        "citesAuthorityFor",
        "constrainsExaminerTo",
        "dependsOnExternalSource",
        "doesNotGiveRiseTo",
        "excludesBasis",
        "extendsTo",
        "interprets",
        "isOvercomeBy",
        "mayGiveRiseTo",
        "qualifies",
        "requiresElement",
        "statesThresholdFor",
    }
)

#: Predicates this pass adds, with the gap in the approved dictionary each one
#: fills. Every one is authored vocabulary: no expert has used it, and
#: `relations.ttl` types them `tmk:AuthoredRelation` (ADR-0109).
NEW_PREDICATES: dict[str, str] = {
    "isDefinedIn": (
        "A concept and the provision or unit of an instrument that defines it. "
        "The approved dictionary has no term for this at all, because the "
        "section 43 material it came from cites the Act and does not define "
        "against it. It is the backbone of the legislation half of the corpus: "
        "23 definition provisions across the Act and the Regulations."
    ),
    "hasStatutoryBasis": (
        "A concept and the provision the Manual's own authors hyperlinked "
        "beside it. Distinct from isDefinedIn, which is the instrument "
        "defining its own word, and from appliesTo, which runs provision to "
        "concept and asserts application rather than derivation. The edge "
        "rests on an `href` the Manual carries — the strongest provenance in "
        "the corpus (CLAUDE.md rule 3)."
    ),
    "isPerformedBy": (
        "An act, proceeding or event and the office that performs it. The "
        "approved dictionary holds constrainsExaminerTo, which names one role "
        "inside the predicate and so cannot express the same relation for the "
        "Registrar, an applicant or an opponent. ADR-0073 made a role "
        "something a statement can be about and nothing has been able to say "
        "anything about one since."
    ),
    "mustOccurWithin": (
        "A procedural step and the provision that fixes the period it must "
        "happen in. 97 sentences in the Manual state a period; not one of them "
        "is expressible in the approved dictionary."
    ),
}

#: Labels too short or too polysemous to match on. Every one of these is a real
#: concept label; the exclusion is about the *matcher*, not the concept. `use`
#: and `mark` appear in almost every sentence in the corpus as ordinary words,
#: and a matcher that fires on them produces edges about grammar.
AMBIGUOUS_LABELS = frozenset(
    {
        "gi",
        "inn",
        "stem",
        "tld",
        "fame",
        "mark",
        "sign",
        "use",
        "ctm",
        "irda",
        "decision",
        "limitations",
        "goods",
        "services",
        "means",
        "notice",
        "period",
        "class",
        "owner",
        "party",
        "person",
    }
)

#: Sentence boundary.
#:
#: The first version required a capital after the punctuation, on the theory
#: that under-splitting is the safer failure. It is not. Chunks in this corpus
#: carry flattened lists and tables — an annex of deferment grounds arrives as
#: one 900-character run — and a window that long makes "the nearest concept
#: before the verb" meaningless: every positional pattern in this module then
#: reads a subject out of a different list item. Every bad edge in the first
#: sample traced to it.
#:
#: So: split after terminal punctuation followed by whitespace, and on a line
#: break. A legislative reference carries no space inside it (`reg 4.4(7)`,
#: `s 44`, `17A.48G(1)`), so the numbered forms this corpus is full of survive.
_SENTENCE = re.compile(r"(?<=[.;:!?])\s+|\n+")

#: Longest window a positional pattern will read a subject and an object out
#: of. Past this the split has failed — the text is a flattened table or a
#: bulleted list — and "nearest preceding concept" stops meaning anything.
MAX_WINDOW = 400

#: How far a subject or object may sit from the verb that relates them. A
#: clause, roughly. Without it the pattern reaches back across a semicolon-free
#: sentence and picks up the last concept mentioned rather than the one the
#: clause is about.
MAX_GAP = 120

_GROUND = re.compile(r"\bground(?:s)? for rejection\b", re.I)
_GROUND_NEGATED = re.compile(
    r"\b(?:is not|are not|was not|were not|not|no)\s+(?:a\s+|an\s+|the\s+)?ground(?:s)? for rejection\b",
    re.I,
)

#: A verb that makes the sentence *about a ground arising*, rather than a
#: sentence that mentions the phrase while discussing something else. Without
#: it the pattern fires on "although the applicant may make submissions…",
#: which is a sentence about submissions.
_GROUND_VERB = re.compile(
    r"\b(?:rais(?:e|es|ed|ing)|aris(?:e|es|en|ing)|exist(?:s|ed)?|appl(?:y|ies|ied)|"
    r"give(?:s|n)? rise|attract(?:s|ed)?|warrant(?:s|ed)?|trigger(?:s|ed)?|"
    r"withdraw(?:n|s)?|maintain(?:ed|s)?|overcome)\b",
    re.I,
)
#: Passive only — `«ground» may be overcome by «thing»`. The active form
#: (`an applicant may attempt to overcome a ground`) puts the *actor* where the
#: passive puts the thing overcome, so a pattern accepting both inverts the
#: edge on every active sentence it meets. Measured: of 21 edges the loose
#: version produced, the four sampled included two inversions.
_OVERCOME_BY = re.compile(r"\b(?:be|been|being)\s+overcome\s+by\b", re.I)

#: `requires` and `it is necessary`, and deliberately **not** `is required to`.
#: `the applicant is required to provide…` is an obligation on an office, which
#: is what isPerformedBy is for; read as a requiresElement it makes the office
#: the thing that has elements.
_REQUIRES = re.compile(r"\b(?:requires|it is necessary (?:to|for|that))\b", re.I)
_PERIOD = re.compile(
    r"\bwithin\s+(?:the\s+|a\s+)?(?:period of\s+)?(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|twelve|fifteen|eighteen|twenty)\s+"
    r"(?:month|months|day|days|week|weeks|year|years)\b",
    re.I,
)
_MUST = re.compile(r"\bmust\b", re.I)

#: `will be notified`, `must be given`, `may be advised` — the office named
#: is the act's object, not its subject.
_PASSIVE = re.compile(r"\b(?:be|been|being)\s+\w+(?:ed|en|n)\b", re.I)

#: The words that make a citation a *basis* rather than a mention.
#:
#: This is the whole of `hasStatutoryBasis`'s precision. A concept label sitting
#: near a hyperlink is evidence the Manual discusses both in one sentence and
#: nothing more — the chunk-to-provision citation already records that, with
#: upstream's trust metadata on it, and re-asserting it as a relationship would
#: add an edge that claims more than the citation it was built from. What these
#: phrases add is the Manual saying the concept *operates under* the provision.
#:
#: Measured on the loose version: 717 edges, of which a sample showed
#: parenthetical cross-references ("…involving the registered trade mark
#: (Paragraph 84A(3)(b))") being recorded as statutory bases.
_BASIS_PHRASE = re.compile(
    r"(?:\bunder|\bpursuant to|\bin accordance with|\bfor the purposes of|\bby virtue of|"
    r"\bprovided (?:for )?(?:in|by)|\bset out in|\brequired by|\bprescribed by|\bimposed by|"
    r"\bconferred by|\bgoverned by)\s*$",
    re.I,
)

#: A unit whose text opens by defining its own term.
_UNIT_DEFINES = re.compile(
    r"^\s*[«\"“‘']?(?P<term>[a-zA-Z][a-zA-Z \-/'()]{2,60}?)[»\"”’']?\s*"
    r"(?P<verb>means\b|includes\b|has the (?:same )?meaning\b)"
)

#: `Definition of X`, `Definitions of X and Y`.
_PROVISION_DEFINES = re.compile(r"^\s*Definitions?\s+of\s+(?P<terms>.+?)\s*$", re.I)

#: A provision that holds definitions at all. Its units are the place a
#: defined term lives, and the title is how the instrument says so.
_DEFINITION_PROVISION = re.compile(r"^\s*(?:Definitions?|Interpretation|Dictionary)\b", re.I)


def _norm(label: str) -> str:
    """Case-folded, whitespace-collapsed. The only normalisation applied to a
    label anywhere in this module, so a match is reproducible."""
    return re.sub(r"\s+", " ", label).strip().casefold()


@dataclass(frozen=True)
class Lexicon:
    """Every concept label in the project, and the concept it names.

    Built over **both** stores, for ADR-0091's reason: after ADR-0079 the
    vocabulary lives in two directories, and a pass that read only the signed
    one would miss 78 of the project's 130 concepts — which is to say, all the
    concepts outside section 43.
    """

    #: normalised label -> concept id. Signed wins a collision (see below).
    by_label: dict[str, str]
    #: concept id -> preferred label, for report text only.
    labels: dict[str, str]
    #: concept id -> typing group, where one exists.
    groups: dict[str, str]
    #: normalised label -> every concept id carrying it, signed and authored.
    collisions: dict[str, tuple[str, ...]]
    #: concept ids a named expert signed.
    signed: frozenset[str]

    @property
    def matcher(self) -> re.Pattern[str]:
        terms = sorted((re.escape(label) for label in self.by_label), key=len, reverse=True)
        return re.compile(r"(?<![A-Za-z])(" + "|".join(terms) + r")(?![A-Za-z])", re.I)

    def concept_at(self, surface: str) -> str | None:
        return self.by_label.get(_norm(surface))

    def collision_note(self, *concept_ids: str) -> str | None:
        """The disclosure owed when a record's subject or object came from a
        label two concepts carry. Never resolved here — named."""
        notes = []
        for label, ids in sorted(self.collisions.items()):
            if any(cid in ids for cid in concept_ids) and len(ids) > 1:
                chosen = self.by_label[label]
                other = [i for i in ids if i != chosen]
                notes.append(
                    f"the label {label!r} is carried by {', '.join(ids)}; this record "
                    f"uses the signed record {chosen} and does not displace {', '.join(other)}"
                )
        return "; ".join(notes) or None


def build_lexicon(
    gold: goldset.GoldSet | None = None, authored: authored_store.AuthoredSet | None = None
) -> Lexicon:
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load()

    by_label: dict[str, str] = {}
    labels: dict[str, str] = {}
    collisions: dict[str, list[str]] = defaultdict(list)
    signed = {record["id"] for record in gold["gold_concept"]}

    # Signed first, so a collision resolves to the signed record without the
    # order of the two loops being load-bearing anywhere else.
    for records in (gold["gold_concept"], authored["gold_concept"]):
        for record in records:
            labels[record["id"]] = record["pref_label"]
            for surface in [record["pref_label"], *(record.get("alt_labels") or [])]:
                key = _norm(surface)
                if len(key) < 5 or key in AMBIGUOUS_LABELS:
                    continue
                collisions[key].append(record["id"])
                by_label.setdefault(key, record["id"])

    groups: dict[str, str] = {}
    for records in (gold["concept_type"], authored["concept_type"]):
        for record in records:
            groups[record["concept"]] = record["type"]

    return Lexicon(
        by_label=by_label,
        labels=labels,
        groups=groups,
        collisions={k: tuple(v) for k, v in collisions.items() if len(v) > 1},
        signed=frozenset(signed),
    )


@dataclass(frozen=True)
class Finding:
    """One edge the corpus states, with the exact words that state it.

    Not yet a record: `render_records` puts the envelope on it. Keeping the two
    apart is the same split `stage0.concepts` keeps between a candidate and an
    authored concept — a finding is what the matcher saw, a record is what an
    agent committed to.
    """

    subject: str
    predicate: str
    object: str
    source_ref: str
    supporting_text: str
    span: tuple[int, int]
    source_content_hash: str
    basis: str
    signal: str
    modality: str | None
    reasoning: str
    alternatives: tuple[str, ...] = ()
    expert_should_check: str | None = None
    confidence: float = 0.6

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.subject, self.predicate, self.object)


def _sentences(text: str) -> Iterator[tuple[str, int, int]]:
    """Sentences with their offsets into `text`, so a span is exact.

    Offsets are found by scanning forward rather than by summing lengths: the
    split discards the whitespace between sentences and reconstructing it by
    arithmetic is how a span drifts by one character and stops locating.
    """
    position = 0
    for sentence in _SENTENCE.split(text):
        if not sentence:
            continue
        start = text.find(sentence, position)
        if start < 0:  # pragma: no cover - split cannot produce a foreign string
            continue
        position = start + len(sentence)
        # A window this long is a flattened list or table, not a sentence. See
        # MAX_WINDOW — reading a subject and an object out of one produces an
        # edge whose two halves came from different list items.
        if len(sentence) > MAX_WINDOW:
            continue
        yield sentence, start, position


@dataclass(frozen=True)
class _Hit:
    concept: str
    start: int
    end: int


def _concept_hits(lexicon: Lexicon, matcher: re.Pattern[str], sentence: str) -> tuple[_Hit, ...]:
    """Every concept label in the sentence, in the order it appears.

    Overlaps are resolved by the matcher's own longest-first alternation —
    `registered trade mark` wins over `trade mark` — which is why the
    alternation is sorted by length in `Lexicon.matcher` rather than
    alphabetically.
    """
    hits = []
    for match in matcher.finditer(sentence):
        concept = lexicon.concept_at(match.group(0))
        if concept:
            hits.append(_Hit(concept, match.start(), match.end()))
    return tuple(hits)


def _nearest_before(hits: Iterable[_Hit], position: int) -> _Hit | None:
    candidates = [hit for hit in hits if hit.end <= position]
    return candidates[-1] if candidates else None


def _nearest_after(hits: Iterable[_Hit], position: int) -> _Hit | None:
    for hit in hits:
        if hit.start >= position:
            return hit
    return None


def _cited_in_span(chunk: Chunk, start: int, end: int) -> tuple[str, ...]:
    """The provisions upstream recorded on this chunk whose mention text falls
    inside `[start, end)`.

    Upstream's edge is the authority for *which* provision a surface names; all
    this does is decide whether the mention sits in this sentence. A chunk
    edge carries a `mention` and not an offset, so the test is a case-folded
    substring search inside the sentence — narrower than "the chunk cites it",
    which is the whole reason for doing it.
    """
    window = chunk.text[start:end].casefold()
    found = []
    for edge in chunk.provisions or ():
        mention = (getattr(edge, "mention", None) or "").strip()
        if mention and mention.casefold() in window:
            found.append(edge)
    return tuple(found)


def _modality(clause: str) -> str | None:
    """`must` or nothing. See the module docstring — this is the narrowest
    reading of ADR-0079's permission to author a modality that still records
    one at all."""
    return "must" if _MUST.search(clause) else None


# --------------------------------------------------------------------------
# Pattern 1 — isDefinedIn
# --------------------------------------------------------------------------


def _definition_findings(corpus: Corpus, lexicon: Lexicon) -> Iterator[Finding]:
    """A concept and the provision or unit of an instrument that defines it.

    Three signals, each a lookup, and a unit can carry two of them at once —
    the ref slug and the opening words. The strongest present wins, and the
    signal is recorded so a reviewer can see which one fired.
    """
    definition_provisions = {
        provision.ref
        for provision in corpus.provisions.values()
        if _DEFINITION_PROVISION.match(provision.title or "")
    }

    for unit in corpus.units.values():
        text = unit.text or ""
        parent = unit.parent_ref or unit.ref.rsplit("/", 1)[0]

        # Signal A — the unit's own ref names the defined term. `TMA1995/s6/trade-mark`
        # is upstream saying "this unit is the definition of «trade mark»" in the
        # only place a ref can say anything.
        tail = unit.ref.rsplit("/", 1)[-1]
        slug = _norm(tail.replace("-", " "))
        concept = lexicon.concept_at(slug) if tail != unit.ref else None

        # Signal B — the text opens `«term» means`.
        match = _UNIT_DEFINES.match(text)
        opened = lexicon.concept_at(match.group("term")) if match else None

        signal = None
        if concept and opened and concept == opened:
            signal = "unit_ref_slug+opening_words"
        elif opened:
            concept, signal = opened, "opening_words"
        elif concept and parent in definition_provisions:
            signal = "unit_ref_slug"
        elif concept and match:
            signal = "unit_ref_slug"

        if not concept or not signal:
            continue

        quote = text[:240].strip()
        if not quote:
            continue
        instrument = unit.ref.split("/", 1)[0]
        yield Finding(
            subject=concept,
            predicate="isDefinedIn",
            object=unit.ref,
            source_ref=unit.ref,
            supporting_text=quote,
            span=(0, len(quote)),
            source_content_hash=unit.content_hash,
            basis="corpus_explicit",
            signal=signal,
            modality=None,
            reasoning=(
                f"{instrument} defines this term at {unit.ref}, in the instrument's own words. "
                f"Matched on {signal.replace('+', ' and ')} — no reading of the definition is "
                f"involved and none is recorded: the edge says where the term is defined, not "
                f"what the definition means."
            ),
            alternatives=(
                "That the term the instrument defines and the concept carrying that label "
                "are different things. The record would be wrong if practice has narrowed or "
                "widened the term away from the statutory definition, which is exactly what "
                "the Manual does to «connotation» for section 43.",
            ),
            expert_should_check=(
                "Whether the concept as this vocabulary holds it is the same term the "
                "instrument defines, or a practice reading of it."
            ),
            confidence=0.9,
        )

    for provision in corpus.provisions.values():
        match = _PROVISION_DEFINES.match(provision.title or "")
        if not match:
            continue
        for term in re.split(r"\s+and\s+|,\s*", match.group("terms")):
            cleaned = re.sub(r"\s+in relation to.*$", "", term.strip(), flags=re.I)
            concept = lexicon.concept_at(cleaned)
            if not concept:
                continue
            # The *signal* is the title; the *evidence* is the provision's own
            # opening words. They are not the same string and the harness is
            # right to refuse a quote that does not land at its span: a quote
            # is copied from the snapshot character for character, and the
            # title is metadata about the provision rather than text in it
            # (ADR-0045).
            quote = (provision.text or "").strip()[:240]
            if not quote:
                continue
            title = (provision.title or "").strip()
            yield Finding(
                subject=concept,
                predicate="isDefinedIn",
                object=provision.ref,
                source_ref=provision.ref,
                supporting_text=quote,
                span=(0, len(quote)),
                source_content_hash=provision.content_hash,
                basis="corpus_explicit",
                signal="provision_title",
                modality=None,
                reasoning=(
                    f"The provision is titled {title!r}: the instrument names the term it is "
                    f"defining in its own heading, and the quoted text is the provision's opening "
                    f"words. The whole provision is the object because a definition stated across "
                    f"several subsections has no single unit to point at."
                ),
                alternatives=(
                    "Pointing at one unit inside the provision instead. Rejected because the "
                    "title governs the provision and choosing a unit would be this pass deciding "
                    "which subsection carries the definition.",
                ),
                expert_should_check=(
                    "Whether the whole provision or one subsection of it is the right object."
                ),
                confidence=0.85,
            )


# --------------------------------------------------------------------------
# Pattern 2 — hasStatutoryBasis
# --------------------------------------------------------------------------


def _statutory_basis_findings(corpus: Corpus, lexicon: Lexicon) -> Iterator[Finding]:
    """A concept and the provision the Manual's own authors linked beside it.

    Restricted to `extraction: href` edges, which are the links the Manual
    carries in its markup rather than something read out of prose. That is the
    strongest provenance in the corpus and it is upstream's word, not this
    module's: nothing here re-parses a citation (CLAUDE.md rules 2 and 3).

    Restricted further to the sentence: a chunk-level "cites" would join every
    concept in a 400-word chunk to every section mentioned anywhere in it.
    """
    matcher = lexicon.matcher
    for chunk in corpus.chunks.values():
        if not chunk.text or not chunk.provisions:
            continue
        href_edges = [
            edge for edge in chunk.provisions if getattr(edge, "extraction", None) == "href"
        ]
        if not href_edges:
            continue
        for sentence, start, end in _sentences(chunk.text):
            hits = _concept_hits(lexicon, matcher, sentence)
            if not hits:
                continue
            window = sentence.casefold()
            for edge in href_edges:
                mention = (getattr(edge, "mention", None) or "").strip()
                if not mention or mention.casefold() not in window:
                    continue
                position = window.find(mention.casefold())
                # The citation has to be introduced as a basis, not merely
                # mentioned. See `_BASIS_PHRASE`.
                if not _BASIS_PHRASE.search(sentence[:position]):
                    continue
                subject = _nearest_before(hits, position)
                # And the concept has to be near enough to be what the clause is
                # about. 120 characters is roughly a clause; beyond it the
                # "nearest preceding" concept is just the last one in a long
                # sentence.
                if subject is None or position - subject.end > MAX_GAP:
                    continue
                yield Finding(
                    subject=subject.concept,
                    predicate="hasStatutoryBasis",
                    object=edge.id,
                    source_ref=chunk.chunk_ref,
                    supporting_text=sentence,
                    span=(start, end),
                    source_content_hash=chunk.content_hash,
                    basis="corpus_explicit",
                    signal="manual_href",
                    modality=_modality(sentence),
                    reasoning=(
                        f"The Manual's authors hyperlinked {edge.id} to the words {mention!r} in "
                        f"this sentence, and the sentence is about "
                        f"{lexicon.labels.get(subject.concept, subject.concept)!r}. The link is "
                        f"upstream's `href` edge, the strongest provenance the corpus carries; "
                        f"the subject is the nearest concept label before the link."
                    ),
                    alternatives=(
                        "A different concept in the same sentence as the subject. The "
                        "nearest-preceding rule is mechanical and will be wrong where the "
                        "sentence puts the governed term after the citation.",
                        "No edge at all, on the ground that the Manual citing a section beside a "
                        "term does not make the section that term's basis.",
                    ),
                    expert_should_check=(
                        "Whether this provision is the concept's statutory basis or merely a "
                        "section the same sentence happens to mention."
                    ),
                    confidence=0.65,
                )


# --------------------------------------------------------------------------
# Patterns 3 and 4 — mayGiveRiseTo / doesNotGiveRiseTo
# --------------------------------------------------------------------------


def _ground_findings(corpus: Corpus, lexicon: Lexicon) -> Iterator[Finding]:
    """What raises a ground for rejection, and what does not.

    The object is the section cited in the same sentence where there is one,
    and the *ground for rejection* concept where there is not. Both forms
    appear in the signed set — `GR-0007` runs concept to concept, `GR-0044`
    concept to provision — so neither is this pass inventing a shape.
    """
    matcher = lexicon.matcher
    ground_concept = lexicon.by_label.get("ground for rejection")
    for chunk in corpus.chunks.values():
        if not chunk.text:
            continue
        for sentence, start, end in _sentences(chunk.text):
            match = _GROUND.search(sentence)
            if not match:
                continue
            # The sentence must be about a ground arising, not merely contain
            # the phrase, and the raising verb must be near it.
            if not _GROUND_VERB.search(sentence[max(0, match.start() - 90) : match.end() + 90]):
                continue
            negation = _GROUND_NEGATED.search(sentence)
            negated = bool(negation) and match.start() - negation.start() < 60
            predicate = "doesNotGiveRiseTo" if negated else "mayGiveRiseTo"
            hits = [
                hit
                for hit in _concept_hits(lexicon, matcher, sentence)
                if hit.concept != ground_concept
                # An office does not give rise to a ground; it raises one. The
                # typing store is what knows which concepts are offices, and
                # letting one through here produced `applicant mayGiveRiseTo
                # ground for rejection` on the first run.
                and lexicon.groups.get(hit.concept) != "process_role"
            ]
            subject = _nearest_before(hits, match.start())
            if subject is None or match.start() - subject.end > MAX_GAP:
                continue

            cited = _cited_in_span(chunk, start + match.start(), end)
            obj = cited[0].id if cited else ground_concept
            if not obj:
                continue

            yield Finding(
                subject=subject.concept,
                predicate=predicate,
                object=obj,
                source_ref=chunk.chunk_ref,
                supporting_text=sentence,
                span=(start, end),
                source_content_hash=chunk.content_hash,
                basis="corpus_inferred",
                signal="ground_phrase_negated" if negated else "ground_phrase",
                modality=None if negated else _modality(sentence),
                reasoning=(
                    f"The sentence states that "
                    f"{lexicon.labels.get(subject.concept, subject.concept)!r} "
                    f"{'does not give rise to' if negated else 'gives rise to'} a ground for "
                    f"rejection. The subject is the nearest concept label before the ground "
                    f"phrase; the object is "
                    + (
                        f"{obj}, the provision the Manual cites in the same sentence."
                        if cited
                        else "the ground-for-rejection concept, because the sentence names no provision."
                    )
                ),
                alternatives=(
                    "Reading the sentence as descriptive rather than as stating a ground — the "
                    "Manual often recites what a ground is before saying when it arises.",
                    "A different concept in the sentence as subject. Nearest-preceding is "
                    "mechanical and will misfire on a sentence that states the condition after "
                    "the consequence.",
                ),
                expert_should_check=(
                    "Whether this sentence states when the ground arises, or merely describes "
                    "it — and whether the subject is the condition or something else in the "
                    "same clause."
                ),
                confidence=0.55,
            )


# --------------------------------------------------------------------------
# Pattern 5 — isOvercomeBy
# --------------------------------------------------------------------------


def _overcome_findings(corpus: Corpus, lexicon: Lexicon) -> Iterator[Finding]:
    matcher = lexicon.matcher
    for chunk in corpus.chunks.values():
        if not chunk.text:
            continue
        for sentence, start, end in _sentences(chunk.text):
            match = _OVERCOME_BY.search(sentence)
            if not match:
                continue
            hits = [
                hit
                for hit in _concept_hits(lexicon, matcher, sentence)
                # An office is neither the thing overcome nor the thing that
                # overcomes it. `«ground» may be overcome by the applicant
                # agreeing to a condition` names the applicant and means the
                # condition, and letting a role through takes the actor.
                if lexicon.groups.get(hit.concept) != "process_role"
            ]
            subject = _nearest_before(hits, match.start())
            obj = _nearest_after(hits, match.end())
            if not subject or not obj or subject.concept == obj.concept:
                continue
            if match.start() - subject.end > MAX_GAP or obj.start - match.end() > MAX_GAP:
                continue
            yield Finding(
                subject=subject.concept,
                predicate="isOvercomeBy",
                object=obj.concept,
                source_ref=chunk.chunk_ref,
                supporting_text=sentence,
                span=(start, end),
                source_content_hash=chunk.content_hash,
                basis="corpus_inferred",
                signal="overcome_clause",
                modality=None,
                reasoning=(
                    f"The sentence says "
                    f"{lexicon.labels.get(subject.concept, subject.concept)!r} is overcome by "
                    f"{lexicon.labels.get(obj.concept, obj.concept)!r}. Subject before the verb, "
                    f"object after it; no other reading of the clause is taken."
                ),
                alternatives=(
                    "That what overcomes the objection is a wider thing than the concept "
                    "matched — evidence of a kind rather than the named concept.",
                ),
                expert_should_check=(
                    "Whether the thing that overcomes the objection is this concept or a "
                    "broader category the sentence names it as an example of."
                ),
                confidence=0.6,
            )


# --------------------------------------------------------------------------
# Pattern 6 — requiresElement
# --------------------------------------------------------------------------


def _requires_findings(corpus: Corpus, lexicon: Lexicon) -> Iterator[Finding]:
    matcher = lexicon.matcher
    for chunk in corpus.chunks.values():
        if not chunk.text:
            continue
        for sentence, start, end in _sentences(chunk.text):
            match = _REQUIRES.search(sentence)
            if not match:
                continue
            hits = [
                hit
                for hit in _concept_hits(lexicon, matcher, sentence)
                # Same reason as the ground pattern: an office is not a thing
                # with elements, and `applicant requiresElement classification`
                # is what comes out when one is allowed to be the subject.
                if lexicon.groups.get(hit.concept) != "process_role"
            ]
            subject = _nearest_before(hits, match.start())
            obj = _nearest_after(hits, match.end())
            if not subject or not obj or subject.concept == obj.concept:
                continue
            if match.start() - subject.end > MAX_GAP or obj.start - match.end() > MAX_GAP:
                continue
            yield Finding(
                subject=subject.concept,
                predicate="requiresElement",
                object=obj.concept,
                source_ref=chunk.chunk_ref,
                supporting_text=sentence,
                span=(start, end),
                source_content_hash=chunk.content_hash,
                basis="corpus_inferred",
                signal="requires_clause",
                modality=_modality(sentence),
                reasoning=(
                    f"The sentence makes "
                    f"{lexicon.labels.get(obj.concept, obj.concept)!r} a requirement of "
                    f"{lexicon.labels.get(subject.concept, subject.concept)!r}. Subject before "
                    f"the requiring verb, object after it."
                ),
                alternatives=(
                    "That the requirement runs the other way — some Manual sentences state the "
                    "requirement first and the thing required of second.",
                ),
                expert_should_check=(
                    "The direction of the requirement, and whether the object is an element of "
                    "the subject or a separate condition stated alongside it."
                ),
                confidence=0.5,
            )


# --------------------------------------------------------------------------
# Pattern 7 — isPerformedBy
# --------------------------------------------------------------------------


def _performed_by_findings(corpus: Corpus, lexicon: Lexicon) -> Iterator[Finding]:
    """A step and the office that takes it.

    Fires only where the sentence carries both a `process_role` concept and a
    `procedural_step` concept, so the typing pass does the work of deciding
    which concept is an office and which is an act. Where the typing is wrong
    this edge is wrong, and that dependency is worth stating: the groups are an
    agent's and OQ-0026 puts them in front of the owner.
    """
    matcher = lexicon.matcher
    modal = re.compile(r"\b(?:will|must|may|should|shall|can)\b", re.I)
    for chunk in corpus.chunks.values():
        if not chunk.text:
            continue
        for sentence, start, end in _sentences(chunk.text):
            hits = _concept_hits(lexicon, matcher, sentence)
            roles = [hit for hit in hits if lexicon.groups.get(hit.concept) == "process_role"]
            steps = [hit for hit in hits if lexicon.groups.get(hit.concept) == "procedural_step"]
            if not roles or not steps:
                continue
            role = roles[0]
            following = sentence[role.end : role.end + 40]
            if not modal.search(following):
                continue
            # `the applicant will be notified` names the office the act is done
            # *to*. The pattern cannot parse, so it declines the passive rather
            # than reading it backwards — this is the alternative the record's
            # own `alternatives_considered` names, caught rather than shipped.
            if _PASSIVE.search(following):
                continue
            step = _nearest_after(steps, role.end)
            if step is None:
                continue
            yield Finding(
                subject=step.concept,
                predicate="isPerformedBy",
                object=role.concept,
                source_ref=chunk.chunk_ref,
                supporting_text=sentence,
                span=(start, end),
                source_content_hash=chunk.content_hash,
                basis="corpus_inferred",
                signal="role_modal_step",
                modality=_modality(following),
                reasoning=(
                    f"The sentence puts "
                    f"{lexicon.labels.get(role.concept, role.concept)!r} in front of a modal "
                    f"verb and names "
                    f"{lexicon.labels.get(step.concept, step.concept)!r} as what follows. The "
                    f"role and step groups come from the typing store, not from this pass."
                ),
                alternatives=(
                    "That the office named is the one the act is done *to* rather than *by* — "
                    "«the applicant must be notified» reads the other way and this pattern "
                    "cannot see the passive.",
                ),
                expert_should_check=(
                    "Whether the office performs the step or merely appears beside it, and "
                    "whether the sentence is passive."
                ),
                confidence=0.45,
            )


# --------------------------------------------------------------------------
# Pattern 8 — mustOccurWithin
# --------------------------------------------------------------------------


def _period_findings(corpus: Corpus, lexicon: Lexicon) -> Iterator[Finding]:
    """A step and the provision that fixes the period it must happen in.

    The object is the provision, never the period itself. A record whose object
    is the string `2 months` would put a quantity where every other record in
    the store puts an identifier, and the period is in `supporting_text`
    already — where it can be read with the words that qualify it, which is the
    only way a period in this corpus means anything.
    """
    matcher = lexicon.matcher
    for chunk in corpus.chunks.values():
        if not chunk.text or not chunk.provisions:
            continue
        for sentence, start, end in _sentences(chunk.text):
            match = _PERIOD.search(sentence)
            if not match:
                continue
            cited = _cited_in_span(chunk, start, end)
            if not cited:
                continue
            hits = _concept_hits(lexicon, matcher, sentence)
            steps = [hit for hit in hits if lexicon.groups.get(hit.concept) == "procedural_step"]
            if not steps:
                continue
            step = steps[0]
            yield Finding(
                subject=step.concept,
                predicate="mustOccurWithin",
                object=cited[0].id,
                source_ref=chunk.chunk_ref,
                supporting_text=sentence,
                span=(start, end),
                source_content_hash=chunk.content_hash,
                basis="corpus_inferred",
                signal="period_clause",
                modality=_modality(sentence),
                reasoning=(
                    f"The sentence states a period — {match.group(0)!r} — for "
                    f"{lexicon.labels.get(step.concept, step.concept)!r}, and cites "
                    f"{cited[0].id} in the same sentence. The object is the provision that fixes "
                    f"the period, not the period, which is in the supporting text with the words "
                    f"that qualify it."
                ),
                alternatives=(
                    "That the period governs a different step in the same sentence, or that the "
                    "provision cited is not the one that fixes it.",
                ),
                expert_should_check=(
                    "Whether the cited provision is the source of the period, and whether the "
                    "period is extendable — the Manual states several that are."
                ),
                confidence=0.5,
            )


_PATTERNS = (
    _definition_findings,
    _statutory_basis_findings,
    _ground_findings,
    _overcome_findings,
    _requires_findings,
    _performed_by_findings,
    _period_findings,
)


def extract(corpus: Corpus | None = None, lexicon: Lexicon | None = None) -> tuple[Finding, ...]:
    """Every edge the patterns find, deduplicated on (subject, predicate, object).

    **One record per triple.** The corpus states the same relation in many
    places and a record per sentence would put 40 identical edges in the store
    and 40 rows in front of a reviewer. The sentence kept is the
    best-evidenced: `corpus_explicit` over `corpus_inferred`, then higher
    confidence, then the lowest ref so the output is byte-stable across runs.
    """
    corpus = corpus if corpus is not None else load_corpus()
    lexicon = lexicon if lexicon is not None else build_lexicon()

    best: dict[tuple[str, str, str], Finding] = {}
    rank = {"corpus_explicit": 2, "corpus_inferred": 1, "general_knowledge": 0}
    for pattern in _PATTERNS:
        for finding in pattern(corpus, lexicon):
            if finding.subject == finding.object:
                continue
            existing = best.get(finding.key)
            if existing is None:
                best[finding.key] = finding
                continue
            challenger = (rank[finding.basis], finding.confidence, existing.source_ref)
            incumbent = (rank[existing.basis], existing.confidence, finding.source_ref)
            if challenger > incumbent:
                best[finding.key] = finding

    return tuple(sorted(best.values(), key=lambda f: (f.predicate, f.subject, f.object)))


def render_records(
    findings: tuple[Finding, ...],
    *,
    lexicon: Lexicon | None = None,
    start_id: int | None = None,
    authored_date: str | None = None,
) -> list[dict[str, Any]]:
    """Findings as authored records, envelope and all.

    Ids continue the one project-wide `GR-` sequence (`docs/IDENTIFIERS.md` §3)
    — allocated by appending past the highest id either store holds, never by
    filling a gap.
    """
    lexicon = lexicon if lexicon is not None else build_lexicon()
    stamp = authored_date or date.today().isoformat()
    if start_id is None:
        start_id = _next_relationship_id()

    records = []
    for offset, finding in enumerate(findings):
        collision = lexicon.collision_note(finding.subject, finding.object)
        check = finding.expert_should_check
        if collision:
            check = f"{check} Also: {collision}."
        records.append(
            {
                "id": f"GR-{start_id + offset:04d}",
                "subject": finding.subject,
                "predicate": finding.predicate,
                "object": finding.object,
                "source_ref": finding.source_ref,
                "supporting_text": finding.supporting_text,
                "span": list(finding.span),
                "source_content_hash": finding.source_content_hash,
                # Tier 3 throughout, and not because every edge is equally
                # consequential. Tier is an expert's call (common.schema.json)
                # and ADR-0082 turned it from a gate into a label, so the safe
                # default is the one that says "a wrong reading here matters"
                # rather than one this pass talks itself into.
                "tier": 3,
                "modality": finding.modality,
                "notes": (
                    f"Authored by a deterministic pass over the whole corpus "
                    f"({finding.signal}). No expert has read this record."
                ),
                "approved_by": None,
                "approved_date": None,
                "authored": {
                    "review_status": "unreviewed",
                    "authored_by": AUTHORED_BY,
                    "authored_date": stamp,
                    "authoring_basis": finding.basis,
                    "evidence": [
                        {
                            "ref": finding.source_ref,
                            "span": list(finding.span),
                            "content_hash": finding.source_content_hash,
                            "quote": finding.supporting_text,
                        }
                    ],
                    "confidence": finding.confidence,
                    "reasoning": finding.reasoning,
                    "alternatives_considered": list(finding.alternatives),
                    "expert_should_check": check,
                },
            }
        )
    return records


def _next_relationship_id() -> int:
    """One past the highest `GR-` in either store. ADR-0080 consequence 1 makes
    an id used by both stores a defect, so the allocator has to see both."""
    highest = 0
    for records in (goldset.load()["gold_relationship"], authored_store.load()["gold_relationship"]):
        for record in records:
            match = re.match(r"^GR-(\d+)$", str(record["id"]))
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


_HEADER = """\
# Relationships authored across the whole Manual and both instruments.
#
# EVERY RECORD HERE WAS WRITTEN BY A MACHINE AND READ BY NOBODY. That is what
# `review_status: unreviewed` means and it is permanent until a named person
# signs the record through `tmk-transcribe` (ADR-0079, ADR-0086).
#
# Generated {stamp} by `tmk-relationships --write`
# (tm_knowledge.stage0.relationships). Deterministic: the same pin and the same
# pattern set produce the same bytes. Do not hand-edit — a correction belongs
# in a review round, not in this file.
"""


def write_records(
    records: list[dict[str, Any]], path: Path | None = None, *, generated: str | None = None
) -> Path:
    path = path or AUTHORED_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(records, sort_keys=False, allow_unicode=True, width=100)
    header = _HEADER.format(stamp=generated or date.today().isoformat())
    path.write_text(header + body, encoding="utf-8")
    return path


def _part_of(ref: str) -> str:
    match = re.match(r"^TMM/(Part[0-9A-Za-z]+)", ref)
    if match:
        return match.group(1)
    return ref.split("/", 1)[0]


def write_report(
    findings: tuple[Finding, ...],
    path: Path | None = None,
    *,
    lexicon: Lexicon | None = None,
    generated: str | None = None,
) -> Path:
    """What the pass found, where it found it, and what it refuses to claim."""
    lexicon = lexicon if lexicon is not None else build_lexicon()
    path = path or REPORT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    by_predicate: dict[str, list[Finding]] = defaultdict(list)
    by_part: dict[str, int] = defaultdict(int)
    by_basis: dict[str, int] = defaultdict(int)
    concepts_touched: set[str] = set()
    for finding in findings:
        by_predicate[finding.predicate].append(finding)
        by_part[_part_of(finding.source_ref)] += 1
        by_basis[finding.basis] += 1
        for value in (finding.subject, finding.object):
            if value.startswith("GC-"):
                concepts_touched.add(value)

    lines = [
        "<!-- Generated by tm_knowledge.stage0.relationships. Do not hand-edit. -->",
        "",
        "# Relationships across the whole Manual — what the pass found",
        "",
        "**Every edge below was written by a machine and read by nobody.** The records"
        " are in `authored/relationships.yaml`, each stamped `unreviewed` with its"
        " evidence, its reasoning and the thing it most expects to have got wrong"
        " (ADR-0079). Nothing here is approved knowledge and no count on this page may"
        " be added to a count of signed records.",
        "",
        f"| Generated | {generated or date.today().isoformat()} |",
        "|---|---|",
        f"| Edges authored | **{len(findings)}** |",
        f"| Predicates used | {len(by_predicate)} |",
        f"| Concepts joined | {len(concepts_touched)} of {len(lexicon.labels)} |",
        f"| Parts and instruments reached | {len(by_part)} |",
        f"| `corpus_explicit` | {by_basis.get('corpus_explicit', 0)} |",
        f"| `corpus_inferred` | {by_basis.get('corpus_inferred', 0)} |",
        f"| `general_knowledge` | {by_basis.get('general_knowledge', 0)} |",
        "",
        "## 1. By predicate",
        "",
        "`approved` means an expert already used the term in a signed record, so it was"
        " on the closed list before today. `authored` means this pass added it and no"
        " expert has used it — `relations.ttl` types those `tmk:AuthoredRelation` and"
        " keeps them apart from the fourteen (ADR-0109).",
        "",
        "| predicate | edges | on the list before today | median confidence |",
        "|---|---|---|---|",
    ]
    for predicate in sorted(by_predicate):
        rows = by_predicate[predicate]
        confidences = sorted(f.confidence for f in rows)
        median = confidences[len(confidences) // 2]
        status = "approved" if predicate in APPROVED_PREDICATES else "**authored**"
        lines.append(f"| `{predicate}` | {len(rows)} | {status} | {median:.2f} |")

    lines += [
        "",
        "## 2. Where the evidence is",
        "",
        "The section 43 test for this whole exercise. `Part29` is the Part the signed"
        " relationship set was drawn from, and every one of its 37 source refs points"
        " there. A pass that only widened the vocabulary would show the same"
        " concentration here.",
        "",
        "| source | edges |",
        "|---|---|",
    ]
    for part, count in sorted(by_part.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{part}` | {count} |")

    lines += [
        "",
        "## 3. What this pass will not claim",
        "",
        "- **It does not read a `may` or a `should` as a modality.** Only `must` is"
        " recorded, and every other modal leaves the field null and reported as a gap."
        " Whether a Manual `may` is possibility or permission is a legal reading"
        " (`gold-relationship.schema.json`), and the signed set's own `GR-0001` records"
        " a reviewer making exactly that judgement by hand.",
        "- **It does not resolve a label two concepts carry.** It takes the signed"
        " concept and names the collision on the record (ADR-0101).",
        "- **It does not choose between several definitions of one term.** *notice of"
        " opposition* is defined in six places and gets six records; upstream refused"
        " to choose and so does this (Q-07).",
        "- **It does not re-derive a citation.** Every provision ref on an edge is an"
        " edge upstream already recorded, with its `extraction` and `certainty` intact"
        " (CLAUDE.md rules 2 and 3).",
        "- **It does not state an examination outcome**, and nothing built on it may"
        " (CLAUDE.md §6, PU-0001 to PU-0003).",
        "",
        "## 4. The weakest edges, named",
        "",
        "Lowest confidence first — the rows a reviewer should open before any other,"
        " because they are where the pattern is thinnest.",
        "",
        "| subject | predicate | object | confidence | source |",
        "|---|---|---|---|---|",
    ]
    weakest = sorted(findings, key=lambda f: (f.confidence, f.subject, f.object))[:25]
    for finding in weakest:
        subject = lexicon.labels.get(finding.subject, finding.subject)
        obj = lexicon.labels.get(finding.object, finding.object)
        lines.append(
            f"| {subject} | `{finding.predicate}` | {obj} | {finding.confidence:.2f} | "
            f"`{finding.source_ref}` |"
        )

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

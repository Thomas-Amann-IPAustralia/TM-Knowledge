"""Definitions of concepts — machine-written, unreviewed (the review response, F06).

The owner lifted the deferral on definitions on 2026-10-17 (CHAT-0078, ADR-0136). Two
reviews had named their absence: the expert asked for them first, and the ontology was
a vocabulary of names with sources and no meanings.

A definition is **its own record**, in `authored/definitions.yaml`, never a field on
the concept, for the reason a concept's kind is its own record (ADR-0071): a signed
concept cannot be edited, and writing a definition into it would put machine content
inside a signature (CLAUDE.md rule 4). It follows that approving a label approves no
definition. Ids are `GD-`, one sequence across the project (`docs/IDENTIFIERS.md` §3).

**One definition per concept per scope** (the second review response, A03; ADR-0146,
superseding ADR-0137's "one per concept"). A word can mean different things in different
Parts of the Regulations or in different periods, and the honest model of that is two
scoped definitions, not one definition that blurs them or a split concept (which the
owner postponed for "application", CHAT-0025). The disambiguation rule: a concept with
one definition has it; a concept with several has a `scope` on every one, no two alike,
and a reader picks one only when the context names its scope. Otherwise the concept is
`unresolved`, every candidate is shown and none is chosen (`resolve`).

Each carries the authoring envelope like any machine-written record, and says where its
words come from (`basis`), because a definition is where practice and law are easiest to
blur (CLAUDE.md rule 5):

- `statutory_definition` — the Act's or Regulations' own definition, quoted verbatim
  (preferred wherever one exists: CHAT-0045);
- `statutory_provision` — written from a provision that says what the thing is or does;
- `manual` — written from the Manual's own explanation, which states practice, not law.

A concept whose sources do not define it gets no record: "If the corpus does not support
it, the record says so or is not written" (ADR-0079 guard 2).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.authored import store as authored_store
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0.schemas import SchemaError, validator_for_file

__all__ = ["DEFINITIONS_FILE", "SCHEMA", "BASES", "Definition", "Definitions", "Resolution", "Flag", "load",
           "triage"]

DEFINITIONS_FILE = "definitions.yaml"
SCHEMA = "definition.schema.json"

#: Where a definition's words come from, and which refs may carry them.
BASES = {
    "statutory_definition": ("TMA1995/", "TMR1995/"),
    "statutory_provision": ("TMA1995/", "TMR1995/"),
    "manual": ("TMM/",),
}


@dataclass(frozen=True)
class Definition:
    record: dict[str, Any]
    envelope: dict[str, Any] | None
    errors: tuple[SchemaError | str, ...] = ()

    @property
    def id(self) -> str:
        return str(self.record.get("id") or "<definition with no id>")

    @property
    def concept(self) -> str:
        return str(self.record.get("concept") or "")

    @property
    def scope(self) -> str | None:
        return self.record.get("scope")

    @property
    def sound(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class Definitions:
    entries: tuple[Definition, ...] = ()
    path: Path | None = None

    @property
    def sound(self) -> tuple[Definition, ...]:
        return tuple(entry for entry in self.entries if entry.sound)

    @property
    def refused(self) -> tuple[Definition, ...]:
        return tuple(entry for entry in self.entries if not entry.sound)

    def by_concept(self) -> dict[str, Definition]:
        """Each concept whose definition needs no context to pick: the ones with exactly
        one. A concept with several scoped definitions is not here; `resolve` it."""
        found: dict[str, list[Definition]] = {}
        for entry in self.sound:
            found.setdefault(entry.concept, []).append(entry)
        return {concept: only[0] for concept, only in found.items() if len(only) == 1}

    def resolve(self, concept: str, scope: str | None = None) -> "Resolution":
        """The definition of `concept` in a context naming `scope`, or why none is chosen.

        `none`: no definition. `single`: one, whatever its scope. `scoped`: several, and
        the context names one's scope. `unresolved`: several, and the context names none
        of them; every candidate is returned and none is chosen (CLAUDE.md rule 6)."""
        candidates = tuple(entry for entry in self.sound if entry.concept == concept)
        if not candidates:
            return Resolution(concept, scope, "none", None, ())
        if len(candidates) == 1:
            return Resolution(concept, scope, "single", candidates[0], candidates)
        named = [entry for entry in candidates if scope is not None and entry.scope == scope]
        if named:
            return Resolution(concept, scope, "scoped", named[0], candidates)
        return Resolution(concept, scope, "unresolved", None, candidates)


@dataclass(frozen=True)
class Resolution:
    concept: str
    scope: str | None
    state: str  # none, single, scoped, unresolved
    chosen: Definition | None
    candidates: tuple[Definition, ...]


def _check(record: dict[str, Any], envelope: Any, concepts: set[str]) -> list[SchemaError | str]:
    """Shape, envelope, and what a schema cannot see."""
    errors: list[SchemaError | str] = []
    record_id = str(record.get("id") or "")
    for error in validator_for_file(SCHEMA).iter_errors(record):
        errors.append(SchemaError(record_id, "/".join(str(p) for p in error.absolute_path), error.message))
    if envelope is None:
        errors.append("no `authored:` envelope — a definition is machine-written and must say so")
    else:
        errors.extend(authored_store.validate_envelope(envelope, record_id=record_id))
    if errors:
        return errors

    if record["concept"] not in concepts:
        errors.append(f"defines {record['concept']}, which is no concept in either store")
    refs = [str(item.get("ref")) for item in envelope.get("evidence") or ()]
    if not refs:
        errors.append("rests on no evidence — a definition the corpus does not support is not written")
    if record["source_ref"] not in refs:
        errors.append(f"source_ref {record['source_ref']} is not among the evidence it quotes")
    allowed = BASES[record["basis"]]
    if not any(ref.startswith(allowed) for ref in refs):
        errors.append(f"basis {record['basis']} but no evidence is from {' or '.join(allowed)}")
    if record["basis"] == "statutory_definition" and not all(ref.startswith(allowed) for ref in refs):
        errors.append("a statutory definition quotes the instrument and nothing else")
    return errors


def load(
    root: Path | None = None,
    gold: goldset.GoldSet | None = None,
    authored: authored_store.AuthoredSet | None = None,
) -> Definitions:
    """Every definition, each checked. Refused, never skipped, like any authored record."""
    root = root or authored_store.AUTHORED_DIR
    path = root / DEFINITIONS_FILE
    if not path.exists():
        return Definitions(path=path)
    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load(root)
    concepts = {str(r["id"]) for r in gold["gold_concept"]} | {
        entry.record_id for entry in authored.of("gold_concept") if entry.sound
    }
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(document, list):
        raise authored_store.MalformedAuthoredFile(f"{path.name}: expected a list of definitions")
    entries = []
    seen_ids: set[str] = set()
    defined: set[tuple[str, str | None]] = set()
    scoped = {str(raw.get("concept")) for raw in document if isinstance(raw, dict) and raw.get("scope")}
    for raw in document:
        if not isinstance(raw, dict):
            raise authored_store.MalformedAuthoredFile(f"{path.name}: a definition is not a mapping")
        record = {k: v for k, v in raw.items() if k != authored_store.ENVELOPE_KEY}
        envelope = raw.get(authored_store.ENVELOPE_KEY)
        errors = _check(record, envelope, concepts)
        concept, scope = str(record.get("concept")), record.get("scope")
        if str(record.get("id")) in seen_ids:
            errors.append("id used twice in definitions.yaml")
        if (concept, scope) in defined:
            errors.append(f"a second definition of {concept} in the same scope ({scope or 'no scope'}); "
                          "one concept, one definition per scope")
        if concept in scoped and not scope:
            # Unscoped beside scoped would read as the general meaning and win by default:
            # the very choice the disambiguation rule leaves to the context (ADR-0146).
            errors.append(f"{concept} has scoped definitions, and this one names no scope")
        seen_ids.add(str(record.get("id")))
        defined.add((concept, scope))
        entries.append(Definition(record=record, envelope=envelope, errors=tuple(errors)))
    return Definitions(entries=tuple(entries), path=path)


# ---------------------------------------------------------------------------
# triage: three deterministic checks for a definition that omits a qualification
# ---------------------------------------------------------------------------
#
# The second review response (R02) found four definitions that drop a qualification
# their source states: GD-0050 (s 41 does not apply to certification marks), GD-0128
# (s 11(1)(c) left out), GD-0084 ("unless ... prescribed in reg 21.28"), GD-0146
# ("unless acceptance is deferred"). Three checks find the first three in seconds and
# run on every definition written later. They flag for a reader; they decide nothing,
# and a flag that was read and stands stays a note.

#: A qualifier that, just after a quoted Manual span, may limit what the span says.
_QUALIFIER = re.compile(r"\bHowever\b|\bBut\b|\b[Uu]nless\b|\bdoes not apply\b")
#: How far after a quoted span a qualifier is looked for.
_AFTER = 200
#: An obligation or a consequence in a definition's own words.
_CONSEQUENCE = re.compile(r"\bmust\b|\brejected\b", re.IGNORECASE)


@dataclass(frozen=True)
class Flag:
    id: str
    check: str
    message: str


def _parent(ref: str) -> str | None:
    found = re.match(r"^(.*)\([^()]*\)$", ref)
    return found.group(1) if found else None


def triage(definitions: Definitions, corpus: Any, kinds: dict[str, str]) -> list[Flag]:
    """(a) a statutory definition quoting some paragraphs of a subsection and not the
    rest; (b) Manual evidence followed, within 200 characters of the same chunk and
    outside any other quoted span, by "However", "But", "unless" or "does not apply";
    (c) the definition of a concept that is not a ground for rejection stating "must"
    or "rejected", an obligation or consequence kept apart from the meaning (for a
    ground, the rejection is the meaning). `kinds` maps a concept to its kind."""
    out: list[Flag] = []
    for entry in definitions.sound:
        evidence = [e for e in (entry.envelope or {}).get("evidence") or () if isinstance(e, dict)]
        cited = {str(e.get("ref")) for e in evidence if str(e.get("ref", "")).startswith(("TMA", "TMR"))}
        for parent in sorted({p for r in cited if (p := _parent(r)) and "(" in p}):
            children = [k for k in corpus.units if k.startswith(parent + "(") and "~" not in k
                        and "(" not in k[len(parent) + 1:].split(")", 1)[1]]
            missing = sorted(k for k in children if k not in cited)
            if missing and len(missing) < len(children):
                out.append(Flag(entry.id, "a", f"quotes some paragraphs of {parent} and not {', '.join(missing)}"))
        for item in evidence:
            ref, span = str(item.get("ref", "")), item.get("span") or (0, 0)
            chunk = corpus.chunks.get(ref) if ref.startswith("TMM/") else None
            if chunk is None:
                continue
            found = _QUALIFIER.search(chunk.text, span[1], span[1] + _AFTER)
            if found and not any(o.get("ref") == ref and o["span"][0] <= found.start() < o["span"][1]
                                 for o in evidence if o.get("span")):
                tail = " ".join(chunk.text[found.start():found.start() + 70].split())
                out.append(Flag(entry.id, "b", f"{ref} continues after the quote: \u201c{tail}\u2026\u201d"))
        if kinds.get(entry.concept) != "ground_of_refusal" and _CONSEQUENCE.search(str(entry.record.get("text"))):
            out.append(Flag(entry.id, "c", "states an obligation or a consequence (\"must\" or \"rejected\") "
                                          "in the definition of a concept that is not a ground"))
    return out

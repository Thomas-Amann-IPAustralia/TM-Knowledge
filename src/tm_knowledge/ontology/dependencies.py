"""What rests on a source: one dependency index over every store, keyed by any ref.

The second review response's R05. RULE-0002 answers "which signed records would
need re-reading if this Manual passage changed", over the approved graph and
nothing else: no definition, no correction, no machine-written record, and no
route from a provision. A policy aid's question usually starts from a provision
("what would amending section 44 touch?"), so this index starts from any ref
upstream mints, a Part, a page, a chunk, a provision or a unit, and answers from
every record type in both stores.

**"No recorded dependency", never "no impact".** Like RULE-0002 (whose limits line
this inherits), the index sees only what a record *names*: a passage on the same
subject that no record cites is invisible to it (Q-28).

Each dependency says which record, of which type, in which store and review state,
names the ref where (`field`), against which content hash, and whether that hash
still matches the pinned snapshot (the harness's staleness comparison, through the
same resolver, `harness._passage`). Two views, never summed:

- **current**: what serves now, the signed records with every correction applied
  (`served_gold()`), the corrections themselves, the definitions, the structured
  legal tests and process templates, and every sound machine-written record;
- **as signed**: the signed records exactly as signed (`goldset.load()`). A
  dependency only here is history: a correction removed it, or replaced the record.

A provision also reaches records through the Manual passages that cite it. That
route is reported apart (`via_manual`), each hop carrying upstream's `extraction`
and `certainty` unchanged; an `ambiguous` edge is listed as ambiguous, never
resolved (CLAUDE.md rules 3 and 6).

Read by `explorer.build.stability` and the ontology report. RULE-0002 is left as it
is: approved for its own scope (OQ-0004), it is the signed-records-only view.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterator

from tm_knowledge.refs import InvalidRef, parse_ref
from tm_knowledge.upstream.loader import Corpus

__all__ = ["Dependency", "DependencyIndex", "build", "coverage_by_part", "SEPARATORS"]

#: How a ref names a part of another: `TMA1995/s44` → `TMA1995/s44(3)`,
#: `TMM/Part29` → `TMM/Part29/1`, a page → its `#` and `~` chunks.
SEPARATORS = ("(", "/", "#", "~")


@dataclass(frozen=True)
class Dependency:
    ref: str
    record: str
    record_type: str
    store: str  # "signed" or "authored"
    review_status: str
    field: str
    content_hash: str | None = None
    stale: bool | None = None  # None: no hash recorded, or nothing to compare it with
    view: str = "current"  # "current" or "as_signed"

    def row(self) -> dict[str, Any]:
        return {"ref": self.ref, "record": self.record, "type": self.record_type, "store": self.store,
                "review_status": self.review_status, "field": self.field, "stale": self.stale,
                "view": self.view}


def _refs(value: Any, path: str) -> Iterator[tuple[str, str]]:
    """Every string in a record that parses as an upstream ref, with where it sits."""
    if isinstance(value, str):
        try:
            parse_ref(value)
        except InvalidRef:
            return
        yield value, path
    elif isinstance(value, dict):
        for key, inner in value.items():
            yield from _refs(inner, f"{path}.{key}" if path else str(key))
    elif isinstance(value, (list, tuple)):
        for index, inner in enumerate(value):
            yield from _refs(inner, f"{path}[{index}]")


def _related(ref: str, other: str) -> str | None:
    """How `other` stands to `ref`: the same, a part of it, or the whole it is part of."""
    if other == ref:
        return "names it"
    if other.startswith(tuple(ref + s for s in SEPARATORS)):
        return "names a part of it"
    if ref.startswith(tuple(other + s for s in SEPARATORS)):
        return "names the whole it is part of"
    return None


@dataclass
class DependencyIndex:
    pin: str
    by_ref: dict[str, list[Dependency]] = field(default_factory=lambda: defaultdict(list))
    #: chunk ref -> (provision ref, extraction, certainty) for every provision it cites
    citing: dict[str, list[tuple[str, str, str | None]]] = field(default_factory=dict)

    def add(self, dep: Dependency) -> None:
        self.by_ref[dep.ref].append(dep)

    def all(self, view: str | None = None) -> list[Dependency]:
        return [d for deps in self.by_ref.values() for d in deps if view is None or d.view == view]

    def touching(self, ref: str, view: str = "current") -> list[dict[str, Any]]:
        """Every dependency on `ref`, a part of it or the whole it is part of."""
        out = []
        for other, deps in self.by_ref.items():
            how = _related(ref, other)
            if how:
                out += [{**d.row(), "how": how} for d in deps if d.view == view]
        return sorted(out, key=lambda r: (r["record"], r["field"]))

    def via_manual(self, ref: str, view: str = "current") -> list[dict[str, Any]]:
        """Records resting on a Manual passage that cites `ref` (or a part of it, or its
        whole), each hop carrying upstream's extraction and certainty unchanged."""
        out = []
        for chunk, cited in self.citing.items():
            hops = [(p, e, c) for p, e, c in cited if _related(ref, p)]
            if not hops:
                continue
            deps = [d for d in self.by_ref.get(chunk, ()) if d.view == view]
            for provision, extraction, certainty in hops:
                out += [{**d.row(), "passage": chunk, "cites": provision, "extraction": extraction,
                         "certainty": certainty} for d in deps]
        return sorted(out, key=lambda r: (r["record"], r["passage"], r["cites"]))

    def records(self, rows: list[dict[str, Any]]) -> list[str]:
        return sorted({r["record"] for r in rows})

    def summary(self) -> dict[str, Any]:
        current, signed = self.all("current"), self.all("as_signed")
        current_keys = {(d.ref, d.record, d.field) for d in current}
        history = [d for d in signed if (d.ref, d.record, d.field) not in current_keys]
        return {
            "pin": self.pin,
            "refs": len({d.ref for d in current}),
            "dependencies": len(current),
            "records": len({d.record for d in current}),
            "by_type": dict(sorted(Counter(d.record_type for d in current).items())),
            "by_status": dict(sorted(Counter(d.review_status for d in current).items())),
            "by_source": dict(sorted(Counter(_source(d.ref) for d in current).items())),
            "stale": sorted({d.record for d in current if d.stale}),
            "history_only": len(history),
        }


def _source(ref: str) -> str:
    return {"TMM": "manual", "TMA1995": "act", "TMR1995": "regulations"}.get(ref.split("/", 1)[0], "case")


def _hash_state(corpus: Corpus, ref: str, recorded: Any) -> bool | None:
    from tm_knowledge.stage0.harness import _passage

    if not isinstance(recorded, str):
        return None
    passage = _passage(corpus, ref)
    if passage is None or not passage.content_hash:
        return None
    return passage.content_hash != recorded


def _record(index: DependencyIndex, corpus: Corpus, record: dict[str, Any], envelope: dict[str, Any] | None,
            *, record_type: str, store: str, status: str, view: str) -> None:
    rid = str(record.get("id"))
    signed_hash = record.get("source_content_hash")
    for ref, path in _refs(record, ""):
        recorded = signed_hash if path == "source_ref" else None
        index.add(Dependency(ref, rid, record_type, store, status, path, recorded if isinstance(recorded, str)
                             else None, _hash_state(corpus, ref, recorded), view))
    for n, item in enumerate((envelope or {}).get("evidence") or ()):
        ref = item.get("ref")
        if isinstance(ref, str):
            recorded = item.get("content_hash")
            index.add(Dependency(ref, rid, record_type, store, status, f"evidence[{n}]",
                                 recorded if isinstance(recorded, str) else None,
                                 _hash_state(corpus, ref, recorded), view))


def build(corpus: Corpus, gold: Any = None, authored: Any = None) -> DependencyIndex:
    """The index over both stores, both views, and the Manual's citations of provisions."""
    from tm_knowledge.authored import corrections as corrections_module
    from tm_knowledge.authored import definitions as definitions_module
    from tm_knowledge.authored import procedure
    from tm_knowledge.authored import store as authored_store
    from tm_knowledge.stage0 import goldset

    gold = gold if gold is not None else goldset.load()
    authored = authored if authored is not None else authored_store.load()
    corrections = corrections_module.load(authored.root, gold=gold, authored=authored)
    definitions = definitions_module.load(authored.root, gold=gold, authored=authored)
    # The structured legal tests and process templates (Package 4, ADR-0142) quote their
    # units and passages as every other record does, so they rest on them too.
    tests = procedure.load_tests(authored.root, gold=gold, authored=authored)
    processes = procedure.load_processes(authored.root, gold=gold, authored=authored)
    index = DependencyIndex(pin=corpus.pin.commit)

    for view, signed in (("current", corrections_module.served_gold(gold, corrections)), ("as_signed", gold)):
        for record_type, record in signed.all_records():
            _record(index, corpus, record, None, record_type=record_type, store="signed",
                    status="approved", view=view)
    for entry in authored.all_entries():
        if entry.sound:
            _record(index, corpus, entry.record, entry.envelope, record_type=entry.record_type,
                    store="authored", status=entry.review_status, view="current")
    for kind, found in (("definition", definitions.sound), ("correction", corrections.sound),
                        ("legal_test", tests.sound), ("process", processes.sound)):
        for entry in found:
            status = str((entry.envelope or {}).get("review_status") or "unknown")
            _record(index, corpus, entry.record, entry.envelope, record_type=kind, store="authored",
                    status=status, view="current")

    for chunk in corpus.chunks.values():
        if chunk.provisions:
            index.citing[chunk.chunk_ref] = [(e.id, e.extraction, e.certainty) for e in chunk.provisions]
    return index


def coverage_by_part(corpus: Corpus, index: DependencyIndex, in_graph: set[str]) -> list[dict[str, Any]]:
    """One row per Part of the Manual (R10): its chunks, how many the source graph holds,
    and the distinct records of each kind resting on it in the current view. Every
    chunk is searchable whatever this says; a 0 is no recorded record, not no content."""
    from tm_knowledge.dashboard import views

    chunks: dict[str, list[str]] = defaultdict(list)
    titles: dict[str, str] = {}
    for chunk in corpus.chunks.values():
        part = views.manual_part(chunk.chunk_ref)
        if part:
            chunks[part].append(chunk.chunk_ref)
            if chunk.heading_path and part not in titles:
                titles[part] = chunk.heading_path[0]
    resting: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for dep in index.all("current"):
        part = views.manual_part(dep.ref) if dep.ref.startswith("TMM/") else None
        if not part:
            continue
        resting[part][dep.record_type].add(dep.record)
        if dep.store == "signed":
            resting[part]["signed"].add(dep.record)

    def order(part: str) -> tuple[int, str]:
        import re

        match = re.match(r"Part(\d+)(.*)", part)
        return (int(match.group(1)), match.group(2)) if match else (999, part)

    rows = []
    for part in sorted(chunks, key=order):
        held = resting.get(part, {})
        rows.append({
            "part": part, "title": titles.get(part, ""), "chunks": len(chunks[part]),
            "in_graph": sum(1 for ref in chunks[part] if ref in in_graph),
            "concepts": len(held.get("gold_concept", ())), "relationships": len(held.get("gold_relationship", ())),
            "definitions": len(held.get("definition", ())), "signed": len(held.get("signed", ())),
        })
    return rows

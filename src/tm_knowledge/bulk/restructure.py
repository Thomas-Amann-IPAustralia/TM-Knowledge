"""Apply the structure review (ADR-0131): an agent session's ledger of judgements.

The owner, on 2026-10-09: *"Not having elements connect seems like a bit of a cop out.
Similarly 'is related to' is about as non-descript as you can get. … Apply common sense to
the structures and ensure that the information is represented correctly and accurately."*

`data/derived/audit/restructure.yaml` is the S029 agent's answer, a judgement per line,
and this module turns it into records — checked first, the way the edge audit's verdicts
are (`bulk.audit`), and written only with `--write`:

- **edges** — a machine-written relationship re-read as the triple the ledger gives (same
  id, same sentence; the first reading kept in `alternatives_considered`) or withdrawn into
  `authored/retired-ids.yaml` with the ledger's reason. A re-read must pass every check a
  new relationship passes: a defined predicate, two concepts the ontology holds, a sentence
  naming any concept the re-read brings in, no "kind of" beside a "not the same as", ends
  that are kinds the predicate joins (`predicates.off_schema`), and no triple another record
  already states — that last one withdraws it in the other record's favour.
- **new_edges** — a relationship from a passage that states it, the quote located verbatim.
- **types** — a concept moved to the kind it is.
- **concepts** — an authored concept's fields changed (a relabel).
- **corrections** — a signed concept's list fields changed outside the signature (ADR-0122).

Every record written carries the session's stamp, `unreviewed`, and the ruling. Nothing
here calls a model, and nothing here decides: the ledger decides, and the checks refuse.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.authored import corrections as corrections_module
from tm_knowledge.authored import store as authored_store
from tm_knowledge.bulk import jobs
from tm_knowledge.ontology import hygiene
from tm_knowledge.ontology.predicates import PREDICATES, RETIRED, off_schema

__all__ = ["LEDGER_PATH", "REPORT_PATH", "Plan", "apply", "load_ledger", "plan", "render"]

LEDGER_PATH = jobs.REPO_ROOT / "data" / "derived" / "audit" / "restructure.yaml"
REPORT_PATH = jobs.REPO_ROOT / "data" / "derived" / "reports" / "restructure.md"


@dataclass
class Plan:
    ledger: dict[str, Any]
    rereads: dict[str, dict[str, Any]] = field(default_factory=dict)
    withdrawn: list[dict[str, Any]] = field(default_factory=list)
    new_edges: list[dict[str, Any]] = field(default_factory=list)
    types: dict[str, dict[str, Any]] = field(default_factory=dict)
    concepts: dict[str, dict[str, Any]] = field(default_factory=dict)
    corrections: list[dict[str, Any]] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)
    #: Lines an earlier run already applied.
    done: int = 0
    #: (edge, old triple, new triple or None, why) for the report.
    log: list[tuple[str, tuple[str, str, str], tuple[str, str, str] | None, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.refused


def load_ledger(path: Path | None = None) -> dict[str, Any]:
    path = path or LEDGER_PATH
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _triple(record: dict[str, Any]) -> tuple[str, str, str]:
    return str(record.get("subject")), str(record.get("predicate")), str(record.get("object"))


def _stamp(ledger: dict[str, Any], *, evidence: list[dict[str, Any]], basis: str, reasoning: str,
           alternatives: list[str], check: str, confidence: float) -> dict[str, Any]:
    return {
        "review_status": "unreviewed",
        "authored_by": str(ledger["authored_by"]),
        "authored_date": str(ledger.get("date") or date.today().isoformat()),
        "authoring_basis": basis,
        "evidence": evidence,
        "confidence": confidence,
        "reasoning": reasoning,
        "alternatives_considered": alternatives,
        "expert_should_check": check,
    }


def _first(envelope: dict[str, Any], what: str) -> str:
    """The reading a re-read replaces, for `alternatives_considered`."""
    return (f"As first written by {envelope.get('authored_by')} on {envelope.get('authored_date')}: {what}"
            + (f" — {envelope.get('reasoning')}" if envelope.get("reasoning") else ""))


def _relabelled(ledger: dict[str, Any], quote: str) -> set[str]:
    """Concepts the ledger relabels whose new labels the quote uses — recognition still
    holds their old labels until the ledger is written."""
    text = quote.casefold()
    out = set()
    for row in ledger.get("concepts") or ():
        labels = [row["set"].get("pref_label"), *(row["set"].get("alt_labels") or ())]
        if any(label and str(label).casefold() in text for label in labels):
            out.add(str(row["concept"]))
    return out


def _ours(envelope: Any, ledger: dict[str, Any]) -> bool:
    """Whether a record carries this ledger's stamp — written by an earlier run of it."""
    return bool(envelope) and str(envelope.get("authored_by")) == str(ledger["authored_by"])


def _replaced_here(ctx: jobs.Context, edge: str, ledger: dict[str, Any]) -> bool:
    meta = ctx.authored.retired_ids.get(edge) or {}
    return str(meta.get("ruling", "")).startswith(str(ledger["ruling"]))


def kinds_after(ctx: jobs.Context, ledger: dict[str, Any]) -> dict[str, str]:
    """Concept id -> kind, with the ledger's re-typings applied."""
    kinds = {cid: (c.group or "") for cid, c in ctx.links.concepts.items()}
    for row in ledger.get("types") or ():
        kinds[str(row["concept"])] = str(row["type"])
    return kinds


def _refusal(ctx: jobs.Context, kinds: dict[str, str], new: tuple[str, str, str], named: set[str],
             affirmed: dict[tuple[str, str], Any]) -> str | None:
    subject, predicate, obj = new
    if predicate in RETIRED:
        return f"{predicate!r} is retired"
    if predicate not in PREDICATES:
        return f"{predicate!r} is not in the relation dictionary"
    if subject == obj:
        return "it relates a concept to itself"
    ends = [x for x in (subject, obj) if x.startswith("GC-")]
    if any(x not in ctx.links.concepts for x in ends):
        return "it names a concept the ontology does not hold"
    if not set(ends) <= named:
        return f"the sentence does not name {sorted(set(ends) - named)}"
    clash = hygiene.kind_of_clashes(ctx.links.concepts, [{"id": "(new)", "subject": subject,
                                                          "predicate": predicate, "object": obj}], affirmed)
    if clash and not clash[0].affirmed:
        return f"a kind-of beside a near-miss ({clash[0].describe()})"
    why = off_schema(subject, predicate, obj, kinds)
    if why:
        return why
    return None


def plan(ctx: jobs.Context, ledger: dict[str, Any]) -> Plan:
    """Check every line of the ledger and decide what it writes. Nothing is written here."""
    out = Plan(ledger=ledger)
    kinds = kinds_after(ctx, ledger)
    affirmed = hygiene.affirmations(ctx.authored.root)
    records = {e.record_id: e for e in ctx.authored.of("gold_relationship") if e.sound}
    existing: dict[tuple[str, str, str], str] = {}
    for rows in (ctx.gold["gold_relationship"], ctx.authored["gold_relationship"]):
        for record in rows:
            existing.setdefault(_triple(record), str(record["id"]))
    today = str(ledger.get("date") or date.today().isoformat())

    seen: set[str] = set()
    for row in ledger.get("edges") or ():
        edge = str(row["edge"])
        if edge in seen:
            out.refused.append(f"{edge}: two lines in the ledger")
            continue
        seen.add(edge)
        entry = records.get(edge)
        if entry is None:
            if edge in ctx.authored.retired_ids and "withdraw" in row or _replaced_here(ctx, edge, ledger):
                out.done += 1  # applied by an earlier run
            else:
                out.refused.append(f"{edge}: not a sound machine-written relationship")
            continue
        old = _triple(entry.record)
        if "to" in row and old == tuple(str(x) for x in row["to"]) and _ours(entry.envelope, ledger):
            out.done += 1
            continue
        if existing.get(old) == edge:
            del existing[old]
        if "withdraw" in row:
            out.withdrawn.append({"id": edge, "reason": str(row["withdraw"])})
            out.log.append((edge, old, None, str(row["withdraw"])))
            continue
        new = tuple(str(x) for x in row["to"])
        named = jobs._quote_names(ctx, str(entry.record.get("supporting_text") or "")) | {old[0], old[2]}
        problem = _refusal(ctx, kinds, new, named, affirmed)  # type: ignore[arg-type]
        if problem:
            out.refused.append(f"{edge} → {' '.join(new)}: {problem}")
            continue
        duplicate = existing.get(new)  # type: ignore[arg-type]
        if duplicate and duplicate != edge:
            reason = f"Re-read as {' '.join(new)}, which {duplicate} already states. {row.get('why', '')}".strip()
            out.withdrawn.append({"id": edge, "reason": reason, "replaced_by": duplicate})
            out.log.append((edge, old, new, f"withdrawn: {duplicate} states it"))  # type: ignore[arg-type]
            continue
        existing[new] = edge  # type: ignore[index]
        envelope = dict(entry.envelope or {})
        record: dict[str, Any] = {}
        for key, value in entry.record.items():
            record[key] = value
        subject, predicate, obj = new
        record.update({"subject": subject, "predicate": predicate, "object": obj,
                       "tier": 2 if predicate == "broader" else 3})
        note = (f"Re-read on {today} in the structure review (ADR-0131): was {old[0]} {old[1]} {old[2]}.")
        record["notes"] = (str(record["notes"]) + " " + note) if record.get("notes") else note
        record["authored"] = _stamp(
            ledger, evidence=list(envelope.get("evidence") or []),
            basis=str(envelope.get("authoring_basis") or "corpus_inferred"),
            reasoning=str(row.get("why") or ""),
            alternatives=[_first(envelope, " ".join(old))],
            check="Whether the sentence states this relationship, read the way the predicate reads.",
            confidence=float(row.get("confidence", 0.8)),
        )
        out.rereads[edge] = record
        out.log.append((edge, old, new, str(row.get("why") or "")))  # type: ignore[arg-type]

    # Every machine-written edge on a retired predicate must have a line.
    for edge, entry in records.items():
        if str(entry.record.get("predicate")) in RETIRED and edge not in seen:
            out.refused.append(f"{edge}: uses retired {entry.record.get('predicate')!r} and the ledger has no line")

    number = jobs.next_number("GR")
    for row in ledger.get("new_edges") or ():
        new = (str(row["subject"]), str(row["predicate"]), str(row["object"]))
        found = jobs.evidence(ctx.corpus, str(row["ref"]), str(row["quote"]))
        if found is None:
            out.refused.append(f"new {' '.join(new)}: the quote does not occur in {row['ref']}")
            continue
        named = (jobs._quote_names(ctx, found["quote"]) | {x for x in new if not x.startswith("GC-")}
                 | _relabelled(ledger, found["quote"]))
        problem = _refusal(ctx, kinds, new, named, affirmed)
        if problem:
            out.refused.append(f"new {' '.join(new)}: {problem}")
            continue
        if new in existing:
            held_new = records.get(existing[new])
            if held_new is not None and _ours(held_new.envelope, ledger):
                out.done += 1
            else:
                out.refused.append(f"new {' '.join(new)}: {existing[new]} already states it")
            continue
        identifier = f"GR-{number:04d}"
        number += 1
        existing[new] = identifier
        out.new_edges.append({
            "id": identifier, "subject": new[0], "predicate": new[1], "object": new[2],
            "source_ref": found["ref"], "supporting_text": found["quote"], "span": found["span"],
            "source_content_hash": found["content_hash"], "tier": 2 if new[1] == "broader" else 3,
            "modality": None, "approved_by": None, "approved_date": None,
            "authored": _stamp(ledger, evidence=[found], basis=str(row.get("basis") or "corpus_explicit"),
                               reasoning=str(row["why"]), alternatives=[],
                               check="Whether the passage states this relationship.",
                               confidence=float(row.get("confidence", 0.8))),
        })
        out.log.append((identifier, ("", "", ""), new, str(row["why"])))

    typing = {str(e.record.get("concept")): e for e in ctx.authored.of("concept_type") if e.sound}
    for row in ledger.get("types") or ():
        cid, kind = str(row["concept"]), str(row["type"])
        entry = typing.get(cid)
        if entry is None:
            out.refused.append(f"type {cid}: no machine-written typing to re-type")
            continue
        if str(entry.record.get("type")) == kind and _ours(entry.envelope, ledger):
            out.done += 1
            continue
        envelope = dict(entry.envelope or {})
        record = dict(entry.record)
        was = str(record.get("type"))
        record["type"] = kind
        record["authored"] = _stamp(
            ledger, evidence=list(envelope.get("evidence") or []),
            basis=str(envelope.get("authoring_basis") or "corpus_inferred"), reasoning=str(row["why"]),
            alternatives=[_first(envelope, was)],
            check=str(row.get("check") or f"Whether {cid} is a {kind.replace('_', ' ')}."),
            confidence=float(row.get("confidence", 0.8)),
        )
        out.types[entry.record_id] = record

    held = {e.record_id: e for e in ctx.authored.of("gold_concept") if e.sound}
    for row in ledger.get("concepts") or ():
        cid = str(row["concept"])
        entry = held.get(cid)
        if entry is None:
            out.refused.append(f"concept {cid}: not a machine-written concept (a signed one takes a correction)")
            continue
        if all(entry.record.get(k) == v for k, v in row["set"].items()) and _ours(entry.envelope, ledger):
            out.done += 1
            continue
        envelope = dict(entry.envelope or {})
        record = dict(entry.record)
        before = {k: record.get(k) for k in row["set"]}
        record.update(row["set"])
        evidence = list(envelope.get("evidence") or [])
        for item in row.get("evidence") or ():
            found = jobs.evidence(ctx.corpus, str(item["ref"]), str(item["quote"]))
            if found is None:
                out.refused.append(f"concept {cid}: the quote does not occur in {item['ref']}")
                continue
            evidence.append(found)
        record["authored"] = _stamp(
            ledger, evidence=evidence, basis=str(envelope.get("authoring_basis") or "corpus_inferred"),
            reasoning=str(row["why"]), alternatives=[_first(envelope, repr(before))],
            check=str(row.get("check") or "Whether the concept as now labelled is what the corpus uses."),
            confidence=float(row.get("confidence", 0.8)),
        )
        out.concepts[cid] = record

    number = jobs.next_number("GK")
    made = [c.record for c in corrections_module.load(ctx.authored.root).sound]
    for row in ledger.get("corrections") or ():
        if any(str(c.get("corrects")) == str(row["corrects"]) and c.get("remove") == row.get("remove")
               and str(c.get("ruling", "")).startswith(str(ledger["ruling"])) for c in made):
            out.done += 1
            continue
        evidence = []
        for item in row.get("evidence") or ():
            found = jobs.evidence(ctx.corpus, str(item["ref"]), str(item["quote"]))
            if found is None:
                out.refused.append(f"correction of {row['corrects']}: the quote does not occur in {item['ref']}")
            else:
                evidence.append(found)
        record = {"id": f"GK-{number:04d}", "corrects": str(row["corrects"]), "record_type": "gold_concept"}
        number += 1
        for key in ("remove", "add"):
            if row.get(key):
                record[key] = row[key]
        record.update({
            "ruling": f"{ledger['ruling']}#{row.get('item', 'CHAT-0073')}", "notes": row.get("notes"),
            "approved_by": None, "approved_date": None,
            "authored": _stamp(ledger, evidence=evidence, basis=str(row.get("basis") or "corpus_inferred"),
                               reasoning=str(row["why"]),
                               alternatives=list(row.get("alternatives") or []),
                               check=str(row.get("check") or "Whether the signed link was meant as a kind-of."),
                               confidence=float(row.get("confidence", 0.85))),
        })
        out.corrections.append(record)
    return out


def apply(result: Plan, root: Path | None = None) -> dict[str, int]:
    """Write what the plan decided. Refuses to write a plan with refusals in it."""
    if not result.ok:
        raise ValueError("the plan has refusals; fix the ledger first:\n" + "\n".join(result.refused))
    root = root or authored_store.AUTHORED_DIR
    ruling = f"{result.ledger['ruling']}#CHAT-0072"
    removed = {row["id"] for row in result.withdrawn}
    jobs.rewrite_records(root / "relationships.yaml", replace=result.rereads, remove=removed)
    if result.new_edges:
        jobs.append_records(root / "relationships.yaml", result.new_edges, "")
    if result.types:
        jobs.rewrite_records(root / "concept-types.yaml", replace=result.types)
    if result.concepts:
        ids = {r["id"]: r for r in result.concepts.values()}
        jobs.rewrite_records(root / "concepts.yaml", replace=ids)
    if result.corrections:
        jobs.append_records(root / "corrections.yaml", result.corrections, "")
    if result.withdrawn:
        today = str(result.ledger.get("date") or date.today().isoformat())
        rows = []
        for row in result.withdrawn:
            out: dict[str, Any] = {"id": row["id"], "record_type": "gold_relationship", "retired_on": today,
                                   "reason": f"Structure review (ADR-0131): {row['reason']}"}
            if row.get("replaced_by"):
                out["replaced_by"] = row["replaced_by"]
            out["ruling"] = ruling
            rows.append(out)
        jobs.append_records(root / authored_store.RETIRED_IDS_FILE, rows, "")
    return {"reread": len(result.rereads), "withdrawn": len(result.withdrawn), "new": len(result.new_edges),
            "types": len(result.types), "concepts": len(result.concepts), "corrections": len(result.corrections)}


def render(result: Plan, labels: dict[str, str]) -> str:
    """The report: what each line did, for a reader checking the judgements."""
    def name(ref: str) -> str:
        return labels.get(ref, ref)

    def triple(t: tuple[str, str, str]) -> str:
        return f"{name(t[0])} — *{t[1]}* → {name(t[2])}"

    rereads = [x for x in result.log if x[2] is not None and x[1][0]]
    withdrawn = [x for x in result.log if x[2] is None]
    added = [x for x in result.log if not x[1][0]]
    by_predicate = Counter(x[2][1] for x in rereads if x[2] and not x[3].startswith("withdrawn:"))
    lines = [
        "<!-- Generated by `tmk-bulk restructure --write` from data/derived/audit/restructure.yaml. "
        "Do not hand-edit. -->",
        "",
        "# The structure review (ADR-0131)",
        "",
        "The owner, on 2026-10-09: *\"Not having elements connect seems like a bit of a cop out. "
        "Similarly 'is related to' is about as non-descript as you can get.\"* Every line below is an "
        "agent session's judgement (`claude-code-agent-S029`), machine-written and unreviewed.",
        "",
        f"- **{len(result.rereads)} relationships re-read** as what their sentence states — "
        + ", ".join(f"{p} {n}" for p, n in by_predicate.most_common()) + ".",
        f"- **{len(result.withdrawn)} withdrawn** — the sentence mentions both ideas but states no relation "
        "between them, or a re-read landed on a triple another record already states.",
        f"- **{len(result.new_edges)} new** relationships, each from a passage that states it.",
        f"- **{len(result.types)} concepts re-typed**, **{len(result.concepts)} relabelled**, "
        f"**{len(result.corrections)} signed \"kind of\" links corrected** outside the signature.",
        "",
        "## Re-read",
        "",
        "| edge | was | now | why |",
        "|---|---|---|---|",
    ]
    for edge, old, new, why in rereads:
        lines.append(f"| {edge} | {triple(old)} | {triple(new) if new else '—'} | {why.replace('|', '/')} |")
    lines += ["", "## Withdrawn", "", "| edge | was | why |", "|---|---|---|"]
    for edge, old, _new, why in withdrawn:
        lines.append(f"| {edge} | {triple(old)} | {why.replace('|', '/')} |")
    lines += ["", "## New", "", "| edge | relationship | why |", "|---|---|---|"]
    for edge, _old, new, why in added:
        lines.append(f"| {edge} | {triple(new)} | {why.replace('|', '/')} |")  # type: ignore[arg-type]
    lines += ["", "## Re-typed", "", "| concept | kind | why |", "|---|---|---|"]
    for row in result.ledger.get("types") or ():
        lines.append(f"| {name(str(row['concept']))} | {row['type'].replace('_', ' ')} | {str(row['why']).replace('|', '/')} |")
    if result.corrections:
        lines += ["", "## Signed links corrected", "", "| correction | concept | withdrawn | why |", "|---|---|---|---|"]
        for record in result.corrections:
            gone = "; ".join(f"{k} {', '.join(name(v) for v in vs)}" for k, vs in (record.get("remove") or {}).items())
            lines.append(f"| {record['id']} | {name(record['corrects'])} | {gone} | "
                         f"{record['authored']['reasoning'].replace('|', '/')} |")
    return "\n".join(lines) + "\n"

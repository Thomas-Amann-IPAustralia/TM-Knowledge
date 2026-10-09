"""Act on a second model's audit of the machine-written relationships (D5, ADR-0127).

`tmk-bulk run audit` asks a second model — the owner chose Gemini 3.1 Pro (ADR-0125) —
whether each machine-written relationship's sentence supports it, and writes the
verdicts to `data/derived/audit/edges.yaml`. The quote the owner approved promised "a
corrected reading for wrong ones"; his rule for a known defect is "correct known
defects" (D2). So this module turns a verdict of *wrong* into one of two changes:

- **re-read** — the corrected triple replaces the record's when it passes every check a
  new relationship must pass: a defined predicate, two concepts the ontology holds (or
  the provision the record already had as its subject), a sentence that names each
  concept — or, for one the first reading already used, two models reading the sentence
  as about it — no "kind of" refused beside a near-miss (D4), and no triple another
  record already states. The record keeps its id and its sentence; the reading is now
  the second model's, stamped with that model, and the first reading is kept in
  `alternatives_considered`.
- **withdrawn** — otherwise, into `authored/retired-ids.yaml`, with the second model's
  reason and, where another record already states the corrected triple, that record.

A verdict on a record serving in place of a signed one (`authored/corrections.yaml`) is
reported, never applied: that reading is the expert's, corrected only where the owner
ruled, and only a person overrules an expert. A verdict of *vague* or *sound* changes
nothing. Nor does a correction that only widens
one end to a concept it is a kind of (the s 39 ground to "ground for rejection"): the
record already entails it, and the narrower end is what the passage is about. A verdict
on a record that has changed since it was judged is skipped: it was about something else.

Nothing here calls a model, and nothing here judges: every change is a verdict the
second model gave, applied only when the checks pass.
"""

from __future__ import annotations

import math
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
from tm_knowledge.ontology.predicates import PREDICATES

__all__ = ["REPORT_PATH", "RULING", "Action", "apply", "load_verdicts", "plan", "render"]

REPORT_PATH = jobs.REPO_ROOT / "data" / "derived" / "reports" / "edge-audit.md"
#: The rulings a change rests on: the D5 quote approved on 2026-10-09, and D2's
#: "correct known defects".
RULING = "review/rulings/2026-10-09-chat-approvals.yaml#D5"


@dataclass
class Action:
    edge: str
    kind: str  # "reread" | "withdraw" | "keep" | "skip"
    why: str
    verdict: dict[str, Any] = field(default_factory=dict)
    record: dict[str, Any] | None = None  # the new record, for a re-read
    duplicate_of: str | None = None


def load_verdicts(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or jobs.AUDIT_PATH
    if not path.exists():
        return []
    return list((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("verdicts") or ())


def _triple(record: dict[str, Any]) -> tuple[str, str, str]:
    return str(record.get("subject")), str(record.get("predicate")), str(record.get("object"))


def _existing(ctx: jobs.Context) -> dict[tuple[str, str, str], str]:
    """Every triple a serving record states -> its id, both stores."""
    out: dict[tuple[str, str, str], str] = {}
    for records in (ctx.gold["gold_relationship"], ctx.authored["gold_relationship"]):
        for record in records:
            out.setdefault(_triple(record), str(record["id"]))
    return out


def _broader(ctx: jobs.Context) -> dict[str, set[str]]:
    """Each concept -> every concept it is a kind of, transitively, both stores."""
    up: dict[str, set[str]] = {}
    for records in (ctx.gold["gold_relationship"], ctx.authored["gold_relationship"]):
        for record in records:
            if record.get("predicate") == "broader":
                up.setdefault(str(record["subject"]), set()).add(str(record["object"]))
    closed: dict[str, set[str]] = {}
    for start, direct in up.items():
        seen: set[str] = set()
        stack = list(direct)
        while stack:
            node = stack.pop()
            if node not in seen:
                seen.add(node)
                stack.extend(up.get(node, ()))
        closed[start] = seen
    return closed


def _generalises(old: tuple[str, str, str], new: tuple[str, str, str], broader: dict[str, set[str]]) -> str | None:
    """The end the correction only widens, if that is all it does: same predicate, one end
    the same, the other replaced by a concept the original end is a kind of."""
    if old[1] != new[1]:
        return None
    if old[0] == new[0] and new[2] in broader.get(old[2], ()):
        return f"{old[2]} to {new[2]}"
    if old[2] == new[2] and new[0] in broader.get(old[0], ()):
        return f"{old[0]} to {new[0]}"
    return None


def plan(ctx: jobs.Context, verdicts: list[dict[str, Any]]) -> list[Action]:
    """What each verdict of *wrong* does, checked and decided before anything is written."""
    records = {e.record_id: e for e in ctx.authored.of("gold_relationship") if e.sound}
    existing = _existing(ctx)
    broader = _broader(ctx)
    affirmed = hygiene.affirmations(ctx.authored.root)
    # A record serving in place of a signed one carries the expert's reading, corrected
    # only where the owner ruled (A2, D1): a second model may dispute it, never undo it.
    stands_for = {replacement: signed for signed, replacement in
                  corrections_module.load(ctx.authored.root).replacements().items()}
    actions: list[Action] = []
    for v in verdicts:
        if v.get("verdict") != "wrong":
            continue
        edge = str(v["edge"])
        entry = records.get(edge)
        if entry is None:
            actions.append(Action(edge, "skip", "no longer held", v))
            continue
        record = entry.record
        judged = v.get("judged") or {}
        if judged and tuple(judged.get(k) for k in ("subject", "predicate", "object")) != _triple(record):
            actions.append(Action(edge, "skip", "changed since it was judged", v))
            continue
        if edge in stands_for:
            actions.append(Action(edge, "keep", f"it serves in place of signed {stands_for[edge]}, corrected on "
                                                "the owner's ruling; a second model does not overrule a reading an "
                                                "expert signed — for a person", v))
            continue
        corrected = v.get("corrected")
        if v.get("remove") or not corrected:
            actions.append(Action(edge, "withdraw", "the second model found no relationship the sentence supports", v))
            continue
        new = (str(corrected["subject"]), str(corrected["predicate"]), str(corrected["object"]))
        if new == _triple(record):
            actions.append(Action(edge, "skip", "judged wrong but re-read as the same triple", v))
            continue
        widened = _generalises(_triple(record), new, broader)
        if widened:
            # The correction follows from the record by the hierarchy, so it cannot make
            # the record truer; the narrower end is what the passage is about (S027).
            actions.append(Action(edge, "keep", f"its correction only widens {widened}, which the record "
                                                "already entails", v))
            continue
        problem = _refusal(ctx, record, new, affirmed)
        duplicate = existing.get(new)
        if problem:
            actions.append(Action(edge, "withdraw", f"its corrected reading is refused: {problem}", v))
        elif duplicate and duplicate != edge:
            actions.append(Action(edge, "withdraw", f"its corrected reading is what {duplicate} already states",
                                  v, duplicate_of=duplicate))
        else:
            actions.append(Action(edge, "reread", "re-read as the second model corrected it", v,
                                  record=_reread(entry, new, v)))
            existing[new] = edge
    return actions


def _refusal(ctx: jobs.Context, record: dict[str, Any], new: tuple[str, str, str],
             affirmed: dict[tuple[str, str], Any]) -> str | None:
    """Why the corrected triple may not be written, or None. The relate job's own rules."""
    subject, predicate, obj = new
    if predicate not in PREDICATES:
        return f"{predicate!r} is not in the relation dictionary"
    if subject == obj:
        return "it relates a concept to itself"
    ends = [x for x in (subject, obj) if x.startswith("GC-")]
    if any(x not in ctx.links.concepts for x in ends):
        return "it names a concept the ontology does not hold"
    if any(not x.startswith("GC-") and x != str(record.get("subject")) for x in (subject, obj)):
        return "it names a provision the record did not"
    # A concept the first reading already used may stay though the sentence names it only
    # in other words: both models then read the sentence as about it (S027). A concept the
    # correction brings in must be named, as the relate job requires.
    named = jobs._quote_names(ctx, str(record["supporting_text"])) | {str(record.get("subject")),
                                                                      str(record.get("object"))}
    if not set(ends) <= named:
        return "the sentence does not name both concepts"
    clash = hygiene.kind_of_clashes(ctx.links.concepts, [{"id": "(new)", "subject": subject,
                                                          "predicate": predicate, "object": obj}], affirmed)
    if clash and not clash[0].affirmed:
        return f"a kind-of beside a near-miss ({clash[0].describe()})"
    return None


def _reread(entry: authored_store.AuthoredRecord, new: tuple[str, str, str], v: dict[str, Any]) -> dict[str, Any]:
    """The record as the second model read it: same id and sentence, its reading and stamp."""
    old = dict(entry.record)
    envelope = dict(entry.envelope or {})
    subject, predicate, obj = new
    first = (f"As first written by {envelope.get('authored_by')} on {envelope.get('authored_date')}: "
             f"{old['subject']} {old['predicate']} {old['object']}"
             + (f" — {envelope.get('reasoning')}" if envelope.get("reasoning") else ""))
    note = (f"Re-read on {date.today().isoformat()} from a second model's audit ({v.get('model')}, "
            f"{v.get('prompt_version', 'audit-v1')}): was {old['subject']} {old['predicate']} {old['object']}.")
    record: dict[str, Any] = {}
    for key, value in old.items():
        if key == "notes":
            continue
        record[key] = value
        if key == "modality":
            record["notes"] = (str(old["notes"]) + " " + note) if old.get("notes") else note
    record.update({"subject": subject, "predicate": predicate, "object": obj,
                   "tier": 2 if predicate in ("broader", "related") else 3})
    if predicate in ("broader", "related"):
        record["modality"] = None
    record["authored"] = {
        "review_status": "unreviewed",
        "authored_by": str(v.get("model")),
        "authored_date": date.today().isoformat(),
        "authoring_basis": envelope.get("authoring_basis") or "corpus_inferred",
        "evidence": envelope.get("evidence") or [],
        # Its own rating, or none: Gemini returned none, and a default would read as one (F6).
        "confidence": float(v["confidence"]) if isinstance(v.get("confidence"), (int, float)) else None,
        "reasoning": str(v.get("reason") or "(no reason given)"),
        "alternatives_considered": [first],
        "expert_should_check": ("Whether the second model's reading is right where the first model's was "
                                "judged wrong; both read the same sentence."),
    }
    return record


def apply(actions: list[Action], root: Path | None = None) -> dict[str, int]:
    """Write the re-reads and the withdrawals. Returns counts."""
    root = root or authored_store.AUTHORED_DIR
    rereads = {a.edge: a.record for a in actions if a.kind == "reread" and a.record}
    withdrawn = [a for a in actions if a.kind == "withdraw"]
    if rereads or withdrawn:
        jobs.rewrite_records(root / "relationships.yaml", replace=rereads, remove={a.edge for a in withdrawn})
    if withdrawn:
        ledger = root / authored_store.RETIRED_IDS_FILE
        rows = []
        for a in withdrawn:
            row: dict[str, Any] = {
                "id": a.edge, "record_type": "gold_relationship", "retired_on": date.today().isoformat(),
                "reason": (f"A second model ({a.verdict.get('model')}) judged it wrong — "
                           f"{a.verdict.get('reason') or 'no reason given'} — and {a.why}."),
            }
            if a.duplicate_of:
                row["replaced_by"] = a.duplicate_of
            row["ruling"] = RULING
            rows.append(row)
        text = yaml.dump(rows, Dumper=jobs._PlainDumper, sort_keys=False, allow_unicode=True, width=88)
        existing = ledger.read_text(encoding="utf-8") if ledger.exists() else ""
        body = [line for line in existing.splitlines() if line.strip() and not line.lstrip().startswith("#")]
        if body in ([], ["[]"]):  # an empty ledger: keep its comments, start the list
            comments = "".join(line + "\n" for line in existing.splitlines() if line.lstrip().startswith("#"))
            ledger.write_text(comments + text, encoding="utf-8")
        else:
            ledger.write_text(existing.rstrip("\n") + "\n" + text, encoding="utf-8")
    return {"reread": len(rereads), "withdrawn": len(withdrawn)}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """A 95% interval for a proportion, sound at small counts."""
    if n == 0:
        return 0.0, 0.0
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def render(verdicts: list[dict[str, Any]], authors: dict[str, str], predicates: dict[str, str],
           actions: list[Action]) -> str:
    """The audit as a report: verdicts by author and by predicate, intervals, and what was done."""
    by_author: dict[str, Counter[str]] = {}
    by_predicate: dict[str, Counter[str]] = {}
    for v in verdicts:
        by_author.setdefault(authors.get(v["edge"], "?"), Counter())[v["verdict"]] += 1
        by_predicate.setdefault(predicates.get(v["edge"], "?"), Counter())[v["verdict"]] += 1
    total = Counter(v["verdict"] for v in verdicts)
    n = sum(total.values())
    low, high = wilson(total["wrong"], n)
    models = sorted({str(v.get("model")) for v in verdicts})
    lines = [
        "# The edge audit — a second model reads every machine-written relationship",
        "",
        f"{n} relationships, each judged against the sentence it quotes and the relation dictionary by "
        f"`{', '.join(models)}` — a different model from the ones that wrote them (review D5, ADR-0127). "
        "**A model judging models, not a review:** nothing here was read by a trade marks expert, and a "
        "verdict is a second opinion, not a finding of fact.",
        "",
        f"**Sound {total['sound']} · vague {total['vague']} · wrong {total['wrong']}.** Wrong: "
        f"{total['wrong'] / max(n, 1):.1%} (95% interval {low:.1%}–{high:.1%}, Wilson). The S026 hand sample "
        "put it at about 28% of 25 (14–48%).",
        "",
        "## By author",
        "",
        "Counted apart, never summed across authors into a quality score (ADR-0125, F6).",
        "",
        "| Written by | n | sound | vague | wrong | wrong share |",
        "|---|---|---|---|---|---|",
    ]
    for author, counts in sorted(by_author.items()):
        m = sum(counts.values())
        lines.append(f"| `{author}` | {m} | {counts['sound']} | {counts['vague']} | {counts['wrong']} | "
                     f"{counts['wrong'] / max(m, 1):.0%} |")
    lines += ["", "## By predicate", "", "| Predicate | n | sound | vague | wrong |", "|---|---|---|---|---|"]
    for predicate, counts in sorted(by_predicate.items(), key=lambda kv: -sum(kv[1].values())):
        lines.append(f"| `{predicate}` | {sum(counts.values())} | {counts['sound']} | {counts['vague']} | "
                     f"{counts['wrong']} |")
    done = Counter(a.kind for a in actions)
    lines += ["", "## What was done with the wrong ones", "",
              f"**{done['reread']} re-read** as the second model corrected them, **{done['withdraw']} withdrawn**, "
              f"{done['keep']} kept (a correction that only widened an end the record entails, or a record "
              f"serving for a signed one), {done['skip']} skipped. A re-read keeps its id and its sentence, "
              "carries the second model's "
              "stamp, and keeps the first reading in `alternatives_considered`; a withdrawal is in "
              "`authored/retired-ids.yaml` with the reason.", "",
              "| Relationship | Done | Why | Second model's reason |", "|---|---|---|---|"]
    signed = [a for a in actions if a.kind == "keep" and "signed" in a.why]
    if signed:
        table = lines[-2:]
        lines[-2:] = ["## Disputes of a reading an expert signed — for a person", "",
                      "These records serve in place of signed ones, corrected only where the owner ruled. The "
                      "second model judged them wrong; nothing was changed, because only a person overrules "
                      "an expert.", ""]
        for a in sorted(signed, key=lambda a: a.edge):
            reason = " ".join(str(a.verdict.get("reason") or "").split())
            lines.append(f"- `{a.edge}` ({a.why.split(',')[0].removeprefix('it serves in place of ')}): {reason}")
        lines += ["", "## Every wrong verdict and what it did", "", *table]
    for a in sorted(actions, key=lambda a: a.edge):
        reason = " ".join(str(a.verdict.get("reason") or "").split()).replace("|", "/")
        lines.append(f"| `{a.edge}` | {a.kind} | {a.why} | {reason} |")
    return "\n".join(lines) + "\n"

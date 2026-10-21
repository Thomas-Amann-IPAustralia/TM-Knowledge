"""What-ifs: an invented new right, laid over the ontology as it stands (ADR-0149).

A what-if (`scenarios/what-if.yaml`, `FW-`, fictional and fixture-only like a matter or a
scenario) asks where examination practice would need to be read again if a right that does not
exist were created. It differs from a normative scenario (`scenarios.py`) in what it may touch:
a scenario edits a legal test in memory; **a what-if edits nothing.** It names ideas, legal tests,
process steps, provisions and passages that are already records, and every one is read as it is.
Only the premise, the "what if" paragraphs and the questions are new, and they are a machine's,
stamped and never reviewed.

What the site draws is computed here, never in the browser: for each touch point, the records
that would go back to be re-read (the dependency index from its provisions, and the records
quoting the pages its passages sit on), and the connections among its ideas. "No recorded
dependency" is said as such, never as "no impact". The behavioural question (what applicants or
examiners would do) is unknown, as in a scenario, and the result says so.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.config import REPO_ROOT
from tm_knowledge.explain.scenarios import BEHAVIOURAL

__all__ = ["WHATIF_PATH", "STAMP", "BEHAVIOURAL", "WhatIf", "load", "payload"]

WHATIF_PATH = REPO_ROOT / "scenarios" / "what-if.yaml"
STAMP = ("An invented premise, written by a machine and never reviewed by a trade marks expert. No such right exists "
         "and no draft is assumed. It changes nothing in the ontology: every idea, test and passage shown is one already "
         "there, read as it is. It shows where practice would need to be read again; it decides nothing, and only the "
         "Registrar decides whether an application is accepted.")
_REQUIRED = ("id", "fictional", "title", "premise", "written_by", "written_date", "extraction_method", "confidence",
             "review_status", "touchpoints")


@dataclass(frozen=True)
class WhatIf:
    record: dict[str, Any]
    errors: tuple[str, ...] = ()

    @property
    def id(self) -> str:
        return str(self.record.get("id"))


def _check(record: dict[str, Any], corpus: Any, onto: dict[str, Any] | None) -> list[str]:
    from tm_knowledge.stage0.harness import passage_at

    errors = [f"missing {key}" for key in _REQUIRED if key not in record]
    if errors:
        return errors
    if record["fictional"] is not True:
        errors.append("a what-if is fictional: true")
    if record["review_status"] != "unreviewed" or "approved_by" in record:
        errors.append("a what-if is unreviewed, and no one has approved it")
    concepts = {c["id"] for c in onto["concepts"]} if onto else None
    tests = {t["id"] for t in onto["structures"]["tests"]} if onto else None
    steps = ({(p["id"], s["id"]) for p in onto["structures"]["processes"] for s in p.get("steps") or ()}
             if onto else None)
    seen: set[str] = set()
    for point in record["touchpoints"]:
        pid = point.get("id")
        if pid in seen:
            errors.append(f"touch point {pid} twice")
        seen.add(pid)
        for item in point.get("today") or ():
            passage = passage_at(corpus, item["ref"])
            if passage is None:
                errors.append(f"{pid}: {item['ref']} is not in the snapshot")
                continue
            start, end = item.get("span") or (None, None)
            if start is None or passage.text[start:end] != item["quote"]:
                errors.append(f"{pid}: the quote from {item['ref']} is not at its span")
            held = corpus.chunks.get(item["ref"]) or corpus.resolve_provision(item["ref"])
            if getattr(held, "content_hash", None) != item.get("content_hash"):
                errors.append(f"{pid}: {item['ref']} has changed since it was quoted")
        for ref in point.get("provisions") or ():
            if corpus.resolve_provision(ref) is None:
                errors.append(f"{pid}: {ref} is not in the snapshot")
        if concepts is not None:
            errors += [f"{pid}: no idea {c}" for c in point.get("ideas") or () if c not in concepts]
            errors += [f"{pid}: no legal test {t}" for t in point.get("tests") or () if t not in tests]
            errors += [f"{pid}: no step {s['step']} in {s['process']}" for s in point.get("steps") or ()
                       if (s["process"], s["step"]) not in steps]
    return errors


def load(path: Path = WHATIF_PATH, *, corpus: Any = None, onto: dict[str, Any] | None = None) -> list[WhatIf]:
    """Every what-if, each with what is wrong with it. With no corpus, nothing is checked
    against the snapshot; with no ontology, nothing against the records."""
    records = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [WhatIf(r, tuple(_check(r, corpus, onto)) if corpus is not None else ()) for r in records]


def payload(found: list[WhatIf], corpus: Any, onto: dict[str, Any], stability: dict[str, Any]) -> dict[str, Any]:
    """What the site's what-if page draws. A what-if with errors is left out and named."""
    pages = {p["ref"]: p for p in stability["pages"]}
    provisions = stability.get("provisions") or {}
    relations = onto["relations"]
    out, broken = [], []
    for w in found:
        if w.errors:
            broken.append(w.id)
            continue
        points = []
        for point in w.record["touchpoints"]:
            ideas = set(point.get("ideas") or ())
            on_pages = sorted({corpus.chunks[i["ref"]].page_ref for i in point["today"] if i["ref"] in corpus.chunks})
            direct: set[str] = set()
            via: set[str] = set()
            unnamed = []
            for ref in point.get("provisions") or ():
                hit = provisions.get(ref)
                if hit:
                    direct |= set(hit["direct"])
                    via |= set(hit["via_manual"])
                else:
                    unnamed.append(ref)
            for ref in on_pages:
                p = pages.get(ref)
                if p:
                    direct |= {*p["concepts"], *p["relations"], *p["definitions"], *p["corrections"], *(p.get("structures") or ())}
            points.append({
                **point,
                "pages": on_pages,
                "connections": sorted(r["id"] for r in relations if r["s"] in ideas or r["o"] in ideas),
                "recheck": sorted(direct),
                "recheck_via": sorted(via - direct),
                "no_recorded_dependency": unnamed,
            })
        everything = {k: sorted({x for p in points for x in (p[k] if k != "steps" else [f"{s['process']}/{s['step']}" for s in p[k]])})
                      for k in ("ideas", "tests", "steps", "provisions", "pages", "connections", "recheck", "recheck_via")}
        everything["recheck_via"] = sorted(set(everything["recheck_via"]) - set(everything["recheck"]))
        all_ideas = set(everything["ideas"])
        links = [{"id": r["id"], "s": r["s"], "p": r["p"], "o": r["o"]} for r in relations
                 if r["s"] in all_ideas and r["o"] in all_ideas]
        # What rests on each provision today, as Trace a change counts it: what names it, and
        # what rests on a Manual passage citing it.
        rests = {ref: {"direct": len(provisions[ref]["direct"]), "via_manual": len(provisions[ref]["via_manual"]),
                       "passages": len(provisions[ref].get("passages") or ())} if ref in provisions else None
                 for ref in everything["provisions"]}
        out.append({**{k: v for k, v in w.record.items() if k != "touchpoints"}, "touchpoints": points, "links": links,
                    "rests_on_provision": rests,
                    "totals": {k: len(v) for k, v in everything.items()}, "stamp": STAMP, "behavioural": BEHAVIOURAL})
    return {"fictional": True, "stamp": STAMP, "whatifs": out, "left_out": broken}

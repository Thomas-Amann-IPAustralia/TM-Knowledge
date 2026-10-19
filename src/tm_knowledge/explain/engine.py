"""One explanation object per fictional matter, and its text equivalent (A08, A09).

Built from three records and nothing else: the legal test each objection names (`GL-`),
the process template (`GP-`) and the matter (`FM-`). The page's views and the text are
both drawn from the object this returns, so a changed fact changes them together.

The rules it keeps, each held by a test in `tests/unit/test_explain.py`:

1. **Three values, never two.** A condition is recorded as met, recorded as not met, or
   open. Open is "not established from the available facts", never a negative.
2. **An evaluative condition is reported, never made.** It is met or not only where a
   named person's assessment is recorded (the fictional report's examiner); otherwise it
   is for the Registrar to assess.
3. **A "may" stays a "may".** An exception's effect is stated as its kind says: a
   discretion is what the Registrar may do, a bar what the Registrar may not do.
4. **No outcome, no date.** Nothing says an application will be accepted, rejected or
   lapse. A date is repeated where the matter states it and never calculated (A02).
5. **Ask only what changes the explanation.** An unknown fact is asked about only if
   knowing it either way would change the reading.
6. **Practice and law stay apart.** Every source is labelled law (the Act, the
   Regulations) or practice (the Manual).
"""

from __future__ import annotations

from typing import Any

from tm_knowledge.authored import procedure
from tm_knowledge.explain.matters import Matter

__all__ = ["explain", "render_text", "read_test", "position", "evidence_view", "STAMP", "OPEN"]

STAMP = ("Written by a machine from records no trade marks expert has reviewed, for a fictional matter. It explains "
         "what the law and the Manual say and what the report records; it does not decide anything. Only the "
         "Registrar decides whether an application is accepted.")
OPEN = "not established from the available facts"
_MET, _NOT, _OPEN = "met", "not_met", "open"


def _authority(ref: str) -> str:
    return "law" if ref.startswith(("TMA1995/", "TMR1995/")) else "practice"


def _source(element: dict[str, Any]) -> dict[str, str]:
    return {"ref": element["ref"], "quote": element["quote"], "authority": _authority(element["ref"])}


def _leaf(leaf: dict[str, Any], facts: dict[str, Any], assessments: dict[str, Any]) -> dict[str, Any]:
    out = {"id": leaf["id"], "text": leaf["text"], "kind": leaf["kind"], **_source(leaf)}
    if leaf["kind"] == "evaluative":
        found = assessments.get(leaf["id"])
        if found is None:
            return {**out, "state": _OPEN, "why": "for the Registrar to assess; no assessment is recorded"}
        return {**out, "state": _MET if found["value"] else _NOT,
                "why": f"assessed by {found['by']} on {found['recorded']}"}
    found = facts.get(leaf["id"])
    if (found is None or found["value"] is None) and leaf.get("derive") and facts.get("__dates__"):
        found = _compared(leaf["derive"]["not_earlier_than"], facts["__dates__"])
    if found is None or found["value"] is None:
        return {**out, "state": _OPEN, "why": "not known", "ask": leaf.get("ask")}
    return {**out, "state": _MET if found["value"] else _NOT, "why": f"recorded in {found['source']}"}


def _compared(paths: list[str], dates: dict[str, str | None]) -> dict[str, Any] | None:
    """A fact the matter's stated dates settle: the first is not earlier than the second.
    A comparison of two dates the matter states, never a date calculated."""
    first, second = (dates.get(path) for path in paths)
    if not first or not second:
        return None
    return {"value": first >= second, "source": f"the dates stated: {first} against {second}"}


def _dates(objection: dict[str, Any], application: dict[str, Any] | None) -> dict[str, str | None]:
    application = application or {}
    return {"application.priority_date": application.get("priority_date"),
            "application.filing_date": application.get("filing_date"),
            "cited_mark.priority_date": (objection.get("cited_mark") or {}).get("priority_date")}


def _node(node: dict[str, Any], facts: dict[str, Any], assessments: dict[str, Any]) -> dict[str, Any]:
    if "all" not in node and "any" not in node:
        return _leaf(node, facts, assessments)
    join = "all" if "all" in node else "any"
    children = [_node(child, facts, assessments) for child in node[join]]
    states = [c["state"] for c in children]
    if join == "all":
        state = _NOT if _NOT in states else _MET if all(s == _MET for s in states) else _OPEN
    else:
        state = _MET if _MET in states else _NOT if all(s == _NOT for s in states) else _OPEN
    return {"id": node.get("id"), "text": node.get("text"), "kind": join, "state": state, "children": children}


def _evaluate(tree: dict[str, Any], facts: dict[str, Any], assessments: dict[str, Any]) -> str:
    return _node(tree, facts, assessments)["state"]


def _overall(state: str) -> str:
    return {_MET: ("The report records every condition as met. That is the Registrar's belief as the report states it, "
                   "not a decision, and an exception may still apply."),
            _NOT: "A condition is recorded as not met.",
            _OPEN: f"Whether every condition is met is {OPEN}."}[state]


def _asks(tree: dict[str, Any], facts: dict[str, Any], assessments: dict[str, Any]) -> list[dict[str, str]]:
    """Unknown facts whose value would change the reading, and the question for each."""
    before = _evaluate(tree, facts, assessments)
    out = []
    for leaf in procedure.leaves(tree):
        if leaf["kind"] != "fact" or _leaf(leaf, facts, assessments)["state"] != _OPEN:
            continue
        outcomes = {_evaluate(tree, {**facts, leaf["id"]: {"value": v, "source": "supposed"}}, assessments)
                    for v in (True, False)}
        if outcomes != {before}:
            out.append({"condition": leaf["id"], "question": leaf.get("ask") or f"Is it so that {leaf['text'][0].lower()}{leaf['text'][1:]}"})
    return out


def read_test(test: dict[str, Any], objection: dict[str, Any],
              application: dict[str, Any] | None = None) -> dict[str, Any]:
    """The test as it reads on one objection's recorded facts and assessments, and on the
    dates the matter states."""
    facts: dict[str, Any] = {f["condition"]: f for f in objection.get("facts") or ()}
    facts["__dates__"] = _dates(objection, application)
    assessments = {a["condition"]: a for a in objection.get("assessments") or ()}
    condition = _node(test["condition"], facts, assessments)
    exceptions = []
    for exception in test.get("exceptions") or ():
        read = _node(exception["condition"], facts, assessments)
        effect = exception["effect"]
        kind = {"discretion": "This is a discretion: the Registrar may, but need not.",
                "bar": "This is a bar: if satisfied of this, the Registrar may not reject on this ground.",
                "obligation": "This is an obligation."}[effect["kind"]]
        exceptions.append({
            "id": exception["id"], "text": exception["text"], **_source(exception), "condition": read,
            "effect": {**_source(effect), "kind": effect["kind"], "text": effect["text"],
                       "reads": f"{effect['text']} {kind}"},
            "state": read["state"],
            "reads": _overall(read["state"]).replace("every condition", "this exception's condition"),
            "asks": _asks(exception["condition"], facts, assessments)})
    return {
        "test": test["id"], "title": test["title"], "provision": test["provision"], "actor": test["actor"],
        "effect": {**_source(test["effect"]), "kind": test["effect"]["kind"], "text": test["effect"]["text"]},
        "scope": test.get("scope") or {}, "condition": condition, "state": condition["state"],
        "reads": _overall(condition["state"]), "exceptions": exceptions,
        "asks": _asks(test["condition"], facts, assessments),
        "routes": [{"id": r["id"], "text": r["text"], **_source(r), "scope": r.get("scope")}
                   for r in test.get("routes") or ()],
    }


def position(process: dict[str, Any], events: list[dict[str, Any]], raised: set[str] | None = None) -> dict[str, Any]:
    """Where the matter is in the template, what can happen next and on what it depends.
    Never a date the matter does not state; never lapse unless a lapse is recorded. A
    branch that exists only for some grounds (deferment, section 44) is offered only where
    the matter raised one (`raised`: the provisions of its open objections)."""
    steps = {s["id"]: s for s in process["steps"]}
    history = [{"step": e["step"], "label": steps[e["step"]]["label"], "date": e.get("date"), "note": e.get("note")}
               for e in events]
    current = events[-1]["step"] if events else None
    following = [{"to": t["to"], "label": steps[t["to"]]["label"], "when": t["when"], "needs": t.get("needs") or [],
                  **_source(t)} for t in process["transitions"] if t["from"] == current
                 and (raised is None or not t.get("grounds") or set(t["grounds"]) & raised)]
    done = {e["step"] for e in events}
    deadlines = [{"id": d["id"], "text": d["text"], **_source(d)} for d in process.get("deadlines") or ()
                 if done & set(d["from"])]
    stated = [e for e in events if e.get("stated_lapse_date")]
    lapse = None
    if stated:
        lapse = (f"The report of {stated[-1].get('date') or 'an unknown date'} states that the application will lapse on "
                 f"{stated[-1]['stated_lapse_date']} if it is not accepted earlier.")
        if any(e["step"] == "deferment" for e in events[events.index(stated[-1]):]):
            lapse += (" Acceptance has since been deferred, and a deferment does not count towards the 15 months, so "
                      "that date may have moved; the Registrar's notice states it.")
    elif "report" in done:
        lapse = "The report's lapse date is not known here; the report states it."
    return {"process": process["id"], "current": current, "current_label": steps[current]["label"] if current else None,
            "current_text": steps[current]["text"] if current else None, "history": history, "next": following,
            "deadlines": deadlines, "lapse": lapse,
            "note": "No date is calculated here: the dates are the ones the report states."}


def _check(check: str, exhibit: dict[str, Any], application: dict[str, Any], items: list[str]) -> tuple[str, str]:
    filing = application.get("filing_date")
    labels = {i["id"]: i["text"] for i in application["items"]}
    if check == "in_australia":
        place = exhibit.get("place")
        return ("present", "shows use in Australia") if place == "australia" else (
            ("missing", "shows use overseas, not in Australia") if place == "overseas" else ("cannot tell", "does not say where"))
    if check == "dated":
        return ("present", f"dated {exhibit['dated']}") if exhibit.get("dated") else ("missing", "is not dated")
    if check == "before_filing_date":
        if not exhibit.get("dated"):
            return "cannot tell", "is not dated"
        if not filing:
            return "cannot tell", "the filing date is not known"
        return ("present", f"dated before the filing date ({filing})") if exhibit["dated"] < filing else (
            "missing", f"dated on or after the filing date ({filing})")
    if check == "sign_as_applied":
        shown = exhibit.get("sign_shown")
        return ("present", "shows the trade mark applied for" if shown == "as_applied" else
                "shows a substantially identical trade mark") if shown in ("as_applied", "substantially_identical") else (
            ("missing", "shows a different sign") if shown == "different" else ("cannot tell", "does not say which sign"))
    if check == "items_covered":
        missing = [labels[i] for i in items if i not in (exhibit.get("items") or ())]
        return ("present", "covers every item objected to") if not missing else ("missing", "does not cover " + ", ".join(missing))
    raise ValueError(check)


def evidence_view(test: dict[str, Any], objection: dict[str, Any], application: dict[str, Any]) -> dict[str, Any]:
    """What each exhibit may help address and what is missing. Never whether it succeeds:
    how much is enough is the examiner's assessment (A05)."""
    requirements = test.get("evidence_requirements") or []
    assessments = {a["condition"] for a in objection.get("assessments") or () if a["value"]}
    # The subsection a report's recorded assessment points to, where there is one.
    reported = set()
    for branch in (test["condition"].get("any") or []):
        ids = {leaf["id"] for leaf in procedure.leaves(branch)}
        if ids & assessments:
            reported |= ids
    in_play = [r for r in requirements if not reported or set(r["for"]) & reported]
    labels = {i["id"]: i["text"] for i in application["items"]}
    conditions = {leaf["id"]: leaf["text"] for leaf in procedure.leaves(test["condition"])}
    offered = sorted({c for r in in_play for c in r["for"] if not reported or c in reported})
    exhibits = []
    for exhibit in objection.get("exhibits") or ():
        checks = []
        for requirement in in_play:
            for check in requirement.get("checks") or ():
                result, detail = _check(check, exhibit, application, objection["items"])
                checks.append({"requirement": requirement["id"], "check": check, "result": result, "detail": detail,
                               **_source(requirement)})
        missing = [c["detail"] for c in checks if c["result"] == "missing"]
        unclear = [c["detail"] for c in checks if c["result"] == "cannot tell"]
        exhibits.append({
            "id": exhibit["id"], "description": exhibit["description"],
            "items": [labels[i] for i in exhibit.get("items") or ()],
            "may_address": offered,
            "checks": checks, "missing": sorted(set(missing)), "unclear": sorted(set(unclear)),
            "reads": "Offered on: " + "; ".join(conditions[c][0].lower() + conditions[c][1:].rstrip(".") for c in offered) + ". "
            + (f"What it lacks: {'; '.join(sorted(set(missing)))}. " if missing else "")
            + (f"Cannot tell: {'; '.join(sorted(set(unclear)))}. " if unclear else "")
            + "Whether the evidence is enough is the examiner's assessment.",
        })
    sufficiency = [{"id": r["id"], "text": r["text"], **_source(r)} for r in in_play if r["kind"] == "sufficiency"]
    relevance = [{"id": r["id"], "text": r["text"], **_source(r)} for r in in_play if r["kind"] == "relevance"]
    asks = []
    if any(c["detail"] == "the filing date is not known" for e in exhibits for c in e["checks"]):
        asks.append({"condition": "filing_date", "question": "What is your application's filing date?"})
    return {"relevance": relevance, "sufficiency": sufficiency, "exhibits": exhibits, "asks": asks}


_CAPACITY = {"applicant": "applicant", "representative": "representative",
             "owner_of_cited_mark": "owner of the cited trade mark"}


def _roles(record: dict[str, Any]) -> list[dict[str, Any]]:
    names = {p["id"]: p["name"] for p in record["parties"]}
    held: dict[str, list[str]] = {}
    for role in record["roles"]:
        held.setdefault(role["party"], []).append(_CAPACITY[role["capacity"]])
    return [{"party": names[p], "capacities": caps} for p, caps in held.items()]


def explain(matter: Matter, tests: dict[str, Any] | None = None, process: dict[str, Any] | None = None) -> dict[str, Any]:
    """The explanation object for one fictional matter."""
    if matter.errors:
        raise ValueError(f"{matter.id} has errors: {'; '.join(matter.errors)}")
    record = matter.record
    tests = tests if tests is not None else {k: v.record for k, v in procedure.load_tests().by_id().items()}
    if process is None:
        process = procedure.load_processes().sound[0].record
    labels = {i["id"]: i["text"] for i in record["application"]["items"]}
    issues = []
    for objection in record["objections"]:
        test = tests[objection["test"]]
        reading = read_test(test, objection, record["application"])
        issue = {
            "objection": objection["id"], "test": reading, "status": objection["status"],
            "items": [labels[i] for i in objection["items"]], "reasons": objection["reasons"],
            "standing": ("The report records this objection as withdrawn." if objection["status"] == "withdrawn" else
                         "The report records this objection as maintained after the response." if objection["status"] == "maintained"
                         else "The report raises this objection."),
        }
        if test.get("evidence_requirements"):
            issue["evidence"] = evidence_view(test, objection, record["application"])
        issues.append(issue)
    open_items = {i for o in record["objections"] if o["status"] != "withdrawn" for i in o["items"]}
    clear = [labels[i] for i in labels if i not in open_items]
    asks: list[dict[str, str]] = []
    for issue in issues:
        for ask in issue["test"]["asks"] + [a for x in issue["test"]["exceptions"] for a in x["asks"]] + (
                issue.get("evidence", {}).get("asks") or []):
            if ask["question"] not in {a["question"] for a in asks}:
                asks.append(ask)
    sources: dict[str, str] = {}
    def collect(node: Any) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("ref"), str) and node.get("authority") in ("law", "practice"):
                sources.setdefault(node["ref"], node["authority"])
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)
    raised = {tests[o["test"]]["provision"] for o in record["objections"] if o["status"] != "withdrawn"}
    where = position(process, record["events"], raised)
    collect(issues)
    collect(where)
    return {
        "matter": record["id"], "fictional": True, "title": record["title"], "sign": record["application"]["sign"],
        "roles": _roles(record), "issues": issues,
        "unresolved": {"items": [labels[i] for i in labels if i in open_items], "clear": clear,
                       "reads": ("Objections remain open for: " + ", ".join(labels[i] for i in labels if i in open_items) + ". "
                                 if open_items else "No objection is recorded as open. ")
                       + (f"No open objection is recorded for: {', '.join(clear)}. " if clear else "")
                       + "Resolving one objection does not accept the application: only the Registrar accepts it."},
        "process": where, "asks": asks,
        "sources": [{"ref": r, "authority": a} for r, a in sorted(sources.items())],
        "stamp": STAMP,
    }


def render_text(explanation: dict[str, Any]) -> str:
    """The text equivalent of every view: the same object, in words."""
    e = explanation
    out = [f"{e['title']} — fictional matter {e['matter']}, trade mark {e['sign']}", ""]
    out.append("Who is who: " + "; ".join(f"{r['party']} is the {' and the '.join(r['capacities'])}" for r in e["roles"]) + ".")
    for issue in e["issues"]:
        t = issue["test"]
        out += ["", f"Objection {issue['objection']}: {t['title']}",
                f"Goods or services affected: {', '.join(issue['items'])}.", issue["standing"],
                f"What the report says: {issue['reasons']}",
                f"What the law says ({t['provision']}, law): if the conditions below hold, "
                f"{t['effect']['text'][0].lower()}{t['effect']['text'][1:]}"]
        def walk(node: dict[str, Any], depth: int) -> None:
            pad = "  " * depth
            if node["kind"] in ("all", "any"):
                if node.get("text"):
                    out.append(f"{pad}- {node['text']}")
                out.append(f"{pad}  {'All of these' if node['kind'] == 'all' else 'Any one of these'}:")
                for child in node["children"]:
                    walk(child, depth + 1)
            else:
                state = {"met": "recorded as met", "not_met": "recorded as not met", "open": OPEN}[node["state"]]
                out.append(f"{pad}- {node['text']} [{state}: {node['why']}] ({node['ref']}, {node['authority']})")
        walk(t["condition"], 1)
        out.append(t["reads"])
        for x in t["exceptions"]:
            out += [f"Exception ({x['ref']}, law): {x['text']}", f"  {x['effect']['reads']}", f"  {x['reads']}"]
        for r in t["routes"]:
            out.append(f"A way to respond ({r['ref']}, {r['authority']}{', ' + r['scope'] if r.get('scope') else ''}): {r['text']}")
        if issue.get("evidence"):
            ev = issue["evidence"]
            for x in ev["exhibits"]:
                out.append(f"Exhibit {x['id']} ({x['description']}): {x['reads']}")
            for s in ev["sufficiency"]:
                out.append(f"How much is enough ({s['ref']}, practice): {s['text']}")
    p = e["process"]
    out += ["", f"Where the application is: {p['current_label']}. {p['current_text']}"]
    out += [f"What can happen next: {n['label']}, when {n['when']}"
            + (f" (depends on: {'; '.join(n['needs'])})" if n["needs"] else "") + f" ({n['ref']}, {n['authority']})."
            for n in p["next"]]
    if p["lapse"]:
        out.append(p["lapse"])
    out += [f"Time rule ({d['ref']}, law): {d['text']}" for d in p["deadlines"]]
    out += [p["note"], "", e["unresolved"]["reads"]]
    if e["asks"]:
        out += ["", "What would change this explanation:"] + [f"- {a['question']}" for a in e["asks"]]
    out += ["", "Sources: " + "; ".join(f"{s['ref']} ({s['authority']})" for s in e["sources"]), "", e["stamp"]]
    return "\n".join(out) + "\n"

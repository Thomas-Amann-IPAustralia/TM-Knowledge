"""Normative scenarios: a fictional amendment, run on fictional matters (A10).

The second review response's A10 separates three questions an amendment raises, and
this module answers each in its own layer, never summing them:

1. **Which records would need re-reading?** (editorial) The dependency index
   (`ontology.dependencies`, R05) from the amended provision: the records that name it
   or a part of it, and those resting on a Manual passage that cites it. "No recorded
   dependency", never "no impact".
2. **Would these matters be read differently?** (normative) The structured test of
   the provision (`GL-`) is edited as the draft says, and each fictional matter is
   explained under the test as held and under the edited test (`explain.engine`); the
   difference is reported element by element. Never an outcome: "the reading of this
   condition changes from recorded as met to open", not "the application would now be
   accepted".
3. **How would applicants or examiners behave?** (behavioural) Unknown: that needs an
   empirical model and data nobody here holds, and the result says so every time.

**The draft is kept out of anything operative.** A scenario (`scenarios/amendments.yaml`,
`FS-`, fictional and fixture-only like a matter) never enters the graph, the search
index, the site or a prompt; the edited test exists in memory for one comparison; every
element a draft changed is labelled `draft`, never law. A scenario names the compilation
whose text it amends (A03), and is refused if that compilation is not held, so a scenario
cannot silently run against a text it was not written for.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

from tm_knowledge.authored import procedure
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.explain import engine
from tm_knowledge.explain.matters import Matter
from tm_knowledge.stage0.schemas import validator_for_file

__all__ = ["AMENDMENTS_PATH", "BEHAVIOURAL", "STAMP", "Scenario", "load", "apply", "compare", "run", "render_text"]

AMENDMENTS_PATH = REPO_ROOT / "scenarios" / "amendments.yaml"
STAMP = ("A fictional amendment, written by a machine, run on fictional matters over records no trade marks expert has "
         "reviewed. The draft is not law and not a proposal. This shows how the reading of each matter would change; it "
         "decides nothing, and only the Registrar decides whether an application is accepted.")
BEHAVIOURAL = ("Unknown. How applicants, attorneys or examiners would respond to the change, and what it would do to "
               "filings, objections or workload, needs an empirical model and data that are not held here.")
_STATE = {"met": "recorded as met", "not_met": "recorded as not met", "open": engine.OPEN}


@dataclass(frozen=True)
class Scenario:
    record: dict[str, Any]
    errors: tuple[str, ...] = ()

    @property
    def id(self) -> str:
        return str(self.record.get("id"))


def _elements(test: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any], list[Any] | None]]:
    """Every element of a test with an id, with the list holding it (None for the effect)."""
    yield "effect", test["effect"], None

    def walk(node: dict[str, Any], holder: list[Any] | None) -> Iterator[tuple[str, dict[str, Any], list[Any] | None]]:
        if node.get("id"):
            yield node["id"], node, holder
        for join in ("all", "any"):
            for child in node.get(join) or ():
                yield from walk(child, node[join])

    yield from walk(test["condition"], None)
    for exception in test.get("exceptions") or ():
        yield exception["id"], exception, test["exceptions"]
        yield from walk(exception["condition"], None)
    for key in ("evidence_requirements", "routes"):
        for element in test.get(key) or ():
            yield element["id"], element, test[key]


def _check(record: dict[str, Any], tests: dict[str, Any], matters: dict[str, Matter], held: dict[str, set[str]]) -> list[str]:
    errors = [f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}"
              for e in validator_for_file("fictional-amendment.schema.json").iter_errors(record)]
    if errors:
        return errors
    amends = record["amends"]
    if amends["compilation"] not in held.get(amends["instrument"], set()):
        errors.append(f"amends compilation {amends['compilation']} of {amends['instrument']}, which is not held: a "
                      "scenario runs only against the text it was written for (A03)")
    if not amends["provision"].startswith(amends["instrument"] + "/"):
        errors.append(f"{amends['provision']} is not in {amends['instrument']}")
    test = tests.get(amends["test"])
    if test is None:
        return errors + [f"names {amends['test']}, which is no sound legal test"]
    if not (amends["provision"] == test["provision"] or amends["provision"].startswith(test["provision"] + "(")):
        errors.append(f"{amends['provision']} is not part of {test['provision']}, the provision {amends['test']} reads")
    found = {element_id: element for element_id, element, _ in _elements(test)}
    for change in record["changes"]:
        element = found.get(change["target"])
        if element is None:
            errors.append(f"{change['op']} targets {change['target']}, which is no element of {amends['test']}")
        elif change["op"] == "remove" and change["target"] == "effect":
            errors.append("a test's effect cannot be removed; set its kind or its words")
        elif change["op"] == "replace_text" and not change.get("text"):
            errors.append(f"replace_text on {change['target']} gives no text")
        elif change["op"] == "set_effect_kind" and ("kind" not in change or "kind" not in (element.get("effect") or element)):
            errors.append(f"set_effect_kind on {change['target']} needs a kind, and an element with an effect")
        elif change["op"] == "drop_check" and change.get("check") not in (element.get("checks") or ()):
            errors.append(f"drop_check: {change['target']} has no check {change.get('check')}")
    for matter_id in record["runs_on"]:
        matter = matters.get(matter_id)
        if matter is None:
            errors.append(f"runs on {matter_id}, which is no fictional matter")
        elif matter.errors:
            errors.append(f"runs on {matter_id}, which has errors")
        elif not any(o["test"] in (amends["test"], None) for o in matter.record["objections"]):
            errors.append(f"runs on {matter_id}, which has no objection under {amends['test']}")
    return errors


def load(path: Path | None = None, corpus: Any = None) -> list[Scenario]:
    """Every fictional amendment, each checked. One with errors is returned with them."""
    from tm_knowledge import versions
    from tm_knowledge.explain import matters as matters_module

    path = path or AMENDMENTS_PATH
    if corpus is None:
        from tm_knowledge.upstream.loader import load_corpus

        corpus = load_corpus()
    held = {code: {c.number for c in found} for code, found in versions.held(corpus).items()}
    tests = {k: v.record for k, v in procedure.load_tests().by_id().items()}
    matters = {m.id: m for m in matters_module.load()}
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    seen: set[str] = set()
    out = []
    for record in document:
        errors = _check(record, tests, matters, held)
        if str(record.get("id")) in seen:
            errors.append("id used twice")
        seen.add(str(record.get("id")))
        out.append(Scenario(record=record, errors=tuple(errors)))
    return out


def apply(test: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    """The test as the draft would leave it: a copy, never the record. Every element the
    draft changes quotes the draft and is marked with the scenario's id."""
    variant = copy.deepcopy(test)
    ref, draft, sid = scenario["amends"]["provision"], scenario["draft_text"], scenario["id"]
    for change in scenario["changes"]:
        found = {element_id: (element, holder) for element_id, element, holder in _elements(variant)}
        element, holder = found[change["target"]]
        if change["op"] == "remove":
            holder_list = holder if holder is not None else []
            holder_list[:] = [e for e in holder_list if e is not element]
            continue
        target = element.get("effect") if change["op"] == "set_effect_kind" and "effect" in element else element
        if change["op"] == "replace_text":
            element["text"] = change["text"]
        elif change["op"] == "set_effect_kind":
            target["kind"] = change["kind"]
        elif change["op"] == "drop_check":
            element["checks"] = [c for c in element["checks"] if c != change["check"]]
        for changed in (element, target):
            changed.update({"ref": ref, "quote": draft, "draft": sid})
    variant["scenario"] = sid
    return variant


# --- the comparison ----------------------------------------------------------


def _leaves(node: dict[str, Any], prefix: str) -> Iterator[tuple[str, dict[str, Any]]]:
    if node.get("id"):
        yield f"{prefix}{node['id']}", node
    for child in node.get("children") or ():
        yield from _leaves(child, prefix)


def _readings(issue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Everything an objection's explanation reads, keyed so the two versions line up."""
    out: dict[str, dict[str, Any]] = {}
    test = issue["test"]
    out["test"] = {"what": "whether every condition is met", "reads": _STATE[test["state"]]}
    out["effect"] = {"what": "what follows if the conditions hold", "reads": f"{test['effect']['text']} ({test['effect']['kind']})",
                     "authority": test["effect"].get("authority", "law") if "authority" in test["effect"] else None,
                     "draft": test["effect"].get("draft")}
    for key, node in _leaves(test["condition"], "condition:"):
        out[key] = {"what": node.get("text") or key, "reads": _STATE[node["state"]], "draft": node.get("draft"),
                    "authority": node.get("authority")}
    for exception in test["exceptions"]:
        out[f"exception:{exception['id']}"] = {"what": exception["text"], "reads": _STATE[exception["state"]],
                                               "draft": exception.get("draft")}
        out[f"exception:{exception['id']}:effect"] = {"what": f"the effect of {exception['id']}",
                                                      "reads": exception["effect"]["reads"],
                                                      "draft": exception["effect"].get("draft")}
        for key, node in _leaves(exception["condition"], f"exception:{exception['id']}:"):
            out[key] = {"what": node.get("text") or key, "reads": _STATE[node["state"]], "draft": node.get("draft")}
    # An exhibit is read gap by gap, so a draft that closes one gap and leaves another
    # says exactly which.
    for exhibit in (issue.get("evidence") or {}).get("exhibits") or ():
        name = f"Exhibit {exhibit['id']} ({exhibit['description']})"
        for detail in exhibit["missing"]:
            out[f"gap:{exhibit['id']}:{detail}"] = {"what": name, "gap": detail, "reads": "lacking"}
        for detail in exhibit["unclear"]:
            out[f"gap:{exhibit['id']}:{detail}"] = {"what": name, "gap": detail, "reads": "cannot tell"}
    for kind in ("relevance", "sufficiency", "set_aside"):
        for requirement in (issue.get("evidence") or {}).get(kind) or ():
            out[f"evidence:{requirement['id']}"] = {"what": requirement["text"],
                                                    "reads": "set aside" if kind == "set_aside" else "in play"}
    return out


def _asks(explanation: dict[str, Any]) -> set[str]:
    return {a["question"] for a in explanation["asks"]}


def compare(base: dict[str, Any], variant: dict[str, Any], test_id: str) -> dict[str, Any]:
    """How one matter's explanation differs between the test as held and as the draft
    leaves it: for each objection under the test, what is removed, what changes and what
    stays; and what the explanation would ask."""
    issues = []
    for before, after in zip(base["issues"], variant["issues"]):
        if before["test"] is None:
            issues.append({"objection": before["objection"], "under_test": False,
                           "reads": "The ground of this objection is not known, so the draft's effect on it cannot be "
                                    "read: the report's ground is needed first."})
            continue
        if before["test"]["test"] != test_id:
            continue
        old, new = _readings(before), _readings(after)
        closed = [{"what": old[k]["what"], "gap": old[k]["gap"], "was": old[k]["reads"]}
                  for k in old if k.startswith("gap:") and k not in new]
        opened = [{"what": new[k]["what"], "gap": new[k]["gap"], "now": new[k]["reads"]}
                  for k in new if k.startswith("gap:") and k not in old]
        old = {k: v for k, v in old.items() if not k.startswith("gap:")}
        new = {k: v for k, v in new.items() if not k.startswith("gap:")}
        removed = [{"key": k, "what": old[k]["what"], "was": old[k]["reads"]} for k in old if k not in new]
        added = [{"key": k, "what": new[k]["what"], "now": new[k]["reads"]} for k in new if k not in old]
        changed = [{"key": k, "what": new[k]["what"], "was": old[k]["reads"], "now": new[k]["reads"],
                    "draft": bool(new[k].get("draft"))}
                   for k in old if k in new and old[k]["reads"] != new[k]["reads"]]
        reworded = [{"key": k, "what": new[k]["what"], "was": old[k]["what"]}
                    for k in old if k in new and old[k]["what"] != new[k]["what"]]
        same = old["test"]["reads"] == new["test"]["reads"]
        issues.append({
            "objection": before["objection"], "under_test": True, "removed": removed, "added": added,
            "changed": changed, "reworded": reworded, "gaps": {"closed": closed, "opened": opened},
            "reads": ("On the recorded facts, the reading of this objection changes." if changed or added or closed or opened
                      else "On the recorded facts, the reading of this objection does not change"
                           + (", although the test's elements do." if removed or reworded else ".")),
            "overall": {"was": old["test"]["reads"], "now": new["test"]["reads"], "same": same},
        })
    before_asks, after_asks = _asks(base), _asks(variant)
    return {"matter": base["matter"], "title": base["title"], "issues": issues,
            "asks": {"no_longer": sorted(before_asks - after_asks), "newly": sorted(after_asks - before_asks)},
            "differs": any(i.get("changed") or i.get("added") or (i.get("gaps") or {}).get("closed")
                           or (i.get("gaps") or {}).get("opened") for i in issues) or before_asks != after_asks}


def _editorial(scenario: dict[str, Any], index: Any) -> dict[str, Any]:
    """Layer 1: the records that would need re-reading, by how they reach the provision.
    Naming the whole section is reported apart from naming the amended part, because a
    record about s 44 as a whole may or may not turn on s 44(3)."""
    provision = scenario["amends"]["provision"]
    direct = index.touching(provision)
    via = index.via_manual(provision)
    exact = index.records([r for r in direct if r["how"] != "names the whole it is part of"])
    whole = sorted(set(index.records([r for r in direct if r["how"] == "names the whole it is part of"])) - set(exact))
    through = sorted(set(index.records(via)) - set(exact) - set(whole))
    by_type: dict[str, set[str]] = {}
    for row in direct + via:
        by_type.setdefault(row["type"], set()).add(row["record"])
    total = len(set(exact) | set(whole) | set(through))
    return {
        "provision": provision, "names_it": exact, "names_the_whole": whole, "via_manual": through,
        "by_type": {k: sorted(v) for k, v in sorted(by_type.items())},
        "ambiguous": sorted({r["record"] for r in via if r.get("certainty") == "ambiguous"}),
        "reads": (f"{len(exact)} records name {provision} or a part of it; {len(whole)} more name only the whole it is "
                  f"part of; {len(through)} more rest on a Manual passage that cites it or its whole. That is recorded dependency only: "
                  "a passage on the same subject that no record cites is not counted, so this is not every effect."
                  if total else f"No recorded dependency on {provision}; that is not the same as no impact."),
    }


def run(scenario: Scenario, tests: dict[str, Any] | None = None, processes: dict[str, Any] | None = None,
        matters: dict[str, Matter] | None = None, index: Any = None) -> dict[str, Any]:
    """The scenario's three layers. `index` is a built dependency index (the editorial
    layer is left out without one)."""
    from tm_knowledge.explain import matters as matters_module

    if scenario.errors:
        raise ValueError(f"{scenario.id} has errors: {'; '.join(scenario.errors)}")
    record = scenario.record
    tests = tests if tests is not None else {k: v.record for k, v in procedure.load_tests().by_id().items()}
    processes = processes if processes is not None else {k: v.record for k, v in procedure.load_processes().by_id().items()}
    matters = matters if matters is not None else {m.id: m for m in matters_module.load()}
    test_id = record["amends"]["test"]
    variant = apply(tests[test_id], record)
    process = processes[engine.EXAMINATION_PROCESS]
    runs = []
    for matter_id in record["runs_on"]:
        base = engine.explain(matters[matter_id], tests, process)
        drafted = engine.explain(matters[matter_id], {**tests, test_id: variant}, process)
        runs.append(compare(base, drafted, test_id))
    return {
        "scenario": record["id"], "fictional": True, "title": record["title"], "question": record["question"],
        "amends": record["amends"], "draft_text": record["draft_text"],
        "changes": [{"op": c["op"], "target": c["target"], "why": c["why"]} for c in record["changes"]],
        "editorial": _editorial(record, index) if index is not None else None,
        "normative": runs, "behavioural": BEHAVIOURAL, "stamp": STAMP,
    }


def render_text(result: dict[str, Any]) -> str:
    """The text equivalent: the three layers in order, the draft labelled as draft."""
    r, a = result, result["amends"]
    out = [f"{r['title']} — fictional amendment {r['scenario']}", "", r["question"], "",
           f"The draft (fictional, not law), amending {a['provision']} as in compilation {a['compilation']}:",
           f"  “{r['draft_text']}”", "", f"Read as edits to {a['test']}:"]
    out += [f"- {c['op']} {c['target']}: {c['why']}" for c in r["changes"]]
    out += ["", "1. Which records would need re-reading (recorded dependency)"]
    if r["editorial"] is None:
        out.append("  Not computed here.")
    else:
        e = r["editorial"]
        out.append(f"  {e['reads']}")
        if e["names_it"]:
            out.append(f"  Naming {e['provision']} or a part of it: {', '.join(e['names_it'])}")
        out.append("  By record type, all three routes: "
                   + ", ".join(f"{kind.replace('_', ' ')} {len(ids)}" for kind, ids in e["by_type"].items()) + ".")
        if e["ambiguous"]:
            out.append(f"  Through an edge upstream marks ambiguous (listed, not resolved): {', '.join(e['ambiguous'])}")
    out += ["", "2. Would these fictional matters be read differently"]
    for run_ in r["normative"]:
        out.append(f"  {run_['matter']} ({run_['title']}): " + ("yes, in the places below." if run_["differs"] else
                                                                  "no change on the recorded facts."))
        for issue in run_["issues"]:
            out.append(f"    Objection {issue['objection']}: {issue['reads']}")
            if not issue["under_test"]:
                continue
            out += [f"      Removed by the draft: {x['what'].rstrip('.')} (was {x['was']})." for x in issue["removed"]]
            out += [f"      {x['what']}: gap closed ({x['was']}): {x['gap']}." for x in issue["gaps"]["closed"]]
            out += [f"      {x['what']}: new gap ({x['now']}): {x['gap']}." for x in issue["gaps"]["opened"]]
            out += [f"      Reworded by the draft (draft, not law): {x['what']}" for x in issue["reworded"]]
            out += [f"      {x['what']}: {x['was']} → {x['now']}" + (" (draft, not law)" if x["draft"] else "") + "."
                    for x in issue["changed"]]
            out += [f"      New under the draft: {x['what']} ({x['now']})." for x in issue["added"]]
            o = issue["overall"]
            out.append(f"      Whether every condition is met: {o['was']}" + ("" if o["same"] else f" → {o['now']}") + ".")
        out += [f"    No longer asked: {q}" for q in run_["asks"]["no_longer"]]
        out += [f"    Newly asked: {q}" for q in run_["asks"]["newly"]]
    out += ["", "3. How people would respond", f"  {r['behavioural']}", "", r["stamp"]]
    return "\n".join(out) + "\n"

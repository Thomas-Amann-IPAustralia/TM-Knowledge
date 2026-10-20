"""The three views of an explanation, as one standalone HTML page (A09).

An issue card per objection, the process timeline, and the evidence-to-issue view, each
drawn from the explanation object `engine.explain` returns and each followed by its text
equivalent, so a changed fact changes the picture and the words together. State is shown
by a word and a mark as well as a colour. The page is written to a file for the owner to
look at; it is not deployed, and nothing here is for customers until the owner says so
(CLAUDE.md §3a, ADR-0142).
"""

from __future__ import annotations

import html
from typing import Any

from tm_knowledge.explain import engine

__all__ = ["render_page"]

_STATE = {"met": ("✓", "recorded as met"), "not_met": ("✗", "recorded as not met"), "open": ("?", engine.OPEN)}

_CSS = """
:root{--bg:#fbfaf7;--card:#fff;--ink:#1d2329;--ink-2:#4b5560;--line:#d9dde1;--law:#2f5d8a;--practice:#7a5a1a;
--met:#2e6b3f;--not:#9b2f2f;--open:#6b6f75;--now:#2f5d8a;--soft:#eef2f6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15181b;--card:#1d2125;--ink:#e6e8ea;
--ink-2:#a9b0b7;--line:#353b41;--law:#8db7e0;--practice:#e0bf7a;--met:#7fc493;--not:#e48b8b;--open:#a5aab0;--now:#8db7e0;--soft:#252a30}}
:root[data-theme="dark"]{--bg:#15181b;--card:#1d2125;--ink:#e6e8ea;--ink-2:#a9b0b7;--line:#353b41;--law:#8db7e0;
--practice:#e0bf7a;--met:#7fc493;--not:#e48b8b;--open:#a5aab0;--now:#8db7e0;--soft:#252a30}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.5rem;margin:.2rem 0}h2{font-size:1.2rem;margin:2rem 0 .4rem}
h3{font-size:1rem;margin:0 0 .3rem}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.stamp{border-left:4px solid var(--open);padding:8px 12px;background:var(--soft);border-radius:6px;font-size:.9rem}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:1px 9px;margin:2px 4px 2px 0;font-size:.85rem}
.law{color:var(--law)}.practice{color:var(--practice)}.badge{font-size:.75rem;border-radius:4px;padding:1px 6px;border:1px solid currentColor;white-space:nowrap}
.tree{list-style:none;margin:.3rem 0;padding-left:1.1rem;border-left:2px solid var(--line)}.tree li{margin:.25rem 0}
.join{font-size:.8rem;color:var(--ink-2);text-transform:uppercase;letter-spacing:.04em}
.st{display:inline-block;min-width:1.4em;text-align:center;font-weight:700;border-radius:4px;margin-right:.35rem}
.st-met{color:var(--met)}.st-not_met{color:var(--not)}.st-open{color:var(--open)}
.why{color:var(--ink-2);font-size:.85rem}.ref{font-family:ui-monospace,Menlo,monospace;font-size:.8rem}
.text-eq{margin-top:.6rem}.text-eq summary{cursor:pointer;color:var(--ink-2);font-size:.9rem}.text-eq pre{white-space:pre-wrap;font:inherit;font-size:.9rem}
table{border-collapse:collapse;width:100%;font-size:.9rem}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
svg text{fill:var(--ink);font:12px system-ui,sans-serif}.overflow{overflow-x:auto}
"""


def _e(text: Any) -> str:
    return html.escape(str(text))


def _source(ref: str, authority: str) -> str:
    return (f'<span class="ref {authority}">{_e(ref)}</span> '
            f'<span class="badge {authority}">{"law" if authority == "law" else "Manual · practice"}</span>')


def _tree(node: dict[str, Any]) -> str:
    if node["kind"] in ("all", "any"):
        head = f'<span class="join">{"all of these" if node["kind"] == "all" else "any one of these"}</span>'
        label = f' {_e(node["text"])}' if node.get("text") else ""
        mark, word = _STATE[node["state"]]
        inner = "".join(f"<li>{_tree(child)}</li>" for child in node["children"])
        return (f'<span class="st st-{node["state"]}" aria-hidden="true">{mark}</span>{head}{label} '
                f'<span class="why">({_e(word)})</span><ul class="tree">{inner}</ul>')
    mark, word = _STATE[node["state"]]
    return (f'<span class="st st-{node["state"]}" aria-hidden="true">{mark}</span>{_e(node["text"])} '
            f'<span class="why">— {_e(word)}: {_e(node["why"])}</span><br>{_source(node["ref"], node["authority"])}'
            f' <span class="badge">{_e(node["kind"])}</span>')


def _issue(issue: dict[str, Any]) -> str:
    t = issue["test"]
    parts = [f'<div class="card"><h3>Objection {_e(issue["objection"])}: {_e(t["title"])}</h3>',
             f'<p>{_e(issue["standing"])} Goods or services: {"".join(f"<span class=chip>{_e(i)}</span>" for i in issue["items"])}</p>',
             f'<p><b>The report says:</b> {_e(issue["reasons"])}</p>',
             f'<p><b>The law</b> ({_source(t["provision"], "law")}): if the conditions below hold, '
             f'{_e(t["effect"]["text"][0].lower() + t["effect"]["text"][1:])}</p>',
             f'<div role="group" aria-label="The conditions and what is recorded for each">{_tree(t["condition"])}</div>',
             f'<p><b>{_e(t["reads"])}</b></p>']
    for x in t["exceptions"]:
        parts.append(f'<div class="card"><b>Exception</b> ({_source(x["ref"], "law")}) <span class="badge">{_e(x["effect"]["kind"])}</span>'
                     f'<p>{_e(x["text"])}</p><p>{_e(x["effect"]["reads"])}</p>{_tree(x["condition"])}<p>{_e(x["reads"])}</p></div>')
    if t["routes"]:
        parts.append("<p><b>Ways to respond</b></p><ul>" + "".join(
            f'<li>{_e(r["text"])} {_source(r["ref"], r["authority"])}{" <span class=why>(" + _e(r["scope"]) + ")</span>" if r.get("scope") else ""}</li>'
            for r in t["routes"]) + "</ul>")
    if issue.get("evidence"):
        parts.append(_evidence(issue["evidence"]))
    parts.append("</div>")
    return "".join(parts)


def _evidence(ev: dict[str, Any]) -> str:
    # One column per check: two requirements may ask the same of an exhibit ("dated"),
    # and the answer is the exhibit's, not the requirement's.
    checks = sorted({c["check"] for x in ev["exhibits"] for c in x["checks"]})
    names = {"in_australia": "in Australia", "before_filing_date": "before the filing date", "sign_as_applied": "the sign applied for",
             "items_covered": "all the goods or services", "dated": "dated"}
    mark = {"present": ("✓", "met"), "missing": ("✗", "not_met"), "cannot tell": ("?", "open")}
    head = "".join(f"<th>{_e(names[c])}</th>" for c in checks)
    rows = []
    for x in ev["exhibits"]:
        cells = []
        for check in checks:
            found = next((c for c in x["checks"] if c["check"] == check), None)
            if found is None:
                cells.append("<td></td>")
            else:
                m, cls = mark[found["result"]]
                cells.append(f'<td><span class="st st-{cls}" aria-hidden="true">{m}</span>{_e(found["detail"])}</td>')
        rows.append(f"<tr><th scope=row>{_e(x['id'])}: {_e(x['description'])}</th>{''.join(cells)}</tr>")
    text = "\n".join(f"Exhibit {x['id']} ({x['description']}): {x['reads']}" for x in ev["exhibits"])
    sufficiency = "".join(f'<p class="why">{_e(s["text"])} {_source(s["ref"], "practice")}</p>' for s in ev["sufficiency"])
    return (f'<h3 style="margin-top:1rem">Evidence and what it is offered for</h3><div class="overflow"><table>'
            f'<thead><tr><th>Exhibit</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>{sufficiency}'
            f'<details class="text-eq"><summary>Text equivalent</summary><pre>{_e(text)}</pre></details>')


def _timeline(p: dict[str, Any]) -> str:
    done = p["history"]
    nodes = [(h["label"], h["date"] or "date not known", "done") for h in done]
    nxt = p["next"]
    last = 20 + 150 * (len(nodes) - 1) + 65
    labels = [f"{n['label']}, if {n['when']}" for n in nxt]
    width = max(150 * len(nodes) + 40, last + 30 + 7 * max((len(t) for t in labels), default=0))
    height = 80 + 34 * max(1, len(nxt))
    svg = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="tl-title tl-desc">',
           '<title id="tl-title">Where the application is in the examination process</title>',
           f'<desc id="tl-desc">{_e("Steps so far: " + ", then ".join(n[0] for n in nodes) + ". Possible next steps: " + "; ".join(n["label"] for n in nxt) + ".")}</desc>']
    for i, (label, date, _) in enumerate(nodes):
        x = 20 + 150 * i
        current = i == len(nodes) - 1
        svg.append(f'<rect x="{x}" y="20" width="130" height="46" rx="8" fill="none" stroke="var({"--now" if current else "--line"})" stroke-width="{3 if current else 1.5}"/>')
        svg.append(f'<text x="{x + 8}" y="40">{_e(label[:22])}</text><text x="{x + 8}" y="57" style="fill:var(--ink-2)">{_e(date)}</text>')
        if i:
            svg.append(f'<line x1="{x - 20}" y1="43" x2="{x}" y2="43" stroke="var(--line)" stroke-width="1.5"/>')
    for j, label in enumerate(labels):
        y = 96 + 34 * j
        svg.append(f'<path d="M{last} 66 L{last} {y - 6} L{last + 20} {y - 6}" fill="none" stroke="var(--ink-2)" stroke-dasharray="4 3"/>')
        svg.append(f'<text x="{last + 26}" y="{y - 2}">{_e(label)}</text>')
    svg.append("</svg>")
    text = [f"Where the application is: {p['current_label']}."] + [
        f"Next, possibly: {n['label']}, when {n['when']}" + (f" (depends on: {'; '.join(n['needs'])})" if n["needs"] else "")
        for n in nxt]
    if p["lapse"]:
        text.append(p["lapse"])
    text += [f"Time rule ({d['ref']}): {d['text']}" for d in p["deadlines"]] + [p["note"]]
    rules = "".join(f'<li>{_e(d["text"])} {_source(d["ref"], d["authority"])}</li>' for d in p["deadlines"])
    return (f'<div class="card"><div class="overflow">{"".join(svg)}</div>'
            f'<p>{_e(p["lapse"] or "")}</p><ul>{rules}</ul><p class="why">{_e(p["note"])}</p>'
            f'<details class="text-eq"><summary>Text equivalent</summary><pre>{_e(chr(10).join(text))}</pre></details></div>')


def _matter(e: dict[str, Any]) -> str:
    roles = "; ".join(f"{r['party']}: {' and '.join(r['capacities'])}" for r in e["roles"])
    asks = "".join(f"<li>{_e(a['question'])}</li>" for a in e["asks"])
    return (f'<section><h2>{_e(e["title"])}</h2><p class="why">Fictional matter {_e(e["matter"])} · trade mark '
            f'<b>{_e(e["sign"])}</b> · {_e(roles)}</p>'
            + "".join(_issue(i) for i in e["issues"])
            + f'<h3>Where the application is</h3>{_timeline(e["process"])}'
            + f'<div class="card"><p><b>{_e(e["unresolved"]["reads"])}</b></p>'
            + (f"<p>What would change this explanation:</p><ul>{asks}</ul>" if asks else "<p>Nothing more is needed to read the objections as recorded.</p>")
            + f'<p class="stamp">{_e(e["stamp"])}</p>'
            + f'<details class="text-eq"><summary>The whole explanation as text</summary><pre>{_e(engine.render_text(e))}</pre></details></div></section>')


def render_page(explanations: list[dict[str, Any]]) -> str:
    """Every fictional matter's explanation on one page."""
    body = "".join(_matter(e) for e in explanations)
    return (f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Objection Explainer Prototype</title><style>{_CSS}</style></head><body><main>'
            f'<p class="stamp"><b>Fictional matters only. Not for customers.</b> A prototype of the customer explanation aid '
            f'(Package 4), built from machine-written legal tests and a process template that no trade marks expert has reviewed. '
            f'Every case on this page is invented.</p><h1>Objection explainer — prototype</h1>{body}</main></body></html>\n')

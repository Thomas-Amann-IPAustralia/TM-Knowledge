"""Gather the explainer's data from the explorer build (site/data) and the bench files.

Run from the repo root after `tmk-explorer --write`. Writes data.json beside this script.
No expert notes, reviewer names or initials are copied: concepts keep label, wordings,
kind, origin, mentions, Parts and basis only.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path.cwd()
OUT = Path(__file__).with_name("data.json")  # git-ignored
site = ROOT / "site" / "data"
onto = json.loads((site / "ontology.json").read_text())
tour = json.loads((site / "tour.json").read_text())
stab = json.loads((site / "stability.json").read_text())
ex = json.loads((site / "examples.json").read_text())
pas = json.loads((site / "passages.json").read_text())
pools = {p["key"]: p for p in yaml.safe_load((ROOT / "data/derived/bench/pools.yaml").read_text())["pools"]}
judg = {j["need"]: j["grades"] for j in yaml.safe_load((ROOT / "data/derived/bench/judgements.yaml").read_text())["judgements"]}

chunks = {c[0]: c for c in pas["chunks"]}
pages = pas["pages"]


def page_of(ref):
    return "/".join(ref.split("#")[0].split("/")[:3])


def heading_of(c):
    return (c[2] or "").split(" > ")[-1]


def pmeta(ref, text_len=420):
    """[page title, heading, text, url] for a Manual passage, or legislation."""
    if ref in chunks:
        c = chunks[ref]
        pg = pages.get(c[1], {})
        t = c[3]
        if len(t) > text_len:
            t = t[:text_len].rsplit(" ", 1)[0] + " …"
        return [pg.get("title", ""), heading_of(c), t, pg.get("url", "")]
    if ref in pas["legislation"]:
        l = pas["legislation"][ref]
        t = l[3]
        if len(t) > text_len:
            t = t[:text_len].rsplit(" ", 1)[0] + " …"
        return [l[0] + " " + l[1], l[2].split(" > ")[-1], t, ""]
    return ["", "", "", ""]


# ---------------------------------------------------------------- reading order
key = lambda part: (lambda m: (int(m.group(1)), m.group(2)) if m else (999, part))(re.match(r"^Part(\d+)(.*)$", part or ""))
rows = [(c, i) for i, c in enumerate(pas["chunks"])]
rows.sort(key=lambda r: (key(pages.get(r[0][1], {}).get("part")), r[0][1], r[1]))
order = [r[0][0] for r in rows]
assert len(order) == tour["passages"] == 2460

parts = [[p["id"], p["title"], p["n"]] for p in tour["parts"]]

# ---------------------------------------------------------------- wordings
def snippet(text, words, width=230):
    low = text.lower()
    best = None
    for w in sorted(words, key=len, reverse=True):
        m = re.search(r"(?<![a-z])" + re.escape(w.lower()) + r"(?![a-z])", low)
        if m:
            best = m
            break
    if not best:
        return text[:width] + (" …" if len(text) > width else "")
    s = max(0, best.start() - width // 2)
    e = min(len(text), best.end() + width // 2)
    out = text[s:e]
    if s > 0:
        out = "… " + out.split(" ", 1)[-1]
    if e < len(text):
        out = out.rsplit(" ", 1)[0] + " …"
    return out


showcase = []
for s in tour["showcase"]:
    if s["label"] == "written permission":
        continue  # Q-88: counts "consent", a label on the too-general list
    words = list(s["wordings"].keys())
    snips = {}
    for w, idxs in s["wordings"].items():
        for i in idxs:
            if str(i) in snips:
                continue
            c = chunks[order[i]]
            snips[str(i)] = [order[i], pages.get(c[1], {}).get("title", ""), heading_of(c), snippet(c[3], words)]
    showcase.append({"label": s["label"], "kind": s["kind"], "wordings": s["wordings"], "total": s["total"],
                     "missed": s["missed"], "named": s["named"], "snips": snips})

wp = next(s for s in tour["showcase"] if s["label"] == "written permission")
consent_idx = wp["wordings"]["consent"]
consent_snips = {}
for i in consent_idx:
    c = chunks[order[i]]
    consent_snips[str(i)] = [order[i], pages.get(c[1], {}).get("title", ""), heading_of(c), snippet(c[3], ["consent"])]
by_part = {}
for i in consent_idx:
    part = pages.get(chunks[order[i]][1], {}).get("part")
    by_part[part] = by_part.get(part, 0) + 1

# ---------------------------------------------------------------- the ontology
concepts = {}
for c in onto["concepts"]:
    concepts[c["id"]] = {"l": c["label"], "alt": c["alt"], "not": c["not"], "k": c["kind"],
                         "o": "reviewed" if c["origin"] == "signed" else "machine",
                         "m": c["mentions"], "parts": c["parts"], "basis": c["basis"], "generic": c["generic"]}
preds = {k: v["label"] for k, v in onto["predicates"].items()}
rels = []
for r in onto["relations"]:
    rels.append([r["id"], r["s"], r["p"], r["o"], "reviewed" if r["origin"] == "signed" else "machine",
                 r.get("ref") or "", r.get("quote") or "", r.get("modality") or ""])
kinds = [{"id": k["id"], "label": k["label"], "plain": k["plain"], "family": k["family"]} for k in onto["kinds"]]
family_links = []
for f in onto["family_links"]:
    top = sorted(f["predicates"].items(), key=lambda x: -x[1])[:4]
    family_links.append({"s": f["s"], "o": f["o"], "total": f["total"], "top": [[preds.get(p, p), n] for p, n in top]})

# provisions named as the end of a connection or a basis: label them
provs = {}
for ref in {x for r in onto["relations"] for x in (r["s"], r["o"]) if x not in concepts} | {b for c in onto["concepts"] for b in c["basis"]}:
    m = pmeta(ref, 300)
    provs[ref] = m[:3]

# ---------------------------------------------------------------- pages and change
pages_out = []
for pg in stab["pages"]:
    am = pg["amended"][-1] if pg["amended"] else None
    pages_out.append([pg["ref"], pg["title"], pg["part"], pg["url"], pg["passages"], pg["relations"],
                      len(pg["mentioned"]), len(pg["amended"]), am])
stability = {"events": stab["events"], "by_year": stab["by_year"], "reasons": stab["reasons"][:9],
             "snapshot": stab["snapshot"], "part_titles": pas["parts"]}

# ---------------------------------------------------------------- Ask the Manual
answers = {a["key"]: a for a in ex["answers"]}
ask = []
used = set()
for k in ["BN-0017", "BN-0077", "BN-0022"]:
    a = answers[k]
    pool = pools[k]["systems"]
    g = judg.get(k, {})
    item = {"key": k, "kind": a["kind"], "q": a["question"], "ndcg": a["ndcg"],
            "recognised": [concepts[x["id"]]["l"] for x in a["recognised"] if x["id"] in concepts],
            "paths": [[concepts.get(p["subject"], {}).get("l", p["subject_label"]), preds.get(p["predicate"], p["predicate"]),
                       concepts.get(p["object"], {}).get("l", p["object_label"]), "reviewed" if p["origin"] == "signed" else "machine"]
                      for p in a["paths"] if p["predicate"] != "related"],
            "keyword": [[r, g.get(r)] for r in pool["keyword"]],
            "hybrid": [[r, g.get(r)] for r in pool["hybrid"]],
            "ontology": [[r, g.get(r)] for r in pool["ontology"]],
            "answer": a["answer"], "declined": a["declined"], "decline_reason": a["decline_reason"],
            "ncites": len(a["citations"]), "citations": [[c["ref"], c["quote"]] for c in a["citations"]], "legislation": a["legislation"], "model": a["model"], "date": a["date"]}
    for sysname in ("keyword", "hybrid", "ontology"):
        used.update(r for r, _ in item[sysname])
    used.update(c[0] for c in item["citations"] if c[0].startswith("TMM/"))
    ask.append(item)
passages_out = {r: pmeta(r) for r in sorted(used)}

# ---------------------------------------------------------------- worked examples: page urls
for r in onto["relations"]:
    if r.get("ref", "").startswith("TMM/"):
        passages_out.setdefault(r["ref"], None)
ref_urls = {}
for r in list(passages_out):
    pg = pages.get(page_of(r), {})
    ref_urls[r] = [pg.get("title", ""), pg.get("url", "")]
passages_out = {k: v for k, v in passages_out.items() if v is not None}

data = {
    "asof": "12 October 2026", "snapshot": "3 August 2026",
    "counts": onto["counts"], "parts": parts, "showcase": showcase,
    "consent": {"idx": consent_idx, "by_part": by_part, "snips": consent_snips},
    "kinds": kinds, "families": onto["families"], "family_links": family_links,
    "concepts": concepts, "preds": preds, "rels": rels, "provs": provs,
    "pages": pages_out, "stability": stability, "ask": ask, "passages": passages_out, "ref_pages": ref_urls,
}
OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
print(OUT, OUT.stat().st_size)

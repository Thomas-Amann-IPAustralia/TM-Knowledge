"""The data behind the examiner's explorer at `site/`.

`tmk-explorer --write` turns the two knowledge stores, the pinned snapshot and the
benchmark into the JSON files the explorer reads. Nothing here writes knowledge:
every concept, relationship and answer is copied from a record that already
exists, with who wrote it and whether a person has signed it carried on its face
(CLAUDE.md rules 3, 4 and 8). What this module adds is *arrangement* — counts,
groupings and indexes — and each one is computed here on every build, never
stored by hand.

Unlike the workbench (`tm_knowledge.dashboard`), the explorer reads the pinned
snapshot, because "Ask the Manual" searches the Manual in the browser and has to
hold its text (ADR-0117). The snapshot is read through `upstream.loader` and is
never written.

Files written under `site/data/`:

    ontology.json   kinds, concepts, relationships, kind-to-kind links, predicates
    search.json     what the browser needs to recognise concepts and rank passages
    passages.json   every Manual passage and every provision, verbatim
    stability.json  the Manual's amendment history and what rests on each page
    tour.json       the Manual by Part, ideas named many ways, one worked example
    examples.json   the 129 prepared answers and how each search system scored
    chat.json       the measured answer prompt, so the live chat asks the same way
    live.json       whether the live chat may call the model (ADR-0118)
"""

from __future__ import annotations

import base64
import json
import os
import re
import secrets
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge.authored import corrections as corrections_module
from tm_knowledge.authored import store as authored_store
from tm_knowledge.bulk import jobs
from tm_knowledge.bulk import links as links_module
from tm_knowledge import config
from tm_knowledge.config import PIN_PATH, REPO_ROOT
from tm_knowledge.dashboard import views
from tm_knowledge.search import index as search_index
from tm_knowledge.stage0 import goldset
from tm_knowledge.stage0 import typing as typing_module
from tm_knowledge.stage0.harness import passage_at
from tm_knowledge.upstream.loader import Corpus, load_corpus

__all__ = ["DATA_DIR", "SITE_DIR", "build", "write", "live_payload"]

SITE_DIR = REPO_ROOT / "site"
DATA_DIR = SITE_DIR / "data"
RELATIONS_TTL = REPO_ROOT / "ontology" / "draft" / "relations.ttl"
ALIASES_PATH = jobs.SEARCH_DIR / "aliases.yaml"

#: The live chat's model settings. The model is the owner's choice for knowledge
#: work (ADR-0111) and the one the 129 prepared answers were written with; the
#: effort is lower than theirs for speed in a live demo, and says so on the page.
CHAT_MODEL = "gpt-6.1-sol"
CHAT_EFFORT = "low"
CHAT_MAX_OUTPUT_TOKENS = 10000
OPENAI_RESPONSES = "https://api.openai.com/v1/responses"
#: The environment variables the Pages workflow sets from its secret. A distinct
#: name, so a key that happens to be in a developer's shell is never picked up.
KEY_ENV = "TMK_LIVE_OPENAI_KEY"
ENDPOINT_ENV = "TMK_LIVE_ENDPOINT"
#: A per-browser courtesy limit on live questions. It is not a control — anyone
#: can clear it — but it stops one enthusiastic tab running up the bill.
DAILY_LIMIT = 40

SOURCES = {"TMM": "Manual (practice)", "TMA1995": "Trade Marks Act 1995",
           "TMR1995": "Trade Marks Regulations 1995"}

#: What each family of kinds is, in the words `stage0.typing` uses for them.
FAMILIES = {
    "reasoning": "The questions the law asks",
    "examined": "What those questions are asked about",
    "process": "The process around them",
    "other": "Fits none of the ten",
}

#: SKOS predicates the pipeline writes, which `relations.ttl` does not list.
SKOS_LABELS = {"broader": "is a kind of", "related": "is related to"}

QUESTION_KINDS = {
    "lookup": "Looking something up",
    "problem": "Everyday problems, in plain words",
    "cross_part": "Questions that cross Parts of the Manual",
    "impact": "What a provision changes",
    # Plain on purpose: the site does not single out the expert's review (ADR-0130).
    "signed": "Questions a person reviewed",
}


def _source(ref: str) -> str:
    return SOURCES.get(ref.split("/", 1)[0], "other")


def _origin(store_origin: str) -> str:
    """`signed` for a record a named person approved, `machine` for one no person has."""
    return "signed" if store_origin in ("approved", "signed") else "machine"


# ------------------------------------------------------------------ ontology


def predicate_labels(path: Path = RELATIONS_TTL) -> dict[str, str]:
    """Predicate -> its `rdfs:label` in the approved relation list, plus SKOS."""
    text = path.read_text(encoding="utf-8")
    labels = dict(SKOS_LABELS)
    for name, body in re.findall(r"^tmk:(\w+) a owl:ObjectProperty ;(.*?)\.\s*$", text, re.M | re.S):
        match = re.search(r'rdfs:label "([^"]+)"', body)
        if match:
            labels[name] = match.group(1)
    return labels


def approved_predicates(path: Path = RELATIONS_TTL) -> set[str]:
    """Predicates a signed record uses — `tmk:ApprovedRelation` in the dictionary.
    One the owner admitted and nobody has signed a use of is on the list, but is
    not shown as approved."""
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"^tmk:(\w+) a owl:ObjectProperty ;\n\s+a tmk:ApprovedRelation ;", text, re.M))


def _camel(name: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r" \1", name).lower()


def kinds() -> list[dict[str, Any]]:
    reasoning = {k for k, _ in typing_module.REASONING_GROUPS}
    examined = {k for k, _ in typing_module.EXAMINED_GROUPS}
    process = {k for k, _ in typing_module.PROCESS_GROUPS}
    out = []
    for key, plain in typing_module.GROUPS:
        family = ("reasoning" if key in reasoning else "examined" if key in examined
                  else "process" if key in process else "other")
        out.append({"id": key, "label": views._group_label(key), "plain": plain, "family": family})
    return out


def _concept(view: views.ConceptView, mentions: dict[str, list[str]], generic: set[str]) -> dict[str, Any]:
    refs = mentions.get(view.identifier, [])
    parts = Counter(p for p in (views.manual_part(r) for r in refs) if p)
    record: dict[str, Any] = {
        "id": view.identifier,
        "label": view.label,
        "alt": list(view.alt_labels),
        "not": list(view.not_labels),
        "kind": view.group or "none_of_these",
        "origin": _origin(view.origin),
        "notes": view.notes,
        "broader": list(view.broader),
        "narrower": list(view.narrower),
        "related": list(view.related),
        "basis": list(view.provisions),
        "sources": list(view.sources),
        "mentions": len(refs),
        "parts": [p for p, _ in parts.most_common(5)],
        "generic": view.identifier in generic,
    }
    if view.origin == "approved":
        # The expert's initials and date are what "signed" means; they are shown
        # because they are the record's own fields, never written by this module.
        record["signed"] = {"by": view.signed_by, "date": view.signed_date}
    if view.authored:
        env = view.authored
        record["machine"] = {
            "by": env.get("authored_by"), "date": env.get("authored_date"),
            "review_status": env.get("review_status"), "confidence": env.get("confidence"),
            "reasoning": env.get("reasoning"), "check": env.get("expert_should_check"),
        }
    evidence = []
    for env, why in ((view.authored, "concept"), (view.typed_by, "kind")):
        for item in (env or {}).get("evidence") or ():
            if item.get("quote"):
                evidence.append({"ref": str(item.get("ref")), "quote": str(item["quote"]), "for": why})
    record["evidence"] = evidence
    if view.typed_by:
        record["typed"] = {"by": view.typed_by.get("authored_by"), "date": view.typed_by.get("authored_date"),
                           "review_status": view.typed_by.get("review_status"),
                           "confidence": view.typed_by.get("confidence")}
    return record


def _relations(gold: Any, authored: Any) -> list[dict[str, Any]]:
    """Every relationship record from both stores, its origin kept."""
    out = []
    for record in gold["gold_relationship"]:
        out.append({
            "id": str(record["id"]), "s": str(record["subject"]), "p": str(record["predicate"]),
            "o": str(record["object"]), "origin": "signed", "modality": record.get("modality"),
            "ref": record.get("source_ref"), "quote": record.get("supporting_text"),
            "signed": {"by": record.get("approved_by"), "date": record.get("approved_date")},
        })
    for entry in authored.of("gold_relationship"):
        if not entry.sound:
            continue
        record, env = entry.record, entry.envelope
        evidence = (env.get("evidence") or [{}])[0]
        out.append({
            "id": str(record["id"]), "s": str(record["subject"]), "p": str(record["predicate"]),
            "o": str(record["object"]), "origin": "machine", "modality": record.get("modality"),
            "ref": record.get("source_ref") or evidence.get("ref"),
            "quote": record.get("supporting_text") or evidence.get("quote"),
            "machine": {"by": env.get("authored_by"), "date": env.get("authored_date"),
                        "review_status": env.get("review_status"), "confidence": env.get("confidence"),
                        "reasoning": env.get("reasoning")},
        })
    return out


def _kind_links(concepts: dict[str, dict[str, Any]], relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Concept-to-concept relationships rolled up to the kinds at either end.

    An arrangement, not a record: it counts what the relationship records say
    and asserts nothing of its own.
    """
    rolled: dict[tuple[str, str], dict[str, Any]] = {}
    for rel in relations:
        a, b = concepts.get(rel["s"]), concepts.get(rel["o"])
        if a is None or b is None:
            continue
        key = (a["kind"], b["kind"])
        row = rolled.setdefault(key, {"s": key[0], "o": key[1], "total": 0, "signed": 0, "machine": 0,
                                      "predicates": Counter(), "examples": []})
        row["total"] += 1
        row[rel["origin"]] += 1
        row["predicates"][rel["p"]] += 1
        if len(row["examples"]) < 6 and (rel["origin"] == "signed" or rel["p"] != "related"):
            row["examples"].append(rel["id"])
    out = []
    for row in sorted(rolled.values(), key=lambda r: (-r["total"], r["s"], r["o"])):
        row["predicates"] = dict(row["predicates"].most_common())
        out.append(row)
    return out


def _predicates(relations: list[dict[str, Any]], labels: dict[str, str],
                concepts: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    approved = approved_predicates()
    out: dict[str, dict[str, Any]] = {}
    for rel in relations:
        row = out.setdefault(rel["p"], {"label": labels.get(rel["p"], _camel(rel["p"])),
                                        "approved": rel["p"] in approved,
                                        "signed": 0, "machine": 0, "example": None})
        row[rel["origin"]] += 1
        if row["example"] is None or (rel["origin"] == "signed" and row["example"]["origin"] != "signed"):
            def name(ref: str) -> str:
                return concepts[ref]["label"] if ref in concepts else views._provision_label(ref)
            row["example"] = {"id": rel["id"], "origin": rel["origin"],
                              "text": f"{name(rel['s'])} — {row['label']} → {name(rel['o'])}"}
    return dict(sorted(out.items(), key=lambda kv: -(kv[1]["signed"] + kv[1]["machine"])))


def ontology(corpus: Corpus, gold: Any, authored: Any, links: links_module.Links) -> dict[str, Any]:
    mentions = {cid: sorted({hit[0] for hit in hits}) for cid, hits in links.mentions.items()}
    concept_list = [_concept(v, mentions, set(links.generic)) for v in views.concept_views(gold, authored)]
    concepts = {c["id"]: c for c in concept_list}
    relations = _relations(gold, authored)
    # A signed record that serves corrected says so, by the correction's id: the
    # page must never show a corrected record as exactly what the expert signed
    # (ADR-0122). A replacement relationship names the signed one it re-reads.
    fixes = corrections_module.load(authored=authored)
    for concept in concept_list:
        if fixes.for_target(concept["id"]):
            concept["corrected"] = [c.id for c in fixes.for_target(concept["id"])]
    replaced = {new: old for old, new in fixes.replacements().items()}
    for rel in relations:
        if rel["id"] in replaced:
            rel["replaces"] = replaced[rel["id"]]
    labels = predicate_labels()
    provisions = sorted({r for c in concept_list for r in c["basis"]}
                        | {x for rel in relations for x in (rel["s"], rel["o"]) if not x.startswith("GC-")})
    kind_list = kinds()
    for kind in kind_list:
        members = [c for c in concept_list if c["kind"] == kind["id"]]
        kind["signed"] = sum(1 for c in members if c["origin"] == "signed")
        kind["machine"] = len(members) - kind["signed"]
    return {
        "kinds": kind_list,
        "families": FAMILIES,
        "concepts": concept_list,
        "relations": relations,
        "kind_links": _kind_links(concepts, relations),
        "predicates": _predicates(relations, labels, concepts),
        "provisions": {ref: {"label": views._provision_label(ref), "source": _source(ref),
                             "title": _provision_title(corpus, ref)} for ref in provisions},
        "counts": {
            "concepts": {"signed": sum(c["origin"] == "signed" for c in concept_list),
                         "machine": sum(c["origin"] == "machine" for c in concept_list)},
            "relations": {"signed": sum(r["origin"] == "signed" for r in relations),
                          "machine": sum(r["origin"] == "machine" for r in relations)},
            "links": sum(len(v) for v in mentions.values()),
            "passages_linked": len({r for v in mentions.values() for r in v}),
        },
    }


def _provision_title(corpus: Corpus, ref: str) -> str | None:
    found = corpus.resolve_provision(ref)
    if found is None:
        return None
    title = getattr(found, "title", None)
    if title:
        return str(title)
    parent = corpus.resolve_provision(views.root_provision(ref) or "")
    return str(getattr(parent, "title", None) or "") or None


# -------------------------------------------------------------------- search


def _recognition(corpus: Corpus, links: links_module.Links) -> tuple[list[Any], set[str]]:
    """The patterns `Systems.recognise` matches — record labels plus everyday
    phrasings — and the lower-cased keys that are only an everyday phrasing,
    which a machine wrote (`bulk aliases`) and the page marks as such."""
    aliases = jobs.load_aliases(corpus, links.concepts)
    extra = {cid: tuple(phrases) for cid, phrases in aliases.items()}
    patterns = links_module._patterns({
        cid: links_module.Concept(id=c.id, pref_label=c.pref_label, labels=c.labels + extra.get(cid, ()),
                                  origin=c.origin)
        for cid, c in links.concepts.items()
    })
    alias_keys = {phrase.lower() for phrases in aliases.values() for phrase in phrases}
    label_keys = {label.lower() for c in links.concepts.values() for label in c.labels}
    return patterns, alias_keys - label_keys


def search(corpus: Corpus, gold: Any, authored: Any, links: links_module.Links) -> dict[str, Any]:
    """Everything `search.index.Systems` uses, less the vectors, for the browser.

    The browser re-implements `Systems.keyword` and `Systems.ontology` without
    the dense ranking; `tests/unit/test_explorer.py` and the parity script pin
    the two together.
    """
    patterns, alias_only = _recognition(corpus, links)
    bases = sorted({r for c in links.concepts.values() for r in c.legislative_basis})
    return {
        "stopwords": sorted(search_index.STOPWORDS),
        "rrf_k": search_index.RRF_K,
        "depth": search_index.DEPTH,
        "min_label": links_module.MIN_LABEL_CHARS,
        # (label as written, concepts carrying it, whether it is only an everyday phrasing)
        "patterns": [[label, list(owners), label.lower() in alias_only] for label, _, owners in patterns],
        "concepts": {cid: {"pref": c.pref_label, "labels": list(c.labels), "basis": list(c.legislative_basis),
                           "not": list(c.not_labels)}
                     for cid, c in links.concepts.items()},
        "generic": sorted(links.generic),
        "mentions": {cid: [hit[0] for hit in hits] for cid, hits in links.mentions.items()},
        "relations": [list(edge) for edge in search_index.relations_from(gold, authored)],
        "citing": {ref: [c.chunk_ref for c in corpus.chunks_citing(ref)] for ref in bases},
    }


# ------------------------------------------------------------------ passages


def passages(corpus: Corpus, also: set[str] = frozenset()) -> dict[str, Any]:
    """Every Manual passage and provision, verbatim, in the keyword index's order,
    plus the units and definitions in `also` (what the concepts rest on)."""
    chunks = sorted(corpus.chunks.values(), key=lambda c: (c.page_ref, c.ordinal))
    rows = []
    legislation_refs: set[str] = set()
    for chunk in chunks:
        cites = [e.id for e in chunk.provisions if not e.needs_a_human]
        legislation_refs.update(cites)
        rows.append([chunk.chunk_ref, chunk.page_ref, " > ".join(chunk.heading_path), chunk.text, cites])
    legislation_refs.update(corpus.provisions)
    legislation_refs.update(also)
    legislation = {}
    for ref in sorted(legislation_refs):
        found = passage_at(corpus, ref)
        if found is None or not found.text:
            continue
        provision = corpus.resolve_provision(ref)
        heading = " > ".join(getattr(provision, "heading_path", ()) or ())
        legislation[ref] = [_source(ref), views._provision_label(ref), heading, found.text]
    pages = {}
    for page in sorted(corpus.pages.values(), key=lambda p: p.page_ref):
        pages[page.page_ref] = {"title": page.nav_title, "part": page.part_id, "url": page.url}
    return {"chunks": rows, "legislation": legislation, "pages": pages, "parts": _part_titles(corpus)}


def _part_titles(corpus: Corpus) -> dict[str, str]:
    titles: dict[str, str] = {}
    for chunk in corpus.chunks.values():
        part = views.manual_part(chunk.chunk_ref)
        if part and chunk.heading_path and part not in titles:
            titles[part] = chunk.heading_path[0]
    return dict(sorted(titles.items(), key=lambda kv: _part_sort(kv[0])))


def _part_sort(part: str) -> tuple[int, str]:
    match = re.match(r"Part(\d+)(.*)", part)
    return (int(match.group(1)), match.group(2)) if match else (999, part)


# ----------------------------------------------------------------- stability


def stability(corpus: Corpus, ontology_data: dict[str, Any], links: links_module.Links) -> dict[str, Any]:
    """What changes in the Manual, and what rests on each page of it.

    The amendment history is upstream's, verbatim. What rests on a page is
    computed from the records' own evidence refs: if the page's text changed,
    these are the records whose quoted span would need re-checking.
    """
    page_of = {ref: chunk.page_ref for ref, chunk in corpus.chunks.items()}
    concept_refs: dict[str, set[str]] = defaultdict(set)
    typing_refs: dict[str, set[str]] = defaultdict(set)
    for concept in ontology_data["concepts"]:
        for ref in concept["sources"]:
            concept_refs[ref].add(concept["id"])
        for item in concept["evidence"]:
            (concept_refs if item["for"] == "concept" else typing_refs)[item["ref"]].add(concept["id"])
    relation_refs: dict[str, set[str]] = defaultdict(set)
    for rel in ontology_data["relations"]:
        if rel.get("ref"):
            relation_refs[str(rel["ref"])].add(rel["id"])
    mention_refs: dict[str, set[str]] = defaultdict(set)
    for cid, hits in links.mentions.items():
        for hit in hits:
            mention_refs[hit[0]].add(cid)

    rows = []
    for page in sorted(corpus.pages.values(), key=lambda p: (_part_sort(p.part_id), p.page_ref)):
        chunk_refs = [ref for ref, pg in page_of.items() if pg == page.page_ref]

        def gather(index: dict[str, set[str]]) -> list[str]:
            return sorted({x for ref in chunk_refs for x in index.get(ref, ())})

        rows.append({
            "ref": page.page_ref, "title": page.nav_title, "part": page.part_id, "url": page.url,
            "passages": len(chunk_refs),
            "amended": [[a.get("date"), (a.get("reason") or "").strip()] for a in page.amendments],
            "concepts": gather(concept_refs), "typings": gather(typing_refs),
            "relations": gather(relation_refs), "mentioned": gather(mention_refs),
            "links": sum(len(mention_refs.get(ref, ())) for ref in chunk_refs),
        })
    events = [(a.get("date") or "", (a.get("reason") or "").strip())
              for page in corpus.pages.values() for a in page.amendments]
    snapshot = max(page.crawled_at for page in corpus.pages.values())
    return {
        "snapshot": snapshot[:10],
        "pages": rows,
        "parts": _part_titles(corpus),
        "events": len(events),
        "by_year": dict(sorted(Counter(d[:4] for d, _ in events if d).items())),
        "reasons": [[reason, n] for reason, n in Counter(r or "(no reason given)" for _, r in events).most_common(12)],
    }


# ------------------------------------------------------------------ examples


def examples() -> dict[str, Any]:
    """The prepared answers, with each search system's score on the same question."""
    bench = jobs.BENCH_DIR
    answers = (yaml.safe_load((bench / "answers.yaml").read_text(encoding="utf-8")) or {}).get("answers", [])
    results = json.loads((bench / "results.json").read_text(encoding="utf-8"))
    scores = {row["key"]: row for row in results.get("rows", [])}
    pools = {p["key"]: p for p in (yaml.safe_load((bench / "pools.yaml").read_text(encoding="utf-8")) or {})
             .get("pools", [])}
    out = []
    for a in answers:
        row = scores.get(a["key"], {})
        out.append({
            "key": a["key"], "kind": a.get("kind"), "question": a["question"], "answer": a["answer"],
            "recognised": a.get("recognised") or [], "paths": a.get("paths") or [],
            "passages": [p["ref"] for p in a.get("passages") or ()],
            "legislation": [p["ref"] for p in a.get("legislation") or ()],
            "plain": [p["ref"] for p in a.get("plain_search") or ()],
            "keyword10": list(pools.get(a["key"], {}).get("systems", {}).get("keyword", [])),
            "citations": [{"ref": c["ref"], "quote": c.get("quote")} for c in a.get("citations") or ()],
            "declined": bool(a.get("declined")), "decline_reason": a.get("decline_reason") or "",
            "model": a.get("model"), "date": str(a.get("date") or ""), "review_status": a.get("review_status"),
            "ndcg": {s: row.get(f"ndcg:{s}") for s in ("keyword", "hybrid", "ontology")},
        })
    return {"kinds": QUESTION_KINDS, "answers": out, "summary": results.get("summary", {})}


# ---------------------------------------------------------------------- tour


def _display_order(corpus: Corpus) -> list[str]:
    """Passages in reading order: by Part number, then page, then position."""
    return [c.chunk_ref for c in sorted(
        corpus.chunks.values(),
        key=lambda c: (_part_sort(views.manual_part(c.chunk_ref) or ""), c.page_ref, c.ordinal))]


def _wordings(corpus: Corpus, concept: dict[str, Any], order: list[str]) -> dict[str, list[int]]:
    """Each of a concept's labels -> the passages (by display position) that use it."""
    out: dict[str, list[int]] = {}
    for label in [concept["label"], *concept["alt"]]:
        if len(label) < links_module.MIN_LABEL_CHARS:
            continue
        pattern = links_module._regex(label)
        hits = [i for i, ref in enumerate(order) if pattern.search(corpus.chunks[ref].text)]
        if hits:
            out[label] = hits
    return out


def tour(corpus: Corpus, onto: dict[str, Any], links: links_module.Links) -> dict[str, Any]:
    """What the guided tour draws: the Manual by Part, a few ideas named many
    ways, and one benchmark question where following connections found what
    keyword search did not. Every figure is computed here from the records and
    the benchmark files; the tour's text only points at them."""
    order = _display_order(corpus)
    parts: list[dict[str, Any]] = []
    titles = _part_titles(corpus)
    for ref in order:
        part = views.manual_part(ref) or "?"
        if not parts or parts[-1]["id"] != part:
            parts.append({"id": part, "title": titles.get(part, part), "n": 0})
        parts[-1]["n"] += 1

    showcase = []
    for concept in onto["concepts"]:
        if concept["origin"] != "signed" or concept["generic"]:
            continue
        wordings = _wordings(corpus, concept, order)
        pref = set(wordings.get(concept["label"], []))
        others = set().union(*(set(v) for k, v in wordings.items() if k != concept["label"])) if wordings else set()
        missed = len(others - pref)
        # A wording found in more than this many passages is an everyday word that
        # happens to be a label ("evidence"), and would overstate the point.
        common = any(len(v) > 120 for k, v in wordings.items() if k != concept["label"])
        if len(wordings) >= 2 and missed >= 5 and not common:
            showcase.append({"id": concept["id"], "label": concept["label"], "kind": concept["kind"],
                             "wordings": wordings, "missed": missed, "named": len(pref),
                             "total": len(pref | others)})
    # The clearest case first: the formal term is rare and the idea is common.
    showcase.sort(key=lambda s: (not 1 <= s["named"] <= 10, -s["missed"], s["id"]))

    example = _tour_example()
    if example:
        patterns, alias_only = _recognition(corpus, links)
        found = links_module.find_mentions(example["question"], patterns, links_module._vetoes(links.concepts))
        for item in example["recognised"]:
            start, end, label = found.get(item["id"], (None, None, None))
            item["matched"] = example["question"][start:end] if start is not None else None
            item["everyday"] = bool(label and label.lower() in alias_only)
        # The connection worth narrating: the one whose far end names the most of
        # the passages only the ontology found — the hop that brought them in.
        recognised = {item["id"] for item in example["recognised"]}
        found = set(example["only_ontology_relevant"])
        named = {cid: {hit[0] for hit in hits} for cid, hits in links.mentions.items()}

        def brought(path: dict[str, Any]) -> tuple[int, bool]:
            far = path["object"] if path["subject"] in recognised else path["subject"]
            return len(named.get(far, set()) & found), path["predicate"] not in ("related", "broader")

        if example["paths"]:
            best = max(example["paths"], key=brought)
            example["path_focus"] = {**best, "brought": brought(best)[0]}
    return {"parts": parts, "passages": len(order), "showcase": showcase[:5], "example": example}


def _tour_example() -> dict[str, Any] | None:
    """An everyday-words question where the ontology system's top ten held the
    most passages the judge graded relevant (2 or 3) that **neither** keyword nor
    hybrid search held — so they came through the ontology, not the vectors —
    breaking ties on the gain over keyword search."""
    bench = jobs.BENCH_DIR
    results = json.loads((bench / "results.json").read_text(encoding="utf-8"))
    pools = {p["key"]: p for p in (yaml.safe_load((bench / "pools.yaml").read_text(encoding="utf-8")) or {})
             .get("pools", [])}
    grades = {j["need"]: j["grades"] for j in (yaml.safe_load(
        (bench / "judgements.yaml").read_text(encoding="utf-8")) or {}).get("judgements", [])}
    answers = {a["key"]: a for a in (yaml.safe_load(
        (bench / "answers.yaml").read_text(encoding="utf-8")) or {}).get("answers", [])}
    def only(pool: dict[str, Any], graded: dict[str, Any]) -> list[str]:
        systems = pool["systems"]
        return [ref for ref in systems["ontology"] if ref not in systems["keyword"]
                and ref not in systems["hybrid"] and (graded.get(ref) or 0) >= 2]

    best = None
    for row in results.get("rows", []):
        key = row["key"]
        answer, pool = answers.get(key), pools.get(key)
        if row.get("kind") != "problem" or not answer or not pool or not answer.get("paths"):
            continue
        rank = (len(only(pool, grades.get(key, {}))), row["ndcg:ontology"] - row["ndcg:keyword"])
        if best is None or rank > best[0]:
            best = (rank, row, answer, pool)
    if best is None:
        return None
    _, row, answer, pool = best
    graded = grades.get(row["key"], {})
    keyword, onto = pool["systems"]["keyword"], pool["systems"]["ontology"]
    return {
        "key": row["key"], "question": answer["question"],
        "ndcg": {s: row[f"ndcg:{s}"] for s in ("keyword", "hybrid", "ontology")},
        "recognised": answer.get("recognised") or [], "paths": answer.get("paths") or [],
        "keyword": [[ref, graded.get(ref)] for ref in keyword],
        "ontology": [[ref, graded.get(ref)] for ref in onto],
        "hybrid": [[ref, graded.get(ref)] for ref in pool["systems"]["hybrid"]],
        "only_ontology_relevant": only(pool, graded),
        "grader": "gpt-6.1-sol",
    }


# ---------------------------------------------------------------------- chat


def chat(ctx: jobs.Context) -> dict[str, Any]:
    """The measured answer prompt, verbatim, so a live question is asked the same way.

    The instructions, the schema and the ontology map come from `bulk.jobs`, the
    code that wrote the 129 prepared answers; the browser assembles the input in
    the shape `_answer_render` does.
    """
    return {
        "model": CHAT_MODEL, "effort": CHAT_EFFORT, "max_output_tokens": CHAT_MAX_OUTPUT_TOKENS,
        "measured_effort": "medium", "prompt_version": "answer-v2",
        "instructions": jobs._ANSWER_INSTRUCTIONS, "schema": jobs._ANSWER_SCHEMA,
        "ontology_map": jobs.ontology_map(ctx),
        "passages_k": 8, "legislation_k": 3, "paths_k": 12, "plain_k": 5, "passage_chars": 1600,
        "daily_limit": DAILY_LIMIT,
        "prices": config.PRICES_PER_MTOK[CHAT_MODEL]["default"],
    }


def live_payload(key: str | None, endpoint: str | None = None) -> dict[str, Any]:
    """Whether the live chat may call a model, and with what.

    With a key, the key is published in the page (the owner's decision,
    ADR-0118). It is masked so that pattern-matching scrapers do not find an
    `sk-` string — which is obfuscation, not security: anyone who reads the
    page's code can recover it. With an endpoint and no key, the browser calls a
    proxy that holds the key instead, and nothing secret is published.
    """
    if not key and not endpoint:
        return {"enabled": False}
    out: dict[str, Any] = {"enabled": True, "endpoint": endpoint or OPENAI_RESPONSES}
    if key:
        raw = key.strip().encode("utf-8")
        mask = secrets.token_bytes(len(raw))
        mixed = bytes(a ^ b for a, b in zip(raw, mask))[::-1]
        out["m"] = base64.b64encode(mask).decode("ascii")
        out["x"] = base64.b64encode(mixed).decode("ascii")
    return out


# --------------------------------------------------------------------- build


def build(corpus: Corpus | None = None, *, generated: str | None = None,
          key: str | None = None, endpoint: str | None = None) -> dict[str, Any]:
    """Every file, as data. `write` puts them on disk."""
    corpus = corpus or load_corpus()
    # What serves: the signed records with the owner's corrections applied (ADR-0122).
    gold = corrections_module.served_gold()
    authored = authored_store.load()
    links = links_module.link(corpus)
    ctx = jobs.Context(corpus=corpus, links=links, gold=gold, authored=authored)
    onto = ontology(corpus, gold, authored, links)
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    onto["build"] = {"generated": generated or date.today().isoformat(), "upstream": pin["commit"][:12]}
    return {
        "ontology.json": onto,
        "search.json": search(corpus, gold, authored, links),
        "passages.json": passages(corpus, {r for c in links.concepts.values() for r in c.legislative_basis}
                                  | set(onto["provisions"])),
        "stability.json": stability(corpus, onto, links),
        "tour.json": tour(corpus, onto, links),
        "examples.json": examples(),
        "chat.json": chat(ctx),
        "live.json": live_payload(key, endpoint),
    }


def write(files: dict[str, Any], out_dir: Path | None = None) -> list[Path]:
    out_dir = out_dir or DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in files.items():
        path = out_dir / name
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        written.append(path)
    return written


def from_environment() -> tuple[str | None, str | None]:
    return os.environ.get(KEY_ENV) or None, os.environ.get(ENDPOINT_ENV) or None

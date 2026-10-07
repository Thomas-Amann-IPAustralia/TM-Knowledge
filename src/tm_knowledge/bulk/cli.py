"""`tmk-bulk` — the pipeline's command line.

    tmk-bulk links [--write]                 the free pass: mentions and candidate pairs
    tmk-bulk run JOB --dry-run               what a run would cost; spends nothing
    tmk-bulk run JOB --limit 3 --confirm     a smoke run: cached, capped, reported
    tmk-bulk run JOB --confirm --write       the same, and write what passed checks
    tmk-bulk spend                           recorded spend against the cap
    tmk-bulk quote --write                   price the full runs from what was measured

A run with `--confirm` and without `--write` still caches every response, so
writing afterwards is free: read the smoke run's report first (KB SOP §6).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from tm_knowledge import config
from tm_knowledge.bulk import client, jobs
from tm_knowledge.bulk import links as links_module
from tm_knowledge.config import REPO_ROOT

REPORTS_DIR = REPO_ROOT / "data" / "derived" / "reports"


def _context() -> jobs.Context:
    from tm_knowledge.upstream.loader import load_corpus

    corpus = load_corpus()
    return jobs.Context(corpus=corpus, links=links_module.link(corpus))


def search_engine(ctx: jobs.Context):
    """Keyword index plus ontology expansion over both stores' relationships."""
    from tm_knowledge.search.index import KeywordIndex, OntologySearch

    neighbours: dict[str, set[str]] = {}
    for records in (ctx.gold["gold_relationship"], ctx.authored["gold_relationship"]):
        for r in records:
            s, o = str(r["subject"]), str(r["object"])
            if s.startswith("GC-") and o.startswith("GC-"):
                neighbours.setdefault(s, set()).add(o)
                neighbours.setdefault(o, set()).add(s)
    return OntologySearch(KeywordIndex(ctx.corpus), ctx.links, jobs.load_aliases(), neighbours)


def _questions(ctx: jobs.Context) -> list[dict[str, Any]]:
    """Benchmark needs, then the expert's signed retrieval questions as a cross-check."""
    rows = []
    path = jobs.BENCH_DIR / "needs.yaml"
    if path.exists():
        for need in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("needs", []):
            rows.append({"key": need["id"], "question": need["question"], "narrative": need["narrative"],
                         "required": []})
    for record in ctx.gold["gold_retrieval_question"]:
        rows.append({"key": record["id"], "question": record["question"],
                     "narrative": str(record.get("qualifications_expected") or ""),
                     "required": [r for r in record.get("required_evidence") or () if r in ctx.corpus.chunks]})
    return rows


def _measurement_items(job: str, ctx: jobs.Context) -> list[jobs.Item]:
    engine = search_engine(ctx)
    items = []
    for q in _questions(ctx):
        if job == "judge":
            pooled = [h.ref for h in engine.index.search(q["question"], 15)]
            hits, _ = engine.search(q["question"], 15)
            pooled += [h.ref for h in hits] + q["required"]
            pool = sorted(set(pooled), key=lambda r: hashlib.sha256((q["key"] + r).encode()).hexdigest())
            items.append(jobs.Item(q["key"], {**q, "pool": pool}))
        else:
            hits, recognised = engine.search(q["question"], 8)
            items.append(jobs.Item(q["key"], {**q, "passages": [h.ref for h in hits], "recognised": recognised}))
    return items


def _select(items: list[jobs.Item], args: argparse.Namespace) -> list[jobs.Item]:
    if args.items:
        wanted = set(args.items.split(","))
        items = [i for i in items if i.key in wanted]
    items = items[args.offset:]
    return items[: args.limit] if args.limit else items


def _run(args: argparse.Namespace) -> int:
    ctx = _context()
    registry = jobs.registry(ctx)
    if args.job not in registry:
        print(f"unknown job {args.job!r}; one of {', '.join(registry)}", file=sys.stderr)
        return 2
    job = registry[args.job]
    all_items = _measurement_items(args.job, ctx) if args.job in ("judge", "answer") else job.items(ctx)
    items = _select(all_items, args)
    model = args.model or config.authoring_model()
    effort = args.effort or config.DEFAULT_AUTHORING_EFFORT

    totals: Counter[str] = Counter()
    worst = 0.0
    new_cost = 0.0
    records: dict[str, list[dict[str, Any]]] = {}
    refused: list[str] = []
    notes: list[str] = []
    per_item: list[str] = []
    for item in items:
        text = job.render(ctx, item)
        try:
            entry, estimate = client.respond(
                job=job.name, prompt_version=job.prompt_version, item=item.key,
                instructions=job.instructions, input_text=text, schema=job.schema,
                max_output_tokens=job.max_output_tokens, model=model, effort=effort, tier=args.tier,
                confirm=args.confirm, dry_run=args.dry_run,
            )
        except (client.BudgetExceeded, client.NotConfirmed) as error:
            print(f"stopped: {error}", file=sys.stderr)
            break
        worst += estimate.worst_case_usd
        if entry is None:
            totals["estimated"] += 1
            continue
        if not entry.get("from_cache"):
            new_cost += float(entry["cost_usd"])
        totals["calls"] += 1
        parsed = jobs.parse(entry)
        if parsed is None:
            refused.append(f"{item.key}: response not parseable (status {entry.get('status')})")
            continue
        outcome = job.accept(ctx, item, parsed, entry)
        totals["proposed"] += outcome.proposed
        for kind, rows in outcome.records.items():
            records.setdefault(kind, []).extend(rows)
            totals["accepted"] += len(rows) if kind not in ("concept_types",) else 0
        refused += outcome.refused
        notes += outcome.notes
        usage = entry.get("usage") or {}
        per_item.append(
            f"| `{item.key}` | {usage.get('input_tokens', '?')} | "
            f"{(usage.get('output_tokens_details') or {}).get('reasoning_tokens', '?')} | "
            f"{usage.get('output_tokens', '?')} | ${float(entry['cost_usd']):.4f}"
            f"{' (cached)' if entry.get('from_cache') else ''} | {outcome.proposed} | "
            f"{sum(len(v) for k, v in outcome.records.items() if k != 'concept_types')} |"
        )

    if args.dry_run:
        print(f"{job.name}: {totals['estimated']} uncached of {len(items)} selected "
              f"({len(all_items)} in a full run); worst case ${worst:.2f}, nothing spent. "
              f"Recorded spend ${client.Cache().spent_usd():.4f} of ${config.spend_cap_usd():.2f}.")
        return 0

    written: list[Path] = job.write(records) if args.write else []
    report = _report(job, model, effort, args, items, len(all_items), totals, new_cost, per_item,
                     refused, notes, written)
    print(f"{job.name}: {totals['calls']} calls, {totals['proposed']} proposed, {totals['accepted']} accepted, "
          f"{len(refused)} refused; this run spent ${new_cost:.4f}; recorded spend "
          f"${client.Cache().spent_usd():.4f} of ${config.spend_cap_usd():.2f}. Report: {report}")
    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def _report(job, model, effort, args, items, full, totals, new_cost, per_item, refused, notes, written) -> Path:
    path = REPORTS_DIR / f"bulk-{job.name}.md"
    lines = [
        f"# `tmk-bulk run {job.name}` — {job.describe}", "",
        f"Prompt `{job.prompt_version}` · model `{model}` · effort `{effort}` · tier `{args.tier}` · "
        f"{len(items)} of {full} items · written: {'yes' if written else 'no'}", "",
        f"**{totals['calls']} calls, {totals['proposed']} judgements proposed, {totals['accepted']} accepted, "
        f"{len(refused)} refused.** This run spent ${new_cost:.4f}; recorded spend across every job "
        f"${client.Cache().spent_usd():.4f} of the ${config.spend_cap_usd():.2f} cap.", "",
        "Everything accepted is machine-written and unreviewed; nothing here was read by an expert.", "",
        "| Item | Input tokens | Reasoning tokens | Output tokens | Cost | Proposed | Accepted |",
        "|---|---|---|---|---|---|---|", *per_item, "",
    ]
    if refused:
        lines += ["## Refused — and why", "", *[f"- {r}" for r in refused], ""]
    if notes:
        lines += ["## Notes for a person", "", *[f"- {n}" for n in notes], ""]
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _links(args: argparse.Namespace) -> int:
    ctx = _context()
    already = links_module.existing_edges(ctx.gold, ctx.authored)
    pair_list = links_module.pairs(ctx.links, already)
    groups = links_module.anchors(pair_list)
    tagged = len(ctx.links.by_passage())
    print(f"{len(ctx.links.concepts)} concepts name something in {tagged} of {ctx.links.passages} passages; "
          f"generic: {', '.join(sorted(ctx.links.generic)) or 'none'}. {len(pair_list)} candidate pairs "
          f"in {len(groups)} relationship calls; {len(already)} pairs already joined by a record.")
    if args.write:
        for path in links_module.write(ctx.links, pair_list):
            print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def _spend(args: argparse.Namespace) -> int:
    cache = client.Cache()
    by_job: Counter[str] = Counter()
    calls: Counter[str] = Counter()
    for entry in cache.entries():
        by_job[entry["job"]] += float(entry.get("cost_usd") or 0)
        calls[entry["job"]] += 1
    for job_name in sorted(by_job):
        print(f"{job_name:10} {calls[job_name]:4} calls  ${by_job[job_name]:.4f}")
    print(f"{'total':10} {sum(calls.values()):4} calls  ${cache.spent_usd():.4f} of ${config.spend_cap_usd():.2f}")
    return 0


def _quote(args: argparse.Namespace) -> int:
    from tm_knowledge.bulk import quote

    ctx = _context()
    text = quote.render(quote.build(ctx))
    if args.write:
        quote.QUOTE_PATH.write_text(text, encoding="utf-8")
        print(f"wrote {quote.QUOTE_PATH.relative_to(REPO_ROOT)}")
    else:
        print(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tmk-bulk", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("links", help="the free pass: mentions and candidate pairs")
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("run", help="run one paid job")
    p.add_argument("job")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--items", help="comma-separated item keys")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--confirm", action="store_true", help="allow paid calls")
    p.add_argument("--write", action="store_true", help="write accepted records")
    p.add_argument("--model")
    p.add_argument("--effort", choices=["none", "low", "medium", "high"])
    # Flex is half price on the same endpoint (ADR-0111); the Batch API is the same
    # price through a different door, and not wired up here.
    p.add_argument("--tier", choices=["flex", "default"], default="flex")
    sub.add_parser("spend", help="recorded spend against the cap")
    p = sub.add_parser("quote", help="price the full runs")
    p.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    return {"links": _links, "run": _run, "spend": _spend, "quote": _quote}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

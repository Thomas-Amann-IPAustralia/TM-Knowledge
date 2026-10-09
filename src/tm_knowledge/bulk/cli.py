"""`tmk-bulk` — the pipeline's command line.

    tmk-bulk links [--write]                 the free pass: mentions and candidate pairs
    tmk-bulk run JOB --dry-run               what a run would cost; spends nothing
    tmk-bulk run JOB --limit 3 --confirm     a smoke run: cached, capped, reported
    tmk-bulk run JOB --confirm --write       the same, and write what passed checks
    tmk-bulk spend                           recorded spend against the cap
    tmk-bulk quote --write                   price the full runs from what was measured
    tmk-bulk audit-apply [--write]           act on the edge audit: re-read or withdraw the wrong ones

A run with `--confirm` and without `--write` still caches every response, so
writing afterwards is free: read the smoke run's report first (KB SOP §6).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from datetime import date
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
    cache = client.Cache()
    return jobs.Context(corpus=corpus, links=links_module.link(corpus),
                        judged=jobs.judged_pairs(cache.entries("relate")),
                        defined={str(e["item"]) for e in cache.entries("define") if e.get("status") == "completed"})


def search_systems(ctx: jobs.Context):
    """The three systems of `search.index`, over both stores and the vector store."""
    from tm_knowledge.search.index import KeywordIndex, Systems, relations_from
    from tm_knowledge.search.vectors import Dense

    dense = Dense()
    return Systems(KeywordIndex(ctx.corpus), ctx.links, dense if dense.ready else None,
                   jobs.load_aliases(ctx.corpus, ctx.links.concepts), relations_from(ctx.gold, ctx.authored))


def _questions(ctx: jobs.Context) -> list[dict[str, Any]]:
    """Benchmark needs, then the expert's signed retrieval questions as a cross-check."""
    rows = []
    path = jobs.BENCH_DIR / "needs.yaml"
    if path.exists():
        for need in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("needs", []):
            rows.append({"key": need["id"], "kind": need["kind"], "question": need["question"],
                         "narrative": need["narrative"], "required": []})
    for record in ctx.gold["gold_retrieval_question"]:
        rows.append({"key": record["id"], "kind": "signed", "question": record["question"],
                     "narrative": str(record.get("qualifications_expected") or ""),
                     "required": [r for r in record.get("required_evidence") or () if r in ctx.corpus.chunks]})
    return rows


POOLS_PATH = jobs.BENCH_DIR / "pools.yaml"


def _require_vectors(systems: Any, questions: list[dict[str, Any]]) -> None:
    """Without vectors "hybrid" is keyword search under another name: refuse to measure it."""
    if systems.dense is None:
        raise SystemExit("no passage vectors: run `tmk-bulk embed --confirm` first (ADR-0115)")
    missing = [q["key"] for q in questions if systems.dense.query_vector(q["question"]) is None]
    if missing:
        raise SystemExit(f"{len(missing)} questions have no vector (first: {missing[0]}): "
                         "run `tmk-bulk embed --confirm` first (ADR-0115)")


def _pools(ctx: jobs.Context, variants: dict[str, dict[str, list[str]]] | None = None) -> list[dict[str, Any]]:
    """Every question's top ten from each system, and the pool the judge grades.

    `variants` are other rankings to score on the same grades — the ontology system as
    last measured, or run on another state of the records — so a change is measured,
    not guessed at. They join the pool, because a passage nobody graded scores 0."""
    systems = search_systems(ctx)
    questions = _questions(ctx)
    _require_vectors(systems, questions)
    out = []
    for q in questions:
        ranked = {
            "keyword": [h.ref for h in systems.keyword(q["question"], 10)],
            "hybrid": [h.ref for h in systems.hybrid(q["question"], 10)],
            "ontology": [h.ref for h in systems.ontology(q["question"], 10)[0]],
        }
        extra = {name: list(rankings[q["key"]])[:10] for name, rankings in (variants or {}).items()
                 if q["key"] in rankings}
        pooled = {ref for refs in [*ranked.values(), *extra.values()] for ref in refs} | set(q["required"])
        pool = sorted(pooled, key=lambda r: hashlib.sha256((q["key"] + r).encode()).hexdigest())
        row = {"key": q["key"], "kind": q["kind"], "question": q["question"], "systems": ranked}
        if extra:
            row["variants"] = extra
        out.append({**row, "pool": pool})
    return out


def _graded() -> dict[str, dict[str, int]]:
    """Every grade already given, by question: a passage is graded once and keeps it."""
    path = jobs.BENCH_DIR / "judgements.yaml"
    rows = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("judgements", []) if path.exists() else []
    return {r["need"]: {k: int(v) for k, v in r["grades"].items()} for r in rows}


def _measurement_items(job: str, ctx: jobs.Context) -> list[jobs.Item]:
    questions = {q["key"]: q for q in _questions(ctx)}
    if job == "judge":
        if not POOLS_PATH.exists():
            raise SystemExit("no pools yet: run `tmk-bulk pools --write` after the ontology and vectors are in")
        pools = (yaml.safe_load(POOLS_PATH.read_text(encoding="utf-8")) or {}).get("pools", [])
        # Only what nobody has graded: a re-pooled question sends its new passages, and a
        # grade once given stands, so a re-measurement costs only what changed (ADR-0127).
        graded = _graded()
        items = []
        for p in pools:
            if p["key"] not in questions:
                continue
            todo = [ref for ref in p["pool"] if ref not in graded.get(p["key"], {})]
            if todo:
                items.append(jobs.Item(p["key"], {**questions[p["key"]], "pool": todo}))
        return items
    systems = search_systems(ctx)
    _require_vectors(systems, list(questions.values()))
    items = []
    for q in questions.values():
        hits, trace = systems.ontology(q["question"], 8)
        passages = [h.ref for h in hits]
        legislation: list[str] = []
        cited = [e.id for ref in passages[:3] for e in ctx.corpus.chunks[ref].provisions if not e.needs_a_human]
        for ref in trace.provisions + cited:
            passage = jobs.passage_at(ctx.corpus, ref)
            if ref not in legislation and passage is not None and passage.text:
                legislation.append(ref)
        items.append(jobs.Item(q["key"], {
            **q, "passages": passages, "legislation": legislation[:3],
            "recognised": trace.recognised, "neighbours": trace.neighbours,
            "paths": [list(p) for p in trace.paths][:12],
            "plain": [h.ref for h in systems.keyword(q["question"], 5)],
        }))
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
    if args.touching:
        ctx.touching = {cid.strip() for cid in args.touching.split(",") if cid.strip()}
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
    stop = threading.Event()

    def call(item: jobs.Item):
        if stop.is_set():
            return item, None, None, "not sent: an earlier call stopped the run"
        try:
            entry, estimate = client.respond(
                job=job.name, prompt_version=job.prompt_version, item=item.key,
                instructions=job.instructions, input_text=job.render(ctx, item), schema=job.schema,
                max_output_tokens=job.max_output_tokens, model=model, effort=effort, tier=args.tier,
                confirm=args.confirm, dry_run=args.dry_run,
            )
            return item, entry, estimate, None
        except (client.BudgetExceeded, client.NotConfirmed) as error:
            stop.set()
            return item, None, None, f"stopped: {error}"
        except client.Queued as error:
            return item, None, None, f"queued: {error}"
        except RuntimeError as error:  # an HTTP failure: no answer, reported, the run goes on
            return item, None, None, f"failed: {error}"

    if args.tier == "batch":
        # One upload per batch; answers come back together and are handled in order.
        requests = [dict(job=job.name, prompt_version=job.prompt_version, item=item.key,
                         instructions=job.instructions, input_text=job.render(ctx, item), schema=job.schema,
                         max_output_tokens=job.max_output_tokens, model=model, effort=effort)
                    for item in items]
        try:
            answers = client.batch_respond(requests, confirm=args.confirm, dry_run=args.dry_run,
                                           progress=lambda line: print(line, file=sys.stderr, flush=True))
            results = [(item, entry, estimate, None if (entry or args.dry_run) else "no answer")
                       for item, (entry, estimate) in zip(items, answers)]
        except (client.BudgetExceeded, client.NotConfirmed) as error:
            print(f"stopped: {error}", file=sys.stderr)
            results = [(item, None, None, f"stopped: {error}") for item in items]
    else:
        # Parallel calls, results handled in item order so a run reads the same twice.
        # An overloaded flex call fails in seconds and costs nothing (Q-67), so keep
        # trying on a short, capped backoff rather than giving the item up.
        client.RETRY_WAITS = tuple(min(10 * 2 ** i, 60) for i in range(max(0, args.retries)))
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            results = list(pool.map(call, items))

    for item, entry, estimate, problem in results:
        if args.dry_run and problem is None and entry is None:
            worst += estimate.worst_case_usd if estimate else 0.0
            totals["estimated"] += 1
            continue
        if problem:
            if problem.startswith("stopped"):
                print(problem, file=sys.stderr)
            refused.append(f"{item.key}: {problem}")
            continue
        worst += estimate.worst_case_usd
        if entry is None:
            totals["estimated"] += 1
            continue
        if not entry.get("from_cache"):
            new_cost += float(entry["cost_usd"])
        if entry.get("status") == "failed":  # nothing came back and nothing was billed
            code = (entry.get("error") or {}).get("code") if isinstance(entry.get("error"), dict) else None
            refused.append(f"{item.key}: no answer ({code or 'failed'}) — a re-run asks again")
            continue
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


def _embed(args: argparse.Namespace) -> int:
    from tm_knowledge.search import vectors

    ctx = _context()
    n, est = vectors.embed_passages(ctx.corpus, confirm=args.confirm, dry_run=args.dry_run)
    q, est_q = vectors.embed_queries([q["question"] for q in _questions(ctx)], confirm=args.confirm,
                                     dry_run=args.dry_run)
    verb = "would cost at most" if args.dry_run else "done; this run's worst case was"
    print(f"embed: {n} passages and {q} questions; {verb} ${est + est_q:.4f}. "
          f"Recorded spend ${client.Cache().spent_usd():.4f} of ${config.spend_cap_usd():.2f}.")
    return 0


def _pools_cmd(args: argparse.Namespace) -> int:
    ctx = _context()
    variants: dict[str, dict[str, list[str]]] = {}
    notes: dict[str, str] = {}
    previous = (yaml.safe_load(POOLS_PATH.read_text(encoding="utf-8")) or {}) if POOLS_PATH.exists() else {}
    if args.keep_previous:
        variants["ontology_previous"] = {p["key"]: p["systems"]["ontology"] for p in previous.get("pools", [])}
        notes["ontology_previous"] = (f"the ontology system's top ten as last measured"
                                      f"{' (' + previous['measured'] + ')' if previous.get('measured') else ''}")
    for spec in args.variant or ():
        name, _, path = spec.partition("=")
        document = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        variants[name] = document["rankings"]
        notes[name] = str(document.get("note") or name)
    pools = _pools(ctx, variants)
    graded = _graded()
    sizes = [len(p["pool"]) for p in pools]
    todo = sum(1 for p in pools for ref in p["pool"] if ref not in graded.get(p["key"], {}))
    print(f"pools: {len(pools)} questions, {sum(sizes)} passages pooled "
          f"(mean {sum(sizes) / max(len(sizes), 1):.1f} per question), {todo} not yet graded")
    if args.write:
        POOLS_PATH.parent.mkdir(parents=True, exist_ok=True)
        document = {"note": "Each question's top ten from the three systems (search.index), and the pool the "
                            "judge grades. Fixed before judging; the measurement scores exactly these rankings.",
                    "measured": date.today().isoformat()}
        if notes:
            document["variants"] = notes
        POOLS_PATH.write_text(yaml.safe_dump({**document, "pools": pools}, sort_keys=False, allow_unicode=True,
                                             width=100), encoding="utf-8")
        print(f"wrote {POOLS_PATH.relative_to(REPO_ROOT)}")
    return 0


def _measure(args: argparse.Namespace) -> int:
    import json

    from tm_knowledge.search import measure

    pools = (yaml.safe_load(POOLS_PATH.read_text(encoding="utf-8")) or {}).get("pools", [])
    path = jobs.BENCH_DIR / "judgements.yaml"
    rows = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("judgements", []) if path.exists() else []
    judgements = {r["need"]: {k: int(v) for k, v in r["grades"].items()} for r in rows}
    models = sorted({r.get("model", "?") for r in rows} | {x.get("model", "?") for r in rows for x in r.get("later") or ()})
    document = (yaml.safe_load(POOLS_PATH.read_text(encoding="utf-8")) or {})
    scored = measure.score(pools, judgements)
    summary = measure.summarise(scored["rows"], scored["variants"])
    cases = measure.examples(scored["rows"], {p["key"]: p["question"] for p in pools})
    from tm_knowledge.authored.corrections import served_gold

    required = {str(r["id"]): list(r.get("required_evidence") or ())
                for r in served_gold()["gold_retrieval_question"]}
    evidence = measure.by_evidence(pools, required)
    text = measure.render(summary, judged=sum(len(g) for g in judgements.values()), pooled=len(judgements),
                          judge_model=", ".join(models), cases=cases, variants=document.get("variants") or {},
                          measured=document.get("measured"), evidence=evidence)
    print(text)
    if args.write:
        (REPORTS_DIR / "measure.md").write_text(text, encoding="utf-8")
        (jobs.BENCH_DIR / "results.json").write_text(json.dumps(
            {"summary": summary, "rows": scored["rows"], "cases": cases, "by_evidence": evidence}, indent=1,
            sort_keys=True) + "\n",
            encoding="utf-8")
        print("wrote data/derived/reports/measure.md and data/derived/bench/results.json")
    return 0


def _audit_apply(args: argparse.Namespace) -> int:
    """Act on the second model's verdicts (D5): re-read or withdraw every wrong one."""
    from tm_knowledge.bulk import audit

    verdicts = audit.load_verdicts()
    if not verdicts:
        print("no verdicts yet: run `tmk-bulk run audit --tier batch --confirm --write` first", file=sys.stderr)
        return 1
    ctx = _context()
    entries = ctx.authored.of("gold_relationship")
    authors = {e.record_id: e.authored_by or "?" for e in entries}
    predicates = {e.record_id: str(e.record.get("predicate")) for e in entries}
    actions = audit.plan(ctx, verdicts)
    counts = Counter(a.kind for a in actions)
    print(f"audit: {len(verdicts)} verdicts, {sum(1 for v in verdicts if v['verdict'] == 'wrong')} wrong — "
          f"{counts['reread']} to re-read, {counts['withdraw']} to withdraw, {counts['keep']} kept as entailing "
          f"the correction, {counts['skip']} skipped")
    if not args.write:
        print("(dry run — nothing written. Pass --write.)")
        return 0
    text = audit.render(verdicts, authors, predicates, actions)
    done = audit.apply(actions)
    audit.REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    audit.REPORT_PATH.write_text(text, encoding="utf-8")
    print(f"re-read {done['reread']}, withdrew {done['withdrawn']}; wrote "
          f"{audit.REPORT_PATH.relative_to(REPO_ROOT)}. Rebuild the graph next.")
    return 0


def _spend(args: argparse.Namespace) -> int:
    cache = client.Cache()
    by_job: Counter[str] = Counter()
    calls: Counter[str] = Counter()
    done: Counter[str] = Counter()
    for entry in cache.entries():
        by_job[entry["job"]] += float(entry.get("cost_usd") or 0)
        calls[entry["job"]] += 1
        done[entry["job"]] += entry.get("status") == "completed"
    # Attempts include every failed flex call, which costs nothing (Q-67): divide
    # dollars by *completed* calls to price a job, never by attempts (Q-85).
    for job_name in sorted(by_job):
        print(f"{job_name:12} {done[job_name]:4} completed of {calls[job_name]:4} attempts  ${by_job[job_name]:.4f}")
    print(f"{'total':12} {sum(done.values()):4} completed of {sum(calls.values()):4} attempts  "
          f"${cache.spent_usd():.4f} of ${config.spend_cap_usd():.2f}")
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
    # Batch and flex both cost half the standard price (ADR-0111). Flex is the
    # default: an overloaded flex call fails fast and free and is retried, while
    # a batch can sit untouched for half an hour or more (Q-67).
    p.add_argument("--tier", choices=["batch", "flex", "default"], default="flex")
    p.add_argument("--workers", type=int, default=6, help="calls in flight at once")
    p.add_argument("--retries", type=int, default=12, help="retries of an overloaded flex call")
    p.add_argument("--touching", help="relate only: just the pairs that touch these concept ids, "
                                      "so a pass for new concepts can run beside another pass")
    p = sub.add_parser("embed", help="vectors for every passage and benchmark question")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--confirm", action="store_true")
    p = sub.add_parser("pools", help="each question's top ten per system, and the pool to judge")
    p.add_argument("--write", action="store_true")
    p.add_argument("--keep-previous", action="store_true",
                   help="also score the ontology system's rankings from the pools being replaced")
    p.add_argument("--variant", action="append", metavar="NAME=FILE",
                   help="also score these rankings (YAML: note, rankings: {question key: [refs]})")
    p = sub.add_parser("measure", help="score the systems from the judged pools")
    p.add_argument("--write", action="store_true")
    sub.add_parser("collect", help="record every finished batch")
    p = sub.add_parser("audit-apply", help="re-read or withdraw what the edge audit found wrong")
    p.add_argument("--write", action="store_true")
    sub.add_parser("spend", help="recorded spend against the cap")
    p = sub.add_parser("quote", help="price the full runs")
    p.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    return {"links": _links, "run": _run, "embed": _embed, "pools": _pools_cmd, "measure": _measure,
            "collect": lambda a: (print("open:", client.collect_batches()) or 0),
            "audit-apply": _audit_apply,
            "spend": _spend, "quote": _quote}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

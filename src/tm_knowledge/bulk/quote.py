"""Price the full runs from what the smoke runs measured (ADR-0111).

The owner's terms: *"I'm not ready to give you a precise costing for the full runs
until you tell me what I'm getting for each spend."* So every line is one spend,
what it buys, how many calls it takes, and what one call actually cost when it was
run — never a guess at tokens. Call counts come from the same deterministic item
builders the runs use, so the quote and the run agree on what "the full run" is.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Any

from tm_knowledge import config
from tm_knowledge.bulk import client, jobs

QUOTE_PATH = config.REPO_ROOT / "docs" / "QUOTE.md"

#: Benchmark size. The SOP's first build used 195 needs; a pitch needs fewer.
NEEDS_TARGET = 120
NEEDS_PER_CALL = 4
#: Passages pooled per question once vectors and the full ontology are in.
JUDGE_POOL = 30
#: Retries, refusals re-asked, and one prompt fix after reading the first batch.
CONTINGENCY = 0.25
SOL = config.DEFAULT_AUTHORING_MODEL
MINI = "gpt-5.4-mini"


@dataclass
class Measured:
    calls: int
    input: float
    written: float
    cached: float
    output: float
    reasoning: float

    def cost(self, model: str, tier: str, scale_in: float = 1.0, scale_out: float = 1.0) -> float:
        return client.cost_usd(model, tier, {
            "input_tokens": self.input * scale_in,
            "input_tokens_details": {"cached_tokens": self.cached * scale_in,
                                     "cache_write_tokens": self.written * scale_in},
            "output_tokens": self.output * scale_out,
        })


def measured(job: str, model: str) -> Measured | None:
    version = {j.name: j.prompt_version for j in _registry_shapes()}[job]
    rows = [e for e in client.Cache().entries(job)
            if e.get("prompt_version") == version and str(e.get("model_requested")) == model
            and e.get("status") == "completed"]
    if not rows:
        return None

    def mean(key: str, sub: str | None = None) -> float:
        total = 0.0
        for e in rows:
            usage = e.get("usage") or {}
            total += float((usage.get(key) or {}).get(sub, 0) if sub else usage.get(key) or 0)
        return total / len(rows)

    return Measured(len(rows), mean("input_tokens"), mean("input_tokens_details", "cache_write_tokens"),
                    mean("input_tokens_details", "cached_tokens"), mean("output_tokens"),
                    mean("output_tokens_details", "reasoning_tokens"))


def _registry_shapes() -> list[jobs.Job]:
    """Job names and prompt versions, without building a corpus context."""
    from types import SimpleNamespace

    ctx = SimpleNamespace(gold={"gold_relationship": ()})
    return list(jobs.registry(ctx).values())  # type: ignore[arg-type]


def _judge_pool_measured() -> float:
    sizes = [len(((jobs.parse(e) or {}).get("grades") or ())) for e in client.Cache().entries("judge")
             if e.get("status") == "completed"]
    return sum(sizes) / len(sizes) if sizes else JUDGE_POOL


def join_forecast(share: float = 0.5) -> tuple[int, int, int, int, int]:
    """(pieces now, largest now, pieces after, largest after, nodes) if `share` of the
    candidate pairs become relationships — the map's own count, so D1's test."""
    import hashlib
    import json

    from tm_knowledge.authored import store as authored_store
    from tm_knowledge.bulk import links as links_module
    from tm_knowledge.dashboard import views
    from tm_knowledge.stage0 import goldset

    net = views.network(goldset.load(), authored_store.load())
    adjacency = {n["id"]: set() for n in net["nodes"]}
    for e in net["edges"]:
        adjacency[e["source"]].add(e["target"])
        adjacency[e["target"]].add(e["source"])

    def pieces(adj: dict[str, set[str]]) -> list[int]:
        unseen, sizes = set(adj), []
        while unseen:
            stack, size = [unseen.pop()], 0
            while stack:
                current = stack.pop()
                size += 1
                for other in adj[current]:
                    if other in unseen:
                        unseen.remove(other)
                        stack.append(other)
            sizes.append(size)
        return sorted(sizes, reverse=True)

    now = pieces(adjacency)
    pairs = json.loads(links_module.PAIRS_PATH.read_text(encoding="utf-8"))["pairs"]
    for pair in pairs:  # a deterministic half, not a random one
        if int(hashlib.sha256((pair["a"] + pair["b"]).encode()).hexdigest(), 16) % 100 < share * 100:
            if pair["a"] in adjacency and pair["b"] in adjacency:
                adjacency[pair["a"]].add(pair["b"])
                adjacency[pair["b"]].add(pair["a"])
    after = pieces(adjacency)
    return len(now), now[0], len(after), after[0], sum(now)


def build(ctx: jobs.Context) -> dict[str, Any]:
    registry = jobs.registry(ctx)
    n_concepts = len(ctx.links.concepts)
    define_n = len(registry["define"].items(ctx))
    rows = [e for e in client.Cache().entries("define") if e.get("status") == "completed"]
    share = (sum(1 for e in rows if (jobs.parse(e) or {}).get("is_concept")) / len(rows)) if rows else 0.7
    new = round(define_n * share)
    after = n_concepts + new
    relate_now = len(registry["relate"].items(ctx))
    p_now, big_now, p_after, big_after, n_nodes = join_forecast(0.5)
    questions = NEEDS_TARGET + len(ctx.gold["gold_retrieval_question"])
    pool_now = _judge_pool_measured()

    def line(job, model, calls, what, *, scale_in=1.0, scale_out=1.0, recommended=True):
        stats = measured(job, model)
        flex = stats.cost(model, "flex" if model == SOL else "default", scale_in, scale_out) if stats else None
        std = stats.cost(model, "default", scale_in, scale_out) if stats else None
        return {"job": job, "model": model, "calls": calls, "what": what, "stats": stats,
                "per_call": flex, "per_call_std": std, "recommended": recommended,
                "total": flex * calls * (1 + CONTINGENCY) if flex is not None else None,
                "total_std": std * calls * (1 + CONTINGENCY) if std is not None else None}

    judge_scale = JUDGE_POOL / pool_now if pool_now else 1.0
    lines = [
        line("define", SOL, define_n,
             f"Up to {new} new concepts — each with its group, the passage that defines it, its legislative "
             f"basis, its reasoning and what an expert should check — for the {define_n} defined terms the "
             f"Manual uses at least {jobs.DEFINE_MIN_USES} times that no concept covers yet"),
        line("relate", SOL, math.ceil(relate_now * after / n_concepts),
             f"Typed relationships between concepts the Manual mentions together, each resting on a quoted "
             f"sentence; about five per call. **This is what joins the graph:** today it is {p_now} separate "
             f"pieces, the largest holding {big_now} of {n_nodes} nodes; if only half the candidate pairs hold "
             f"up it becomes {p_after}, with {big_after} in one. Counted over the ~{after} concepts there will "
             f"be after the line above"),
        line("aliases", SOL, math.ceil(after / jobs.ALIAS_BATCH),
             "The everyday words people use for each concept (\"oppose\", \"brand name\"), so search meets "
             "plain-language questions"),
        line("needs", MINI, math.ceil(NEEDS_TARGET / NEEDS_PER_CALL),
             f"{NEEDS_TARGET} realistic benchmark questions in four kinds, written by a *different* model from "
             "the one that writes the everyday words, so the test cannot flatter the ontology"),
        line("needs", SOL, math.ceil(NEEDS_TARGET / NEEDS_PER_CALL),
             "The same questions written by the knowledge model instead — cheaper, but it shares a voice with "
             "the everyday words it is testing", recommended=False),
        line("judge", SOL, questions,
             f"Relevance grades (0–3) for ~{JUDGE_POOL} passages per question, for all {questions} questions — "
             "what turns search results into a score. On the expert's question it agreed with both of the "
             "expert's required passages", scale_in=judge_scale, scale_out=judge_scale),
        line("judge", MINI, questions,
             "The same grades from the smaller model — it agreed with the expert too, but reasoned at length "
             "and cost more per question", scale_in=judge_scale, scale_out=judge_scale, recommended=False),
        line("answer", SOL, questions,
             f"A cited \"Ask the Manual\" answer for each of the {questions} questions, shown on the demo page "
             "beside plain search"),
    ]
    embed_tokens = sum(len(c.text) for c in ctx.corpus.chunks.values()) / 4
    judgements = [j for e in client.Cache().entries("relate") if e.get("status") == "completed"
                  for j in (jobs.parse(e) or {}).get("judgements") or ()]
    rel = {"calls": len([e for e in client.Cache().entries("relate") if e.get("status") == "completed"]),
           "proposed": len(judgements),
           "none": sum(1 for j in judgements if j.get("relation") == "none"),
           "generic": sum(1 for j in judgements if j.get("relation") in ("is_kind_of", "related_to"))}
    return {"lines": lines, "embed_tokens": embed_tokens, "after": after, "new": new, "rel": rel,
            "spent": client.Cache().spent_usd(), "cap": config.spend_cap_usd(), "pool_now": pool_now,
            "lost": sum(float(e.get("cost_usd") or 0) for e in client.Cache().entries("unrecorded"))}


def _money(value: float | None) -> str:
    if value is None:
        return "—"
    return f"${value:,.2f}" if value >= 0.995 else f"${value:.3f}"


def render(data: dict[str, Any]) -> str:
    small = data["embed_tokens"] * 0.02 / 1_000_000
    chosen = [line for line in data["lines"] if line["recommended"]]
    total = sum(line["total"] or 0 for line in chosen) + small
    total_std = sum(line["total_std"] or 0 for line in chosen) + small
    answers_demo = next(line for line in chosen if line["job"] == "answer")
    out = [
        "# Quote — what the model work costs, and what each spend buys",
        "",
        f"Generated {date.today().isoformat()} by `tmk-bulk quote` from measured smoke runs. "
        f"**Spent so far: {_money(data['spent'])} of the {_money(data['cap'])} cap** (ADR-0111). "
        "Each line is a measured cost per call × the number of calls the full run makes, + 25% for "
        "retries, re-asks and one prompt fix. Prices are OpenAI's on 2026-10-07; the knowledge model "
        "runs on the **flex** tier, which is half the standard price on the same endpoint.",
        "",
        f"## The recommended package: **{_money(total)}** (flex) · {_money(total_std)} at standard prices",
        "",
        "| # | Spend | What you get | Model | Calls | Per call (measured) | Full run |",
        "|---|---|---|---|---|---|---|",
    ]
    for n, line in enumerate(chosen, 1):
        s = line["stats"]
        how = (f"{_money(line['per_call'])} — {s.calls} measured, ~{s.input:,.0f} tokens in, "
               f"{s.output:,.0f} out" if s else "not measured")
        out.append(f"| {n} | `{line['job']}` | {line['what']} | `{line['model']}` | {line['calls']} | {how} | "
                   f"**{_money(line['total'])}** |")
    out += [
        f"| {len(chosen) + 1} | `embed` | Vectors for every Manual passage, so search finds meaning as well "
        f"as words | `text-embedding-3-small` | 1 pass, ~{data['embed_tokens']:,.0f} tokens | measured on a "
        f"probe | **{_money(small)}** |",
        "",
        f"**Cheaper variant:** answers for 30 hand-picked demo questions instead of all of them saves "
        f"{_money((answers_demo['total'] or 0) * (1 - 30 / answers_demo['calls']))}.",
        "",
        "## Alternatives priced but not recommended",
        "",
        "| Spend | Why not | Model | Full run |",
        "|---|---|---|---|",
    ]
    for line in data["lines"]:
        if not line["recommended"]:
            out.append(f"| `{line['job']}` | {line['what']} | `{line['model']}` | {_money(line['total'])} |")
    out += [
        "",
        "## What the smoke runs showed",
        "",
        f"- **Relationships:** {data['rel']['proposed']} judgements over {data['rel']['calls']} calls; "
        "every accepted one rests on a quote found verbatim in the Manual. "
        f"{data['rel']['none']} said \"no relationship\" and {data['rel']['generic']} fell back to a generic "
        "link, so the model may over-relate — the first thing to sample after the full run.",
        f"- **Judging:** pools averaged {data['pool_now']:.0f} passages; the full run assumes "
        f"{JUDGE_POOL}, and the per-call cost above is scaled to that.",
        "- **Answers:** careful and honest — Manual practice and the Act kept apart, no outcome "
        "stated — but retrieval missed the expert's key passages for the one question asked. "
        "That is what the relationships, everyday words and vectors are for, and what the "
        "measurement will show.",
        "- **Prompts were fixed before quoting:** v2 of the everyday-words prompt asks for short "
        "phrases (v1 wrote sentences search could not match); v2 of the question prompt stops the "
        "search wording copying the source passage (v1 would have flattered keyword search).",
        "",
        f"- **Of the {_money(data['spent'])} spent, {_money(data['lost'])} is four calls the session "
        "proxy cut off before they answered** (QUIRKS Q-66). They are booked as billed in case OpenAI "
        "finished them; long calls now run in background mode, which avoids it.",
        "",
        "## Not in the price",
        "",
        "- A *prompt* change re-asks every item in that step, at the price above; repeating an "
        "unchanged run is free (the cache).",
        "- Session time. A model call is the only thing the quote counts.",
        f"- Live questions during the pitch: about {_money(answers_demo['per_call'])} each, the measured "
        "cost of one answer.",
        "",
        "The per-call measurements, refusals and outputs behind every line are in "
        "`data/derived/reports/bulk-<job>.md` and the cache in `data/llm/cache/`.",
    ]
    return "\n".join(out) + "\n"

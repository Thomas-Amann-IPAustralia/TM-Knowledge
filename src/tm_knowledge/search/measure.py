"""The value measurement (D3): does the ontology make search better, and where?

Three systems (`search.index`) are run on every benchmark question. The top ten
of each are pooled and every pooled passage is graded 0–3 by the judge, so every
passage any system ranks in its top ten has a grade — nothing is scored as
irrelevant merely because nobody looked at it (KB SOP §6, "judged@k").

- **nDCG@10** (primary): the top ten, order counting, gain = grade.
- **Recall@10**: the share of the question's relevant passages (grade 2 or 3)
  in the top ten.
- **Paired bootstrap 95% intervals** over questions for each difference. If an
  interval includes zero, the difference is not established.

Reported overall and per kind of question, because an average hides where a
method helps (KB SOP §7.1). Nothing was tuned on these questions.

**A report names what it was scored on** (the review response, F11): the commit, and
a hash and count of the grade file and the rankings. The pooled grade file grows, so
the same rankings scored later give other absolute numbers; git already freezes
every input, and the stamp is the pointer to it. `write_report` never overwrites a
report scored on other inputs: it writes a dated one beside it.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
import subprocess
from pathlib import Path
from typing import Any

SYSTEMS = ("keyword", "hybrid", "ontology")
COMPARISONS = (("ontology", "hybrid"), ("ontology", "keyword"), ("hybrid", "keyword"))
K = 10
RESAMPLES = 10_000
SEED = 20261007


def ndcg(ranking: list[str], grades: dict[str, int], k: int = K) -> float:
    gains = [grades.get(ref, 0) for ref in ranking[:k]]
    dcg = sum(g / math.log2(i + 2) for i, g in enumerate(gains))
    ideal = sorted(grades.values(), reverse=True)[:k]
    idcg = sum(g / math.log2(i + 2) for i, g in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def recall(ranking: list[str], grades: dict[str, int], k: int = K) -> float | None:
    relevant = {ref for ref, g in grades.items() if g >= 2}
    if not relevant:
        return None
    return len(relevant & set(ranking[:k])) / len(relevant)


def bootstrap(differences: list[float], resamples: int = RESAMPLES, seed: int = SEED) -> tuple[float, float, float]:
    """Mean difference and a percentile 95% interval, paired over questions."""
    if not differences:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    n = len(differences)
    means = sorted(sum(differences[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    return sum(differences) / n, means[int(0.025 * resamples)], means[int(0.975 * resamples) - 1]


def score(pools: list[dict[str, Any]], judgements: dict[str, dict[str, int]],
          systems: tuple[str, ...] = SYSTEMS) -> dict[str, Any]:
    """Per-question metrics for every question that has both a pool and grades.

    A variant — another ranking scored on the same grades, such as the ontology system as
    last measured — is scored only on the questions it ranked; its comparison with the
    ontology system is paired over those questions alone."""
    rows = []
    variants: list[str] = []
    for q in pools:
        grades = judgements.get(q["key"])
        if grades is None:
            continue
        row = {"key": q["key"], "kind": q["kind"], "relevant": sum(1 for g in grades.values() if g >= 2)}
        for system in systems:
            ranking = q["systems"][system]
            row[f"ndcg:{system}"] = ndcg(ranking, grades)
            row[f"recall:{system}"] = recall(ranking, grades)
        for name, ranking in (q.get("variants") or {}).items():
            if name not in variants:
                variants.append(name)
            row[f"ndcg:{name}"] = ndcg(ranking, grades)
            row[f"recall:{name}"] = recall(ranking, grades)
        rows.append(row)
    return {"rows": rows, "variants": variants}


def summarise(rows: list[dict[str, Any]], variants: list[str] | tuple[str, ...] = (),
              systems: tuple[str, ...] = SYSTEMS,
              comparisons: tuple[tuple[str, str], ...] = COMPARISONS) -> dict[str, Any]:
    kinds = ["all"] + sorted({r["kind"] for r in rows})
    out: dict[str, Any] = {}
    for kind in kinds:
        subset = rows if kind == "all" else [r for r in rows if r["kind"] == kind]
        entry: dict[str, Any] = {"n": len(subset), "no_relevant": sum(1 for r in subset if r["relevant"] == 0)}
        for metric in ("ndcg", "recall"):
            for system in (*systems, *variants):
                values = [r[f"{metric}:{system}"] for r in subset if r.get(f"{metric}:{system}") is not None]
                entry[f"{metric}:{system}"] = sum(values) / len(values) if values else None
            for a, b in (*comparisons, *(("ontology", v) for v in variants)):
                pairs = [(r[f"{metric}:{a}"], r[f"{metric}:{b}"]) for r in subset
                         if r.get(f"{metric}:{a}") is not None and r.get(f"{metric}:{b}") is not None]
                entry[f"{metric}:{a}-{b}"] = bootstrap([x - y for x, y in pairs])
                entry[f"n:{metric}:{a}-{b}"] = len(pairs)
        out[kind] = entry
    return out


def by_evidence(pools: list[dict[str, Any]], required: dict[str, list[str]]) -> dict[str, Any]:
    """The systems scored on the expert's own evidence lists, with no model judge.

    A signed retrieval question names the passages an answer needs; scoring each system
    against those alone (1 if listed, else 0) is a yardstick no model touched. It is
    coarse — a passage the list leaves out counts as irrelevant — so it cross-checks the
    judged result rather than replacing it."""
    rows = []
    for q in pools:
        listed = [ref for ref in required.get(q["key"], ()) if ref]
        if not listed:
            continue
        grades = {ref: 1 for ref in listed}
        rankings = {**q["systems"], **(q.get("variants") or {})}
        rows.append({name: (ndcg(r, grades), recall(r, {ref: 2 for ref in listed})) for name, r in rankings.items()})
    names = list(dict.fromkeys([*SYSTEMS, *(rows[0] if rows else ())]))
    out: dict[str, Any] = {"n": len(rows)}
    for name in names:
        out[f"ndcg:{name}"] = sum(r[name][0] for r in rows) / len(rows) if rows else None
        out[f"recall:{name}"] = sum(r[name][1] for r in rows) / len(rows) if rows else None
    for a, b in (("ontology", "hybrid"), ("ontology", "keyword")):
        out[f"ndcg:{a}-{b}"] = bootstrap([r[a][0] - r[b][0] for r in rows])
    return out


def _cell(value: float | None) -> str:
    return "—" if value is None else f"{value:.3f}"


def _diff(triple: tuple[float, float, float]) -> str:
    mean, low, high = triple
    mark = " ✓" if low > 0 else (" ✗" if high < 0 else "")
    return f"{mean:+.3f} [{low:+.3f}, {high:+.3f}]{mark}"


def examples(rows: list[dict[str, Any]], questions: dict[str, str], n: int = 4) -> dict[str, list[dict]]:
    """The questions where the ontology changed nDCG@10 most, each way."""
    scored = sorted(rows, key=lambda r: r["ndcg:ontology"] - r["ndcg:hybrid"])
    pick = lambda rs: [{"key": r["key"], "kind": r["kind"], "question": questions.get(r["key"], ""),
                        "hybrid": r["ndcg:hybrid"], "ontology": r["ndcg:ontology"]} for rs_ in [rs] for r in rs_]
    return {"helped": pick(list(reversed(scored))[:n]), "hurt": pick(scored[:n])}


def render(summary: dict[str, Any], *, judged: int, pooled: int, judge_model: str,
           cases: dict[str, list[dict]] | None = None, variants: dict[str, str] | None = None,
           measured: str | None = None, evidence: dict[str, Any] | None = None) -> str:
    kinds = list(summary)
    lines = [
        "# The value measurement — does the ontology make search better?",
        "",
        (f"Rankings taken on {measured}. " if measured else "")
        + f"{summary['all']['n']} questions, every pooled passage graded 0–3 by `{judge_model}` "
        f"({judged} grades over {pooled} pools). Three systems, fixed before any passage was judged: "
        "**keyword** (BM25), **hybrid** (keyword + vectors — good search with no ontology) and "
        "**ontology** (hybrid + concept recognition, query expansion and concept-linked passages). "
        "Intervals are paired bootstrap 95%; ✓ means the difference is established, ✗ that it is "
        "established the other way.",
        "",
        "## nDCG@10 — the quality of the top ten",
        "",
        "| Questions | n | keyword | hybrid | ontology | ontology − hybrid | ontology − keyword |",
        "|---|---|---|---|---|---|---|",
    ]
    for kind in kinds:
        e = summary[kind]
        lines.append(f"| {kind} | {e['n']} | {_cell(e['ndcg:keyword'])} | {_cell(e['ndcg:hybrid'])} | "
                     f"{_cell(e['ndcg:ontology'])} | {_diff(e['ndcg:ontology-hybrid'])} | "
                     f"{_diff(e['ndcg:ontology-keyword'])} |")
    lines += ["", "## Recall@10 — the share of relevant passages found in the top ten", "",
              "| Questions | n | keyword | hybrid | ontology | ontology − hybrid | ontology − keyword |",
              "|---|---|---|---|---|---|---|"]
    for kind in kinds:
        e = summary[kind]
        lines.append(f"| {kind} | {e['n'] - e['no_relevant']} | {_cell(e['recall:keyword'])} | "
                     f"{_cell(e['recall:hybrid'])} | {_cell(e['recall:ontology'])} | "
                     f"{_diff(e['recall:ontology-hybrid'])} | {_diff(e['recall:ontology-keyword'])} |")
    lines += ["", "Recall counts only questions with at least one relevant passage in the pool. "
                  "`signed` is the expert's ten retrieval questions, run as a cross-check — they "
                  "were not written for this benchmark and are not in it."]
    if variants:
        lines += ["", "## What changed — the ontology system against other rankings, on the same grades", "",
                  "Each row scores another ranking of the same questions against the same grades, so the "
                  "difference is the change in the system, not in the judge or the pool.", "",
                  "| Ranking | n | nDCG@10 then | now | now − then | Recall@10 now − then |", "|---|---|---|---|---|---|"]
        for name, note in variants.items():
            e = summary["all"]
            lines.append(f"| `{name}` — {note} | {e.get(f'n:ndcg:ontology-{name}', 0)} | {_cell(e.get(f'ndcg:{name}'))} | "
                         f"{_cell(e['ndcg:ontology'])} | {_diff(e[f'ndcg:ontology-{name}'])} | "
                         f"{_diff(e[f'recall:ontology-{name}'])} |")
        for name in variants:
            lines += ["", f"By kind of question, `{name}`:", "", "| Questions | n | then | now | now − then |",
                      "|---|---|---|---|---|"]
            for kind in kinds:
                e = summary[kind]
                lines.append(f"| {kind} | {e.get(f'n:ndcg:ontology-{name}', 0)} | {_cell(e.get(f'ndcg:{name}'))} | "
                             f"{_cell(e['ndcg:ontology'])} | {_diff(e[f'ndcg:ontology-{name}'])} |")
    if evidence and evidence.get("n"):
        lines += ["", "## Cross-check with no model judge — the expert's own evidence lists", "",
                  f"The {evidence['n']} signed retrieval questions, each system scored against only the passages "
                  "the expert listed as required (listed = relevant, anything else = not). No model graded "
                  "anything here; it is coarse, and ten questions are few.", "",
                  "| System | nDCG@10 | Recall@10 |", "|---|---|---|"]
        for name in [k.split(":", 1)[1] for k in evidence if k.startswith("ndcg:") and "-" not in k]:
            lines.append(f"| {name} | {_cell(evidence[f'ndcg:{name}'])} | {_cell(evidence[f'recall:{name}'])} |")
        lines += ["", f"ontology − hybrid {_diff(evidence['ndcg:ontology-hybrid'])}; ontology − keyword "
                      f"{_diff(evidence['ndcg:ontology-keyword'])} (nDCG@10)."]
    if cases:
        for title, key in (("Where the ontology helped most", "helped"), ("Where it hurt most", "hurt")):
            lines += ["", f"## {title}", "", "| Question | Kind | hybrid | ontology |", "|---|---|---|---|"]
            lines += [f"| {c['question']} | {c['kind']} | {c['hybrid']:.3f} | {c['ontology']:.3f} |"
                      for c in cases[key]]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# The live reading (ADR-0132, ADR-0133)
# ---------------------------------------------------------------------------

#: The page's own configuration, which has no vectors: plain keyword search, the
#: ontology system starting from names alone, and the same starting also from the
#: ideas the live model read in the question.
READING_SYSTEMS = ("keyword", "names", "reading")
READING_COMPARISONS = (("reading", "names"), ("names", "keyword"), ("reading", "keyword"))


def render_reading(summary: dict[str, Any], touched: dict[str, Any], *, coverage: dict[str, Any],
                   judged: int, judge_model: str, reading: dict[str, Any], measured: str | None,
                   ungraded: list[tuple[str, str]] = ()) -> str:
    """The reading's measurement: does starting from the ideas a model read help?"""
    kinds = list(summary)
    lines = [
        "# The live reading — does a model's reading of the question make search better?",
        "",
        (f"Rankings taken on {measured}. " if measured else "")
        + f"{summary['all']['n']} benchmark questions, each read once by `{reading['model']}` "
        f"(prompt `{reading['prompt_version']}`, effort {reading['effort']}), the picks checked as the page "
        f"checks them. Every passage any of the three systems ranks in its top ten is graded 0–3 by "
        f"`{judge_model}` ({judged} grades). The systems are the page's own, with no vectors: **keyword** (BM25), "
        "**names** (the ontology system starting from ideas named in the question) and **reading** (the same, "
        "starting also from the ideas the model read). Intervals are paired bootstrap 95%; ✓ means the "
        "difference is established, ✗ that it is established the other way."
        + (f" **{len(ungraded)} pooled passages have no grade** ({', '.join(sorted({k for k, _ in ungraded}))}) and "
           "score 0: the judge's answer for them was refused because it also graded passages not in its pool."
           if ungraded else ""),
        "",
        "## What the reading found",
        "",
        "| Questions | n | a specific idea by name | the reading added an idea | of those, none by name | "
        "ideas added | set aside |",
        "|---|---|---|---|---|---|---|",
    ]
    for kind in kinds:
        c = coverage[kind]
        lines.append(f"| {kind} | {c['n']} | {c['named']} | {c['touched']} | {c['only_read']} | {c['added']} | "
                     f"{c['set_aside']} |")
    for title, metric, count in (("nDCG@10 — the quality of the top ten", "ndcg", "n"),
                                 ("Recall@10 — the share of relevant passages found in the top ten", "recall", None)):
        lines += ["", f"## {title}", "",
                  "| Questions | n | keyword | names | reading | reading − names | names − keyword | reading − keyword |",
                  "|---|---|---|---|---|---|---|---|"]
        for kind in kinds:
            e = summary[kind]
            n = e["n"] if count else e["n"] - e["no_relevant"]
            lines.append(f"| {kind} | {n} | {_cell(e[f'{metric}:keyword'])} | {_cell(e[f'{metric}:names'])} | "
                         f"{_cell(e[f'{metric}:reading'])} | {_diff(e[f'{metric}:reading-names'])} | "
                         f"{_diff(e[f'{metric}:names-keyword'])} | {_diff(e[f'{metric}:reading-keyword'])} |")
    if touched.get("all", {}).get("n"):
        e = touched["all"]
        lines += ["", "## Only the questions the reading changed", "",
                  "On a question where the reading added no idea, *reading* and *names* rank the same passages, "
                  "so the difference is zero there by construction. Here are the questions where it added one.", "",
                  "| n | names | reading | reading − names (nDCG@10) | reading − names (Recall@10) |", "|---|---|---|---|---|",
                  f"| {e['n']} | {_cell(e['ndcg:names'])} | {_cell(e['ndcg:reading'])} | "
                  f"{_diff(e['ndcg:reading-names'])} | {_diff(e['recall:reading-names'])} |"]
    lines += ["", "## What this does not show", "",
              "- The page's search has no meaning-vectors; the measured system (`measure.md`) has. These numbers "
              "are for the page's configuration and are not comparable with that report's.",
              "- The benchmark questions were written beside the ontology and often use its names, so the "
              "reading has less to add here than on a question typed the way a person asks.",
              "- The grades are a model's, and the questions are model-written. `signed` is the expert's ten "
              "retrieval questions, run as a cross-check.",
              "- Each question was read once; a second reading could pick differently."]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ what a report was scored on

_STAMP = re.compile(
    r"<!-- scored-on: commit=(?P<commit>\S+) grades=(?P<grades>sha256:[0-9a-f]{64}) "
    r"grade-count=(?P<grade_count>\d+) rankings=(?P<rankings>sha256:[0-9a-f]{64}) -->"
)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(grades: Path, rankings: Path) -> dict[str, Any]:
    """The commit the working tree is at, and a hash and count of the two inputs.

    A commit with the inputs uncommitted is marked `+uncommitted`: checking it out
    would not reproduce the report.
    """
    import yaml

    root = Path(__file__).resolve().parents[3]

    def git(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                                  check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return ""

    commit = git("rev-parse", "--short=12", "HEAD") or "unknown"
    if git("status", "--porcelain", "--", str(grades), str(rankings)):
        commit += "+uncommitted"
    rows = (yaml.safe_load(grades.read_text(encoding="utf-8")) or {}).get("judgements", [])
    return {"commit": commit, "grades": _sha256(grades),
            "grade_count": sum(len(r.get("grades") or {}) for r in rows), "rankings": _sha256(rankings)}


def stamp(text: str, named: dict[str, Any], command: str = "tmk-bulk measure") -> str:
    """The report with its inputs under the title: a comment to read back, a line to read."""
    title, _, rest = text.partition("\n")
    comment = (f"<!-- scored-on: commit={named['commit']} grades={named['grades']} "
               f"grade-count={named['grade_count']} rankings={named['rankings']} -->")
    line = (f"*Scored at commit `{named['commit']}` on {named['grade_count']} grades "
            f"(`{named['grades'][:19]}…`) and rankings `{named['rankings'][:19]}…`. To reproduce: "
            f"`git checkout {named['commit'].split('+')[0]}`, then `{command}`.*")
    return f"{title}\n{comment}\n\n{line}\n{rest}"


def read_inputs(path: Path) -> dict[str, Any] | None:
    """What a written report says it was scored on, or None if it does not say."""
    if not path.exists():
        return None
    match = _STAMP.search(path.read_text(encoding="utf-8"))
    if match is None:
        return None
    named = match.groupdict()
    named["grade_count"] = int(named["grade_count"])
    return named


def write_report(path: Path, text: str, named: dict[str, Any], *, today: str) -> Path:
    """Write `text` to `path`, unless `path` holds a report scored on other inputs.

    Then the published report stands, and this one is written beside it, dated,
    saying which report it does not replace. A report that names no inputs counts as
    scored on other ones: nothing shows it is not. Returns where it was written.
    """
    old = read_inputs(path)
    same = (old is not None and old["grades"] == named["grades"]
            and old["rankings"] == named["rankings"])
    if not path.exists() or same:
        path.write_text(text, encoding="utf-8")
        return path
    dated = path.with_name(f"{path.stem}-{today}{path.suffix}")
    held = read_inputs(dated)
    if dated.exists() and (held is None or (held["grades"], held["rankings"]) != (named["grades"], named["rankings"])):
        raise SystemExit(f"{dated.name} already holds a report on other inputs; nothing written")
    before = (f"scored on {old['grade_count']} grades (`{old['grades'][:19]}…`) at commit `{old['commit']}`"
              if old else "which does not name the grades it was scored on")
    title, _, rest = text.partition("\n")
    note = (f"\n*This report does not replace `{path.name}`, {before}; that report stands as "
            "written. Different grades move the absolute numbers, not the method.*\n")
    dated.write_text(f"{title}\n{rest.rstrip()}\n{note}", encoding="utf-8")
    return dated

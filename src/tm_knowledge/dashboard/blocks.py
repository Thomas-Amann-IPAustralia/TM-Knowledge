"""The block vocabulary the site renders.

A page is `{id, title, lede, blocks: [...]}` and every block is one of ten
kinds. `site/blocks.js` has one renderer per kind and knows nothing else about
the repo, which is the whole point: **changing what the dashboard says is a
change to this file and to `build.py`, never to the JavaScript.** Adding an
eleventh kind is the only thing that needs both.

Two of the ten are different in a way worth naming. `network` and `tree` carry a
derived arrangement rather than a restatement — the rules that produced them are
in `views.py` and the browser applies none of its own. They still hold no text
the records do not, and `site/network.js` and `site/tree.js` know as little
about trade marks as `blocks.js` does.

Cell and text values are markdown-lite (`**bold**`, `` `code` ``, `[a](b)`) and
may carry `{{glossary term}}` markers, which the browser turns into a tooltip
from `site/data/glossary.json`. A marker naming a term the glossary does not
hold is a build error, not a silently plain word — see `build.check_glossary`.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

__all__ = [
    "TONES",
    "stats",
    "prose",
    "callout",
    "table",
    "cards",
    "bars",
    "listing",
    "report",
    "chips",
    "network",
    "tree",
]

#: The tones a badge, stat or callout may carry. Tone is meaning, not colour:
#: `gap` is "known to be missing", `warn` is "true and uncomfortable", `note` is
#: neutral. The stylesheet decides what each one looks like.
TONES = frozenset({"good", "note", "warn", "gap", "muted"})


def _tone(value: str | None) -> str | None:
    if value is None:
        return None
    if value not in TONES:
        raise ValueError(f"unknown tone {value!r}; expected one of {sorted(TONES)}")
    return value


def stats(items: Sequence[dict[str, Any]], *, note: str | None = None) -> dict[str, Any]:
    """A grid of headline numbers. Each item: label, value, note, tone."""
    return {
        "kind": "stats",
        "items": [
            {
                "label": item["label"],
                "value": item["value"],
                "note": item.get("note"),
                "tone": _tone(item.get("tone")),
                "href": item.get("href"),
            }
            for item in items
        ],
        "note": note,
    }


def prose(text: str) -> dict[str, Any]:
    """Markdown-lite paragraphs. Blank lines separate them."""
    return {"kind": "prose", "text": text.strip()}


def callout(tone: str, title: str, text: str, *, links: Sequence[dict] = ()) -> dict[str, Any]:
    return {
        "kind": "callout",
        "tone": _tone(tone),
        "title": title,
        "text": text.strip(),
        "links": list(links),
    }


def table(
    columns: Sequence[tuple[str, str]],
    rows: Iterable[dict[str, Any]],
    *,
    search: bool = False,
    note: str | None = None,
    empty: str = "Nothing here yet.",
) -> dict[str, Any]:
    """A table. `columns` is (key, label); a row may carry `detail` blocks.

    `search: true` puts a filter box above it, which is what makes the 52
    concepts and the 61 decisions explorable rather than a wall.
    """
    return {
        "kind": "table",
        "columns": [{"key": key, "label": label} for key, label in columns],
        "rows": list(rows),
        "search": search,
        "note": note,
        "empty": empty,
    }


def cards(items: Sequence[dict[str, Any]], *, note: str | None = None) -> dict[str, Any]:
    return {"kind": "cards", "items": list(items), "note": note}


def bars(items: Sequence[dict[str, Any]], *, note: str | None = None) -> dict[str, Any]:
    """A horizontal distribution. Each item: label, value, note, tone."""
    return {"kind": "bars", "items": list(items), "note": note}


def listing(items: Sequence[str], *, ordered: bool = False, note: str | None = None) -> dict[str, Any]:
    return {"kind": "list", "items": list(items), "ordered": ordered, "note": note}


def report(path: str, title: str, *, lede: str | None = None) -> dict[str, Any]:
    """A generated Markdown report, fetched and rendered in place.

    The site does not restate a report it can render. `data/derived/reports/` is
    produced by `tmk-coverage`, `tmk-blockers` and `tmk-ontology-report`, and
    copying its conclusions into JSON would create a second version that goes
    stale on its own schedule.
    """
    return {"kind": "report", "path": path, "title": title, "lede": lede}


def network(payload: dict[str, Any], *, note: str | None = None) -> dict[str, Any]:
    """The node network. `payload` is `views.network()` — nodes, edges, legend.

    The block carries the whole graph rather than a path to it, so the page is
    one fetch and the picture cannot disagree with the counts printed beside it.
    """
    return {"kind": "network", "data": payload, "note": note}


def tree(payload: dict[str, Any], *, note: str | None = None) -> dict[str, Any]:
    """The decision tree. `payload` is `views.decision_tree()` — spines, rules,
    and one `records` map the nodes point into."""
    return {"kind": "tree", "data": payload, "note": note}


def chips(values: Iterable[str], *, tone: str | None = None) -> dict[str, Any]:
    """A cell holding several small labels — alt labels, tags, ids."""
    return {"chips": [{"label": value, "tone": _tone(tone)} for value in values]}

"""The structured tests a question reaches (the second review response, A06 step 2).

A question about section 44 should bring its conditions and both exceptions with it, not
only whichever passages rank highest. A test record already names its provision and the
ground it is the test for, so the lookup is a rule, not a ranking: a test is reached when
the question names its provision ("section 44", "s 44(3)", by `citations.named_provisions`)
or when the ground it tests is among the concepts recognised in the question.

What a reached test brings is its reading with no matter (`explain.engine.requirements`'s
condition tree and exceptions, each with its source and the kind of its effect), shown on
the Ask page in a card of its own, stamped as machine-written. It is not sent to the
answer prompt: what the live chatbot is given is the owner's to change (ADR-0139,
CLAUDE.md §3a). `site/js/engine.js` (`structuredTests`) is the same rule, and a test holds
the two equal on every benchmark question.
"""

from __future__ import annotations

from typing import Any, Iterable

from tm_knowledge.search.citations import named_provisions

__all__ = ["payload", "find"]


def payload(tests: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Every sound test as the browser holds it, in id order: what the lookup reads (the
    provision and the ground) and what the card shows."""
    from tm_knowledge.explain import engine

    out = []
    for test_id, test in sorted(tests.items()):
        view = engine.requirements(test)
        out.append({
            "id": test_id, "title": test["title"], "provision": test["provision"], "ground": test.get("ground"),
            "effect": view["effect"]["reads"], "condition": view["condition"],
            "exceptions": [{"text": x["text"], "ref": x["ref"], "kind": x["effect"]["kind"],
                            "effect": x["effect"]["reads"], "condition": x["condition"]} for x in view["exceptions"]],
            "review_status": "unreviewed",
        })
    return out


def find(question: str, recognised: Iterable[str], tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The tests `question` reaches, in the order `tests` holds them, each with why:
    `named` (the question names its provision) and/or `ground` (its ground is recognised)."""
    named = named_provisions(question, {t["provision"] for t in tests})
    ids = set(recognised)
    out = []
    for test in tests:
        why = [w for w, hit in (("named", test["provision"] in named), ("ground", test.get("ground") in ids)) if hit]
        if why:
            out.append({"id": test["id"], "why": why})
    return out

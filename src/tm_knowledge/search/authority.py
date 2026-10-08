"""PU-0004 at answer time: a Manual statement presented as what the Act requires.

The ontology review found that the graph's two practice-versus-law guards fire only
on test fixtures, and that live answers — model text — are never checked for the
error the signed prohibited use PU-0004 names: attributing to the legislation a
requirement only the Manual states (review F1). The owner approved checking it at
answer time on 2026-10-08 (ADR-0121).

The check is deterministic and deliberately narrow. A sentence of the answer is
flagged when it says the legislation requires, provides, states or prescribes
something — "the Act requires", "section 43 provides", "regulation 4.4 states" —
and the answer cites no provision of that legislation (or of that section, where
the sentence names one). A sentence that names the Manual is attributing the
point to the Manual, which is the right attribution, and a negated one ("the
passages do not include section 57 or state…") says the opposite; neither is
flagged. The Manual quotes the Act in places, so an answer can
appear to cite the Act while having read only the Manual (CQ-0001's caveat); the
flag says so, and nothing is removed. `site/js/engine.js` (`authorityFlags`) runs
the same check on live answers.
"""

from __future__ import annotations

import re
from typing import Iterable

__all__ = ["conflations", "MESSAGE"]

MESSAGE = (
    "Says the legislation requires this, but the answer cites no provision for it — only "
    "the Manual, which states practice and does not bind the Registrar's discretion "
    "(PU-0004). Check the provision itself."
)

_VERB = r"(?:requires?|provides?|states?|says|prescribes?|mandates?|obliges?|imposes?)"
_WHOLE = re.compile(r"\bthe (?P<what>Act|Regulations|legislation)\b[^.;:]{0,40}?\b" + _VERB + r"\b", re.I)
_PART = re.compile(
    r"\b(?P<kind>section|s|subsection|regulation|reg|r)\.?\s?(?P<number>\d+[A-Z]{0,2}(?:\.\d+[A-Z]{0,2})?)"
    r"(?:\([0-9a-z]+\))*[^.;:]{0,40}?\b" + _VERB + r"\b",
    re.I,
)
#: A sentence ends at . ! or ? followed by space and a capital or a quote — not at
#: the point inside "regulation 4.4" — or at a line break.
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'“‘(])|\n+")
_MANUAL = re.compile(r"\bManual\b")
_NEGATION = re.compile(r"\b(?:not|no|never|neither|nor)\b|n['’]t\b", re.I)


def _supported(match: re.Match[str], cited: list[str]) -> bool:
    groups = match.groupdict()
    if groups.get("number"):
        regulation = groups["kind"].lower() in ("regulation", "reg", "r")
        prefix = f"TMR1995/r{groups['number']}" if regulation else f"TMA1995/s{groups['number']}"
        return any(ref == prefix or ref.startswith((prefix + "(", prefix + "/")) for ref in cited)
    what = groups.get("what", "").lower()
    if what == "act":
        return any(ref.startswith("TMA1995/") for ref in cited)
    if what == "regulations":
        return any(ref.startswith("TMR1995/") for ref in cited)
    return any(ref.startswith(("TMA1995/", "TMR1995/")) for ref in cited)


def conflations(answer: str, cited: Iterable[str]) -> list[dict[str, str]]:
    """The answer's sentences that attribute a requirement to legislation it does not cite."""
    refs = [str(ref) for ref in cited]
    flags = []
    for sentence in _SENTENCE_BREAK.split(answer or ""):
        sentence = sentence.strip()
        if not sentence or _MANUAL.search(sentence):
            continue
        for pattern in (_PART, _WHOLE):
            match = pattern.search(sentence)
            if match and not _NEGATION.search(sentence[:match.end()]) and not _supported(match, refs):
                flags.append({"sentence": sentence, "message": MESSAGE})
                break
    return flags

"""Exact-reference lookup: the provisions a question names (A07).

"What does section 44(3) say?" names a provision outright, and until A07 it reached
the answer only if a concept rested on it or one of the top three passages cited it.
This finds every "section 44", "s 44(3)", "subsection 41(4)", "regulation 4.10" or
"reg 4.8" in the text and returns the provision it names, at the provision level (a
subsection resolves to its section, whose blocks `jobs.excerpt` then gives whole or
in part), in order of first mention, and only where the snapshot holds it. No guess:
a number the snapshot does not hold, or one with no word saying which instrument
("44(3)" alone), is not looked up, and an "s" after an apostrophe ("it's 3") is
not a section. `site/js/engine.js` (`namedProvisions`) is the
same rule, and a test holds the two equal.
"""

from __future__ import annotations

import re
from typing import Container

__all__ = ["named_provisions"]

_CITATION = re.compile(
    r"(?<![\w'’])(?P<kind>sections?|subsections?|ss?|regulations?|subregulations?|regs?|r)\.?\s?"
    r"(?P<number>\d+[A-Za-z]{0,2}(?:\.\d+[A-Za-z]{0,2})?)(?![\w.]*\d)",
    re.I,
)
_REGULATION = ("regulation", "regulations", "subregulation", "subregulations", "reg", "regs", "r")


def named_provisions(text: str, held: Container[str]) -> list[str]:
    """The provisions `text` names, as held refs, first mention first."""
    out: list[str] = []
    for match in _CITATION.finditer(text or ""):
        kind = match["kind"].lower()
        code = "TMR1995/r" if kind in _REGULATION else "TMA1995/s"
        ref = code + match["number"].upper()
        if ref in held and ref not in out:
            out.append(ref)
    return out

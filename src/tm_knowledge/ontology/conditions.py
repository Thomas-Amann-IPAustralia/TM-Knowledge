"""What a relationship's applicability is known to be: its condition state, and the
proceeding and kind of mark its source fixes (the second review response, R07).

Only 26 of 337 machine-written relationships carried `applies_when`, and an absent
condition could mean "the sentence states none" or "nobody looked": the two read the
same. The state separates them, and **it is set by rule wherever a machine can**:

- `stated` — the record carries the sentence's condition (`applies_when`);
- `none_stated` — the sentence holds no conditional marker ("if", "where", "unless",
  "when", "except"): a fact about the sentence, not a legal judgement;
- `assessed_none` — it holds one, and the record says why that marker does not
  condition this relationship (`no_condition`, a reader's judgement, stamped);
- `not_assessed` — it holds one and nobody has said either way.

The proceeding and the kind of mark are read off the source's Part with a lookup,
never written on each record: Part 48 is non-use removal, Part 35 certification marks.
A Part covering several proceedings, or none in particular, fixes neither, and the
field stays absent: absent means "not fixed by its Part", not "applies to all".
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["MARKER", "STATES", "PROCEEDING_BY_PART", "MARK_TYPE_BY_PART", "state", "proceeding", "mark_type"]

#: A conditional marker in a supporting sentence. Crude by design: it over-reports, and
#: every over-report becomes a record somebody assessed, never a condition invented.
MARKER = re.compile(r"\b(if|where|unless|when|except)\b", re.IGNORECASE)

STATES = ("stated", "none_stated", "assessed_none", "not_assessed")

#: Manual Part -> the proceeding its practice is about, where the Part fixes one.
PROCEEDING_BY_PART: dict[str, str] = {
    **{part: "application_and_examination" for part in (
        "Part2", "Part5", "Part6", "Part10", "Part11", "Part12", "Part13", "Part14", "Part16", "Part17",
        "Part18", "Part20", "Part21", "Part22", "Part23", "Part24", "Part26", "Part27", "Part28", "Part29",
        "Part30", "Part31", "Part32A", "Part32B")},
    "Part38": "revocation_of_acceptance",
    "Part39": "registration",
    "Part40": "renewal",
    "Part41": "cancellation",
    "Part42": "rectification",
    "Part43": "assignment_and_transmission",
    "Part44": "claim_of_interest",
    "Part46": "opposition_to_registration",
    "Part47": "opposition_to_registration",
    "Part48": "removal_for_non_use",
    "Part49": "removal_for_non_use",
    "Part60": "international_registration",
    "Part62": "revocation_of_registration",
}

#: Manual Part -> the kind of trade mark it is about, where the Part fixes one. Every
#: other Part is about trade marks generally, which no field states.
MARK_TYPE_BY_PART: dict[str, str] = {
    "Part33": "collective",
    "Part34": "defensive",
    "Part35": "certification",
}


def _part(ref: Any) -> str | None:
    parts = str(ref or "").split("/")
    return parts[1] if len(parts) > 1 and parts[0] == "TMM" else None


def state(record: dict[str, Any]) -> str:
    """The record's condition state, by the rule above."""
    if record.get("applies_when"):
        return "stated"
    if not MARKER.search(str(record.get("supporting_text") or "")):
        return "none_stated"
    if record.get("no_condition"):
        return "assessed_none"
    return "not_assessed"


def proceeding(record: dict[str, Any]) -> str | None:
    return PROCEEDING_BY_PART.get(_part(record.get("source_ref")) or "")


def mark_type(record: dict[str, Any]) -> str | None:
    return MARK_TYPE_BY_PART.get(_part(record.get("source_ref")) or "")

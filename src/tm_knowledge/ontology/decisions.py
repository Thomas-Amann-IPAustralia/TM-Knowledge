"""What kind of decision a cited case is — read off the case id, never guessed.

The ontology review found the Manual's 108 ATMO decisions — hearing officers, the
Registrar acting through a delegate — typed `tmk:JudicialDecision` on the same
footing as the High Court and the Full Federal Court (review C7). An answer citing
"[2009] ATMO 68" then presents the office's own earlier view as if a court had
held it. The owner approved separating them on 2026-10-08: "An administrative
decision is different to a judicial decision" (ADR-0121).

Upstream's case id is `CASE/<year>/<series>/<number>[/<page>]`, and the series —
a medium-neutral citation (`ATMO`, `FCAFC`) or a law report (`CLR`, `RPC`) — says
who decided, where it says anything. This table reads it and nothing else:

- **administrative** — the Registrar's delegate (ATMO, and the Official Journal's
  reports of them, AOJP) or the Commissioner of Patents' (APO).
- **judicial** — a court: the series is a court's own citation or a report series
  that reports only courts.
- **unclassified** — a report series that reports courts and registry decisions
  alike (IPR, RPC, FSR, AIPC) or one the table does not know. Reading the case
  would settle it; no decision text exists in the programme (Q-11), so the table
  refuses to choose rather than guess (CLAUDE.md rule 6).

A court's level is recorded where the series fixes it; "further distinction of
judicial power may be required" (the owner, C7) and this is where it would go.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["DecisionKind", "SERIES", "classify"]


@dataclass(frozen=True)
class DecisionKind:
    kind: str  # "administrative" | "judicial" | "unclassified"
    jurisdiction: str | None  # "AU", "UK", or None where the series does not say
    level: str | None  # who decided, where the series fixes it
    series: str


#: series -> (kind, jurisdiction, level). Deterministic: a lookup on the id.
SERIES: dict[str, tuple[str, str | None, str | None]] = {
    "ATMO": ("administrative", "AU", "the Registrar's delegate (Australian Trade Marks Office)"),
    "AOJP": ("administrative", "AU", "the Registrar's delegate (reported in the Official Journal)"),
    "APO": ("administrative", "AU", "the Commissioner of Patents' delegate (Australian Patent Office)"),
    "HCA": ("judicial", "AU", "High Court of Australia"),
    "CLR": ("judicial", "AU", "High Court of Australia (Commonwealth Law Reports)"),
    "FCAFC": ("judicial", "AU", "Full Court of the Federal Court of Australia"),
    "FCA": ("judicial", "AU", "Federal Court of Australia"),
    "FCR": ("judicial", "AU", "Federal Court of Australia (Federal Court Reports)"),
    "ALR": ("judicial", "AU", None),
    "FLR": ("judicial", "AU", None),
    "VLR": ("judicial", "AU", "Supreme Court of Victoria (Victorian Law Reports)"),
    "AC": ("judicial", "UK", "House of Lords or Privy Council (Appeal Cases)"),
    "EWHC": ("judicial", "UK", "High Court of England and Wales"),
    "IPR": ("unclassified", "AU", None),
    "AIPC": ("unclassified", "AU", None),
    "LGERA": ("unclassified", "AU", None),
    "RPC": ("unclassified", "UK", None),
    "FSR": ("unclassified", "UK", None),
}


def classify(case_id: str) -> DecisionKind:
    """The kind of decision `CASE/<year>/<series>/...` is, by its series alone."""
    parts = case_id.split("/")
    series = parts[2] if len(parts) > 2 and parts[0] == "CASE" else ""
    kind, jurisdiction, level = SERIES.get(series, ("unclassified", None, None))
    return DecisionKind(kind=kind, jurisdiction=jurisdiction, level=level, series=series)

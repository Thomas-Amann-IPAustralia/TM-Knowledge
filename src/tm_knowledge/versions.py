"""Which text of the law was in force on a date: the versioning model (A03), defined now.

The second review response's A03 asked for four things to be defined before anything
depends on them, and this module and `ontology/draft/time.ttl` are where they are:

1. **Identity apart from text.** An instrument (`TMA1995`, the Register's title id
   `C2004A04969`) and a provision (`TMA1995/s44`) are enduring; a *compilation* is one
   versioned text of the instrument (`C2026C00421`, compilation 48). A provision's text
   and content hash in the graph are its text in one compilation (`tmk:textFrom`).
2. **Legal effect apart from capture.** A compilation is in force from its start date
   until the next one starts; upstream's capture date is when it was read, and says
   only that the Register then showed it in force. Neither stands in for the other.
3. **Scoped statements.** A definition may be scoped (`authored.definitions`, one per
   concept per scope); every record read from the Act was read against the compilation
   its evidence hashes belong to, and goes stale when the pin moves (Q-95).
4. **An explicit unknown.** Where the date that matters is not given, the answer is
   `no_date`, never the held text by default; a date after the capture is
   `after_capture`, never assumed to fall in the held text.

**Selection needs a second version to be held, and none is.** The snapshot holds one
compilation per instrument (the pin, `data/pin.json`). Historical compilations would
have to be captured upstream (CLAUDE.md rule 2), so `select` is written over a list and
tested on two invented compilations; over the real snapshot it can say only that a date
falls in the held compilation, before it, or after the capture.

Which date governs a question (the filing date, the priority date, the date of a
decision, a transitional provision's own date) is a legal judgement, and this module
never makes it: the caller names the date and says what it is.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

__all__ = ["Compilation", "Selection", "STATES", "held", "select", "for_dates"]

#: The states a selection can be in, as `time.ttl` names them (`tmk:VersionState`).
STATES = ("held", "not_held", "after_capture", "unconfirmed", "no_date")

_NOUN = {"TMA1995": "the Act", "TMR1995": "the Regulations"}


def _day(value: date) -> str:
    return f"{value.day} {value:%B %Y}"


@dataclass(frozen=True)
class Compilation:
    """One versioned text of an instrument."""

    instrument: str
    number: str
    register_id: str
    in_force_from: date
    captured: date
    title_id: str | None = None
    status_at_capture: str | None = None
    unincorporated: bool | None = None

    @property
    def line(self) -> str:
        """"the Act as in force from 19 September 2026 (compilation 48, C2026C00421)"."""
        return (f"{_NOUN.get(self.instrument, self.instrument)} as in force from {_day(self.in_force_from)} "
                f"(compilation {self.number}, {self.register_id})")

    def row(self) -> dict[str, Any]:
        return {"instrument": self.instrument, "compilation": self.number, "register_id": self.register_id,
                "title_id": self.title_id, "in_force_from": self.in_force_from.isoformat(),
                "captured": self.captured.isoformat(), "status_at_capture": self.status_at_capture,
                "unincorporated_amendments": self.unincorporated}


@dataclass(frozen=True)
class Selection:
    instrument: str
    on: date | None
    #: what the date is (the filing date, the date of the report), as the caller says
    what: str
    state: str
    compilation: Compilation | None
    reads: str

    def row(self) -> dict[str, Any]:
        return {"instrument": self.instrument, "on": self.on.isoformat() if self.on else None, "what": self.what,
                "state": self.state, "compilation": self.compilation.row() if self.compilation else None,
                "reads": self.reads}


def _instruments(corpus: Any) -> dict[str, Any]:
    if corpus is not None:
        return dict(getattr(corpus, "instruments", {}))
    # Without a loaded corpus, the instrument records alone: an explanation needs to say
    # which text it read without loading 2,460 chunks. No snapshot, nothing held.
    import json

    from tm_knowledge.config import UPSTREAM_DIR
    from tm_knowledge.upstream.records import Instrument

    found = sorted((UPSTREAM_DIR / "snapshot" / "legislation").glob("*/instrument.json"))
    records = (Instrument.from_dict(json.loads(path.read_text(encoding="utf-8"))) for path in found)
    return {record.code: record for record in records}


def held(corpus: Any = None) -> dict[str, list[Compilation]]:
    """Every compilation the snapshot holds, by instrument, oldest first. One each today."""
    out: dict[str, list[Compilation]] = {}
    for code, instrument in sorted(_instruments(corpus).items()):
        out.setdefault(code, []).append(Compilation(
            instrument=code, number=instrument.compilation_number, register_id=instrument.register_id,
            in_force_from=date.fromisoformat(instrument.compilation_start),
            captured=date.fromisoformat(instrument.captured_at[:10]), title_id=instrument.title_id,
            status_at_capture=instrument.status, unincorporated=instrument.has_unincorporated_amendments))
    return {code: sorted(found, key=lambda c: c.in_force_from) for code, found in out.items()}


def select(compilations: Iterable[Compilation], on: date | str | None, what: str = "the date") -> Selection:
    """The compilation in force `on` a date, from those held, or why it cannot be said.

    A compilation is in force from its start until the next held one starts. The latest
    is known to be in force only up to the day it was captured, and only if the Register
    then showed it in force with no amendments left unincorporated (`unconfirmed`
    otherwise); after that day a later compilation may have started, so the answer is
    `after_capture`, not the held text. Before the earliest held start, the text in force is one the snapshot does not
    hold: `not_held`. No date: `no_date`."""
    ordered = sorted(compilations, key=lambda c: c.in_force_from)
    if not ordered:
        raise ValueError("no compilation held")
    instrument = ordered[0].instrument
    noun = _NOUN.get(instrument, instrument)
    if isinstance(on, str):
        on = date.fromisoformat(on)
    if on is None:
        return Selection(instrument, None, what, "no_date", None,
                         f"Which text of {noun} applies depends on {what}, which is not given. The text held is "
                         f"{ordered[-1].line}; it is not assumed to be the one that applies.")
    if on < ordered[0].in_force_from:
        return Selection(instrument, on, what, "not_held", None,
                         f"On {what} ({_day(on)}) the text of {noun} in force was an earlier one than any held "
                         f"here, which is {ordered[0].line} at the earliest.")
    for current, following in zip(ordered, ordered[1:]):
        if current.in_force_from <= on < following.in_force_from:
            return Selection(instrument, on, what, "held", current,
                             f"On {what} ({_day(on)}) the text in force was {current.line}, which is held.")
    last = ordered[-1]
    confirmed = last.status_at_capture == "InForce" and last.unincorporated is False
    if on <= last.captured and confirmed:
        return Selection(instrument, on, what, "held", last,
                         f"On {what} ({_day(on)}) the text in force was {last.line}, which is held.")
    if on <= last.captured:
        return Selection(instrument, on, what, "unconfirmed", last,
                         f"On {what} ({_day(on)}) the held text was {last.line}, but the Register's record of it "
                         f"does not confirm it was complete and in force when captured.")
    return Selection(instrument, on, what, "after_capture", last,
                     f"{what[0].upper()}{what[1:]} ({_day(on)}) is after this text was captured ({_day(last.captured)}). "
                     f"The text held is {last.line}; whether a later one was in force by then is not known here.")


def for_dates(compilations: dict[str, list[Compilation]], dates: dict[str, str | None],
              instruments: Iterable[str] | None = None) -> list[Selection]:
    """A selection for each named date and each instrument, in that order. `dates` maps
    what the date is ("the filing date") to the date or `None`."""
    chosen = [code for code in (instruments or sorted(compilations)) if code in compilations]
    return [select(compilations[code], on, what) for what, on in dates.items() for code in chosen]

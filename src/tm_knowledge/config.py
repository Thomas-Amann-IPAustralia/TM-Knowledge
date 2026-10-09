"""Project configuration constants.

The base IRI lives here and nowhere else (`docs/IDENTIFIERS.md` §2, HANDOFF Q7).
It is deliberately overridable from the environment so that changing it is a
configuration change and a graph rebuild, never a find-and-replace across
serialised RDF.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Proposed production base. **Unconfirmed** — HANDOFF Q7 is an organisational
#: decision, not a technical one. Nothing outside `refs.py` may read this.
DEFAULT_BASE_IRI = "https://data.ipaustralia.gov.au/tmk/"

#: Repository root, derived from this file's location.
REPO_ROOT = Path(__file__).resolve().parents[2]

#: Where the pinned upstream snapshot is fetched to (ADR-0004). Git-ignored.
UPSTREAM_DIR = REPO_ROOT / "data" / "upstream"

#: The tracked pin manifest (ADR-0004, ADR-0021).
PIN_PATH = REPO_ROOT / "data" / "pin.json"

#: The model that does the bulk knowledge work (ADR-0111, superseding ADR-0087).
#: It lives here and nowhere else, for the same reason the base IRI does: the string
#: ends up stamped on every record the model touches, so changing it is a
#: configuration change and a re-measurement rather than a find-and-replace.
#:
#: What goes in `authored_by` is the model id **the API reports** in its response,
#: never this constant (ADR-0094) — a silently substituted model is provenance
#: corruption nothing can undo. Changing it is a superseding ADR.
DEFAULT_AUTHORING_MODEL = "gpt-6.1-sol"

#: Reasoning effort for the bulk work — the owner's "medium effort" (ADR-0111).
DEFAULT_AUTHORING_EFFORT = "medium"

#: The API endpoint, pinned here so an ambient environment variable cannot
#: redirect calls somewhere else (KB SOP §9).
OPENAI_BASE_URL = "https://api.openai.com/v1"

#: The environment variable holding the credential. In a session container the
#: egress proxy supplies the real key whatever this holds (Q-65), so a placeholder
#: is enough; in any other environment the real key goes here. The value appears
#: nowhere in this repository, in any generated artefact, or in any log line.
AUTHORING_API_KEY_VAR = "OPENAI_API_KEY"

#: Hard cap on total recorded spend across every paid call, in US dollars. First
#: the owner's "a maximum of $1" for the smoke runs (ADR-0111); then the quote was
#: approved — "Approved, go with your recommendations and run it all" — so the
#: cap is the $0.18 already spent plus the $6.41 package (ADR-0114). Then the D5
#: quote: "I'm allowing the expenditure of an additional $2.89 on top of the
#: remaining $3.11, totalling in $6" — so $6.60 + $2.89, and D5 may spend at most
#: the $6.00 above the $3.49 recorded before it (ADR-0125). Raising it again is the
#: owner's decision, made on a quote — overridable for one run by
#: `TMK_SPEND_CAP_USD`, and only on the owner's word.
SPEND_CAP_USD = 9.49

#: US dollars per million tokens, from OpenAI's pricing page on 2026-10-07
#: (ADR-0111). `flex` and `batch` are half of `default`. Reasoning tokens bill as
#: output. The spend ledger computes cost from these and the usage each response
#: reports; a model missing here cannot be called, because its spend could not be
#: counted against the cap.
PRICES_PER_MTOK: dict[str, dict[str, dict[str, float]]] = {
    "gpt-6.1-sol": {
        "default": {"input": 2.00, "cached_input": 0.10, "cache_write": 2.50, "output": 10.00},
        "flex": {"input": 1.00, "cached_input": 0.05, "cache_write": 1.25, "output": 5.00},
        "batch": {"input": 1.00, "cached_input": 0.05, "cache_write": 1.25, "output": 5.00},
    },
    "gpt-5.4-mini": {
        "default": {"input": 0.75, "cached_input": 0.075, "output": 4.50},
        "batch": {"input": 0.375, "cached_input": 0.0375, "output": 2.25},
    },
    "text-embedding-3-small": {"default": {"input": 0.02, "cached_input": 0.02, "output": 0.0}},
    "text-embedding-3-large": {"default": {"input": 0.13, "cached_input": 0.13, "output": 0.0}},
}


def authoring_model() -> str:
    """Return the configured authoring model, overridable for a one-off run.

    Anything that overrides it still stamps what the API reports on every record
    it writes — `authored_by` is written at authoring time from the response,
    never defaulted from this constant (ADR-0079 guard 1, ADR-0094).
    """
    return os.environ.get("TMK_AUTHORING_MODEL", DEFAULT_AUTHORING_MODEL)


def spend_cap_usd() -> float:
    """The spend cap in force for this run (ADR-0111)."""
    return float(os.environ.get("TMK_SPEND_CAP_USD", SPEND_CAP_USD))


def authoring_api_key() -> str:
    """The API credential, or a placeholder the session proxy replaces (Q-65).

    Never raises in a session container: the proxy injects the real key over
    whatever is sent. Outside one, an absent key fails at the API with a 401 —
    loudly, which is the failure mode wanted, never an empty result set.
    """
    return os.environ.get(AUTHORING_API_KEY_VAR, "").strip() or "proxy-supplied"


def base_iri() -> str:
    """Return the configured base IRI, always with a trailing slash."""
    base = os.environ.get("TMK_BASE_IRI", DEFAULT_BASE_IRI)
    return base if base.endswith("/") else base + "/"

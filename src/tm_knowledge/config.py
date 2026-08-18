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


def base_iri() -> str:
    """Return the configured base IRI, always with a trailing slash."""
    base = os.environ.get("TMK_BASE_IRI", DEFAULT_BASE_IRI)
    return base if base.endswith("/") else base + "/"

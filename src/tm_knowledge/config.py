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

#: The model that authors legal content and backs Stage 2-4 extraction (ADR-0087,
#: answering HANDOFF Q3). It lives here and nowhere else, for the same reason the
#: base IRI does: the string ends up stamped on every record the model touches, so
#: changing it must be a configuration change and a re-measurement rather than a
#: find-and-replace.
#:
#: **Confirm this against Google's current model list before the first real call.**
#: A wrong identifier fails loudly at the API, which is the safe failure. The unsafe
#: one is a silently substituted model: an id recorded on ten thousand records that
#: is not the model that wrote them is provenance corruption nothing can undo.
#:
#: Changing it is a superseding ADR (ADR-0087 consequence 3). Output from a
#: different model is different output, and every baseline measured before the
#: change is invalid after it.
DEFAULT_AUTHORING_MODEL = "gemini-3.8-flash"

#: The environment variable holding the API credential. The value is a repository
#: secret and appears nowhere in this repository, in any generated artefact, or in
#: any log line. A repository secret reaches GitHub Actions and **not** a local
#: container, so a session doing model-backed work outside CI must supply it
#: itself — and an absent key must raise, never return an empty result set
#: (ADR-0087 consequence 2).
AUTHORING_API_KEY_VAR = "GEMINI_API_KEY"


def authoring_model() -> str:
    """Return the configured authoring model, overridable for a one-off run.

    Anything that overrides it still has to stamp what it actually used on every
    record it writes — the envelope's `authored_by` is not defaulted from this
    constant at read time, it is written at authoring time (ADR-0079 guard 1).
    """
    return os.environ.get("TMK_AUTHORING_MODEL", DEFAULT_AUTHORING_MODEL)


def authoring_api_key() -> str:
    """The API credential, or raise saying exactly what is missing.

    Never returns an empty string: a model-backed run that quietly produces
    nothing because a key was absent looks identical to one that found nothing,
    and the second is a finding while the first is a broken pipeline.
    """
    key = os.environ.get(AUTHORING_API_KEY_VAR, "").strip()
    if not key:
        raise RuntimeError(
            f"{AUTHORING_API_KEY_VAR} is not set. It is a repository secret, so it "
            f"reaches GitHub Actions but not a local container — export it for a "
            f"local run. Refusing to continue rather than returning no results "
            f"(ADR-0087)."
        )
    return key


def base_iri() -> str:
    """Return the configured base IRI, always with a trailing slash."""
    base = os.environ.get("TMK_BASE_IRI", DEFAULT_BASE_IRI)
    return base if base.endswith("/") else base + "/"

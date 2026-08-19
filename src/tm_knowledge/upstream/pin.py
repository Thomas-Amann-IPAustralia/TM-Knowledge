"""The pin: which upstream snapshot this working copy is entitled to read.

`data/pin.json` is tracked and states the pin. `data/upstream/` is not tracked
and holds whatever a fetch actually put there. This module is the thing that
refuses to let the two drift apart (ADR-0004, confirmed by ADR-0021).

Three checks, in increasing strength:

1. **The receipt** — `data/upstream/.fetch.json`, written by the fetcher. Says
   which commit was fetched and when. Cheap, and the only one that would catch
   a snapshot fetched from the wrong commit.
2. **The counts** — the pinned corpus counts against the fetched manifests.
   Catches a truncated or half-copied fetch.
3. **The tree digest** — sha256 over the pinned paths. Catches a hand edit,
   which `data/README.md` prohibits and nothing else would notice.

A snapshot that fails any of them is not read. Corpus counts quoted anywhere in
this repo are only meaningful next to a pin, which is the whole point.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from tm_knowledge.config import PIN_PATH, UPSTREAM_DIR

#: Name of the fetch receipt, written inside the fetched directory.
RECEIPT_NAME = ".fetch.json"

_SHA = re.compile(r"^[0-9a-f]{40}$")


class UnpinnedSnapshot(RuntimeError):
    """The pin is missing, empty, or malformed. Nothing may be read."""


class SnapshotMismatch(RuntimeError):
    """What is on disk is not what the pin names."""


@dataclass(frozen=True, slots=True)
class Pin:
    """The tracked pin. Everything here is a property of the *pinned release*,
    never of a particular fetch — a fetch-time field in a tracked file makes the
    file churn on every run and tells you nothing about what was pinned."""

    repo: str
    clone_url: str
    commit: str
    manual_extractor_version: str
    legislation_extractor_version: str
    paths: tuple[str, ...]
    corpus: dict[str, int] = field(default_factory=dict)
    tree_sha256: str | None = None
    note: str | None = None

    @classmethod
    def load(cls, path: Path | None = None) -> "Pin":
        path = path or PIN_PATH
        if not path.exists():
            raise UnpinnedSnapshot(
                f"no pin at {path}. The snapshot is fetched, never assumed "
                "(ADR-0004) — see data/README.md."
            )
        data = json.loads(path.read_text(encoding="utf-8"))
        commit = str(data.get("commit", ""))
        if not _SHA.match(commit):
            raise UnpinnedSnapshot(
                f"{path} names commit {commit!r}, which is not a 40-character sha. "
                "An unpinned snapshot is not reproducible and is refused."
            )
        return cls(
            repo=data["repo"],
            clone_url=data["clone_url"],
            commit=commit,
            manual_extractor_version=data["manual_extractor_version"],
            legislation_extractor_version=data["legislation_extractor_version"],
            paths=tuple(data["paths"]),
            corpus=dict(data.get("corpus", {})),
            tree_sha256=data.get("tree_sha256"),
            note=data.get("note"),
        )

    def to_json(self) -> str:
        payload = {
            "repo": self.repo,
            "clone_url": self.clone_url,
            "commit": self.commit,
            "manual_extractor_version": self.manual_extractor_version,
            "legislation_extractor_version": self.legislation_extractor_version,
            "paths": list(self.paths),
            "corpus": self.corpus,
            "tree_sha256": self.tree_sha256,
        }
        if self.note:
            payload["note"] = self.note
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def tree_digest(root: Path, paths: tuple[str, ...]) -> str:
    """A deterministic digest over the pinned paths.

    Files in sorted relative-path order; each contributes its path and the
    sha256 of its bytes. Ordering is fixed rather than filesystem-dependent, so
    the digest is a fact about the content and reproduces on any machine.
    """
    outer = hashlib.sha256()
    for relative in paths:
        base = root / relative
        if not base.exists():
            raise SnapshotMismatch(f"pinned path missing from the snapshot: {relative}")
        for file in sorted(p for p in base.rglob("*") if p.is_file()):
            inner = hashlib.sha256()
            with file.open("rb") as handle:
                for block in iter(lambda: handle.read(1 << 20), b""):
                    inner.update(block)
            outer.update(file.relative_to(root).as_posix().encode("utf-8"))
            outer.update(b"\0")
            outer.update(inner.hexdigest().encode("ascii"))
            outer.update(b"\n")
    return outer.hexdigest()


def measure_corpus(root: Path) -> dict[str, int]:
    """Count the fetched corpus, in the terms `docs/UPSTREAM.md` §2 uses.

    Deliberately shallow: it reads the two manifests and counts files. It is a
    check that the fetch is complete, not a second implementation of the loader
    — and it must stay cheap enough to run before every session's first read.
    """
    manual = json.loads((root / "snapshot" / "manifest.json").read_text(encoding="utf-8"))
    legislation = json.loads(
        (root / "snapshot" / "legislation" / "manifest.json").read_text(encoding="utf-8")
    )
    return {
        "pages": int(manual["corpus"]["pages"]),
        "parts": int(manual["corpus"]["parts"]),
        "chunks": int(manual["corpus"]["chunks"]),
        "links": int(manual["corpus"]["links"]),
        "instruments": int(legislation["corpus"]["instruments"]),
        "provisions": int(legislation["corpus"]["provisions"]),
        "units": int(legislation["corpus"]["units"]),
        "page_files": sum(1 for _ in (root / "snapshot" / "pages").rglob("*.json")),
        "provision_files": sum(
            1 for _ in (root / "snapshot" / "legislation").rglob("provisions/*/*.json")
        ),
    }


def read_receipt(root: Path | None = None) -> dict:
    root = root or UPSTREAM_DIR
    path = root / RECEIPT_NAME
    if not path.exists():
        raise SnapshotMismatch(
            f"no fetch receipt at {path}. Either nothing has been fetched, or "
            "something other than the fetcher wrote data/upstream/. Run "
            "`tmk-fetch-upstream`."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def write_receipt(root: Path, pin: Pin, *, digest: str, counts: dict[str, int]) -> None:
    payload = {
        "commit": pin.commit,
        "repo": pin.repo,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "paths": list(pin.paths),
        "tree_sha256": digest,
        "corpus": counts,
    }
    (root / RECEIPT_NAME).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def verify(root: Path | None = None, pin: Pin | None = None, *, deep: bool = True) -> dict:
    """Verify the fetched snapshot against the pin. Raises, or returns the receipt.

    `deep=False` skips the tree digest, which reads every pinned byte. The
    default is on: a hand edit is exactly the failure this is here to catch, and
    `data/README.md` calls it an invisible fork of the corpus.
    """
    pin = pin or Pin.load()
    root = root or UPSTREAM_DIR
    if not root.exists():
        raise SnapshotMismatch(
            f"no snapshot at {root}. Run `tmk-fetch-upstream` — nothing in this "
            "repo works from a bare clone until it has (ADR-0004)."
        )

    receipt = read_receipt(root)
    if receipt.get("commit") != pin.commit:
        raise SnapshotMismatch(
            f"snapshot is at {receipt.get('commit')!r}, the pin names "
            f"{pin.commit!r}. Re-fetch, or bump the pin deliberately and say "
            "what moved (data/README.md)."
        )

    counts = measure_corpus(root)
    for key, expected in pin.corpus.items():
        if counts.get(key) != expected:
            raise SnapshotMismatch(
                f"corpus count {key} is {counts.get(key)}, the pin says {expected}. "
                "The fetch is incomplete or the pin is wrong."
            )

    if deep and pin.tree_sha256:
        digest = tree_digest(root, pin.paths)
        if digest != pin.tree_sha256:
            raise SnapshotMismatch(
                f"tree digest is {digest}, the pin says {pin.tree_sha256}. "
                "Something has edited data/upstream/. It is read-only "
                "(ADR-0002); delete it and re-fetch."
            )
    return receipt

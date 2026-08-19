"""Fetch the pinned upstream snapshot into `data/upstream/`.

Scripted, not documented as manual steps — ADR-0004's own consequence clause,
and the reason is Q-14: agent containers are ephemeral, so any manual step is
skipped or done differently each time. A bare clone plus

    tmk-fetch-upstream

must produce a working `data/upstream/`.

**Upstream publishes no releases and no tags** (checked 2026-08-18: zero of
either). "Pinned release" is therefore realised as a **pinned commit**, fetched
by sha, which is what ADR-0004 actually records in the manifest anyway. See
Q-19. Fetching by sha rather than cloning a branch is the load-bearing part: a
branch moves and would silently re-point the corpus under a repo whose whole
provenance story rests on knowing which text an assertion was made against.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tm_knowledge.config import PIN_PATH, UPSTREAM_DIR
from tm_knowledge.upstream.pin import (
    Pin,
    SnapshotMismatch,
    UnpinnedSnapshot,
    measure_corpus,
    tree_digest,
    verify,
    write_receipt,
)


def _git(*args: str, cwd: Path | None = None) -> str:
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({result.returncode}):\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def fetch(pin: Pin, dest: Path, *, force: bool = False) -> Path:
    """Fetch the pinned commit and copy the pinned paths into `dest`."""
    if dest.exists() and not force:
        raise SnapshotMismatch(
            f"{dest} already exists. Verify it with `--verify`, or pass `--force` "
            "to discard and re-fetch."
        )

    with tempfile.TemporaryDirectory(prefix="tmk-upstream-", dir=str(dest.parent)) as tmp:
        work = Path(tmp)
        _git("init", "--quiet", str(work))
        _git("remote", "add", "origin", pin.clone_url, cwd=work)
        # Fetch the pinned object itself. Depth 1: this repo consumes the
        # snapshot, never its history. Anything point-in-time needs a full
        # clone of upstream and is a different job (Q-05, Q-14).
        _git("fetch", "--quiet", "--depth", "1", "origin", pin.commit, cwd=work)
        _git("checkout", "--quiet", "--detach", "FETCH_HEAD", cwd=work)

        head = _git("rev-parse", "HEAD", cwd=work)
        if head != pin.commit:
            raise SnapshotMismatch(
                f"fetched {head}, the pin names {pin.commit}. Refusing to use it."
            )

        staging = dest.with_name(dest.name + ".incoming")
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        for relative in pin.paths:
            source = work / relative
            if not source.exists():
                raise SnapshotMismatch(
                    f"pinned path {relative!r} is not in {pin.repo} at {pin.commit}."
                )
            shutil.copytree(source, staging / relative)

    digest = tree_digest(staging, pin.paths)
    if pin.tree_sha256 and digest != pin.tree_sha256:
        shutil.rmtree(staging)
        raise SnapshotMismatch(
            f"fetched tree digest {digest} does not match the pinned "
            f"{pin.tree_sha256}. The pin and the remote disagree about what that "
            "commit contains; do not proceed."
        )

    counts = measure_corpus(staging)
    for key, expected in pin.corpus.items():
        if counts.get(key) != expected:
            shutil.rmtree(staging)
            raise SnapshotMismatch(
                f"fetched corpus count {key} is {counts.get(key)}, the pin says "
                f"{expected}. Refusing to install an unexpected corpus."
            )

    write_receipt(staging, pin, digest=digest, counts=counts)
    if dest.exists():
        shutil.rmtree(dest)
    staging.rename(dest)
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-fetch-upstream",
        description="Fetch and verify the pinned manual-XtrACTor snapshot.",
    )
    parser.add_argument("--pin", type=Path, default=PIN_PATH, help="path to pin.json")
    parser.add_argument("--dest", type=Path, default=UPSTREAM_DIR, help="where to install")
    parser.add_argument(
        "--verify", action="store_true", help="verify what is on disk; no network"
    )
    parser.add_argument(
        "--shallow-verify",
        action="store_true",
        help="skip the tree digest, which reads every pinned byte",
    )
    parser.add_argument(
        "--force", action="store_true", help="discard an existing snapshot and re-fetch"
    )
    parser.add_argument(
        "--write-digest",
        action="store_true",
        help=(
            "record the fetched tree digest into the pin. A deliberate act: use it "
            "when first pinning a commit, and commit the result on its own."
        ),
    )
    args = parser.parse_args(argv)

    try:
        pin = Pin.load(args.pin)
    except UnpinnedSnapshot as error:
        print(f"refusing to run: {error}", file=sys.stderr)
        return 2

    try:
        if args.verify:
            receipt = verify(args.dest, pin, deep=not args.shallow_verify)
            print(
                f"ok: {pin.repo} @ {pin.commit[:12]} "
                f"({pin.manual_extractor_version}, {pin.legislation_extractor_version}) "
                f"fetched {receipt.get('fetched_at')}"
            )
            return 0

        fetch(pin, args.dest, force=args.force)
    except (SnapshotMismatch, RuntimeError) as error:
        print(f"refusing to proceed: {error}", file=sys.stderr)
        return 1

    if args.write_digest:
        digest = tree_digest(args.dest, pin.paths)
        updated = Pin(
            repo=pin.repo,
            clone_url=pin.clone_url,
            commit=pin.commit,
            manual_extractor_version=pin.manual_extractor_version,
            legislation_extractor_version=pin.legislation_extractor_version,
            paths=pin.paths,
            corpus=measure_corpus(args.dest),
            tree_sha256=digest,
            note=pin.note,
        )
        args.pin.write_text(updated.to_json(), encoding="utf-8")
        print(f"wrote tree digest {digest[:16]}… into {args.pin}")

    print(f"fetched {pin.repo} @ {pin.commit[:12]} into {args.dest}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

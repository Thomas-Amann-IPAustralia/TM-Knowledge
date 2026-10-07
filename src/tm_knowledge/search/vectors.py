"""Vectors for every Manual passage and every benchmark question.

Stored as float16 matrices with a JSON index beside each, in
`data/derived/search/`, and committed. 512 dimensions of
`text-embedding-3-small` keeps the passage matrix near 2.5 MB; the full 1,536
would be three times that for retrieval quality a pitch cannot tell apart.

A vector is reused while its passage's `content_hash` is unchanged and the model
and size match, so a second run calls the API only for what changed. The ledger
records each call (`bulk.client.embed`); this module is what persists the vectors.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np

from tm_knowledge.bulk import client
from tm_knowledge.config import REPO_ROOT
from tm_knowledge.upstream.loader import Corpus

SEARCH_DIR = REPO_ROOT / "data" / "derived" / "search"
MODEL = "text-embedding-3-small"
DIMENSIONS = 512
BATCH = 96


def _text_key(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


class Store:
    """One matrix and its index: `<name>.npy` and `<name>.json`."""

    def __init__(self, name: str, root: Path | None = None) -> None:
        root = root or SEARCH_DIR
        self.npy, self.index_path = root / f"{name}.npy", root / f"{name}.json"
        self.keys: list[str] = []
        self.hashes: list[str] = []
        self.matrix = np.zeros((0, DIMENSIONS), dtype=np.float32)
        if self.npy.exists() and self.index_path.exists():
            index = json.loads(self.index_path.read_text(encoding="utf-8"))
            if index.get("model") == MODEL and index.get("dimensions") == DIMENSIONS:
                self.keys, self.hashes = index["keys"], index["hashes"]
                self.matrix = np.load(self.npy).astype(np.float32)

    def lookup(self) -> dict[str, tuple[int, str]]:
        return {key: (i, h) for i, (key, h) in enumerate(zip(self.keys, self.hashes))}

    def save(self) -> None:
        self.npy.parent.mkdir(parents=True, exist_ok=True)
        np.save(self.npy, self.matrix.astype(np.float16))
        self.index_path.write_text(json.dumps(
            {"model": MODEL, "dimensions": DIMENSIONS, "keys": self.keys, "hashes": self.hashes},
            ensure_ascii=False, indent=0) + "\n", encoding="utf-8")


def passage_text(chunk) -> str:
    """The breadcrumb leads the embedding input, never the stored text (KB SOP §4.5)."""
    return " > ".join(chunk.heading_path) + "\n" + chunk.text


def _fill(store: Store, wanted: list[tuple[str, str, str]], job: str, *, confirm: bool, dry_run: bool) -> float:
    """Embed every (key, hash, text) the store does not already hold. Returns the estimate."""
    have = store.lookup()
    missing = [(k, h, t) for k, h, t in wanted if have.get(k, (None, None))[1] != h]
    estimate = 0.0
    keys, hashes, rows = list(store.keys), list(store.hashes), [store.matrix]
    position = {k: i for i, k in enumerate(keys)}
    for start in range(0, len(missing), BATCH):
        batch = missing[start:start + BATCH]
        entry, vectors, est = client.embed(job=job, texts=[t for _, _, t in batch], model=MODEL,
                                           dimensions=DIMENSIONS, confirm=confirm, dry_run=dry_run)
        estimate += est.worst_case_usd
        if dry_run:
            continue
        block = np.asarray(vectors, dtype=np.float32)
        block /= np.linalg.norm(block, axis=1, keepdims=True)
        for (key, digest, _), vector in zip(batch, block):
            if key in position:
                rows[0][position[key]] = vector
                hashes[position[key]] = digest
            else:
                position[key] = len(keys)
                keys.append(key)
                hashes.append(digest)
                rows.append(vector[None, :])
    if not dry_run and missing:
        store.keys, store.hashes, store.matrix = keys, hashes, np.vstack(rows)
        store.save()
    return estimate


def embed_passages(corpus: Corpus, *, confirm: bool = False, dry_run: bool = False) -> tuple[int, float]:
    store = Store("passages")
    wanted = [(c.chunk_ref, c.content_hash, passage_text(c))
              for c in sorted(corpus.chunks.values(), key=lambda c: c.chunk_ref)]
    estimate = _fill(store, wanted, "embed", confirm=confirm, dry_run=dry_run)
    return len(wanted), estimate


def embed_queries(texts: Iterable[str], *, confirm: bool = False, dry_run: bool = False) -> tuple[int, float]:
    store = Store("queries")
    wanted = [(_text_key(t), _text_key(t), t) for t in dict.fromkeys(texts)]
    estimate = _fill(store, wanted, "embed-query", confirm=confirm, dry_run=dry_run)
    return len(wanted), estimate


class Dense:
    """Cosine search over the passage matrix, by a query vector from the query store."""

    def __init__(self) -> None:
        self.passages = Store("passages")
        self.queries = Store("queries")
        self._q = self.queries.lookup()

    @property
    def ready(self) -> bool:
        return len(self.passages.keys) > 0

    def query_vector(self, text: str) -> np.ndarray | None:
        found = self._q.get(_text_key(text))
        return None if found is None else self.queries.matrix[found[0]]

    def search(self, text: str, k: int = 50) -> list[tuple[str, float]]:
        vector = self.query_vector(text)
        if vector is None or not self.ready:
            return []
        scores = self.passages.matrix @ vector
        top = np.argsort(-scores)[:k]
        return [(self.passages.keys[i], float(scores[i])) for i in top]

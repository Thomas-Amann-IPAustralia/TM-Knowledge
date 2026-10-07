"""One door to the paid model: cached, priced, capped, and refusing to guess.

Every call goes through `respond()` (or `embed()`), and four things happen in a
fixed order that the KB SOP learned the expensive way:

1. **The cache is checked first.** A response is keyed by everything that shapes
   it — model, effort, prompt version, schema, instructions, input — and stored in
   `data/llm/cache/`, which is committed. Asking again is free.
2. **A dry run stops there**, with an estimate and no spend.
3. **The cap is checked before the call**, against the worst case: the estimated
   input plus `max_output_tokens`, at the tier's prices. Spend already recorded is
   the sum of every cache entry's cost, so the ledger cannot drift from the cache.
4. **The response is cached whatever happens to it next** — including a reply
   that later fails validation, because it was paid for.

The transport is a parameter so tests can pass a stub. The command line never
does: a stub's output reaching the cache would poison it (KB SOP §10).
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from tm_knowledge import config

CACHE_DIR = config.REPO_ROOT / "data" / "llm" / "cache"

#: (path, body) -> parsed JSON response. Replaced only in tests.
Transport = Callable[[str, dict[str, Any]], dict[str, Any]]


#: Worst-case cost of calls in flight, so parallel workers cannot each pass the
#: cap check and pass the cap together.
_LOCK = threading.Lock()
_RESERVED = [0.0]

#: A flex request can come back `failed` because the discounted capacity is busy.
#: That costs nothing and is retried, after these waits in seconds.
RETRY_WAITS = (20, 45, 90, 180, 300)
RETRYABLE = frozenset({"server_is_overloaded", "rate_limit_exceeded", "resource_unavailable"})


def _reserve(cache: "Cache", worst: float, what: str) -> None:
    with _LOCK:
        spent, cap = cache.spent_usd(), config.spend_cap_usd()
        if spent + _RESERVED[0] + worst > cap:
            raise BudgetExceeded(
                f"{what}: recorded spend ${spent:.4f} + in flight ${_RESERVED[0]:.4f} + worst case "
                f"${worst:.4f} would pass the ${cap:.2f} cap (ADR-0111, ADR-0114). Nothing was sent."
            )
        _RESERVED[0] += worst


def _release(worst: float) -> None:
    with _LOCK:
        _RESERVED[0] = max(0.0, _RESERVED[0] - worst)


class BudgetExceeded(RuntimeError):
    """The call could take recorded spend past the cap. Nothing was sent."""


class NotConfirmed(RuntimeError):
    """A paid call was asked for without `--confirm`. Nothing was sent."""


class UnpricedModel(RuntimeError):
    """A model with no price cannot be counted against the cap, so it is not called."""


@dataclass(frozen=True)
class Estimate:
    """What a call would cost, before it is made."""

    input_tokens: int
    max_output_tokens: int
    worst_case_usd: float


def _prices(model: str, tier: str) -> dict[str, float]:
    base = model
    if base not in config.PRICES_PER_MTOK:
        # A dated snapshot id ("gpt-6.1-sol-2026-09-30") prices as its family.
        base = next((m for m in config.PRICES_PER_MTOK if model.startswith(m + "-")), model)
    table = config.PRICES_PER_MTOK.get(base)
    if table is None:
        raise UnpricedModel(f"no price for {model!r} in config.PRICES_PER_MTOK")
    return table.get(tier) or table["default"]


def cost_usd(model: str, tier: str, usage: dict[str, Any]) -> float:
    """Price one response from the usage it reported. Reasoning bills as output."""
    prices = _prices(model, tier)
    input_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
    details = usage.get("input_tokens_details") or {}
    cached = int(details.get("cached_tokens") or 0)
    written = int(details.get("cache_write_tokens") or 0)
    output_tokens = int(usage.get("output_tokens") or 0)
    return (
        (input_tokens - cached - written) * prices["input"]
        + cached * prices["cached_input"]
        + written * prices.get("cache_write", prices["input"])
        + output_tokens * prices["output"]
    ) / 1_000_000


def estimate_tokens(text: str) -> int:
    """A deliberately high estimate: ~3.5 characters a token for English legal text."""
    return int(len(text) / 3.5) + 1


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def cache_key(body: dict[str, Any], prompt_version: str) -> str:
    """Everything that shapes the answer, and nothing that only changes its price."""
    shaping = {k: v for k, v in body.items() if k not in ("service_tier", "store", "background")}
    return hashlib.sha256((prompt_version + "\n" + _canonical(shaping)).encode()).hexdigest()


class Cache:
    """`data/llm/cache/<job>/<prompt version>/<key>.json` — committed, never pruned."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or CACHE_DIR

    def _path(self, job: str, prompt_version: str, key: str) -> Path:
        return self.root / job / prompt_version / f"{key}.json"

    def get(self, job: str, prompt_version: str, key: str) -> dict[str, Any] | None:
        path = self._path(job, prompt_version, key)
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def put(self, entry: dict[str, Any]) -> Path:
        path = self._path(entry["job"], entry["prompt_version"], entry["key"])
        if entry.get("status") == "failed":
            # Kept as a record, but never under the key: a failure must not be
            # replayed as if it were the answer. A later call retries.
            n = len(list(path.parent.glob(f"{entry['key']}.failed-*.json"))) + 1 if path.parent.exists() else 1
            path = path.with_name(f"{entry['key']}.failed-{n}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(entry, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
        tmp.replace(path)  # atomic (KB SOP §4.1)
        return path

    def entries(self, job: str | None = None) -> list[dict[str, Any]]:
        if not self.root.exists():
            return []
        pattern = f"{job}/*/*.json" if job else "*/*/*.json"
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.root.glob(pattern))]

    def spent_usd(self) -> float:
        """Recorded spend: the sum of every cached call's cost, across every job."""
        return round(sum(float(e.get("cost_usd") or 0) for e in self.entries()), 6)


def _http(method: str, path: str, body: dict[str, Any] | None = None, *, attempts: int = 3) -> dict[str, Any]:
    """One request to the pinned base URL. The session proxy supplies the key (Q-65)."""
    request = urllib.request.Request(
        config.OPENAI_BASE_URL + path,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + config.authoring_api_key()},
        method=method,
    )
    delay = 5.0
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:500]
            if error.code in (429, 500, 502, 503, 504) and attempt < attempts - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"{method} {path} returned HTTP {error.code}: {detail}") from error
    raise RuntimeError(f"{method} {path}: retries exhausted")


def _urllib_transport(path: str, body: dict[str, Any]) -> dict[str, Any]:
    """Submit in background mode and poll, so no single request outlives the proxy.

    A long reasoning call held open as one request is cut at about 30 seconds by
    the session's egress proxy (Q-66) — and a cut request may still be billed.
    In background mode the submit returns at once and each poll is a short GET.
    The response is stored by OpenAI for retrieval, which background mode
    requires; it holds only published corpus text (ADR-0088).
    """
    if path != "/responses":
        return _http("POST", path, body)
    created = _http("POST", path, {**body, "background": True, "store": True}, attempts=1)
    deadline = time.time() + 1800
    wait = 2.0
    while created.get("status") in ("queued", "in_progress"):
        if time.time() > deadline:
            raise RuntimeError(f"response {created.get('id')} still {created.get('status')} after 30 minutes")
        time.sleep(wait)
        wait = min(wait * 1.5, 15.0)
        created = _http("GET", f"/responses/{created['id']}")
    return created


def output_text(response: dict[str, Any]) -> str:
    """The text of the message item(s) in a Responses API reply."""
    parts = []
    for item in response.get("output") or ():
        if item.get("type") == "message":
            for content in item.get("content") or ():
                if content.get("type") == "output_text":
                    parts.append(content.get("text") or "")
    return "".join(parts)


def respond(
    *,
    job: str,
    prompt_version: str,
    item: str,
    instructions: str,
    input_text: str,
    schema: dict[str, Any],
    max_output_tokens: int,
    model: str | None = None,
    effort: str | None = None,
    tier: str = "flex",
    confirm: bool = False,
    dry_run: bool = False,
    cache: Cache | None = None,
    transport: Transport | None = None,
) -> tuple[dict[str, Any] | None, Estimate]:
    """One structured call. Returns (cache entry or None on a dry run, estimate)."""
    model = model or config.authoring_model()
    effort = effort or config.DEFAULT_AUTHORING_EFFORT
    cache = cache or Cache()
    body: dict[str, Any] = {
        "model": model,
        "instructions": instructions,
        "input": input_text,
        "text": {"format": {"type": "json_schema", "name": job.replace("-", "_"),
                            "schema": schema, "strict": True}},
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    if effort != "none":
        body["reasoning"] = {"effort": effort}
    if tier != "default":
        body["service_tier"] = tier
    key = cache_key(body, prompt_version)
    # The cap is checked at the standard price even on flex: if a flex request
    # is served at full price, the cap must still hold.
    prices = _prices(model, "default")
    est_in = estimate_tokens(instructions + input_text + _canonical(schema))
    estimate = Estimate(
        input_tokens=est_in,
        max_output_tokens=max_output_tokens,
        worst_case_usd=(est_in * prices["input"] + max_output_tokens * prices["output"]) / 1_000_000,
    )
    hit = cache.get(job, prompt_version, key)
    if hit is not None:
        return {**hit, "from_cache": True}, estimate
    if dry_run:
        return None, estimate
    if not confirm:
        raise NotConfirmed(f"{job}/{item}: a paid call needs --confirm (dry run: --dry-run)")
    for attempt, wait in enumerate((0, *RETRY_WAITS)):
        time.sleep(wait if attempt else 0)
        _reserve(cache, estimate.worst_case_usd, f"{job}/{item}")
        try:
            entry = _call_and_record(cache, body, job, prompt_version, key, item, model, effort, tier,
                                     max_output_tokens, transport)
        finally:
            _release(estimate.worst_case_usd)
        error = entry.get("error") or {}
        if entry.get("status") == "failed" and error.get("code") in RETRYABLE and attempt < len(RETRY_WAITS):
            continue
        return entry, estimate
    return entry, estimate


def _call_and_record(cache, body, job, prompt_version, key, item, model, effort, tier,
                     max_output_tokens, transport) -> dict[str, Any]:
    started = time.time()
    response = (transport or _urllib_transport)("/responses", body)
    usage = response.get("usage") or {}
    reported = str(response.get("model") or model)
    served_tier = str(response.get("service_tier") or tier)
    entry = {
        "job": job,
        "prompt_version": prompt_version,
        "key": key,
        "item": item,
        "request_sha256": hashlib.sha256(_canonical(body).encode()).hexdigest(),
        "response_id": response.get("id"),
        "model_requested": model,
        "model_reported": reported,
        "effort": effort,
        "service_tier": served_tier,
        "max_output_tokens": max_output_tokens,
        "status": response.get("status"),
        "incomplete_details": response.get("incomplete_details"),
        "error": response.get("error"),
        "usage": usage,
        "cost_usd": round(cost_usd(reported, served_tier if served_tier in ("flex", "batch") else "default", usage), 6),
        "seconds": round(time.time() - started, 1),
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "output_text": output_text(response),
    }
    cache.put(entry)
    return entry


def embed(
    *, job: str, texts: list[str], model: str = "text-embedding-3-small", dimensions: int | None = None,
    confirm: bool = False, dry_run: bool = False, cache: Cache | None = None,
    transport: Transport | None = None,
) -> tuple[dict[str, Any] | None, list[list[float]], Estimate]:
    """Embed a batch of texts through the cap. Returns (ledger entry, vectors, estimate).

    **The vectors are not cached here.** The store that persists them is
    `search.vectors`, as a compact binary file; a JSON cache of the whole corpus
    would be ~75 MB. So the ledger entry records the call and its cost, and the
    caller decides — from its own store — whether a call is needed at all. Every
    call made is a new entry, because every call made is spend.
    """
    cache = cache or Cache()
    body: dict[str, Any] = {"model": model, "input": texts}
    if dimensions:
        body["dimensions"] = dimensions
    prices = _prices(model, "default")
    est_in = sum(estimate_tokens(t) for t in texts)
    estimate = Estimate(est_in, 0, est_in * prices["input"] / 1_000_000)
    if dry_run:
        return None, [], estimate
    if not confirm:
        raise NotConfirmed(f"{job}: a paid call needs --confirm")
    _reserve(cache, estimate.worst_case_usd, job)
    try:
        response = (transport or _urllib_transport)("/embeddings", body)
    finally:
        _release(estimate.worst_case_usd)
    usage = response.get("usage") or {}
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    entry = {
        "job": job, "prompt_version": "v2", "item": f"{len(texts)} texts",
        "key": hashlib.sha256((cache_key(body, "v2") + created).encode()).hexdigest(),
        "request_sha256": hashlib.sha256(_canonical(body).encode()).hexdigest(),
        "model_requested": model, "model_reported": str(response.get("model") or model),
        "service_tier": "default", "usage": usage, "status": "completed",
        "cost_usd": round(int(usage.get("prompt_tokens") or usage.get("total_tokens") or 0)
                          * prices["input"] / 1_000_000, 8),
        "created_utc": created,
        "dimensions": len((response.get("data") or [{}])[0].get("embedding") or []),
    }
    cache.put(entry)
    data = sorted(response.get("data") or (), key=lambda d: d.get("index", 0))
    return entry, [d.get("embedding") for d in data], estimate

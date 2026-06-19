"""Process-wide LLM token-usage and cost accounting.

Accumulates prompt/completion tokens per model across every LLM call in this
process and converts them to an estimated USD cost via a per-model price table.
The live monitor reads :data:`TRACKER` to show the running API cost of a run.

Each ``skydiscover-run`` invocation is its own process, so the tracker starts at
zero per run automatically — its total is the cost of *that* run.

Prices are **estimates**; edit :data:`MODEL_PRICING` to match your provider, or
override at runtime by setting the ``SKYDISCOVER_LLM_PRICING`` env var to JSON,
e.g. ``{"gpt-5.5": [1.25, 10.0]}`` (USD per 1M input/output tokens).
"""

import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("skydiscover.llm")

# Price per 1,000,000 tokens in USD: model-name prefix -> (input, output).
# Longest matching prefix wins, so "gpt-5-mini" is matched before "gpt-5".
# These are placeholders — correct them for your account/provider.
MODEL_PRICING: Dict[str, Tuple[float, float]] = {
    "gpt-5.5": (1.25, 10.00),
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5": (1.25, 10.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "o4-mini": (1.10, 4.40),
    "o3": (2.00, 8.00),
}


def _load_pricing_overrides() -> None:
    """Merge JSON pricing overrides from SKYDISCOVER_LLM_PRICING, if set."""
    raw = os.environ.get("SKYDISCOVER_LLM_PRICING")
    if not raw:
        return
    try:
        for name, pair in json.loads(raw).items():
            MODEL_PRICING[name.lower()] = (float(pair[0]), float(pair[1]))
    except Exception:
        logger.warning(
            "Ignoring malformed SKYDISCOVER_LLM_PRICING (expected JSON {model: [in, out]})"
        )


_load_pricing_overrides()


def _price_for(model: str) -> Tuple[float, float]:
    """Return (input, output) USD-per-1M price for *model* by longest-prefix match."""
    m = (model or "").lower()
    best_name = ""
    best_price = (0.0, 0.0)
    for name, price in MODEL_PRICING.items():
        if m.startswith(name) and len(name) > len(best_name):
            best_name, best_price = name, price
    return best_price


class _CostTracker:
    """Thread-safe accumulator of token usage and cost, keyed by model name."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._models: Dict[str, Dict[str, float]] = {}

    def record(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        reported_cost: Optional[float] = None,
    ) -> None:
        """Add one call's usage. If *reported_cost* (USD, from the provider) is
        given it is used verbatim; otherwise cost is estimated from the price table."""
        if reported_cost is not None:
            cost = float(reported_cost)
            estimated = False
        else:
            in_price, out_price = _price_for(model)
            cost = (prompt_tokens / 1e6) * in_price + (completion_tokens / 1e6) * out_price
            estimated = True
        with self._lock:
            m = self._models.setdefault(
                model,
                {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost": 0.0,
                    "calls": 0,
                    "estimated": False,
                },
            )
            m["prompt_tokens"] += prompt_tokens
            m["completion_tokens"] += completion_tokens
            m["cost"] += cost
            m["calls"] += 1
            if estimated:
                m["estimated"] = True

    def snapshot(self) -> Dict[str, object]:
        """Return a JSON-safe summary: total cost/tokens and a per-model breakdown.

        ``cost_estimated`` is True if any recorded cost came from the price table
        (vs. a provider-reported amount), so the UI can mark the figure approximate.
        """
        with self._lock:
            by_model = {k: dict(v) for k, v in self._models.items()}
        total_cost = sum(v["cost"] for v in by_model.values())
        total_tokens = sum(v["prompt_tokens"] + v["completion_tokens"] for v in by_model.values())
        cost_estimated = any(v.get("estimated") for v in by_model.values())
        for v in by_model.values():
            v["cost"] = round(v["cost"], 4)
        return {
            "total_cost": round(total_cost, 4),
            "total_tokens": int(total_tokens),
            "cost_estimated": cost_estimated,
            "by_model": by_model,
        }


# Process-global singleton.
TRACKER = _CostTracker()


def _get(usage: Any, key: str) -> Any:
    """Read *key* from a dict or object usage payload."""
    if isinstance(usage, dict):
        return usage.get(key)
    return getattr(usage, key, None)


def record_usage(model: str, usage: Optional[Any]) -> None:
    """Record token usage from an OpenAI-style ``usage`` payload.

    Accepts either an SDK object (attributes) or a raw JSON ``dict``, and both the
    Chat Completions (``prompt_tokens``/``completion_tokens``) and Responses API
    (``input_tokens``/``output_tokens``) field names. If the payload carries a
    provider-reported dollar cost (``cost``/``total_cost``, as some gateways like
    OpenRouter return), that exact amount is used instead of the price table.
    Never raises.
    """
    if usage is None:
        return
    try:
        prompt = _get(usage, "prompt_tokens")
        completion = _get(usage, "completion_tokens")
        if prompt is None:
            prompt = _get(usage, "input_tokens")
        if completion is None:
            completion = _get(usage, "output_tokens")

        reported = _get(usage, "cost")
        if reported is None:
            reported = _get(usage, "total_cost")
        try:
            reported = float(reported) if reported is not None else None
        except (TypeError, ValueError):
            reported = None

        TRACKER.record(model, int(prompt or 0), int(completion or 0), reported_cost=reported)
    except Exception:
        logger.debug("Failed to record token usage", exc_info=True)


# ----------------------------------------------------------------------
# Cross-process pass-through (containerized / out-of-process evaluators)
# ----------------------------------------------------------------------
#
# LLM calls made *inside* a Docker container run in a separate process, so their
# usage lands in that process's tracker, not the host's. To surface it on the
# host's dashboard, a containerized evaluator emits its usage in the result it
# already returns — by convention an ``llm_usage`` array of
# ``{"model", "prompt_tokens", "completion_tokens"}`` entries — and the host
# evaluator calls :func:`merge_usage` on it. In-container code that uses this
# module can produce that array in one call via :func:`export_usage`.


def export_usage() -> List[Dict[str, int]]:
    """Return this process's accumulated per-model usage as a JSON-safe list.

    Call this inside a containerized evaluator and emit the result as the
    ``llm_usage`` field of its JSON output so the host can :func:`merge_usage` it.
    """
    snap = TRACKER.snapshot()
    by_model: Dict[str, Dict[str, float]] = snap["by_model"]  # type: ignore[assignment]
    return [
        {
            "model": model,
            "prompt_tokens": int(v["prompt_tokens"]),
            "completion_tokens": int(v["completion_tokens"]),
        }
        for model, v in by_model.items()
    ]


def merge_usage(payload: Optional[Any]) -> None:
    """Merge usage reported by a containerized/out-of-process evaluator.

    *payload* is the ``llm_usage`` value from the evaluator's result: a list of
    ``{"model", "prompt_tokens", "completion_tokens"}`` dicts (as produced by
    :func:`export_usage`). Tokens are re-priced with the host's table. Never raises.
    """
    if not payload:
        return
    try:
        for item in payload:
            reported = item.get("cost")
            try:
                reported = float(reported) if reported is not None else None
            except (TypeError, ValueError):
                reported = None
            TRACKER.record(
                str(item.get("model", "unknown")),
                int(item.get("prompt_tokens", 0) or 0),
                int(item.get("completion_tokens", 0) or 0),
                reported_cost=reported,
            )
    except Exception:
        logger.debug("Failed to merge container LLM usage", exc_info=True)

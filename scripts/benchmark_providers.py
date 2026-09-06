#!/usr/bin/env python3
"""Benchmark streaming latency and usage across configured providers.

The benchmark makes live requests only to providers that are configured through
environment variables. It never prints secret values. Usage fields are provider
reported when available and otherwise marked as unavailable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples" / "render-agent"))

import app  # noqa: E402


@dataclass
class Result:
    provider: str
    iteration: int
    status: str
    time_to_first_token_ms: float | None = None
    total_latency_ms: float | None = None
    output_chars: int = 0
    input_tokens: int | None = None
    output_tokens: int | None = None
    error: str | None = None


def configured(provider: str) -> bool:
    if provider == "mock":
        return True
    if provider == "gemini":
        return bool(os.getenv("GEMINI_API_KEY"))
    if provider == "claude":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    if provider == "ollama":
        return bool(os.getenv("OLLAMA_BENCHMARK", "")) or bool(os.getenv("BASE_URL"))
    if provider == "openai_compatible":
        return bool(os.getenv("BASE_URL"))
    return False


def run_once(provider: str, prompt: str, iteration: int) -> Result:
    os.environ["PROVIDER"] = provider
    started = time.perf_counter()
    first: float | None = None
    text_parts: list[str] = []
    usage: dict[str, int] = {}
    try:
        for event in app.stream_agent(prompt, "Answer concisely for a latency benchmark."):
            text = event.get("text", "")
            if text and first is None:
                first = time.perf_counter()
            text_parts.append(text)
            usage.update({key: value for key, value in (event.get("usage") or {}).items() if value is not None})
        ended = time.perf_counter()
        return Result(
            provider=provider,
            iteration=iteration,
            status="ok",
            time_to_first_token_ms=round((first - started) * 1000, 2) if first else None,
            total_latency_ms=round((ended - started) * 1000, 2),
            output_chars=len("".join(text_parts)),
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
        )
    except Exception as exc:  # benchmark should report a provider failure and continue
        ended = time.perf_counter()
        return Result(provider, iteration, "error", None, round((ended - started) * 1000, 2), error=str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--providers", default="claude,gemini,ollama,openai_compatible", help="Comma-separated providers")
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--prompt", default="Give one sentence explaining why tests matter.")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    results: list[Result] = []
    for provider in [item.strip() for item in args.providers.split(",") if item.strip()]:
        if not configured(provider):
            results.append(Result(provider, 0, "skipped", error="provider credentials or endpoint not configured"))
            continue
        for iteration in range(1, args.iterations + 1):
            results.append(run_once(provider, args.prompt, iteration))

    serialized = [asdict(result) for result in results]
    output = json.dumps(serialized, indent=2)
    print(output)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    return 0 if all(item.status in {"ok", "skipped"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

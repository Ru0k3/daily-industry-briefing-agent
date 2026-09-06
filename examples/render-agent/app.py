"""Small provider-neutral agent service with unary and streaming provider adapters."""

import json
import os
from collections.abc import Iterator
from typing import Any
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="Provider-Neutral Agent Example")


class RunRequest(BaseModel):
    input: str
    system: str = "You are a concise, helpful agent."


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urlopen(request, timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))) as response:
        return json.loads(response.read().decode("utf-8"))


def _request(url: str, payload: dict[str, Any], headers: dict[str, str]):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    return urlopen(request, timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60")))


def _event(text: str = "", usage: dict[str, int] | None = None, done: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"text": text, "done": done}
    if usage:
        result["usage"] = usage
    return result


def _parse_sse_lines(lines: Iterator[bytes], provider: str) -> Iterator[dict[str, Any]]:
    for raw in lines:
        line = raw.decode("utf-8").strip()
        if not line or not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            yield _event(done=True)
            continue
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            continue
        if provider == "claude":
            event_type = payload.get("type")
            if event_type == "content_block_delta":
                yield _event(payload.get("delta", {}).get("text", ""))
            elif event_type == "message_start":
                usage = payload.get("message", {}).get("usage", {})
                if usage:
                    yield _event(usage={"input_tokens": usage.get("input_tokens", 0)})
            elif event_type == "message_delta":
                usage = payload.get("usage", {})
                if usage:
                    yield _event(usage={"output_tokens": usage.get("output_tokens", 0)})
            elif event_type == "message_stop":
                yield _event(done=True)
        elif provider == "gemini":
            candidates = payload.get("candidates") or [{}]
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            text = "".join(part.get("text", "") for part in parts)
            if text:
                yield _event(text)
            if candidates[0].get("finishReason"):
                yield _event(done=True)
        else:
            choice = (payload.get("choices") or [{}])[0]
            delta = choice.get("delta", {})
            text = delta.get("content", "")
            usage = payload.get("usage")
            if text or usage:
                yield _event(text, usage)
            if choice.get("finish_reason"):
                yield _event(done=True)


def stream_agent(user_input: str, system: str) -> Iterator[dict[str, Any]]:
    """Yield normalized streaming events: text fragments, usage, and done."""
    provider = os.getenv("PROVIDER", "mock").lower()
    if provider == "mock":
        text = f"Mock agent received: {user_input}"
        words = text.split(" ")
        for index, word in enumerate(words):
            yield _event(word + (" " if index < len(words) - 1 else ""))
        yield _event(done=True, usage={"input_tokens": len(user_input.split()), "output_tokens": len(text.split())})
        return

    if provider == "gemini":
        api_key = os.environ["GEMINI_API_KEY"]
        model = os.getenv("MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user_input}]}],
        }
        with _request(url, payload, {}) as response:
            for event in _parse_sse_lines(response, "gemini"):
                if event.get("text") or event.get("usage") or event.get("done"):
                    yield event
        return

    if provider == "claude":
        api_key = os.environ["ANTHROPIC_API_KEY"]
        model = os.getenv("MODEL", "claude-sonnet-4-5")
        payload = {
            "model": model,
            "max_tokens": int(os.getenv("MAX_TOKENS", "512")),
            "system": system,
            "messages": [{"role": "user", "content": user_input}],
            "stream": True,
        }
        with _request("https://api.anthropic.com/v1/messages", payload, {"x-api-key": api_key, "anthropic-version": "2023-06-01"}) as response:
            yield from _parse_sse_lines(response, "claude")
        return

    if provider == "ollama":
        base_url = os.getenv("BASE_URL", "http://localhost:11434/api").rstrip("/")
        payload = {
            "model": os.getenv("MODEL", "gemma4"),
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_input}],
            "stream": True,
        }
        with _request(f"{base_url}/chat", payload, {}) as response:
            for raw in response:
                if not raw.strip():
                    continue
                data = json.loads(raw)
                message = data.get("message", {})
                usage = {}
                if data.get("done"):
                    usage = {"input_tokens": data.get("prompt_eval_count", 0), "output_tokens": data.get("eval_count", 0)}
                yield _event(message.get("content", ""), usage or None, bool(data.get("done")))
        return

    if provider == "openai_compatible":
        base_url = os.getenv("BASE_URL", "http://localhost:11434/v1").rstrip("/")
        headers = {}
        if os.getenv("OPENAI_COMPATIBLE_API_KEY"):
            headers["Authorization"] = f"Bearer {os.environ['OPENAI_COMPATIBLE_API_KEY']}"
        payload = {
            "model": os.getenv("MODEL", "local-model"),
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_input}],
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        with _request(f"{base_url}/chat/completions", payload, headers) as response:
            yield from _parse_sse_lines(response, "openai")
        return

    raise ValueError(f"Unsupported PROVIDER: {provider}")


def run_agent(user_input: str, system: str) -> str:
    provider = os.getenv("PROVIDER", "mock").lower()
    if provider == "mock":
        return f"Mock agent received: {user_input}"
    if provider == "gemini":
        api_key = os.environ["GEMINI_API_KEY"]
        model = os.getenv("MODEL", "gemini-2.5-flash")
        data = _post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user_input}]}]},
            {},
        )
        return data["candidates"][0]["content"]["parts"][0]["text"]
    if provider == "claude":
        data = _post_json(
            "https://api.anthropic.com/v1/messages",
            {"model": os.getenv("MODEL", "claude-sonnet-4-5"), "max_tokens": int(os.getenv("MAX_TOKENS", "512")), "system": system, "messages": [{"role": "user", "content": user_input}]},
            {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
        )
        return "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
    if provider == "ollama":
        base_url = os.getenv("BASE_URL", "http://localhost:11434/api").rstrip("/")
        data = _post_json(f"{base_url}/chat", {"model": os.getenv("MODEL", "gemma4"), "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_input}], "stream": False}, {})
        return data["message"]["content"]
    if provider == "openai_compatible":
        base_url = os.getenv("BASE_URL", "http://localhost:11434/v1").rstrip("/")
        headers = {"Authorization": f"Bearer {os.environ['OPENAI_COMPATIBLE_API_KEY']}"} if os.getenv("OPENAI_COMPATIBLE_API_KEY") else {}
        data = _post_json(f"{base_url}/chat/completions", {"model": os.getenv("MODEL", "local-model"), "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_input}]}, headers)
        return data["choices"][0]["message"]["content"]
    raise ValueError(f"Unsupported PROVIDER: {provider}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": os.getenv("PROVIDER", "mock")}


@app.post("/run")
def run(request: RunRequest) -> dict[str, str]:
    try:
        return {"output": run_agent(request.input, request.system)}
    except (KeyError, ValueError, IndexError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/stream")
def stream(request: RunRequest) -> StreamingResponse:
    def body() -> Iterator[str]:
        try:
            for event in stream_agent(request.input, request.system):
                if event.get("text"):
                    yield event["text"]
        except (KeyError, ValueError, IndexError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            yield f"\n[stream error: {exc}]"

    return StreamingResponse(body(), media_type="text/plain; charset=utf-8")

"""Provider-neutral agent service with streaming, metrics, and multi-turn memory."""

import json
import os
import time
from collections.abc import Iterator
from typing import Any
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

app = FastAPI(title="Provider-Neutral Agent Example")

REQUESTS = Counter("agent_requests_total", "Agent requests", ["endpoint", "provider", "status"])
ERRORS = Counter("agent_errors_total", "Agent errors", ["endpoint", "provider", "error_type"])
LATENCY = Histogram("agent_request_latency_seconds", "Agent request latency", ["endpoint", "provider"])
TOKENS = Counter("agent_tokens_total", "Provider-reported tokens", ["provider", "direction"])


class RunRequest(BaseModel):
    input: str
    system: str = "You are a concise, helpful agent."
    conversation_id: str | None = Field(default=None, max_length=128)
    reset: bool = False


class ConversationMemory:
    """Bounded process-local memory; use an external store for multi-instance production."""

    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self._conversations: dict[str, list[dict[str, str]]] = {}

    def get(self, conversation_id: str | None) -> list[dict[str, str]]:
        if not conversation_id:
            return []
        return [dict(item) for item in self._conversations.get(conversation_id, [])]

    def append(self, conversation_id: str | None, user_input: str, assistant_output: str) -> None:
        if not conversation_id:
            return
        history = self._conversations.setdefault(conversation_id, [])
        history.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_output},
        ])
        self._conversations[conversation_id] = history[-(self.max_turns * 2):]

    def clear(self, conversation_id: str | None) -> None:
        if conversation_id:
            self._conversations.pop(conversation_id, None)


memory = ConversationMemory(max_turns=int(os.getenv("MAX_CONVERSATION_TURNS", "20")))


def _provider() -> str:
    return os.getenv("PROVIDER", "mock").lower()


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", **headers}, method="POST")
    with urlopen(request, timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))) as response:
        return json.loads(response.read().decode("utf-8"))


def _request(url: str, payload: dict[str, Any], headers: dict[str, str]):
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", **headers}, method="POST")
    return urlopen(request, timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60")))


def _event(text: str = "", usage: dict[str, int] | None = None, done: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"text": text, "done": done}
    if usage:
        result["usage"] = usage
    return result


def _record_usage(provider: str, usage: dict[str, int] | None) -> None:
    for direction in ("input_tokens", "output_tokens"):
        if usage and usage.get(direction) is not None:
            TOKENS.labels(provider, direction).inc(usage[direction])


def _provider_messages(history: list[dict[str, str]], system: str, user_input: str, provider: str) -> list[dict[str, Any]]:
    turns = history + [{"role": "user", "content": user_input}]
    if provider == "gemini":
        return [{"role": "model" if turn["role"] == "assistant" else "user", "parts": [{"text": turn["content"]}]} for turn in turns]
    return turns


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
            text = "".join(part.get("text", "") for part in content.get("parts", []))
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


def stream_agent(user_input: str, system: str, history: list[dict[str, str]] | None = None) -> Iterator[dict[str, Any]]:
    """Yield normalized streaming events while including prior turns in the request."""
    provider = _provider()
    history = history or []
    if provider == "mock":
        text = f"Mock agent received: {user_input}"
        if history:
            text += f" (remembered {len(history) // 2} prior turns)"
        words = text.split(" ")
        for index, word in enumerate(words):
            yield _event(word + (" " if index < len(words) - 1 else ""))
        yield _event(done=True, usage={"input_tokens": len(user_input.split()), "output_tokens": len(text.split())})
        return

    if provider == "gemini":
        api_key = os.environ["GEMINI_API_KEY"]
        model = os.getenv("MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}"
        payload = {"systemInstruction": {"parts": [{"text": system}]}, "contents": _provider_messages(history, system, user_input, "gemini")}
        with _request(url, payload, {}) as response:
            yield from _parse_sse_lines(response, "gemini")
        return

    if provider == "claude":
        payload = {"model": os.getenv("MODEL", "claude-sonnet-4-5"), "max_tokens": int(os.getenv("MAX_TOKENS", "512")), "system": system, "messages": _provider_messages(history, system, user_input, "claude"), "stream": True}
        with _request("https://api.anthropic.com/v1/messages", payload, {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"}) as response:
            yield from _parse_sse_lines(response, "claude")
        return

    if provider == "ollama":
        base_url = os.getenv("BASE_URL", "http://localhost:11434/api").rstrip("/")
        payload = {"model": os.getenv("MODEL", "gemma4"), "messages": [{"role": "system", "content": system}] + _provider_messages(history, system, user_input, "ollama"), "stream": True}
        with _request(f"{base_url}/chat", payload, {}) as response:
            for raw in response:
                if raw.strip():
                    data = json.loads(raw)
                    usage = {"input_tokens": data.get("prompt_eval_count", 0), "output_tokens": data.get("eval_count", 0)} if data.get("done") else None
                    yield _event(data.get("message", {}).get("content", ""), usage, bool(data.get("done")))
        return

    if provider == "openai_compatible":
        base_url = os.getenv("BASE_URL", "http://localhost:11434/v1").rstrip("/")
        headers = {"Authorization": f"Bearer {os.environ['OPENAI_COMPATIBLE_API_KEY']}"} if os.getenv("OPENAI_COMPATIBLE_API_KEY") else {}
        payload = {"model": os.getenv("MODEL", "local-model"), "messages": [{"role": "system", "content": system}] + _provider_messages(history, system, user_input, "openai_compatible"), "stream": True, "stream_options": {"include_usage": True}}
        with _request(f"{base_url}/chat/completions", payload, headers) as response:
            yield from _parse_sse_lines(response, "openai")
        return

    raise ValueError(f"Unsupported PROVIDER: {provider}")


def run_agent(user_input: str, system: str, history: list[dict[str, str]] | None = None) -> str:
    provider = _provider()
    history = history or []
    if provider == "mock":
        return f"Mock agent received: {user_input}" + (f" (remembered {len(history) // 2} prior turns)" if history else "")
    if provider == "gemini":
        data = _post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{os.getenv('MODEL', 'gemini-2.5-flash')}:generateContent?key={os.environ['GEMINI_API_KEY']}", {"systemInstruction": {"parts": [{"text": system}]}, "contents": _provider_messages(history, system, user_input, "gemini")}, {})
        return data["candidates"][0]["content"]["parts"][0]["text"]
    if provider == "claude":
        data = _post_json("https://api.anthropic.com/v1/messages", {"model": os.getenv("MODEL", "claude-sonnet-4-5"), "max_tokens": int(os.getenv("MAX_TOKENS", "512")), "system": system, "messages": _provider_messages(history, system, user_input, "claude")}, {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"})
        return "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
    if provider == "ollama":
        data = _post_json(f"{os.getenv('BASE_URL', 'http://localhost:11434/api').rstrip('/')}/chat", {"model": os.getenv("MODEL", "gemma4"), "messages": [{"role": "system", "content": system}] + _provider_messages(history, system, user_input, "ollama"), "stream": False}, {})
        return data["message"]["content"]
    if provider == "openai_compatible":
        headers = {"Authorization": f"Bearer {os.environ['OPENAI_COMPATIBLE_API_KEY']}"} if os.getenv("OPENAI_COMPATIBLE_API_KEY") else {}
        data = _post_json(f"{os.getenv('BASE_URL', 'http://localhost:11434/v1').rstrip('/')}/chat/completions", {"model": os.getenv("MODEL", "local-model"), "messages": [{"role": "system", "content": system}] + _provider_messages(history, system, user_input, "openai_compatible")}, headers)
        return data["choices"][0]["message"]["content"]
    raise ValueError(f"Unsupported PROVIDER: {provider}")


def _record_request(endpoint: str, started: float, status: str = "success", error: Exception | None = None) -> None:
    provider = _provider()
    REQUESTS.labels(endpoint, provider, status).inc()
    LATENCY.labels(endpoint, provider).observe(time.perf_counter() - started)
    if error:
        ERRORS.labels(endpoint, provider, type(error).__name__).inc()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": _provider()}


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/run")
def run(request: RunRequest) -> dict[str, str]:
    started = time.perf_counter()
    if request.reset:
        memory.clear(request.conversation_id)
    history = memory.get(request.conversation_id)
    try:
        output = run_agent(request.input, request.system, history)
        memory.append(request.conversation_id, request.input, output)
        _record_request("run", started)
        return {"output": output, "conversation_id": request.conversation_id or ""}
    except (KeyError, ValueError, IndexError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        _record_request("run", started, "error", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/stream")
def stream(request: RunRequest) -> StreamingResponse:
    if request.reset:
        memory.clear(request.conversation_id)
    history = memory.get(request.conversation_id)

    def body() -> Iterator[str]:
        started = time.perf_counter()
        output_parts: list[str] = []
        try:
            for event in stream_agent(request.input, request.system, history):
                _record_usage(_provider(), event.get("usage"))
                text = event.get("text", "")
                output_parts.append(text)
                if text:
                    yield text
            output = "".join(output_parts)
            memory.append(request.conversation_id, request.input, output)
            _record_request("stream", started)
        except (KeyError, ValueError, IndexError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            _record_request("stream", started, "error", exc)
            yield f"\n[stream error: {exc}]"

    return StreamingResponse(body(), media_type="text/plain; charset=utf-8")

import json
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "examples", "render-agent"))

import app  # noqa: E402


class FakeStreamingResponse:
    def __init__(self, lines):
        self.lines = lines

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __iter__(self):
        return iter(self.lines)


def fake_stream(lines):
    return lambda request, timeout: FakeStreamingResponse(lines)


def collect(provider, fake, monkeypatch):
    monkeypatch.setenv("PROVIDER", provider)
    with patch.object(app, "urlopen", fake):
        return list(app.stream_agent("question", "system"))


def test_mock_streaming(monkeypatch):
    events = collect("mock", None, monkeypatch)
    assert "".join(event["text"] for event in events) == "Mock agent received: question"
    assert events[-1]["done"] is True
    assert events[-1]["usage"]["output_tokens"] > 0


def test_claude_sse_stream(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
    lines = [
        b'data: {"type":"message_start","message":{"usage":{"input_tokens":4}}}\n\n',
        b'data: {"type":"content_block_delta","delta":{"text":"Hello"}}\n\n',
        b'data: {"type":"message_delta","usage":{"output_tokens":2}}\n\n',
        b'data: {"type":"message_stop"}\n\n',
    ]
    events = collect("claude", fake_stream(lines), monkeypatch)
    assert "".join(event["text"] for event in events) == "Hello"
    assert events[-1]["done"] is True
    assert {key for event in events for key in event.get("usage", {})} == {"input_tokens", "output_tokens"}


def test_gemini_sse_stream(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "key")
    lines = [
        b'data: {"candidates":[{"content":{"parts":[{"text":"Hi"}]}}]}\n\n',
        b'data: {"candidates":[{"finishReason":"STOP"}]}\n\n',
    ]
    events = collect("gemini", fake_stream(lines), monkeypatch)
    assert "".join(event["text"] for event in events) == "Hi"


def test_ollama_ndjson_stream(monkeypatch):
    lines = [
        json.dumps({"message": {"content": "Hi"}, "done": False}).encode() + b"\n",
        json.dumps({"message": {"content": "!"}, "done": True, "prompt_eval_count": 4, "eval_count": 2}).encode() + b"\n",
    ]
    events = collect("ollama", fake_stream(lines), monkeypatch)
    assert "".join(event["text"] for event in events) == "Hi!"
    assert events[-1]["usage"] == {"input_tokens": 4, "output_tokens": 2}


def test_openai_compatible_sse_stream(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://example/v1")
    lines = [
        b'data: {"choices":[{"delta":{"content":"Hi"}}]}\n\n',
        b'data: {"choices":[{"delta":{"content":"!"},"finish_reason":"stop"}],"usage":{"prompt_tokens":4,"completion_tokens":2}}\n\n',
        b'data: [DONE]\n\n',
    ]
    events = collect("openai_compatible", fake_stream(lines), monkeypatch)
    assert "".join(event["text"] for event in events) == "Hi!"
    assert events[-1]["done"] is True

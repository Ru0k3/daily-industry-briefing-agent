import json
import os
import sys
from unittest.mock import patch
from urllib.request import Request

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "examples", "render-agent"))

import app  # noqa: E402


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def fake_response(payload):
    return FakeResponse(payload)


def capture_urlopen(payload):
    calls = []

    def _urlopen(request: Request, timeout: float):
        calls.append((request, timeout))
        return fake_response(payload)

    return calls, _urlopen


def test_mock_provider_is_deterministic(monkeypatch):
    monkeypatch.setenv("PROVIDER", "mock")
    assert app.run_agent("hello", "system") == "Mock agent received: hello"


def test_gemini_request_shape_and_response(monkeypatch):
    monkeypatch.setenv("PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("MODEL", "gemini-test")
    calls, fake = capture_urlopen(
        {"candidates": [{"content": {"parts": [{"text": "Gemini answer"}]}}]}
    )
    with patch.object(app, "urlopen", fake):
        result = app.run_agent("question", "be precise")
    request, timeout = calls[0]
    body = json.loads(request.data)
    assert result == "Gemini answer"
    assert request.full_url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-test:generateContent?key=test-key"
    assert body["systemInstruction"]["parts"][0]["text"] == "be precise"
    assert body["contents"][0]["parts"][0]["text"] == "question"
    assert timeout == 60.0


def test_ollama_native_request_shape(monkeypatch):
    monkeypatch.setenv("PROVIDER", "ollama")
    monkeypatch.setenv("MODEL", "qwen3")
    monkeypatch.setenv("BASE_URL", "http://ollama:11434/api")
    calls, fake = capture_urlopen({"message": {"content": "Ollama answer"}})
    with patch.object(app, "urlopen", fake):
        result = app.run_agent("question", "system")
    request, _ = calls[0]
    body = json.loads(request.data)
    assert result == "Ollama answer"
    assert request.full_url == "http://ollama:11434/api/chat"
    assert body["model"] == "qwen3"
    assert body["stream"] is False


def test_openai_compatible_request_and_optional_auth(monkeypatch):
    monkeypatch.setenv("PROVIDER", "openai_compatible")
    monkeypatch.setenv("BASE_URL", "https://llm.example/v1/")
    monkeypatch.setenv("MODEL", "local-model")
    monkeypatch.setenv("OPENAI_COMPATIBLE_API_KEY", "secret")
    calls, fake = capture_urlopen(
        {"choices": [{"message": {"content": "Compatible answer"}}]}
    )
    with patch.object(app, "urlopen", fake):
        result = app.run_agent("question", "system")
    request, _ = calls[0]
    body = json.loads(request.data)
    assert result == "Compatible answer"
    assert request.full_url == "https://llm.example/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer secret"
    assert body["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "question"},
    ]


def test_missing_gemini_key_fails_before_network(monkeypatch):
    monkeypatch.setenv("PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(KeyError, match="GEMINI_API_KEY"):
        app.run_agent("question", "system")


def test_unsupported_provider_is_explicit(monkeypatch):
    monkeypatch.setenv("PROVIDER", "unknown")
    with pytest.raises(ValueError, match="Unsupported PROVIDER: unknown"):
        app.run_agent("question", "system")


def test_http_errors_are_not_silently_converted(monkeypatch):
    monkeypatch.setenv("PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    with patch.object(app, "urlopen", side_effect=TimeoutError("upstream timeout")):
        with pytest.raises(TimeoutError, match="upstream timeout"):
            app.run_agent("question", "system")

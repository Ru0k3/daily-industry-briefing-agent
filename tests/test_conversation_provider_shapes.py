import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "examples", "render-agent"))

import app  # noqa: E402


HISTORY = [
    {"role": "user", "content": "My name is Alex."},
    {"role": "assistant", "content": "Hello Alex."},
]


def run_with(provider, monkeypatch, response):
    monkeypatch.setenv("PROVIDER", provider)
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    with patch.object(app, "_post_json", return_value=response) as post:
        app.run_agent("What is my name?", "Be concise.", HISTORY)
    return post.call_args.args[1]


def test_claude_receives_prior_turns(monkeypatch):
    payload = run_with("claude", monkeypatch, {"content": [{"type": "text", "text": "Alex"}]})
    assert payload["messages"][:2] == HISTORY


def test_gemini_maps_assistant_to_model(monkeypatch):
    payload = run_with("gemini", monkeypatch, {"candidates": [{"content": {"parts": [{"text": "Alex"}]}}]})
    assert payload["contents"][0] == {"role": "user", "parts": [{"text": "My name is Alex."}]}
    assert payload["contents"][1] == {"role": "model", "parts": [{"text": "Hello Alex."}]}


def test_ollama_receives_system_and_prior_turns(monkeypatch):
    payload = run_with("ollama", monkeypatch, {"message": {"content": "Alex"}})
    assert payload["messages"][:3] == [{"role": "system", "content": "Be concise."}] + HISTORY


def test_openai_compatible_receives_system_and_prior_turns(monkeypatch):
    payload = run_with("openai_compatible", monkeypatch, {"choices": [{"message": {"content": "Alex"}}]})
    assert payload["messages"][:3] == [{"role": "system", "content": "Be concise."}] + HISTORY

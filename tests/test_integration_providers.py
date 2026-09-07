"""Credential-gated live provider tests.

These tests never contain API keys. They run only when the corresponding
environment variables are supplied by a secure CI secret store.
"""

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "examples", "render-agent"))

import app  # noqa: E402


pytestmark = pytest.mark.integration


def require(name: str) -> str:
    if os.getenv("RUN_LIVE_INTEGRATION", "false").lower() not in {"1", "true", "yes"}:
        pytest.skip("live integration tests require RUN_LIVE_INTEGRATION=true")
    value = os.getenv(name)
    if not value:
        pytest.skip(f"{name} is not configured; live provider test skipped")
    return value


def test_live_claude():
    require("CLAUDE_API_KEY")
    os.environ.update({"PROVIDER": "claude", "ANTHROPIC_API_KEY": os.environ["CLAUDE_API_KEY"], "MODEL": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")})
    output = app.run_agent("Reply with the single word: ok", "You are a test provider.")
    assert output.strip()


def test_live_gemini():
    require("GEMINI_API_KEY")
    os.environ.update({"PROVIDER": "gemini", "MODEL": os.getenv("GEMINI_MODEL", "gemini-2.5-flash")})
    output = app.run_agent("Reply with the single word: ok", "You are a test provider.")
    assert output.strip()


def test_live_openai():
    require("OPENAI_API_KEY")
    os.environ.update({"PROVIDER": "openai_compatible", "OPENAI_COMPATIBLE_API_KEY": os.environ["OPENAI_API_KEY"], "BASE_URL": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"), "MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini")})
    output = app.run_agent("Reply with the single word: ok", "You are a test provider.")
    assert output.strip()

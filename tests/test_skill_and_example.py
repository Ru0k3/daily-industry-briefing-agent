from pathlib import Path

from fastapi.testclient import TestClient

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples" / "render-agent"))

from app import app  # noqa: E402


client = TestClient(app)


def test_skill_has_provider_neutral_metadata():
    skill = (ROOT / "provider-neutral-agent-launch" / "SKILL.md").read_text()
    assert "name: provider-neutral-agent-launch" in skill
    assert "without assuming a specific model vendor" in skill
    assert "Claude Managed Agents" not in skill
    assert "ANTHROPIC_API_KEY" not in skill


def test_references_cover_hosting_and_adapters():
    hosting = (ROOT / "provider-neutral-agent-launch" / "references" / "hosting-options.md").read_text()
    adapters = (ROOT / "provider-neutral-agent-launch" / "references" / "provider-adapters.md").read_text()
    assert "Render" in hosting
    assert "Google Gemini" in adapters
    assert "Open-source and self-hosted models" in adapters


def test_render_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "provider": "mock"}


def test_mock_agent_endpoint():
    response = client.post("/run", json={"input": "hello"})
    assert response.status_code == 200
    assert response.json()["output"] == "Mock agent received: hello"

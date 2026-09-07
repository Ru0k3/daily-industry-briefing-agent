import pytest


@pytest.fixture(autouse=True)
def isolate_service_environment(monkeypatch):
    monkeypatch.setenv("PROVIDER", "mock")
    monkeypatch.delenv("REQUIRE_API_KEY", raising=False)
    monkeypatch.delenv("AGENT_API_KEYS", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    yield

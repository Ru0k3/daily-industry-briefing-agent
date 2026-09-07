import hashlib
import json
import os
import sys

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "examples", "render-agent"))

import app as app_module  # noqa: E402


client = TestClient(app_module.app)


def configure(monkeypatch, limit="60"):
    key = "tenant-a-secret"
    monkeypatch.setenv("REQUIRE_API_KEY", "true")
    monkeypatch.setenv("AGENT_API_KEYS", json.dumps({"tenant-a": hashlib.sha256(key.encode()).hexdigest(), "tenant-b": hashlib.sha256(b"tenant-b-secret").hexdigest()}))
    app_module.rate_limiter.limit = int(limit)
    app_module.rate_limiter._local.clear()
    return key


def test_missing_and_invalid_api_keys_are_rejected(monkeypatch):
    configure(monkeypatch)
    assert client.post("/run", json={"input": "hello"}).status_code == 401
    assert client.post("/run", headers={"X-API-Key": "wrong"}, json={"input": "hello"}).status_code == 401


def test_tenant_header_must_match_authenticated_key(monkeypatch):
    key = configure(monkeypatch)
    response = client.post("/run", headers={"X-API-Key": key, "X-Tenant-ID": "tenant-b"}, json={"input": "hello"})
    assert response.status_code == 403


def test_valid_key_returns_tenant_and_isolates_history(monkeypatch):
    key = configure(monkeypatch)
    first = client.post("/run", headers={"X-API-Key": key}, json={"conversation_id": "same-id", "input": "first"})
    second = client.post("/run", headers={"X-API-Key": key}, json={"conversation_id": "same-id", "input": "second"})
    assert first.status_code == 200
    assert first.json()["tenant_id"] == "tenant-a"
    assert "remembered 1 prior turns" in second.json()["output"]


def test_rate_limit_returns_retry_after(monkeypatch):
    key = configure(monkeypatch, limit="1")
    assert client.post("/run", headers={"X-API-Key": key}, json={"input": "one"}).status_code == 200
    response = client.post("/run", headers={"X-API-Key": key}, json={"input": "two"})
    assert response.status_code == 429
    assert "Retry-After" in response.headers

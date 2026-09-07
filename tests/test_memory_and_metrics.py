from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples" / "render-agent"))

from app import app  # noqa: E402


client = TestClient(app)


def test_run_persists_and_reuses_conversation_history():
    conversation_id = "memory-test-run"
    first = client.post("/run", json={"input": "first", "conversation_id": conversation_id})
    second = client.post("/run", json={"input": "second", "conversation_id": conversation_id})
    assert first.status_code == 200
    assert second.status_code == 200
    assert "remembered 1 prior turns" in second.json()["output"]


def test_reset_clears_conversation_history():
    conversation_id = "memory-test-reset"
    client.post("/run", json={"input": "first", "conversation_id": conversation_id})
    reset = client.post("/run", json={"input": "new conversation", "conversation_id": conversation_id, "reset": True})
    assert "remembered" not in reset.json()["output"]


def test_stream_persists_history_and_metrics_are_exposed():
    conversation_id = "memory-test-stream"
    first = client.post("/stream", json={"input": "first", "conversation_id": conversation_id})
    second = client.post("/stream", json={"input": "second", "conversation_id": conversation_id})
    metrics = client.get("/metrics")
    assert first.status_code == 200
    assert second.status_code == 200
    assert "remembered 1 prior turns" in second.text
    assert metrics.status_code == 200
    assert "agent_requests_total" in metrics.text
    assert "agent_request_latency_seconds" in metrics.text

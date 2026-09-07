import os
import uuid

from locust import HttpUser, between, task


class AgentUser(HttpUser):
    """Load profile for authenticated tenant traffic.

    Each virtual user owns a conversation ID and makes two turns so a Redis-backed
    deployment can be checked for history continuity while many users run at once.
    """

    wait_time = between(0.05, 0.25)

    def on_start(self):
        self.api_key = os.environ.get("LOAD_TEST_API_KEY", "")
        self.tenant_id = os.environ.get("LOAD_TEST_TENANT", "load-test-tenant")
        self.conversation_id = f"locust-{uuid.uuid4()}"
        self.headers = {
            "X-API-Key": self.api_key,
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json",
        }

    @task(4)
    def conversation_round_trip(self):
        payload = {"conversation_id": self.conversation_id, "input": "Remember the code word: blue."}
        with self.client.post("/run", json=payload, headers=self.headers, name="run:first-turn", catch_response=True) as first:
            if first.status_code == 429:
                first.success()
                return
            if first.status_code != 200:
                first.failure(f"first turn returned {first.status_code}: {first.text[:200]}")
                return

        follow_up = {"conversation_id": self.conversation_id, "input": "What was the code word?"}
        with self.client.post("/run", json=follow_up, headers=self.headers, name="run:follow-up", catch_response=True) as second:
            if second.status_code == 429:
                second.success()
            elif second.status_code != 200:
                second.failure(f"follow-up returned {second.status_code}: {second.text[:200]}")
            elif "remembered" not in second.text and os.getenv("LOAD_TEST_REQUIRE_MEMORY", "true").lower() in {"1", "true", "yes"}:
                second.failure("follow-up did not show a remembered turn; check REDIS_URL and tenant configuration")

    @task(1)
    def rate_limit_probe(self):
        with self.client.post(
            "/run",
            json={"conversation_id": f"locust-probe-{uuid.uuid4()}", "input": "Rate-limit probe."},
            headers=self.headers,
            name="run:rate-limit-probe",
            catch_response=True,
        ) as response:
            if response.status_code in {200, 429}:
                response.success()
            else:
                response.failure(f"unexpected status {response.status_code}: {response.text[:200]}")

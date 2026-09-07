# Locust load testing

This load test targets an already deployed agent endpoint. It sends authenticated tenant traffic, performs two-turn conversations, and accepts `429` responses as expected when the configured rate limit is reached. The follow-up turn fails when `LOAD_TEST_REQUIRE_MEMORY=true` and the response does not show that the prior turn was retained; use this as a smoke signal for Redis-backed persistence in the reference mock provider.

## Install

```bash
python -m venv .venv-loadtest
source .venv-loadtest/bin/activate
python -m pip install -r loadtest/requirements.txt
```

## Generate and configure a tenant key

Generate a hash without committing the clear key:

```bash
export LOAD_TEST_API_KEY="a-long-random-test-key"
export AGENT_API_KEYS="{\"load-test-tenant\":\"$(python scripts/hash_api_key.py "$LOAD_TEST_API_KEY")\"}"
export LOAD_TEST_TENANT="load-test-tenant"
```

Configure the same `AGENT_API_KEYS` JSON mapping and `REQUIRE_API_KEY=true` on the deployed service. Keep the clear key only in the shell session or a secret manager.

## Run a local headless test

Start the service with Redis and the mock provider first:

```bash
docker compose up --build -d redis ollama agent
```

Then run 50 concurrent users, starting 5 users per second for two minutes:

```bash
locust -f loadtest/locustfile.py \
  --host http://127.0.0.1:8000 \
  --headless \
  --users 50 \
  --spawn-rate 5 \
  --run-time 2m \
  --csv loadtest/results
```

For a deployed host, replace `--host` with the service URL and use a restricted load-test key. Do not run high-concurrency traffic against production without an approved load window and provider spend limits.

## What to inspect

The Locust report separates first-turn, follow-up, and rate-limit-probe requests. The expected rate-limit behavior is a rising count of `429` responses after the tenant exceeds `RATE_LIMIT_REQUESTS_PER_MINUTE`, with a `Retry-After` response header. The follow-up requests should remain successful and should preserve conversation continuity when `REDIS_URL` points to the shared store. Run the test against at least two application instances or a scale-out deployment when validating multi-instance behavior; a single instance can pass even if the fallback memory store is being used.

Load tests measure the deployed system, not just the model. Record the image digest, provider/model, region, Redis tier, concurrency, spawn rate, request mix, test duration, p50/p95/p99 latency, error rate, 429 rate, and provider token usage. Keep Locust CSV output out of Git unless it is a deliberately reviewed benchmark artifact.

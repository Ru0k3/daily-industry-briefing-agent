# Monitoring setup

The FastAPI service exposes Prometheus metrics at `/metrics`. The instrumentation records request count, request latency, errors by provider and error type, and provider-reported input/output tokens. The included `prometheus.yml` scrapes the service named `agent` on the Docker Compose network, and `grafana-dashboard.json` is an importable Grafana dashboard.

## Local setup

Start the stack with the monitoring profile:

```bash
docker compose --profile monitoring up --build
```

Prometheus is available at `http://localhost:9090` and Grafana at `http://localhost:3000`. The default Grafana login is `admin` / `admin` only for this local example; set a real password and use a managed secret in any shared environment.

In Grafana, add Prometheus as a data source with URL `http://prometheus:9090`, then import `grafana-dashboard.json`. The dashboard includes request rate, error rate, P95 latency, and provider-reported token rate. For Cloud Run, replace the local scrape configuration with Google Cloud Managed Service for Prometheus or export OpenTelemetry metrics to the selected observability backend; do not expose `/metrics` publicly without authentication or network controls.

## Alerting suggestions

Set alerts for a sustained error ratio above the service’s normal baseline, P95 latency above the user-facing SLO, and an absence of successful requests when traffic is expected. Choose thresholds from measured production behavior rather than copying generic values. Include provider, model, revision, region, and deployment version in logs and traces, but never log API keys or full user prompts by default.

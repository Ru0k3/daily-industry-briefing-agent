# Provider-Neutral Agent Launch

A reusable skill for designing, building, evaluating, deploying, and iterating AI agents without locking the workflow to Anthropic, OpenAI, Google, local models, or another specific provider.

## What it does

The skill guides an agent-building session through a practical sequence:

1. Understand the job.
2. Scope a useful v0.
3. Choose a model provider and adapter.
4. Choose the agent runtime.
5. Select application hosting and supporting infrastructure.
6. Build a versionable launch kit.
7. Run evaluations and regression tests.
8. Iterate, add approval gates, and schedule recurring work.
9. Close out with a clear deployment and next-directions recap.

The workflow keeps the model provider, runtime, application host, database, secrets, and scheduler as separate decisions. It supports hosted APIs, provider SDKs, direct API loops, local models, PaaS, VPS, serverless, containers, static frontends, managed databases, queues, and scheduled jobs.

## Installation

Copy the `provider-neutral-agent-launch` directory into your agent platform’s skills directory, or use the platform’s skill installation flow. The required file is `SKILL.md`; the `references/` directory contains supporting material loaded as needed.

## Provider support

The core skill is provider-neutral. To add a model provider, implement the adapter boundary described in `references/provider-adapters.md`, keep the provider endpoint and model in configuration, translate tool calls and results into the neutral contract, and rerun the evaluation set. Gemini can use the official Google Gen AI SDK or API. Open-source models can use a documented serving layer such as vLLM or Ollama, including an OpenAI-compatible endpoint when appropriate; compatibility must be tested for the exact model and server pair.

## Render example

`examples/render-agent/` contains a small FastAPI service, `render.yaml`, and dependency manifest. Create a Render web service from this repository, set `PROVIDER=mock` for a safe smoke test, or configure `PROVIDER=gemini` with `GEMINI_API_KEY`. For a local or self-hosted OpenAI-compatible model, set `PROVIDER=openai_compatible`, `BASE_URL`, `MODEL`, and the optional `OPENAI_COMPATIBLE_API_KEY`. The service exposes `GET /health` and `POST /run`.

The GitHub Actions workflow in `.github/workflows/test.yml` runs the tests on pushes and pull requests. Render’s `autoDeploy: true` setting can deploy changes after the repository’s checks pass; configure branch protection if production deployments must require passing checks.

## Included references

- `references/hosting-options.md` contains the supplied hosting catalog. Prices, quotas, and free-tier behavior must be rechecked against official provider documentation before production use.
- `references/provider-adapters.md` defines the neutral adapter boundary and capability checklist for changing model providers.

## Design principles

The skill favors the smallest reliable deployment, explicit evaluation criteria, replaceable provider adapters, safe secret handling, dry runs for external actions, and a numbered `NEXT-DIRECTIONS.md` plan for future versions.

## License

Apache-2.0. See `LICENSE`.

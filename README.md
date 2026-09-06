# Provider-Neutral Agent Launch

A provider-neutral skill and reference service for designing, testing, deploying, and iterating AI agents. The workflow separates the **model provider**, **agent runtime**, **application host**, **database**, **secrets**, and **scheduler**, so the same agent design can move between Gemini, OpenAI-compatible services, Ollama, vLLM, Anthropic, or another provider.

> The included service is a small reference implementation, not a complete production agent platform. Add authentication, rate limiting, persistent state, approval workflows, observability, and a durable job system before exposing it to untrusted users.

## Repository layout

```text
provider-neutral-agent-launch/
├── provider-neutral-agent-launch/
│   ├── SKILL.md
│   └── references/
│       ├── hosting-options.md
│       └── provider-adapters.md
├── examples/render-agent/
│   ├── app.py
│   ├── render.yaml
│   └── requirements.txt
├── tests/
│   ├── test_skill_and_example.py
│   ├── test_llm_abstraction.py
│   └── test-output.txt
└── .github/workflows/test.yml
```

## How the abstraction works

The example exposes one application boundary, `run_agent(user_input, system)`. The selected provider is configuration rather than application architecture:

| `PROVIDER` value | Runtime | Required configuration |
|---|---|---|
| `mock` | Deterministic local smoke test | None |
| `gemini` | Google Gemini Developer API | `GEMINI_API_KEY`, optional `MODEL` |
| `claude` | Anthropic Claude Messages API | `ANTHROPIC_API_KEY`, optional `MODEL` and `MAX_TOKENS` |
| `ollama` | Native Ollama `/api/chat` endpoint | `BASE_URL`, `MODEL`; default is local Ollama |
| `openai_compatible` | OpenAI-compatible `/v1/chat/completions` endpoint | `BASE_URL`, `MODEL`, optional API key |

The adapter returns plain text to the API layer. A larger implementation should return a structured `AgentResult` containing output, tool events, usage, warnings, and resumable state, as described in `provider-neutral-agent-launch/references/provider-adapters.md`.

## Local setup

Use Python 3.11 or newer. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r examples/render-agent/requirements.txt
python -m pip install pytest
pytest -q
```

Start the service in mock mode:

```bash
export PROVIDER=mock
uvicorn app:app --app-dir examples/render-agent --host 127.0.0.1 --port 8000
```

Check it:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/run \
  -H 'Content-Type: application/json' \
  -d '{"input":"Summarize this task","system":"Be concise."}'
```

Never commit a real API key. Use a local `.env` only if it is ignored by Git, and use the host’s secret manager for deployed services.

## Google Gemini configuration

Google’s official Python SDK is `google-genai`; its documentation supports both the Gemini Developer API and the enterprise API. The SDK can read `GEMINI_API_KEY` or `GOOGLE_API_KEY`, although this example uses `GEMINI_API_KEY` explicitly. [1]

For the included reference service, configure:

```bash
export PROVIDER=gemini
export GEMINI_API_KEY='your-key'
export MODEL='gemini-2.5-flash'
uvicorn app:app --app-dir examples/render-agent --host 127.0.0.1 --port 8000
```

The example uses the Gemini `generateContent` REST shape. For a production adapter, prefer the current official SDK or current Gemini API documentation, then add translation for function declarations, function-call results, structured outputs, streaming, files, multimodal inputs, and safety settings. Gemini function calling is a four-part loop: define a function, request a model decision, execute the function in your application, and send the function result back to the model. [2]

Install the SDK when implementing a native Python adapter:

```bash
python -m pip install google-genai
```

Keep provider-specific code in `gemini_adapter.py` and expose the same neutral method as the other adapters. Test request construction with mocked transport, then run a small live smoke test with a low-risk prompt and a restricted key.

## Anthropic Claude configuration

For Claude, set `PROVIDER=claude`, `ANTHROPIC_API_KEY`, and a supported Claude model name. The reference adapter calls the Messages API, sends the system instruction separately, and normalizes text content blocks into the neutral response boundary:

```bash
export PROVIDER=claude
export ANTHROPIC_API_KEY='your-key'
export MODEL='claude-sonnet-4-5'
export MAX_TOKENS=512
uvicorn app:app --app-dir examples/render-agent --host 127.0.0.1 --port 8000
```

Keep the key in the host secret manager. For tools, preserve Claude content blocks and implement the `tool_use` to `tool_result` loop described in `provider-neutral-agent-launch/references/structured-output-and-tools.md`. Verify the current Claude model identifier and API capabilities in the official platform documentation before deployment.

## Ollama and local open-source models

Ollama serves its native API at `http://localhost:11434/api` by default and also provides official Python and JavaScript libraries. [3] The native chat endpoint is `POST /api/chat`; set `stream` to `false` when the application expects one JSON response. [4]

Install Ollama, pull a model, and run the example locally:

```bash
ollama serve
ollama pull qwen3
export PROVIDER=ollama
export BASE_URL='http://localhost:11434/api'
export MODEL='qwen3'
uvicorn app:app --app-dir examples/render-agent --host 127.0.0.1 --port 8000
```

The example also supports an OpenAI-compatible serving layer. Use that mode for an Ollama-compatible `/v1` endpoint, vLLM, or another server only after confirming the exact model and server support tool calling, structured output, streaming, authentication, and concurrency:

```bash
export PROVIDER=openai_compatible
export BASE_URL='http://localhost:11434/v1'
export MODEL='qwen3'
export OPENAI_COMPATIBLE_API_KEY='optional-key'
```

For a remote Ollama host, do not expose port `11434` directly to the public internet. Place it behind a private network or authenticated reverse proxy, restrict ingress to the application host, and use TLS. Ensure the machine has enough RAM or GPU memory for the selected model. Record the model tag, quantization, context length, license, and serving version in the build sheet.

## Render deployment

The checked-in `examples/render-agent/render.yaml` is a Render Blueprint for a Python web service. Render’s FastAPI guide uses a Python service with `pip install -r requirements.txt` and `uvicorn ... --host 0.0.0.0 --port $PORT`. [5]

1. Push this repository to GitHub.
2. In Render, create a new Blueprint or Web Service from the repository.
3. Review the service name, root directory, build command, start command, and health path.
4. Keep `PROVIDER=mock` for the first deployment smoke test.
5. Add `GEMINI_API_KEY` as a Render secret and change `PROVIDER=gemini` only after the health check passes.
6. For Ollama, use a separately hosted Ollama machine reachable through a private or authenticated network. Do not assume a small web-service instance can run a useful local model.
7. Use the `/health` endpoint for the host health check and `/run` for a basic request.

Render is a good fit for a lightweight request/response API. It is not automatically the right place for GPU inference, durable queues, or long-running agent sessions. Add a database and queue when sessions or background work must survive restarts.

## Other deployment choices

Choose the host according to the runtime rather than popularity:

| Host type | Best fit | Important caveat |
|---|---|---|
| Render, Koyeb, Railway, Northflank | Git-based Python/Node web services and small workers | Confirm sleep behavior, quotas, persistent storage, and pricing for the selected plan. |
| Fly.io | Containerized services needing regional placement | You manage more infrastructure and must design persistence and recovery. |
| Google Cloud Run | Stateless containers and event-driven APIs | Scale-to-zero can add cold starts; use a separate database and queue. |
| Oracle Cloud, Hetzner, DigitalOcean, Linode, Vultr | Full Linux control, self-hosted Ollama, workers, Docker, or Coolify | You own patching, firewalls, backups, monitoring, and incident recovery. |
| Coolify, CapRover, Dokku on a VPS | A low-cost self-hosted PaaS | The PaaS is free, but the VPS and operations are not. |
| Vercel, Netlify, Cloudflare Pages/Workers | Static frontends and short request-based APIs | Do not place long-running workers, private model keys, or stateful inference here without a suitable backend. |
| GitHub Actions | Tests, CI/CD, and low-frequency scheduled jobs | It is not a 24/7 agent host; jobs have time and quota limits. |

For an agent that needs an always-on worker, WebSockets, a queue consumer, or local Ollama, choose an always-on container or VPS. For a scheduled low-frequency agent, a scheduled job is usually cheaper than keeping a process alive. For GPU inference, choose a GPU-capable host or use a hosted model API.

## Provider contract verification

Run the offline provider-matrix script to verify structured-output schema placement and tool-call parsing across Claude, Gemini, native Ollama, and OpenAI-compatible endpoints:

```bash
python scripts/verify_provider_contracts.py
```

The script makes no network requests. It uses representative provider wire formats and exits nonzero if a provider loses the neutral schema or tool-call contract. Live integration tests should remain separately gated because they require credentials, incur provider costs, and can vary with model versions.

## Google Cloud Run deployment

A complete container deployment example is available in `deploy/cloud-run/`. It covers Artifact Registry, Cloud Build, Secret Manager, authenticated Cloud Run deployment, health checks, and provider-specific configuration. Start with `deploy/cloud-run/README.md` and substitute your own project, region, service account, image, and secret names.

## Docker and Docker Compose

Build and run the reference service in a container:

```bash
docker build -t provider-neutral-agent .
docker run --rm -p 8000:8000 \
  -e PROVIDER=mock \
  provider-neutral-agent
```

The included `docker-compose.yml` starts the agent and an Ollama service on a private Compose network:

```bash
docker compose up --build
curl http://127.0.0.1:8000/health
```

The default Compose configuration uses `PROVIDER=ollama`, `MODEL=qwen3`, and `BASE_URL=http://ollama:11434/api`. Pull a model inside the Ollama container before sending requests:

```bash
docker compose exec ollama ollama pull qwen3
```

To use Claude or Gemini with Compose, set `PROVIDER`, `MODEL`, and the relevant secret in a local `.env` file or through your deployment secret manager. Do not commit `.env`. The Ollama container is suitable for development and small self-hosted deployments; use a GPU-capable host and explicit resource limits for larger models.

## Structured output and tool calling

See `provider-neutral-agent-launch/references/structured-output-and-tools.md` for the cross-provider contract, provider mapping, request patterns, validation rules, tool execution loop, and safety checklist. Use structured output for final machine-readable results; use tool calling when the model needs the application to execute an operation. Always validate arguments and require authorization before side effects.

## CI/CD

`.github/workflows/test.yml` runs on pushes and pull requests to `main`. It installs the example dependencies and runs `pytest -q`. A typical deployment policy is:

1. Run tests on every pull request.
2. Require the `test` check before merging to `main`.
3. Let the hosting platform auto-deploy only from `main`.
4. Store API keys and deployment tokens as repository or host secrets.
5. Use a separate staging service for live-provider smoke tests.
6. Require manual approval before enabling external write actions.

The workflow intentionally does not call Gemini, Ollama, or another paid provider. Provider tests use mocked HTTP responses so CI remains deterministic and does not expose credentials.

## Testing strategy

Run the unit suite with:

```bash
pytest -q
```

The abstraction tests cover mock behavior, Gemini request construction and response parsing, native Ollama request construction, OpenAI-compatible request construction and authorization, missing credentials, unsupported providers, and upstream timeouts. The latest output is stored in `tests/test-output.txt`.

Add live integration tests separately and gate them behind an explicit environment variable such as `RUN_LIVE_PROVIDER_TESTS=1`. Never make paid provider calls part of the default pull-request suite.

## Security and production checklist

Before production, add authentication and authorization, request size limits, rate limiting, structured input validation, output filtering, audit logging, approval gates for side effects, secret-manager integration, retries with backoff, idempotency keys, durable session storage, queue-based background execution, metrics, traces, alerting, backups, and a rollback procedure. Review each model’s data-retention and license terms. Treat prompts, retrieved documents, tool outputs, and model responses as untrusted data.

## References

[1]: https://googleapis.github.io/python-genai/ — *Google Gen AI Python SDK documentation*

[2]: https://ai.google.dev/gemini-api/docs/function-calling — *Google AI for Developers, Function calling with the Gemini API*

[3]: https://docs.ollama.com/api/introduction — *Ollama API introduction*

[4]: https://docs.ollama.com/api/chat — *Ollama API, Generate a chat message*

[5]: https://render.com/docs/deploy-fastapi — *Render, Deploy a FastAPI App*

## License

Apache-2.0. See `LICENSE`.

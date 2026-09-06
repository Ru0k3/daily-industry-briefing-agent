# Provider Adapter Reference

Use this reference when the user has selected, or is comparing, model providers. Treat provider names and capabilities as configuration, not as assumptions in the core skill. Verify live official documentation before implementation because APIs, models, pricing, and product availability change.

## Adapter interface

Expose a small application boundary such as:

```text
run_agent(input, context) -> AgentResult
register_tool(tool_definition, handler)
resume_session(session_id, input) -> AgentResult
request_approval(action, details) -> ApprovalResult
```

`AgentResult` should carry the final response, structured output when requested, tool events, usage metadata, warnings, and a resumable state reference where supported. The adapter should translate provider-specific events and errors into this neutral shape.

## Capability matrix

Record these fields in `build-sheet.json` for every candidate provider:

| Capability | Questions to answer |
| --- | --- |
| Model access | Which model endpoint and model version are used? Is the endpoint hosted, self-hosted, or hybrid? |
| Tool calling | Are function tools, MCP, browser/computer tools, code execution, or custom tools available? |
| Output control | Are JSON schema, structured outputs, citations, or typed results supported? |
| Context and state | What are the context limits? Is conversation state stored by the provider, by the SDK, or by the application? |
| Streaming | Are token, tool, and approval events streamable? |
| Long-running work | Are background jobs, resumable runs, retries, or durable sessions supported? |
| Execution environment | Who runs commands and files? Where are credentials relative to generated code? |
| Safety | Are input/output guardrails, approvals, audit logs, and policy controls available? |
| Data and privacy | What retention, residency, training-use, and deletion controls apply? |
| Operations | What are rate limits, timeouts, quotas, observability, and incident-recovery options? |
| Portability | How difficult is it to swap the model while keeping tools and application logic? |

## Provider examples

### Google Gemini

Implement Gemini behind the same neutral adapter. The official `google-genai` Python SDK supports the Gemini Developer API and the Gemini enterprise API; configure the client with `GEMINI_API_KEY` for the Developer API or the documented Google Cloud project and location variables for enterprise use. [1]

Map Gemini function declarations and function-call results into the neutral tool contract. The function-calling loop is: define declarations, send them with the model request, execute the selected function in the application, and send the result back for the final response. [2] Validate structured responses at the application boundary, and record the selected model, API version, region, safety settings, files, multimodal inputs, grounding, and quota assumptions in the build sheet. Keep the Google API key in the deployment secret manager.

A minimal Python configuration is:

```python
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
response = client.models.generate_content(
    model=os.getenv("MODEL", "gemini-2.5-flash"),
    contents=user_input,
)
text = response.text
```

Use the current Gemini documentation when adding tools, streaming, structured output, or the Interactions API; do not assume that a request shape from another provider is interchangeable.

### Open-source and self-hosted models

For open-source models, separate the inference server from the agent application. Common choices include Ollama, vLLM, or another documented serving layer, but verify the exact model/server pair for tool calling, structured output, streaming, batching, GPU support, and authentication. Point the adapter at a configurable `BASE_URL`, keep model identifiers in configuration, and test the real response schema rather than assuming that OpenAI-compatible means behavior-compatible.

Ollama’s native API is served at `http://localhost:11434/api` by default, and its chat endpoint is `POST /api/chat`. Set `stream: false` when the application expects one JSON response. [3] Ollama also has official Python and JavaScript libraries. [4] A native request has this shape:

```json
{
  "model": "qwen3",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}
```

For tool use, pass the documented `tools` array and implement the same execute-and-return loop used by other providers. For structured output, validate the returned JSON against the application schema. Do not expose an unauthenticated Ollama port to the public internet; use a private network or authenticated TLS proxy.

For production, run the inference server on a suitable GPU or CPU host, restrict network access, set request timeouts and concurrency limits, monitor memory and latency, pin model tags and serving versions, and document model-license obligations. If the user does not need local inference, prefer a hosted provider API to reduce operations burden.

## Common implementation patterns

### Hosted managed-agent runtime

Use this when the provider supplies a durable agent runtime, sessions, tools, sandbox, and deployment controls. Confirm what is included and what remains in the user’s infrastructure. Do not assume that a hosted model API includes a hosted worker, scheduler, database, or frontend.

### Provider SDK in the user’s server

Use this when the provider supplies an agent loop or orchestration SDK but the application owns deployment, secrets, tools, state, approvals, and scheduling. This is often the most portable production pattern.

### Direct model API loop

Use this when the application must own every loop, branch, retry, state, and tool call. Keep the provider call behind an adapter and persist run events so the workflow can be inspected and resumed.

### Local or self-hosted model

Use this when privacy, offline operation, or cost control dominates. Confirm hardware, model licensing, inference latency, tool-calling quality, context size, concurrency, observability, and update procedures. The host must usually run the inference server as well as the agent application.

## Migration checklist

When changing providers, preserve the neutral agent contract and update only the adapter, model configuration, prompt formatting where necessary, tool-call parsing, structured-output validation, streaming translation, token accounting, safety controls, and evaluation baselines. Rerun the full evaluation set because equivalent model names do not imply equivalent behavior.

Never copy a provider-specific credential into source code. Use a provider-labeled environment variable in `.env.example`, document its acquisition location, and store the real value in the selected host’s secret manager.

## References

[1]: https://googleapis.github.io/python-genai/ — Google Gen AI Python SDK documentation
[2]: https://ai.google.dev/gemini-api/docs/function-calling — Google Gemini function-calling documentation
[3]: https://docs.ollama.com/api/introduction — Ollama API introduction
[4]: https://docs.ollama.com/api/chat — Ollama chat API documentation

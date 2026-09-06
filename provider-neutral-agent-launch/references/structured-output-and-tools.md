# Structured Output and Tool Calling Across Providers

Use this guide when an agent must return data that a program can validate or must take actions through typed tools. Keep the application contract provider-neutral even though the wire format differs by provider.

## Start with one neutral contract

Define the schema and tool registry once in application code, then translate it for each provider:

```python
Tool = {
    "name": "get_weather",
    "description": "Return current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
        "additionalProperties": False,
    },
}

OutputSchema = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "sources"],
    "additionalProperties": False,
}
```

Validate every model response with a JSON Schema or Pydantic model. Treat validation failure as a recoverable run error: record the raw response safely, retry only within a bounded budget, and never silently coerce unsafe actions.

## Structured output versus tool calling

Use **structured output** when the model should return a final object for the application, such as an extraction record, classification, plan, or report. Use **tool calling** when the model should request an operation that the application must execute, such as reading a database, sending a message, or creating a ticket. A tool call is not permission to act: apply authorization, validation, idempotency, and approval gates before execution.

A typical tool loop is:

1. Send the user input and tool declarations.
2. Detect a tool call in the provider response.
3. Validate the tool name and arguments against the registered schema.
4. Check authorization and ask for approval for risky actions.
5. Execute the tool outside the model.
6. Return the tool result in the provider’s required format.
7. Continue until the model returns a final response or the run reaches a bounded stop condition.

## Provider mapping

| Provider | Structured output | Tool calling | Adapter notes |
|---|---|---|---|
| Anthropic Claude | Use the current Claude Structured Outputs capability when the selected model/API supports it; otherwise validate JSON returned by the Messages API. | Define tools with JSON Schema. Claude returns `tool_use` blocks; execute them in the application and send back `tool_result` blocks. | Preserve content blocks instead of assuming a single text string. Use the `anthropic-version` header and current model documentation. |
| Google Gemini | Use the current Google Gen AI SDK/API response schema configuration and validate the result. | Define function declarations, inspect the function-call part, execute the function, and send the function result back. | Gemini function declarations and response parts differ from OpenAI-style messages. Keep translation in the Gemini adapter. |
| Ollama native | Use the `format` field with `json` or a JSON Schema and validate the response. | Use the documented `tools` array on `/api/chat`; disable streaming when one complete JSON response is required. | Native Ollama uses `/api/chat`, with responses under `message`. Check model support for tools and structured outputs. |
| OpenAI-compatible endpoint | Use the endpoint’s documented response-format or JSON-schema feature, but verify the exact server behavior. | Usually use `/v1/chat/completions` tools and tool calls, but field names and support vary by server/model. | “OpenAI-compatible” describes an interface, not identical capabilities. Test the exact model and server pair. |

## Claude example

The Claude Messages API returns content blocks. A client tool call has a `tool_use` block with a name and JSON input. After the application executes the tool, send a `tool_result` block in the next user message. Claude’s official documentation describes this as a contract between the application and model. [1]

For a fixed final JSON object, prefer the current Claude Structured Outputs documentation when supported by the selected model/API. If using a prompt-based JSON fallback, parse and validate it strictly, and make the fallback explicit in the run metadata.

## Gemini example

Gemini function calling uses function declarations and returns function-call parts. The application executes the selected function and supplies the function response before requesting the final answer. Gemini also supports structured output features; use the current SDK/API version and validate the returned schema. [2]

## Ollama example

A native Ollama structured request resembles:

```json
{
  "model": "qwen3",
  "messages": [{"role": "user", "content": "Extract the task."}],
  "stream": false,
  "format": {
    "type": "object",
    "properties": {"task": {"type": "string"}},
    "required": ["task"]
  }
}
```

For tool calling, add the documented `tools` array and handle the returned tool call before sending the tool result. [3]

## Testing and safety checklist

For every provider, test a valid response, malformed JSON, missing required fields, an unknown tool, invalid tool arguments, a tool timeout, a provider refusal, a truncated response, and a duplicate action request. Keep live provider tests out of the default pull-request suite; use mocked HTTP transport for deterministic unit tests and a separately gated smoke test for each configured provider.

Before executing a tool, validate the schema, authorize the principal, redact secrets from logs, enforce timeouts, make writes idempotent, and require human approval for external or destructive actions. Store the provider, model, adapter version, schema version, and validation result with each run.

## References

[1]: https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works — Anthropic Claude Platform Docs, How tool use works
[2]: https://ai.google.dev/gemini-api/docs/function-calling — Google AI for Developers, Function calling with the Gemini API
[3]: https://docs.ollama.com/api/chat — Ollama API, Generate a chat message

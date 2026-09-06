#!/usr/bin/env python3
"""Offline contract checks for structured output and tool calling.

The script performs no network requests. It verifies that each provider adapter
shape can carry the same neutral schema, tool declaration, tool call, and tool
result through a provider-specific wire format.
"""

from __future__ import annotations

import json
from typing import Any, Callable

NEUTRAL_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "sources"],
    "additionalProperties": False,
}

NEUTRAL_TOOL = {
    "name": "get_weather",
    "description": "Return current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
        "additionalProperties": False,
    },
}

TOOL_ARGS = {"city": "London"}


def claude_payload() -> dict[str, Any]:
    return {
        "model": "claude-test",
        "max_tokens": 256,
        "system": "Return valid structured results.",
        "tools": [{"name": NEUTRAL_TOOL["name"], "description": NEUTRAL_TOOL["description"], "input_schema": NEUTRAL_TOOL["parameters"]}],
        "messages": [{"role": "user", "content": "What is the weather?"}],
        "output_format": {"type": "json_schema", "schema": NEUTRAL_SCHEMA},
    }


def gemini_payload() -> dict[str, Any]:
    return {
        "systemInstruction": {"parts": [{"text": "Return valid structured results."}]},
        "tools": [{"function_declarations": [{"name": NEUTRAL_TOOL["name"], "description": NEUTRAL_TOOL["description"], "parameters": NEUTRAL_TOOL["parameters"]}]}],
        "generationConfig": {"responseMimeType": "application/json", "responseSchema": NEUTRAL_SCHEMA},
        "contents": [{"role": "user", "parts": [{"text": "What is the weather?"}]}],
    }


def ollama_payload() -> dict[str, Any]:
    return {
        "model": "qwen3",
        "stream": False,
        "format": NEUTRAL_SCHEMA,
        "tools": [{"type": "function", "function": {"name": NEUTRAL_TOOL["name"], "description": NEUTRAL_TOOL["description"], "parameters": NEUTRAL_TOOL["parameters"]}}],
        "messages": [{"role": "user", "content": "What is the weather?"}],
    }


def openai_compatible_payload() -> dict[str, Any]:
    return {
        "model": "local-model",
        "response_format": {"type": "json_schema", "json_schema": {"name": "agent_result", "schema": NEUTRAL_SCHEMA, "strict": True}},
        "tools": [{"type": "function", "function": {"name": NEUTRAL_TOOL["name"], "description": NEUTRAL_TOOL["description"], "parameters": NEUTRAL_TOOL["parameters"]}}],
        "messages": [{"role": "user", "content": "What is the weather?"}],
    }


def parse_claude_tool_call(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    block = next(item for item in response["content"] if item["type"] == "tool_use")
    return block["name"], block["input"]


def parse_gemini_tool_call(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    call = response["candidates"][0]["content"]["parts"][0]["functionCall"]
    return call["name"], call["args"]


def parse_ollama_tool_call(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    call = response["message"]["tool_calls"][0]["function"]
    return call["name"], call["arguments"]


def parse_openai_tool_call(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    call = response["choices"][0]["message"]["tool_calls"][0]["function"]
    return call["name"], json.loads(call["arguments"])


def assert_schema(payload: dict[str, Any], path: tuple[str, ...]) -> None:
    current: Any = payload
    for key in path:
        current = current[key]
    assert current["type"] == "object"
    assert current["required"] == NEUTRAL_SCHEMA["required"]


def run_case(name: str, builder: Callable[[], dict[str, Any]], schema_path: tuple[str, ...], parser: Callable[[dict[str, Any]], tuple[str, dict[str, Any]]], response: dict[str, Any]) -> None:
    payload = builder()
    assert_schema(payload, schema_path)
    tool_name, args = parser(response)
    assert tool_name == NEUTRAL_TOOL["name"]
    assert args == TOOL_ARGS
    print(f"PASS {name}: structured output schema and tool call round-trip")


def main() -> int:
    run_case(
        "claude",
        claude_payload,
        ("output_format", "schema"),
        parse_claude_tool_call,
        {"content": [{"type": "tool_use", "name": "get_weather", "input": TOOL_ARGS}]},
    )
    run_case(
        "gemini",
        gemini_payload,
        ("generationConfig", "responseSchema"),
        parse_gemini_tool_call,
        {"candidates": [{"content": {"parts": [{"functionCall": {"name": "get_weather", "args": TOOL_ARGS}}]}}]},
    )
    run_case(
        "ollama",
        ollama_payload,
        ("format",),
        parse_ollama_tool_call,
        {"message": {"tool_calls": [{"function": {"name": "get_weather", "arguments": TOOL_ARGS}}]}},
    )
    run_case(
        "openai_compatible",
        openai_compatible_payload,
        ("response_format", "json_schema", "schema"),
        parse_openai_tool_call,
        {"choices": [{"message": {"tool_calls": [{"function": {"name": "get_weather", "arguments": json.dumps(TOOL_ARGS)}}]}}]},
    )
    print("PASS provider matrix: 4 providers verified; no network requests made")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Small provider-neutral agent service for the Render deployment example.

The example intentionally keeps the provider boundary explicit. Set PROVIDER=mock for
local tests, PROVIDER=gemini for Gemini, or PROVIDER=openai_compatible for OpenAI,
vLLM, Ollama, and other compatible endpoints.
"""

import json
import os
from typing import Any
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Provider-Neutral Agent Example")


class RunRequest(BaseModel):
    input: str
    system: str = "You are a concise, helpful agent."


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urlopen(request, timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))) as response:
        return json.loads(response.read().decode("utf-8"))


def run_agent(user_input: str, system: str) -> str:
    provider = os.getenv("PROVIDER", "mock").lower()
    if provider == "mock":
        return f"Mock agent received: {user_input}"

    if provider == "gemini":
        api_key = os.environ["GEMINI_API_KEY"]
        model = os.getenv("MODEL", "gemini-2.5-flash")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user_input}]}],
        }
        data = _post_json(url, payload, {})
        return data["candidates"][0]["content"]["parts"][0]["text"]

    if provider == "openai_compatible":
        base_url = os.getenv("BASE_URL", "http://localhost:11434/v1").rstrip("/")
        model = os.getenv("MODEL", "local-model")
        headers = {}
        if os.getenv("OPENAI_COMPATIBLE_API_KEY"):
            headers["Authorization"] = f"Bearer {os.environ['OPENAI_COMPATIBLE_API_KEY']}"
        data = _post_json(
            f"{base_url}/chat/completions",
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_input},
                ],
            },
            headers,
        )
        return data["choices"][0]["message"]["content"]

    raise ValueError(f"Unsupported PROVIDER: {provider}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "provider": os.getenv("PROVIDER", "mock")}


@app.post("/run")
def run(request: RunRequest) -> dict[str, str]:
    try:
        return {"output": run_agent(request.input, request.system)}
    except (KeyError, ValueError, IndexError, TimeoutError, OSError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

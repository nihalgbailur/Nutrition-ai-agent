from __future__ import annotations

import os
from functools import lru_cache

import httpx

DEFAULT_OLLAMA_BASE = "http://127.0.0.1:11434"


def ollama_base_url() -> str:
    return os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_BASE).rstrip("/")


@lru_cache(maxsize=1)
def list_ollama_models() -> list[str]:
    """Return installed Ollama model names, or empty if daemon unreachable."""
    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(f"{ollama_base_url()}/api/tags")
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []


def ollama_is_running() -> bool:
    return bool(list_ollama_models())


def resolve_ollama_litellm_model() -> str | None:
    """
    LiteLLM format: ollama/<model_name>
    Uses OLLAMA_MODEL env, else first model from `ollama list`.
    """
    if not ollama_is_running():
        return None
    explicit = os.getenv("OLLAMA_MODEL", "").strip()
    if explicit:
        name = explicit if not explicit.startswith("ollama/") else explicit.split("/", 1)[1]
        return f"ollama/{name}"
    models = list_ollama_models()
    if models:
        return f"ollama/{models[0]}"
    return None


def ollama_display_name() -> str:
    model = resolve_ollama_litellm_model()
    if not model:
        return ""
    return model.split("/", 1)[-1]
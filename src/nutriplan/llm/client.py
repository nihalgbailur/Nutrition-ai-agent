from __future__ import annotations

import json
import os
from collections.abc import Iterator
from typing import TypeVar

from pydantic import BaseModel

from nutriplan.config import (
    AGENT_MAX_TOKENS,
    CHAT_MAX_TOKENS,
    CHAT_SAFETY_APPENDIX,
    CHAT_TIMEOUT_SECONDS,
    DEFAULT_LLM_MODEL,
    SAFETY_SYSTEM_APPENDIX,
)
from nutriplan.llm.ollama_util import ollama_base_url, ollama_display_name, resolve_ollama_litellm_model

T = TypeVar("T", bound=BaseModel)


def resolve_llm_model() -> str | None:
    """Active LiteLLM model id, or None if only fallback templates are available."""
    if os.getenv("LITELLM_MODEL"):
        return os.getenv("LITELLM_MODEL", "")
    if os.getenv("XAI_API_KEY"):
        return DEFAULT_LLM_MODEL
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_model = resolve_ollama_litellm_model()
    if ollama_model:
        return ollama_model
    return None


def llm_available() -> bool:
    return resolve_llm_model() is not None


def llm_provider_label() -> str:
    if os.getenv("LITELLM_MODEL"):
        return f"LiteLLM ({os.getenv('LITELLM_MODEL')})"
    if os.getenv("XAI_API_KEY"):
        return f"Grok ({os.getenv('LITELLM_MODEL', DEFAULT_LLM_MODEL)})"
    if os.getenv("OPENAI_API_KEY"):
        return "OpenAI"
    ollama = resolve_ollama_litellm_model()
    if ollama:
        return f"Ollama ({ollama_display_name()})"
    return "Fallback templates"


def is_ollama_backend() -> bool:
    model = resolve_llm_model() or ""
    return model.startswith("ollama/")


def _build_kwargs(
    system: str,
    user: str,
    model: str | None,
    *,
    mode: str = "agent",
    stream: bool = False,
) -> dict:
    model = model or resolve_llm_model()
    if not model:
        raise RuntimeError("No LLM configured")

    safety = CHAT_SAFETY_APPENDIX if mode == "chat" else SAFETY_SYSTEM_APPENDIX
    max_tokens = int(
        os.getenv(
            "CHAT_MAX_TOKENS" if mode == "chat" else "AGENT_MAX_TOKENS",
            CHAT_MAX_TOKENS if mode == "chat" else AGENT_MAX_TOKENS,
        )
    )
    timeout = int(os.getenv("CHAT_TIMEOUT_SECONDS", CHAT_TIMEOUT_SECONDS))

    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system + "\n" + safety},
            {"role": "user", "content": user},
        ],
        "temperature": 0.5 if mode == "chat" else 0.7,
        "max_tokens": max_tokens,
        "timeout": timeout,
        "stream": stream,
    }
    if model.startswith("ollama/"):
        kwargs["api_base"] = ollama_base_url()
    return kwargs


def _completion(system: str, user: str, model: str | None = None, *, mode: str = "agent") -> str:
    import litellm

    kwargs = _build_kwargs(system, user, model, mode=mode, stream=False)
    response = litellm.completion(**kwargs)
    return response.choices[0].message.content or ""


def completion_stream(
    system: str, user: str, model: str | None = None, *, mode: str = "chat"
) -> Iterator[str]:
    import litellm

    kwargs = _build_kwargs(system, user, model, mode=mode, stream=True)
    response = litellm.completion(**kwargs)
    for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta


def parse_json_response(text: str) -> dict | list:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    return json.loads(text)


def generate_structured(
    system: str,
    user: str,
    model_cls: type[T],
    model: str | None = None,
) -> T | None:
    if not llm_available():
        return None
    try:
        # Compact schema hint for faster local models (full JSON schema is huge)
        hint = (
            '{"days":[{"day_label":"Monday","meals":[{"slot":"breakfast","recipe_name":"..."}]}],'
            '"variety_notes":"...","leftover_strategy":"..."}'
            if model_cls.__name__ == "WeeklyMealPlan"
            else '{"recipes":[{"name":"...","ingredients":[{"name":"...","quantity":"..."}],'
            '"steps":["..."],"prep_minutes":10,"cook_minutes":20,"servings":2,'
            '"nutrition":{"calories":300,"protein_g":10},"why_fits":"..."}]}'
        )
        prompt = user + f"\n\nReply with JSON only. Example shape:\n{hint}"
        raw = _completion(system, prompt, model=model, mode="agent")
        data = parse_json_response(raw)
        if isinstance(data, list):
            return None
        return model_cls.model_validate(data)
    except Exception:
        return None


def generate_json_list(system: str, user: str) -> list[dict]:
    if not llm_available():
        return []
    try:
        raw = _completion(
            system,
            user
            + '\n\nReply JSON only: {"recipes":[{"name":"...","ingredients":[{"name":"...","quantity":"..."}],'
            '"steps":["..."],"prep_minutes":10,"cook_minutes":20,"servings":2,'
            '"nutrition":{"calories":300,"protein_g":10},"why_fits":"...","kb_notes":""}]}',
            mode="agent",
        )
        data = parse_json_response(raw)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "recipes" in data:
            return data["recipes"]
        return []
    except Exception:
        return []
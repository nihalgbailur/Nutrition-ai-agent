from __future__ import annotations

import re
from collections.abc import Iterator

from nutriplan.config import DISCLAIMER
from nutriplan.knowledge.packaged_foods import get_kb
from nutriplan.llm.client import (
    _completion,
    completion_stream,
    is_ollama_backend,
    llm_available,
)
from nutriplan.models.schemas import PantryItem, UserProfile
from nutriplan.safety.guardrails import check_user_text

PACKAGED_RE = re.compile(
    r"\b(maggi|haldiram|parle|namkeen|packaged|snack|chips|noodle|kurkure|biscuit)\b",
    re.I,
)


def detect_chat_agent(message: str) -> str:
    lowered = message.lower()
    if PACKAGED_RE.search(lowered) or re.search(
        r"\b(pantry|inventory|ingredient|have at home|fridge)\b", lowered
    ):
        return "InventoryAgent"
    if re.search(r"\b(recipe|cook|make for dinner|breakfast idea)\b", lowered):
        return "RecipeCreator"
    if re.search(r"\b(week|weekly|meal plan|monday|schedule)\b", lowered):
        return "MealPlanner"
    if re.search(r"\b(shop|shopping list|buy|grocery)\b", lowered):
        return "ShoppingListOptimizer"
    if re.search(r"\b(profile|allerg|diet|vegetarian|preference)\b", lowered):
        return "ProfileManager"
    return "NutriPlan Assistant"


def _profile_summary(profile: UserProfile | None) -> str:
    if not profile:
        return "Guest, vegetarian, no allergies"
    allergies = ", ".join(profile.allergies) or "none"
    return (
        f"{profile.name}; {profile.diet_style.value}; goal={profile.health_goal.value}; "
        f"allergies={allergies}; max_cook={profile.max_cook_minutes}m"
    )


def _pantry_summary(pantry: list[PantryItem], limit: int = 12) -> str:
    if not pantry:
        return "empty"
    return ", ".join(p.name for p in pantry[:limit])


def _fallback_reply(message: str, agent: str, profile: UserProfile | None, pantry: list[PantryItem]) -> str:
    kb = get_kb()
    insights = kb.build_insights(pantry, profile) if profile else []
    kb_text = "\n\n".join(i.gentle_message for i in insights[:2]) if insights else ""

    pantry_list = _pantry_summary(pantry)
    name = profile.name if profile else "there"

    if agent == "InventoryAgent" and (insights or PACKAGED_RE.search(message)):
        return (
            f"Hi {name}! Pantry: {pantry_list}.\n\n"
            f"{kb_text or 'Mention packaged items (e.g. Maggi) for swap ideas.'}\n\n"
            "Use **Pantry** or **Recipes** for full agent flows."
        )
    if agent == "RecipeCreator":
        return (
            f"From pantry ({pantry_list}): try dal tadka + rice, or palak paneer if you have spinach and paneer. "
            "Open **Recipes → Generate** for full steps."
        )
    if agent == "MealPlanner":
        return "Use **Weekly Plan → Generate** for a 7-day schedule with leftovers noted."
    if agent == "ShoppingListOptimizer":
        return "Generate a weekly plan first, then **Shopping List**."
    return (
        f"Hi {name}! Pantry: {pantry_list}. Ask about recipes, swaps, or planning. "
        "Toggle **Fast replies** in Chat for instant answers without waiting on Ollama."
    )


def _build_chat_prompts(
    message: str,
    profile: UserProfile | None,
    pantry: list[PantryItem],
    history: list[dict[str, str]] | None,
    agent: str,
) -> tuple[str, str]:
    kb_bit = ""
    if profile and (PACKAGED_RE.search(message) or agent == "InventoryAgent"):
        insights = get_kb().build_insights(pantry, profile)
        if insights:
            kb_bit = "Packaged notes: " + "; ".join(i.gentle_message[:120] for i in insights[:2])

    hist = ""
    if history:
        for turn in history[-2:]:
            prev = (turn.get("assistant") or "")[:200]
            hist += f"User: {turn.get('user', '')}\nAssistant: {prev}\n"

    system = (
        f"You are {agent} for NutriPlan AI (Indian home cooking). "
        "Reply in 2-4 short paragraphs max. Practical, warm. No medical advice."
    )
    user = (
        f"{hist}User: {message}\n"
        f"Context: {_profile_summary(profile)}. Pantry: {_pantry_summary(pantry)}. {kb_bit}"
    )
    return system, user


def chat_reply(
    message: str,
    profile: UserProfile | None,
    pantry: list[PantryItem],
    history: list[dict[str, str]] | None = None,
    *,
    fast_mode: bool = False,
) -> tuple[str, str]:
    """Returns (agent_name, reply_text)."""
    safety = check_user_text(message)
    if safety.action == "redirect":
        return "SafetyGate", safety.message + f"\n\n_{DISCLAIMER}_"

    agent = detect_chat_agent(message)
    prefix = (safety.message + "\n\n") if safety.action == "require_confirmation" else ""

    if fast_mode or not llm_available():
        return agent, prefix + _fallback_reply(message, agent, profile, pantry)

    system, user = _build_chat_prompts(message, profile, pantry, history, agent)

    try:
        text = _completion(system, user, mode="chat")
        if safety.action == "require_confirmation":
            text = prefix + text
        text += f"\n\n_{DISCLAIMER}_"
        return agent, text
    except Exception:
        return agent, prefix + _fallback_reply(message, agent, profile, pantry)


def chat_reply_stream(
    message: str,
    profile: UserProfile | None,
    pantry: list[PantryItem],
    history: list[dict[str, str]] | None = None,
    *,
    fast_mode: bool = False,
) -> tuple[str, Iterator[str], str]:
    """
    Returns (agent, token_iterator, suffix_to_append_after_stream).
    """
    safety = check_user_text(message)
    if safety.action == "redirect":
        return "SafetyGate", iter([safety.message]), f"\n\n_{DISCLAIMER}_"

    agent = detect_chat_agent(message)
    prefix = (safety.message + "\n\n") if safety.action == "require_confirmation" else ""
    suffix = f"\n\n_{DISCLAIMER}_"

    if fast_mode or not llm_available():

        def _once() -> Iterator[str]:
            yield prefix + _fallback_reply(message, agent, profile, pantry)

        return agent, _once(), ""

    system, user = _build_chat_prompts(message, profile, pantry, history, agent)

    def _gen() -> Iterator[str]:
        if prefix:
            yield prefix
        try:
            for token in completion_stream(system, user, mode="chat"):
                yield token
        except Exception:
            yield _fallback_reply(message, agent, profile, pantry)

    return agent, _gen(), suffix
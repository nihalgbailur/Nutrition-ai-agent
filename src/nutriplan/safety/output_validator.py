from __future__ import annotations

import re

from nutriplan.config import DISCLAIMER
from nutriplan.models.schemas import WeeklyMealPlan
from nutriplan.safety.allergen_filter import recipe_has_allergen

FORBIDDEN_CLAIMS = [
    r"\b(cure|treat|reverse|manage\s+your\s+diabetes|therapeutic\s+diet)\b",
    r"\b(exactly\s+\d+\s*g\s+(protein|carbs))\b",
]

RAW_UNSAFE = [r"\braw\s+(chicken|meat|fish|eggs)\b", r"\bunpasteurized\b"]


def sanitize_text(text: str) -> str:
    cleaned = text
    for pattern in FORBIDDEN_CLAIMS + RAW_UNSAFE:
        cleaned = re.sub(pattern, "[removed for safety]", cleaned, flags=re.IGNORECASE)
    return cleaned


def validate_recipe(recipe, profile) -> tuple[bool, str]:
    hits = recipe_has_allergen(recipe, profile.allergies)
    if hits:
        return False, f"Contains declared allergen(s): {', '.join(sorted(set(hits)))}"
    blob = f"{recipe.name} {recipe.why_fits} {' '.join(recipe.steps)}"
    for pattern in FORBIDDEN_CLAIMS:
        if re.search(pattern, blob, re.IGNORECASE):
            return False, "Contains disallowed medical or precision claims."
    return True, ""


def apply_recipe_safety(recipe, profile):
    recipe.disclaimer = DISCLAIMER
    recipe.why_fits = sanitize_text(recipe.why_fits)
    recipe.kb_notes = sanitize_text(recipe.kb_notes)
    recipe.steps = [sanitize_text(s) for s in recipe.steps]
    recipe.nutrition.label = recipe.nutrition.label or "Approximate estimates only"
    ok, _ = validate_recipe(recipe, profile)
    return recipe if ok else None


def validate_weekly_plan(plan, profile) -> WeeklyMealPlan:
    plan.disclaimer = DISCLAIMER
    plan.variety_notes = sanitize_text(plan.variety_notes)
    plan.leftover_strategy = sanitize_text(plan.leftover_strategy)
    plan.compromises = sanitize_text(plan.compromises)
    return plan
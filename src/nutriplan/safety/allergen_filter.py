from __future__ import annotations

import re

ALLERGEN_SYNONYMS: dict[str, list[str]] = {
    "dairy": ["milk", "paneer", "ghee", "butter", "cheese", "curd", "dahi", "yogurt", "cream", "khoya"],
    "nuts": ["almond", "cashew", "walnut", "peanut", "pista", "nut", "badam", "kaju"],
    "peanut": ["peanut", "groundnut", "moongfali"],
    "gluten": ["wheat", "atta", "maida", "semolina", "rava", "bread", "roti", "naan", "gluten"],
    "shellfish": ["prawn", "shrimp", "crab", "lobster", "shellfish"],
    "egg": ["egg", "omelette", "omelet", "anda"],
    "soy": ["soy", "soya", "tofu"],
    "sesame": ["sesame", "til"],
}


def _normalize_allergen(token: str) -> str:
    t = token.lower().strip()
    for key, synonyms in ALLERGEN_SYNONYMS.items():
        if t == key or t in synonyms:
            return key
    return t


def expand_allergens(allergies: list[str]) -> set[str]:
    expanded: set[str] = set()
    for allergy in allergies:
        key = _normalize_allergen(allergy)
        expanded.add(key)
        expanded.update(ALLERGEN_SYNONYMS.get(key, [allergy.lower()]))
    return expanded


def text_contains_allergen(text: str, allergens: set[str]) -> list[str]:
    if not allergens:
        return []
    lowered = text.lower()
    hits: list[str] = []
    for token in allergens:
        if re.search(rf"\b{re.escape(token)}\b", lowered):
            hits.append(token)
    return hits


def recipe_has_allergen(recipe, allergies: list[str]) -> list[str]:
    allergens = expand_allergens(allergies)
    if not allergens:
        return []
    parts: list[str] = [recipe.name, recipe.why_fits, recipe.kb_notes]
    for ing in recipe.ingredients:
        parts.append(ing.name)
        parts.append(ing.quantity)
    for step in recipe.steps:
        parts.append(step)
    blob = " ".join(parts)
    return text_contains_allergen(blob, allergens)
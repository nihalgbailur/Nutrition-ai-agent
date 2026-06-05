from __future__ import annotations

import json
from pathlib import Path

from nutriplan.config import SAMPLE_DIR, SYNTHETIC_DIR
from nutriplan.db.repository import Repository
from nutriplan.knowledge.packaged_foods import get_kb
from nutriplan.models.schemas import (
    BudgetLevel,
    DayMeals,
    DietStyle,
    FeedbackRecord,
    HealthFlags,
    HealthGoal,
    IngredientLine,
    MealSlot,
    NutritionEstimate,
    PantryItem,
    Recipe,
    ShoppingList,
    ShoppingListItem,
    SpiceLevel,
    UserProfile,
    WeeklyMealPlan,
)


def _load_json(name: str) -> object:
    path = SYNTHETIC_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def _profile_from_dict(pdata: dict) -> UserProfile:
    hf = pdata.get("health_flags", {})
    return UserProfile(
        name=pdata["name"],
        diet_style=DietStyle(pdata["diet_style"]),
        health_goal=HealthGoal(pdata["health_goal"]),
        allergies=pdata.get("allergies", []),
        cuisine_preferences=pdata.get("cuisine_preferences", []),
        spice_level=SpiceLevel(pdata["spice_level"]),
        max_cook_minutes=pdata.get("max_cook_minutes", 30),
        budget_level=BudgetLevel(pdata["budget_level"]),
        preferred_ingredients=pdata.get("preferred_ingredients", []),
        disliked_ingredients=pdata.get("disliked_ingredients", []),
        health_flags=HealthFlags(
            has_medical_condition=hf.get("has_medical_condition", False),
            medical_notes=hf.get("medical_notes", ""),
            is_pregnant_or_breastfeeding=hf.get("is_pregnant_or_breastfeeding", False),
            cooking_for_children=hf.get("cooking_for_children", False),
            cooking_for_elderly=hf.get("cooking_for_elderly", False),
        ),
    )


def _recipe_from_dict(row: dict) -> Recipe:
    nutrition = row.get("nutrition", {})
    return Recipe(
        name=row["name"],
        ingredients=[IngredientLine(**i) for i in row.get("ingredients", [])],
        steps=row.get("steps", []),
        prep_minutes=row.get("prep_minutes", 15),
        cook_minutes=row.get("cook_minutes", 20),
        servings=row.get("servings", 2),
        nutrition=NutritionEstimate(**nutrition) if nutrition else NutritionEstimate(),
        why_fits=row.get("why_fits", ""),
        kb_notes=row.get("kb_notes", ""),
        cuisine_tags=row.get("cuisine_tags", []),
    )


def load_demo_data(repo: Repository) -> None:
    """Small demo (Priya + 18 pantry items) — original sample files."""
    profile_path = SAMPLE_DIR / "demo_profile.json"
    pantry_path = SAMPLE_DIR / "demo_pantry.json"
    pdata = json.loads(profile_path.read_text())
    profile = _profile_from_dict(pdata)
    repo.save_profile(profile)
    repo.clear_pantry()
    for row in json.loads(pantry_path.read_text()):
        repo.save_pantry_item(
            PantryItem(
                name=row["name"],
                category=row.get("category", "Other"),
                quantity=row.get("quantity", ""),
                is_packaged=row.get("is_packaged", False),
            )
        )


def load_synthetic_database(repo: Repository, profile_index: int = 0) -> dict[str, int]:
    """
    Load full synthetic dataset from data/synthetic/*.json into SQLite.
    Returns counts per entity type.
    """
    manifest = _load_json("database_manifest.json")
    profile_index = profile_index or manifest.get("default_profile_index", 0)

    profiles = _load_json(manifest["files"]["profiles"])
    profile = _profile_from_dict(profiles[profile_index])
    repo.save_profile(profile)
    repo.reset_generated_data()
    repo.clear_pantry()
    pantry_rows = _load_json(manifest["files"]["pantry"])
    for row in pantry_rows:
        repo.save_pantry_item(
            PantryItem(
                name=row["name"],
                category=row.get("category", "Other"),
                quantity=row.get("quantity", ""),
                is_packaged=row.get("is_packaged", False),
            )
        )
    pantry = repo.list_pantry()

    recipes = [_recipe_from_dict(r) for r in _load_json(manifest["files"]["recipes"])]
    repo.save_recipes(recipes)

    plan_data = _load_json(manifest["files"]["meal_plan"])
    days = []
    for d in plan_data["days"]:
        days.append(
            DayMeals(
                day_index=d["day_index"],
                day_label=d["day_label"],
                meals=[MealSlot(**m) for m in d["meals"]],
            )
        )
    plan = WeeklyMealPlan(
        days=days,
        variety_notes=plan_data.get("variety_notes", ""),
        leftover_strategy=plan_data.get("leftover_strategy", ""),
        compromises=plan_data.get("compromises", ""),
    )
    repo.save_meal_plan(plan)

    shop_data = _load_json(manifest["files"]["shopping_list"])
    shopping = ShoppingList(
        items=[ShoppingListItem(**i) for i in shop_data.get("items", [])]
    )
    repo.save_shopping_list(shopping)

    for fb in _load_json(manifest["files"]["feedback"]):
        repo.save_feedback(
            FeedbackRecord(
                recipe_id="synthetic",
                recipe_name=fb["recipe_name"],
                rating=fb["rating"],
                cooked=fb.get("cooked", False),
                not_suitable=fb.get("not_suitable", False),
                reason=fb.get("reason", ""),
            )
        )

    kb = get_kb()
    get_kb.cache_clear()  # type: ignore[attr-defined]
    kb = get_kb()
    insights = kb.build_insights(pantry, profile)
    repo.save_kb_insights(insights)

    return {
        "profiles_available": len(profiles),
        "pantry_items": len(pantry_rows),
        "recipes": len(recipes),
        "meal_plan_days": len(days),
        "shopping_items": len(shopping.items),
        "feedback": len(_load_json(manifest["files"]["feedback"])),
        "kb_insights": len(insights),
        "kb_records": len(kb.records),
    }
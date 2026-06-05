from __future__ import annotations

from nutriplan.config import DISCLAIMER, SAFETY_SYSTEM_APPENDIX
from nutriplan.knowledge.packaged_foods import get_kb
from nutriplan.llm.client import generate_json_list, generate_structured, llm_available
from nutriplan.llm.fallback import fallback_recipes, fallback_shopping_list, fallback_weekly_plan
from nutriplan.models.schemas import (
    DayMeals,
    IngredientLine,
    KBInsight,
    MealSlot,
    NutritionEstimate,
    PantryItem,
    Recipe,
    ShoppingList,
    ShoppingListItem,
    UserProfile,
    WeeklyMealPlan,
)
from nutriplan.safety.allergen_filter import recipe_has_allergen
from nutriplan.safety.guardrails import check_user_text
from nutriplan.safety.output_validator import apply_recipe_safety, validate_weekly_plan


def _profile_block(profile: UserProfile) -> str:
    return profile.model_dump_json(indent=2)


def _pantry_block(pantry: list[PantryItem]) -> str:
    return "\n".join(f"- {p.name} ({p.category}) qty={p.quantity}" for p in pantry) or "- empty"


def profile_manager_node(state: dict) -> dict:
    profile = state.get("user_profile")
    if not profile:
        return {"active_agent": "ProfileManager", "error": "No profile to save."}
    text = state.get("user_text", "")
    safety = check_user_text(text) if text else None
    return {
        "active_agent": "ProfileManager",
        "user_profile": profile,
        "safety_result": safety,
    }


def inventory_agent_node(state: dict) -> dict:
    profile: UserProfile = state["user_profile"]
    pantry: list[PantryItem] = state.get("pantry", [])
    kb = get_kb()
    insights = kb.build_insights(pantry, profile)
    sorted_pantry = sorted(
        pantry,
        key=lambda p: (
            0 if any(i.pantry_item_name == p.name for i in kb.match_pantry_items([p])) else 1,
            p.name,
        ),
    )
    return {
        "active_agent": "InventoryAgent",
        "pantry": sorted_pantry,
        "kb_insights": insights,
    }


def recipe_creator_node(state: dict) -> dict:
    profile: UserProfile = state["user_profile"]
    pantry: list[PantryItem] = state.get("pantry", [])
    insights: list[KBInsight] = state.get("kb_insights", [])
    kb_context = get_kb().build_agent_context(insights)
    used_fallback = False
    recipes: list[Recipe] = []

    if llm_available():
        system = (
            "You are RecipeCreator for NutriPlan AI (Indian home cooking). "
            "Generate 4 diverse recipes using pantry items. Respect diet, allergies, time limits. "
            "Nutrition must be rough estimates only."
        )
        user = (
            f"Profile:\n{_profile_block(profile)}\n\nPantry:\n{_pantry_block(pantry)}\n\n"
            f"{kb_context}\n\n"
            "Return JSON object with key 'recipes' as array. Each recipe: name, ingredients "
            "[{name, quantity}], steps[], prep_minutes, cook_minutes, servings, nutrition "
            "{calories, protein_g, carbs_g, fat_g}, why_fits, kb_notes, cuisine_tags."
        )
        raw_list = generate_json_list(system, user)
        for item in raw_list[:5]:
            try:
                recipe = Recipe.model_validate(item)
                safe = apply_recipe_safety(recipe, profile)
                if safe and not recipe_has_allergen(safe, profile.allergies):
                    recipes.append(safe)
            except Exception:
                continue

    if len(recipes) < 3:
        used_fallback = True
        recipes = fallback_recipes(profile, pantry, count=4)
        for r in recipes:
            apply_recipe_safety(r, profile)
        if insights:
            recipes[0].kb_notes = insights[0].gentle_message[:400]

    return {"active_agent": "RecipeCreator", "recipes": recipes, "used_fallback": used_fallback}


def meal_planner_node(state: dict) -> dict:
    profile: UserProfile = state["user_profile"]
    pantry: list[PantryItem] = state.get("pantry", [])
    recipes: list[Recipe] = state.get("recipes") or fallback_recipes(profile, pantry)
    insights: list[KBInsight] = state.get("kb_insights", [])
    kb_context = get_kb().build_agent_context(insights)
    used_fallback = state.get("used_fallback", False)
    plan: WeeklyMealPlan | None = None

    if llm_available():
        system = "You are MealPlanner for NutriPlan AI. Build a 7-day plan (breakfast, lunch, dinner)."
        recipe_names = ", ".join(r.name for r in recipes)
        user = (
            f"Profile:\n{_profile_block(profile)}\n\nRecipes available: {recipe_names}\n"
            f"Pantry:\n{_pantry_block(pantry)}\n{kb_context}\n"
            "Return JSON: days[{day_index, day_label, meals[{slot, recipe_name, notes, uses_leftovers_from}]}], "
            "variety_notes, leftover_strategy, compromises."
        )
        plan = generate_structured(system, user, WeeklyMealPlan)

    if plan is None:
        used_fallback = True
        plan = fallback_weekly_plan(profile, recipes)

    plan = validate_weekly_plan(plan, profile)
    if insights and not plan.compromises:
        plan.compromises = (
            "Packaged snacks/noodles in pantry were noted; plan favors home-cooked meals where possible."
        )

    return {"active_agent": "MealPlanner", "weekly_plan": plan, "used_fallback": used_fallback}


def shopping_list_optimizer_node(state: dict) -> dict:
    profile: UserProfile = state["user_profile"]
    pantry: list[PantryItem] = state.get("pantry", [])
    plan: WeeklyMealPlan | None = state.get("weekly_plan")
    kb = get_kb()
    used_fallback = False

    if plan is None:
        return {"active_agent": "ShoppingListOptimizer", "error": "Generate a weekly plan first."}

    if llm_available():
        system = "You are ShoppingListOptimizer. Consolidate shopping needs from the meal plan minus pantry."
        user = (
            f"Plan:\n{plan.model_dump_json()}\nPantry:\n{_pantry_block(pantry)}\n"
            "Return JSON: items[{name, category, quantity, in_pantry}]"
        )
        data = generate_json_list(system, user)
        items: list[ShoppingListItem] = []
        for row in data:
            try:
                item = ShoppingListItem.model_validate(row)
                item.in_pantry = any(
                    item.name.lower() in p.name.lower() or p.name.lower() in item.name.lower()
                    for p in pantry
                )
                item.suggested_swap = kb.shopping_swap_hint(item.name, profile)
                if not item.in_pantry:
                    items.append(item)
            except Exception:
                continue
        if items:
            shopping = ShoppingList(items=items, disclaimer=DISCLAIMER)
            return {"active_agent": "ShoppingListOptimizer", "shopping_list": shopping}

    used_fallback = True
    hints = {p.name: kb.shopping_swap_hint(p.name, profile) for p in pantry if p.is_packaged}
    shopping = fallback_shopping_list(plan, pantry, hints)
    for item in shopping.items:
        item.suggested_swap = kb.shopping_swap_hint(item.name, profile)
    return {
        "active_agent": "ShoppingListOptimizer",
        "shopping_list": shopping,
        "used_fallback": used_fallback,
    }


def feedback_agent_node(state: dict) -> dict:
    profile: UserProfile | None = state.get("user_profile")
    if profile and state.get("feedback_not_suitable"):
        disliked = state.get("feedback_reason", "").lower()
        if disliked:
            profile.disliked_ingredients = list(set(profile.disliked_ingredients + [disliked]))
        profile.limit_packaged_snacks = state.get("feedback_limit_packaged", profile.limit_packaged_snacks)
    return {"active_agent": "FeedbackAgent", "user_profile": profile}


def safety_gate_node(state: dict) -> dict:
    text = state.get("user_text", "")
    result = check_user_text(text)
    return {"safety_result": result, "active_agent": "SafetyGate"}
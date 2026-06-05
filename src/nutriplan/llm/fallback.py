from __future__ import annotations

from nutriplan.config import DISCLAIMER
from nutriplan.models.schemas import (
    DayMeals,
    IngredientLine,
    MealSlot,
    NutritionEstimate,
    PantryItem,
    Recipe,
    ShoppingList,
    ShoppingListItem,
    UserProfile,
    WeeklyMealPlan,
)

DAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fallback_recipes(profile: UserProfile, pantry: list[PantryItem], count: int = 4) -> list[Recipe]:
    pantry_names = {p.name.lower() for p in pantry}
    recipes: list[Recipe] = []

    def has(*items: str) -> bool:
        return any(i.lower() in " ".join(pantry_names) for i in items)

    candidates = [
        Recipe(
            name="Palak Paneer with Jeera Rice",
            ingredients=[
                IngredientLine(name="Spinach", quantity="2 cups chopped"),
                IngredientLine(name="Paneer", quantity="200g cubed"),
                IngredientLine(name="Basmati Rice", quantity="1 cup"),
                IngredientLine(name="Onion", quantity="1 medium"),
                IngredientLine(name="Tomato", quantity="1"),
            ],
            steps=[
                "Blanch spinach; blend to a coarse puree.",
                "Sauté cumin, onion, ginger-garlic; add tomatoes and spices.",
                "Add paneer and spinach; simmer 8 minutes.",
                "Serve with jeera rice cooked separately.",
            ],
            prep_minutes=15,
            cook_minutes=25,
            servings=2,
            nutrition=NutritionEstimate(calories=480, protein_g=22, carbs_g=45, fat_g=22),
            why_fits="Uses fresh pantry staples; balanced vegetarian dinner for busy weekdays.",
            cuisine_tags=["North Indian"],
        ),
        Recipe(
            name="Tomato Dal Tadka",
            ingredients=[
                IngredientLine(name="Toor Dal", quantity="3/4 cup"),
                IngredientLine(name="Tomato", quantity="2 chopped"),
                IngredientLine(name="Onion", quantity="1"),
                IngredientLine(name="Green Chili", quantity="1-2"),
            ],
            steps=[
                "Pressure-cook dal with turmeric until soft.",
                "Prepare tadka with mustard seeds, onion, tomato, and chili.",
                "Combine and simmer; finish with lemon.",
            ],
            prep_minutes=10,
            cook_minutes=30,
            servings=3,
            nutrition=NutritionEstimate(calories=320, protein_g=14, carbs_g=48, fat_g=8),
            why_fits="High-protein comfort meal using dal — great for maintenance goals.",
            cuisine_tags=["North Indian", "South Indian"],
        ),
        Recipe(
            name="Vegetable Upma Style Poha",
            ingredients=[
                IngredientLine(name="Onion", quantity="1 small"),
                IngredientLine(name="Green Chili", quantity="1"),
                IngredientLine(name="Lemon", quantity="1/2"),
            ],
            steps=[
                "Dry-roast flattened rice if available; otherwise use fine rava style prep with veggies.",
                "Temper mustard seeds, curry leaves, onion, and chili.",
                "Add soaked poha/flakes, peas if on hand; steam 5 minutes.",
                "Finish with lemon and peanuts only if no nut allergy.",
            ],
            prep_minutes=10,
            cook_minutes=15,
            servings=2,
            nutrition=NutritionEstimate(calories=280, protein_g=8, carbs_g=52, fat_g=6),
            why_fits="Quick breakfast using common Indian pantry vegetables.",
            cuisine_tags=["South Indian"],
        ),
        Recipe(
            name="Curd Rice with Lemon Pickle (optional)",
            ingredients=[
                IngredientLine(name="Basmati Rice", quantity="1 cup cooked"),
                IngredientLine(name="Curd", quantity="1 cup"),
                IngredientLine(name="Curry leaves", quantity="few"),
            ],
            steps=[
                "Mash lightly warm rice with curd and salt.",
                "Temper mustard seeds, urad dal, curry leaves in minimal oil.",
                "Mix and serve chilled or room temperature.",
            ],
            prep_minutes=10,
            cook_minutes=10,
            servings=2,
            nutrition=NutritionEstimate(calories=350, protein_g=10, carbs_g=55, fat_g=9),
            why_fits="Light, cooling meal — easy when short on cooking time.",
            cuisine_tags=["South Indian"],
        ),
    ]

    for recipe in candidates:
        recipe.disclaimer = DISCLAIMER
        if has("paneer") or "paneer" not in recipe.name.lower():
            if "paneer" in recipe.name.lower() and not has("paneer"):
                continue
        if "dal" in recipe.name.lower() and not has("dal", "toor"):
            continue
        recipes.append(recipe)
        if len(recipes) >= count:
            break

    if not recipes:
        recipes.append(candidates[1])
    return recipes[:count]


def fallback_weekly_plan(profile: UserProfile, recipes: list[Recipe]) -> WeeklyMealPlan:
    days: list[DayMeals] = []
    recipe_cycle = recipes or fallback_recipes(profile, [])
    for i, label in enumerate(DAY_LABELS):
        r_breakfast = recipe_cycle[i % len(recipe_cycle)]
        r_lunch = recipe_cycle[(i + 1) % len(recipe_cycle)]
        r_dinner = recipe_cycle[(i + 2) % len(recipe_cycle)]
        days.append(
            DayMeals(
                day_index=i,
                day_label=label,
                meals=[
                    MealSlot(slot="breakfast", recipe_name=r_breakfast.name, recipe_id=r_breakfast.id),
                    MealSlot(slot="lunch", recipe_name=r_lunch.name, recipe_id=r_lunch.id, notes="Prep extra dal for dinner reuse" if i % 2 == 0 else ""),
                    MealSlot(
                        slot="dinner",
                        recipe_name=r_dinner.name,
                        recipe_id=r_dinner.id,
                        uses_leftovers_from="lunch" if i % 2 == 0 else None,
                    ),
                ],
            )
        )
    return WeeklyMealPlan(
        days=days,
        variety_notes="Rotates pantry-friendly vegetarian meals across the week.",
        leftover_strategy="Reuse dal and rice components within 24 hours where noted.",
        compromises="",
        disclaimer=DISCLAIMER,
    )


def fallback_shopping_list(
    plan: WeeklyMealPlan,
    pantry: list[PantryItem],
    swap_hints: dict[str, str | None],
) -> ShoppingList:
    pantry_lower = {p.name.lower() for p in pantry}
    needed = [
        ("Fresh coriander", "Produce", "1 bunch"),
        ("Carrot", "Produce", "500g"),
        ("Moong dal", "Proteins", "250g"),
        ("Curry leaves", "Spices", "1 pack"),
    ]
    items: list[ShoppingListItem] = []
    for name, category, qty in needed:
        in_pantry = any(name.lower() in p or p in name.lower() for p in pantry_lower)
        items.append(
            ShoppingListItem(
                name=name,
                category=category,
                quantity=qty,
                in_pantry=in_pantry,
                suggested_swap=swap_hints.get(name),
            )
        )
    return ShoppingList(items=items, disclaimer=DISCLAIMER)
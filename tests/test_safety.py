from nutriplan.models.schemas import IngredientLine, Recipe, UserProfile
from nutriplan.safety.allergen_filter import recipe_has_allergen
from nutriplan.safety.guardrails import check_user_text
from nutriplan.safety.output_validator import validate_recipe


def test_redirect_kidney_plan():
    result = check_user_text("I need a kidney disease meal plan")
    assert result.action == "redirect"


def test_allergen_blocks_peanut():
    recipe = Recipe(
        name="Peanut Chutney",
        ingredients=[IngredientLine(name="Peanut", quantity="1/2 cup")],
        steps=["Grind peanuts."],
    )
    hits = recipe_has_allergen(recipe, ["peanut"])
    assert hits
    ok, _ = validate_recipe(recipe, UserProfile(allergies=["peanut"]))
    assert not ok
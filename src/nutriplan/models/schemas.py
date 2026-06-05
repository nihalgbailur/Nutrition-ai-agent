from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from nutriplan.config import DISCLAIMER, NUTRITION_LABEL


def new_id() -> str:
    return str(uuid4())


class DietStyle(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    EGGETARIAN = "eggetarian"
    NON_VEG = "non_veg"
    JAIN = "jain"


class HealthGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    ENERGY = "energy"
    GENERAL_HEALTH = "general_health"


class SpiceLevel(str, Enum):
    MILD = "mild"
    MEDIUM = "medium"
    HOT = "hot"


class BudgetLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HealthFlags(BaseModel):
    has_medical_condition: bool = False
    medical_notes: str = ""
    is_pregnant_or_breastfeeding: bool = False
    cooking_for_children: bool = False
    cooking_for_elderly: bool = False
    requires_plan_confirmation: bool = False


class UserProfile(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str = "User"
    diet_style: DietStyle = DietStyle.VEGETARIAN
    health_goal: HealthGoal = HealthGoal.MAINTENANCE
    allergies: list[str] = Field(default_factory=list)
    cuisine_preferences: list[str] = Field(default_factory=lambda: ["North Indian", "South Indian"])
    spice_level: SpiceLevel = SpiceLevel.MEDIUM
    max_cook_minutes: int = 45
    budget_level: BudgetLevel = BudgetLevel.MEDIUM
    health_flags: HealthFlags = Field(default_factory=HealthFlags)
    disliked_ingredients: list[str] = Field(default_factory=list)
    preferred_ingredients: list[str] = Field(default_factory=list)
    limit_packaged_snacks: bool = False


class PantryItem(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    category: str = "Other"
    quantity: str = ""
    expiry_date: date | None = None
    is_packaged: bool = False


class NutritionEstimate(BaseModel):
    calories: int | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    label: str = NUTRITION_LABEL


class IngredientLine(BaseModel):
    name: str
    quantity: str = ""


class Recipe(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    ingredients: list[IngredientLine]
    steps: list[str]
    prep_minutes: int = 15
    cook_minutes: int = 20
    servings: int = 2
    nutrition: NutritionEstimate = Field(default_factory=NutritionEstimate)
    why_fits: str = ""
    kb_notes: str = ""
    disclaimer: str = DISCLAIMER
    cuisine_tags: list[str] = Field(default_factory=list)
    contains_allergens: list[str] = Field(default_factory=list)


class MealSlot(BaseModel):
    slot: Literal["breakfast", "lunch", "dinner", "snack"] = "lunch"
    recipe_name: str
    recipe_id: str | None = None
    notes: str = ""
    uses_leftovers_from: str | None = None


class DayMeals(BaseModel):
    day_index: int
    day_label: str
    meals: list[MealSlot] = Field(default_factory=list)


class WeeklyMealPlan(BaseModel):
    id: str = Field(default_factory=new_id)
    days: list[DayMeals] = Field(default_factory=list)
    variety_notes: str = ""
    leftover_strategy: str = ""
    compromises: str = ""
    disclaimer: str = DISCLAIMER


class ShoppingListItem(BaseModel):
    name: str
    category: str = "Other"
    quantity: str = "1"
    in_pantry: bool = False
    suggested_swap: str | None = None


class ShoppingList(BaseModel):
    id: str = Field(default_factory=new_id)
    items: list[ShoppingListItem] = Field(default_factory=list)
    disclaimer: str = DISCLAIMER


class FeedbackRecord(BaseModel):
    id: str = Field(default_factory=new_id)
    recipe_id: str
    recipe_name: str
    rating: int = Field(ge=1, le=5)
    cooked: bool = False
    not_suitable: bool = False
    reason: str = ""


class PantryKBMatch(BaseModel):
    pantry_item_name: str
    kb_product: str
    kb_brand: str
    category: str
    concerns: list[str]
    why_problematic: str
    score: float


class AlternativeSuggestion(BaseModel):
    product: str
    brand: str
    why_better: str
    concerns: list[str] = Field(default_factory=list)


class KBInsight(BaseModel):
    pantry_item: str
    concerns: list[str]
    gentle_message: str
    alternatives: list[AlternativeSuggestion] = Field(default_factory=list)


class SafetyResult(BaseModel):
    action: Literal["allow", "redirect", "require_confirmation"] = "allow"
    message: str = ""
    category: str = ""


class AgentRunMetadata(BaseModel):
    active_agent: str = ""
    message: str = ""
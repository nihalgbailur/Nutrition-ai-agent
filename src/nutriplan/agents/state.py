from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages

from nutriplan.models.schemas import (
    KBInsight,
    Recipe,
    SafetyResult,
    ShoppingList,
    UserProfile,
    WeeklyMealPlan,
)
from nutriplan.models.schemas import PantryItem


class NutriPlanState(TypedDict, total=False):
    messages: Annotated[list[Any], add_messages]
    intent: str
    user_profile: UserProfile | None
    pantry: list[PantryItem]
    kb_insights: list[KBInsight]
    recipes: list[Recipe]
    weekly_plan: WeeklyMealPlan | None
    shopping_list: ShoppingList | None
    safety_result: SafetyResult | None
    active_agent: str
    user_text: str
    error: str
    used_fallback: bool
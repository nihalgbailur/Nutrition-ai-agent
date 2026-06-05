from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from nutriplan.agents.graph import invoke_graph
from nutriplan.api.dependencies import get_repository, set_current_agent_status
from nutriplan.models.schemas import ShoppingList

router = APIRouter()


@router.get("/shopping", response_model=ShoppingList | None)
async def get_latest_shopping(repo=Depends(get_repository)):
    return repo.get_latest_shopping_list()


@router.post("/shopping/generate")
async def generate_shopping(repo=Depends(get_repository)):
    profile = repo.get_profile()
    plan = repo.get_latest_meal_plan()
    if not profile:
        raise HTTPException(400, "Set up profile first")
    if not plan:
        raise HTTPException(400, "Generate a weekly plan first")

    pantry = repo.list_pantry()
    set_current_agent_status("ShoppingListOptimizer")
    result = invoke_graph(
        "generate_shopping_list",
        profile,
        pantry,
        weekly_plan=plan,
    )
    sl = result.get("shopping_list")
    if sl:
        repo.save_shopping_list(sl)
    set_current_agent_status("")
    return {
        "shopping_list": sl,
        "active_agent": result.get("active_agent", ""),
    }

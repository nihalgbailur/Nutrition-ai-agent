from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from nutriplan.agents.graph import invoke_graph
from nutriplan.api.dependencies import get_repository, set_current_agent_status
from nutriplan.models.schemas import WeeklyMealPlan
from nutriplan.safety.guardrails import profile_requires_confirmation

router = APIRouter()


class GeneratePlanRequest(BaseModel):
    confirmed: bool = False  # FE must send true if profile_requires_confirmation


@router.get("/plan", response_model=WeeklyMealPlan | None)
async def get_latest_plan(repo=Depends(get_repository)):
    return repo.get_latest_meal_plan()


@router.post("/plan/generate")
async def generate_weekly_plan(req: GeneratePlanRequest, repo=Depends(get_repository)):
    profile = repo.get_profile()
    if not profile:
        raise HTTPException(400, "Set up profile first")

    if profile_requires_confirmation(profile) and not req.confirmed:
        raise HTTPException(
            400,
            detail={"needs_confirmation": True, "message": "Medical confirmation required before generating plan."},
        )

    pantry = repo.list_pantry()
    set_current_agent_status("MealPlanner")
    result = invoke_graph(
        "generate_weekly_plan",
        profile,
        pantry,
    )
    safety = result.get("safety_result")
    if safety and safety.action == "redirect":
        raise HTTPException(400, detail={"safety": safety.model_dump()})

    plan = result.get("weekly_plan")
    if plan:
        if result.get("kb_insights"):
            repo.save_kb_insights(result["kb_insights"])
        if result.get("recipes"):
            repo.save_recipes(result["recipes"])
        repo.save_meal_plan(plan)

    set_current_agent_status("")
    return {
        "weekly_plan": plan,
        "used_fallback": result.get("used_fallback", False),
        "active_agent": result.get("active_agent", ""),
        "compromises": plan.compromises if plan else None,
        "leftover_strategy": plan.leftover_strategy if plan else None,
    }

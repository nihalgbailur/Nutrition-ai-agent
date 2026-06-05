from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from nutriplan.agents.graph import invoke_graph
from nutriplan.api.dependencies import get_repository, set_current_agent_status
from nutriplan.models.schemas import Recipe

router = APIRouter()


class GenerateRecipesRequest(BaseModel):
    query: str = ""


@router.get("/recipes", response_model=list[Recipe])
async def list_recipes(repo=Depends(get_repository)):
    return repo.list_recipes()


@router.post("/recipes/generate")
async def generate_recipes(req: GenerateRecipesRequest, repo=Depends(get_repository)):
    profile = repo.get_profile()
    if not profile:
        raise HTTPException(400, "Set up profile first")
    pantry = repo.list_pantry()
    set_current_agent_status("RecipeCreator")
    result = invoke_graph(
        "generate_recipes",
        profile,
        pantry,
        user_text=req.query,
    )
    safety = result.get("safety_result")
    if safety and safety.action == "redirect":
        raise HTTPException(400, detail={"safety": safety.model_dump()})

    recipes = result.get("recipes") or []
    if recipes:
        if result.get("kb_insights"):
            repo.save_kb_insights(result["kb_insights"])
        repo.save_recipes(recipes)

    set_current_agent_status("")
    return {
        "recipes": recipes,
        "used_fallback": result.get("used_fallback", False),
        "active_agent": result.get("active_agent", ""),
    }

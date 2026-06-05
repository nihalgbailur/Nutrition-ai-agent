from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from nutriplan.agents.graph import invoke_graph
from nutriplan.api.dependencies import get_repository, set_current_agent_status
from nutriplan.models.schemas import UserProfile

router = APIRouter()


@router.get("/profile", response_model=UserProfile | None)
async def get_profile(repo=Depends(get_repository)):
    return repo.get_profile()


@router.post("/profile", response_model=UserProfile)
async def save_profile(profile: UserProfile, repo=Depends(get_repository)):
    # Mirror old behavior: invoke ProfileManager (for safety/guardrails), then persist
    pantry = repo.list_pantry()
    set_current_agent_status("ProfileManager")
    result = invoke_graph("save_profile", profile, pantry, user_text=profile.health_flags.medical_notes or "")
    safety = result.get("safety_result")
    if safety and safety.action == "redirect":
        # Still save? Old code only saved on non-redirect. Surface error but allow caller to decide.
        # For API we raise with detail so FE can show nice error.
        raise HTTPException(status_code=400, detail={"safety": safety.model_dump(), "message": safety.message})

    repo.save_profile(profile)
    set_current_agent_status("")
    return profile

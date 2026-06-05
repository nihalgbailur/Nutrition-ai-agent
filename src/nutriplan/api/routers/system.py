from __future__ import annotations

from fastapi import APIRouter, Depends

from nutriplan.api.dependencies import get_current_agent_status, get_repository, set_current_agent_status
from nutriplan.llm.client import llm_available, llm_provider_label
from nutriplan.llm.ollama_util import ollama_is_running
from nutriplan.utils.seed import load_demo_data, load_synthetic_database

router = APIRouter()


@router.get("/system/status")
async def system_status():
    return {
        "llm_available": llm_available(),
        "provider": llm_provider_label(),
        "ollama_running": ollama_is_running(),
        "current_agent": get_current_agent_status(),
    }


@router.post("/system/seed/demo")
async def seed_demo(repo=Depends(get_repository)):
    load_demo_data(repo)
    return {"ok": True, "message": "Demo profile + 18 pantry items loaded."}


@router.post("/system/seed/full")
async def seed_full(repo=Depends(get_repository)):
    counts = load_synthetic_database(repo)
    return {
        "ok": True,
        "message": "Full synthetic database loaded.",
        "counts": counts,
    }


@router.post("/system/reset-generated")
async def reset_generated(repo=Depends(get_repository)):
    """Clear recipes, plans, shopping, feedback, kb cache (keep profile + pantry)."""
    repo.reset_generated_data()
    return {"ok": True}

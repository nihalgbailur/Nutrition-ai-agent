from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from nutriplan.agents.graph import invoke_graph
from nutriplan.api.dependencies import get_repository, set_current_agent_status
from nutriplan.models.schemas import FeedbackRecord

router = APIRouter()


@router.get("/feedback", response_model=list[FeedbackRecord])
async def list_feedback(repo=Depends(get_repository), limit: int = 20):
    return repo.list_feedback(limit=limit)


@router.post("/feedback")
async def submit_feedback(record: FeedbackRecord, repo=Depends(get_repository)):
    profile = repo.get_profile()
    if not profile:
        # allow guest-ish feedback but graph expects profile; use existing or error
        raise HTTPException(400, "Profile recommended for feedback learning")

    pantry = repo.list_pantry()
    set_current_agent_status("FeedbackAgent")
    # Build minimal feedback_kwargs like old UI
    result = invoke_graph(
        "feedback",
        profile,
        pantry,
        feedback_kwargs={
            "feedback_not_suitable": record.not_suitable,
            "feedback_reason": record.reason or record.recipe_name,
            "feedback_limit_packaged": "packaged" in (record.reason or "").lower(),
        },
    )
    if result.get("user_profile"):
        repo.save_profile(result["user_profile"])
    repo.save_feedback(record)
    set_current_agent_status("")
    return {"ok": True, "saved": record.id}

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from nutriplan.agents.graph import invoke_graph
from nutriplan.api.dependencies import get_repository, set_current_agent_status
from nutriplan.knowledge.packaged_foods import get_kb
from nutriplan.models.schemas import PantryItem

router = APIRouter()


class AddPantryItem(BaseModel):
    name: str
    category: str = "Other"
    quantity: str = ""
    is_packaged: bool = False
    expiry_date: str | None = None  # ISO or let Pydantic handle; frontend sends date string


@router.get("/pantry", response_model=list[PantryItem])
async def list_pantry(repo=Depends(get_repository)):
    return repo.list_pantry()


@router.post("/pantry", response_model=PantryItem)
async def add_pantry_item(item: AddPantryItem, repo=Depends(get_repository)):
    if not item.name or not item.name.strip():
        raise HTTPException(400, "name required")
    expiry = None
    if item.expiry_date:
        try:
            expiry = date.fromisoformat(item.expiry_date[:10])  # support full ISO or YYYY-MM-DD
        except Exception:
            expiry = None
    p = PantryItem(
        name=item.name.strip(),
        category=item.category,
        quantity=item.quantity,
        is_packaged=item.is_packaged,
        expiry_date=expiry,
    )
    repo.save_pantry_item(p)
    return p


@router.delete("/pantry/{item_id}")
async def delete_pantry_item(item_id: str, repo=Depends(get_repository)):
    repo.delete_pantry_item(item_id)
    return {"ok": True}


@router.post("/pantry/sync")
async def sync_pantry(repo=Depends(get_repository)):
    profile = repo.get_profile()
    if not profile:
        raise HTTPException(400, "Set up profile first")
    pantry = repo.list_pantry()
    set_current_agent_status("InventoryAgent")
    result = invoke_graph("sync_pantry", profile, pantry)
    if result.get("pantry"):
        repo.clear_pantry()
        for p in result["pantry"]:
            repo.save_pantry_item(p)
    insights = result.get("kb_insights") or []
    if insights:
        repo.save_kb_insights(insights)
    set_current_agent_status("")
    return {
        "pantry": repo.list_pantry(),
        "kb_insights": repo.get_kb_insights(),
    }

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from nutriplan.api.dependencies import get_repository
from nutriplan.llm.chat import chat_reply, chat_reply_stream
from nutriplan.models.guest import guest_profile
from nutriplan.models.schemas import UserProfile

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    fast_mode: bool = False


@router.post("/chat")
async def chat_once(req: ChatRequest, repo=Depends(get_repository)):
    """Non-streaming chat (useful for simple clients or testing)."""
    saved = repo.get_profile()
    profile: UserProfile = saved or guest_profile()
    pantry = repo.list_pantry()
    agent, text = chat_reply(
        req.message,
        profile,
        pantry,
        history=[],  # stateless for this endpoint; FE manages history for streaming path
        fast_mode=req.fast_mode,
    )
    return {"agent": agent, "text": text}


async def _event_stream(req: ChatRequest, repo) -> AsyncGenerator[str, None]:
    saved = repo.get_profile()
    profile: UserProfile = saved or guest_profile()
    pantry = repo.list_pantry()

    # For history we keep it simple here — real history lives in FE and can be sent in future extension
    agent, stream, suffix = chat_reply_stream(
        req.message,
        profile,
        pantry,
        history=None,
        fast_mode=req.fast_mode,
    )

    # First event: which agent
    yield f"data: {json.dumps({'type': 'agent', 'agent': agent})}\n\n"

    collected = []
    try:
        for part in stream:
            collected.append(part)
            yield f"data: {json.dumps({'type': 'token', 'text': part})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    if suffix:
        yield f"data: {json.dumps({'type': 'token', 'text': suffix})}\n\n"
        collected.append(suffix)

    yield f"data: {json.dumps({'type': 'done', 'full': ''.join(collected)})}\n\n"


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, repo=Depends(get_repository)):
    """SSE endpoint for token-by-token streaming chat replies."""
    return StreamingResponse(
        _event_stream(req, repo),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

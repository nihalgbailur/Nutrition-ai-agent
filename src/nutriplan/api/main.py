from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from nutriplan.api.dependencies import get_repository
from nutriplan.api.routers import (
    chat,
    feedback,
    pantry,
    planner,
    profile,
    recipes,
    shopping,
    system,
)
from nutriplan.utils.seed import load_synthetic_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-bootstrap on first run (parity with old Streamlit behavior)
    repo = get_repository()
    if repo.is_empty():
        load_synthetic_database(repo)
    yield
    # cleanup if needed (none for SQLite file)


app = FastAPI(
    title="NutriPlan AI API",
    description="Backend API for the premium Next.js frontend. Reuses the full LangGraph agentic core, safety guardrails, and local SQLite repo.",
    version="1.1.0",
    lifespan=lifespan,
)

# Local-only CORS for dev (frontend on 3000, api on 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(pantry.router, prefix="/api", tags=["pantry"])
app.include_router(recipes.router, prefix="/api", tags=["recipes"])
app.include_router(planner.router, prefix="/api", tags=["planner"])
app.include_router(shopping.router, prefix="/api", tags=["shopping"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(system.router, prefix="/api", tags=["system"])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "db": str(get_repository().db_path)}


# For direct uvicorn run: uvicorn src.nutriplan.api.main:app --reload
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("src.nutriplan.api.main:app", host="0.0.0.0", port=port, reload=True)

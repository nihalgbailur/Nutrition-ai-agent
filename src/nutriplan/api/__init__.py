"""FastAPI layer for NutriPlan AI premium frontend.

Exposes the core agentic + repository functionality over REST + SSE.
All heavy logic (agents, safety, LLM) remains in the core package.
"""

from .main import app  # re-export for uvicorn

__all__ = ["app"]

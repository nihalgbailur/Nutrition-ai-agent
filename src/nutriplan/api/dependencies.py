from __future__ import annotations

from functools import lru_cache

from nutriplan.db.repository import Repository


# --- Repository (process lifetime for local app) ---
@lru_cache(maxsize=1)
def get_repository() -> Repository:
    """Singleton-ish repository for the process (local SQLite)."""
    return Repository()


# --- Agent status (simple module state; sufficient for local single-user) ---
# In the premium frontend we primarily drive status from invoke results + client-side
# narrative loaders. This is kept for parity / any direct consumers of old helpers.
_agent_status: str = ""


def get_current_agent_status() -> str:
    return _agent_status


def set_current_agent_status(name: str, message: str = "") -> None:
    global _agent_status
    _agent_status = f"{name}: {message}" if message else name

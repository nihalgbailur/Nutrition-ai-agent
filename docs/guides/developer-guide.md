# Developer Guide

This guide is for contributors and developers who want to understand, extend, or run the NutriPlan AI codebase locally.

## Project Philosophy

NutriPlan AI demonstrates a **clean separation** between:

- A powerful, reusable **agentic core** (Python + LangGraph)
- A thin **delivery layer** (FastAPI)
- A delightful **consumer UI** (Next.js premium frontend)

The agents, safety rules, and knowledge base are the valuable, testable heart of the system. The UI can evolve independently.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (strongly recommended)
- Node.js 18+ + npm
- (Optional but recommended) Ollama for local LLM development
- Git

## Initial Setup

```bash
git clone https://github.com/nihalgbailur/Nutrition-ai-agent.git
cd Nutrition-ai-agent

# Python environment + deps
uv sync

# Optional: dev extras for testing
uv sync --extra dev

# Frontend
cd frontend
npm install
```

## Running for Development

### Recommended (Premium Experience)

```bash
# Terminal 1 - Backend API
uv run uvicorn src.nutriplan.api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

- Frontend: http://localhost:3000 (talks to API via proxy in dev)
- API docs (Swagger): http://localhost:8000/docs (or /redoc)

### Legacy Streamlit (for comparison)

```bash
uv run streamlit run src/nutriplan/main.py
```

## Key Commands

```bash
# Python tests
uv run pytest

# Run with verbose + coverage
uv run pytest -v --cov=src/nutriplan

# Load / reload synthetic data
uv run python scripts/load_database.py

# Format / lint (add your preferred tools)
uv run ruff check src/
uv run ruff format src/
```

Frontend:

```bash
cd frontend
npm run dev
npm run build
npm run lint
```

## Code Organization

### Backend (`src/nutriplan/`)

- **agents/** — The agentic core (most important to understand)
  - `graph.py` — Graph construction and the public `invoke_graph(...)` entrypoint. Contains all routing logic.
  - `nodes.py` — One function per agent. Each returns a dict that updates the shared `NutriPlanState`.
  - `state.py` — The single source of truth TypedDict passed between agents.
- **api/** — FastAPI delivery layer (keep this thin!)
  - Routers call `invoke_graph`, handle safety results, persist via the repository, and return `active_agent` so the UI can show progress.
- **db/repository.py** — All persistence. Uses SQLite + JSON for flexibility. Easy to swap for Postgres later.
- **llm/** — Abstraction over LiteLLM + streaming helpers + template fallbacks.
- **knowledge/** — The Indian packaged foods KB (matching + gentle messaging).
- **safety/** — Non-negotiable guardrails (allergen filter is deterministic code, not LLM).
- **models/schemas.py** — All Pydantic models (shared between agents, API, and frontend types).
- **config.py** — Paths, disclaimers, token limits, etc.

**Important Pattern**: Most "business logic" lives in nodes or the graph. The API layer is mostly plumbing + persistence.

### Frontend (`frontend/`)

- `app/` — Pages + layout (App Router). Each major feature has its own route.
- `components/` — Reusable pieces (keep them small and focused).
- `lib/api.ts` — Central typed client for the backend. Update this when adding new endpoints.
- `lib/types.ts` — Mirrors of key Pydantic models (keep in sync manually or generate later).
- `public/images/` & `public/videos/` — All custom-generated assets (do not commit huge files unnecessarily).

Theming lives almost entirely in `globals.css` via CSS custom properties (`--np-*`). Dark mode is handled by `.dark` overrides.

Animations are concentrated in `framer-motion` usage — prefer spring-based transitions for premium feel.

## Adding a New Feature (Example: "Favorites")

1. **Backend**:
   - Add a `Favorite` model in `models/schemas.py`.
   - Extend the Repository with `save_favorite`, `list_favorites`, etc.
   - Create a new router or add to an existing one (e.g. `routers/favorites.py`).
   - If it needs agents, add a new intent + node in the graph.

2. **Frontend**:
   - Add a new page or section.
   - Add methods to `lib/api.ts`.
   - Add types to `lib/types.ts`.
   - Use existing patterns for loading states, toasts, and animations.

3. **Safety**: If the feature touches user data or generation, ensure SafetyGate still runs.

## Working with Agents

The best way to understand the agents is to read `agents/graph.py` and `agents/nodes.py` side-by-side while calling `invoke_graph` from a test or the Python REPL.

Example exploration:

```python
from nutriplan.agents.graph import invoke_graph
from nutriplan.db.repository import Repository
from nutriplan.utils.seed import load_demo_data

repo = Repository()
load_demo_data(repo)
profile = repo.get_profile()
pantry = repo.list_pantry()

result = invoke_graph("generate_recipes", profile, pantry, user_text="quick dinner")
print(result["active_agent"])
print(len(result.get("recipes", [])))
```

You can inspect `result["kb_insights"]`, safety results, etc.

## Adding or Updating the Knowledge Base

The KB lives in `data/indian_packaged_foods_knowledge_base.json` + synthetic additions.

The matching logic is in `knowledge/packaged_foods.py` (uses rapidfuzz).

When you change the KB, re-run InventoryAgent on existing pantries to see updated insights.

## Testing

- Unit tests live in `tests/`.
- Focus on safety (`test_safety.py`), KB matching (`test_kb.py`), and LLM client behavior (with mocks for fallbacks).
- The agents themselves are best tested via integration-style calls to `invoke_graph` + assertions on the returned state.

## Environment Variables

See `.env.example`. Key ones:

- `XAI_API_KEY` or `OPENAI_API_KEY`
- `OLLAMA_HOST`, `OLLAMA_MODEL`
- `LITELLM_MODEL`

The app gracefully degrades when nothing is configured.

## Common Development Tasks

**Regenerate OpenAPI spec** (after changing routers or models):

```bash
uv run python -c "
from src.nutriplan.api.main import app
import json
with open('docs/api/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
"
```

**Update frontend types** after changing Pydantic models:

Manually sync `frontend/lib/types.ts` (or write a small generator script later).

**Add a new custom image/video**:

1. Use the image generation tools (or place approved assets in `frontend/public/images/` and `public/videos/`).
2. Reference them in pages/components.
3. Optimize file sizes.

## Contribution Guidelines

1. Keep the agentic core pure (minimal dependencies on FastAPI or UI concerns).
2. New agent nodes should return only state updates (no side effects — persistence happens in the caller).
3. All user-facing text must go through the disclaimer/safety system where appropriate.
4. Prefer structured output + Pydantic validation over free-text LLM responses.
5. When adding UI features, also consider the loading narrative (show the agent pipeline).
6. Dark mode and accessibility matter — test both themes and keyboard navigation.

## Debugging Tips

- Set `set_current_agent_status` calls are visible in the UI via the `active_agent` field returned by most generate endpoints.
- For chat, look at `detect_chat_agent` and the fast-mode vs streaming paths.
- The `lifespan` in `api/main.py` auto-seeds on empty DB — useful for fresh dev containers.
- Check the "How it works" page in the running app — it has a live visual of the agent flow.

## Future Ideas (Good First Contributions)

- Persistent chat history (new table + endpoints).
- Export weekly plan to PDF / calendar.
- Vision-based pantry upload (photo → ingredients) as a new agent/tool.
- Family/multi-profile support.
- More sophisticated RAG over the txt corpora.
- Docker Compose for one-command local run.
- CI that runs tests + regenerates docs + type-checks frontend.

## Resources

- LangGraph docs (for the agent graph)
- FastAPI + Pydantic docs
- Next.js App Router + Tailwind best practices
- The original `NutriPlan_AI_PRD.md` for product intent and safety rules

Happy hacking! The agentic core is powerful and the UI is a joy to extend. Focus on making the collaboration between agents visible and delightful.
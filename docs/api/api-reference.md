# NutriPlan AI API Reference

The backend exposes a REST + SSE API under the `/api` prefix. It is intentionally thin — most logic lives in the LangGraph agents.

**Base URL (dev)**: `http://localhost:8000`

**Interactive Docs**: Visit http://localhost:8000/docs (Swagger UI) or http://localhost:8000/redoc after starting the server.

The canonical machine-readable spec lives at `docs/api/openapi.json` (generated from the running FastAPI app).

## Authentication

None in the current local-first design. All endpoints are open (CORS restricted to localhost origins in dev).

For future multi-user deployments, add JWT / API keys in the API layer without changing the agent core.

## Core Endpoints

### Profile

| Method | Path            | Description                          | Key Models          |
|--------|-----------------|--------------------------------------|---------------------|
| GET    | /api/profile    | Get the latest user profile (or null) | `UserProfile`      |
| POST   | /api/profile    | Save/update profile (runs ProfileManager + SafetyGate) | `UserProfile` |

**Notes**:
- Saving a profile with medical notes may trigger a safety redirect.
- The frontend should refetch after save.

### Pantry

| Method | Path                  | Description                                      | Key Models       |
|--------|-----------------------|--------------------------------------------------|------------------|
| GET    | /api/pantry           | List all pantry items (newest first)             | `PantryItem[]`   |
| POST   | /api/pantry           | Add a new pantry item                            | `PantryItem`     |
| DELETE | /api/pantry/{item_id} | Delete a specific item                           | -                |
| POST   | /api/pantry/sync      | Run InventoryAgent (re-prioritize + KB insights) | `{pantry, kb_insights}` |

**Notes**:
- `sync` is the main way to get packaged food insights and reordering.
- Expiry dates are optional (`YYYY-MM-DD` or full ISO).

### Recipes

| Method | Path                  | Description                                      | Key Models          |
|--------|-----------------------|--------------------------------------------------|---------------------|
| GET    | /api/recipes          | List recently generated recipes                  | `Recipe[]`          |
| POST   | /api/recipes/generate | Run RecipeCreator (optionally with a query)      | `{recipes, used_fallback, active_agent}` |

**Notes**:
- Recipes are personalized to current profile + pantry.
- Hard allergen filtering + output validation always applied.
- Returns `active_agent` for UI progress display.

### Weekly Plan (Planner)

| Method | Path                | Description                                      | Key Models                  |
|--------|---------------------|--------------------------------------------------|-----------------------------|
| GET    | /api/plan           | Get the latest weekly plan (or null)             | `WeeklyMealPlan \| null`    |
| POST   | /api/plan/generate  | Run full pipeline (Inventory → RecipeCreator → MealPlanner). Requires confirmation if health flags set. | `{weekly_plan, used_fallback, active_agent, compromises, leftover_strategy}` |

**Notes**:
- The request body is `{ "confirmed": boolean }`.
- If health flags are set and `confirmed` is false, returns 400 with `needs_confirmation`.
- The planner also saves any recipes it generated internally.

### Shopping List

| Method | Path                     | Description                                      | Key Models               |
|--------|--------------------------|--------------------------------------------------|--------------------------|
| GET    | /api/shopping            | Get the latest shopping list (or null)           | `ShoppingList \| null`   |
| POST   | /api/shopping/generate   | Run ShoppingListOptimizer from the latest plan   | `{shopping_list, active_agent}` |

**Notes**:
- Requires an existing weekly plan.
- Items include `suggested_swap` when the KB has a better alternative.

### Feedback

| Method | Path          | Description                                      | Key Models            |
|--------|---------------|--------------------------------------------------|-----------------------|
| GET    | /api/feedback | List recent feedback records                     | `FeedbackRecord[]`    |
| POST   | /api/feedback | Submit feedback (runs FeedbackAgent)             | `FeedbackRecord`      |

**Notes**:
- Submitting "not suitable" or low ratings updates the user's `disliked_ingredients` and `limit_packaged_snacks` via the agent.

### Chat

| Method | Path             | Description                                      | Behavior                     |
|--------|------------------|--------------------------------------------------|------------------------------|
| POST   | /api/chat        | Non-streaming chat reply                         | Returns `{agent, text}`      |
| POST   | /api/chat/stream | Streaming chat (SSE)                             | Events: `agent`, `token`, `done`, `error` |

**Request body** (both):
```json
{
  "message": "string",
  "fast_mode": boolean   // default false; uses templates instantly
}
```

**SSE Event Format** (for `/chat/stream`):
```
data: {"type": "agent", "agent": "InventoryAgent"}

data: {"type": "token", "text": "partial..."}

data: {"type": "done", "full": "complete response"}
```

The backend uses `detect_chat_agent` to pick the right persona and may inject KB context or safety messages.

### System / Admin

| Method | Path                        | Description                              |
|--------|-----------------------------|------------------------------------------|
| GET    | /api/system/status          | LLM availability, provider, Ollama status, current agent |
| POST   | /api/system/seed/demo       | Load small demo data                     |
| POST   | /api/system/seed/full       | Load full synthetic database             |
| POST   | /api/system/reset-generated | Clear recipes, plans, shopping, feedback, KB cache (keeps profile + pantry) |

Also available:
- `GET /health` — Simple health check with DB path.
- `GET /docs` — Swagger UI (redirect from root).

## Common Response Patterns

Most generate endpoints return an object containing:

- `active_agent`: string — which agent just finished (useful for UI pills / loading states)
- `used_fallback`: boolean — whether LLM was unavailable
- Domain object(s) (`weekly_plan`, `recipes`, `shopping_list`, etc.)
- Optional `kb_insights`, `compromises`, `leftover_strategy`, `safety` details

Safety redirects are returned as HTTP 400 with:
```json
{
  "detail": {
    "safety": { "action": "redirect", "message": "...", "category": "..." }
  }
}
```

## Data Models (Key Pydantic Schemas)

See `src/nutriplan/models/schemas.py` for the full definitions. Major ones exposed in the API:

- `UserProfile` + `HealthFlags`
- `PantryItem`
- `Recipe` (with `IngredientLine`, `NutritionEstimate`)
- `WeeklyMealPlan` (with `DayMeals` → `MealSlot`)
- `ShoppingList` (with `ShoppingListItem`)
- `FeedbackRecord`
- `KBInsight`
- `SafetyResult`

The frontend mirrors the important ones in `frontend/lib/types.ts`.

## Error Handling

- 400: Validation, safety redirects, missing prerequisites (e.g. "Generate a weekly plan first")
- 422: Pydantic validation errors (FastAPI standard)
- The UI surfaces these nicely via Sonner toasts.

## Streaming & Real-time

Only the chat endpoint uses SSE. All other operations are synchronous (the graph runs to completion). Long-running generations are expected (10-60s on first Ollama load) — the frontend shows rich multi-step loading animations.

## Versioning & Stability

Current version: 1.1.0 (see `main.py`).

The API is intentionally not versioned in the URL yet (`/api` instead of `/api/v1`) because this is a local-first desktop-style app. Add versioning when moving to multi-user hosted deployments.

## Generating an Updated Spec

After changing routers, models, or adding endpoints:

```bash
uv run python -c '
from src.nutriplan.api.main import app
import json
with open("docs/api/openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)
print("openapi.json regenerated")
'
```

Then restart the server and visit `/docs` to verify.

For a static HTML version of the docs, you can use Redocly CLI or similar tools against the JSON.

## Client Examples

### TypeScript / Next.js (current frontend pattern)

```ts
import { api } from '@/lib/api';

const plan = await api.generatePlan(true);  // confirmed=true
```

### Python (for scripts or testing)

```python
import requests

resp = requests.post(
    "http://localhost:8000/api/plan/generate",
    json={"confirmed": True}
)
print(resp.json()["weekly_plan"]["days"][0])
```

### cURL

```bash
curl -X POST http://localhost:8000/api/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "quick dinner"}'
```

## Related Documentation

- `docs/architecture/system-architecture.md` — Full system and agent flow diagrams
- `docs/guides/user-guide.md` — End-user walkthrough
- `docs/guides/developer-guide.md` — How to extend the system
- Root `README.md` — Quick start and feature overview
- The in-app **How it works** page (includes live visuals and the spices video)
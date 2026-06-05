# NutriPlan AI

Agentic meal planning web app for Indian households. Plans meals around your pantry, surfaces smarter packaged-food swaps via a curated knowledge base, and enforces strict safety boundaries (no medical advice, hard allergen filtering).

## Features

- **Profile & onboarding** — diet style, goals, allergies, cuisine preferences, health flags
- **Pantry management** — CRUD inventory with Indian packaged-foods KB matching (Maggi, Haldiram, Parle-G, etc.)
- **Recipe generation** — LangGraph `RecipeCreator` with approximate nutrition labels
- **Weekly meal planner** — 7-day B/L/D plan with leftover notes
- **Shopping list** — consolidates needs, removes pantry items, suggests KB swaps
- **Feedback loop** — ratings and “not suitable” adjust future preferences

## Agents (LangGraph)

| Agent | Purpose |
|-------|---------|
| ProfileManager | Preferences & health flags |
| InventoryAgent | Pantry scan + KB insights |
| RecipeCreator | Personalized recipes |
| MealPlanner | Weekly schedule |
| ShoppingListOptimizer | Smart shopping list |
| FeedbackAgent | Learning from feedback |

## Quick start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Install & run

```bash
cd nutripan-ai
uv sync
cp .env.example .env   # optional: add XAI_API_KEY for live LLM
uv run streamlit run src/nutriplan/main.py
```

Open the URL shown in the terminal (usually http://localhost:8501).

### Premium frontend (recommended — customers love it)
The original Streamlit UI has been replaced by a premium Next.js + Tailwind frontend + FastAPI backend for a much higher-quality, modern experience while keeping every agent, safety rule, and local SQLite behavior identical.

The UI now features a rich library of custom-generated beautiful food photography (10+ images) and multiple short cinematic videos (steaming dal, spices pour) plus deep framer-motion design animations throughout cards, lists, loading states, chat, navigation, hero, counters and more. Full dark mode toggle (with beautiful adaptation in both themes) using next-themes. All imagery was created specifically for a warm, wholesome, luxurious Indian home-cooking aesthetic.

**Legacy Streamlit** is still present for transition (you can still run `uv run streamlit run src/nutriplan/main.py`). New development happens on the Next.js frontend.

```bash
cd nutripan-ai
uv sync
cp .env.example .env   # optional but recommended

# Terminal 1: start the backend API (FastAPI)
uv run uvicorn src.nutriplan.api.main:app --reload --port 8000

# Terminal 2: start the frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The frontend talks to the API on 8000.

**Same data & agents**: everything (agents, safety, pantry, plans, chat streaming, KB, local db) is identical under the hood. Only the UI layer changed to feel premium.

**No SQLite app required** — data lives in `data/nutriplan.db`. On first launch the app auto-loads synthetic data if the DB is empty. To reload manually:

```bash
uv run python scripts/load_database.py
```

Use **Chat** (in the premium frontend or legacy Streamlit sidebar) to ask questions about meals, pantry items, packaged food swaps, and planning.

### Demo & synthetic database

**Small demo:** Profile → **Load demo data (small)** — Priya + 18 pantry items.

**Full synthetic DB:** Profile → **Load full synthetic database** — loads from `data/synthetic/` into SQLite:

| File | Contents |
|------|----------|
| `profiles.json` | 3 users (Priya, Rahul, Meera) |
| `pantry_items.json` | 44 items (fresh + packaged) |
| `recipes.json` | 8 recipes |
| `meal_plan.json` | 7-day plan |
| `shopping_list.json` | Sample list |
| `feedback.json` | Sample ratings |
| `packaged_foods_synthetic.json` | Extra KB categories (merged with main KB) |
| `txt/*.txt` | Text corpora for search / future RAG |

1. Go to **Profile** → choose a load button above
2. **Pantry** → **Run InventoryAgent** to see KB insights on packaged items
3. **Recipes** or **Weekly Plan** → generate (works without API key using fallback templates)

### LLM configuration

**Local Ollama (recommended for dev)** — no cloud API key needed:

```bash
ollama serve          # if not already running (macOS app does this automatically)
ollama list           # see installed models
```

The app auto-detects Ollama at `http://127.0.0.1:11434` and uses the first model from `ollama list` (or set in `.env`):

```bash
cp .env.example .env
# OLLAMA_MODEL=qwen2.5-coder:3b
```

**Production / Grok** — set when you deploy:

```bash
export XAI_API_KEY=your_key
export LITELLM_MODEL=xai/grok-beta
```

Without Ollama or any API key, the app uses **fallback templates** so flows still work offline.

## Safety & disclaimers

- All recipes and plans show the PRD-mandated disclaimer
- Nutrition is always labeled **Approximate estimates only**
- Allergies are filtered in code — not left to the LLM alone
- Medical / pregnancy / medication queries are redirected per PRD Section 11
- Health flags require explicit confirmation before weekly plan generation

## Project structure

```
src/nutriplan/
  agents/       # LangGraph nodes & graph
  db/           # SQLite persistence
  knowledge/    # Indian packaged foods KB
  llm/          # LiteLLM client + fallbacks
  models/       # Pydantic schemas
  safety/       # Guardrails & allergen filter
  api/          # FastAPI routers + main (premium frontend backend)
  ui/           # Legacy Streamlit pages & CSS (being phased out)
data/
  indian_packaged_foods_knowledge_base.json
  sample/       # demo_profile.json, demo_pantry.json
```

## Tests

```bash
uv sync --extra dev
uv run pytest
```

## Data privacy

User profile, pantry, plans, and feedback are stored locally in `data/nutriplan.db`. Only LLM API calls leave your machine when a key is configured.

## License

MIT (MVP)
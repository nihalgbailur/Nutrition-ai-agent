# NutriPlan AI

**Your intelligent kitchen companion that plans meals around what you already have.**

NutriPlan AI is a fully **agentic** meal planning application for Indian households. It understands your pantry, dietary preferences, allergies, and health goals — then uses a team of specialized AI agents (powered by LangGraph) to generate personalized recipes, weekly plans, and smart shopping lists with strict safety guardrails.

The experience features a **premium Next.js frontend** with rich custom food photography, cinematic videos, smooth animations, and a beautiful dark mode.

![NutriPlan AI](https://github.com/nihalgbailur/Nutrition-ai-agent/blob/main/frontend/public/images/hero-kitchen.jpg)

## ✨ Why It's Special

- **Truly Agentic**: Not a single prompt — a graph of collaborating agents that plan, use tools (Indian packaged foods knowledge base), enforce safety, and learn from your feedback.
- **Premium UI**: Custom-generated appetizing imagery (10+ photos + videos), framer-motion animations, rich cards, animated agent progress, and full dark mode toggle.
- **Safe by Design**: Hard allergen filtering, medical query redirects, approximate nutrition only, and explicit disclaimers.
- **Local-first**: Everything runs on your machine. Your data stays in `data/nutriplan.db`.

## Features

- **Smart Profile & Onboarding** — Diet style, goals, allergies, cuisine preferences, spice level, budget, cooking time, and health flags.
- **Pantry Management** — Add/edit/delete items with automatic matching against a curated Indian packaged foods knowledge base (Maggi, Haldiram, Parle-G, etc.) for gentle swap suggestions.
- **Recipe Generation** — Agent-powered personalized recipes grounded in your actual inventory + safety rules.
- **7-Day Meal Planner** — Balanced breakfast/lunch/dinner plans with leftover reuse, variety, and practical compromises.
- **Smart Shopping List** — Consolidated list that removes pantry items and suggests better alternatives.
- **Feedback Loop** — Rate recipes or mark “not suitable” — the system actually updates your preferences.
- **Agentic Chat** — Ask anything. The chat detects intent and responds in the voice of the relevant specialist agent.

## Agent Architecture (LangGraph)

NutriPlan AI uses a **StateGraph** with specialized agents that collaborate:

| Agent                    | Role |
|--------------------------|------|
| **SafetyGate**           | First line of defense. Blocks or redirects medical/therapeutic queries. |
| **ProfileManager**       | Manages long-term preferences and health flags. |
| **InventoryAgent**       | Analyzes pantry, prioritizes items, and surfaces KB insights. |
| **RecipeCreator**        | Generates safe, pantry-based recipes with structured output + post-validation. |
| **MealPlanner**          | Builds coherent weekly plans with leftovers and compromises. |
| **ShoppingListOptimizer**| Creates consolidated lists with smart swaps. |
| **FeedbackAgent**        | Learns from ratings and updates your profile for future plans. |

**Typical flow** (e.g. Generate Weekly Plan):
SafetyGate → InventoryAgent → RecipeCreator → MealPlanner

The frontend surfaces exactly which agent is working with beautiful loading narratives.

## Quick Start (Recommended)

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js + npm (for frontend)
- (Optional) Ollama for local LLM

### Run the Premium Experience

```bash
# Clone
git clone https://github.com/nihalgbailur/Nutrition-ai-agent.git
cd Nutrition-ai-agent

# Backend dependencies
uv sync

# 1. Start the FastAPI backend (Terminal 1)
uv run uvicorn src.nutriplan.api.main:app --reload --port 8000

# 2. Start the Next.js frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

Toggle dark mode using the ☀️/🌙 button in the header.

### Alternative: Legacy Streamlit UI (for transition)

```bash
uv run streamlit run src/nutriplan/main.py
```

## Loading Demo Data

On first run, the app auto-loads synthetic data if the database is empty.

From the **Profile** page you can also:
- **Load demo data (small)**
- **Load full synthetic database**

This gives you profiles, pantry items, recipes, and a sample plan instantly.

## LLM Configuration

The system works in three modes:

1. **Local Ollama** (recommended for development)
2. **Cloud** (Grok via XAI_API_KEY or OpenAI)
3. **Fallback templates** (works completely offline)

See `.env.example` for configuration.

## Project Structure

```
.
├── src/nutriplan/
│   ├── agents/          # LangGraph graph + nodes (the agentic brain)
│   ├── api/             # FastAPI backend for the premium frontend
│   ├── db/              # SQLite repository
│   ├── knowledge/       # Indian packaged foods KB
│   ├── llm/             # LiteLLM client + fallbacks + chat
│   ├── models/          # Pydantic schemas
│   ├── safety/          # Guardrails and allergen filtering
│   ├── main.py          # Legacy Streamlit entrypoint
│   └── utils/
├── frontend/            # Next.js 16 premium UI (recommended)
├── data/                # SQLite + synthetic/demo data
└── scripts/
```

## Safety & Disclaimers

This is **general meal inspiration only**. 

- Nutrition estimates are approximate.
- Strict code-level allergen filtering (not just prompts).
- Medical, pregnancy, or therapeutic queries are redirected.
- Every recipe and plan shows a clear disclaimer.

## Development

```bash
# Python tests
uv sync --extra dev
uv run pytest

# Frontend
cd frontend
npm run dev
npm run build
```

## Data Privacy

All user data lives locally in `data/nutriplan.db`. Only LLM inference calls (when configured) leave your machine.

## Documentation

Comprehensive documentation is maintained in the `docs/` folder:

- **[docs/README.md](docs/README.md)** — Documentation index and overview
- **[API Reference](docs/api/api-reference.md)** — All endpoints, models, and examples (plus the live Swagger UI at `/docs`)
- **[System Architecture](docs/architecture/system-architecture.md)** — Mermaid diagrams, data flows, component relationships
- **[User Guide](docs/guides/user-guide.md)** — Step-by-step walkthrough of the premium experience
- **[Developer Guide](docs/guides/developer-guide.md)** — Setup, extending agents/UI, contribution guidelines

A script is provided to keep the OpenAPI spec in sync:

```bash
uv run python scripts/generate_openapi.py
```

The in-app **How it works** page (`/how-it-works`) also contains rich explanations and visuals (including the spices video).

## License

MIT

---

Made with ❤️ for busy Indian home cooks who want less decision fatigue and more delicious, low-waste meals. 

**Try it →** Clone the repo and run the two-terminal setup above. The premium UI with dark mode and beautiful food imagery makes the agentic experience genuinely delightful.
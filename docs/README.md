# NutriPlan AI Documentation

This folder contains living documentation for NutriPlan AI, an agentic meal planning application for Indian households.

The documentation is generated and maintained alongside the code using AI-assisted analysis of the actual source (FastAPI routers, LangGraph agents, Next.js components, Pydantic models, etc.).

## Documentation Structure

- **[API Documentation](api/)** — Complete reference for the FastAPI backend
  - `api-reference.md` — Human-readable summary of all endpoints
  - `openapi.json` — Machine-readable OpenAPI 3.0 spec (auto-generated from the running app)
  - Interactive docs available at `/docs` when the server is running

- **[Architecture Documentation](architecture/)** — System and component design
  - `system-architecture.md` — High-level diagrams, data flows, technology choices, and rationale (includes Mermaid diagrams)

- **[User Guides](guides/)** — End-user focused
  - `user-guide.md` — Step-by-step walkthrough of the premium UI (with dark mode, visuals, and agentic flows)

- **[Developer Guides](guides/)** — For contributors and extenders
  - `developer-guide.md` — Setup, architecture deep dive, how to add features, testing, contribution guidelines

## Quick Links

- **Main Project README** (root): Setup, quick start, features, LLM config, safety
- **Frontend README**: UI-specific tech stack and development notes
- **In-App "How it works" page**: Visual agent flow + the spices video (best experienced live)
- **Live API Docs**: Start the backend and visit http://localhost:8000/docs

## How Documentation is Kept Up to Date

1. The OpenAPI spec is generated directly from the FastAPI app (`src/nutriplan/api/main.py` + routers + Pydantic models).
2. Architecture and guides are written against the real code (agents/graph.py, nodes.py, frontend components, etc.).
3. When you change routers, models, or agent nodes, re-run the OpenAPI export script (see api-reference.md).
4. For major changes, re-generate or update the relevant docs using the same analysis process that produced these files.

## Key Concepts Highlighted Across Docs

- **Agentic Core**: LangGraph StateGraph with SafetyGate + 6 specialized agents that collaborate, use tools (KB), and learn.
- **Safety by Design**: Deterministic code-level filters + guardrails before any creative LLM work.
- **Premium Experience**: Next.js frontend with 10+ custom food images, 2 videos, rich framer-motion animations, and full dark mode.
- **Local-First**: Everything (including the SQLite DB) stays on the user's machine.
- **Graceful Degradation**: Full functionality via template fallbacks when no LLM is available.

## Contributing to Documentation

- Keep examples accurate to the current code.
- Update diagrams when the agent graph routing or major components change.
- When adding new UI pages or API endpoints, add corresponding sections to the user guide and API reference.
- Prefer practical, copy-pasteable examples.

## Regenerating Key Artifacts

**OpenAPI spec** (after API changes):

```bash
uv run python scripts/generate_openapi.py
```

This is the recommended way (the script is in `scripts/generate_openapi.py` and handles path setup correctly).

**Full documentation refresh**: Re-run the documentation generation process (this folder was produced by `/doc-generate` against the current codebase). Major changes to agents, routers, or UI components should trigger updates to the relevant docs.

## Documentation Automation (CI/CD)

You can add a GitHub Action to automatically regenerate and deploy docs on changes to `src/**` or `frontend/**`:

```yaml
# .github/workflows/docs.yml (example)
name: Generate & Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'frontend/**'
      - 'scripts/generate_openapi.py'

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: pip install -r requirements-docs.txt || true   # add if you have a docs requirements file
      - run: uv run python scripts/generate_openapi.py
      - run: cd frontend && npm ci && npm run build   # if you want to include frontend docs
      # Deploy step (GitHub Pages, Vercel, etc.)
```

See the reference examples in the skill for more complete CI patterns, Redocly builds, Sphinx, coverage checks, etc.

For the absolute latest experience, start the app and explore the in-app pages — many explanations and visuals are embedded directly in the product (especially the "How it works" page).

---

*Documentation generated for the premium agentic version of NutriPlan AI (FastAPI + Next.js frontend with rich visuals and dark mode).*
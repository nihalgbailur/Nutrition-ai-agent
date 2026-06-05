# NutriPlan AI User Guide

Welcome to NutriPlan AI — your intelligent kitchen companion that plans meals around what you already have.

This guide will walk you through the premium experience (Next.js frontend with dark mode, rich food photography, and smooth animations).

## Getting Started

### 1. Launch the App

Run the two services (see the main README for exact commands):

```bash
# Terminal 1
uv run uvicorn src.nutriplan.api.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Open http://localhost:3000.

### 2. First Run Experience

- The app automatically loads synthetic demo data if the database is empty.
- You'll see a beautiful dashboard with metrics, today's plan preview (if any), and an inspiration gallery of appetizing Indian dishes.

**Tip**: Use the dark mode toggle (☀️/🌙 icon) in the top-right header for a luxurious dark theme.

### 3. Load Demo Data (Recommended for First Use)

Go to the **Profile** page.

- Click **"Load demo data (small)"** — loads Priya + 18 pantry items.
- Or **"Load full synthetic database"** — loads multiple users, 44 pantry items, recipes, plans, etc.

This gives you an instantly usable experience with realistic Indian household data.

## Core Workflows

### Profile & Onboarding

**Location**: `/profile`

1. Fill in your details:
   - Name, Diet style (Vegetarian, Vegan, Eggetarian, Non-Veg, Jain, etc.)
   - Health goal (Weight loss, Muscle gain, Maintenance, etc.)
   - Allergies (comma-separated)
   - Cuisine preferences
   - Spice level, max cook time, budget
2. Health profile flags (important for safety):
   - Medical condition
   - Pregnant/breastfeeding
   - Cooking for children or elderly

3. **Save Profile** — this invokes the ProfileManager agent (and SafetyGate if you added medical notes).

When health flags are active, you'll see prominent medical banners, and weekly plan generation will require an explicit confirmation checkbox.

### Pantry Management

**Location**: `/pantry`

- Add items with name, category, quantity, "packaged" flag, and optional expiry.
- See your list with KB badges for packaged items (e.g., concerns about Maggi or Haldiram).
- Click **"Run InventoryAgent (scan + prioritize + KB insights)"** — this runs the InventoryAgent, re-sorts your pantry, saves insights, and shows gentle swap suggestions.

The UI uses beautiful pantry/spice photography and staggered animations for list items.

### Generate Recipes

**Location**: `/recipes`

1. (Optional) Enter a query like "quick dinner" or "high protein".
2. Click **"Generate recipes (RecipeCreator)"**.
3. Watch the rich animated loading narrative:
   - InventoryAgent scanning...
   - RecipeCreator creating...
4. Browse the results as rich cards with relevant food photos (auto-matched to dish type).
5. Click a card to expand full ingredients, numbered steps, why it fits, KB notes, and disclaimer.

All recipes respect your profile, allergies (hard filtered in code), and pantry.

### Weekly Meal Planner (The Star Feature)

**Location**: `/planner`

1. If you have health flags set, check the confirmation box.
2. Click **"Generate weekly plan"**.
3. Enjoy the multi-step agent pipeline animation:
   - ✓ InventoryAgent
   - ✓ RecipeCreator
   - ⟳ MealPlanner (building with leftovers & variety)
4. View the beautiful 7-day breakdown with day cards, meal slots, leftover notes, and compromise statements.

The plan is saved and can be used to generate a shopping list.

### Shopping List

**Location**: `/shopping`

- Requires an existing weekly plan.
- Click **"Generate shopping list (ShoppingListOptimizer)"**.
- See categorized items with suggested swaps (from the KB).
- Use the "Copy list to clipboard" button (tab-separated for easy pasting into notes/spreadsheets).

### Chat (Agentic Conversation)

**Location**: `/chat`

- Type natural questions: "quick veg dinner with dal", "swaps for Maggi", "what can I make with what's in my pantry?"
- The system uses `detect_chat_agent` to route to the right persona (InventoryAgent, RecipeCreator, etc.).
- Responses stream in real-time (or instant in "Fast mode").
- Each message shows an **AgentPill** so you know which specialist is "talking".
- Fast mode uses smart templates (great for local Ollama cold starts); full mode uses the actual LLM.

History is maintained in the browser for the session.

### Feedback & Learning

**Location**: `/feedback`

- Select a generated recipe.
- Rate it (1-5), mark "I made this", or "Not suitable for me" + reason.
- Submit — this invokes the **FeedbackAgent**, which updates your profile (adds to disliked ingredients, toggles packaged snack limits, etc.).
- Future plans will respect this learning.

### How It Works (Learn the Magic)

**Location**: `/how-it-works`

- Read the agent table and flow explanation.
- See the visual agent pipeline with the beautiful spices video.
- Understand why this is truly agentic (multi-agent collaboration + tools + safety + learning) rather than "just an LLM".

## Visual & Interaction Highlights

- **Rich Media**: Custom-generated appetizing photos of real Indian dishes and a pantry/spices aesthetic. Two cinematic videos (steam + spices) enhance the experience.
- **Animations**: Smooth page transitions, card lifts/hovers, staggered list reveals, animated counters on the dashboard, pulsing active steps in loading states, and more — powered by framer-motion.
- **Dark Mode**: Toggle anytime. The entire design system (greens, golds, cards, text, warnings) adapts elegantly.
- **Responsive**: Works great on desktop and tablet (sidebar collapses gracefully).

## Common Tips

- **No LLM?** The app works 100% with fallback templates. Great for offline or first-time Ollama use.
- **Safety First**: If you set health flags, always confirm before generating plans. The agents will never suggest allergens.
- **KB Power**: Add packaged items (Maggi, Parle-G, etc.) to your pantry and run InventoryAgent — you'll get non-shaming, practical swap ideas.
- **Learning Compounds**: The more feedback you give, the smarter future plans become.
- **Data Location**: Everything is in `data/nutriplan.db` (local SQLite). Delete the file to start fresh.

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| "Set up your profile first" | No profile in DB | Go to Profile and load demo or save one |
| Slow first generation | Ollama model loading | Use Fast mode in chat, or wait (subsequent calls are faster) |
| No LLM / fallback warnings | No Ollama running + no API key | Start `ollama serve` or add XAI_API_KEY to .env |
| Medical banner keeps appearing | Health flags enabled | Edit profile or confirm the checkbox when generating plans |
| Chat not streaming | Browser / network | Try Fast mode; check backend logs |

For more technical details (architecture, API, development), see the other documents in the `docs/` folder or the root README.

Enjoy planning delicious, low-waste, personalized Indian meals! 🍛🥗

**Pro tip**: After loading demo data, immediately go to Pantry → Run InventoryAgent, then generate a Weekly Plan. You'll see the full agent collaboration in action with beautiful visuals.
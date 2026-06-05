import streamlit as st

from nutriplan.ui.components.disclaimer import render_disclaimer


def render() -> None:
    st.header("How NutriPlan AI works")
    st.markdown(
        """
NutriPlan AI uses **LangGraph** to orchestrate specialized agents:

| Agent | Role |
|-------|------|
| **ProfileManager** | Stores diet style, goals, allergies, health flags |
| **InventoryAgent** | Scans pantry; matches Indian packaged foods KB |
| **RecipeCreator** | Generates recipes grounded in pantry + safety rules |
| **MealPlanner** | Builds a 7-day plan with leftover awareness |
| **ShoppingListOptimizer** | Lists missing items; suggests KB swaps |
| **FeedbackAgent** | Learns from ratings and “not suitable” flags |

**Indian Packaged Foods KB** — When your pantry includes items like Maggi, Haldiram bhujia, or Parle-G,
agents surface nutritional concerns (e.g. high sodium/sugar) and gentle swap ideas (e.g. roasted makhana)
without shaming or giving medical advice.

**Safety** — Allergies are filtered deterministically. Medical conditions trigger disclaimers and redirects.
Nutrition numbers are always approximate estimates.
        """
    )
    st.code(
        """
User → Streamlit UI → LangGraph
                          ├─ SafetyGate
                          ├─ ProfileManager / InventoryAgent
                          ├─ RecipeCreator / MealPlanner
                          └─ ShoppingListOptimizer / FeedbackAgent
        """,
        language="text",
    )
    render_disclaimer()
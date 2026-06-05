import streamlit as st

from nutriplan.llm.client import llm_available, llm_provider_label
from nutriplan.llm.ollama_util import list_ollama_models, ollama_is_running
from nutriplan.ui.components.disclaimer import render_disclaimer, render_medical_banner
from nutriplan.ui.session import get_repo


def render() -> None:
    repo = get_repo()
    profile = repo.get_profile()
    pantry = repo.list_pantry()
    plan = repo.get_latest_meal_plan()
    insights = repo.get_kb_insights()

    st.markdown('<p class="hero-title">NutriPlan AI</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-sub">Your intelligent kitchen companion — plans meals around what you already have.</p>',
        unsafe_allow_html=True,
    )

    render_medical_banner(profile)
    render_disclaimer()

    db_path = repo.db_path
    st.caption(f"Local database file (no SQLite app needed): `{db_path}`")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pantry items", len(pantry))
    c2.metric("KB flags", len(insights))
    c3.metric("Saved recipes", len(repo.list_recipes()))
    c4.metric("LLM", llm_provider_label() if llm_available() else "Fallback mode")
    if ollama_is_running():
        st.caption(f"Ollama models on this machine: {', '.join(list_ollama_models())}")
    elif not llm_available():
        st.caption("Start Ollama (`ollama serve`) or add XAI_API_KEY for AI generation.")

    if plan and plan.days:
        today = plan.days[0]
        st.subheader("Today's plan preview")
        for meal in today.meals:
            st.markdown(f"**{meal.slot.title()}**: {meal.recipe_name}")

    st.info(
        "Quick start: load demo data from Profile, use **Chat** for questions, "
        "review Pantry KB badges, then generate Recipes or a Weekly Plan."
    )
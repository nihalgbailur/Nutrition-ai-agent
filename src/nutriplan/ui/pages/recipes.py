import streamlit as st

from nutriplan.agents.graph import invoke_graph
from nutriplan.ui.components.disclaimer import render_disclaimer, render_nutrition_label
from nutriplan.ui.session import get_repo, set_agent_status


def _render_recipe(recipe) -> None:
    st.markdown(f"### {recipe.name}")
    render_nutrition_label()
    n = recipe.nutrition
    st.markdown(
        f'<span class="nutrition-tag">~{n.calories or "?"} kcal</span>'
        f'<span class="nutrition-tag">Protein ~{n.protein_g or "?"}g</span>',
        unsafe_allow_html=True,
    )
    st.write("**Ingredients:**", ", ".join(f"{i.name} ({i.quantity})" for i in recipe.ingredients))
    st.write("**Steps:**")
    for i, step in enumerate(recipe.steps, 1):
        st.write(f"{i}. {step}")
    st.caption(recipe.why_fits)
    if recipe.kb_notes:
        st.info(recipe.kb_notes)
    st.markdown(f'<div class="disclaimer-box">{recipe.disclaimer}</div>', unsafe_allow_html=True)


def render() -> None:
    repo = get_repo()
    profile = repo.get_profile()
    if not profile:
        st.warning("Set up your profile first.")
        return

    st.header("Recipe suggestions")
    query = st.text_input("Optional question (e.g. quick dinner)", "")

    if st.button("Generate recipes (RecipeCreator)"):
        with st.status("InventoryAgent → RecipeCreator", expanded=True):
            set_agent_status("RecipeCreator")
            result = invoke_graph(
                "generate_recipes",
                profile,
                repo.list_pantry(),
                user_text=query,
            )
            if result.get("safety_result") and result["safety_result"].action == "redirect":
                st.error(result["safety_result"].message)
            elif result.get("recipes"):
                if result.get("kb_insights"):
                    repo.save_kb_insights(result["kb_insights"])
                repo.save_recipes(result["recipes"])
                if result.get("used_fallback"):
                    st.warning("LLM unavailable — showing template recipes. Start Ollama or add an API key.")
                st.success(f"Generated {len(result['recipes'])} recipes.")
            else:
                st.error(result.get("error", "Could not generate recipes."))
        st.rerun()

    for recipe in repo.list_recipes():
        with st.expander(recipe.name, expanded=False):
            _render_recipe(recipe)
            render_disclaimer()
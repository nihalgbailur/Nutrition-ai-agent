import streamlit as st

from nutriplan.agents.graph import invoke_graph
from nutriplan.ui.components.disclaimer import (
    render_disclaimer,
    render_medical_banner,
    require_medical_confirmation,
)
from nutriplan.ui.session import get_repo, set_agent_status


def render() -> None:
    repo = get_repo()
    profile = repo.get_profile()
    if not profile:
        st.warning("Set up your profile first.")
        return

    st.header("Weekly meal planner")
    render_medical_banner(profile)

    confirmed = require_medical_confirmation(profile, "plan_confirm")

    if st.button("Generate weekly plan", disabled=not confirmed):
        with st.status("InventoryAgent → RecipeCreator → MealPlanner", expanded=True):
            set_agent_status("MealPlanner")
            result = invoke_graph(
                "generate_weekly_plan",
                profile,
                repo.list_pantry(),
            )
            if result.get("safety_result") and result["safety_result"].action == "redirect":
                st.error(result["safety_result"].message)
            elif result.get("weekly_plan"):
                if result.get("kb_insights"):
                    repo.save_kb_insights(result["kb_insights"])
                if result.get("recipes"):
                    repo.save_recipes(result["recipes"])
                repo.save_meal_plan(result["weekly_plan"])
                if result.get("used_fallback"):
                    st.warning("Using fallback planner — set XAI_API_KEY for full AI plans.")
                st.success("Weekly plan ready.")
            else:
                st.error(result.get("error", "Planning failed."))
        st.rerun()

    plan = repo.get_latest_meal_plan()
    if not plan:
        st.info("No plan yet. Generate one above.")
        return

    if plan.compromises:
        st.caption(f"Compromises: {plan.compromises}")
    if plan.leftover_strategy:
        st.caption(f"Leftovers: {plan.leftover_strategy}")

    for day in plan.days:
        st.markdown(f"#### {day.day_label}")
        for meal in day.meals:
            leftover = f" (leftovers: {meal.uses_leftovers_from})" if meal.uses_leftovers_from else ""
            st.markdown(f"- **{meal.slot.title()}**: {meal.recipe_name}{leftover} — {meal.notes or ''}")

    st.markdown(f'<div class="disclaimer-box">{plan.disclaimer}</div>', unsafe_allow_html=True)
    render_disclaimer()
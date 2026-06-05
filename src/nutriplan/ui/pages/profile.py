import streamlit as st

from nutriplan.agents.graph import invoke_graph
from nutriplan.models.schemas import (
    BudgetLevel,
    DietStyle,
    HealthFlags,
    HealthGoal,
    SpiceLevel,
    UserProfile,
)
from nutriplan.ui.components.disclaimer import render_disclaimer, render_medical_banner
from nutriplan.ui.session import get_repo, set_agent_status
from nutriplan.utils.seed import load_demo_data, load_synthetic_database


def render() -> None:
    repo = get_repo()
    existing = repo.get_profile()
    st.header("Profile & onboarding")

    c1, c2 = st.columns(2)
    if c1.button("Load demo data (small)"):
        load_demo_data(repo)
        st.success("Demo profile + 18 pantry items loaded.")
        st.rerun()
    if c2.button("Load full synthetic database"):
        counts = load_synthetic_database(repo)
        st.success(
            f"Loaded: {counts['pantry_items']} pantry, {counts['recipes']} recipes, "
            f"{counts['meal_plan_days']}-day plan, {counts['kb_records']} KB records."
        )
        st.rerun()

    render_medical_banner(existing)

    with st.form("profile_form"):
        name = st.text_input("Name", value=existing.name if existing else "Nihal")
        diet = st.selectbox(
            "Diet style",
            [e.value for e in DietStyle],
            index=[e.value for e in DietStyle].index(existing.diet_style.value)
            if existing
            else 0,
        )
        goal = st.selectbox(
            "Health goal",
            [e.value for e in HealthGoal],
            index=[e.value for e in HealthGoal].index(existing.health_goal.value)
            if existing
            else 2,
        )
        allergies = st.text_input(
            "Allergies (comma-separated)",
            value=", ".join(existing.allergies) if existing else "",
        )
        cuisines = st.text_input(
            "Cuisine preferences (comma-separated)",
            value=", ".join(existing.cuisine_preferences) if existing else "North Indian, South Indian",
        )
        spice = st.selectbox(
            "Spice level",
            [e.value for e in SpiceLevel],
            index=1 if not existing else [e.value for e in SpiceLevel].index(existing.spice_level.value),
        )
        max_cook = st.slider("Max cooking time (minutes)", 15, 90, existing.max_cook_minutes if existing else 30)
        budget = st.selectbox(
            "Budget",
            [e.value for e in BudgetLevel],
            index=1 if not existing else [e.value for e in BudgetLevel].index(existing.budget_level.value),
        )

        st.subheader("Health profile (optional)")
        hf = existing.health_flags if existing else HealthFlags()
        has_medical = st.checkbox("I have a medical condition", value=hf.has_medical_condition)
        medical_notes = st.text_area("Medical notes (not used for therapy)", value=hf.medical_notes)
        pregnant = st.checkbox("Pregnant / breastfeeding", value=hf.is_pregnant_or_breastfeeding)
        children = st.checkbox("Cooking for children under 12", value=hf.cooking_for_children)
        elderly = st.checkbox("Cooking for elderly (70+)", value=hf.cooking_for_elderly)

        submitted = st.form_submit_button("Save profile")

    if submitted:
        profile = UserProfile(
            id=existing.id if existing else UserProfile().id,
            name=name,
            diet_style=DietStyle(diet),
            health_goal=HealthGoal(goal),
            allergies=[a.strip() for a in allergies.split(",") if a.strip()],
            cuisine_preferences=[c.strip() for c in cuisines.split(",") if c.strip()],
            spice_level=SpiceLevel(spice),
            max_cook_minutes=max_cook,
            budget_level=BudgetLevel(budget),
            health_flags=HealthFlags(
                has_medical_condition=has_medical,
                medical_notes=medical_notes,
                is_pregnant_or_breastfeeding=pregnant,
                cooking_for_children=children,
                cooking_for_elderly=elderly,
            ),
            disliked_ingredients=existing.disliked_ingredients if existing else [],
            preferred_ingredients=existing.preferred_ingredients if existing else [],
            limit_packaged_snacks=existing.limit_packaged_snacks if existing else False,
        )
        with st.status("ProfileManager agent saving preferences...", expanded=True):
            set_agent_status("ProfileManager")
            result = invoke_graph("save_profile", profile, repo.list_pantry(), user_text=medical_notes)
            if result.get("safety_result") and result["safety_result"].action == "redirect":
                st.error(result["safety_result"].message)
            else:
                repo.save_profile(profile)
                st.success("Profile saved.")
        st.rerun()

    render_disclaimer()
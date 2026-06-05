import streamlit as st

from nutriplan.agents.graph import invoke_graph
from nutriplan.models.schemas import FeedbackRecord
from nutriplan.ui.session import get_repo, set_agent_status


def render() -> None:
    repo = get_repo()
    profile = repo.get_profile()
    recipes = repo.list_recipes()
    if not recipes:
        st.info("Generate recipes first to leave feedback.")
        return

    st.header("Feedback & learning")
    recipe = st.selectbox("Recipe", recipes, format_func=lambda r: r.name)
    rating = st.slider("Rating", 1, 5, 4)
    cooked = st.checkbox("I made this")
    not_suitable = st.checkbox("Not suitable for me")
    reason = st.text_input("Reason (optional)", placeholder="too spicy, missing ingredient")

    if st.button("Submit feedback"):
        record = FeedbackRecord(
            recipe_id=recipe.id,
            recipe_name=recipe.name,
            rating=rating,
            cooked=cooked,
            not_suitable=not_suitable,
            reason=reason,
        )
        with st.status("FeedbackAgent updating preferences...", expanded=True):
            set_agent_status("FeedbackAgent")
            result = invoke_graph(
                "feedback",
                profile,
                repo.list_pantry(),
                feedback_kwargs={
                    "feedback_not_suitable": not_suitable,
                    "feedback_reason": reason or recipe.name,
                    "feedback_limit_packaged": "packaged" in reason.lower(),
                },
            )
            if result.get("user_profile"):
                repo.save_profile(result["user_profile"])
            repo.save_feedback(record)
        st.success("Thanks — future plans will avoid low-rated recipes.")

    st.subheader("Recent feedback")
    for fb in repo.list_feedback()[:10]:
        st.caption(f"{fb.recipe_name}: {fb.rating}/5 — cooked={fb.cooked} not_suitable={fb.not_suitable}")
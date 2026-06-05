import streamlit as st

from nutriplan.agents.graph import invoke_graph
from nutriplan.ui.components.disclaimer import render_disclaimer
from nutriplan.ui.session import get_repo, set_agent_status


def render() -> None:
    repo = get_repo()
    profile = repo.get_profile()
    plan = repo.get_latest_meal_plan()
    if not profile:
        st.warning("Set up your profile first.")
        return
    if not plan:
        st.warning("Generate a weekly plan first.")
        return

    st.header("Shopping list")

    if st.button("Generate shopping list (ShoppingListOptimizer)"):
        with st.status("ShoppingListOptimizer consolidating items...", expanded=True):
            set_agent_status("ShoppingListOptimizer")
            result = invoke_graph(
                "generate_shopping_list",
                profile,
                repo.list_pantry(),
                weekly_plan=plan,
            )
            if result.get("shopping_list"):
                repo.save_shopping_list(result["shopping_list"])
                st.success("Shopping list generated.")
            else:
                st.error(result.get("error", "Failed to build list."))
        st.rerun()

    shopping = repo.get_latest_shopping_list()
    if not shopping:
        st.info("No shopping list yet.")
        return

    by_cat: dict[str, list] = {}
    for item in shopping.items:
        by_cat.setdefault(item.category, []).append(item)

    lines = []
    for cat, items in sorted(by_cat.items()):
        st.subheader(cat)
        for item in items:
            swap = f" — _{item.suggested_swap}_" if item.suggested_swap else ""
            st.markdown(f"- {item.name} ({item.quantity}){swap}")
            lines.append(f"{item.name}\t{item.quantity}\t{cat}")

    if st.button("Copy list to clipboard"):
        st.code("\n".join(lines))

    st.markdown(f'<div class="disclaimer-box">{shopping.disclaimer}</div>', unsafe_allow_html=True)
    render_disclaimer()
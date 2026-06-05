import streamlit as st
from datetime import date

from nutriplan.agents.graph import invoke_graph
from nutriplan.knowledge.packaged_foods import get_kb
from nutriplan.models.schemas import PantryItem
from nutriplan.ui.session import get_repo, set_agent_status


def render() -> None:
    repo = get_repo()
    profile = repo.get_profile()
    if not profile:
        st.warning("Set up your profile first.")
        return

    st.header("Pantry / inventory")
    kb = get_kb()

    with st.form("add_item"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Ingredient name")
        category = c2.selectbox(
            "Category",
            ["Vegetables", "Proteins", "Grains", "Dairy", "Spices", "Packaged", "Pantry", "Other"],
        )
        qty = c3.text_input("Quantity", placeholder="e.g. 500g")
        is_packaged = st.checkbox("Packaged / branded product")
        use_expiry = st.checkbox("Track expiry date")
        expiry_val = st.date_input("Expiry") if use_expiry else None
        if st.form_submit_button("Add item") and name:
            item = PantryItem(
                name=name.strip(),
                category=category,
                quantity=qty,
                is_packaged=is_packaged,
                expiry_date=expiry_val,
            )
            repo.save_pantry_item(item)
            st.rerun()

    if st.button("Run InventoryAgent (scan + prioritize)"):
        pantry = repo.list_pantry()
        with st.status("InventoryAgent analyzing pantry...", expanded=True):
            set_agent_status("InventoryAgent")
            result = invoke_graph("sync_pantry", profile, pantry)
            if result.get("pantry"):
                repo.clear_pantry()
                for p in result["pantry"]:
                    repo.save_pantry_item(p)
            if result.get("kb_insights"):
                repo.save_kb_insights(result["kb_insights"])
        st.success("Pantry synced with knowledge base insights.")
        st.rerun()

    pantry = repo.list_pantry()
    matches = kb.match_pantry_items(pantry)

    for item in pantry:
        match = next((m for m in matches if m.pantry_item_name == item.name), None)
        cols = st.columns([3, 2, 2, 1])
        cols[0].markdown(f"**{item.name}** — {item.category}")
        cols[1].caption(item.quantity or "—")
        if match:
            cols[2].markdown(
                f'<span class="kb-badge">KB: {", ".join(match.concerns[:2])}</span>',
                unsafe_allow_html=True,
            )
        if cols[3].button("Delete", key=f"del_{item.id}"):
            repo.delete_pantry_item(item.id)
            st.rerun()

    insights = repo.get_kb_insights()
    if insights:
        st.subheader("Packaged food insights")
        for ins in insights:
            st.markdown(f'<div class="card">{ins.gentle_message}</div>', unsafe_allow_html=True)
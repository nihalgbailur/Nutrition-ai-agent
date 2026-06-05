from __future__ import annotations

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from nutriplan.ui.pages import chat, feedback, home, how_it_works, pantry, planner, profile, recipes, shopping
from nutriplan.ui.session import get_repo
from nutriplan.utils.seed import load_synthetic_database

load_dotenv()


def _bootstrap_database() -> None:
    """First launch: auto-load synthetic data if DB is empty."""
    if st.session_state.get("db_bootstrapped"):
        return
    repo = get_repo()
    if repo.is_empty():
        load_synthetic_database(repo)
        st.session_state["db_bootstrapped"] = True
        st.session_state["db_auto_loaded"] = True
    else:
        st.session_state["db_bootstrapped"] = True

PAGES = {
    "Home": home,
    "Chat": chat,
    "Profile": profile,
    "Pantry": pantry,
    "Recipes": recipes,
    "Weekly Plan": planner,
    "Shopping List": shopping,
    "Feedback": feedback,
    "How it works": how_it_works,
}


def inject_css() -> None:
    css_path = Path(__file__).parent / "ui" / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="NutriPlan AI",
        page_icon="🥗",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    _bootstrap_database()

    st.sidebar.title("NutriPlan AI")
    if st.session_state.get("db_auto_loaded"):
        st.sidebar.success("Database loaded (first run)")
        st.session_state.pop("db_auto_loaded", None)
    st.sidebar.caption("Agentic meal planning for Indian kitchens")
    choice = st.sidebar.radio("Navigate", list(PAGES.keys()))
    status = st.session_state.get("agent_status")
    if status:
        st.sidebar.markdown(f'<span class="agent-pill">{status}</span>', unsafe_allow_html=True)

    PAGES[choice].render()


if __name__ == "__main__":
    main()
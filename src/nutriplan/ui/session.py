import streamlit as st

from nutriplan.db.repository import Repository


def get_repo() -> Repository:
    if "repo" not in st.session_state:
        st.session_state.repo = Repository()
    return st.session_state.repo


def get_agent_status() -> str:
    return st.session_state.get("agent_status", "")


def set_agent_status(name: str, message: str = "") -> None:
    st.session_state.agent_status = f"{name}: {message}" if message else name
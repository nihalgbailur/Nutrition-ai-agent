import streamlit as st

from nutriplan.config import DISCLAIMER, MEDICAL_EXTRA_BANNER, NUTRITION_LABEL
from nutriplan.models.schemas import UserProfile
from nutriplan.safety.guardrails import profile_requires_confirmation


def render_disclaimer() -> None:
    st.markdown(f'<div class="disclaimer-box">{DISCLAIMER}</div>', unsafe_allow_html=True)


def render_nutrition_label() -> None:
    st.caption(f"_{NUTRITION_LABEL}_")


def render_medical_banner(profile: UserProfile | None) -> None:
    if profile and profile_requires_confirmation(profile):
        st.warning(MEDICAL_EXTRA_BANNER)


def require_medical_confirmation(profile: UserProfile | None, key: str) -> bool:
    if not profile or not profile_requires_confirmation(profile):
        return True
    return st.checkbox("I understand this is general meal inspiration only, not medical advice.", key=key)
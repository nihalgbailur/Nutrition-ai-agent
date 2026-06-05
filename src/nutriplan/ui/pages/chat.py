import streamlit as st

from nutriplan.llm.chat import chat_reply_stream
from nutriplan.llm.client import is_ollama_backend, llm_available, llm_provider_label
from nutriplan.models.guest import guest_profile
from nutriplan.ui.components.disclaimer import render_disclaimer, render_medical_banner
from nutriplan.ui.session import get_repo, set_agent_status


def render() -> None:
    repo = get_repo()
    saved_profile = repo.get_profile()
    pantry = repo.list_pantry()
    profile = saved_profile or guest_profile()
    using_guest = saved_profile is None

    st.header("Chat with NutriPlan")

    fast_default = is_ollama_backend()
    fast_mode = st.toggle(
        "Fast replies (instant, no Ollama wait)",
        value=st.session_state.get("chat_fast_mode", fast_default),
        help="Recommended on local Ollama — uses smart templates immediately. "
        "Turn off for full AI chat (first reply can take 30–60s).",
    )
    st.session_state.chat_fast_mode = fast_mode

    if llm_available() and is_ollama_backend() and not fast_mode:
        st.caption(
            f"**{llm_provider_label()}** — streaming enabled. First message may be slow while the model loads."
        )
    else:
        st.caption(
            f"Using **{llm_provider_label()}**."
            if llm_available() and not fast_mode
            else "Instant template replies."
        )

    if using_guest:
        st.info(
            "Chatting as **Guest**. Save **Profile** for personalization — demo is optional."
        )
    else:
        render_medical_banner(saved_profile)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(f'<span class="agent-pill">{turn["agent"]}</span>', unsafe_allow_html=True)
            st.write(turn["assistant"])

    prompt = st.chat_input("Ask anything about meals, pantry, or planning…")
    if prompt:
        agent, stream, suffix = chat_reply_stream(
            prompt,
            profile,
            pantry,
            history=st.session_state.chat_history,
            fast_mode=fast_mode,
        )
        set_agent_status(agent)

        with st.chat_message("assistant"):
            st.markdown(f'<span class="agent-pill">{agent}</span>', unsafe_allow_html=True)

            collected: list[str] = []

            def _stream():
                for part in stream:
                    collected.append(part)
                    yield part
                if suffix:
                    collected.append(suffix)
                    yield suffix

            if fast_mode or not llm_available():
                st.write("".join(_stream()))
            else:
                st.write_stream(_stream())

        st.session_state.chat_history.append(
            {"user": prompt, "assistant": "".join(collected), "agent": agent}
        )
        st.rerun()

    st.divider()
    st.markdown("**Try asking:**")
    st.markdown(
        "- Quick veg dinner ideas in 20 minutes\n"
        "- Is Maggi unhealthy? Swaps?\n"
        "- What can I make with dal and rice?"
    )

    if st.button("Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

    render_disclaimer()
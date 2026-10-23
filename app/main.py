"""Streamlit user interface for the question answering application."""

from __future__ import annotations

import logging

import streamlit as st

from app.config.settings import ConfigurationError, Settings, load_settings
from app.services.gemini_service import GeminiService, GeminiServiceError
from app.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


@st.cache_resource(show_spinner=False)
def get_gemini_service(settings: Settings) -> GeminiService:
    """Reuse the API client across Streamlit reruns, not conversation state."""
    return GeminiService(settings)


def main() -> None:
    """Render the chat UI and handle submitted questions."""
    configure_logging()
    st.set_page_config(page_title="AI Question & Answering System", page_icon="💬")
    st.title("AI Question & Answering System")
    st.write(
        "Ask a question and get a helpful answer from a Google Gemini model. "
        "Continue the conversation with follow-up questions."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Conversation")
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    try:
        settings = load_settings()
    except ConfigurationError as exc:
        with st.sidebar:
            st.caption("Model: set GEMINI_MODEL to choose a model.")
        st.error(str(exc))
        st.stop()

    with st.sidebar:
        st.caption(f"Model: `{settings.model}`")
        st.caption(f"Temperature: `{settings.temperature:g}`")

    service = get_gemini_service(settings)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Type your question...")
    if question is None:
        return

    question = question.strip()
    if not question:
        st.warning("Please enter a question before submitting.")
        return

    user_message = {"role": "user", "content": question}
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = service.generate_answer(st.session_state.messages)
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except GeminiServiceError as exc:
        st.session_state.messages.pop()
        logger.warning("The answer request failed.")
        st.error(str(exc))


if __name__ == "__main__":
    main()

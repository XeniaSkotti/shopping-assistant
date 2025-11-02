import streamlit as st
from shopping_assistant.qa import QAAgent


def render() -> None:
    st.set_page_config(page_title="Shopping Assistant", page_icon="🛒", layout="centered")
    st.title("🛒 Shopping Assistant")

    # Lazy initialize agent so the UI loads even if the model init is slow or errors
    if "agent" not in st.session_state:
        st.session_state.agent = None
        st.session_state.agent_error = None
    if "history" not in st.session_state:
        st.session_state.history = []  # [{role: "user"|"assistant", content: str}]

    # Sidebar actions
    with st.sidebar:
        st.markdown("### Controls")
        # show agent status
        if st.session_state.agent is None and st.session_state.agent_error is None:
            st.info("Agent not initialized")
        elif st.session_state.agent_error is not None:
            st.error(f"Agent error: {st.session_state.agent_error}")
        else:
            st.success("Agent ready")

        if st.button("Reset chat"):
            st.session_state.history = []
            st.session_state.agent = None
            st.session_state.agent_error = None
            st.experimental_rerun()

    # Render chat history
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box
    prompt = st.chat_input("Ask me anything…")
    if prompt:
        # Show user message
        st.session_state.history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Initialize the agent lazily (on first prompt) and handle init errors
        if st.session_state.agent is None and st.session_state.agent_error is None:
            with st.spinner("Initializing agent… this may take a moment"):
                try:
                    st.session_state.agent = QAAgent()
                except Exception as e:
                    st.session_state.agent_error = str(e)

        # Get assistant reply
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                if st.session_state.agent is None:
                    # show init error
                    answer = f"Agent not available. Error: {st.session_state.agent_error}"
                else:
                    try:
                        answer = st.session_state.agent.ask(prompt)
                    except Exception as e:
                        answer = f"Error: {e}"
            st.markdown(answer)
        st.session_state.history.append({"role": "assistant", "content": answer})


# Allow running directly for quick debugging
if __name__ == "__main__":
    render()

"""
Streamlit Shopping Assistant App

A web interface for the AI-powered shopping assistant with chat functionality.
"""

import streamlit as st
import time
from typing import Dict, Any


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hi! I'm your AI shopping assistant. I can help you find"
                    "products, compare prices, and make recommendations. "
                    "What are you looking for today?"
                ),
            }
        ]


def generate_dummy_response(user_input: str) -> str:
    """Generate a dummy response based on user input."""
    # Simple keyword-based dummy responses
    user_lower = user_input.lower()

    if any(word in user_lower for word in ["laptop", "computer", "macbook"]):
        return (
            "🖥️ I found some great laptop options for you! "
            "Here are some popular choices:\n\n"
            "1. **MacBook Air M3** - $1,199\n"
            "   - 13-inch display, 8GB RAM, 256GB SSD\n"
            "   - Perfect for everyday tasks and portability\n\n"
            "2. **Dell XPS 13** - $999\n"
            "   - 13.4-inch display, 16GB RAM, 512GB SSD\n"
            "   - Great Windows alternative with premium build\n\n"
            "Would you like more details about any of these options?"
        )

    elif any(word in user_lower for word in ["phone", "smartphone", "iphone", "android"]):
        return (
            "📱 Here are some excellent smartphone recommendations:\n\n"
            "1. **iPhone 15 Pro** - $999\n"
            "   - 6.1-inch display, A17 Pro chip, 128GB\n"
            "   - Excellent camera and build quality\n\n"
            "2. **Samsung Galaxy S24** - $799\n"
            "   - 6.2-inch display, Snapdragon 8 Gen 3, 256GB\n"
            "   - Great Android experience with S Pen support\n\n"
            "What's your budget and preferred operating system?"
        )

    elif any(word in user_lower for word in ["headphones", "earbuds", "audio"]):
        return (
            "🎧 I've found some amazing audio options:\n\n"
            "1. **AirPods Pro (2nd gen)** - $249\n"
            "   - Active noise cancellation, spatial audio\n"
            "   - Perfect for Apple ecosystem users\n\n"
            "2. **Sony WH-1000XM5** - $399\n"
            "   - Industry-leading noise cancellation\n"
            "   - 30-hour battery life\n\n"
            "Are you looking for wireless earbuds or over-ear headphones?"
        )

    elif any(word in user_lower for word in ["budget", "cheap", "affordable", "price"]):
        return (
            "💰 I understand you're looking for budget-friendly options! "
            "I can help you find great deals. What's your budget range and "
            "what type of product are you interested in?"
        )

    elif any(word in user_lower for word in ["compare", "vs", "difference"]):
        return (
            "🔍 I'd be happy to help you compare products! Please let me know "
            "which specific items you'd like me to compare, and I'll break down "
            "the key differences for you."
        )

    else:
        return (
            f"🤔 I understand you're interested in '{user_input}'. "
            "Let me search for the best options for you!\n\n"
            "Here's what I can help you with:\n"
            "• Product recommendations and reviews\n"
            "• Price comparisons across retailers\n"
            "• Feature breakdowns and specifications\n"
            "• Budget-friendly alternatives\n\n"
            "Could you provide a bit more detail about what you're looking for? "
            "For example, your budget range or specific features that matter "
            "to you?"
        )


def display_chat_message(message: Dict[str, Any]) -> None:
    """Display a chat message with appropriate styling."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def main():
    """Main Streamlit app."""
    # Page configuration
    st.set_page_config(
        page_title="AI Shopping Assistant",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Initialize session state
    initialize_session_state()

    # App header
    st.title("🛒 AI Shopping Assistant")
    st.markdown("*Find the perfect products with AI-powered recommendations*")

    # Sidebar with app info
    with st.sidebar:
        st.header("About")
        st.markdown(
            """
        This AI shopping assistant helps you:
        - 🔍 Find products based on your needs
        - 💰 Compare prices across retailers
        - ⭐ Get personalized recommendations
        - 📊 Understand product specifications
        """
        )

        st.header("Tips")
        st.markdown(
            """
        Try asking:
        - "I need a laptop for programming"
        - "Compare iPhone vs Samsung phones"
        - "Best budget headphones under $100"
        - "Gaming laptop recommendations"
        """
        )

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
            st.rerun()

    # Chat interface
    chat_container = st.container()

    with chat_container:
        # Display existing messages
        for message in st.session_state.messages:
            display_chat_message(message)

    # Chat input
    if prompt := st.chat_input("Ask me about any product you're looking for..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Simulate processing time
                time.sleep(1)
                response = generate_dummy_response(prompt)
                st.markdown(response)

        # Add assistant response to session state
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()

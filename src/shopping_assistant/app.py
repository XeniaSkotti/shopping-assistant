"""
Simple Fashion Shopping Assistant Chat Interface
"""

import streamlit as st
from typing import Dict, Any, List
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from shopping_assistant.indexing import SearchEngine

    INDEXING_AVAILABLE = True
except ImportError:
    INDEXING_AVAILABLE = False
    st.error("Indexing system not available. Please install required dependencies.")


class ShoppingAssistant:
    """Simple shopping assistant with product search capabilities."""

    def __init__(self):
        """Initialize the shopping assistant."""
        self.search_engine = None
        self.is_initialized = False

        if INDEXING_AVAILABLE:
            self._initialize_search_engine()

    def _initialize_search_engine(self):
        """Initialize the search engine."""
        try:
            data_path = project_root / "data" / "FashionDataset.csv"
            index_path = project_root / "data" / "product_index.pkl"

            self.search_engine = SearchEngine()
            currency_rate = 0.0095

            self.search_engine.load_from_saved_index(str(index_path), str(data_path), currency_rate)
            self.is_initialized = True

        except Exception as e:
            st.error(f"Failed to initialize search engine: {e}")
            self.is_initialized = False

    def search_products(self, query: str) -> List[Dict]:
        """Search for products using the query."""
        if not self.is_initialized:
            return []

        try:
            results = self.search_engine.smart_search(query, top_k=10)
            return results
        except Exception as e:
            st.error(f"Search error: {e}")
            return []

    def get_trending_products(self) -> List[Dict]:
        """Get trending products."""
        if not self.is_initialized:
            return []

        try:
            return self.search_engine.get_trending_products(limit=5)
        except Exception as e:
            st.error(f"Error getting trending products: {e}")
            return []

    def get_categories(self) -> List[str]:
        """Get available categories."""
        if not self.is_initialized:
            return []

        try:
            return self.search_engine.get_categories()
        except Exception:
            return []


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": ("👋 Hi! I'm your AI shopping assistant. " "What fashion items are you looking for today?"),
            }
        ]

    if "assistant" not in st.session_state:
        st.session_state.assistant = ShoppingAssistant()


def generate_ai_response(user_input: str) -> str:
    """Generate AI response with product search."""
    assistant = st.session_state.assistant

    if not assistant.is_initialized:
        return "Sorry, I can't access the product database right now."

    user_lower = user_input.lower()
    if any(word in user_lower for word in ["trending", "popular", "hot"]):
        trending = assistant.get_trending_products()
        if trending:
            response = "🔥 **Trending Products Right Now:**\n\n"
            for i, product in enumerate(trending, 1):
                brand = product.get("BrandName", "Unknown Brand").title()
                price = product.get("SellPrice_numeric", 0)
                details = product.get("Deatils", "No details available")
                if len(details) > 60:
                    details = details[:60] + "..."
                response += f"**{i}. {brand}** - £{price:.2f}\n{details}\n\n"
            return response
        else:
            return "I couldn't fetch trending products right now. Please try again."

    elif any(word in user_lower for word in ["categories", "category", "browse"]):
        categories = assistant.get_categories()
        if categories:
            response = "🏷️ Here are our available categories:\n\n"
            response += ", ".join(categories)
            response += "\n\nJust tell me which category you're interested in!"
            return response

    else:
        # Perform product search
        products = assistant.search_products(user_input)

        if products:
            response = f"🔍 **Found {len(products)} products for '{user_input}':**\n\n"
            for i, product in enumerate(products[:5], 1):  # Show top 5 results
                brand = product.get("BrandName", "Unknown Brand").title()
                price = product.get("SellPrice_numeric", 0)
                details = product.get("Deatils", "No details available")
                category = product.get("Category", "Unknown Category")
                if len(details) > 60:
                    details = details[:60] + "..."
                response += f"**{i}. {brand}** - £{price:.2f}\n*{category}*\n{details}\n\n"

            if len(products) > 5:
                response += f"*...and {len(products) - 5} more results available!*"
            return response
        else:
            return (
                f"I couldn't find any products matching '{user_input}'. "
                "Try different keywords like 'dress', 'jeans', 'cotton top', etc."
            )


def display_chat_message(message: Dict[str, Any]) -> None:
    """Display a chat message."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def main():
    """Main Streamlit app."""
    # Page configuration
    st.set_page_config(
        page_title="AI Fashion Shopping Assistant",
        page_icon="👗",
        layout="centered",
    )

    # Initialize session state
    initialize_session_state()

    # App header
    st.title("👗 AI Fashion Shopping Assistant")
    st.markdown("*Chat with your AI shopping assistant to find fashion products*")

    # Display chat messages
    for message in st.session_state.messages:
        display_chat_message(message)

    # Chat input with clear button
    col1, col2 = st.columns([4, 1])

    with col1:
        prompt = st.chat_input("Ask me about fashion products...")

    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()

    if prompt:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate and add assistant response
        with st.spinner("Searching products..."):
            response = generate_ai_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})

        st.rerun()


if __name__ == "__main__":
    main()

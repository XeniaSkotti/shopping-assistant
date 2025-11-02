"""Top-level Streamlit launcher for the Shopping Assistant package.

Run this with:

    streamlit run streamlit_app.py

It calls the UI's render() on every run so Streamlit reruns re-render the page.
"""

import logging
from shopping_assistant.ui import render


# Configure logging for the app entrypoint
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

render()

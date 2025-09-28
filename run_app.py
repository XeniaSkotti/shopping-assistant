#!/usr/bin/env python3
"""
Run the Shopping Assistant Streamlit App

This script launches the Streamlit web interface for the AI shopping assistant.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit app."""
    # Get the path to the app.py file
    app_path = Path(__file__).parent / "shopping_assistant" / "app.py"

    try:
        # Run streamlit with the app
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                "--server.address",
                "localhost",
                "--server.port",
                "8501",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApp stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()

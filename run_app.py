#!/usr/bin/env python3
"""
Run the enhanced shopping assistant with product indexing.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the enhanced Streamlit app."""
    project_root = Path(__file__).parent
    app_path = project_root / "src" / "shopping_assistant" / "app.py"

    # Get the Python executable path
    venv_python = project_root / ".venv" / "bin" / "python"

    if not venv_python.exists():
        print("❌ Virtual environment not found. Please run devenv.sh to set up the environment.")
        sys.exit(1)

    if not app_path.exists():
        print(f"❌ App file not found: {app_path}")
        sys.exit(1)

    print("🚀 Starting Enhanced Shopping Assistant...")
    print("📱 App will open in your browser at http://localhost:8501")

    # Run streamlit
    cmd = [str(venv_python), "-m", "streamlit", "run", str(app_path)]

    try:
        subprocess.run(cmd, cwd=str(project_root))
    except KeyboardInterrupt:
        print("\n👋 Shopping Assistant stopped.")
    except Exception as e:
        print(f"❌ Error running app: {e}")


if __name__ == "__main__":
    main()

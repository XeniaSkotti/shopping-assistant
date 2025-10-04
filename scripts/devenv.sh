#!/bin/bash

echo "🚀 Setting up Shopping Assistant development environment..."

# Check if Python 3.11+ is available
if ! python3 --version | grep -E "3\.(1[1-9]|[2-9][0-9])" > /dev/null; then
    echo "❌ Python 3.11+ is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install the package with all optional dependencies
echo "📥 Installing dependencies (including notebook tools)..."
pip install -e ".[dev,test,notebooks]"

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

echo "✅ Setup complete! Run 'source .venv/bin/activate' to activate the environment."

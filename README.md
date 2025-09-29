# 🛍️ AI Shopping Assistant

An end-to-end prototype of a conversational shopping assistant.
Built in **Python 3.13** with **Streamlit** UI, this demo showcases how an LLM can help users find products based on natural-language queries, while staying grounded in structured catalog data.

> **⚠️ Current Status**: This project is in early development. The features listed below represent the target architecture. See [Current Implementation](#current-implementation) for what's currently available.

---

## 🎯 Target Features

- **Conversational search**
  Ask questions like:
  *"Looking for a waterproof hiking jacket under £180, UK stock, sustainable brand."*

- **Hybrid retrieval**
  Combines lexical filtering (DuckDB) and semantic similarity search (LanceDB/Chroma).

- **Constraint handling**
  Filters by price, brand, size, region, and sustainability flags via an LLM intent parser.

- **Grounded answers with citations**
  Every product card includes explicit attributes and source references.

- **Guardrails-lite**
  Restricted items (e.g. weapons, meds) are blocked. Numeric fields (price, rating) come directly from the catalog.

- **Diagnostics tab**
  Simple metrics dashboard: latency, recall@k, groundedness rate.

## 📍 Current Implementation

**What's working now:**
- ✅ Data preprocessing pipeline (`DataPreprocessor`)
- ✅ Basic project structure and dependencies
- ✅ Jupyter notebook for data exploration

**In development:**
- 🚧 Streamlit UI
- 🚧 Vector search and retrieval system
- 🚧 LLM integration for conversational queries

**Planned:**
- 📋 Hybrid search (lexical + semantic)
- 📋 Intent parsing and constraint handling
- 📋 Guardrails and safety measures
- 📋 Performance metrics and diagnostics

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (tested with 3.13)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/XeniaSkotti/shopping-assistant.git
   cd shopping-assistant
   ```

2. **Run the setup script:**
   ```bash
   chmod +x scripts/devenv.sh
   ./scripts/devenv.sh
   ```

3. **Activate the environment:**
   ```bash
   source .venv/bin/activate
   ```

4. **Explore the data (current functionality):**
   ```bash
   jupyter notebook notebooks/eda.ipynb
   ```

## 📊 Dataset

The demo uses a fashion e-commerce dataset sourced from:
- **Source**: [Kaggle - E-commerce Fashion Dataset](https://www.kaggle.com/code/tabassumbano/ecommerce-fashion-dataset/)
- **Contents**: ~30,000 fashion items with attributes like brand, price, sizes, categories, and discounts

*Note: This dataset is used for demonstration purposes only.*

## 🗺️ Development Roadmap

1. **Phase 1** (Current): Data preprocessing and exploration
2. **Phase 2**: Basic search and retrieval
3. **Phase 3**: LLM integration and conversational interface
4. **Phase 4**: Advanced features (hybrid search, guardrails)
5. **Phase 5**: Performance optimization and metrics

# 🛍️ AI Shopping Assistant

An end-to-end prototype of a conversational shopping assistant.
Built in **Python 3.13** with **Streamlit** UI, this demo showcases how an LLM can help users find products based on natural-language queries, while staying grounded in structured catalog data.

---

## ✨ Features

- **Conversational search**
  Ask questions like:
  *“Looking for a waterproof hiking jacket under £180, UK stock, sustainable brand.”*

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
   source venv/bin/activate
   ```

4. **Start the Streamlit app:**
   ```bash
   streamlit run src/shopping_assistant/app.py

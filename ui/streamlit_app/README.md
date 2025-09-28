# Streamlit App

This directory contains the Streamlit-based user interface for the AI shopping assistant.

## Structure

- `components/` - Reusable UI components
- `pages/` - Individual pages/screens of the application
- `utils/` - Utility functions for the UI
- `app.py` - Main application entry point (to be created)

## Features

The Streamlit app will provide:

- **Search Interface**: Natural language query input for product search
- **Results Display**: Product recommendations with explanations
- **Filters & Constraints**: UI for refining search parameters
- **Audit Trail**: Transparency into AI decision-making process
- **Observability Dashboard**: Monitoring and debugging interface

## Development

Run the app locally with:
```bash
streamlit run ui/streamlit_app/app.py
```
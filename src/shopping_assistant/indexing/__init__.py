"""
Indexing module for the shopping assistant.
Provides functionality for indexing, searching, and retrieving fashion products.
"""

from .data_preprocessor import DataPreprocessor
from .product_index import ProductIndex
from .search_engine import SearchEngine

__all__ = ["DataPreprocessor", "ProductIndex", "SearchEngine"]

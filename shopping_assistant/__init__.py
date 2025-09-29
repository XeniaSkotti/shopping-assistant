"""
AI Shopping Assistant

A conversational AI shopping assistant that helps users find products
based on natural language queries with hybrid retrieval and grounded responses.
"""

__version__ = "0.1.0"
__author__ = "Xenia Skotti"
__email__ = "xeniaskotti@gmail.com"

# Import main components
from .preprocessor import DataPreprocessor

__all__ = ["DataPreprocessor"]

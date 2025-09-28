"""
High-level search engine that combines indexing and filtering capabilities.
Provides a simple interface for all product search and recommendation needs.
"""

from typing import Dict, List, Optional

from .data_preprocessor import DataPreprocessor
from .product_index import ProductIndex


class SearchEngine:
    """High-level search engine for fashion products."""

    def __init__(self):
        """Initialize the search engine."""
        self.preprocessor: Optional[DataPreprocessor] = None
        self.index: Optional[ProductIndex] = None
        self.is_ready = False

    def initialize_from_csv(self, csv_path: str, rebuild_index: bool = True, currency_conversion_rate: float = 0.0095):
        """
        Initialize the search engine from a CSV file.

        Args:
            csv_path: Path to the CSV file containing product data
            rebuild_index: Whether to rebuild the index from scratch
            currency_conversion_rate: Conversion rate from INR to GBP (default: 0.0095)
        """
        # Initialize preprocessor and load data
        self.preprocessor = DataPreprocessor(csv_path, currency_conversion_rate)
        processed_data = self.preprocessor.process_dataset()

        # Initialize and build index
        self.index = ProductIndex()
        if rebuild_index:
            self.index.build_index(processed_data)

        self.is_ready = True
        print("Search engine initialized successfully!")

    def load_from_saved_index(self, index_path: str, csv_path: str, currency_conversion_rate: float = 0.0095):
        """
        Load the search engine from a pre-built index.

        Args:
            index_path: Path to the saved index file
            csv_path: Path to the original CSV (for preprocessor initialization)
            currency_conversion_rate: Conversion rate from INR to GBP (default: 0.0095)
        """
        # Initialize preprocessor (needed for data summary functions)
        self.preprocessor = DataPreprocessor(csv_path, currency_conversion_rate)

        # Load pre-built index
        self.index = ProductIndex()
        self.index.load_index(index_path)

        self.is_ready = True
        print("Search engine loaded from saved index!")

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        material: Optional[str] = None,
        size: Optional[str] = None,
        price_range: Optional[str] = None,
        top_k: int = 20,
    ) -> List[Dict]:
        """
        Perform a comprehensive search with text query and filters.

        Args:
            query: Text search query
            category: Category filter
            brand: Brand filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            material: Material filter
            size: Size filter
            price_range: Price range filter ('budget', 'mid-range', 'premium', 'luxury')
            top_k: Maximum number of results to return

        Returns:
            List of matching products with relevance scores
        """
        if not self.is_ready:
            raise ValueError("Search engine not initialized. Call initialize_from_csv() first.")

        # First apply filters to reduce search space
        filtered_products = self.index.filter_products(
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            material=material,
            size=size,
            price_range=price_range,
        )

        if filtered_products.empty:
            return []

        # If we have a text query, perform text search on filtered results
        if query.strip():
            # Temporarily update the index with filtered products for search
            original_products = self.index.products
            original_tfidf_matrix = self.index.tfidf_matrix

            # Build temporary TF-IDF for filtered products
            filtered_search_texts = filtered_products["search_text"].fillna("")
            temp_tfidf_matrix = self.index.tfidf_vectorizer.transform(filtered_search_texts)

            # Update index temporarily
            self.index.products = filtered_products
            self.index.tfidf_matrix = temp_tfidf_matrix

            # Perform search
            results = self.index.text_search(query, top_k=top_k)

            # Restore original index
            self.index.products = original_products
            self.index.tfidf_matrix = original_tfidf_matrix

            return results
        else:
            # No text query, just return filtered results
            return filtered_products.head(top_k).to_dict("records")

    def get_recommendations(self, product_id: int, top_k: int = 10) -> List[Dict]:
        """
        Get product recommendations based on similarity.

        Args:
            product_id: ID of the reference product
            top_k: Number of recommendations to return

        Returns:
            List of similar products
        """
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        return self.index.get_similar_products(product_id, top_k)

    def get_product_details(self, product_id: int) -> Optional[Dict]:
        """Get detailed information about a specific product."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        return self.index.get_product_by_id(product_id)

    def get_trending_products(self, limit: int = 20) -> List[Dict]:
        """Get trending products based on discounts and popularity."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        return self.index.get_trending_products(limit)

    def browse_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Browse products in a specific category."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        return self.index.get_products_by_category(category, limit)

    def get_categories(self) -> List[str]:
        """Get all available categories."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        return self.index.products["Category"].unique().tolist()

    def get_brands(self) -> List[str]:
        """Get all available brands."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        return self.index.products["BrandName"].unique().tolist()

    def get_price_ranges(self) -> Dict[str, int]:
        """Get distribution of products across price ranges."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        return self.index.products["price_range"].value_counts().to_dict()

    def get_data_summary(self) -> Dict:
        """Get a comprehensive summary of the indexed data."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        if self.preprocessor and self.preprocessor.processed_data is not None:
            return self.preprocessor.get_data_summary()
        else:
            # Fallback summary from index
            df = self.index.products
            return {
                "total_products": len(df),
                "unique_brands": df["BrandName"].nunique(),
                "categories": df["Category"].value_counts().to_dict(),
                "price_ranges": df["price_range"].value_counts().to_dict(),
            }

    def save_index(self, index_path: str):
        """Save the current index for faster loading later."""
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        self.index.save_index(index_path)
        print(f"Index saved to {index_path}")

    def smart_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Intelligent search that automatically detects search intent and applies appropriate filters.

        Args:
            query: Natural language search query
            top_k: Maximum number of results

        Returns:
            List of relevant products
        """
        if not self.is_ready:
            raise ValueError("Search engine not initialized.")

        query_lower = query.lower()

        # Auto-detect category (using cleaned category names)
        category_keywords = {
            "dress": "Western Wear",
            "western": "Western Wear",
            "indian": "Indian Wear",
            "ethnic": "Indian Wear",
            "lingerie": "Lingerie & Nightwear",
            "nightwear": "Lingerie & Nightwear",
            "shoes": "Footwear",
            "footwear": "Footwear",
            "boots": "Footwear",
            "sandals": "Footwear",
            "watch": "Watches",
            "jewelry": "Jewellery",
            "jewellery": "Jewellery",
            "perfume": "Fragrance",
            "fragrance": "Fragrance",
        }

        detected_category = None
        for keyword, category in category_keywords.items():
            if keyword in query_lower:
                detected_category = category
                break

        # Auto-detect price range keywords
        price_range = None
        if any(word in query_lower for word in ["cheap", "budget", "affordable"]):
            price_range = "budget"
        elif any(word in query_lower for word in ["premium", "expensive", "luxury"]):
            price_range = "luxury"
        elif "mid" in query_lower:
            price_range = "mid-range"

        # Auto-detect material
        materials = ["cotton", "silk", "denim", "wool", "polyester", "linen"]
        detected_material = None
        for material in materials:
            if material in query_lower:
                detected_material = material
                break

        # Perform search with auto-detected filters
        return self.search(
            query=query, category=detected_category, price_range=price_range, material=detected_material, top_k=top_k
        )

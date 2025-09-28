"""
Product index for efficient search and retrieval of fashion products.
Supports text-based search, filtering, and similarity-based recommendations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


class ProductIndex:
    """Index for fast product search and recommendations."""

    def __init__(self):
        """Initialize the product index."""
        self.products: Optional[pd.DataFrame] = None
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.price_scaler: Optional[StandardScaler] = None
        self.feature_weights = {"text_similarity": 0.6, "price_similarity": 0.2, "category_similarity": 0.2}

    def build_index(self, processed_data: pd.DataFrame):
        """
        Build the search index from processed product data.

        Args:
            processed_data: DataFrame with processed product information
        """
        self.products = processed_data.copy()

        # Build TF-IDF index for text search
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000, stop_words="english", ngram_range=(1, 2), min_df=2, max_df=0.8
        )

        # Fit TF-IDF on search text
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.products["search_text"].fillna(""))

        # Build price scaler for price-based similarity
        self.price_scaler = StandardScaler()
        price_data = (
            self.products["SellPrice_numeric"].fillna(self.products["SellPrice_numeric"].median()).values.reshape(-1, 1)
        )
        self.price_scaler.fit(price_data)

        print(f"Index built successfully for {len(self.products)} products")

    def text_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Perform text-based search on products.

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of product dictionaries with similarity scores
        """
        if self.tfidf_matrix is None:
            raise ValueError("Index not built. Call build_index() first.")

        # Transform query using fitted vectorizer
        query_vector = self.tfidf_vectorizer.transform([query.lower()])

        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]

        # Get top results
        top_indices = similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include results with some similarity
                product = self.products.iloc[idx].to_dict()
                product["similarity_score"] = float(similarities[idx])
                results.append(product)

        return results

    def filter_products(
        self,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        material: Optional[str] = None,
        size: Optional[str] = None,
        price_range: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Filter products based on various criteria.

        Args:
            category: Product category filter
            brand: Brand name filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            material: Material filter
            size: Size filter
            price_range: Price range category filter

        Returns:
            Filtered DataFrame
        """
        if self.products is None:
            raise ValueError("Index not built. Call build_index() first.")

        filtered_df = self.products.copy()

        # Apply filters
        if category:
            filtered_df = filtered_df[filtered_df["Category"].str.contains(category, case=False, na=False)]

        if brand:
            filtered_df = filtered_df[filtered_df["BrandName"].str.contains(brand, case=False, na=False)]

        if min_price is not None:
            filtered_df = filtered_df[filtered_df["SellPrice_numeric"] >= min_price]

        if max_price is not None:
            filtered_df = filtered_df[filtered_df["SellPrice_numeric"] <= max_price]

        if material:
            filtered_df = filtered_df[filtered_df["material"].str.contains(material, case=False, na=False)]

        if size:
            # Check if size is in the sizes_list
            filtered_df = filtered_df[
                filtered_df["sizes_list"].apply(
                    lambda sizes: any(size.lower() in s.lower() for s in sizes) if sizes else False
                )
            ]

        if price_range:
            filtered_df = filtered_df[filtered_df["price_range"] == price_range]

        return filtered_df

    def get_similar_products(self, product_id: int, top_k: int = 10) -> List[Dict]:
        """
        Find similar products based on multiple features.

        Args:
            product_id: ID of the reference product
            top_k: Number of similar products to return

        Returns:
            List of similar product dictionaries with similarity scores
        """
        if self.products is None:
            raise ValueError("Index not built. Call build_index() first.")

        # Get reference product
        ref_product = self.products[self.products["product_id"] == product_id]
        if ref_product.empty:
            raise ValueError(f"Product with ID {product_id} not found")

        ref_idx = ref_product.index[0]

        # Calculate text similarity
        reference_vector = self.tfidf_matrix[ref_idx : ref_idx + 1]
        text_similarities = cosine_similarity(reference_vector, self.tfidf_matrix)[0]

        # Calculate price similarity (inverse of normalized price difference)
        ref_price = ref_product["SellPrice_numeric"].iloc[0]
        price_diffs = np.abs(self.products["SellPrice_numeric"] - ref_price)
        max_price_diff = price_diffs.max()
        price_similarities = 1 - (price_diffs / max_price_diff) if max_price_diff > 0 else np.ones(len(self.products))

        # Calculate category similarity (binary: same category = 1, different = 0)
        ref_category = ref_product["Category"].iloc[0]
        category_similarities = (self.products["Category"] == ref_category).astype(float)

        # Combine similarities with weights
        combined_similarities = (
            self.feature_weights["text_similarity"] * text_similarities
            + self.feature_weights["price_similarity"] * price_similarities
            + self.feature_weights["category_similarity"] * category_similarities
        )

        # Exclude the reference product itself
        combined_similarities[ref_idx] = 0

        # Get top similar products
        top_indices = combined_similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            product = self.products.iloc[idx].to_dict()
            product["similarity_score"] = float(combined_similarities[idx])
            product["text_similarity"] = float(text_similarities[idx])
            product["price_similarity"] = float(price_similarities[idx])
            product["category_similarity"] = float(category_similarities[idx])
            results.append(product)

        return results

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by its ID."""
        if self.products is None:
            raise ValueError("Index not built. Call build_index() first.")

        product = self.products[self.products["product_id"] == product_id]
        return product.iloc[0].to_dict() if not product.empty else None

    def get_products_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Get products from a specific category."""
        filtered_products = self.filter_products(category=category)
        return filtered_products.head(limit).to_dict("records")

    def get_trending_products(self, limit: int = 20) -> List[Dict]:
        """
        Get trending products based on discount percentage and price range.
        Higher discounts and mid-range prices are considered more trending.
        """
        if self.products is None:
            raise ValueError("Index not built. Call build_index() first.")

        # Create a trending score based on discount and inverse price
        trending_scores = (
            self.products["Discount_numeric"].fillna(0) * 0.7
            + (1 / (self.products["SellPrice_numeric"].fillna(1000) / 1000)) * 0.3
        )

        top_indices = trending_scores.nlargest(limit).index
        trending_products = self.products.loc[top_indices].to_dict("records")

        # Add trending scores
        for i, product in enumerate(trending_products):
            product["trending_score"] = float(trending_scores[top_indices[i]])

        return trending_products

    def save_index(self, index_path: str):
        """Save the built index to disk."""
        if self.products is None:
            raise ValueError("Index not built. Call build_index() first.")

        index_data = {
            "products": self.products,
            "tfidf_vectorizer": self.tfidf_vectorizer,
            "tfidf_matrix": self.tfidf_matrix,
            "price_scaler": self.price_scaler,
            "feature_weights": self.feature_weights,
        }

        with open(index_path, "wb") as f:
            pickle.dump(index_data, f)

    def load_index(self, index_path: str):
        """Load a pre-built index from disk."""
        with open(index_path, "rb") as f:
            index_data = pickle.load(f)

        self.products = index_data["products"]
        self.tfidf_vectorizer = index_data["tfidf_vectorizer"]
        self.tfidf_matrix = index_data["tfidf_matrix"]
        self.price_scaler = index_data["price_scaler"]
        self.feature_weights = index_data["feature_weights"]

        print(f"Index loaded successfully for {len(self.products)} products")

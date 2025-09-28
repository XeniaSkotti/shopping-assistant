"""
Data preprocessor for the fashion dataset.
Handles cleaning, transformation, and preparation of product data for indexing.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional
from pathlib import Path


class DataPreprocessor:
    """Preprocesses fashion dataset for indexing and search."""

    def __init__(self, data_path: str, currency_conversion_rate: float = 0.0095):
        """
        Initialize the preprocessor.

        Args:
            data_path: Path to the CSV file containing fashion data
            currency_conversion_rate: Conversion rate from INR to GBP (default: 0.0095)
        """
        self.data_path = Path(data_path)
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        self.currency_conversion_rate = currency_conversion_rate

    def load_data(self) -> pd.DataFrame:
        """Load the raw dataset from CSV."""
        self.raw_data = pd.read_csv(self.data_path)
        return self.raw_data

    def clean_price_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and convert price columns to numeric values, converting INR to GBP."""
        df_clean = df.copy()

        # Clean MRP column (remove 'Rs' and convert to numeric)
        df_clean["MRP_numeric"] = (
            df_clean["MRP"].astype(str).str.replace("Rs\n", "", regex=False).str.replace(",", "").astype(float)
        )

        # Clean SellPrice column
        df_clean["SellPrice_numeric"] = pd.to_numeric(df_clean["SellPrice"], errors="coerce")

        # Convert prices from INR to GBP
        df_clean["MRP_numeric_gbp"] = df_clean["MRP_numeric"] * self.currency_conversion_rate
        df_clean["SellPrice_numeric_gbp"] = df_clean["SellPrice_numeric"] * self.currency_conversion_rate

        # Round to 2 decimal places for currency
        df_clean["MRP_numeric_gbp"] = df_clean["MRP_numeric_gbp"].round(2)
        df_clean["SellPrice_numeric_gbp"] = df_clean["SellPrice_numeric_gbp"].round(2)

        # Keep original INR columns for reference, but use GBP as primary
        df_clean["MRP_numeric"] = df_clean["MRP_numeric_gbp"]
        df_clean["SellPrice_numeric"] = df_clean["SellPrice_numeric_gbp"]

        # Clean Discount column (extract percentage)
        df_clean["Discount_numeric"] = df_clean["Discount"].str.extract(r"(\d+)").astype(float)

        return df_clean

    def parse_sizes(self, size_string: str) -> List[str]:
        """Parse size information from the size string."""
        if pd.isna(size_string):
            return []

        # Extract sizes from the format "Size:Large,Medium,Small,X-Large,X-Small"
        if "Size:" in str(size_string):
            sizes_part = size_string.split("Size:")[1]
            sizes = [size.strip() for size in sizes_part.split(",")]
            return sizes
        return []

    def extract_features_from_details(self, details: str) -> Dict[str, str]:
        """Extract product features from the details column."""
        if pd.isna(details):
            return {}

        features = {}
        details_lower = details.lower()

        # Extract material
        materials = ["cotton", "polyester", "silk", "wool", "denim", "linen", "viscose", "rayon"]
        for material in materials:
            if material in details_lower:
                features["material"] = material
                break

        # Extract fit type
        fits = ["regular fit", "slim fit", "loose fit", "tight fit", "oversized"]
        for fit in fits:
            if fit in details_lower:
                features["fit"] = fit
                break

        # Extract neck type
        necks = ["collar neck", "v-neck", "round neck", "boat neck", "turtleneck", "cowl neck"]
        for neck in necks:
            if neck in details_lower:
                features["neck_type"] = neck
                break

        # Extract pattern
        patterns = ["solid", "striped", "printed", "checked", "floral", "geometric"]
        for pattern in patterns:
            if pattern in details_lower:
                features["pattern"] = pattern
                break

        # Extract garment type
        garments = ["dress", "top", "jeans", "shirt", "blouse", "skirt", "pants", "jacket"]
        for garment in garments:
            if garment in details_lower:
                features["garment_type"] = garment
                break

        return features

    def create_search_text(self, row: pd.Series) -> str:
        """Create a comprehensive search text for each product."""
        search_parts = []

        # Add brand name
        if pd.notna(row["BrandName"]):
            search_parts.append(row["BrandName"])

        # Add details
        if pd.notna(row["Deatils"]):
            search_parts.append(row["Deatils"])

        # Add category
        if pd.notna(row["Category"]):
            search_parts.append(row["Category"])

        # Add extracted features
        for feature in ["material", "fit", "neck_type", "pattern", "garment_type"]:
            if feature in row and pd.notna(row[feature]):
                search_parts.append(row[feature])

        return " ".join(search_parts).lower()

    def categorize_price_range(self, price: float) -> str:
        """Categorize products into price ranges (in GBP)."""
        if pd.isna(price):
            return "unknown"
        elif price < 5:  # Under £5 (was ₹500)
            return "budget"
        elif price < 15:  # £5-15 (was ₹500-1500)
            return "mid-range"
        elif price < 30:  # £15-30 (was ₹1500-3000)
            return "premium"
        else:  # Over £30 (was ₹3000+)
            return "luxury"

    def clean_categories(self, category: str) -> str:
        """Clean and standardize category names."""
        if pd.isna(category):
            return "Other"

        # Dictionary for category mapping and cleaning
        category_mapping = {
            "westernwear-women": "Western Wear",
            "indianwear-women": "Indian Wear",
            "lingerie&nightwear-women": "Lingerie & Nightwear",
            "footwear-women": "Footwear",
            "watches-women": "Watches",
            "jewellery-women": "Jewellery",
            "fragrance-women": "Fragrance",
        }

        # Normalize the category string
        cleaned = str(category).lower().strip()

        # Remove extra spaces and normalize separators
        cleaned = re.sub(r"\s+", " ", cleaned)  # Multiple spaces to single
        cleaned = cleaned.replace(" - ", "-")  # Normalize hyphens
        cleaned = cleaned.replace("_", "-")  # Underscores to hyphens

        # Use mapping if available, otherwise clean it up
        if cleaned in category_mapping:
            return category_mapping[cleaned]

        # Fallback: remove "-women" suffix and clean up
        if cleaned.endswith("-women"):
            cleaned = cleaned[:-6]  # Remove "-women"

        # Replace & with "and", capitalize words
        cleaned = cleaned.replace("&", " and ")
        cleaned = cleaned.replace("-", " ")

        # Title case and clean up extra spaces
        cleaned = " ".join(word.capitalize() for word in cleaned.split())

        return cleaned if cleaned else "Other"

    def process_dataset(self) -> pd.DataFrame:
        """Process the entire dataset with all cleaning and feature extraction."""
        if self.raw_data is None:
            self.load_data()

        df = self.raw_data.copy()

        # Remove unnamed index column
        if "Unnamed: 0" in df.columns:
            df = df.drop("Unnamed: 0", axis=1)

        # Clean price columns
        df = self.clean_price_columns(df)

        # Parse sizes
        df["sizes_list"] = df["Sizes"].apply(self.parse_sizes)
        df["size_count"] = df["sizes_list"].apply(len)

        # Extract features from details
        feature_dicts = df["Deatils"].apply(self.extract_features_from_details)

        # Add features as separate columns
        for feature in ["material", "fit", "neck_type", "pattern", "garment_type"]:
            df[feature] = feature_dicts.apply(lambda x: x.get(feature, np.nan))

        # Create price range categories
        df["price_range"] = df["SellPrice_numeric"].apply(self.categorize_price_range)

        # Create search text
        df["search_text"] = df.apply(self.create_search_text, axis=1)

        # Add product ID
        df["product_id"] = df.index

        # Clean brand names
        df["BrandName"] = df["BrandName"].str.strip().str.lower()

        # Clean and standardize categories
        df["Category_Raw"] = df["Category"]  # Keep original for reference
        df["Category"] = df["Category"].apply(self.clean_categories)

        self.processed_data = df
        return df

    def save_processed_data(self, output_path: str):
        """Save the processed dataset to a file."""
        if self.processed_data is None:
            raise ValueError("No processed data available. Run process_dataset() first.")

        output_path = Path(output_path)

        if output_path.suffix == ".csv":
            self.processed_data.to_csv(output_path, index=False)
        elif output_path.suffix == ".json":
            self.processed_data.to_json(output_path, orient="records", indent=2)
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")

    def get_data_summary(self) -> Dict:
        """Get a summary of the processed dataset."""
        if self.processed_data is None:
            raise ValueError("No processed data available. Run process_dataset() first.")

        df = self.processed_data

        summary = {
            "total_products": len(df),
            "unique_brands": df["BrandName"].nunique(),
            "categories": df["Category"].value_counts().to_dict(),
            "price_ranges": df["price_range"].value_counts().to_dict(),
            "materials": df["material"].value_counts().to_dict(),
            "garment_types": df["garment_type"].value_counts().to_dict(),
            "price_stats": {
                "min_price": df["SellPrice_numeric"].min(),
                "max_price": df["SellPrice_numeric"].max(),
                "avg_price": df["SellPrice_numeric"].mean(),
                "median_price": df["SellPrice_numeric"].median(),
            },
        }

        return summary

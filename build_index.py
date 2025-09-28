#!/usr/bin/env python3
"""
Rebuild the index with cleaned categories and GBP currency conversion.
"""

import sys
from pathlib import Path
from shopping_assistant.indexing import SearchEngine

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def main():
    """Build the index."""
    print("🔄 Building index...")

    # Paths
    data_path = project_root / "data" / "FashionDataset.csv"
    processed_data_path = project_root / "data" / "processed_fashion_data.csv"
    index_path = project_root / "data" / "product_index_clean.pkl"

    # Currency conversion rate (INR to GBP)
    exchange_rate = 0.0095

    print(f"💱 Using exchange rate: 1 INR = {exchange_rate} GBP")
    print(f"🧹 Cleaning categories and processing data from: {data_path}")

    # Initialize search engine with currency conversion
    search_engine = SearchEngine()
    search_engine.initialize_from_csv(str(data_path), currency_conversion_rate=exchange_rate)

    # Save the new index
    print(f"\n💾 Saving cleaned index to: {index_path}")
    search_engine.save_index(str(index_path))

    if search_engine.preprocessor and search_engine.preprocessor.processed_data is not None:
        print(f"💾 Saving cleaned processed data to: {processed_data_path}")
        search_engine.preprocessor.save_processed_data(str(processed_data_path))


if __name__ == "__main__":
    main()

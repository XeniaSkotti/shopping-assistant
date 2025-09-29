"""
Data preprocessor for the fashion dataset.
Handles cleaning, transformation, and preparation of product data for indexing.
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional

CURRENCY_RE = re.compile(r"[₹]|Rs\.?|INR|,|\s", re.IGNORECASE)

COLOR_FAMILY = {
    "red": ["red", "crimson", "maroon", "burgundy", "scarlet", "rust"],
    "blue": ["blue", "navy", "teal", "turquoise", "cobalt", "azure", "indigo", "midnight", "denim", "aqua", "ocean"],
    "green": ["green", "olive", "mint", "emerald", "sage", "peacock", "lime", "forest", "khaki", "jade"],
    "black": ["black", "ebony", "jet", "charcoal", "onyx", "coal"],
    "white": ["white", "ivory", "off[- ]white", "cream"],
    "yellow": ["yellow", "mustard", "gold", "lemon", "honey", "ecru"],
    "pink": ["pink", "rose", "blush", "coral", "peach", "fuchsia", "magenta", "bubblegum"],
    "purple": ["purple", "lavender", "lilac", "violet", "plum", "mauve", "amethyst", "orchid"],
    "orange": ["orange", "tangerine"],
    "brown": ["brown", "tan", "camel", "chocolate", "coffee", "mocha", "bronze", "copper"],
    "grey": ["grey", "gray", "charcoal", "slate", "graphite", "silver", "ash"],
    "beige": ["beige", "natural", "nude", "sand"],
    "multi": ["multi[- ]?color", "multicolor", "multicolour", "multi", "mixed"],
}
# precompile family patterns
COLOR_PATTERNS = {
    fam: re.compile(r"\b(" + "|".join(vals) + r")\b", re.IGNORECASE) for fam, vals in COLOR_FAMILY.items()
}

PRODUCT_TYPES = [
    "dress",
    "top",
    "jeans",
    "shirt",
    "blouse",
    "skirt",
    "pants",
    "trousers",
    "jacket",
    "saree",
    "kurta",
    "tunic",
    "lehenga",
    "palazzo",
    "jumpsuit",
    "romper",
    "shorts",
    "cardigan",
    "sweater",
    "hoodie",
    "coat",
    "shoes",
    "heels",
    "flats",
    "boots",
    "sandals",
    "sneakers",
    "loafers",
    "slippers",
    "watch",
    "bracelet",
    "necklace",
    "earrings",
    "ring",
    "pendant",
    "bangle",
    "handbag",
    "purse",
    "wallet",
    "clutch",
    "backpack",
    "tote",
    "bra",
    "panties",
    "lingerie",
    "nightwear",
    "sleepwear",
    "robe",
]
PRODUCT_RE = re.compile(r"\b(" + "|".join(map(re.escape, PRODUCT_TYPES)) + r")\b", re.IGNORECASE)

SIZE_TOKEN_RE = re.compile(r"\b(XXS|XS|S|M|L|XL|XXL|XXXL|3XL|4XL|\d{2})\b", re.IGNORECASE)
SIZE_NORMALIZE = {
    "xxs": "XXS",
    "xs": "XS",
    "s": "S",
    "m": "M",
    "l": "L",
    "xl": "XL",
    "xxl": "XXL",
    "xxxl": "3XL",
    "3xl": "3XL",
    "4xl": "4XL",
}


class DataPreprocessor:
    def __init__(self, data_path: str, currency_conversion_rate: float = 0.0095):
        self.data_path = Path(data_path)
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None
        self.currency_conversion_rate = currency_conversion_rate

    def load(self):
        df = pd.read_csv(self.data_path)
        self.raw_data = df.rename(columns={"Deatils": "Details"})

    def process(self):
        if self.raw_data is None:
            self.load()

        df = self.raw_data.copy()
        if "Unnamed: 0" in df.columns:
            df = df.drop(columns=["Unnamed: 0"])

        df = self._clean_prices(df)
        df["sizes"] = self._parse_sizes_series(df.get("Sizes"))
        df["sizes_count"] = df["sizes"].apply(len)

        # brand
        if "BrandName" in df.columns:
            df["brand"] = df["BrandName"].astype(str).str.strip().str.lower()
            df = df.drop(columns=["BrandName"])

        # category
        if "Category" in df.columns:
            df["category"] = df["Category"].apply(self._clean_category)
            df = df.drop(columns=["Category"])

        # light features from Details: color + product_type only
        details = df.get("Details").astype(str).str.lower()
        df["color_family"] = self._extract_color_family(details)
        df["product_type"] = details.str.extract(PRODUCT_RE, expand=False).str.lower()

        # price bucket (simple, cheap heuristic)
        df["price_range"] = df["sell_price"].apply(self._price_bucket)

        # stable id
        df["product_id"] = df.index.astype(int)

        # final: lowercase all column names once
        df.columns = [c.lower() for c in df.columns]
        self.processed_data = df

    def save(self, output_path: str):
        if self.processed_data is None:
            raise ValueError("No processed data available. Run process() first.")
        p = Path(output_path)
        if p.suffix == ".csv":
            self.processed_data.to_csv(p, index=False)
        elif p.suffix == ".json":
            self.processed_data.to_json(p, orient="records", indent=2)
        else:
            raise ValueError("Unsupported file format. Use .csv or .json")

    # ---- helpers ----
    def _clean_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        # resilient numeric parse
        if "MRP" in out.columns:
            mrp_num = (
                out["MRP"].astype(str).str.replace("\n", " ", regex=False).str.replace(CURRENCY_RE, "", regex=True)
            )
            out["mrp"] = pd.to_numeric(mrp_num, errors="coerce")
        if "SellPrice" in out.columns:
            sp_num = out["SellPrice"].astype(str).str.replace(CURRENCY_RE, "", regex=True)
            out["sell_price"] = pd.to_numeric(sp_num, errors="coerce")
            out = out.drop(columns=["SellPrice"])

        # convert INR→GBP
        for col in ["mrp", "sell_price"]:
            if col in out.columns:
                out[col] = (out[col] * self.currency_conversion_rate).round(2)

        # backfill sell_price from mrp if missing
        if "sell_price" in out.columns and "mrp" in out.columns:
            out["sell_price"] = out["sell_price"].fillna(out["mrp"])

        # discount %
        if "Discount" in out.columns:
            out["discount_pct"] = out["Discount"].astype(str).str.extract(r"(\d+)", expand=False).astype(float)
            out = out.drop(columns=["Discount"])

        return out

    def _parse_sizes_series(self, sizes: Optional[pd.Series]) -> pd.Series:
        if sizes is None:
            return pd.Series([[]] * len(self.raw_data), index=self.raw_data.index)

        def parse_one(s: str) -> List[str]:
            if pd.isna(s):
                return []
            tokens = SIZE_TOKEN_RE.findall(str(s))
            norm = []
            for t in tokens:
                t_low = t.lower()
                norm.append(SIZE_NORMALIZE.get(t_low, t.upper()))
            # preserve numeric waist sizes as-is
            return sorted(set(norm), key=lambda x: (len(x), x))

        return sizes.apply(parse_one)

    def _extract_color_family(self, s: pd.Series) -> pd.Series:
        def find_family(text: str) -> Optional[str]:
            for fam, pat in COLOR_PATTERNS.items():
                if pat.search(text):
                    return fam
            return np.nan

        return s.apply(find_family)

    def _price_bucket(self, price: float) -> str:
        if pd.isna(price):
            return "unknown"
        if price < 5:
            return "budget"
        if price < 15:
            return "mid-range"
        if price < 30:
            return "premium"
        return "luxury"

    def _clean_category(self, cat: str) -> str:
        if pd.isna(cat):
            return "Other"
        mapping = {
            "westernwear-women": "Western Wear",
            "indianwear-women": "Indian Wear",
            "lingerie&nightwear-women": "Lingerie & Nightwear",
            "footwear-women": "Footwear",
            "watches-women": "Watches",
            "jewellery-women": "Jewellery",
            "fragrance-women": "Fragrance",
        }
        cleaned = str(cat).lower().strip()
        label = mapping.get(cleaned, cleaned.replace("&", " and ").replace("-", " "))
        return label.title() if label else "Other"

#!/usr/bin/env python3
import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from preprocessor import DataPreprocessor as Preprocessor

DB_PATH = Path("data/products.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
CORE_CATEGORIES = ["Western Wear", "Indian Wear", "Lingerie & Nightwear", "Footwear"]


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def create_schema(conn: sqlite3.Connection, schema_sql_path: Path = SCHEMA_PATH):
    with open(schema_sql_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def preprocess(csv_path: Path) -> pd.DataFrame:
    """Run your existing Preprocessor and return a trimmed dataframe ready for insert."""
    dp = Preprocessor(str(csv_path))
    dp.process()  # your class loads internally if needed
    df = dp.processed_data.copy()

    # --- light post-processing for DB invariants ---
    # Core flag (don’t drop anything; just tag)
    df["is_core"] = df["category"].astype(str).str.lower().isin(CORE_CATEGORIES).astype(int)

    # Ensure sell_price present (backfill from mrp if missing)
    if "mrp" in df.columns:
        df["sell_price"] = df["sell_price"].fillna(df["mrp"])
    # Drop any rows still missing price (rare but prevents price filter failures)
    df = df[~df["sell_price"].isna()].copy()

    # Serialize sizes list to JSON text
    def to_json_list(x):
        if isinstance(x, list):
            return json.dumps(x)
        return json.dumps([])

    df["sizes"] = df.get("sizes", pd.Series([], dtype=object)).apply(to_json_list)

    # Optional provenance
    df["source_file"] = str(csv_path)
    df["ingest_ts"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def to_product_type_str(x):
        if isinstance(x, list):
            return ", ".join(map(str, x))
        return str(x) if x is not None else ""

    df["product_type"] = df.get("product_type", pd.Series([], dtype=object)).apply(to_product_type_str)

    # Keep only columns that exist in the table (add missing as None)
    cols = [
        "product_id",
        "title",
        "details",
        "brand",
        "category",
        "is_core",
        "color_family",
        "product_type",
        "sizes",
        "sizes_count",
        "mrp",
        "sell_price",
        "discount_pct",
        "price_range",
        "source_file",
        "ingest_ts",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = None

    # product_id must be int (SQLite PRIMARY KEY)
    df["product_id"] = df["product_id"].astype(int)
    return df[cols]


def insert_products(conn: sqlite3.Connection, df: pd.DataFrame):
    rows = df.to_dict(orient="records")
    sql = """
    INSERT INTO products
      (product_id, title, details, brand, category, is_core,
       color_family, product_type, sizes, sizes_count,
       mrp, sell_price, discount_pct, price_range, source_file, ingest_ts)
    VALUES
      (:product_id, :title, :details, :brand, :category, :is_core,
       :color_family, :product_type, :sizes, :sizes_count,
       :mrp, :sell_price, :discount_pct, :price_range, :source_file, :ingest_ts)
    ON CONFLICT(product_id) DO UPDATE SET
       title=excluded.title,
       details=excluded.details,
       brand=excluded.brand,
       category=excluded.category,
       is_core=excluded.is_core,
       color_family=excluded.color_family,
       product_type=excluded.product_type,
       sizes=excluded.sizes,
       sizes_count=excluded.sizes_count,
       mrp=excluded.mrp,
       sell_price=excluded.sell_price,
       discount_pct=excluded.discount_pct,
       price_range=excluded.price_range,
       source_file=excluded.source_file,
       ingest_ts=excluded.ingest_ts;
    """
    with conn:  # single transaction for speed & atomicity
        conn.executemany(sql, rows)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True, help="Path to raw CSV")
    p.add_argument("--db", type=Path, default=DB_PATH, help="Path to SQLite DB")
    p.add_argument("--sample", type=int, default=1000, help="Number of rows to ingest (post-process)")
    return p.parse_args()


def main():
    args = parse_args()
    df = preprocess(args.csv).sort_values("product_id")
    if args.sample:
        df = df.head(args.sample).copy()

    conn = connect(args.db)
    create_schema(conn)
    insert_products(conn, df)

    # tiny smoke test
    cur = conn.cursor()
    (total,) = cur.execute("SELECT COUNT(*) FROM products;").fetchone()
    (core,) = cur.execute("SELECT COUNT(*) FROM products WHERE is_core=1;").fetchone()
    print(f"Ingested rows: {len(df)} | Table count: {total} | Core: {core}")
    conn.close()


if __name__ == "__main__":
    main()

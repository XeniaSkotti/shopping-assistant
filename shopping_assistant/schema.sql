PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS products (
  product_id     INTEGER PRIMARY KEY,   -- from your df index or a stable id
  title          TEXT,                  -- optional if you have it
  details        TEXT,
  brand          TEXT,
  category       TEXT,                  -- "Western Wear", ...
  is_core        INTEGER NOT NULL,      -- 1 = apparel/footwear/bags, 0 = watches/jewellery/fragrance
  color_family   TEXT,                  -- "red","blue",...
  product_type   TEXT,                  -- "dress","kurta",...
  sizes          TEXT,                  -- JSON array as string
  sizes_count    INTEGER,
  mrp            REAL,
  sell_price     REAL NOT NULL,         -- backfilled from mrp if needed
  discount_pct   REAL,
  price_range    TEXT,                  -- "budget/mid-range/premium/luxury"
  source_file    TEXT,                  -- optional provenance
  ingest_ts      TEXT                   -- ISO timestamp
);

CREATE INDEX IF NOT EXISTS ix_products_category ON products(category);
CREATE INDEX IF NOT EXISTS ix_products_brand    ON products(brand);
CREATE INDEX IF NOT EXISTS ix_products_color    ON products(color_family);
CREATE INDEX IF NOT EXISTS ix_products_price    ON products(sell_price);
CREATE INDEX IF NOT EXISTS ix_products_core     ON products(is_core);
CREATE INDEX IF NOT EXISTS ix_products_type     ON products(product_type);

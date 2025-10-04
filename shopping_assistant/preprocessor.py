"""
Data preprocessor for the fashion dataset.
Handles cleaning, transformation, and preparation of product data for indexing.
"""
import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CURRENCY_RE = re.compile(r"[₹]|Rs\.?|INR|,|\s", re.IGNORECASE)

COLOR_FAMILY = {
    "red": [
        "red",
        "crimson",
        "maroon",
        "burgundy",
        "scarlet",
        "rust",
        "wine",
        "cherry",
        "ruby",
        "bordeaux",
        "rosewood",
        "tomato",
        "blood",
        "carmine",
        "cranberry",
        "rouge",
        "port",
        "terracotta",
    ],
    "blue": [
        "blue",
        "navy",
        "teal",
        "turquoise",
        "cobalt",
        "azure",
        "indigo",
        "midnight",
        "denim",
        "aqua",
        "ocean",
        "ice",
        "denimex",
        "rinse",
        "midstone",
        "dark streak",
        "indiaink",
        "ultramarine",
        "royal",
        "sapphire",
        "cornflower",
        "glacier",
        "neptune",
        "lapis",
        "lapiz",
        "canal",
        "sky",
        "air force",
        "cadet",
        "placid",
        "weft_blue",
        "twilight",
    ],
    "green": [
        "green",
        "olive",
        "mint",
        "emerald",
        "sage",
        "peacock",
        "lime",
        "forest",
        "khaki",
        "jade",
        "pistachio",
        "seagreen",
        "cactus",
        "fluid_olive",
        "teal_green",
        "spruce",
        "meadow",
        "alpine",
        "cilantro",
    ],
    "black": ["black", "ebony", "jet", "onyx", "coal", "raven", "eclipse", "black_satin", "blackout", "ink", "carbon"],
    "white": [
        "white",
        "ivory",
        "cream",
        "ecru",
        "shell",
        "oyster",
        "pearl",
        "porcelain",
        "snow",
        "vanilla",
        r"off[ _-]?white",
        "eggshell",
        "cloud",
        "chalk",
        "marble",
        "bleach",
    ],
    "yellow": ["yellow", "mustard", "lemon", "honey", "maize", "butter", "corn", "sulphur", "buttercup"],
    "pink": [
        "pink",
        "rose",
        "blush",
        "coral",
        "peach",
        "fuchsia",
        "magenta",
        "bubblegum",
        "salmon",
        "berry",
        "onion[ _-]?pink",
        "raspberry",
    ],
    "purple": [
        "purple",
        "lavender",
        "lilac",
        "violet",
        "plum",
        "mauve",
        "amethyst",
        "orchid",
        "grape",
        "mulberry",
        "aubergine",
        "thistle",
        "cadbury",
        "prune",
    ],
    "orange": [
        "orange",
        "tangerine",
        "jaffa",
        "melon",
        "mango",
        "apricot",
        "carrot",
        "ochre",
        "paprika",
        "harvest",
        "amber",
        "cider",
        "sunset",
    ],
    "brown": [
        "brown",
        "tan",
        "camel",
        "chocolate",
        "coffee",
        "mocha",
        "bronze",
        "copper",
        "walnut",
        "chestnut",
        "bark",
        "bracken",
        "cocoa",
        "maple",
        "nutmeg",
    ],
    "grey": [
        "grey",
        "gray",
        "charcoal",
        "slate",
        "graphite",
        "silver",
        "ash",
        "stone",
        "gunmetal",
        r"anthra(?:\s+melange)?",
        "anthra",
        "darkslate",
        "glaze",
        "granite",
    ],
    "beige": ["beige", "natural", "nude", "sand", "taupe"],
    "multi": ["multi[- ]?color", "multicolor", "multicolour", "multi", "mixed", "print", "106_multi"],
    "metallic": ["gold", "silver", "bronze", "copper", "rose[ -]?gold"],
}
# precompile family patterns
COLOR_PATTERNS = {
    fam: re.compile(r"\b(" + "|".join(vals) + r")\b", re.IGNORECASE) for fam, vals in COLOR_FAMILY.items()
}

MISSPELLINGS = {
    r"\bfuschia\b": "fuchsia",
    r"\bburgandy\b": "burgundy",
    r"\bnavyblue\b": "navy blue",
    r"\bgrey\b": "gray",  # or keep both, up to you
    r"\bgren\b": "green",
    r"\bwhte\b": "white",
    r"\bblck\b": "black",
}

TAXONOMY: Dict[str, List[str]] = {
    # Outerwear
    "blazer": ["blazer", "notched lapel", "lapel blazer"],
    "coat": ["coat", "overcoat", "trench coat", "peacoat", "pea coat"],
    "poncho/cape": ["poncho", "cape"],
    "jacket": ["jacket", "bomber", "puffer", "denim jacket", "biker jacket"],
    # Knit/Fleece tops
    "sweatshirt": ["sweatshirt", "sweat shirt", "crew neck fleece", "zip-up hoodie", "zip through"],
    "hoodie": ["hoodie"],
    # Co-ords & sets
    "co-ord set": ["co-ord", "co ord", "coordinate set", "co-ordinates"],
    "western set": ["evening wear set", "women's set", "womens set"],
    "ethnic set": [
        "suit set",
        "indian wear set",
        "kurta set",
        "straight suit set",
        "ethnic set",
        "clothing set",
        "coordinate set",
    ],
    # One-pieces
    "dress": ["dress"],
    "gown": ["gown", "maxi"],
    "jumpsuit": ["jump suit", "jumpsuit"],
    "romper": ["romper", "playsuit"],
    "kaftan": ["kaftan"],
    "dungarees": ["dungarees", "overalls"],
    # Tops
    "top": ["top", "camisole", "tank", "crop top", "bodysuit"],
    "tshirt": ["t-shirt", "tshirt", "tee"],
    "shirt": ["shirt", "button down", "button-down", "oxford"],
    "blouse": ["blouse"],
    "sweater": ["sweater", "pullover", "jumper"],
    "cardigan": ["cardigan", "shrug"],
    "kurta": ["kurta", "kurti"],
    "tunic": ["tunic"],
    # Bottoms
    "pants": ["pant", "pants", "chino", "chinos", "formal pants", "casual pants", "paper bag pants"],
    "trousers": ["trouser", "trousers"],
    "track pants": ["track pants", "trackpants", "tracks"],  # we'll disambiguate tracksuit later
    "joggers": ["jogger", "joggers", "jogger pants", "jogger fit"],
    "leggings": ["legging", "leggings", "churidar"],
    "tights": ["tight", "tights"],
    "jeggings": ["jeggings", "denim leggings"],
    "treggings": ["treggings"],
    "jeans": ["jean", "jeans", "denim"],
    "shorts": ["shorts", "hot pant", "hot pants"],
    "capris": ["capri", "capris"],
    "culottes": ["culottes"],
    "palazzo": ["palazzo"],
    "dhoti pants": ["dhoti pant", "dhoti pants"],
    "skirt": ["skirt", "maxi skirt"],
    "thermal pants": ["thermal pant", "thermal pants", "thermal bottoms", "thermal leggings"],
    # Ethnic & occasion
    "saree": ["sari", "saree"],
    "lehenga": ["lehenga"],
    "salwar": ["salwar", "shalwar"],
    "salwar suit": ["salwar suit", "unstitched suit"],
    "choli": ["choli"],
    "dupatta": ["dupatta"],
    "sharara": ["sharara"],
    "festive set": ["festive set"],
    # Sleep & lounge
    "pyjamas": ["pyjama", "pyjamas", "pajama", "pajamas"],
    "nightdress": ["night dress", "nightdress", "nighty", "nightie"],
    "sleep set": ["sleep set", "lounge set"],
    "lounge pants": ["lounge pant", "lounge pants"],
    "tracksuit": ["track suit", "tracksuit"],
    "robe": ["robe"],
    "chemise": ["chemise"],
    "babydoll": ["baby doll", "babydoll"],
    "sleepsuit": ["sleepsuit", "sleep suit"],
    # Swimwear & shapewear
    "monokini": ["monokini"],
    "swim set": ["swim set"],
    "shapewear": ["shapewear", "tummy tucker", "tummy control", "thigh slimmer", "waist cincher", "hi waist slimmer"],
    # Bags & SLG
    "handbag": ["handbag", "hand bag"],
    "wallet": ["wallet"],
    "clutch": ["clutch"],
    "backpack": ["backpack", "back pack"],
    "tote": ["tote"],
    "belt": ["belt"],
    # Footwear
    "slides": ["slides", "slide"],
    "loafers": ["loafers", "loafer"],
    "mules": ["mules", "mule"],
    "wedges": ["wedges", "wedge"],
    "platforms": ["platforms", "platform"],
    "brogues": ["brogues", "oxford", "oxfords"],
    "bellies": ["bellies", "ballet flats", "ballet flat"],
    "peep toes": ["peep toes", "peep toe"],
    "clogs": ["clogs", "clog"],
    "floaters": ["floaters", "floater"],
    "slip-ons": ["slip-ons", "slip ons", "slip on"],
    "shoes": ["shoes", "shoe"],
    "heels": ["heels", "heel", "stiletto", "stilettos", "pump", "pumps"],
    "flats": ["flats", "flat", "ballerina", "ballerinas"],
    "boots": ["boots", "boot"],
    "sandals": ["sandals", "sandal"],
    "sneakers": ["sneakers", "sneaker", "trainers", "trainer"],
    "slippers": ["slippers", "slipper", "flip flops", "flip-flops", "flip flop"],
    # Jewelry
    "bracelet": ["bracelet"],
    "necklace": ["necklace"],
    "earrings": ["earring", "earrings", "stud", "studs", "jhumka", "jhumki", "jhumkas", "jhumkis"],
    "ring": ["ring", "rings"],
    "pendant": ["pendant"],
    "bangle": ["bangle", "kada", "kadas", "bangles"],
    # Innerwear
    "bralette": ["bralette"],
    "bra": ["bra", "brassiere"],
    "panties": ["panty", "panties", "briefs", "knickers", "thong", "thongs", "hipster", "hipsters"],
    "lingerie": ["lingerie", "intimates"],
    # Accessories
    "scarf": ["scarf", "scarves"],
    "stole": ["stole", "stoles"],
    "muffler": ["muffler", "mufflers"],
    "cap": ["cap", "baseball cap", "caps"],
    "face mask": ["face mask", "mask", "n95", "reusable mask"],
    "socks": ["sock", "socks", "no show socks", "ankle socks"],
    "thermal": ["thermal", "thermals"],
}


def _wb(s: str) -> str:
    """Wrap a token with word boundaries; allow spaces or hyphens between words."""
    # Replace spaces with [\\s-]+ and collapse duplicates, keep it escaped safely.
    s = re.escape(s.strip())
    s = re.sub(r"\\\s+", r"[\\s-]+", s)  # spaces -> [\s-]+
    # Optional plural for common nouns (very simple; irregulars covered via aliases list)
    # Only add (?:s|es)? if token ends with a letter and not already pluralized explicitly
    if not s.endswith(("s", "S")) and s.split(r"[\\s-]+")[-1].isalpha():
        s = f"{s}(?:e?s)?"
    return rf"\b{s}\b"


# 2) Build one regex per canonical from aliases (order agnostic)
CANONICAL_PATTERNS: Dict[str, re.Pattern] = {
    canon: re.compile("|".join(_wb(a) for a in aliases), re.IGNORECASE) for canon, aliases in TAXONOMY.items()
}

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
        df["product_type"] = details.apply(self._extract_product_type)

        # price bucket (simple, cheap heuristic)
        df["price_range"] = df["sell_price"].apply(self._price_bucket)

        # stable id
        df["product_id"] = df.index.astype(int)

        # final: lowercase all column names once
        df.columns = [c.lower() for c in df.columns]

        df = df.dropna(subset=["sell_price"], how="all")
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
            out["MRP"] = pd.to_numeric(mrp_num, errors="coerce")
        if "SellPrice" in out.columns:
            sp_num = out["SellPrice"].astype(str).str.replace(CURRENCY_RE, "", regex=True)
            out["sell_price"] = pd.to_numeric(sp_num, errors="coerce")
            out = out.drop(columns=["SellPrice"])

        # convert INR→GBP
        for col in ["MRP", "sell_price"]:
            if col in out.columns:
                out[col] = (out[col] * self.currency_conversion_rate).round(2)

        # backfill sell_price from MRP if missing
        if "sell_price" in out.columns and "MRP" in out.columns:
            out["sell_price"] = out["sell_price"].fillna(out["MRP"])

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

    def _normalize_spelling(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        t = text.lower()
        for bad, good in MISSPELLINGS.items():
            t = re.sub(bad, good, t)
        return t

    def _extract_color_family(self, s: pd.Series) -> pd.Series:
        def find_family(text: str) -> Optional[str]:
            for fam, pat in COLOR_PATTERNS.items():
                if pat.search(text):
                    return fam
            return np.nan

        s_norm = s.astype(str).apply(self._normalize_spelling)
        return s_norm.apply(find_family)

    def _post_rules(self, text: str, labels: List[str]) -> List[str]:
        """
        Apply compact, domain-specific cleanups to product labels.
        - Collapse kurta+dupatta+bottoms into 'salwar suit'
        - Prefer 'tracksuit' over 'track pants' when text says tracksuit
        - Guard 'jeans' when 'denim jacket' appears
        - Prefer specific footwear over generic ('slip-ons'/'shoes'/'flats')
        - Drop 'pendant' when 'necklace' is present
        Returns labels with original order preserved.
        """
        t = " " + re.sub(r"\s+", " ", text.lower()) + " "

        # Work set for quick membership; keep original order separately
        L = set(labels)

        # --- 1) Tracksuit vs track pants ---
        if " tracksuit " in t or " track suit " in t:
            L.discard("track pants")
            L.add("tracksuit")

        # --- 2) Denim jacket guard for 'jeans' ---
        if " denim jacket " in t:
            L.discard("jeans")

        # --- 3) Kurta-set collapse ---
        bottoms = {"salwar", "palazzo", "trousers", "leggings", "pants", "dhoti pants", "sharara"}
        if "kurta" in L and ("dupatta" in L or "choli" in L) and (L & bottoms):
            # collapse to salwar suit
            L -= {"kurta", "dupatta", "choli"} | bottoms
            L.add("salwar suit")
        elif "kurta" in L and (L & bottoms):
            # looser pairing without dupatta → ethnic set
            L.add("ethnic set")

        # --- 4) Footwear specificity ---
        specific = {
            "heels",
            "wedges",
            "sandals",
            "boots",
            "sneakers",
            "peep toes",
            "mules",
            "loafers",
            "platforms",
            "clogs",
            "slides",
            "floaters",
            "bellies",
            "brogues",
        }
        generic = {"slip-ons", "shoes", "flats"}
        if L & specific:
            L -= generic  # drop generics when any specific style is present

        # --- 5) Jewelry de-dup ---
        if "necklace" in L and "pendant" in L:
            L.discard("pendant")

        # Preserve original order, append any newly added labels at the end
        seen = set()
        ordered = [x for x in labels if x in L and not (x in seen or seen.add(x))]
        for x in L:
            if x not in seen:
                ordered.append(x)
                seen.add(x)
        return ordered

    def _extract_product_type(self, text: str) -> Optional[str]:
        # 1) collect all candidate matches
        candidates: List[Tuple[str, Tuple[int, int], str]] = []
        for canon, pat in CANONICAL_PATTERNS.items():
            for m in pat.finditer(text):
                candidates.append((canon, m.span(), m.group(0)))

        # 2) sort by longest match, then earliest start, then name
        candidates.sort(key=lambda x: (-(x[1][1] - x[1][0]), x[1][0], x[0]))

        # 3) resolve overlaps
        picked, occupied = [], []
        for canon, (a, b), s in candidates:
            if any(not (b <= x0 or a >= x1) for (x0, x1) in occupied):
                continue
            picked.append(canon)
            occupied.append((a, b))

        # 4) post rules (tiny, readable tweaks)
        t = " " + re.sub(r"\s+", " ", text.lower()) + " "
        labels = set(picked)

        if " track suit " in t or " tracksuit " in t:
            labels.discard("track pants")
            labels.add("tracksuit")

        if " denim jacket " in t:
            labels.discard("jeans")

        return self._post_rules(text, list(labels))

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

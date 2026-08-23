"""Beispiel-Export im Kalodata-Format - zum Ausprobieren ohne echten Account."""

from __future__ import annotations

import csv
import os
import random
from datetime import date, timedelta
from typing import List

HEADERS = ["Product ID", "Product Name", "Category", "Shop Name", "Price", "Revenue",
           "Items Sold", "Commission Rate", "Revenue Growth", "Rating", "Creators",
           "Videos", "Lives", "Launch Date", "Product Link"]

SAMPLES = [
    # (Name, Kategorie, Preis, Umsatz, Stueck, Provision, Wachstum, Rating, Creator, Videos, Alter in Tagen)
    ("LED Sunset Projector Lamp", "Home Supplies", 24.99, 412_000, 16_500, 0.25, 3.8, 4.8, 86, 240, 21),
    ("Heatless Curling Rod Set", "Beauty & Personal Care", 15.90, 288_000, 18_100, 0.30, 2.1, 4.7, 140, 520, 34),
    ("Posture Corrector Back Brace", "Health", 29.99, 176_000, 5_870, 0.22, 0.9, 4.6, 62, 180, 48),
    ("Mini Portable Blender 500ml", "Kitchenware", 32.50, 940_000, 28_900, 0.12, 0.4, 4.5, 780, 3_400, 210),
    ("Magnetic Eyelash Kit", "Beauty & Personal Care", 19.99, 63_000, 3_150, 0.28, 1.6, 4.4, 45, 96, 17),
    ("Car Vacuum Cleaner Cordless", "Automotive", 45.00, 520_000, 11_500, 0.18, 0.2, 4.6, 410, 1_900, 160),
    ("Kids Dinosaur Night Light", "Toys", 21.90, 98_000, 4_470, 0.26, 2.9, 4.9, 33, 71, 12),
    ("Slim Fit Compression Shirt", "Menswear", 26.00, 145_000, 5_580, 0.15, 0.6, 4.2, 220, 640, 95),
    ("Cat Self-Groomer Brush", "Pet Supplies", 12.99, 51_000, 3_930, 0.32, 4.2, 4.7, 28, 60, 9),
    ("Gift Card 50 USD", "Other", 50.00, 300_000, 6_000, 0.02, 0.1, 4.9, 5, 3, 400),
    ("Wireless Earbuds Pro Max", "Electronics", 39.99, 1_250_000, 31_200, 0.08, 0.3, 4.3, 1_450, 6_800, 300),
    ("Silk Bonnet Hair Wrap", "Beauty & Personal Care", 9.50, 74_000, 7_790, 0.29, 1.9, 4.8, 51, 130, 25),
    ("Digital Kitchen Scale", "Kitchenware", 18.00, 42_000, 2_330, 0.14, -0.2, 4.5, 190, 410, 260),
    ("Acne Patch Set 120pcs", "Beauty & Personal Care", 14.99, 610_000, 40_700, 0.24, 1.2, 4.8, 305, 1_250, 70),
    ("Foldable Laptop Stand", "Computers", 27.99, 88_000, 3_140, 0.16, 0.5, 4.6, 96, 210, 130),
]


def build_rows(seed: int = 7) -> List[dict]:
    random.seed(seed)
    today = date.today()
    rows = []
    for index, (name, category, price, revenue, sold, commission,
                growth, rating, creators, videos, age) in enumerate(SAMPLES, 1):
        rows.append({
            "Product ID": f"17{index:08d}",
            "Product Name": name,
            "Category": category,
            "Shop Name": f"{name.split()[0]} Official Store",
            "Price": f"${price:,.2f}",
            "Revenue": f"${revenue:,.0f}",
            "Items Sold": f"{sold:,}",
            "Commission Rate": f"{commission * 100:.0f}%",
            "Revenue Growth": f"{growth * 100:.0f}%",
            "Rating": f"{rating:.1f}",
            "Creators": f"{creators:,}",
            "Videos": f"{videos:,}",
            "Lives": random.randint(0, 60),
            "Launch Date": (today - timedelta(days=age)).isoformat(),
            "Product Link": f"https://shop.tiktok.com/view/product/17{index:08d}",
        })
    return rows


def write_sample(path: str = "data/demo_export.csv", seed: int = 7) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(build_rows(seed))
    return path

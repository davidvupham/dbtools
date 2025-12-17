"""Shared dataset generator used throughout the pandas tutorial.

This module intentionally has no external dependencies beyond numpy + pandas.

Usage (from repo root):

```python
from pathlib import Path
import sys

shared = (
    Path.cwd()
    / "docs"
    / "tutorials"
    / "python"
    / "modules"
    / "pandas"
    / "shared"
)
sys.path.insert(0, str(shared))

from make_orders import make_orders

orders = make_orders(n=200, seed=42)
```
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_orders(n: int = 200, seed: int = 42) -> pd.DataFrame:
    """Create a reproducible synthetic orders dataset.

    Columns:
    - order_id: unique int
    - order_date: datetime64[ns]
    - customer: string-ish
    - category: one of a small set
    - quantity: int
    - price: float
    - shipping_status: category-like string
    - revenue: quantity * price
    """

    rng = np.random.default_rng(seed)

    customers = np.array(
        [
            "Alice Smith",
            "Bob Jones",
            "Charlie Zhang",
            "Diana Lopez",
            "Evan Kim",
            "Fatima Ali",
        ]
    )
    categories = np.array(["avocados", "bananas", "laptops", "phones", "tablets"])
    shipping_status = np.array(["delivered", "shipped", "in transit", "pending"])

    base = pd.Timestamp("2025-01-01")
    order_date = base + pd.to_timedelta(rng.integers(0, 180, size=n), unit="D")

    df = pd.DataFrame(
        {
            "order_id": np.arange(1, n + 1),
            "order_date": order_date,
            "customer": rng.choice(customers, size=n),
            "category": rng.choice(categories, size=n, p=[0.25, 0.15, 0.2, 0.2, 0.2]),
            "quantity": rng.integers(1, 8, size=n),
            "price": rng.choice([0.99, 1.49, 2.99, 399.0, 499.0, 999.0], size=n),
            "shipping_status": rng.choice(shipping_status, size=n, p=[0.55, 0.25, 0.15, 0.05]),
        }
    )

    df["revenue"] = df["quantity"] * df["price"]
    return df

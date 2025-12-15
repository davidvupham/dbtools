# Solutions — 07_cleaning_quality: Cleaning + data quality

## What this solution demonstrates

- Make cleaning rules explicit (drop/normalize/coerce).
- Create validation flags before filtering.
- Normalize text via `.astype("string").str.strip().str.lower()`.

## Why this pattern

Flags let you measure data quality and make a conscious drop/keep decision.

## Common pitfalls

- Silently dropping “bad” rows without tracking how many you lost.
- Using regex replaces without testing edge cases.

## One useful variant

Instead of filtering invalid rows, keep them and route to a “quarantine” DataFrame for review.

## Expected output (example)

- `(len(dirty), len(clean), len(clean2))` shows the dataset shrinking after dropping missing customers and filtering invalid values.
- Validation means are between 0 and 1.
- `shipping_status` values are standardized (e.g. `delivered`, `in_transit`).

## Reference implementation

```python
import numpy as np
import pandas as pd


from pathlib import Path
import sys

# If running from the repository root, this makes the shared module importable:
shared = Path.cwd() / "docs" / "tutorials" / "python" / "modules" / "pandas" / "shared"
sys.path.insert(0, str(shared))

from make_orders import make_orders
orders = make_orders(n=200, seed=42)

dirty = orders.copy()
dirty.loc[0, "shipping_status"] = " Delivered  "
dirty.loc[1, "shipping_status"] = "In Transit"
dirty.loc[2, "price"] = -10

dirty.loc[3, "customer"] = None

status_map = {"in transit": "in_transit", "in-transit": "in_transit"}

clean = (
    dirty
    .dropna(subset=["customer"]).copy()
    .assign(
        shipping_status=lambda d: d["shipping_status"].astype("string").str.strip().str.lower().replace(status_map),
        price=lambda d: pd.to_numeric(d["price"], errors="coerce"),
        quantity=lambda d: pd.to_numeric(d["quantity"], errors="coerce"),
    )
    .assign(
        is_valid_price=lambda d: d["price"].ge(0) & d["price"].notna(),
        is_valid_qty=lambda d: d["quantity"].ge(0) & d["quantity"].notna(),
    )
)

clean2 = clean.loc[clean["is_valid_price"] & clean["is_valid_qty"]].copy()

print((len(dirty), len(clean), len(clean2)))
print(clean[["is_valid_price", "is_valid_qty"]].mean())
```


[← Back to course home](../README.md)

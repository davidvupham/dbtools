# Solutions — 06_transform_assign: Transformations

## What this solution demonstrates

- Prefer vectorized ops + `np.where`/`np.select`.
- Use `.assign()` for method-chaining.
- Use `.pipe()` to compose reusable transformations.

## Why this pattern

Method chains are easier to review and test than scattered mutations.

## Common pitfalls

- Overusing `.apply(axis=1)` (slow, harder to type-check).
- Mixing mutation and chaining without `.copy()` when needed.

## One useful variant

If you need complex logic, consider a small helper function returning a Series, then assign it.

## Expected output (example)

- `segment` has two values (`high`/`low`) and `tier` has (`vip`/`high`/`standard`).
- Pipeline output keeps the same number of rows as input.

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

orders2 = (
    orders
    .assign(is_big=lambda d: d["revenue"].ge(500))
    .assign(segment=lambda d: np.where(d["is_big"], "high", "low"))
)

conds = [orders2["revenue"].ge(1000), orders2["revenue"].between(500, 999.99, inclusive="both")]
choices = ["vip", "high"]
orders2 = orders2.assign(tier=np.select(conds, choices, default="standard"))

print(orders2["segment"].value_counts())
print(orders2["tier"].value_counts())


def normalize_status(d: pd.DataFrame) -> pd.DataFrame:
    return d.assign(shipping_status=d["shipping_status"].astype("string").str.strip().str.lower())


def add_revenue(d: pd.DataFrame) -> pd.DataFrame:
    return d.assign(revenue=d["quantity"] * d["price"])

clean = orders2.pipe(normalize_status).pipe(add_revenue)
print(clean.head())
```


[← Back to course home](../README.md)

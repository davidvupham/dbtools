# Solutions — 03_explore_inspect: Explore + inspect

## What this solution demonstrates

- Use a consistent “first 60 seconds” inspection checklist.
- Use `value_counts(dropna=False)` to detect category issues.
- Build a missingness table (count + rate).

## Why this pattern

Good EDA prevents you from computing “correct” metrics on broken data.

## Common pitfalls

- Skipping `info()` and missing silent dtype problems.
- Ignoring missingness and duplicates before aggregations.

## One useful variant

Add `describe(percentiles=[...])` for tail-risk/outliers.

## Expected output (example)

- `info()` shows row count and non-null counts per column.
- `value_counts` shows a small set of categories/statuses.
- Missingness table shows 0 missing for this synthetic dataset.

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

print(orders.shape)
print(orders.columns)
print(orders.dtypes)
print(orders.head())
print(orders.sample(5, random_state=0))

orders.info()
print(orders.describe(numeric_only=True))

print(orders["category"].value_counts(dropna=False))
print(orders["shipping_status"].value_counts(dropna=False))

missing = (
    orders.isna().sum().to_frame("missing_count")
    .join(orders.isna().mean().to_frame("missing_rate"))
    .sort_values("missing_rate", ascending=False)
)
print(missing)

assert orders["order_id"].is_unique
assert orders["quantity"].ge(0).all()
```


[← Back to course home](../README.md)

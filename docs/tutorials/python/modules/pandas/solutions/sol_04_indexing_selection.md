# Solutions — 04_indexing_selection: Indexing + selection

## What this solution demonstrates

- Use `iloc` for positional, `loc` for label-based selection.
- Set meaningful indices intentionally.
- Use `.loc[mask, col] = ...` for safe assignment.

## Why this pattern

Indexing is where many pandas bugs come from; explicit accessors reduce ambiguity.

## Common pitfalls

- Chained indexing like `df[mask]["col"] = ...` (SettingWithCopy).
- Assuming default integer index is stable after filtering/concat.

## One useful variant

Use `.at`/`.iat` for faster scalar access when you only need one value.

## Expected output (example)

- `orders.iloc[0]` returns a Series for the first row.
- `by_id.loc[10, ...]` returns one row’s fields.
- `segment` is set to `high` only where `revenue >= 500`.

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

print(orders.iloc[0])
print(orders.iloc[:5].shape)

by_id = orders.set_index("order_id")
print(by_id.loc[10, ["customer", "revenue"]])

mi = orders.set_index(["customer", "category"]).sort_index()
print(mi.loc["Alice Smith"].head())
print(mi.loc[("Alice Smith", "avocados"), :].head())

mask = orders["revenue"].ge(500)
orders.loc[mask, "segment"] = "high"
print(orders[["revenue", "segment"]].head())
```


[← Back to course home](../README.md)

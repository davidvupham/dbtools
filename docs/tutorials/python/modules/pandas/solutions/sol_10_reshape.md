# Solutions — 10_reshape: Reshaping

## What this solution demonstrates

- Use `pivot_table` (safe with duplicates) rather than `pivot` when unsure.
- Use `melt` to return to long format.
- Verify totals after reshaping to ensure you didn’t lose/double-count data.

## Why this pattern

Reshaping is easy to get wrong when duplicates exist; checks keep you honest.

## Common pitfalls

- Using `pivot` when keys are not unique (errors or silent assumptions).
- Forgetting to choose an aggregation function when duplicates exist.

## One useful variant

Try adding `margins=True` to `pivot_table` for totals rows/cols (quick reporting).

## Expected output (example)

- The printed totals are nearly equal; the absolute difference should be 0 (or extremely close).
- `unstacked.shape == pivot.shape` passes.

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
orders = make_orders(n=500, seed=42)

pivot = orders.pivot_table(index="customer", columns="category", values="revenue", aggfunc="sum", fill_value=0)

wide = pivot.reset_index()
long = wide.melt(id_vars=["customer"], var_name="category", value_name="revenue")

# total revenue consistency (tolerance for floats)
orig_total = float(orders["revenue"].sum())
pivot_total = float(pivot.to_numpy().sum())
print(orig_total, pivot_total, abs(orig_total - pivot_total))

stacked = pivot.stack()
unstacked = stacked.unstack()

assert unstacked.shape == pivot.shape
```


[← Back to course home](../README.md)

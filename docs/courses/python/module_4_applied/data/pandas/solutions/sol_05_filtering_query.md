# Solutions — 05_filtering_query: Filtering + query

## What this solution demonstrates

- Build boolean masks with parentheses.
- Use `isin` and `between` for readability.
- Use `query()` when it improves clarity and you can express the logic safely.

## Why this pattern

Readable filters are easier to debug and harder to get wrong.

## Common pitfalls

- Forgetting parentheses with `&`/`|` (operator precedence).
- Not handling missing strings in `.str.contains` (use `na=False`).

## One useful variant

Compare `df.query(...)` vs boolean masks; use whichever your team reads faster.

## Expected output (example)

- Boolean mask and `query()` versions return the same row count for equivalent logic.
- `str.contains(..., na=False)` returns a subset of customers matching the pattern.

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

mask = (orders["customer"] == "Alice Smith") & (orders["revenue"] >= 500)
print(orders.loc[mask].head())

print(orders.loc[orders["category"].isin(["avocados", "bananas"])].head())
print(orders.loc[orders["revenue"].between(100, 500, inclusive="both")].head())

mask2 = orders["revenue"].ge(500) & orders["category"].isin(["laptops", "phones"])
q = orders.query("revenue >= 500 and category in ['laptops', 'phones']")
print(len(orders.loc[mask2]), len(q))

contains = orders.loc[orders["customer"].str.contains("ali", case=False, na=False)]
print(contains[["customer"]].drop_duplicates())
```


[← Back to course home](../README.md)

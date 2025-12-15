# Solutions — 09_merge_join_concat: Merge / join / concat

## What this solution demonstrates

- Use `validate=` in `merge` to catch key cardinality bugs.
- Prefer index-based `join` when the right side is indexed on the key.
- Always sanity-check row counts after merges.

## Why this pattern

The most expensive pandas bugs are wrong merges that “look plausible”.

## Common pitfalls

- Many-to-many merges exploding row counts.
- Key dtype mismatch (string vs int) leading to unexpected missing matches.

## One useful variant

Use `indicator=True` in `merge` to see which rows matched (left_only/right_only/both).

## Expected output (example)

- `(len(orders), len(merged_ok), len(merged_bad))`: `merged_ok` equals `orders`, while `merged_bad` can be larger due to duplicated keys.
- `joined.head()` includes the extra `country` column.

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

customers = orders[["customer"]].drop_duplicates().assign(country="US")
merged_ok = orders.merge(customers, on="customer", how="left", validate="m:1")

customers_ix = customers.set_index("customer")
joined = orders.join(customers_ix, on="customer", how="left")

# many-to-many demo
customers_bad = pd.concat([customers, customers.iloc[[0]]], ignore_index=True)
merged_bad = orders.merge(customers_bad, on="customer", how="left")

print((len(orders), len(merged_ok), len(merged_bad)))
print(joined.head())
```


[← Back to course home](../README.md)

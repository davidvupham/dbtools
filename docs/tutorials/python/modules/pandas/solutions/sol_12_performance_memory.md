# Solutions — 12_performance_memory: Performance + memory + CoW

## What this solution demonstrates

- Measure memory first.
- Use `category` for repeated strings.
- Downcast numerics where safe.
- Use `.loc` for assignment to avoid copy/view ambiguity.

## Why this pattern

dtype choices are often the biggest, safest performance win in pandas.

## Common pitfalls

- Over-optimizing without measuring.
- Downcasting without verifying you won’t overflow/lose precision.

## One useful variant

For huge CSVs, process in chunks and aggregate incrementally instead of loading everything.

## Expected output (example)

- Printed memory total after optimization is typically lower than baseline.
- `segment` is populated for rows meeting the revenue threshold.

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
orders = make_orders(n=2000, seed=42)
base_mem = orders.memory_usage(deep=True).sum()

opt = orders.copy()
opt["category"] = opt["category"].astype("category")
opt["shipping_status"] = opt["shipping_status"].astype("category")

opt["quantity"] = pd.to_numeric(opt["quantity"], downcast="integer")
opt["price"] = pd.to_numeric(opt["price"], downcast="float")

opt_mem = opt.memory_usage(deep=True).sum()
print(base_mem, opt_mem)

mask = opt["revenue"].ge(500)
opt.loc[mask, "segment"] = "high"
print(opt[["revenue", "segment"]].head())
```


[← Back to course home](../README.md)

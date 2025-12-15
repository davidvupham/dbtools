# Solutions — 00_setup: Setup + mental model

## What this solution demonstrates

- Verify pandas is installed and the version is known.
- Set display options so tables are readable while learning.
- Create a tiny DataFrame manually, then a reproducible course dataset.

## Why this pattern

You want deterministic data and readable output before you start learning transformations.

## Common pitfalls

- Using `pip` instead of `python -m pip` in multi-Python setups.
- Not seeding randomness (hard to reproduce results).

## One useful variant

If you prefer, set options temporarily using `with pd.option_context(...):`.

## Expected output (example)

- `pd.__version__` prints a version string (e.g. `2.2.x`).
- The manual DataFrame prints with 3 rows and correct `dtypes`.
- `orders.head()` shows columns: `order_id, order_date, customer, category, quantity, price, shipping_status, revenue`.

## Reference implementation

```python
import pandas as pd

print(pd.__version__)

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 120)
pd.set_option("display.max_rows", 30)

df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35], "city": ["NYC", "LA", "NYC"]})
print(df.head())
print(df.dtypes)

import numpy as np
import pandas as pd


from pathlib import Path
import sys

# If running from the repository root, this makes the shared module importable:
shared = Path.cwd() / "docs" / "tutorials" / "python" / "modules" / "pandas" / "shared"
sys.path.insert(0, str(shared))

from make_orders import make_orders
orders = make_orders(n=200, seed=42)
print(orders.head())
print(orders.shape)
print(orders.dtypes)
```


[← Back to course home](../README.md)

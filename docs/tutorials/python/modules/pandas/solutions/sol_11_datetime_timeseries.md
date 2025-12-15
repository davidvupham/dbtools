# Solutions — 11_datetime_timeseries: Datetime + time series

## What this solution demonstrates

- Parse datetimes explicitly.
- Set a sorted DateTimeIndex before `resample`/`rolling`.
- Use `shift` for lag features.

## Why this pattern

Most time-series mistakes come from non-datetime dtypes or unsorted indexes.

## Common pitfalls

- Rolling windows on unsorted indexes.
- Mixing time zones without realizing it (use `utc=True` if needed).

## One useful variant

Use `.rolling(7, min_periods=1)` for row-based windows when timestamps are irregular.

## Expected output (example)

- `monthly_rev` index contains month-start timestamps and a revenue sum per month.
- Rolling mean and lag columns contain `NaN` near the start (expected).
- `dow` is 0–6 and `month` is 1–12.

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
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")

ts = orders.set_index("order_date").sort_index()

monthly_rev = ts["revenue"].resample("MS").sum()
print(monthly_rev.tail())

ts["rev_ma_7d"] = ts["revenue"].rolling("7D").mean()
ts["rev_lag_1"] = ts["revenue"].shift(1)

idx = ts.index

ts = ts.assign(dow=idx.dayofweek, month=idx.month)
print(ts[["dow", "month"]].head())
```


[← Back to course home](../README.md)

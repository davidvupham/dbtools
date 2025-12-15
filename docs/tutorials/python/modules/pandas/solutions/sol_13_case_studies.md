# Solutions — 13_case_studies: Case studies

## What this solution demonstrates

- Compose steps: clean → validate → aggregate → reshape.
- Use groupby named aggregations for report tables.
- Use time-series resample + pivot for trend reporting.

## Why this pattern

This is how pandas is used in practice: end-to-end workflows with deliverables.

## Common pitfalls

- Skipping validation checks before reporting numbers.
- Building pivots before cleaning categories (inconsistent labels).

## One useful variant

Add a “data quality” section to the report: missing rate + invalid flags by column.

## Expected output (example)

- Category report is sorted by `revenue_total`.
- Monthly pivot has one row per month and columns per category.
- Top customers table has 10 rows.

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
orders = make_orders(n=1000, seed=42)
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")

# A — category report
cat_report = (
    orders.groupby("category").agg(
        revenue_total=("revenue", "sum"),
        orders=("order_id", "nunique"),
        items=("quantity", "sum"),
    )
    .sort_values("revenue_total", ascending=False)
)
print(cat_report.head())

# B — monthly pivot

ts = orders.set_index("order_date").sort_index()
monthly = ts.groupby("category")["revenue"].resample("MS").sum().reset_index()
pivot = monthly.pivot_table(index="order_date", columns="category", values="revenue", aggfunc="sum", fill_value=0)
print(pivot.tail())

# C — top customers

top_customers = (
    orders.groupby("customer").agg(revenue_total=("revenue", "sum"), orders=("order_id", "nunique"))
    .sort_values("revenue_total", ascending=False)
    .head(10)
)
print(top_customers)
```


[← Back to course home](../README.md)

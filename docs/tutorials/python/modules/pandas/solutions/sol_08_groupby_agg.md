# Solutions — 08_groupby_agg: GroupBy + aggregations

## What this solution demonstrates

- Use named aggregations for readable column names.
- `transform` returns same-size results for per-row features.
- Ranking within groups is a standard “top-N per group” pattern.

## Why this pattern

Readable aggregation outputs prevent downstream confusion (especially in joins/pivots).

## Common pitfalls

- Using `groupby.apply` when `agg/transform` would be simpler and faster.
- Counting rows instead of unique ids when duplicates exist.

## One useful variant

Try `observed=True` when grouping on categoricals to avoid unused categories.

## Expected output (example)

- Category revenue totals are sorted descending.
- `customer_avg_revenue` column exists and repeats per customer.
- Top-2 per customer contains at most 2 rows for each customer.

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

rev_by_cat = orders.groupby("category")["revenue"].sum().sort_values(ascending=False)
print(rev_by_cat)

summary = orders.groupby("category").agg(
    revenue_total=("revenue", "sum"),
    revenue_avg=("revenue", "mean"),
    orders_count=("order_id", "nunique"),
)
print(summary.sort_values("revenue_total", ascending=False))

multi = orders.groupby(["customer", "category"]).agg(revenue_total=("revenue", "sum"))
print(multi.head())

orders = orders.assign(customer_avg_revenue=orders.groupby("customer")["revenue"].transform("mean"))

ranked = orders.assign(rank_in_customer=orders.groupby("customer")["revenue"].rank(method="dense", ascending=False))
top2 = ranked.loc[ranked["rank_in_customer"].le(2)].sort_values(["customer", "rank_in_customer"])
print(top2[["customer", "order_id", "revenue", "rank_in_customer"]].head(20))
```


[← Back to course home](../README.md)

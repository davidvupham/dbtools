# 06 — Transformations (`assign`, vectorization, `pipe`)

Transformations are how you create features, normalize data, and build reproducible pipelines.

## Prefer vectorization over `.apply`

Vectorized:

```python
orders["revenue"] = orders["quantity"] * orders["price"]
```

Avoid row-by-row `apply` unless you must:

```python
# orders["x"] = orders.apply(lambda row: ..., axis=1)  # usually slow
```

## `assign` for readable pipelines

```python
orders2 = (
    orders
    .assign(revenue=lambda d: d["quantity"] * d["price"])
    .assign(is_big=lambda d: d["revenue"].ge(500))
)
```

## Conditional logic

### `np.where`

```python
import numpy as np

orders["segment"] = np.where(orders["revenue"].ge(500), "high", "low")
```

### `np.select` for multiple conditions

```python
import numpy as np

conds = [
    orders["revenue"].ge(1000),
    orders["revenue"].between(500, 999.99, inclusive="both"),
]
choices = ["vip", "high"]
orders["tier"] = np.select(conds, choices, default="standard")
```

## String normalization (clean + safe)

```python
orders["shipping_status"] = (
    orders["shipping_status"]
    .astype("string")
    .str.strip()
    .str.lower()
)
```

## Extract patterns (IDs, numbers)

```python
# Extract digits from a messy customer_id column
# orders["customer_id"] = "CUS-" + orders["customer_id"].str.extract(r"(\d+)")[0].fillna("0000")
```

## Numeric coercion

```python
import pandas as pd

orders["price"] = pd.to_numeric(orders["price"], errors="coerce")
```

## Outlier handling (simple clip)

```python
q1 = orders["quantity"].quantile(0.25)
q3 = orders["quantity"].quantile(0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
orders["quantity_capped"] = orders["quantity"].clip(upper=upper)
```

## `pipe` for reusable steps

```python
def normalize_status(d):
    return d.assign(
        shipping_status=d["shipping_status"].astype("string").str.strip().str.lower()
    )


def add_revenue(d):
    return d.assign(revenue=d["quantity"] * d["price"])


clean = orders.pipe(normalize_status).pipe(add_revenue)
```

## Summary

- Prefer vectorized ops, `.str`, `.dt`, `np.where/np.select`.
- Use `.assign` + `.pipe` to create readable, testable pipelines.

## Next

Continue to [07 — Cleaning + data quality](07_cleaning_quality.md).

[← Back to course home](../README.md)
